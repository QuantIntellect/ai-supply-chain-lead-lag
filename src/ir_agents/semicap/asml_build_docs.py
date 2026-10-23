"""Build ASML document set: EDGAR press releases + presentations (all quarters 2014Q4-2026Q3), transcript PDFs from
asml.com-hosted storage (ourbrand.asml.com / Sitecore edge). Writes text files and _manifest_rows.json."""
import sys, os, re, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import irlib
T = 'ASML.AS'
R = irlib.raw_dir(T)
idx = json.load(open(os.path.join(R, 'edgar_q', '_index.json')))
date_of = {}
rows = []
best = {}
for e in idx:
    name = e['url'].rsplit('/', 1)[1].lower()
    date_of[e['period']] = e['date']
    if 'financial_statements' in name:
        continue
    kind = 'presentation' if re.search(r'presentation|pres(?!s)|presq', name) else 'press_release'
    score = 2 if re.search(r'pressrelease|dex991', name) else 1
    k = (e['period'], kind)
    if k not in best or score > best[k][0]:
        best[k] = (score, e)
for (per, kind), (_, e) in sorted(best.items()):
    path = os.path.join(irlib.ROOT, e['path'])
    tp = irlib.write_text(T, per, kind, irlib.to_text(path))
    rows.append({'ticker': T, 'local_path': e['path'], 'url': e['url'], 'doc_type': kind, 'fiscal_period': per,
                 'pub_date': e['date']})
# transcript PDFs
links = json.load(open(os.path.join(R, '_wayback_doclinks.json')))
links.setdefault('2026Q2', []).extend([
    'https://ourbrand.asml.com/asset/1fd3908a-0381-47b5-9b69-a3094f656651/2026_07_15-ASML-Transcript-investor-call-Q2-2026.pdf'])
extra = json.load(open(os.path.join(R, '_extra_links.json'))) if os.path.exists(os.path.join(R, '_extra_links.json')) else {}
for k, v in extra.items():
    links.setdefault(k, []).extend(v)
QW = {'Q1': ['q1', 'q-1'], 'Q2': ['q2'], 'Q3': ['q3'], 'Q4': ['q4']}
for per, urls in sorted(links.items()):
    y, q = per[:4], per[4:]
    for u in urls:
        fn = u.rsplit('/', 1)[1].lower()
        if re.search(r'transcript-investor-call|transcript-investor-call|results.investor.call|investor-call-prepared|investor-call-script', fn):
            kind = 'transcript'
        elif re.search(r'transcript', fn):
            kind = 'video_transcript'
        else:
            continue
        # sanity: filename must not name a different quarter/year
        qs = set(re.findall(r'q([1-4])', fn))
        ys = set(re.findall(r'20(1[5-9]|2[0-6])', fn))
        if qs and q[1] not in qs:
            continue
        if per[:4] == '2020' and q == 'Q2' and '04-15' in fn:
            continue
        src = re.sub(r'^https://www\.asml\.com/-/media/asml/',
                     'https://edge.sitecorecloud.io/asmlnetherlaaea-asmlcom-prd-5369/media/project/asmlcom/asmlcom/asml/', u)
        path = os.path.join(R, 'pdf', f'{per}_{kind}.pdf')
        st, b = irlib.fetch(src, path, timeout=90)
        if st != 200 or not b.startswith(b'%PDF'):
            print('FAIL', per, kind, st, src[-80:]); continue
        irlib.write_text(T, per, kind, irlib.to_text(path))
        rows.append({'ticker': T, 'local_path': os.path.relpath(path, irlib.ROOT), 'url': src, 'doc_type': 'transcript',
                     'fiscal_period': per, 'pub_date': date_of.get(per, '')})
        print(per, kind, len(b) // 1024, 'KB')
json.dump(rows, open(os.path.join(R, '_manifest_rows.json'), 'w'), indent=0)
from collections import Counter
print(Counter((r['doc_type']) for r in rows), len(rows))
