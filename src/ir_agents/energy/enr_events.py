"""Siemens Energy (ENR.DE) release calendar -> data/processed/ir/ENR.DE_events.csv

Sources:
  * results dates: IR 'Publications & Ad hoc' page accordion titles (e.g. 'Q3 FY2026 Financial Results | Berlin | August 5, 2026')
  * ad-hoc times: EQS News datelines ('22-Jun-2023 / 19:22 CET/CEST') through 2024-08; pressetext (pta) datelines
    ('pta030/12.11.2024/19:37 UTC+1' = local CET/CEST wall-clock) from 2024-11. Both are already Europe/Berlin local time.
  * results-release clock times: see TIMES below (evidence documented in ENR.DE_notes.md)
"""
import sys; sys.path.insert(0, "/Users/sinamirzaei/Documents/aimapping/src/ir_agents/energy"); import irlib
import re

T = "ENR.DE"
PUB = "https://www.siemens-energy.com/global/en/home/investor-relations/publications-ad-hoc.html"
EQS = "https://www.eqs-news.com/news/ad-hoc/"
PTA = "https://www.pressetext.com/news/"

# (date, type, fiscal_period) for regular results publications (dates from the IR publications page)
RESULTS = [
    ("2020-11-10", "FY", "FY2020"), ("2021-02-02", "Q1", "FY2021Q1"), ("2021-05-05", "Q2", "FY2021Q2"),
    ("2021-08-04", "Q3", "FY2021Q3"), ("2021-11-10", "FY", "FY2021"), ("2022-02-09", "Q1", "FY2022Q1"),
    ("2022-05-11", "Q2", "FY2022Q2"), ("2022-08-08", "Q3", "FY2022Q3"), ("2022-11-16", "FY", "FY2022"),
    ("2023-02-07", "Q1", "FY2023Q1"), ("2023-05-15", "Q2", "FY2023Q2"), ("2023-08-07", "Q3", "FY2023Q3"),
    ("2023-11-15", "FY", "FY2023"), ("2024-02-07", "Q1", "FY2024Q1"), ("2024-05-08", "Q2", "FY2024Q2"),
    ("2024-08-07", "Q3", "FY2024Q3"), ("2024-11-12", "FY", "FY2024"), ("2025-02-12", "Q1", "FY2025Q1"),
    ("2025-05-08", "Q2", "FY2025Q2"), ("2025-08-06", "Q3", "FY2025Q3"), ("2025-11-13", "FY", "FY2025"),
    ("2026-02-11", "Q1", "FY2026Q1"), ("2026-05-12", "Q2", "FY2026Q2"), ("2026-08-05", "Q3", "FY2026Q3"),
]
# event-specific timing evidence for results releases: date -> (HH:MM or "", timing, source_url)
TIMES = {
    # pta 'Business news': "Siemens Energy achieves all annual goals ... Please see attached the Earnings Release Q4 FY 2024"
    "2024-11-12": ("19:44", "", PTA + "20241112031"),
    # pta ad-hoc 21:15 CET: "Siemens Energy AG will publish its full earnings release for the fourth quarter of FY2025 today"
    "2025-11-13": ("", "AMC", PTA + "20251113030"),
}
CMDS = [  # IR page 'Events & Conferences' accordion titles
    ("2020-09-01", "Capital Markets Day | Munich | September 1, 2020 (pre-listing)"),
    ("2022-05-24", "Capital Market Day | Berlin | May 24, 2022"),
    ("2023-11-21", "Capital Market Day 2023 | Hamburg | November 21, 2023"),
    ("2025-11-20", "Capital Market Day | November 20, 2025"),
]
# CMD start times from the published agendas (local time)
CMD_TIMES = {
    "2020-09-01": ("12:00", "", "https://assets.siemens-energy.com/siemens/assets/api/uuid:2d8e8b0e/200901+CMD+Siemens+Energy+Agenda"),
    "2022-05-24": ("09:00", "", None),
    "2023-11-21": ("13:00", "", None),
}

