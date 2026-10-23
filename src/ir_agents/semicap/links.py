"""Fetch a page (curl_cffi chrome impersonation) and print links matching a regex. Usage: links.py URL REGEX [save_path]"""
import sys, re, time
from curl_cffi import requests as cr
from bs4 import BeautifulSoup
from urllib.parse import urljoin
u, pat = sys.argv[1], re.compile(sys.argv[2], re.I)
s = cr.Session(impersonate="chrome")
r = s.get(u, timeout=40)
print('status', r.status_code, len(r.text))
if len(sys.argv) > 3:
    open(sys.argv[3], 'w').write(r.text)
soup = BeautifulSoup(r.text, 'html.parser')
seen = set()
for a in soup.find_all('a', href=True):
    h = urljoin(u, a['href'])
    txt = ' '.join(a.get_text(' ', strip=True).split())[:90]
    if (pat.search(h) or pat.search(txt)) and h not in seen:
        seen.add(h); print(h, '|', txt)
