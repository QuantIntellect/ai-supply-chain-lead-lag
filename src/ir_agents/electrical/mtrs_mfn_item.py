"""Fetch MFN item pages for Munters and grep them.

Usage: mtrs_mfn_item.py PATTERN URL [URL ...]
Saves raw HTML to data/raw/ir/MTRS.ST/mfn_items/<slug>.html and prints regex
context snippets (text only) for PATTERN.
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from irlib import Fetcher, RAW_IR, ensure  # noqa: E402

D = ensure(os.path.join(RAW_IR, "MTRS.ST", "mfn_items"))


def text_of(path):
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(open(path, "rb").read(), "html.parser")
    for t in soup(["script", "style", "noscript"]):
        t.decompose()
    body = soup.find(class_=re.compile("full-item|mfn-body|news-item")) or soup
    return re.sub(r"\s+", " ", body.get_text(" "))


def fetch(f, url):
    slug = url.rstrip("/").split("/")[-1][:150]
    p = os.path.join(D, slug + ".html")
    if not os.path.exists(p):
        r = f.get(url)
        with open(p, "wb") as fh:
            fh.write(r.content)
    return p


if __name__ == "__main__":
    pat = re.compile(sys.argv[1], re.I)
    f = Fetcher(min_gap=1.2)
    for u in sys.argv[2:]:
        p = fetch(f, u)
        t = text_of(p)
        hits = [t[max(0, m.start() - 150): m.end() + 150] for m in pat.finditer(t)][:6]
        print("==", u.split("/")[-1][:90])
        for h in hits:
            print("   ..", h)
