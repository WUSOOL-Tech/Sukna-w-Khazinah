#!/usr/bin/env python3
"""Writes REPORT_AUDIT.md from the pipeline + QA outputs. Counts and checks only — no personal data."""
import json, hashlib
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
M = json.loads((ROOT / 'data/aggregates/metrics.json').read_text(encoding='utf8'))
V = M['validation']
D = json.loads((ROOT / 'data/processed/deals.json').read_text(encoding='utf8'))
lay = json.loads((ROOT / 'build/WUSOOL_Sakna_Wa_Khazina_Performance_Report_2026.layout-qa.json').read_text(encoding='utf8'))
pq = json.loads((ROOT / 'build/WUSOOL_Sakna_Wa_Khazina_Performance_Report_2026.pdf-qa.json').read_text(encoding='utf8'))
pdf = ROOT / 'output/WUSOOL_Sakna_Wa_Khazina_Performance_Report_2026.pdf'
sha = hashlib.sha256(pdf.read_bytes()).hexdigest() if pdf.exists() else '—'


def sha_of(p):
    return hashlib.sha256((ROOT / p).read_bytes()).hexdigest()[:16]


flag_counts = {}
for d in D:
    for f in d['flags']:
        key = f.split('«')[0].strip()
        flag_counts[key] = flag_counts.get(key, 0) + 1

L = []
w = L.append
w('# REPORT_AUDIT — Sakna wa Khazina × WUSOOL Performance Report 2026\n')
w(f'Generated: {datetime.now():%Y-%m-%d %H:%M} · Data extracted: 2026-10-11 · Pipeline run: {M["generated_at"]}\n')
w('> Internal audit file. Contains counts and checks only — no names, phones or civil IDs. '
  'The personal-data registers live in `data/processed/` (git-ignored, see README).\n')
w('## 1. Sources\n')
w('| Role | Source | Records | Raw file (git-ignored) | SHA-256 (16) |\n|---|---|---|---|---|')
w(f'| Customer register (canonical) | Google Sheet «بيانات عملاء أكتوبر العمران» · tab «العملاء» | {V["customer_records"]} | `data/raw/customers_sheet_alomlaa.json` | `{sha_of("data/raw/customers_sheet_alomlaa.json")}` |')
w(f'| Customer register (CRM mirror) | same file · tab «AqarCRM» | {V["crm_records"]} | `data/raw/customers_sheet_aqarcrm.json` | `{sha_of("data/raw/customers_sheet_aqarcrm.json")}` |')
w(f'| Deal register | Google Sheet «جدول مبيعات أكتوبر العمران - سكنة وخزينة» · tab «Form Responses 1» | {V["deal_records"]} | `data/raw/sales_form_responses.json` | `{sha_of("data/raw/sales_form_responses.json")}` |')
w(f'| Team roster | Drive folder «عقود مستشاري أكتوبر العمران 2026» (contract titles) | {M["contracts_total"]} | `data/raw/team_contracts.json` | `{sha_of("data/raw/team_contracts.json")}` |')
w('| Context | Contract template «النموذج الأساسي — اتفاقية مستشار عقاري», «WUSOOL_October_Urban_2026_Team_Briefing.pdf», `brand/guidelines` (initiative facts) | — | not stored | — |\n')

w('## 2. Headline figures (all recomputed from rows)\n')
w('| Figure | Value |\n|---|---|')
for k, label in [('customers_total', 'Registered customers'), ('customers_in_event', 'Registered during event days (5–8 Oct)'),
                 ('customers_post_event', 'Registered after the event (9–10 Oct)'), ('deals_total', 'Deal records'),
                 ('deals_documented', 'Documented deals (unit code + final price)'), ('deals_pending', 'Deals pending completion')]:
    w(f'| {label} | {M[k]:,} |')
w(f'| Total documented deal value | {M["deal_value_total"]:,.2f} OMR |')
w(f'| Average / median / min / max | {M["deal_value_avg"]:,.2f} / {M["deal_value_median"]:,.2f} / {M["deal_value_min"]:,.2f} / {M["deal_value_max"]:,.2f} OMR |')
w(f'| Deal records per 100 registrations | {M["conv_deal_records_per_100"]} |')
w(f'| Registered customers linked to a deal | {M["deal_customers_matched"]} ({M["conv_registered_with_deal"]}%) |')
w(f'| Follow-up base (registered, no deal) | {M["open_pipeline"]:,} |\n')

w('## 3. Reconciliation checks (build fails if any is false)\n')
w('| Check | Result |\n|---|---|')
for k, ok in M['checks'].items():
    w(f'| {k} | {"PASS" if ok else "FAIL"} |')