# Ad-hoc (Art. 17 MAR) announcements with results/guidance content (EQS / pressetext datelines, local time)
ADHOC = [
    ("2021-01-24", "20:20", "prelim", "FY2021Q1", EQS + "siemens-energy-ag-siemens-energy-ag-announces-preliminary-results-for-first-quarter-of-fiscal-year-2021-and-confirms-its-outlook-for-fiscal-year-2021/755130c0"),
    ("2021-07-14", "23:22", "profit_warning", "FY2021", EQS + "siemens-energy-ag-siemens-gamesa-renewable-energy-s-a-lowers-outlook-for-fiscal-year-2021-impacting-siemens-energy/2fad60a0-2bfd-4b05-a55e-f4258b1a280e_en"),
    ("2022-01-20", "21:08", "profit_warning", "FY2022", EQS + "siemens-energy-ag-ad-hoc-announcement/9971443b-4b83-44b2-8b62-e3b2cecae4a2_en"),
    ("2022-04-19", "22:00", "profit_warning", "FY2022", EQS + "siemens-energy-ag-ad-hoc-announcement/98c4eea5-f932-44fa-a824-c760e6597b6f_en"),
    ("2023-01-19", "19:56", "profit_warning", "FY2023", None),
    ("2023-06-22", "19:22", "profit_warning", "FY2023", None),
    ("2023-10-26", "10:41", "trading_update", "FY2023Q4", EQS + "siemens-energy-ag-siemens-energy-comments-on-media-reports/c4d11d9c-7040-4ced-a0cb-cd158afb3b84_en"),
    ("2024-01-23", "19:31", "prelim", "FY2024Q1", None),
    ("2024-11-12", "19:37", "trading_update", "FY2024Q4", PTA + "20241112030"),
    ("2025-01-27", "19:40", "prelim", "FY2025Q1", PTA + "20250127029"),
    ("2025-04-16", "19:25", "trading_update", "FY2025Q2", PTA + "20250416026"),
    ("2025-11-13", "21:15", "trading_update", "FY2025Q4", PTA + "20251113030"),
    ("2026-04-23", "17:55", "trading_update", "FY2026Q2", PTA + "20260423027"),
]


def eqs_urls():
    """full EQS URLs from the scraped EQS list (scratch TSV) keyed by local date."""
    import os, datetime as dt
    p = "/private/tmp/claude-501/-Users-sinamirzaei-Documents-aimapping/57e0a0d0-6441-40ef-828b-57eeb87e7b21/scratchpad/enr/eqs_adhoc_detail.tsv"
    out = {}
    if os.path.exists(p):
        for line in open(p):
            dgrp, shown, dl, title, url, rel = line.rstrip("\n").split("\t")
            d = dt.datetime.strptime(dgrp, "%d %B %Y").strftime("%Y-%m-%d")
            out.setdefault(d, []).append((shown, url))
    return out


def er_urls():
    """fiscal_period -> earnings-release PDF URL (from the manifest); agenda URLs for CMDs."""
    out, ag = {}, {}
    for r in irlib.read_csv(f"data/processed/ir/{T}_manifest.csv"):
        if r["doc_type"] == "press_release" and re.search(r"earnings|ER_E|ER-E", r["local_path"], re.I) and "pta_" not in r["local_path"]:
            out.setdefault(r["fiscal_period"], r["url"])
        if "Agenda" in r["local_path"]:
            ag[r["pub_date"]] = r["url"]
    return out, ag


def build():
    import re as _re
    rows = []
    ers, agendas = er_urls()
    for d, et, fp in RESULTS:
        # Every regular earnings release states a same-day press conference call before the 09:00 Xetra open
        # ("...starting at 8:30 a.m. CET today"; 8 a.m. FY2021Q1, 7:15 a.m. FY2023Q1, 9 a.m. FY2020) -> BMO, time unknown.
        TIMES.setdefault(d, ("", "BMO", ers.get(fp, PUB)))
    for d, (hh, tm, u) in list(CMD_TIMES.items()):
        CMD_TIMES[d] = (hh, tm, agendas.get(d, u or PUB))
    for d, et, fp in RESULTS:
        hhmm, timing, url = TIMES.get(d, ("", "UNKNOWN", PUB))
        rows.append(dict(event_date=d, event_time_local=hhmm, timing=timing or None, event_type=et,
                         fiscal_period=fp, source_url=url))
    for d, _ in CMDS:
        hhmm, timing, url = CMD_TIMES.get(d, ("", "UNKNOWN", PUB))
        rows.append(dict(event_date=d, event_time_local=hhmm, timing=timing, event_type="CMD",
                         fiscal_period="", source_url=url))
    eq = eqs_urls()
    for d, hhmm, et, fp, url in ADHOC:
        if d in eq:  # prefer exact EQS URL matched on local date + time
            for shown, u in eq[d]:
                if shown == hhmm:
                    url = u
        assert url, d
        rows.append(dict(event_date=d, event_time_local=hhmm, timing=None, event_type=et, fiscal_period=fp,
                         source_url=url))
    return rows


if __name__ == "__main__":
    rows = build()
    irlib.write_events(T, rows)
    import collections
    ev = irlib.read_csv(f"data/processed/ir/{T}_events.csv")
    print(collections.Counter(r["timing"] for r in ev), collections.Counter(r["event_type"] for r in ev))
    print(ev[0]["event_date"], "->", ev[-1]["event_date"])
