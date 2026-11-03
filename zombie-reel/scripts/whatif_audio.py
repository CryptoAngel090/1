"""What If #1 — Zombies only move when you blink.

Источник правды по таймингу: реплики, фразы субтитров, моргания, сцены.
Пишет src/whatif/timeline.json и public/whatif/music.wav.
Запуск из корня zombie-reel: python3 scripts/whatif_audio.py
"""
import json
import subprocess
import wave

import numpy as np

SR = 44100
FPS = 30
DUR = 58.0
N = int(SR * DUR)
rng = np.random.default_rng(1)

# (файл, старт в ролике, [(начало, конец, текст)] — тайминги внутри файла по silencedetect)
VO = [
    ("whatif/b1.mp3", 0.3, [
        (0.0, 1.9, "What if zombies could only move..."),
        (2.34, 3.11, "...when you BLINK?"),
        (3.68, 5.03, "At first, it sounds easy."),
        (5.41, 6.35, "Just don't blink."),
    ]),
    ("whatif/b2.mp3", 7.4, [
        (0.0, 3.76, "But the average person blinks 15 to 20 times a minute."),
        (4.44, 8.07, "That's up to 1,200 chances an hour for them to get closer."),
        (8.80, 10.21, "Try to hold your eyes open,"),
        (10.56, 12.22, "and within a minute they burn,"),
        (12.52, 13.24, "they water,"),
        (13.63, 14.92, "and you can't see a thing."),
    ]),
    ("whatif/b3.mp3", 23.2, [
        (0.0, 0.97, "So you team up."),
        (1.45, 3.67, "One person watches while the other blinks."),
        (4.18, 5.08, "You take turns."),
        (5.58, 6.28, "And it works."),
        (6.78, 7.49, "Day one."),
        (8.07, 8.77, "Day two."),
        (9.25, 10.19, "Day three."),
    ]),
    ("whatif/b4.mp3", 34.4, [
        (0.0, 1.79, "But after a day or two without sleep,"),
        (2.24, 4.19, "your brain starts shutting off on its own."),
        (4.66, 5.65, "MICROSLEEPS."),
        (6.03, 7.35, "A few seconds at a time."),
        (7.63, 8.61, "You don't even notice."),
        (9.12, 10.68, "And every time your eyes close..."),
        (11.33, 11.97, "they MOVE."),
        (12.54, 15.01, "Sooner or later, everyone has to sleep."),
        (15.51, 15.97, "So..."),
        (16.39, 17.33, "who's watching YOU?"),
        (18.04, 20.04, "Comment how you'd survive the first night."),
    ]),
]

# Моргания: (старт, длительность закрытых глаз) — глобальные секунды
BLINKS = [
    (2.55, 0.18),
    (12.3, 0.14), (13.1, 0.14), (13.85, 0.14), (14.6, 0.14), (15.35, 0.14),
    (21.9, 0.35),
    (39.6, 0.45), (40.9, 0.5), (42.1, 0.55),
    (44.1, 1.6),  # медленное закрытие → скример на «they MOVE»
]

SCENES = [
    ("hook", 0.0, 7.2),
    ("eye", 7.2, 11.7),
    ("count", 11.7, 16.0),
    ("strain", 16.0, 23.0),
    ("team", 23.0, 34.2),
    ("awake", 34.2, 38.9),
    ("micro", 38.9, 46.6),
    ("sleep", 46.6, 49.7),
    ("watch", 49.7, 54.6),
    ("end", 54.6, 58.0),
]

captions = []
lines = []
for file, start, chunks in VO:
    lines.append({"file": file, "start": start})
    for a, b, text in chunks:
        captions.append({"from": round(start + a, 3), "to": round(start + b, 3), "text": text})

with open("src/whatif/timeline.json", "w") as f:
    json.dump({"fps": FPS, "duration": DUR, "lines": lines, "captions": captions,
               "blinks": BLINKS, "scenes": SCENES}, f, indent=1)

# ───────────────────────── саунд-дизайн ─────────────────────────
t = np.arange(N) / SR


def lp(x, a):
    y = np.empty_like(x)
    acc = 0.0
    for i in range(len(x)):
        acc += a * (x[i] - acc)
        y[i] = acc
    return y


def add(buf, at, sig, g=1.0):
    s = int(at * SR)
    e = min(N, s + len(sig))
    if 0 <= s < N:
        buf[s:e] += sig[: e - s] * g


def env(n, a, r):
    e = np.ones(n)
    na, nr = max(1, int(a * SR)), max(1, int(r * SR))
    e[:na] = np.linspace(0, 1, na)
    e[-nr:] *= np.linspace(1, 0, nr)
    return e


def kick(f0=50, d=0.45):
    n = int(d * SR)
    tt = np.arange(n) / SR
    ph = 2 * np.pi * np.cumsum(f0 + 110 * np.exp(-tt * 30)) / SR
    return np.sin(ph) * np.exp(-tt * 7)


def tick():
    n = int(0.05 * SR)
    tt = np.arange(n) / SR
    return (np.sin(2 * np.pi * 2400 * tt) + rng.standard_normal(n) * 0.3) * np.exp(-tt * 120)


