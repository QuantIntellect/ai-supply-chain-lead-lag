"""Download Nexans results press releases (2015+) and presentations (2022+), extract text, write manifest."""
import sys, re, os
sys.path.insert(0, "/Users/sinamirzaei/Documents/aimapping/src/ir_agents/energy"); import irlib
from bs4 import BeautifulSoup

T = "NEX.PA"
PAGES = ["https://www.nexans.com/finance/financial-information/financial-results/",
         "https://www.nexans.com/finance/financial-information/2024-capital-markets-day/",
         "https://www.nexans.com/finance/financial-information/2021-capital-markets-day/"]
ev = {r["fiscal_period"] + "|" + r["event_type"]: r["event_date"] for r in irlib.read_csv(f"data/processed/ir/{T}_events.csv")}


def classify(name):
    n = name.lower()
    rest = re.sub(r"^20\d\d-\d\d-\d\d[-_]", "", n)
    if re.search(r"(^|[-_])pr[-_]|press-release|earnings-press", n):
        kind = "press_release"
    elif "presentation" in n:
        kind = "presentation"
    elif "transcript" in n:
        kind = "transcript"
    else:
        return None
    m = re.match(r"(20\d\d)-(\d\d)-(\d\d)", n)
    rel = m.group(0) if m else ""
    yrs = re.findall(r"20\d\d", rest)
    if re.search(r"h1|half", n):
        typ = "H1"
    elif re.search(r"full-year|[-_]fy[-_]|fy-20|-2019-financial|nexans-fy|year-results", n):
        typ = "FY"
    elif re.search(r"q1|first-quarter", n):
        typ = "Q1"
    elif re.search(r"q3|9m|third", n):
        typ = "Q3"
    else:
        typ = None
    if yrs:
        fy = int(yrs[0])
    elif rel:
        fy = int(rel[:4]) - (1 if typ == "FY" else 0)
    else:
        return None
    if typ is None:
        return (kind, None, rel)
    fp = f"FY{fy}" if typ == "FY" else f"FY{fy}{typ}"
    return (kind, fp, rel or ev.get(f"{fp}|{typ}", ""))


rows = []
for page in PAGES:
    s = BeautifulSoup(irlib.fetch(page).text, "html.parser")
    for a in s.find_all("a", href=True):
        h = a["href"]
        if not h.lower().endswith(".pdf"):
            continue
        name = h.rsplit("/", 1)[-1]
        c = classify(name)
        is_cmd = "capital-markets-day" in page
        if c is None and not is_cmd:
            continue
        if is_cmd:
            kind = "presentation" if "presentation" in name.lower() or "cmd" in name.lower() else ("press_release" if "-pr-" in name.lower() else "other")
            yr = "2024" if "2024" in page else "2021"
            fp = "FY" + yr
            rel = {"2024": "2024-11-13", "2021": "2021-02-17"}[yr]
            per = f"CMD{yr}"
        else:
            kind, fp, rel = c
            if fp is None:
                continue
            per = fp
        yr = int(fp[2:6])
        if kind == "presentation" and yr < 2022 and not is_cmd:
            continue
        if yr < 2015:
            continue
        lp = irlib.download(h, T, name)
        if not lp:
            continue
        txt = irlib.extract_text(lp, T, per, kind)
        rows.append({"local_path": lp, "url": h, "doc_type": kind, "fiscal_period": fp, "pub_date": rel})
        print(f"{per:10s} {kind:13s} {rel} {name[:60]}")
irlib.write_manifest(T, rows)
