grant select on public.anonbox_messages_v2 to service_role;
grant select on public.anonbox_boxes to service_role;
grant select, update on public.anonbox_push_tokens to service_role;
grant select, insert, update, delete on public.anonbox_push_deliveries to service_role;
