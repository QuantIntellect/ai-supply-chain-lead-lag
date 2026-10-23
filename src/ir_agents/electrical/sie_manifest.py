"""Write SIE.DE manifest from downloaded.json; pub_date = results event date of the period."""
import os, sys, json, csv
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from irlib import *
T = "SIE.DE"
rows = json.load(open(os.path.join(RAW_IR, T, "pages", "downloaded.json")))
ev = {}
for r in csv.DictReader(open(os.path.join(PROC_IR, f"{T}_events.csv"))):
    if r["event_type"] in ("Q1", "Q2", "Q3", "Q4"):
        ev[r["fiscal_period"]] = r["event_date"]
for r in rows:
    r["pub_date"] = ev.get(r["fiscal_period"], "")
    if r["doc_type"] == "ad_hoc":
        r["pub_date"] = {"2016Q1": "2016-01-25", "2017Q1": "2017-01-31", "2023Q1": "2023-02-08",
                         "2018Q3": "2018-08-01"}.get(r["fiscal_period"], r["pub_date"])
print(write_manifest(T, rows), len(rows))
from collections import Counter
print(Counter(r["doc_type"] for r in rows))
