"""DT: write DTE.DE_events.csv (2015-01..2026-10) from official telekom.com dates; times only where documented."""
import sys, os, re, json, csv, html
from urllib.parse import unquote
sys.path.insert(0, os.path.dirname(__file__))
import fetch_util as fu

T = "DTE.DE"
OUT = os.path.join(fu.PROC_IR, T + "_events.csv")
DATES = {"2014Q4": "2015-02-26", "2015Q1": "2015-05-13", "2015Q2": "2015-08-06", "2015Q3": "2015-11-05",
         "2015Q4": "2016-02-25", "2016Q1": "2016-05-04", "2016Q2": "2016-08-11", "2016Q3": "2016-11-10",
         "2016Q4": "2017-03-02", "2017Q1": "2017-05-11", "2017Q2": "2017-08-03", "2017Q3": "2017-11-09",
         "2017Q4": "2018-02-22", "2018Q1": "2018-05-09", "2018Q2": "2018-08-09", "2018Q3": "2018-11-08",
         "2018Q4": "2019-02-21", "2019Q1": "2019-05-09", "2019Q2": "2019-08-08", "2019Q3": "2019-11-07",
         "2019Q4": "2020-02-19", "2020Q1": "2020-05-14", "2020Q2": "2020-08-13", "2020Q3": "2020-11-12",
         "2020Q4": "2021-02-26", "2021Q1": "2021-05-12", "2021Q2": "2021-08-12", "2021Q3": "2021-11-12",
         "2021Q4": "2022-02-24", "2022Q1": "2022-05-13", "2022Q2": "2022-08-11", "2022Q3": "2022-11-10",
         "2022Q4": "2023-02-23", "2023Q1": "2023-05-11", "2023Q2": "2023-08-10", "2023Q3": "2023-11-09",
         "2023Q4": "2024-02-23", "2024Q1": "2024-05-16", "2024Q2": "2024-08-08", "2024Q3": "2024-11-14",
         "2024Q4": "2025-02-26", "2025Q1": "2025-05-15", "2025Q2": "2025-08-07", "2025Q3": "2025-11-13",
         "2025Q4": "2026-02-26", "2026Q1": "2026-05-13", "2026Q2": "2026-08-06"}
# publication times documented by DT itself (IR page / archived IR page / calendar detail page)
VERIFIED = {"2022Q3": "07:00", "2022Q4": "07:00", "2023Q1": "07:00", "2023Q2": "07:00", "2025Q2": "07:00", "2025Q3": "07:00"}
COLS = ["ticker", "event_date", "event_time_local", "timezone", "timing", "event_type", "fiscal_period", "source_url"]

def timing(t):
    if not t: return "UNKNOWN"
    h, m = map(int, t.split(":")); x = h * 60 + m
    return "BMO" if x < 540 else ("AMC" if x >= 1050 else "INTRADAY")

def main():
    rel = json.load(open(os.path.join(fu.RAW_IR, T, "dte_release_dates.json")))
    src = {q: v[0]["link"] for q, v in rel.items() if v and "ad-hoc" not in v[0]["link"] and "Ad hoc" not in (v[0]["title"] or "")}
    # fallbacks: document URLs on year pages / downloads page
    pdfs = {}
    for y in (2017, 2018, 2020, 2021, 2023, 2026):
        h = fu.cached_html("https://www.telekom.com/en/investor-relations/publications/financial-results/%d" % y)
        for l in re.findall(r'href="(https://delivery-[^"]+)"', h):
            l = html.unescape(l); nm = unquote(l.split("/as/")[-1].split("?")[0])
            pdfs[nm] = l
    dl = fu.cached_html("https://www.telekom.com/en/investor-relations/publications/downloads")
    for l in re.findall(r'href="(https://delivery-[^"]+)"', dl):
        l = html.unescape(l); nm = unquote(l.split("/as/")[-1].split("?")[0]); pdfs.setdefault(nm, l)
    fb = {"2018Q1": "DL_2018_Q1_Medieninformation.data.pdf", "2018Q3": "DL_2018_Q3_Medieninformation.data.pdf",
          "2020Q2": "DL_2020_Q2_Zwischenbericht-en.data.pdf", "2020Q3": "DL_2020_Q3_Zwischenbericht-en.data.pdf",
          "2023Q2": "DT 23Q2 Media information.data.pdf", "2023Q3": "DT 23Q3 Media information.data.pdf",
          "2026Q1": "DT 26Q1 Media information.data.pdf", "2026Q2": "dt-26q2-media-information.pdf", "2017Q4": "DL_media-information.data.pdf", "2021Q4": "DL_2021_GB_media-information.data.pdf"}
    rows = []
    for q, d in DATES.items():
        u = src.get(q) or pdfs.get(fb.get(q, ""), "")
        t = VERIFIED.get(q, "")
        rows.append({"ticker": T, "event_date": d, "event_time_local": t, "timezone": "Europe/Berlin",
                     "timing": timing(t) if t else "BMO", "event_type": "Q" + q[-1], "fiscal_period": q, "source_url": u})
    adhoc = "https://www.telekom.com/en/investor-relations/publications/ad-hoc-disclosures/%d/ad-hoc-notification"
    extra = [
        ("2015-02-26", "", "CMD", "", "https://www.telekom.com/en/investor-relations/publications/capital-markets-days/capital-markets-day-2015"),
        ("2018-05-24", "14:00", "CMD", "", "https://www.telekom.com/en/investor-relations/publications/capital-markets-days/capital-markets-day-2018"),
        ("2021-05-20", "07:00", "CMD", "", "https://www.telekom.com/en/newsroom/latest-updates/media-information/2021/5/deutsche-telekom-plans-to-accelerate-growth"),
        ("2023-11-02", "13:15", "trading_update", "2023", adhoc % 2023),
        ("2024-10-10", "13:00", "CMD", "", "https://www.telekom.com/en/newsroom/latest-updates/media-information/2024/10/deutsche-telekom-plans-to-accelerate-growth"),
        ("2024-10-10", "18:30", "trading_update", "2024", adhoc % 2024),
        ("2026-08-06", "18:30", "trading_update", "2026", adhoc % 2026),
        ("2026-10-05", "12:00", "CMD", "", "https://www.telekom.com/en/newsroom/latest-updates/media-information/2026/10/deutsche-telekom-boosts-growth-efficiency-and-quality-through-t"),
    ]
    for d, t, et, fp, u in extra:
        rows.append({"ticker": T, "event_date": d, "event_time_local": t, "timezone": "Europe/Berlin",
                     "timing": timing(t), "event_type": et, "fiscal_period": fp, "source_url": u})
    rows.sort(key=lambda r: (r["event_date"], r["event_time_local"]))
    with open(OUT, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLS); w.writeheader(); w.writerows(rows)
    print(len(rows), rows[0]["event_date"], rows[-1]["event_date"], sum(1 for r in rows if not r["source_url"]), "missing urls")

if __name__ == "__main__":
    main()
