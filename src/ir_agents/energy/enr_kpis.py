"""Parse Siemens Energy earnings releases (extracted text) into data/processed/ir/ENR.DE_kpis.csv.
Group figures: 'II Key figures' table; segments: 'Overview of Segment figures' table; guidance: Outlook section;
FY2022 segments: restated 'Comparable key figures FY2022' (new GS/GT/TI/SGRE structure, published 2023-02-07)."""
import sys; sys.path.insert(0, "/Users/sinamirzaei/Documents/aimapping/src/ir_agents/energy"); import irlib
import re, os, json
T = "ENR.DE"
TXT = os.path.join(irlib.TEXT_IR, T)
SEGS = ["Gas Services", "Grid Technologies", "Transformation of Industry", "Siemens Gamesa Renewable Energy",
        "Siemens Gamesa", "Gas and Power"]
SEGNAME = {"Siemens Gamesa Renewable Energy": "Siemens Gamesa"}


def norm(t):
    t = re.sub(r"\s+", " ", t)
    t = re.sub(r"[¹²³⁴⁵]", "", t)
    t = re.sub(r"(\S)\s+%", r"\1%", t)
    t = re.sub(r"\s+p\.p\.", "p.p.", t)
    return t


def num(tok):
    if tok is None:
        return None
    s = tok.replace(",", "").replace("€", "")
    m = re.fullmatch(r"\(?(-?\d+(?:\.\d+)?)\)?(%|p\.p\.)?", s)
    if not m:
        return None
    v = float(m.group(1))
    return -v if s.startswith("(") else v


def row(text, label, n):
    m = re.search(re.escape(label) + r" ((?:\S+ ){%d}\S+)" % (n - 1), text)
    return m.group(1).split(" ") if m else None


def period_end(fp):
    y = int(fp[2:6])
    suf = fp[6:]
    return {"Q1": f"{y-1}-12-31", "Q2": f"{y}-03-31", "H1": f"{y}-03-31", "Q3": f"{y}-06-30", "_9M": f"{y}-06-30",
            "Q4": f"{y}-09-30", "": f"{y}-09-30"}[suf]


def sentences(t):
    return re.split(r"(?<=[.!?])\s+(?=[A-Z•])", t)


def parse_guidance(t):
    i = [m.start() for m in re.finditer(r"\bOutlook\b", t)]
    j = t.find("Notes and forward-looking")
    if not i:
        return {}
    starts = [k for k in i if k < j] or i
    sec = t[starts[-1]: j if j > starts[-1] else starts[-1] + 3000]
    grp = []
    for s in sentences(sec):
        s2 = s.strip("• ").strip()
        if re.match(r"(GS|GT|TI|Gas Services|Grid Technologies|Transformation of Industry|Siemens Gamesa|SGRE|For the GP segment|GP)\b", s2):
            continue
        if re.search(r"comparable revenue|Profit margin before Special|Adjusted EBITA margin before|Net (income|loss)|Free cash flow pre tax|guidance|outlook", s2, re.I) \
                and re.search(r"Siemens Energy|Group|we (now )?expect|We (now )?expect|management", s2):
            grp.append(s2)
    g = " ".join(grp)[:900]
    g = re.sub(r"\b(neg|pos)- (ative|itive)", r"\1\2", g)
    out = {"guidance_text": g}
    sgn = lambda w: -1 if w and w.strip().lower().startswith("neg") else 1
    rr = re.search(r"comparable revenue (?:growth|development)[^.]*?(?:(?:range of|between|of|be)\s*)?\(?(negative |positive |neg\. |pos\. )?(\d+(?:\.\d+)?)\s?%\s*(?:to|and)\s*(negative |positive |neg\. |pos\. )?(\d+(?:\.\d+)?)\s?%", g)
    if rr:
        out["rev_low"] = sgn(rr.group(1)) * float(rr.group(2))
        out["rev_high"] = sgn(rr.group(3)) * float(rr.group(4))
    other = []
    mm = re.search(r"(Profit margin before Special items|Adjusted EBITA margin before [Ss]pecial items)[^.]*?(?:range of|between|of)\s*(negative |positive )?(\d+(?:\.\d+)?)\s?%\s*(?:to|and)\s*(negative |positive )?(\d+(?:\.\d+)?)\s?%", g)
    if mm:
        other.append({"metric": mm.group(1).lower(), "low": sgn(mm.group(2)) * float(mm.group(3)),
                      "high": sgn(mm.group(4)) * float(mm.group(5)), "unit": "%"})
    for lab, rx in (("net income", r"Net income[^.()€]{0,40}?(?:of around|around|of up to|up to|in the range of|range of|of)\s*€\s?(\d+(?:\.\d+)?)\s?(bn|billion)(?:\s*to\s*€\s?(\d+(?:\.\d+)?)\s?(?:bn|billion))?"),
                    ("free cash flow pre tax", r"Free cash flow pre tax[^.()€]{0,40}?(?:of around|around|of up to|up to|in the range of|range of|of)\s*€\s?(\d+(?:\.\d+)?)\s?(bn|billion)(?:\s*to\s*€\s?(\d+(?:\.\d+)?)\s?(?:bn|billion))?")):
        m = re.search(rx, g)
        if m:
            lo = float(m.group(1)) * 1000
            hi = float(m.group(3)) * 1000 if m.group(3) else lo
            if "up to" in m.group(0):
                lo = None
            other.append({"metric": lab, "low": lo, "high": hi, "unit": "EUR m", "text": m.group(0)[:120]})
    if other:
        out["guidance_other"] = other
    fy = re.search(r"fiscal year (20\d\d)", g)
    if fy:
        out["guidance_fy"] = f"FY{fy.group(1)}"
    return out


