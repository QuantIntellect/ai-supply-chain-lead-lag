"""Parse SAP quarterly statements (text) into the KPI panel."""
import sys, os, re, json, csv
sys.path.insert(0, os.path.dirname(__file__))
import fetch_util as fu

T = "SAP.DE"
TXT = os.path.join(fu.TXT_IR, T)
QEND = {1: "03-31", 2: "06-30", 3: "09-30", 4: "12-31"}
QW = {1: "First", 2: "Second", 3: "Third", 4: "Fourth"}
NUM = r"(?:[–\-−]?[\d,]+(?:\.\d+)?|>100|<[–\-−]100|n\.a\.|N/A|NA|\d+pp)"

def flat(s):
    return re.sub(r"\s+", " ", s)

def num(x):
    if x is None:
        return None
    x = x.replace(",", "").replace("–", "-").replace("−", "-")
    try:
        return float(x)
    except ValueError:
        return None

def glance_segment(t, q, y):
    m = re.search(r"at a glance\s*[–-]\s*(?:%s quarter|Q%d) %d" % (QW[q], q, y), t, re.I)
    if not m:
        m = re.search(r"at a glance", t, re.I)
    if not m:
        return ""
    seg = t[m.start(): m.start() + 3500]
    nxt = seg.find("at a glance", 20)
    return seg[:nxt] if nxt > 0 else seg

def row(seg, label, n=7):
    m = re.search(re.escape(label) + r"\d?\s+((?:%s\s+){1,%d}%s?)" % (NUM, n - 1, NUM), seg)
    if not m:
        return None
    return re.findall(NUM, m.group(1))[:n]

def ccb(t):
    out = {}
    m = re.search(r"Current Cloud Backlog (?:Total\d? )?([\d]{1,2},\d{3}) (–?\d+) (–?\d+)", t)
    if m:
        out["ccb_m"] = num(m.group(1)); out["ccb_yoy"] = num(m.group(2)); out["ccb_yoy_cc"] = num(m.group(3))
    m = re.search(r"Current cloud backlog ([\d]{1,2},\d{3}) ([\d]{1,2},\d{3}) (–?\d+) (–?\d+)", t)
    if m and "ccb_m" not in out:
        out["ccb_m"] = num(m.group(1)); out["ccb_yoy"] = num(m.group(3)); out["ccb_yoy_cc"] = num(m.group(4))
    m = re.search(r"Current cloud backlog S/4HANA current cloud backlog \d+% ([\d]{1,2},\d{3}) [\d,]+ \+\d+pp \+(\d+)% \(\+(\d+)% @cc\)", t)
    if m and "ccb_m" not in out:
        out["ccb_m"] = num(m.group(1)); out["ccb_yoy"] = num(m.group(2)); out["ccb_yoy_cc"] = num(m.group(3))
    pats = [r"[Cc]urrent cloud backlog (?:grew|was up|increased|expanded)(?: by)? (\d+)% to €([\d.]+) billion[^.]{0,60}?up (\d+)% at constant",
            r"[Cc]urrent cloud backlog of €([\d.]+) billion, up (\d+)% and up (\d+)% at constant",
            r"[Cc]urrent cloud backlog[^.]{0,60}?expanded to €([\d.]+) billion, accelerating growth to (\d+)% and (\d+)% at constant"]
    for i, p in enumerate(pats):
        m = re.search(p, t)
        if m:
            if i == 0:
                bn, g, gcc = m.group(2), m.group(1), m.group(3)
            else:
                bn, g, gcc = m.group(1), m.group(2), m.group(3)
            out.setdefault("ccb_bn_text", num(bn)); out.setdefault("ccb_yoy", num(g)); out.setdefault("ccb_yoy_cc", num(gcc))
            break
    return out

def outlook(t):
    m = re.search(r"Financial Outlook(.{0,3000})", t)
    if not m:
        m = re.search(r"(?:SAP (?:now |continues to )?expects?:)(.{0,2500})", t)
    if not m:
        return {}, ""
    s = m.group(1)
    o = {}
    def rng(label_pat):
        for p in [r"€\s?([\d.]+)\s?[–\-]\s?([\d.]+) billion %s" % label_pat,
                  r"%s[^€]{0,80}?€\s?([\d.]+)\s?[–\-]\s?([\d.]+) billion" % label_pat]:
            mm = re.search(p, s)
            if mm:
                return num(mm.group(1)), num(mm.group(2))
        return None
    for key, lp in [("cloud_rev", r"cloud revenue"), ("cs_rev", r"cloud and software revenue"),
                    ("op_nonifrs", r"non-IFRS operating profit"), ("fcf", r"free cash flow")]:
        r = rng(lp)
        if r:
            o["guide_%s_low_bn" % key], o["guide_%s_high_bn" % key] = r
    mm = re.search(r"(?:[Aa]pproximately|[Aa]bove|[Aa]round|more than) €\s?([\d.]+) billion free cash flow", s)
    if mm and "guide_fcf_low_bn" not in o:
        o["guide_fcf_approx_bn"] = num(mm.group(1))
    txt = s[:700]
    return o, txt

