"""Build data/processed/ir/LR.PA_events.csv from Legrand's regulated-information pages
(results dates), the AMF regulated-information feed (deposit timestamps, Paris time) and,
when available, Legrand newsroom JSON-LD datePublished (data/raw/ir/LR.PA/pages/news_times.json)."""
import os, sys, re, json, datetime as dt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from irlib import *

TK = "LR.PA"
MONTHS = {m: i + 1 for i, m in enumerate(["january", "february", "march", "april", "may", "june", "july",
                                            "august", "september", "october", "november", "december"])}
reg = json.load(open(os.path.join(RAW_IR, TK, "pages", "regpages_parsed.json")))
amf = json.load(open(os.path.join(RAW_IR, TK, "amf", "amf_records.json")))
news_path = os.path.join(RAW_IR, TK, "pages", "news_times.json")
news = json.load(open(news_path)) if os.path.exists(news_path) else {}   # date -> [(HH:MM, url, slug)]


def parse_date(s):
    s = s.replace("1st", "1").replace(",", " ")
    m = re.search(r"(\d{1,2})\s+([A-Za-z]+)\s+(20\d\d)", s)
    if m:
        return dt.date(int(m.group(3)), MONTHS[m.group(2).lower()], int(m.group(1)))
    m = re.search(r"([A-Za-z]+)\s+(\d{1,2})\s+(20\d\d)", s)
    if m:
        return dt.date(int(m.group(3)), MONTHS[m.group(1).lower()], int(m.group(2)))
    return None


def amf_local(r):
    d = r.get("uin_dat_amf")
    if not d:
        return None
    t = dt.datetime.fromisoformat(d)
    h, m = map(int, (r.get("timezone_uin_dat_amf") or "01:00").split(":"))
    return (t + dt.timedelta(hours=h, minutes=m)).replace(tzinfo=None)


PR_TYPES = {"001001", "001002", "001006", "001007", "001008", "005000", "005001", "005002"}
RPT_TYPES = {"003000", "004000", "002002", "002003", "002004"}
amf_by_day = {}
for r in amf:
    l = amf_local(r)
    if l:
        amf_by_day.setdefault(l.date().isoformat(), []).append((l.strftime("%H:%M"), r.get("informationdeposee_inf_stp_pri"),
                                                                r.get("url_de_recuperation")))


def amf_time(day, morning_only=True):
    recs = amf_by_day.get(day, [])
    pr = sorted(x for x in recs if x[1] in PR_TYPES and (not morning_only or x[0] < "12:00"))
    if pr:
        return pr[0][0], pr[0][2], "AMF press-release deposit"
    rp = sorted(x for x in recs if x[1] in RPT_TYPES and x[0] < "09:00")
    if rp:
        return rp[0][0], rp[0][2], "AMF report deposit"
    return "", "", ""


def kind_of(title):
    t = title.lower()
    if "full-year" in t or "full year" in t:
        return "FY", 4
    if "nine-month" in t or "nine month" in t:
        return "Q3", 3
    if "first half" in t or "half-year" in t:
        return "H1", 2
    if "first quarter" in t:
        return "Q1", 1
    return None, None


events = {}
for o in reg:
    if o["section"] != "Financial presentations":
        continue
    et, q = kind_of(o["title"])
    d = parse_date(o["title"])
    if not et or not d:
        continue
    fy = o["page_year"]
    if fy == 2026 and et == "Q1":       # website typo "7 May 2025" for Q1 2026
        d = dt.date(2026, 5, 7)
    fp = f"{fy}Q{q}"
    href = o["hrefs"][0] if o["hrefs"] else ""
    if href.startswith("/"):
        href = "https://www.legrand.com" + href
    events[(d.isoformat(), et)] = {"event_date": d.isoformat(), "event_type": et, "fiscal_period": fp,
                                   "source_url": href}
# FY2014 results (published 12 Feb 2015) are listed only on the 2014 page
events[("2015-02-12", "FY")] = {"event_date": "2015-02-12", "event_type": "FY", "fiscal_period": "2014Q4",
                                "source_url": ""}

