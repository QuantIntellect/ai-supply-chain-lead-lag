"""SUSS: download financial reports 2022..2026 (finanzberichte page) + results news pages; extract text; manifest;
KPIs (quarterly sales, order intake, backlog, gross margin) by regex from the results news releases."""
import os
import re
import sys
import json
import pandas as pd
from bs4 import BeautifulSoup
from urllib.parse import urljoin

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import irlib  # noqa: E402

T = "SMHN.DE"
st, html, fin = irlib.fetch("https://www.suss.com/en/investor-relations/finanzberichte",
                            cache_dir=os.path.join(irlib.raw_dir(T), "pages"))
soup = BeautifulSoup(html, "html.parser")
ev = pd.read_csv(os.path.join(irlib.PROC_IR, f"{T}_events.csv"))
man = []
for a in soup.find_all("a", href=True):
    lab = re.sub(r"\s+", " ", a.get_text(" ")).strip()
    u = urljoin(fin, a["href"])
    if "download" not in u:
        continue
    m = None
    if re.search(r"Annual Report (\d{4})", lab):
        y = re.search(r"Annual Report (\d{4})", lab).group(1)
        fp, dt = f"FY{y}", "annual_report"
    elif re.search(r"(?:Quarterly|Interim) (?:Report|Statement).*March 31,? (\d{4})|January 1 - March 31, (\d{4})", lab):
        y = re.findall(r"(\d{4})", lab)[-1]
        fp, dt = f"FY{y}Q1", "interim_report"
    elif re.search(r"Half-yearly Financial Report (\d{4})|June 30, (\d{4})", lab):
        y = re.findall(r"(\d{4})", lab)[-1]
        fp, dt = f"FY{y}Q2", "interim_report"
    elif re.search(r"September 30, (\d{4})", lab):
        y = re.findall(r"(\d{4})", lab)[-1]
        fp, dt = f"FY{y}Q3", "interim_report"
    else:
        continue
    if int(fp[2:6]) < 2022:
        continue
    dest = os.path.join(irlib.raw_dir(T), f"{fp}_{dt}.pdf")
    if irlib.download(u, dest):
        irlib.extract_text(dest, T, fp, dt)
        pub = ev[(ev.fiscal_period == fp) & ev.event_type.isin(["Q1", "Q2", "Q3", "FY"])].event_date
        man.append(dict(local_path=dest, url=u, doc_type=dt, fiscal_period=fp, pub_date=pub.iloc[0] if len(pub) else ""))
# current investor presentation
ip = "https://www.suss.com/en/content/download/3502/file/2026_10_02_SUSS_Investor%20Presentation_October%202026.pdf"
dest = os.path.join(irlib.raw_dir(T), "FY2026Q3_presentation.pdf")
if irlib.download(ip, dest):
    irlib.extract_text(dest, T, "FY2026Q3", "presentation")
    man.append(dict(local_path=dest, url=ip, doc_type="presentation", fiscal_period="FY2026Q3", pub_date="2026-10-02"))
