---
name: sukna-motion-system
description: Motion system for «سكنة وخزينة» (Sukna w Khazinah) — principles, motion tokens, CSS animation utilities, the signature logo reveal and how to render MP4/GIF. Use for any animation, transition, micro-interaction, loader, video intro/outro, reel, motion graphic or animated logo for the initiative.
---

# Sukna w Khazinah — Motion System v1.0

Full spec: `brand/motion/README.md`. CSS: `brand/motion/motion.css`. Tokens: `motion.*` in `brand/design-system/tokens.json` (CSS `--sk-motion-*`).

## Principles (taken from the logo)
1. **Ascend (الصعود):** enter by moving up along the 7.5° ascent line (lower-left → upper-right), with a fast lift and a long settle. Never drop or bounce hard.
2. **Two beats (إيقاعان):** beat 1 (600ms) → pause (300ms, "the five years") → beat 2. Use it for any sequence that tells the story: «سكنة» then «خزينة», apartment then land.
3. **Lines lead (الخطوط تقود):** rules draw first, right → left; content follows; dots land last with `pop`.

## Tokens
Durations: instant 80 · fast 160 · base 240 · moderate 360 · slow 560 · beat 600 · pause 300 · signature 2400 (ms).
Easings: standard `(0.2,0,0,1)` · enter `(0.05,0.7,0.1,1)` · exit `(0.3,0,0.8,0.15)` · **ascend `(0.16,1,0.3,1)`** · draw `(0.65,0,0.35,1)` · pop `(0.34,1.56,0.64,1)` (dots only).
Distance: nudge 4 · rise 16 · travel 48px. Ascent vector (48px, −6.32px). Stagger: 40 / 80 / 70ms.

## CSS utilities
`.sk-anim-ascend`, `.sk-anim-rise` (UI default), `.sk-anim-draw` (origin right in RTL), `.sk-anim-pop`, `.sk-anim-exit`, `.sk-stagger` + `style="--i:n"`, `.sk-beat-1` / `.sk-beat-2`, `.sk-loader` (two dots, double beat).

## Logo reveal (signature, 2.4s + 0.8s hold)
`brand/motion/logo-reveal.html` (self-contained; `?bg=green` for the reverse version; `window.seek(ms)` for frame capture).
Order: rules around «و» draw (0–600) → «سكنة» ascends (150–850) and its dots pop → «و» drops (850–1270) → «خزينة» ascends (1150–1930) → underlines draw (1450–2170) → «خزينة» dots pop (1650–2330) → hold.
Renders: `brand/motion/renders/logo-reveal_{yellow,green}_1920x1080.mp4`, `logo-reveal_yellow_1080x1920.mp4`, `*_800w.gif`, storyboard PNGs.
Re-render or make new formats by editing the `jobs` list in `scripts/render_motion.cjs`, then run `NODE_PATH=$(npm root -g) node scripts/render_motion.cjs` (Playwright and ffmpeg).

## Rules
- Use the reveal once per piece, at the intro or outro. Don't loop, reverse, reorder or split letters, and don't run it faster than 1.5× (minimum 1600ms). Hold the end card at least 1.5s.
- UI motion stays at 240–360ms. Exits are faster than entrances (≤ 160ms).
- Video: 30fps or more. Text appears on beats. Keep the 9:16 safe zones (250px top and bottom). Optional sound is two soft hits on the two beats, with no whooshes.
- Always honour `prefers-reduced-motion` (the tokens collapse to 0ms and the logo shows its final state). Nothing flashes more than 3 times per second.
