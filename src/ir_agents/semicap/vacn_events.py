"""Build VACN.SW release calendar (2016 IPO -> 2026-10).
Dates: VAT news archive (vatgroup.com/news?year=...) + dated PDFs on the financial-reports page.
Times (Europe/Zurich local):
  * EQS News company feed (times displayed in CET/CEST; verified against dpa-AFX copy '23.07.2025 / 06:30 CET/CEST')
  * dpa-AFX copy of EQS ad hoc for 2026-01-15 (not in EQS English list)
  * VAT invitations stating 'VAT will publish its ... at 7am CET/CEST' (2018-2021)
  * Convention 07:00 for scheduled results releases 2016-08..2021-04 without a direct stamp (verified on stated/stamped
    results releases in 2018, 2019, 2020, 2021 - all 07:00-07:04, no exceptions). Listed in notes as convention-based.
Output: data/processed/ir/VACN.SW_events.csv and data/raw/ir/VACN.SW/events_detail.json (incl. time_source)."""
import os
import sys
import re
import json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from irlib import raw_dir, write_events, timing_class

T = "VACN.SW"
R = raw_dir(T)

# (date, event_type, fiscal_period, title-regex-or-None, source_url override)
MANUAL = [
    # Q1/Q3 2017 trading updates are on the financial-reports page, not in the news archive (dates from PDF datelines)
    ("2017-05-17", "trading_update", "2017Q1",
     "https://www.vatgroup.com/files/live/sites/vat/files/financial_reports/2017/vat_media_release_q1_2017_trading_update.pdf"),
    ("2017-10-17", "trading_update", "2017Q3",
     "https://www.vatgroup.com/files/live/sites/vat/files/financial_reports/2017/vat-media-release-on-q3-2017-trading-update.pdf"),
]

# classification of news-archive investor items: (regex on title, event_type, period builder from title year)
CLASS = [
    (r"Capital Markets Day (20\d\d)$|Media Release Capital Markets Day (20\d\d)|Media Release on Capital Markets Day (20\d\d)", "CMD", None),
    (r"Q4 and FY (20\d\d) Preliminary|^VAT Media release - (20\d\d) Sales", "prelim", "{y}Q4"),
    (r"Q2 and HY (20\d\d) Preliminary|Q2 (20\d\d) Trading Update|Sales Half Year (20\d\d)|Half-year (20\d\d) net sales, EBITDA",
     "prelim", "{y}Q2"),
    (r"ahead of Q3 (20\d\d)", "profit_warning", "{y}Q3"),
    (r"Q([13]) (20\d\d) (?:Trading Update|trading update|Results)", "trading_update", "{y}Q{q}"),
    (r"Half Year Results (20\d\d)|Half Year (20\d\d) Report|Half Year (20\d\d) Results|Half-Year (20\d\d) Results|H1 (20\d\d) Results|half-year (20\d\d) results|Half-year (20\d\d) Results|Q2 and H1 (20\d\d) results",
     "H1", "{y}H1"),
    (r"Full-Year Results (20\d\d)|Full-Year (20\d\d)|Full Year (20\d\d)|full-year (20\d\d) results|Full-Year (20\d\d) Results", "FY", "{y}FY"),
    (r"[Ss]hort [Tt]ime [Ww]ork", "trading_update", "STW"),
]

SLUG_OVERRIDE = {
    # generic 'Media Release' titles -> determined from text
    "fixed/listarticle/2021/10/medienmitteilung.html": ("trading_update", "2021Q3"),
    "news/medienmitteilung": ("FY", "2021FY"),  # 2022-03-03 FY2021 results
    "umsatzwachstum-von-23-im-dritten-quartal": ("trading_update", "2025Q3"),
    "sehr-starker-auftragseingang-im-ersten-quartal": ("profit_warning", "2026Q1"),
    "vat-mit-rekordquartal-bei-auftragseingang": ("trading_update", "2026Q3"),
    "medienmitteilung-zum-lagebericht-des-4-quartals-20": ("prelim", "2025Q4"),
    "medienmitteilung-zum-lagebericht-q1-2026": ("trading_update", "2026Q1"),
    "vat-mit-rekordergebnissen-bei-umsatz-ebitda-ebitda": ("prelim", "2021Q4"),
    "rekordergebnisse-im-2-quartal-und-1-halbjahr-2021": ("H1", "2021H1"),
    "vat-setzt-starker-wachstum-fort": ("prelim", "2021Q2"),
}
EXCLUDE = re.compile(r"invitation|einladung|conference call|webcast|investor meeting|analyst conference|disclosure|block sale|ceo|cfo|coo|board|general meeting|bond|refinanc|"
                     r"sustainab|award|krebs|gerber|announcement juergen|date change|over-allotment|ipo|exit from|"
                     r"group executive|atonarp|headquarters|investiert|160 million|media release - (september|october) 2016",
                     re.I)


