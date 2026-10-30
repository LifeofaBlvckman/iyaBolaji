// Rasterise the SVG dish illustrations in assets/art to WebP. The site uses the
// WebPs: they are smaller and much cheaper for phones to draw than the SVGs.
// Run after tools/make_art.py:  node tools/export_art.js  (needs Playwright)
const fs = require("fs");
const path = require("path");
const { chromium } = require("playwright");

const dir = path.join(__dirname, "..", "assets", "art");
const SIZE = 560; // longest side in pixels: sharp at 2x for the 280px cards

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  for (const file of fs.readdirSync(dir).filter((f) => f.endsWith(".svg"))) {
    const svg = fs.readFileSync(path.join(dir, file), "utf8");
    const dataUrl = await page.evaluate(async ({ svg, size }) => {
      const img = new Image();
      img.src = "data:image/svg+xml;base64," + btoa(unescape(encodeURIComponent(svg)));
      await img.decode();
      const scale = size / Math.max(img.naturalWidth, img.naturalHeight);
      const canvas = document.createElement("canvas");
      canvas.width = Math.round(img.naturalWidth * scale);
      canvas.height = Math.round(img.naturalHeight * scale);
      canvas.getContext("2d").drawImage(img, 0, 0, canvas.width, canvas.height);
      return canvas.toDataURL("image/webp", 0.78);
    }, { svg, size: SIZE });
    const out = path.join(dir, file.replace(/\.svg$/, ".webp"));
    fs.writeFileSync(out, Buffer.from(dataUrl.split(",")[1], "base64"));
    console.log("wrote", path.basename(out), Math.round(fs.statSync(out).size / 1024) + " KB");
  }
  await browser.close();
})();
