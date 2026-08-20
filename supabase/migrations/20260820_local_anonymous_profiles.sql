drop function if exists public.anonbox_submit_message(text,text,text,text,bigint);

create or replace function public.anonbox_submit_message(
  p_slug text,
  p_body text,
  p_mode text,
  p_device_id text,
  p_reply_to_id bigint default null,
  p_anon_pseudonym text default null,
  p_anon_avatar_path text default null
)
returns jsonb
language plpgsql
security definer
set search_path to ''
as $function$
declare
  v_slug text := lower(trim(coalesce(p_slug, '')));
  v_body text := trim(coalesce(p_body, ''));
  v_mode text := case when p_mode = 'profile' then 'profile' else 'anonymous' end;
  v_device text := coalesce(p_device_id, '');
  v_anon_pseudo text := nullif(trim(coalesce(p_anon_pseudonym, '')), '');
  v_anon_avatar text := nullif(trim(coalesce(p_anon_avatar_path, '')), '');
  b public.anonbox_boxes%rowtype;
  v_fingerprint text;
  v_device_hash text;
  v_recent_count bigint;
  v_sender uuid := null;
  v_pseudo text := null;
  v_avatar text := null;
  v_conversation uuid;
  v_reply_conversation uuid;
  v_message_id bigint;
begin
  if length(v_body) < 1 or length(v_body) > 1500 then
    return jsonb_build_object('ok', false, 'error', 'Le message doit contenir entre 1 et 1500 caractères.');
  end if;
  if length(v_device) < 8 or length(v_device) > 200 then
    return jsonb_build_object('ok', false, 'error', 'Navigateur non reconnu. Recharge la page.');
  end if;
  if v_slug !~ '^[a-z0-9][a-z0-9_-]{2,31}$' then
    return jsonb_build_object('ok', false, 'error', 'Boîte introuvable.');
  end if;

  select * into b from public.anonbox_boxes where slug = v_slug limit 1;
  if not found then return jsonb_build_object('ok', false, 'error', 'Boîte introuvable.'); end if;
  if not b.is_open then return jsonb_build_object('ok', false, 'error', 'Cette boîte est fermée pour le moment.'); end if;
  if v_mode = 'anonymous' and not b.allow_anonymous then return jsonb_build_object('ok', false, 'error', 'Les messages anonymes sont désactivés.'); end if;
  if v_mode = 'profile' and not b.allow_profile_messages then return jsonb_build_object('ok', false, 'error', 'Les messages avec profil sont désactivés.'); end if;

  v_fingerprint := encode(extensions.digest(convert_to(b.id::text || ':' || v_device, 'UTF8'), 'sha256'), 'hex');
  v_device_hash := encode(extensions.digest(convert_to(v_device, 'UTF8'), 'sha256'), 'hex');

  select count(*) into v_recent_count
  from public.anonbox_messages_v2
  where box_id=b.id and sender_fingerprint=v_fingerprint and direction='visitor' and created_at>=now()-interval '10 minutes';
  if v_recent_count >= 5 then
    return jsonb_build_object('ok', false, 'error', 'Trop de messages envoyés. Réessaie un peu plus tard.');
  end if;

  if v_mode='profile' then
    v_sender:=auth.uid();
    if v_sender is null then return jsonb_build_object('ok', false, 'error', 'Connecte-toi pour envoyer avec ton profil.'); end if;
    select pseudonym,avatar_path into v_pseudo,v_avatar from public.anonbox_profiles where user_id=v_sender limit 1;
    if not found then return jsonb_build_object('ok', false, 'error', 'Profil introuvable.'); end if;

    select conversation_id into v_conversation
    from public.anonbox_messages_v2
    where box_id=b.id and direction='visitor' and sender_mode='profile' and sender_user_id=v_sender
    order by created_at desc limit 1;
  else
    if v_anon_pseudo is not null then
      if length(v_anon_pseudo) < 2 or length(v_anon_pseudo) > 32 then
        return jsonb_build_object('ok', false, 'error', 'Le nom du profil anonyme doit contenir entre 2 et 32 caractères.');
      end if;
      v_pseudo := v_anon_pseudo;
    end if;

    if v_anon_avatar is not null then
      if v_anon_avatar not like ('anonymous/' || v_device_hash || '/%') then
        return jsonb_build_object('ok', false, 'error', 'Avatar anonyme invalide.');
      end if;
      v_avatar := v_anon_avatar;
    end if;

    select conversation_id into v_conversation
    from public.anonbox_messages_v2
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
    'message',case
      when v_mode='profile' then 'Message envoyé avec ton profil ✓'
      when v_pseudo is not null then 'Message envoyé avec ton profil anonyme ✓'
      else 'Message envoyé anonymement ✓'
    end
  );
end;
$function$;

revoke all on function public.anonbox_submit_message(text,text,text,text,bigint,text,text) from public;
grant execute on function public.anonbox_submit_message(text,text,text,text,bigint,text,text) to anon, authenticated;
