"""Query the 1Info (Computershare) regulated-information storage for PRYSMIAN (ndg 902)
-> data/raw/ir/PRY.MI/1info_index.json (raw rows)."""
import sys; sys.path.insert(0, "/Users/sinamirzaei/Documents/aimapping/src/ir_agents/energy"); import irlib
import json, os, time
URL = "https://www.1info.it/PORTALE1INFO/API/Comunicati"
s = irlib._sess()
allrows, start, length = [], 0, 100
while True:
    data = {"draw": "1", "start": str(start), "length": str(length),
            "order[0][column]": "2", "order[0][dir]": "desc",
            "SearchFilter[emittente]": "902", "SearchFilter[sdir1info]": "true", "SearchFilter[sdirTerzi]": "true"}
    for i, c in enumerate(["", "", "dataDiffusione", "", ""]):
        data[f"columns[{i}][data]"] = c
    time.sleep(1.2)
    r = s.post(URL, data=data, timeout=60, headers={"X-Requested-With": "XMLHttpRequest",
               "Referer": "https://www.1info.it/PORTALE1INFO"})
    if r.status_code != 200:
        print("HTTP", r.status_code, r.text[:300]); break
    j = r.json()
    rows = j.get("data") or []
    if start == 0:
        print("recordsTotal", j.get("recordsTotal"), "recordsFiltered", j.get("recordsFiltered"))
        print(json.dumps(rows[:1], ensure_ascii=False)[:800])
    allrows += rows
    start += length
    if not rows or start >= int(j.get("recordsFiltered") or 0) or start > 5000:
        break
out = os.path.join(irlib.raw_dir("PRY.MI"), "1info_index.json")
json.dump(allrows, open(out, "w"), ensure_ascii=False)
print("rows", len(allrows), "->", out)
