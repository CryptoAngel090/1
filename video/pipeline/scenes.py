"""Сцены. Каждая функция рисует кадр в момент t (сек от начала сцены) и возвращает камеру
(zoom, cx, cy) для лёгкого «кен бёрнса». Когда подключим генерацию картинок, сюда же
пойдёт вариант «фон-картинка + анимированные слои»."""
import math
from draw import Canvas, W, H, sky, ground, zzz, gus, horse, campfire, INK

DAY = ((140, 200, 245), (225, 242, 255))
GRASS = (120, 186, 90)
HILL = (150, 205, 115)


def ease(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3 - 2 * x)


def label(c, s, t, x=W / 2, y=130, size=120, col=(255, 222, 40)):
    k = ease(t / 0.35)
    if k <= 0:
        return
    pop = 1 + 0.25 * math.sin(k * math.pi)
    c.text(x, y, s, int(size * k * pop) or 1, fill=col, sw=12)


def hook(c, t, d):
    sky(c, (190, 180, 170), (235, 228, 220))
    c.rect(0, 0, W, 840, fill=(220, 210, 196), outline=None)
    ground(c, 840, (180, 165, 150))
    for i, x in enumerate((300, 520, 1500, 1700)):  # очередь
        gus_c = (200, 200, 200)
        c.ellipse(x, 470, 60, 60, fill=gus_c, w=5)
        c.line([(x, 530), (x, 840)], w=10, fill=(150, 150, 150))
    fall = ease((t - (d - 2.4)) / 0.6)
    gus(c, 960, 840 + 40 * fall, 1.25, mood="shock" if fall > 0 else "yawn", t=t,
        eyes_closed=(fall == 0 and t > 2.0), legs="bent" if fall > 0 else "stand")
    if fall == 0:
        zzz(c, 1080, 280, t)
    label(c, "STANDING?!", t - 0.3)
    return 1.0 + 0.06 * t / d, 960, 560


def horse_scene(c, t, d):
    sky(c, *DAY)
    ground(c, 800, GRASS, HILL)
    c.rect(0, 690, W, 710, fill=(150, 100, 60), outline=None)  # забор
    for x in range(40, W, 160):
        c.rect(x, 640, x + 22, 810, fill=(150, 100, 60), w=4)
    head = horse(c, 1150, 860, 1.0, t=t, asleep=True)
    zzz(c, head[0] + 40, head[1] - 80, t)
    gus(c, 320, 900, 0.9, mood="worried", t=t, look=1, arms="shrug")
    label(c, "WAIT, WHAT?", t - 0.2)
    return 1.04 - 0.04 * t / d, 900, 540


def lock(c, t, d):
    c.rect(0, 0, W, H, fill=(250, 246, 235), outline=None)
    for x in range(0, W, 60):  # клетка «чертежа»
        c.line([(x, 0), (x, H)], w=1, fill=(210, 220, 235))
    for y in range(0, H, 60):
        c.line([(0, y), (W, y)], w=1, fill=(210, 220, 235))
    horse(c, 760, 900, 1.0, t=t, asleep=True, highlight_legs=True)
    k = ease((t - 1.0) / 0.5)
    if k > 0:
        c.rect(1280, 380, 1820, 640, fill=(255, 255, 255), w=6, r=24)
        c.text(1550, 450, "LOCKED", int(70 * k) or 1, fill=(255, 220, 60), sw=8)
        c.text(1550, 560, "bones hold the weight", int(34 * k) or 1, fill=INK, stroke=INK, sw=0)
        c.line([(1280, 560), (920, 780)], w=6)
    label(c, "STAY APPARATUS", t - 0.2, size=100)
    return 1.0 + 0.1 * ease(t / d), 900, 600


