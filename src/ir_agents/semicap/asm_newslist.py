"""Scrape ASM news listing pages (section filter) into a CSV of (date, title, url). Usage: asm_newslist.py SECTION MAXPAGE OUT"""
import sys, re, os, csv
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from irlib import fetch
from bs4 import BeautifulSoup
from urllib.parse import quote
section, maxpage, out = sys.argv[1], int(sys.argv[2]), sys.argv[3]
rows = []
for p in range(0, maxpage + 1):
    url = f"https://www.asm.com/news?section={quote(section)}&page={p}"
    st, b = fetch(url)
    if st != 200:
        print('status', st, url); break
    s = BeautifulSoup(b, 'html.parser')
    n = 0
    for a in s.find_all('a', class_='article-items__anchor', href=True):
        t = ' '.join(a.get_text(' ', strip=True).split())
        m = re.search(r'([A-Z][a-z]+ \d{1,2}, \d{4})', t)
        h3 = a.find('h3')
        title = ' '.join(h3.get_text(' ', strip=True).split()) if h3 else t[:150]
        rows.append({'page': p, 'date': m.group(1) if m else '', 'title': title, 'url': 'https://www.asm.com' + a['href'] if a['href'].startswith('/') else a['href'], 'raw': t[:200]})
        n += 1
    print('page', p, 'items', n)
    if n == 0:
        break
with open(out, 'w') as f:
    w = csv.DictWriter(f, fieldnames=['page', 'date', 'title', 'url', 'raw'])
    w.writeheader(); w.writerows(rows)
print('total', len(rows))
