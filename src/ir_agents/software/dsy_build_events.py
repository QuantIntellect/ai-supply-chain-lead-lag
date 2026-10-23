"""Build data/processed/ir/DSY.PA_events.csv from scraped IR news (investor.3ds.com) + 3ds.com newsroom metadata.
Timing rule (Euronext Paris 09:00-17:30): BMO <09:00, AMC >=17:30, INTRADAY otherwise, UNKNOWN if no time.
Time source priority: investor.3ds.com news-release timestamp (precise from 2019) > 3ds.com newsroom
article:published_time (2015-2018; uniform 07:00 Paris) > blank."""
import sys, os, re, json
from datetime import datetime
from zoneinfo import ZoneInfo
import pandas as pd
sys.path.insert(0, os.path.dirname(__file__))
import fetch_util as fu

T = "DSY.PA"
PAR = ZoneInfo("Europe/Paris")
ir = json.load(open(os.path.join(fu.RAW_IR, T, "ir_news_releases.json")))
nr = json.load(open(os.path.join(fu.RAW_IR, T, "newsroom_times.json")))

def ir_dt(txt):
    """'October 23, 2025 at 1:00 AM EDT' -> Paris-local datetime"""
    m = re.search(r"([A-Z][a-z]+ \d{1,2}, \d{4}) at (\d{1,2}:\d{2} [AP]M) (EDT|EST|CEST|CET)", txt or "")
    if not m:
        return None
    tz = {"EDT": "America/New_York", "EST": "America/New_York", "CEST": "Europe/Paris", "CET": "Europe/Paris"}[m.group(3)]
    dt = datetime.strptime(m.group(1) + " " + m.group(2), "%B %d, %Y %I:%M %p").replace(tzinfo=ZoneInfo(tz))
    return dt.astimezone(PAR)

def nr_dt(s):
    if not s:
        return None
    s = s.replace("+0000", "+00:00")
    return datetime.fromisoformat(s).astimezone(PAR)

def find_ir(pat):
    c = [r for r in ir if re.search(pat, r["title"], re.I) and "Releases Year" not in r["title"]]
    if not c:
        return None
    r = c[0]
    if not r.get("datetime_text"):
        from bs4 import BeautifulSoup
        h = fu.cached_html(r["link"])
        d = BeautifulSoup(h, "html.parser").select_one(".field--name-field-nir-news-date") if h else None
        r["datetime_text"] = d.get_text(" ", strip=True) if d else ""
    return r

def find_nr(pat):
    c = [r for r in nr if re.search(pat, r["url"].split("/")[-1], re.I)]
    return c[0] if c else None

