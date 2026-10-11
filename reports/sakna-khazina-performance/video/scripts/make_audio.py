#!/usr/bin/env python3
"""Original, deterministic soundtrack (no samples): D-major pad + mallet pulse at 90 BPM, soft cues on scene
changes and hero numbers, narration on top with automatic ducking. Output: build/audio/mix.wav (48 kHz stereo).
WUSOOL sonic rules: voice 0 dB reference, music −12 dB alone / ≈ −22 dB under speech, ≥ 0.35 s between cues,
final −14 LUFS, peak ≤ −1 dBFS (loudnorm in ffmpeg)."""
import json, re, subprocess, wave
import numpy as np
from pathlib import Path

V = Path(__file__).resolve().parents[1]
OUT = V / 'build/audio'; OUT.mkdir(parents=True, exist_ok=True)
js = (V / 'build/video_data.js').read_text(encoding='utf8')
T = json.loads(re.search(r'window\.T = (\[.*?\]);', js, re.S).group(1))
DUR = float(re.search(r'window\.DURATION = ([\d.]+)', js).group(1))
VO = float(re.search(r'window\.VO = ([\d.]+)', js).group(1))
SR = 48000
n = int(DUR * SR) + SR
t = np.arange(n) / SR
rng = np.random.default_rng(11)


def hz(note):
    names = {'C': 0, 'C#': 1, 'D': 2, 'D#': 3, 'E': 4, 'F': 5, 'F#': 6, 'G': 7, 'G#': 8, 'A': 9, 'A#': 10, 'B': 11}
    m = re.match(r'([A-G]#?)(\d)', note)
    return 440.0 * 2 ** ((names[m.group(1)] + 12 * (int(m.group(2)) + 1) - 69) / 12)


def env_adsr(length, a, r):
    e = np.ones(length)
    na, nr = int(a * SR), int(r * SR)
    e[:na] = np.linspace(0, 1, na) if na else 1
    if nr:
        e[-nr:] *= np.linspace(1, 0, nr)
    return e


def lowpass(x, fc):
    a = np.exp(-2 * np.pi * fc / SR)
    y = np.empty_like(x); acc = 0.0
    for i in range(len(x)):          # one-pole; fine for these short buffers
        acc = (1 - a) * x[i] + a * acc; y[i] = acc
    return y


def mallet(f, dur=1.4, amp=.2):
    """Glass-mallet tone: sine + light FM + wooden partial at 2.76× with exponential decay."""
    k = np.arange(int(dur * SR)) / SR
    e = np.exp(-k * 3.2) * (1 - np.exp(-k * 400))
    s = np.sin(2 * np.pi * f * k + .35 * np.sin(2 * np.pi * f * 2 * k) * np.exp(-k * 6))
    s += .18 * np.sin(2 * np.pi * f * 2.76 * k) * np.exp(-k * 9)
    s *= e * amp
    s[-int(.015 * SR):] *= np.linspace(1, 0, int(.015 * SR))
    return s


def add(buf, x, at, pan=0.0):
    i = int(at * SR)
    if i >= buf.shape[0]:
        return
    x = x[:buf.shape[0] - i]
    buf[i:i + len(x), 0] += x * np.sqrt(.5 * (1 - pan)) * 1.414
    buf[i:i + len(x), 1] += x * np.sqrt(.5 * (1 + pan)) * 1.414


# ------------------------------------------------------------------ music bed (90 BPM, D major)
music = np.zeros((n, 2))
BEAT = 60 / 90; BAR = 4 * BEAT
prog = [['D3', 'A3', 'E4', 'F#4'], ['B2', 'F#3', 'A3', 'D4'], ['G2', 'D3', 'F#3', 'B3'], ['A2', 'D3', 'E3', 'A3']]   # Dadd9 Bm7 Gmaj7 Asus4
bass = ['D2', 'B1', 'G1', 'A1']
seg = 2 * BAR
nseg = int(np.ceil(DUR / seg)) + 1
for s in range(nseg):
    ch = prog[s % 4] if (s + 1) * seg < DUR - 4 else prog[0]      # resolve on Dadd9 for the ending
    t0 = s * seg
    L = int((seg + 1.2) * SR); k = np.arange(L) / SR
    pad = np.zeros(L)
    for j, nt in enumerate(ch):
        f = hz(nt)
        for det in (-.0025, .0025):
            pad += np.sin(2 * np.pi * f * (1 + det) * k + j) * .05
    pad += np.sin(2 * np.pi * hz(bass[s % 4] if (s + 1) * seg < DUR - 4 else 'D2') * k) * .07
    pad *= env_adsr(L, .9, 1.4)
    add(music, pad, t0, pan=(-.2 if s % 2 else .2))
    # mallet arpeggio on 8ths gives forward motion without competing with the voice
    arp = ch[1:] + [ch[2]]
    for b in range(16):
        f = hz(arp[b % 4]) * 2
        add(music, mallet(f, 1.0, .045 if b % 2 else .06), t0 + b * BEAT / 2, pan=(.35 if b % 2 else -.35))
