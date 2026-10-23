"""Probe Schneider doc refs on download.se.com for 2022-2026 periods."""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from irlib import *

f = Fetcher(min_gap=1.0)
periods = []
for y in range(2022, 2027):
    periods += [(f"{y}Q1", ["q1-revenues", "Q1-revenues"], ["Q1-results", "q1-results", "q1-revenues", "Q1-revenues"]),
                (f"{y}Q2", ["hy-results", "HY-results", "h1-results"], ["hy-results", "HY-results"]),
                (f"{y}Q3", ["q3-revenues", "Q3-revenues"], ["Q3-results", "q3-results", "q3-revenues", "Q3-revenues"]),
                (f"{y}Q4", ["fy-results", "FY-results"], ["fy-results", "FY-results"])]
only = sys.argv[1:]  # optional list of periods
found = {}
outp = os.path.join(RAW_IR, "SU.PA", "pages", "docref_probe.json")
if os.path.exists(outp):
    found = json.load(open(outp))
for per, rel_vars, tr_vars in periods:
    if only and per not in only:
        continue
    y = per[:4]
    for dtype, variants in [("release", rel_vars), ("presentation", rel_vars), ("transcript", tr_vars)]:
        key = f"{per}_{dtype}"
        if key in found:
            continue
        for v in variants:
            ref = f"{dtype}-{v}-{y}"
            url = f"https://download.se.com/files?p_Doc_Ref={ref}"
            r = f.get(url)
            okpdf = r.status_code == 200 and r.content[:5] == b"%PDF-"
            if okpdf:
                out = os.path.join(RAW_IR, "SU.PA", f"{per}_{dtype}.pdf")
                with open(out, "wb") as fh:
                    fh.write(r.content)
                found[key] = {"url": url, "path": out, "bytes": len(r.content)}
                break
        print(key, "OK" if key in found else "MISSING", flush=True)
        json.dump(found, open(outp, "w"), indent=1)
