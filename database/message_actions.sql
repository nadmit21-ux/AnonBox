-- AnonBox message actions v1
-- Reply-to, reactions, secure deletion and realtime refresh support.

alter table public.anonbox_messages_v2
  add column if not exists reply_to_id bigint null,
  add column if not exists reaction_summary jsonb not null default '{}'::jsonb;

do $$
begin
  if not exists (
    select 1 from pg_constraint
    where conname='anonbox_messages_v2_reply_to_id_fkey'
      and conrelid='public.anonbox_messages_v2'::regclass
  ) then
    alter table public.anonbox_messages_v2
      add constraint anonbox_messages_v2_reply_to_id_fkey
      foreign key (reply_to_id) references public.anonbox_messages_v2(id) on delete set null;
  end if;
end
$$;

create table if not exists public.anonbox_message_reactions (
  message_id bigint not null references public.anonbox_messages_v2(id) on delete cascade,
  actor_key text not null,
  emoji text not null,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  primary key (message_id, actor_key)
);

alter table public.anonbox_message_reactions enable row level security;
revoke all on public.anonbox_message_reactions from public, anon, authenticated;
grant select,insert,update,delete on public.anonbox_message_reactions to service_role;

drop function if exists public.anonbox_submit_message(text,text,text,text);
create function public.anonbox_submit_message(
  p_slug text,
  p_body text,
  p_mode text,
  p_device_id text,
  p_reply_to_id bigint default null
)
returns jsonb
language plpgsql
security definer
set search_path = ''
as $$
declare
  v_slug text := lower(trim(coalesce(p_slug, '')));
  v_body text := trim(coalesce(p_body, ''));
  v_mode text := case when p_mode = 'profile' then 'profile' else 'anonymous' end;
  v_device text := coalesce(p_device_id, '');
  b public.anonbox_boxes%rowtype;
  v_fingerprint text;
  v_recent_count bigint;
  v_sender uuid := null;
  v_pseudo text := null;
  v_avatar text := null;
  v_conversation uuid;
  v_reply_conversation uuid;
  v_message_id bigint;
begin
  if length(v_body) < 1 or length(v_body) > 1500 then return jsonb_build_object('ok', false, 'error', 'Le message doit contenir entre 1 et 1500 caractères.'); end if;
  if length(v_device) < 8 or length(v_device) > 200 then return jsonb_build_object('ok', false, 'error', 'Navigateur non reconnu. Recharge la page.'); end if;
  if v_slug !~ '^[a-z0-9][a-z0-9_-]{2,31}$' then return jsonb_build_object('ok', false, 'error', 'Boîte introuvable.'); end if;

  select * into b from public.anonbox_boxes where slug = v_slug limit 1;
  if not found then return jsonb_build_object('ok', false, 'error', 'Boîte introuvable.'); end if;
  if not b.is_open then return jsonb_build_object('ok', false, 'error', 'Cette boîte est fermée pour le moment.'); end if;
  if v_mode = 'anonymous' and not b.allow_anonymous then return jsonb_build_object('ok', false, 'error', 'Les messages anonymes sont désactivés.'); end if;
  if v_mode = 'profile' and not b.allow_profile_messages then return jsonb_build_object('ok', false, 'error', 'Les messages avec profil sont désactivés.'); end if;

  v_fingerprint := encode(extensions.digest(convert_to(b.id::text || ':' || v_device, 'UTF8'), 'sha256'), 'hex');

  select count(*) into v_recent_count from public.anonbox_messages_v2
  where box_id=b.id and sender_fingerprint=v_fingerprint and direction='visitor' and created_at>=now()-interval '10 minutes';
  if v_recent_count >= 5 then return jsonb_build_object('ok', false, 'error', 'Trop de messages envoyés. Réessaie un peu plus tard.'); end if;

  if v_mode='profile' then
    v_sender:=auth.uid();
    if v_sender is null then return jsonb_build_object('ok', false, 'error', 'Connecte-toi pour envoyer avec ton profil.'); end if;
    select pseudonym,avatar_path into v_pseudo,v_avatar from public.anonbox_profiles where user_id=v_sender limit 1;
    if not found then return jsonb_build_object('ok', false, 'error', 'Profil introuvable.'); end if;

    select conversation_id into v_conversation from public.anonbox_messages_v2
    where box_id=b.id and direction='visitor' and sender_mode='profile' and sender_user_id=v_sender
    order by created_at desc limit 1;
  else
    select conversation_id into v_conversation from public.anonbox_messages_v2
    where box_id=b.id and sender_fingerprint=v_fingerprint and direction='visitor' and sender_mode='anonymous'
    order by created_at desc limit 1;
  end if;

  if v_conversation is null then v_conversation:=gen_random_uuid(); end if;

  if p_reply_to_id is not null then
    select conversation_id into v_reply_conversation
    from public.anonbox_messages_v2
    where id=p_reply_to_id and deleted_at is null
    limit 1;
    if v_reply_conversation is null or v_reply_conversation<>v_conversation then
      return jsonb_build_object('ok',false,'error','Le message cité ne fait pas partie de cette conversation.');
    end if;
  end if;

  insert into public.anonbox_messages_v2(
    box_id,conversation_id,direction,body,sender_mode,sender_user_id,
    sender_pseudonym_snapshot,sender_avatar_path_snapshot,sender_fingerprint,reply_to_id
  ) values(
    b.id,v_conversation,'visitor',v_body,v_mode,v_sender,v_pseudo,v_avatar,v_fingerprint,p_reply_to_id
  ) returning id into v_message_id;

  return jsonb_build_object(
    'ok',true,
    'message_id',v_message_id,
    'conversation_id',v_conversation,
    'message',case when v_mode='anonymous' then 'Message envoyé anonymement ✓' else 'Message envoyé avec ton profil ✓' end
  );
