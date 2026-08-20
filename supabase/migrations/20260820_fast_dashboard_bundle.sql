create or replace function public.anonbox_get_dashboard()
returns jsonb
language plpgsql
security definer
set search_path to ''
as $function$
declare
  v_uid uuid := auth.uid();
  v_profile jsonb;
  v_box jsonb;
  v_box_id uuid;
  v_messages jsonb;
  v_preferences jsonb;
begin
  if v_uid is null then
    raise exception 'Session requise';
  end if;

  select to_jsonb(p) into v_profile
  from public.anonbox_profiles p
  where p.user_id = v_uid
  limit 1;

  select to_jsonb(b), b.id into v_box, v_box_id
  from public.anonbox_boxes b
  where b.owner_id = v_uid
  limit 1;

  if v_profile is null or v_box is null then
    raise exception 'Profil ou boîte introuvable';
  end if;

  select coalesce(jsonb_agg(to_jsonb(x) order by x.created_at), '[]'::jsonb)
  into v_messages
  from (
    select
      m.id,m.conversation_id,m.direction,m.body,m.sender_mode,m.sender_user_id,
      m.sender_pseudonym_snapshot,m.sender_avatar_path_snapshot,m.sender_fingerprint,
      m.created_at,m.read_at,m.deleted_at,m.reply_to_id,m.reaction_summary,
      m.attachment_id,m.attachment_name,m.attachment_mime,m.attachment_size,
      m.view_once,m.view_once_opened_at,m.voice_duration_ms
    from public.anonbox_messages_v2 m
    where m.box_id = v_box_id and m.deleted_at is null
    order by m.created_at desc
    limit 500
  ) x;

  select coalesce(jsonb_agg(to_jsonb(p) order by p.updated_at desc nulls last), '[]'::jsonb)
  into v_preferences
  from public.anonbox_conversation_preferences p
  where p.owner_id = v_uid;

  return jsonb_build_object(
    'profile', v_profile,
    'box', v_box,
    'messages', v_messages,
    'preferences', v_preferences
  );
end;
$function$;

revoke all on function public.anonbox_get_dashboard() from public;
grant execute on function public.anonbox_get_dashboard() to authenticated;
