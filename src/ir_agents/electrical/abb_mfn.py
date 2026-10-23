"""Pull ABB items from MFN (timestamps in Europe/Stockholm == CET/CEST) with a query filter."""
import os, sys, re, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from irlib import *
from bs4 import BeautifulSoup

f = Fetcher()
out = json.load(open(os.path.join(RAW_IR, 'ABBN.SW', 'pages', 'mfn_items.json'))) if os.path.exists(os.path.join(RAW_IR, 'ABBN.SW', 'pages', 'mfn_items.json')) else []
queries = sys.argv[1:] or ['results']
for q in queries:
    from urllib.parse import quote
    url = f'https://www.mfn.se/all/a/abb?query={quote(q)}&limit=500'
    path = os.path.join(RAW_IR, 'ABBN.SW', 'pages', f'mfn_q_{re.sub(r"[^a-z0-9]+","_",q.lower())}.html')
    ok, st, _ = f.download(url, path, overwrite=True)
    if not ok:
        print(q, "FAILED", st); continue
    soup = BeautifulSoup(open(path, 'rb').read(), 'html.parser')
    n = 0
    for div in soup.find_all('div', class_='short-item'):
        t = div.find('span', class_='compressed-title')
        a = t.find_parent('a') if t else None
        txt = ' '.join(div.get_text(' ').split())
        m = re.match(r'(\d{4}-\d{2}-\d{2}) (\d{2}:\d{2}:\d{2})', txt)
        href = ''
        for aa in div.find_all('a', href=True):
            if '/a/abb/' in aa['href']:
                href = aa['href']; break
        out.append({'q': q, 'date': m.group(1) if m else '', 'time': m.group(2) if m else '',
                    'title': t.get_text(' ').strip() if t else txt[:100], 'href': href})
        n += 1
    print(q, st, n, out[-1]['date'] if out else '')
json.dump(out, open(os.path.join(RAW_IR, 'ABBN.SW', 'pages', 'mfn_items.json'), 'w'), indent=0)
