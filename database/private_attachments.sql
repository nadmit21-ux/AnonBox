-- AnonBox private message attachments v1

alter table public.anonbox_messages_v2
  add column if not exists attachment_id uuid null,
  add column if not exists attachment_name text null,
  add column if not exists attachment_mime text null,
  add column if not exists attachment_size bigint null,
  add column if not exists attachment_path text null;

create unique index if not exists anonbox_messages_attachment_id_uidx
  on public.anonbox_messages_v2(attachment_id) where attachment_id is not null;
create unique index if not exists anonbox_messages_attachment_path_uidx
  on public.anonbox_messages_v2(attachment_path) where attachment_path is not null;

insert into storage.buckets(id,name,public,file_size_limit,allowed_mime_types)
values(
  'anonbox-attachments','anonbox-attachments',false,10485760,
  array[
    'image/jpeg','image/png','image/webp','image/gif',
    'application/pdf','text/plain','application/zip',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'application/vnd.openxmlformats-officedocument.presentationml.presentation',
    'audio/mpeg','audio/mp4','video/mp4'
  ]::text[]
)
on conflict(id) do update set
  public=false,
  file_size_limit=excluded.file_size_limit,
  allowed_mime_types=excluded.allowed_mime_types;

grant select,insert on public.anonbox_messages_v2 to service_role;
grant select on public.anonbox_boxes to service_role;
grant select on public.anonbox_profiles to service_role;

-- anonbox_get_library is replaced in production to include attachment_id,
-- attachment_name, attachment_mime and attachment_size, while attachment_path
-- stays server-side only.
