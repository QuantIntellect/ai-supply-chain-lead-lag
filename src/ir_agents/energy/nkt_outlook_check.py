"""Fetch NKT ad-hoc outlook announcements, save raw HTML, print the outlook sentences (direction check)."""
import sys, csv, re, os
sys.path.insert(0, "/Users/sinamirzaei/Documents/aimapping/src/ir_agents/energy"); import irlib

rows = irlib.read_csv("data/raw/ir/NKT.CO/ir_announcements_list.csv")
pat = re.compile(r"(outlook|preliminar|trading statement|Capital Markets Day 2015|Investor Day|Capital Markets Day)", re.I)
for r in rows:
    if r["category"].startswith("Financial") or not pat.search(r["title"]):
        continue
    if re.search(r"hosts|reschedul", r["title"], re.I):
        continue
    slug = r["url"].rstrip("/").rsplit("/", 1)[-1][:70]
    lp = irlib.download(r["url"], "NKT.CO", f"ann_{r['year']}_{slug}.html")
    if not lp:
        continue
    t = re.sub(r"\s+", " ", irlib.html_to_text(lp))
    i = t.find(r["title"][:30])
    body = t[i:] if i >= 0 else t
    sents = [m.group(0) for m in re.finditer(r"[^.]{0,200}(?:outlook|expects?|now expected|revenue|EBITDA)[^.]{0,220}\.", body[:6000], re.I)][:3]
    print(f"== {r['year']} {r['date']} {r['time']} | {r['title'][:80]}")
    for s in sents:
        print("   -", s.strip()[:330])
