"""Build data/processed/ir/BESI.AS_events.csv (2015-01 .. 2026-10).
Sources: Euronext Live company press-release list (exact publication timestamps, May-2018 onward);
Besi call-invite press releases (pre-announced publication time, 2015-2018) and press-release pages (Wayback captures);
Besi financial calendar / investor-day pages and presentation PDFs for analyst meetings / CMDs."""
import os, sys, re, datetime as dt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pandas as pd
import irlib

T = "BESI.AS"
SCR = "/private/tmp/claude-501/-Users-sinamirzaei-Documents-aimapping/57e0a0d0-6441-40ef-828b-57eeb87e7b21/scratchpad"
BESI = "https://www.besi.com/investor-relations/press-releases"
WB = "https://web.archive.org/web/2023/https://www.besi.com"

def euronext_events():
    df = pd.read_csv(os.path.join(SCR, "besi_euronext.csv"))
    ev = []
    for _, r in df.iterrows():
        m = re.match(r"(\d{2} \w{3} \d{4}) (\d{2}:\d{2}) (CET|CEST)", r.released)
        d = dt.datetime.strptime(m.group(1), "%d %b %Y").date().isoformat()
        hhmm = m.group(2)
        t = r.title
        q = re.search(r"Announces (?:Annual and )?Q([1-4])-(\d{2,4})(?: and (?:H1-\d\d|Full Year \d{4}))? Results", t)
        if q:
            yy = q.group(2); yy = yy if len(yy) == 4 else "20" + yy
            ev.append(dict(event_date=d, event_time_local=hhmm, event_type="Q" + q.group(1),
                           fiscal_period=f"{yy}Q{q.group(1)}", source_url=r.href, note=t))
            continue
        if re.search(r"Adjusts Q2-18 Revenue Guidance", t):
            ev.append(dict(event_date=d, event_time_local=hhmm, event_type="profit_warning", fiscal_period="2018Q2", source_url=r.href, note=t))
        elif re.search(r"Trading Update\. Q1-21 Orders", t):
            ev.append(dict(event_date=d, event_time_local=hhmm, event_type="prelim", fiscal_period="2021Q1", source_url=r.href, note=t))
        elif re.search(r"Shah Alam", t):
            ev.append(dict(event_date=d, event_time_local=hhmm, event_type="profit_warning", fiscal_period="2021Q4", source_url=r.href, note=t))
        elif t.strip() == "BE Semiconductor Industries N.V. Announces Trading Update" and d.startswith("2026-01"):
            ev.append(dict(event_date=d, event_time_local=hhmm, event_type="prelim", fiscal_period="2025Q4", source_url=r.href, note=t))
        elif re.search(r"Order for 26 Hybrid Bonding|TCB Next Orders", t):
            fp = "2024Q2" if "26 Hybrid" in t else "2025Q2"
            ev.append(dict(event_date=d, event_time_local=hhmm, event_type="trading_update", fiscal_period=fp, source_url=r.href, note=t + " [order announcement]"))
        elif re.search(r"Investor Day", t):
            ev.append(dict(event_date=d, event_time_local=hhmm, event_type="CMD", fiscal_period="", source_url=r.href, note=t))
    return ev

