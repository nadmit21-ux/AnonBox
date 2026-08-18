-- AnonBox push notification infrastructure
-- Applied to Supabase project ugyrgvbfwvmuhsjmjtue.

create extension if not exists pg_net with schema extensions;

create table if not exists public.anonbox_push_deliveries (
  message_id bigint primary key references public.anonbox_messages_v2(id) on delete cascade,
  created_at timestamptz not null default now(),
  sent_at timestamptz,
  delivered_count integer not null default 0 check (delivered_count >= 0),
  last_error text
);

alter table public.anonbox_push_deliveries enable row level security;
revoke all on public.anonbox_push_deliveries from anon, authenticated;

comment on table public.anonbox_push_deliveries is
  'Internal idempotency log for AnonBox FCM notification delivery.';

-- The automatic pg_net trigger is intentionally installed only after
-- FIREBASE_SERVICE_ACCOUNT_JSON has been configured as a Supabase Edge Function secret.
