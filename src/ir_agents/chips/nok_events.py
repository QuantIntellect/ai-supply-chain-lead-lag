"""Build NOKIA.HE_events.csv from Nasdaq Nordic exchange notices (exact release times, Helsinki local)."""
import os
import re
import sys
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import irlib  # noqa: E402

T = "NOKIA.HE"
df = pd.read_csv(os.path.join(irlib.raw_dir(T), "nasdaq_news", "nokia_notices.csv"))
df = df[(df.releaseTime >= "2015-01-01") & (df.releaseTime <= "2026-10-23 23:59") & (df.language == "en")]

PERIODIC = {"Interim report (Q1 and Q3)", "Half Year financial report", "Financial Statement Release",
            "Quarterly report"}
rows = []
for _, r in df.iterrows():
    h = str(r.headline).strip()
    if r.category not in PERIODIC and not re.search(r"(Interim|Financial) Report for Q|Report for Q\d", h, re.I):
        continue
    if re.search(r"correction", h, re.I):
        continue
    d, tm = r.releaseTime[:10], r.releaseTime[11:16]
    y, m = int(d[:4]), int(d[5:7])
    q = {1: 4, 2: 4, 3: 4, 4: 1, 5: 1, 7: 2, 8: 2, 10: 3, 11: 3}[m]
    fy = y - 1 if q == 4 else y
    mq = re.search(r"Q([1-4])", h)
    if mq:
        assert int(mq.group(1)) == q, (h, d)
    rows.append(dict(event_date=d, event_time_local=tm, timing=irlib.timing_class(T, tm),
                     event_type=f"Q{q}", fiscal_period=f"FY{fy}Q{q}", source_url=r.messageUrl))

# Non-periodic market-moving releases (identified from the same feed; headline -> type)
SPECIAL = [
    ("2016-11-15", "CMD", "FY2016Q4", "Capital Markets Day 2016"),
    ("2018-07-30", "trading_update", "FY2018Q3", "reiterates its outlook"),
    ("2020-12-16", "trading_update", "FY2020Q4", "mid-point update on strategy"),
    ("2021-03-16", "trading_update", "FY2021Q1", "reset its cost base"),
    ("2021-03-18", "CMD", "FY2021Q1", "speeds up transformation"),
    ("2021-07-13", "trading_update", "FY2021Q3", "revise upwards its 2021 financial guidance"),
    ("2022-01-11", "prelim", "FY2021Q4", "expects to exceed 2021 financial guidance"),
    ("2023-07-14", "profit_warning", "FY2023Q3", "lowers net sales and narrows"),
    ("2023-12-12", "trading_update", "FY2023Q4", "update on group strategy"),
    ("2023-12-30", "profit_warning", "FY2023Q4", "will not achieve its 2023 financial outlook"),
    ("2025-07-22", "profit_warning", "FY2025Q3", "lowers 2025 operating profit guidance"),
    ("2025-11-19", "CMD", "FY2025Q4", "announces new strategy"),
]
for d, et, fp, key in SPECIAL:
    hit = df[(df.releaseTime.str[:10] == d) & df.headline.str.contains(key, case=False, regex=False)]
    assert len(hit) >= 1, (d, key)
    r = hit.sort_values("releaseTime").iloc[0]
    tm = r.releaseTime[11:16]
    rows.append(dict(event_date=d, event_time_local=tm, timing=irlib.timing_class(T, tm), event_type=et,
                     fiscal_period=fp, source_url=r.messageUrl))

p, out = irlib.write_events(T, rows)
print(p, len(out))
print(out.event_type.value_counts().to_dict(), out.timing.value_counts().to_dict())
