# Motion video — تقرير الأداء · سكنة وخزينة × وصول (16:9 + 9:16)

This is a ~128-second 1920 × 1080 motion film of the performance report. It has an Arabic male narration and 12 scenes, and every figure comes from `../data/aggregates/metrics.json`. The video carries **aggregate figures only**: no customer names, phones or IDs.

| Output (`output/`, git-ignored) | |
|---|---|
| `WUSOOL_Sakna_Wa_Khazina_Performance_Motion_2026_9x16.mp4` | Vertical 1080 × 1920 version (`src/composition_9x16.html`): same timeline, voice, data and motion; laid out inside the safe zones (top 250 px, bottom 300 px, right 110 px) |
| `WUSOOL_Sakna_Wa_Khazina_Performance_Motion_2026_16x9.mp4` | H.264 High, yuv420p (Rec.709), 30 fps, AAC 256k 48 kHz, −14 LUFS, true peak ≤ −1 dBFS, faststart |
| `WUSOOL_Sakna_Wa_Khazina_Performance_Motion_2026_AR.srt` | Arabic subtitles (27 cues) timed to the narration |

## Scenes
| # | Scene | Motion | Data |
|---|---|---|---|
| 1 | Intro | Sukna logo reveal (official master geometry and choreography: lines lead → «سكنة» ascends → «و» → «خزينة» ascends → dots pop); Ministry × initiative lockup; title ascends on the 7.5° line | — |
| 2 | Initiative | The old single-benefit model gives way to the two-beat journey (benefit 1 → «5 years from handover» → benefit 2) | brand guidelines |
| 3 | Participation | KPI counters; an arrival path draws through the four role verbs as they are spoken | 4 days · 52 h · 21 consultants |
| 4 | Customers | Hero counter 0 → 720 with settle chips | 697 / 23 / 0 duplicates / 100% consent |
| 5 | Peak and timing | Day columns grow from the baseline (right → left); evening share; hourly mini chart | 228 on Tuesday · 44.5% after 17:00 |
| 6 | Needs | Bars draw; investment vs residence | 33 / 22 / 4 · 35 vs 4 |
| 7 | Deals | 14 tiles pop; 8 fill as documented; value counter | 466,367.50 OMR · average 58,295.94 |
| 8 | Projects | Share bars in the order they are named | جود 58.1% · حي الوفاء 30.3% · وادي صفا 11.6% (client correction: the sales form recorded «رِواق») |
| 9 | Last day | Deal dots stack per day; Thursday highlighted | 9 of 14 |
| 10 | Continues | KPI counters | 709 · 6 · 41 · 23 |
| 11 | Thanks | Ministry × initiative lockup | — |
| 12 | Closing | Two-beat line «الرحلة بدأت… / وما زالت مستمرة.», WUSOOL logo and approved contacts | — |

A world change (dark ↔ paper ↔ Midnight) is revealed right → left behind a Khazinah-yellow leading edge. Inside a scene, content uses settle (fade + 8 px focus + short rise), Sukna ascend, draw and pop. Exits are faster than entrances. A progress line reads right → left along the bottom.

## Pipeline
```bash
cd reports/sakna-khazina-performance/video
# 1. narration: ElevenLabs eleven_v4, voice «Rawi — Calm & Clear Fusha Narrator», take 1 → build/voice/take1.mp3
python3 scripts/prepare_voice.py      # shorten pauses (scene 0.62 s / ellipsis 0.42 s / comma 0.26 s), atempo 1.10, −16 LUFS; scene timing
python3 scripts/build_video_data.py   # metrics + timing → build/video_data.js (logo geometry: build/logo_paths.js)
python3 scripts/make_audio.py         # original D-major 90 BPM bed + cues + ducking → build/audio/mix.wav (+ stems)
python3 scripts/make_srt.py           # Arabic SRT
node scripts/render_video.cjs 4 30 16x9   # 4 Chromium workers, PNG frames → x264 CRF 15 → MP4 + AAC
node scripts/render_video.cjs 4 30 9x16   # vertical version
node scripts/still.cjs <dir> 12.5 40          # single frames for review (FMT=9x16 for vertical)
```
`src/composition.html` is deterministic: `window.render(t)` seeks every Web Animation to `t` and runs the per-frame counters, so preview and export are identical. Open it with `?t=40` to inspect any moment.

## Notes
- **Correction (2026-10-11):** Al Ahly Sabbour's project is «وادي صفا» (the sales form recorded «رِواق»). It is applied on screen (`PROJECT_NAME` in `build_video_data.py`), in the SRT, and in the narration, where the projects sentence was re-recorded with the same voice and spliced over take 1 (`PATCHES` in `prepare_voice.py`; level and pause pattern matched).
- **Voice:** ElevenLabs synthetic voice, generated from the script in `scripts/make_srt.py`. Amounts are rounded in speech («أكثر من 466 ألف ريال») and exact on screen.
- **Sound:** all music and cues are synthesised in code (no samples, no licensing).
- **Not human-checked:** the audio was verified by measurement only (loudness, peaks, levels per stem), not by listening. Approve the voice and mix before publishing.
- **Sync check:** scene boundaries were mapped from the narration's pause structure (13 long pauses = 11 scene breaks + 2 in-scene ellipses). If a different take is used, re-check `INNER_LONG` in `prepare_voice.py`.
