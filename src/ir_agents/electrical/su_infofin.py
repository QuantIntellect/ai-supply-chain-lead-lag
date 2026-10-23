"""Pull Schneider (ISIN FR0000121972) regulated-information records from the
AMF/DILA info-financiere OpenDataSoft API (flux-amf-new-prod)."""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from irlib import *

ISIN = sys.argv[1] if len(sys.argv) > 1 else "FR0000121972"
TICK = sys.argv[2] if len(sys.argv) > 2 else "SU.PA"
base = "https://www.info-financiere.gouv.fr/api/explore/v2.1/catalog/datasets/flux-amf-new-prod/records"
f = Fetcher()
allrec = []
offset = 0
while True:
    params = {"where": f'identificationsociete_iso_cd_isi="{ISIN}"', "limit": 100,
              "offset": offset, "order_by": "informationdeposee_inf_dat_emt"}
    r = f.get(base, params=params)
    if r.status_code != 200:
        print("HTTP", r.status_code, r.text[:300]); break
    d = r.json()
    recs = d.get("results", [])
    allrec += recs
    print("total", d.get("total_count"), "got", len(allrec))
    if len(recs) < 100 or offset + 100 >= 10000:
        break
    offset += 100
out = os.path.join(RAW_IR, TICK, "pages", "infofin_records.json")
ensure(os.path.dirname(out))
json.dump(allrec, open(out, "w"), ensure_ascii=False, indent=0)
print("saved", out, len(allrec))
