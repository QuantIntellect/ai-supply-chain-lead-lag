"""Crawl Legrand newsroom listing -> slugs; then fetch finance-related news pages and read
JSON-LD datePublished (local Paris time). Output data/raw/ir/LR.PA/pages/news_times.json"""
import os, sys, re, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from irlib import *
TK = "LR.PA"
f = Fetcher()
pdir = ensure(os.path.join(RAW_IR, TK, "pages", "newsroom"))
slugs = []
for pg in range(0, 80):
    p = os.path.join(pdir, f"list_{pg:02d}.html")
    ok, st, _ = f.download(f"https://www.legrand.com/en/press/newsroom?page={pg}", p)
    if not ok:
        print("stop", pg, st); break
    h = open(p, encoding="utf-8", errors="ignore").read()
    new = [s for s in dict.fromkeys(re.findall(r'href="/en/news/([^"?#]+)"', h)) if s not in slugs]
    slugs += new
    if not new:
        print("no new slugs at page", pg); break
print(len(slugs))
json.dump(slugs, open(os.path.join(pdir, "slugs.json"), "w"), indent=0)
pat = re.compile(r"result|sales|capital-markets|investor-day|covid|health-context|guidance|target|nine-month|half|quarter|full-year|annual", re.I)
cand = [s for s in slugs if pat.search(s)]
print("candidates", len(cand))
times = {}
for s in cand:
    p = os.path.join(pdir, f"news_{s[:120]}.html")
    ok, st, _ = f.download(f"https://www.legrand.com/en/news/{s}", p)
    if not ok:
        continue
    h = open(p, encoding="utf-8", errors="ignore").read()
    m = re.search(r'"datePublished"\s*:\s*"(\d{4}-\d{2}-\d{2}) (\d{2}:\d{2})', h)
    if m:
        times.setdefault(m.group(1), []).append((m.group(2), f"https://www.legrand.com/en/news/{s}", s))
json.dump(times, open(os.path.join(RAW_IR, TK, "pages", "news_times.json"), "w"), indent=0)
for d in sorted(times):
    print(d, times[d])
