# Score ~100 US adult niches from vidIQ channel_search samples (vq_*.tsv).
import glob, os, statistics as st, json, csv, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rpm_bench import bench
D = os.path.dirname(os.path.abspath(__file__))
F = ['topic', 'channelId', 'channelTitle', 'niche', 'subNiches', 'mainCategory', 'subscriberCount', 'viewCount', 'videoCount', 'avgViews',
     'estimatedEarnings', 'subsGrowth30d', 'subsGrowth1y', 'viewsGrowth30d', 'viewsGrowth1y', 'longAvgDuration30d', 'longAvgDuration1y',
     'longVideoCount30d', 'longVideoCount1y', 'longViewCount30d', 'longViewCount1y', 'shortViewCount30d', 'shortVideoCount30d',
     'publishedAt', 'lastVideoPublished', 'isFaceless', 'breakoutChannel', 'country', 'languages']
NUM = F[6:23]
rows = []
for fp in sorted(glob.glob(os.path.join(D, 'vq_*.tsv'))):
    for line in open(fp, encoding='utf-8', errors='replace'):
        p = line.rstrip('\n').split('\t')
        if len(p) != len(F): continue
        r = dict(zip(F, p))
        for k in NUM:
            try: r[k] = float(r[k]) if r[k] != '' else None
            except ValueError: r[k] = None
        views30 = (r['longViewCount30d'] or 0) + (r['shortViewCount30d'] or 0)
        r['rpm'] = r['estimatedEarnings'] / (views30 / 1000) if r['estimatedEarnings'] and views30 > 20000 else None
        if r['rpm'] is not None and not (0.2 <= r['rpm'] <= 60): r['rpm'] = None
        lv, lc = r['longViewCount30d'], r['longVideoCount30d']
        r['vpv'] = lv / lc if lv and lc else None                         # recent views per long video
        r['reach'] = r['vpv'] / r['subscriberCount'] if r['vpv'] and r['subscriberCount'] else None
        r['young'] = (r['publishedAt'] or '0') >= '2024-01-01'
        rows.append(r)
uniq = {r['channelId'] for r in rows}
print('rows', len(rows), 'unique channels', len(uniq))

def med(xs):
    xs = [x for x in xs if x is not None]
    return st.median(xs) if xs else None
stats = {}
for t in sorted({r['topic'] for r in rows}):
    g = [r for r in rows if r['topic'] == t]
    if len(g) < 10: continue
    y = [r for r in g if r['young']]
    yw = [r for r in y if (r['longViewCount30d'] or 0) >= 300000]          # new channel already pulling 300k+ long-form views/month
    grp, lo, hi = bench(t)
    stats[t] = dict(n=len(g), grp=grp, rpm_lo=lo, rpm_hi=hi, rpm=(lo + hi) / 2, vq_rpm=med([r['rpm'] for r in g]), earn=med([r['estimatedEarnings'] for r in g]),
                    dur=(med([r['longAvgDuration1y'] for r in g]) or 0) / 60, reach=med([r['reach'] for r in g]),
                    vpv=med([r['vpv'] for r in g]), growth=med([r['viewsGrowth1y'] for r in g]),
                    giants=sum(1 for r in g if (r['subscriberCount'] or 0) >= 1e6), young=len(y), young_win=len(yw),
                    ywr=len(yw) / len(y) if y else 0, faceless=sum(1 for r in g if r['isFaceless'] == 'True') / len(g),
                    medsubs=med([r['subscriberCount'] for r in g]))
def pct(key, rev=False):
    vals = sorted(v[key] for v in stats.values() if v[key] is not None)
    out = {}
    for t, v in stats.items():
        x = v[key]
        k = .5 if x is None else sum(1 for y in vals if y < x) / max(1, len(vals) - 1)
        out[t] = 1 - k if rev else k
    return out
W = {'rpm': .35, 'ywr': .20, 'reach': .10, 'dur': .10, 'growth': .15, 'giants': .10}
P = {k: pct(k, rev=(k == 'giants')) for k in W}
for t, v in stats.items(): v['score'] = round(100 * sum(W[k] * P[k][t] for k in W), 1)
json.dump(stats, open(os.path.join(D, 'vq_stats.json'), 'w'), indent=1)
with open(os.path.join(D, 'vq_channels.csv'), 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=F + ['rpm', 'vpv', 'reach', 'young'], extrasaction='ignore'); w.writeheader(); w.writerows(rows)
print(f"{'topic':46} {'n':>3} {'score':>5} {'RPM':>7} {'earn$':>7} {'dur':>5} {'reach':>5} {'gr1y%':>6} {'1M+':>3} {'new':>3} {'newWin':>6} {'face':>4}")
for t, v in sorted(stats.items(), key=lambda kv: -kv[1]['score']):
    print(f"{t[:46]:46} {v['n']:>3} {v['score']:>5} {v['rpm_lo']:>3}-{v['rpm_hi']:<3} {(v['earn'] or 0):>7.0f} {v['dur']:>5.1f} {(v['reach'] or 0):>5.2f} "
          f"{(v['growth'] or 0):>6.0f} {v['giants']:>3} {v['young']:>3} {v['young_win']:>2}/{v['young']:<3} {100*v['faceless']:>3.0f}%")
