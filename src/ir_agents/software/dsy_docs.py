"""Download DSY.PA IR documents (press releases, presentations, conference-call texts, CMD decks),
extract text, and write data/processed/ir/DSY.PA_manifest.csv."""
import sys, os, re, json
import pandas as pd
sys.path.insert(0, os.path.dirname(__file__))
import fetch_util as fu
from dsy_parse_qr import parse, BASE

T = "DSY.PA"
RAW = os.path.join(fu.RAW_IR, T)
TXT = os.path.join(fu.TXT_IR, T)
os.makedirs(RAW, exist_ok=True); os.makedirs(TXT, exist_ok=True)

ev = pd.read_csv(os.path.join(fu.PROC_IR, T + "_events.csv"), dtype=str).fillna("")
rel = {r.fiscal_period: r.event_date for r in ev.itertuples() if r.event_type in ("Q1", "Q2", "Q3", "Q4")}

def doctype(label):
    l = label.lower()
    if "press release" in l:
        return "press_release"
    if "presentation" in l:
        return "presentation"
    if "conference call" in l and "link" not in l:
        return "transcript"
    return None

rows = []
html = fu.cached_html(BASE + "/financial-information/quarterly-results")
items = parse(html)
want = []
for it in items:
    if not it["year"] or not it["q"].startswith("Q"):
        continue
    y, q = int(it["year"]), int(it["q"][1])
    period = "%dQ%d" % (y, q)
    dt = doctype(it["label"])
    if dt is None or not re.search(r"(static-files|\.pdf|globenewswire)", it["url"]):
        continue
    if period < "2014Q4" or period not in rel:
        continue
    if dt == "presentation" and period < "2022Q1":
        continue
    want.append((period, dt, it["url"], rel[period]))

# CMD / prelim extras
extras = [
    ("CMD2025", "cmd_presentation", BASE + "/static-files/e12b3b59-ec2b-4a65-be7e-c3012c664636", "2025-06-06"),
    ("CMD2025", "cmd_cfo_presentation", BASE + "/static-files/370f62be-b861-4664-b1f2-a86f9a7bb889", "2025-06-06"),
    ("CMD2025", "cmd_press_release", BASE + "/static-files/c4623390-2e85-4f97-9e2c-bd6ac594ae03", "2025-06-06"),
    ("CMD2022", "cmd_cfo_presentation", BASE + "/static-files/db5f0dba-cdff-4c16-aa08-a88b9d034a7f", "2022-06-16"),
]
ev_json = json.load(open(os.path.join(RAW, "ir_calendar_events.json")))
for e in ev_json:
    if "Preliminary Second Quarter 2024" in e["title"]:
        for l in e.get("detail_links", []):
            u = l if l.startswith("http") else BASE + l
            extras.append(("2024Q2", "prelim_transcript" if "Script" in l else "prelim_press_release", u, "2024-07-09"))
want += extras

seen = set()
for period, dt, url, pub in want:
    key = (period, dt)
    if key in seen:
        continue
    seen.add(key)
    dest = os.path.join(RAW, "%s_%s.pdf" % (period, dt))
    ok = fu.download(url, dest)
    if not ok:
        continue
    with open(dest, "rb") as f:
        head = f.read(5)
    if head != b"%PDF-":
        print("NOT PDF", period, dt, url); continue
    tpath = os.path.join(TXT, "%s_%s.txt" % (period, dt))
    if not os.path.exists(tpath):
        try:
            txt = fu.pdf_to_text(dest)
        except Exception as e:
            print("PDFERR", dest, e); continue
        with open(tpath, "w", encoding="utf-8") as f:
            f.write(txt)
    rows.append({"ticker": T, "local_path": os.path.relpath(dest, fu.ROOT), "url": url, "doc_type": dt,
                 "fiscal_period": period, "pub_date": pub})
m = pd.DataFrame(rows).sort_values(["fiscal_period", "doc_type"])
m.to_csv(os.path.join(fu.PROC_IR, T + "_manifest.csv"), index=False)
print(len(m)); print(m.groupby("doc_type").size())
