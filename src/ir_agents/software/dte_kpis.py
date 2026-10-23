"""DT: build DTE.DE_kpis.csv from extracted press releases / backups / transcripts (regex, no invention)."""
import sys, os, re, json, csv
sys.path.insert(0, os.path.dirname(__file__))
import fetch_util as fu

T = "DTE.DE"
TXT = os.path.join(fu.TXT_IR, T)
OUT = os.path.join(fu.PROC_IR, T + "_kpis.csv")
REL = {"2022Q1": "2022-05-13", "2022Q2": "2022-08-11", "2022Q3": "2022-11-10", "2022Q4": "2023-02-23",
       "2023Q1": "2023-05-11", "2023Q2": "2023-08-10", "2023Q3": "2023-11-09", "2023Q4": "2024-02-23",
       "2024Q1": "2024-05-16", "2024Q2": "2024-08-08", "2024Q3": "2024-11-14", "2024Q4": "2025-02-26",
       "2025Q1": "2025-05-15", "2025Q2": "2025-08-07", "2025Q3": "2025-11-13", "2025Q4": "2026-02-26",
       "2026Q1": "2026-05-13", "2026Q2": "2026-08-06", "2026Q3": ""}
QEND = {"1": "03-31", "2": "06-30", "3": "09-30", "4": "12-31"}
COLS = ["ticker", "fiscal_period", "period_end", "release_date", "currency", "unit", "revenue", "revenue_yoy_pct",
        "orders", "orders_yoy_pct", "book_to_bill", "backlog", "gross_margin_pct", "guidance_text", "guidance_rev_low",
        "guidance_rev_high", "ai_dc_notes", "extra_json", "source_doc"]

def num(s):
    s = s.strip().replace("−", "-").replace("–", "-")
    neg = s.startswith("(") and s.endswith(")")
    s = s.strip("()").strip()
    if re.fullmatch(r"-?\d{1,3}( \d{3})+(,\d+)?", s): s = s.replace(" ", "").replace(",", ".")
    elif re.fullmatch(r"-?\d{1,3}(,\d{3})+(\.\d+)?", s): s = s.replace(",", "")
    elif re.fullmatch(r"-?\d{1,3}(\.\d{3})+(,\d+)?", s): s = s.replace(".", "").replace(",", ".")
    elif re.fullmatch(r"-?\d+,\d+", s): s = s.replace(",", ".")
    elif re.fullmatch(r"-?\d{1,3}(,\d{3})+(\.\d+)?", s): s = s.replace(",", "")
    elif not re.fullmatch(r"-?\d+(\.\d+)?", s): return None
    v = float(s)
    return -v if neg else v

def tokens(txt):
    tk = [x.strip() for x in txt.split("\n") if x.strip()]
    out, i = [], 0
    while i < len(tk):
        if tk[i] in ("Adjusted", "Adjusted EBITDA", "Free cash flow", "Adjusted net", "Net") and i + 1 < len(tk) and not re.search(r"\d", tk[i + 1]):
            out.append(tk[i] + " " + tk[i + 1]); i += 2; continue
        out.append(tk[i]); i += 1
    return out

def read(per, dt):
    p = os.path.join(TXT, "%s_%s.txt" % (per, dt))
    return (open(p).read(), p) if os.path.exists(p) else (None, None)

def glance(txt, labels):
    """Return (cur, prev, chg) for the first row whose label matches one of labels."""
    tk = tokens(txt)
    st = next((i for i, t in enumerate(tk) if re.search(r"(at a glance|auf einen Blick)", t, re.I) and i > 20), 0)
    for i, t in enumerate(tk):
        if i < st: continue
        if t in labels:
            vals = []
            for x in tk[i + 1:i + 12]:
                v = num(x.replace("p", "")) if re.fullmatch(r"\(?-?[\d.,]+\)?p?", x) else None
                if v is not None: vals.append(v)
                elif vals: break
                if len(vals) == 3: break
            if len(vals) >= 2:
                return vals + [None] * (3 - len(vals))
    return [None, None, None]

