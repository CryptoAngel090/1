# Synthesised sound effects for the subscribe overlay (no third-party samples).
import numpy as np, wave, sys
SR = 48000; DUR = 12.0
T_SUB, T_BELL, T_LIKE = 2.8, 4.9, 7.2
out = np.zeros(int(SR * DUR) + SR)
rng = np.random.default_rng(3)
def add(sig, t, g=1.0):
    i = int(t * SR); out[i:i + len(sig)] += sig[:len(out) - i] * g
def env(n, a, d):                      # attack / exponential decay
    t = np.arange(n) / SR; e = np.exp(-t / d); k = int(a * SR)
    if k: e[:k] *= np.linspace(0, 1, k)
    return e
def lp(x, a):                          # one-pole low-pass, a in (0,1)
    y = np.zeros_like(x); acc = 0.0
    for i, v in enumerate(x): acc += a * (v - acc); y[i] = acc
    return y
def whoosh(d, up=True):
    n = int(d * SR); x = rng.standard_normal(n)
    sweep = np.linspace(.03, .25, n) if up else np.linspace(.25, .03, n)
    y = np.zeros(n); acc = 0.0
    for i in range(n): acc += sweep[i] * (x[i] - acc); y[i] = acc
    sh = np.sin(np.linspace(0, np.pi, n)) ** 2
    return y * sh * 2.2
def click():
    n = int(.05 * SR); t = np.arange(n) / SR
    a = rng.standard_normal(n) * env(n, 0, .002) * .9
    b = np.sin(2 * np.pi * 2200 * t) * env(n, 0, .004) * .5
    c = np.zeros(n); j = int(.035 * SR); c[j:] = (rng.standard_normal(n - j) * env(n - j, 0, .0015) * .5)  # release
    return a + b + c
def pop(f0=420, f1=900, d=.12):
    n = int(d * SR); t = np.arange(n) / SR
    f = np.linspace(f0, f1, n); ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph) * env(n, .002, d / 4)
def chime(freqs, d=.8, g=.5):
    n = int(d * SR); t = np.arange(n) / SR
    return sum(np.sin(2 * np.pi * f * t) * env(n, .003, d / (3 + k)) / (1 + k) for k, f in enumerate(freqs)) * g
def bell(f=1320, d=1.2):              # inharmonic bell partials
    n = int(d * SR); t = np.arange(n) / SR
    parts = [(1, 1, .5), (2.76, .5, .25), (5.4, .3, .12), (8.93, .15, .07), (.5, .35, .7)]
    return sum(np.sin(2 * np.pi * f * r * t) * env(n, .001, d * dd) * a for r, a, dd in parts) * .55
def sparkle(d=.6):
    s = np.zeros(int(d * SR))
    for k in range(7):
        c = chime([2400 + k * 380], .25, .18); i = int(k * .055 * SR); s[i:i + len(c)] += c[:len(s) - i]
    return s

add(whoosh(.7), 0.0, .55)                                   # bar slides in
add(chime([660, 990]), 0.55, .25)                           # soft landing
for T in (T_SUB, T_BELL, T_LIKE): add(click(), T, .8)       # mouse clicks
add(pop(380, 760), T_SUB + .12, .6); add(chime([880, 1320, 1760], .9, .45), T_SUB + .16)   # subscribed
add(bell(1320), T_BELL + .12, .8); add(bell(1480), T_BELL + .45, .65); add(bell(1320), T_BELL + .8, .45)  # ring-ring
add(pop(300, 1100, .15), T_LIKE + .12, .7); add(sparkle(), T_LIKE + .2, .9)                # like + sparkles
add(whoosh(.8, False), DUR - 1.3, .5)

out = out[:int(SR * DUR)]
out = out / np.max(np.abs(out)) * .89
st = np.stack([out, out], 1)
with wave.open(sys.argv[1], 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((st * 32767).astype('<i2').tobytes())
print('ok')
