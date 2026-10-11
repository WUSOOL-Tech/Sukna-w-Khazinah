# REPORT_METHODOLOGY

## Period
- Event days: **5–8 October 2026**, 9:00–22:00 (4 days, 52 operating hours).
- Registrations run from 5 Oct 11:16 to 10 Oct 12:10. Of these, 697 fall on event days and 23 are follow-up registrations on 9–10 Oct.
- Deals run from 5 Oct 20:09 to 9 Oct 12:07.
- All times are Muscat time (UTC+4). Each record is dated by its **entry** time-stamp.
- Data extracted on 11 October 2026.

## Definitions
| Term | Definition |
|---|---|
| Registered customer | A row in the «العملاء» tab with a unique civil ID. All 720 consented to the privacy policy |
| Lead | Every registered customer. Seriousness is visible only through consultant notes |
| Deal (recorded) | A row in the sales form naming the customer, developer and project |
| Documented deal | A recorded deal with a unit code and a final price above 0. **Only documented deals count toward value** |
| Pending deal | A recorded deal missing the unit code or the price |
| Conversion | (a) Recorded deals per 100 registered customers = 14 / 720 = 1.94; (b) registered customers linked to a deal = 11 / 720 = 1.53%; (c) documented deals per 100 = 8 / 720 = 1.11 |
| Follow-up base | Registered customers with no linked deal = 709 |
| Shared service | A registration naming two or more staff (`+` in the staff field). Credit goes to each named person, so involvement sums to more than 720 |

## Calculations
- **Deal value** is the sum of `سعر الوحدة النهائي` over documented deals, held at 2-decimal precision; percentages are rounded only for display. The sheet's total cell (`=SUM(H2:H13)`) omits two rows and is not used.
- Average, median, minimum, maximum and price per m² use documented deals only.
- **Price bands** are 50–60k, 60–70k and 70–80k OMR (lower bound inclusive).
- **Timing** uses event days only. An hour bucket covers HH:00–HH:59.
- **Every breakdown is re-summed against its total**: developer, project, consultant, day, hour, heat-map and price band. The build fails on any mismatch.

## Normalisation and duplicates
- Text: invisible bidi marks are stripped and whitespace collapsed. Placeholder values («.», «-», «0», «…», «ء», «|», «لايوجد») are treated as missing.
- Phones: digits only; a `+968` prefix is removed. A phone is valid when it has 8 digits starting with 7 or 9. Invalid phones are printed as recorded and marked †.
- Civil ID: 6–9 digits is valid. 2 records fail and are excluded from matching.
- **Duplicates**: a customer is a unique civil ID (720 of 720 unique, 0 duplicates). Repeated names belong to different civil IDs and are not duplicates. One phone number is shared by two different people. Deals are unique on (developer, project, unit, customer), and no unit code repeats.

## Linking deals to customers
1. Match on civil ID (10 deals).
2. Otherwise, match on phone **and** family name, with Arabic spelling normalised for hamza forms, ة/ه and ى/ي (1 deal).
3. Otherwise the deal is unmatched (3 deals) and listed with a flag. Phone alone is never accepted.

Name differences between the two forms are shown, never corrected.

## Interest and needs
The registration form has no structured fields for budget, bedrooms or purpose. The free-text «التعليقات» field is tagged with fixed keyword rules (`TAG_RULES` in `scripts/pipeline.py`): bedrooms (1BR, 2BR, 3BR), investment, residence, villa, land swap, interested or serious, and limited budget. Coverage is 145 of 720 records (20.1%), and the report states this coverage wherever the tags are used.

## Attribution
- **Registration attribution** comes from the «العملاء» staff field. Names are shown as recorded. Contracted consultants are identified against the contract roster (12 appear in records). The other 14 names are «supporting names».
- The **«AqarCRM» staff column** is reported as the 7 system **entry accounts**, not as who served the customer.
- **Deal attribution** comes from the sales-form consultant. No per-consultant conversion rate is computed, because the two forms are separate: the deal consultant matches the registration staff in 10 of the 11 linked deals.

## Privacy
- The PDF omits civil IDs, except the last 3 digits in the deal register, and never prints e-mails.
- Raw and processed personal data, the charts, the HTML and the PDFs are git-ignored, because the repository is public.

## Reproducibility
`scripts/build.sh` rebuilds everything from `data/raw/`. Each build writes `data/aggregates/metrics.json`, from which every printed number is read; nothing in the page text is typed by hand. It also writes `REPORT_AUDIT.md` (counts, checks and QA).
