"""Build data/processed/ir/SU.PA_events.csv.

Dates: Schneider IR results table (results_table.json) + AMF/DILA filings for
2026.  Times: AMF/DILA 'flux-amf-new-prod' deposit timestamps (wire
dissemination), converted to wall-clock with the record's own offset field
(2013-2016 records carry a fixed +01:00 offset, so tz_convert would be 1h off
in summer).  Gaps filled from the 2018 financial calendar (press release at
7:30am local time) and call transcripts (morning call => BMO)."""
import os, sys, json
from datetime import datetime
import pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from irlib import *

T = "SU.PA"
P = os.path.join(RAW_IR, T, "pages")
amf = pd.read_csv(os.path.join(P, "infofin_records_flat.csv"))
amf["local"] = pd.to_datetime(amf["local"])
amf["d"] = amf.local.dt.strftime("%Y-%m-%d")
amf["title"] = amf.title.astype(str)
RES_PAT = (r"r[ée]sultat|results|revenue|chiffre d|trimestre|quarter|semestr|half|"
           r"comptes|accounts|performance|turnover|Communicated under|Communiqués au titre|"
           r"Communiqué sur|Document availability|growth|croissance|rebound|rebond|record|2020 année")

tab = json.load(open(os.path.join(P, "results_table.json")))
QMAP = [("Q1", ("Q1", 1)), ("Half", ("H1", 2)), ("Q3", ("Q3", 3)), ("Full", ("FY", 4)), ("Annual", ("FY", 4))]
ev = []
for r in tab:
    hit = next((v for k, v in QMAP if r["title"].startswith(k)), None)
    if not hit:
        continue
    d = datetime.strptime(r["date"].strip(), "%B %d, %Y").strftime("%Y-%m-%d")
    if d < "2015-01-01":
        continue
    rel = next((u for u in r["urls"] if "release" in u.lower() or "revenues-" in u.lower()), r["urls"][0] if r["urls"] else "")
    rel = ("https://www.se.com" + rel) if rel.startswith("/") else rel
    ev.append({"event_date": d, "event_type": hit[0], "fiscal_period": f"{r['year']}Q{hit[1]}", "ir_url": rel})
for d, et, fp, u in [("2026-02-26", "FY", "2025Q4", None), ("2026-04-30", "Q1", "2026Q1", "https://www.se.com/ww/en/assets/pdf/release-q1-revenues-2026"),
                     ("2026-07-30", "H1", "2026Q2", "https://www.se.com/ww/en/assets/pdf/release-hy-results-2026"),
                     ("2026-10-16", "Q3", "2026Q3", "https://www.se.com/ww/en/assets/pdf/release-Q3-revenues-2026")]:
    if not any(e["event_date"] == d for e in ev):
        ev.append({"event_date": d, "event_type": et, "fiscal_period": fp, "ir_url": u})

CAL2018 = "https://fr.ftp.opendatasoft.com/datadila/INFOFI/ECO/2018/01/FCECO045516_20180105.pdf"
rows = []
for e in ev:
    same = amf[(amf.d == e["event_date"]) & amf.title.str.contains(RES_PAT, case=False, regex=True)]
    same = same[~same.title.str.contains("droits de vote|voting rights|bond issue|obligataire|Rapport financier semestriel$", case=False, regex=True)]
    row = {"event_date": e["event_date"], "event_type": e["event_type"], "fiscal_period": e["fiscal_period"]}
    if len(same):
        first = same.sort_values("local").iloc[0]
        row["event_time_local"] = first.local.strftime("%H:%M")
        eng = same[same.title.str.contains(r"[A-Za-z]", regex=True) & ~same.title.str.contains("[éèà]|Communiqu|Rapport|Etats|Chiffre", regex=True)]
        row["source_url"] = (eng.sort_values("local").iloc[0].url if len(eng) else first.url)
    else:
        row["event_time_local"] = ""
        row["source_url"] = e["ir_url"]
    rows.append(row)

# --- manual evidence for releases without an AMF timestamp
fix = {
    "2018-07-26": ("07:30", "", CAL2018),   # 2018 financial calendar: press release at 7:30am local
    "2018-10-25": ("07:30", "", CAL2018),
    "2017-02-16": ("", "BMO", None),        # call 16 Feb 2017 8:30am GMT (transcript header); release before
    "2019-10-24": ("", "BMO", None),        # AMF deposit was late (25 Oct 14:11); morning call per transcript
}
for r in rows:
    if r["event_date"] in fix:
        t, timing, src = fix[r["event_date"]]
        r["event_time_local"] = t
        if timing:
            r["timing"] = timing
        if src:
            r["source_url"] = src

# --- investor days / CMDs (AMF inside-information releases)
cmd = [("2015-02-19", "2014 Annual Results and Investor Day"), ("2017-12-12", "Digital Day for investors"),
       ("2019-06-26", "Capital Markets Day"), ("2020-11-16", "virtual ESG Investor Day"),
       ("2021-11-30", "Capital Markets Day"), ("2023-11-09", "Capital Markets Day"),
       ("2024-12-02", "India specific Investor"), ("2025-12-11", "Capital Markets Day")]
for d, key in cmd:
    s = amf[(amf.d == d)]
    if d == "2015-02-19":
        s = s[s.title.str.startswith("Communicated under the obligation to provide permanent information / Other")]
    else:
        s = s[s.title.str.contains(key.split()[0] if d != "2021-11-30" else "Strategic Roadmap", case=False)]
    s = s.sort_values("local")
    rows.append({"event_date": d, "event_type": "CMD", "fiscal_period": "",
                 "event_time_local": s.iloc[0].local.strftime("%H:%M") if len(s) else "",
                 "source_url": s.iloc[0].url if len(s) else ""})

# --- unscheduled inside-information update on results (non-cash DTA write-down)
s = amf[(amf.d == "2017-01-09") & amf.title.str.contains("deferred tax", case=False)]
rows.append({"event_date": "2017-01-09", "event_type": "trading_update", "fiscal_period": "2016Q4",
             "event_time_local": s.iloc[0].local.strftime("%H:%M"), "source_url": s.iloc[0].url})

p = write_events(T, rows)
df = pd.read_csv(p)
print(p, len(df), df.event_date.min(), df.event_date.max())
print(df.groupby(df.event_date.str[:4]).size().to_dict())
print(df.timing.value_counts().to_dict(), "with time:", df.event_time_local.notna().sum())
print(df[df.event_type.isin(["Q1", "H1", "Q3", "FY"])].event_time_local.value_counts().head(12).to_dict())
