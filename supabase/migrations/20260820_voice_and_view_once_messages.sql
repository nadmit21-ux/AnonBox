alter table public.anonbox_messages_v2
  add column if not exists view_once boolean not null default false,
  add column if not exists view_once_opened_at timestamptz,
  add column if not exists voice_duration_ms integer;

alter table public.anonbox_messages_v2
  drop constraint if exists anonbox_messages_v2_voice_duration_check;
alter table public.anonbox_messages_v2
  add constraint anonbox_messages_v2_voice_duration_check
  check (voice_duration_ms is null or (voice_duration_ms >= 0 and voice_duration_ms <= 300000));

create table if not exists public.anonbox_view_once_payloads (
  message_id bigint primary key references public.anonbox_messages_v2(id) on delete cascade,
  body text,
  attachment_id uuid,
  attachment_name text,
  attachment_mime text,
  attachment_size bigint,
  attachment_path text,
  voice_duration_ms integer,
  created_at timestamptz not null default now(),
  opened_at timestamptz,
  opened_by text
);

alter table public.anonbox_view_once_payloads enable row level security;
revoke all on table public.anonbox_view_once_payloads from public, anon, authenticated;
grant select, insert, update, delete on table public.anonbox_view_once_payloads to service_role;

alter table public.anonbox_view_once_payloads
  drop constraint if exists anonbox_view_once_payloads_voice_duration_check;
alter table public.anonbox_view_once_payloads
  add constraint anonbox_view_once_payloads_voice_duration_check
  check (voice_duration_ms is null or (voice_duration_ms >= 0 and voice_duration_ms <= 300000));

-- anonbox_submit_message and anonbox_reply were upgraded in production to accept
-- p_view_once boolean. When enabled, the normal message row stores only a
-- placeholder while the real content is written to anonbox_view_once_payloads.
-- anonbox_get_library now returns view_once, view_once_opened_at and
-- voice_duration_ms. anonbox_realtime_message_update also broadcasts changes to
-- view_once_opened_at.
