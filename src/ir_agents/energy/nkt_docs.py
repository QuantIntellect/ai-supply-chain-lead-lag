"""Download NKT reports / presentations / transcripts / quarterly-figure workbooks (2022+), extract text, manifest."""
import sys, re, os
sys.path.insert(0, "/Users/sinamirzaei/Documents/aimapping/src/ir_agents/energy"); import irlib
from bs4 import BeautifulSoup

T = "NKT.CO"
BASE = "https://investors.nkt.com"
ev = {}
for r in irlib.read_csv(f"data/processed/ir/{T}_events.csv"):
    if r["event_type"] in ("Q1", "Q2", "Q3", "H1", "FY"):
        ev[r["fiscal_period"]] = r["event_date"]


def period_of(name):
    n = name.lower()
    m = re.search(r"annual[-_ ]?reports?[-_ ]?(20\d\d)", n)
    if m:
        return f"FY{m.group(1)}"
    m = re.search(r"(q[1-4]|h1)[-_ ]?(?:20)?(\d\d)(?!\d)", n)
    if m:
        q, y = m.group(1).upper(), "20" + m.group(2)
        if q == "H1":
            q = "H1" if int(y) >= 2026 else "Q2"
        return f"FY{y}" if q == "Q4" else f"FY{y}{q}"
    return None


rows, seen = [], set()
pages = [f"{BASE}/financial-reports/"] + [f"{BASE}/financial-reports/?year={y}" for y in (2022, 2023, 2024, 2025, 2026)]
for pg in pages:
    s = BeautifulSoup(irlib.fetch(pg).text, "html.parser")
    cur = None
    for a in s.find_all("a", href=True):
        h = a["href"]
        if not re.search(r"\.(pdf|xlsx)$", h, re.I):
            continue
        label = a.get_text(" ", strip=True).lower()
        name = h.rsplit("/", 1)[-1]
        nl = name.lower()
        if re.search(r"nilfisk|volt_", nl):
            continue
        if re.search(r"cmd|investor-day|medium-term-ambitions|reaffirms", nl):
            y = re.search(r"(20\d\d)", nl).group(1)
            cmd_dates = {"2015": "2015-09-23", "2017": "2017-09-19", "2022": "2022-09-22", "2024": "2024-12-02", "2026": "2026-09-29"}
            kind = "transcript" if "transcript" in nl else ("press_release" if "reaffirms" in nl else "presentation")
            url = h if h.startswith("http") else BASE + h
            if h in seen:
                continue
            seen.add(h)
            lp = irlib.download(url, T, f"CMD{y}_{name}")
            if lp:
                irlib.extract_text(lp, T, f"CMD{y}", kind)
                rows.append({"local_path": lp, "url": url, "doc_type": kind, "fiscal_period": f"FY{y}", "pub_date": cmd_dates.get(y, "")})
                print(f"CMD{y}     {kind:12s} {name[:60]}")
            continue
        if label == "report":
            cur = period_of(name)
        fp = cur
        if label in ("presentation", "excel") and period_of(name):
            fp = period_of(name)
        if not fp or int(fp[2:6]) < 2022 or h in seen:
            continue
        seen.add(h)
        kind = {"report": "report", "presentation": "presentation", "transcript": "transcript", "excel": "other"}.get(label, "other")
        url = h if h.startswith("http") else BASE + h
        lp = irlib.download(url, T, f"{fp}_{name}")
        if not lp:
            continue
        if kind != "other":
            irlib.extract_text(lp, T, fp, kind)
        rows.append({"local_path": lp, "url": url, "doc_type": kind, "fiscal_period": fp, "pub_date": ev.get(fp, "")})
        print(f"{fp:10s} {kind:12s} {name[:60]}")
irlib.write_manifest(T, rows)
