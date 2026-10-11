# REPORT_AUDIT — Sakna wa Khazina × WUSOOL Performance Report 2026

Generated: 2026-10-11 13:36 · Data extracted: 2026-10-11 · Pipeline run: 2026-10-11 13:35

> Internal audit file. Contains counts and checks only — no names, phones or civil IDs. The personal-data registers live in `data/processed/` (git-ignored, see README).

## 1. Sources

| Role | Source | Records | Raw file (git-ignored) | SHA-256 (16) |
|---|---|---|---|---|
| Customer register (canonical) | Google Sheet «بيانات عملاء أكتوبر العمران» · tab «العملاء» | 720 | `data/raw/customers_sheet_alomlaa.json` | `fc1763481c9f60cf` |
| Customer register (CRM mirror) | same file · tab «AqarCRM» | 720 | `data/raw/customers_sheet_aqarcrm.json` | `2da7089d011975b4` |
| Deal register | Google Sheet «جدول مبيعات أكتوبر العمران - سكنة وخزينة» · tab «Form Responses 1» | 14 | `data/raw/sales_form_responses.json` | `98f7fb61c24a21b6` |
| Team roster | Drive folder «عقود مستشاري أكتوبر العمران 2026» (contract titles) | 22 | `data/raw/team_contracts.json` | `f7c45a08a259909c` |
| Context | Contract template «النموذج الأساسي — اتفاقية مستشار عقاري», «WUSOOL_October_Urban_2026_Team_Briefing.pdf», `brand/guidelines` (initiative facts) | — | not stored | — |

## 2. Headline figures (all recomputed from rows)

| Figure | Value |
|---|---|
| Registered customers | 720 |
| Registered during event days (5–8 Oct) | 697 |
| Registered after the event (9–10 Oct) | 23 |
| Deal records | 14 |
| Documented deals (unit code + final price) | 8 |
| Deals pending completion | 6 |
| Total documented deal value | 466,367.50 OMR |
| Average / median / min / max | 58,295.94 / 54,237.00 / 54,000.00 / 70,591.50 OMR |
| Deal records per 100 registrations | 1.94 |
| Registered customers linked to a deal | 11 (1.53%) |
| Follow-up base (registered, no deal) | 709 |

## 3. Reconciliation checks (build fails if any is false)

| Check | Result |
|---|---|
| by_developer: value sum = total | PASS |
| by_developer: deal count sum = total | PASS |
| by_project: value sum = total | PASS |
| by_project: deal count sum = total | PASS |
| by_consultant: value sum = total | PASS |
| by_consultant: deal count sum = total | PASS |
| by_day: value sum = total | PASS |
| by_day: deals sum = total | PASS |
| by_day: registrations sum = 720 | PASS |
| by_hour: sum = in-event registrations | PASS |
| heatmap: sum = in-event registrations | PASS |
| solo + shared = 720 | PASS |
| price bands cover documented deals | PASS |
| customer count = 720 | PASS |
| customer civil IDs unique | PASS |
| CRM mirror: same civil IDs | PASS |
| no duplicate deals | PASS |
| documented + pending = deals | PASS |

## 4. Data issues found and how they were handled

