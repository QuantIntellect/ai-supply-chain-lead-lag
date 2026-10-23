"""Build data/processed/ir/SIE.DE_events.csv.

Sources (all official):
  * IR results pages (doc_links*.json): presentation filenames carry yymmdd.
  * Earnings release / press release datelines ("Munich, Germany, <date>").
  * press.siemens.com results event pages (press_event_times.json): release
    time statements "(7:00 a.m. CEST)", 'Save the date' start time, press call.
  * EQS ad hoc feed (eqs_adhoc.json): exact UTC timestamps -> Europe/Berlin.
  * IR events page: Capital Market Days.
"""
import os, sys, re, json
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from irlib import *

T = "SIE.DE"
PG = os.path.join(RAW_IR, T, "pages")
TXT = os.path.join(TEXT_IR, T)
BER = ZoneInfo("Europe/Berlin")
MONTHS = {m: i for i, m in enumerate(["January", "February", "March", "April", "May", "June", "July",
                                       "August", "September", "October", "November", "December"], 1)}


def dateline(path):
    if not os.path.exists(path):
        return None
    t = open(path, encoding="utf-8", errors="ignore").read()[:6000]
    m = re.search(r"Munich,(?: Germany,)?\s+(January|February|March|April|May|June|July|August|"
                  r"September|October|November|December)\s+(\d{1,2}),\s+(20\d\d)", t)
    if not m:
        return None
    return f"{m.group(3)}-{MONTHS[m.group(1)]:02d}-{int(m.group(2)):02d}"


def first_call(p):
    """Earliest 'Starting today at HH:MM' (press/analyst call) in the earnings release."""
    fp = os.path.join(TXT, f"{p}_earnings_release.txt")
    if not os.path.exists(fp):
        return None
    t = re.sub(r"\s+", " ", open(fp, encoding="utf-8", errors="ignore").read())
    ts = re.findall(r"[Ss]tarting (?:today )?at (\d{1,2})[:.](\d{2})", t)
    if not ts:
        return None
    return min(f"{int(h):02d}:{m}" for h, m in ts)


# --- presentation filename dates and source URLs -------------------------------
links = json.load(open(os.path.join(PG, "doc_links.json")))
pres_date, er_url, pr_url = {}, {}, {}
for r in links:
    m = re.match(r"Q([1-4]) FY(\d\d)", r["label"])
    if not m:
        continue
    p = f"20{m.group(2)}Q{m.group(1)}"
    href = r["href"] if not r["href"].startswith("//") else "https:" + r["href"]
    fn = href.split("/")[-1]
    m2 = re.match(r"(\d{2})(\d{2})(\d{2})-q[1-4]-presentation", fn)
    if m2:
        pres_date[p] = f"20{m2.group(1)}-{m2.group(2)}-{m2.group(3)}"
    if "earnings-release" in fn:
        er_url[p] = href
    if "press-release" in fn and re.fullmatch(r"Q[1-4]", r["text"].strip()):
        pr_url[p] = href
for u in json.load(open(os.path.join(PG, "doc_links_fy15.json"))):
    href = "https:" + u if u.startswith("//") else u
    fn = href.split("/")[-1]
    m2 = re.match(r"(\d{2})(\d{2})(\d{2})-q([1-4])-presentation", fn)
    if m2 and m2.group(1) == "15":
        pres_date[f"2015Q{m2.group(4)}"] = f"20{m2.group(1)}-{m2.group(2)}-{m2.group(3)}"
    m3 = re.match(r"2015-q([1-4])-earnings-release", fn)
    if m3:
        er_url[f"2015Q{m3.group(1)}"] = href

pe = json.load(open(os.path.join(PG, "press_event_times.json")))