def tsys_from_backup(txt, per):
    tk = tokens(txt)
    try:
        oe = tk.index("ORDER ENTRY")
    except ValueError:
        return {}
    s = max(i for i in range(oe) if tk[i].startswith("FINANCIALS (ADJUSTED")) - 2
    sec = tk[s:oe + 40]
    try:
        h0 = next(i for i, x in enumerate(sec) if x.startswith("FINANCIALS (ADJUSTED"))
        h1 = next(i for i, x in enumerate(sec) if x == "TOTAL REVENUE" and i > h0)
    except StopIteration:
        return {}
    labels, hdr, i = [], sec[h0 + 1:h1], 0
    while i < len(hdr):
        x = hdr[i]
        if re.fullmatch(r"(Q[1-4]|FY|H1|9M|Q1 - Q[234]|Q1-Q[234])", x) and i + 1 < len(hdr) and re.fullmatch(r"\d{4}", hdr[i + 1]):
            labels.append("%s %s" % (x, hdr[i + 1])); i += 2; continue
        if x == "Change": labels.append("Change")
        i += 1
    cur = "Q%s %s" % (per[-1], per[:4])
    if cur not in labels: return {}
    k = labels.index(cur)
    def row(name, start):
        for j in range(start, len(sec)):
            if sec[j] == name:
                vals = []
                for x in sec[j + 1:j + 1 + len(labels) + 3]:
                    v = num(x)
                    if v is None and x not in ("%",): break
                    if v is not None: vals.append(v)
                if len(vals) >= len(labels): return vals
                return None
        return None
    out = {}
    for nm, key in [("TOTAL REVENUE", "tsystems_total_revenue_eur_m"), ("EBITDA AL", "tsystems_adj_ebitda_al_eur_m"), ("ORDER ENTRY", "tsystems_order_entry_eur_m")]:
        v = row(nm, h1)
        if v:
            out[key] = v[k]
            if k + 1 < len(labels) and labels[k + 1] == "Change": out[key.replace("_eur_m", "_yoy_pct")] = v[k + 1]
    return out

AIKW = re.compile(r"\b(AI|artificial intelligence|AI [Ff]actor(y|ies)|Industrial AI Cloud|NVIDIA|Nvidia|data cent(er|re)s?|GPU|sovereign cloud|inference)\b")

def ai_snips(txt, maxn=3, maxlen=420):
    if not txt: return []
    body = re.sub(r"\s+", " ", txt)
    sents = re.split(r"(?<=[.!?])\s+(?=[A-Z“\"])", body)
    out = []
    for s in sents:
        if AIKW.search(s) and 40 < len(s) < 600 and not re.search(r"(forward-looking|cookie|Privacy|Disclaimer)", s):
            out.append(s.strip())
        if len(out) >= maxn: break
    return out

def guidance(txt):
    if not txt: return "", {}
    body = re.sub(r"\s+", " ", txt[:20000])
    sents = re.split(r"(?<=[.!?])\s+(?=[A-Z“\"])", body)
    g = [s for s in sents if re.search(r"(guidance|expect|forecast|outlook)", s, re.I) and re.search(r"billion euros", s)]
    ex = {}
    for s in g:
        m = re.search(r"EBITDA AL[^.]{0,120}?(more than|around|approximately|at least|over|of)?\s*(\d{2}\.\d)\s*billion euros", s)
        if m and "guidance_adj_ebitda_al_eur_bn" not in ex:
            ex["guidance_adj_ebitda_al_eur_bn"] = float(m.group(2)); ex["guidance_adj_ebitda_al_qualifier"] = (m.group(1) or "").strip()
        m = re.search(r"free cash flow AL[^.]{0,120}?(more than|around|approximately|at least|over|of)?\s*(\d{1,2}\.\d)\s*billion euros", s, re.I)
        if m and "guidance_fcf_al_eur_bn" not in ex:
            ex["guidance_fcf_al_eur_bn"] = float(m.group(2)); ex["guidance_fcf_al_qualifier"] = (m.group(1) or "").strip()
    gs = []
    for x in g:
        if not re.search(r"(EBITDA AL|free cash flow)", x, re.I): continue
        m = re.search(r"(guidance|expect|forecast|outlook)", x, re.I)
        st = max(0, m.start() - 80) if m else 0
        st = x.rfind(" ", 0, st) + 1 if st else 0
        gs.append(x[st:st + 300].strip())
    gt = " ... ".join(gs[:2])[:450]
    return gt, ex