# special events: (date, type, fiscal_period, time_override, source)
SPECIAL = [
    ("2016-06-30", "CMD", "", None, "https://fr.ftp.opendatasoft.com/datadila/INFOFI/BWR/2016/06/FCBWR093922_20160630.pdf"),
    ("2019-06-12", "CMD", "", None, "https://www.legrand.com/en/investors-and-shareholders/investor-day/investor-day-2019"),
    ("2020-03-26", "profit_warning", "2020Q1", None, "https://www.legrand.com/en/news/legrand-information-global-health-context-covid-19"),
    ("2021-09-22", "CMD", "", None, "https://www.legrand.com/en/investors-and-shareholders/investor-day/capital-markets-day-2021"),
    ("2022-03-29", "CMD", "", None, "https://www.legrand.com/en/investors-and-shareholders/capital-markets-days/esg-capital-markets-day-2022"),
    ("2024-09-24", "CMD", "", None, "https://www.legrand.com/sites/default/files/Documents_PDF_Legrand/Finance/2024/autres/Legrand_Press_Release_CMD_September-2024_1727107150.pdf"),
    ("2025-03-25", "CMD", "", None, "https://www.legrand.com/en/investors-and-shareholders/capital-markets-days/csr-capital-markets-day-2025"),
    ("2025-07-17", "prelim", "2025Q2", None, "https://www.legrand.com/sites/default/files/Documents_PDF_Legrand/Finance/2025/6m/Legrand_Press_Release_Sales_H1_2025-vf_1752729073.pdf"),
    ("2026-09-28", "CMD", "", None, "https://www.legrand.com/sites/default/files/Documents_PDF_Legrand/Finance/2026/autre/CMD/Legrand_Press_Release_CMD_Sep-2026_1790606990.pdf"),
]
for d, et, fp, tov, src in SPECIAL:
    events[(d, et)] = {"event_date": d, "event_type": et, "fiscal_period": fp, "source_url": src, "_tov": tov}

# Times not in the AMF feed, taken from Legrand newsroom JSON-LD datePublished (Paris time).
# 2017-era newsroom stamps are shifted by +UTC offset (verified: 2017-05-10 news 09:30 vs AMF 07:32;
# 2017-07-31 news 09:30 vs AMF 07:30), so 2017-02-09 news 08:30 CET -> 07:30.
TIME_OVERRIDE = {
    ("2017-02-09", "FY"): ("07:30", "https://www.legrand.com/en/news/2016-results"),
    ("2018-07-31", "H1"): ("07:30", "https://www.legrand.com/en/news/2018-first-half-results"),
    ("2020-03-26", "profit_warning"): ("07:30", "https://www.legrand.com/en/news/legrand-information-global-health-context-covid-19"),
}
events[("2019-06-12", "CMD")]["source_url"] = ("https://www.legrand.com/sites/default/files/Documents_PDF_Legrand/Finance/2019/"
                                               "autres/Legrand_Press_Release_Investor_Day_2019_1560269114.pdf")
for k, (t, u) in TIME_OVERRIDE.items():
    events[k]["_tov"] = t
    events[k]["source_url"] = u

rows = []
for k, e in sorted(events.items()):
    d = e["event_date"]
    t_amf, u_amf, how = amf_time(d, morning_only=e["event_type"] not in ("CMD",))
    if e["event_type"] == "CMD" and not t_amf:
        t_amf, u_amf, how = amf_time(d, morning_only=False)
    n = news.get(d, [])
    t_news = n[0][0] if n else ""
    t = e.get("_tov") or t_amf or t_news
    # cite the record that carries the timestamp (AMF deposit) unless a newsroom override was used
    src = e["source_url"] if (e.get("_tov") or not u_amf) else u_amf
    e2 = {"event_date": d, "event_time_local": t, "timezone": TZ[TK], "event_type": e["event_type"],
          "fiscal_period": e["fiscal_period"], "source_url": src,
          "_amf": t_amf, "_news": t_news}
    rows.append(e2)
path = write_events(TK, [dict(r) for r in rows])
print(path, len(rows))
for r in rows:
    flag = "" if (not r["_amf"] or not r["_news"] or r["_amf"] == r["_news"]) else "  <-- AMF/news differ"
    print(r["event_date"], r["event_type"], r["fiscal_period"], "amf", r["_amf"] or "-", "news", r["_news"] or "-", flag)
