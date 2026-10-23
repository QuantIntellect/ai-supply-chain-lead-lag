"""Build data/processed/ir/MTRS.ST_events.csv from the parsed MFN index.

Times are MFN publication timestamps (Europe/Stockholm local), cross-checked
against the MAR "submitted for publication at HH.MM CET" statements.
"""
import os
import sys
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from irlib import RAW_IR, write_events  # noqa: E402

T = "MTRS.ST"
idx = pd.read_csv(os.path.join(RAW_IR, T, "mfn_index.csv"), dtype=str).fillna("")
idx = idx[~idx.title.str.contains("[åäöÅÄÖ]")]  # English versions only

# (date, title substring, event_type, fiscal_period)
SPEC = [
    ("2017-08-15", "", "Q2", "2017Q2"),
    ("2017-11-09", "", "Q3", "2017Q3"),
    ("2017-12-13", "LOWER THAN PREVIOUSLY", "profit_warning", "2017Q4"),
    ("2018-02-16", "", "Q4", "2017Q4"),
    ("2018-04-26", "QUARTER REPORT 2018", "Q1", "2018Q1"),
    ("2018-07-18", "", "Q2", "2018Q2"),
    ("2018-10-25", "INTERIM REPORT", "Q3", "2018Q3"),
    ("2019-02-13", "", "Q4", "2018Q4"),
    ("2019-04-24", "", "Q1", "2019Q1"),
    ("2019-05-09", "Capital Markets Day 2019", "CMD", ""),
    ("2019-07-18", "", "Q2", "2019Q2"),
    ("2019-10-23", "ADDITONAL COSTS", "profit_warning", "2019Q3"),
    ("2019-10-24", "third quarter 2019", "Q3", "2019Q3"),
    ("2020-02-13", "", "Q4", "2019Q4"),
    ("2020-04-23", "", "Q1", "2020Q1"),
    ("2020-07-17", "", "Q2", "2020Q2"),
    ("2020-10-22", "", "Q3", "2020Q3"),
    ("2021-02-04", "", "Q4", "2020Q4"),
    ("2021-04-22", "", "Q1", "2021Q1"),
    ("2021-07-16", "Interim Report", "Q2", "2021Q2"),
    ("2021-10-22", "", "Q3", "2021Q3"),
    ("2022-02-04", "", "Q4", "2021Q4"),
    ("2022-04-22", "", "Q1", "2022Q1"),
    ("2022-07-15", "", "Q2", "2022Q2"),
    ("2022-10-21", "", "Q3", "2022Q3"),
    ("2022-12-08", "Capital Markets Day 2022", "CMD", ""),
    ("2023-02-09", "", "Q4", "2022Q4"),
    ("2023-04-21", "", "Q1", "2023Q1"),
    ("2023-07-18", "Strong growth and margin", "Q2", "2023Q2"),
    ("2023-10-24", "", "Q3", "2023Q3"),
    ("2024-01-22", "preliminary", "prelim", "2023Q4"),
    ("2024-02-01", "", "Q4", "2023Q4"),
    ("2024-04-23", "", "Q1", "2024Q1"),
    ("2024-05-21", "increased net sales growth target", "CMD", ""),
    ("2024-07-17", "strong second quarter", "Q2", "2024Q2"),
    ("2024-10-22", "Strong growth and profits", "Q3", "2024Q3"),
    ("2025-02-05", "", "Q4", "2024Q4"),
    ("2025-04-29", "", "Q1", "2025Q1"),
    ("2025-07-18", "", "Q2", "2025Q2"),
    ("2025-10-24", "Strong performance", "Q3", "2025Q3"),
    ("2026-01-29", "", "Q4", "2025Q4"),
    ("2026-04-28", "", "Q1", "2026Q1"),
    ("2026-07-17", "", "Q2", "2026Q2"),
]

# Events announced in advance but not in the MFN feed as a release item
EXTRA = [
    # Capital Markets Update webcasts (dates/times from MFN invitations)
    {"event_date": "2020-05-28", "event_time_local": "14:00", "event_type": "CMD",
     "fiscal_period": "", "source_url": "https://www.mfn.se/cis/a/munters-group/"
     "munters-group-ab-invitation-to-munters-capital-markets-update-d12e6c38"},
    {"event_date": "2021-05-11", "event_time_local": "14:00", "event_type": "CMD",
     "fiscal_period": "", "source_url": "https://www.mfn.se/cis/a/munters-group/"
     "munters-group-ab-save-the-date-munters-capital-markets-update-50b8db34"},
]


def morning(s):
    return s[(s.time >= "06:00") & (s.time <= "08:10")]


def build(extra_scheduled=None):
    rows = []
    for d, key, et, fp in SPEC:
        s = idx[idx.date == d]
        if key:
            s = s[s.title.str.contains(key, case=False, regex=False)]
        else:
            s = morning(s)
        if len(s) == 0:
            raise SystemExit(f"missing {d} {key}")
        r = s.sort_values("time").iloc[0]
        rows.append({"event_date": d, "event_time_local": r.time[:5],
                     "event_type": et, "fiscal_period": fp, "source_url": r.url})
    rows += [dict(x) for x in EXTRA]
    if extra_scheduled:
        rows += extra_scheduled
    return rows


if __name__ == "__main__":
    sched = [{
        # Announced in the 2026-10-09 invitation: "On October 23, at 07.30 CEST,
        # Munters will release the interim report for the third quarter of 2026."
        "event_date": "2026-10-23", "event_time_local": "07:30", "event_type": "Q3",
        "fiscal_period": "2026Q3",
        "source_url": "https://www.mfn.se/cis/a/munters-group/munters-group-ab-"
        "invitation-to-presentation-of-munters-report-for-the-third-quarter-2026-902677d3"}]
    rows = build(sched)
    p = write_events(T, rows)
    df = pd.read_csv(p)
    print(p, len(df), df.event_date.min(), df.event_date.max())
    print(df.groupby(df.event_date.str[:4]).size().to_dict())
    print(df.timing.value_counts().to_dict())
