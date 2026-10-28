const { chromium } = require('playwright');
const path = require('path');
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 794, height: 1123 }, deviceScaleFactor: 1.5 });
  await p.goto('file://' + path.resolve(__dirname, 'catalogo.html'));
  await p.evaluate(() => document.fonts.ready);
  await p.pdf({ path: path.resolve(__dirname, 'Catalogo-SDV.pdf'), width: '210mm', height: '297mm', printBackground: true });
  const n = await p.locator('.page').count();
  for (let i = 0; i < n; i++) await p.locator('.page').nth(i).screenshot({ path: `/tmp/claude-0/-home-user-Claude/541e5d39-7122-5a81-ade8-2c04752d55f4/scratchpad/p${i + 1}.png` });
  await b.close();
})();
