"""Fetch the Schneider call transcripts for the four releases lacking an AMF
timestamp (call greeting is used as BMO/AMC evidence)."""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from irlib import *
T = "SU.PA"
tab = json.load(open(os.path.join(RAW_IR, T, "pages", "results_table.json")))
want = {("2016", "Annual"): "2016Q4", ("2018", "Half"): "2018Q2", ("2018", "Q3"): "2018Q3", ("2019", "Q3"): "2019Q3"}
mp = os.path.join(RAW_IR, T, "pages", "manifest_rows.json")
man = json.load(open(mp))
f = Fetcher(min_gap=1.0)
from datetime import datetime
for r in tab:
    key = next(((y, k) for (y, k) in want if r["year"] == y and r["title"].startswith(k)), None)
    if not key:
        continue
    per = want[key]
    for u in r["urls"]:
        if "transcript" not in u.lower():
            continue
        url = "https://www.se.com" + u if u.startswith("/") else u
        out = os.path.join(RAW_IR, T, f"{per}_transcript.pdf")
        ok, st, p = f.download(url, out)
        print(per, ok, st, is_pdf(p) if ok else None)
        if ok and is_pdf(p):
            txt, n = to_text(p, T, per, "transcript")
            for s in grep(txt, r"good (morning|afternoon|evening)", width=60, maxhits=2):
                print("   ", s[:160])
            d = datetime.strptime(r["date"], "%B %d, %Y").strftime("%Y-%m-%d")
            man.append({"local_path": p, "url": url, "doc_type": "transcript", "fiscal_period": per, "pub_date": d})
json.dump(man, open(mp, "w"), indent=1)
write_manifest(T, [dict(m) for m in man])