end;
$$;
revoke all on function public.anonbox_submit_message(text,text,text,text,bigint) from public;
grant execute on function public.anonbox_submit_message(text,text,text,text,bigint) to anon, authenticated;

drop function if exists public.anonbox_reply(uuid,text);
create function public.anonbox_reply(
  p_conversation_id uuid,
  p_body text,
  p_reply_to_id bigint default null
)
returns jsonb
language plpgsql
security definer
set search_path = ''
as $$
declare
  v_uid uuid := auth.uid();
  v_body text := trim(coalesce(p_body, ''));
  v_box_id uuid;
  v_fingerprint text;
  v_pseudo text;
  v_avatar text;
  v_recent bigint;
  v_reply_conversation uuid;
  v_message_id bigint;
begin
  if v_uid is null then return jsonb_build_object('ok', false, 'error', 'Connexion requise.'); end if;
  if length(v_body) < 1 or length(v_body) > 1500 then return jsonb_build_object('ok', false, 'error', 'La réponse doit contenir entre 1 et 1500 caractères.'); end if;

  select m.box_id, m.sender_fingerprint into v_box_id, v_fingerprint
  from public.anonbox_messages_v2 m
  join public.anonbox_boxes b on b.id = m.box_id
  where m.conversation_id = p_conversation_id and b.owner_id = v_uid
  order by m.created_at asc limit 1;
  if not found then return jsonb_build_object('ok', false, 'error', 'Conversation introuvable.'); end if;

  if p_reply_to_id is not null then
    select conversation_id into v_reply_conversation
    from public.anonbox_messages_v2
    where id=p_reply_to_id and deleted_at is null
    limit 1;
    if v_reply_conversation is null or v_reply_conversation<>p_conversation_id then
      return jsonb_build_object('ok',false,'error','Le message cité ne fait pas partie de cette conversation.');
    end if;
  end if;

  select count(*) into v_recent from public.anonbox_messages_v2
  where conversation_id = p_conversation_id and direction = 'owner' and created_at >= now() - interval '10 minutes';
  if v_recent >= 30 then return jsonb_build_object('ok', false, 'error', 'Trop de réponses envoyées. Réessaie un peu plus tard.'); end if;

  select pseudonym, avatar_path into v_pseudo, v_avatar from public.anonbox_profiles where user_id = v_uid limit 1;
  v_pseudo := coalesce(nullif(v_pseudo,''), 'Propriétaire');

  insert into public.anonbox_messages_v2(
    box_id, conversation_id, direction, body, sender_mode, sender_user_id,
    sender_pseudonym_snapshot, sender_avatar_path_snapshot, sender_fingerprint, read_at, reply_to_id
  ) values (
    v_box_id, p_conversation_id, 'owner', v_body, 'owner', v_uid,
    v_pseudo, v_avatar, v_fingerprint, null, p_reply_to_id
  ) returning id into v_message_id;

  return jsonb_build_object('ok', true, 'message_id',v_message_id, 'message', 'Réponse envoyée ✓');
end;
$$;
revoke all on function public.anonbox_reply(uuid,text,bigint) from public, anon;
grant execute on function public.anonbox_reply(uuid,text,bigint) to authenticated;