def organic(txt):
    if not txt: return None
    body = re.sub(r"\s+", " ", txt[:6000])
    for pat in [r"[Nn]et revenue (?:up|down|increased|grew|rose) (?:by )?(-?\d+\.\d) percent (?:on an organic basis|in organic terms|organically)",
                r"[Ii]n organic terms,? (?:the Group'?s? )?(?:net )?revenue[^.]{0,80}?(-?\d+\.\d) percent",
                r"organic[^.]{0,60}?net revenue (?:was )?(?:up|increased|grew|rose|declined|down)[^.]{0,20}?(-?\d+\.\d) percent",
                r"[Nn]et revenue[^.]{0,120}?(-?\d+\.\d) percent in organic terms",
                r"[Nn]et revenue[^.]{0,60}?organic(?:ally)?[^.]{0,40}?(-?\d+\.\d) percent"]:
        m = re.search(pat, body)
        if m: return float(m.group(1))
    return None

def main():
    rows = []
    for per in sorted(REL, reverse=True):
        pr, prp = read(per, "press_release")
        prh, prhp = read(per, "press_release_html")
        src_txt, src_path = (pr, prp) if pr else (prh, prhp)
        bk, bkp = read(per, "backup")
        tr, trp = read(per, "transcript")
        r = {c: "" for c in COLS}
        r.update({"ticker": T, "fiscal_period": per, "period_end": "%s-%s" % (per[:4], QEND[per[-1]]),
                  "release_date": REL[per], "currency": "EUR", "unit": "EUR m"})
        ex = {"basis": "IFRS reported; EBITDA AL/FCF AL are DT adjusted (after leases) measures",
              "orders_scope": "orders = T-Systems (Systems Solutions segment) order entry, EUR m, from backup"}
        if src_txt:
            nr = glance(src_txt, {"Net revenue"})
            if nr[0] is not None:
                r["revenue"] = nr[0]; r["revenue_yoy_pct"] = nr[2] if nr[2] is not None else ""
            for lab, key in [({"Service revenue", "Service revenues"}, "service_revenue"), ({"Adjusted EBITDA AL"}, "adj_ebitda_al"),
                             ({"Free cash flow AL"}, "fcf_al"), ({"Adjusted net profit"}, "adj_net_profit")]:
                v = glance(src_txt, lab)
                if v[0] is not None:
                    ex[key + "_eur_m"] = v[0]
                    if v[2] is not None: ex[key + "_yoy_pct"] = v[2]
            og = organic(src_txt)
            if og is not None: ex["net_revenue_organic_yoy_pct"] = og
            gt, gx = guidance(src_txt)
            if gx.get("guidance_fcf_al_eur_bn") is not None and gx["guidance_fcf_al_eur_bn"] < 8:
                gx.pop("guidance_fcf_al_eur_bn"); gx.pop("guidance_fcf_al_qualifier", None)  # quarterly figure, not FY guidance
            if gx.get("guidance_adj_ebitda_al_eur_bn") is not None and gx["guidance_adj_ebitda_al_eur_bn"] < 30:
                gx.pop("guidance_adj_ebitda_al_eur_bn"); gx.pop("guidance_adj_ebitda_al_qualifier", None)
            if gx: gx["guidance_note"] = "FY group guidance parsed from release text (EUR bn); check qualifier/organic basis in source"
            r["guidance_text"] = gt; ex.update(gx)
        if bk:
            ts = tsys_from_backup(bk, per)
            if ts.get("tsystems_total_revenue_eur_m") is not None and ts["tsystems_total_revenue_eur_m"] < 300:
                ts = {k: v for k, v in ts.items() if k.startswith("tsystems_order_entry")}  # layout changed (2026 resegmentation); keep order entry only
            ex.update(ts)
            if "tsystems_order_entry_eur_m" in ts:
                r["orders"] = ts["tsystems_order_entry_eur_m"]; r["orders_yoy_pct"] = ts.get("tsystems_order_entry_yoy_pct", "")
        if not src_txt:
            ex = {"status": "not yet reported; Q3 2026 results scheduled for 2026-11-05 (telekom.com financial calendar)"}
        sn = ai_snips(src_txt, 2) + ai_snips(tr, 2)
        r["ai_dc_notes"] = " | ".join(sn)[:700]
        r["extra_json"] = json.dumps(ex, ensure_ascii=False)
        r["source_doc"] = ";".join(os.path.relpath(p, fu.ROOT) for p in [src_path, bkp, trp] if p)
        rows.append(r)
        print(per, r["revenue"], r["revenue_yoy_pct"], r["orders"], ex.get("adj_ebitda_al_eur_m"), ex.get("net_revenue_organic_yoy_pct"), ex.get("guidance_adj_ebitda_al_eur_bn"), ex.get("tsystems_total_revenue_eur_m"))
    with open(OUT, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLS); w.writeheader(); w.writerows(rows)

if __name__ == "__main__":
    main()
