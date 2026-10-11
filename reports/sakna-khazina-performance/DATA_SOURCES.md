# DATA_SOURCES — data inventory

The repository itself holds the **brand** sources: the initiative identity, the Ministry logo and the fonts. The **operational data** lives in the WUSOOL Google Drive and was exported on **11 October 2026**. Raw exports go to `data/raw/`, which is git-ignored because it holds personal data.

## Operational data (used for figures)
| File in `data/raw/` | Source (Google Drive) | Shape | Role |
|---|---|---|---|
| `customers_sheet_alomlaa.json` | Spreadsheet «بيانات عملاء أكتوبر العمران», tab **«العملاء»** (Asia/Muscat) | 720 rows × 12 columns: `#`, registration date-time, full name (AR), name (EN), civil ID, ID expiry, mobile, e-mail, sales staff, comments, broker, privacy consent | **Canonical customer register** and attribution of who served each customer |
| `customers_sheet_aqarcrm.json` | Same spreadsheet, tab **«AqarCRM»** | 720 rows × 8 columns: `#`, date-time, names, civil ID, mobile, sales staff (CRM account), broker | CRM mirror. Used to reconcile the customer register; its staff column is the **entry account**, not the person who served the customer |
| `sales_form_responses.json` | Spreadsheet «جدول مبيعات أكتوبر العمران - سكنة وخزينة», tab «Form Responses 1» (Asia/Dubai = UTC+4) | 14 response rows × 12 columns: timestamp, consultant, developer, project, unit type, unit code, total area, final unit price, customer name, civil ID, phone, notes. Also a total cell `H17 = SUM(H2:H13)` | **Deal register** |
| `team_contracts.json` | Drive folder «عقود مستشاري أكتوبر العمران 2026» — the 22 contract document titles (number, role, name) | 22 entries | Team roster (21 consultants and 1 photographer) |

## Operational references (used for context, not figures)
| Document | Used for |
|---|---|
| «النموذج الأساسي — اتفاقية مستشار عقاري — أكتوبر العمران 2026» (Google Doc) | Event dates (5–8 Oct 2026) and hours (9:00–22:00, 12 effective hours). The two booths: the Ministry «سكنة وخزينة» booth and the Majd booth A150. Consultant duties, conduct limits, booking rules and confidentiality |
| «WUSOOL_October_Urban_2026_Team_Briefing.pdf» (22 slides) | Customer journey (first impression → qualify → present → close and follow-up), the five core responsibilities, and training day (2 Oct, 12 hours) |

## Brand and initiative sources (repository)
| Path | Used for |
|---|---|
| `brand/guidelines/` | Initiative facts: one benefit → two, an apartment in مدينة السلطان هيثم, 5 years **from handover**, the apartment kept; the core line; the meaning of the name |
| `brand/logo/cobrand/sukna-w-khazinah_x_mhup(.svg, _on-dark.svg)` | Ministry × initiative lockups (cover, closing) |
| `brand/fonts/` | Changa and IBM Plex Sans Arabic |
| `reports/…/logos/`, `reports/…/assets/fonts/` | WUSOOL approved logo SVGs and Almarai, copied from the approved WUSOOL brand system v1.0 |

## Searched for and not found
- **Developer logos** (طلعت مصطفى، الأبرار، الأهلي صبور) and project imagery: not in the repository or the shared Drive, so not used.
- **Event photography**: none, so the report uses none.
- **Attendance log, booking deposits, payment method, financing, floor, bedrooms, commissions per deal**: not in any source, so they are not reported.
- **Ministry department and Minister naming**: the repository has no official naming. «دائرة الهوية والوصول» is taken from the report brief; the Minister is addressed by title.

## Precedence when sources disagree
1. A **deal** is defined by its row in the sales sheet; the sheet's own total cell is ignored in favour of the recomputed row sum.
2. A **customer** is defined by the «العملاء» tab. The «AqarCRM» tab is identical on number, civil ID, time-stamp and name for all 720 records, and identical on phone after normalisation.
3. **Attribution** comes from «العملاء», because it names the people who served the customer, including shared service. «AqarCRM» is reported separately as entry accounts.
4. **Names, developers and projects** are never rewritten. Disagreements are flagged in the report (Appendix A notes) and in `REPORT_AUDIT.md`.
