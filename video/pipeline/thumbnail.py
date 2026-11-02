"""Обложка 1280x720: крупный жёлтый текст с обводкой + герой + лошадь."""
import json, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from PIL import Image
from draw import Canvas, W, H, sky, ground, gus, horse, zzz

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
script = json.load(open(os.path.join(ROOT, "script.json")))
c = Canvas()
sky(c, (140, 200, 245), (225, 242, 255))
ground(c, 830, (120, 186, 90), (150, 205, 115))
head = horse(c, 1300, 1000, 1.15, t=0.5, asleep=True)
zzz(c, head[0] - 40, head[1] - 60, 0.2, 90)
gus(c, 470, 1040, 1.35, mood="shock", t=0, look=1, arms="shrug")
c.text(W / 2, 150, script["thumbnail_text"], 230, fill=(255, 222, 40), sw=22)
c.img.resize((1280, 720), Image.LANCZOS).save(os.path.join(ROOT, "out", "thumbnail.png"))
print("out/thumbnail.png")
