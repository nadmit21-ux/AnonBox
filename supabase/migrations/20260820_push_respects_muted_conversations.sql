-- Skip notification enqueue when the owner muted this conversation.
create or replace function public.anonbox_enqueue_push()
returns trigger
language plpgsql
security definer
set search_path to 'public', 'vault', 'net'
as $function$
declare
  hook_secret text;
  request_id bigint;
begin
  if new.direction <> 'visitor' then
    return new;
  end if;

  if exists (
    select 1
    from public.anonbox_conversation_preferences p
    join public.anonbox_boxes b on b.owner_id = p.owner_id
    where p.conversation_id = new.conversation_id
      and b.id = new.box_id
      and p.muted_until is not null
      and p.muted_until > now()
  ) then
    return new;
  end if;

  select decrypted_secret
  into hook_secret
  from vault.decrypted_secrets
  where name = 'anonbox_push_hook_secret'
  limit 1;

  if hook_secret is null or hook_secret = '' then
    return new;
  end if;

  select net.http_post(
    url := 'https://ugyrgvbfwvmuhsjmjtue.supabase.co/functions/v1/anonbox-push',
    headers := jsonb_build_object(
      'Content-Type', 'application/json',
      'x-anonbox-hook-secret', hook_secret
    ),
    body := jsonb_build_object('message_id', new.id::text)
  ) into request_id;

  return new;
exception when others then
  return new;
end;
$function$;
