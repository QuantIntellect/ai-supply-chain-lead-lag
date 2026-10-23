"""Crawl GlobeNewswire organization listing for Nexans -> raw CSV (url, title, listed datetime)."""
import sys, csv, os, re
sys.path.insert(0, "/Users/sinamirzaei/Documents/aimapping/src/ir_agents/energy"); import irlib
from bs4 import BeautifulSoup

OUT = os.path.join(irlib.raw_dir("NEX.PA"), "globenewswire_list.csv")
rows, seen = [], set()
for page in range(1, 80):
    r = irlib.fetch(f"https://www.globenewswire.com/en/search/organization/Nexans?pageSize=50&page={page}")
    s = BeautifulSoup(r.text, "html.parser")
    got = 0
    for li in s.select("li"):
        a = li.find("a", href=re.compile(r"/news-release/"))
        if not a:
            continue
        h = a["href"]
        if h in seen:
            continue
        seen.add(h)
        title = a.get_text(" ", strip=True)
        dt = ""
        m = re.search(r"([A-Z][a-z]+ \d{1,2}, \d{4} \d{2}:\d{2} ET)", li.get_text(" ", strip=True))
        if m:
            dt = m.group(1)
        rows.append({"url": "https://www.globenewswire.com" + h, "title": title, "listed": dt})
        got += 1
    print(page, got, rows[-1]["url"][40:60] if rows else "", rows[-1]["listed"] if rows else "")
    if got == 0:
        break
with open(OUT, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["url", "title", "listed"])
    w.writeheader(); w.writerows(rows)
print("saved", len(rows))
