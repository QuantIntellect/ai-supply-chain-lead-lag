"""Download Siemens Energy IR documents (results releases, analyst decks, half-year reports, CMD decks,
pre-close transcripts, ad-hoc PDFs), extract text, and write data/processed/ir/ENR.DE_manifest.csv.
Document list comes from the IR 'Publications & Ad hoc' page (parsed by enr_pub_map.py -> scratch pub_map.json)."""
import sys; sys.path.insert(0, "/Users/sinamirzaei/Documents/aimapping/src/ir_agents/energy"); import irlib
import json, os, re, datetime as dt
from urllib.parse import unquote
T = "ENR.DE"
SP = "/private/tmp/claude-501/-Users-sinamirzaei-Documents-aimapping/57e0a0d0-6441-40ef-828b-57eeb87e7b21/scratchpad/enr"
pub = json.load(open(os.path.join(SP, "pub_map.json")))
MON = {m: i for i, m in enumerate(["January", "February", "March", "April", "May", "June", "July", "August",
                                    "September", "October", "November", "December"], 1)}


def sec_date(sec):
    m = re.search(r"([A-Z][a-z]+) (\d{1,2})(?:-\d+)?, (\d{4})", sec)
    return f"{m.group(3)}-{MON[m.group(1)]:02d}-{int(m.group(2)):02d}" if m else ""


def fname(url):
    f = unquote(url.split("/")[-1]).replace("-pdf_Original file.pdf", ".pdf").replace(" ", "_")
    return f if f.lower().endswith(".pdf") else f + ".pdf"


jobs = []  # (url, filename, doc_type, fiscal_period, pub_date, text_period, text_doctype)
for r in pub:
    sec, txt, url = r["section"], r["text"], r["url"]
    if ".pdf" not in url.lower():
        continue
    m = re.match(r"Q([1-4]) FY(\d{4}) Financial Results", sec)
    if m:
        q, y = m.group(1), m.group(2)
        fp = f"FY{y}" if q == "4" else f"FY{y}Q{q}"
        d = sec_date(sec)
        if re.search(r"Earnings Release", txt):
            dtp, tdt = "press_release", "earnings_release"
        elif re.search(r"Presentation", txt):
            dtp, tdt = "presentation", "analyst_presentation"
        elif re.search(r"Half-year", txt):
            dtp, tdt = "report", "half_year_report"
        elif re.search(r"Comparable Key Figures", txt):
            dtp, tdt, fp = "other", "comparable_key_figures_restated", "FY2022"
        elif re.search(r"Press Release", txt):
            dtp, tdt = "press_release", "press_release"
        else:
            continue
        jobs.append((url, fname(url), dtp, fp, d, fp, tdt))
        continue
    m = re.match(r"Capital Markets? Day", sec)
    if m:
        d = sec_date(sec)
        if re.search(r"Agenda|CEO|CFO|Gas Services|Grid Technologies|Transformation|SGRE|Siemens Gamesa|Press Release|Service|Generation|Transmission|Industrial", txt) or "Press-Release" in url:
            tag = re.sub(r"[^A-Za-z]+", "_", txt or "press_release")[:30].strip("_").lower()
            jobs.append((url, fname(url), "presentation" if "Press" not in (txt + url) else "press_release",
                         "", d, f"CMD_{d}", f"cmd_{tag}"))
# pre-close call transcripts + ad-hoc PDFs linked on the IR start page / publications page
extra = [l.split("\t") for l in open(os.path.join(SP, "enr_pub_pdfs.txt")).read().splitlines()]
ir_home = open(os.path.join(SP, "www.siemens-energy.com_global_en_home_investor-relations.html.html"), encoding="utf-8", errors="replace").read()
for u in sorted(u for u in set(re.findall(r'href="(https://assets[^"]+Pre-Close[^"]+)"', ir_home)) if "Recording" not in u):
    f = fname(u)
    d = re.match(r"(\d{4}-\d{2}-\d{2})", f).group(1)
    fp = "FY2026Q3" if "Q3FY26" in f.replace("-", "") or "Q3FY26" in f else ("FY2026Q4" if "Q4" in f else "")
    jobs.append((u, f, "transcript", fp, d, fp or d, "preclose_call_transcript"))
