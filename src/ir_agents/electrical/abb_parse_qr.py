"""Parse ABB quarterly-results page into (heading, link text, url) rows."""
import os, sys, re, json, html as htmlmod
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from irlib import *
from bs4 import BeautifulSoup

src = sys.argv[1]
out = sys.argv[2]
soup = BeautifulSoup(open(src, 'rb').read(), 'html.parser')
rows = []
for a in soup.find_all('a', href=True):
    href = htmlmod.unescape(a['href'])
    if 'search.abb.com/library' not in href and not re.search(r'\.pdf|transcript|webcast', href, re.I):
        continue
    text = ' '.join(a.get_text(' ').split())
    # find nearest preceding heading
    h = a.find_previous(['h1', 'h2', 'h3', 'h4', 'h5'])
    head = ' '.join(h.get_text(' ').split()) if h else ''
    # nearest container text (title of block)
    par = a.find_parent(['li', 'div', 'td'])
    ptxt = ' '.join(par.get_text(' ').split())[:120] if par else ''
    m = re.search(r'DocumentID=([^&]+)', href)
    rows.append({'head': head[:80], 'text': text[:80], 'ptxt': ptxt, 'docid': m.group(1) if m else '', 'url': href})
json.dump(rows, open(out, 'w'), indent=0)
print(len(rows))
heads = {}
for r in rows:
    heads.setdefault(r['head'], []).append(r['text'])
for h, ts in heads.items():
    print(repr(h), len(ts), '|', '; '.join(sorted(set(ts)))[:200])
