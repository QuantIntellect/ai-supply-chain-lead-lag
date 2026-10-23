"""Assemble data/processed/ir/MTRS.ST_kpis.csv (2022Q1 -> latest reported quarter).

Sources per quarter (as reported at the time of release):
  * own interim report: page-1 financial summary (orders, net sales, delta %,
    organic sales growth, adj. EBITA margin), text (organic order growth,
    outlook / mid-term targets, data-center commentary), business-area tables;
  * "Quarterly overview" table (9 quarters) of the same report for order backlog;
    for 2022Q3/2022Q4/2023Q1 (PDF text layer is fragmented) the overview table of
    the 2023Q2 / 2024Q2 report is used and flagged in extra_json.
"""
import os
import re
import sys
import json
import glob

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from irlib import RAW_IR, TEXT_IR, write_kpis  # noqa: E402
from mtrs_kpi_parse import parse_report, norm, num, NUM  # noqa: E402
from mtrs_events import SPEC  # noqa: E402

T = "MTRS.ST"
REL = {fp: d for d, k, et, fp in SPEC if et in ("Q1", "Q2", "Q3", "Q4")}
QEND = {1: "03-31", 2: "06-30", 3: "09-30", 4: "12-31"}


def qprev(per, k=1):
    y, q = int(per[:4]), int(per[5])
    i = y * 4 + (q - 1) - k
    return f"{i // 4}Q{i % 4 + 1}"


def txt(per):
    return norm(open(os.path.join(TEXT_IR, T, f"{per}_interim_report.txt"), encoding="utf-8").read())


def despace(tt):
    """Repair fragmented PDF text: '- 4 4 %' -> '-44%', '+ 145 %' -> '+145%'."""
    for _ in range(3):
        tt = re.sub(r"(?<=[\d+\-]) (?=[\d%])", "", tt)
    return tt


def overview(per):
    """Parse 'Quarterly overview' table -> {period: {row: value}}."""
    tt = txt(per)
    m = re.search(r"Quarterly overview.{0,200}?MSEK((?: Q[1-4]){8,9})", tt)
    if not m:
        return {}
    labels = m.group(1).split()
    periods = [qprev(per, i) for i in range(len(labels))]
    seg = tt[m.end(): m.end() + 6000]
    out = {p: {} for p in periods}
    n = len(labels)
    rows = {"backlog": r"Order backlog", "orders": r"Order intake", "net_sales": r"Net sales",
            "adj_ebita": r"Adjusted EBITA", "org_ns": r"Organic Growth, Net Sales",
            "fx_adj_ns": r"Currency adjusted Growth, Net Sales",
            "adj_ebita_margin": r"Adjusted EBITA margin, %"}
    for key, lab in rows.items():
        mm = re.search(lab + r" ((?:-?\d{1,3}(?:,\d{3})*(?:\.\d+)?%%? ){%d})" % n, seg + " ")
        if not mm:
            continue
        vals = [num(v.rstrip("%")) for v in mm.group(1).split()]
        for p, v in zip(periods, vals):
            out[p][key] = v
    return out


def org_orders(tt):
    t2 = despace(tt)
    pats = [r"Order intake (?:amounted to|was) MSEK %s \(%s\),? \((?:organic(?: development of)?|"
            r"organically) ([+-]?\d+(?:\.\d+)?)%%" % (NUM, NUM),
            r"Order intake (?:increased|decreased) by [+-]?\d+% FX ?-?adjusted \(organic ([+-]?\d+)%",
            r"Order intake (?:increased|decreased) [+-]?\d+(?:\.\d+)? per cent \(([+-]?\d+) organic\)",
            r"Order intake (?:increased|decreased) by [+-]?\d+%, a currency adjusted (?:increase|decrease)"
            r" of [+-]?\d+% and an organic (?:growth|decline|decrease|increase) of ([+-]?\d+)%",
            r"Order intake (?:increased|decreased) ([+-]?\d+)% organically",
            r"Order intake (?:was|amounted to) MSEK %s \(%s\),? \(organic ([+-]?\d+)%%" % (NUM, NUM),
            r"Order intake was [^(]{0,40}?FX ?-?adjusted \(organic ([+-]?\d+)%",
            r"Order intake (?:increased|decreased) by [+-]?\d+% \(an organic (?:growth|decline|decrease|increase) of ([+-]?\d+)%"]
    best = None
    for p in pats:
        m = re.search(p, t2, re.I)
        if m and (best is None or m.start() < best.start()):
            best = m
    return num(best.group(1).lstrip("+")) if best else None


