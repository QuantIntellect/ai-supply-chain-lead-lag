"""Build data/processed/ir/RR.L_events.csv from the Investegate RNS index (times as displayed by
Investegate = UK local clock time; discriminating check: the 6 May 2022 notice says the AGM update
'will be published at 7am on 12 May' (BST) and Investegate lists it at 07:00 AM, not 06:00)."""
import sys; sys.path.insert(0, "/Users/sinamirzaei/Documents/aimapping/src/ir_agents/energy"); import irlib
import rr_common as C

# final classification of CHECK items: (date, headline) -> (event_type, fiscal_period) or None (exclude)
OVERRIDE = {
    ("2015-07-06", "Rolls-Royce Guidance Update"): ("profit_warning", "FY2015"),   # 2015 PBT/FCF guidance cut + 2016 headwinds
    ("2015-11-12", "Interim Management Statement"): ("profit_warning", "FY2016"),  # Q3 IMS: 2016 profit headwinds, dividend review
    ("2015-11-24", "Rolls-Royce presents operations review update"): ("CMD", ""),  # CEO operations-review investor presentation
    ("2018-06-15", "Rolls-Royce Outlines Mid-Term Ambition"): ("CMD", ""),         # 2018 Capital Markets Event
    ("2018-10-26", "STATEMENT re TRENT 7000. FY GUIDANCE CONFIRMED"): ("trading_update", "FY2018Q3"),
    ("2020-04-06", "Trading Update"): ("profit_warning", "FY2020"),                # COVID: 2020 guidance withdrawn
    ("2020-10-01", "Proposed Recapitalisation"): ("trading_update", "FY2020Q3"),   # capital raise incl. trading update
    ("2021-01-26", "Trading Update"): ("profit_warning", "FY2021"),                # 2021 FCF ~£(2)bn vs positive H2-21 target
}
# Investor day without an RNS on the day: date + webcast start time stated in the 6 May 2022 notice
EXTRA = [
    {"event_date": "2022-05-13", "event_time_local": "10:00", "event_type": "CMD", "fiscal_period": "",
     "notice": ("2022-05-06", "Civil Aerospace Investor Day - 13 May 2022")},
    # Power Systems teach-in webinar: no RNS; date from the rolls-royce.com results page listing
    # ("26 June 2026 | Power Systems Teach-in Webinar"); clock time not published -> UNKNOWN
    {"event_date": "2026-06-26", "event_time_local": "", "event_type": "CMD", "fiscal_period": "",
     "source_url": "https://www.rolls-royce.com/investors/results-reports-and-presentations/financial-results.aspx"},
]


def build():
    idx = C.load_index()
    rows = []
    for date, head, et, fp, dt in C.CANDIDATES:
        if (date, head) in OVERRIDE:
            v = OVERRIDE[(date, head)]
            if v is None:
                continue
            et, fp = v
        if et == "CHECK":
            continue
        r = C.find(idx, date, head)
        rows.append({"event_date": date, "event_time_local": r["hhmm"], "event_type": et,
                     "fiscal_period": fp, "source_url": r["url"], "timing": ""})
    for e in EXTRA:
        url = C.find(idx, *e["notice"])["url"] if "notice" in e else e["source_url"]
        rows.append({"event_date": e["event_date"], "event_time_local": e["event_time_local"],
                     "event_type": e["event_type"], "fiscal_period": e["fiscal_period"],
                     "source_url": url, "timing": ""})
    rows = [r for r in rows if "2015-01-01" <= r["event_date"] <= "2026-10-23"]
    return rows


if __name__ == "__main__":
    rows = build()
    irlib.write_events(C.TICKER, rows)
    from collections import Counter
    out = irlib.read_csv("data/processed/ir/RR.L_events.csv")
    print(Counter(r["timing"] for r in out), Counter(r["event_type"] for r in out))
    print(out[0]["event_date"], out[-1]["event_date"])
