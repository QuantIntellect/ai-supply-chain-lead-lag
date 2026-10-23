"""Parse Munters interim-report text into a per-quarter KPI digest (JSON).

Writes data/raw/ir/MTRS.ST/kpi_digest.json and prints a compact table.
Numbers are only taken from the report text; anything not matched stays None.
"""
import os
import re
import sys
import json
import glob

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from irlib import RAW_IR, TEXT_IR  # noqa: E402

T = "MTRS.ST"
NUM = r"-?\d{1,3}(?:,\d{3})*(?:\.\d+)?"


def norm(t):
    t = t.replace("−", "-").replace("–", "-").replace("\xa0", " ")
    return re.sub(r"\s+", " ", t)


def num(s):
    if s is None:
        return None
    try:
        return float(s.replace(",", ""))
    except ValueError:
        return None


def row_after(tt, label, n=3, start=0, end=None):
    """First n numbers following `label` (table row) within tt[start:end]."""
    seg = tt[start:end] if end else tt[start:]
    m = re.search(re.escape(label) + r"(?:, ?%%)? ((?:%s%%? ){%d})" % (NUM, n), seg + " ")
    if not m:
        return None
    return [num(x.rstrip("%")) for x in m.group(1).split()]


def first(pat, tt, g=1, flags=re.I):
    m = re.search(pat, tt, flags)
    return m.group(g) if m else None


def parse_report(path):
    tt = norm(open(path, encoding="utf-8").read())
    d = {}
    # Financial summary (page 1): Q current, Q prior, delta
    fs = tt.find("Financial summary")
    seg_end = fs + 6000 if fs >= 0 else 8000
    st = max(fs, 0)
    oi = row_after(tt, "Order intake", 3, st, seg_end)
    ns = row_after(tt, "Net sales", 3, st, seg_end)
    d["orders"], d["orders_prior"], d["orders_yoy"] = (oi or [None] * 3)[:3]
    d["revenue"], d["revenue_prior"], d["revenue_yoy"] = (ns or [None] * 3)[:3]
    org = re.search(r"of which organic growth ((?:-?\d+(?:\.\d+)?%|-) )", tt[st:seg_end])
    d["organic_sales_growth_pct"] = num(org.group(1).strip().rstrip("%")) if org else None
    m = re.search(r"Adjusted EBITA margin,? ?%%? (%s) (%s)" % (NUM, NUM), tt[st:seg_end])
    d["adj_ebita_margin_pct"] = num(m.group(1)) if m else None
    d["adj_ebita_margin_prior_pct"] = num(m.group(2)) if m else None
    # Order intake text: "Order intake was MSEK 4,159 (2,646), (organic +56%"
    m = re.search(r"Order intake (?:was|amounted to|increased to|decreased to|"
                  r"increased by -?\d+%% to|decreased by -?\d+%% to) (?:MSEK|SEKm) (%s) \((%s)\),? "
                  r"\(?(?:of which )?organic(?:ally)? ([+-]?\d+(?:\.\d+)?)%%" % (NUM, NUM), tt, re.I)
    if not m:
        m = re.search(r"Order intake[^.]{0,80}?(?:MSEK|SEKm) (%s) \((%s)\)[^.]{0,80}?"
                      r"([+-]?\d+(?:\.\d+)?)%% organic" % (NUM, NUM), tt, re.I)
    d["orders_organic_pct"] = num(m.group(3).lstrip("+")) if m else None
    # Order backlog at the end of the period
    m = re.search(r"order backlog (?:at the end of the (?:period|quarter) )?(?:amounted to|was|"
                  r"totaled|totalled) (?:MSEK|SEKm) (%s)(?: \((%s)\))?" % (NUM, NUM), tt, re.I)
    d["backlog"] = num(m.group(1)) if m else None
    d["backlog_prior"] = num(m.group(2)) if m and m.group(2) else None
    m = re.search(r"book-to-bill(?: ratio)?(?: of| was| at| amounted to)? (\d+(?:\.\d+)?)", tt, re.I)
    d["book_to_bill_text"] = num(m.group(1)) if m else None
    # Business-area tables: "External order backlog a b c ... Order intake q qp d"
    bas = {}
    tables = []
    for m in re.finditer(r"External order backlog (%s) (%s) (-?\d+|n/?a|-) " % (NUM, NUM), tt):
        after = tt[m.end(): m.end() + 800]
        oi = re.search(r"Order intake (%s) (%s) (-?\d+|n/?a|n\.?m\.?|-|>\d+) (?:(%s) (%s) )?" % (NUM, NUM, NUM, NUM), after)
        ns = re.search(r"Net sales (%s) (%s) (-?\d+) " % (NUM, NUM), after)
        mg = re.search(r"Adjusted EBITA margin,? ?%%? (%s) (%s)" % (NUM, NUM), after)
        tables.append({"orders_ytd": num(oi.group(4)) if oi and oi.group(4) else None,"backlog": num(m.group(1)),
                       "orders": num(oi.group(1)) if oi else None,
                       "orders_prior": num(oi.group(2)) if oi else None,
                       "orders_yoy_pct": num(oi.group(3)) if oi else None,
                       "net_sales": num(ns.group(1)) if ns else None,
                       "net_sales_yoy_pct": num(ns.group(3)) if ns else None,
                       "adj_ebita_margin_pct": num(mg.group(1)) if mg else None})
    names = {3: ["AirTech", "Data Center Technologies", "FoodTech"],
             2: ["AirTech", "FoodTech"]}.get(len(tables))
    if names:
        bas = dict(zip(names, tables))
    d["ba"] = bas
    return d


def main():
    out = {}
    for p in sorted(glob.glob(os.path.join(TEXT_IR, T, "*_interim_report.txt"))):
        per = os.path.basename(p).split("_")[0]
        out[per] = parse_report(p)
    with open(os.path.join(RAW_IR, T, "kpi_digest.json"), "w") as f:
        json.dump(out, f, indent=1)
    for per, d in out.items():
        ba = {k[:4]: (v["orders"], v["orders_yoy_pct"], v["net_sales"]) for k, v in d["ba"].items()}
        print(per, "OI", d["orders"], d["orders_yoy"], "org", d["orders_organic_pct"],
              "| NS", d["revenue"], d["revenue_yoy"], "org", d["organic_sales_growth_pct"],
              "| m", d["adj_ebita_margin_pct"], "| BL", d["backlog"], "| b2b", d["book_to_bill_text"],
              "|", ba)


if __name__ == "__main__":
    main()
