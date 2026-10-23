"""AMF feed records for Legrand by company name (catches records lacking ISIN)."""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from irlib import *
API = "https://www.info-financiere.gouv.fr/api/explore/v2.1/catalog/datasets/flux-amf-new-prod/records"
f = Fetcher()
recs, off = [], 0
where = 'identificationsociete_iso_nom_soc like "LEGRAND%" and (identificationsociete_iso_cd_isi is null or identificationsociete_iso_cd_isi != "FR0010307819")'
while True:
    r = f.get(API, params={"where": where, "limit": 100, "offset": off})
    if r.status_code != 200:
        print("status", r.status_code, r.text[:300]); break
    d = r.json(); res = d.get("results", []); recs += res; off += len(res)
    print("got", len(res), "total", d.get("total_count"))
    if not res or off >= d.get("total_count", 0):
        break
json.dump(recs, open(os.path.join(RAW_IR, "LR.PA", "amf", "amf_records_byname.json"), "w"), ensure_ascii=False, indent=0)
import collections
print(collections.Counter((x.get("identificationsociete_iso_nom_soc"), x.get("identificationsociete_iso_cd_isi")) for x in recs).most_common(10))
