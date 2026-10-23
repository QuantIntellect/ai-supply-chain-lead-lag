"""Crawl investors.nkt.com company-announcement listing 2015-2026 -> raw CSV (date, time, category, title, url)."""
import sys, csv, os, re
sys.path.insert(0, "/Users/sinamirzaei/Documents/aimapping/src/ir_agents/energy"); import irlib
from bs4 import BeautifulSoup

OUT = os.path.join(irlib.raw_dir("NKT.CO"), "ir_announcements_list.csv")
rows, seen = [], set()
for year in range(2015, 2027):
    for pg in range(0, 30):
        u = f"https://investors.nkt.com/company-announcements/?category=&year={year}&_paging={pg}"
        s = BeautifulSoup(irlib.fetch(u).text, "html.parser")
        got = 0
        for a in s.find_all("a", href=re.compile(rf"^/company-announcements/{year}/")):
            h = a["href"]
            if h in seen:
                continue
            txt = a.get_text(" ", strip=True)
            m = re.match(r"([A-Z][a-z]+ \d{1,2}), (\d{2}:\d{2}) (Company Announcement|Investor News|Financial Report|[A-Za-z ]+?) (.*)", txt)
            if not m:
                continue
            seen.add(h)
            rows.append({"year": year, "date": m.group(1), "time": m.group(2), "category": m.group(3),
                         "title": m.group(4).replace(" Learn more", ""), "url": "https://investors.nkt.com" + h})
            got += 1
        if got == 0:
            break
    print(year, sum(1 for r in rows if r["year"] == year))
with open(OUT, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["year", "date", "time", "category", "title", "url"])
    w.writeheader(); w.writerows(rows)
print("saved", len(rows))
