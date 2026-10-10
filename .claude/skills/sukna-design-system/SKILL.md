---
name: sukna-design-system
description: Design system (tokens, CSS components, Tailwind preset, RTL layout rules) for «سكنة وخزينة» (Sukna w Khazinah). Use whenever building or styling a website, landing page, web app, dashboard, form, email or any HTML/CSS/React UI for the initiative, or when asked for its design tokens, components or Figma variables.
---

# Sukna w Khazinah — Design System v1.0

Source of truth: `brand/design-system/tokens.json`. Regenerate with `python3 scripts/build_tokens.py`. Never hard-code a value that has a token.

## Load
```html
<html lang="ar" dir="rtl">
<link rel="stylesheet" href="brand/design-system/fonts.css">
<link rel="stylesheet" href="brand/design-system/tokens.css">
<link rel="stylesheet" href="brand/design-system/components.css">
<link rel="stylesheet" href="brand/motion/motion.css">
```
Tailwind: `presets: [require('./brand/design-system/tailwind.preset.js')]` and still load `tokens.css`. Outside the repo, the fonts are on Google Fonts: `Changa:wght@400..800` and `IBM Plex Sans Arabic:wght@400;500;600;700`.
Live reference: `brand/design-system/index.html`.

## Key tokens (`--sk-*`)
- Colour: `--sk-color-brand-{green #02C277, yellow #F0FF0B, ink #0B2A1E, deep #00563A, paper #F6F8F5}`. Scales `--sk-color-{green,yellow,neutral}-{50…900}`. Semantic `--sk-color-semantic-{bg-canvas,bg-brand,text-primary,text-secondary,text-link,border,focus-ring}`. Status `--sk-color-status-{success,warning,danger,info}` (all ≥ 4.5:1 on white).
- Type: `--sk-font-family-display` (Changa), `--sk-font-family-text` (IBM Plex Sans Arabic). Sizes `xs 12 … 8xl 96`. Line-heights `tight 1.15 / heading 1.35 / body 1.75`.
- Space: 4px base, `--sk-space-1…12` (4, 8, 12, 16, 24, 32, 40, 48, 64, 80, 96, 128).
- Radius: `none 0, sm 2, md 4, lg 8, pill, chamfer 14` (the logo is sharp, so keep corners small).
- Shadow: `sm, md, lg, block` (hard poster shadow, at most one per view).
- `--sk-angle-ascent: -7.5deg` for rules, bands and motion paths.
- Layout: container 1200, gutter 24, 12 columns. Breakpoints 480 / 768 / 1024 / 1280. Page margin 16 → 32 → 48.

## Components (`components.css`)
`.sk-btn--primary` (ink bg + yellow text, the main CTA) · `--secondary` (green bg + ink text) · `--outline` · `--ghost` · `--lg`; `.sk-card` (`--brand`, `--green`, `--poster`); `.sk-badge` (`--yellow`, `--ink`); `.sk-field .sk-label .sk-input .sk-help .sk-error` (use `aria-invalid`); `.sk-stat`; **`.sk-journey`** (signature: step ١ apartment → "5 سنوات" gap → step ٢ land/support); `.sk-list` (dot bullets); `.sk-dot`, `.sk-dots-2`; `.sk-rule`; `.sk-band`; `.sk-chamfer`; `.sk-surface-{yellow,green,ink,paper}`; `.sk-container`, `.sk-grid`, `.sk-stack`.

## Rules
1. RTL first: logical properties only (`margin-inline-start`, `inset-inline-end`, `padding-block`). "Forward" arrows point left (←).
2. Text is Ink on every brand surface. Never use Sukna Green as text (2.1–2.3:1). Use `--sk-color-green-700` (5.4:1) or Deep Green for green text on white.
3. Focus is always visible: 3px ink outline plus a yellow halo (built into the base).
4. Hit targets are at least 48px tall. Body text is at least 16px.
5. Use the logo SVGs from `brand/logo/svg/`. Never rebuild the wordmark with a font.
6. Use at most two graphic devices per view. The dot motif is the only full circle.
7. Any screen that explains the offer should use `.sk-journey` and the exact wording from the brand skill ("بعد 5 سنوات من استلام الشقة").
8. Check new colour pairs against `contrast-report.md` (AA 4.5:1 for body text).
