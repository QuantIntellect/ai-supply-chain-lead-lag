"""Build data/processed/ir/LR.PA_kpis.csv from Legrand results press-release texts.
Quarterly sales are derived as differences of cumulative (3M/6M/9M/12M) consolidated sales
reported in consecutive releases; prior-year quarters likewise from the prior-year columns."""
import os, sys, re, json
import pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from irlib import *
TK = "LR.PA"
NUM = r"\d[\d,]*(?:[ ]\d{3})*(?:\.\d+)?"
PCT = r"[+\-−]?\d+(?:[\.,]\d+)?\s?%"


def num(s):
    return float(s.replace(",", "").replace(" ", ""))


def pct(s):
    return float(s.replace("−", "-").replace("%", "").replace(",", ".").strip())


ev = pd.read_csv(os.path.join(PROC_IR, f"{TK}_events.csv"), dtype=str).fillna("")
rel_date = {r.fiscal_period: r.event_date for r in ev.itertuples() if r.event_type in ("Q1", "H1", "Q3", "FY")}
QEND = {1: "03-31", 2: "06-30", 3: "09-30", 4: "12-31"}
data = {}
FIRST_FY = int(sys.argv[1]) if len(sys.argv) > 1 else 2022
for fy in range(FIRST_FY, 2027):
    for q in range(1, 5):
        fp = f"{fy}Q{q}"
        p = os.path.join(TEXT_IR, TK, f"{fp}_release.txt")
        if not os.path.exists(p):
            continue
        t = re.sub(r"\s+", " ", open(p, encoding="utf-8").read())
        d = {"fp": fp}
        m = re.search(r"Key figures.{0,250}?Sales (" + NUM + r") (" + NUM + r") (" + PCT + ")", t)
        if m:
            d["cum_prior"], d["cum_cur"], d["cum_chg"] = num(m.group(1)), num(m.group(2)), pct(m.group(3))
        else:  # 3-column layout (e.g. 2021 releases: 2019 | 2020 | 2021)
            m = re.search(r"Key figures.{0,250}?Sales (" + NUM + r") (" + NUM + r") (" + NUM + r") (" + PCT + ")", t)
            if m:
                d["cum_prior"], d["cum_cur"], d["cum_chg"] = num(m.group(2)), num(m.group(3)), pct(m.group(4))
        m = re.search(r"Adjusted(?:\(\d\))? operating profit (" + NUM + r") (" + NUM + r") " + PCT + r" As % of sales (" + PCT + r") (" + PCT + ")", t)
        if m:
            d["adj_op_margin_cum"] = pct(m.group(4))
            d["adj_op_margin_cum_prior"] = pct(m.group(3))
        m = re.search(r"Changes in sales by destination at constant scope.{0,400}?Total (" + PCT + r")(?: (" + PCT + r"))?", t)
        if m:
            d["org_cum"] = pct(m.group(1))
            if m.group(2):
                d["org_q"] = pct(m.group(2))
        # guidance (first statement of full-year targets)
        g = re.search(r"(targeting (?:the following )?(?:for |in )?(?:full-year )?20\d\d|20\d\d (?:full-year )?targets?[^.]{0,40}(?:confirmed|raised|unchanged|specified|revised)?)[^.]{0,30}:?(.{0,600})", t, re.I)
        gt = g.group(0) if g else ""
        d["guid_raw"] = gt
        so = re.search(r"organic (?:sales )?growth (?:of )?(?:between )?(" + PCT + r")(?: and| to) (" + PCT + ")", gt, re.I)
        sg = re.search(r"sales growth[^%]{0,140}?(?:between )?(" + PCT + r")(?: and| to) (" + PCT + ")", gt, re.I)
        mg = re.search(r"adjusted operating margin[^%]{0,90}?(?:between |of )?(\d+(?:\.\d+)?\s?%)(?: and| to) (\d+(?:\.\d+)?\s?%)", gt, re.I)
        d["g_org"] = (pct(so.group(1)), pct(so.group(2))) if so else None
        d["g_sales"] = (pct(sg.group(1)), pct(sg.group(2))) if sg else None
        d["g_margin"] = (pct(mg.group(1)), pct(mg.group(2))) if mg else None
        dc = re.findall(r"datacenters?[^.]{0,110}?(\d+)% of (?:our |Group |total )?(?:sales|revenue)", t, re.I)
        d["dc_share_mentions"] = sorted(set(dc))
        data[fp] = d

rows = []
for fp in sorted(data):
    d = data[fp]
    fy, q = int(fp[:4]), int(fp[-1])
    prev = data.get(f"{fy}Q{q-1}") if q > 1 else None
    rev = rev_prior = None
    if "cum_cur" in d:
        if q == 1:
            rev, rev_prior = d["cum_cur"], d["cum_prior"]
        elif prev and "cum_cur" in prev:
            rev = round(d["cum_cur"] - prev["cum_cur"], 1)
            rev_prior = round(d["cum_prior"] - prev["cum_prior"], 1)
    extra = {"organic_growth_q_pct": d.get("org_q") if q > 1 else d.get("org_cum"),
             "organic_growth_ytd_pct": d.get("org_cum"),
             "sales_ytd": d.get("cum_cur"), "sales_ytd_yoy_pct": d.get("cum_chg"),
             "adj_operating_margin_ytd_pct": d.get("adj_op_margin_cum"),
             "revenue_q_method": "difference of cumulative consolidated sales" if q > 1 else "reported Q1 sales",
             "guidance_sales_growth_exfx_pct": d["g_sales"], "guidance_organic_growth_pct": d["g_org"],
             "guidance_adj_op_margin_pct": d["g_margin"], "dc_share_mentions_pct": d["dc_share_mentions"]}
    row = {"fiscal_period": fp, "period_end": f"{fy}-{QEND[q]}", "release_date": rel_date.get(fp, ""),
           "currency": "EUR", "unit": "m", "revenue": rev,
           "revenue_yoy_pct": round((rev / rev_prior - 1) * 100, 1) if rev and rev_prior else "",
           "orders": "", "orders_yoy_pct": "", "book_to_bill": "", "backlog": "", "gross_margin_pct": "",
           "guidance_text": "", "guidance_rev_low": "", "guidance_rev_high": "",
           "ai_dc_notes": "", "extra_json": extra,
           "source_doc": f"data/processed/ir_text/{TK}/{fp}_release.txt"}
    if d["g_org"]:
        row["guidance_rev_low"], row["guidance_rev_high"] = d["g_org"]
    rows.append(row)
json.dump({k: {kk: vv for kk, vv in v.items()} for k, v in data.items()},
          open(os.path.join(RAW_IR, TK, "kpi_parse_debug.json"), "w"), indent=0, default=str)
for r in rows:
    e = r["extra_json"]
    print(r["fiscal_period"], r["revenue"], r["revenue_yoy_pct"], "org_q", e["organic_growth_q_pct"], "ytd", e["organic_growth_ytd_pct"],
          "m", e["adj_operating_margin_ytd_pct"], "gS", e["guidance_sales_growth_exfx_pct"], "gO", e["guidance_organic_growth_pct"],
          "gM", e["guidance_adj_op_margin_pct"], "dc", e["dc_share_mentions_pct"])
json.dump(rows, open(os.path.join(RAW_IR, TK, "kpi_rows.json"), "w"), indent=0, default=str)