# (fiscal_period, event_type, ir_title_regex, newsroom_slug_regex, time_source)
# time_source: 'ir' (precise IR timestamp), 'nr' (3ds.com newsroom metadata), 'none'
EV = [
 ("2014Q4", "Q4", r"2014 Organic New Licenses", r"2014-organic-new-licenses", "nr"),
 ("2015Q1", "Q1", r"^Dassault Syst.mes Reports Strong Revenue and EPS Growth", r"reports-strong-revenue-and-eps-growth$", "nr"),
 ("2015Q2", "Q2", r"Upgrades 2015 Financial Objectives", r"upgrades-2015-financial-objectives", "nr"),
 ("2015Q3", "Q3", r"Strong Third Quarter EPS Growth", r"reports-strong-third-quarter-eps-growth", "nr"),
 ("2015Q4", "Q4", r"Strong Fourth Quarter Software Revenue Growth", r"strong-fourth-quarter-software-revenue-growth", "nr"),
 ("2016Q1", "Q1", r"Q1 Non-IFRS Total Revenues at High End", r"q1-non-ifrs-total-revenues-high-end", "nr"),
 ("2016Q2", "Q2", r"Confirms 2016 Financial Objectives", r"confirms-2016-financial-objectives", "nr"),
 ("2016Q3", "Q3", r"Up 40% in 2016 Third Quarter", r"revenue-40-2016-third-quarter", "nr"),
 ("2016Q4", "Q4", r"Q416 Total Revenue", r"q416-total-revenue", "nr"),
 ("2017Q1", "Q1", r"First Quarter Revenue and EPS Ahead of its Guidance", r"first-quarter-revenue-and-eps-ahead", "nr"),
 ("2017Q2", "Q2", r"Delivers Q2 Software Revenue and EPS", r"delivers-q2-software-revenue-and-eps", "nr"),
 ("2017Q3", "Q3", r"Third Quarter Non-IFRS Software Revenue Up 8%", r"third-quarter-non-ifrs-software-revenue-8", "nr"),
 ("2017Q4", "Q4", r"New Licenses Revenue Up 16% in Fourth Quarter", r"new-licenses-revenue-16-fourth-quarter", "nr"),
 ("2018Q1", "Q1", r"broad-based growth in first quarter", r"broad-based-growth-first-quarter", "nr"),
 ("2018Q2", "Q2", r"raises EPS guidance for 2018", r"raises-eps-guidance-2018", "nr"),
 ("2018Q3", "Q3", r"Q3 and YTD EPS up double-digits and reaffirms 2018", r"q3-and-ytd-eps-double-digits", "nr"),
 ("2018Q4", "Q4", r"Fourth Quarter total revenue up 13%", r"fourth-quarter-total-revenue-1", "ir"),
 ("2019Q1", "Q1", r"First Quarter Revenue and EPS Growth Up Double-digits", r"zzz", "ir"),
 ("2019Q2", "Q2", r"First Half Revenue and EPS Growth Up Double-digits", r"zzz", "ir"),
 ("2019Q3", "Q3", r"Q3 and YTD Total Revenue and EPS Growth", r"q3-and-ytd-total-revenue-and-eps-growth", "ir"),
 ("2019Q4", "Q4", r"Sustaining Diversification Dynamic", r"sustaining-diversification-dynamic", "ir"),
 ("2020Q1", "Q1", r"First Quarter Financial Results With Recurring Software", r"zzz", "ir"),
 ("2020Q2", "Q2", r"Well Aligned with its Guidance, IFRS and non-IFRS Total Revenue up 11%", r"zzz", "ir"),
 ("2020Q3", "Q3", r"Strong Third Quarter Operational Performance, Confirms its 2020", r"zzz", "ir"),
 ("2020Q4", "Q4", r"2020 Fourth Quarter Results at the High End", r"zzz", "ir"),
 ("2021Q1", "Q1", r"2021 First Quarter Results Above the High End", r"zzz", "ir"),
 ("2021Q2", "Q2", r"Strong Second Quarter Results, Raises Full Year Guidance", r"zzz", "ir"),
 ("2021Q3", "Q3", r"Strong Third Quarter Growth, Raises Guidance", r"zzz", "ir"),
 ("2021Q4", "Q4", r"Strong 2021 Results, With Fourth Quarter", r"zzz", "ir"),
 ("2022Q1", "Q1", r"Raising 2022 EPS Objectives on Good First Quarter", r"zzz", "ir"),
 ("2022Q2", "Q2", r"Delivers Strong Second Quarter, Reaffirms 2022", r"zzz", "ir"),
 ("2022Q3", "Q3", r"Delivers Solid Third Quarter Driven By Accelerating Recurring", r"zzz", "ir"),
 ("2022Q4", "Q4", r"Strong FY 2022, Q4 Revenue and EPS", r"zzz", "ir"),
 ("2023Q1", "Q1", r"Solid First Quarter Driven by Strong Subscription", r"zzz", "ir"),
 ("2023Q2", "Q2", r"Strong Second Quarter Results with Broad-Based Momentum", r"zzz", "ir"),
 ("2023Q3", "Q3", r"Outperforming Third Quarter", r"zzz", "ir"),
 ("2023Q4", "Q4", r"Doubles EPS as Planned in 2018", r"zzz", "ir"),
 ("2024Q1", "Q1", r"Solid First Quarter Results And Reaffirms Full-Year", r"zzz", "ir"),
 ("2024Q2", "profit_warning", r"Preliminary Second Quarter 2024 Results", r"zzz", "ir"),
 ("2024Q2", "Q2", r"Second Quarter 2024 Results in Line With Preliminary", r"zzz", "ir"),
 ("2024Q3", "Q3", r"Third quarter results in-line - Anticipating", r"zzz", "ir"),
 ("2024Q4", "Q4", r"Strong Q4 results driven by new business acceleration", r"zzz", "ir"),
 ("2025Q1", "Q1", r"Solid start to the year with strong subscription growth", r"zzz", "ir"),
 ("2025Q2", "Q2", r"Q2 well aligned with objectives; Reaffirming 2025", r"zzz", "ir"),
 ("2025Q3", "Q3", r"Solid third quarter with strong operational performance", r"zzz", "ir"),
 ("2025Q4", "Q4", r"Q4 revenue growth of 1% with solid operating margin", r"zzz", "ir"),
 ("2026Q1", "Q1", r"reports first quarter 2026 results in line", r"zzz", "ir"),
 ("2026Q2", "Q2", r"Solid Q2 results and confirming full-year objectives", r"zzz", "ir"),
 ("2020Q1", "profit_warning", r"Preliminary First Quarter 2020", r"zzz", "ir"),
 # Capital markets / investor days
 ("", "CMD", r"Re-affirms its 2019 Non-IFRS EPS Objective", r"re-affirms-its-2019-non-ifrs-eps", "none"),
 ("", "CMD", r"Initiates a 2023 Non-IFRS EPS Objective", r"initiates-2023-non-ifrs-eps-objective", "none"),
 ("", "CMD", r"Holding Life Sciences Day", r"zzz", "ir"),
 ("", "CMD", r"Updates Multi-year Growth Plan", r"zzz", "ir"),
 ("", "CMD", r"Capital Markets Day: On Trajectory to Achieve 2024", r"zzz", "ir"),
 ("", "CMD", r"Capital Markets Day: Doubling non-IFRS EPS by 2028", r"zzz", "ir"),
 ("", "CMD", r"Doubling EPS by 2029", r"zzz", "ir"),
]
# dateline dates for CMDs where the IR listing date is unreliable
CMD_DATES = {r"Re-affirms its 2019": "2016-06-10", r"Initiates a 2023": "2018-06-15"}