# Pre-Euronext-list results (Feb-2015 .. Apr-2018): date + time "7.00 a.m. CET" stated in Besi's own call-invite releases;
# date confirmed by the results press-release page (Wayback capture of besi.com).
PRE = [  # (fiscal_period, date, results-release slug or invite slug)
    ("2014Q4", "2015-02-26", "2015/details/besi-announces-2014-fourth-quarter-and-full-year-results-release-conference-call-and-webcast-date/"),
    ("2015Q1", "2015-04-30", "2015/details/besi-posts-strong-q1-15-results-revenue-and-net-income-of-eur-949-million-and-eur-175-million-up-356-and-149-respectively-vs-q1-14-orders-up-280-vs-q4-14-revenue-and-profit-exceed-expectations/"),
    ("2015Q2", "2015-07-23", "2015/details/besi-posts-strong-q2-and-h1-15-results-significant-expansion-of-net-cash-position-vs-q2-2014/"),
    ("2015Q3", "2015-10-22", "2015/details/besi-reports-net-income-of-eur-63-million-and-eur-393-million-for-q3-15-and-ytd-15-respectively-net-cash-position-expands-to-eur-1090-million-backlog-indicates-q4-15-revenue-comparable-to-q3-15/"),
    ("2015Q4", "2016-02-25", "2016/details/besi-reports-q4-15-revenue-and-net-income-of-eur-778-million-and-eur-97-million-annual-revenue-and-net-income-of-eur-3492-million-and-eur-490-million-net-cash-position-increases-to-eur-1365-million-proposed-2015-dividend-of-eur-120-per-share/"),
    ("2016Q1", "2016-04-29", "2016/details/besi-reports-q1-16-revenue-and-net-income-of-eur-790-million-and-eur-80-million-respectively-q1-16-orders-increase-by-344-sequentially-vs-q4-15-net-cash-position-increases-to-eur-1484-million/"),
    ("2016Q2", "2016-07-28", "2016/details/besi-reports-q2-16-revenue-of-eur-1090-million-up-38-vs-q1-16-and-net-income-of-eur-240-million-up-200-vs-prior-quarter-results-exceed-expectations/"),
    ("2016Q3", "2016-10-27", "2015/details/article/besi-reports-strong-q3-16-results-revenue-and-net-income-up-by-307-and-1635-respectively-vs"),
    ("2016Q4", "2017-02-23", "2017/details/besi-reports-strong-q4-16-revenue-and-net-income-of-eur-931-million-and-eur-167-million-results-exceed-expectations-solid-2016-performance-with-revenue-and-net-income-up-75-and-333-vs-2015-proposed-2016-dividend-of-eur-174-per-share/"),
    ("2017Q1", "2017-04-25", "2017/details/besi-reports-q1-17-revenue-of-eur-1102-million-and-net-income-of-eur-243-million-q1-17-orders-of-eur-2398-million-increase-1624-vs-q4-16-strong-first-half-2017-business-outlook/"),
    ("2017Q2", "2017-07-27", "2017/details/besi-posts-strong-q2-17-and-h1-17-results-q2-17-revenue-of-eur-1700-million-and-net-income-of-eur-524-million-are-up-56-and-118-respectively-vs-q2-16-h1-17-revenue-and-net-income-up-49-and-140-respectively-vs-h1-16/"),
    ("2017Q3", "2017-10-26", "2017/details/besi-posts-strong-q3-2017-and-ytd-17-results/"),
    ("2017Q4", "2018-02-15", "2018/details/strong-q4-17-results-revenue-and-net-income-of-eur1532-million-and-eur436-million-up-646-and-1611-respectively-vs-q4-16-orders-of-eur1494-million-up-635-vs-q4-16-2017-revenue-and-net-income-up-579-and-1652-respectively-vs-2016/"),
    ("2018Q1", "2018-04-26", "2018/details/be-semiconductor-industries-announces-q1-18-results-solid-performance-as-revenue-and-net-income-up-405-and-527-respectively-vs-q1-17/"),
]
OTHER_PRE = [
    # profit warning, 2015-09-10 (time not documented)
    dict(event_date="2015-09-10", event_time_local="", event_type="profit_warning", fiscal_period="2015Q3",
         source_url=BESI + "/2015/details/be-semiconductor-industries-lowers-q3-15-revenue-guidance/", note="Lowers Q3-15 revenue guidance"),
    dict(event_date="2015-09-01", event_time_local="", event_type="trading_update", fiscal_period="2015Q3",
         source_url=BESI + "/2015/details/be-semiconductor-industries-announces-tcb-orders/", note="TCB orders (order announcement)"),
    # analyst meetings / capital markets / investor days (time = documented event start where stated)
    dict(event_date="2015-06-18", event_time_local="", event_type="CMD", fiscal_period="",
         source_url="https://www.besi.com/fileadmin/data/Investor_Relations/Investor_Presentations/Analyst_Presentation_18_June_2015.pdf", note="Analyst meeting"),
    dict(event_date="2016-06-21", event_time_local="", event_type="CMD", fiscal_period="",
         source_url="https://www.besi.com/fileadmin/data/Investor_Relations/Investor_Presentations/Analyst_Presentation_June_2016.pdf", note="Analyst meeting (date from deck cover)"),
    dict(event_date="2017-06-15", event_time_local="", event_type="CMD", fiscal_period="",
         source_url="https://www.besi.com/investor-relations/financial-calendar/details/article/besi-analyst-meeting/", note="Analyst meeting Amsterdam"),
    dict(event_date="2018-06-14", event_time_local="", event_type="CMD", fiscal_period="",
         source_url="https://www.besi.com/fileadmin/data/Investor_Relations/Investor_Presentations/Analyst_Presentation_June_2018.pdf", note="Analyst meeting (date from deck cover)"),
    dict(event_date="2019-06-06", event_time_local="", event_type="CMD", fiscal_period="",
         source_url="https://www.besi.com/fileadmin/data/Investor_Relations/Investor_Presentations/Analyst_Presentation_060619.pdf", note="Analyst meeting (date from file name)"),
    dict(event_date="2020-06-18", event_time_local="", event_type="CMD", fiscal_period="",
         source_url="https://www.besi.com/fileadmin/data/Investor_Relations/Investor_Presentations/Besi_Analyst_Session_180620.pdf", note="Analyst session (date from file name)"),
    dict(event_date="2021-06-10", event_time_local="16:00", event_type="CMD", fiscal_period="",
         source_url="https://www.besi.com/investor-relations/financial-calendar/details/besi-analyst-meeting/", note="Virtual analyst meeting 4.00 pm CET (financial calendar)"),
    dict(event_date="2022-06-15", event_time_local="", event_type="CMD", fiscal_period="",
         source_url="https://www.besi.com/events/events-shows/details/capital-markets-day-presentation-2022/", note="Capital Markets Day"),
    dict(event_date="2023-06-06", event_time_local="", event_type="CMD", fiscal_period="",
         source_url="https://www.besi.com/investor-relations/financial-calendar/details/besi-capital-markets-day/", note="Capital Markets Day (Radfeld, Austria)"),
    dict(event_date="2024-06-06", event_time_local="", event_type="CMD", fiscal_period="",
         source_url="https://www.besi.com/investor-relations/financial-calendar/details/besis-investor-day/", note="Investor Day (Radfeld, Austria)"),
]

