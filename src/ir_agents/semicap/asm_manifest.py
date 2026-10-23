"""Build data/processed/ir/ASM.AS_manifest.csv for downloaded ASM documents."""
import sys, os, json, glob, re
import pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from irlib import write_manifest, PROC_IR, RAW_IR
T = "ASM.AS"; ROOT = "/Users/sinamirzaei/Documents/aimapping"
SP = "/private/tmp/claude-501/-Users-sinamirzaei-Documents-aimapping/57e0a0d0-6441-40ef-828b-57eeb87e7b21/scratchpad/asm"
urls = json.load(open(os.path.join(SP, "dl_urls.json")))
urls["data/raw/ir/ASM.AS/2023Q3_presentation.pdf"] = ("https://web.archive.org/web/20231206072953id_/https://www.asm.com/media/"
                                                      "u3up3vrs/2023_q3_investor-presentation.pdf")
ev = pd.read_csv(os.path.join(PROC_IR, f"{T}_events.csv"), dtype=str)
rel = {r.fiscal_period: r.event_date for r in ev.itertuples() if r.event_type in ("Q1", "Q2", "Q3", "Q4")}
rows = []
for p in sorted(glob.glob(os.path.join(RAW_IR, T, "*.pdf"))):
    rp = os.path.relpath(p, ROOT)
    per, dt = os.path.basename(p)[:-4].split("_", 1)
    rows.append({"ticker": T, "local_path": rp, "url": urls.get(rp, ""), "doc_type": dt, "fiscal_period": per,
                 "pub_date": rel.get(per, "")})
for s in json.load(open(os.path.join(SP, "special.json"))):
    rows.append({"ticker": T, "local_path": os.path.relpath(s["path"], ROOT), "url": s["url"], "doc_type": "press_release",
                 "fiscal_period": s["period"], "pub_date": s["date_local"]})
df = write_manifest(T, rows)
print(len(df), df.doc_type.value_counts().to_dict(), (df.url == "").sum(), "missing urls")