def guidance(tt):
    parts = []
    m = re.search(r"Business Outlook (20\d\d)\*+ Net sales (Expected to .{5,120}?) Adjusted EBITA margin "
                  r"(Expected to .{5,140}?) Tax rate", tt)
    if m:
        parts.append(f"Business outlook {m.group(1)}: net sales {m.group(2).strip()}; "
                     f"adj. EBITA margin {m.group(3).strip()}")
    m = re.search(r"Midterm financial targets.{0,80}?Net sales growth: (.{10,120}?)\.? ?Performance", tt)
    if m:
        parts.append("Mid-term target: " + m.group(1).strip())
    m = re.search(r"Adjusted EBITA margin: (.{5,80}?)\.? ?Performance", tt)
    if m:
        parts.append("adj. EBITA margin target: " + m.group(1).strip())
    m = re.search(r"((?:Our outlook|We expect|We maintain our (?:business )?outlook)[^.]{10,220}\.)", tt)
    if m:
        parts.append("Outlook: " + m.group(1).strip())
    return "; ".join(parts)[:700]


DC_PAT = re.compile(r"(data cent|DCT|hyperscal|colocation|\bAI\b|liquid cool|chiller|SyCool|CDU)", re.I)


def clean(s):
    s = re.sub(r"=== page \d+ ===", " ", s)
    m = re.search(r"(Order intake|Net sales|DCT|Data Center|Demand|The adjusted|In DCT|Our |We |"
                  r"Strong|Record|Munters)", s)
    if m and m.start() > 0 and re.search(r"(page|Interim report|October|July|April|January|"
                                         r"EBITA margin \d|\d%$)", s[:m.start()]):
        s = s[m.start():]
    return re.sub(r"\s+", " ", s).strip(" -–•|")


def dc_notes(tt, maxn=3):
    sents = [clean(x) for x in re.split(r"(?<=[.!?]) (?=[A-Z–-])", tt[:40000])]
    picks = []
    for s in sents:
        s = s.strip(" -–•")
        if 40 < len(s) < 330 and DC_PAT.search(s) and re.search(
                r"(order|demand|growth|grew|increase|declin|backlog|sales|AI|hyperscal|record)", s, re.I):
            if not any(s[:60] == p[:60] for p in picks):
                picks.append(s)
        if len(picks) >= maxn:
            break
    return " | ".join(picks)[:900]


