"""STM: download earnings release / presentation / CEO script (investors.st.com quarterly-results table) for
FY2022Q1..latest, extract text, manifest; KPIs by regex from the earnings release."""
import os
import re
import sys
import json
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import irlib  # noqa: E402

T = "STMPA.PA"
qr = pd.read_csv(os.path.join(irlib.raw_dir(T), "qr_table.csv")).fillna("")
QEND = {1: "03-31", 2: "06-30", 3: "09-30", 4: "12-31"}
man, rows = [], []
for _, r in qr.iterrows():
    m = re.search(r"Q([1-4])\s*(\d{4})", r.quarter)
    if not m or r.date > "2026-10-23" or r.date < "2021-12-01":
        continue
    fp = f"FY{m.group(2)}Q{m.group(1)}"
    docs = {"press_release": r.get("earnings release") or r.get("press release"),
            "presentation": r.get("earnings presentation") or r.get("presentation"),
            "transcript": r.get("ceo script") or r.get("ceo")}
    for dt, u in docs.items():
        if not u:
            continue
        dest = os.path.join(irlib.raw_dir(T), f"{fp}_{dt}.pdf")
        if irlib.download(u, dest):
            irlib.extract_text(dest, T, fp, dt)
            man.append(dict(local_path=dest, url=u, doc_type=dt, fiscal_period=fp, pub_date=r.date))
    tp = os.path.join(irlib.TXT_IR, T, f"{fp}_press_release.txt")
    if not os.path.exists(tp):
        continue
    t = re.sub(r"\s+", " ", open(tp, errors="replace").read())
    head = t[:12000]
    k = dict(fiscal_period=fp, period_end=f"{m.group(2)}-{QEND[int(m.group(1))]}", release_date=r.date,
             currency="USD", unit="USD m", source_doc=os.path.join(irlib.raw_dir(T), f"{fp}_press_release.pdf"))
    extra = {}
    nr = re.search(r"ST reported (?:first|second|third|fourth|full year)?\s*quarter (?:20\d\d )?net revenues of \$\s?([\d.,]+) "
                   r"(million|billion), gross margin of ([\d.]+)%(?:, operating (?:margin of (-?[\d.]+)%|income))?", head)
    if nr:
        v = float(nr.group(1).replace(",", ""))
        k["revenue"] = v * 1000 if nr.group(2) == "billion" else v
        k["gross_margin_pct"] = float(nr.group(3))
        if nr.group(4):
            extra["operating_margin_pct"] = float(nr.group(4))
    yy = re.search(r"year-over-year basis,? (?:Q[1-4] |(?:first|second|third|fourth) quarter )?net revenues "
                   r"(increased|decreased|were down|were up|grew|declined) (?:by )?([\d.]+)%", head)
    if yy:
        k["revenue_yoy_pct"] = (-1 if yy.group(1) in ("decreased", "were down", "declined") else 1) * float(yy.group(2))
    gd = re.search(r"[Bb]usiness outlook at (?:the )?mid-point:? Q([1-4])(?:\s?\d{2})? net revenues of \$\s?([\d.,]+) (million|billion) "
                   r"and gross margin of ([\d.]+)%", head)
    pm = re.search(r"plus or minus (\d+) basis points", t)
    if gd:
        mid = float(gd.group(2).replace(",", "")) * (1000 if gd.group(3) == "billion" else 1)
        k["guidance_text"] = re.sub(r"\s+", " ", gd.group(0))[:300] + (f"; +/- {pm.group(1)} bps" if pm else "")
        extra.update({"guidance_mid": mid, "guidance_gross_margin_pct": float(gd.group(4)),
                      "guidance_quarter": f"Q{gd.group(1)}"})
        if pm:
            pp = float(pm.group(1)) / 100
            k["guidance_rev_low"], k["guidance_rev_high"] = round(mid * (1 - pp / 100), 1), round(mid * (1 + pp / 100), 1)
            extra["guidance_derived"] = True
    fy = re.search(r"(?:full[- ]year|FY ?20\d\d)[^.]{0,120}?(?:revenues?|net revenues)[^.]{0,80}?\$\s?([\d.]+) (?:billion)[^.]*\.", head)
    if fy:
        extra["fy_revenue_comment"] = re.sub(r"\s+", " ", fy.group(0))[:250]
    b2b = re.search(r"book[- ]to[- ]bill[^.]{0,100}", t, re.I)
    if b2b:
        extra["book_to_bill_context"] = b2b.group(0)[:160]
        bb = re.search(r"(\d\.\d+)", b2b.group(0))
        if bb:
            k["book_to_bill"] = float(bb.group(1))
    notes = []
    for s in re.split(r"(?<=[.!?])\s+", t[:25000]):
        if re.search(r"\bAI\b|data ?cent|datacenter|hyperscal|photonic|cloud|server", s) and 25 < len(s) < 500:
            notes.append(s.strip()[:240])
        if len(notes) >= 3:
            break
    k["ai_dc_notes"] = " | ".join(notes)
    k["extra_json"] = json.dumps(extra)
    rows.append(k)
p, out = irlib.write_manifest(T, man)
print(p, len(out), out.doc_type.value_counts().to_dict())
p, out = irlib.write_kpis(T, rows)
print(p, len(out))
print(out[["fiscal_period", "revenue", "revenue_yoy_pct", "gross_margin_pct", "guidance_rev_low",
           "guidance_rev_high", "book_to_bill"]].to_string())
