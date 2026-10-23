"""Soitec events from downloaded press releases (datelines) + agenda statements ('after market close')."""
import os
import re
import sys
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import irlib  # noqa: E402

T = "SOI.PA"
df = pd.read_csv(os.path.join(irlib.raw_dir(T), "pr_index.csv"))
ev, docs = [], []
for _, r in df.iterrows():
    t = re.sub(r"\s+", " ", irlib.pdf_to_text(r.local))
    head = t[:600].upper()
    fn = os.path.basename(r.local).lower()
    if "trading-update" in fn:
        et, fy, q = "trading_update", 2027, 2
    elif "results" in fn and "fy24" in fn:      # FY24 results presentation dated the call day
        continue
    else:
        # Soitec's regular calendar (FY ends 31 Mar): month of release -> report type
        y, mth = int(r.date[:4]), int(r.date[5:7])
        if mth in (1, 2):
            et, fy = "Q3", y
        elif mth in (3, 4):
            et, fy = "Q4", y
        elif mth in (5, 6):
            et, fy = "FY", y
        elif mth in (7, 8):
            et, fy = "Q1", y + 1
        elif mth == 10:
            et, fy = "Q2", y + 1
        elif mth in (11, 12):
            et, fy = "H1", y + 1
        else:
            et, fy = "UNK", None
    if fy is None or et == "UNK":
        print("unclassified", r.date, fn, head[:120])
        continue
    if et == "trading_update":
        fp = "FY2027Q2"
    elif et == "H1":
        fp = f"FY{fy}H1"
    elif et == "FY":
        fp = f"FY{fy}"
    else:
        fp = f"FY{fy}{et}"
    ev.append(dict(event_date=r.date, event_time_local="", timing="AMC" if et != "trading_update" else "UNKNOWN",
                   event_type=et, fiscal_period=fp, source_url=r.url))
    docs.append(dict(local=r.local, url=r.url, fp=fp, et=et, date=r.date))
# FY24 results (press release itself not on the page; date/timing from the Q3'24 release agenda)
ev.append(dict(event_date="2024-05-22", event_time_local="", timing="AMC", event_type="FY", fiscal_period="FY2024",
               source_url="https://www.soitec.com/docs/default-source/financial-documents/2023-2024/en/pr-q3.pdf"))
# 2026 financial targets release (FY21 results PR: 'issued on June 10th, 2021 before market opens')
ev.append(dict(event_date="2021-06-10", event_time_local="", timing="BMO", event_type="CMD", fiscal_period="FY2022Q1",
               source_url="https://www.soitec.com/docs/default-source/financial-reports/2020-2021/en/pr---soitec-pr-fy21-results-va.pdf"))
# FY18 results: date + timing from the Q4'18 sales release agenda ("June 13th, 2018, after market close")
ev.append(dict(event_date="2018-06-13", event_time_local="", timing="AMC", event_type="FY", fiscal_period="FY2018",
               source_url="https://www.soitec.com/docs/default-source/financial-reports/2017-2018/en/en---soitec_fy_18_va.pdf"))
# FY2016 (Apr 2015-Mar 2016) releases located via web search of soitec.com / AMF (DILA) archive; no time stated
for d, et, fp, u in [
    ("2015-10-19", "Q2", "FY2016Q2", "https://www.soitec.com/media/financialreleasedocuments/92/file/soitec_q2_sales_19102015.pdf"),
    ("2015-11-18", "H1", "FY2016H1", "https://soitec.com/home/group/newsroom/press-releases/2015/11/18/half-year-results-for-fy-2015-2016"),
    ("2016-01-20", "Q3", "FY2016Q3", "https://echanges.dila.gouv.fr/OPENDATA/AMF/CNS/2016/04/FCCNS144013_20160425.pdf"),
    ("2016-05-02", "prelim", "FY2016", "https://echanges.dila.gouv.fr/OPENDATA/AMF/CNS/2016/05/FCCNS144453_20160502.pdf"),
    ("2016-06-16", "FY", "FY2016", "https://echanges.dila.gouv.fr/OPENDATA/AMF/CNS/2016/06/FCCNS145762_20160616.pdf")]:
    ev.append(dict(event_date=d, event_time_local="", timing="UNKNOWN", event_type=et, fiscal_period=fp, source_url=u))
evd = pd.DataFrame(ev).drop_duplicates(["event_date", "event_type"])
evd.to_csv(os.path.join(irlib.raw_dir(T), "events_draft.csv"), index=False)
p, out = irlib.write_events(T, evd.to_dict("records"))
print(p, len(out))
pd.DataFrame(docs).drop_duplicates("fp").to_csv(os.path.join(irlib.raw_dir(T), "doc_map.csv"), index=False)
print(evd.sort_values("event_date")[["event_date", "event_type", "fiscal_period"]].to_string())
