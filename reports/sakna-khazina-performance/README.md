# تقرير الأداء — مبادرة «سكنة وخزينة» × وصول للاستثمار
**Official Performance Report 2026 · WUSOOL team at the «Sukna w Khazinah» booth, October Urban (أكتوبر العمران) 2026, 5–8 Oct**

An Arabic-first, A4-portrait, print-ready PDF documenting the WUSOOL team's work at the Ministry of Housing and Urban Planning's booth for the initiative. It covers 720 registered customers, 14 deal records (8 documented, 466,367.50 OMR), and full customer and deal registers. Every figure is computed from the source rows by a reproducible pipeline.

> **Confidential — official use.** The report and its registers contain personal data (names, phones). **This repository is public**, so the raw exports, the processed registers, the generated charts and HTML, and the PDFs are **git-ignored on purpose** (see `.gitignore`). Only the code, styles, approved brand assets and audit-level documentation (counts only) are versioned. Keep the PDF inside official channels.

## Deliverables (generated locally by `scripts/build.sh`)
| Path | What | Versioned |
|---|---|---|
| `output/WUSOOL_Sakna_Wa_Khazina_Performance_Report_2026.pdf` | **Final PDF**, A4 portrait 210 × 297 mm | no (personal data) |
| `output/WUSOOL_Sakna_Wa_Khazina_Performance_Report_2026_Print_3mm-Bleed.pdf` | Print version, 216 × 303 mm (3 mm bleed) — `BLEED=1` | no |
| `data/processed/customers.csv` · `deals.csv` (+ `.json`) | Normalised full customer register (720) and deal register (14) | no |
| `data/aggregates/metrics.json` · `validation.json` | Every number printed in the report + validation results | no (names consultants) |
| `charts/*.svg` | Every chart in the report as standalone SVG | no |
| `build/report.html` | Source HTML of the PDF | no |
| `build/qa/contact_sheet.png` · `build/*.layout-qa.json` · `build/*.pdf-qa.json` | Visual and automated QA outputs | no |
| [`REPORT_AUDIT.md`](REPORT_AUDIT.md) | Sources, counts, checks, data issues, assets, QA (no personal data) | **yes** |
| [`DATA_SOURCES.md`](DATA_SOURCES.md) · [`REPORT_METHODOLOGY.md`](REPORT_METHODOLOGY.md) | Data inventory and methodology | **yes** |

## Rebuild
Requirements: Python 3.10+ (stdlib only), Node 18+ with Playwright and Chromium, poppler-utils (`pdfinfo`, `pdftotext`, `pdftoppm`) and ImageMagick (`montage`) for QA.

1. Place the raw exports in `data/raw/`, using the file names listed in [`DATA_SOURCES.md`](DATA_SOURCES.md). Each is the Sheets API `values` JSON of the named tab: `{"values": [[...], ...]}`.
2. Run:
   ```bash
   cd reports/sakna-khazina-performance
   ./scripts/build.sh              # A4 PDF
   BLEED=1 ./scripts/build.sh      # + 3 mm-bleed print PDF
   ```

The pipeline runs these steps:

| Step | Script | Fails the build when |
|---|---|---|
| Normalize → validate → reconcile → calculate | `scripts/pipeline.py` | Any breakdown (by developer, project, consultant or day) does not sum to the total, the customer count is not 720, a civil ID is duplicated, or a deal is duplicated |
| Charts + HTML (pass 1) | `scripts/build_report.py` | — |
| Measure | `scripts/render_pdf.cjs` | — (records real register row heights to `build/register_metrics.json`) |
| Charts + HTML (pass 2) | `scripts/build_report.py` | — (paginates the 720-row register on measured heights, so no row is ever clipped) |
| Render PDF + layout QA | `scripts/render_pdf.cjs` | Content overflows a page, an element leaves the frame, a table cell is clipped, an image is broken, or a font is missing |
| PDF QA | `scripts/qa_pdf.py` | A page is not A4 portrait, register rows 1–720 are missing or out of order, a deal ID is missing, or placeholder text is present |
| Audit | `scripts/write_audit.py` | — (writes `REPORT_AUDIT.md`) |

`scripts/peek.sh <pdf> <dir> <dpi> <pages…>` renders pages to PNG for manual review.

## Stack and design decisions
- **HTML/CSS → PDF with Playwright/Chromium.** It gives the best Arabic shaping, real RTL, SVG, `@font-face` embedding and exact page size. Every page is a fixed 210 × 297 mm frame, and pagination is computed, not left to the browser. That makes running headers, footers and page numbers deterministic, and repeats register headers on every page.
- **Identity.** «سكنة وخزينة» and the Ministry lead: the co-brand lockup, Ink, the Sukna green ascent rule (7.5°), the Khazinah yellow band and dividers, and Changa with IBM Plex Sans Arabic. WUSOOL is the issuing partner: its logo on the cover, letters and closing, the Almarai attribution in the footer, and its Midnight, Aquamarine and Marigold palette in the charts.
- **RTL charts.** Categories and time read right to left, and bars grow from a right-hand baseline. Latin digits are isolated LTR («10%», «13:00», «9949 9232»), and ranges and ratios are single LTR tokens.
- **Privacy in the PDF.** Civil IDs are masked to the last three digits in the deal register and omitted from the customer register. E-mails are not printed.

## QA log (visual review — issues found and fixed)
1. Customer register rows were clipped at the page foot (the estimated row height was too small). Fixed by two-pass measured pagination.
2. The contents page overflowed. Fixed by compacting the spacing.
3. The deals KPI row was too wide and pushed one KPI off the page. Fixed with a weighted grid.
4. A strip plot overlapped 54,000 and 54,237. Replaced by one bar per deal.
5. Time ranges and ratios rendered in reversed order under RTL («21:57 – 11:16», «14/9»). Each is now a single LTR token or written as «9 من 14».
6. Chart labels rounded 70,591.50 to 70,592. All rial values now show two decimals everywhere.
7. The WUSOOL logo sat on fluorescent yellow on the cover. The band was lowered so the logo sits on paper.
8. Timeline date circles were unreadable. Replaced by date chips.
9. Marigold was used as a category colour in the donut. It is now kept for highlights only.
10. `BLEED=1 ./scripts/build.sh` leaked `BLEED` into the A4 passes, so the A4 PDF was rendered from stale HTML. The A4 passes now pin `BLEED=0`.
11. The last register page held only 6 rows. Pagination now finds the smallest page capacity that keeps the minimum page count, so rows spread evenly (35–41 per page).
