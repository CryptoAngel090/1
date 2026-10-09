#!/usr/bin/env python3
"""Ищет свежевыложенные полицейские видео на публичных порталах NextRequest.

Ничего не скачивает и не требует логина: читает открытый список документов
(/client/documents) и печатает таблицу с прямыми ссылками на файлы.

Пример:
    python3 tools/nextrequest_watch.py --days 30 --out research/reserve.md
"""
import argparse, concurrent.futures as cf, datetime as dt, json, re, urllib.request
from collections import defaultdict
from pathlib import Path

VIDEO = ("mp4", "mov", "avi", "wmv", "m4v", "mpg", "asf", "mkv", "zip")
TERMS = ["axon", "bwc", "body", "bodycam", "dash", "icv", "squad", "fleet", "watchguard",
         "ois", "arrest", "interview", "interrogation", "video", "mp4"]
POLICE = re.compile(r"axon|bwc|body|dash|icv|in.?car|squad|fleet|extraction|ois|officer|"
                    r"deputy|sgt|ofc|arrest|watchguard|interview|interrog|redact|mav|cam\b", re.I)
HEAD = {"User-Agent": "Mozilla/5.0", "Accept": "application/json"}


def get(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=HEAD), timeout=40) as r:
        return json.load(r)


def scan(sub, since):
    found = {}
    for term in TERMS:
        try:
            docs = get(f"https://{sub}.nextrequest.com/client/documents"
                       f"?per_page=100&page_number=1&search_term={term}").get("documents", [])
        except Exception:
            continue
        for d in docs:
            ext = (d.get("file_extension") or "").lower()
            if d.get("state") != "public" or ext not in VIDEO or not POLICE.search(d["title"]):
                continue
            try:
                created = dt.datetime.strptime(d["created_at"], "%m/%d/%Y").date()
            except Exception:
                continue
            if created >= since:
                found[d["id"]] = dict(portal=sub, id=d["id"], title=d["title"], ext=ext,
                                      created=created.isoformat(), request=d.get("pretty_id"))
    return list(found.values())


def request_text(sub, rid):
    try:
        t = get(f"https://{sub}.nextrequest.com/client/requests/{rid}").get("request_text", "")
        return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", t)).strip()[:220]
    except Exception:
        return ""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=30)
    ap.add_argument("--portals", default=str(Path(__file__).with_name("nextrequest_portals.txt")))
    ap.add_argument("--out", default="")
    a = ap.parse_args()
    since = dt.date.today() - dt.timedelta(days=a.days)
    subs = [s.strip() for s in open(a.portals) if s.strip()]
    with cf.ThreadPoolExecutor(12) as p:
        rows = [r for rs in p.map(lambda s: scan(s, since), subs) for r in rs]
    cases = defaultdict(list)
    for r in rows:
        cases[(r["portal"], r["request"])].append(r)
    lines = [f"# Свежие полицейские видео на NextRequest (с {since}, найдено файлов: {len(rows)}, дел: {len(cases)})", "",
             "| портал | дело | файлов | последняя выкладка | о чём запрос | пример файла |", "|---|---|---|---|---|---|"]
    for (sub, rid), fs in sorted(cases.items(), key=lambda kv: (-len(kv[1]), kv[0])):
        fs.sort(key=lambda f: f["created"], reverse=True)
        txt = request_text(sub, rid).replace("|", "/") if rid else ""
        req = f"https://{sub}.nextrequest.com/requests/{rid}" if rid else "—"
        lines.append(f"| {sub} | {req} | {len(fs)} | {fs[0]['created']} | {txt} | "
                     f"https://{sub}.nextrequest.com/documents/{fs[0]['id']} ({fs[0]['title'][:60]}) |")
    out = "\n".join(lines) + "\n"
    if a.out:
        Path(a.out).write_text(out, encoding="utf-8")
    print(out)


if __name__ == "__main__":
    main()
