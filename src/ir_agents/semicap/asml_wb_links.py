"""Collect document links (ourbrand.asml.com / sitecorecloud / asml.com media) from saved Wayback quarter pages."""
import os, re, json, glob, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import irlib
T = 'ASML.AS'
d = os.path.join(irlib.raw_dir(T), 'wayback_qpages')
out = {}
for f in sorted(glob.glob(os.path.join(d, 'q*.html'))):
    slug = os.path.basename(f)[:7]
    per = slug[3:7] + slug[:2].upper()
    h = open(f, errors='ignore').read()
    for m in re.finditer(r'href="([^"]+?\.pdf)[^"]*"', h, re.I):
        u = m.group(1)
        u = re.sub(r'^https?://web\.archive\.org/web/\d+(?:id_)?/', '', u)
        if u.startswith('/'):
            u = 'https://www.asml.com' + u
        out.setdefault(per, set()).add(u)
res = {k: sorted(v) for k, v in sorted(out.items())}
json.dump(res, open(os.path.join(irlib.raw_dir(T), '_wayback_doclinks.json'), 'w'), indent=1)
for k, v in res.items():
    names = [re.sub(r'.*/', '', x)[:60] for x in v]
    print(k, len(v), names[:7])