ADHOC_FP = {"2021January24": ("FY2021Q1", "trading_update"), "2021January14": ("FY2021", "trading_update"),
            "2022January20": ("FY2022", "trading_update"), "2022April19": ("FY2022", "trading_update"),
            "2023January19": ("FY2023", "trading_update"), "2023June22": ("FY2023", "trading_update"),
            "2023October26": ("FY2023Q4", "trading_update"), "2024January23": ("FY2024Q1", "trading_update")}
for fn, u in extra:
    m = re.match(r"Ad-Hoc-EN-(\d{4}[A-Za-z]+\d{2})-(\d)", fn)
    if not m:
        continue
    k = m.group(1)
    if k not in ADHOC_FP:
        continue
    fp, dtp = ADHOC_FP[k]
    d = dt.datetime.strptime(k, "%Y%B%d").strftime("%Y-%m-%d")
    if k == "2021January14":  # file name date differs from the announcement date (14 July 2021)
        d = "2021-07-14"
    jobs.append((u, fname(u), dtp, fp, d, fp, f"adhoc_{d}"))

manifest = []
for url, f, dtp, fp, d, tper, tdt in jobs:
    rel = irlib.download(url, T, f)
    if not rel:
        continue
    txt = irlib.extract_text(rel, T, tper, tdt)
    manifest.append(dict(local_path=rel, url=url, doc_type=dtp, fiscal_period=fp, pub_date=d))
    print(f"{d} {dtp:13s} {fp:9s} {rel.split('/')[-1][:60]:60s} -> {txt.split('/')[-1] if txt else None}")

# regulatory-feed HTML pages saved by enr_eqs_detail.py / enr_pta_detail.py (timing evidence)
EQS_FP = {"24_January_2021": "FY2021Q1", "14_July_2021": "FY2021", "20_January_2022": "FY2022", "19_April_2022": "FY2022",
          "19_January_2023": "FY2023", "22_June_2023": "FY2023", "26_October_2023": "FY2023Q4", "23_January_2024": "FY2024Q1"}
eqs_rows = [l.rstrip("\n").split("\t") for l in open(os.path.join(SP, "eqs_adhoc_detail.tsv"))]
for dgrp, shown, dl, title, url, rel in eqs_rows:
    key = dgrp.replace(" ", "_")
    d = dt.datetime.strptime(dgrp, "%d %B %Y").strftime("%Y-%m-%d")
    fp = EQS_FP.get(key, "")
    manifest.append(dict(local_path=rel, url=url, doc_type="trading_update" if fp else "other", fiscal_period=fp, pub_date=d))
PTA = {"20241112030": ("FY2024Q4", "trading_update"), "20241112032": ("FY2024", "press_release"),
       "20250127029": ("FY2025Q1", "trading_update"), "20250416026": ("FY2025Q2", "trading_update"),
       "20251113030": ("FY2025Q4", "trading_update"), "20260423027": ("FY2026Q2", "trading_update"),
       "20250730015": ("", "other"), "20260825031": ("", "other")}
for nid, (fp, dtp) in PTA.items():
    rel = f"data/raw/ir/{T}/pta_{nid}.html"
    if os.path.exists(os.path.join(irlib.ROOT, rel)):
        d = f"{nid[:4]}-{nid[4:6]}-{nid[6:8]}"
        txt = irlib.extract_text(rel, T, fp or d, f"pta_{dtp}")
        manifest.append(dict(local_path=rel, url=f"https://www.pressetext.com/news/{nid}", doc_type=dtp, fiscal_period=fp, pub_date=d))
irlib.write_manifest(T, manifest)
