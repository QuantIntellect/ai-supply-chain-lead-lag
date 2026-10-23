"""SUSS events: suss.com news (EQS-distributed corporate news / ad-hocs, 2020-06..2026-10) with EQS timestamps
parsed from each release page; Yahoo dates (no time) for 2015..mid-2020 report dates."""
import os
import re
import sys
import pandas as pd
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import irlib  # noqa: E402

T = "SMHN.DE"
ni = pd.read_csv(os.path.join(irlib.raw_dir(T), "news_index.csv"))
ni = ni[ni.category.isin(["ad-hoc", "corporate-news"])]
REL = (r"quarter|half-year|half year|figures|results|forecast|guidance|order|preliminary|sales|financial year|"
       r"fiscal year|Capital Markets Day|nine months|record|grow|successful year|financial statements|Quartalsmitteilung")
EXCL = r"Supervisory Board|Chief Executive|CEO|CFO|appoint|Bendele|Frick|merger|sell the MicroOptics|sale of the MicroOptics|" \
       r"lease agreement|production site|production facility|corporate design|TecDax|SDax|MDAX|loan|Annual General|" \
       r"Innovation Center|wins|Imprint|imprint|collaboration|Partner|partner|XBC300|Temporary bonding|retire"
ni = ni[ni.title.str.contains(REL, case=False, regex=True) & ~ni.title.str.contains(EXCL, regex=True)]
rows = []
for _, r in ni.iterrows():
    st, html, _ = irlib.fetch(r.url, cache_dir=os.path.join(irlib.raw_dir(T), "pages"))
    txt = irlib.html_to_text(html, is_html=True) if st == 200 else ""
    m = re.search(r"(\d{2}-[A-Z][a-z]{2}-\d{4}|\d{2}\.\d{2}\.\d{4}) / (\d{2}:\d{2}) CET/CEST", txt)
    d, tm = r.date, ""
    if m:
        fmt = "%d-%b-%Y" if "-" in m.group(1) else "%d.%m.%Y"
        d = datetime.strptime(m.group(1), fmt).strftime("%Y-%m-%d")
        tm = m.group(2)
    else:  # fallback: suss.com page timestamp (matches the EQS stamp where both exist)
        m2 = re.search(r"([A-Z][a-z]{2} \d{1,2}, \d{4}) (\d{2}:\d{2}):\d{2}", txt)
        if m2:
            d2 = datetime.strptime(m2.group(1), "%b %d, %Y").strftime("%Y-%m-%d")
            if d2 == r.date and "06:00" <= m2.group(2) <= "23:00":
                tm = m2.group(2)
    rows.append(dict(date=d, time=tm, cat=r.category, title=r.title, url=r.url))
nd = pd.DataFrame(rows).sort_values(["date", "cat"])
nd.to_csv(os.path.join(irlib.raw_dir(T), "news_timed.csv"), index=False)


def classify(r):
    t, m, y = r.title.lower(), int(r.date[5:7]), int(r.date[:4])
    if "capital markets day" in t:
        return "CMD", f"FY{y}Q{(m - 1) // 3 + 1}"
    if re.search(r"adjusts forecast|below market expectations", t):
        if "third quarter" in t or "q3" in t:
            return "profit_warning", f"FY{y}Q3"
        if "half" in t or m == 7:
            return "profit_warning", f"FY{y}Q2"
        return "profit_warning", f"FY{y}Q{(m - 1) // 3}"
    if r["cat"] == "ad-hoc":
        if re.search(r"preliminary|exceed.*forecast|forecast to exceed|meets guidance", t) and m in (1, 2):
            return "prelim", f"FY{y - 1}"
        if re.search(r"first quarter", t):
            return "prelim", f"FY{y}Q1"
        if re.search(r"q3 2020", t):
            return "prelim", f"FY{y}Q3"
        if re.search(r"first half year|first half-year", t):
            return "prelim", f"FY{y}Q2"
        if re.search(r"raise|increased earnings|order entry|order intake", t):
            return "trading_update", f"FY{y}Q{(m - 1) // 3 + 1}"
        return None, None
    # corporate news (regular reports)
    if re.search(r"preliminary|meets guidance", t) and m in (1, 2):
        return "prelim", f"FY{y - 1}"
    if m in (3, 4) and not re.search(r"first quarter", t):
        return "FY", f"FY{y - 1}"
    if m == 5:
        return "Q1", f"FY{y}Q1"
    if m in (7, 8):
        return "Q2", f"FY{y}Q2"
    if m in (10, 11):
        return ("Q3", f"FY{y}Q3") if not re.search(r"order entry in the third quarter", t) else (None, None)
    return None, None


ev = []
for _, r in nd.iterrows():
    et, fp = classify(r)
    if not et:
        continue
    ev.append(dict(event_date=r.date, event_time_local=r.time, timing=irlib.timing_class(T, r.time),
                   event_type=et, fiscal_period=fp, source_url=r.url))
evd = pd.DataFrame(ev)
# same date: keep ad-hoc (earlier, market-moving) over corporate news duplicate of same type
evd["_pri"] = evd.event_type.map(lambda x: 0 if x in ("profit_warning", "prelim", "trading_update", "CMD") else 1)
evd["_nt"] = (evd.event_time_local == "").astype(int)
evd = evd.sort_values(["event_date", "_pri", "_nt"]).drop_duplicates(["event_date"], keep="first")
evd = evd.drop(columns=["_pri", "_nt"])
# Yahoo report dates (no time) before the suss.com news archive starts (Jun 2020)
y = pd.read_parquet(os.path.join(irlib.ROOT, "data", "processed", "yahoo_earnings_dates.parquet"))
yd = sorted(set(y[y.ticker == T].earn_ts_utc.astype(str).str[:10]))
for d in yd:
    if not ("2015-01-01" <= d < "2020-06-01"):
        continue
    yy, m = int(d[:4]), int(d[5:7])
    et, fp = {3: ("FY", f"FY{yy - 1}"), 4: ("FY", f"FY{yy - 1}"), 5: ("Q1", f"FY{yy}Q1"), 8: ("Q2", f"FY{yy}Q2"),
              11: ("Q3", f"FY{yy}Q3")}.get(m, (None, None))
    if et:
        ev.append(dict(event_date=d, event_time_local="", timing="UNKNOWN", event_type=et, fiscal_period=fp,
                       source_url="https://finance.yahoo.com/quote/SMHN.DE/ (earnings date; no time)"))
evd = pd.concat([evd, pd.DataFrame(ev[len(evd):])]).drop_duplicates(["event_date"], keep="first")
p, out = irlib.write_events(T, evd.to_dict("records"))
print(p, len(out))
print(out[["event_date", "event_time_local", "timing", "event_type", "fiscal_period"]].to_string())
