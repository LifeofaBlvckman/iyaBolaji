// Export the logo lockup to PNGs: node tools/export_logos.js  (needs Playwright + network for Google Fonts)
const path = require("path");
const { chromium } = require("playwright");

const variants = [
  { file: "iyabolaji-logo-on-red.png", word: "#fdf0dc", mark: "#141211", bg: "#d9151d" },
  { file: "iyabolaji-logo-on-cream.png", word: "#d9151d", mark: "#141211", bg: "#fdf0dc" },
  { file: "iyabolaji-logo-on-black.png", word: "#fdf0dc", mark: "#d9151d", bg: "#141211" },
  { file: "iyabolaji-logo-transparent.png", word: "#d9151d", mark: "#141211", bg: null },
];

(async () => {
  const proxy = process.env.HTTPS_PROXY ? { server: process.env.HTTPS_PROXY, bypass: "127.0.0.1,localhost" } : undefined;
  const browser = await chromium.launch({ proxy });
  const page = await browser.newPage({ deviceScaleFactor: 2 });
  await page.goto("file://" + path.join(__dirname, "logo.html"), { waitUntil: "networkidle" });
  await page.evaluate(() => document.fonts.ready);
  for (const v of variants) {
    await page.evaluate(({ word, mark, bg }) => {
      document.querySelector(".word").style.color = word;
      document.querySelector(".mark").style.color = mark;
      document.querySelector("#lockup").style.background = bg || "transparent";
    }, v);
    await page.locator("#lockup").screenshot({ path: path.join(__dirname, "..", "assets", "brand", v.file), omitBackground: !v.bg });
    console.log("wrote", v.file);
  }
  await browser.close();
})();
