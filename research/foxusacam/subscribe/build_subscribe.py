# Animated "Subscribe + Bell + Like" overlay for Fox USA Cam.
# Renders transparent PNG frames 1920x1080 @30fps; encode with ffmpeg afterwards.
import math, os, random, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter

D = os.path.dirname(os.path.abspath(__file__))
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(D, 'frames')
os.makedirs(OUT, exist_ok=True)

W, H, FPS, DUR = 1920, 1080, 30, 12.0
K = 2                                   # supersampling
RED = (227, 38, 46); WHITE = (255, 255, 255); GREY = (170, 170, 176)
f = lambda w, s: ImageFont.truetype(os.path.join(D, f'roboto-{w}.woff'), s * K)
icon = lambda s: ImageFont.truetype(os.path.join(D, 'mdi.ttf'), s * K)
I_BELL_O, I_BELL_RING = '\U000F009C', '\U000F009E'
I_UP_O, I_UP, I_DOWN_O = '\U000F0514', '\U000F0513', '\U000F0512'
I_CHECK, I_CURSOR = '\U000F012C', '\U000F01C0'

# ---------- layout (1x, relative to bar origin) ----------
BW, BH = 1310, 150
AV = (25, 20, 110)                      # x, y, diameter
SUB = (480, 30, 330, 90)                # x, y, w, h
BELL = (835, 30, 90)                    # x, y, diameter
LIKE = (950, 30, 335, 90)
MX, MY = 120, 140                       # margins around bar for effects/cursor
CW, CH = BW + 2 * MX, BH + 2 * MY
BX, BY = (W - BW) // 2, 1080 - 110 - BH  # bar position on screen

def cpos(r):  # centre of element
    return (r[0] + r[2] / 2, r[1] + r[3] / 2) if len(r) == 4 else (r[0] + r[2] / 2, r[1] + r[2] / 2)

# ---------- easing ----------
clamp = lambda x: max(0.0, min(1.0, x))
def seg(t, a, b): return clamp((t - a) / (b - a))
def ease_out(x): return 1 - (1 - x) ** 3
def ease_io(x): return 4 * x ** 3 if x < .5 else 1 - (-2 * x + 2) ** 3 / 2
def back(x, s=1.9): x -= 1; return 1 + (s + 1) * x ** 3 + s * x ** 2
def press(t, t0):  # button squash: down 0.12s, back up with overshoot 0.4s
    if t < t0: return 1.0
    if t < t0 + .12: return 1 - .1 * ease_out(seg(t, t0, t0 + .12))
    return .9 + .1 * back(seg(t, t0 + .12, t0 + .55))

# ---------- timeline ----------
T_SUB, T_BELL, T_LIKE = 2.8, 4.9, 7.2          # click moments
PATH = [(1.3, (BW + 40, BH + 110)), (2.5, cpos(SUB)), (3.5, cpos(SUB)),
        (4.55, cpos(BELL)), (5.9, cpos(BELL)), (6.85, (LIKE[0] + 75, LIKE[1] + 45)),
        (8.3, (LIKE[0] + 75, LIKE[1] + 45)), (9.3, (BW + 60, BH + 120))]

def cursor_at(t):
    if t <= PATH[0][0]: return PATH[0][1]
    for (t0, p0), (t1, p1) in zip(PATH, PATH[1:]):
        if t <= t1:
            e = ease_io(seg(t, t0, t1))
            arc = math.sin(e * math.pi) * -18      # slight curved motion
            return (p0[0] + (p1[0] - p0[0]) * e, p0[1] + (p1[1] - p0[1]) * e + arc)
    return PATH[-1][1]

# ---------- helpers ----------
def S(v): return int(round(v * K))

def paste_scaled(base, layer, cx, cy, s, rot=0):
    if rot: layer = layer.rotate(rot, resample=Image.BICUBIC, center=(layer.width / 2, layer.height * .18))
    if s != 1:
        layer = layer.resize((max(1, int(layer.width * s)), max(1, int(layer.height * s))), Image.LANCZOS)
    base.alpha_composite(layer, (int(S(cx) - layer.width / 2), int(S(cy) - layer.height / 2)))

def pill(w, h, fill, outline=None):
    L = Image.new('RGBA', (S(w), S(h)), (0, 0, 0, 0))
    ImageDraw.Draw(L).rounded_rectangle((0, 0, S(w) - 1, S(h) - 1), radius=S(h / 2), fill=fill, outline=outline, width=S(2) if outline else 0)
    return L

def centered_text(L, x, y, txt, font, fill):
    d = ImageDraw.Draw(L); bb = d.textbbox((0, 0), txt, font=font)
    d.text((x - (bb[0] + bb[2]) / 2, y - (bb[1] + bb[3]) / 2), txt, font=font, fill=fill)

