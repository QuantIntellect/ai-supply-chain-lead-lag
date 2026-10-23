"""Validate the chips IR outputs: schema, vocab, per-year event counts, manifest files present, KPI coverage.
Usage: validate.py [TICKER ...]"""
import os
import sys
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import irlib  # noqa: E402

TICKERS = sys.argv[1:] or ["IFX.DE", "STMPA.PA", "SOI.PA", "SMHN.DE", "NOKIA.HE"]
for t in TICKERS:
    print("=" * 20, t)
    for kind, cols in (("events", irlib.EVENT_COLS), ("kpis", irlib.KPI_COLS),
                       ("manifest", irlib.MANIFEST_COLS)):
        p = os.path.join(irlib.PROC_IR, f"{t}_{kind}.csv")
        if not os.path.exists(p):
            print(f"  {kind}: MISSING")
            continue
        df = pd.read_csv(p, dtype=str).fillna("")
        ok = list(df.columns) == cols
        print(f"  {kind}: rows={len(df)} schema_ok={ok}")
        if kind == "events":
            bad = set(df.event_type) - irlib.EVENT_TYPES
            badt = set(df.timing) - irlib.TIMINGS
            if bad or badt:
                print("   BAD vocab", bad, badt)
            df["yr"] = df.event_date.str[:4]
            tab = df.pivot_table(index="yr", columns="event_type", values="ticker", aggfunc="count",
                                 fill_value=0)
            print(tab.to_string())
            print("   timing:", df.timing.value_counts().to_dict(), "| with time:",
                  (df.event_time_local != "").sum(), "| range:", df.event_date.min(), df.event_date.max())
            dup = df[df.duplicated(["event_date"], keep=False)]
            if len(dup):
                print("   same-date rows:", len(dup))
        if kind == "manifest":
            miss = [x for x in df.local_path if not os.path.exists(x if x.startswith("/") else
                                                                    os.path.join(irlib.ROOT, x))]
            print("   doc_types:", df.doc_type.value_counts().to_dict(), "| missing files:", len(miss))
            bad = set(df.doc_type) - irlib.DOC_TYPES
            if bad:
                print("   BAD doc_type", bad)
        if kind == "kpis":
            cov = {c: int((df[c] != "").sum()) for c in ["revenue", "revenue_yoy_pct", "orders",
                                                       "book_to_bill", "backlog", "gross_margin_pct",
                                                       "guidance_text", "ai_dc_notes"]}
            print("   coverage:", cov, "| periods:", df.fiscal_period.min(), "->", df.fiscal_period.max())
    n = os.path.join(irlib.PROC_IR, f"{t}_notes.md")
    print("  notes.md:", "present" if os.path.exists(n) else "MISSING")
    td = os.path.join(irlib.TXT_IR, t)
    print("  text files:", len(os.listdir(td)) if os.path.isdir(td) else 0)
