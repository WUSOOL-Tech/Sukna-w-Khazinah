# نظام التصميم — Design System v1.0

`tokens.json` is the single source of truth (W3C design-tokens format). Edit it, then run `python3 scripts/build_tokens.py`.

| File | Purpose |
|---|---|
| `tokens.json` | Source tokens: colour, type, space, radius, border, shadow, ascent angle, breakpoints, layout, motion |
| `tokens.css` | Generated CSS custom properties (`--sk-*`), including reduced-motion overrides |
| `tailwind.preset.js` | Generated Tailwind preset (maps to the CSS variables, so load `tokens.css` too) |
| `tokens.flat.json` | Generated flat map for Figma Tokens / scripts |
| `contrast-report.md` | Generated WCAG contrast matrix |
| `fonts.css` | `@font-face` for Changa + IBM Plex Sans Arabic (files in `../fonts`, OFL) |
| `components.css` | Base styles and components (`.sk-*`) |
| `index.html` | Live reference of every component (open in a browser) |

## Usage
```html
<html lang="ar" dir="rtl">
<link rel="stylesheet" href="brand/design-system/fonts.css">
<link rel="stylesheet" href="brand/design-system/tokens.css">
<link rel="stylesheet" href="brand/design-system/components.css">
<link rel="stylesheet" href="brand/motion/motion.css">
```

## Core rules
- RTL first: `dir="rtl"`, logical properties (`margin-inline-start`, `inset-inline-end`). "Forward" arrows point left.
- Text colour is Ink `#0B2A1E` on white, paper, yellow **and** green. Sukna Green is never used for reading text (2.1–2.3:1).
- Primary CTA: Ink background with Yellow text. Secondary: Green background with Ink text.
- Corners stay small (0–8px). The full circle is reserved for the dot motif. The signature shape is the chamfer (`.sk-chamfer`).
- Use at most two graphic devices per view (ascent rule, two dots, ascent band, chamfer). Use at most one block shadow per view.

## Components
`.sk-btn` (`--primary | --secondary | --outline | --ghost`, `--lg`), `.sk-card` (`--brand | --green | --poster`), `.sk-badge` (`--yellow | --ink`), `.sk-field` / `.sk-input` / `.sk-help` / `.sk-error`, `.sk-stat`, `.sk-journey` (signature two-benefit timeline), `.sk-list`, `.sk-dot`, `.sk-dots-2`, `.sk-rule`, `.sk-band`, `.sk-chamfer`, `.sk-container`, `.sk-grid`, `.sk-stack`, surfaces `.sk-surface-yellow | -green | -ink | -paper`.