def main():
    ev = euronext_events()
    first_eu = min(e["event_date"] for e in ev)
    for fp, d, slug in PRE:
        assert d < first_eu
        ev.append(dict(event_date=d, event_time_local="07:00", event_type="Q" + fp[-1], fiscal_period=fp,
                       source_url=f"{BESI}/{slug}", note="time = '7.00 a.m. CET' stated in Besi call-invite release"))
    ev += OTHER_PRE
    df = pd.DataFrame(ev).drop_duplicates(["event_date", "event_type", "fiscal_period"])
    df = df[(df.event_date >= "2015-01-01") & (df.event_date <= "2026-10-31")]
    rows = []
    for _, r in df.iterrows():
        rows.append(dict(ticker=T, event_date=r.event_date, event_time_local=r.event_time_local, timezone=irlib.TZ[T],
                         timing=irlib.timing_class(r.event_time_local), event_type=r.event_type,
                         fiscal_period=r.fiscal_period, source_url=r.source_url))
    out = irlib.write_events(T, rows)
    df.sort_values("event_date").to_csv(os.path.join(SCR, "besi_events_annotated.csv"), index=False)
    print(len(out), out.event_date.min(), out.event_date.max())
    print(out.event_type.value_counts().to_dict(), out.timing.value_counts().to_dict())
    # completeness check: every quarter 2014Q4..2026Q3 has a results event
    have = set(out[out.event_type.isin(["Q1", "Q2", "Q3", "Q4"])].fiscal_period)
    need = [f"{y}Q{q}" for y in range(2015, 2027) for q in range(1, 5) if f"{y}Q{q}" <= "2026Q3"] + ["2014Q4"]
    print("missing quarters:", sorted(set(need) - have))

if __name__ == "__main__":
    main()
