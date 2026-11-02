"""Сборка ролика: script.json -> тайминги -> кадры -> субтитры -> звук -> MP4.

Сейчас тайминги считаются из темпа речи (wpm). Когда подключим TTS с выравниванием по словам
(ElevenLabs /with-timestamps), функция build_timeline() будет брать времена слов из ответа API,
а make_audio() — класть реальный голос вместо заглушки.
"""
import argparse, json, math, os, subprocess, sys, time, wave
from multiprocessing import Pool
import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(__file__))
from draw import Canvas, W, H, SS, INK
from scenes import SCENES

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FPS = 24
PAD = 0.7  # пауза между сценами, сек
SR = 44100


def build_timeline(script):
    sec_per_word = 60.0 / script["wpm"]
    t, scenes = 0.0, []
    for sc in script["scenes"]:
        words = sc["text"].split()
        wt = []
        for w in words:
            dur = sec_per_word * (1.0 + 0.04 * len(w.strip(".,?!")) - 0.15)
            if w[-1] in ".?!":
                dur += 0.35
            elif w[-1] == ",":
                dur += 0.15
            wt.append((w, t + 0.3 + sum(x[2] for x in wt), dur))
        wt = [(w, s, d) for (w, s, d) in wt]
        end = wt[-1][1] + wt[-1][2] + PAD
        scenes.append({**sc, "start": t, "end": end, "words": wt})
        t = end
    return scenes, t


def caption_chunks(words, max_words=7):
    chunks, cur = [], []
    for w in words:
        cur.append(w)
        if len(cur) >= max_words or w[0][-1] in ".?!,":
            chunks.append(cur); cur = []
    if cur:
        chunks.append(cur)
    return [(" ".join(w[0] for w in ch), ch[0][1], ch[-1][1] + ch[-1][2]) for ch in chunks]


def draw_caption(c, text, cur_word_idx, t_since):
    size = 54
    words = text.split()
    widths = [c.text_width(w + " ", size) for w in words]
    x = (W - sum(widths)) / 2
    y = H - 110
    c.rect(x - 30, y - 50, x + sum(widths) + 20, y + 50, fill=(0, 0, 0, 120), outline=None, r=20)
    for i, w in enumerate(words):
        col = (255, 222, 40) if i == cur_word_idx else (255, 255, 255)
        c.text(x, y, w, size, fill=col, sw=6, anchor="lm")
        x += widths[i]


def render_frame(args):
    i, timeline, show_badge = args
    t = i / FPS
    sc = next((s for s in timeline if s["start"] <= t < s["end"]), timeline[-1])
    lt = t - sc["start"]
    c = Canvas()
    zoom, cx, cy = SCENES[sc["id"]](c, lt, sc["end"] - sc["start"])
    # субтитры поверх картинки, но вне камеры — рисуем после кропа
    cw, ch = W * SS / zoom, H * SS / zoom
    x0 = min(max(cx * SS - cw / 2, 0), W * SS - cw)
    y0 = min(max(cy * SS - ch / 2, 0), H * SS - ch)
    frame = c.img.crop((int(x0), int(y0), int(x0 + cw), int(y0 + ch))).resize((W * SS, H * SS), Image.BILINEAR)
    c2 = Canvas(frame)
    for text, s, e in sc["chunks"]:
        if s <= t < e:
            draw_caption(c2, text, _word_index(sc["words"], s, t), t - s)
            break
    # затухание в чёрный на стыках сцен
    fade = min(1.0, lt / 0.25, (sc["end"] - t) / 0.25)
    if show_badge:
        c2.rect(30, 30, 520, 90, fill=(220, 40, 40, 220), outline=None, r=14)
        c2.text(275, 60, "ЗАГЛУШКА: ГОЛОС И АРТ", 26, sw=0)
    out = frame.resize((W, H), Image.LANCZOS)
    if fade < 1:
        out = Image.blend(Image.new("RGB", (W, H), (0, 0, 0)), out, max(0.0, fade))
    return out.tobytes()