def _clean(s):
    return s.split("•")[-1].strip()


def _texty(s):
    return "(in millions" not in s and len(re.findall(r"\d", s)) < 0.12 * max(len(s), 1) and 40 < len(s) < 500


def ai_notes(t, pres=None):
    sents = [_clean(s) for s in sentences(t)]
    hits = [s for s in sents if re.search(r"data cent|hyperscal|artificial intelligence|\bAI\b", s) and _texty(s)]
    if not hits and pres:
        ps = [_clean(s) for s in sentences(norm(open(pres, encoding="utf-8").read()))]
        hits = [("[analyst deck] " + s) for s in ps if re.search(r"data cent|hyperscal|\bAI\b", s) and 20 < len(s) < 300][:1]
    if not hits:
        hits = [s for s in sents if re.search(r"Grid Technologies|grid", s) and re.search(r"demand|record|large order|backlog", s, re.I) and _texty(s)][:1]
    return " ".join(hits[:2])[:420]


def parse_er(fp_doc, path):
    t = norm(open(path, encoding="utf-8").read())
    a = t.find("Key figures (in millions")
    b = t.find("Consolidated Statements of Income", a)
    kf = t[a:b] if a >= 0 else ""
    head = kf[:160]
    ytd = "FY" if "Fiscal year" in head else ("H1" if "First half" in head else ("9M" if re.search(r"Q1\s*[-–]\s*Q3|Nine months", head) else None))
    k = 2 if ytd else 1
    res = {"ytd": ytd, "q": {}, "y": {}}
    def put(key, toks, per):  # toks list -> dict entries for quarter / ytd
        if not toks:
            return
        n = len(toks) // k
        res["q"][key] = toks[:n]
        if ytd:
            res["y"][key] = toks[n:]
    put("orders", row(kf, "Orders", 4 * k), None)
    put("revenue", row(kf, "Revenue", 4 * k), None)
    put("btb", row(kf, "Book-to-bill ratio", 3 * k), None)
    put("backlog", row(kf, "Order backlog (in billions of €)", 3 * k), None)
    lab_p = "Profit before SI" if "Profit before SI" in kf else "Adjusted EBITA before Special items"
    lab_m = "Profit margin before SI" if "Profit margin before SI" in kf else "Adjusted EBITA margin before Special items"
    put("pbsi", row(kf, lab_p, 3 * k), None)
    put("margin", row(kf, lab_m, 3 * k), None)
    put("ni", row(kf, "Net income (loss)", 3 * k), None)
    f = row(kf, "Free cash flow pre tax", 2 * k)
    if f:
        res["q"]["fcf"] = f[:2]
        if ytd:
            res["y"]["fcf"] = f[2:]
    res["margin_def"] = "Profit margin before Special items" if lab_m.startswith("Profit") else "Adjusted EBITA margin before special items (as originally reported)"
    # segment overview tables
    s0 = t.find("Consolidated Statements of Cash Flows")
    s1 = t.find("EBITDA", t.find("Overview of Segment figures", s0) if "Overview of Segment figures" in t else s0 + 2000)
    reg = t[s0:]
    tables, cur = [], {}
    for m in re.finditer(r"(Gas Services|Grid Technologies|Transformation of Industry|Siemens Gamesa Renewable Energy|Siemens Gamesa|Gas and Power|Siemens Energy) ((?:\S+ ){15}\S+)", reg):
        toks = m.group(2).split(" ")
        if num(toks[0]) is None or not toks[2].endswith("%") or not toks[3].endswith("%") and toks[3] != "n/a":
            continue
        name = SEGNAME.get(m.group(1), m.group(1))
        if name in cur:
            tables.append(cur); cur = {}
        cur[name] = toks
        if name == "Siemens Energy":
            tables.append(cur); cur = {}
        if len(tables) >= 2:
            break
    if cur:
        tables.append(cur)
    res["seg_tables"] = tables
    # segment book-to-bill / backlog from the segment narrative bullets ("Book-to-bill ratio was 2.65 and order backlog increased to €73bn")
    res["seg_text"] = {}
    for nm in ["Gas Services", "Grid Technologies", "Transformation of Industry", "Siemens Gamesa Renewable Energy", "Siemens Gamesa"]:
        m = re.search(re.escape(nm) + r" Q[1-4] \(in millions of €\)", t)
        if not m:
            continue
        blk = t[m.end(): m.end() + 2200]
        nxt = re.search(r"(Gas Services|Grid Technologies|Transformation of Industry|Siemens Gamesa)( Renewable Energy)? Q[1-4] \(in millions", blk)
        if nxt:
            blk = blk[:nxt.start()]
        b2b = re.search(r"[Bb]ook.to.bill ratio (?:was|of|amounted to|came in at|stood at|reached)?\s*(\d+\.\d+)", blk)
        bl = re.search(r"order backlog[^.€]{0,80}?€\s?(\d+(?:\.\d+)?)\s?(bn|billion)", blk)
        key = SEGNAME.get(nm, nm)
        if key in res["seg_text"]:
            continue
        res["seg_text"][key] = {"book_to_bill": float(b2b.group(1)) if b2b else None,
                                "backlog": float(bl.group(1)) * 1000 if bl else None}
    res["guid"] = parse_guidance(t)
    pres = path.replace("_earnings_release.txt", "_analyst_presentation.txt")
    res["ai"] = ai_notes(t, pres if os.path.exists(pres) else None)
    m = re.search(r"order backlog[^.]{0,60}?€\s?(\d+(?:\.\d+)?)\s?(bn|billion)", t)
    res["backlog_text"] = float(m.group(1)) * 1000 if m else None
    return res


