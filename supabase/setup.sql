-- IyaBolaji Restaurant: database setup for Supabase.
-- Paste the whole file into Supabase → SQL Editor → New query, then Run.
-- It is safe to run again: existing tables and dishes are left as they are.
--
-- What the public website (the anon key) can do:
--   * read visible dishes
--   * place an order through place_order() (prices are looked up here, so
--     nobody can change them in the browser)
--   * send a job application
-- Everything else (orders, applications, editing the menu, uploading photos)
-- needs a signed-in user listed in admin_users.

-- Admins ---------------------------------------------------------------------

create table if not exists public.admin_users (
  user_id uuid primary key references auth.users (id) on delete cascade,
  created_at timestamptz not null default now()
);
-- No policies: the website can never read or change who is an admin.
alter table public.admin_users enable row level security;

create or replace function public.is_admin()
returns boolean
language sql
stable
security definer
set search_path = public
as $$
  select exists (select 1 from public.admin_users where user_id = auth.uid());
$$;

revoke all on function public.is_admin() from public;
grant execute on function public.is_admin() to anon, authenticated;

create or replace function public.touch_updated_at()
returns trigger
language plpgsql
as $$
begin
  new.updated_at := now();
  return new;
end;
$$;

-- Menu -----------------------------------------------------------------------

create table if not exists public.dishes (
  id text primary key check (id ~ '^[a-z0-9-]{1,60}$'),
  name text not null check (char_length(name) between 1 and 80),
  cat text not null check (cat in ('rice', 'swallow', 'protein', 'sides')),
  badge text not null default '' check (char_length(badge) <= 24),
  price integer check (price >= 0),                 -- naira; empty hides the dish
  description text not null default '' check (char_length(description) <= 300),
  alt text not null default '' check (char_length(alt) <= 200),
  img text not null default '' check (char_length(img) <= 500),
  photo boolean not null default false,             -- true for real photos
  heat smallint not null default 0 check (heat between 0 and 5),
  fullness smallint not null default 0 check (fullness between 0 and 5),
  napkins smallint not null default 0 check (napkins between 0 and 5),
  serves text not null default '' check (char_length(serves) <= 30),
  available boolean not null default true,          -- false = sold out today
  visible boolean not null default true,            -- false = hidden from the site
  sort integer not null default 0,
  updated_at timestamptz not null default now()
);

drop trigger if exists dishes_touch on public.dishes;
create trigger dishes_touch before update on public.dishes
  for each row execute function public.touch_updated_at();

alter table public.dishes enable row level security;

drop policy if exists "Anyone can read visible dishes" on public.dishes;
create policy "Anyone can read visible dishes" on public.dishes
  for select to anon, authenticated
  using (visible or public.is_admin());

drop policy if exists "Admins add dishes" on public.dishes;
create policy "Admins add dishes" on public.dishes
  for insert to authenticated
  with check (public.is_admin());

drop policy if exists "Admins edit dishes" on public.dishes;
create policy "Admins edit dishes" on public.dishes
  for update to authenticated
  using (public.is_admin())
  with check (public.is_admin());

drop policy if exists "Admins delete dishes" on public.dishes;
create policy "Admins delete dishes" on public.dishes
  for delete to authenticated
  using (public.is_admin());

grant select on public.dishes to anon, authenticated;
grant insert, update, delete on public.dishes to authenticated;

-- Orders ---------------------------------------------------------------------

create table if not exists public.orders (
  id bigint generated always as identity (start with 1001) primary key,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  status text not null default 'new'
    check (status in ('new', 'preparing', 'ready', 'completed', 'cancelled')),
  customer_name text not null check (char_length(customer_name) between 1 and 80),
  phone text not null check (char_length(phone) between 7 and 20),
  order_type text not null check (order_type in ('pickup', 'dine-in', 'delivery')),
  address text check (char_length(address) <= 300),
  note text check (char_length(note) <= 500),
  items jsonb not null,                             -- [{id, name, price, qty}]
  total integer not null check (total >= 0)
);

drop trigger if exists orders_touch on public.orders;
create trigger orders_touch before update on public.orders
  for each row execute function public.touch_updated_at();

alter table public.orders enable row level security;

drop policy if exists "Admins read orders" on public.orders;
create policy "Admins read orders" on public.orders
  for select to authenticated
  using (public.is_admin());

drop policy if exists "Admins update orders" on public.orders;
create policy "Admins update orders" on public.orders
  for update to authenticated
  using (public.is_admin())
  with check (public.is_admin());

