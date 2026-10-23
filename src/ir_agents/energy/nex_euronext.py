"""Crawl Euronext company press-release list for Nexans (Euronext id 092642) -> raw CSV with stamps."""
import sys, csv, os, re
sys.path.insert(0, "/Users/sinamirzaei/Documents/aimapping/src/ir_agents/energy"); import irlib
from bs4 import BeautifulSoup

BASE = "https://live.euronext.com/en/listview/company-press-release/092642"
OUT = os.path.join(irlib.raw_dir("NEX.PA"), "euronext_press_list.csv")
rows, page = [], 0
while True:
    r = irlib.fetch(f"{BASE}?page={page}")
    s = BeautifulSoup(r.text, "html.parser")
    trs = s.find_all("tr")[1:]
    got = 0
    for tr in trs:
        tds = tr.find_all("td")
        if len(tds) < 3:
            continue
        a = tr.find("a", href=True)
        cells = [td.get_text(" ", strip=True) for td in tds]
        rows.append({"released": cells[0], "company": cells[1], "title": cells[2],
                     "topic": cells[-1] if len(cells) > 4 else "",
                     "href": ("https://live.euronext.com" + a["href"]) if a and a["href"].startswith("/") else (a["href"] if a else "")})
        got += 1
    last = rows[-1]["released"] if rows else ""
    print(page, got, last)
    if got == 0 or re.search(r"20(0\d|1[0-4])\b", last):
        break
    page += 1
    if page > 120:
        break
with open(OUT, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["released", "company", "title", "topic", "href"])
    w.writeheader(); w.writerows(rows)
print("saved", len(rows), OUT)
