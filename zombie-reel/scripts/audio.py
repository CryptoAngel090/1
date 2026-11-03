"""Генерация саундтрека + огибающих голоса для lip-sync.

Запуск: python3 scripts/audio.py  (из корня zombie-reel)
Выход:  public/music.wav, src/envelopes.json
"""
import json
import subprocess
import numpy as np

SR = 44100
FPS = 30
DUR = 60.0
N = int(SR * DUR)
rng = np.random.default_rng(47)
t = np.arange(N) / SR

# ---------- Огибающие голоса (RMS на кадр) ----------
VO = ["01_narr", "02_max", "03_max", "04_liza", "05_liza", "06_max", "07_radio", "08_liza", "09_narr"]


def load(path):
    raw = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", path, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
        check=True, capture_output=True,
    ).stdout
    return np.frombuffer(raw, dtype=np.float32)


env = {}
hop = SR // FPS
for name in VO:
    x = load(f"public/vo/{name}.mp3")
    n = int(np.ceil(len(x) / hop))
    rms = np.array([np.sqrt(np.mean(x[i * hop:(i + 1) * hop] ** 2) + 1e-12) for i in range(n)])
    rms = rms / (np.percentile(rms, 95) + 1e-9)
    env[name] = [round(float(min(1.0, v)), 3) for v in rms]
with open("src/envelopes.json", "w") as f:
    json.dump(env, f)

# ---------- Утилиты синтеза ----------


def lp(x, a):
    """Однополюсный ФНЧ (a 0..1, меньше = темнее)."""
    y = np.empty_like(x)
    acc = 0.0
    for i in range(len(x)):
        acc += a * (x[i] - acc)
        y[i] = acc
    return y


def seg(start, length):
    s = int(start * SR)
    return s, min(N, s + int(length * SR))


def add(buf, start, sig, gain=1.0):
    s = int(start * SR)
    e = min(N, s + len(sig))
    if s < N:
        buf[s:e] += sig[: e - s] * gain


def adsr(n, a=0.01, r=0.3):
    e = np.ones(n)
    na, nr = int(a * SR), int(r * SR)
    e[:na] = np.linspace(0, 1, max(na, 1))[: len(e[:na])]
    if nr > 0:
        e[-nr:] *= np.linspace(1, 0, nr)
    return e


def kick(f0=55, dur=0.5):
    n = int(dur * SR)
    tt = np.arange(n) / SR
    f = f0 + 120 * np.exp(-tt * 35)
    ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph) * np.exp(-tt * 7)


def snare(dur=0.25):
    n = int(dur * SR)
    tt = np.arange(n) / SR
    noise = rng.standard_normal(n)
    noise = noise - lp(noise, 0.08)
    return (noise * 0.6 + np.sin(2 * np.pi * 190 * tt) * 0.5) * np.exp(-tt * 18)


def braam(dur=3.0, f=43.65):
    n = int(dur * SR)
    tt = np.arange(n) / SR
    s = np.zeros(n)
    for k, det in enumerate([1.0, 1.003, 0.997, 2.0, 1.5]):
        ph = 2 * np.pi * f * det * tt
        s += (2 * ((ph / (2 * np.pi)) % 1) - 1) * (0.5 if k < 3 else 0.25)
    s = lp(s, 0.06)
    s = np.tanh(s * 2.2)
    return s * adsr(n, 0.02, dur * 0.8) * np.exp(-tt * 0.6)


def whoosh(dur=0.9, up=True):
    n = int(dur * SR)
    noise = rng.standard_normal(n)
    sweep = np.linspace(0.02, 0.35, n) if up else np.linspace(0.35, 0.02, n)
    y = np.empty(n)
    acc = 0.0
    for i in range(n):
        acc += sweep[i] * (noise[i] - acc)
        y[i] = acc
    shape = np.sin(np.linspace(0, np.pi, n)) ** 2
    return y * shape * 1.6


def hit(dur=1.6):
    n = int(dur * SR)
    tt = np.arange(n) / SR
    k = np.zeros(n)
    kk = kick(45, dur)
    k[: len(kk)] += kk
    noise = rng.standard_normal(n) * np.exp(-tt * 9) * 0.4
    metal = sum(np.sin(2 * np.pi * fr * tt) for fr in [311, 467, 733, 1021]) * np.exp(-tt * 4) * 0.12
    return np.tanh((k * 1.2 + lp(noise, 0.2) + metal) * 1.5)


def growl(dur=1.4, f=70):
    n = int(dur * SR)
    tt = np.arange(n) / SR
    noise = lp(rng.standard_normal(n), 0.05)
    am = 0.5 + 0.5 * np.sin(2 * np.pi * (11 + 4 * np.sin(2 * np.pi * 1.3 * tt)) * tt)
    tone = np.sign(np.sin(2 * np.pi * f * (1 + 0.15 * np.sin(2 * np.pi * 3 * tt)) * tt)) * 0.3
    s = (noise * 3 + lp(tone, 0.1)) * am
    return np.tanh(s * 2) * adsr(n, 0.15, 0.5)


def static_noise(dur):
    n = int(dur * SR)
    x = rng.standard_normal(n)
    x = x - lp(x, 0.15)
    crackle = (rng.random(n) > 0.9985) * rng.standard_normal(n) * 4
    return (x * 0.25 + crackle) * (0.6 + 0.4 * np.sin(2 * np.pi * 0.7 * np.arange(n) / SR))