def quarter_of(date):
    y, m = int(date[:4]), int(date[5:7])
    return f"{y}Q{(m - 1) // 3 + 1}"


def classify(it):
    url = it["url"]
    for slug, (et, fp) in SLUG_OVERRIDE.items():
        if slug in url and (slug != "news/medienmitteilung" or url.rstrip("/").endswith("news/medienmitteilung")):
            return et, fp
    title = " ".join(it["title"].split())
    if EXCLUDE.search(title) and not re.search(r"short time work", title, re.I):
        return None, None
    for pat, et, per in CLASS:
        m = re.search(pat, title)
        if m:
            g = [x for x in m.groups() if x]
            if et == "CMD":
                return "CMD", ""
            if per == "STW":
                return et, quarter_of(it["date"])
            if "{q}" in per:
                return et, per.format(q=g[0], y=g[1])
            return et, per.format(y=g[0])
    return None, None


def norm_title(s):
    return re.sub(r"[^a-z0-9]+", " ", s.lower()).strip()


def main():
    idx = json.load(open(os.path.join(R, "news_index.json")))
    eqs = json.load(open(os.path.join(R, "eqs_index.json")))
    eqs_by_date = {}
    for e in eqs:
        if e.get("date"):
            eqs_by_date.setdefault(e["date"], []).append(e)
    events = []
    for it in idx:
        if "Investors" not in it["tags"] or not it["date"]:
            continue
        et, fp = classify(it)
        if not et:
            continue
        events.append({"event_date": it["date"], "event_type": et, "fiscal_period": fp, "source_url": it["url"],
                       "title": it["title"]})
    for d, et, fp, url in MANUAL:
        events.append({"event_date": d, "event_type": et, "fiscal_period": fp, "source_url": url, "title": "(PDF)"})
    # de-duplicate same date/type (news page + pdf entries for 2016-2020)
    seen, ev2 = set(), []
    for e in sorted(events, key=lambda x: (x["event_date"], x["event_type"], 0 if x["source_url"].endswith(".pdf") else 1)):
        k = (e["event_date"], e["event_type"], e["fiscal_period"])
        if k in seen:
            continue
        seen.add(k)
        ev2.append(e)
    events = ev2

    stated = json.load(open(os.path.join(R, "stated_times.json"))) if os.path.exists(
        os.path.join(R, "stated_times.json")) else {}
    for e in events:
        d = e["event_date"]
        e["event_time_local"], e["time_source"] = "", ""
        # 1) EQS feed: ad-hoc items on that date (pick earliest Ad-hoc not about CEO/Atonarp unless only one)
        cands = [x for x in eqs_by_date.get(d, []) if x["kind"].lower().startswith("ad")]
        cands = [x for x in cands if not re.search(r"CEO|Atonarp|Executive Committee|Board", x["title"])] or []
        if cands:
            best = sorted(cands, key=lambda x: x["time"])[0]
            e["event_time_local"], e["time_source"] = best["time"], "EQS feed: " + best["url"]
        elif d in stated:
            e["event_time_local"], e["time_source"] = stated[d]["time"], stated[d]["source"]
        elif d < "2021-05-01" and e["event_type"] in ("H1", "FY", "trading_update", "prelim", "CMD") \
                and not re.search(r"short time", e["title"], re.I):
            e["event_time_local"], e["time_source"] = "07:00", "CONVENTION (07:00 verified 2018-2021)"
        e["timing"] = timing_class(e["event_time_local"])
    rows = [{k: e[k] for k in ("event_date", "event_time_local", "timing", "event_type", "fiscal_period", "source_url")}
            for e in events]
    for r in rows:
        r["ticker"] = T
    write_events(T, rows)
    json.dump(events, open(os.path.join(R, "events_detail.json"), "w"), indent=1)
    print("events", len(events), events[0]["event_date"], events[-1]["event_date"])
    for e in events:
        print(e["event_date"], e["event_time_local"] or "--:--", e["timing"][:4], e["event_type"][:8].ljust(8),
              e["fiscal_period"].ljust(7), e["time_source"][:22].ljust(22), "|", e["title"][:55])


if __name__ == "__main__":
    main()
