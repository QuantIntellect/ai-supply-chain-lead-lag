"""NKT KPI panel FY2022Q1 -> FY2026Q2 (+ FY rows): numbers from NKT's quarterly-figures workbook
(latest: H1 2026), HV/Transmission order backlog + outlook + DC notes from the interim/annual report texts.
revenue = revenue at standard metal prices (NKT headline & guidance basis); market-price revenue in extra_json."""
import sys, re, os, glob
import pandas as pd
sys.path.insert(0, "/Users/sinamirzaei/Documents/aimapping/src/ir_agents/energy"); import irlib

T = "NKT.CO"
WB = sorted(glob.glob(os.path.join(irlib.RAW_IR, T, "FY2026H1_quarterly-figures-*.xlsx")))[0]
WB_REL = os.path.relpath(WB, irlib.ROOT)


def sheet_map(sh):
    d = pd.read_excel(WB, sheet_name=sh, header=None)
    yr, cols = None, {}
    for j in range(d.shape[1]):
        y = d.iloc[1, j]
        if isinstance(y, (int, float)) and not pd.isna(y) and 2000 < y < 2100:
            yr = int(y)
        q = str(d.iloc[2, j]).strip()
        if yr and q in ("Q1", "Q2", "Q3", "Q4", "Total"):
            cols[(yr, q)] = j
    return d, cols


def row_val(d, cols, row_label_idx, yr, q):
    j = cols.get((yr, q))
    if j is None:
        return None
    v = d.iloc[row_label_idx, j]
    if isinstance(v, str):
        v = v.strip()
        if not v or v in ("-", "n/a", "na"):
            return None
        if v.endswith("%"):
            return float(v[:-1].replace(",", ".")) / 100.0
        return float(v.replace(",", ""))
    return None if pd.isna(v) else float(v)


def find_row(d, section, label, start=0):
    sec = None
    for i in range(start, len(d)):
        lab = str(d.iloc[i, 0]).strip()
        if lab.startswith(section):
            sec = i
        if sec is not None and i > sec and lab == label:
            return i
    return None


fh, fhc = sheet_map(" Financial Highlights")
new, newc = sheet_map("Segment Data 2024-2026")
old, oldc = sheet_map("OLD_Segment Data 2017-2025")
R_MKT = find_row(fh, "Income Statement", "Revenue, market prices")
R_STD = find_row(fh, "Income Statement", "Revenue, standard metal prices")

man = irlib.read_csv(f"data/processed/ir/{T}_manifest.csv")
rep = {r["fiscal_period"]: r for r in man if r["doc_type"] == "report"}
ev = {r["fiscal_period"]: r["event_date"] for r in irlib.read_csv(f"data/processed/ir/{T}_events.csv")
      if r["event_type"] in ("Q1", "Q2", "Q3", "H1", "FY")}


def text(fp):
    p = os.path.join(irlib.TEXT_IR, T, f"{fp}_report.txt")
    return re.sub(r"\s+", " ", open(p, encoding="utf-8").read()) if os.path.exists(p) else ""


def parse_text(t):
    out = {}
    m = re.search(r"(?:high-voltage|Transmission|HV) order backlog,?\s?(?:was|of|amounted to|at|stood at|reached|totall?ed|increased to|grew to|is)?\s?(?:a (?:new )?record(?:-high)? (?:level )?(?:of )?)?(?:EUR|€)\s?(\d+(?:\.\d+)?)\s?bn", t, re.I)
    if m:
        out["backlog"] = float(m.group(1)) * 1000
        out["backlog_snip"] = t[max(0, m.start() - 60): m.end() + 40]
    g = e = None
    for mo in re.finditer(r"outlook", t, re.I):
        w = t[mo.start(): mo.start() + 700]
        gg = re.search(r"[Rr]evenues?\s*\((?:in |at )?(?:std\.?|standard) metal prices\).{0,90}?EUR ?~?(\d+(?:\.\d+)?)\s?[-–]\s?(\d+(?:\.\d+)?)\s?bn", w)
        if gg:
            g = gg
            e = re.search(r"[Oo]perational EBITDA.{0,80}?EUR ?(\d+)\s?[-–]\s?(\d+)\s?m\b", w[gg.start():])
            t_win = w
            break
    if g:
        out["g_rev"] = (float(g.group(1)) * 1000, float(g.group(2)) * 1000)
        out["g_txt"] = t_win[g.start(): g.end() + 160][:400]
    if e:
        out["g_ebitda"] = (float(e.group(1)), float(e.group(2)))
    oi = re.search(r"order intake.{0,80}?(?:EUR|€)\s?(\d+(?:\.\d+)?)\s?(bn|m)\b", t, re.I)
    if oi:
        out["order_intake"] = float(oi.group(1)) * (1000 if oi.group(2) == "bn" else 1)
        out["oi_snip"] = t[max(0, oi.start() - 40): oi.end() + 20]
    dc = []
    for mm in re.finditer(r"data[ -]?cent(?:er|re)s?", t, re.I):
        a = max(t.rfind(". ", 0, mm.start()) + 2, mm.start() - 200)
        b = t.find(". ", mm.end()); b = min(b if b > 0 else mm.end() + 160, mm.end() + 160)
        s = t[a:b + 1].strip()
        if s not in dc:
            dc.append(s)
        if len(dc) >= 2:
            break
    out["dc"] = " | ".join(dc)[:600]
    return out


