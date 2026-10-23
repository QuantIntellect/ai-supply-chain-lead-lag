"""Infineon events: quarterly releases (IR press list JSON 2021-11..2026-08; Yahoo dates for 2015-2021, which
match the IR list 20/20 in the overlap), ad-hoc releases with time from Infineon's ad-hoc PDF names, CMD."""
import os
import sys
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import irlib  # noqa: E402

T = "IFX.DE"
pl = pd.read_csv(os.path.join(irlib.raw_dir(T), "press_list.csv"))
pl["d"] = pd.to_datetime(pl.articlePublishFormattedDate, format="%b %d, %Y").dt.strftime("%Y-%m-%d")
qr = pl[pl.articleType.eq("Quarterly Report") | pl.articleTitle.str.contains(
    r"Q[1-4] FY|fiscal year|June quarter", case=False, regex=True) & pl.d.isin(
    ["2023-08-03", "2023-11-15", "2024-02-06"])]
qr = qr[~qr.articleUrl.str.contains("202308-140")]
y = pd.read_parquet(os.path.join(irlib.ROOT, "data", "processed", "yahoo_earnings_dates.parquet"))
y = y[(y.ticker == T)]
yd = sorted(set(y.earn_ts_utc.astype(str).str[:10]))
yd = [d for d in yd if "2015-01-01" <= d < "2021-10-01"]


def fq(d):
    """Infineon FY ends 30 Sep: release month -> (fiscal quarter, fiscal year)."""
    yy, m = int(d[:4]), int(d[5:7])
    if m in (1, 2, 3):
        return 1, yy
    if m in (4, 5, 6):
        return 2, yy
    if m in (7, 8, 9):
        return 3, yy
    return 4, yy  # Nov/Dec release = Q4 of FY ending Sep same year


TIMED = {}  # date -> HH:MM where a document states it (filled by ifx_docs.py later if verified)
ev = []
for d in yd:
    q, fy = fq(d)
    ev.append(dict(event_date=d, event_time_local="", timing="UNKNOWN", event_type=f"Q{q}",
                   fiscal_period=f"FY{fy}Q{q}",
                   source_url="https://finance.yahoo.com/quote/IFX.DE/ (earnings date; no time)"))
for _, r in qr.iterrows():
    q, fy = fq(r.d)
    ev.append(dict(event_date=r.d, event_time_local="", timing="UNKNOWN", event_type=f"Q{q}",
                   fiscal_period=f"FY{fy}Q{q}", source_url="https://www.infineon.com" + r.articleUrl))
AH = "https://www.infineon.com/assets/row/public/documents/corporate/investors/ad-hoc-news/"
ADHOC = [  # (date, time, type, fiscal period, file) -- results/guidance-relevant ad-hocs only
    ("2019-03-27", "14:36", "profit_warning", "FY2019Q2", "2019-ifx-ad-hoc-27-march-2019-14-36-uhr-v01-00-en.pdf"),
    ("2020-03-26", "13:30", "profit_warning", "FY2020Q2", "2020-ifx-ad-hoc-26-march-2020-13-30-uhr-v01-00-en.pdf"),
    ("2020-05-04", "20:59", "profit_warning", "FY2020Q2", "2020-ifx-ad-hoc-4-may-2020-20-59-uhr-v01-00-en.pdf"),
    ("2023-03-28", "18:31", "prelim", "FY2023Q2", "2023-ifx-ad-hoc-28-march-2023-18-31-uhr-v01-00-en.pdf"),
]
for d, tm, et, fp, f in ADHOC:
    ev.append(dict(event_date=d, event_time_local=tm, timing=irlib.timing_class(T, tm), event_type=et,
                   fiscal_period=fp, source_url=AH + f))
ev.append(dict(event_date="2021-10-05", event_time_local="", timing="UNKNOWN", event_type="CMD",
               fiscal_period="FY2022Q1", source_url="https://www.infineon.com/press-release/2021/infxx202110-002"))
# Releases whose own text announces a same-day press/analyst conference at 08:00 CET/CEST (before the 09:00
# Xetra open) must have been published before 08:00 -> BMO (time itself not stated, left blank).
BMO_BY_CALL = {"FY2024Q2", "FY2024Q3", "FY2024Q4", "FY2025Q1", "FY2025Q2", "FY2026Q1", "FY2026Q2", "FY2026Q3"}
for e in ev:
    if e["fiscal_period"] in BMO_BY_CALL and e["event_type"].startswith("Q"):
        e["timing"] = "BMO"
p, out = irlib.write_events(T, ev)
print(p, len(out), out.event_type.value_counts().to_dict())
