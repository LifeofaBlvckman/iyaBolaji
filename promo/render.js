// Capture every frame: node render.js <html> <outdir> <fps> <duration_s>
const { chromium } = require('playwright');
(async () => {
  const [,, html, out, fps, dur] = process.argv;
  const browser = await chromium.launch({ proxy: { server: process.env.HTTPS_PROXY, bypass: '127.0.0.1,localhost' } });
  const page = await browser.newPage({ viewport: { width: 1080, height: 1080 } });
  page.on('pageerror', e => console.error('PAGEERROR', e.message));
  await page.goto('file://' + require('path').resolve(html), { waitUntil: 'networkidle' });
  await page.evaluate(() => document.fonts.ready);
  await page.evaluate(async () => { await Promise.all([...document.images].map(i => i.decode().catch(() => {}))); });
  const n = Math.round(Number(fps) * Number(dur));
  const from = Number(process.argv[6] || 0);
  for (let f = from; f < n; f++) {
    await page.evaluate((t) => window.render(t), f / Number(fps));
    await page.screenshot({ path: `${out}/${String(f).padStart(5, '0')}.png` });
    if (f % 100 === 0) console.log('frame', f, 'of', n);
  }
  console.log('done', n, 'frames');
  await browser.close();
})();
