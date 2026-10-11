#!/usr/bin/env bash
# Rebuild the report end to end:
#   raw data -> normalize/validate/reconcile/calculate -> charts + HTML -> measure -> paginate -> PDF -> QA
set -euo pipefail
cd "$(dirname "$0")/.."
python3 scripts/pipeline.py                      # data/processed + data/aggregates (fails on any reconciliation gap)
rm -f build/register_metrics.json
BLEED=0 python3 scripts/build_report.py          # pass 1 (estimated register pagination)
node scripts/render_pdf.cjs >/dev/null || true   # measures real row heights -> build/register_metrics.json
BLEED=0 python3 scripts/build_report.py          # pass 2 (measured pagination)
node scripts/render_pdf.cjs                      # final A4 PDF + in-page layout QA (fails on overflow/clipping)
python3 scripts/qa_pdf.py                        # PDF geometry, completeness, forbidden strings, contact sheet
WANT_BLEED="${BLEED:-0}"
if [[ "$WANT_BLEED" == "1" ]]; then              # optional print version: 3 mm bleed on every side (216 x 303 mm)
  BLEED=1 python3 scripts/build_report.py
  node scripts/render_pdf.cjs build/report_bleed.html output/WUSOOL_Sakna_Wa_Khazina_Performance_Report_2026_Print_3mm-Bleed.pdf
  python3 scripts/qa_pdf.py output/WUSOOL_Sakna_Wa_Khazina_Performance_Report_2026_Print_3mm-Bleed.pdf
fi
python3 scripts/write_audit.py                   # REPORT_AUDIT.md (counts only)
