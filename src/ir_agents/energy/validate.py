"""Validate the five energy/cable IR outputs against the task schemas and print a coverage summary."""
import sys, os, json, csv, re
from collections import Counter
sys.path.insert(0, "/Users/sinamirzaei/Documents/aimapping/src/ir_agents/energy"); import irlib

TICKERS = sys.argv[1:] or ["ENR.DE", "RR.L", "PRY.MI", "NEX.PA", "NKT.CO"]
TODAY = "2026-10-23"


def header(path):
    with open(path, newline="", encoding="utf-8") as f:
        return next(csv.reader(f))


for t in TICKERS:
    print(f"===== {t}")
    errs = []
    paths = {k: os.path.join(irlib.PROC_IR, f"{t}_{k}.csv") for k in ("events", "kpis", "manifest")}
    notes = os.path.join(irlib.PROC_IR, f"{t}_notes.md")
    for k, p in paths.items():
        if not os.path.exists(p):
            errs.append(f"missing {k}")
    if not os.path.exists(notes):
        errs.append("missing notes.md")
    cols = {"events": irlib.EVENT_COLS, "kpis": irlib.KPI_COLS, "manifest": irlib.MANIFEST_COLS}
    for k, p in paths.items():
        if os.path.exists(p) and header(p) != cols[k]:
            errs.append(f"{k} header mismatch: {header(p)}")
    ev = irlib.read_csv(paths["events"])
    if ev:
        tz = irlib.MARKETS[t][0]
        seen = Counter((r["event_date"], r["event_type"], r["fiscal_period"]) for r in ev)
        dups = [k for k, v in seen.items() if v > 1]
        if dups:
            errs.append(f"dup events {dups[:3]}")
        for r in ev:
            if not irlib.DATE_RE.match(r["event_date"]) or not ("2015-01-01" <= r["event_date"] <= TODAY):
                errs.append(f"event date out of range {r['event_date']}")
            if r["event_type"] not in irlib.EVENT_TYPES:
                errs.append(f"bad event_type {r['event_type']}")
            if r["timing"] not in irlib.TIMINGS:
                errs.append(f"bad timing {r['timing']}")
            if r["timezone"] != tz:
                errs.append(f"bad tz {r['timezone']}")
            tm = r["event_time_local"]
            if tm and irlib.classify_timing(t, tm) != r["timing"]:
                errs.append(f"timing mismatch {r['event_date']} {tm} {r['timing']}")
            if r["fiscal_period"] and not irlib.FP_RE.match(r["fiscal_period"]):
                errs.append(f"bad fiscal_period {r['fiscal_period']}")
        tc = Counter(r["timing"] for r in ev)
        et = Counter(r["event_type"] for r in ev)
        years = Counter(r["event_date"][:4] for r in ev)
        thin = [y for y in map(str, range(2015, 2027)) if years.get(y, 0) < 3]
        print(f"events {len(ev)}  {min(r['event_date'] for r in ev)} -> {max(r['event_date'] for r in ev)}  timing {dict(tc)}")
        print(f"  types {dict(et)}  with_time {sum(1 for r in ev if r['event_time_local'])}  thin_years(<3 events) {thin}")
    man = irlib.read_csv(paths["manifest"])
    if man:
        miss = [r["local_path"] for r in man if not os.path.exists(os.path.join(irlib.ROOT, r["local_path"]))]
        if miss:
            errs.append(f"manifest missing files {len(miss)}")
        bad = [r["doc_type"] for r in man if r["doc_type"] not in irlib.DOC_TYPES]
        if bad:
            errs.append(f"bad doc_type {set(bad)}")
        txtdir = os.path.join(irlib.TEXT_IR, t)
        ntxt = len(os.listdir(txtdir)) if os.path.isdir(txtdir) else 0
        print(f"docs {len(man)} {dict(Counter(r['doc_type'] for r in man))}  text_files {ntxt}")
    kp = irlib.read_csv(paths["kpis"])
    if kp:
        for r in kp:
            if r["source_doc"] and not os.path.exists(os.path.join(irlib.ROOT, r["source_doc"])):
                errs.append(f"kpi source_doc missing {r['fiscal_period']}")
            if r["extra_json"]:
                try:
                    json.loads(r["extra_json"])
                except Exception:
                    errs.append(f"bad extra_json {r['fiscal_period']}")
        fps = [r["fiscal_period"] for r in kp]
        if len(set(fps)) != len(fps):
            errs.append("dup kpi fiscal_period")
        nz = lambda c: sum(1 for r in kp if r.get(c, "") not in ("", None))
        seg = sum(1 for r in kp if r["extra_json"] and json.loads(r["extra_json"]).get("segments"))
        print(f"kpis {len(kp)} {fps[0]} -> {fps[-1]}  revenue {nz('revenue')} orders {nz('orders')} backlog {nz('backlog')} "
              f"b2b {nz('book_to_bill')} guid_text {nz('guidance_text')} guid_rev {nz('guidance_rev_low')} dc_notes {nz('ai_dc_notes')} segments {seg}")
    print("ERRORS:" if errs else "OK", errs[:12])
