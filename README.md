# IyaBolaji Restaurant website

Website for IyaBolaji Restaurant, 3rd Ave Rd, Ipaja, Lagos. Plain HTML, CSS and JavaScript: no build step, no framework.

The four pages share the same header, footer and bag markup, so a change to one of those needs making in all four files.

## Preview it

Serve the folder (opening the files directly also works, but the map and page transitions need a server):

```bash
python3 -m http.server 8000
```

Then visit http://localhost:8000.

## What's where

| Path | What it is |
|------|------------|
| `index.html` | Home page: hero, craving picker, menu carousel, "why it tastes like home", weekly drop |
| `menu.html` | Full menu by category, built from `js/data.js` |
| `about.html` | Our story |
| `visit.html` | Find us: address, hours, how to order, map, allergens |
| `css/styles.css` | All styling. Colours and fonts are tokens at the top (`--red`, `--cream`, `--ink`, ...) |
| `js/data.js` | **Menu, prices, cravings, WhatsApp/phone numbers.** Edit this first. |
| `js/main.js` | Behaviour: animations, craving picker, menu, bag, drop countdown, scratch card, sizzle sound |
| `assets/art/` | Illustrated dish placeholders: SVG sources from `tools/make_art.py`, WebP copies used by the site |
| `assets/brand/` | Logo exports (red, cream, black and transparent backgrounds) |
| `assets/patterns/` | The doodle background tiles |

## Animations

Text and pictures animate in once as they scroll into view, and the home page has a short intro on load. It is all CSS (only movement and fades, nothing that makes phones redraw), started by small class changes in `js/main.js`; no animation library is loaded. Visitors whose phone is set to reduce motion get the page without animation.

Mark an element with `data-reveal` (or `data-reveal="left"`, `"right"`, `"pop"`) to fade it in, `data-split` on a heading to bring it in word by word, and `style="--d: .2s"` to delay it.

## Common edits

**Prices and dishes**: change the `dishes` list in `js/data.js` (it mirrors the Chowdeck menu). Each dish has a name, category, badge, price (naira), description and 0–5 ratings for heat, "belle full" and napkins. A dish with `price: null` stays in the file but is hidden on the site until it has a price.

**Real food photos**: put the photo in `assets/img/` (create the folder), then in `js/data.js` set the dish's `img` to that path and add `photo: true`. Photos get a round enamel-plate frame to match the illustrations. The big hero plate, the "why" photo and the drop photo are set directly in `index.html`.

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

## Link previews

Each page has its own preview image (`assets/og/*.jpg`, 1200x630) plus title and description tags, so shared links show a card on WhatsApp, iMessage, Facebook and X. Rebuild the images after changing prices or photos:

```bash
node tools/export_og.js
```

The tags use the full address `https://iyabolaji.vercel.app`. If the site moves to its own domain, replace that address in the `<head>` of all four pages.

## Publishing

Any static host works. On GitHub: Settings → Pages → deploy from this branch, folder `/ (root)`.

## Credits

Fonts from Google Fonts: Modak (wordmark), Bagel Fat One (accents), Archivo Expanded (headlines) and DM Sans (body). Layout inspired by a fast-food concept shot by Instaquirk on Dribbble.
