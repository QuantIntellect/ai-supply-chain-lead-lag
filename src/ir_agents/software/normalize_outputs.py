"""Cross-company harmonisation of the software/IT/telecom IR outputs:
 - CMD fiscal_period -> event year (YYYY)
 - DSY 2015-2018Q3 times from 3ds.com newsroom metadata (uniform 07:00, possibly a default) -> blank (timing kept BMO)
 - drop events dated after the as-of date (not yet published) and KPI rows for unreported periods."""
import os, sys
import pandas as pd
sys.path.insert(0, os.path.dirname(__file__))
import fetch_util as fu

ASOF = "2026-10-23"
for t in ["SAP.DE", "DTE.DE", "DSY.PA", "CAP.PA"]:
    p = os.path.join(fu.PROC_IR, t + "_events.csv")
    e = pd.read_csv(p, dtype=str).fillna("")
    n0 = len(e)
    cmd = e.event_type == "CMD"
    e.loc[cmd, "fiscal_period"] = e.loc[cmd, "event_date"].str[:4]
    if t == "DSY.PA":
        m = (e.event_date < "2018-10-01") & e.source_url.str.contains("www.3ds.com/newsroom") & (e.event_time_local == "07:00")
        e.loc[m, "event_time_local"] = ""
        print(t, "blanked metadata times:", int(m.sum()))
    fut = e.event_date > ASOF
    if fut.any():
        print(t, "dropping future events:", e.loc[fut, ["event_date", "event_type", "fiscal_period"]].values.tolist())
    e = e[~fut].sort_values(["event_date", "event_time_local"]).reset_index(drop=True)
    e.to_csv(p, index=False)
    k = pd.read_csv(os.path.join(fu.PROC_IR, t + "_kpis.csv"), dtype=str).fillna("")
    empty = (k.revenue == "") & (k.orders == "") & (k.ai_dc_notes == "") & (k.guidance_text == "")
    if empty.any():
        print(t, "dropping empty KPI rows:", k.loc[empty, "fiscal_period"].tolist())
    k[~empty].to_csv(os.path.join(fu.PROC_IR, t + "_kpis.csv"), index=False)
    print(t, "events", n0, "->", len(e), "| kpis", len(k), "->", int((~empty).sum()))
