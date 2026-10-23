"""Download ABB quarterly docs (press release, financial information, presentation) and extract text."""
import os, sys, re, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from irlib import *

T = 'ABBN.SW'
rows = json.load(open(os.path.join(RAW_IR, T, 'pages', 'qr_table.json')))
ev = {}
import csv
for r in csv.DictReader(open(os.path.join(PROC_IR, f'{T}_events.csv'))):
    if r['event_type'] in ('Q1', 'Q2', 'Q3', 'Q4'):
        ev[r['fiscal_period']] = r['event_date']
COLMAP = {'Press release': 'release', 'Financial information': 'fininfo', 'Presentation': 'presentation'}
start = sys.argv[1] if len(sys.argv) > 1 else '2022Q1'
only = sys.argv[2].split(',') if len(sys.argv) > 2 else list(COLMAP.values())
f = Fetcher()
man_path = os.path.join(RAW_IR, T, 'manifest_rows.json')
man = json.load(open(man_path)) if os.path.exists(man_path) else []
have = {m['local_path'] for m in man}
for r in rows:
    m = re.fullmatch(r'Q([1-4]) (\d{4})', r['label'])
    if not m or r['col'] not in COLMAP:
        continue
    fp = f'{m.group(2)}Q{m.group(1)}'
    if fp < start:
        continue
    dt = COLMAP[r['col']]
    if dt not in only:
        continue
    if r['text'].upper().startswith('XLS'):
        continue
    url = r['url']
    local = os.path.join(RAW_IR, T, f'{fp}_{dt}.pdf')
    ok, st, _ = f.download(url, local)
    if not ok or not is_pdf(local):
        print('FAIL', fp, dt, st, url[:100])
        if os.path.exists(local) and not is_pdf(local):
            os.remove(local)
        continue
    txt, n = to_text(local, T, fp, dt)
    rel = local[len(ROOT) + 1:]
    if rel not in have:
        man.append(dict(ticker=T, local_path=rel, url=url, doc_type=dt, fiscal_period=fp, pub_date=ev.get(fp, '')))
        have.add(rel)
    print(fp, dt, os.path.getsize(local), n)
json.dump(man, open(man_path, 'w'), indent=0)
write_manifest(T, [dict(x) for x in man])
