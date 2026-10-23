"""Scrape the pressetext (pta) press map of Siemens Energy AG (regulatory distributor from ~Sep 2024)
-> scratch TSV of (date, time, title, url)."""
import sys; sys.path.insert(0, "/Users/sinamirzaei/Documents/aimapping/src/ir_agents/energy"); import irlib
import re, os
from bs4 import BeautifulSoup
SP = "/private/tmp/claude-501/-Users-sinamirzaei-Documents-aimapping/57e0a0d0-6441-40ef-828b-57eeb87e7b21/scratchpad/enr"
base = sys.argv[1] if len(sys.argv) > 1 else "https://www.pressetext.com/pressmap/2016676"
maxp = int(sys.argv[2]) if len(sys.argv) > 2 else 60
tag = sys.argv[3] if len(sys.argv) > 3 else "de"
rows, seen = [], set()
for p in range(1, maxp + 1):
    url = base + ("" if p == 1 else (("&" if "?" in base else "?") + f"page={p}"))
    r = irlib.fetch(url)
    s = BeautifulSoup(r.text, "html.parser")
    n = 0
    for blk in s.select("div.odd, div.even"):
        sp = blk.find("span")
        a = blk.select_one("a.NewsTitle")
        if not sp or not a:
            continue
        m = re.search(r"(\d{2}\.\d{2}\.\d{4})\s*-\s*(\d{2}:\d{2})", sp.get_text())
        href = a.get("href", "")
        if href in seen:
            continue
        seen.add(href)
        rows.append([m.group(1) if m else "", m.group(2) if m else "", a.get_text(" ", strip=True), href])
        n += 1
    print(f"page {p}: {n} items, last {rows[-1][0] if rows else ''}")
    if n == 0:
        break
with open(os.path.join(SP, f"pta_{tag}.tsv"), "w") as f:
    for r_ in rows:
        f.write("\t".join(r_) + "\n")
print("total", len(rows))
