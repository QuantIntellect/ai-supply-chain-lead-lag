"""Pull Legrand records from the AMF regulated-information feed (info-financiere.gouv.fr, OpenDataSoft API)."""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from irlib import *

ISIN = sys.argv[1] if len(sys.argv) > 1 else "FR0010307819"
OUT = sys.argv[2] if len(sys.argv) > 2 else os.path.join(RAW_IR, "LR.PA", "amf", "amf_records.json")
API = "https://www.info-financiere.gouv.fr/api/explore/v2.1/catalog/datasets/flux-amf-new-prod/records"
f = Fetcher()
recs, off = [], 0
while True:
    r = f.get(API, params={"where": f'identificationsociete_iso_cd_isi="{ISIN}"', "limit": 100, "offset": off,
                           "order_by": "informationdeposee_inf_dat_emt"})
    if r.status_code != 200:
        print("status", r.status_code, r.text[:300]); break
    d = r.json()
    res = d.get("results", [])
    recs += res
    print("got", len(res), "total", d.get("total_count"))
    off += len(res)
    if not res or off >= d.get("total_count", 0) or off >= 9900:
        break
ensure(os.path.dirname(OUT))
json.dump(recs, open(OUT, "w"), ensure_ascii=False, indent=0)
print(len(recs))
