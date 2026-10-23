"""Download SAP quarterly statements / presentations / half-year reports / press releases and
extract text. Writes a raw download log used later to build the manifest."""
import sys, os, re, json
sys.path.insert(0, os.path.dirname(__file__))
import fetch_util as fu

T = "SAP.DE"
RAW = os.path.join(fu.RAW_IR, T)
TXT = os.path.join(fu.TXT_IR, T)
LOG = os.path.join(RAW, "download_log.json")
BASE = "https://www.sap.com/docs/download/investors/%d/sap-%d-%s.pdf"

def save_txt(period, doctype, text):
    os.makedirs(TXT, exist_ok=True)
    p = os.path.join(TXT, "%s_%s.txt" % (period, doctype))
    with open(p, "w", encoding="utf-8") as f:
        f.write(text)
    return p

def main(y0=2022, y1=2026):
    log = json.load(open(LOG)) if os.path.exists(LOG) else []
    done = {(r["fiscal_period"], r["doc_type"]) for r in log}
    for y in range(y0, y1 + 1):
        for q in (1, 2, 3, 4):
            per = "%dQ%d" % (y, q)
            if (y, q) > (2026, 3):
                continue
            items = [("statement", "q%d-statement" % q), ("presentation", "q%d-presentation" % q)]
            if q == 2:
                items.append(("half_year_report", "half-year-report"))
            for doctype, k in items:
                if (per, doctype) in done:
                    continue
                url = BASE % (y, y, k)
                dest = os.path.join(RAW, "sap-%d-%s.pdf" % (y, k))
                if fu.download(url, dest, min_bytes=20000):
                    try:
                        txt = fu.pdf_to_text(dest)
                    except Exception as e:
                        print("PDFERR", dest, e); continue
                    tp = save_txt(per, doctype, txt)
                    log.append({"fiscal_period": per, "doc_type": doctype, "url": url,
                                "local_path": os.path.relpath(dest, fu.ROOT), "text_path": os.path.relpath(tp, fu.ROOT),
                                "chars": len(txt)})
                    print("OK", per, doctype, len(txt))
    with open(LOG, "w") as f:
        json.dump(log, f, indent=1)

if __name__ == "__main__":
    a = sys.argv[1:]
    main(int(a[0]), int(a[1])) if a else main()
