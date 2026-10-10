#!/usr/bin/env node
/* Render brand/guidelines/src/guidelines.html to the guidelines PDF (+ page previews).
 *
 *   NODE_PATH=$(npm root -g) node scripts/build_guidelines.cjs
 *
 * Run scripts/build_logo.py, build_tokens.py and render_motion.cjs first —
 * the guide embeds the master logo, tokens.css and the motion storyboard.
 */
const fs = require("fs");
const path = require("path");
const { chromium } = require("playwright");

const ROOT = path.resolve(__dirname, "..");
const SRC = path.join(ROOT, "brand/guidelines/src/guidelines.html");
const OUT = path.join(ROOT, "brand/guidelines");
const master = JSON.parse(fs.readFileSync(path.join(ROOT, "brand/logo/master/sukna-w-khazinah_master.json"), "utf8"));
const tokens = JSON.parse(fs.readFileSync(path.join(ROOT, "brand/design-system/tokens.flat.json"), "utf8"));

const W = master.width, H = master.height, f = n => n.toFixed(2);
const ink = "#0B2A1E";
const lightText = hex => {
  const n = parseInt(hex.slice(1), 16), r = n >> 16, g = (n >> 8) & 255, b = n & 255;
  return 0.2126 * r + 0.7152 * g + 0.0722 * b < 140;
};
const scale = name => Object.keys(tokens)
  .filter(k => k.startsWith(`color.${name}.`))
  .map(k => { const v = tokens[k], s = k.split(".").pop();
    return `<div style="background:${v};color:${lightText(v) ? "#fff" : ink}"><span class="mono">${s}<br>${v}</span></div>`; })
  .join("");
const spaceBars = Object.keys(tokens).filter(k => k.startsWith("space.") && k !== "space.0")
  .map(k => `<div style="display:flex;align-items:center;gap:3mm;margin-bottom:1.2mm"><span class="mono small" style="width:16mm">${k.slice(6)} · ${tokens[k]}</span><span style="height:3mm;width:${parseInt(tokens[k]) * 0.35}mm;background:var(--sk-color-brand-green)"></span></div>`)
  .join("");
const gridCols = Array.from({ length: 12 }, () => `<div style="background:var(--sk-color-green-100)"></div>`).join("");
const curve = (name, [x1, y1, x2, y2]) => {
  const P = v => 4 + v * 92, Q = v => 96 - v * 80; // fit overshoot inside the box
  return `<div><svg class="curve" viewBox="0 0 100 100" preserveAspectRatio="none">
    <rect width="100" height="100" fill="var(--sk-color-neutral-50)"/>
    <path d="M ${P(0)} ${Q(0)} C ${P(x1)} ${Q(y1)} ${P(x2)} ${Q(y2)} ${P(1)} ${Q(1)}" fill="none" stroke="${ink}" stroke-width="3" vector-effect="non-scaling-stroke"/>
  </svg><span class="mono small">${name} (${[x1, y1, x2, y2].join(", ")})</span></div>`;
};
const curves = ["standard", "ascend", "draw", "pop"]
  .map(n => curve(n, JSON.parse(JSON.stringify(require(path.join(ROOT, "brand/design-system/tokens.json")).motion.easing[n].$value))))
  .join("");

const symbol = master.paths.map(d => `<path fill="currentColor" d="${d}"/>`).join("");
const html = fs.readFileSync(SRC, "utf8")
  .replaceAll("{{MARK_SYMBOL}}", symbol)
  .replaceAll("{{MARK_VIEWBOX}}", `0 0 ${f(W)} ${f(H)}`)
  .replaceAll("{{MARK_W}}", f(W)).replaceAll("{{MARK_H}}", f(H))
  .replaceAll("{{CS_W}}", f(W + 220)).replaceAll("{{CS_H}}", f(H + 220))
  .replaceAll("{{CS_INNER_W}}", f(W + 144)).replaceAll("{{CS_INNER_H}}", f(H + 144))
  .replaceAll("{{MARK_W_P54}}", f(W + 54)).replaceAll("{{MARK_W_P18}}", f(W + 18)).replaceAll("{{MARK_H_P54}}", f(H + 54))
  .replaceAll("{{SCALE_GREEN}}", scale("green")).replaceAll("{{SCALE_YELLOW}}", scale("yellow") + "<div></div>")
  .replaceAll("{{SCALE_NEUTRAL}}", scale("neutral"))
  .replaceAll("{{SPACE_BARS}}", spaceBars).replaceAll("{{GRID_COLS}}", gridCols).replaceAll("{{CURVES}}", curves);

const built = path.join(path.dirname(SRC), "_built.html");
fs.writeFileSync(built, html);

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.goto("file://" + built, { waitUntil: "networkidle" });
  await page.evaluate(() => document.fonts.ready);
  await page.pdf({ path: path.join(OUT, "sukna-w-khazinah_brand-guidelines.pdf"), width: "297mm", height: "210mm", printBackground: true, preferCSSPageSize: true });
  if (process.argv.includes("--previews")) {
    const dir = process.argv[process.argv.indexOf("--previews") + 1];
    fs.mkdirSync(dir, { recursive: true });
    await page.setViewportSize({ width: 1123, height: 794 });
    const n = await page.$$eval("section.page", s => s.length);
    for (let i = 0; i < n; i++) {
      const el = (await page.$$("section.page"))[i];
      await el.screenshot({ path: path.join(dir, `p${String(i + 1).padStart(2, "0")}.png`) });
    }
  }
  await browser.close();
  fs.unlinkSync(built);
  console.log("guidelines PDF written");
})();
