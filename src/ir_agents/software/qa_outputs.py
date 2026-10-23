"""QA of the IR outputs for the software/IT/telecom group: schema, counts, coverage."""
import os, sys, json
import pandas as pd
sys.path.insert(0, os.path.dirname(__file__))
import fetch_util as fu

EV = "ticker,event_date,event_time_local,timezone,timing,event_type,fiscal_period,source_url".split(",")
KP = ("ticker,fiscal_period,period_end,release_date,currency,unit,revenue,revenue_yoy_pct,orders,orders_yoy_pct,"
      "book_to_bill,backlog,gross_margin_pct,guidance_text,guidance_rev_low,guidance_rev_high,ai_dc_notes,extra_json,source_doc").split(",")
MF = "ticker,local_path,url,doc_type,fiscal_period,pub_date".split(",")
TYPES = set("Q1,Q2,Q3,Q4,H1,FY,trading_update,profit_warning,prelim,CMD".split(","))

for t in ["SAP.DE", "DTE.DE", "DSY.PA", "CAP.PA"]:
    print("=" * 20, t)
    e = pd.read_csv(os.path.join(fu.PROC_IR, t + "_events.csv"), dtype=str).fillna("")
    k = pd.read_csv(os.path.join(fu.PROC_IR, t + "_kpis.csv"), dtype=str).fillna("")
    m = pd.read_csv(os.path.join(fu.PROC_IR, t + "_manifest.csv"), dtype=str).fillna("")
    print("events cols ok:", list(e.columns) == EV, "| kpis cols ok:", list(k.columns) == KP, "| manifest cols ok:", list(m.columns) == MF)
    print("events:", len(e), e.event_date.min(), "->", e.event_date.max(), "| types:", e.event_type.value_counts().to_dict())
    print("  timing:", e.timing.value_counts().to_dict(), "| bad types:", sorted(set(e.event_type) - TYPES),
          "| tz:", e.timezone.unique().tolist(), "| blank src:", (e.source_url == "").sum(),
          "| time set but UNKNOWN:", ((e.event_time_local != "") & (e.timing == "UNKNOWN")).sum(),
          "| no time but BMO/AMC:", ((e.event_time_local == "") & e.timing.isin(["BMO", "AMC", "INTRADAY"])).sum())
    bad_t = e[(e.event_time_local != "") & ~e.event_time_local.str.match(r"^\d{2}:\d{2}$")]
    if len(bad_t): print("  bad time fmt:", bad_t.event_time_local.tolist()[:5])
    dup = e[e.duplicated(["event_date", "event_type", "fiscal_period"], keep=False)]
    if len(dup): print("  dup rows:", dup[["event_date", "event_type", "fiscal_period"]].values.tolist()[:6])
    fut = e[e.event_date > "2026-10-23"]
    if len(fut): print("  FUTURE events:", fut[["event_date", "event_type", "fiscal_period"]].values.tolist())
    print("kpis:", len(k), k.fiscal_period.min(), "->", k.fiscal_period.max(), "| rev filled:", (k.revenue != "").sum(),
          "| yoy:", (k.revenue_yoy_pct != "").sum(), "| orders:", (k.orders != "").sum(), "| b2b:", (k.book_to_bill != "").sum(),
          "| backlog:", (k.backlog != "").sum(), "| GM:", (k.gross_margin_pct != "").sum(), "| guide_txt:", (k.guidance_text != "").sum(),
          "| guide_rev:", (k.guidance_rev_low != "").sum(), "| ai:", (k.ai_dc_notes != "").sum(), "| reldate:", (k.release_date != "").sum())
    badjs = 0
    for x in k.extra_json:
        if x:
            try: json.loads(x)
            except Exception: badjs += 1
    print("  bad extra_json:", badjs, "| units:", k.unit.unique().tolist(), "| empty rows:", ((k.revenue == "") & (k.ai_dc_notes == "")).sum())
    miss = [p for p in m.local_path if not os.path.exists(os.path.join(fu.ROOT, p))]
    print("manifest:", len(m), "| doc types:", m.doc_type.value_counts().to_dict(), "| missing files:", len(miss))
    txtdir = os.path.join(fu.TXT_IR, t)
    print("  text files:", len(os.listdir(txtdir)) if os.path.isdir(txtdir) else 0,
          "| raw files:", sum(len(f) for _, _, f in os.walk(os.path.join(fu.RAW_IR, t))))
