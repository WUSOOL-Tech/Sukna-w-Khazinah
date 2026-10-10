# نظام الحركة — Motion System v1.0

Motion for «سكنة وخزينة» comes from the logo. It has three principles.

| # | المبدأ | Principle | In practice |
|---|---|---|---|
| 1 | **الصعود** | **Ascend** | Things enter by moving *up* along the logo's 7.5° ascent line (from lower-left to upper-right), with a fast lift and a long settle (`ascend` easing). Nothing falls or bounces hard. |
| 2 | **إيقاعان** | **Two beats** | Important sequences run as *beat 1 → pause → beat 2*, like the two benefits. The 300 ms pause stands for "the five years". |
| 3 | **الخطوط تقود** | **Lines lead** | Rules draw first, right → left (the reading direction), and content follows. Dots land last with a small overshoot (`pop`). |

## Tokens (`brand/design-system/tokens.json → motion.*`)

| Token | Value | Use |
|---|---|---|
| `duration.instant` | 80ms | press, toggle |
| `duration.fast` | 160ms | hover, focus |
| `duration.base` | 240ms | most UI transitions |
| `duration.moderate` | 360ms | cards, panels |
| `duration.slow` | 560ms | hero / page content |
| `duration.beat` / `duration.pause` | 600 / 300ms | two-beat rhythm |
| `duration.signature` | 2400ms | logo reveal |
| `easing.standard` | `cubic-bezier(0.2, 0, 0, 1)` | default |
| `easing.enter` | `cubic-bezier(0.05, 0.7, 0.1, 1)` | elements arriving |
| `easing.exit` | `cubic-bezier(0.3, 0, 0.8, 0.15)` | elements leaving (keep exits ≤ 160ms) |
| `easing.ascend` | `cubic-bezier(0.16, 1, 0.3, 1)` | signature lift |
| `easing.draw` | `cubic-bezier(0.65, 0, 0.35, 1)` | rules drawing |
| `easing.pop` | `cubic-bezier(0.34, 1.56, 0.64, 1)` | dots only |
| `distance.nudge / rise / travel` | 4 / 16 / 48px | |
| `stagger.tight / content / dots` | 40 / 80 / 70ms | |

Ascent vector: for every 48px of horizontal travel, rise 6.32px (tan 7.5°). In the logo's own units (641 wide) the reveal uses (−60, +7.9).

## Logo reveal — `logo-reveal.html`

Total 2400 ms plus an 800 ms hold. Path indices refer to `brand/logo/master/sukna-w-khazinah_master.json`.

| Time (ms) | Element | Motion |
|---|---|---|
| 0–600 (+120 stagger) | Rules around «و» (paths 4, 6) | `scaleX 0→1`, origin right, `draw` |
| 150–850 | «سكنة» (path 0) | ascend: translate(−60, 7.9) → 0, opacity 0→1, `ascend` |
| 650–1050 | «سكنة» dots (10, 16, 15) | pop, 260ms, 70ms stagger |
| 850–1270 | «و» (path 3) | drop 24 units, `pop` |
| 1150–1930 | «خزينة» (paths 2, 1) | ascend, 80ms stagger |
| 1450–2170 | Underlines (7, 5) | draw, 120ms stagger |
| 1650–2330 | «خزينة» dots (9, 8, 17, 12, 11, 14, 13) | pop, 70ms stagger |
| 2400–3200 | — | hold |

Renders in `renders/`: MP4 at 16:9 (yellow and green) and 9:16 (yellow), GIFs 800px wide, a storyboard and the end frame.
Re-render with `NODE_PATH=$(npm root -g) node scripts/render_motion.cjs` (needs Playwright and ffmpeg).

### Rules
- Use the reveal at the start or end of a video and on app splash screens, once per piece. Never loop it inside content.
- Don't speed it up past 1.5× (minimum 1600 ms). Don't reverse it, change the order or animate the letters separately.
- Video end cards: hold the static logo for at least 1.5 s after the reveal.
- Sound (optional): two soft hits on beat 1 (~200 ms) and beat 2 (~1200 ms). No whooshes.

## UI motion (`motion.css`)
`.sk-anim-ascend`, `.sk-anim-rise`, `.sk-anim-draw`, `.sk-anim-pop`, `.sk-anim-exit`, `.sk-stagger` (set `--i` on each child), `.sk-beat-1` / `.sk-beat-2`, `.sk-loader` (two dots, double beat).

## Accessibility
`prefers-reduced-motion: reduce` sets every duration token to 0, turns the utilities into an instant fade, stops the loader and shows the logo in its final state. Nothing flashes more than 3 times per second. Motion never carries meaning on its own.
