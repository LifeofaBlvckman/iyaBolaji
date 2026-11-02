(() => {
  const D = window.IYA;
  const C = window.IYA_CONFIG || {};
  const $ = (sel, el = document) => el.querySelector(sel);
  const $$ = (sel, el = document) => [...el.querySelectorAll(sel)];
  const money = (n) => D.currency + Number(n).toLocaleString("en-NG");
  const icon = (id, cls = "") => `<svg class="${cls}" aria-hidden="true"><use href="#i-${id}"/></svg>`;
  const esc = (v) => String(v ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const reduceMotion = matchMedia("(prefers-reduced-motion: reduce)").matches;
  const root = document.documentElement;

  // Scroll reveals only hide things once this script is running, so the page
  // stays readable if it ever fails to load.
  root.classList.add("motion");

  const store = {
    get(key, fallback) {
      try { return JSON.parse(localStorage.getItem(key)) ?? fallback; } catch { return fallback; }
    },
    set(key, value) {
      try { localStorage.setItem(key, JSON.stringify(value)); } catch { /* private mode */ }
    },
  };

  /* Supabase ------------------------------------------------------------ */
  // Plain REST calls (no library) keep the public pages light. What the key
  // may do is decided by the rules in supabase/setup.sql.

  const hasDb = Boolean(C.supabaseUrl && C.supabaseKey);

  async function db(path, { method = "GET", body, headers = {}, timeout = 8000 } = {}) {
    const h = { apikey: C.supabaseKey, "Content-Type": "application/json", ...headers };
    // Legacy anon keys are JWTs and also go in Authorization; new publishable keys don't.
    if (C.supabaseKey.startsWith("eyJ")) h.Authorization = `Bearer ${C.supabaseKey}`;
    const ctrl = new AbortController();
    const timer = setTimeout(() => ctrl.abort(), timeout);
    try {
      const res = await fetch(`${C.supabaseUrl.replace(/\/+$/, "")}/rest/v1/${path}`, {
        method, headers: h, body: body ? JSON.stringify(body) : undefined, signal: ctrl.signal,
      });
      const text = await res.text();
      let data = null;
      try { data = text ? JSON.parse(text) : null; } catch { data = text; }
      if (!res.ok) throw new Error((data && data.message) || `Request failed (${res.status})`);
      return data;
    } catch (err) {
      if (err.name === "AbortError") throw new Error("The connection timed out. Please try again.");
      throw err;
    } finally {
      clearTimeout(timer);
    }
  }

  /* Motion -------------------------------------------------------------- */
  // JS only adds classes here; the animations are CSS moves and fades, and each
  // element animates once.

  function splitWords(el) {
    let i = 0;
    const walk = (node) => {
      for (const child of [...node.childNodes]) {
        if (child.nodeType === Node.TEXT_NODE) {
          const frag = document.createDocumentFragment();
          for (const part of child.textContent.split(/(\s+)/)) {
            if (!part) continue;
            if (/^\s+$/.test(part)) { frag.append(part); continue; }
            const w = document.createElement("span");
            const wi = document.createElement("span");
            w.className = "w";
            wi.className = "wi";
            wi.style.setProperty("--wi", i++);
            wi.textContent = part;
            w.append(wi);
            frag.append(w);
          }
          child.replaceWith(frag);
        } else if (child.nodeType === Node.ELEMENT_NODE && child.tagName !== "BR") {
          walk(child);
        }
      }
    };
    walk(el);
  }

  function splitChars(el) {
    // Letters of a word stay in one nowrap group so lines only break between words.
    let i = 0;
    el.innerHTML = el.textContent.trim().split(/\s+/).map((word) => `<span style="white-space: nowrap">${
      [...word].map((c) => `<span class="ch" style="--i: ${i++}">${esc(c)}</span>`).join("")
    }</span>`).join(" ");
  }

  function countText(el, n) {
    return (el.dataset.prefix || "") + Math.round(n).toLocaleString("en-NG") + (el.dataset.suffix || "");
  }

  function countUp(el) {
    if (el.dataset.counted || !el.dataset.count) return;
    el.dataset.counted = "1";
    const target = Number(el.dataset.count);
    if (reduceMotion) { el.textContent = countText(el, target); return; }
    const start = performance.now();
    const step = (now) => {
      const k = Math.min(1, (now - start) / 1400);
      el.textContent = countText(el, target * (1 - Math.pow(1 - k, 3)));
      if (k < 1) requestAnimationFrame(step);
    };
    requestAnimationFrame(step);
  }

  function show(el) {
    el.classList.add("is-in");
    if (el.dataset.count) countUp(el);
    $$("[data-count]", el).forEach(countUp);
  }

  let revealReady = false;
  const io = "IntersectionObserver" in window && !reduceMotion
    ? new IntersectionObserver((entries) => {
      for (const entry of entries) {
        if (!entry.isIntersecting) continue;
        show(entry.target);
        io.unobserve(entry.target);
      }
    }, { rootMargin: "0px 0px -8% 0px", threshold: 0.12 })
    : null;

  // Watch anything under `scope` that should animate in when scrolled to.
  function observe(scope = document) {
    if (!revealReady) return;
    for (const el of $$("[data-reveal], [data-split], [data-chars], [data-draw], [data-count]", scope)) {
      if (el.classList.contains("is-in")) continue;
      if (io) io.observe(el); else show(el);
    }
  }

  $$("[data-split]").forEach(splitWords);
  $$("[data-chars]").forEach(splitChars);
  if (!reduceMotion) $$("[data-count]").forEach((el) => { el.textContent = countText(el, 0); });

  // Looping animations (tickers, the floating plate) pause while off screen.
  if ("IntersectionObserver" in window) {
    const pauser = new IntersectionObserver((entries) => {
      for (const entry of entries) entry.target.classList.toggle("is-paused", !entry.isIntersecting);
    });
    $$(".ticker, .hero-visual, .page-hero-visual, .mood-badge").forEach((el) => pauser.observe(el));
  }

  /* Header turns to glass once the announcement bar scrolls away ------- */

  const header = $("#site-header");
  const announce = $(".announce");
  if (header && announce && "IntersectionObserver" in window) {
    new IntersectionObserver(([entry]) => header.classList.toggle("is-glass", !entry.isIntersecting)).observe(announce);
  }

  /* Toast -------------------------------------------------------------- */

  const toastEl = $("#toast");
  let toastTimer;
  function toast(message) {
    toastEl.textContent = message;
    toastEl.classList.add("is-on");
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => toastEl.classList.remove("is-on"), 2600);
  }

  /* Menu data ----------------------------------------------------------- */

  let dishes = [];
  let byId = {};

  const fromRow = (r) => ({
    id: r.id, name: r.name, cat: r.cat, badge: r.badge, price: r.price, desc: r.description,
    alt: r.alt, img: r.img, photo: r.photo, heat: r.heat, full: r.fullness, napkins: r.napkins,
    serves: r.serves, available: r.available,
  });

  async function loadMenu() {
    if (!hasDb) return D.dishes;
    try {
      const rows = await db("dishes?select=*&order=sort.asc,name.asc", { timeout: 5000 });
      if (Array.isArray(rows) && rows.length) {
        const list = rows.map(fromRow);
        store.set("iya-menu", list);
        return list;
      }
    } catch (err) {
      console.warn("Couldn't load the menu from Supabase, using the saved copy.", err);
    }
    return store.get("iya-menu", null) || D.dishes;
  }

  /* Bag and checkout ---------------------------------------------------- */

  let bag = store.get("iya-bag", {});
  const bagDialog = $("#bag");
  const bagCountEl = $("#bag-count");
  const views = { list: $("#bag-view"), checkout: $("#checkout"), done: $("#order-done") };
  const showView = (name) => { for (const [key, el] of Object.entries(views)) el.hidden = key !== name; };

  function bagLines() {
    return Object.entries(bag).filter(([id, q]) => q > 0 && byId[id]).map(([id, qty]) => ({ dish: byId[id], qty }));
  }

  function renderBag() {
    const lines = bagLines();
    const count = lines.reduce((sum, l) => sum + l.qty, 0);
    const total = lines.reduce((sum, l) => sum + l.qty * l.dish.price, 0);

    bagCountEl.textContent = count;
    $("#bag-open").setAttribute("aria-label", `Open bag, ${count} item${count === 1 ? "" : "s"}`);
    $("#bag-total").textContent = money(total);
    $("#checkout-total").textContent = money(total);
    $("#place-order").textContent = `Place order · ${money(total)}`;

    $("#bag-list").innerHTML = lines.length
      ? lines.map(({ dish, qty }) => `
        <li>
          <img src="${esc(dish.img)}" alt="" class="${dish.photo ? "is-photo" : ""}" width="64" height="64">
          <div><div class="bag-item-name">${esc(dish.name)}</div><div class="bag-item-price">${dish.available === false ? "Sold out today" : `${money(dish.price)} each`}</div></div>
          <div class="stepper">
            <button type="button" data-dec="${esc(dish.id)}" aria-label="Remove one ${esc(dish.name)}">${icon("minus")}</button>
            <output aria-label="${esc(dish.name)} quantity">${qty}</output>
            <button type="button" data-inc="${esc(dish.id)}" aria-label="Add one more ${esc(dish.name)}">${icon("plus")}</button>
          </div>
        </li>`).join("")
      : `<li class="bag-empty">Your bag is empty. Belle no go full like this.</li>`;

    const checkout = $("#bag-checkout");
    const note = $("#bag-note");
    checkout.removeAttribute("target");
    checkout.dataset.mode = "link";
    if (hasDb && lines.length) {
      checkout.href = "#checkout";
      checkout.dataset.mode = "checkout";
      checkout.textContent = "Checkout";
      note.textContent = "Pickup, delivery or dine-in. We'll call to confirm.";
    } else if (D.whatsapp && lines.length) {
      const text = ["Hello IyaBolaji, I'd like to order:", ...lines.map((l) => `${l.qty} x ${l.dish.name} (${money(l.qty * l.dish.price)})`), `Total: ${money(total)}`].join("\n");
      checkout.href = `https://wa.me/${D.whatsapp}?text=${encodeURIComponent(text)}`;
      checkout.target = "_blank";
      checkout.rel = "noopener";
      checkout.textContent = "Send order on WhatsApp";
      note.textContent = "We'll confirm your order and delivery time on WhatsApp.";
    } else if (D.phone) {
      checkout.href = `tel:${D.phone}`;
      checkout.textContent = "Call to order";
      note.textContent = "Read us your bag and we'll have it ready.";
    } else {
      checkout.href = "visit.html";
      checkout.textContent = "Visit us to order";
      note.textContent = "3rd Ave Rd, Ipaja. Dine-in, takeaway or delivery.";
    }
  }

  function saveBag() {
    store.set("iya-bag", bag);
    renderBag();
  }

  function bumpBag() {
    bagCountEl.classList.remove("is-bumped");
    void bagCountEl.offsetWidth;
    bagCountEl.classList.add("is-bumped");
  }

  function addToBag(id) {
    const d = byId[id];
    if (!d) return;
    if (d.available === false) { toast(`${d.name} is sold out today`); return; }
    bag[id] = (bag[id] || 0) + 1;
    saveBag();
    toast(`${d.name} added to your bag`);
    bumpBag();
  }

  function openBag() {
    showView("list");
    if (typeof bagDialog.showModal === "function") bagDialog.showModal();
    else bagDialog.setAttribute("open", "");
  }

  $("#bag-open").addEventListener("click", openBag);
  $$("[data-open-bag]").forEach((a) => a.addEventListener("click", (e) => { e.preventDefault(); openBag(); }));
  $("#bag-close").addEventListener("click", () => bagDialog.close());
  bagDialog.addEventListener("click", (e) => {
    if (e.target === bagDialog) bagDialog.close();
    const inc = e.target.closest("[data-inc]");
    const dec = e.target.closest("[data-dec]");
    if (inc) { bag[inc.dataset.inc] = (bag[inc.dataset.inc] || 0) + 1; saveBag(); }
    if (dec) {
      const id = dec.dataset.dec;
      bag[id] = (bag[id] || 0) - 1;
      if (bag[id] <= 0) delete bag[id];
      saveBag();
    }
  });

  const checkoutForm = views.checkout;
  const addressField = $("#address-field");
  const checkoutMsg = $("#checkout-msg");

  $("#bag-checkout").addEventListener("click", (e) => {
    if (e.currentTarget.dataset.mode !== "checkout") { bagDialog.close(); return; }
    e.preventDefault();
    const saved = store.get("iya-customer", {});
    for (const key of ["name", "phone", "address"]) {
      if (saved[key] && !checkoutForm.elements[key].value) checkoutForm.elements[key].value = saved[key];
    }
    checkoutMsg.textContent = "";
    showView("checkout");
    checkoutForm.elements.name.focus();
  });
  $("#checkout-back").addEventListener("click", () => showView("list"));
  $("#done-close").addEventListener("click", () => { bagDialog.close(); showView("list"); });
  checkoutForm.addEventListener("change", (e) => {
    if (e.target.name === "type") addressField.hidden = e.target.value !== "delivery";
  });
  checkoutForm.addEventListener("input", (e) => { e.target.removeAttribute("aria-invalid"); checkoutMsg.textContent = ""; });

  checkoutForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const f = new FormData(checkoutForm);
    const name = String(f.get("name") || "").trim();
    const phone = String(f.get("phone") || "").trim();
    const type = String(f.get("type") || "pickup");
    const address = String(f.get("address") || "").trim();
    const note = String(f.get("note") || "").trim();

    const problems = [];
    if (!name) problems.push(["name", "Please add your name."]);
    if (phone.replace(/\D/g, "").length < 7) problems.push(["phone", "Please add a phone number we can call."]);
    if (type === "delivery" && !address) problems.push(["address", "Please add a delivery address."]);
    for (const [field] of problems) checkoutForm.elements[field].setAttribute("aria-invalid", "true");
    if (problems.length) {
      checkoutMsg.textContent = problems[0][1];
      checkoutForm.elements[problems[0][0]].focus();
      return;
    }
    const lines = bagLines();
    if (!lines.length) { checkoutMsg.textContent = "Your bag is empty."; return; }

    const btn = $("#place-order");
    btn.disabled = true;
    btn.textContent = "Placing your order...";
    checkoutMsg.textContent = "";
    try {
      const order = await db("rpc/place_order", {
        method: "POST",
        body: {
          p_name: name, p_phone: phone, p_type: type, p_address: address, p_note: note,
          p_items: lines.map((l) => ({ id: l.dish.id, qty: l.qty })),
        },
      });
      const placed = new Set(order.items.map((i) => i.id));
      const dropped = lines.filter((l) => !placed.has(l.dish.id)).map((l) => l.dish.name);
      bag = {};
      saveBag();
      store.set("iya-customer", { name, phone, address });

      $("#done-title").textContent = `Order #${order.id} is in!`;
      $("#done-text").textContent = `We'll call ${phone} to confirm${type === "delivery" ? " your delivery and the delivery fee" : ""}.`
        + (dropped.length ? ` ${dropped.join(", ")} sold out just now, so we left ${dropped.length > 1 ? "them" : "it"} out.` : "");
      $("#done-items").innerHTML = order.items.map((i) => `<li><span>${i.qty} × ${esc(i.name)}</span><span>${money(i.price * i.qty)}</span></li>`).join("")
        + `<li><strong>Total</strong><strong>${money(order.total)}</strong></li>`;
      checkoutForm.elements.note.value = "";
      showView("done");
      $("#done-close").focus();
    } catch (err) {
      checkoutMsg.textContent = err.message || "We couldn't place your order. Please try again or call us.";
    } finally {
      btn.disabled = false;
      renderBag();
    }
  });

  document.addEventListener("click", (e) => {
    const add = e.target.closest("[data-add]");
    if (add) addToBag(add.dataset.add);
  });

  /* Dish cards (home carousel and menu page) ---------------------------- */

  const tones = ["red", "white", "ink", "white"];
  const tilts = [-4, 3, -2, 5];

  function cardHTML(d, i) {
    const out = d.available === false;
    return `
      <li class="card card--${tones[i % 4]}${out ? " is-soldout" : ""}" style="--tilt: ${tilts[i % 4]}deg; --d: ${(i % 4) * 0.08}s" data-reveal>
        ${d.badge ? `<span class="card-badge">${esc(d.badge)}</span>` : ""}
        ${out ? `<span class="soldout-tag">Sold out</span>` : ""}
        <img src="${esc(d.img)}" alt="${esc(d.alt)}" width="560" height="560" loading="lazy" decoding="async" class="${d.photo ? "is-photo" : ""}">
        <h3>${esc(d.name)}</h3>
        <p>${esc(d.desc)}</p>
        <div class="card-foot">
          <span class="card-price">${money(d.price)}</span>
          <button class="add-btn" type="button" data-add="${esc(d.id)}" aria-label="${out ? `${esc(d.name)} is sold out today` : `Add ${esc(d.name)} to bag`}"${out ? " disabled" : ""}>${icon("plus")}</button>
        </div>
      </li>`;
  }

  /* Cravings (home) ----------------------------------------------------- */

  function initCravings() {
    const chipsEl = $("#craving-chips");
    if (!chipsEl) return;
    const cravings = D.cravings.filter((c) => byId[c.dish]);
    if (!cravings.length) return;
    const featureImg = $("#feature-img");
    let featured = cravings[0].dish;

    chipsEl.innerHTML = cravings.map((c, i) => `
      <button class="chip" type="button" aria-pressed="${i === 0}" data-dish="${esc(c.dish)}">${icon("spark")}${esc(c.label)}</button>`).join("");

    const meter = (kind, value, label) => {
      const marks = Array.from({ length: 5 }, (_, i) => {
        const inner = kind === "heat" ? icon("chili") : kind === "napkins" ? icon("napkin") : "";
        return `<span class="m-${kind}${i < value ? "" : " off"}">${inner}</span>`;
      }).join("");
      return `<span class="sr-only">${label}: ${value} out of 5</span><span aria-hidden="true" style="display:contents">${marks}</span>`;
    };

    const showFeature = (id, animate = true) => {
      const d = byId[id];
      const out = d.available === false;
      featured = id;
      $("#feature-name").textContent = d.name;
      $("#feature-desc").textContent = d.desc;
      $("#feature-price").textContent = money(d.price);
      $("#feature-serves").textContent = out ? "Sold out today" : d.serves;
      $("#meter-heat").innerHTML = meter("heat", d.heat, "Heat");
      $("#meter-full").innerHTML = meter("full", d.full, "Belle full");
      $("#meter-napkins").innerHTML = meter("napkins", d.napkins, "Napkins needed");
      const addBtn = $("#feature-add");
      addBtn.disabled = out;
      addBtn.setAttribute("aria-label", out ? `${d.name} is sold out today` : `Add ${d.name} to bag`);
      $(".feature-visual").classList.toggle("is-soldout", out);

      const swap = () => {
        featureImg.src = d.img;
        featureImg.alt = d.alt;
        featureImg.classList.toggle("is-photo", !!d.photo);
        featureImg.classList.remove("is-swapping");
      };
      if (!animate || reduceMotion) return swap();
      featureImg.classList.add("is-swapping");
      setTimeout(swap, 200);
    };

    chipsEl.addEventListener("click", (e) => {
      const chip = e.target.closest(".chip");
      if (!chip) return;
      $$(".chip", chipsEl).forEach((c) => c.setAttribute("aria-pressed", String(c === chip)));
      showFeature(chip.dataset.dish);
    });
    $("#feature-add").addEventListener("click", () => addToBag(featured));
    showFeature(featured, false);
  }

  /* Menu carousel (home) ------------------------------------------------ */

  function initCarousel() {
    const cardsEl = $("#cards");
    if (!cardsEl) return;
    const filtersEl = $("#menu-filters");
    filtersEl.innerHTML = D.filters.map((f, i) => `
      <button class="chip" type="button" aria-pressed="${i === 0}" data-filter="${esc(f.id)}">${esc(f.label)}</button>`).join("");

    const renderCards = (filter) => {
      cardsEl.innerHTML = dishes.filter((d) => filter === "all" || d.cat === filter).map(cardHTML).join("");
      cardsEl.scrollTo({ left: 0 });
      observe(cardsEl);
    };

    filtersEl.addEventListener("click", (e) => {
      const chip = e.target.closest(".chip");
      if (!chip) return;
      $$(".chip", filtersEl).forEach((c) => c.setAttribute("aria-pressed", String(c === chip)));
      renderCards(chip.dataset.filter);
    });
    $$("[data-scroll]").forEach((btn) => btn.addEventListener("click", () => {
      const card = $(".card", cardsEl);
      const step = card ? card.offsetWidth + 28 : 320;
      cardsEl.scrollBy({ left: step * Number(btn.dataset.scroll), behavior: reduceMotion ? "auto" : "smooth" });
    }));
    renderCards("all");
  }

  /* Full menu page ------------------------------------------------------ */

  function initMenuPage() {
    const menuPage = $("#menu-page");
    if (!menuPage) return;
    const cats = D.filters.filter((f) => f.id !== "all");
    menuPage.innerHTML = cats.map((c, ci) => {
      const list = dishes.filter((d) => d.cat === c.id);
      return `
        <section class="menu-cat ${ci % 2 ? "bg-peach" : "bg-cream"}" id="${esc(c.id)}" aria-labelledby="cat-${esc(c.id)}">
          <div class="container">
            <div class="menu-cat-head">
              <div>
                <span class="count-pill" data-reveal="pop">${list.length} dishes</span>
                <h2 class="display" id="cat-${esc(c.id)}" data-split>${esc(c.label)}</h2>
              </div>
              <p data-reveal style="--d: .2s">${esc(c.blurb || "")}</p>
            </div>
            <ul class="menu-grid">${list.map(cardHTML).join("")}</ul>
          </div>
        </section>`;
    }).join("");
    $$("[data-split]", menuPage).forEach(splitWords);

    const tabs = $("#menu-tabs");
    tabs.innerHTML = cats.map((c) => `<a class="chip" href="#${esc(c.id)}">${esc(c.label)}</a>`).join("");
    if ("IntersectionObserver" in window) {
      const spy = new IntersectionObserver((entries) => {
        for (const entry of entries) {
          if (!entry.isIntersecting) continue;
          for (const tab of $$("a", tabs)) {
            const on = tab.getAttribute("href") === `#${entry.target.id}`;
            tab.setAttribute("aria-current", String(on));
            if (on) tabs.scrollTo({ left: tab.offsetLeft - 16, behavior: reduceMotion ? "auto" : "smooth" });
          }
        }
      }, { rootMargin: "-40% 0px -55% 0px" });
      $$(".menu-cat", menuPage).forEach((s) => spy.observe(s));
    }
    // The page may have been opened at #rice etc. before the sections existed.
    if (location.hash && $(location.hash)) $(location.hash).scrollIntoView();
  }

  /* Build your plate (home) --------------------------------------------- */

  function initBuilder() {
    const listEl = $("#builder-list");
    if (!listEl) return;
    const tabsEl = $("#builder-tabs");
    const plateEl = $("#builder-plate");
    const max = D.builderMax || 8;
    const groups = (D.builder || [])
      .map((g) => ({ label: g.label, items: g.ids.map((id) => byId[id]).filter(Boolean) }))
      .filter((g) => g.items.length);
    if (!groups.length) return;
    // Where scoops land on the plate, as % of the plate (centre first).
    const slots = [[50, 50], [31, 37], [68, 35], [34, 67], [66, 66], [50, 25], [25, 53], [75, 52]];
    let plate = [];
    let active = 0;

    $("#receipt-no").textContent = `Plate P-${Math.floor(1000 + Math.random() * 9000)}`;
    tabsEl.innerHTML = groups.map((g, i) => `<button class="chip" type="button" aria-pressed="${i === 0}" data-group="${i}">${esc(g.label)}</button>`).join("");

    const renderList = () => {
      listEl.innerHTML = groups[active].items.map((d) => {
        const out = d.available === false;
        return `<li><button class="pick" type="button" data-pick="${esc(d.id)}"${out ? " disabled" : ""} aria-label="Add ${esc(d.name)} to the plate, ${money(d.price)}${out ? ", sold out today" : ""}">
          <img src="${esc(d.img)}" alt="" width="58" height="58" loading="lazy" class="${d.photo ? "is-photo" : ""}">
          <span><span class="pick-name">${esc(d.name)}</span><span class="pick-meta">${out ? "Sold out today" : `Heat ${d.heat}/5 · Belle ${d.full}/5`}</span></span>
          <span class="pick-price">+${money(d.price)}</span>
        </button></li>`;
      }).join("");
    };

    const plateName = () => {
      const has = (...ids) => ids.some((id) => plate.includes(id));
      const protein = plate.some((id) => byId[id].cat === "protein");
      const swallow = has("eba", "fufu", "semo");
      const soup = has("egusi", "efo-riro");
      const rice = has("jollof-rice", "ofada-rice", "basmati-fried-rice");
      if (!plate.length) return "Start tapping...";
      if (plate.length < 3) return "Keep going...";
      if (plate.length >= max) return "Belle Full Deluxe. Respect.";
      if (swallow && soup && protein) return "Mama's Swallow Special";
      if (rice && protein && has("plantain")) return "The Ipaja Party Plate";
      if (has("asun", "bokoto")) return "Pepper Dey Plate";
      if (has("turkey")) return "Turkey Boss Plate";
      if (rice && protein) return "Rice and Correct Protein";
      if (!protein) return "No Meat, No Wahala";
      return "Your Own Way Plate";
    };

    const render = () => {
      const empty = $(".builder-empty", plateEl);
      if (!plate.length && !empty) plateEl.innerHTML = `<p class="builder-empty">Tap a dish to start your plate</p>`;
      if (plate.length && empty) empty.remove();
      const scoops = $$(".scoop", plateEl);
      scoops.slice(plate.length).forEach((s) => s.remove());
      for (let i = scoops.length; i < plate.length; i++) {
        const d = byId[plate[i]];
        const [x, y] = slots[i % slots.length];
        const s = document.createElement("span");
        s.className = d.photo ? "scoop is-photo" : "scoop";
        s.style.setProperty("--x", `${x}%`);
        s.style.setProperty("--y", `${y}%`);
        s.style.setProperty("--r", `${Math.round(Math.random() * 40 - 20)}deg`);
        s.style.backgroundImage = `url("${encodeURI(d.img)}")`;
        plateEl.append(s);
      }

      const counts = {};
      plate.forEach((id) => { counts[id] = (counts[id] || 0) + 1; });
      const ids = Object.keys(counts);
      $("#receipt-lines").innerHTML = ids.length
        ? ids.map((id) => `<li><span>${counts[id]} × ${esc(byId[id].name)}</span><span class="dots"></span><span>${money(byId[id].price * counts[id])}</span></li>`).join("")
        : `<li class="muted">Your plate is empty.</li>`;
      const total = plate.reduce((sum, id) => sum + byId[id].price, 0);
      const belle = Math.min(100, plate.reduce((sum, id) => sum + byId[id].full * 7, 0));
      $("#receipt-total").textContent = money(total);
      $("#receipt-count").textContent = `${plate.length} of ${max} scoops`;
      $("#receipt-belle").textContent = `Belle ${belle}% full`;
      $("#belle-fill").style.height = `${belle}%`;
      const tag = $("#belle-tag");
      tag.style.bottom = `${belle}%`;
      tag.textContent = `${belle}%`;
      $("#receipt-name").textContent = plateName();
      for (const id of ["plate-add", "plate-undo", "plate-reset"]) $(`#${id}`).disabled = !plate.length;
    };

    tabsEl.addEventListener("click", (e) => {
      const chip = e.target.closest(".chip");
      if (!chip) return;
      active = Number(chip.dataset.group);
      $$(".chip", tabsEl).forEach((c) => c.setAttribute("aria-pressed", String(c === chip)));
      renderList();
    });
    listEl.addEventListener("click", (e) => {
      const pick = e.target.closest("[data-pick]");
      if (!pick || pick.disabled) return;
      if (plate.length >= max) { toast(`Max ${max} scoops. Mama counted.`); return; }
      plate.push(pick.dataset.pick);
      render();
    });
    $("#plate-undo").addEventListener("click", () => { plate.pop(); render(); });
    $("#plate-reset").addEventListener("click", () => { plate = []; render(); });
    $("#plate-add").addEventListener("click", () => {
      if (!plate.length) return;
      const name = plate.length >= 3 ? plateName() : "Your plate";
      plate.forEach((id) => { bag[id] = (bag[id] || 0) + 1; });
      saveBag();
      bumpBag();
      toast(`${name} is in your bag`);
      plate = [];
      render();
    });
    renderList();
    render();
  }

  /* Everything that needs the menu -------------------------------------- */

  function initMenu(list) {
    dishes = list.filter((d) => d.price != null).map((d) => ({ available: true, ...d }));
    byId = Object.fromEntries(dishes.map((d) => [d.id, d]));
    for (const id of Object.keys(bag)) if (!byId[id]) delete bag[id];
    renderBag();
    initCravings();
    initCarousel();
    initMenuPage();
    initBuilder();
    $$("[data-price-of]").forEach((el) => {
      const d = byId[el.dataset.priceOf];
      if (d) el.textContent = money(d.price);
    });
    $$("[data-dish-count]").forEach((el) => {
      el.dataset.count = dishes.length;
      el.textContent = reduceMotion ? dishes.length : countText(el, 0);
      if (el.closest(".is-in")) countUp(el);
    });
    observe();
  }

  /* Drop countdown (home) ----------------------------------------------- */

  const countdown = $("#countdown");
  if (countdown) {
    const nextDrop = (now = new Date()) => {
      // Lagos is UTC+1 all year, so the drop hour in UTC is one earlier on the same day.
      const t = new Date(Date.UTC(now.getUTCFullYear(), now.getUTCMonth(), now.getUTCDate(), D.drop.hour - 1));
      t.setUTCDate(t.getUTCDate() + ((D.drop.weekday - t.getUTCDay() + 7) % 7));
      if (t <= now) t.setUTCDate(t.getUTCDate() + 7);
      return t;
    };
    const units = Object.fromEntries($$("[data-unit]", countdown).map((el) => [el.dataset.unit, el]));
    const tick = () => {
      let s = Math.max(0, Math.floor((nextDrop() - Date.now()) / 1000));
      const d = Math.floor(s / 86400); s -= d * 86400;
      const h = Math.floor(s / 3600); s -= h * 3600;
      const m = Math.floor(s / 60); s -= m * 60;
      units.d.textContent = d;
      units.h.textContent = String(h).padStart(2, "0");
      units.m.textContent = String(m).padStart(2, "0");
      units.s.textContent = String(s).padStart(2, "0");
    };
    tick();
    setInterval(tick, 1000);
  }

  /* Scratch card (home) ------------------------------------------------- */

  const scratch = $("#scratch");
  if (scratch) {
    const canvas = $("canvas", scratch);
    const ctx = canvas.getContext("2d", { willReadFrequently: true });
    let scratching = false;
    let last = null;
    let moves = 0;

    const paintFoil = () => {
      if (scratch.classList.contains("is-revealed")) return;
      const { width, height } = canvas.getBoundingClientRect();
      const dpr = window.devicePixelRatio || 1;
      canvas.width = Math.round(width * dpr);
      canvas.height = Math.round(height * dpr);
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      ctx.globalCompositeOperation = "source-over";

      const g = ctx.createLinearGradient(0, 0, width, height);
      g.addColorStop(0, "#f3e0c4");
      g.addColorStop(.5, "#fffaf0");
      g.addColorStop(1, "#e7cfac");
      ctx.fillStyle = g;
      ctx.fillRect(0, 0, width, height);

      ctx.fillStyle = "rgba(217, 21, 29, .16)";
      for (let y = 14; y < height; y += 30) {
        for (let x = (y / 30) % 2 ? 10 : 25; x < width; x += 30) {
          ctx.beginPath();
          ctx.moveTo(x, y - 6); ctx.quadraticCurveTo(x + 1, y - 1, x + 6, y);
          ctx.quadraticCurveTo(x + 1, y + 1, x, y + 6); ctx.quadraticCurveTo(x - 1, y + 1, x - 6, y);
          ctx.quadraticCurveTo(x - 1, y - 1, x, y - 6); ctx.fill();
        }
      }
      ctx.fillStyle = "#141211";
      ctx.textAlign = "center";
      ctx.textBaseline = "middle";
      ctx.font = '400 30px "Bagel Fat One", sans-serif';
      ctx.fillText("Scratch me!", width / 2, height / 2 - 10);
      ctx.font = '700 14px "DM Sans", sans-serif';
      ctx.fillText("Today's deal is hiding under here", width / 2, height / 2 + 24);
    };

    const revealDeal = () => {
      scratch.classList.add("is-revealed");
      toast("Deal unlocked: free dodo with any combo");
    };

    const clearedRatio = () => {
      const { data } = ctx.getImageData(0, 0, canvas.width, canvas.height);
      let clear = 0, total = 0;
      for (let i = 3; i < data.length; i += 4 * 24) { total++; if (data[i] === 0) clear++; }
      return clear / total;
    };

    const scratchAt = (e) => {
      // offsetX/Y are in the canvas's own (untilted) coordinates
      const p = { x: e.offsetX, y: e.offsetY };
      ctx.globalCompositeOperation = "destination-out";
      ctx.lineCap = "round";
      ctx.lineJoin = "round";
      ctx.lineWidth = 42;
      ctx.beginPath();
      ctx.moveTo((last || p).x, (last || p).y);
      ctx.lineTo(p.x, p.y);
      ctx.stroke();
      last = p;
      if (++moves % 12 === 0 && clearedRatio() > 0.5) revealDeal();
    };

    canvas.addEventListener("pointerdown", (e) => { scratching = true; last = null; canvas.setPointerCapture(e.pointerId); scratchAt(e); });
    canvas.addEventListener("pointermove", (e) => { if (scratching) scratchAt(e); });
    const stop = () => {
      if (!scratching) return;
      scratching = false;
      if (!scratch.classList.contains("is-revealed") && clearedRatio() > 0.5) revealDeal();
    };
    canvas.addEventListener("pointerup", stop);
    canvas.addEventListener("pointercancel", stop);
    $(".scratch-reveal", scratch).addEventListener("click", revealDeal);

    (document.fonts ? document.fonts.ready : Promise.resolve()).then(paintFoil);
    let resizeTimer;
    addEventListener("resize", () => { clearTimeout(resizeTimer); resizeTimer = setTimeout(paintFoil, 150); });
  }

  /* Kitchen sizzle sound ------------------------------------------------ */

  let sizzle;
  function makeSizzle() {
    const ac = new (window.AudioContext || window.webkitAudioContext)();
    const len = ac.sampleRate * 3;
    const buffer = ac.createBuffer(1, len, ac.sampleRate);
    const data = buffer.getChannelData(0);
    let pop = 0;
    for (let i = 0; i < len; i++) {
      if (Math.random() < 0.0007) pop = 1;
      pop *= 0.993;
      data[i] = (Math.random() * 2 - 1) * (0.16 + pop * 0.85);
    }
    const src = ac.createBufferSource();
    src.buffer = buffer;
    src.loop = true;
    const band = ac.createBiquadFilter();
    band.type = "bandpass";
    band.frequency.value = 3200;
    band.Q.value = 0.6;
    const gain = ac.createGain();
    gain.gain.value = 0;
    src.connect(band).connect(gain).connect(ac.destination);
    src.start();
    return { ac, gain };
  }

  $("#sound").addEventListener("click", (e) => {
    const btn = e.currentTarget;
    const on = btn.getAttribute("aria-pressed") !== "true";
    sizzle = sizzle || makeSizzle();
    sizzle.ac.resume();
    sizzle.gain.gain.setTargetAtTime(on ? 0.22 : 0, sizzle.ac.currentTime, 0.25);
    btn.setAttribute("aria-pressed", String(on));
    btn.setAttribute("aria-label", on ? "Stop kitchen sizzle sound" : "Play kitchen sizzle sound");
    $("use", btn).setAttribute("href", on ? "#i-sound" : "#i-mute");
  });

  /* Mobile navigation --------------------------------------------------- */

  const nav = $(".nav");
  const toggle = $("#menu-toggle");
  function setNav(open) {
    nav.classList.toggle("is-open", open);
    toggle.setAttribute("aria-expanded", String(open));
    toggle.setAttribute("aria-label", open ? "Close navigation" : "Open navigation");
    $("use", toggle).setAttribute("href", open ? "#i-close" : "#i-menu");
  }
  toggle.addEventListener("click", () => setNav(!nav.classList.contains("is-open")));
  $$("#nav-links a").forEach((a) => a.addEventListener("click", () => setNav(false)));
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && nav.classList.contains("is-open")) { setNav(false); toggle.focus(); }
  });

  /* Email sign-up ------------------------------------------------------- */

  const form = $("#signup-form");
  const email = $("#email");
  const msg = $("#form-msg");
  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    if (!email.value.trim() || !email.checkValidity()) {
      email.setAttribute("aria-invalid", "true");
      msg.textContent = "That email doesn't look right. Try again?";
      email.focus();
      return;
    }
    email.removeAttribute("aria-invalid");
    if (D.signupEndpoint) {
      msg.textContent = "Signing you up...";
      try {
        const res = await fetch(D.signupEndpoint, { method: "POST", body: new FormData(form), headers: { Accept: "application/json" } });
        if (!res.ok) throw new Error(res.statusText);
      } catch {
        msg.textContent = "Couldn't sign you up just now. Please try again.";
        return;
      }
    }
    msg.textContent = "You're on the list. See you Friday!";
    form.reset();
  });
  email.addEventListener("input", () => { email.removeAttribute("aria-invalid"); msg.textContent = ""; });

  /* Job applications (careers page) ------------------------------------- */

  const applyForm = $("#apply-form");
  if (applyForm) {
    const applyMsg = $("#apply-msg");
    applyForm.addEventListener("input", (e) => { e.target.removeAttribute("aria-invalid"); applyMsg.textContent = ""; });
    applyForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const f = new FormData(applyForm);
      const val = (k) => String(f.get(k) || "").trim();
      const app = {
        full_name: val("full_name"), phone: val("phone"), email: val("email") || null,
        role: val("role"), experience: val("experience"), specialties: val("specialties") || null,
        availability: val("availability"), message: val("message") || null,
      };
      const problems = [];
      if (app.full_name.length < 2) problems.push(["full_name", "Please add your full name."]);
      if (app.phone.replace(/\D/g, "").length < 7) problems.push(["phone", "Please add a phone number we can call."]);
      if (app.email && !applyForm.elements.email.checkValidity()) problems.push(["email", "That email doesn't look right."]);
      if (!app.role) problems.push(["role", "Pick the role you want."]);
      if (!app.experience) problems.push(["experience", "Tell us how long you've been cooking."]);
      if (!f.get("consent")) problems.push(["consent", "Please tick the box so we can contact you."]);
      for (const [field] of problems) applyForm.elements[field].setAttribute("aria-invalid", "true");
      if (problems.length) {
        applyMsg.textContent = problems[0][1];
        applyForm.elements[problems[0][0]].focus();
        return;
      }

      const btn = $("button[type=submit]", applyForm);
      btn.disabled = true;
      applyMsg.textContent = "";
      try {
        if (hasDb) {
          await db("applications", { method: "POST", body: app, headers: { Prefer: "return=minimal" } });
        } else if (D.whatsapp) {
          const text = ["Hello IyaBolaji, I'd like to apply.", ...Object.entries(app).filter(([, v]) => v).map(([k, v]) => `${k.replace("_", " ")}: ${v}`)].join("\n");
          window.open(`https://wa.me/${D.whatsapp}?text=${encodeURIComponent(text)}`, "_blank", "noopener");
        } else {
          applyMsg.textContent = "Online applications open soon. Come by 3rd Ave Rd, Ipaja and ask for the kitchen.";
          return;
        }
        applyForm.hidden = true;
        const done = $("#apply-done");
        done.hidden = false;
        $("h3", done).focus();
      } catch (err) {
        applyMsg.textContent = err.message || "We couldn't send your application. Please try again.";
      } finally {
        btn.disabled = false;
      }
    });
  }

  /* Links and numbers from data.js -------------------------------------- */

  for (const [label, url] of Object.entries(D.links || {})) {
    if (!url) continue;
    $("#footer-pills").insertAdjacentHTML("beforeend", `<li><a class="pill" href="${esc(url)}" target="_blank" rel="noopener">${esc(label)}</a></li>`);
  }

  // Order buttons on the Find us page only appear once their number or link is set.
  const contact = {
    whatsapp: D.whatsapp && `https://wa.me/${D.whatsapp}`,
    phone: D.phone && `tel:${D.phone}`,
    chowdeck: D.links && D.links.Chowdeck,
  };
  $$("[data-contact]").forEach((el) => {
    const url = contact[el.dataset.contact];
    if (url) el.href = url; else el.remove();
  });

  $("#year").textContent = new Date().getFullYear();

  /* Start: menu, then the intro once fonts are in (or after 1.2s at most) - */

  loadMenu().then(initMenu);

  const ready = () => {
    root.classList.add("is-loaded");
    revealReady = true;
    observe();
  };
  if (reduceMotion) ready();
  else Promise.race([document.fonts ? document.fonts.ready : Promise.resolve(), new Promise((r) => setTimeout(r, 1200))]).then(ready);
})();