# avatar (round crop)
av = Image.open(os.path.join(D, 'avatar-800.png')).convert('RGBA').resize((S(AV[2]), S(AV[2])), Image.LANCZOS)
m = Image.new('L', av.size, 0); ImageDraw.Draw(m).ellipse((0, 0, av.width - 1, av.height - 1), fill=255)
av.putalpha(m)

def ripple(C, cx, cy, t, t0, rmax, color):
    p = seg(t, t0, t0 + .8)
    if 0 < p < 1:
        d = ImageDraw.Draw(C); r = S(rmax * ease_out(p)); a = int(200 * (1 - p))
        d.ellipse((S(cx) - r, S(cy) - r, S(cx) + r, S(cy) + r), outline=color + (a,), width=S(4))

random.seed(7)
PARTS = [(random.uniform(0, 2 * math.pi), random.uniform(55, 110), random.choice([RED, WHITE, (255, 140, 60)]), random.uniform(4, 8)) for _ in range(18)]

def frame(t):
    C = Image.new('RGBA', (S(CW), S(CH)), (0, 0, 0, 0))
    d = ImageDraw.Draw(C)
    ox, oy = MX, MY                                   # bar origin inside canvas
    # bar
    d.rounded_rectangle((S(ox), S(oy), S(ox + BW), S(oy + BH)), radius=S(42), fill=(16, 16, 18, 238), outline=(255, 255, 255, 28), width=S(2))
    # avatar + red ring
    ax, ay, ad = ox + AV[0], oy + AV[1], AV[2]
    d.ellipse((S(ax - 4), S(ay - 4), S(ax + ad + 4), S(ay + ad + 4)), outline=RED + (255,), width=S(4))
    C.alpha_composite(av, (S(ax), S(ay)))
    # name + handle
    d.text((S(ox + 160), S(oy + 30)), 'Fox USA Cam', font=f(700, 46), fill=WHITE)
    d.text((S(ox + 162), S(oy + 88)), '@foxusacam', font=f(400, 30), fill=GREY)

    # --- subscribe button
    subbed = t >= T_SUB + .12
    sx, sy, sw, sh = SUB
    if not subbed:
        L = pill(sw, sh, (255, 255, 255, 255)); centered_text(L, S(sw / 2), S(sh / 2), 'Subscribe', f(500, 38), (15, 15, 15))
    else:
        L = pill(sw, sh, (52, 52, 56, 255))
        p = back(seg(t, T_SUB + .12, T_SUB + .6))
        ck = Image.new('RGBA', (S(50), S(50)), (0, 0, 0, 0)); centered_text(ck, S(25), S(25), I_CHECK, icon(40), WHITE)
        if p > 0: paste_scaled(L, ck, 62, sh / 2, max(.01, p))
        centered_text(L, S(sw / 2 + 25), S(sh / 2), 'Subscribed', f(500, 36), WHITE)
    ripple(C, ox + sx + sw / 2, oy + sy + sh / 2, t, T_SUB + .12, 210, WHITE)
    paste_scaled(C, L, ox + sx + sw / 2, oy + sy + sh / 2, press(t, T_SUB))

    # --- bell button
    bx, by, bd = BELL
    rung = t >= T_BELL + .12
    L = Image.new('RGBA', (S(bd), S(bd)), (0, 0, 0, 0)); dl = ImageDraw.Draw(L)
    dl.ellipse((0, 0, S(bd) - 1, S(bd) - 1), fill=(RED if rung else (52, 52, 56)) + (255,))
    ic = Image.new('RGBA', (S(70), S(70)), (0, 0, 0, 0))
    centered_text(ic, S(35), S(35), I_BELL_RING if rung else I_BELL_O, icon(50), WHITE)
    rot = 0
    if rung:
        k = seg(t, T_BELL + .12, T_BELL + 1.7)
        rot = 26 * math.sin(k * math.pi * 10) * (1 - k) if k < 1 else 0
    paste_scaled(L, ic, bd / 2, bd / 2, 1, rot)
    ripple(C, ox + bx + bd / 2, oy + by + bd / 2, t, T_BELL + .12, 110, RED)
    # sound waves
    k = seg(t, T_BELL + .12, T_BELL + 1.4)
    if 0 < k < 1:
        for side in (-1, 1):
            for i in range(2):
                fr = (k * 3 + i * .5) % 1                  # waves pulse out 3 times
                r = S(50 + 30 * fr); cxx, cyy = S(ox + bx + bd / 2), S(oy + by + bd / 2)
                a0 = -35 if side > 0 else 145
                d.arc((cxx - r, cyy - r, cxx + r, cyy + r), a0, a0 + 70, fill=WHITE + (int(230 * (1 - fr) * (1 - k ** 3)),), width=S(4))
    paste_scaled(C, L, ox + bx + bd / 2, oy + by + bd / 2, press(t, T_BELL))

    # --- like / dislike pill
    lx, ly, lw, lh = LIKE
    liked = t >= T_LIKE + .12
    L = pill(lw, lh, (52, 52, 56, 255)); dl = ImageDraw.Draw(L)
    dl.line((S(215), S(20), S(215), S(lh - 20)), fill=(110, 110, 116, 255), width=S(3))
    dn = Image.new('RGBA', (S(60), S(60)), (0, 0, 0, 0)); centered_text(dn, S(30), S(30), I_DOWN_O, icon(46), WHITE)
    L.alpha_composite(dn, (S(245), S(15)))
    centered_text(L, S(150), S(lh / 2), 'Like', f(500, 36), WHITE)
    th = Image.new('RGBA', (S(70), S(70)), (0, 0, 0, 0))
    centered_text(th, S(35), S(35), I_UP if liked else I_UP_O, icon(48), RED if liked else WHITE)
    ts = 1.0
    if liked:
        k = seg(t, T_LIKE + .12, T_LIKE + .75)
        ts = 1 + .45 * math.sin(k * math.pi) if k < 1 else 1
    paste_scaled(L, th, 68, lh / 2 - 2, ts, -18 * math.sin(seg(t, T_LIKE + .12, T_LIKE + .7) * math.pi) if liked else 0)
    paste_scaled(C, L, ox + lx + lw / 2, oy + ly + lh / 2, press(t, T_LIKE))
    # particle burst from thumb
    k = seg(t, T_LIKE + .12, T_LIKE + 1.2)
    if 0 < k < 1:
        px0, py0 = ox + lx + 68, oy + ly + lh / 2
        for ang, dist, col, sz in PARTS:
            r = dist * ease_out(k); x = px0 + math.cos(ang) * r; y = py0 + math.sin(ang) * r
            s = sz * (1 - k) + 1
            d.ellipse((S(x - s), S(y - s), S(x + s), S(y + s)), fill=col + (int(255 * (1 - k ** 2)),))

    # --- cursor
    ca = seg(t, 1.3, 1.7) * (1 - seg(t, 8.9, 9.4))
    if ca > 0:
        cx, cy = cursor_at(t); cx += ox - 15; cy += oy - 15       # path is bar-relative
        cs = min(press(t, T_SUB - .02), press(t, T_BELL - .02), press(t, T_LIKE - .02))
        cur = Image.new('RGBA', (S(90), S(90)), (0, 0, 0, 0)); dc = ImageDraw.Draw(cur)
        fb = dc.textbbox((0, 0), I_CURSOR, font=icon(84))   # place glyph so arrow tip sits at layer (30, 22)
        dc.text((S(30) - fb[0] - S(2), S(22) - fb[1] - S(2)), I_CURSOR, font=icon(84), fill=WHITE, stroke_width=S(3), stroke_fill=(0, 0, 0))
        sh_ = cur.copy().filter(ImageFilter.GaussianBlur(S(4))); sh_.putalpha(sh_.getchannel('A').point(lambda v: v * .5))
        cur2 = Image.new('RGBA', cur.size, (0, 0, 0, 0)); cur2.alpha_composite(sh_, (S(3), S(5))); cur2.alpha_composite(cur)
        cur2.putalpha(cur2.getchannel('A').point(lambda v: int(v * ca)))
        # tip of arrow ≈ (S(30), S(22)) inside layer -> position tip at cursor point
        paste_scaled(C, cur2, cx + 45 - 30 * cs + 0, cy + 45 - 22 * cs, cs)

    small = C.resize((CW, CH), Image.LANCZOS)
    # enter / exit animation of the whole bar
    ein = seg(t, 0, 1.0); eout = seg(t, DUR - 1.3, DUR - .3)
    dy = 140 * (1 - ease_out(ein)) + 140 * ease_io(eout)
    sc = (.85 + .15 * back(ein, 1.4)) if ein < 1 else 1.0
    alpha = ease_out(ein) * (1 - eout)
    if sc != 1: small = small.resize((int(CW * sc), int(CH * sc)), Image.LANCZOS)
    if alpha < 1: small.putalpha(small.getchannel('A').point(lambda v: int(v * alpha)))
    out = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    out.alpha_composite(small, (int(BX - MX + (CW - small.width) / 2), int(BY - MY + dy + (CH - small.height) / 2)))
    return out

if __name__ == '__main__':
    n = int(DUR * FPS)
    only = [int(a) for a in sys.argv[2:]]
    for i in (only or range(n)):
        frame(i / FPS).save(os.path.join(OUT, f'f{i:04d}.png'))
    print('frames', len(only) or n)
