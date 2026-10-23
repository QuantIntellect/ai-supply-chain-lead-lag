"""Parse ASM quarterly press releases (text) into KPI rows -> data/processed/ir/ASM.AS_kpis.csv
Sources: 'Financial highlights' table (orders, revenue, gross margin), 'Bookings' table (backlog, book-to-bill),
'Outlook' section (guidance). Anything not found is left blank. Optional manual overrides in asm_kpi_overrides.json."""
import sys, os, re, json, glob
import pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from irlib import write_kpis, PROC_IR, TEXT_IR

T = "ASM.AS"
ROOT = "/Users/sinamirzaei/Documents/aimapping"
TD = os.path.join(TEXT_IR, T)
QEND = {1: "03-31", 2: "06-30", 3: "09-30", 4: "12-31"}
NUM = r"\(?-?[\d][\d,]*\.?\d*\)?\s*%?"
HERE = os.path.dirname(os.path.abspath(__file__))


def norm(t):
    t = t.replace("–", "-").replace("—", "-").replace("‑", "-").replace(" ", " ")
    t = t.replace("’", "'")
    return " ".join(t.split())


def to_f(tok):
    tok = tok.strip().replace("%", "").strip()
    neg = tok.startswith("(") and tok.endswith(")")
    tok = tok.strip("()").replace(",", "")
    try:
        v = float(tok)
    except ValueError:
        return None
    return -v if neg else v


def row_vals(block, label_re, n=3):
    m = re.search(label_re + r"\s+((?:" + NUM + r"\s+){%d}" % (n - 1) + NUM + ")", block)
    if not m:
        return None
    toks = re.findall(NUM, m.group(1))
    return [to_f(x) for x in toks[:n]]


def period_cols(s):
    return [f"{y}Q{q}" for q, y in re.findall(r"Q([1-4]) (\d{4})", s)]


