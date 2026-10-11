// Render single frames for review: node scripts/still.cjs out_dir t1 t2 ...
const path = require('path'); const fs = require('fs');
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
(async () => {
  const [out, ...ts] = process.argv.slice(2); fs.mkdirSync(out, { recursive: true });
  const b = await chromium.launch(); const v = process.env.FMT === '9x16'; const p = await b.newPage({ viewport: { width: v ? 1080 : 1920, height: v ? 1920 : 1080 } });
  p.on('console', m => { if (m.type() === 'error') console.log('console:', m.text()); });
  p.on('pageerror', e => console.log('pageerror:', e.message));
  await p.goto('file://' + path.resolve(__dirname, v ? '../src/composition_9x16.html' : '../src/composition.html'));
  await p.evaluate(() => window.ready);
  for (const t of ts) { await p.evaluate(t => window.render(t), parseFloat(t)); await p.screenshot({ path: path.join(out, `t${String(t).padStart(6, '0')}.png`) }); }
  await b.close();
})();
