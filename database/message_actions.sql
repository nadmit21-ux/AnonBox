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

-- The production migration also replaces anonbox_submit_message and anonbox_reply
-- with compatible signatures that accept an optional p_reply_to_id argument,
-- creates anonbox_delete_message and anonbox_toggle_reaction, extends the
-- Realtime update trigger to reactions/deletions, and includes reply/reaction
-- metadata in anonbox_get_library.
