"""Soitec: manifest + text for downloaded results press releases (FY2022Q4..FY2027Q1) and KPIs by regex."""
import os
import re
import sys
import json
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import irlib  # noqa: E402

T = "SOI.PA"
pr = pd.read_csv(os.path.join(irlib.raw_dir(T), "pr_index.csv"))
ev = pd.read_csv(os.path.join(irlib.PROC_IR, f"{T}_events.csv"))
man, rows = [], []
QEND = {1: "06-30", 2: "09-30", 3: "12-31", 4: "03-31"}
for _, e in ev[(ev.event_date >= "2022-04-01")].iterrows():
    hit = pr[pr.url == e.source_url]
    if hit.empty:
        continue
    src = hit.iloc[0].local
    fp = e.fiscal_period
    out = irlib.extract_text(src, T, fp, "press_release", overwrite=True)
    man.append(dict(local_path=src, url=e.source_url, doc_type="press_release", fiscal_period=fp, pub_date=e.event_date))
    t = re.sub(r"\s+", " ", open(out, errors="replace").read())
    head = t[:6000]
    y = int(fp[2:6])
    if fp.endswith("H1"):
        q, pe = 2, f"{y - 1}-09-30"
    elif re.match(r"FY\d{4}$", fp):
        q, pe = 4, f"{y}-03-31"
    else:
        q = int(fp[-1])
        pe = f"{y - 1 if q < 4 else y}-{QEND[q]}"
    k = dict(fiscal_period=fp, period_end=pe, release_date=e.event_date, currency="EUR", unit="EUR m", source_doc=src)
    extra = {"event_type": e.event_type}
    rv = re.search(r"(Q[1-4]|H1|FY|[Ff]ull[- ]year|[Ff]irst[- ]half)[’'‘]?\s?\d{0,2} (?:consolidated )?revenue (?:of|reached|was at|was|"
                   r"amounted to|totaled|came in at|stood at) (?:€|EUR\s?)([\d.,]+)\s?(m|million|bn|billion)", head)
    if rv:
        v = float(rv.group(2).replace(",", ""))
        k["revenue"] = v * 1000 if rv.group(3) in ("bn", "billion") else v
        extra["revenue_scope"] = rv.group(1)
    cc = re.search(r"(up|down) (\d+(?:\.\d)?)% (?:year-on-year |y-o-y )?(?:on a reported basis|as reported|reported)", head)
    if cc:
        k["revenue_yoy_pct"] = (-1 if cc.group(1) == "down" else 1) * float(cc.group(2))
    lfl = re.search(r"(up|down) (\d+(?:\.\d)?)% (?:year-on-year |y-o-y )?at constant (?:exchange rates|currency)", head)
    if lfl:
        extra["revenue_yoy_constant_fx_pct"] = (-1 if lfl.group(1) == "down" else 1) * float(lfl.group(2))
    eb = re.search(r"EBITDA margin[^.]{0,80}?(\d{1,2}\.\d)%", head)
    if eb:
        extra["ebitda_margin_pct"] = float(eb.group(1))
    gm = re.search(r"[Gg]ross margin[^.]{0,60}?(\d{1,2}\.\d)%", head)
    if gm:
        k["gross_margin_pct"] = float(gm.group(1))
    gl = re.search(r"[^.●]*(?:guidance|[Oo]utlook|expects?)[^.●]*(?:%|€)[^.●]*", head)
    if gl:
        k["guidance_text"] = gl.group(0).strip()[:400]
    notes = [s.strip()[:240] for s in re.split(r"(?<=[.!?●])\s+", t[:15000])
             if re.search(r"\bAI\b|[Dd]ata [Cc]enter|hyperscal|Photonics-SOI|optical transceiver", s) and 25 < len(s) < 500][:3]
    k["ai_dc_notes"] = " | ".join(notes)
    k["extra_json"] = json.dumps(extra)
    rows.append(k)
p, o = irlib.write_manifest(T, man)
print(p, len(o))
p, o = irlib.write_kpis(T, rows)
print(o[["fiscal_period", "revenue", "revenue_yoy_pct", "gross_margin_pct"]].to_string())

# post-process: label rows by the period the extracted revenue refers to; drop FY2024 (no FY24 PR on IR page)
k = pd.read_csv(os.path.join(irlib.PROC_IR, f"{T}_kpis.csv"), dtype=str).fillna("")
k = k[~((k.fiscal_period == "FY2024") & k.source_doc.str.contains("pr-q3"))]
fix = []
for _, r in k.iterrows():
    ex = json.loads(r.extra_json or "{}")
    sc = ex.get("revenue_scope", "")
    if re.match(r"FY\d{4}$", r.fiscal_period) and sc.startswith("Q4"):
        r["fiscal_period"] = r.fiscal_period + "Q4"
    elif r.fiscal_period.endswith("H1") and sc.startswith("Q2"):
        r["fiscal_period"] = r.fiscal_period[:-2] + "Q2"
    fix.append(r.to_dict())
p, o = irlib.write_kpis(T, fix)
print(o[["fiscal_period", "period_end", "revenue", "revenue_yoy_pct"]].to_string())
