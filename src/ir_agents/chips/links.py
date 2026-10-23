"""List links on a page matching a regex (token-economical). Usage: links.py URL [regex] [max]"""
import sys
import re
import os
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import irlib  # noqa: E402

url = sys.argv[1]
pat = sys.argv[2] if len(sys.argv) > 2 else "."
mx = int(sys.argv[3]) if len(sys.argv) > 3 else 60
cache = os.path.join(os.path.dirname(irlib.LOCK_DIR), "pages")
st, html, final = irlib.fetch(url, cache_dir=cache)
print("status", st, "len", len(html), final[:100])
soup = BeautifulSoup(html, "html.parser")
seen = set()
n = 0
for a in soup.find_all("a", href=True):
    href = urljoin(final, a["href"])
    txt = re.sub(r"\s+", " ", a.get_text(" ")).strip()[:70]
    key = href
    if key in seen:
        continue
    seen.add(key)
    if re.search(pat, href + " " + txt, re.I):
        print(txt, "|", href[:160])
        n += 1
        if n >= mx:
            break
