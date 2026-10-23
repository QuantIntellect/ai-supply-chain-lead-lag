"""Parse ASML financial-results page (saved HTML) into per-quarter document links (walk in document order)."""
import sys, re, json
from bs4 import BeautifulSoup
from urllib.parse import urljoin
html = open(sys.argv[1]).read()
soup = BeautifulSoup(html, 'html.parser')
base = 'https://www.asml.com/en/investors/financial-results'
year, q = None, None
out = []
for el in soup.find_all(['h2', 'h3', 'a']):
    t = ' '.join(el.get_text(' ', strip=True).split())
    if el.name == 'h2':
        m = re.match(r'(Q[1-4]) (20\d\d) financial results', t)
        if m:
            year, q = m.group(2), m.group(1)
    elif el.name == 'h3':
        if re.fullmatch(r'20\d\d', t):
            year = t
        elif re.fullmatch(r'Q[1-4]', t):
            q = t
    elif el.get('href'):
        h = urljoin(base, el['href'])
        if 'static-files' in h or 'news-release-details' in h:
            out.append({'period': f'{year}{q}', 'url': h, 'label': t[:80]})
json.dump(out, open(sys.argv[2], 'w'), indent=0)
from collections import Counter
c = Counter(o['period'] for o in out)
print(len(out)); print(sorted(c.items()))
labs = Counter(re.sub(r'^(PDF|ZIP|XLS\w*|MP\d) - ', '', o['label']).lower() for o in out)
print(labs.most_common(40))