def parse(per, t):
    out, extra = {}, {}
    y, q = int(per[:4]), int(per[-1])
    # ---------------- highlights table
    m = re.search(r"financial highlights", t, re.I)
    if m:
        blk = t[m.end(): m.end() + 2500]
        cols = period_cols(blk[:120])[:3]
        idx = cols.index(per) if per in cols else None
        prev = f"{y-1}Q{q}"
        pidx = cols.index(prev) if prev in cols else None
        if idx is not None:
            o = row_vals(blk, r"New orders")
            r_ = row_vals(blk, r"(?:Net sales|Revenue)")
            g = row_vals(blk, r"(?<!djusted )(?<!ormalized )Gross (?:profit )?margin\s?%?")
            gn = row_vals(blk, r"Normalized gross profit margin(?: \d\)?)?")
            ga = row_vals(blk, r"Adjusted gross (?:profit )?margin(?: \d)?")
            if o:
                out["orders"] = o[idx]
                if pidx is not None and o[pidx]:
                    out["orders_yoy_pct"] = round((o[idx] / o[pidx] - 1) * 100, 1)
            if r_:
                out["revenue"] = r_[idx]
                if pidx is not None and r_[pidx]:
                    out["revenue_yoy_pct"] = round((r_[idx] / r_[pidx] - 1) * 100, 1)
            if g:
                out["gross_margin_pct"] = g[idx]
            if ga and ga[idx] is not None:
                extra["adj_gross_margin_pct"] = ga[idx]
            if gn and gn[idx] is not None:
                extra["normalized_gross_margin_pct"] = gn[idx]
        else:
            extra["parse_warning"] = f"highlights header {cols}"
    # ---------------- bookings table (backlog, book-to-bill)
    m = re.search(r"Backlog at the beginning of the (?:period|quarter)", t)
    if m:
        hdr = t[max(0, m.start() - 260): m.start()]
        k = hdr.rfind("million")
        cols = period_cols(hdr[k:] if k >= 0 else hdr)[:3]
        idx = cols.index(per) if per in cols else None
        blk = t[m.start(): m.start() + 1400]
        if idx is not None:
            b = row_vals(blk, r"Backlog at the end of the (?:period|quarter)", n=3)
            if b:
                out["backlog"] = b[idx]
            bb = row_vals(blk, r"Book-to-bill ratio \(new orders divided by (?:net sales|revenue)\)", n=3)
            if bb:
                out["book_to_bill"] = bb[idx]
        else:
            extra["parse_warning_bookings"] = f"bookings header {cols}"
    if m is None or "backlog" not in out:  # 2016-2017 style: Backlog / Book-to-bill rows inside highlights table
        mh = re.search(r"financial highlights", t, re.I)
        if mh:
            blk = t[mh.end(): mh.end() + 2500]
            cols = period_cols(blk[:200])[:3]
            if per in cols:
                idx = cols.index(per)
                b = row_vals(blk, r"\bBacklog")
                bb = row_vals(blk, r"\bBook-to-bill")
                if b and "backlog" not in out:
                    out["backlog"] = b[idx]
                if bb and "book_to_bill" not in out:
                    out["book_to_bill"] = bb[idx]
    # ---------------- outlook
    ms = [x for x in re.finditer(r"\b(OUTLOOK|Outlook)\b", t)]
    otxt = ""
    for x in reversed(ms):
        cand = t[x.start(): x.start() + 1800]
        if re.search(r"(expect|project|anticipate|guid)", cand[:900], re.I):
            otxt = cand
            break
    if otxt:
        cut = re.search(r"About ASM|\d of \d About|Investor and analyst|Conference call|Webcast", otxt)
        if cut:
            otxt = otxt[: cut.start()]
        ss = re.split(r"(?<=[.])\s+(?=[A-Z])", otxt)
        gs = [x for x in ss if re.search(r"expect|project|anticipate|guid", x, re.I) and re.search(r"\d", x)]
        out["guidance_text"] = (" ".join(gs) if gs else otxt[:400]).strip()[:700]
        rev_rng, ord_rng, fy = None, None, []
        RNG = (r"(?:between\s)?(?:€|EUR)\s?([\d,.]+)\s?(?:million|billion)?\s?(?:-|to|and)\s?(?:€|EUR)?\s?([\d,.]+)\s?(million|billion)")
        for mm in re.finditer(RNG, otxt):
            pre = otxt[max(0, mm.start() - 110): mm.start()].lower()
            lo, hi, unit = to_f(mm.group(1)), to_f(mm.group(2)), mm.group(3)
            if lo is None or hi is None or lo > hi:
                continue
            if unit == "billion":
                fy.append(f"{mm.group(0)} | ctx: {pre[-80:]}")
                continue
            last_ord = max(pre.rfind("order"), pre.rfind("booking"))
            last_rev = max(pre.rfind("sales"), pre.rfind("revenue"))
            if last_ord > last_rev and ord_rng is None:
                ord_rng = (lo, hi)
            elif last_rev >= 0 and rev_rng is None:
                rev_rng = (lo, hi)
        if rev_rng is None:  # "€830 million, with a range of +/-4%" / "€1,100 million, plus or minus 5%"
            mm = re.search(r"(?:revenue|sales)[^.]{0,80}?€\s?([\d,.]+)\s?million,?\s*(?:with a range of\s*)?(?:\+/-|plus or minus)\s?(\d+)\s?%", otxt)
            if mm:
                mid, pct = to_f(mm.group(1)), float(mm.group(2))
                rev_rng = (round(mid * (1 - pct / 100), 1), round(mid * (1 + pct / 100), 1))
                extra["guidance_rev_mid"] = mid
                extra["guidance_band_pct"] = pct
                extra["guidance_note"] = "low/high derived from stated midpoint +/- stated %"
        if rev_rng is None:  # 2025 style growth-rate guidance at constant currencies
            mm = re.search(r"range of ([+-]?\d+)% to ([+-]?\d+)%", otxt)
            if mm:
                extra["guidance_growth_pct_low"] = min(float(mm.group(1)), float(mm.group(2)))
                extra["guidance_growth_pct_high"] = max(float(mm.group(1)), float(mm.group(2)))
                extra["guidance_note"] = "growth-rate guidance (constant currency) - see guidance_text; EUR range not stated"
        if rev_rng:
            out["guidance_rev_low"], out["guidance_rev_high"] = rev_rng
        if ord_rng:
            extra["guidance_orders_low"], extra["guidance_orders_high"] = ord_rng
        if fy:
            extra["guidance_billion_ranges"] = fy[:3]
    # ---------------- AI / GAA / HBM / China notes (short key sentences)
    sents = re.split(r"(?<=[.!?])\s+(?=[A-Z•“])", t)
    keys = [(r"\bAI\b|artificial intelligence", "AI"), (r"\bGAA\b|gate-all-around", "GAA"), (r"\bHBM\b|high-bandw", "HBM"),
            (r"China|Chinese", "China"), (r"hybrid bonding|advanced packaging", "AdvPkg"), (r"DRAM|memory", "Memory")]
    notes, seen = [], set()
    for pat, tag in keys:
        for s in sents:
            if re.search(pat, s) and len(s) < 450 and not re.search(r"forward-looking|Safe Harbor|cautionary", s, re.I):
                s2 = s.strip()
                if s2 in seen:
                    continue
                seen.add(s2)
                notes.append(f"[{tag}] {s2[:260]}")
                break
    out["ai_dc_notes"] = " | ".join(notes)
    out["_extra"] = extra
    return out