def main():
    reps = sorted(os.path.basename(p).split("_")[0]
                  for p in glob.glob(os.path.join(TEXT_IR, T, "*_interim_report.txt")))
    ov = {p: overview(p) for p in reps}
    parsed = {p: parse_report(os.path.join(TEXT_IR, T, f"{p}_interim_report.txt")) for p in reps}
    rows = []
    for per in reps:
        if per < "2022Q1":
            continue
        tt = txt(per)
        d = parse_report(os.path.join(TEXT_IR, T, f"{per}_interim_report.txt"))
        own = ov.get(per, {}).get(per, {})
        flags = {}
        # fallbacks from later reports' quarterly overview tables
        fb = {}
        for later in reps:
            if later > per and per in ov.get(later, {}) and ov[later][per]:
                fb = ov[later][per]
                fb_src = later
                break
        orders, revenue = d["orders"], d["revenue"]
        o_yoy, r_yoy = d["orders_yoy"], d["revenue_yoy"]
        if orders is None and fb.get("orders") is not None:
            orders, flags["orders_src"] = fb["orders"], f"quarterly overview in {fb_src} report"
        if revenue is None and fb.get("net_sales") is not None:
            revenue, flags["revenue_src"] = fb["net_sales"], f"quarterly overview in {fb_src} report"
        backlog = own.get("backlog")
        if backlog is None and fb.get("backlog") is not None:
            backlog, flags["backlog_src"] = fb["backlog"], f"quarterly overview in {fb_src} report"
        # prior-year same-basis levels for computed YoY when not stated
        py = qprev(per, 4)
        if o_yoy is None and orders is not None:
            base = ov.get(per, {}).get(py, {}) or (ov.get(fb_src, {}).get(py, {}) if fb else {})
            if base.get("orders"):
                o_yoy = round(100 * (orders / base["orders"] - 1), 1)
                flags["orders_yoy_computed"] = True
        if r_yoy is None and revenue is not None:
            base = ov.get(per, {}).get(py, {}) or (ov.get(fb_src, {}).get(py, {}) if fb else {})
            if base.get("net_sales"):
                r_yoy = round(100 * (revenue / base["net_sales"] - 1), 1)
                flags["revenue_yoy_computed"] = True
        org_ns = d["organic_sales_growth_pct"]
        if org_ns is None:
            org_ns = own.get("org_ns", fb.get("org_ns"))
        margin = d["adj_ebita_margin_pct"]
        if margin is None:
            margin = own.get("adj_ebita_margin", fb.get("adj_ebita_margin"))
        segs = {}
        for name, v in d["ba"].items():
            v = dict(v)
            if v.get("orders") and v.get("orders_prior") and v.get("orders_yoy_pct") is not None:
                calc = 100 * (v["orders"] / v["orders_prior"] - 1)
                if abs(calc - v["orders_yoy_pct"]) > 6:
                    v["orders_yoy_pct"] = None
            v.pop("orders_prior", None)
            if isinstance(v.get("orders_yoy_pct"), float) is False:
                v["orders_yoy_pct"] = None if not isinstance(v.get("orders_yoy_pct"), (int, float)) else v["orders_yoy_pct"]
            segs[name] = v
        nxt = qprev(per, -4)
        if nxt in parsed:
            for name, v in parsed[nxt]["ba"].items():
                if name in ("AirTech", "Data Center Technologies", "FoodTech") and (
                        name not in segs or segs[name].get("orders") is None) and v.get("orders_prior"):
                    segs.setdefault(name, {})["orders"] = v["orders_prior"]
                    segs[name]["orders_src"] = f"prior-year column of {nxt} report (may be restated)"
        if per.endswith("Q1"):  # derive Q1 from next report's H1 YTD minus Q2 when missing
            q2 = per[:4] + "Q2"
            for name, v in parsed.get(q2, {}).get("ba", {}).items():
                if (name not in segs or segs[name].get("orders") is None) and v.get("orders_ytd") \
                        and v.get("orders") is not None:
                    segs.setdefault(name, {})["orders"] = round(v["orders_ytd"] - v["orders"], 1)
                    segs[name]["orders_src"] = f"derived: Jan-Jun minus Apr-Jun in {q2} report"
        for v in segs.values():
            v.pop("orders_ytd", None)
        dct = segs.get("Data Center Technologies", {})
        prefix = ""
        if dct.get("orders") is not None:
            prefix = f"DCT orders {dct['orders']:,.0f} MSEK"
            if dct.get("orders_yoy_pct") is not None:
                prefix += f" ({dct['orders_yoy_pct']:+.0f}% y/y)"
            if dct.get("net_sales") is not None:
                prefix += f"; DCT net sales {dct['net_sales']:,.0f}"
            if dct.get("backlog") is not None:
                prefix += f"; DCT ext. backlog {dct['backlog']:,.0f}"
            prefix += ". "
        extra = {"organic_sales_growth_pct": org_ns,
                 "organic_orders_growth_pct": (d["orders_organic_pct"] if d["orders_organic_pct"]
                                               is not None else org_orders(tt)),
                 "adj_ebita_margin_pct": margin,
                 "book_to_bill_calc": round(orders / revenue, 2) if orders and revenue else None,
                 "segments": segs}
        b2b = d["book_to_bill_text"]
        if b2b is not None and extra["book_to_bill_calc"] and abs(b2b - extra["book_to_bill_calc"]) > 0.06:
            extra["book_to_bill_stated_other_scope"] = b2b  # e.g. DCT-level ratio in CEO text
            b2b = None
        extra.update(flags)
        y, q = int(per[:4]), int(per[5])
        rows.append({
            "fiscal_period": per, "period_end": f"{y}-{QEND[q]}", "release_date": REL.get(per, ""),
            "currency": "SEK", "unit": "million", "revenue": revenue, "revenue_yoy_pct": r_yoy,
            "orders": orders, "orders_yoy_pct": o_yoy, "book_to_bill": b2b,
            "backlog": backlog, "gross_margin_pct": None, "guidance_text": guidance(tt),
            "guidance_rev_low": None, "guidance_rev_high": None, "ai_dc_notes": (prefix + dc_notes(tt))[:1000],
            "extra_json": extra,
            "source_doc": f"data/raw/ir/{T}/docs/{per}_interim_report.pdf"})
    p = write_kpis(T, rows)
    print(p, len(rows))
    for r in rows:
        e = json.loads(r["extra_json"]) if isinstance(r["extra_json"], str) else r["extra_json"]
        print(r["fiscal_period"], r["orders"], r["orders_yoy_pct"], "org", e["organic_orders_growth_pct"],
              "| NS", r["revenue"], r["revenue_yoy_pct"], "org", e["organic_sales_growth_pct"],
              "| BL", r["backlog"], "| m", e["adj_ebita_margin_pct"],
              "| flags", [k for k in e if k.endswith(("src", "computed"))])


if __name__ == "__main__":
    main()