def riser(dur):
    n = int(dur * SR)
    tt = np.arange(n) / SR
    f = 80 * (2 ** (tt / dur * 3))
    ph = 2 * np.pi * np.cumsum(f) / SR
    tone = np.sin(ph) + 0.5 * np.sin(ph * 1.5)
    return (tone * 0.4 + whoosh(dur, True) * 0.6) * (tt / dur) ** 2


def clank():
    n = int(0.6 * SR)
    tt = np.arange(n) / SR
    s = sum(np.sin(2 * np.pi * fr * tt) * np.exp(-tt * d) for fr, d in [(420, 9), (1130, 14), (2210, 20), (95, 6)])
    return s * 0.5 + rng.standard_normal(n) * np.exp(-tt * 40) * 0.6


def zap(dur=0.8):
    n = int(dur * SR)
    tt = np.arange(n) / SR
    buzz = np.sign(np.sin(2 * np.pi * 120 * tt)) * (rng.random(n) > 0.4)
    return lp(buzz.astype(float), 0.3) * np.exp(-tt * 3) * 0.6


# ---------- Сборка ----------
L = np.zeros(N)

# 1. Дрон по всему ролику (интенсивность по сценам)
drone = np.zeros(N)
for f, g in [(36.71, 0.5), (36.9, 0.4), (55.0, 0.25), (73.42, 0.15), (87.31, 0.08)]:
    drone += np.sin(2 * np.pi * f * t + rng.random() * 6) * g
drone *= 0.75 + 0.25 * np.sin(2 * np.pi * 0.11 * t)
intensity = np.interp(t, [0, 6, 7, 15, 19, 25, 31, 41, 44, 50, 53.5, 56.5, 60],
                      [0.5, 0.7, 0.55, 0.7, 1.0, 1.0, 0.6, 0.8, 0.9, 0.7, 1.2, 0.5, 0.2])
L += drone * intensity * 0.22

# 2. Ветер
wind = lp(rng.standard_normal(N), 0.01) * (0.6 + 0.4 * np.sin(2 * np.pi * 0.07 * t))
L += wind * 0.9 * np.interp(t, [0, 15, 19, 31, 41, 50, 56, 60], [1, 1, 0.4, 1, 1.2, 1, 0.6, 0])

# 3. Пэд-аккорды (минор) в спокойных сценах
pad = np.zeros(N)
for f in [110.0, 130.81, 164.81, 220.0]:
    pad += np.sin(2 * np.pi * f * t) * np.sin(2 * np.pi * f * 1.004 * t)
pad = lp(pad, 0.05)
L += pad * np.interp(t, [0, 3, 15, 16, 31, 33, 41, 50, 56, 58], [0, 0.05, 0.05, 0, 0, 0.07, 0.07, 0.05, 0.05, 0])

# 4. Сердцебиение (S3/S4) — ускоряется
tb = 15.0
while tb < 31.0:
    bpm = 70 if tb < 19 else 125 if tb < 25 else 100
    add(L, tb, kick(50, 0.35), 0.55)
    add(L, tb + 0.22, kick(48, 0.3), 0.4)
    tb += 60 / bpm
# 5. Погоня: ударные 19–25
bt = 19.0
beat = 60 / 140
i = 0
while bt < 25.0:
    if i % 2 == 1:
        add(L, bt, snare(), 0.35)
    add(L, bt + beat / 2, snare(0.06), 0.12)
    bt += beat
    i += 1
# 6. Ударные к финалу (тревога) 44–53
bt = 44.0
while bt < 53.3:
    add(L, bt, kick(52, 0.4), 0.45)
    bt += 60 / 110

# 7. Акценты
for at in [4.5, 25.0, 31.0, 41.0, 50.0]:
    add(L, at - 0.85, whoosh(0.9), 0.5)
add(L, 4.6, hit(), 0.75)
add(L, 19.0, braam(3.2), 0.8)
add(L, 19.0, hit(), 0.5)
add(L, 25.0, hit(1.0), 0.5)
add(L, 42.5, clank(), 0.7)
add(L, 42.6, zap(), 0.5)
add(L, 43.0, braam(2.5, 65.4), 0.4)
add(L, 50.6, riser(2.9), 0.55)
add(L, 53.5, braam(3.5, 41.2), 0.95)
add(L, 53.5, hit(2.0), 0.6)
add(L, 56.5, hit(2.5), 0.8)

# 8. Рычание зомби
for at, f in [(16.8, 65), (18.0, 80), (20.5, 60), (22.8, 75), (26.0, 70), (28.6, 62), (54.0, 55), (55.2, 68)]:
    add(L, at, growl(1.4, f), 0.35)

# 9. Помехи рации
add(L, 7.8, static_noise(5.8), 0.09)
add(L, 44.6, static_noise(4.6), 0.12)

# Стерео-расширение + мастер
R = L.copy()
d = int(0.012 * SR)
R[d:] = L[:-d] * 0.6 + L[d:] * 0.4
st = np.stack([L, R], axis=1)
fade = np.ones(N)
fade[-int(1.5 * SR):] = np.linspace(1, 0, int(1.5 * SR))
st *= fade[:, None]
st = np.tanh(st * 1.3)
st /= np.max(np.abs(st)) + 1e-9
st *= 0.85

pcm = (st * 32767).astype(np.int16)
import wave

with wave.open("public/music.wav", "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes(pcm.tobytes())
print("done: music.wav,", {k: len(v) for k, v in env.items()})
