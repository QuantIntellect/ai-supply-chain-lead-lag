"""Harvest Besi press-release listings (2015-2026) from Wayback captures of besi.com year pages.
Output: scratchpad besi_pr_list.csv (title, date, url)"""
import os, sys, re, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pandas as pd
from bs4 import BeautifulSoup
import besi_wb, irlib

RAW = irlib.raw_dir("BESI.AS")
LIST_DIR = irlib.ensure(os.path.join(RAW, "wayback_listings"))
MONTHS = "January|February|March|April|May|June|July|August|September|October|November|December"
DATE_RE = re.compile(r"Duiven,?\s+(?:the\s+)?Netherlands,?\s+(" + MONTHS + r")\s+(\d{1,2}),?\s+(\d{4})", re.I)

def latest_captures(prefix):
    caps = besi_wb.cdx_query(prefix + "*", "&filter=statuscode:200&filter=mimetype:text/html")
    best = {}
    for c in caps:
        u = besi_wb.norm(c[2]).rstrip("/")
        if not re.search(r"/press-releases/(20\d\d(-2)?)(/page/\d+)?$", u):
            continue
        if u not in best or c[1] > best[u][0]:
            best[u] = (c[1], c[2])
    return best

def parse(b, base):
    soup = BeautifulSoup(b, "html.parser")
    out = []
    for a in soup.find_all("a", href=True):
        h = a["href"]
        if "/details" not in h or "share-repurchase" in h:
            continue
        par = a.find_parent(["div", "li", "article"])
        txt = " ".join((par.get_text(" ", strip=True) if par else a.get_text(" ", strip=True)).split())
        m = DATE_RE.search(txt)
        title = " ".join(a.get_text(" ", strip=True).split())
        h = re.sub(r"^https?://web\.archive\.org/web/\d+(id_)?/", "", h)
        if h.startswith("/"):
            h = "https://www.besi.com" + h
        out.append({"title": title, "date": (f"{m.group(3)}-{m.group(1)}-{m.group(2)}" if m else ""), "url": h})
    return out

def main():
    allrows = []
    for y in range(2015, 2027):
        best = latest_captures(f"besi.com/investor-relations/press-releases/{y}")
        for u, (ts, orig) in sorted(best.items()):
            fn = os.path.join(LIST_DIR, re.sub(r"[^A-Za-z0-9]+", "_", u.strip("/")) + f"_{ts}.html")
            st, b = besi_wb.wb_get(ts, orig, fn)
            rows = parse(b, orig) if st == 200 else []
            for r in rows:
                r.update({"list_page": u, "cap": ts})
            allrows += rows
            print(y, u, ts, st, len(rows))
    df = pd.DataFrame(allrows)
    df["date"] = pd.to_datetime(df["date"], format="%Y-%B-%d", errors="coerce")
    df["slug"] = df["url"].str.rstrip("/").str.split("/").str[-1]
    df = df.sort_values(["slug", "date"]).groupby("slug", as_index=False).agg(
        {"title": "first", "date": "max", "url": "first", "list_page": "first"})
    df.to_csv(os.path.join(besi_wb.SCR, "besi_pr_list.csv"), index=False)
    print(len(df), df.date.min(), df.date.max(), df.date.isna().sum())

if __name__ == "__main__":
    main()
