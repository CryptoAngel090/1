#!/usr/bin/env python3
"""footage_gate.py — cheap-first checks that a bodycam file is worth editing.

Gates (run in this order, stop at the first FAIL):
  probe    — ffprobe only (works on a local path or an HTTP(S) URL via range reads):
             duration, resolution, aspect, audio stream, encoder tags.
  sample   — N still frames pulled remotely (one fresh URL per frame) -> contact sheet,
             mean brightness, how many frames are near-identical (static / blurred-out).
  analyze  — full local file: per-second motion energy, loudness peaks, muted spans
             (redacted audio), optional transcript keywords -> "action minutes".

Usage:
  footage_gate.py probe   FILE_OR_URL
  footage_gate.py sample  FILE_OR_URL  --out sheet.jpg [--n 12]
  footage_gate.py analyze FILE [--transcript whisper.json] [--sheet top.jpg] [--json out.json]

Thresholds live in CONFIG and MUST be calibrated on ~30 files you have already labelled
good/bad by hand (see calibrate notes at the bottom). The defaults are starting points.
"""
import argparse, json, math, re, subprocess, sys
from pathlib import Path

CONFIG = {
    'min_total_minutes': 20,      # whole incident (all files of the request), checked by caller
    'min_main_minutes': 12,       # the main file itself
    'min_height': 720,
    'aspect_min': 1.70,           # 16:9 = 1.777; 4:3 = 1.333
    'muted_span_sec': 8,          # silence longer than this = probably redacted audio
    'max_muted_share': 0.25,      # >25% of the file muted -> reject
    'dark_luma': 35,              # mean Y below this (0-255) = too dark to use
    'motion_rel': 2.0,            # second is "moving" if motion > rel * file's calm (p25) level ...
    'motion_abs': 6.0,            # ... and above this absolute floor (mean abs diff, 0-255)
    'loud_lufs': -16.0,           # momentary loudness above this = shouting / struggle
    'min_action_minutes': 8,
}
ACTION_WORDS = re.compile(
    r"\b(stop resisting|get on the ground|hands behind|put your hands|you'?re under arrest|"
    r"stop|taser|tase|let go|don'?t move|get down|show me your hands|get out of the car|"
    r"step out|turn around|on your stomach|give me your hand|quit|cuff)\b", re.I)


def run(cmd, timeout=None):
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)


# ---------------------------------------------------------------- probe
def probe(src):
    """Header-only facts. ffprobe reads the moov atom with HTTP range requests, so a
    remote MP4 is not downloaded (if moov is at the end it reads the tail)."""
    r = run(['ffprobe', '-v', 'error', '-show_format', '-show_streams', '-of', 'json', src], timeout=60)
    if r.returncode != 0:
        return {'ok': False, 'error': r.stderr.strip()[:300]}
    d = json.loads(r.stdout)
    v = next((s for s in d['streams'] if s.get('codec_type') == 'video'), None)
    a = next((s for s in d['streams'] if s.get('codec_type') == 'audio'), None)
    fmt = d.get('format', {})
    dur = float(fmt.get('duration') or (v or {}).get('duration') or 0)
    w, h = int((v or {}).get('width', 0)), int((v or {}).get('height', 0))
    rot = 0
    for sd in (v or {}).get('side_data_list', []):
        rot = abs(int(sd.get('rotation', 0) or 0))
    if rot in (90, 270): w, h = h, w
    tags = {**fmt.get('tags', {}), **(v or {}).get('tags', {})}
    out = {
        'ok': True, 'duration_min': round(dur / 60, 2), 'width': w, 'height': h,
        'aspect': round(w / h, 3) if h else 0, 'fps': (v or {}).get('avg_frame_rate'),
        'has_audio': a is not None, 'audio_channels': (a or {}).get('channels'),
        'bitrate_kbps': int(fmt.get('bit_rate', 0) or 0) // 1000,
        # Edited agency releases often carry an editor encoder tag (Premiere, Resolve,
        # HandBrake…). Raw camera exports usually do not. Treat as a hint, not a verdict.
        'encoder_tags': {k: v for k, v in tags.items() if k.lower() in ('encoder', 'handler_name', 'com.apple.quicktime.software', 'comment', 'title')},
    }
    fails = []
    if out['height'] < CONFIG['min_height']: fails.append(f"height {h}<{CONFIG['min_height']}")
    if out['aspect'] < CONFIG['aspect_min']: fails.append(f"aspect {out['aspect']} (not 16:9)")
    if not out['has_audio']: fails.append('no audio stream')
    if out['duration_min'] < CONFIG['min_main_minutes']: fails.append(f"only {out['duration_min']} min")
    out['fails'] = fails
    out['pass'] = not fails
    return out