def seg_dict(tab, margin_label):
    out = {}
    for name, tk in tab.items():
        if name == "Siemens Energy":
            continue
        out[name] = {"orders": num(tk[0]), "orders_yoy_pct": num(tk[2]), "orders_comp_pct": num(tk[3]),
                     "revenue": num(tk[4]), "revenue_yoy_pct": num(tk[6]), "revenue_comp_pct": num(tk[7]),
                     "profit": num(tk[8]), "margin_pct": num(tk[10])}
    return out


def mk_row(fp, d, rel, release_date, kind):
    g = d[kind]
    o, r = g.get("orders"), g.get("revenue")
    ej = {"margin_pct": num(g["margin"][0]) if g.get("margin") else None, "margin_def": d["margin_def"],
          "organic_growth_pct": num(r[3]) if r else None, "orders_organic_growth_pct": num(o[3]) if o else None,
          "organic_def": "comparable basis (excl. currency translation and portfolio effects)",
          "profit_before_special_items": num(g["pbsi"][0]) if g.get("pbsi") else None,
          "net_income": num(g["ni"][0]) if g.get("ni") else None,
          "fcf_pre_tax": num(g["fcf"][0]) if g.get("fcf") else None,
          "backlog_def": "Group order backlog at period end, stated in EUR bn (rounded) in the Key figures table; converted x1000"}
    tabs = d["seg_tables"]
    ti = 0 if kind == "q" else 1
    if len(tabs) > ti:
        ej["segments"] = seg_dict(tabs[ti], d["margin_def"])
        if kind == "q":
            for nm, v in d.get("seg_text", {}).items():
                if nm in ej["segments"]:
                    for kk, vv in v.items():
                        if vv is not None:
                            ej["segments"][nm][kk] = vv
            ej["segment_backlog_def"] = "segment order backlog at quarter end as stated in EUR bn in the ER segment commentary (x1000)"
        ej["segment_margin_def"] = ("Profit margin before Special items" if d["margin_def"].startswith("Profit")
                                    else "Adjusted EBITA margin (incl. special items) as reported in the segment overview")
    bl = num(g["backlog"][0]) * 1000 if g.get("backlog") and num(g["backlog"][0]) is not None else None
    gd = d["guid"]
    if gd.get("guidance_other"):
        ej["guidance_other"] = gd["guidance_other"]
    if gd.get("rev_low") is not None:
        ej["guidance_rev_basis"] = "comparable revenue growth %, Siemens Energy group"
    if gd.get("guidance_text"):  # Q1-Q3 releases guide the current FY; Q4/annual releases guide the next FY
        y = int(fp[2:6])
        ej["guidance_fy"] = f"FY{y}" if fp[6:] in ("Q1", "Q2", "Q3") else f"FY{y + 1}"
    ej = {k: v for k, v in ej.items() if v not in (None, "", [], {})}
    return dict(fiscal_period=fp, period_end=period_end(fp), release_date=release_date, currency="EUR", unit="m",
                revenue=num(r[0]) if r else None, revenue_yoy_pct=num(r[2]) if r else None,
                orders=num(o[0]) if o else None, orders_yoy_pct=num(o[2]) if o else None,
                book_to_bill=num(g["btb"][0]) if g.get("btb") else None, backlog=bl, gross_margin_pct=None,
                guidance_text=gd.get("guidance_text", ""), guidance_rev_low=gd.get("rev_low"),
                guidance_rev_high=gd.get("rev_high"), ai_dc_notes=d["ai"], extra_json=ej, source_doc=rel)


