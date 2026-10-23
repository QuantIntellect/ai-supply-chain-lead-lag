"""Final manifest assembly for Legrand: fix mislinked 2016Q3 doc, add misc docs, verify files."""
import os, sys, shutil
import pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from irlib import *
TK = "LR.PA"
mp = os.path.join(PROC_IR, f"{TK}_manifest.csv")
m = pd.read_csv(mp, dtype=str).fillna("").to_dict("records")
m = [r for r in m if not (r["fiscal_period"] == "2016Q3" and r["doc_type"] == "release")]
f = Fetcher()
# 2019 Investor Day press release
p19 = os.path.join(RAW_IR, TK, "2019-06-12_cmd_release.pdf")
u19 = "https://www.legrand.com/sites/default/files/Documents_PDF_Legrand/Finance/2019/autres/Legrand_Press_Release_Investor_Day_2019_1560269114.pdf"
ok, st, _ = f.download(u19, p19)
# 2016 Investor Day release (official AMF copy) -> move into company dir
src16 = os.path.join(RAW_IR, TK, "amf_docs", "FCBWR093922_20160630.pdf")
p16 = os.path.join(RAW_IR, TK, "2016-06-30_cmd_release.pdf")
if os.path.exists(src16) and not os.path.exists(p16):
    shutil.copy(src16, p16)
extra = [
    (os.path.join(RAW_IR, TK, "2016Q3_financial_statements.pdf"), "https://fr.ftp.opendatasoft.com/datadila/INFOFI/BWR/2016/11/FCBWR096806_20161110.pdf", "financial_statements", "2016Q3", "2016-11-10", "2016Q3"),
    (p16, "https://fr.ftp.opendatasoft.com/datadila/INFOFI/BWR/2016/06/FCBWR093922_20160630.pdf", "cmd_release", "", "2016-06-30", "2016-06-30"),
    (p19, u19, "cmd_release", "", "2019-06-12", "2019-06-12"),
    (os.path.join(RAW_IR, TK, "2018-09-11_other.pdf"), "https://www.legrand.com/sites/default/files/Documents_PDF_Legrand/Finance/2018/autres/Press_Release_Legrand_09112018.pdf", "other_release", "", "2018-09-11", "2018-09-11"),
    (os.path.join(RAW_IR, TK, "2022-10-20_other.pdf"), "https://www.legrand.com/sites/default/files/Documents_PDF_Legrand/Finance/2022/autres/Legrand_PressRelease_20102022_1666284381.pdf", "other_release", "", "2022-10-20", "2022-10-20"),
]
have = {r["local_path"] for r in m}
for path, url, dtp, fp, d, tag in extra:
    rel = path.replace(ROOT + "/", "")
    if os.path.exists(path) and is_pdf(path):
        txt = os.path.join(TEXT_IR, TK, f"{tag}_{dtp}.txt")
        if not os.path.exists(txt):
            to_text(path, TK, tag, dtp)
        if rel not in have:
            m.append({"local_path": path, "url": url, "doc_type": dtp, "fiscal_period": fp, "pub_date": d})
# verify
keep = []
for r in m:
    full = r["local_path"] if r["local_path"].startswith("/") else os.path.join(ROOT, r["local_path"])
    if os.path.exists(full) and is_pdf(full):
        keep.append(r)
    else:
        print("dropping missing/non-pdf", r["local_path"])
print(write_manifest(TK, keep), len(keep))
