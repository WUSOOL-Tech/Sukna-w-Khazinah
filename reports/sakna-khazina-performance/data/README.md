# data/

| Folder | Content | In git |
|---|---|---|
| `raw/` | Source exports (see `../DATA_SOURCES.md` for exact file names and shapes) | no — personal data |
| `processed/` | `customers.csv/json`, `deals.csv/json` — normalised full registers | no — personal data |
| `aggregates/` | `metrics.json` (every number in the report), `validation.json` | no — names consultants |

Recreate everything with `../scripts/build.sh` once `raw/` is populated.
