"""Download Schneider results documents listed on the IR results page
(results_table.json from su_nuxt.py + the 2026 links) and extract text."""
import os, sys, re, json
from datetime import datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from irlib import *

T = "SU.PA"
tab = json.load(open(os.path.join(RAW_IR, T, "pages", "results_table.json")))
QMAP = [("Q1", 1), ("Half", 2), ("Q3", 3), ("Full", 4), ("Annual", 4)]
rows = []
for r in tab:
    q = next((n for k, n in QMAP if r["title"].startswith(k)), None)
    if q is None:
        continue
    per = f"{r['year']}Q{q}"
    d = datetime.strptime(r["date"].strip(), "%B %d, %Y").strftime("%Y-%m-%d")
    for u in r["urls"]:
        rows.append({"period": per, "pub_date": d, "url": u})
# 2026 documents (top section of the page; dates from AMF filings)
D26 = {"2026Q1": "2026-04-30", "2026Q2": "2026-07-30", "2026Q3": "2026-10-16"}
for per, names in {"2026Q1": ["/ww/en/assets/pdf/release-q1-revenues-2026", "/ww/en/assets/pdf/presentation-q1-revenues-2026", "/ww/en/assets/pdf/transcript-Q1-results-2026"],
                   "2026Q2": ["/ww/en/assets/pdf/release-hy-results-2026", "https://download.se.com/files?p_Doc_Ref=presentation-hy-results-2026", "/ww/en/assets/pdf/accounts-hy-results-2026", "/ww/en/assets/pdf/transcript-hy-results-2026"],
                   "2026Q3": ["/ww/en/assets/pdf/release-Q3-revenues-2026", "/ww/en/assets/pdf/presentation-Q3-revenues-2026", "/ww/en/assets/pdf/transcript-Q3-results-2026"]}.items():
    for u in names:
        rows.append({"period": per, "pub_date": D26[per], "url": u})


def doctype(u):
    b = u.split("?")[0].split("/")[-1].lower()
    if "sustainability" in b:
        return None
    if "historical_revenues" in b:
        return "recast"
    if "transcript" in b:
        return "transcript"
    if "presentation" in b:
        return "presentation"
    if "accounts" in b:
        return "accounts"
    if "release" in b or "revenues" in b or "results" in b:
        return "release"
    return "other"


minyear = int(sys.argv[1]) if len(sys.argv) > 1 else 2022
f = Fetcher(min_gap=1.0)
man_path = os.path.join(RAW_IR, T, "pages", "manifest_rows.json")
man = json.load(open(man_path)) if os.path.exists(man_path) else []
have = {m["url"] for m in man}
for r in rows:
    dt = doctype(r["url"])
    if dt is None:
        continue
    y = int(r["period"][:4])
    if y < minyear and dt != "release":
        continue  # older years: releases only
    url = r["url"] if r["url"].startswith("http") else "https://www.se.com" + r["url"]
    if url in have:
        continue
    fname = f"{r['period']}_{dt}.pdf"
    out = os.path.join(RAW_IR, T, fname)
    if any(m["local_path"] == out for m in man):  # same period/doctype already taken
        dt = dt + "2"
        out = os.path.join(RAW_IR, T, f"{r['period']}_{dt}.pdf")
    ok, st, p = f.download(url, out)
    if ok and not is_pdf(p):
        os.rename(p, p + ".notpdf"); ok = False
    if not ok:
        print("FAIL", st, r["period"], dt, url[:100]); continue
    txt, n = to_text(p, T, r["period"], dt)
    man.append({"local_path": p, "url": url, "doc_type": dt, "fiscal_period": r["period"], "pub_date": r["pub_date"]})
    have.add(url)
    json.dump(man, open(man_path, "w"), indent=1)
    print("OK", r["period"], dt, os.path.getsize(p), n, flush=True)
write_manifest(T, [dict(m) for m in man])
print("manifest rows", len(man))
