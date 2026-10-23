"""Register cached MFN release pages (report press releases) as documents.

Uses pages already fetched by mtrs_mar_scan.py (data/raw/ir/MTRS.ST/mfn_items/);
fetches any missing one politely. Writes data/raw/ir/MTRS.ST/manifest_extra.csv.
"""
import os, sys, csv
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from irlib import Fetcher, RAW_IR, TEXT_IR, ensure  # noqa: E402
from mtrs_events import SPEC, idx  # noqa: E402
from mtrs_mfn_item import fetch, text_of  # noqa: E402

T = "MTRS.ST"
f = Fetcher(min_gap=1.2)
rows = []
for d, key, et, fp in SPEC:
    if d < "2022-01-01":
        continue
    s = idx[idx.date == d]
    s = s[s.title.str.contains(key, case=False, regex=False)] if key else s[(s.time >= "06:00") & (s.time <= "08:10")]
    r = s.sort_values("time").iloc[0]
    p = fetch(f, r.url)
    per = fp if fp else f"{d[:4]}Q{(int(d[5:7]) - 1) // 3 + 1}"
    dt = {"prelim": "prelim_press_release", "CMD": "cmd_press_release"}.get(et, "press_release")
    out = os.path.join(ensure(os.path.join(TEXT_IR, T)), f"{per}_{dt}.txt")
    with open(out, "w", encoding="utf-8") as fh:
        fh.write(text_of(p))
    rows.append({"local_path": p, "url": r.url, "doc_type": dt, "fiscal_period": per, "pub_date": d})
with open(os.path.join(RAW_IR, T, "manifest_extra.csv"), "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=["local_path", "url", "doc_type", "fiscal_period", "pub_date"])
    w.writeheader(); w.writerows(rows)
print("release pages", len(rows))
