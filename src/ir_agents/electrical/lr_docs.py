"""Download Legrand results press releases + slideshows (+ prelim/CMD docs), extract text,
write data/processed/ir/LR.PA_manifest.csv. Usage: lr_docs.py [first_fy]"""
import os, sys, re, json
import pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from irlib import *
TK = "LR.PA"
FIRST = int(sys.argv[1]) if len(sys.argv) > 1 else 2022
reg = json.load(open(os.path.join(RAW_IR, TK, "pages", "regpages_parsed.json")))
ev = pd.read_csv(os.path.join(PROC_IR, f"{TK}_events.csv"), dtype=str).fillna("")
pub = {r.fiscal_period: r.event_date for r in ev.itertuples() if r.event_type in ("Q1", "H1", "Q3", "FY")}


def q_of(t):
    t = t.lower()
    if "full" in t:
        return 4
    if "nine" in t:
        return 3
    if "half" in t:
        return 2
    if "first quarter" in t:
        return 1
    return None


docs = []
for o in reg:
    if not o["hrefs"]:
        continue
    href = o["hrefs"][0]
    url = href if href.startswith("http") else "https://www.legrand.com" + href
    if o["section"] == "Regular information" and o["title"].lower().startswith(("results for", "result for", "release for")):
        q = q_of(o["title"])
        ys = re.findall(r"20\d\d", o["title"])
        fy = int(ys[-1]) if ys else o["page_year"]
        if q:
            docs.append((f"{fy}Q{q}", "release", url))
    elif o["section"] == "Financial presentations":
        q = q_of(o["title"])
        if q:
            docs.append((f"{o['page_year']}Q{q}", "presentation", url))
extra = [  # non-results docs worth keeping (already downloaded by lr_dl_misc.py)
    ("2025Q2", "prelim_release", "https://www.legrand.com/sites/default/files/Documents_PDF_Legrand/Finance/2025/6m/Legrand_Press_Release_Sales_H1_2025-vf_1752729073.pdf", "2025-07-17", "2025-07-17_prelim_release.pdf"),
    ("CMD2024", "cmd_release", "https://www.legrand.com/sites/default/files/Documents_PDF_Legrand/Finance/2024/autres/Legrand_Press_Release_CMD_September-2024_1727107150.pdf", "2024-09-24", "2024-09-24_cmd_release.pdf"),
    ("CMD2024", "cmd_presentation", "https://www.legrand.com/sites/default/files/Documents_PDF_Legrand/Finance/2024/autres/2024-09-20-CMD-2024-Presentation_1727156999.pdf", "2024-09-24", "2024-09-24_cmd_presentation.pdf"),
    ("CMD2026", "cmd_release", "https://www.legrand.com/sites/default/files/Documents_PDF_Legrand/Finance/2026/autre/CMD/Legrand_Press_Release_CMD_Sep-2026_1790606990.pdf", "2026-09-28", "2026-09-28_cmd_release.pdf"),
    ("CMD2026", "cmd_presentation", "https://www.legrand.com/sites/default/files/Documents_PDF_Legrand/Finance/2026/autre/CMD/CMD-2026-Deck_1790662658.pdf", "2026-09-29", "2026-09-29_cmd_presentation.pdf"),
    ("2020Q1", "covid_update", "https://www.legrand.com/sites/default/files/Documents_PDF_Legrand/Finance/2020/autres/Legrand_Press_Release_Regulated_Information_Covid-19_1585161940.pdf", "2020-03-26", "2020-03-25_covid_update.pdf"),
]
f = Fetcher()
man = []
seen = set()
for fp, dtp, url in docs:
    if int(fp[:4]) < FIRST or (fp, dtp) in seen:
        continue
    seen.add((fp, dtp))
    path = os.path.join(RAW_IR, TK, f"{fp}_{dtp}.pdf")
    ok, st, _ = f.download(url, path)
    if not ok or not is_pdf(path):
        print("FAIL", st, fp, dtp, url[-80:])
        if os.path.exists(path) and not is_pdf(path):
            os.remove(path)
        continue
    out, n = to_text(path, TK, fp, dtp)
    man.append({"local_path": path, "url": url, "doc_type": dtp, "fiscal_period": fp, "pub_date": pub.get(fp, "")})
    print("ok", fp, dtp, n)
for fp, dtp, url, d, fn in extra:
    path = os.path.join(RAW_IR, TK, fn)
    if os.path.exists(path) and is_pdf(path):
        tag = fp if fp.startswith("20") else d
        to_text(path, TK, tag if dtp != "covid_update" else "2020-03-26", dtp)
        man.append({"local_path": path, "url": url, "doc_type": dtp, "fiscal_period": fp if fp.startswith("20") else "", "pub_date": d})
# keep previously listed rows for other periods (incremental runs)
mp = os.path.join(PROC_IR, f"{TK}_manifest.csv")
if os.path.exists(mp):
    old = pd.read_csv(mp, dtype=str).fillna("").to_dict("records")
    have = {m["local_path"].replace(ROOT + "/", "") for m in man}
    man += [o for o in old if o["local_path"] not in have]
print(write_manifest(TK, man), len(man))
