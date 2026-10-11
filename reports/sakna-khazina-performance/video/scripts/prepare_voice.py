#!/usr/bin/env python3
"""Tighten the narration: shorten every pause (scene pauses -> SCENE_GAP, ellipsis pauses -> INNER_GAP,
comma pauses -> COMMA_GAP), cut at the middle of each silence with short fades, then speed up 10% (pitch kept).
Writes build/voice/voice_edit.wav and build/voice/voice_timing.json (scene start/end in the final timeline)."""
import json, subprocess, sys, wave
import numpy as np
from pathlib import Path

V = Path(__file__).resolve().parents[1]
SRC = V / 'build/voice/take1.mp3'
OUT = V / 'build/voice'
SR = 48000
TEMPO = 1.10
SCENE_GAP, INNER_GAP, COMMA_GAP, LEAD = 0.62, 0.42, 0.26, 0.10
# Long pauses (>= 0.9 s) in take 1 that are ellipses INSIDE a scene (all others separate scenes):
#   #1 after «تقرير الأداء…» and #3 after «من استفادة واحدة…» (verified against segment lengths vs script text)
INNER_LONG = {0, 2}
SCENES = ['intro', 'initiative', 'participation', 'customers', 'peak', 'needs', 'deals', 'developers', 'lastday', 'continues', 'thanks', 'closing']

raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', str(SRC), '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True, check=True).stdout
x = np.frombuffer(raw, dtype=np.float32).copy()
log = subprocess.run(['ffmpeg', '-hide_banner', '-i', str(SRC), '-af', 'silencedetect=noise=-40dB:d=0.35', '-f', 'null', '-'], capture_output=True, text=True).stderr
ev = [(l.split('silence_')[1].split(':')[0], float(l.split(': ')[1].split()[0])) for l in log.splitlines() if 'silence_start' in l or 'silence_end' in l]
sil, s = [], None
for k, v in ev:
    if k == 'start':
        s = v
    elif s is not None:
        sil.append((s, v)); s = None
dur = len(x) / SR
if s is not None:
    sil.append((s, dur))

pieces, t_out, scene_starts, long_i = [], 0.0, [], 0
fade = int(0.012 * SR)


def seg(a, b):
    y = x[int(a * SR):int(b * SR)].copy()
    n = min(fade, len(y) // 2)
    if n:
        y[:n] *= np.linspace(0, 1, n); y[-n:] *= np.linspace(1, 0, n)
    return y


cursor = 0.0
pieces.append(np.zeros(int(LEAD * SR), np.float32)); t_out += LEAD
scene_starts.append(t_out)
for i, (a, b) in enumerate(sil):
    d = b - a
    if a <= 0.01:          # leading silence: skip it
        cursor = max(0.0, b - 0.06); continue
    if b >= dur - 0.01:    # trailing silence
        break
    # speech from cursor to a (keep 60 ms of the silence on each side for natural tails)
    sp = seg(cursor, a + 0.06); pieces.append(sp); t_out += len(sp) / SR
    if d >= 0.9:
        gap = INNER_GAP if long_i in INNER_LONG else SCENE_GAP
        is_scene = long_i not in INNER_LONG
        long_i += 1
    else:
        gap, is_scene = COMMA_GAP, False
    pieces.append(np.zeros(int(gap * SR), np.float32)); t_out += gap
    if is_scene:
        scene_starts.append(t_out)
    cursor = b - 0.06
end_speech = sil[-1][0] if sil and sil[-1][1] >= dur - 0.01 else dur
sp = seg(cursor, end_speech + 0.08); pieces.append(sp); t_out += len(sp) / SR
pieces.append(np.zeros(int(0.3 * SR), np.float32))
y = np.concatenate(pieces)
if len(scene_starts) != len(SCENES):
    sys.exit(f'scene count {len(scene_starts)} != {len(SCENES)}')
tmp = OUT / 'voice_tight.wav'
with wave.open(str(tmp), 'wb') as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((np.clip(y, -1, 1) * 32767).astype(np.int16).tobytes())
final = OUT / 'voice_edit.wav'
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(tmp), '-af', f'atempo={TEMPO},highpass=f=70,acompressor=threshold=-20dB:ratio=2.5:attack=8:release=120,loudnorm=I=-16:TP=-1.5:LRA=7',
                '-ar', str(SR), '-ac', '1', str(final)], check=True)
total = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', str(final)], capture_output=True, text=True).stdout)
starts = [s_ / TEMPO for s_ in scene_starts]
timing = [dict(id=sid, voice_start=round(st, 3), voice_end=round((starts[i + 1] - SCENE_GAP / TEMPO) if i + 1 < len(starts) else total - 0.3 / TEMPO, 3))
          for i, (sid, st) in enumerate(zip(SCENES, starts))]
(OUT / 'voice_timing.json').write_text(json.dumps(dict(source=SRC.name, tempo=TEMPO, duration=round(total, 3), scenes=timing), indent=1))
print(f'original {dur:.2f}s -> edited {total:.2f}s')
for t in timing:
    print(f"{t['id']:13s} {t['voice_start']:7.2f} – {t['voice_end']:7.2f}  ({t['voice_end'] - t['voice_start']:.2f}s)")
