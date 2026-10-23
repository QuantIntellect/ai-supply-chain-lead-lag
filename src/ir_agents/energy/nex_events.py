"""Nexans release calendar 2015-2026 with GlobeNewswire / Euronext timestamps."""
import sys, csv, re, os
from datetime import datetime
sys.path.insert(0, "/Users/sinamirzaei/Documents/aimapping/src/ir_agents/energy"); import irlib

T = "NEX.PA"
# (local date, event_type, fiscal_period, title regex used to pick the stamped wire item)
EVENTS = [
    ("2015-02-13", "FY", "FY2014", r"2014 Full-Year Results"),
    ("2015-04-28", "Q1", "FY2015Q1", r"First-Quarter"), ("2015-07-29", "H1", "FY2015H1", r"First-Half"),
    ("2015-10-16", "Q3", "FY2015Q3", r"Third-Quarter"), ("2016-01-26", "prelim", "FY2015", r"Net debt and asset impairments"),
    ("2016-02-18", "FY", "FY2015", r"FULL-YEAR"),
    ("2016-05-03", "Q1", "FY2016Q1", r"FIRST-QUARTER"), ("2016-07-28", "H1", "FY2016H1", r"FIRST-HALF"),
    ("2016-11-04", "Q3", "FY2016Q3", r"Third-Quarter"), ("2017-02-09", "FY", "FY2016", r"FULL-YEAR"),
    ("2017-05-03", "Q1", "FY2017Q1", r"FIRST-QUARTER"), ("2017-07-27", "H1", "FY2017H1", r"FIRST-HALF"),
    ("2017-11-07", "Q3", "FY2017Q3", r"THIRD-QUARTER"), ("2017-12-13", "CMD", "FY2017", r"Strategic Plan"),
    ("2018-02-15", "FY", "FY2017", r"FULL-YEAR"),
    ("2018-05-03", "Q1", "FY2018Q1", r"FIRST QUARTER"), ("2018-07-26", "H1", "FY2018H1", r"FIRST HALF"),
    ("2018-11-09", "Q3", "FY2018Q3", r"(Third quarter|troisième trimestre)"), ("2018-11-09", "CMD", "FY2018", r"value delivery model"),
    ("2019-02-14", "FY", "FY2018", r"FULL-YEAR"),
    ("2019-05-02", "Q1", "FY2019Q1", r"FIRST QUARTER"), ("2019-07-24", "H1", "FY2019H1", r"First Half 2019"),
    ("2019-11-07", "Q3", "FY2019Q3", r"THIRD QUARTER"), ("2020-02-20", "FY", "FY2019", r"2019 FINANCIAL INFORMATION"),
    ("2020-03-24", "profit_warning", "FY2020", r"Update on Covid-19"),
    ("2020-05-07", "Q1", "FY2020Q1", r"first quarter"), ("2020-07-29", "H1", "FY2020H1", r"Robust performance"),
    ("2020-11-05", "Q3", "FY2020Q3", r"Q3 2020"), ("2021-02-17", "FY", "FY2020", r"steered for growth"),
    ("2021-02-17", "CMD", "FY2021", r"ELECTRIFICATION PURE PLAYER"),
    ("2021-04-29", "Q1", "FY2021Q1", r"HEAD START"), ("2021-07-28", "H1", "FY2021H1", r"Structural Value Growth"),
    ("2021-11-03", "Q3", "FY2021Q3", r"Selective growth"), ("2022-02-16", "FY", "FY2021", r"Successful Turnaround"),
    ("2022-04-27", "Q1", "FY2022Q1", r"strong start to the year"), ("2022-07-27", "H1", "FY2022H1", r"H1 2022"),
    ("2022-10-26", "Q3", "FY2022Q3", r"CONTINUED STRONG MOMENTUM"), ("2023-02-15", "FY", "FY2022", r"A RECORD YEAR"),
    ("2023-04-26", "Q1", "FY2023Q1", r"Value-Driven Growth Model"), ("2023-07-26", "H1", "FY2023H1", r"H1 2023"),
    ("2023-10-25", "Q3", "FY2023Q3", r"9M 2023"), ("2024-02-15", "FY", "FY2023", r"ROBUST PERFORMANCE IN 2023"),
    ("2024-04-24", "Q1", "FY2024Q1", r"First quarter 2024"), ("2024-07-24", "H1", "FY2024H1", r"H1 2024"),
    ("2024-10-30", "Q3", "FY2024Q3", r"9M 2024"), ("2024-11-13", "CMD", "FY2024", r"2028 ambition"),
    ("2025-02-19", "FY", "FY2024", r"record-breaking performance"),
    ("2025-04-30", "Q1", "FY2025Q1", r"Q1 2025"), ("2025-07-30", "H1", "FY2025H1", r"H1 2025"),
    ("2025-10-23", "Q3", "FY2025Q3", r"9M 2025"),
    ("2025-12-22", "trading_update", "FY2025", r"Autoelectric"),  # FY2025 guidance re-based to continuing ops
    ("2026-02-19", "FY", "FY2025", r"2025 Full-Year results"),
    ("2026-04-28", "Q1", "FY2026Q1", r"Q1 2026"), ("2026-07-29", "H1", "FY2026H1", r"2026 Half-year results"),
    ("2026-10-22", "Q3", "FY2026Q3", r"9M 2026"),
]


def load_wire():
    items = []
    for r in irlib.read_csv(os.path.join(irlib.RAW_IR, T, "globenewswire_list.csv")):
        d = datetime.strptime(r["listed"].replace(" ET", ""), "%B %d, %Y %H:%M")
        ld, lt = irlib.to_local(d.strftime("%Y-%m-%d %H:%M"), "America/New_York", T)
        items.append(("GNW", ld, lt, r["title"], r["url"]))
    for r in irlib.read_csv(os.path.join(irlib.RAW_IR, T, "euronext_press_list.csv")):
        m = re.match(r"(\d{2} \w{3} \d{4}) (\d{2}:\d{2}) (CET|CEST)", r["released"])
        if not m:
            continue
        ld = datetime.strptime(m.group(1), "%d %b %Y").strftime("%Y-%m-%d")
        items.append(("ENX", ld, m.group(2), r["title"], r["href"] or "https://live.euronext.com/en/listview/company-press-release/092642"))
    return items


def main():
    wire = load_wire()
    out, issues = [], []
    for d, et, fp, pat in EVENTS:
        hits = [w for w in wire if w[1] == d and re.search(pat, w[3], re.I)]
        gnw = [w for w in hits if w[0] == "GNW" and "/0/en/" in w[4]] or [w for w in hits if w[0] == "GNW"]
        enx = [w for w in hits if w[0] == "ENX"]
        best = (gnw or enx or [None])[0]
        if best is None:
            issues.append((d, et, "NO STAMP"))
            out.append({"event_date": d, "event_time_local": "", "timing": "UNKNOWN", "event_type": et,
                        "fiscal_period": fp, "source_url": ""})
            continue
        times = sorted({w[2] for w in hits})
        if len(times) > 1:
            issues.append((d, et, "times differ " + ",".join(times)))
        out.append({"event_date": d, "event_time_local": min(w[2] for w in hits), "event_type": et,
                    "fiscal_period": fp, "source_url": best[4]})
    irlib.write_events(T, out)
    for i in issues:
        print("  ", i)


if __name__ == "__main__":
    main()
