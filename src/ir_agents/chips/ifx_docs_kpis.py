"""Infineon: quarterly press releases (IR press list, FY2021Q4..FY2026Q3) -> page + PDF, text, manifest, KPIs."""
import os
import re
import sys
import json
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import irlib  # noqa: E402

T = "IFX.DE"
ev = pd.read_csv(os.path.join(irlib.PROC_IR, f"{T}_events.csv"))
ev = ev[ev.source_url.str.contains("/press-release/") & ev.event_type.str.match(r"^Q[1-4]$")]
QEND = {1: "12-31", 2: "03-31", 3: "06-30", 4: "09-30"}
man, rows = [], []
for _, e in ev.iterrows():
    fp = e.fiscal_period
    st, h, _ = irlib.fetch(e.source_url, cache_dir=os.path.join(irlib.raw_dir(T), "pages"))
    if st != 200:
        continue
    dest = os.path.join(irlib.raw_dir(T), f"{fp}_press_release.html")
    with open(dest, "w") as f:
        f.write(h)
    out = irlib.extract_text(dest, T, fp, "press_release", overwrite=True)
    man.append(dict(local_path=dest, url=e.source_url, doc_type="press_release", fiscal_period=fp, pub_date=e.event_date))
    pdfs = sorted(set(re.findall(r'(?:https://assets\.infineon\.com/is/content/infineon/infineon|)'
                                 r'(/?(?:assets/)?row/public/documents/corporate/(?:press|investors)[^"\'\s<>]+?\.pdf)', h)))
    for pth in pdfs[:2]:
        u = ("https://www.infineon.com/" + pth.lstrip("/")) if not pth.startswith("/assets") else "https://www.infineon.com" + pth
        if "presentation" in pth:
            dt = "presentation"
        else:
            dt = "press_release"
        d2 = os.path.join(irlib.raw_dir(T), f"{fp}_{dt}.pdf")
        if irlib.download(u, d2):
            if dt == "presentation":
                irlib.extract_text(d2, T, fp, dt)
            man.append(dict(local_path=d2, url=u, doc_type=dt, fiscal_period=fp, pub_date=e.event_date))
    pdfp = os.path.join(irlib.raw_dir(T), f"{fp}_press_release.pdf")
    if os.path.exists(pdfp):
        with open(pdfp, "rb") as f:
            if f.read(4) == b"%PDF":
                out = irlib.extract_text(pdfp, T, fp, "press_release", overwrite=True)
                k_src = pdfp
    t = re.sub(r"\s+", " ", open(out, errors="replace").read())
    body = t[:15000]
    q, y = int(fp[-1]), int(fp[2:6])
    k = dict(fiscal_period=fp, period_end=f"{y - 1 if q == 1 else y}-{QEND[q]}", release_date=e.event_date,
             currency="EUR", unit="EUR m", source_doc=dest)
    extra = {}
    rv = re.search(r"Q[1-4] FY ?\d{2,4}:? ?[Rr]evenue (?:of )?(?:€|EUR)\s?([\d,.]+) (million|billion)", body) or \
        re.search(r"[Rr]evenue (?:in|for) the (?:first|second|third|fourth|final|last) (?:fiscal )?quarter[^.]{0,80}?"
                  r"(?:€|EUR)\s?([\d,.]+) (million|billion)", body)
    if rv:
        v = float(rv.group(1).replace(",", ""))
        k["revenue"] = v * 1000 if rv.group(2) == "billion" else v
    sr = re.search(r"Segment Result [Mm]argin[^.]{0,40}?([\d.]+)\s?(?:percent|%)", body)
    fyo = re.search(r"Outlook for FY ?\d{2,4}:[^–]{0,400}", body)
    if fyo:
        extra["fy_outlook"] = fyo.group(0)[:400]
    if sr:
        extra["segment_result_margin_pct"] = float(sr.group(1))
    gm = re.search(r"[Gg]ross margin[^.]{0,60}?([\d]{2}\.\d)\s?(?:percent|%)", t)
    if gm:
        k["gross_margin_pct"] = float(gm.group(1))
    gl = re.search(r"Outlook for Q[1-4] FY ?\d{2,4}:[^–]{0,300}?(?:€|EUR)\s?[\d,.]+ (?:million|billion)[^.–]*", body) or \
        re.search(r"[^.]*(?:[Oo]utlook|expects?|forecast)[^.]*(?:revenue|Revenue)[^.]*(?:€|EUR)\s?[\d,.]+ (?:million|billion)[^.]*\.", body)
    if gl:
        k["guidance_text"] = gl.group(0).strip()[:400]
        g = re.search(r"(?:around|approximately|about) (?:€|EUR)\s?([\d,.]+) (million|billion)", gl.group(0)) or \
            re.search(r"(?:€|EUR)\s?([\d,.]+) (million|billion)", gl.group(0))
        if g and re.search(r"around|approximately|about", gl.group(0)):
            v = float(g.group(1).replace(",", "")) * (1000 if g.group(2) == "billion" else 1)
            k["guidance_rev_low"] = k["guidance_rev_high"] = v
            extra["guidance_point_estimate"] = True
    bl = re.search(r"(?:order backlog|backlog)[^.]{0,80}?(?:€|EUR)\s?([\d,.]+) (billion|million)", t, re.I)
    if bl:
        k["backlog"] = float(bl.group(1).replace(",", "")) * (1000 if bl.group(2).lower() == "billion" else 1)
    bb = re.search(r"book[- ]to[- ]bill[^.]{0,60}?(\d\.\d+)", t, re.I)
    if bb:
        k["book_to_bill"] = float(bb.group(1))
    notes = [s.strip()[:240] for s in re.split(r"(?<=[.!?])\s+", body)
             if re.search(r"\bAI\b|data cent|hyperscal|server", s) and 25 < len(s) < 500][:3]
    k["ai_dc_notes"] = " | ".join(notes)
    k["extra_json"] = json.dumps(extra)
    rows.append(k)
p, o = irlib.write_manifest(T, man)
print(p, len(o), o.doc_type.value_counts().to_dict())
p, o = irlib.write_kpis(T, rows)
print(o[["fiscal_period", "revenue", "gross_margin_pct", "guidance_rev_low", "backlog", "book_to_bill"]].to_string())