| # | Issue | Size | Treatment |
|---|---|---|---|
| 1 | Deal-sheet total cell `H17` uses =SUM(H2:H13) and omits the last two rows | 357,893.50 vs 466,367.50 OMR (gap 108,474.00) | Total recomputed from rows; issue shown in the report (insights + data-quality log) |
| 2 | Deals without unit code / final price | 6 | Kept as «قيد الاستكمال»; excluded from value |
| 3 | Deals whose customer is not in the registration register | 3 | Kept; flagged; listed in Appendix A notes |
| 4 | Deals matched by civil ID / by phone + family name | 10 / 1 | Phone alone never accepted (one phone is shared) |
| 5 | Name differs between deal and registration record | 3 | Shown as recorded; flagged |
| 6 | Same project recorded under different developers | 1 | Shown as recorded; flagged |
| 7 | Unit code / area pattern of another project | 1 | Shown as recorded; flagged for verification |
| 8 | Same phone on two deal records (different civil IDs) | 2 | Flagged |
| 9 | Deal documented after the event days | 1 | Counted on its entry date |
| 10 | Duplicate customers (civil ID) | 0 | — |
| 11 | Repeated names (different people, different civil IDs) | 51 records in 19 groups | Not duplicates; kept |
| 12 | Shared phone number among customers | 1 number / 2 records | Kept (different civil IDs) |
| 13 | Invalid phone format (not 8 digits starting 7/9) | 7 | Shown with † in the register |
| 14 | Phones stored with +968 prefix | 2 | Normalised to 8 digits |
| 15 | Invalid civil ID format | 2 | Excluded from matching; not printed |
| 16 | E-mail field truncated at ~12–14 characters at source | 68 non-trivial values, 0 well-formed | Excluded from report |
| 17 | ID-expiry field partially filled / default-looking dates | 362 of 720 | Not analysed |
| 18 | Free-text notes: junk values («.», «ء», «\|», «-»…) and start-truncated notes | 261 non-empty, 157 meaningful, 145 tagged | Rule-based tags only (rules in pipeline.py) |
| 19 | Staff attribution differs between «العملاء» and «AqarCRM» tabs | 323 | «العملاء» = who served the customer (used); «AqarCRM» = entry account (7 accounts, shown separately) |
| 20 | Phone format differs between the two tabs | 2 | Identical after normalisation |

## 5. Assets used

| Asset | File | Note |
|---|---|---|
| Ministry × initiative lockup (light) | `brand/logo/cobrand/sukna-w-khazinah_x_mhup.svg` | Cover. Vector (trace of the official ministry JPG — see `brand/partners/mhup/README.md`) |
| Ministry × initiative lockup (dark) | `brand/logo/cobrand/sukna-w-khazinah_x_mhup_on-dark.svg` | Closing page |
| WUSOOL primary / reversed | `reports/sakna-khazina-performance/logos/WUSOOL_Primary_FullColor.svg`, `WUSOOL_Reversed.svg` | From the approved WUSOOL brand system v1.0 |
| Fonts | Changa, IBM Plex Sans Arabic (`brand/fonts`), Almarai (`assets/fonts`) | SIL OFL 1.1, embedded in the PDF |

### Missing assets (not invented)

- **Developer logos** for طلعت مصطفى، الأبرار، الأهلي صبور — not present in the repository or the shared Drive. Developer pages use a typographic name plate; no logo was downloaded or recreated.
- **Project images** for جود، حي الوفاء، رِواق، ريفيرا صلالة، بلوميريا — not available; project section is data-only.
- **Event photography** — no photos of the booth or team exist in the repository; the report uses no photography (no stock images).
- **Ministry department naming** — «دائرة الهوية والوصول» comes from the report brief; it is not in the repository files. The Minister is addressed by title only (name not documented). Verify both before submission.

## 6. Output QA

- PDF: `output/WUSOOL_Sakna_Wa_Khazina_Performance_Report_2026.pdf` — 56 pages, A4 portrait (594.96 x 841.92 pt), SHA-256 `cfcee86e4343f854…`
- In-page layout QA (Chromium): overflow 0, elements outside frame 0, clipped table cells 0, broken images 0, fonts loaded {'Changa': True, 'IBM Plex Sans Arabic': True, 'Almarai': True}
- Customer register: 720 rows (1–720, each once) over 19 pages with contiguous ranges; all 14 deal IDs present in the PDF text
- Forbidden strings (Lorem, TBD, placeholder, None, NaN, {{ }}): none
- Visual review: every page rendered to PNG and inspected; issues found and fixed are listed in README «QA log».