drop policy if exists "Admins delete orders" on public.orders;
create policy "Admins delete orders" on public.orders
  for delete to authenticated
  using (public.is_admin());

grant select, update, delete on public.orders to authenticated;

-- The website places orders only through this function. It looks every dish
-- up again, so prices and availability always come from the database.
create or replace function public.place_order(
  p_name text,
  p_phone text,
  p_type text,
  p_address text,
  p_note text,
  p_items jsonb
)
returns jsonb
language plpgsql
security definer
set search_path = public
as $$
declare
  v_items jsonb := '[]'::jsonb;
  v_total integer := 0;
  v_line record;
  v_id bigint;
begin
  if p_items is null or jsonb_typeof(p_items) <> 'array'
     or jsonb_array_length(p_items) = 0 or jsonb_array_length(p_items) > 40 then
    raise exception 'Your bag is empty.';
  end if;
  if coalesce(trim(p_name), '') = '' then
    raise exception 'Please add your name.';
  end if;
  if char_length(regexp_replace(coalesce(p_phone, ''), '[^0-9]', '', 'g')) < 7 then
    raise exception 'Please add a phone number we can call.';
  end if;
  if p_type = 'delivery' and coalesce(trim(p_address), '') = '' then
    raise exception 'Please add a delivery address.';
  end if;

  for v_line in
    select d.id, d.name, d.price,
           least(greatest(coalesce((i ->> 'qty')::int, 1), 1), 50) as qty
    from jsonb_array_elements(p_items) as i
    join public.dishes d on d.id = i ->> 'id'
    where d.visible and d.available and d.price is not null
  loop
    v_items := v_items || jsonb_build_object(
      'id', v_line.id, 'name', v_line.name, 'price', v_line.price, 'qty', v_line.qty);
    v_total := v_total + v_line.price * v_line.qty;
  end loop;

  if jsonb_array_length(v_items) = 0 then
    raise exception 'Sorry, nothing in your bag is available right now.';
  end if;

  insert into public.orders (customer_name, phone, order_type, address, note, items, total)
  values (trim(p_name), trim(p_phone), p_type, nullif(trim(p_address), ''),
          nullif(trim(p_note), ''), v_items, v_total)
  returning id into v_id;

  return jsonb_build_object('id', v_id, 'total', v_total, 'items', v_items);
end;
$$;

revoke all on function public.place_order(text, text, text, text, text, jsonb) from public;
grant execute on function public.place_order(text, text, text, text, text, jsonb) to anon, authenticated;

-- Job applications -------------------------------------------------------------

create table if not exists public.applications (
  id bigint generated always as identity primary key,
  created_at timestamptz not null default now(),
  status text not null default 'new'
    check (status in ('new', 'contacted', 'hired', 'declined')),
  full_name text not null check (char_length(full_name) between 2 and 80),
  phone text not null check (char_length(phone) between 7 and 20),
  email text check (char_length(email) <= 120),
  role text not null check (char_length(role) between 2 and 40),
  experience text check (char_length(experience) <= 40),
  specialties text check (char_length(specialties) <= 300),
  availability text check (char_length(availability) <= 40),
  message text check (char_length(message) <= 1000)
);

alter table public.applications enable row level security;

drop policy if exists "Anyone can apply" on public.applications;
create policy "Anyone can apply" on public.applications
  for insert to anon, authenticated
  with check (status = 'new');

drop policy if exists "Admins read applications" on public.applications;
create policy "Admins read applications" on public.applications
  for select to authenticated
  using (public.is_admin());

drop policy if exists "Admins update applications" on public.applications;
create policy "Admins update applications" on public.applications
  for update to authenticated
  using (public.is_admin())
  with check (public.is_admin());

drop policy if exists "Admins delete applications" on public.applications;
create policy "Admins delete applications" on public.applications
  for delete to authenticated
  using (public.is_admin());

grant insert on public.applications to anon, authenticated;
grant select, update, delete on public.applications to authenticated;

-- Food photos --------------------------------------------------------------------

-- Public bucket: anyone can view photos, only admins can upload or remove them.
insert into storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
values ('dish-photos', 'dish-photos', true, 5242880, array['image/jpeg', 'image/png', 'image/webp'])
on conflict (id) do nothing;

-- Uploading, replacing and removing files also needs read access to them.
drop policy if exists "Admins read dish photos" on storage.objects;
create policy "Admins read dish photos" on storage.objects
  for select to authenticated
  using (bucket_id = 'dish-photos' and public.is_admin());

drop policy if exists "Admins upload dish photos" on storage.objects;
create policy "Admins upload dish photos" on storage.objects
  for insert to authenticated
  with check (bucket_id = 'dish-photos' and public.is_admin());

