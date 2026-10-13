create table if not exists public.markdown (
    kind text not null check (kind in ('menus', 'about_region', 'tours')),
    name text not null,
    content text not null,
    updated_at timestamptz not null default now(),
    primary key (kind, name)
);

create table if not exists public.suggestions (
    id bigint generated always as identity primary key,
    created_at timestamptz not null default now(),
    user_id bigint not null,
    username text,
    region_name text,
    tour text
);

create table if not exists public.bug_reports (
    id bigint generated always as identity primary key,
    created_at timestamptz not null default now(),
    user_id bigint not null,
    username text,
    report text
);

alter table public.markdown enable row level security;
alter table public.suggestions enable row level security;
alter table public.bug_reports enable row level security;

grant select, insert, update, delete on public.markdown, public.suggestions, public.bug_reports to service_role;
grant usage, select on all sequences in schema public to service_role;

create table if not exists public.regions (
    id bigint generated always as identity primary key,
    slug text not null unique check (slug ~ '^[a-z0-9_]+$'),
    title text not null,
    position integer not null default 0
);

create table if not exists public.tours (
    id bigint generated always as identity primary key,
    region_id bigint not null references public.regions (id) on delete cascade,
    slug text not null check (slug ~ '^[a-z0-9_]+$'),
    title text not null,
    pages integer not null check (pages > 0),
    map_links jsonb not null default '{}'::jsonb,
    position integer not null default 0,
    unique (region_id, slug)
);

alter table public.regions enable row level security;
alter table public.tours enable row level security;

grant select, insert, update, delete on public.regions, public.tours to service_role;
grant usage, select on all sequences in schema public to service_role;

insert into storage.buckets (id, name, public)
values ('images', 'images', false)
on conflict (id) do nothing;
