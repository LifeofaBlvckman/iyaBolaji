(() => {
  const D = window.IYA;
  const $ = (sel, el = document) => el.querySelector(sel);
  const $$ = (sel, el = document) => [...el.querySelectorAll(sel)];
  const byId = Object.fromEntries(D.dishes.map((d) => [d.id, d]));
  const money = (n) => D.currency + n.toLocaleString("en-NG");
  const icon = (id, cls = "") => `<svg class="${cls}" aria-hidden="true"><use href="#i-${id}"/></svg>`;
  const reduceMotion = matchMedia("(prefers-reduced-motion: reduce)").matches;

  const store = {
    get(key, fallback) {
      try { return JSON.parse(localStorage.getItem(key)) ?? fallback; } catch { return fallback; }
    },
    set(key, value) {
      try { localStorage.setItem(key, JSON.stringify(value)); } catch { /* private mode */ }
    },
  };

  /* Toast -------------------------------------------------------------- */

  const toastEl = $("#toast");
  let toastTimer;
  function toast(message) {
    toastEl.textContent = message;
    toastEl.classList.add("is-on");
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => toastEl.classList.remove("is-on"), 2600);
  }

  /* Bag ---------------------------------------------------------------- */

  let bag = store.get("iya-bag", {});
  for (const id of Object.keys(bag)) if (!byId[id]) delete bag[id];

  const bagDialog = $("#bag");
  const bagCountEl = $("#bag-count");

  function bagLines() {
    return Object.entries(bag).filter(([, q]) => q > 0).map(([id, qty]) => ({ dish: byId[id], qty }));
  }

  function renderBag() {
    const lines = bagLines();
    const count = lines.reduce((sum, l) => sum + l.qty, 0);
    const total = lines.reduce((sum, l) => sum + l.qty * l.dish.price, 0);

    bagCountEl.textContent = count;
    $("#bag-open").setAttribute("aria-label", `Open bag, ${count} item${count === 1 ? "" : "s"}`);
    $("#bag-total").textContent = money(total);

    $("#bag-list").innerHTML = lines.length
      ? lines.map(({ dish, qty }) => `
        <li>
          <img src="${dish.img}" alt="" class="${dish.photo ? "is-photo" : ""}" width="64" height="64">
          <div><div class="bag-item-name">${dish.name}</div><div class="bag-item-price">${money(dish.price)} each</div></div>
          <div class="stepper">
            <button type="button" data-dec="${dish.id}" aria-label="Remove one ${dish.name}">${icon("minus")}</button>
            <output aria-label="${dish.name} quantity">${qty}</output>
            <button type="button" data-inc="${dish.id}" aria-label="Add one more ${dish.name}">${icon("plus")}</button>
          </div>
        </li>`).join("")
      : `<li class="bag-empty">Your bag is empty. Belle no go full like this.</li>`;

    const checkout = $("#bag-checkout");
    const note = $("#bag-note");
    if (D.whatsapp && lines.length) {
      const text = ["Hello IyaBolaji, I'd like to order:", ...lines.map((l) => `${l.qty} x ${l.dish.name} (${money(l.qty * l.dish.price)})`), `Total: ${money(total)}`].join("\n");
      checkout.href = `https://wa.me/${D.whatsapp}?text=${encodeURIComponent(text)}`;
      checkout.target = "_blank";
      checkout.rel = "noopener";
      checkout.textContent = "Send order on WhatsApp";
      note.textContent = "We'll confirm your order and delivery time on WhatsApp.";
    } else if (D.phone) {
      checkout.href = `tel:${D.phone}`;
      checkout.removeAttribute("target");
      checkout.textContent = "Call to order";
      note.textContent = "Read us your bag and we'll have it ready.";
    } else {
      checkout.href = "#find";
      checkout.removeAttribute("target");
      checkout.textContent = "Visit us to order";
      note.textContent = "3rd Ave Rd, Ipaja. Dine-in, takeaway or delivery.";
    }
  }

  function setQty(id, qty) {
    if (qty > 0) bag[id] = qty; else delete bag[id];
    store.set("iya-bag", bag);
    renderBag();
  }

  function addToBag(id) {
    setQty(id, (bag[id] || 0) + 1);
    toast(`${byId[id].name} added to your bag`);
    bagCountEl.classList.remove("is-bumped");
    void bagCountEl.offsetWidth;
    bagCountEl.classList.add("is-bumped");
  }

  function openBag() {
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
    if (inc) setQty(inc.dataset.inc, (bag[inc.dataset.inc] || 0) + 1);
    if (dec) setQty(dec.dataset.dec, (bag[dec.dataset.dec] || 0) - 1);
  });
  $("#bag-checkout").addEventListener("click", (e) => {
    if (e.currentTarget.getAttribute("href") === "#find") bagDialog.close();
  });

  document.addEventListener("click", (e) => {
    const add = e.target.closest("[data-add]");
    if (add) addToBag(add.dataset.add);
  });

  /* Cravings ------------------------------------------------------------ */

  const chipsEl = $("#craving-chips");
  const featureImg = $("#feature-img");
  let featured = D.cravings[0].dish;

  chipsEl.innerHTML = D.cravings.map((c, i) => `
    <button class="chip" type="button" aria-pressed="${i === 0}" data-dish="${c.dish}">${icon("spark")}${c.label}</button>`).join("");

  function meter(kind, value, label) {
    const marks = Array.from({ length: 5 }, (_, i) => {
      const inner = kind === "heat" ? icon("chili") : kind === "napkins" ? icon("napkin") : "";
      return `<span class="m-${kind}${i < value ? "" : " off"}">${inner}</span>`;
    }).join("");
    return `<span class="sr-only">${label}: ${value} out of 5</span><span aria-hidden="true" style="display:contents">${marks}</span>`;
  }

  function showFeature(id, animate = true) {
    const d = byId[id];
    featured = id;
    $("#feature-name").textContent = d.name;
    $("#feature-desc").textContent = d.desc;
    $("#feature-price").textContent = money(d.price);
    $("#feature-serves").textContent = d.serves;
    $("#meter-heat").innerHTML = meter("heat", d.heat, "Heat");
    $("#meter-full").innerHTML = meter("full", d.full, "Belle full");
    $("#meter-napkins").innerHTML = meter("napkins", d.napkins, "Napkins needed");
    $("#feature-add").setAttribute("aria-label", `Add ${d.name} to bag`);

    const swap = () => {
      featureImg.src = d.img;
      featureImg.alt = d.alt;
      featureImg.classList.toggle("is-photo", !!d.photo);
      featureImg.classList.remove("is-swapping");
    };
    if (!animate || reduceMotion) return swap();
    featureImg.classList.add("is-swapping");
    setTimeout(swap, 200);
  }

  chipsEl.addEventListener("click", (e) => {
    const chip = e.target.closest(".chip");
    if (!chip) return;
    $$(".chip", chipsEl).forEach((c) => c.setAttribute("aria-pressed", String(c === chip)));
    showFeature(chip.dataset.dish);
  });
  $("#feature-add").addEventListener("click", () => addToBag(featured));
  showFeature(featured, false);

  /* Menu lineup --------------------------------------------------------- */

  const filtersEl = $("#menu-filters");
  const cardsEl = $("#cards");
  const tones = ["red", "white", "ink", "white"];
  const tilts = [-4, 3, -2, 5];

  filtersEl.innerHTML = D.filters.map((f, i) => `
    <button class="chip" type="button" aria-pressed="${i === 0}" data-filter="${f.id}">${f.label}</button>`).join("");

  function renderCards(filter) {
    const list = D.dishes.filter((d) => filter === "all" || d.cat === filter);
    cardsEl.innerHTML = list.map((d, i) => `
      <li class="card card--${tones[i % 4]}" style="--tilt:${tilts[i % 4]}deg">
        ${d.badge ? `<span class="card-badge">${d.badge}</span>` : ""}
        <img src="${d.img}" alt="${d.alt}" width="600" height="600" loading="lazy" class="${d.photo ? "is-photo" : ""}">
        <h3>${d.name}</h3>
        <p>${d.desc}</p>
        <div class="card-foot">
          <span class="card-price">${money(d.price)}</span>
          <button class="add-btn" type="button" data-add="${d.id}" aria-label="Add ${d.name} to bag">${icon("plus")}</button>
        </div>
      </li>`).join("");
    cardsEl.scrollTo({ left: 0 });
  }

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

  /* Drop countdown ------------------------------------------------------ */

  function nextDrop(now = new Date()) {
    // Lagos is UTC+1 all year, so the drop hour in UTC is one earlier on the same day.
    const t = new Date(Date.UTC(now.getUTCFullYear(), now.getUTCMonth(), now.getUTCDate(), D.drop.hour - 1));
    t.setUTCDate(t.getUTCDate() + ((D.drop.weekday - t.getUTCDay() + 7) % 7));
    if (t <= now) t.setUTCDate(t.getUTCDate() + 7);
    return t;
  }

  const units = Object.fromEntries($$("#countdown [data-unit]").map((el) => [el.dataset.unit, el]));
  function tick() {
    let s = Math.max(0, Math.floor((nextDrop() - Date.now()) / 1000));
    const d = Math.floor(s / 86400); s -= d * 86400;
    const h = Math.floor(s / 3600); s -= h * 3600;
    const m = Math.floor(s / 60); s -= m * 60;
    units.d.textContent = d;
    units.h.textContent = String(h).padStart(2, "0");
    units.m.textContent = String(m).padStart(2, "0");
    units.s.textContent = String(s).padStart(2, "0");
  }
  tick();
  setInterval(tick, 1000);

  /* Scratch card -------------------------------------------------------- */

  const scratch = $("#scratch");
  const canvas = $("canvas", scratch);
  const ctx = canvas.getContext("2d", { willReadFrequently: true });
  let scratching = false;
  let last = null;
  let moves = 0;

  function paintFoil() {
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
  }

  function reveal() {
    scratch.classList.add("is-revealed");
    toast("Deal unlocked: free dodo with any rice plate");
  }

  function clearedRatio() {
    const { data } = ctx.getImageData(0, 0, canvas.width, canvas.height);
    let clear = 0, total = 0;
    for (let i = 3; i < data.length; i += 4 * 24) { total++; if (data[i] === 0) clear++; }
    return clear / total;
  }

  function scratchAt(e) {
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
    if (++moves % 12 === 0 && clearedRatio() > 0.5) reveal();
  }

  canvas.addEventListener("pointerdown", (e) => { scratching = true; last = null; canvas.setPointerCapture(e.pointerId); scratchAt(e); });
  canvas.addEventListener("pointermove", (e) => { if (scratching) scratchAt(e); });
  const stop = () => {
    if (!scratching) return;
    scratching = false;
    if (!scratch.classList.contains("is-revealed") && clearedRatio() > 0.5) reveal();
  };
  canvas.addEventListener("pointerup", stop);
  canvas.addEventListener("pointercancel", stop);
  $(".scratch-reveal", scratch).addEventListener("click", reveal);

  (document.fonts ? document.fonts.ready : Promise.resolve()).then(paintFoil);
  let resizeTimer;
  addEventListener("resize", () => { clearTimeout(resizeTimer); resizeTimer = setTimeout(paintFoil, 150); });

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

  $("#year").textContent = new Date().getFullYear();
  renderBag();
})();
