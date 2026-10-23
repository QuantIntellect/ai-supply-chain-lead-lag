"""Normalise SAP text-file names to <period>_<doctype>.txt and write SAP.DE_manifest.csv."""
import sys, os, json, csv, re
sys.path.insert(0, os.path.dirname(__file__))
import fetch_util as fu

T = "SAP.DE"
RAW = os.path.join(fu.RAW_IR, T)
TXT = os.path.join(fu.TXT_IR, T)
OUT = os.path.join(fu.PROC_IR, "%s_manifest.csv" % T)
ADHOC_PERIOD = {"2020/04": "2020Q1", "2020/07": "2020Q2", "2020/10": "2020Q3", "2021/01": "2020Q4",
                "2021/04": "2021Q1", "2021/10": "2021Q3", "2022/01": "2021Q4", "2024/01": "2023Q4"}

def main():
    log = json.load(open(os.path.join(RAW, "download_log.json")))
    ev = {}
    for r in csv.DictReader(open(os.path.join(fu.PROC_IR, "%s_events.csv" % T))):
        if r["event_type"] in ("Q1", "Q2", "Q3", "Q4"):
            ev[r["fiscal_period"]] = r["event_date"]
    rows = []
    for r in log:
        per, dt = r["fiscal_period"], r["doc_type"]
        pub = ""
        if dt == "adhoc":
            m = re.search(r"ad-hoc-news/(\d{4})/(\d{2})/", r["url"])
            per = ADHOC_PERIOD.get("%s/%s" % (m.group(1), m.group(2)), "")
            d = re.match(r"(\d{2})-(\w{3})-(\d{4})", r["pub_date"])
            from datetime import datetime
            pub = datetime.strptime(" ".join(d.groups()), "%d %b %Y").strftime("%Y-%m-%d")
        elif dt in ("statement", "presentation", "press_release"):
            pub = ev.get(per, "")
        new_txt = os.path.join(TXT, "%s_%s.txt" % (per, dt))
        old_txt = os.path.join(fu.ROOT, r["text_path"])
        if os.path.abspath(old_txt) != os.path.abspath(new_txt) and os.path.exists(old_txt):
            os.replace(old_txt, new_txt)
        r["text_path"] = os.path.relpath(new_txt, fu.ROOT)
        rows.append([T, r["local_path"], r["url"], dt, per, pub])
    # FAC (capital-markets-day type) presentations
    for y, name, d in [(2024, "sap-2024-financial-analyst-conference-presentation", "2024-06-05"),
                       (2025, "sapphire-2025-financial-analyst-presentation", "2025-05-21"),
                       (2026, "sapphire-2026-financial-analyst-presentation", "2026-05-13")]:
        old = os.path.join(TXT, "%dFAC_cmd_presentation.txt" % y)
        new = os.path.join(TXT, "%d_cmd_presentation.txt" % y)
        if os.path.exists(old):
            os.replace(old, new)
        rows.append([T, "data/raw/ir/SAP.DE/%s.pdf" % name,
                     "https://www.sap.com/docs/download/investors/%d/%s.pdf" % (y, name), "cmd_presentation", str(y), d])
    json.dump(log, open(os.path.join(RAW, "download_log.json"), "w"), indent=1)
    rows.sort(key=lambda r: (r[4], r[3]))
    with open(OUT, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["ticker", "local_path", "url", "doc_type", "fiscal_period", "pub_date"])
        w.writerows(rows)
    missing = [r[1] for r in rows if not os.path.exists(os.path.join(fu.ROOT, r[1]))]
    print(len(rows), "manifest rows; missing files:", missing)

if __name__ == "__main__":
    main()
