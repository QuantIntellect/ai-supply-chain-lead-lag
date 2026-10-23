"""Crawl MFN news feed for Munters Group (all releases with Stockholm timestamps).

Saves raw pages to data/raw/ir/MTRS.ST/pages/ and a parsed index to
data/raw/ir/MTRS.ST/mfn_index.csv (date, time, title, url, attachments).
"""
import os
import re
import sys
import csv
import html as htmlmod

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from irlib import Fetcher, RAW_IR, ensure  # noqa: E402

T = "MTRS.ST"
BASE = "https://www.mfn.se/all/a/munters-group"
PAGES = ensure(os.path.join(RAW_IR, T, "pages"))
OUT = os.path.join(RAW_IR, T, "mfn_index.csv")

ITEM_RE = re.compile(
    r'class="short-item compressible" id="([^"]+)".*?'
    r'compressed-date">([^<]+)</span>\s*<span class="compressed-time">([^<]+)</span>'
    r'.*?<a class="title-link item-link" href="([^"]+)"[^>]*>([^<]+)</a>(.*?)(?=class="short-item compressible"|$)',
    re.S)


def parse(h):
    out = []
    for m in ITEM_RE.finditer(h):
        iid, d, t, href, title, rest = m.groups()
        atts = re.findall(r'class="attachment-icon"[^>]*href="([^"]+)"', rest)
        atts += re.findall(r'href="([^"]+)"[^>]*class="attachment-icon"', rest)
        tags = re.findall(r'class="tag[^"]*"[^>]*>([^<]+)<', rest)
        out.append({"id": iid, "date": d.strip(), "time": t.strip(),
                    "title": htmlmod.unescape(title.strip()),
                    "url": "https://www.mfn.se" + href,
                    "attachments": "|".join(dict.fromkeys(atts)),
                    "tags": "|".join(tags)})
    return out


def main():
    f = Fetcher(min_gap=1.2)
    allitems, seen = [], set()
    offset, limit = 0, 48
    while True:
        p = os.path.join(PAGES, f"mfn_offset_{offset:04d}.html")
        url = f"{BASE}?limit={limit}&offset={offset}" if offset else f"{BASE}?limit={limit}"
        if not os.path.exists(p):
            r = f.get(url)
            if r.status_code != 200:
                print("stop", r.status_code, url)
                break
            with open(p, "wb") as fh:
                fh.write(r.content)
        h = open(p, encoding="utf-8", errors="ignore").read()
        items = parse(h)
        new = [i for i in items if i["id"] not in seen]
        for i in new:
            seen.add(i["id"])
        allitems += new
        print(offset, len(items), len(new), items[-1]["date"] if items else None)
        if not new or (items and items[-1]["date"] < "2017-01-01"):
            break
        offset += limit
        if offset > 3000:
            break
    with open(OUT, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(allitems[0].keys()))
        w.writeheader()
        w.writerows(allitems)
    print("items", len(allitems), "->", OUT)


if __name__ == "__main__":
    main()