def ai_notes(t):
    sents = re.split(r"(?<=[.!?])\s+(?=[A-Z])", t)
    bad = re.compile(r"(forward-looking|litigation|Notes to|acquire|acquisition|chose|Executive Board|trademark|"
                     r"Copyright|risk|Teradata|For more information)", re.I)
    scored = []
    for s in sents:
        if len(s) > 450 or bad.search(s) or not re.search(r"\b(AI|Joule|Business Data Cloud|agentic|AI agents?)\b", s):
            continue
        sc = 0
        if re.search(r"order entry", s): sc += 5
        if re.search(r"\d+%|two thirds|half|third|quarter of", s): sc += 3
        if re.search(r"(CEO|CFO):", s): sc += 2
        if re.search(r"(demand|pipeline|adoption|monetiz|driver|growth)", s): sc += 2
        if re.search(r"Business Data Cloud|Joule", s): sc += 1
        scored.append((sc, s.strip()))
    scored.sort(key=lambda x: -x[0])
    out, seen = [], set()
    for sc, s in scored:
        k = s[:50]
        if k in seen or sc < 2:
            continue
        seen.add(k); out.append(re.sub(r"^.*?(CEO|CFO): ", "", s))
        if len(out) >= 2:
            break
    return " | ".join(out)

def parse(y, q):
    per = "%dQ%d" % (y, q)
    p = os.path.join(TXT, "%s_statement.txt" % per)
    if not os.path.exists(p):
        return None
    t = flat(open(p, encoding="utf-8").read())
    seg = glance_segment(t, q, y)
    rec = {"fiscal_period": per, "period_end": "%d-%s" % (y, QEND[q])}
    ex = {"basis": "IFRS reported unless noted; *_cc = non-IFRS growth at constant currencies"}
    r = row(seg, "Total revenue")
    if r and len(r) >= 7:
        rec["revenue"] = num(r[0]); rec["revenue_yoy_pct"] = num(r[2]); ex["total_rev_yoy_cc"] = num(r[6])
    r = row(seg, "Cloud revenue")
    if r and len(r) >= 7:
        ex["cloud_rev_m"] = num(r[0]); ex["cloud_rev_yoy"] = num(r[2]); ex["cloud_rev_yoy_cc"] = num(r[6])
    r = row(seg, "Cloud and software revenue")
    if r and len(r) >= 7:
        ex["cs_rev_m"] = num(r[0]); ex["cs_rev_yoy"] = num(r[2]); ex["cs_rev_yoy_cc"] = num(r[6])
    r = row(seg, "Thereof Cloud ERP Suite")
    if r and len(r) >= 7:
        ex["cloud_erp_suite_rev_m"] = num(r[0]); ex["cloud_erp_suite_yoy"] = num(r[2]); ex["cloud_erp_suite_yoy_cc"] = num(r[6])
    r = row(seg, "Thereof SAP S/4HANA Cloud revenue")
    if r and len(r) >= 7:
        ex["s4hana_cloud_rev_m"] = num(r[0]); ex["s4hana_cloud_yoy"] = num(r[2]); ex["s4hana_cloud_yoy_cc"] = num(r[6])
    r = row(seg, "Software licenses")
    if r and len(r) >= 3 and r[0] not in ("and",):
        ex["software_licenses_m"] = num(r[0]); ex["software_licenses_yoy"] = num(r[2])
    r = row(seg, "Operating profit (loss)")
    if r and len(r) >= 6:
        ex["op_ifrs_m"] = num(r[0]); ex["op_nonifrs_m"] = num(r[3]); ex["op_nonifrs_yoy"] = num(r[5])
        if len(r) >= 7:
            ex["op_nonifrs_yoy_cc"] = num(r[6])
    r = row(seg, "Share of more predictable revenue (in %)", n=2)
    if r:
        ex["share_predictable_rev_pct"] = num(r[0])
    r = row(seg, "Cloud gross profit")
    if r and len(r) >= 4:
        ex["cloud_gross_profit_ifrs_m"] = num(r[0]); ex["cloud_gross_profit_nonifrs_m"] = num(r[3])
    r = row(seg, "Gross profit")
    gp = None
    if r and len(r) >= 1:
        gp = num(r[0])
    else:
        m = re.search(r"Gross profit (?:\(Gross margin in %\) )?([\d]{1,2},\d{3}) ", t)
        if m:
            gp = num(m.group(1))
    if gp and rec.get("revenue"):
        rec["gross_margin_pct"] = round(100 * gp / rec["revenue"], 1)
        ex["gross_profit_ifrs_m"] = gp
        ex["gross_margin_note"] = "computed: IFRS gross profit / total revenue"
    r = row(seg, "Free cash flow", n=3)
    if r:
        ex["fcf_m"] = num(r[0])
    c = ccb(t)
    if c.get("ccb_m"):
        rec["backlog"] = c["ccb_m"]
    elif c.get("ccb_bn_text"):
        rec["backlog"] = c["ccb_bn_text"] * 1000
        ex["ccb_note"] = "backlog from rounded EUR bn text"
    if c.get("ccb_yoy") is not None:
        ex["ccb_yoy"] = c["ccb_yoy"]
    if c.get("ccb_yoy_cc") is not None:
        ex["ccb_yoy_cc"] = c["ccb_yoy_cc"]
    o, otxt = outlook(t)
    ex.update(o)
    if o.get("guide_cs_rev_low_bn"):
        rec["guidance_rev_low"] = o["guide_cs_rev_low_bn"] * 1000
        rec["guidance_rev_high"] = o["guide_cs_rev_high_bn"] * 1000
        ex["guidance_rev_basis"] = "guidance_rev_* left blank: SAP gives no total revenue range; see guide_cs_rev_* (cloud and software revenue, cc)"
    parts = []
    if o.get("guide_cloud_rev_low_bn"):
        parts.append("cloud rev EUR %.2f-%.2fbn cc" % (o["guide_cloud_rev_low_bn"], o["guide_cloud_rev_high_bn"]))
    if o.get("guide_cs_rev_low_bn"):
        parts.append("cloud+software rev EUR %.2f-%.2fbn cc" % (o["guide_cs_rev_low_bn"], o["guide_cs_rev_high_bn"]))
    if o.get("guide_op_nonifrs_low_bn"):
        parts.append("non-IFRS op profit EUR %.2f-%.2fbn cc" % (o["guide_op_nonifrs_low_bn"], o["guide_op_nonifrs_high_bn"]))
    if o.get("guide_fcf_approx_bn"):
        parts.append("FCF ~EUR %.1fbn" % o["guide_fcf_approx_bn"])
    elif o.get("guide_fcf_low_bn"):
        parts.append("FCF EUR %.1f-%.1fbn" % (o["guide_fcf_low_bn"], o["guide_fcf_high_bn"]))
    if re.search(r"upper end", otxt):
        parts.append("(towards upper end)")
    if re.search(r"lower end", otxt):
        parts.append("(towards lower end)")
    if re.search(r"\b(updat|rais|lower|now expects)", otxt[:400]):
        parts.append("[outlook updated this quarter]")
    rec["guidance_text"] = "FY%s outlook: " % (y + 1 if q == 4 else y) + "; ".join(parts) if parts else ""
    rec["ai_dc_notes"] = ai_notes(t)
    rec["extra_json"] = json.dumps(ex, ensure_ascii=False)
    rec["source_doc"] = os.path.relpath(p.replace(fu.TXT_IR, fu.TXT_IR), fu.ROOT)
    return rec

if __name__ == "__main__":
    out = []
    for y in range(2022, 2027):
        for q in (1, 2, 3, 4):
            r = parse(y, q)
            if r:
                out.append(r)
                ex = json.loads(r["extra_json"])
                print(r["fiscal_period"], r.get("revenue"), r.get("revenue_yoy_pct"), ex.get("total_rev_yoy_cc"),
                      "| cloud", ex.get("cloud_rev_m"), ex.get("cloud_rev_yoy_cc"), "| CCB", r.get("backlog"), ex.get("ccb_yoy"), ex.get("ccb_yoy_cc"),
                      "| GM", r.get("gross_margin_pct"), "| OPn", ex.get("op_nonifrs_m"), "|", r["guidance_text"][:110])
    json.dump(out, open(os.path.join(fu.RAW_IR, T, "kpis_parsed.json"), "w"), indent=1)
