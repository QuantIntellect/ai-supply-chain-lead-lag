"""Build data/processed/ir/CAP.PA_events.csv from scraped Capgemini calendar/event pages + timing evidence.

Timing evidence hierarchy:
 1. 2019-07 onward: publication timestamp shown on investors.capgemini.com (Paris local time).
 2. 2016-10 .. 2019-04: conference-call time stated in the press release itself
    ('call ... today at 8 a.m.' => BMO; 'today at 6/6.30 p.m.' => AMC); HH:MM only when the
    calendar time is consistent with that evidence.
 3. 2015-02 .. 2016-07: timestamp of the first CercleFinance/BFM news item on tradingsat.com
    (upper bound on release time; all before 08:15 => BMO). HH:MM left blank.
 Calendar 'Starts at 10:00 am' for pre-2019 events is a site default and is ignored.
"""
import sys, os, re, json, csv
sys.path.insert(0, os.path.dirname(__file__))
import fetch_util as fu
import cap_util as cu

T = "CAP.PA"
RAW = os.path.join(fu.RAW_IR, T)
OUT = os.path.join(fu.PROC_IR, "%s_events.csv" % T)
EV = "https://investors.capgemini.com/en/event/%s/"
PUB = "https://investors.capgemini.com/en/publication/%s/"

# (date, time_local, timing, event_type, fiscal_period, source_url)
MANUAL = [
    ("2015-02-19", "", "BMO", "FY", "2014FY", EV % "fy-2014-results"),          # CercleFinance 07:57
    ("2015-04-27", "", "BMO", "Q1", "2015Q1", EV % "q1-2015-revenues"),         # CercleFinance 07:37 (with IGATE deal)
    ("2015-05-28", "", "UNKNOWN", "CMD", "2015CMD", EV % "2015-capital-market-day"),
    ("2015-07-30", "", "BMO", "H1", "2015H1", EV % "h1-2015-results"),          # CercleFinance/Reuters 08:12
    ("2015-10-29", "", "UNKNOWN", "Q3", "2015Q3", EV % "q3-2015-revenues"),
    ("2016-02-18", "", "BMO", "FY", "2015FY", EV % "fy-2015-results"),          # CercleFinance 08:01
    ("2016-04-27", "", "BMO", "Q1", "2016Q1", EV % "q1-2016-revenues"),         # CercleFinance 07:52
    ("2016-06-01", "", "UNKNOWN", "CMD", "2016CMD", EV % "2016-capital-market-day"),
    ("2016-07-27", "", "BMO", "H1", "2016H1", EV % "h1-2016-results"),          # CercleFinance 08:11
    ("2016-10-26", "", "BMO", "Q3", "2016Q3", PUB % "q3-2016-revenues-revenues"),  # call 8:30 a.m.
    ("2017-02-16", "", "BMO", "FY", "2016FY", PUB % "fy-2016-results"),         # call 8 a.m.
    ("2017-04-26", "", "BMO", "Q1", "2017Q1", PUB % "q1-2017-revenues"),        # call 8 a.m.
    ("2017-07-27", "", "BMO", "H1", "2017H1", PUB % "2017-h1-results"),         # call 8 a.m.
    ("2017-09-12", "", "UNKNOWN", "CMD", "2017CMD", PUB % "2017-capital-market-day"),
    ("2017-10-25", "07:00", "BMO", "Q3", "2017Q3", PUB % "q3-2017-revenues"),   # calendar 7:00, call 8 a.m.
    ("2018-02-15", "", "BMO", "FY", "2017FY", PUB % "fy-2017-results"),         # call 8 a.m. (calendar 5:40 pm inconsistent)
    ("2018-04-26", "17:40", "AMC", "Q1", "2018Q1", PUB % "q1-2018-revenues"),   # call 6.30 p.m.
    ("2018-07-26", "", "AMC", "H1", "2018H1", PUB % "2018-h1-results"),         # call 6.30 p.m.
    ("2018-10-24", "17:40", "AMC", "Q3", "2018Q3", PUB % "q3-2018-revenues"),   # call 6 p.m.
    ("2018-10-30", "", "UNKNOWN", "CMD", "2018CMD", PUB % "2018-capital-markets-day"),
    ("2019-02-14", "07:00", "BMO", "FY", "2018FY", PUB % "fy-2018-results"),    # call 8.00 a.m.
    ("2019-04-25", "17:45", "AMC", "Q1", "2019Q1", PUB % "capgemini-revenue-growth-of-6-7-in-q1-2019"),  # call 6 p.m.
    ("2020-07-28", "18:45", "AMC", "prelim", "2020H1", PUB % "h1-2020-estimated-results"),
]

def main():
    cards = json.load(open(os.path.join(RAW, "event_cards.json")))
    rows = []
    manual_fp = {(m[3], m[4]) for m in MANUAL}
    # scheduled results events from 2019-07 onward: use the press-release card time
    evs = json.load(open(os.path.join(RAW, "event_pages.json")))
    for e in evs:
        slug = e["url"].rstrip("/").split("/")[-1]
        et, fp = cu.event_period(slug)
        is_cmd = "capital-market" in slug
        if not et and not is_cmd:
            continue
        if is_cmd:
            et, fp = "CMD", re.search(r"(\d{4})", slug).group(1) + "CMD"
        if (et, fp) in manual_fp:
            continue
        prs = [c for c in cards if c["event_slug"] == slug and (c["type"] or "").lower().startswith("press")
               and "notice" not in (c["title"] or "").lower()]
        d = None; tm = ""; src = e["url"]
        m0 = re.search(r"(\w+ \d{1,2}, \d{4})", e["card_text"])
        cal_d = cu.to_iso(m0.group(1)) if m0 else None
        same = [c for c in prs if cu.to_iso(c["date"]) == cal_d]
        if same:
            prs = same
        if prs:
            pr = sorted(prs, key=lambda c: cu.to_iso(c["date"]) or "")[0]
            d = cu.to_iso(pr["date"]); tm = cu.to_hhmm(pr["time"]); src = pr["view"] or e["url"]
        if not d:
            m = re.search(r"(\w+ \d{1,2}, \d{4})", e["card_text"])
            d = cu.to_iso(m.group(1)); tm = cu.to_hhmm(e.get("starts"))
        if d < "2019-07-01":
            print("WARN unhandled pre-2019H2 event", slug, d); continue
        rows.append((d, tm, cu.timing(tm), et, fp, src))
    # scheduled but not yet published (upcoming calendar): Q3 2026 revenues
    rows.append(("2026-10-30", "07:00", "BMO", "Q3", "2026Q3", EV % "q3-2026-revenues"))
    rows += MANUAL
    rows = sorted(set(rows))
    with open(OUT, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["ticker", "event_date", "event_time_local", "timezone", "timing", "event_type", "fiscal_period", "source_url"])
        for r in rows:
            if r[0] < "2015-01-01":
                continue
            w.writerow([T, r[0], r[1], "Europe/Paris", r[2], r[3], r[4], r[5]])
    print("wrote", OUT, len(rows))

if __name__ == "__main__":
    main()
