"""Build data/processed/ir/ASM.AS_events.csv from press-release headers (stated time) + GlobeNewswire timestamps."""
import sys, os, re, csv, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from irlib import write_events, timing_class
SP = "/private/tmp/claude-501/-Users-sinamirzaei-Documents-aimapping/57e0a0d0-6441-40ef-828b-57eeb87e7b21/scratchpad/asm"
T = "ASM.AS"
gnw = list(csv.DictReader(open(os.path.join(SP, "gnw_all.csv"))))
hdr = json.load(open(os.path.join(SP, "headers.json")))
WORD = {"FIRST": 1, "SECOND": 2, "THIRD": 3, "FOURTH": 4}
rows = []
# --- scheduled quarterly results (2014Q4 published 2015-03-04 onward)
for g in gnw:
    if g["date_local"] < "2015-01-01":
        continue
    t = g["title"].upper()
    if re.search(r"CONFERENCE CALL|AVAILABILITY|ANNUAL REPORT|INTERIM|DETAILS", t):
        continue
    m = re.search(r"(?:REPORTS|ANNOUNCES)\s+(FIRST|SECOND|THIRD|FOURTH)\s+QUARTER\s+(\d{4})", t) or \
        re.search(r"REPORTS\s+Q([1-4])\s+AND\s+FULL-YEAR\s+(\d{4})", t)
    if not m:
        continue
    q = WORD.get(m.group(1), None) or int(m.group(1))
    per = f"{m.group(2)}Q{q}"
    h = hdr.get(per, {})
    if h.get("date") and h["date"] != g["date_local"]:
        print("DATE MISMATCH", per, h["date"], g["date_local"])
    hhmm = h.get("hdr_time") or g["time_local"]
    rows.append({"ticker": T, "event_date": g["date_local"], "event_time_local": hhmm, "timing": timing_class(hhmm),
                 "event_type": f"Q{q}", "fiscal_period": per, "source_url": g["url"]})
# --- unscheduled / special releases (times stated in release header; equal to GNW stamp)
SPECIAL = [  # date, header time, event_type, fiscal_period, title-regex
    ("2020-01-14", "17:45", "prelim", "2019Q4", r"Q4 2019 ORDERS"),
    ("2021-07-01", "17:45", "prelim", "2021Q2", r"Q2 2021 ORDERS"),
    ("2021-09-28", "07:45", "CMD", "", r"INVESTOR DAY"),
    ("2021-09-28", "07:45", "trading_update", "2021Q3", r"INVESTOR DAY"),
    ("2022-11-28", "17:45", "trading_update", "2022Q4", r"UPDATES Q4 GUIDANCE"),
    ("2023-01-17", "17:45", "prelim", "2022Q4", r"Q4 2022 REVENUE"),
    ("2023-09-26", "07:45", "CMD", "", r"INVESTOR DAY"),
    ("2024-12-04", "08:00", "trading_update", "2024Q4", r"EXPORT REGULATIONS"),
    ("2025-09-23", "07:45", "CMD", "", r"INVESTOR DAY"),
    ("2025-09-23", "07:45", "profit_warning", "2025Q4", r"INVESTOR DAY"),
    ("2026-01-19", "08:00", "prelim", "2025Q4", r"PRE-ANNOUNCES"),
]
for d, hhmm, et, per, pat in SPECIAL:
    g = [x for x in gnw if x["date_local"] == d and re.search(pat, x["title"].upper()) and "NET ZERO" not in x["title"].upper()]
    assert len(g) == 1, (d, pat, len(g))
    assert g[0]["time_local"] == hhmm, (d, g[0]["time_local"], hhmm)
    rows.append({"ticker": T, "event_date": d, "event_time_local": hhmm, "timing": timing_class(hhmm),
                 "event_type": et, "fiscal_period": per, "source_url": g[0]["url"]})
df = write_events(T, rows)
print(len(df), df.event_date.min(), df.event_date.max())
print(df.event_type.value_counts().to_dict(), df.timing.value_counts().to_dict())
