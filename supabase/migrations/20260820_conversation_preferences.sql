-- AnonBox owner conversation preferences: pin, archive and mute.
create table if not exists public.anonbox_conversation_preferences (
  owner_id uuid not null references auth.users(id) on delete cascade,
  conversation_id uuid not null,
  pinned_at timestamptz null,
  archived_at timestamptz null,
  muted_until timestamptz null,
  updated_at timestamptz not null default now(),
  primary key (owner_id, conversation_id)
);

alter table public.anonbox_conversation_preferences enable row level security;
revoke all on public.anonbox_conversation_preferences from public, anon;
grant select, insert, update, delete on public.anonbox_conversation_preferences to authenticated;
grant select, insert, update, delete on public.anonbox_conversation_preferences to service_role;

drop policy if exists anonbox_conversation_preferences_select on public.anonbox_conversation_preferences;
create policy anonbox_conversation_preferences_select
on public.anonbox_conversation_preferences for select
to authenticated
using (owner_id = auth.uid());

drop policy if exists anonbox_conversation_preferences_insert on public.anonbox_conversation_preferences;
create policy anonbox_conversation_preferences_insert
on public.anonbox_conversation_preferences for insert
to authenticated
with check (
  owner_id = auth.uid()
  and exists (
    select 1
    from public.anonbox_messages_v2 m
    join public.anonbox_boxes b on b.id = m.box_id
    where m.conversation_id = anonbox_conversation_preferences.conversation_id
      and b.owner_id = auth.uid()
      and m.deleted_at is null
  )
);

drop policy if exists anonbox_conversation_preferences_update on public.anonbox_conversation_preferences;
create policy anonbox_conversation_preferences_update
on public.anonbox_conversation_preferences for update
to authenticated
using (owner_id = auth.uid())
with check (owner_id = auth.uid());

drop policy if exists anonbox_conversation_preferences_delete on public.anonbox_conversation_preferences;
create policy anonbox_conversation_preferences_delete
on public.anonbox_conversation_preferences for delete
to authenticated
using (owner_id = auth.uid());

create index if not exists anonbox_conversation_preferences_owner_idx
  on public.anonbox_conversation_preferences(owner_id, updated_at desc);
