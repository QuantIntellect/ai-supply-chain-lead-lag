"""Extract Besi quarterly KPIs from press-release text (data/processed/ir_text/BESI.AS/<period>_press_release.txt)
-> data/processed/ir/BESI.AS_kpis.csv.  Numbers are taken from the release's summary table / highlights;
book-to-bill is the stated 'Book to Bill Ratio' row where present (2018-2023), otherwise computed orders/revenue
(flagged in extra_json). Besi does not report a numeric backlog; guidance is a % change vs. the reported quarter."""
import os, sys, re, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pandas as pd
import irlib

T = "BESI.AS"
SCR = "/private/tmp/claude-501/-Users-sinamirzaei-Documents-aimapping/57e0a0d0-6441-40ef-828b-57eeb87e7b21/scratchpad"
TD = irlib.text_dir(T)
QEND = {1: "03-31", 2: "06-30", 3: "09-30", 4: "12-31"}
NUM = r"[-+]?\d+(?:[.,]\d+)?%?x?"
KW = re.compile(r"\b(AI|artificial intelligence|data ?cent(?:er|re)s?|HBM|hybrid bonding|2\.5D|3D|photonics|co-packaged|"
                r"TC ?Next|TCB|chiplet|high performance computing|HPC|China|Chinese|advanced logic|memory|GPU|subcontractors?)\b", re.I)


def row_tokens(t, label, stop_labels, n=8):
    """tokens following the first line that equals `label` (summary table), up to the next stop label."""
    m = re.search(r"^\s*" + label + r"\s*\*?\s*$", t, re.M)
    if not m:
        return []
    seg = t[m.end(): m.end() + 600]
    stop = re.search(r"^\s*(" + "|".join(stop_labels) + r")\b", seg, re.M)
    if stop:
        seg = seg[:stop.start()]
    return re.findall(NUM, seg)[:n]


def fnum(s):
    s = s.replace(",", ".").rstrip("%x")
    try:
        return float(s)
    except ValueError:
        return None


def section(t, start_pat, end_pat, maxlen=2500):
    m = re.search(start_pat, t, re.M | re.I)
    if not m:
        return ""
    seg = t[m.end(): m.end() + maxlen]
    e = re.search(end_pat, seg, re.M | re.I)
    return seg[:e.start()] if e else seg


def clean(s):
    return " ".join(s.replace("●", " ").split())


def sentences(s):
    return [x.strip() for x in re.split(r"(?<=[.;])(?<!vs\.)(?<!approx\.)\s+(?=[A-Z])", clean(s)) if x.strip()]


def parse_guidance(guid, r_cur):
    """Parse next-quarter revenue % range (vs reported quarter) and gross-margin range from the Outlook text."""
    ex = {}
    sents = [x for x in re.split(r"(?<=\D)\.\s+|\s(?=(?:Gross margin|Operating expenses|Baseline operating|Opex|Orders are|Orders expected)\b)", guid) if x]
    rs = next((x for x in sents if re.search(r"revenue", x, re.I)), "")
    lo = hi = None
    m = re.search(r"(?:flat|equal (?:to )?[^%]{0,25}?)\s*(?:to\s*)?\(?\s*(?:plus or minus|\+/-|\+/–|±)\s*(\d+)%", rs, re.I)
    if m:
        lo, hi = -float(m.group(1)), float(m.group(1))
    else:
        m = re.search(r"flat to (down|up) (?:approximately )?(\d+)%", rs, re.I)
        if m:
            v = float(m.group(2)); lo, hi = ((-v, 0.0) if m.group(1).lower() == "down" else (0.0, v))
        else:
            m = re.search(r"(increase|decrease|rise|decline|grow|be up|be down|up|down)\w*\s+(?:by\s+)?(?:approximately\s+|~)?"
                          r"(\d+)%?(?:\s*[-–]\s*(\d+))?%(?:\s*\(\s*(?:\+/-|\+/–|±|plus or minus)\s*(\d+)%\s*\))?", rs, re.I)
            if m:
                sign = -1 if re.match(r"decrease|decline|be down|down", m.group(1), re.I) else 1
                a = float(m.group(2)); b = float(m.group(3)) if m.group(3) else a
                if m.group(4) and not m.group(3):
                    a, b = a - float(m.group(4)), a + float(m.group(4))
                lo, hi = sorted([sign * a + 0.0, sign * b + 0.0])
    if lo is not None:
        ex["guide_rev_qoq_pct_low"], ex["guide_rev_qoq_pct_high"] = lo, hi
        if r_cur:
            ex["guide_rev_implied_eur_m"] = [round(r_cur * (1 + lo / 100), 1), round(r_cur * (1 + hi / 100), 1)]
    gs = next((x for x in sents if re.search(r"gross margin", x, re.I)), "")
    m = re.search(r"(\d{2})(?:\.\d)?%?\s*(?:[-–]|and|to)\s*(\d{2})(?:\.\d)?%", gs, re.I)
    if m:
        ex["guide_gm_low"], ex["guide_gm_high"] = float(m.group(1)), float(m.group(2))
    return ex


