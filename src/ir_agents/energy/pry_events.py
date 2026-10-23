"""Build data/processed/ir/PRY.MI_events.csv.
Timing evidence: SDIR cover sheets of eMarket Storage PDFs ('Data/Ora Inizio Diffusione'), parsed into
data/raw/ir/PRY.MI/sdir_covers.csv by pry_sdir_covers.py; FY2014 from the 1Info storage API (dataDiffusione).
For each event the earliest dissemination stamp among its regulatory filings (IT/EN versions) is used."""
import sys; sys.path.insert(0, "/Users/sinamirzaei/Documents/aimapping/src/ir_agents/energy"); import irlib
import json, os
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
T = "PRY.MI"
EM = "https://www.emarketstorage.it/sites/default/files/comunicati/"
covers = {r["url"].rsplit("/", 1)[-1].replace(".pdf", ""): r for r in irlib.read_csv(os.path.join(irlib.RAW_IR, T, "sdir_covers.csv")) if r.get("diffusione") and r.get("n", "").startswith("0902-")}
cover_url = {k: r["url"] for k, r in covers.items()}
NEWS = {r["date"] + "|" + r["title"][:40]: r["url"] for r in irlib.read_csv(os.path.join(irlib.RAW_IR, T, "press_release_index_en.csv"))}
def news(date, title_start):
    for k, u in NEWS.items():
        if k.startswith(date + "|" + title_start[:20]):
            return u
    return ""
# (date, event_type, fiscal_period, [sdir doc keys], fallback dict)
EV = [
 ("2015-02-25", "FY", "FY2014", ["1INFO"], None),
 ("2015-05-07", "Q1", "FY2015Q1", ["20150507_2216", "20150507_2217"], None),
 ("2015-07-30", "H1", "FY2015H1", ["20150730_4711", "20150730_4712"], None),
 ("2015-11-05", "Q3", "FY2015Q3", ["20151105_7547", "20151105_7548"], None),
 ("2016-02-24", "FY", "FY2015", ["20160224_11159", "20160224_11160"], None),
 ("2016-05-10", "Q1", "FY2016Q1", ["20160510_15624", "20160510_15625"], None),
 ("2016-07-28", "H1", "FY2016H1", ["20160728_18863", "20160728_18864"], None),
 ("2016-11-08", "Q3", "FY2016Q3", ["20161108_22230", "20161108_22231"], None),
 ("2017-03-01", "FY", "FY2016", ["20170301_26408", "20170301_26410"], None),
 ("2017-05-10", "Q1", "FY2017Q1", ["20170510_30998", "20170510_30999"], None),
 ("2017-07-27", "H1", "FY2017H1", ["20170727_34085", "20170727_34087"], None),
 ("2017-11-07", "Q3", "FY2017Q3", ["20171107_37395", "20171107_37396"], None),
 ("2018-02-27", "FY", "FY2017", ["20180227_41289", "20180227_41290"], None),
 ("2018-05-10", "Q1", "FY2018Q1", ["20180510_46836", "20180510_46837"], None),
 ("2018-06-20", "trading_update", "FY2018", ["PROBE_20180620"],
  {"timing": "AMC", "source_url": news("2018-06-20", "INFORMATION DOCUMENT")}),
 ("2018-06-22", "profit_warning", "FY2018", ["20180622_49082", "20180622_49083"], None),
 ("2018-09-18", "H1", "FY2018H1", ["20180918_52181", "20180918_52182"], None),
 ("2018-11-14", "Q3", "FY2018Q3", ["20181114_54392", "20181114_54393"], None),
 ("2019-03-05", "FY", "FY2018", ["20190305_58108", "20190305_58109"], None),
 ("2019-04-17", "profit_warning", "FY2018", ["20190417_61697", "20190417_61698"], None),
 ("2019-05-13", "Q1", "FY2019Q1", ["20190513_63033", "20190513_63034"], None),
 ("2019-08-01", "H1", "FY2019H1", ["20190801_66355", "20190801_66356"], None),
 ("2019-11-12", "Q3", "FY2019Q3", ["20191112_69812", "20191112_69813"], None),
 ("2020-03-05", "FY", "FY2019", ["PROBE_20200305"],
  {"timing": "UNKNOWN", "source_url": news("2020-03-05", "Prysmian S.p.A. Results at 31")}),
 ("2020-05-12", "Q1", "FY2020Q1", ["20200512_79095", "20200512_79098"], None),
 ("2020-07-30", "H1", "FY2020H1", ["20200730_82845", "20200730_82846"], None),
 ("2020-10-29", "Q3", "FY2020Q3", ["20201029_86191", "20201029_86192"], None),
 ("2021-03-10", "FY", "FY2020", ["20210310_91337", "20210310_91338"], None),
 ("2021-05-13", "Q1", "FY2021Q1", ["20210513_96935", "20210513_96936"], None),
 ("2021-07-28", "H1", "FY2021H1", ["20210728_100637", "20210728_100638"], None),
 ("2021-11-11", "Q3", "FY2021Q3", ["20211111_104611", "20211111_104612"], None),
 ("2022-03-01", "FY", "FY2021", ["20220301_108631", "20220301_108632"], None),
 ("2022-05-12", "Q1", "FY2022Q1", ["20220512_114822", "20220512_114823"], None),
 ("2022-07-28", "H1", "FY2022H1", ["20220728_118470", "20220728_118471"], None),
 ("2022-11-10", "Q3", "FY2022Q3", ["20221110_122409", "20221110_122410"], None),
 ("2023-03-09", "FY", "FY2022", ["20230309_126453", "20230309_126454"], None),
 ("2023-05-11", "Q1", "FY2023Q1", ["20230511_131953", "20230511_131954"], None),
 ("2023-07-27", "H1", "FY2023H1", ["20230727_135119", "20230727_135120"], None),
 ("2023-10-05", "CMD", "", ["20231005_137719", "20231005_137720"], None),
 ("2023-11-09", "Q3", "FY2023Q3", ["20231109_138900", "20231109_138901"], None),
 ("2024-02-29", "FY", "FY2023", ["20240229_142658", "20240229_142659"], None),
 ("2024-05-09", "Q1", "FY2024Q1", [], None),
 ("2024-08-01", "H1", "FY2024H1", [], None),
 ("2024-10-31", "Q3", "FY2024Q3", [], None),
 ("2025-02-27", "FY", "FY2024", [], None),
 ("2025-03-26", "CMD", "", ["20250326_162884", "20250326_162885"], None),
 ("2025-05-08", "Q1", "FY2025Q1", [], None),
 ("2025-07-31", "H1", "FY2025H1", [], None),
 ("2025-10-30", "Q3", "FY2025Q3", [], None),
 ("2026-02-26", "FY", "FY2025", [], None),
 ("2026-04-30", "Q1", "FY2026Q1", [], None),
 ("2026-07-30", "H1", "FY2026H1", [], None),
]
# for 2024+ results: all covers on that date whose Oggetto is a results title
def date_keys(d):
    ymd = d.replace("-", "")
    return [k for k, r in covers.items() if k.startswith(ymd + "_") and ("isultati al" in r["oggetto"] or "results" in r["oggetto"].lower()) and "presentation" not in r["oggetto"].lower()]
