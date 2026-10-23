"""Cross-check IR event dates against Yahoo earnings dates (+/-1 day).
Yahoo timestamps are unreliable; only dates are compared (UTC date and the
local date are both tried)."""
import os, sys
import pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from irlib import *
y = pd.read_parquet(os.path.join(ROOT, "data", "processed", "yahoo_earnings_dates.parquet"))
for t in sys.argv[1:]:
    e = pd.read_csv(os.path.join(PROC_IR, f"{t}_events.csv"), dtype=str).fillna("")
    ed = pd.to_datetime(e.event_date)
    res = ed[e.event_type.isin(["Q1", "Q2", "Q3", "Q4", "H1", "FY", "prelim"])]
    yy = y[y.ticker == t].copy()
    yy["loc"] = yy.earn_ts_utc.dt.tz_convert(TZ[t]).dt.tz_localize(None).dt.normalize()
    yy = yy[(yy["loc"] >= "2015-01-01") & (yy["loc"] <= "2026-10-23")]
    miss = []
    for d in yy["loc"]:
        if not ((ed - d).abs() <= pd.Timedelta(days=1)).any():
            miss.append(d.strftime("%Y-%m-%d"))
    extra = []
    for d in res:
        if not ((yy["loc"] - d).abs() <= pd.Timedelta(days=1)).any():
            extra.append(d.strftime("%Y-%m-%d"))
    print(f"{t}: yahoo dates in window {len(yy)}; yahoo dates w/o IR event: {miss}; IR results w/o yahoo date: {len(extra)} {extra[:12]}")