def main():
    ev = pd.read_csv(os.path.join(SCR, "besi_events_annotated.csv")).fillna("")
    rel = {r.fiscal_period: (r.event_date, r.source_url) for _, r in ev.iterrows() if r.event_type in ("Q1", "Q2", "Q3", "Q4")}
    man = pd.read_csv(os.path.join(irlib.PROC_IR, f"{T}_manifest.csv")).fillna("")
    rows = []
    for fp in sorted(rel):
        p = os.path.join(TD, f"{fp}_press_release.txt")
        if not os.path.exists(p):
            continue
        t = open(p).read()
        y, q = int(fp[:4]), int(fp[-1])
        rev = row_tokens(t, "Revenue", ["Orders", "Operating", "Gross"])
        orders = row_tokens(t, "Orders", ["Gross", "Operating", "EBITDA", "Net"])
        gm_row = row_tokens(t, "Gross Margin", ["Operating", "EBITDA", "Net"])
        btb = row_tokens(t, "Book to Bill Ratio", ["[A-Z][a-z]"], n=5)
        r_cur = fnum(rev[0]) if rev else None
        o_cur = fnum(orders[0]) if orders else None
        flat = clean(t[:6000])
        if r_cur is None:  # web-page fallback (highlights only)
            m = re.search(r"Revenue of € ([\d.]+) million", flat); r_cur = float(m.group(1)) if m else None
            m = re.search(r"Orders of € ([\d.]+) million", flat); o_cur = float(m.group(1)) if m else None
        extra = {"orders_definition": "orders (new bookings) as reported by Besi; no numeric backlog disclosed",
                 "guidance_basis": "next-quarter revenue % change vs reported quarter; gross-margin range"}
        r_yoy = o_yoy = None
        if len(rev) >= 5:
            extra["revenue_qoq_pct"] = fnum(rev[2]); r_yoy = fnum(rev[4]); extra["revenue_prior_year_q"] = fnum(rev[3])
        if len(orders) >= 5:
            extra["orders_qoq_pct"] = fnum(orders[2]); o_yoy = fnum(orders[4]); extra["orders_prior_year_q"] = fnum(orders[3])
        pq = f"Q{q}-{str(y - 1)[2:]}"
        if r_yoy is None and r_cur is not None:
            m = re.search(r"Revenue of € [\d.]+ million[^●]{0,200}?(Up|Down|up|down) ([\d.]+)% vs\.? " + pq, flat)
            if m:
                r_yoy = float(m.group(2)) * (-1 if m.group(1).lower() == "down" else 1)
        if o_yoy is None and o_cur is not None:
            m = re.search(r"Orders of € [\d.]+ million, (up|down) [\d.]+% and ([\d.]+)% vs\. Q[1-4]-\d\d and " + pq, flat)
            if m:
                o_yoy = float(m.group(2)) * (-1 if m.group(1) == "down" else 1)
        # gross margin: summary-table row (2024+) else first "gross margin ... xx.x%" in highlights
        hl = section(t, r"^Key Highlights", r"^(Outlook|Q[1-4]-\d\d Outlook|\(€ millions)")
        gm = fnum(gm_row[0]) if gm_row and gm_row[0].endswith("%") else None
        if gm is None:
            m = re.search(r"gross margin[^%]{0,60}?(\d{2}\.\d)%", clean(hl) or clean(t[:6000]), re.I)
            gm = float(m.group(1)) if m else None
        # book to bill
        b2b = None
        if btb and btb[0].endswith("x"):
            b2b = fnum(btb[0]); extra["book_to_bill_source"] = "stated"
        elif r_cur and o_cur:
            b2b = round(o_cur / r_cur, 2); extra["book_to_bill_source"] = "computed orders/revenue"
        # outlook
        out = section(t, r"^\s*(?:Q[1-4]-\d\d )?Outlook(?: Q[1-4]-\d\d)?\s*$", r"^\s*(\(€ millions|Key Highlights|Revenue\s*$)", 900)
        guid = clean(out)
        extra.update(parse_guidance(guid, r_cur))
        # China share of orders (validated against total orders)
        mo = re.search(r"^ORDERS\s*$", t, re.M)  # case-sensitive: supplemental table, not the summary 'Orders' row
        osec = t[mo.end(): mo.end() + 2500] if mo else ""
        me = re.search(r"^(REVENUE|Headcount|HEADCOUNT|Supplemental|BALANCE)", osec, re.M)
        osec = osec[:me.start()] if me else osec
        cm = re.search(r"China\s*\n((?:\s*[\d.]+%?\s*\n){2,16})", osec)
        tm = re.search(r"Total\s*\n((?:\s*[\d.]+%?\s*\n){2,16})", osec)
        if cm and tm and o_cur:
            cv = [fnum(x) for x in cm.group(1).split() if not x.endswith("%")]
            cp = [fnum(x) for x in cm.group(1).split() if x.endswith("%")]
            tv = [fnum(x) for x in tm.group(1).split() if not x.endswith("%")]
            idx = [i for i, v in enumerate(tv) if v is not None and abs(v - o_cur) < 0.15]
            if idx and idx[0] < len(cv) and idx[0] < len(cp):
                extra["orders_china_eur_m"], extra["orders_china_pct"] = cv[idx[0]], cp[idx[0]]
        # AI / data-centre / hybrid bonding / China commentary: keyword sentences from highlights + CEO comment
        ceo = section(t, r"(Richard W\. Blickman|Blickman), (?:President|Chief Executive)", r"^(Second|Third|First|Fourth|Full|Outlook|Q[1-4]-\d\d Outlook|Results of Operations|Financial)", 4000)
        sents = [s for s in sentences(hl) + sentences(ceo) if KW.search(s)]
        notes, seen = [], set()
        for s in sents:
            s2 = re.sub(r"\s+", " ", s)[:300]
            if s2[:60] in seen:
                continue
            seen.add(s2[:60]); notes.append(s2)
            if sum(len(x) for x in notes) > 700:
                break
        ni = row_tokens(t, r"Net Income", ["EPS", "Net Margin", "Orders"])
        if ni:
            extra["net_income_eur_m"] = fnum(ni[0])
        src = man[(man.fiscal_period == fp) & (man.doc_type == "press_release") & man.local_path.str.contains("press_release")]
        rows.append(dict(ticker=T, fiscal_period=fp, period_end=f"{y}-{QEND[q]}", release_date=rel[fp][0], currency="EUR",
                         unit="million", revenue=r_cur, revenue_yoy_pct=r_yoy, orders=o_cur, orders_yoy_pct=o_yoy,
                         book_to_bill=b2b, backlog=None, gross_margin_pct=gm, guidance_text=guid[:600],
                         guidance_rev_low=None, guidance_rev_high=None, ai_dc_notes=" | ".join(notes)[:900],
                         extra_json=extra, source_doc=(src.local_path.iloc[0] if len(src) else p)))
    df = irlib.write_kpis(T, rows)
    print(df[["fiscal_period", "revenue", "revenue_yoy_pct", "orders", "orders_yoy_pct", "book_to_bill", "gross_margin_pct"]].to_string())


if __name__ == "__main__":
    main()