# probe results (pry_probe_sdir.py) recorded as covers too
rows, missing = [], []
for d, et, fp, keys, fb in EV:
    if not keys:
        keys = date_keys(d)
    if keys == ["1INFO"]:
        js = json.load(open(os.path.join(irlib.RAW_IR, T, "1info_index.json")))
        cand = [r for r in js if r.get("dataDiffusione") and ((r.get("oggetto") or "").lower().endswith("full year 2014 results") or (r.get("oggetto") or "").lower().endswith("risultati al 31 dicembre 2014"))]
        ts = min(r["dataDiffusione"] for r in cand)
        loc = datetime.fromtimestamp(ts, timezone.utc).astimezone(ZoneInfo("Europe/Rome"))
        rows.append({"event_date": d, "event_time_local": loc.strftime("%H:%M"), "event_type": et, "fiscal_period": fp,
                     "source_url": "https://www.1info.it/PORTALE1INFO"})  # 1Info storage API (POST /API/Comunicati, emittente=902), see notes
        assert loc.strftime("%Y-%m-%d") == d
        continue
    if keys and keys[0].startswith("PROBE_"):
        ymd = keys[0].split("_")[1]
        keys = [k for k, r in covers.items() if k.startswith(ymd + "_")]
    got = [(covers[k]["diffusione"], k) for k in keys if k in covers]
    if got:
        dif, k = min(got)
        assert dif[:10] == d, (d, dif, k)
        rows.append({"event_date": d, "event_time_local": dif[11:16], "event_type": et, "fiscal_period": fp,
                     "source_url": cover_url[k]})
    else:
        missing.append(d)
        fb = fb or {"timing": "UNKNOWN", "source_url": ""}
        rows.append({"event_date": d, "event_time_local": "", "timing": fb["timing"], "event_type": et,
                     "fiscal_period": fp, "source_url": fb["source_url"]})
irlib.write_events(T, rows)
print("missing SDIR stamp:", missing)
from collections import Counter
print(Counter(irlib.classify_timing(T, r["event_time_local"]) if r["event_time_local"] else r.get("timing") for r in rows))
