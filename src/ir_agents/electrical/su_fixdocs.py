"""Fix-ups for the Schneider manifest: duplicate 2023Q2 release, 2026Q2 'other'
(presentation), and the H1 2024 release fetched from the AMF/DILA archive."""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from irlib import *
import pandas as pd

T = "SU.PA"
mp = os.path.join(RAW_IR, T, "pages", "manifest_rows.json")
man = json.load(open(mp))
f = Fetcher(min_gap=1.0)
for m in man:
    if m["fiscal_period"] == "2026Q2" and m["doc_type"] == "other":
        new = m["local_path"].replace("_other.pdf", "_presentation.pdf")
        if os.path.exists(m["local_path"]):
            os.rename(m["local_path"], new)
        old_txt = os.path.join(TEXT_IR, T, "2026Q2_other.txt")
        if os.path.exists(old_txt):
            os.remove(old_txt)
        to_text(new, T, "2026Q2", "presentation")
        m["local_path"], m["doc_type"] = new, "presentation"
    if "hy-gross-margin" in m["url"]:
        out = os.path.join(RAW_IR, T, "2023Q2_grossmargin_note.pdf")
        ok, st, p = f.download(m["url"], out)
        print("gm", ok, st, is_pdf(p))
        to_text(p, T, "2023Q2", "grossmargin_note")
        m["local_path"], m["doc_type"] = out, "release_note"
# H1 2024 release from the AMF archive (English version)
df = pd.read_csv(os.path.join(RAW_IR, T, "pages", "infofin_records_flat.csv"))
hit = df[df.title.astype(str).str.fullmatch("Half Year 2024 Results")]
if len(hit) and not any(m["fiscal_period"] == "2024Q2" and m["doc_type"] == "release" for m in man):
    url = hit.iloc[0].url
    out = os.path.join(RAW_IR, T, "2024Q2_release.pdf")
    ok, st, p = f.download(url, out)
    print("h1-2024", ok, st, url, is_pdf(p) if ok else None)
    if ok and is_pdf(p):
        to_text(p, T, "2024Q2", "release")
        man.append({"local_path": p, "url": url, "doc_type": "release", "fiscal_period": "2024Q2", "pub_date": "2024-07-31"})
json.dump(man, open(mp, "w"), indent=1)
write_manifest(T, [dict(m) for m in man])
print(len(man))
