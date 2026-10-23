"""Shared helpers for the RR.L (Rolls-Royce) IR collection scripts."""
import sys; sys.path.insert(0, "/Users/sinamirzaei/Documents/aimapping/src/ir_agents/energy"); import irlib
import csv, os, re
from datetime import datetime

TICKER = "RR.L"
INDEX = os.path.join(irlib.RAW_IR, TICKER, "_investegate_index.csv")
SCR = "/private/tmp/claude-501/-Users-sinamirzaei-Documents-aimapping/57e0a0d0-6441-40ef-828b-57eeb87e7b21/scratchpad/rr"

# (date, exact Investegate headline, event_type or None (=not a calendar event / to check),
#  fiscal_period, doc_type)
CANDIDATES = [
    ("2015-02-13", "Full Year 2014 Final Results", "FY", "FY2014", "press_release"),
    ("2015-05-08", "Interim Management Statement", "trading_update", "FY2015Q1", "trading_update"),
    ("2015-07-06", "Rolls-Royce Guidance Update", "CHECK", "", "trading_update"),
    ("2015-07-30", "Rolls-Royce Holdings plc Half Year Results", "H1", "FY2015H1", "press_release"),
    ("2015-09-18", "ROLLS-ROYCE PROVIDES DATES FOR Q4 IR EVENTS", "CHECK", "", "other"),
    ("2015-11-12", "Interim Management Statement", "CHECK", "FY2015Q3", "trading_update"),
    ("2015-11-24", "Rolls-Royce presents operations review update", "CHECK", "", "other"),
    ("2016-02-12", "Rolls-Royce Holdings plc FY Results", "FY", "FY2015", "press_release"),
    ("2016-04-05", "AGM Statement", "CHECK", "", "other"),
    ("2016-05-05", "Rolls-Royce Holdings plc AGM Statement", "trading_update", "FY2016Q1", "trading_update"),
    ("2016-06-28", "Pre-close Statement", "trading_update", "FY2016Q2", "trading_update"),
    ("2016-07-28", "ROLLS-ROYCE HOLDINGS PLC 2016 HALF YEAR RESULTS", "H1", "FY2016H1", "press_release"),
    ("2016-11-16", "Trading Statement", "trading_update", "FY2016Q3", "trading_update"),
    ("2017-02-14", "Rolls-Royce 2016 Full Year Results", "FY", "FY2016", "press_release"),
    ("2017-05-04", "Rolls-Royce Holdings plc AGM Statement", "trading_update", "FY2017Q1", "trading_update"),
    ("2017-06-16", "Paris Airshow and Pre-Close Statement", "trading_update", "FY2017Q2", "trading_update"),
    ("2017-08-01", "Rolls-Royce Holdings plc 2017 Half Year Results", "H1", "FY2017H1", "press_release"),
    ("2017-11-09", "Rolls-Royce confirms trading outlook unchanged", "trading_update", "FY2017Q3", "trading_update"),
    ("2018-03-07", "2017 Full Year Results", "FY", "FY2017", "press_release"),
    ("2018-04-13", "Trent 1000 Package C Update", "CHECK", "", "other"),
    ("2018-04-20", "Notice of Capital Markets Event & 2018 HY Results", "CHECK", "", "other"),
    ("2018-05-03", "Rolls-Royce Holdings plc AGM Statement", "trading_update", "FY2018Q1", "trading_update"),
    ("2018-06-11", "Trent 1000 Service Management Update", "CHECK", "", "other"),
    ("2018-06-14", "Rolls-Royce Confirms Fundamental Restructuring", "CHECK", "", "other"),
    ("2018-06-15", "Rolls-Royce Outlines Mid-Term Ambition", "CHECK", "", "other"),
    ("2018-08-02", "2018 Half Year Results", "H1", "FY2018H1", "press_release"),
    ("2018-10-26", "STATEMENT re TRENT 7000. FY GUIDANCE CONFIRMED", "CHECK", "FY2018Q3", "trading_update"),
    ("2018-12-12", "Trading Update - Full Year Guidance Confirmed", "trading_update", "FY2018Q4", "trading_update"),
    ("2019-02-28", "2018 Full Year Results", "FY", "FY2018", "press_release"),
    ("2019-04-10", "Trent 1000 TEN Service Management", "CHECK", "", "other"),
    ("2019-05-02", "Trading Update: On Track to Deliver", "trading_update", "FY2019Q1", "trading_update"),
    ("2019-08-06", "2019 Half Year Results", "H1", "FY2019H1", "press_release"),
    ("2019-09-20", "TRENT 1000 UPDATE", "CHECK", "", "other"),
    ("2019-11-07", "Trading and Trent 1000 Update", "trading_update", "FY2019Q3", "trading_update"),
    ("2020-02-28", "2019 Full Year Results", "FY", "FY2019", "press_release"),
    ("2020-04-06", "Trading Update", "CHECK", "FY2020Q1", "trading_update"),
    ("2020-05-07", "AGM Statement", "trading_update", "FY2020Q1", "trading_update"),
    ("2020-05-20", "Rolls-Royce Proposes Major Reorganisation", "CHECK", "", "other"),
    ("2020-07-09", "H1 Trading Update", "trading_update", "FY2020Q2", "trading_update"),
    ("2020-08-27", "2020 Half Year Results", "H1", "FY2020H1", "press_release"),
    ("2020-10-01", "Proposed Recapitalisation", "CHECK", "FY2020Q3", "trading_update"),
    ("2020-12-04", "Notice of Trading Update", "CHECK", "", "other"),
    ("2020-12-11", "Trading Update", "trading_update", "FY2020Q4", "trading_update"),
    ("2021-01-26", "Trading Update", "CHECK", "FY2020Q4", "trading_update"),
    ("2021-03-11", "2020 Full Year Results", "FY", "FY2020", "press_release"),
    ("2021-05-13", "AGM Statement", "trading_update", "FY2021Q1", "trading_update"),
    ("2021-08-05", "2021 Half Year Results", "H1", "FY2021H1", "press_release"),
    ("2021-11-23", "Notice of Trading Update and Conference Call", "CHECK", "", "other"),
    ("2021-12-09", "Trading Update", "trading_update", "FY2021Q4", "trading_update"),
    ("2022-02-24", "2021 Full Year Results", "FY", "FY2021", "press_release"),
    ("2022-05-06", "Civil Aerospace Investor Day - 13 May 2022", "CHECK", "", "other"),
    ("2022-05-12", "AGM Statement and Trading Update", "trading_update", "FY2022Q1", "trading_update"),
    ("2022-08-04", "2022 Half Year Results", "H1", "FY2022H1", "press_release"),
    ("2022-11-03", "Trading Statement", "trading_update", "FY2022Q3", "trading_update"),
    ("2023-02-23", "2022 Full Year Results", "FY", "FY2022", "press_release"),
    ("2023-05-11", "AGM Statement and Trading Update", "trading_update", "FY2023Q1", "trading_update"),
    ("2023-07-26", "Trading Update", "trading_update", "FY2023Q2", "trading_update"),
    ("2023-08-03", "2023 Half Year Results", "H1", "FY2023H1", "press_release"),
    ("2023-10-17", "Rolls-Royce creates more efficient organisation", "CHECK", "", "other"),
    ("2023-11-28", "Capital Markets Day", "CMD", "", "press_release"),
    ("2024-02-22", "Full Year Results 2023", "FY", "FY2023", "press_release"),
    ("2024-02-29", "AGM Statement", "CHECK", "", "other"),
    ("2024-05-23", "AGM Statement and Trading Update", "trading_update", "FY2024Q1", "trading_update"),
    ("2024-05-23", "Notice of Results", "CHECK", "", "other"),
    ("2024-08-01", "2024 Half Year Results", "H1", "FY2024H1", "press_release"),
    ("2024-11-07", "Trading Update", "trading_update", "FY2024Q3", "trading_update"),
    ("2025-02-27", "Full Year Results 2024", "FY", "FY2024", "press_release"),
    ("2025-03-06", "AGM Statement", "CHECK", "", "other"),
    ("2025-05-01", "AGM Statement and Trading Update", "trading_update", "FY2025Q1", "trading_update"),
    ("2025-07-31", "2025 Half Year Results", "H1", "FY2025H1", "press_release"),
    ("2025-11-13", "Trading Update", "trading_update", "FY2025Q3", "trading_update"),
    ("2026-02-26", "Full Year Results 2025", "FY", "FY2025", "press_release"),
    ("2026-04-30", "AGM Statement and Trading Update", "trading_update", "FY2026Q1", "trading_update"),
    ("2026-07-30", "2026 Half Year Results", "H1", "FY2026H1", "press_release"),
]


def load_index():
    rows = []
    with open(INDEX, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            d = datetime.strptime(r["date_disp"], "%d %b %Y")
            t = datetime.strptime(r["time_disp"], "%I:%M %p").strftime("%H:%M") if r["time_disp"] else ""
            r["date"] = d.strftime("%Y-%m-%d")
            r["hhmm"] = t
            r["rns_id"] = r["url"].rstrip("/").split("/")[-1]
            rows.append(r)
    return rows


def find(index, date, headline):
    hits = [r for r in index if r["date"] == date and r["headline"] == headline]
    if len(hits) != 1:
        raise ValueError(f"{date} {headline}: {len(hits)} hits")
    return hits[0]


def body_html(full_html: str, header: str) -> str:
    """Keep only the announcement body (Investegate 'news-window' div); drop site chrome and
    Investegate's AI summary."""
    from bs4 import BeautifulSoup
    s = BeautifulSoup(full_html, "html.parser")
    nw = s.find("div", class_="news-window")
    inner = str(nw) if nw else full_html
    return f"<html><body><p>{header}</p>\n{inner}\n</body></html>"
