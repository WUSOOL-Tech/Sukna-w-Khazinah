# سكنة وخزينة — Sukna w Khazinah

> **استفد اليوم بشقة، واستفد مرة أخرى بعد 5 سنوات.**

«سكنة وخزينة» is a housing initiative in Oman. It changes the government housing benefit from **one benefit for life** into **two**. The first benefit is an apartment in **Sultan Haitham City (مدينة السلطان هيثم)**. Five years after the apartment is handed over, the citizen becomes eligible again and chooses either **land** or **government support for a housing unit** (apartment or villa). The citizen **keeps the first apartment** as an asset to live in, rent out or sell.

- **سكنة** — a home: the first benefit.
- **خزينة** — a treasury: the apartment stays the citizen's asset while the benefit right returns.

This repository holds the brand identity, design system and motion system.

## What's inside
| Path | Contents |
|---|---|
| [`brand/guidelines/sukna-w-khazinah_brand-guidelines.pdf`](brand/guidelines/sukna-w-khazinah_brand-guidelines.pdf) | **Brand guidelines** (28 pages, Arabic): idea, logo analysis, versions, clear space, misuse, colour, type, graphic elements, voice, design system, motion, applications, co-branding |
| [`brand/logo/`](brand/logo/) | Logo in **SVG · PNG · PDF (RGB + CMYK) · AI**, 10 variants + master geometry + original source |
| [`brand/partners/mhup/`](brand/partners/mhup/) | Ministry of Housing and Urban Planning logo: official original plus traced vectors (SVG · PDF · AI, colour / black / white) |
| [`brand/design-system/`](brand/design-system/) | Tokens (JSON → CSS / Tailwind), components CSS, live reference `index.html`, contrast report |
| [`brand/motion/`](brand/motion/) | Motion principles and tokens, `motion.css`, interactive logo reveal, MP4/GIF renders |
| [`brand/fonts/`](brand/fonts/) | Changa + IBM Plex Sans Arabic (SIL OFL 1.1) |
| [`.claude/skills/`](.claude/skills/) | Claude skills: `sukna-brand-identity`, `sukna-design-system`, `sukna-motion-system` |
| [`scripts/`](scripts/) | Reproducible build pipeline |
| [`reports/sakna-khazina-performance/`](reports/sakna-khazina-performance/) | **WUSOOL performance report** (October Urban 2026 booth): data pipeline → A4 Arabic PDF. Personal data and the PDF are git-ignored (public repo) |

## Brand at a glance
| | |
|---|---|
| أخضر سكنة · Sukna Green | `#02C277` · RGB 2 194 119 |
| أصفر خزينة · Khazinah Yellow | `#F0FF0B` · RGB 240 255 11 |
| حبر · Ink (text) | `#0B2A1E` |
| Display type | Changa (800 / 700) |
| Text type | IBM Plex Sans Arabic (400–700) |
| Ascent angle | 7.5° |
| Clear space | 2D (D = logo dot diameter) |

## Rebuild everything
```bash
pip install reportlab           # plus poppler-utils (pdftocairo), potrace, ffmpeg, Node + Playwright
./scripts/build_all.sh
```
