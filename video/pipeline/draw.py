"""Примитивы и персонажи. Логическое пространство 1920x1080, рисуем в SS-кратном масштабе
и потом уменьшаем — так получаем сглаживание, которого нет у ImageDraw."""
import math
from functools import lru_cache
from PIL import Image, ImageDraw, ImageFont

W, H = 1920, 1080
SS = 2  # суперсэмплинг

INK = (25, 22, 20)
SKIN = (246, 214, 180)
FONT_BLACK = "/usr/share/fonts/opentype/inter/Inter-Black.otf"


@lru_cache(maxsize=64)
def font(size):
    return ImageFont.truetype(FONT_BLACK, int(size * SS))


class Canvas:
    def __init__(self, img=None, bg=(255, 255, 255)):
        self.img = img or Image.new("RGB", (W * SS, H * SS), bg)
        self.d = ImageDraw.Draw(self.img, "RGBA")

    @staticmethod
    def p(pts):
        return [(x * SS, y * SS) for x, y in pts]

    def line(self, pts, w=6, fill=INK):
        self.d.line(self.p(pts), fill=fill, width=int(w * SS), joint="curve")
        for x, y in (pts[0], pts[-1]):  # скруглённые концы
            r = w / 2
            self.d.ellipse([(x - r) * SS, (y - r) * SS, (x + r) * SS, (y + r) * SS], fill=fill)

    def ellipse(self, cx, cy, rx, ry, fill=None, outline=INK, w=6):
        self.d.ellipse([(cx - rx) * SS, (cy - ry) * SS, (cx + rx) * SS, (cy + ry) * SS],
                       fill=fill, outline=outline, width=int(w * SS) if outline else 0)

    def poly(self, pts, fill=None, outline=INK, w=6):
        self.d.polygon(self.p(pts), fill=fill, outline=outline, width=int(w * SS) if outline else 0)

    def rect(self, x0, y0, x1, y1, fill=None, outline=INK, w=6, r=0):
        self.d.rounded_rectangle([x0 * SS, y0 * SS, x1 * SS, y1 * SS], radius=r * SS, fill=fill,
                                 outline=outline, width=int(w * SS) if outline else 0)

    def arc(self, cx, cy, rx, ry, a0, a1, w=6, fill=INK):
        self.d.arc([(cx - rx) * SS, (cy - ry) * SS, (cx + rx) * SS, (cy + ry) * SS], a0, a1,
                   fill=fill, width=int(w * SS))

    def text(self, x, y, s, size, fill=(255, 255, 255), stroke=INK, sw=None, anchor="mm"):
        sw = sw if sw is not None else max(3, size // 9)
        self.d.text((x * SS, y * SS), s, font=font(size), fill=fill, anchor=anchor,
                    stroke_width=int(sw * SS), stroke_fill=stroke)

    def text_width(self, s, size):
        return self.d.textlength(s, font=font(size)) / SS


# ---------- фоны ----------
def sky(c, top, bottom, horizon=H):
    for y in range(0, horizon, 4):
        k = y / horizon
        col = tuple(int(top[i] + (bottom[i] - top[i]) * k) for i in range(3))
        c.rect(0, y, W, y + 4, fill=col, outline=None)


def ground(c, y, col, hill=None):
    if hill:
        c.ellipse(500, y + 60, 900, 220, fill=hill, outline=None)
        c.ellipse(1600, y + 80, 800, 180, fill=hill, outline=None)
    c.rect(0, y, W, H, fill=col, outline=None)
    c.line([(0, y), (W, y)], w=5)


def zzz(c, x, y, t, size=60):
    for i in range(3):
        ph = (t * 0.6 + i / 3) % 1
        c.text(x + ph * 90 + i * 10, y - ph * 160, "z", int(size * (0.6 + ph * 0.6)),
               fill=(255, 255, 255, int(255 * (1 - ph))), sw=4)


# ---------- Гас: оригинальный персонаж ----------
def gus(c, x, y, s=1.0, mood="neutral", t=0.0, look=0.0, arms="down", legs="stand", eyes_closed=False):
    """x, y — точка между стоп. s — масштаб. look — смещение зрачков (-1..1)."""
    bob = math.sin(t * 3) * 3 * s
    hip = (x, y - 170 * s)
    neck = (x, y - 330 * s + bob)
    head = (x, y - 410 * s + bob)
    lw = 9 * s
    # ноги
    if legs == "stand":
        c.line([hip, (x - 35 * s, y)], w=lw); c.line([hip, (x + 35 * s, y)], w=lw)
    elif legs == "bent":
        c.line([hip, (x - 70 * s, y - 80 * s), (x - 30 * s, y)], w=lw)
        c.line([hip, (x + 70 * s, y - 80 * s), (x + 30 * s, y)], w=lw)
    # туловище в рубашке
    c.poly([(neck[0] - 45 * s, neck[1] + 10 * s), (neck[0] + 45 * s, neck[1] + 10 * s),
            (hip[0] + 50 * s, hip[1] + 15 * s), (hip[0] - 50 * s, hip[1] + 15 * s)],
           fill=(92, 168, 108), w=6 * s)
    # руки
    sh_l, sh_r = (neck[0] - 40 * s, neck[1] + 25 * s), (neck[0] + 40 * s, neck[1] + 25 * s)
    if arms == "down":
        c.line([sh_l, (x - 70 * s, y - 210 * s)], w=lw); c.line([sh_r, (x + 70 * s, y - 210 * s)], w=lw)
    elif arms == "up":
        wave = math.sin(t * 8) * 20 * s
        c.line([sh_l, (x - 110 * s, neck[1] - 90 * s + wave)], w=lw)
        c.line([sh_r, (x + 110 * s, neck[1] - 90 * s - wave)], w=lw)
    elif arms == "shrug":
        c.line([sh_l, (x - 100 * s, neck[1] + 40 * s), (x - 130 * s, neck[1] - 10 * s)], w=lw)
        c.line([sh_r, (x + 100 * s, neck[1] + 40 * s), (x + 130 * s, neck[1] - 10 * s)], w=lw)
    # голова
    r = 85 * s
    c.ellipse(*head, r, r * 0.95, fill=SKIN, w=6 * s)
    for i in (-1, 0, 1):  # вихор
        c.line([(head[0] + i * 18 * s, head[1] - r * 0.92), (head[0] + i * 26 * s, head[1] - r * 1.25)], w=6 * s)
    ex = 32 * s
    ey = head[1] - 10 * s
    for side in (-1, 1):
        cx = head[0] + side * ex
        if eyes_closed:
            c.arc(cx, ey, 16 * s, 10 * s, 0, 180, w=6 * s)
        else:
            c.ellipse(cx, ey, 24 * s, 28 * s, fill=(255, 255, 255), w=5 * s)
            c.ellipse(cx + look * 9 * s, ey + 4 * s, 9 * s, 10 * s, fill=INK, outline=None)
        if mood in ("worried", "sad"):  # брови домиком
            c.line([(cx - side * 22 * s, ey - 36 * s), (cx + side * 18 * s, ey - 46 * s)], w=5 * s)
        elif mood == "angry":
            c.line([(cx - side * 22 * s, ey - 48 * s), (cx + side * 18 * s, ey - 34 * s)], w=5 * s)
    my = head[1] + 45 * s
    if mood == "happy":
        c.arc(head[0], my - 15 * s, 30 * s, 20 * s, 10, 170, w=6 * s)
    elif mood in ("sad", "worried"):
        c.arc(head[0], my + 12 * s, 26 * s, 14 * s, 200, 340, w=6 * s)
    elif mood == "shock":
        c.ellipse(head[0], my, 14 * s, 18 * s, fill=(120, 40, 40), w=5 * s)
    elif mood == "yawn":
        o = 14 + 10 * abs(math.sin(t * 1.5))
        c.ellipse(head[0], my, 18 * s, o * s, fill=(120, 40, 40), w=5 * s)
    else:
        c.line([(head[0] - 18 * s, my), (head[0] + 18 * s, my)], w=6 * s)
    if mood in ("worried", "shock"):  # капля пота
        c.ellipse(head[0] + r * 0.9, head[1] - r * 0.4, 9 * s, 13 * s, fill=(130, 190, 255), w=3 * s)


# ---------- лошадь ----------
def horse(c, x, y, s=1.0, t=0.0, asleep=True, lying=False, highlight_legs=False):
    brown, dark = (168, 112, 62), (90, 55, 30)
    breathe = math.sin(t * 1.2) * 4 * s
    if lying:
        by = y - 90 * s
        c.ellipse(x, by, 230 * s, 95 * s + breathe, fill=brown, w=7 * s)
        c.line([(x - 150 * s, y - 20 * s), (x - 20 * s, y - 10 * s)], w=24 * s, fill=dark)
        c.line([(x + 60 * s, y - 15 * s), (x + 210 * s, y - 8 * s)], w=24 * s, fill=dark)
        head = (x + 270 * s, y - 60 * s)
        c.poly([(x + 160 * s, by - 60 * s), (x + 210 * s, by - 80 * s), (head[0] + 20 * s, head[1] - 20 * s),
                (head[0] - 30 * s, head[1] + 30 * s)], fill=brown, w=7 * s)
    else:
        by = y - 260 * s
        leg_col = (230, 70, 60) if highlight_legs else dark
        for lx in (-150, -100, 110, 160):
            c.line([(x + lx * s, by + 40 * s), (x + lx * s, y)], w=24 * s, fill=INK)
            c.line([(x + lx * s, by + 40 * s), (x + lx * s, y - 4 * s)], w=16 * s, fill=leg_col)
            if highlight_legs:  # «замок» в суставе
                c.ellipse(x + lx * s, y - 120 * s, 17 * s, 17 * s, fill=(255, 220, 60), w=5 * s)
        c.ellipse(x, by, 250 * s, 105 * s + breathe, fill=brown, w=7 * s)
        droop = 60 if asleep else 0
        head = (x + 330 * s, by - 90 * s + droop * s)
        c.poly([(x + 170 * s, by - 60 * s), (x + 230 * s, by - 20 * s), (head[0] + 10 * s, head[1] + 40 * s),
                (head[0] - 20 * s, head[1] - 40 * s)], fill=brown, w=7 * s)
        c.line([(x + 175 * s, by - 70 * s), (head[0] - 30 * s, head[1] - 50 * s)], w=20 * s, fill=dark)
        c.line([(x - 240 * s, by - 10 * s), (x - 300 * s, by + 120 * s + math.sin(t * 2) * 10 * s)], w=22 * s, fill=dark)
    c.ellipse(head[0] + 40 * s, head[1] + 10 * s, 75 * s, 45 * s, fill=brown, w=7 * s)
    c.poly([(head[0] - 10 * s, head[1] - 40 * s), (head[0] + 5 * s, head[1] - 85 * s), (head[0] + 25 * s, head[1] - 40 * s)],
           fill=brown, w=6 * s)
    ex, ey = head[0] + 30 * s, head[1] - 5 * s
    if asleep:
        c.arc(ex, ey, 14 * s, 8 * s, 0, 180, w=5 * s)
    else:
        c.ellipse(ex, ey, 10 * s, 11 * s, fill=INK, outline=None)
    c.ellipse(head[0] + 95 * s, head[1] + 20 * s, 6 * s, 6 * s, fill=INK, outline=None)
    return head


def campfire(c, x, y, t):
    for a in (-1, 1):
        c.line([(x - 70 * a, y), (x + 60 * a, y - 30)], w=18, fill=(110, 70, 40))
    for i, (col, sc) in enumerate([((255, 120, 40), 1.0), ((255, 200, 60), 0.6)]):
        f = 1 + 0.12 * math.sin(t * 9 + i * 2)
        h = 150 * sc * f
        c.poly([(x - 55 * sc, y - 10), (x, y - h), (x + 55 * sc, y - 10)], fill=col, outline=None)
    c.ellipse(x, y - 60, 320, 200, fill=(255, 180, 60, 28), outline=None)
