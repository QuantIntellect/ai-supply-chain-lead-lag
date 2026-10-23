"""Fetch Wayback snapshots of ASML per-quarter results pages and extract publication time statements."""
import sys, os, re, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import irlib
T = 'ASML.AS'
rows = json.load(open(sys.argv[1]))
pdir = irlib.ensure(os.path.join(irlib.raw_dir(T), 'wayback_qpages'))
best = {}
for ts, orig, st in rows:
    m = re.search(r'/(q[1-4]-20\d\d)(?:-[0-9a-f]+)?/?(?:\?.*)?$', orig)
    if not m:
        continue
    best.setdefault(m.group(1), []).append((ts, orig))
res = {}
for slug in sorted(best, key=lambda s: (s[3:], s[:2])):
    for ts, orig in sorted(best[slug])[:2]:   # earliest two snapshots
        url = f'http://web.archive.org/web/{ts}id_/{orig}'
        path = os.path.join(pdir, f'{slug}_{ts}.html')
        st, b = irlib.fetch(url, path, timeout=90)
        if st != 200:
            print(slug, ts, st); continue
        flat = ' '.join(irlib.html_to_text(b).split())
        times = re.findall(r'[^.]{0,160}\b\d{1,2}[:.]\d{2}\s*(?:hours\s*)?(?:CET|CEST|ET|EST|EDT|US Eastern|Central European)[^.]{0,60}', flat)
        dates = re.findall(r'[^.]{0,60}(?:announced|publishe[sd]|will publish|released|will release)[^.]{0,100}?(?:January|February|March|April|May|June|July|August|September|October|November|December) \d{1,2},? 20\d\d', flat)
        res.setdefault(slug, []).append({'ts': ts, 'url': orig, 'times': times[:5], 'dates': dates[:3]})
        print(slug, ts, '| T:', (' || '.join(x[-150:] for x in times[:2]) if times else '-'), '| D:', (dates[0][-110:] if dates else '-'))
json.dump(res, open(os.path.join(pdir, '_summary.json'), 'w'), indent=1)
