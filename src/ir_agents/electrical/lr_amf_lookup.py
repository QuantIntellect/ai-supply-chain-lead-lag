"""Print Legrand AMF records (local Paris time) for given date windows. Usage: lr_amf_lookup.py D1[:D2] ..."""
import os, sys, json, datetime as dt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from irlib import *
recs = json.load(open(os.path.join(RAW_IR, "LR.PA", "amf", "amf_records.json")))

def loc(r):
    d = r.get("uin_dat_amf")
    if not d:
        return None
    t = dt.datetime.fromisoformat(d)
    h, m = map(int, (r.get("timezone_uin_dat_amf") or "01:00").split(":"))
    return (t + dt.timedelta(hours=h, minutes=m)).replace(tzinfo=None)

for arg in sys.argv[1:]:
    a, b = (arg.split(":") + [None])[:2]
    b = b or a
    hits = set()
    for r in recs:
        l = loc(r)
        if l and a <= l.strftime("%Y-%m-%d") <= b and (r.get("informationdeposee_inf_lng_inf") or "").startswith("An"):
            hits.add((l.strftime("%Y-%m-%d %H:%M"), r.get("informationdeposee_inf_stp_pri"), (r.get("informationdeposee_inf_tit_inf") or "")[:60]))
    print(arg, sorted(hits) if hits else "NONE")
