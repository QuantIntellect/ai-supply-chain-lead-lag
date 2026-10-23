"""Build data/processed/ir/PRY.MI_manifest.csv from docs_index.csv (+ selected SDIR regulatory copies)."""
import sys; sys.path.insert(0, "/Users/sinamirzaei/Documents/aimapping/src/ir_agents/energy"); import irlib
import os
T = "PRY.MI"
ev = {r["fiscal_period"]: r["event_date"] for r in irlib.read_csv(os.path.join(irlib.PROC_IR, f"{T}_events.csv"))
      if r["event_type"] in ("Q1", "H1", "Q3", "FY")}
rows = []
for r in irlib.read_csv(os.path.join(irlib.RAW_IR, T, "docs_index.csv")):
    if not r["local_path"]:
        continue
    p = r["period"]
    if p.startswith("CMD2025"):
        fp, pub = "", "2025-03-26"
    elif "EncoreWire" in p:
        fp, pub = "", "2024-04-15"
    elif "Atkore" in p:
        fp, pub = "", "2026-08-03"
    else:
        fp, pub = p, ev.get(p, "")
    rows.append({"local_path": r["local_path"], "url": r["url"], "doc_type": r["doctype"], "fiscal_period": fp, "pub_date": pub})
# regulatory (SDIR) copies of non-results events, used as event evidence and narrative sources
covers = {c["url"].rsplit("/", 1)[-1]: c for c in irlib.read_csv(os.path.join(irlib.RAW_IR, T, "sdir_covers.csv")) if c.get("local")}
EXTRA = [("20180622_49083.pdf", "press_release", "FY2018", "2018-06-22"),
         ("20190409_61084.pdf", "other", "FY2019Q1", "2019-04-08"),
         ("20190417_61698.pdf", "press_release", "FY2018", "2019-04-17"),
         ("20231005_137720.pdf", "press_release", "", "2023-10-05"),
         ("20250326_162885.pdf", "press_release", "", "2025-03-26")]
for fn, dt, fp, pub in EXTRA:
    c = covers.get(fn)
    if c:
        rows.append({"local_path": c["local"], "url": c["url"], "doc_type": dt, "fiscal_period": fp, "pub_date": pub})
irlib.write_manifest(T, rows)
from collections import Counter
print(Counter(r["doc_type"] for r in rows))
