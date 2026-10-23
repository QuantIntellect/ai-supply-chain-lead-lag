"""DT: download 2022Q1-2026Q3 quarterly documents from telekom.com year pages, extract text, write manifest."""
import sys, os, re, html, json, csv
from urllib.parse import unquote
sys.path.insert(0, os.path.dirname(__file__))
import fetch_util as fu

T = "DTE.DE"
RAW = os.path.join(fu.RAW_IR, T)
TXT = os.path.join(fu.TXT_IR, T)
MAN = os.path.join(fu.PROC_IR, T + "_manifest.csv")
SKIP = re.compile(r"(Consensus|\.xlsx|Anteilsbesitz|investment holdings|Financial Statements|Share Property|Investor[ -]Pr|Unternehmenspr|Einzelabschluss|Geschäftsbericht|Annual Report|Investor-Pr)", re.I)

def classify(nm):
    n = nm.lower()
    if "adhoc" in n or "ad-hoc" in n: return "adhoc"
    if "transcript" in n or "transkript" in n: return "transcript"
    if "backup" in n: return "backup"
    if "zwischenbericht" in n: return "interim_report_de"
    if "interim" in n: return "interim_report"
    if "medieninformation" in n: return "press_release_de"
    if "media information" in n or "media-information" in n: return "press_release"
    if "presentation" in n or "präsentation" in n or "praesentation" in n or "charts" in n: return "presentation"
    return None

def period_from_name(nm, page_year):
    m = re.search(r"(\d{2})Q([1-4])", nm, re.I)
    if m: return "20%sQ%s" % (m.group(1), m.group(2))
    m = re.search(r"(\d{2})FY", nm)
    if m: return "20%sQ4" % m.group(1)
    m = re.search(r"9M(\d{2})", nm)
    if m: return "20%sQ3" % m.group(1)
    m = re.search(r"dt-(\d{2})q([1-4])", nm, re.I)
    if m: return "20%sQ%s" % (m.group(1), m.group(2))
    m = re.search(r"\bq([1-4])\b|[-_]q([1-4])[-_.]|Q([1-4])-", nm, re.I)
    if m:
        q = next(g for g in m.groups() if g)
        return "%dQ%s" % (page_year, q)
    if re.search(r"DL_backup", nm): return "%dQ4" % page_year
    return None

def main():
    os.makedirs(RAW, exist_ok=True); os.makedirs(TXT, exist_ok=True)
    rows = []
    seen_periods = {}
    for y in range(2022, 2027):
        page = "https://www.telekom.com/en/investor-relations/publications/financial-results/%d" % y
        h = fu.cached_html(page)
        for l in re.findall(r'href="(https://delivery-[^"]+)"', h):
            url = html.unescape(l)
            nm = unquote(url.split("/as/")[-1].split("?")[0])
            if SKIP.search(nm) or not nm.lower().endswith(".pdf"):
                continue
            dtp = classify(nm)
            per = period_from_name(nm, y)
            if not dtp or not per:
                print("UNMAPPED", y, nm); continue
            # known mislabeled link: 2023 page re-links the 2022Q4 transcript
            if nm.startswith("DL_230223-Q4") and y == 2023:
                continue
            if nm.startswith("DL_230223-Q4"):
                per = "2022Q4"
            # 2025 page links 'DT 24Q1 Transcript' inside the Q1 2025 block; keep as 2025Q1 candidate, verify later
            if nm.startswith("DT 24Q1 Transcript") and y == 2025:
                per = "2025Q1?"
            key = (per, dtp)
            if key in seen_periods:
                continue
            seen_periods[key] = url
            fn = re.sub(r"[^A-Za-z0-9._-]+", "_", nm)
            dest = os.path.join(RAW, per.replace("?", "x"), fn)
            ok = fu.download(url, dest, min_bytes=2000)
            if not ok:
                continue
            tname = "%s_%s.txt" % (per.replace("?", "x"), dtp)
            tp = os.path.join(TXT, tname)
            if not os.path.exists(tp):
                try:
                    txt = fu.pdf_to_text(dest)
                    with open(tp, "w") as f:
                        f.write(txt)
                except Exception as e:
                    print("PDFERR", dest, e)
            rows.append({"ticker": T, "local_path": os.path.relpath(dest, fu.ROOT), "url": url, "doc_type": dtp,
                         "fiscal_period": per, "pub_date": ""})
            print("OK", per, dtp, fn[:60], flush=True)
        # English newsroom media information pages (HTML)
        for link, ly, lm in sorted(set(re.findall(r'href="(https://www\.telekom\.com/en/newsroom/latest-updates/media-information/(\d{4})/(\d{1,2})/[^"]+)"', h))):
            ly, lm = int(ly), int(lm)
            if lm in (1, 2, 3) and ly == y + 1: per = "%dQ4" % y
            elif lm in (4, 5, 6) and ly == y: per = "%dQ1" % y
            elif lm in (7, 8, 9) and ly == y: per = "%dQ2" % y
            elif lm in (10, 11, 12) and ly == y: per = "%dQ3" % y
            else: continue
            hh = fu.cached_html(link)
            if not hh: continue
            if "ad-hoc" in link or "Ad hoc" in (re.search(r"<title>(.*?)</title>", hh, re.S).group(1) if re.search(r"<title>(.*?)</title>", hh, re.S) else ""):
                dtp = "adhoc_html"
            else:
                dtp = "press_release_html"
            if (per, dtp) in seen_periods: continue
            seen_periods[(per, dtp)] = link
            dest = os.path.join(RAW, per, link.rstrip("/").split("/")[-1][:80] + ".html")
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            with open(dest, "w") as f: f.write(hh)
            from bs4 import BeautifulSoup
            s = BeautifulSoup(hh, "html.parser"); main = s.find("main") or s
            txt = re.sub(r"\n\s*\n+", "\n\n", main.get_text("\n"))
            with open(os.path.join(TXT, "%s_%s.txt" % (per, dtp)), "w") as f: f.write(txt)
            md = re.search(r'<meta name="date" content="([0-9-]+)"', hh)
            rows.append({"ticker": T, "local_path": os.path.relpath(dest, fu.ROOT), "url": link, "doc_type": dtp,
                         "fiscal_period": per, "pub_date": md.group(1) if md else ""})
            print("OK", per, dtp, link[-50:], flush=True)
    json.dump(rows, open(os.path.join(RAW, "dte_docs_rows.json"), "w"), indent=1)

if __name__ == "__main__":
    main()