def fall(c, t, d):
    sky(c, (190, 180, 170), (235, 228, 220))
    ground(c, 860, (180, 165, 150))
    k = ease((t - 2.0) / 1.2)
    # падение: рисуем Гаса на отдельном слое и поворачиваем вокруг стоп
    layer = Canvas(bg=(0, 0, 0))
    layer.img = layer.img.convert("RGBA")
    layer.img.putalpha(0)
    from PIL import ImageDraw
    layer.d = ImageDraw.Draw(layer.img, "RGBA")
    gus(layer, 960, 860, 1.2, mood="shock" if k > 0.1 else "neutral", t=t, eyes_closed=k < 0.1,
        legs="bent" if k > 0 else "stand")
    from draw import SS
    rot = layer.img.rotate(-80 * k, center=(960 * SS, 860 * SS), resample=3)
    c.img.paste(rot, (0, 0), rot)
    if k >= 1:
        c.text(1300, 520, "THUD!", 110, fill=(255, 120, 60), sw=10)
    if k < 0.1:
        zzz(c, 1070, 300, t)
    label(c, "NO LOCK", t - 0.2)
    return 1.0 + 0.05 * k, 960, 600


def rem(c, t, d):
    sky(c, (20, 26, 60), (60, 70, 120), 800)
    for i in range(60):
        x, y = (i * 397) % W, (i * 211) % 700
        tw = 0.5 + 0.5 * math.sin(t * 2 + i)
        c.ellipse(x, y, 3 + 2 * tw, 3 + 2 * tw, fill=(255, 255, 230), outline=None)
    c.ellipse(1650, 160, 70, 70, fill=(250, 245, 210), w=0, outline=None)
    ground(c, 800, (50, 90, 60), (40, 75, 55))
    head = horse(c, 760, 900, 1.0, t=t, asleep=True, lying=True)
    zzz(c, head[0] + 40, head[1] - 80, t, 70)
    horse(c, 1550, 860, 0.6, t=t, asleep=False)  # «часовой»
    label(c, "BUT...", t - 0.2)
    return 1.06 - 0.06 * t / d, 900, 560


def why(c, t, d):
    half = d / 2
    if t < half:  # саванна, хищник в траве
        sky(c, (250, 205, 130), (255, 236, 190))
        ground(c, 780, (200, 170, 90), (215, 185, 110))
        horse(c, 700, 880, 0.9, t=t, asleep=False)
        px = 1700 - 120 * ease(t / half)
        c.ellipse(px, 760, 110, 40, fill=(160, 120, 50), w=5)
        for i in (-1, 1):
            c.ellipse(px - 40 + i * 25, 745, 9, 9, fill=(255, 230, 0), w=3)
        for x in range(1350, 1920, 45):  # трава поверх хищника
            c.line([(x, 800), (x + 15, 700 + (x % 3) * 20)], w=6, fill=(170, 140, 60))
        c.text(1100, 420, "SECONDS COUNT", 70, fill=(255, 90, 60), sw=8)
        return 1.0 + 0.08 * t / half, 1100, 600
    t2 = t - half  # люди у костра
    sky(c, (25, 25, 50), (70, 50, 70), 800)
    ground(c, 800, (60, 50, 40))
    campfire(c, 960, 860, t)
    gus(c, 560, 880, 0.8, mood="happy", t=t, look=1)
    gus(c, 1360, 880, 0.8, mood="neutral", t=t + 1, look=-1, eyes_closed=True)
    label(c, "WHY?", t - 0.2) if t < 1 else None
    c.text(960, 300, "GROUP + FIRE", 80, fill=(255, 210, 80), sw=8) if t2 > 0.6 else None
    return 1.05 - 0.05 * t2 / half, 960, 620


def outro(c, t, d):
    c.rect(0, 0, W, H, fill=(60, 70, 120), outline=None)
    c.rect(400, 640, 1520, 820, fill=(240, 240, 250), w=7, r=30)  # кровать
    c.rect(400, 600, 520, 900, fill=(150, 100, 60), w=7, r=10)
    c.rect(1400, 660, 1520, 900, fill=(150, 100, 60), w=7, r=10)
    c.ellipse(560, 600, 85, 80, fill=(246, 214, 180), w=6)
    c.arc(530, 590, 16, 10, 0, 180, w=6); c.arc(590, 590, 16, 10, 0, 180, w=6)
    c.rect(610, 610, 1440, 700, fill=(230, 90, 90), w=7, r=30)  # одеяло
    zzz(c, 680, 460, t, 80)
    label(c, "GOOD NIGHT", t - 0.2)
    return 1.0, 960, 540


SCENES = {"hook": hook, "horse": horse_scene, "lock": lock, "fall": fall,
          "rem": rem, "why": why, "outro": outro}