def main():
    ev = pd.read_csv(os.path.join(PROC_IR, f"{T}_events.csv"), dtype=str)
    rel = {r.fiscal_period: r.event_date for r in ev.itertuples() if r.event_type in ("Q1", "Q2", "Q3", "Q4")}
    man = {}
    mp = os.path.join(PROC_IR, f"{T}_manifest.csv")
    if os.path.exists(mp):
        mdf = pd.read_csv(mp, dtype=str)
        man = {r.fiscal_period: r.url for r in mdf.itertuples() if r.doc_type == "press_release"}
    ov_path = os.path.join(HERE, "asm_kpi_overrides.json")
    overrides = json.load(open(ov_path)) if os.path.exists(ov_path) else {}
    rows = []
    files = sorted(glob.glob(os.path.join(TD, "*_press_release.txt")))
    # reported GM by period as shown in ANY release's highlights comparison columns (later releases win)
    gm_cols = {}
    for f in files:
        rel_per = os.path.basename(f).split("_")[0]
        t = norm(open(f).read())
        m = re.search(r"financial highlights", t, re.I)
        if not m:
            continue
        blk = t[m.end(): m.end() + 2500]
        cols = period_cols(blk[:120])[:3]
        g = row_vals(blk, r"(?<!djusted )(?<!ormalized )Gross (?:profit )?margin\s?%?")
        if g and len(cols) == 3:
            for c, v in zip(cols, g):
                if v is not None and c != rel_per:
                    gm_cols[c] = (v, rel_per)
    for f in files:
        per = os.path.basename(f).split("_")[0]
        if per < "2015Q1":
            continue
        t = norm(open(f).read())
        o = parse(per, t)
        extra = o.pop("_extra")
        extra["orders_definition"] = "new orders (bookings) incl. FX as reported in highlights table; book-to-bill = new orders / revenue"
        extra["gm_definition"] = "reported (IFRS; US GAAP before 2016) gross profit margin %"
        if o.get("gross_margin_pct") is None and per in gm_cols:
            o["gross_margin_pct"] = gm_cols[per][0]
            extra["gm_source"] = f"reported GM taken from comparison column of {gm_cols[per][1]} release (own release shows normalized GM only)"
        elif o.get("gross_margin_pct") is None and extra.get("normalized_gross_margin_pct") is not None:
            o["gross_margin_pct"] = extra["normalized_gross_margin_pct"]
            extra["gm_source"] = "normalized GM (excl. LPE purchase-price-allocation effects); reported GM not shown"
        if o.get("book_to_bill") is None and o.get("orders") and o.get("revenue"):
            o["book_to_bill"] = round(o["orders"] / o["revenue"], 2)
            extra["book_to_bill_source"] = "computed = orders / revenue (not stated in release)"
        if per >= "2026Q1":
            extra["disclosure_change"] = "ASM discontinued quarterly bookings/backlog disclosure as of Q1 2026 (backlog reported at year-end only)"
        ov = overrides.get(per, {})
        for k, v in ov.items():
            if k == "extra":
                extra.update(v)
            else:
                o[k] = v
        y, q = int(per[:4]), int(per[-1])
        row = {"ticker": T, "fiscal_period": per, "period_end": f"{y}-{QEND[q]}", "release_date": rel.get(per, ""),
               "currency": "EUR", "unit": "million", **o, "extra_json": extra,
               "source_doc": os.path.relpath(f, ROOT) + (" ; " + man[per] if per in man else "")}
        rows.append(row)
    df = write_kpis(T, rows)
    show = df[["fiscal_period", "release_date", "revenue", "revenue_yoy_pct", "orders", "orders_yoy_pct", "book_to_bill",
               "backlog", "gross_margin_pct", "guidance_rev_low", "guidance_rev_high"]]
    print(show.to_string(index=False))


if __name__ == "__main__":
    main()
