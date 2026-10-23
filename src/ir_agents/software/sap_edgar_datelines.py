"""For SAP 6-K filings, fetch exhibit documents from EDGAR and extract the press-release dateline
(WALLDORF, Germany - <date>) and headline, to pin release dates of regular results."""
import sys, os, re, json
sys.path.insert(0, os.path.dirname(__file__))
import fetch_util as fu
import pandas as pd

OUT = os.path.join(fu.RAW_IR, "SAP.DE", "edgar_6k_datelines.json")

def main(years):
    df = pd.read_parquet(os.path.join(fu.ROOT, "data", "processed", "edgar_filings.parquet"))
    s = df[(df.cik.astype(str).str.lstrip("0") == "1000184") & (df.form == "6-K")]
    s = s[s.filingDate.str[:4].isin([str(y) for y in years])]
    res = json.load(open(OUT)) if os.path.exists(OUT) else []
    done = {r["acc"] for r in res}
    for r in s.itertuples():
        acc = r.accessionNumber
        if acc in done:
            continue
        accnd = acc.replace("-", "")
        idx = "https://www.sec.gov/Archives/edgar/data/1000184/%s/index.json" % accnd
        try:
            j = fu.get(idx, gap=0.4).json()
        except Exception as e:
            print("IDXERR", acc); continue
        docs = [it for it in j.get("directory", {}).get("item", []) if it["name"].lower().endswith((".htm", ".html"))]
        docs.sort(key=lambda it: -int(it.get("size") or 0))
        found = None
        for it in docs[:3]:
            u = "https://www.sec.gov/Archives/edgar/data/1000184/%s/%s" % (accnd, it["name"])
            try:
                h = fu.get(u, gap=0.4).text
            except Exception:
                continue
            t = re.sub(r"\s+", " ", fu.html_to_text(h[:400000]))
            m = re.search(r"WALLDORF,? (?:Germany)?\s*[–—-]+\s*((?:January|February|March|April|May|June|July|August|September|October|November|December) \d{1,2}, 20\d\d)", t, re.I)
            if m:
                head = t[max(0, m.start() - 400): m.start()]
                found = {"acc": acc, "filed": r.filingDate, "doc": it["name"], "dateline": m.group(1),
                         "context": head[-300:], "lead": t[m.end(): m.end() + 250]}
                break
        if not found:
            found = {"acc": acc, "filed": r.filingDate, "doc": None, "dateline": None, "context": "", "lead": ""}
        res.append(found)
        print(found["filed"], found["dateline"], "|", found["lead"][:150])
    json.dump(res, open(OUT, "w"), indent=1)

if __name__ == "__main__":
    main([int(a) for a in sys.argv[1:]])
