-- Hakka Legend voice-agent schema
-- Run this in Supabase SQL Editor (or `supabase db execute`).
-- The app auto-switches to Supabase when SUPABASE_URL + SUPABASE_SERVICE_KEY are set.

create table if not exists menu (
  id            text primary key,
  name          text not null,
  category      text not null,
  price         numeric(10,2) not null default 0,
  options       jsonb default '[]'::jsonb,
  option_prices jsonb default '{}'::jsonb,
  created_at    timestamptz default now()
);

create table if not exists orders (
  order_id      text primary key,
  customer_name text not null,
  phone         text not null,
  items         jsonb not null default '[]'::jsonb,
  total         numeric(10,2) not null default 0,
  status        text not null default 'created',
  payment_link  text,
  created_at    timestamptz default now()
);

create table if not exists reservations (
  reservation_id text primary key,
  customer_name  text not null,
  phone          text not null,
  party_size     int not null default 1,
  date           text not null,
  time           text not null,
  status         text not null default 'confirmed',
  created_at     timestamptz default now()
);

create index if not exists idx_orders_created on orders (created_at desc);
create index if not exists idx_res_created on reservations (created_at desc);
create index if not exists idx_menu_category on menu (category);

-- Row Level Security: the app uses the service_role key (bypasses RLS), so we
-- leave RLS off. If you later expose the anon key to a browser, enable RLS and
-- add policies. For the MVP, keep this as-is.
