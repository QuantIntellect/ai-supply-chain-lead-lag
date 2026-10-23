"""Crawl GlobeNewswire organization listings for NKT A/S -> raw CSV (url, title, listed ET stamp)."""
import sys, csv, os, re
sys.path.insert(0, "/Users/sinamirzaei/Documents/aimapping/src/ir_agents/energy"); import irlib
from bs4 import BeautifulSoup

OUT = os.path.join(irlib.raw_dir("NKT.CO"), "globenewswire_list.csv")
rows, seen = [], set()
for org in ["NKT%2520A%252FS", "Nkt%2520A%252FS"]:
    for page in range(1, 80):
        r = irlib.fetch(f"https://www.globenewswire.com/en/search/organization/{org}?pageSize=50&page={page}")
        s = BeautifulSoup(r.text, "html.parser")
        got = 0
        for li in s.select("li"):
            a = li.find("a", href=re.compile(r"/news-release/"))
            if not a or a["href"] in seen:
                continue
            seen.add(a["href"])
            m = re.search(r"([A-Z][a-z]+ \d{1,2}, \d{4} \d{2}:\d{2} ET)", li.get_text(" ", strip=True))
            rows.append({"org": org, "url": "https://www.globenewswire.com" + a["href"], "title": a.get_text(" ", strip=True),
                         "listed": m.group(1) if m else ""})
            got += 1
        print(org, page, got, rows[-1]["listed"] if rows else "")
        if got == 0:
            break
with open(OUT, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["org", "url", "title", "listed"])
    w.writeheader(); w.writerows(rows)
print("saved", len(rows))
