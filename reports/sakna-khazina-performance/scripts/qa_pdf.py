#!/usr/bin/env python3
"""PDF-level QA: page geometry, page count, register completeness (all 720 sequence numbers and all deal IDs
present in the extracted text), no placeholder strings, and a contact sheet of every page for visual review."""
import json, re, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
pdf = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / 'output/WUSOOL_Sakna_Wa_Khazina_Performance_Report_2026.pdf'
bleed = 'Bleed' in pdf.name
M = json.loads((ROOT / 'data/aggregates/metrics.json').read_text(encoding='utf8'))
D = json.loads((ROOT / 'data/processed/deals.json').read_text(encoding='utf8'))
info = json.loads((ROOT / 'build/build_info.json').read_text(encoding='utf8'))
res, fails = {}, []

out = subprocess.run(['pdfinfo', '-f', '1', '-l', '999', str(pdf)], capture_output=True, text=True).stdout
pages = int(re.search(r'Pages:\s+(\d+)', out).group(1))
sizes = set(re.findall(r'Page\s+\d+ size:\s+([\d.]+ x [\d.]+)', out))
res['pages'] = pages
res['page_sizes_pt'] = sorted(sizes)
want = (216 if bleed else 210) / 25.4 * 72, (303 if bleed else 297) / 25.4 * 72
for sz in sizes:
    w, h = map(float, sz.split(' x '))
    if abs(w - want[0]) > 1 or abs(h - want[1]) > 1:
        fails.append(f'page size {sz} != {want[0]:.1f} x {want[1]:.1f} (portrait)')
if pages != info['pages']:
    fails.append(f'pdf pages {pages} != html pages {info["pages"]}')

txt = subprocess.run(['pdftotext', '-layout', str(pdf), '-'], capture_output=True, text=True).stdout
pages_txt = txt.split('\f')
# Arabic lam-alef ligatures are extracted out of order by pdftotext, so locate register pages by their
# Latin/number markers: each register page prints its record range "a–b … 720".
ranges = sorted({(int(a), int(b)) for a, b in re.findall(r'(\d+)–(\d+)\D{0,12}720', txt)})
res['register_pages'] = len(ranges)
cover, nxt = [], 1
for a, b in ranges:
    if a != nxt:
        fails.append(f'register range gap/overlap at {a} (expected {nxt})')
    nxt = b + 1
if nxt != M['customers_total'] + 1:
    fails.append(f'register ranges end at {nxt - 1}, expected {M["customers_total"]}')
html = (ROOT / 'build' / ('report_bleed.html' if bleed else 'report.html')).read_text(encoding='utf8')
seqs = [int(x) for x in re.findall(r'<tr data-seq="(\d+)"', html)]
res['register_rows_in_document'] = len(seqs)
if sorted(seqs) != list(range(1, M['customers_total'] + 1)):
    fails.append('register rows are not exactly 1..720 once each')
if res['register_pages'] != info['register_pages']:
    fails.append(f'register pages in PDF {res["register_pages"]} != built {info["register_pages"]}')
missing_deals = [d['deal_id'] for d in D if d['deal_id'] not in txt]
res['deal_ids_missing'] = missing_deals
if missing_deals:
    fails.append(f'deal ids missing: {missing_deals}')
for bad in [r'Lorem', r'\bTBD\b', r'Coming soon', r'placeholder', r'\{\{', r'\}\}', r'\bNone\b', r'\bnan\b', r'\bundefined\b', r'\bNaN\b']:
    if re.search(bad, txt):
        fails.append(f'forbidden string in PDF text: {bad!r}')
for must in [f"{M['deal_value_total']:,.2f}", f"{M['customers_total']}", 'Performance Report 2026', 'H2:H13']:
    if must not in txt:
        fails.append(f'expected text not found: {must}')

# contact sheet for visual review
sheet_dir = ROOT / 'build/qa'
sheet_dir.mkdir(parents=True, exist_ok=True)
for f in sheet_dir.glob('p-*.png'):
    f.unlink()
subprocess.run(['pdftoppm', '-r', '28', '-png', str(pdf), str(sheet_dir / 'p')], check=True)
subprocess.run(['montage', *sorted(str(f) for f in sheet_dir.glob('p-*.png')), '-tile', '8x', '-geometry', '+4+4', '-background', '#9aa',
                str(sheet_dir / ('contact_sheet_bleed.png' if bleed else 'contact_sheet.png'))], check=True)
res['fails'] = fails
(ROOT / 'build' / (pdf.stem + '.pdf-qa.json')).write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding='utf8')
print(json.dumps(res, ensure_ascii=False))
sys.exit(1 if fails else 0)
