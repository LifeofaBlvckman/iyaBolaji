# IyaBolaji Restaurant website

Website for IyaBolaji Restaurant, 3rd Ave Rd, Ipaja, Lagos. Plain HTML, CSS and JavaScript: no build step, no framework.

The five public pages share the same header, footer and bag markup, so a change to one of those needs making in all four files.

## Preview it

Serve the folder (opening the files directly also works, but the map and page transitions need a server). Locally the pages are at `/menu.html` etc.; on Vercel `vercel.json` gives them clean addresses like `/menu`:

```bash
python3 -m http.server 8000
```

Then visit http://localhost:8000.

## What's where

| Path | What it is |
|------|------------|
| `index.html` | Home page (`/`): hero, craving picker, menu carousel, "why it tastes like home", weekly drop |
| `menu.html` | `/menu`: full menu by category, built from `js/data.js` |
| `about.html` | `/about`: our story |
| `visit.html` | `/visit`: address, hours, how to order, map, FAQ, allergens |
| `careers.html` | `/careers`: we're hiring, open roles and the cook application form |
| `admin.html` | `/admin`: kitchen dashboard, orders, menu and photos, job applications (needs Supabase) |
| `js/config.js` | Supabase Project URL and anon key, shared by the site and the dashboard |
| `js/admin.js`, `css/admin.css` | The dashboard |
| `supabase/setup.sql` | Creates the database tables, security rules and photo storage |
| `vercel.json` | Clean addresses (`/menu`, not `/menu.html`) and a few response headers |
| `sitemap.xml`, `robots.txt`, `404.html` | For search engines, plus the "page not found" page |
| `css/styles.css` | All styling. Colours and fonts are tokens at the top (`--red`, `--cream`, `--ink`, ...) |
| `js/data.js` | Starting menu (used until Supabase is connected), cravings, plate-builder groups, WhatsApp/phone numbers |
| `js/main.js` | Behaviour: animations, craving picker, menu, bag, drop countdown, scratch card, sizzle sound |
| `assets/art/` | Illustrated dish placeholders: SVG sources from `tools/make_art.py`, WebP copies used by the site |
| `assets/brand/` | Logo exports (red, cream, black and transparent backgrounds) |
| `assets/patterns/` | The doodle background tiles |

## Supabase: orders, menu editing and job applications

Until Supabase is connected the site works on its own: the menu comes from `js/data.js` and the bag sends people to visit, call or WhatsApp. Once connected, the menu comes from the database, the bag has a real checkout, cook applications are saved, and the owner manages it all at `/admin`.

