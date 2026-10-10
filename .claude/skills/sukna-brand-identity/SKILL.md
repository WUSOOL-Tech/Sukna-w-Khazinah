---
name: sukna-brand-identity
description: Brand identity of «سكنة وخزينة» (Sukna w Khazinah), the Omani housing initiative that gives citizens two housing benefits (an apartment in مدينة السلطان هيثم now, then land or housing-unit support 5 years after handover). Use for ANY deliverable about this initiative — logo placement or export, colours, typography, Arabic copy and messaging, social posts, flyers, presentations, reports, signage, co-branding with the Ministry of Housing — even when the user never says "brand" or "guidelines".
---

# Sukna w Khazinah — Brand Identity v1.0

Files live in this repo. Read them; never redraw or retype the logo.
- Guidelines PDF: `brand/guidelines/sukna-w-khazinah_brand-guidelines.pdf` (source: `brand/guidelines/src/guidelines.html`)
- Logo files: `brand/logo/{svg,png,pdf,pdf-cmyk,ai}/sukna-w-khazinah_<variant>.*` (see `brand/logo/README.md`)
- Fonts: `brand/fonts/` · Tokens: `brand/design-system/tokens.json`

## The idea (get the facts right)
- **Old system:** one government housing benefit for life, usually land.
- **Sukna w Khazinah:** benefit 1 is buying an apartment in **مدينة السلطان هيثم**. **5 years after the apartment is handed over** (من استلام الشقة), eligibility reopens. Benefit 2 is the citizen's choice of **land** or **government support for a housing unit (apartment or villa)**.
- The citizen **keeps the first apartment** as an asset, to hold, rent out or sell later.
- Name: **سكنة** = a home (benefit 1). **خزينة** = a treasury or asset (the apartment you keep).
- Core line: **«استفد اليوم بشقة، واستفد مرة أخرى بعد 5 سنوات.»**
- Never say "two free apartments", never promise prices or returns, and never drop "from handover" when stating the 5 years. Label renders «تصور فني».

## Logo
- Custom geometric-Kufi lettering: «سكنة» over «خزينة», joined by «و» between two ruled lines, with a baseline that rises about **7.5°**. Ratio 1.208:1. Made of 18 vector paths.
- Variants: `primary` (green on yellow, the default), `reverse` (yellow on green), `mark-green` (light backgrounds), `mark-yellow` (green, ink and dark), `mark-black`, `mark-white`, `mark-ink`, `mono-black-on-white`, `avatar-yellow`, `avatar-green`.
- **Clear space 2D** (D = dot diameter ≈ 5.6% of logo width). **Minimum width** 120px on screen, 30mm in print.
- Don't stretch, rotate, recolour, outline, add shadows or glow, split or rearrange the words, retype it in a font, put yellow on white, or place it on busy images.
- Co-branding: ministry logo (وزارة الإسكان والتخطيط العمراني) first, on the right, then an ink vertical divider, then the initiative logo. Equal optical height, 2D gap. Partners go in a smaller separate row under «بالشراكة مع».

## Colour
| Name | HEX | RGB | CMYK* | Pantone* |
|---|---|---|---|---|
| أخضر سكنة Sukna Green | `#02C277` | 2 194 119 | 75 0 70 0 | 7480 C |
| أصفر خزينة Khazinah Yellow | `#F0FF0B` | 240 255 11 | 8 0 92 0 | 803 C (fluorescent) |
| حبر Ink | `#0B2A1E` | | | |
| أخضر عميق Deep Green | `#00563A` | | | |
| ورق Paper | `#F6F8F5` | | | |
*CMYK and Pantone values are suggestions; confirm with a print proof. The HEX values are exact, from the source file.

- Campaign proportion: yellow 50 / green 25 / ink 15 / white 10. In digital UI white and paper dominate.
- **Contrast:** green on yellow is 2.1:1, so it is for the logo and big shapes only. Text is **Ink** on yellow, green, white and paper. Deep Green also works on yellow and white. No white text on yellow or green. Full matrix: `brand/design-system/contrast-report.md`.

## Typography
- Display: **Changa** 800/700. Headlines, big numbers, short slogans. Line-height 1.15–1.35.
- Text: **IBM Plex Sans Arabic** 400–700. Body, UI, legal, tables (tabular numbers). Line-height 1.75.
- Body text at least 16px on screen or 9pt in print. Arabic first, English as translation.

## Graphic devices (max two per design)
Ascent rule (thin line at 7.5°, thickness ¼D) · two dots (= two benefits) · ascent band (bottom edge rising to the right at 7.5°) · chamfer (two opposite corners cut).

## Voice
Clear (one idea per sentence), reassuring (the language of rights, not favours), motivating (verbs: استفد، اختر، احتفظ). Simplified Modern Standard Arabic.

## Layout
RTL first. Social safe margin 64px; stories keep the top and bottom 250px clear. Logo at least 22% of canvas width, placed top-left or bottom-centre.

Related skills: `sukna-design-system` (UI and code), `sukna-motion-system` (animation and video).
