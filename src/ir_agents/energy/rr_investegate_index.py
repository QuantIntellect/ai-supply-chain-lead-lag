"""Crawl the Investegate RNS archive for Rolls-Royce Holdings (RR.) and save a full index
(date, time as displayed, source, headline, url) to data/raw/ir/RR.L/_investegate_index.csv."""
import sys; sys.path.insert(0, "/Users/sinamirzaei/Documents/aimapping/src/ir_agents/energy"); import irlib
import csv, os, re
from bs4 import BeautifulSoup

BASE = "https://www.investegate.co.uk/company/RR."
OUT = os.path.join(irlib.raw_dir("RR.L"), "_investegate_index.csv")


def parse(html):
    s = BeautifulSoup(html, "html.parser")
    rows = []
    for tr in s.select("table.table-investegate tbody tr"):
        tds = tr.find_all("td")
        if len(tds) < 4:
            continue
        a = tds[3].find("a", class_="announcement-link") or tds[3].find("a")
        src = tds[2].get_text(" ", strip=True)
        rows.append({
            "date_disp": tds[0].get_text(" ", strip=True),
            "time_disp": tds[1].get_text(" ", strip=True),
            "source": src,
            "headline": a.get_text(" ", strip=True) if a else tds[3].get_text(" ", strip=True),
            "url": a["href"] if a and a.has_attr("href") else "",
        })
    total = None
    m = re.search(r'fw-semibold">\s*(\d+)\s*</span>\s*results', html)
    if m:
        total = int(m.group(1))
    return rows, total


def main():
    per = 300
    allrows, page, total = [], 1, None
    while True:
        url = f"{BASE}?perPage={per}&page={page}"
        r = irlib.fetch(url)
        rows, t = parse(r.text)
        total = total or t
        print(page, r.status_code, len(rows), rows[0]["date_disp"] if rows else None, rows[-1]["date_disp"] if rows else None)
        if not rows:
            break
        allrows.extend(rows)
        if total and len(allrows) >= total:
            break
        page += 1
        if page > 40:
            break
    with open(OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["date_disp", "time_disp", "source", "headline", "url"])
        w.writeheader()
        w.writerows(allrows)
    print("total rows", len(allrows), "site total", total, "->", OUT)


if __name__ == "__main__":
    main()