drop policy if exists "Admins replace dish photos" on storage.objects;
create policy "Admins replace dish photos" on storage.objects
  for update to authenticated
  using (bucket_id = 'dish-photos' and public.is_admin());

drop policy if exists "Admins delete dish photos" on storage.objects;
create policy "Admins delete dish photos" on storage.objects
  for delete to authenticated
  using (bucket_id = 'dish-photos' and public.is_admin());

-- Live orders on the dashboard ------------------------------------------------------

do $$
begin
  if not exists (
    select 1 from pg_publication_tables
    where pubname = 'supabase_realtime' and schemaname = 'public' and tablename = 'orders'
  ) then
    alter publication supabase_realtime add table public.orders;
  end if;
end;
$$;

-- Starting menu (the current Chowdeck menu) ---------------------------------------------
-- Only added once: dishes that already exist are not overwritten.

insert into public.dishes (id, name, cat, badge, price, description, alt, img, photo, heat, fullness, napkins, serves, sort) values
  ('jollof-enjoyment', 'Jollof Enjoyment Combo', 'rice', 'Combo', 6000, 'Jollof rice, plantain, two pieces of beef and an egg.', 'Jollof rice with fried plantain, two pieces of beef and a boiled egg', 'assets/art/jollof-enjoyment.webp', false, 3, 5, 3, 'Combo', 10),
  ('royal-basmati', 'Royal Basmati Combo', 'rice', 'Combo', 6000, 'Basmati rice with two pieces of beef and plantain.', 'Basmati fried rice with two pieces of beef and fried plantain', 'assets/art/royal-basmati.webp', false, 2, 5, 3, 'Combo', 20),
  ('white-rice-special', 'White Rice Special', 'rice', 'Combo', 6000, 'White rice, plantain, one egg, one meat and one assorted meat.', 'White rice and stew with plantain, egg, beef and assorted meat', 'assets/art/white-rice-special.webp', false, 3, 5, 3, 'Combo', 30),
  ('ofada-special', 'Ofada Special Combo', 'rice', 'Combo', 6000, 'Ofada rice, egg, plantain and assorted meats.', 'Ofada rice with egg, fried plantain and assorted meats', 'assets/art/ofada-special.webp', false, 4, 5, 3, 'Combo', 40),
  ('chicken-chips', 'Chicken & Chips Delight', 'rice', 'Combo', 9000, 'Juicy fried chicken paired with crispy golden chips.', 'Fried chicken drumsticks with golden chips and ketchup', 'assets/art/chicken-chips.webp', false, 1, 4, 4, 'Combo', 50),
  ('basmati-fried-rice', 'Basmati Fried Rice', 'rice', '', 2000, 'Our special fried rice, made with basmati.', 'Basmati fried rice with peas and carrots', 'assets/art/basmati-fried-rice.webp', false, 1, 3, 1, 'Plate', 60),
  ('jollof-rice', 'Jollof Rice', 'rice', '', 800, 'Delicious jollof rice, served plain without protein.', 'Plate of jollof rice', 'assets/art/jollof-rice.webp', false, 2, 3, 1, 'Plate', 70),
  ('ofada-rice', 'Ofada', 'rice', '', 800, 'Native ofada rice.', 'Plate of native ofada rice', 'assets/art/ofada-rice.webp', false, 0, 3, 1, 'Plate', 80),
  ('stir-fry-spaghetti', 'Stir Fry Spaghetti', 'rice', '', 2000, 'Stir-fried spaghetti, peppers and all.', 'Stir-fried spaghetti with peppers and sausage', 'assets/art/stir-fry-spaghetti.webp', false, 2, 3, 2, 'Plate', 90),
  ('porridge', 'Yam Porridge', 'rice', '', 1000, 'Freshly prepared yam porridge.', 'Yam porridge in red pepper sauce with greens', 'assets/art/porridge.webp', false, 3, 4, 2, 'Plate', 100),
  ('amala-feast', 'Amala Swallow Feast', 'swallow', 'Combo', 5000, 'Amala (two wraps) served with ewedu, gbegiri and two pieces of meat.', 'Two wraps of amala with ewedu, gbegiri and meat', 'assets/art/amala-feast.webp', false, 3, 5, 2, 'Combo', 110),
  ('semo-combo', 'Semo Combo', 'swallow', 'Combo', 4000, 'Semo, efo riro, two pieces of meat and ponmo.', 'Semo with efo riro, two pieces of meat and ponmo', 'assets/art/semo-combo.webp', false, 3, 5, 2, 'Combo', 120),
  ('eba', 'Eba', 'swallow', '', 500, 'Soft, smooth and freshly prepared eba.', 'Wrap of eba', 'assets/art/eba.webp', false, 0, 4, 1, 'Swallow', 130),
  ('fufu', 'Fufu', 'swallow', '', 500, 'Our soft and stretchy fufu.', 'Wrap of fufu', 'assets/art/fufu.webp', false, 0, 4, 1, 'Swallow', 140),
  ('semo', 'Semo', 'swallow', '', 500, 'Soft, smooth and freshly prepared semo.', 'Wrap of semo', 'assets/art/semo.webp', false, 0, 4, 1, 'Swallow', 150),
  ('egusi', 'Egusi', 'swallow', 'Soup', 500, 'Flavourful egusi soup.', 'Egusi soup with greens and meat', 'assets/art/egusi.webp', false, 2, 3, 2, 'Soup', 160),
  ('efo-riro', 'Efo Riro', 'swallow', 'Soup', 500, 'Flavourful Yoruba vegetable soup.', 'Efo riro vegetable soup with meat and ponmo', 'assets/art/efo-riro.webp', false, 3, 3, 2, 'Soup', 170),
  ('turkey', 'Turkey', 'protein', '', 7000, 'Fried turkey.', 'Three fried turkey wings', 'assets/img/turkey.jpg', true, 2, 3, 5, 'Protein', 180),
  ('fried-chicken', 'Fried Chicken', 'protein', '', null, 'Golden, juicy chicken.', 'Fried chicken drumsticks', 'assets/art/fried-chicken.webp', false, 1, 3, 4, 'Protein', 190),
  ('bokoto', 'Bokoto', 'protein', 'Peppered', 4500, 'Peppered cow meat.', 'Peppered cow foot in red pepper sauce', 'assets/art/bokoto.webp', false, 5, 3, 5, 'Protein', 200),
  ('asun', 'Asun Goat Meat', 'protein', 'Peppered', 3500, 'Succulent pieces of goat meat, peppered asun style.', 'Peppered goat meat with onions and peppers', 'assets/art/asun.webp', false, 5, 3, 4, 'Protein', 210),
  ('croaker', 'Croaker Fish', 'protein', '', 3500, 'Well-seasoned croaker fish.', 'Whole croaker fish in pepper sauce', 'assets/art/croaker.webp', false, 3, 3, 4, 'Protein', 220),
  ('eja-kika', 'Eja Kika', 'protein', 'Peppered', 3000, 'Peppered eja kika.', 'Peppered fish in red pepper sauce', 'assets/art/eja-kika.webp', false, 4, 3, 4, 'Protein', 230),
  ('beef', 'Beef', 'protein', 'Peppered', 2000, 'Peppered meat.', 'Peppered beef with green peppers and onions', 'assets/art/beef.webp', false, 4, 2, 3, 'Protein', 240),
  ('assorted-meat', 'Assorted Meat', 'protein', '', 500, 'Shaki, liver and roundabout.', 'Shaki, liver and roundabout in pepper sauce', 'assets/art/assorted-meat.webp', false, 3, 2, 3, 'Protein', 250),
  ('ponmo', 'Ponmo', 'protein', 'Peppered', 500, 'Peppered ponmo.', 'Peppered ponmo in red pepper sauce', 'assets/art/ponmo.webp', false, 4, 1, 3, 'Protein', 260),
  ('plantain', 'Plantain', 'sides', 'Side', 1000, 'Sweet fried plantain, per portion.', 'Plate of sweet fried plantain', 'assets/art/plantain.webp', false, 0, 2, 2, 'Per portion', 270),
  ('salad', 'Salad', 'sides', 'Side', 1000, 'Fresh salad.', 'Fresh coleslaw with cabbage and carrots', 'assets/art/salad.webp', false, 0, 1, 1, 'Side', 280),
  ('moi-moi', 'Moimoi', 'sides', 'Side', 500, 'Soft, full-of-flavour moimoi.', 'Moimoi with boiled egg on a leaf', 'assets/art/moi-moi.webp', false, 2, 3, 1, 'Side', 290)
on conflict (id) do nothing;

-- Make yourself an admin ------------------------------------------------------------
-- 1. Supabase → Authentication → Users → Add user → Create new user
--    (your email and a strong password).
-- 2. Run this line with that email:
--
--    insert into public.admin_users (user_id)
--    select id from auth.users where email = 'you@example.com'
--    on conflict do nothing;