def whoosh(d=0.5, up=True):
    n = int(d * SR)
    x = rng.standard_normal(n)
    sweep = np.linspace(0.02, 0.3, n) if up else np.linspace(0.3, 0.02, n)
    y = np.empty(n)
    acc = 0.0
    for i in range(n):
        acc += sweep[i] * (x[i] - acc)
        y[i] = acc
    return y * np.sin(np.linspace(0, np.pi, n)) ** 2 * 1.8


def stinger(d=2.2):
    """Скример: диссонансный кластер + шумовой удар."""
    n = int(d * SR)
    tt = np.arange(n) / SR
    s = sum(np.sin(2 * np.pi * f * tt + np.sin(2 * np.pi * 6 * tt) * 0.6) for f in [233, 247, 262, 349, 370, 494])
    s = s / 6 + lp(rng.standard_normal(n), 0.4) * 0.8
    k = np.zeros(n)
    kk = kick(38, 1.2)
    k[: len(kk)] = kk
    return np.tanh((s * np.exp(-tt * 1.6) + k * 1.3) * 1.8)


def braam(d=2.5, f=41.2):
    n = int(d * SR)
    tt = np.arange(n) / SR
    s = sum((2 * ((f * m * tt) % 1) - 1) * g for m, g in [(1, 0.5), (1.004, 0.5), (2, 0.25), (1.5, 0.2)])
    return np.tanh(lp(s, 0.05) * 2.5) * env(n, 0.03, d * 0.7)


def growl(d=1.2, f=70):
    n = int(d * SR)
    tt = np.arange(n) / SR
    am = 0.5 + 0.5 * np.sin(2 * np.pi * 12 * tt)
    return np.tanh(lp(rng.standard_normal(n), 0.05) * 3 * am * 2) * env(n, 0.1, 0.4)


L = np.zeros(N)

# дрон — тянет весь ролик
drone = sum(np.sin(2 * np.pi * f * t + rng.random() * 6) * g for f, g in [(43.65, 0.5), (43.9, 0.4), (65.4, 0.2), (87.3, 0.1)])
inten = np.interp(t, [0, 7, 11.7, 16, 23, 34, 39, 46, 49.7, 54.6, 58], [0.6, 0.5, 0.7, 1.0, 0.5, 0.7, 1.0, 0.7, 1.1, 0.5, 0.2])
L += drone * inten * 0.22
L += lp(rng.standard_normal(N), 0.012) * 0.7 * inten

# пульс (тёмный электронный бит) в счётных/напряжённых местах
bt = 7.2
while bt < 34.0:
    if bt < 11.7 or (bt > 23.0):
        add(L, bt, kick(50, 0.4), 0.30)
        bt += 60 / 90
    else:
        add(L, bt, kick(52, 0.35), 0.42)
        bt += 60 / 120

# тиканье часов: счёт 1200 и таймер «держи глаза»
for k in range(int((15.9 - 11.8) / 0.125)):
    add(L, 11.8 + k * 0.125, tick(), 0.18)
for k in range(int((21.8 - 16.4) / 0.5)):
    add(L, 16.4 + k * 0.5, tick(), 0.35)

# сердцебиение — нагнетание
for start, end, bpm in [(16.0, 22.0, 100), (38.9, 46.0, 120), (49.7, 54.5, 70)]:
    x = start
    while x < end:
        add(L, x, kick(46, 0.3), 0.5)
        add(L, x + 0.2, kick(44, 0.25), 0.35)
        x += 60 / bpm

# моргание = «вжух + удар», зомби прыгают ближе
for b, d in BLINKS[:-1]:
    add(L, b - 0.05, whoosh(0.25, False), 0.45)
    add(L, b + d * 0.5, kick(40, 0.5), 0.75)
    add(L, b + d * 0.5, growl(0.7, 60 + rng.random() * 20), 0.22)

# переходы сцен
for _, s, _ in SCENES[1:]:
    add(L, s - 0.45, whoosh(0.5), 0.35)

add(L, 0.0, braam(3.0), 0.7)
add(L, 21.9, braam(2.0, 46.2), 0.55)
add(L, 43.6, whoosh(2.0, True), 0.5)          # подъём перед скримером
add(L, 45.70, stinger(2.2), 1.0)              # «they MOVE»
add(L, 49.7, braam(3.0, 38.9), 0.6)
add(L, 54.6, kick(40, 1.0), 0.8)

# день/ночь — мягкие колокольчики «Day one/two/three»
for at in [29.98, 31.27, 32.45]:
    n = int(1.2 * SR)
    tt = np.arange(n) / SR
    add(L, at, (np.sin(2 * np.pi * 523 * tt) + 0.5 * np.sin(2 * np.pi * 784 * tt)) * np.exp(-tt * 3), 0.12)

R = L.copy()
dly = int(0.011 * SR)
R[dly:] = L[:-dly] * 0.55 + L[dly:] * 0.45
st = np.stack([L, R], 1)
fade = np.ones(N)
fade[-int(1.2 * SR):] = np.linspace(1, 0, int(1.2 * SR))
st = np.tanh(st * fade[:, None] * 1.2)
st = st / (np.abs(st).max() + 1e-9) * 0.85
with wave.open("public/whatif/music.wav", "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes((st * 32767).astype(np.int16).tobytes())
print("ok", len(captions), "captions")
