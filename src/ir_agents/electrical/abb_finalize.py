"""Finalize ABB manifest (adds CMD release page) and print coverage summary."""
import os, sys, json, csv
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from irlib import *
T = 'ABBN.SW'
man_path = os.path.join(RAW_IR, T, 'manifest_rows.json')
man = json.load(open(man_path))
extra = dict(ticker=T, local_path=f'data/raw/ir/{T}/2025Q4_cmd_release.html',
             url='https://www.mfn.se/eqs/a/abb/abb-ltd-abb-capital-markets-day-2025',
             doc_type='cmd_release', fiscal_period='2025Q4', pub_date='2025-11-18')
# use exact MFN href
items = json.load(open(os.path.join(RAW_IR, T, 'pages', 'mfn_items.json')))
for it in items:
    if it['date'] == '2025-11-18' and 'Capital Markets' in it['title']:
        extra['url'] = 'https://www.mfn.se' + it['href']
man = [m for m in man if m['local_path'] != extra['local_path']] + [extra]
json.dump(man, open(man_path, 'w'), indent=0)
p = write_manifest(T, [dict(m) for m in man])
rows = list(csv.DictReader(open(p)))
print(p, len(rows))
from collections import Counter
print(Counter(r['doc_type'] for r in rows))
print(min(r['fiscal_period'] for r in rows), max(r['fiscal_period'] for r in rows))
missing = [r['local_path'] for r in rows if not os.path.exists(os.path.join(ROOT, r['local_path']))]
print('missing files', missing)
