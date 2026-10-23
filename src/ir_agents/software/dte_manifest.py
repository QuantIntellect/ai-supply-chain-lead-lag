"""DT: fix mislabeled files and write DTE.DE_manifest.csv."""
import sys, os, json, csv, shutil
sys.path.insert(0, os.path.dirname(__file__))
import fetch_util as fu
from dte_events import DATES

T = "DTE.DE"
RAW = os.path.join(fu.RAW_IR, T)
TXT = os.path.join(fu.TXT_IR, T)
OUT = os.path.join(fu.PROC_IR, T + "_manifest.csv")

def main():
    rows = json.load(open(os.path.join(RAW, "dte_docs_rows.json"))) + json.load(open(os.path.join(RAW, "dte_docs_extra_rows.json")))
    # the 2025 year page links a file named 'DT 24Q1 Transcript' in the Q1-2025 block; content is the Q1 2025 call
    for r in rows:
        if r["fiscal_period"] == "2025Q1?":
            src = os.path.join(fu.ROOT, r["local_path"]); dst_dir = os.path.join(RAW, "2025Q1")
            os.makedirs(dst_dir, exist_ok=True)
            dst = os.path.join(dst_dir, os.path.basename(src))
            if os.path.exists(src): shutil.move(src, dst)
            t0 = os.path.join(TXT, "2025Q1x_transcript.txt"); t1 = os.path.join(TXT, "2025Q1_transcript.txt")
            if os.path.exists(t0) and not os.path.exists(t1): shutil.move(t0, t1)
            r["local_path"] = os.path.relpath(dst, fu.ROOT); r["fiscal_period"] = "2025Q1"
    d0 = os.path.join(RAW, "2025Q1x")
    if os.path.isdir(d0) and not os.listdir(d0): os.rmdir(d0)
    for r in rows:
        if not r.get("pub_date"):
            r["pub_date"] = DATES.get(r["fiscal_period"], "")
    rows.sort(key=lambda r: (r["fiscal_period"], r["doc_type"]))
    with open(OUT, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["ticker", "local_path", "url", "doc_type", "fiscal_period", "pub_date"])
        w.writeheader(); w.writerows(rows)
    print(len(rows), "docs")

if __name__ == "__main__":
    main()
