alter table public.anonbox_messages_v2 drop constraint if exists anonbox_messages_v2_profile_consistency;

alter table public.anonbox_messages_v2 add constraint anonbox_messages_v2_profile_consistency check (
  (
    direction = 'visitor'
    and sender_mode = 'anonymous'
    and sender_user_id is null
  )
  or
  (
    direction = 'visitor'
    and sender_mode = 'profile'
    and sender_user_id is not null
    and sender_pseudonym_snapshot is not null
  )
  or
  (
    direction = 'owner'
    and sender_mode = 'owner'
    and sender_user_id is not null
    and sender_pseudonym_snapshot is not null
  )
);