def timing(dt):
    if dt is None:
        return "UNKNOWN"
    hm = dt.hour * 60 + dt.minute
    if hm < 9 * 60:
        return "BMO"
    if hm >= 17 * 60 + 30:
        return "AMC"
    return "INTRADAY"

rows = []
for fp, et, irpat, nrpat, src in EV:
    r = find_ir(irpat)
    n = find_nr(nrpat)
    dt, url, date = None, "", None
    if src == "ir" and r and r.get("datetime_text"):
        dt = ir_dt(r["datetime_text"]); url = r["link"]
    elif src == "nr" and n and n.get("published_time"):
        dt = nr_dt(n["published_time"]); url = n["url"]
    elif src == "none":
        url = (n or {}).get("url") or (r or {}).get("link", "")
    if dt is not None:
        date = dt.strftime("%Y-%m-%d")
    for k, v in CMD_DATES.items():
        if re.search(k, irpat):
            date = v
    if date is None:
        print("MISSING", fp, et, irpat); continue
    rows.append({"ticker": T, "event_date": date,
                 "event_time_local": dt.strftime("%H:%M") if dt is not None else "",
                 "timezone": "Europe/Paris", "timing": timing(dt), "event_type": et,
                 "fiscal_period": fp, "source_url": url})
df = pd.DataFrame(rows).sort_values(["event_date", "event_type"]).reset_index(drop=True)
# CMD fiscal_period: label by event year (e.g. CMD2023) for readability
df.loc[df.event_type == "CMD", "fiscal_period"] = "CMD" + df.loc[df.event_type == "CMD", "event_date"].str[:4]
os.makedirs(fu.PROC_IR, exist_ok=True)
df.to_csv(os.path.join(fu.PROC_IR, T + "_events.csv"), index=False)
print(df.to_string())
