"""Parse Prysmian 2024+ press-release segment tables ('BUSINESS OVERVIEW' rows) into JSON:
data/raw/ir/PRY.MI/segment_tables.json  {period: [ {seg: {...}}, ... ] } (one list item per table, in order)."""
import sys; sys.path.insert(0, "/Users/sinamirzaei/Documents/aimapping/src/ir_agents/energy"); import irlib
import json, os, re
ROW = re.compile(r"(TRANSMISSION|POWER GRID|ELECTRIFICATION|INDUSTRIAL & CONS(?:TRUCTION)?\.?|SPECIALTIES|DIGITAL SOLUTIONS|TOTAL GROUP)"
                 r"\s+(\d[\d,]*)\s+(\d[\d,]*)\s+([-+]?[\d.]+)%\*?\s+(-?\d[\d,]*)\s+(-?\d[\d,]*)\s+(-?[\d.]+)%\s+(-?[\d.]+)%"
                 r"(?:\s+(-?[\d.]+)%\s+(-?[\d.]+)%)?", re.I)
NAME = {"TRANSMISSION": "Transmission", "POWER GRID": "Power Grid", "ELECTRIFICATION": "Electrification",
        "SPECIALTIES": "Specialties", "DIGITAL SOLUTIONS": "Digital Solutions", "TOTAL GROUP": "Total Group"}
f = lambda s: float(s.replace(",", ""))
out = {}
for p in sys.argv[1:]:
    t = re.sub(r"\s+", " ", open(os.path.join(irlib.TEXT_IR, "PRY.MI", f"{p}_press_release.txt"), encoding="utf-8").read())
    tables, cur = [], {}
    for m in ROW.finditer(t):
        nm = m.group(1).upper()
        nm = "Industrial & Construction" if nm.startswith("INDUSTRIAL") else NAME[nm]
        d = {"revenue": f(m.group(2)), "revenue_prior": f(m.group(3)), "organic_growth_pct": float(m.group(4)),
             "adj_ebitda": f(m.group(5)), "adj_ebitda_prior": f(m.group(6)),
             "margin_pct": float(m.group(7)), "margin_prior_pct": float(m.group(8))}
        if m.group(9):
            d["margin_current_metal_pct"] = float(m.group(9)); d["margin_current_metal_prior_pct"] = float(m.group(10))
        if nm in cur and nm != "Total Group":
            tables.append(cur); cur = {}
        cur[nm] = d
        if nm == "Total Group":
            tables.append(cur); cur = {}
    if cur: tables.append(cur)
    out[p] = tables
    print(p, [(len(tb), tb.get("Total Group", {}).get("revenue")) for tb in tables])
json.dump(out, open(os.path.join(irlib.RAW_IR, "PRY.MI", "segment_tables.json"), "w"), indent=1)