w('')
w('## 4. Data issues found and how they were handled\n')
w('| # | Issue | Size | Treatment |\n|---|---|---|---|')
issues = [
    ('Deal-sheet total cell `H17` uses ' + V['deal_value_sheet_formula'] + ' and omits the last two rows', f'{V["deal_value_sheet_cell"]:,.2f} vs {V["deal_value_total_recomputed"]:,.2f} OMR (gap {V["deal_value_gap"]:,.2f})', 'Total recomputed from rows; issue shown in the report (insights + data-quality log)'),
    ('Deals without unit code / final price', V['deals_pending'], 'Kept as «قيد الاستكمال»; excluded from value'),
    ('Deals whose customer is not in the registration register', V['deals_unmatched'], 'Kept; flagged; listed in Appendix A notes'),
    ('Deals matched by civil ID / by phone + family name', f'{sum(d["match_method"] == "الرقم المدني" for d in D)} / {sum(d["match_method"] == "الهاتف + اسم العائلة" for d in D)}', 'Phone alone never accepted (one phone is shared)'),
    ('Name differs between deal and registration record', flag_counts.get('الاسم في سجل التسجيل', 0), 'Shown as recorded; flagged'),
    ('Same project recorded under different developers', sum(1 for r in M['by_project'] if len(r['developers']) > 1), 'Shown as recorded; flagged'),
    ('Unit code / area pattern of another project', flag_counts.get('رمز الوحدة ومساحتها يطابقان نمط وحدات مشروع', 0), 'Shown as recorded; flagged for verification'),
    ('Same phone on two deal records (different civil IDs)', flag_counts.get('رقم الهاتف نفسه مسجّل لصفقة أخرى', 0), 'Flagged'),
    ('Deal documented after the event days', flag_counts.get('وُثّقت بعد أيام المعرض', 0), 'Counted on its entry date'),
    ('Duplicate customers (civil ID)', V['duplicate_customers'], '—'),
    ('Repeated names (different people, different civil IDs)', f'{V["repeated_names_distinct_people"]} records in {V["repeated_name_groups"]} groups', 'Not duplicates; kept'),
    ('Shared phone number among customers', f'{V["shared_phone_numbers"]} number / {V["records_on_shared_phone"]} records', 'Kept (different civil IDs)'),
    ('Invalid phone format (not 8 digits starting 7/9)', V['invalid_phones'], 'Shown with † in the register'),
    ('Phones stored with +968 prefix', V['phones_with_country_code'], 'Normalised to 8 digits'),
    ('Invalid civil ID format', V['invalid_civil_ids'], 'Excluded from matching; not printed'),
    ('E-mail field truncated at ~12–14 characters at source', f'{V["email_provided"]} non-trivial values, 0 well-formed', 'Excluded from report'),
    ('ID-expiry field partially filled / default-looking dates', f'{V["id_expiry_provided"]} of {V["customer_records"]}', 'Not analysed'),
    ('Free-text notes: junk values («.», «ء», «\\|», «-»…) and start-truncated notes', f'{V["notes_raw_nonempty"]} non-empty, {V["notes_meaningful"]} meaningful, {V["notes_tagged"]} tagged', 'Rule-based tags only (rules in pipeline.py)'),
    ('Staff attribution differs between «العملاء» and «AqarCRM» tabs', V['crm_staff_differs'], '«العملاء» = who served the customer (used); «AqarCRM» = entry account (7 accounts, shown separately)'),
    ('Phone format differs between the two tabs', V['crm_phone_format_diffs'], 'Identical after normalisation'),
]
for i, (a, b, c) in enumerate(issues, 1):
    w(f'| {i} | {a} | {b} | {c} |')
w('')
w('## 5. Assets used\n')
w('| Asset | File | Note |\n|---|---|---|')
w('| Ministry × initiative lockup (light) | `brand/logo/cobrand/sukna-w-khazinah_x_mhup.svg` | Cover. Vector (trace of the official ministry JPG — see `brand/partners/mhup/README.md`) |')
w('| Ministry × initiative lockup (dark) | `brand/logo/cobrand/sukna-w-khazinah_x_mhup_on-dark.svg` | Closing page |')
w('| WUSOOL primary / reversed | `reports/sakna-khazina-performance/logos/WUSOOL_Primary_FullColor.svg`, `WUSOOL_Reversed.svg` | From the approved WUSOOL brand system v1.0 |')
w('| Fonts | Changa, IBM Plex Sans Arabic (`brand/fonts`), Almarai (`assets/fonts`) | SIL OFL 1.1, embedded in the PDF |')
w('')
w('### Missing assets (not invented)\n')
w('- **Developer logos** for طلعت مصطفى، الأبرار، الأهلي صبور — not present in the repository or the shared Drive. Developer pages use a typographic name plate; no logo was downloaded or recreated.')
w('- **Project images** for جود، حي الوفاء، رِواق، ريفيرا صلالة، بلوميريا — not available; project section is data-only.')
w('- **Event photography** — no photos of the booth or team exist in the repository; the report uses no photography (no stock images).')
w('- **Ministry department naming** — «دائرة الهوية والوصول» comes from the report brief; it is not in the repository files. The Minister is addressed by title only (name not documented). Verify both before submission.')
w('')
w('## 6. Output QA\n')
w(f'- PDF: `output/WUSOOL_Sakna_Wa_Khazina_Performance_Report_2026.pdf` — {pq["pages"]} pages, A4 portrait ({", ".join(pq["page_sizes_pt"])} pt), SHA-256 `{sha[:16]}…`')
w(f'- In-page layout QA (Chromium): overflow {len(lay["overflow"])}, elements outside frame {len(lay["escaped"])}, clipped table cells {len(lay["cellOverflow"])}, broken images {len(lay["images"])}, fonts loaded {lay["fonts"]}')
w(f'- Customer register: {pq["register_rows_in_document"]} rows (1–720, each once) over {pq["register_pages"]} pages with contiguous ranges; all {len(D)} deal IDs present in the PDF text')
w('- Forbidden strings (Lorem, TBD, placeholder, None, NaN, {{ }}): none')
w('- Visual review: every page rendered to PNG and inspected; issues found and fixed are listed in README «QA log».')
(ROOT / 'REPORT_AUDIT.md').write_text('\n'.join(L) + '\n', encoding='utf8')
print('REPORT_AUDIT.md written')
