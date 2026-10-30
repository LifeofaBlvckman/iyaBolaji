// Render the link-preview images (assets/og/*.jpg, 1200x630) and the iPhone
// home-screen icon (assets/apple-touch-icon.png) from tools/og.html.
// Run: node tools/export_og.js  (needs Playwright and internet for Google Fonts)
const fs = require("fs");
const path = require("path");
const { chromium } = require("playwright");

const pages = [
  { slug: "home", line1: "Smoky jollof.", line2: "Mama's touch.", img: "../assets/img/turkey.jpg", art: false, top: "Fried turkey", big: "₦7,000" },
  { slug: "menu", line1: "See the", line2: "full menu.", img: "../assets/art/jollof-enjoyment.webp", art: true, top: "Jollof from", big: "₦800" },
  { slug: "about", line1: "Our story.", line2: "Mama's pot.", img: "../assets/img/fish-pepper-stew.jpg", art: false, top: "Belle", big: "full" },
  { slug: "visit", line1: "Find us in", line2: "Ipaja, Lagos.", img: "../assets/img/turkey.jpg", art: false, top: "Open till", big: "11:59PM" },
];

(async () => {
  const proxy = process.env.HTTPS_PROXY ? { server: process.env.HTTPS_PROXY, bypass: "127.0.0.1,localhost" } : undefined;
  const browser = await chromium.launch({ proxy });
  const page = await browser.newPage({ viewport: { width: 1200, height: 900 } });
  await page.goto("file://" + path.join(__dirname, "og.html"), { waitUntil: "networkidle" });
  await page.evaluate(() => document.fonts.ready);

  const outDir = path.join(__dirname, "..", "assets", "og");
  fs.mkdirSync(outDir, { recursive: true });
  for (const p of pages) {
    await page.evaluate(async (p) => {
      document.getElementById("line1").textContent = p.line1;
      document.getElementById("line2").textContent = p.line2;
      document.getElementById("sticker-top").textContent = p.top;
      document.getElementById("sticker-big").textContent = p.big;
      const img = document.getElementById("plate");
      img.classList.toggle("art", p.art);
      img.src = p.img;
      await img.decode();
    }, p);
    const out = path.join(outDir, `${p.slug}.jpg`);
    await page.locator("#card").screenshot({ path: out, type: "jpeg", quality: 84 });
    console.log("wrote", path.relative(process.cwd(), out), Math.round(fs.statSync(out).size / 1024) + " KB");
  }

  const icon = path.join(__dirname, "..", "assets", "apple-touch-icon.png");
  await page.locator("#icon").screenshot({ path: icon });
  console.log("wrote", path.relative(process.cwd(), icon), Math.round(fs.statSync(icon).size / 1024) + " KB");
  await browser.close();
})();
