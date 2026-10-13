# Extract vidIQ channel_search JSON (raw or MCP-wrapped) into TSV rows. Usage: vq_extract.py FILE TOPIC >> vq.tsv
import json, sys, re
txt = open(sys.argv[1], encoding='utf-8', errors='replace').read()
topic = sys.argv[2]
def find_channels(o):
    if isinstance(o, dict):
        if isinstance(o.get('channels'), list): return o['channels']
        for v in o.values():
            r = find_channels(v)
            if r: return r
    if isinstance(o, list):
        for v in o:
            r = find_channels(v)
            if r: return r
    if isinstance(o, str) and '"channels"' in o:
        try: return find_channels(json.loads(o))
        except Exception: return None
    return None
try: data = json.loads(txt)
except Exception:
    m = re.search(r'\{"channels".*\}', txt, re.S); data = json.loads(m.group(0))
ch = find_channels(data) or []
F = ['channelId', 'channelTitle', 'niche', 'subNiches', 'mainCategory', 'subscriberCount', 'viewCount', 'videoCount', 'avgViews',
     'estimatedEarnings', 'subsGrowth30d', 'subsGrowth1y', 'viewsGrowth30d', 'viewsGrowth1y', 'longAvgDuration30d', 'longAvgDuration1y',
     'longVideoCount30d', 'longVideoCount1y', 'longViewCount30d', 'longViewCount1y', 'shortViewCount30d', 'shortVideoCount30d',
     'publishedAt', 'lastVideoPublished', 'isFaceless', 'breakoutChannel', 'country', 'languages']
for c in ch:
    vals = [topic]
    for k in F:
        v = c.get(k)
        if isinstance(v, list): v = '|'.join(map(str, v))
        vals.append('' if v is None else str(v).replace('\t', ' ').replace('\n', ' '))
    print('\t'.join(vals))
print(f'{topic}: {len(ch)} channels', file=sys.stderr)