def _word_index(words, chunk_start, t):
    k = -1
    for (w, s, d) in words:
        if s < chunk_start - 1e-6:
            continue
        if s <= t:
            k += 1
    return k


def make_audio(timeline, total, path):
    """Заглушка звука: тихий эмбиент-пэд + короткий «тик» на каждое слово, чтобы было
    слышно, что синхронизация работает. Будет заменено реальной озвучкой."""
    n = int(total * SR)
    tt = np.arange(n) / SR
    chords = [(220.0, 277.18, 329.63), (196.0, 246.94, 293.66), (174.61, 220.0, 261.63), (196.0, 246.94, 329.63)]
    pad = np.zeros(n)
    seg = 4.0
    for k in range(int(math.ceil(total / seg))):
        a, b = int(k * seg * SR), min(n, int((k + 1) * seg * SR) + SR // 2)
        env = np.sin(np.linspace(0, math.pi, b - a))
        for f in chords[k % 4]:
            pad[a:b] += env * (np.sin(2 * math.pi * f * tt[a:b]) + 0.3 * np.sin(4 * math.pi * f * tt[a:b]))
    pad *= 0.035
    blip = np.zeros(n)
    bl = int(0.05 * SR)
    shape = np.sin(2 * math.pi * 660 * np.arange(bl) / SR) * np.exp(-np.arange(bl) / (0.012 * SR))
    for sc in timeline:
        for (w, s, d) in sc["words"]:
            i = int(s * SR)
            if i + bl < n:
                blip[i:i + bl] += shape * 0.12
    mix = np.clip(pad + blip, -1, 1)
    data = (np.stack([mix, mix], 1) * 32767).astype(np.int16)
    with wave.open(path, "wb") as f:
        f.setnchannels(2); f.setsampwidth(2); f.setframerate(SR)
        f.writeframes(data.tobytes())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--script", default=os.path.join(ROOT, "script.json"))
    ap.add_argument("--out", default=os.path.join(ROOT, "out"))
    ap.add_argument("--still", type=float, help="отрендерить один кадр на этой секунде в PNG")
    ap.add_argument("--no-badge", action="store_true")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    script = json.load(open(a.script))
    timeline, total = build_timeline(script)
    for sc in timeline:
        sc["chunks"] = caption_chunks(sc["words"])
    badge = not a.no_badge
    if a.still is not None:
        img = Image.frombytes("RGB", (W, H), render_frame((int(a.still * FPS), timeline, badge)))
        p = os.path.join(a.out, f"still_{a.still:.1f}.png"); img.save(p); print(p); return

    nframes = int(total * FPS)
    print(f"Длительность {total:.1f} c, кадров {nframes}, сцен {len(timeline)}")
    wav = os.path.join(a.out, "audio.wav")
    make_audio(timeline, total, wav)
    mp4 = os.path.join(a.out, "video.mp4")
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
                           "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-i", wav,
                           "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
                           "-c:a", "aac", "-b:a", "160k", "-shortest", "-movflags", "+faststart", mp4],
                          stdin=subprocess.PIPE)
    t0 = time.time()
    with Pool(os.cpu_count()) as pool:
        for k, buf in enumerate(pool.imap(render_frame, ((i, timeline, badge) for i in range(nframes)), chunksize=8)):
            ff.stdin.write(buf)
            if k % (FPS * 10) == 0:
                print(f"  {k / FPS:5.0f} c / {total:.0f} c  ({time.time() - t0:.0f} c прошло)", flush=True)
    ff.stdin.close(); ff.wait()
    # субтитры отдельным файлом — пригодятся для загрузки на YouTube
    with open(os.path.join(a.out, "captions.srt"), "w") as f:
        n = 1
        for sc in timeline:
            for text, s, e in sc["chunks"]:
                ts = lambda x: f"{int(x // 3600):02}:{int(x % 3600 // 60):02}:{int(x % 60):02},{int(x * 1000 % 1000):03}"
                f.write(f"{n}\n{ts(s)} --> {ts(e)}\n{text}\n\n"); n += 1
    print(f"Готово: {mp4} за {time.time() - t0:.0f} c")


if __name__ == "__main__":
    main()