1. Create a free project at [supabase.com](https://supabase.com).
2. In the project open **SQL Editor → New query**, paste the whole of `supabase/setup.sql` and click **Run**. This creates the tables, the security rules, the `dish-photos` storage bucket, live order updates, and loads the current menu. Running it again is safe.
3. Create the admin login: **Authentication → Users → Add user → Create new user**, with the owner's email and a strong password (tick *Auto Confirm User*). Then run this in the SQL Editor with that email:

   ```sql
   insert into public.admin_users (user_id)
   select id from auth.users where email = 'owner@example.com'
   on conflict do nothing;
   ```

4. Turn off public sign-ups: **Authentication → Sign In / Providers → Allow new users to sign up** off. Admin accounts are only ever added by you.
5. Copy the **Project URL** and the **anon / publishable key** from **Project Settings → API** into `js/config.js`, then push. Never put the `service_role` / secret key in the site.
6. Open `https://iyabolaji.vercel.app/admin` and sign in.

What the public key can do is limited by the database itself: anyone can read the visible menu, place an order, and send an application. Only signed-in admins can see orders and applications, change the menu or upload photos. Order totals are worked out in the database from its own prices, so nobody can change a price in their browser.

**In the dashboard**: new orders appear instantly with a chime (keep the tab open; it also re-checks every 30 seconds). Move each order through *Start preparing → Mark ready → Complete*, or cancel it. In **Menu**, switch *In stock* off when a dish runs out today (it shows as "Sold out"), switch *On website* off to hide a dish, or tap **Edit** to change the name, price, description or photo. Photos are shrunk on the phone before uploading. **Hiring** lists cook applications with call and WhatsApp buttons.

The dashboard uses the official Supabase browser library, saved in `js/vendor/` (MIT licence) so it doesn't depend on another server.

## Animations

Text and pictures animate in once as they scroll into view, and the home page has a short intro on load. It is all CSS (only movement and fades, nothing that makes phones redraw), started by small class changes in `js/main.js`; no animation library is loaded. Visitors whose phone is set to reduce motion get the page without animation.

**Lottie animations**: put a LottieFiles link (`.json` or `.lottie`, from *Download & Handoff → CDN → Create asset link*) in `animations` in `js/data.js`. It plays in the "We're hiring cooks" band, beside the application form on `/careers`, and on the order confirmation. Any element with `data-lottie="cooking"` becomes another spot. The player (`js/vendor/lottie_light`, MIT licence) and the file load only when a spot is about to scroll into view, pause off screen, and stay still for visitors who prefer reduced motion. With no link, the spots stay hidden.

Mark an element with `data-reveal` (or `data-reveal="left"`, `"right"`, `"pop"`) to fade it in, `data-split` on a heading to bring it in word by word, and `style="--d: .2s"` to delay it.

## Common edits

**Prices and dishes**: once Supabase is connected, use the admin dashboard. Before that, change the `dishes` list in `js/data.js` (it mirrors the Chowdeck menu). Each dish has a name, category, badge, price (naira), description and 0–5 ratings for heat, "belle full" and napkins. A dish with `price: null` stays in the file but is hidden on the site until it has a price.

**Real food photos**: with Supabase, upload them in the dashboard. Without it, put the photo in `assets/img/` (create the folder), then in `js/data.js` set the dish's `img` to that path and add `photo: true`. Photos get a round enamel-plate frame to match the illustrations. The big hero plate, the "why" photo and the drop photo are set directly in `index.html`.

**WhatsApp ordering**: set `whatsapp` in `js/data.js` to the number in international format without `+` (e.g. `2348012345678`). The bag's checkout button then sends the whole order on WhatsApp. If you only set `phone`, it becomes a "Call to order" button.

**Email sign-up**: the form only shows a thank-you message until `signupEndpoint` is set (for example a Formspree or Mailchimp form URL).

**Weekly drop**: the countdown targets `drop` in `js/data.js` (Friday 18:00 Lagos time). The drop dish and the scratch-card deal text are in `index.html`.

## Regenerating art and logos

```bash
python3 tools/make_art.py
```

```bash
node tools/export_art.js
```

The second step turns the SVGs into the small WebP files the site loads.

```bash
node tools/export_logos.js
```

The logo export needs Playwright and an internet connection (it loads the Modak font from Google Fonts).

## Search engines (SEO)

Every public page has its own title and description, a canonical address, and structured data that Google reads: the restaurant (address, map position, cuisine, price range, menu link), the full menu with prices (kept in step with the dashboard when the page loads), breadcrumbs, an FAQ on `/visit`, and job postings on `/careers`. `sitemap.xml` lists the pages; `robots.txt` keeps `/admin` out of search.

To get indexed:

1. Open [Google Search Console](https://search.google.com/search-console), add a **URL prefix** property for `https://iyabolaji.vercel.app/`, and verify it with the **HTML tag** method: paste the `<meta name="google-site-verification" ...>` tag into the `<head>` of `index.html`.
2. In Search Console, go to **Sitemaps** and submit `sitemap.xml`.
3. Claim the restaurant on [Google Business Profile](https://business.google.com) and add the website link. For searches like "restaurant near me" or "amala in Ipaja", the Business Profile matters more than anything on the site.

When pages change a lot, update the `<lastmod>` dates in `sitemap.xml`. The FAQ on `/visit` quotes a few prices; update it if those change.

## Link previews

Each page has its own preview image (`assets/og/*.jpg`, 1200x630) plus title and description tags, so shared links show a card on WhatsApp, iMessage, Facebook and X. Rebuild the images after changing prices or photos:

```bash
node tools/export_og.js
```

The tags use the full address `https://iyabolaji.vercel.app`. If the site moves to its own domain, replace that address everywhere it appears: the `<head>` of every page, `sitemap.xml` and `robots.txt`.

## Publishing

Deployed on Vercel from the `main` branch (Framework preset: Other, no build command). `vercel.json` is picked up automatically.

## Credits

Made by blvckman with 💜.

Fonts from Google Fonts: Modak (wordmark), Bagel Fat One (accents), Archivo Expanded (headlines) and DM Sans (body). Layout inspired by a fast-food concept shot by Instaquirk on Dribbble.
