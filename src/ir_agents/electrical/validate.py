"""Validate the four IR outputs per ticker (schema, enums, paths, coverage)."""
import os, sys, json, re
import pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from irlib import *

TICKS = sys.argv[1:] or ["SU.PA", "SIE.DE", "ABBN.SW", "LR.PA", "MTRS.ST"]
for t in TICKS:
    print("=" * 20, t)
    pe = os.path.join(PROC_IR, f"{t}_events.csv")
    pk = os.path.join(PROC_IR, f"{t}_kpis.csv")
    pm = os.path.join(PROC_IR, f"{t}_manifest.csv")
    pn = os.path.join(PROC_IR, f"{t}_notes.md")
    for p in (pe, pk, pm, pn):
        if not os.path.exists(p):
            print("MISSING", os.path.basename(p))
    if os.path.exists(pe):
        e = pd.read_csv(pe, dtype=str).fillna("")
        assert list(e.columns) == EVENT_COLS, ("event cols", list(e.columns))
        bad = e[~e.event_type.isin(EVENT_TYPES)]
        if len(bad): print("bad event_type", bad.event_type.unique())
        mism = e[(e.event_time_local != "") & (e.timing != e.event_time_local.map(classify_timing))]
        if len(mism): print("timing mismatch rows:", len(mism))
        dup = e[e.duplicated(["event_date", "event_type"], keep=False)]
        if len(dup): print("dup date/type:", dup[["event_date", "event_type"]].values.tolist()[:6])
        e15 = e[(e.event_date >= "2015-01-01") & (e.event_date <= "2026-10-31")]
        res = e15[e15.event_type.isin(["Q1", "Q2", "Q3", "Q4", "H1", "FY"])]
        per_year = res.groupby(res.event_date.str[:4]).size().to_dict()
        print(f"events {len(e)} [{e.event_date.min()}..{e.event_date.max()}] results/yr {per_year}")
        print("  types", e.event_type.value_counts().to_dict(), "| timing", e.timing.value_counts().to_dict(),
              "| with HH:MM", (e.event_time_local != "").sum(), "| no source", (e.source_url == "").sum())
        fp_bad = e[(e.fiscal_period != "") & ~e.fiscal_period.str.fullmatch(r"\d{4}Q[1-4]")]
        if len(fp_bad): print("  nonstandard fiscal_period:", fp_bad.fiscal_period.unique()[:8])
    if os.path.exists(pk):
        k = pd.read_csv(pk, dtype=str).fillna("")
        assert list(k.columns) == KPI_COLS, ("kpi cols", list(k.columns))
        k22 = k[k.fiscal_period >= "2022Q1"]
        cov = {c: int((k22[c] != "").sum()) for c in ["revenue", "revenue_yoy_pct", "orders", "orders_yoy_pct", "book_to_bill", "backlog", "gross_margin_pct", "guidance_text", "ai_dc_notes", "extra_json"]}
        print(f"kpis {len(k)} rows [{k.fiscal_period.min()}..{k.fiscal_period.max()}]; 2022+ rows {len(k22)} cov {cov}")
        badj = 0
        for x in k.extra_json:
            if x:
                try: json.loads(x)
                except Exception: badj += 1
        if badj: print("  bad extra_json rows", badj)
        dupk = k[k.duplicated("fiscal_period", keep=False)]
        if len(dupk): print("  dup kpi periods", dupk.fiscal_period.unique()[:5])
    if os.path.exists(pm):
        m = pd.read_csv(pm, dtype=str).fillna("")
        assert list(m.columns) == MANIFEST_COLS, ("manifest cols", list(m.columns))
        miss = [p for p in m.local_path if not os.path.exists(os.path.join(ROOT, p) if not p.startswith("/") else p)]
        dupp = m[m.duplicated("local_path", keep=False)]
        txtdir = os.path.join(TEXT_IR, t)
        ntxt = len(os.listdir(txtdir)) if os.path.isdir(txtdir) else 0
        print(f"manifest {len(m)} docs; types {m.doc_type.value_counts().to_dict()}; missing files {len(miss)}; dup paths {len(dupp)}; text files {ntxt}")
        m22 = m[m.fiscal_period >= "2022Q1"]
        print("  2022+ periods with docs:", m22.fiscal_period.nunique())
    if os.path.exists(pn):
        txt = open(pn).read()
        print("notes bullets:", len(re.findall(r"^\s*[-*] ", txt, re.M)), "chars", len(txt))
