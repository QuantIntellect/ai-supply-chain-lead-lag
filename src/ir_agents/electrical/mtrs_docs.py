"""Download Munters interim-report PDFs (Cision attachments listed on MFN items),
extract text, and write the manifest.

Usage: mtrs_docs.py [--from 2017Q2]
"""
import os
import re
import sys
import glob
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from irlib import (Fetcher, RAW_IR, TEXT_IR, ROOT, is_pdf, to_text,  # noqa: E402
                   write_manifest)
from mtrs_events import SPEC, idx  # noqa: E402

T = "MTRS.ST"
DOCS = os.path.join(RAW_IR, T, "docs")
start = sys.argv[sys.argv.index("--from") + 1] if "--from" in sys.argv else "2022Q1"
DOCTYPE = {"Q1": "interim_report", "Q2": "interim_report", "Q3": "interim_report",
           "Q4": "interim_report", "prelim": "prelim_release",
           "profit_warning": "profit_warning_release", "CMD": "cmd_release"}


def item_for(d, key):
    s = idx[idx.date == d]
    if key:
        s = s[s.title.str.contains(key, case=False, regex=False)]
    else:
        s = s[(s.time >= "06:00") & (s.time <= "08:10")]
    return s.sort_values("time").iloc[0]


def main():
    f = Fetcher(min_gap=1.2)
    for d, key, et, fp in SPEC:
        per = fp or d
        if fp and fp < start:
            continue
        if not fp and d < "2022-01-01":
            continue
        r = item_for(d, key)
        pdfs = [a for a in r.attachments.split("|") if a.lower().endswith(".pdf")]
        if not pdfs:
            print("no pdf", d, et)
            continue
        dt = DOCTYPE[et]
        tag = fp if fp else f"{d[:4]}Q{(int(d[5:7]) - 1) // 3 + 1}"
        out = os.path.join(DOCS, f"{tag}_{dt}.pdf")
        ok, st, p = f.download(pdfs[0], out)
        if not ok or not is_pdf(p):
            print("FAIL", d, et, st, pdfs[0])
            if os.path.exists(p) and not is_pdf(p):
                os.remove(p)
            continue
        txt, n = to_text(p, T, tag, dt)
        print(d, et, tag, os.path.getsize(p), n)
        logp = os.path.join(RAW_IR, T, "docs_log.csv")
        new = not os.path.exists(logp)
        with open(logp, "a", encoding="utf-8") as fh:
            if new:
                fh.write("local_path,url,doc_type,fiscal_period,pub_date\n")
            fh.write(f"{p},{pdfs[0]},{dt},{tag},{d}\n")


def manifest():
    log = os.path.join(RAW_IR, T, "docs_log.csv")
    rows = pd.read_csv(log, dtype=str).fillna("").drop_duplicates("local_path", keep="last")
    rows = [r for r in rows.to_dict("records") if os.path.exists(r["local_path"])]
    extra = os.path.join(RAW_IR, T, "manifest_extra.csv")
    if os.path.exists(extra):
        rows += pd.read_csv(extra, dtype=str).fillna("").to_dict("records")
    path = write_manifest(T, rows)
    print("manifest", path, len(rows))


if __name__ == "__main__":
    if "--manifest-only" not in sys.argv:
        main()
    manifest()