# ---------------------------------------------------------------- sample
def sample(src_or_fn, out_jpg, n=12, duration=None):
    """Grab n frames spread over the file. `src_or_fn` may be a callable returning a FRESH
    signed URL each call (portal links die after ~60 s), so every frame gets its own link."""
    from PIL import Image
    import numpy as np
    get = src_or_fn if callable(src_or_fn) else (lambda: src_or_fn)
    if duration is None:
        duration = probe(get())['duration_min'] * 60
    tiles, lumas = [], []
    tmp = Path(out_jpg).with_suffix('.tmp.jpg')
    for i in range(n):
        t = duration * (i + 0.5) / n
        r = run(['ffmpeg', '-v', 'error', '-y', '-ss', f'{t:.1f}', '-i', get(), '-frames:v', '1',
                 '-vf', 'scale=320:-2', str(tmp)], timeout=60)
        if r.returncode or not tmp.exists():
            continue
        im = Image.open(tmp).convert('RGB'); tiles.append((t, im.copy()))
        lumas.append(float(np.asarray(im.convert('L')).mean()))
    tmp.unlink(missing_ok=True)
    if not tiles:
        return {'ok': False}
    # near-identical consecutive frames -> static scene / camera covered / full-frame blur
    same = 0
    for (_, a), (_, b) in zip(tiles, tiles[1:]):
        da = np.asarray(a.convert('L').resize((32, 18)), dtype=float)
        db = np.asarray(b.convert('L').resize((32, 18)), dtype=float)
        if np.abs(da - db).mean() < 4: same += 1
    cols = 4; rows = math.ceil(len(tiles) / cols); tw, th = tiles[0][1].size
    sheet = Image.new('RGB', (cols * tw, rows * th))
    from PIL import ImageDraw
    d = ImageDraw.Draw(sheet)
    for k, (t, im) in enumerate(tiles):
        x, y = (k % cols) * tw, (k // cols) * th
        sheet.paste(im, (x, y)); d.rectangle((x, y, x + 52, y + 14), fill='black')
        d.text((x + 3, y + 2), f'{int(t)//60:02d}:{int(t)%60:02d}', fill='yellow')
    sheet.save(out_jpg, quality=85)
    dark = sum(1 for l in lumas if l < CONFIG['dark_luma'])
    return {'ok': True, 'frames': len(tiles), 'dark_frames': dark, 'static_pairs': same,
            'pass': dark <= len(tiles) // 3 and same <= len(tiles) // 3, 'sheet': str(out_jpg)}


# ---------------------------------------------------------------- analyze
def motion_per_second(path):
    """Mean absolute frame difference on 64x36 grey frames at 4 fps -> one value per second.
    Running / struggling bodycam = large global change; standing and talking = small."""
    import numpy as np
    W, H, FPS = 64, 36, 4
    p = subprocess.Popen(['ffmpeg', '-v', 'error', '-i', str(path), '-vf', f'fps={FPS},scale={W}:{H},format=gray',
                          '-f', 'rawvideo', '-'], stdout=subprocess.PIPE)
    prev, diffs, lum = None, [], []
    while True:
        buf = p.stdout.read(W * H)
        if len(buf) < W * H: break
        f = np.frombuffer(buf, dtype=np.uint8).astype(np.int16)
        lum.append(f.mean())
        diffs.append(0.0 if prev is None else float(np.abs(f - prev).mean()))
        prev = f
    p.wait()
    sec = [max(diffs[i:i + FPS]) if diffs[i:i + FPS] else 0 for i in range(0, len(diffs), FPS)]
    lsec = [sum(lum[i:i + FPS]) / len(lum[i:i + FPS]) for i in range(0, len(lum), FPS)]
    return sec, lsec


def loudness_per_second(path):
    """Max momentary loudness (LUFS) per second via ebur128."""
    r = run(['ffmpeg', '-v', 'verbose', '-nostats', '-i', str(path), '-vn', '-af', 'ebur128=framelog=verbose', '-f', 'null', '-'])
    per = {}
    for m in re.finditer(r't:\s*([\d.]+)\s+TARGET.*?M:\s*(-?[\d.]+|-inf)', r.stderr):
        t, mval = int(float(m.group(1))), m.group(2)
        v = -120.0 if 'inf' in mval else float(mval)
        per[t] = max(per.get(t, -120.0), v)
    n = max(per) + 1 if per else 0
    return [per.get(i, -120.0) for i in range(n)]


def muted_spans(path):
    r = run(['ffmpeg', '-v', 'info', '-nostats', '-i', str(path), '-vn', '-af',
             f"silencedetect=noise=-50dB:d={CONFIG['muted_span_sec']}", '-f', 'null', '-'])
    starts = [float(x) for x in re.findall(r'silence_start: ([\d.]+)', r.stderr)]
    ends = [float(x) for x in re.findall(r'silence_end: ([\d.]+)', r.stderr)]
    return list(zip(starts, ends))


def keywords_per_minute(transcript_json):
    """Accepts faster-whisper / openai-whisper style JSON: {"segments":[{"start":..,"text":..}]}"""
    if not transcript_json: return {}, {}
    d = json.loads(Path(transcript_json).read_text())
    kw, words = {}, {}
    for s in d.get('segments', d if isinstance(d, list) else []):
        m = int(float(s['start']) // 60)
        kw[m] = kw.get(m, 0) + len(ACTION_WORDS.findall(s.get('text', '')))
        words[m] = words.get(m, 0) + len(s.get('text', '').split())
    return kw, words


def analyze(path, transcript=None, sheet=None):
    import statistics as st
    meta = probe(str(path))
    mot, lum = motion_per_second(path)
    loud = loudness_per_second(path) if meta.get('has_audio') else []
    mutes = muted_spans(path) if meta.get('has_audio') else []
    kw, words = keywords_per_minute(transcript)
    calm = sorted(mot)[len(mot) // 4] if mot else 1                  # 25th percentile = this file's 'calm' level
    thr = max(CONFIG['motion_abs'], min(CONFIG['motion_rel'] * calm, 3 * CONFIG['motion_abs']))  # capped: an all-action file must still pass
    n_min = math.ceil(len(mot) / 60)
    minutes = []
    for m in range(n_min):
        ms = mot[m * 60:(m + 1) * 60]
        ls = loud[m * 60:(m + 1) * 60] if loud else []
        moving = sum(1 for x in ms if x > thr)                      # seconds with strong motion
        loud_s = sum(1 for x in ls if x > CONFIG['loud_lufs'])       # seconds of shouting
        dark = bool((sum(lum[m * 60:(m + 1) * 60]) / max(1, len(lum[m * 60:(m + 1) * 60]))) < CONFIG['dark_luma'])
        k = kw.get(m, 0)
        # Action minute: real movement for a good part of the minute AND a sound cue,
        # or lots of shouting plus command words (struggle on the ground can look still).
        action = (moving >= 15 and (loud_s >= 3 or k >= 1)) or (loud_s >= 10 and k >= 2)
        minutes.append({'min': m, 'moving_s': moving, 'loud_s': loud_s, 'kw': k,
                        'words': words.get(m, 0), 'dark': dark, 'action': bool(action and not dark)})
    act = [x['min'] for x in minutes if x['action']]
    muted = sum(e - s for s, e in mutes)
    dur = len(mot)
    fails = list(meta.get('fails', []))
    if muted / max(1, dur) > CONFIG['max_muted_share']: fails.append(f'muted/redacted audio {muted/60:.1f} min')
    if len(act) < CONFIG['min_action_minutes']: fails.append(f'only {len(act)} action minutes')
    first_action = act[0] if act else None
    res = {'file': str(path), 'probe': meta, 'motion_threshold': round(thr, 2), 'action_minutes': len(act),
           'action_list': act, 'first_action_min': first_action, 'muted_min': round(muted / 60, 1),
           'minutes': minutes, 'fails': fails, 'pass': not fails}
    if sheet and act:
        res['sheet'] = top_windows_sheet(path, minutes, sheet)
    return res


def top_windows_sheet(path, minutes, out_jpg, k=8):
    """Contact sheet of the k strongest minutes (3 frames each) — this is what you show
    Claude to confirm 'real action' instead of spending a Gemini quota."""
    from PIL import Image, ImageDraw
    best = sorted(minutes, key=lambda x: (x['action'], x['moving_s'] + x['loud_s'] + 5 * x['kw']), reverse=True)[:k]
    best.sort(key=lambda x: x['min'])
    tiles = []
    tmp = Path(out_jpg).with_suffix('.tmp.jpg')
    for b in best:
        for off in (10, 30, 50):
            t = b['min'] * 60 + off
            r = run(['ffmpeg', '-v', 'error', '-y', '-ss', str(t), '-i', str(path), '-frames:v', '1', '-vf', 'scale=320:-2', str(tmp)])
            if r.returncode == 0 and tmp.exists():
                tiles.append((t, Image.open(tmp).convert('RGB').copy()))
    tmp.unlink(missing_ok=True)
    if not tiles: return None
    tw, th = tiles[0][1].size; cols = 3; rows = math.ceil(len(tiles) / cols)
    sheet = Image.new('RGB', (cols * tw, rows * th)); d = ImageDraw.Draw(sheet)
    for i, (t, im) in enumerate(tiles):
        x, y = (i % cols) * tw, (i // cols) * th
        sheet.paste(im, (x, y)); d.rectangle((x, y, x + 52, y + 14), fill='black')
        d.text((x + 3, y + 2), f'{int(t)//60:02d}:{int(t)%60:02d}', fill='yellow')
    sheet.save(out_jpg, quality=85)
    return str(out_jpg)


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest='cmd', required=True)
    a = sub.add_parser('probe'); a.add_argument('src')
    b = sub.add_parser('sample'); b.add_argument('src'); b.add_argument('--out', required=True); b.add_argument('--n', type=int, default=12)
    c = sub.add_parser('analyze'); c.add_argument('file'); c.add_argument('--transcript'); c.add_argument('--sheet'); c.add_argument('--json')
    args = ap.parse_args()
    if args.cmd == 'probe': res = probe(args.src)
    elif args.cmd == 'sample': res = sample(args.src, args.out, args.n)
    else:
        res = analyze(args.file, args.transcript, args.sheet)
        if args.json: Path(args.json).write_text(json.dumps(res, indent=1))
        res = {k: v for k, v in res.items() if k != 'minutes'}
    print(json.dumps(res, indent=1))


if __name__ == '__main__':
    main()

# Calibration (do this once, ~1 hour): take 15 files you KNOW are good and 15 known junk
# ("people standing and talking", clips, redacted). Run `analyze --json` on all 30, then
# look at moving_s / loud_s / kw per minute for both groups and move motion_abs,
# motion_rel and loud_lufs until good files get >= 8 action minutes and junk gets < 4.
