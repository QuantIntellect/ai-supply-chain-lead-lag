"""Crawl eMarket Storage (emarketstorage.it, Teleborsa SDIR storage) listings for PRYSMIAN (azienda=1113)
-> data/raw/ir/PRY.MI/emarket_storage_index.csv (stamp_local 'dd/mm/yyyy - HH:MM' as displayed, Europe/Rome)."""
import sys; sys.path.insert(0, "/Users/sinamirzaei/Documents/aimapping/src/ir_agents/energy"); import irlib
import csv, os, re
from bs4 import BeautifulSoup
BASE = "https://www.emarketstorage.it"
extra = sys.argv[1] if len(sys.argv) > 1 else ""
out = os.path.join(irlib.raw_dir("PRY.MI"), "emarket_storage_index.csv")
rows, seen = [], set()
page, last = 0, None
while True:
    url = f"{BASE}/it/comunicati-finanziari?azienda=1113&page={page}{extra}"
    r = irlib.fetch(url)
    if r.status_code != 200:
        print("HTTP", r.status_code, url); break
    s = BeautifulSoup(r.text, "html.parser")
    if last is None:
        nums = [int(x) for x in re.findall(r"[?&]page=(\d+)", r.text.replace("&amp;", "&"))]
        last = max(nums) if nums else 0
        print("last page", last)
    items = s.select("div.azienda-wrapper")
    for it in items:
        tm = it.select_one("time")
        a = it.select_one(".news-data a")
        wrap = it.find_parent("span")
        ttl = wrap.select_one(".news-title a") if wrap else None
        if not tm: continue
        rec = {"stamp_local": tm.get_text(strip=True), "dt_attr": tm.get("datetime", ""),
               "protocollo": it.get("data-protocollo", ""), "title": ttl.get_text(" ", strip=True) if ttl else "",
               "pdf": BASE + a["href"] if a else "", "page": page}
        if rec["protocollo"] in seen: continue
        seen.add(rec["protocollo"])
        rows.append(rec)
    if page >= last or not items:
        break
    page += 1
with open(out, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=["stamp_local", "dt_attr", "protocollo", "title", "pdf", "page"])
    w.writeheader(); w.writerows(rows)
print("rows", len(rows), rows[-1]["stamp_local"] if rows else "", "->", out)
