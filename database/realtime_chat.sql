-- AnonBox secure realtime chat
-- Opaque per-conversation topics, message/read broadcasts and typing events.

do $$
begin
  if not exists (select 1 from vault.secrets where name = 'anonbox_realtime_topic_secret') then
    perform vault.create_secret(
      replace(gen_random_uuid()::text, '-', '') || replace(gen_random_uuid()::text, '-', ''),
      'anonbox_realtime_topic_secret',
      'Secret interne pour dériver les topics Realtime AnonBox'
    );
  end if;
end
$$;

create or replace function public.anonbox_realtime_topic(p_conversation_id uuid)
returns text
language plpgsql
security definer
set search_path = ''
as $$
declare
  v_secret text;
begin
  select decrypted_secret into v_secret
  from vault.decrypted_secrets
  where name = 'anonbox_realtime_topic_secret'
  limit 1;

  if v_secret is null or v_secret = '' then
    raise exception 'Realtime topic unavailable';
  end if;

  return 'anonbox-chat-' || encode(
    extensions.digest(convert_to(v_secret || ':' || p_conversation_id::text, 'UTF8'), 'sha256'),
    'hex'
  );
end;
$$;

revoke all on function public.anonbox_realtime_topic(uuid) from public, anon, authenticated;
grant execute on function public.anonbox_realtime_topic(uuid) to service_role;

create or replace function public.anonbox_get_realtime_topic(
  p_conversation_id uuid,
  p_device_id text default null
)
returns text
language plpgsql
security definer
set search_path = ''
as $$
declare
  v_uid uuid := auth.uid();
  v_device text := coalesce(p_device_id, '');
  v_allowed boolean := false;
begin
  select exists(
    select 1
    from public.anonbox_messages_v2 m
    join public.anonbox_boxes b on b.id = m.box_id
    where m.conversation_id = p_conversation_id
      and b.owner_id = v_uid
  ) into v_allowed;

  if not v_allowed and length(v_device) between 8 and 200 then
    select exists(
      select 1
      from public.anonbox_messages_v2 m
      where m.conversation_id = p_conversation_id
        and m.direction = 'visitor'
        and (
          (m.sender_mode = 'anonymous' and m.sender_fingerprint = encode(
            extensions.digest(convert_to(m.box_id::text || ':' || v_device, 'UTF8'), 'sha256'),
            'hex'
          ))
          or
          (m.sender_mode = 'profile' and v_uid is not null and m.sender_user_id = v_uid)
        )
    ) into v_allowed;
  end if;

  if not v_allowed then return null; end if;
  return public.anonbox_realtime_topic(p_conversation_id);
end;
$$;

grant execute on function public.anonbox_get_realtime_topic(uuid,text) to anon, authenticated;

create or replace function public.anonbox_set_typing(
  p_conversation_id uuid,
  p_device_id text,
  p_typing boolean
)
returns jsonb
language plpgsql
security definer
set search_path = ''
as $$
declare
  v_uid uuid := auth.uid();
  v_device text := coalesce(p_device_id, '');
  v_actor text := null;
  v_topic text;
begin
  if exists(
    select 1
    from public.anonbox_messages_v2 m
    join public.anonbox_boxes b on b.id = m.box_id
    where m.conversation_id = p_conversation_id
      and b.owner_id = v_uid
  ) then
    v_actor := 'owner';
  elsif length(v_device) between 8 and 200 and exists(
    select 1
    from public.anonbox_messages_v2 m
    where m.conversation_id = p_conversation_id
      and m.direction = 'visitor'
      and (
        (m.sender_mode = 'anonymous' and m.sender_fingerprint = encode(
          extensions.digest(convert_to(m.box_id::text || ':' || v_device, 'UTF8'), 'sha256'),
          'hex'
        ))
        or
        (m.sender_mode = 'profile' and v_uid is not null and m.sender_user_id = v_uid)
      )
  ) then
    v_actor := 'visitor';
  end if;

  if v_actor is null then
    return jsonb_build_object('ok', false, 'error', 'Conversation introuvable.');
  end if;

  v_topic := public.anonbox_realtime_topic(p_conversation_id);
  perform realtime.send(
    jsonb_build_object(
      'actor', v_actor,
      'typing', coalesce(p_typing, false),
      'conversation_id', p_conversation_id::text
    ),
    'typing', v_topic, false
  );

  return jsonb_build_object('ok', true);
end;
$$;

grant execute on function public.anonbox_set_typing(uuid,text,boolean) to anon, authenticated;

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
  v_event := case when tg_op = 'INSERT' then 'message' else 'read' end;

  perform realtime.send(
    jsonb_build_object(
      'message_id', new.id::text,
      'conversation_id', new.conversation_id::text,
      'direction', new.direction,
      'read_at', new.read_at
    ),
    v_event, v_topic, false
  );

  return new;
exception when others then
  return new;
end;
$$;

revoke all on function public.anonbox_broadcast_message_event() from public, anon, authenticated;

drop trigger if exists anonbox_realtime_message_insert on public.anonbox_messages_v2;
create trigger anonbox_realtime_message_insert
after insert on public.anonbox_messages_v2
for each row execute function public.anonbox_broadcast_message_event();

drop trigger if exists anonbox_realtime_message_read on public.anonbox_messages_v2;
create trigger anonbox_realtime_message_read
after update of read_at on public.anonbox_messages_v2
for each row
when (old.read_at is distinct from new.read_at)
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
          'sender_pseudonym',mm.sender_pseudonym_snapshot,'created_at',mm.created_at,'read_at',mm.read_at
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
