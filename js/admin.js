(() => {
  const C = window.IYA_CONFIG || {};
  const $ = (sel, el = document) => el.querySelector(sel);
  const $$ = (sel, el = document) => [...el.querySelectorAll(sel)];
  const esc = (v) => String(v ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const money = (n) => "₦" + Number(n || 0).toLocaleString("en-NG");
  const icon = (id) => `<svg aria-hidden="true"><use href="#i-${id}"/></svg>`;
  const clock = new Intl.DateTimeFormat("en-NG", { hour: "numeric", minute: "2-digit" });
  const day = new Intl.DateTimeFormat("en-NG", { day: "numeric", month: "short" });
  const store = {
    get(key, fallback) { try { return JSON.parse(localStorage.getItem(key)) ?? fallback; } catch { return fallback; } },
    set(key, value) { try { localStorage.setItem(key, JSON.stringify(value)); } catch { /* private mode */ } },
  };

  const CATS = { rice: "Rice & more", swallow: "Swallow & soup", protein: "Protein", sides: "Sides" };
  const TYPES = { pickup: "Pickup", delivery: "Delivery", "dine-in": "Dine-in" };
  const NEXT = {
    new: ["preparing", "Start preparing"],
    preparing: ["ready", "Mark ready"],
    ready: ["completed", "Complete"],
  };
  const BUCKET = "dish-photos";

  let sb = null;
  let channel = null;
  let pollTimer = null;
  let orders = [];
  let dishes = [];
  let applications = [];
  let knownOrderIds = null;
  let orderFilter = "open";
  let appFilter = "active";
  let catFilter = "all";

  /* Toast ---------------------------------------------------------------- */

  let toastTimer;
  function toast(message, error = false) {
    const el = $("#toast");
    el.textContent = message;
    el.classList.toggle("is-error", error);
    el.classList.add("is-on");
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => el.classList.remove("is-on"), error ? 5000 : 2800);
  }

  /* New-order chime ------------------------------------------------------- */

  let audio;
  let soundOn = store.get("iya-admin-sound", true);
  function unlockAudio() {
    try {
      audio = audio || new (window.AudioContext || window.webkitAudioContext)();
      if (audio.state === "suspended") audio.resume();
    } catch { /* no audio */ }
  }
  document.addEventListener("pointerdown", unlockAudio, { once: true });
  document.addEventListener("keydown", unlockAudio, { once: true });

  function chime() {
    if (!soundOn || !audio) return;
    const now = audio.currentTime;
    [[880, 0], [1320, 0.16], [1760, 0.32]].forEach(([freq, at]) => {
      const osc = audio.createOscillator();
      const gain = audio.createGain();
      osc.type = "sine";
      osc.frequency.value = freq;
      gain.gain.setValueAtTime(0.0001, now + at);
      gain.gain.exponentialRampToValueAtTime(0.35, now + at + 0.02);
      gain.gain.exponentialRampToValueAtTime(0.0001, now + at + 0.5);
      osc.connect(gain).connect(audio.destination);
      osc.start(now + at);
      osc.stop(now + at + 0.55);
    });
  }

  function renderSound() {
    const btn = $("#sound-toggle");
    btn.setAttribute("aria-pressed", String(soundOn));
    btn.setAttribute("aria-label", soundOn ? "Turn new-order sound off" : "Turn new-order sound on");
    $("use", btn).setAttribute("href", soundOn ? "#i-bell" : "#i-bell-off");
  }
  $("#sound-toggle").addEventListener("click", () => {
    soundOn = !soundOn;
    store.set("iya-admin-sound", soundOn);
    renderSound();
    unlockAudio();
    if (soundOn) chime();
  });
  renderSound();

  /* Helpers --------------------------------------------------------------- */

  function ago(iso) {
    const mins = Math.round((Date.now() - new Date(iso)) / 60000);
    if (mins < 1) return "just now";
    if (mins < 60) return `${mins} min ago`;
    const hrs = Math.floor(mins / 60);
    if (hrs < 24) return `${hrs} hr${hrs > 1 ? "s" : ""} ago`;
    return day.format(new Date(iso));
  }

  // Nigerian numbers: 0803... -> 234803... for WhatsApp links.
  function waNumber(phone) {
    let d = String(phone || "").replace(/\D/g, "");
    if (d.startsWith("0") && d.length === 11) d = "234" + d.slice(1);
    return d;
  }

  function contactButtons(phone, text) {
    const tel = String(phone || "").replace(/[^\d+]/g, "");
    return `<div class="contact-row">
      <a class="btn btn-soft btn-sm" href="tel:${esc(tel)}">${icon("phone")} ${esc(phone)}</a>
      <a class="btn btn-soft btn-sm" href="https://wa.me/${waNumber(phone)}?text=${encodeURIComponent(text)}" target="_blank" rel="noopener">${icon("chat")} WhatsApp</a>
    </div>`;
  }

  function friendly(error) {
    const msg = (error && (error.message || error.error_description)) || String(error || "");
    if (/invalid login credentials/i.test(msg)) return "That email or password isn't right.";
    if (/email not confirmed/i.test(msg)) return "Confirm your email first (check your inbox), or mark the user as confirmed in Supabase.";
    if (/failed to fetch|network/i.test(msg)) return "Can't reach Supabase. Check your internet connection.";
    if (/row-level security|permission denied/i.test(msg)) return "This account isn't allowed to do that. Is it set up as an admin?";
    return msg || "Something went wrong. Please try again.";
  }

  /* Tabs -------------------------------------------------------------------- */

  const tabs = $$(".tab");
  function selectTab(id, focus = false) {
    for (const tab of tabs) {
      const on = tab.id === id;
      tab.setAttribute("aria-selected", String(on));
      tab.tabIndex = on ? 0 : -1;
      $(`#${tab.getAttribute("aria-controls")}`).hidden = !on;
      if (on && focus) tab.focus();
    }
    history.replaceState(null, "", `#${id.replace("tab-", "")}`);
    if (id === "tab-applications") loadApplications();
  }
  tabs.forEach((tab, i) => {
    tab.addEventListener("click", () => selectTab(tab.id));
    tab.addEventListener("keydown", (e) => {
      const step = e.key === "ArrowRight" ? 1 : e.key === "ArrowLeft" ? -1 : 0;
      if (!step) return;
      e.preventDefault();
      selectTab(tabs[(i + step + tabs.length) % tabs.length].id, true);
    });
  });

  /* Orders ------------------------------------------------------------------ */

  async function loadOrders() {
    const { data, error } = await sb.from("orders").select("*").order("created_at", { ascending: false }).limit(300);
    if (error) { toast(friendly(error), true); return; }
    const fresh = [];
    if (knownOrderIds) {
      for (const o of data) if (!knownOrderIds.has(o.id) && o.status === "new") fresh.push(o.id);
    }
    knownOrderIds = new Set(data.map((o) => o.id));
    orders = data;
    renderOrders(new Set(fresh));
    if (fresh.length) {
      chime();
      toast(fresh.length === 1 ? `New order #${fresh[0]}!` : `${fresh.length} new orders!`);
    }
  }

  function renderOrders(fresh = new Set()) {
    const open = (o) => ["new", "preparing", "ready"].includes(o.status);
    const shown = orders.filter((o) => orderFilter === "all" || (orderFilter === "open" ? open(o) : o.status === orderFilter));
    // The kitchen works oldest-first; history reads newest-first.
    if (orderFilter === "open") shown.sort((a, b) => new Date(a.created_at) - new Date(b.created_at));

    $("#orders").innerHTML = shown.length ? shown.map((o) => {
      const next = NEXT[o.status];
      const items = Array.isArray(o.items) ? o.items : [];
      return `
        <article class="order${o.status === "new" ? " is-new" : ""}${fresh.has(o.id) ? " is-fresh" : ""}" aria-label="Order ${o.id}">
          <div class="order-top">
            <div>
              <div class="order-no">#${o.id}</div>
              <div class="order-when" title="${esc(new Date(o.created_at).toLocaleString("en-NG"))}">${ago(o.created_at)} · ${clock.format(new Date(o.created_at))}</div>
            </div>
            <span class="pill pill-${esc(o.status)}">${esc(o.status)}</span>
          </div>
          <div class="who">
            <strong>${esc(o.customer_name)}</strong>
            <span class="type-tag">${esc(TYPES[o.order_type] || o.order_type)}</span>
          </div>
          ${contactButtons(o.phone, `Hello ${o.customer_name}, this is IyaBolaji Restaurant about your order #${o.id}.`)}
          ${o.address ? `<div class="address"><strong>Deliver to:</strong> ${esc(o.address)}</div>` : ""}
          ${o.note ? `<div class="order-note"><strong>Note:</strong> ${esc(o.note)}</div>` : ""}
          <ul class="items">${items.map((i) => `<li><span>${Number(i.qty)} × ${esc(i.name)}</span><span>${money(i.price * i.qty)}</span></li>`).join("")}</ul>
          <div class="order-total"><span>Total</span><span>${money(o.total)}</span></div>
          <div class="order-actions">
            ${next ? `<button class="btn btn-red" type="button" data-status="${next[0]}" data-order="${o.id}">${next[1]}</button>` : ""}
            ${open(o) ? `<button class="btn btn-ghost" type="button" data-status="cancelled" data-order="${o.id}">Cancel</button>` : ""}
            ${!open(o) ? `<button class="btn btn-ghost" type="button" data-status="preparing" data-order="${o.id}">Reopen</button>` : ""}
          </div>
        </article>`;
    }).join("") : `<p class="empty">${orderFilter === "open" ? "No open orders. The kitchen is calm." : "Nothing here yet."}</p>`;

    // Stats use the device's own clock, which is Lagos time for the kitchen.
    const midnight = new Date();
    midnight.setHours(0, 0, 0, 0);
    const today = orders.filter((o) => new Date(o.created_at) >= midnight && o.status !== "cancelled");
    $("#stat-today").textContent = today.length;
    $("#stat-revenue").textContent = money(today.reduce((sum, o) => sum + o.total, 0));
    $("#stat-open").textContent = orders.filter(open).length;
    const fresh2 = orders.filter((o) => o.status === "new").length;
    const badge = $("#new-count");
    badge.textContent = fresh2;
    badge.hidden = !fresh2;
    document.title = `${fresh2 ? `(${fresh2}) ` : ""}Admin · IyaBolaji`;
  }

  $("#orders").addEventListener("click", async (e) => {
    const btn = e.target.closest("[data-status]");
    if (!btn) return;
    const id = Number(btn.dataset.order);
    const status = btn.dataset.status;
    if (status === "cancelled" && !confirm(`Cancel order #${id}?`)) return;
    btn.disabled = true;
    const { error } = await sb.from("orders").update({ status }).eq("id", id);
    if (error) { toast(friendly(error), true); btn.disabled = false; return; }
    const o = orders.find((x) => x.id === id);
    if (o) o.status = status;
    renderOrders();
    toast(`Order #${id}: ${status}`);
  });

  $$("[data-show]").forEach((chip) => chip.addEventListener("click", () => {
    orderFilter = chip.dataset.show;
    $$("[data-show]").forEach((c) => c.setAttribute("aria-pressed", String(c === chip)));
    renderOrders();
  }));

  function setLive(state) {
    const el = $("#live");
    el.classList.toggle("is-on", state === "on");
    el.classList.toggle("is-off", state === "off");
    $("#live-text").textContent = state === "on" ? "Live" : state === "off" ? "Auto-refresh" : "Connecting";
    el.title = state === "on" ? "New orders appear instantly" : "Checking for new orders every 30 seconds";
  }

  function startLive() {
    stopLive();
    channel = sb.channel("orders-feed")
      .on("postgres_changes", { event: "*", schema: "public", table: "orders" }, () => loadOrders())
      .subscribe((status) => setLive(status === "SUBSCRIBED" ? "on" : status === "CLOSED" ? "" : "off"));
    // Polling as a safety net in case the live connection drops.
    pollTimer = setInterval(() => { if (!document.hidden) loadOrders(); }, 30000);
    // Keep the "x min ago" labels fresh.
    setInterval(() => renderOrders(), 60000);
  }

  function stopLive() {
    if (channel) sb.removeChannel(channel);
    channel = null;
    clearInterval(pollTimer);
  }

  document.addEventListener("visibilitychange", () => { if (!document.hidden && sb && knownOrderIds) loadOrders(); });

  /* Menu ------------------------------------------------------------------- */

  async function loadDishes() {
    const { data, error } = await sb.from("dishes").select("*").order("sort").order("name");
    if (error) { toast(friendly(error), true); return; }
    dishes = data;
    renderDishes();
  }

  function renderDishes() {
    const q = $("#dish-search").value.trim().toLowerCase();
    const shown = dishes.filter((d) => (catFilter === "all" || d.cat === catFilter) && (!q || d.name.toLowerCase().includes(q)));
    $("#dishes").innerHTML = shown.length ? shown.map((d) => `
      <li class="dish${d.visible ? "" : " is-hidden"}">
        <img src="${esc(d.img || "assets/favicon.svg")}" alt="" width="64" height="64" loading="lazy">
        <div>
          <div class="dish-name">${esc(d.name)}</div>
          <div class="dish-meta">${esc(CATS[d.cat] || d.cat)}${d.badge ? ` · ${esc(d.badge)}` : ""}${d.photo ? " · Photo" : ""}</div>
        </div>
        <div class="dish-price${d.price == null ? " is-empty" : ""}">${d.price == null ? "No price: hidden" : money(d.price)}</div>
        <div class="dish-switches">
          <label class="switch"><input type="checkbox" data-flag="available" data-dish="${esc(d.id)}"${d.available ? " checked" : ""}><span></span>In stock</label>
          <label class="switch"><input type="checkbox" data-flag="visible" data-dish="${esc(d.id)}"${d.visible ? " checked" : ""}><span></span>On website</label>
        </div>
        <button class="btn btn-ghost btn-sm edit-btn" type="button" data-edit="${esc(d.id)}" aria-label="Edit ${esc(d.name)}">Edit</button>
      </li>`).join("") : `<li class="empty">No dishes match.</li>`;
  }

  $("#dishes").addEventListener("change", async (e) => {
    const box = e.target.closest("[data-flag]");
    if (!box) return;
    const d = dishes.find((x) => x.id === box.dataset.dish);
    const flag = box.dataset.flag;
    const value = box.checked;
    box.disabled = true;
    const { error } = await sb.from("dishes").update({ [flag]: value }).eq("id", d.id);
    box.disabled = false;
    if (error) { box.checked = !value; toast(friendly(error), true); return; }
    d[flag] = value;
    box.closest(".dish").classList.toggle("is-hidden", !d.visible);
    toast(flag === "available"
      ? `${d.name} is ${value ? "back in stock" : "marked sold out"}`
      : `${d.name} is ${value ? "on the website" : "hidden from the website"}`);
  });

  $("#dishes").addEventListener("click", (e) => {
    const btn = e.target.closest("[data-edit]");
    if (btn) openEditor(dishes.find((d) => d.id === btn.dataset.edit));
  });
  $("#dish-search").addEventListener("input", renderDishes);
  $$("[data-cat]").forEach((chip) => chip.addEventListener("click", () => {
    catFilter = chip.dataset.cat;
    $$("[data-cat]").forEach((c) => c.setAttribute("aria-pressed", String(c === chip)));
    renderDishes();
  }));
  $("#add-dish").addEventListener("click", () => openEditor(null));

  /* Dish editor ------------------------------------------------------------- */

  const editor = $("#editor");
  const form = $("#dish-form");
  const editorMsg = $("#editor-msg");
  let editing = null;
  let newPhoto = null;
  let previewUrl = null;

  function setPreview(src) {
    if (previewUrl) URL.revokeObjectURL(previewUrl);
    previewUrl = null;
    $("#photo-preview").src = src || "assets/favicon.svg";
  }

  function openEditor(dish) {
    editing = dish;
    newPhoto = null;
    form.reset();
    editorMsg.textContent = "";
    $$("[aria-invalid]", form).forEach((el) => el.removeAttribute("aria-invalid"));
    const d = dish || {
      name: "", price: "", cat: catFilter === "all" ? "rice" : catFilter, description: "", badge: "", serves: "",
      alt: "", heat: 2, fullness: 3, napkins: 2, available: true, visible: true,
      sort: Math.max(0, ...dishes.map((x) => x.sort || 0)) + 10, img: "",
    };
    $("#editor-title").textContent = dish ? `Edit ${dish.name}` : "Add a dish";
    for (const key of ["name", "cat", "description", "badge", "serves", "alt", "heat", "fullness", "napkins", "sort"]) {
      form.elements[key].value = d[key] ?? "";
    }
    form.elements.price.value = d.price ?? "";
    form.elements.available.checked = !!d.available;
    form.elements.visible.checked = !!d.visible;
    for (const key of ["heat", "fullness", "napkins"]) $(`#out-${key}`).textContent = form.elements[key].value;
    setPreview(d.img);
    $("#photo-label").textContent = d.img ? "Change photo" : "Add photo";
    $("#photo-hint").textContent = "JPG, PNG or WebP. Big photos are shrunk automatically.";
    $("#delete-dish").hidden = !dish;
    $("#save-dish").textContent = dish ? "Save changes" : "Add dish";
    editor.showModal();
  }

  form.addEventListener("input", (e) => {
    e.target.removeAttribute("aria-invalid");
    const out = $(`#out-${e.target.name}`);
    if (out) out.textContent = e.target.value;
  });
  $("#editor-close").addEventListener("click", () => editor.close());
  editor.addEventListener("click", (e) => { if (e.target === editor) editor.close(); });

  $("#photo-input").addEventListener("change", (e) => {
    const file = e.target.files[0];
    if (!file) return;
    if (!/^image\/(jpeg|png|webp)$/.test(file.type)) { editorMsg.textContent = "Please choose a JPG, PNG or WebP photo."; return; }
    if (file.size > 25 * 1024 * 1024) { editorMsg.textContent = "That photo is too big (over 25 MB)."; return; }
    newPhoto = file;
    setPreview("");
    previewUrl = URL.createObjectURL(file);
    $("#photo-preview").src = previewUrl;
    $("#photo-hint").textContent = `${file.name}: ready to upload when you save.`;
    editorMsg.textContent = "";
  });

  // Shrink photos to 1000px and re-encode before upload: phones take 5-10 MB photos.
  async function shrink(file) {
    const bitmap = await createImageBitmap(file);
    const scale = Math.min(1, 1000 / Math.max(bitmap.width, bitmap.height));
    const canvas = document.createElement("canvas");
    canvas.width = Math.round(bitmap.width * scale);
    canvas.height = Math.round(bitmap.height * scale);
    canvas.getContext("2d").drawImage(bitmap, 0, 0, canvas.width, canvas.height);
    bitmap.close && bitmap.close();
    const encode = (type, q) => new Promise((resolve) => canvas.toBlob(resolve, type, q));
    let blob = await encode("image/webp", 0.82);
    if (!blob || blob.type !== "image/webp") blob = await encode("image/jpeg", 0.85);
    return blob;
  }

  function slug(name) {
    const base = name.toLowerCase().normalize("NFKD").replace(/[^a-z0-9]+/g, "-").replace(/^-+|-+$/g, "").slice(0, 50) || "dish";
    let id = base;
    for (let n = 2; dishes.some((d) => d.id === id); n++) id = `${base}-${n}`;
    return id;
  }

  // Path inside our bucket for a public storage URL, or null for other images.
  function storagePath(url) {
    const marker = `/storage/v1/object/public/${BUCKET}/`;
    const i = String(url || "").indexOf(marker);
    return i === -1 ? null : decodeURIComponent(url.slice(i + marker.length));
  }

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const f = form.elements;
    const name = f.name.value.trim();
    const priceText = f.price.value.trim();
    const price = priceText === "" ? null : Math.round(Number(priceText));
    const problems = [];
    if (!name) problems.push(["name", "Give the dish a name."]);
    if (priceText !== "" && (!Number.isFinite(price) || price < 0)) problems.push(["price", "The price must be a number, or empty to hide the dish."]);
    if (!editing && !newPhoto) problems.push(["photo-input", "Add a photo so the dish looks good on the menu."]);
    if (problems.length) {
      editorMsg.textContent = problems[0][1];
      const field = f[problems[0][0]] || $(`#${problems[0][0]}`);
      if (field && field.type !== "file") { field.setAttribute("aria-invalid", "true"); field.focus(); }
      return;
    }

    const row = {
      name, price, cat: f.cat.value,
      description: f.description.value.trim(), badge: f.badge.value.trim(), serves: f.serves.value.trim(),
      alt: f.alt.value.trim() || name,
      heat: Number(f.heat.value), fullness: Number(f.fullness.value), napkins: Number(f.napkins.value),
      sort: Number(f.sort.value) || 0, available: f.available.checked, visible: f.visible.checked,
    };
    const id = editing ? editing.id : slug(name);
    const save = $("#save-dish");
    save.disabled = true;
    editorMsg.textContent = "";
    let uploadedPath = null;
    try {
      if (newPhoto) {
        save.textContent = "Uploading photo...";
        const blob = await shrink(newPhoto);
        const ext = blob.type === "image/webp" ? "webp" : "jpg";
        uploadedPath = `${id}/${Date.now()}.${ext}`;
        const up = await sb.storage.from(BUCKET).upload(uploadedPath, blob, { contentType: blob.type, cacheControl: "31536000", upsert: false });
        if (up.error) throw up.error;
        row.img = sb.storage.from(BUCKET).getPublicUrl(uploadedPath).data.publicUrl;
        row.photo = true;
      }
      save.textContent = "Saving...";
      const res = editing
        ? await sb.from("dishes").update(row).eq("id", id).select().single()
        : await sb.from("dishes").insert({ id, ...row }).select().single();
      if (res.error) throw res.error;

      // Tidy up the replaced photo, if it was one we uploaded.
      const oldPath = editing && newPhoto && storagePath(editing.img);
      if (oldPath) sb.storage.from(BUCKET).remove([oldPath]);

      if (editing) Object.assign(editing, res.data); else dishes.push(res.data);
      dishes.sort((a, b) => (a.sort - b.sort) || a.name.localeCompare(b.name));
      renderDishes();
      editor.close();
      toast(editing ? `${name} saved` : `${name} added to the menu`);
    } catch (err) {
      if (uploadedPath) sb.storage.from(BUCKET).remove([uploadedPath]);
      editorMsg.textContent = friendly(err);
    } finally {
      save.disabled = false;
      save.textContent = editing ? "Save changes" : "Add dish";
    }
  });

  $("#delete-dish").addEventListener("click", async () => {
    if (!editing || !confirm(`Delete ${editing.name} from the menu? Past orders keep their details.`)) return;
    const { error } = await sb.from("dishes").delete().eq("id", editing.id);
    if (error) { editorMsg.textContent = friendly(error); return; }
    const path = storagePath(editing.img);
    if (path) sb.storage.from(BUCKET).remove([path]);
    dishes = dishes.filter((d) => d !== editing);
    renderDishes();
    editor.close();
    toast(`${editing.name} deleted`);
  });

  /* Applications ----------------------------------------------------------- */

  async function loadApplications() {
    const { data, error } = await sb.from("applications").select("*").order("created_at", { ascending: false }).limit(300);
    if (error) { toast(friendly(error), true); return; }
    applications = data;
    renderApplications();
  }

  function renderApplications() {
    const shown = applications.filter((a) => appFilter === "all" || (appFilter === "active" ? ["new", "contacted"].includes(a.status) : a.status === appFilter));
    $("#applications").innerHTML = shown.length ? shown.map((a) => `
      <article class="appl">
        <div class="order-top">
          <div>
            <div class="order-no">${esc(a.full_name)}</div>
            <div class="order-when">Applied ${ago(a.created_at)}</div>
          </div>
          <span class="pill pill-${esc(a.status)}">${esc(a.status)}</span>
        </div>
        <dl>
          <dt>Role</dt><dd>${esc(a.role)}</dd>
          <dt>Experience</dt><dd>${esc(a.experience || "-")}</dd>
          <dt>Available</dt><dd>${esc(a.availability || "-")}</dd>
          ${a.specialties ? `<dt>Best at</dt><dd>${esc(a.specialties)}</dd>` : ""}
          ${a.email ? `<dt>Email</dt><dd><a href="mailto:${esc(a.email)}">${esc(a.email)}</a></dd>` : ""}
        </dl>
        ${a.message ? `<p class="msg">${esc(a.message)}</p>` : ""}
        ${contactButtons(a.phone, `Hello ${a.full_name}, this is IyaBolaji Restaurant about your application to work with us.`)}
        <label class="field">Status
          <select class="status-select" data-app-status="${a.id}">
            ${["new", "contacted", "hired", "declined"].map((s) => `<option value="${s}"${a.status === s ? " selected" : ""}>${s[0].toUpperCase() + s.slice(1)}</option>`).join("")}
          </select>
        </label>
      </article>`).join("") : `<p class="empty">No applications here yet.</p>`;
    const n = applications.filter((a) => a.status === "new").length;
    const badge = $("#app-count");
    badge.textContent = n;
    badge.hidden = !n;
  }

  $("#applications").addEventListener("change", async (e) => {
    const sel = e.target.closest("[data-app-status]");
    if (!sel) return;
    const id = Number(sel.dataset.appStatus);
    const a = applications.find((x) => x.id === id);
    const before = a.status;
    const { error } = await sb.from("applications").update({ status: sel.value }).eq("id", id);
    if (error) { sel.value = before; toast(friendly(error), true); return; }
    a.status = sel.value;
    renderApplications();
    toast(`${a.full_name}: ${a.status}`);
  });
  $$("[data-app]").forEach((chip) => chip.addEventListener("click", () => {
    appFilter = chip.dataset.app;
    $$("[data-app]").forEach((c) => c.setAttribute("aria-pressed", String(c === chip)));
    renderApplications();
  }));

  /* Sign in / out ---------------------------------------------------------- */

  const loginForm = $("#login-form");
  const loginMsg = $("#login-msg");

  function showLogin(message = "") {
    stopLive();
    knownOrderIds = null;
    $("#app").hidden = true;
    $("#login-view").hidden = false;
    loginMsg.textContent = message;
    document.title = "Admin · IyaBolaji";
  }

  async function enter() {
    const { data, error } = await sb.rpc("is_admin");
    if (error || data !== true) {
      await sb.auth.signOut();
      showLogin(error ? friendly(error) : "This account isn't an admin yet. Add it with the last step in supabase/setup.sql.");
      return;
    }
    $("#login-view").hidden = true;
    $("#app").hidden = false;
    const hash = location.hash.replace("#", "");
    selectTab(["menu", "applications"].includes(hash) ? `tab-${hash}` : "tab-orders");
    setLive("");
    await Promise.all([loadOrders(), loadDishes(), loadApplications()]);
    startLive();
  }

  loginForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    unlockAudio();
    const email = loginForm.elements.email.value.trim();
    const password = loginForm.elements.password.value;
    if (!email || !password) { loginMsg.textContent = "Enter your email and password."; return; }
    const btn = $("button[type=submit]", loginForm);
    btn.disabled = true;
    btn.textContent = "Signing in...";
    loginMsg.textContent = "";
    const { error } = await sb.auth.signInWithPassword({ email, password });
    btn.disabled = false;
    btn.textContent = "Sign in";
    if (error) { loginMsg.textContent = friendly(error); return; }
    loginForm.elements.password.value = "";
    await enter();
  });

  $("#sign-out").addEventListener("click", async () => {
    await sb.auth.signOut();
    showLogin("You're signed out.");
  });

  /* Start ------------------------------------------------------------------ */

  if (!C.supabaseUrl || !C.supabaseKey || !window.supabase) {
    $("#setup-notice").hidden = false;
    $$("input, button", loginForm).forEach((el) => { el.disabled = true; });
    return;
  }
  sb = window.supabase.createClient(C.supabaseUrl, C.supabaseKey, { auth: { persistSession: true, autoRefreshToken: true } });
  sb.auth.onAuthStateChange((event) => { if (event === "SIGNED_OUT" && !$("#app").hidden) showLogin("Your session ended. Please sign in again."); });
  sb.auth.getSession().then(({ data }) => { if (data.session) enter(); });
})();
