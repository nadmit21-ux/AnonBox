-- Enable owner-side live message updates through Supabase Realtime.
-- RLS on public.anonbox_messages_v2 remains authoritative for visibility.
do $$
begin
  if not exists (
    select 1
    from pg_publication_tables
    where pubname = 'supabase_realtime'
      and schemaname = 'public'
      and tablename = 'anonbox_messages_v2'
  ) then
    alter publication supabase_realtime add table public.anonbox_messages_v2;
  end if;
end
$$;
