"""Scan non-routine English MFN items for MAR (inside information) statements.

Writes data/raw/ir/MTRS.ST/mfn_mar_scan.csv: date,time,title,url,mar,mar_time
"""
import os
import re
import sys
import csv
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from irlib import Fetcher, RAW_IR  # noqa: E402
from mtrs_mfn_item import fetch, text_of  # noqa: E402

T = "MTRS.ST"
idx = pd.read_csv(os.path.join(RAW_IR, T, "mfn_index.csv"), dtype=str).fillna("")
idx = idx[~idx.title.str.contains("[åäöÅÄÖ]")]
routine = re.compile(r"(annual general meeting|nomination committee|invitation|save the date|"
                     r"annual report|annual and sustainability|repurchase|buy-back|number of shares|"
                     r"shares and votes|welcome to|webinar|award|launches|joins|inaugurat|"
                     r"turns 65|red dot|notice of|bolagsst|general meeting|incentive)", re.I)
sel = idx[~idx.title.str.contains(routine)]
OUT = os.path.join(RAW_IR, T, "mfn_mar_scan.csv")
f = Fetcher(min_gap=1.2)
rows = []
for _, r in sel.iterrows():
    try:
        p = fetch(f, r.url)
        t = text_of(p)
    except Exception as e:  # keep going
        print("ERR", r.url, e)
        continue
    mar = bool(re.search(r"Market Abuse Regulation|inside information", t, re.I))
    m = re.search(r"publication[^.]{0,120}?at (\d{1,2}[.:]\d{2}) ?(CET|CEST)", t, re.I)
    rows.append({"date": r.date, "time": r.time, "title": r.title, "url": r.url,
                 "mar": int(mar), "mar_time": m.group(1) + " " + m.group(2) if m else ""})
with open(OUT, "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=["date", "time", "title", "url", "mar", "mar_time"])
    w.writeheader()
    w.writerows(rows)
print("scanned", len(rows), "mar", sum(r["mar"] for r in rows), "->", OUT)
