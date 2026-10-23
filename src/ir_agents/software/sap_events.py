"""Build SAP.DE release calendar (2015-01 .. 2026-10) from verified sources:
 - SAP News Center WordPress API post times (2022-07+) and 'to release' schedule posts,
 - EQS/DGAP ad hoc timestamps mirrored on sap.com IR (pre-announcements, warnings),
 - EDGAR 6-K exhibit datelines (dates of regular releases),
 - Wayback snapshots of news.sap.com posts (article:published_time) where available."""
import sys, os, re, json, csv
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
sys.path.insert(0, os.path.dirname(__file__))
import fetch_util as fu

T = "SAP.DE"
TZ = ZoneInfo("Europe/Berlin")
RAW = os.path.join(fu.RAW_IR, T)
OUT = os.path.join(fu.PROC_IR, "%s_events.csv" % T)
EDGAR = "https://www.sec.gov/Archives/edgar/data/1000184/%s/%s"
ADHOC = "https://www.sap.com/investors/en/financial-news/ad-hoc-news/"

def timing(hhmm):
    if not hhmm:
        return "UNKNOWN"
    h, m = map(int, hhmm.split(":"))
    mins = h * 60 + m
    if mins < 9 * 60:
        return "BMO"
    if mins >= 17 * 60 + 30:
        return "AMC"
    return "INTRADAY"

def utc_to_local(iso):
    dt = datetime.fromisoformat(iso.replace("Z", "+00:00"))
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    lt = dt.astimezone(TZ)
    return lt.strftime("%Y-%m-%d"), lt.strftime("%H:%M")

