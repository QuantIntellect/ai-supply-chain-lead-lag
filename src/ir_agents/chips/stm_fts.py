"""EDGAR full-text search for STM (CIK 932787) 6-K earnings releases and timing announcements.
Saves hits to data/raw/ir/STMPA.PA/edgar_fts_hits.csv"""
import os
import sys
import json
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import irlib  # noqa: E402

T = "STMPA.PA"
QUERIES = ['"Financial Results" "STMicroelectronics Reports"',
           '"announces timing" earnings',
           '"before the opening of trading"',
           '"Capital Markets Day"',
           'outlook revised OR "updates its" guidance']
rows = []
for q in QUERIES:
    frm = 0
    while True:
        u = ("https://efts.sec.gov/LATEST/search-index?q=" + q.replace(" ", "%20").replace('"', "%22") +
             f"&ciks=0000932787&forms=6-K&dateRange=custom&startdt=2015-01-01&enddt=2026-10-23&from={frm}")
        st, t, _ = irlib.sec_fetch(u)
        if st != 200:
            print("fail", st, q)
            break
        j = json.loads(t)
        hits = j.get("hits", {}).get("hits", [])
        for h in hits:
            s = h["_source"]
            rows.append(dict(query=q, file_date=s.get("file_date"), adsh=s.get("adsh"), id=h.get("_id"),
                             desc=s.get("file_description"), display=";".join(s.get("display_names", []))[:60]))
        tot = j.get("hits", {}).get("total", {}).get("value", 0)
        frm += len(hits)
        if not hits or frm >= tot or frm >= 400:
            break
    print(q, frm)
df = pd.DataFrame(rows)
df.to_csv(os.path.join(irlib.raw_dir(T), "edgar_fts_hits.csv"), index=False)
print(df.groupby("query").size())
