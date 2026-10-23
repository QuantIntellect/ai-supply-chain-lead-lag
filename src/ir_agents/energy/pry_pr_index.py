"""Crawl the prysmian.com press-release archive (all pages) -> data/raw/ir/PRY.MI/press_release_index.csv
Columns: date (YYYY-MM-DD), time_raw (as displayed, e.g. '4:00 PM'), price_sensitive, category_alt, title, url, page"""
import sys; sys.path.insert(0, "/Users/sinamirzaei/Documents/aimapping/src/ir_agents/energy"); import irlib
import csv, os, re
from datetime import datetime
from bs4 import BeautifulSoup

BASE = "https://www.prysmian.com"
lang = sys.argv[1] if len(sys.argv) > 1 else "en"
path = "/en/media/press-releases" if lang == "en" else "/it/media/comunicati-stampa"
out = os.path.join(irlib.raw_dir("PRY.MI"), f"press_release_index_{lang}.csv")
rows = []
page = 0
last_page = None
while True:
    url = f"{BASE}{path}?page={page}"
    r = irlib.fetch(url)
    if r.status_code != 200:
        print("HTTP", r.status_code, url); break
    s = BeautifulSoup(r.text, "html.parser")
    items = s.select("div.news-archive-row")
    if last_page is None:
        nums = [int(m.group(1)) for a in s.find_all("a", href=True) for m in [re.search(r"[?&]page=(\d+)", a["href"])] if m]
        last_page = max(nums) if nums else 0
        print("last page", last_page)
    for it in items:
        d = it.select_one(".news-archive-date a")
        t = it.select_one(".prys2-search-result__title a")
        img = it.select_one("img")
        if not d or not t:
            continue
        ds = " ".join(d.get_text(" ").split())
        try:
            dt = datetime.strptime(ds, "%b %d, %Y").strftime("%Y-%m-%d")
        except ValueError:
            dt = ds
        tt = " ".join(t.get_text(" ").split())
        m = re.match(r"^(\d{1,2}:\d{2}\s*[AP]M)\s*(-\s*Price Sensitive)?\s*(.*)$", tt)
        if m:
            time_raw, ps, title = m.group(1), bool(m.group(2)), m.group(3)
        else:
            time_raw, ps, title = "", "Price Sensitive" in tt, tt
        rows.append({"date": dt, "time_raw": time_raw, "price_sensitive": int(ps),
                     "category_alt": img.get("alt", "") if img else "", "title": title,
                     "url": BASE + t["href"] if t["href"].startswith("/") else t["href"], "page": page})
    if page >= last_page or not items:
        break
    page += 1
with open(out, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=["date", "time_raw", "price_sensitive", "category_alt", "title", "url", "page"])
    w.writeheader(); w.writerows(rows)
print("rows", len(rows), "->", out)