def main():
    rows = []
    # ---- 1) regular releases: date from EDGAR datelines / WP; time from WP (verified) ----
    ed = json.load(open(os.path.join(RAW, "edgar_6k_datelines.json")))
    def edgar_url(date_str):
        for r in ed:
            if r.get("dateline") and datetime.strptime(r["dateline"], "%B %d, %Y").strftime("%Y-%m-%d") == date_str \
               and re.search(r"(financial results|preliminary financial results)", r.get("lead", "")):
                return EDGAR % (r["acc"].replace("-", ""), r["doc"])
        return ""
    wp = json.load(open(os.path.join(RAW, "news_sap_posts.json")))
    wpmap = {}
    for p in wp:
        m = re.match(r"SAP Announces (?:Q([1-4])|(First|Second|Third|Fourth) Quarter)(?: and (?:FY|Full-Year|Half-Year|HY))?(?: and Half-Year)? (20\d\d)", p["title"])
        if m:
            q = int(m.group(1)) if m.group(1) else {"First": 1, "Second": 2, "Third": 3, "Fourth": 4}[m.group(2)]
            wpmap["%sQ%d" % (m.group(3), q)] = (p["date_gmt"] + "+00:00", p["link"])
    wb = json.load(open(os.path.join(RAW, "news_sap_wayback_posts.json")))
    wbmap = {}
    for r in wb:
        m = re.search(r"/(20\d\d)/\d\d/sap-announces-(?:preliminary-)?(first|second|third|fourth)-quarter.*?(20\d\d)-results", r["url"])
        if m and r.get("published_time"):
            q = {"first": 1, "second": 2, "third": 3, "fourth": 4}[m.group(2)]
            wbmap.setdefault("%sQ%d" % (m.group(3), q), []).append(
                (r["published_time"], "https://web.archive.org/web/%s/%s" % (r["snapshot_ts"], r["url"])))
    # regular release dates (local). Sources: EDGAR datelines; WP API; Yahoo agrees.
    reg = {
        "2014Q4": "2015-01-20", "2015Q1": "2015-04-21", "2015Q2": "2015-07-21", "2015Q3": "2015-10-20",
        "2015Q4": "2016-01-22", "2016Q1": "2016-04-20", "2016Q2": "2016-07-20", "2016Q3": "2016-10-21",
        "2016Q4": "2017-01-24", "2017Q1": "2017-04-25", "2017Q2": "2017-07-20", "2017Q3": "2017-10-19",
        "2017Q4": "2018-01-30", "2018Q1": "2018-04-24", "2018Q2": "2018-07-19", "2018Q3": "2018-10-18",
        "2018Q4": "2019-01-29", "2019Q1": "2019-04-24", "2019Q2": "2019-07-18", "2019Q3": "2019-10-21",
        "2019Q4": "2020-01-28", "2020Q1": "2020-04-21", "2020Q2": "2020-07-27", "2020Q3": "2020-10-25",
        "2020Q4": "2021-01-29", "2021Q1": "2021-04-22", "2021Q2": "2021-07-21", "2021Q3": "2021-10-21",
        "2021Q4": "2022-01-27", "2022Q1": "2022-04-22", "2022Q2": "2022-07-21", "2022Q3": "2022-10-25",
        "2022Q4": "2023-01-26", "2023Q1": "2023-04-21", "2023Q2": "2023-07-20", "2023Q3": "2023-10-18",
        "2023Q4": "2024-01-23", "2024Q1": "2024-04-22", "2024Q2": "2024-07-22", "2024Q3": "2024-10-21",
        "2024Q4": "2025-01-28", "2025Q1": "2025-04-22", "2025Q2": "2025-07-22", "2025Q3": "2025-10-22",
        "2025Q4": "2026-01-29", "2026Q1": "2026-04-23", "2026Q2": "2026-07-23", "2026Q3": "2026-10-21",
    }
    def trusted(d, lt):
        # News Center post times (live API or Wayback article:published_time) are used when the post's local
        # date equals the release date (EDGAR dateline / WP API). From 2016 on they agree with DGAP wire stamps
        # within minutes for the pre-announcements; 2015 post times do not, so 2015 times are left blank.
        return d >= "2016-01-01"
    for per, d in reg.items():
        hhmm, src = "", ""
        cands = []
        if per in wpmap:
            cands.append(wpmap[per])
        cands += wbmap.get(per, [])
        for iso, url in cands:
            ld, lt = utc_to_local(iso)
            if ld == d:
                src = src or url
                if trusted(d, lt):
                    hhmm, src = lt, url
                    break
        if not src:
            src = edgar_url(d)
        if not src:
            src = {"2019-04-24": EDGAR % ("000110465919023552", "a19-8816_16k.htm"),
                   "2019-07-18": EDGAR % ("000110465919041503", "a19-13044_16k.htm")}.get(d, "")
        tm = timing(hhmm) if hhmm else ("BMO" if d < "2023-07-01" else "UNKNOWN")
        rows.append({"event_date": d, "event_time_local": hhmm, "timing": tm, "event_type": "Q" + per[-1],
                     "fiscal_period": per, "source_url": src, "_basis": "post_time" if hhmm else "practice_07:00"})
    # ---- 2) ad hoc pre-announcements / warnings / updates (EQS timestamps) ----
    adhoc = [
        ("2015-01-12", "16:06", "prelim", "2014Q4", ADHOC + "2015/01/1443311.html"),
        ("2015-10-13", "02:38", "prelim", "2015Q3", ADHOC + "2015/10/1513863.html"),
        ("2016-01-12", "00:11", "prelim", "2015Q4", ADHOC + "2016/01/dc47b9f2-ce6d-4b8a-9b0f-3c54730d78b0.html"),
        ("2016-04-08", "23:46", "prelim", "2016Q1", ADHOC + "2016/04/8ce5aede-eebc-4b68-a961-484db82eaf63.html"),
        ("2019-10-11", "00:05", "prelim", "2019Q3", ADHOC + "2019/10/1834973.html"),
        ("2020-04-08", "23:39", "profit_warning", "2020Q1", ADHOC + "2020/04/ae0f1fc6-0c16-4778-a0d7-0c36ff78dbeb.html"),
        ("2020-07-08", "22:43", "prelim", "2020Q2", ADHOC + "2020/07/34f13fa7-1bc8-4c0b-baf2-67c13fb222ad.html"),
        ("2020-10-25", "19:19", "profit_warning", "2020Q3", ADHOC + "2020/10/87bc8870-6f7e-4b2d-8100-6098cf09b0c7.html"),
        ("2021-01-14", "23:35", "prelim", "2020Q4", ADHOC + "2021/01/82be73d9-0e4e-4922-8f59-d18c407a901f.html"),
        ("2021-04-13", "22:39", "prelim", "2021Q1", ADHOC + "2021/04/6c4e33bf-f860-453d-a275-ceeab03c704f.html"),
        ("2021-10-12", "23:37", "prelim", "2021Q3", ADHOC + "2021/10/d5b75cff-44a0-41b3-bc6f-ff370c6b7984.html"),
        ("2022-01-13", "22:52", "prelim", "2021Q4", ADHOC + "2022/01/56c56732-9981-40f6-b80e-6e5decd03f95.html"),
        ("2023-05-16", "17:47", "trading_update", "2023", "https://news.sap.com/2023/05/sap-updates-mid-term-financial-ambition-2025/"),
        ("2024-01-23", "23:14", "trading_update", "2024", ADHOC + "2024/01/311d894d-b3e3-405a-99e3-8169a0345ca4.html"),
    ]
    for d, hhmm, typ, per, src in adhoc:
        rows.append({"event_date": d, "event_time_local": hhmm, "timing": timing(hhmm), "event_type": typ,
                     "fiscal_period": per, "source_url": src, "_basis": "eqs_timestamp" if "ad-hoc" in src else "post_time"})
    # ---- 3) capital markets day / financial analyst conferences ----
    cmd = [
        ("2019-11-12", "", "2019", "https://insidesap.com/?p=11114"),
        ("2024-06-05", "", "2024", "https://www.sap.com/docs/download/investors/2024/sap-2024-financial-analyst-conference-presentation.pdf"),
        ("2025-05-21", "", "2025", "https://www.sap.com/docs/download/investors/2025/sapphire-2025-financial-analyst-presentation.pdf"),
        ("2026-05-13", "", "2026", "https://www.sap.com/investors/en/financial-documents-and-events/events/fac.html"),
    ]
    for d, hhmm, per, src in cmd:
        rows.append({"event_date": d, "event_time_local": hhmm, "timing": timing(hhmm), "event_type": "CMD",
                     "fiscal_period": per, "source_url": src, "_basis": "date_only"})
    rows.sort(key=lambda r: (r["event_date"], r["event_time_local"] or "99"))
    with open(OUT, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["ticker", "event_date", "event_time_local", "timezone", "timing", "event_type", "fiscal_period", "source_url"])
        for r in rows:
            w.writerow([T, r["event_date"], r["event_time_local"], "Europe/Berlin", r["timing"], r["event_type"], r["fiscal_period"], r["source_url"]])
    json.dump(rows, open(os.path.join(RAW, "events_basis.json"), "w"), indent=1)
    for r in rows:
        print(r["event_date"], r["event_time_local"] or "-----", r["timing"], r["event_type"], r["fiscal_period"], r["_basis"], r["source_url"][-60:])

if __name__ == "__main__":
    main()
