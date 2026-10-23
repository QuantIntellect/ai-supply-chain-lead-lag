"""STM: parse investors.st.com quarterly-results table (dates + document links), merge EDGAR FTS dates,
write STMPA.PA_events.csv and a doc index (data/raw/ir/STMPA.PA/qr_table.csv)."""
import os
import re
import sys
from datetime import datetime
import pandas as pd
from bs4 import BeautifulSoup
from urllib.parse import urljoin

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import irlib  # noqa: E402

T = "STMPA.PA"
st, html, fin = irlib.fetch("https://investors.st.com/financial-information/quarterly-results",
                            cache_dir=os.path.join(irlib.raw_dir(T), "pages"))
soup = BeautifulSoup(html, "html.parser")
rows = []
for tr in soup.find_all("tr"):
    d = tr.find("td", class_="bdate")
    q = tr.find("td", class_="bquarter")
    if not d or not q:
        continue
    date = datetime.strptime(re.sub(r"\s+", " ", d.get_text()).strip(), "%b %d, %Y").strftime("%Y-%m-%d")
    qt = re.sub(r"\s+", " ", q.get_text()).strip()
    links = {}
    for a in tr.find_all("a", href=True):
        lab = a.get_text(" ").strip().lower()
        links[lab] = urljoin(fin, a["href"])
    rows.append(dict(date=date, quarter=qt, **{k: v for k, v in links.items()}))
qr = pd.DataFrame(rows)
qr.to_csv(os.path.join(irlib.raw_dir(T), "qr_table.csv"), index=False)
print(qr.shape, qr.date.min(), qr.date.max())
print(qr.columns.tolist())

fts = pd.read_csv(os.path.join(irlib.raw_dir(T), "edgar_fts_hits.csv"))
fts = fts[fts["query"].str.contains("Financial Results")].drop_duplicates("file_date")
fdates = set(fts.file_date)
today = "2026-10-23"


def qlabel(qt):
    m = re.search(r"Q([1-4])\s*(\d{4})", qt)
    return (int(m.group(1)), int(m.group(2))) if m else (None, None)


ev = []
seen = set()
for _, r in qr.iterrows():
    if r.date > today or r.date < "2015-01-01":
        continue
    q, y = qlabel(r.quarter)
    if not q:
        print("skip", r.quarter)
        continue
    seen.add(r.date)
    ev.append(dict(event_date=r.date, event_time_local="", timing="BMO", event_type=f"Q{q}",
                   fiscal_period=f"FY{y}Q{q}",
                   source_url=r.get("earnings release") or r.get("press release") or
                   "https://investors.st.com/financial-information/quarterly-results"))
# dates in EDGAR FTS but not in the IR table (older years)
from datetime import date as _d
def _near(d, ds, k=3):
    a = _d.fromisoformat(d)
    return any(abs((_d.fromisoformat(x) - a).days) <= k for x in ds)
for d in sorted(fdates - seen):
    if _near(d, seen):
        continue
    m = int(d[5:7])
    q = {1: 4, 2: 4, 4: 1, 5: 1, 7: 2, 8: 2, 10: 3, 11: 3}[m]
    y = int(d[:4]) - (1 if q == 4 else 0)
    adsh = fts[fts.file_date == d].adsh.iloc[0]
    ev.append(dict(event_date=d, event_time_local="", timing="BMO", event_type=f"Q{q}",
                   fiscal_period=f"FY{y}Q{q}",
                   source_url=f"https://www.sec.gov/Archives/edgar/data/932787/{adsh.replace('-', '')}/{adsh}-index.htm"))
evd = pd.DataFrame(ev)
print("table vs fts mismatch:", sorted(set(evd.event_date) ^ fdates)[:20])
# Capital markets days (EDGAR FTS hits + ST press items "to webcast Capital Markets Day")
CMD = [("2018-05-15", "FY2018Q2", "https://www.st.com/content/st_com/en/about/media-center/press-item.html/c2849.html"),
       ("2019-05-14", "FY2019Q2", "https://st.com/content/st_com/en/about/media-center/press-item.html/c2896.html"),
       ("2022-05-12", "FY2022Q2", "https://efts.sec.gov/LATEST/search-index?q=%22Capital%20Markets%20Day%22&ciks=0000932787&forms=6-K"),
       ("2024-11-20", "FY2024Q4", "https://efts.sec.gov/LATEST/search-index?q=%22Capital%20Markets%20Day%22&ciks=0000932787&forms=6-K")]
for d, fp, u in CMD:
    ev.append(dict(event_date=d, event_time_local="", timing="UNKNOWN", event_type="CMD", fiscal_period=fp,
                   source_url=u))
# exact time verified from investors.st.com JSON-LD datePublished (2026-07-23T01:00:27-0400 = 07:00 CEST)
for e in ev:
    if e["event_date"] == "2026-07-23":
        e["event_time_local"] = "07:00"
        e["source_url"] = ("https://investors.st.com/news-releases/news-release-details/"
                           "stmicroelectronics-reports-q2-2026-financial-results")
p, out = irlib.write_events(T, ev)
print(p, len(out), out.event_type.value_counts().to_dict())
