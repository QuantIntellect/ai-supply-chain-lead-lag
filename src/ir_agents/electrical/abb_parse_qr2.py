"""Parse ABB quarterly-results tables: Quarter | Press release | Financial information | Presentation | Webcast."""
import os, sys, re, json, html as htmlmod
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from irlib import *
from bs4 import BeautifulSoup

src, out = sys.argv[1], sys.argv[2]
soup = BeautifulSoup(open(src, 'rb').read(), 'html.parser')
rows = []
for table in soup.find_all('table'):
    trs = table.find_all('tr')
    if not trs:
        continue
    hdr = [' '.join(c.get_text(' ').split()) for c in trs[0].find_all(['th', 'td'])]
    for tr in trs[1:]:
        cells = tr.find_all(['td', 'th'])
        if not cells:
            continue
        label = ' '.join(cells[0].get_text(' ').split())
        for ci, c in enumerate(cells[1:], start=1):
            col = hdr[ci] if ci < len(hdr) else f'col{ci}'
            for a in c.find_all('a', href=True):
                href = htmlmod.unescape(a['href'])
                rows.append({'hdr0': hdr[0] if hdr else '', 'label': label, 'col': col,
                             'text': ' '.join(a.get_text(' ').split()), 'url': href})
json.dump(rows, open(out, 'w'), indent=0)
print(len(rows))
labels = []
for r in rows:
    k = (r['hdr0'], r['label'])
    if k not in labels:
        labels.append(k)
print(len(labels))
print(' ; '.join(f"{a}:{b}" for a, b in labels))
cols = sorted(set(r['col'] for r in rows))
print(cols)
