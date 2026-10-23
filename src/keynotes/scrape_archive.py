"""Scrape the NVIDIA newsroom archive (press releases + blogs) with dates.

Writes data/raw/keynotes/_index/archive/<year>_p<n>.html and
data/processed/keynotes/newsroom_archive.csv (date,title,url,kind,year,page).
"""
import os
import re
import sys
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))
from fetch import get  # noqa: E402

ROOT = "/Users/sinamirzaei/Documents/aimapping"
ADIR = os.path.join(ROOT, "data/raw/keynotes/_index/archive")
OUT = os.path.join(ROOT, "data/processed/keynotes/newsroom_archive.csv")
BASE = "https://nvidianews.nvidia.com"


def parse(html, year, page):
    soup = BeautifulSoup(html, "html.parser")
    rows = []
    for art in soup.select("article.index-item"):
        a = art.select_one("h3.index-item-text-title a")
        d = art.select_one(".index-item-text-info-date")
        if not a:
            continue
        url = a["href"]
        if url.startswith("/"):
            url = BASE + url
        ds = d.get_text(strip=True) if d else ""
        try:
            dt = datetime.strptime(ds, "%B %d, %Y").date().isoformat()
        except ValueError:
            dt = ds
        kind = "blog" if "blogs.nvidia.com" in url else ("release" if "/news/" in url else "other")
        rows.append({"date": dt, "title": a.get_text(" ", strip=True), "url": url.rstrip("/"),
                     "kind": kind, "year": year, "page": page})
    m = re.findall(r'\?page=(\d+)&(?:amp;)?year=%d' % year, html)
    maxp = max([int(x) for x in m] + [page])
    return rows, maxp


if __name__ == "__main__":
    years = [int(y) for y in sys.argv[1:]] or [2023, 2024, 2025, 2026]
    allrows = []
    if os.path.exists(OUT):
        allrows = pd.read_csv(OUT).to_dict("records")
        allrows = [r for r in allrows if r["year"] not in years]
    for y in years:
        p, maxp = 1, 1
        while p <= maxp:
            st, html = get(f"{BASE}/news?page={p}&year={y}", os.path.join(ADIR, f"{y}_p{p}.html"))
            if st != 200:
                print("fail", y, p, st)
                break
            rows, mp = parse(html, y, p)
            maxp = max(maxp, mp)
            allrows.extend(rows)
            if not rows:
                break
            p += 1
        print(y, "pages", maxp, flush=True)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    df = pd.DataFrame(allrows).drop_duplicates(subset=["url"])
    df.to_csv(OUT, index=False)
    print(len(df), "items")