# Q1 releases published the evening before the AGM / press conference: the
# earnings release is dated that day and followed an ad hoc (EQS timestamp).
EVENING_Q1 = {
    "2016Q1": "ER dated 2016-01-25; ad hoc 18:23 CET same evening; press/analyst events 2016-01-26",
    "2017Q1": "ER dated 2017-01-31; ad hoc 20:07 CET same evening; presentation dated 2017-02-01",
    "2023Q1": "ER+press release dated 2023-02-08; ad hoc 19:50 CET same evening; press event 2023-02-09 07:30",
}
rows, audit = [], []
periods = [f"{fy}Q{q}" for fy in range(2015, 2027) for q in range(1, 5) if not (fy == 2026 and q == 4)]
for p in periods:
    erd = dateline(os.path.join(TXT, f"{p}_earnings_release.txt"))
    prd = dateline(os.path.join(TXT, f"{p}_press_release.txt"))
    psd = pres_date.get(p)
    ev = pe.get(p, {})
    std = (ev.get("save_the_date") or [None, None])
    # date priority: press release dateline > earnings release dateline > presentation date
    date = prd or erd or psd or std[0]
    hhmm, timing, note = "", "", ""
    rt = ev.get("release_time")
    if rt and ev.get("status") == 200:
        h, mnt = re.split(r"[:.]", rt[0])
        hhmm = f"{int(h):02d}:{mnt}"
        note = "release time stated on press.siemens.com event page"
    elif std[1] and std[1] == "07:00" and p >= "2025Q1":
        hhmm = "07:00"
        note = "press event page start time 07:00 (= release time on 2025+ pages)"
    elif p in EVENING_Q1:
        timing = "AMC"
        note = EVENING_Q1[p]
    elif first_call(p) and first_call(p) <= "09:00":
        timing = "BMO"
        note = f"earnings release: 'Starting today at {first_call(p)}' press call -> release earlier that morning"
    elif std[1] and "06:00" <= std[1] <= "08:30" and std[0] == date:
        timing = "BMO"
        note = f"release precedes press event starting {std[1]} (press.siemens.com)"
    elif ev.get("press_call") and std[0] == date:
        timing = "BMO"
        note = f"release precedes press call {ev['press_call']}"
    src = pr_url.get(p) or er_url.get(p) or ev.get("url", "")
    rows.append({"event_date": date, "event_time_local": hhmm, "timing": timing,
                 "event_type": f"Q{p[-1]}", "fiscal_period": p, "source_url": src})
    audit.append((p, date, prd, erd, psd, std[0], std[1], hhmm, timing or classify_timing(hhmm), note))

# --- ad hoc announcements (EQS, exact timestamps) --------------------------------
ADHOC_TYPES = {  # date (UTC) -> (event_type, fiscal_period)
    "2016-01-25": ("prelim", "2016Q1"),            # raises EPS guidance FY16 (with Q1 release)
    "2017-01-31": ("prelim", "2017Q1"),            # raises earnings outlook FY17 (with Q1 release)
    "2021-01-21": ("prelim", "2021Q1"),            # prelim Q1 FY21 significantly above expectations
    "2022-06-30": ("profit_warning", "2022Q3"),    # ~EUR2.8bn impairment of Siemens Energy stake
    "2023-02-08": ("prelim", "2023Q1"),            # raises FY23 outlook on strong Q1
}
eqs = json.load(open(os.path.join(PG, "eqs_adhoc.json")))
for it in eqs["items"]:
    d_utc = it["date_published"][:10]
    if d_utc not in ADHOC_TYPES:
        continue
    ts = datetime.strptime(it["date_published"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc).astimezone(BER)
    et, fp = ADHOC_TYPES[d_utc]
    rows.append({"event_date": ts.strftime("%Y-%m-%d"), "event_time_local": ts.strftime("%H:%M"),
                 "event_type": et, "fiscal_period": fp,
                 "source_url": "https://irpages2.eqs.com/websites/newsfeed/English/4/json-feed.html?companyToken=c34f511e-40f9-4c7a-9eb6-934a84aa0543&type=adhoc&limit=-1#" + str(it["id"])})

# --- Capital Market Days (IR events page) ---------------------------------------
IREV = "https://www.siemens.com/en-us/company/investor-relations/ir-events/"
for d, label in [("2016-06-29", "CMD Energy and Oil & Gas"), ("2019-05-08", "CMD Vision 2020+"),
                 ("2021-06-24", "Capital Market Day 2021"), ("2024-12-12", "Smart Infrastructure Capital Market Event"),
                 ("2025-11-13", "Siemens ONE Tech - Strategy & Results 2025")]:
    rows.append({"event_date": d, "event_time_local": "08:30" if d == "2025-11-13" else "", "timing": "", "event_type": "CMD",
                 "fiscal_period": "", "source_url": IREV + "#" + label.replace(" ", "_")})

for r in rows:
    if not r.get("timing"):
        r["timing"] = classify_timing(r.get("event_time_local"))
path = write_events(T, rows)
with open(os.path.join(PG, "events_audit.tsv"), "w") as f:
    f.write("period\tdate\tpr_dateline\ter_dateline\tpres_file\tsave_date\tsave_time\thhmm\ttiming\tnote\n")
    for a in audit:
        f.write("\t".join("" if x is None else str(x) for x in a) + "\n")
print(path, len(rows))
