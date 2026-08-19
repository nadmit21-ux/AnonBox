do $$
begin
  if not exists (select 1 from vault.secrets where name = 'anonbox_push_hook_secret') then
    perform vault.create_secret(
      replace(gen_random_uuid()::text, '-', '') || replace(gen_random_uuid()::text, '-', ''),
      'anonbox_push_hook_secret',
      'Secret interne pour authentifier le trigger push AnonBox vers Edge Function'
    );
  end if;
end
$$;

create or replace function public.anonbox_internal_push_config()
returns jsonb
language sql
security definer
set search_path = public, vault
as $$
  select jsonb_build_object(
    'hook_secret', (select decrypted_secret from vault.decrypted_secrets where name = 'anonbox_push_hook_secret' limit 1),
    'firebase_service_account', (select decrypted_secret from vault.decrypted_secrets where name = 'anonbox_firebase_service_account' limit 1)
  );
$$;

revoke all on function public.anonbox_internal_push_config() from public;
revoke all on function public.anonbox_internal_push_config() from anon;
revoke all on function public.anonbox_internal_push_config() from authenticated;
grant execute on function public.anonbox_internal_push_config() to service_role;

create or replace function public.anonbox_enqueue_push()
returns trigger
language plpgsql
security definer
set search_path = public, vault, net
as $$
declare
  hook_secret text;
  request_id bigint;
begin
  if new.direction <> 'visitor' then
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
$$;

revoke all on function public.anonbox_enqueue_push() from public;
revoke all on function public.anonbox_enqueue_push() from anon;
revoke all on function public.anonbox_enqueue_push() from authenticated;

drop trigger if exists anonbox_push_after_insert on public.anonbox_messages_v2;
create trigger anonbox_push_after_insert
after insert on public.anonbox_messages_v2
for each row
when (new.direction = 'visitor')
execute function public.anonbox_enqueue_push();