create or replace function public.anonbox_delete_message(
  p_message_id bigint,
  p_device_id text default null
)
returns jsonb
language plpgsql
security definer
set search_path = ''
as $$
declare
  v_uid uuid := auth.uid();
  v_device text := coalesce(p_device_id,'');
  m public.anonbox_messages_v2%rowtype;
  v_owner uuid;
  v_expected_fingerprint text;
  v_allowed boolean := false;
begin
  select * into m from public.anonbox_messages_v2 where id=p_message_id limit 1;
  if not found then return jsonb_build_object('ok',false,'error','Message introuvable.'); end if;
  if m.deleted_at is not null then return jsonb_build_object('ok',true,'already_deleted',true); end if;

  select owner_id into v_owner from public.anonbox_boxes where id=m.box_id;

  if m.direction='owner' and v_uid is not null and v_uid=v_owner then
    v_allowed:=true;
  elsif m.direction='visitor' and m.sender_mode='profile' and v_uid is not null and m.sender_user_id=v_uid then
    v_allowed:=true;
  elsif m.direction='visitor' and m.sender_mode='anonymous' and length(v_device) between 8 and 200 then
    v_expected_fingerprint:=encode(extensions.digest(convert_to(m.box_id::text || ':' || v_device,'UTF8'),'sha256'),'hex');
    v_allowed:=m.sender_fingerprint=v_expected_fingerprint;
  end if;

  if not v_allowed then return jsonb_build_object('ok',false,'error','Tu ne peux supprimer que tes propres messages.'); end if;

  update public.anonbox_messages_v2 set deleted_at=now() where id=p_message_id;
  return jsonb_build_object('ok',true);
end;
$$;
revoke all on function public.anonbox_delete_message(bigint,text) from public;
grant execute on function public.anonbox_delete_message(bigint,text) to anon, authenticated;

create or replace function public.anonbox_toggle_reaction(
  p_message_id bigint,
  p_emoji text,
  p_device_id text default null
)
returns jsonb
language plpgsql
security definer
set search_path = ''
as $$
declare
  v_uid uuid := auth.uid();
  v_device text := coalesce(p_device_id,'');
  v_emoji text := coalesce(p_emoji,'');
  m public.anonbox_messages_v2%rowtype;
  v_owner uuid;
  v_actor_key text := null;
  v_existing text;
  v_fingerprint text;
  v_summary jsonb := '{}'::jsonb;
begin
  if v_emoji not in ('❤️','😂','😮','😢','👍','👎') then
    return jsonb_build_object('ok',false,'error','Réaction non prise en charge.');
  end if;

  select * into m from public.anonbox_messages_v2 where id=p_message_id and deleted_at is null limit 1;
  if not found then return jsonb_build_object('ok',false,'error','Message introuvable.'); end if;
  select owner_id into v_owner from public.anonbox_boxes where id=m.box_id;

  if v_uid is not null and v_uid=v_owner then
    v_actor_key:='owner:'||v_uid::text;
  elsif v_uid is not null and exists(
    select 1 from public.anonbox_messages_v2 x
    where x.conversation_id=m.conversation_id and x.direction='visitor' and x.sender_mode='profile' and x.sender_user_id=v_uid
  ) then
    v_actor_key:='profile:'||v_uid::text;
  elsif length(v_device) between 8 and 200 then
    v_fingerprint:=encode(extensions.digest(convert_to(m.box_id::text || ':' || v_device,'UTF8'),'sha256'),'hex');
    if exists(
      select 1 from public.anonbox_messages_v2 x
      where x.conversation_id=m.conversation_id and x.direction='visitor' and x.sender_mode='anonymous' and x.sender_fingerprint=v_fingerprint
    ) then
      v_actor_key:='anon:'||v_fingerprint;
    end if;
  end if;

  if v_actor_key is null then return jsonb_build_object('ok',false,'error','Conversation introuvable.'); end if;

  select emoji into v_existing
  from public.anonbox_message_reactions
  where message_id=p_message_id and actor_key=v_actor_key;

  if found and v_existing=v_emoji then
    delete from public.anonbox_message_reactions
    where message_id=p_message_id and actor_key=v_actor_key;
  elsif found then
    update public.anonbox_message_reactions
    set emoji=v_emoji,updated_at=now()
    where message_id=p_message_id and actor_key=v_actor_key;
  else
    insert into public.anonbox_message_reactions(message_id,actor_key,emoji)
    values(p_message_id,v_actor_key,v_emoji);
  end if;

  select coalesce(jsonb_object_agg(emoji,cnt),'{}'::jsonb) into v_summary
  from (
    select emoji,count(*)::int cnt
    from public.anonbox_message_reactions
    where message_id=p_message_id
    group by emoji
  ) s;

  update public.anonbox_messages_v2
  set reaction_summary=v_summary
  where id=p_message_id;

  return jsonb_build_object('ok',true,'reactions',v_summary);