# results news releases (EQS corporate news / ad-hoc) as press_release docs + KPI source
nt = pd.read_csv(os.path.join(irlib.raw_dir(T), "news_timed.csv"))
QEND = {1: "03-31", 2: "06-30", 3: "09-30", 4: "12-31"}
rows = []
for _, e in ev[(ev.event_date >= "2022-01-01")].iterrows():
    n = nt[nt.url == e.source_url]
    if n.empty:
        continue
    st, h, _ = irlib.fetch(e.source_url, cache_dir=os.path.join(irlib.raw_dir(T), "pages"))
    dt = "press_release"
    fp = e.fiscal_period
    tag = f"{fp}_{e.event_type}" if e.event_type not in ("Q1", "Q2", "Q3", "FY") else fp
    dest = os.path.join(irlib.raw_dir(T), f"{tag}_{dt}.html")
    with open(dest, "w") as f:
        f.write(h)
    out = irlib.extract_text(dest, T, tag, dt, overwrite=True)
    man.append(dict(local_path=dest, url=e.source_url, doc_type=dt, fiscal_period=fp, pub_date=e.event_date))
    if e.event_type not in ("Q1", "Q2", "Q3", "FY", "prelim"):
        continue
    t = re.sub(r"\s+", " ", open(out, errors="replace").read())
    i = t.find("CET/CEST")
    body = t[i:i + 9000] if i > 0 else t[:9000]
    for stop in ("End of Announcement", "More News", "Discover more news"):
        j = body.find(stop)
        if j > 0:
            body = body[:j]
    if e.event_type in ("FY", "prelim") and not re.match(r"FY\d{4}Q", fp):
        q = 4
        y = int(fp[2:6])
    else:
        q, y = int(fp[-1]), int(fp[2:6])
    k = dict(fiscal_period=f"FY{y}Q{q}", period_end=f"{y}-{QEND[q]}", release_date=e.event_date, currency="EUR",
             unit="EUR m", source_doc=dest)
    extra = {"source_event_type": e.event_type}
    qw = {1: "first quarter", 2: "second quarter", 3: "third quarter", 4: "fourth quarter"}[q]

    def grab(pat):
        m = re.search(pat, body, re.I)
        return float(m.group(1).replace(",", "")) if m else ""
    k["revenue"] = grab(rf"{qw}[^.]{{0,160}}?sales (?:of|amounted to|totaled|reached|rose to|increased to|came to)"
                        r"[^.]{0,20}?€\s?([\d.,]+)\s?million") or \
        grab(rf"sales (?:of|amounting to|totaling) €\s?([\d.,]+)\s?million[^.]{{0,60}}?{qw}") or \
        grab(rf"(?:Q{q}|{qw})[^.]{{0,40}}? sales[^.]{{0,40}}?€\s?([\d.,]+)\s?million")
    k["orders"] = grab(rf"{qw}[^.]{{0,200}}?order (?:intake|entry)[^.]{{0,40}}?€\s?([\d.,]+)\s?million") or \
        grab(rf"order (?:intake|entry) (?:of|amounting to|totaling|reached|rose to) €\s?([\d.,]+)\s?million[^.]{{0,60}}?{qw}") or \
        grab(rf"(?:Q{q}|{qw})[^.]{{0,40}}? order (?:intake|entry)[^.]{{0,40}}?€\s?([\d.,]+)\s?million") or \
        grab(rf"order (?:intake|entry)[^.]{{0,40}}?€\s?([\d.,]+)\s?million[^.]{{0,30}}?{qw}")
    k["backlog"] = grab(r"order (?:backlog|book)[^.]{0,80}?€\s?([\d.,]+)\s?million")
    k["gross_margin_pct"] = grab(r"gross profit margin[^.]{0,120}?(\d{2}\.\d)\s?(?:%|percent)") or \
        grab(r"gross (?:profit )?margin[^.]{0,80}?(\d{2}\.\d)\s?(?:%|percent)")
    yy = re.search(r"sales[^.]{0,120}?(?:up|increase[ds]?|growth|rose|down|decrease[ds]?|declined?) (?:of |by )?"
                   r"(?:around |about |roughly )?(\d+(?:\.\d)?)\s?(?:%|percent)", body, re.I)
    if yy:
        sign = -1 if re.search(r"down|decreas|declin", yy.group(0), re.I) else 1
        k["revenue_yoy_pct"] = sign * float(yy.group(1))
    gt = re.search(r"[^.]*(?:forecast|guidance|expects?)[^.]*(?:€\s?[\d.,]+\s?(?:million|billion)|percent|%)[^.]*\.", body)
    if gt:
        k["guidance_text"] = gt.group(0).strip()[:350]
        rg = re.search(r"€\s?([\d.,]+)\s?(?:million)?\s?(?:and|to|-|–)\s?€?\s?([\d.,]+)\s?million", gt.group(0))
        if rg:
            k["guidance_rev_low"], k["guidance_rev_high"] = float(rg.group(1)), float(rg.group(2))
    notes = [s.strip()[:240] for s in re.split(r"(?<=[.!?])\s+", body)
             if re.search(r"\bAI\b|artificial intelligence|HBM|high[- ]bandwidth|hybrid bond|temporary bond", s, re.I)
             and 25 < len(s) < 500][:3]
    k["ai_dc_notes"] = " | ".join(notes)
    if k["orders"] and k["revenue"]:
        k["book_to_bill"] = round(k["orders"] / k["revenue"], 2)
        extra["book_to_bill_derived"] = True
    k["extra_json"] = json.dumps(extra)
    rows.append(k)
p, out = irlib.write_manifest(T, man)
print(p, len(out), out.doc_type.value_counts().to_dict())
kp = pd.DataFrame(rows)
kp["_pri"] = kp.extra_json.str.contains('"prelim"').astype(int)
kp = kp.sort_values(["fiscal_period", "_pri"]).drop_duplicates("fiscal_period").drop(columns="_pri")
p, out = irlib.write_kpis(T, kp.to_dict("records"))
print(p, len(out))
print(out[["fiscal_period", "release_date", "revenue", "revenue_yoy_pct", "orders", "backlog", "gross_margin_pct"]].to_string())
