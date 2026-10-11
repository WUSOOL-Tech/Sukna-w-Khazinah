// build/report.html -> output/*.pdf via Playwright Chromium, with in-page layout QA.
// Usage: node scripts/render_pdf.cjs [report.html] [output.pdf]
const path = require('path');
const fs = require('fs');
let chromium;
try { ({ chromium } = require('playwright')); } catch (e) { ({ chromium } = require('/opt/node22/lib/node_modules/playwright')); }

const ROOT = path.resolve(__dirname, '..');
const htmlFile = path.resolve(ROOT, process.argv[2] || 'build/report.html');
const pdfFile = path.resolve(ROOT, process.argv[3] || 'output/WUSOOL_Sakna_Wa_Khazina_Performance_Report_2026.pdf');

const out_reg = qa => qa.register;
(async () => {
  const exe = fs.existsSync('/opt/pw-browsers/chromium') ? undefined : undefined;
  const browser = await chromium.launch(exe ? { executablePath: exe } : {});
  const page = await browser.newPage();
  await page.goto('file://' + htmlFile, { waitUntil: 'load' });
  await page.evaluate(() => document.fonts.ready);
  await page.emulateMedia({ media: 'print' });
  const qa = await page.evaluate(() => {
    const out = { pages: 0, overflow: [], escaped: [], cellOverflow: [], images: [], fonts: {} };
    const fams = ['Changa', 'IBM Plex Sans Arabic', 'Almarai'];
    for (const f of fams) out.fonts[f] = document.fonts.check(`700 12px "${f}"`) && [...document.fonts].some(x => x.family.replace(/"/g, '') === f && x.status === 'loaded');
    document.querySelectorAll('img').forEach(im => { if (!im.complete || im.naturalWidth === 0) out.images.push(im.getAttribute('src')); });
    document.querySelectorAll('section.sheet').forEach(sh => {
      out.pages++;
      const n = sh.dataset.page;
      const body = sh.querySelector('.body');
      if (body) {
        if (body.scrollHeight > body.clientHeight + 1) out.overflow.push({ page: n, by: body.scrollHeight - body.clientHeight });
        const br = body.getBoundingClientRect();
        body.querySelectorAll('*').forEach(el => {
          const r = el.getBoundingClientRect();
          if (r.width === 0 && r.height === 0) return;
          if (el.closest('svg') && el.tagName.toLowerCase() !== 'svg') return;
          if (r.bottom > br.bottom + 0.5 || r.left < br.left - 0.5 || r.right > br.right + 0.5)
            out.escaped.push({ page: n, el: el.tagName + '.' + el.className, text: (el.textContent || '').trim().slice(0, 40), dy: Math.round(r.bottom - br.bottom), dl: Math.round(br.left - r.left), dr: Math.round(r.right - br.right) });
        });
      }
      const pr = sh.getBoundingClientRect();
      sh.querySelectorAll('img, .run-foot, .run-head').forEach(el => {
        const r = el.getBoundingClientRect();
        if (r.bottom > pr.bottom + 0.5 || r.top < pr.top - 0.5 || r.left < pr.left - 0.5 || r.right > pr.right + 0.5)
          out.escaped.push({ page: n, el: el.tagName + '.' + el.className, text: 'outside sheet' });
      });
      sh.querySelectorAll('td, th').forEach(td => {
        if (td.scrollWidth > td.clientWidth + 1) out.cellOverflow.push({ page: n, text: td.textContent.trim().slice(0, 40), by: td.scrollWidth - td.clientWidth });
      });
    });
    // register metrics for measured pagination (mm)
    const PX = 96 / 25.4;
    out.register = { rows: {}, avail_first: null, avail_next: null };
    document.querySelectorAll('tr[data-seq]').forEach(tr => { out.register.rows[tr.dataset.seq] = +(tr.getBoundingClientRect().height / PX).toFixed(3); });
    document.querySelectorAll('table[data-reg]').forEach(t => {
      const body = t.closest('.body'), tb = t.querySelector('tbody'), note = body.querySelector('.regnote');
      const nr = note.getBoundingClientRect(), cs = getComputedStyle(note);
      const avail = (body.getBoundingClientRect().bottom - tb.getBoundingClientRect().top - nr.height - parseFloat(cs.marginTop)) / PX;
      if (t.dataset.reg === '0') out.register.avail_first = +avail.toFixed(3); else if (out.register.avail_next === null) out.register.avail_next = +avail.toFixed(3);
    });
    return out;
  });
  if (htmlFile.endsWith('report.html')) fs.writeFileSync(path.join(ROOT, 'build', 'register_metrics.json'), JSON.stringify(out_reg(qa)));
  fs.mkdirSync(path.dirname(pdfFile), { recursive: true });
  await page.pdf({ path: pdfFile, preferCSSPageSize: true, printBackground: true, displayHeaderFooter: false });
  await browser.close();
  fs.writeFileSync(path.join(ROOT, 'build', path.basename(pdfFile, '.pdf') + '.layout-qa.json'), JSON.stringify(qa, null, 1));
  const bad = qa.overflow.length + qa.escaped.length + qa.cellOverflow.length + qa.images.length + Object.values(qa.fonts).filter(x => !x).length;
  console.log(`pages=${qa.pages} overflow=${qa.overflow.length} escaped=${qa.escaped.length} cellOverflow=${qa.cellOverflow.length} brokenImages=${qa.images.length} fonts=${JSON.stringify(qa.fonts)}`);
  if (bad) { console.log(JSON.stringify({ overflow: qa.overflow, escaped: qa.escaped.slice(0, 40), cellOverflow: qa.cellOverflow.slice(0, 40), images: qa.images }, null, 1)); process.exitCode = 2; }
})();
