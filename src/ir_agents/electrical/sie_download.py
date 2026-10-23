"""Download Siemens quarterly documents listed on the IR results pages.

Reads data/raw/ir/SIE.DE/pages/doc_links.json (built by sie_parse_archive.py),
downloads press releases + earnings releases for FY2016-FY2026 (event dating),
presentations / half-year reports / Excel results for FY2022+, ad hoc PDFs,
extracts text, and writes the manifest.
"""
import os, sys, re, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from irlib import *

T = "SIE.DE"
RAW = os.path.join(RAW_IR, T)
links = json.load(open(os.path.join(RAW, "pages", "doc_links.json")))


def classify(fname, text):
    f = fname.lower()
    if f.endswith(".xlsx"):
        return "financial_results_xlsx"
    if "earnings-release" in f:
        return "earnings_release"
    if "presentation" in f:
        return "presentation"
    if "hy-report" in f or "half-year" in f or "h1-financialreport" in f:
        return "half_year_report"
    if "ad-hoc" in f or "ad_hoc" in f:
        return "ad_hoc"
    if "press-release" in f and re.fullmatch(r"Q[1-4]", text.strip()):
        return "press_release"
    if re.match(r"\d{6}-press-release-en\.pdf$", f) and re.fullmatch(r"Q[1-4]", text.strip()):
        return "press_release"
    return None


rows = []
f = Fetcher(min_gap=1.0)
todo = []
for r in links:
    lab = r["label"]
    m = re.match(r"Q([1-4]) FY(\d\d)", lab)
    if not m:
        continue
    q, fy = int(m.group(1)), 2000 + int(m.group(2))
    href = r["href"]
    if href.startswith("//"):
        href = "https:" + href
    if not href.startswith("http"):
        continue
    fname = href.split("/")[-1].split("?")[0]
    dt = classify(fname, r["text"])
    if dt is None:
        continue
    if dt in ("presentation", "half_year_report", "financial_results_xlsx") and fy < 2022:
        continue
    if dt == "financial_results_xlsx" and not fname.lower().endswith(".xlsx"):
        continue
    period = f"{fy}Q{q}"
    ext = ".xlsx" if fname.lower().endswith(".xlsx") else ".pdf"
    out = os.path.join(RAW, f"{period}_{dt}{ext}")
    todo.append((period, dt, href, out))

print("todo", len(todo))
for period, dt, href, out in todo:
    try:
        ok, st, p = f.download(href, out)
    except Exception as e:
        print("ERR", period, dt, e)
        continue
    if not ok:
        print("FAIL", st, period, dt, href[-60:])
        continue
    if out.endswith(".pdf") and not is_pdf(out):
        print("NOTPDF", period, dt)
        os.remove(out)
        continue
    txt = ""
    if out.endswith(".pdf"):
        txt, n = to_text(out, T, period, dt)
    rows.append({"local_path": out, "url": href, "doc_type": dt,
                 "fiscal_period": period, "pub_date": ""})
json.dump(rows, open(os.path.join(RAW, "pages", "downloaded.json"), "w"), indent=1)
print("downloaded", len(rows))