def restated_fy2022():
    p = os.path.join(TXT, "FY2022_comparable_key_figures_restated.txt")
    t = norm(open(p).read())
    out = {}
    names = ["Gas Services", "Grid Technologies", "Transformation of Industry", "Siemens Gamesa Renewable Energy", "Siemens Energy"]
    a = t.find("Orders Revenue")
    b = t.find("Profit before Special Items Profit margin")
    for nm in names:
        m1 = re.search(re.escape(nm) + r" ((?:\S+ ){11}\S+)", t[a:b])
        m2 = re.search(re.escape(nm) + r" ((?:\S+ ){11}\S+)", t[b:])
        if not (m1 and m2):
            continue
        o, p_ = m1.group(1).split(" "), m2.group(1).split(" ")
        if nm == "Siemens Energy":  # group line only used as a cross-check, not a segment
            continue
        for i, per in enumerate(["FY2022Q1", "FY2022Q2", "FY2022Q3", "FY2022Q4", "FY2022"]):
            out.setdefault(per, {})[SEGNAME.get(nm, nm)] = {"orders": num(o[i]), "revenue": num(o[6 + i]),
                                                             "profit": num(p_[i]), "margin_pct": num(p_[6 + i])}
    return out


def main():
    man = irlib.read_csv(f"data/processed/ir/{T}_manifest.csv")
    ers = {r["fiscal_period"]: r for r in man if r["doc_type"] == "press_release"
           and re.search(r"earnings|ER_E|ER-E", r["local_path"], re.I) and "pta_" not in r["local_path"]}
    rel_dates = {"FY2024": "2024-11-12"}  # published 19:44 CET the evening before the ER dateline (pressetext)
    restated = restated_fy2022()
    rows = []
    for fp, r in sorted(ers.items()):
        if fp < "FY2022" or fp.startswith("FY2020") or fp.startswith("FY2021"):
            continue
        txt = os.path.join(TXT, f"{fp}_earnings_release.txt")
        if not os.path.exists(txt):
            print("missing text", fp); continue
        d = parse_er(fp, txt)
        rd = rel_dates.get(fp, r["pub_date"])
        is_q4 = len(fp) == 6
        qfp = fp + "Q4" if is_q4 else fp
        q = mk_row(qfp, d, r["local_path"], rd, "q")
        rows.append(q)
        if d["ytd"]:
            yfp = fp if d["ytd"] == "FY" else fp[:6] + ("H1" if d["ytd"] == "H1" else "_9M")
            y = mk_row(yfp, d, r["local_path"], rd, "y")
            if d["ytd"] != "FY":  # guidance/AI notes belong to the quarterly row; keep once
                y["guidance_text"], y["guidance_rev_low"], y["guidance_rev_high"], y["ai_dc_notes"] = "", None, None, ""
                y["extra_json"].pop("guidance_other", None); y["extra_json"].pop("guidance_rev_basis", None); y["extra_json"].pop("guidance_fy", None)
            rows.append(y)
    for row_ in rows:
        fp = row_["fiscal_period"]
        if fp in restated:
            ej = row_["extra_json"]
            ej["segments_as_reported"] = ej.pop("segments", None)
            ej["segments"] = restated[fp]
            ej["segments_basis"] = ("restated: 'Comparable key figures' (published 2023-02-07) reflecting the org. structure as of "
                                    "Oct 1, 2022; margin = Profit margin before Special items")
            ej = {k: v for k, v in ej.items() if v is not None}
            row_["extra_json"] = ej
            row_["source_doc"] = row_["source_doc"]
    for row_ in rows:
        if row_["fiscal_period"] in ("FY2022H1", "FY2022_9M"):
            row_["extra_json"]["segments_basis"] = "as reported in the FY2022 ERs (segments Gas and Power, Siemens Gamesa Renewable Energy); no restated H1/9M available"
    for row_ in rows:  # Q3 FY2025 release reaffirms the Q2 (raised) outlook by reference, without restating numbers
        if row_["fiscal_period"] == "FY2025Q3":
            row_["extra_json"]["guidance_reaffirmed_ref"] = "FY2025Q2 (raised outlook: comparable revenue growth 13%-15%, margin 4%-6%; tendency to upper end)"
    irlib.write_kpis(T, rows)
    return rows


if __name__ == "__main__":
    rows = main()
    for r in rows:
        ej = r["extra_json"]
        segs = ej.get("segments", {})
        print(r["fiscal_period"], r["release_date"], "rev", r["revenue"], r["revenue_yoy_pct"], "ord", r["orders"], r["orders_yoy_pct"],
              "btb", r["book_to_bill"], "bl", r["backlog"], "m", ej.get("margin_pct"), "| GS", (segs.get("Gas Services") or {}).get("orders"),
              "GT", (segs.get("Grid Technologies") or {}).get("orders"), "| g", r["guidance_rev_low"], r["guidance_rev_high"],
              len(ej.get("guidance_other", [])), "| ai", len(r["ai_dc_notes"]))