# soft air bed
air = rng.standard_normal(n) * .006
air = np.convolve(air, np.ones(200) / 200, mode='same')
music[:, 0] += air; music[:, 1] += np.roll(air, 900)
# fade in / out
fi = int(1.2 * SR); music[:fi] *= np.linspace(0, 1, fi)[:, None]
fo = int(3.0 * SR); end = int(DUR * SR); music[end - fo:end] *= np.linspace(1, 0, fo)[:, None]; music[end:] = 0

# ------------------------------------------------------------------ cues (sfx)
sfx = np.zeros((n, 2))
cues = []


def cue(at, kind, prio):
    cues.append((at, kind, prio))


def swoosh(dur=1.1):
    L = int(dur * SR); k = np.arange(L) / SR
    x = rng.standard_normal(L)
    x = np.convolve(x, np.ones(40) / 40, mode='same')
    e = np.sin(np.pi * np.clip(k / dur, 0, 1)) ** 2
    return x * e * .08


cue(0.15, 'signature', 6)
for i, sc in enumerate(T[1:], 1):
    cue(sc['t0'], 'transition', 2)
by = {s['id']: s for s in T}
cue(by['customers']['v0'] + .2, 'reveal', 3)
cue(by['deals']['v0'] + (by['deals']['v1'] - by['deals']['v0']) * .6, 'reveal', 3)
cue(by['lastday']['v0'] + .4, 'accent', 3)
cue(by['closing']['v1'] - .4, 'signature', 6)
# resolveCues: ≥ 0.35 s apart (lower priority dropped), ≤ 6 per 10 s
cues.sort()
kept = []
for c in cues:
    if kept and c[0] - kept[-1][0] < .35:
        if c[2] > kept[-1][2]:
            kept[-1] = c
        continue
    if sum(1 for k_ in kept if c[0] - k_[0] < 10) >= 6:
        continue
    kept.append(c)
for at, kind, _ in kept:
    if kind == 'signature':     # D4 (the line) → A4 (zero rises) → E5 (arrival)
        for dt, nt in ((0, 'D4'), (.35, 'A4'), (.75, 'E5')):
            add(sfx, mallet(hz(nt), 2.2, .16), at + dt)
    elif kind == 'transition':  # filtered air moving right → left with the reading direction
        w = swoosh(); L = len(w)
        pan = np.linspace(.7, -.7, L)
        i = int(at * SR); seg_ = slice(i, min(i + L, n)); m = seg_.stop - i
        sfx[seg_, 0] += w[:m] * np.sqrt(.5 * (1 - pan[:m])); sfx[seg_, 1] += w[:m] * np.sqrt(.5 * (1 + pan[:m]))
    elif kind == 'reveal':
        add(sfx, mallet(hz('A4'), 1.6, .12), at); add(sfx, mallet(hz('E5'), 1.6, .09), at + .12)
    elif kind == 'accent':
        add(sfx, mallet(hz('D5'), 1.0, .13), at)

# ------------------------------------------------------------------ voice + ducking
raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', str(V / 'build/voice/voice_edit.wav'), '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True, check=True).stdout
vo = np.frombuffer(raw, dtype=np.float32)
voice = np.zeros(n); i0 = int(VO * SR); voice[i0:i0 + len(vo)] = vo[:n - i0]
win = int(.05 * SR)
rms = np.sqrt(np.convolve(voice ** 2, np.ones(win) / win, mode='same'))
act = (rms > 10 ** (-38 / 20)).astype(float)
g = np.empty(n); acc = 0.0
att, rel = 1 - np.exp(-1 / (.12 * SR)), 1 - np.exp(-1 / (.45 * SR))
for j in range(0, n, 48):                 # 1 ms control rate
    target = act[j]; acc += (att if target > acc else rel) * 48 * (target - acc)
    acc = min(max(acc, 0.0), 1.0); g[j:j + 48] = acc
music_gain = 10 ** ((-12 + (-10) * g) / 20)      # −12 dB alone → −22 dB under speech
sfx_gain = 10 ** ((-0 + (-8) * g) / 20)
mix = np.zeros((n, 2))
mix += music * music_gain[:, None] * 2.2
mix += sfx * sfx_gain[:, None]
mix[:, 0] += voice; mix[:, 1] += voice
mix = mix[:int(DUR * SR)]


def wr(path, x):
    x = np.clip(x, -1, 1)
    with wave.open(str(path), 'wb') as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((x * 32767).astype(np.int16).tobytes())


wr(OUT / 'mix_raw.wav', mix / max(1.0, np.abs(mix).max() / .95))
wr(OUT / 'stem_music.wav', (music * music_gain[:, None] * 2.2)[:int(DUR * SR)])
wr(OUT / 'stem_sfx.wav', (sfx * sfx_gain[:, None])[:int(DUR * SR)])
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(OUT / 'mix_raw.wav'), '-af', 'loudnorm=I=-14:TP=-1:LRA=9', '-ar', str(SR), str(OUT / 'mix.wav')], check=True)
print('cues kept:', [(round(a, 2), k) for a, k, _ in kept])
print(subprocess.run(['ffmpeg', '-hide_banner', '-i', str(OUT / 'mix.wav'), '-af', 'ebur128=peak=true', '-f', 'null', '-'], capture_output=True, text=True).stderr.split('Summary:')[-1])