end;
$$;
revoke all on function public.anonbox_toggle_reaction(bigint,text,text) from public;
grant execute on function public.anonbox_toggle_reaction(bigint,text,text) to anon, authenticated;

create or replace function public.anonbox_broadcast_message_event()
returns trigger
language plpgsql
security definer
set search_path = ''
as $$
declare
  v_topic text;
  v_event text;
begin
  v_topic := public.anonbox_realtime_topic(new.conversation_id);
  if tg_op='INSERT' then
    v_event:='message';
  elsif old.read_at is distinct from new.read_at then
    v_event:='read';
  elsif old.reaction_summary is distinct from new.reaction_summary then
    v_event:='reaction';
  else
    v_event:='message';
  end if;

  perform realtime.send(
    jsonb_build_object(
      'message_id',new.id::text,
      'conversation_id',new.conversation_id::text,
      'direction',new.direction,
      'read_at',new.read_at,
      'deleted',new.deleted_at is not null,
      'reactions',new.reaction_summary
    ),
    v_event,v_topic,false
  );
  return new;
exception when others then
  return new;
end;
$$;
revoke all on function public.anonbox_broadcast_message_event() from public, anon, authenticated;

drop trigger if exists anonbox_realtime_message_read on public.anonbox_messages_v2;
drop trigger if exists anonbox_realtime_message_update on public.anonbox_messages_v2;
create trigger anonbox_realtime_message_update
after update of read_at,deleted_at,reaction_summary on public.anonbox_messages_v2
for each row
when (
  old.read_at is distinct from new.read_at
  or old.deleted_at is distinct from new.deleted_at
  or old.reaction_summary is distinct from new.reaction_summary
)
execute function public.anonbox_broadcast_message_event();

create or replace function public.anonbox_get_library(p_device_id text)
returns jsonb
language plpgsql
security definer
set search_path = ''
as $$
declare
  v_device text := coalesce(p_device_id, '');
  v_uid uuid := auth.uid();
  v_result jsonb;
begin
  if length(v_device) < 8 or length(v_device) > 200 then return '[]'::jsonb; end if;

  with eligible as (
    select distinct m.conversation_id,m.box_id
    from public.anonbox_messages_v2 m
    where m.direction='visitor' and (
      (m.sender_mode='anonymous' and m.sender_fingerprint=encode(extensions.digest(convert_to(m.box_id::text || ':' || v_device,'UTF8'),'sha256'),'hex'))
      or
      (m.sender_mode='profile' and v_uid is not null and m.sender_user_id=v_uid)
    )
  )
  select coalesce(jsonb_agg(conv order by (conv->>'last_at') desc),'[]'::jsonb) into v_result
  from (
    select jsonb_build_object(
      'conversation_id',e.conversation_id,
      'realtime_topic',public.anonbox_realtime_topic(e.conversation_id),
      'box_id',b.id,
      'slug',b.slug,
      'title',b.title,
      'owner',jsonb_build_object(
        'pseudonym',coalesce(nullif(p.pseudonym,''),'Utilisateur'),
        'avatar_url',case when p.avatar_path is not null and p.avatar_path<>'' then 'https://ugyrgvbfwvmuhsjmjtue.supabase.co/storage/v1/object/public/anonbox-avatars/'||p.avatar_path else null end
      ),
      'last_at',max(m.created_at),
      'messages',(
        select coalesce(jsonb_agg(jsonb_build_object(
          'id',mm.id,'body',mm.body,'direction',mm.direction,'sender_mode',mm.sender_mode,
          'sender_pseudonym',mm.sender_pseudonym_snapshot,'created_at',mm.created_at,'read_at',mm.read_at,
          'reply_to_id',mm.reply_to_id,'reaction_summary',mm.reaction_summary
        ) order by mm.created_at),'[]'::jsonb)
        from public.anonbox_messages_v2 mm
        where mm.conversation_id=e.conversation_id and mm.deleted_at is null
      )
    ) conv
    from eligible e
    join public.anonbox_boxes b on b.id=e.box_id
    join public.anonbox_profiles p on p.user_id=b.owner_id
    join public.anonbox_messages_v2 m on m.conversation_id=e.conversation_id and m.deleted_at is null
    group by e.conversation_id,b.id,b.slug,b.title,p.pseudonym,p.avatar_path
  ) s;

  return coalesce(v_result,'[]'::jsonb);
end;
$$;
grant execute on function public.anonbox_get_library(text) to anon, authenticated;
