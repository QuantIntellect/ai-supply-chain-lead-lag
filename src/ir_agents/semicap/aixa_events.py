"""Build data/processed/ir/AIXA.DE_events.csv from parsed Aixtron news timestamps (2017+) and archived 2015-2016 pages."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import irlib
import pandas as pd

T = "AIXA.DE"
WB = "http://web.archive.org/web/"
# 2015-2016: dates from archived aixtron.com pages (Wayback); no publication timestamp on the archived pages.
OLD = [
    ("2015-02-24", "Q4", "2014Q4", WB + "20150327000427/http://www.aixtron.com:80/en/investors/financial-news/detail/news/aixtron-anticipates-growth-in-all-technology-areas-and-further-improvement-of-results-in-2015"),
    ("2015-04-28", "Q1", "2015Q1", WB + "20151001141203/http://www.aixtron.com/en/investors/financial-news/detail/news/aixtron-earnings-position-improved-outlook-confirmed/"),
    ("2015-07-28", "Q2", "2015Q2", WB + "20151001090518/http://www.aixtron.com/en/investors/financial-news/detail/news/aixtron-order-backlog-supports-strong-growth-in-h22015/"),
    ("2015-10-13", "profit_warning", "2015FY", WB + "20160707061459/http://www.aixtron.com/en/investors/financial-news/archive-2015/page/2/"),
    ("2015-10-27", "Q3", "2015Q3", WB + "20160120210423/http://www.aixtron.com:80/en/investors/financial-news/detail/aixtron-umsatzwachstum-in-q32015-auf-breiter-basis"),
    ("2015-12-09", "trading_update", "2015Q4", WB + "20160526135435/http://www.aixtron.com:80/en/press/press-releases/archive-2015/detail/aixtron-se-einigt-sich-mit-sanan-optoelectronics-auf-erhebliche-reduzierung-des-auftragsvolumens"),
    ("2016-02-23", "Q4", "2015Q4", WB + "20170831154415/https://www.aixtron.com/de/investoren/finanznachrichten/archiv-2016/page/2/"),
    ("2016-04-26", "Q1", "2016Q1", WB + "20160523111528/http://www.aixtron.com:80/en/press/press-releases/detail/aixtron-auftragseingaenge-und-auftragsbestand-im-ersten-quartal-2016-deutlich-gestiegen"),
    ("2016-08-11", "Q2", "2016Q2", WB + "20160813182609/http://www.aixtron.com:80/en/press/press-releases/detail/aixtron-herausforderndes-h12016-im-rahmen-der-erwartungen/"),
    ("2016-11-08", "Q3", "2016Q3", WB + "20161114200207/http://www.aixtron.com:80/en/press/press-releases/detail/aixtron-auftragseingangs-und-umsatzentwicklung-in-q32016-stuetzen-prognose-fuer-das-geschaeftsjahr-2016/"),
]
# 2017+: (list_date, event_type, fiscal_period, preferred src) ; times come from EQS/DGAP header on the aixtron.com page
NEW = [
    ("2017-02-23", "Q4", "2016Q4"), ("2017-04-25", "Q1", "2017Q1"), ("2017-07-25", "Q2", "2017Q2"),
    ("2017-10-26", "Q3", "2017Q3"), ("2018-02-27", "Q4", "2017Q4"), ("2018-04-26", "Q1", "2018Q1"),
    ("2018-07-26", "Q2", "2018Q2"), ("2018-10-30", "Q3", "2018Q3"), ("2019-02-26", "Q4", "2018Q4"),
    ("2019-04-30", "Q1", "2019Q1"), ("2019-07-25", "Q2", "2019Q2"), ("2019-10-24", "Q3", "2019Q3"),
    ("2020-02-27", "Q4", "2019Q4"), ("2020-04-30", "Q1", "2020Q1"), ("2020-07-23", "Q2", "2020Q2"),
    ("2020-10-29", "Q3", "2020Q3"), ("2021-02-25", "Q4", "2020Q4"), ("2021-04-29", "Q1", "2021Q1"),
    ("2021-06-09", "trading_update", "2021FY"), ("2021-07-29", "Q2", "2021Q2"), ("2021-11-04", "Q3", "2021Q3"),
    ("2022-02-24", "Q4", "2021Q4"), ("2022-05-05", "Q1", "2022Q1"), ("2022-07-28", "Q2", "2022Q2"),
    ("2022-10-27", "Q3", "2022Q3"), ("2023-02-28", "Q4", "2022Q4"), ("2023-04-27", "Q1", "2023Q1"),
    ("2023-07-27", "Q2", "2023Q2"), ("2023-10-26", "Q3", "2023Q3"), ("2024-02-29", "Q4", "2023Q4"),
    ("2024-04-25", "Q1", "2024Q1"), ("2024-07-04", "profit_warning", "2024Q2"), ("2024-07-25", "Q2", "2024Q2"),
    ("2024-10-31", "Q3", "2024Q3"), ("2025-02-27", "Q4", "2024Q4"), ("2025-04-30", "Q1", "2025Q1"),
    ("2025-07-31", "Q2", "2025Q2"), ("2025-10-17", "profit_warning", "2025Q3"), ("2025-10-30", "Q3", "2025Q3"),
    ("2026-02-26", "Q4", "2025Q4"), ("2026-04-14", "prelim", "2026Q1"), ("2026-04-30", "Q1", "2026Q1"),
    ("2026-07-30", "Q2", "2026Q2"), ("2026-10-15", "prelim", "2026Q3"),
]
SCHEDULED = {"Q1", "Q2", "Q3", "Q4"}


def main():
    ts = pd.read_csv(os.path.join(irlib.raw_dir(T), "news_timestamps.csv"), dtype=str).fillna("")
    a = pd.read_csv(os.path.join(irlib.raw_dir(T), "listing_all.csv"), dtype=str).fillna("")
    rows = []
    for d, et, fp, url in OLD:
        # regular results: verified BMO convention (07:25-07:48 on every timestamped 2017-2026 release); ad-hocs UNKNOWN
        rows.append({"ticker": T, "event_date": d, "event_time_local": "", "timing": "BMO" if et in SCHEDULED else "UNKNOWN",
                     "event_type": et, "fiscal_period": fp, "source_url": url})
    for d, et, fp in NEW:
        c = ts[ts.list_date == d]
        # prefer ad-hoc copy (earliest timestamp) for unscheduled releases, finance copy otherwise
        if len(c):
            c = c.assign(k=c.ts_time.replace("", "99:99")).sort_values(["k"])
            r = c.iloc[0]
            url, hm, tsd = r.url, r.ts_time, r.ts_date
        else:  # Q1 2026 results listed as press release
            r = a[a.date == d].iloc[0]
            url = r.url
            import re
            from aixa_news import parse_ts
            p = [f for f in os.listdir(os.path.join(irlib.raw_dir(T), "news")) if f.startswith(d)]
            tsd, hm, _ = parse_ts(irlib.html_to_text(open(os.path.join(irlib.raw_dir(T), "news", p[0]), "rb").read()))
        if tsd and tsd != d:
            print("WARN date mismatch", d, tsd)
        timing = irlib.timing_class(hm) if hm else ("BMO" if et in SCHEDULED else "UNKNOWN")
        rows.append({"ticker": T, "event_date": d, "event_time_local": hm, "timing": timing, "event_type": et,
                     "fiscal_period": fp, "source_url": url})
    df = irlib.write_events(T, rows)
    print(len(df), df.event_date.min(), df.event_date.max())
    print(df.timing.value_counts().to_dict(), df.event_type.value_counts().to_dict())
    print("no-time rows:", df[df.event_time_local.astype(str).isin(["", "nan"])].event_date.tolist())


if __name__ == "__main__":
    main()
