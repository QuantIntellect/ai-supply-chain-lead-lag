"""Nokia KPIs from interim-report text (regex on the summary bullets/table). Values as reported, EUR m."""
import os
import re
import sys
import json
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import irlib  # noqa: E402

T = "NOKIA.HE"
man = pd.read_csv(os.path.join(irlib.PROC_IR, f"{T}_manifest.csv"))
man = man[man.doc_type == "interim_report"]
QEND = {1: "03-31", 2: "06-30", 3: "09-30", 4: "12-31"}


def num(s):
    s = s.replace(" ", " ").replace(" ", "").replace(",", "")
    neg = s.startswith("(")
    s = s.strip("()")
    try:
        v = float(s)
    except ValueError:
        return ""
    return -v if neg else v


def sents(txt, pat, n=2, maxlen=260):
    out = []
    for s in re.split(r"(?<=[.!?])\s+", txt):
        if re.search(pat, s, re.I) and 25 < len(s) < 600:
            out.append(s.strip()[:maxlen])
        if len(out) >= n:
            break
    return out


rows = []
for _, m in man.iterrows():
    fp = m.fiscal_period
    tp = os.path.join(irlib.TXT_IR, T, f"{fp}_interim_report.txt")
    raw = open(tp, errors="replace").read()
    t = re.sub(r"[|\n]+", " ", raw)
    t = re.sub(r"\s+", " ", t)
    head = t[:9000]
    r = dict(fiscal_period=fp, period_end=f"{fp[2:6]}-{QEND[int(fp[-1])]}", release_date=m.pub_date,
             currency="EUR", unit="EUR m", source_doc=m.local_path)
    N = r"(\d{1,3}(?: \d{3})*)"
    mm = re.search(r"Reported results.{0,60}?Net sales\s+" + N + r"\s+" + N + r"\s+\(?(-?\d+)\)?%", head) or \
        re.search(r"Net sales\s+" + N + r"\s+" + N + r"\s+\(?(-?\d+)\)?%", head)
    if mm:
        r["revenue"] = num(mm.group(1))
        prev = num(mm.group(2))
        if r["revenue"] != "" and prev:
            r["revenue_yoy_pct"] = round(100 * (r["revenue"] / prev - 1), 1)
    g = re.search(r"Gross margin %\s+(\d+\.\d)%", head)
    if g:
        r["gross_margin_pct"] = float(g.group(1))
    extra = {}
    cc = re.search(r"net sales (?:grew|declined|decreased|increased|were flat|flat)[^.]{0,40}?(-?\d+)?%?[^.]{0,30}"
                   r"constant currency", head, re.I)
    ccm = re.search(r"Q[1-4] net sales[^.]*?(-?\d+)% y-o-y[^.]*?constant currency", head)
    if ccm:
        extra["net_sales_cc_yoy_pct"] = float(ccm.group(1))
    cg = re.search(r"comparable gross margin[^.]{0,80}?(\d+\.\d)%", head, re.I)
    if cg:
        extra["comparable_gross_margin_pct"] = float(cg.group(1))
    co = re.search(r"comparable operating margin[^.]{0,80}?(\d+\.\d)%", head, re.I)
    if co:
        extra["comparable_operating_margin_pct"] = float(co.group(1))
    ni = re.search(r"Network Infrastructure net sales (?:grew|increased|declined|decreased)\s*(-?\d+)%", head)
    if ni:
        extra["network_infrastructure_cc_growth_pct"] = float(ni.group(1))
    on = re.search(r"Optical Networks(?: net sales)?(?: grew| growing| increased)?\s*(-?\d+)%", head)
    if on:
        extra["optical_networks_growth_pct"] = float(on.group(1))
    aio = re.search(r"AI (?:&|and) Cloud customers[^.]{0,80}?order intake\s*(?:grew\s*)?(\d+)%", head, re.I)
    if aio:
        r["orders_yoy_pct"] = float(aio.group(1))
        extra["orders_scope"] = "AI & Cloud customers order intake"
    aiv = re.search(r"secured EUR ([\d.]+) (billion|million) in new orders", head)
    if aiv:
        r["orders"] = float(aiv.group(1)) * (1000 if aiv.group(2) == "billion" else 1)
        extra["orders_scope"] = "AI & Cloud new orders (CEO quote)"
    b2b = re.search(r"book[- ]to[- ]bill[^.]{0,80}?(\d\.\d+)", t, re.I)
    if b2b:
        r["book_to_bill"] = float(b2b.group(1))
        extra["book_to_bill_context"] = re.sub(r"\s+", " ", b2b.group(0))[:160]
    gl = sents(head, r"outlook|expects? (?:full[- ]year|20\d\d)|comparable operating profit (?:of|in the range|between)", 2)
    r["guidance_text"] = " | ".join(gl)
    gr = re.search(r"net sales in the range of EUR ([\d.]+) billion to EUR ([\d.]+) ?(?:billion|bn)", head)
    if gr:
        r["guidance_rev_low"], r["guidance_rev_high"] = float(gr.group(1)) * 1000, float(gr.group(2)) * 1000
    r["ai_dc_notes"] = " | ".join(sents(head, r"\bAI\b|cloud|hyperscal|data cent", 3))
    r["extra_json"] = json.dumps(extra)
    rows.append(r)
p, out = irlib.write_kpis(T, rows)
print(p, len(out))
print(out[["fiscal_period", "revenue", "revenue_yoy_pct", "gross_margin_pct", "orders", "orders_yoy_pct",
           "book_to_bill"]].to_string())