SEG_NEW = ["NKT - Transmission", "NKT - Grid solutions & Accessories", "NKT - Distribution"]
SEG_OLD = ["NKT - Solutions", "NKT - Applications", "NKT - Service & Accessories"]
rows = []
for yr in range(2022, 2027):
    for q in ("Q1", "Q2", "Q3", "Q4", "Total"):
        fp = f"FY{yr}" if q == "Total" else f"FY{yr}{q}"
        doc_fp = f"FY{yr}" if q in ("Q4", "Total") else (f"FY{yr}H1" if (yr >= 2026 and q == "Q2") else fp)
        std = row_val(fh, fhc, R_STD, yr, q)
        if q == "Total" and yr >= 2026:
            continue
        if std is None:
            continue
        mkt = row_val(fh, fhc, R_MKT, yr, q)
        use_new = yr >= 2024
        d, c, segs = (new, newc, SEG_NEW) if use_new else (old, oldc, SEG_OLD)
        grp = "NKT Group" if use_new else "NKT Group"
        r_ebitda = find_row(d, "Operational EBITDA", grp)
        org_label = "NKT Group" if use_new else "NKT"
        r_org = find_row(d, "Organic growth", org_label)
        ebitda = row_val(d, c, r_ebitda, yr, q)
        ebitda_scope = "NKT Group"
        if ebitda is None and not use_new:
            ebitda = row_val(d, c, find_row(d, "Operational EBITDA", "NKT"), yr, q)
            ebitda_scope = "NKT power cables (excl. NKT Photonics)"
        org = row_val(d, c, r_org, yr, q) if r_org is not None else None
        if org is None and use_new:
            org = row_val(old, oldc, find_row(old, "Organic growth", "NKT"), yr, q)
        ex = {"basis": "12M" if q == "Total" else "Q", "market_price_revenue": mkt,
              "revenue_def": "revenue at standard metal prices (EUR m)", "fin_source": WB_REL}
        if ebitda is not None:
            ex["operational_ebitda"] = round(ebitda, 1)
            ex["margin_pct"] = round(100 * ebitda / std, 1) if std else None
            ex["margin_def"] = "operational EBITDA / revenue at std metal prices (computed from workbook values)"
            ex["operational_ebitda_scope"] = ebitda_scope
        if org is not None:
            ex["organic_growth_pct"] = round(org * 100, 1) if abs(org) < 3 else round(org, 1)
            if not use_new:
                ex["organic_growth_scope"] = "NKT power cables (excl. NKT Photonics)"
        seg = {}
        for s in segs:
            sv = {}
            i1 = find_row(d, "Revenue* (std. metal prices)", s); i2 = find_row(d, "Operational EBITDA", s); i3 = find_row(d, "Organic growth", s)
            v1 = row_val(d, c, i1, yr, q) if i1 is not None else None
            v2 = row_val(d, c, i2, yr, q) if i2 is not None else None
            v3 = row_val(d, c, i3, yr, q) if i3 is not None else None
            if v1 is not None: sv["revenue_std"] = round(v1, 1)
            if v2 is not None: sv["operational_ebitda"] = round(v2, 1)
            if v3 is not None: sv["organic_growth_pct"] = round(v3 * 100, 1) if abs(v3) < 3 else round(v3, 1)
            if sv:
                seg[s.replace("NKT - ", "")] = sv
        ex["segments"] = seg
        t = text(doc_fp) if q != "Total" or True else ""
        tp = parse_text(t) if t else {}
        r = {"fiscal_period": fp, "period_end": f"{yr}-" + {"Q1": "03-31", "Q2": "06-30", "Q3": "09-30", "Q4": "12-31", "Total": "12-31"}[q],
             "release_date": ev.get(doc_fp, ""), "currency": "EUR", "unit": "m", "revenue": round(std, 1),
             "source_doc": rep[doc_fp]["local_path"] if doc_fp in rep else WB_REL}
        if "backlog" in tp:
            r["backlog"] = tp["backlog"]
            ex["backlog_def"] = "high-voltage (from 2025: Transmission) order backlog at period end, EUR"
        if "g_rev" in tp or "g_ebitda" in tp:
            ex["guidance_year"] = yr + 1 if q in ("Q4", "Total") else yr
        if "g_rev" in tp:
            r["guidance_rev_low"], r["guidance_rev_high"] = tp["g_rev"]
            ex["guidance_rev_basis"] = "full-year revenue at std metal prices, EUR m"
            r["guidance_text"] = tp["g_txt"]
        if "g_ebitda" in tp:
            ex["guidance_year"] = yr + 1 if q in ("Q4", "Total") else yr
            ex["guidance_other"] = [{"metric": "operational EBITDA (full year)", "low": tp["g_ebitda"][0], "high": tp["g_ebitda"][1], "unit": "EUR m"}]
        if "order_intake" in tp:
            ex["order_intake_snippet"] = tp["oi_snip"][:160]
        r["ai_dc_notes"] = tp.get("dc", "")
        r["extra_json"] = ex
        rows.append(r)
        print(f"{fp:9s} rel={r['release_date']} std={std:7.1f} mkt={mkt or 0:7.1f} ebitda={ex.get('operational_ebitda')} org={ex.get('organic_growth_pct')} "
              f"bl={r.get('backlog')} g={r.get('guidance_rev_low')}-{r.get('guidance_rev_high')}/{tp.get('g_ebitda')} dc={'Y' if r['ai_dc_notes'] else '-'}")
        if "--snips" in sys.argv:
            print("     BL:", tp.get("backlog_snip", "")[:150])
if "--write" in sys.argv:
    irlib.write_kpis(T, rows)
