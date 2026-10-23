"""Parse DSY press-release text (pymupdf extraction) for headline non-IFRS KPIs."""
import re, os

NUM = re.compile(r"^\(?[-+]?[\d,]+(\.\d+)?\)?\s*(%|pt|pts)?\)?$")

def lines(txt):
    return [l.strip() for l in txt.splitlines() if l.strip()]

def _vals(L, i, maxn=8):
    out = []
    j = i + 1
    while j < len(L) and len(out) < maxn:
        tok = L[j].replace("€", "").strip()
        if NUM.match(tok):
            out.append(tok)
        elif tok in ("", "-"):
            pass
        else:
            break
        j += 1
    return out

def tofloat(tok):
    if tok is None:
        return None
    t = tok.replace(",", "").replace("%", "").replace("pts", "").replace("pt", "").strip()
    neg = t.startswith("(") and t.endswith(")") or t.startswith("(")
    t = t.strip("()").strip()
    try:
        v = float(t)
    except ValueError:
        return None
    return -v if neg else v

def summary_table(txt):
    """Return dict with non-IFRS quarterly values from the 'Financial Summary' table."""
    L = lines(txt)
    try:
        s = next(i for i, l in enumerate(L) if l.startswith("Financial Summary"))
    except StopIteration:
        return {}
    sec = L[s:s + 160]
    occ = [i for i, l in enumerate(sec) if l.startswith("Total Revenue")]
    if not occ:
        return {}
    res = {}
    v0 = _vals(sec, occ[0])
    hdr0 = sec[:occ[0]]
    side = any(h.startswith("Non-IFRS") for h in hdr0) and any(h == "IFRS" for h in hdr0) and len(v0) >= 6
    if side:
        res["layout"] = "side"; anchor = occ[0]
    else:
        # separate tables: non-IFRS table is the first Total Revenue row preceded by a 'Non-IFRS' header
        anchor = None
        for i in occ:
            if any(h.startswith("Non-IFRS") for h in sec[max(0, i - 25):i]):
                anchor = i; break
        if anchor is None:
            return {}
        res["layout"] = "sep"
    for label, key in (("Total Revenue", "rev"), ("Software Revenue", "sw"), ("Operating Margin", "om"), ("Diluted EPS", "eps")):
        idx = [i for i, l in enumerate(sec) if l.startswith(label) and i >= anchor]
        if not idx:
            continue
        v = _vals(sec, idx[0])
        if side:
            n = len(v) // 2
            v = v[n:] if n >= 2 else v
        res[key] = v
    return res

def first(pat, txt, flags=re.I | re.S):
    m = re.search(pat, txt, flags)
    return m

def quarter_section(txt):
    """Narrative section for the quarter (before YTD / full-year sections)."""
    m = re.search(r"(First|Second|Third|Fourth) Quarter 20\d\d Versus 20\d\d Financial Comparisons", txt, re.I)
    if not m:
        m = re.search(r"Versus 20\d\d Financial Comparisons", txt, re.I)
    if not m:
        return txt
    rest = txt[m.end():]
    m2 = re.search(r"(First Half|Nine Months|Year-to-Date|Full Year|Fiscal(?: Year)?|Six Months|YTD)[^\n]{0,40}Versus", rest, re.I)
    return rest[:m2.start()] if m2 else rest[:8000]

def narrative(txt):
    q = re.sub(r"\s+", " ", quarter_section(txt))
    out = {}
    pats = {
        "subscription_support_growth_cc_pct": r"Subscription (?:&|and) support revenue (?:rose|increased|grew|was up|up)(?: by)? (\d+)%",
        "recurring_share_of_software_pct": r"recurring revenue represented (\d+)% of (?:total )?software revenue",
        "industrial_innovation_sw_growth_cc_pct": r"Industrial Innovation software revenue (?:rose|increased|grew|was up|was down|decreased|declined)(?: by)? ([\d.]+)%",
        "industrial_innovation_flat": r"Industrial Innovation software revenue (?:was )?(flat|stable)",
        "industrial_innovation_sw_eur_m": r"Industrial Innovation software revenue [^€]{0,40}€\s?([\d,.]+) (million|billion)",
        "life_sciences_sw_growth_cc_pct": r"Life Sciences software revenue (?:rose|increased|grew|was up|was down|decreased|declined)(?: by)? ([\d.]+)%",
        "life_sciences_flat": r"Life Sciences software revenue (?:was )?(flat|stable)",
        "life_sciences_sw_eur_m": r"Life Sciences software revenue [^€]{0,60}€\s?([\d,.]+) (million|billion)",
        "mainstream_sw_growth_cc_pct": r"Mainstream Innovation software revenue (?:rose|increased|grew|was up|was down|decreased|declined)(?: by)? ([\d.]+)%",
        "mainstream_flat": r"Mainstream Innovation software revenue (?:was )?(flat|stable)",
        "mainstream_sw_eur_m": r"Mainstream Innovation software revenue [^€]{0,50}€\s?([\d,.]+) (million|billion)",
        "3dx_sw_growth_cc_pct": r"3DEXPERIENCE (?:software )?revenue (?:rose|increased|grew|was up|up|decreased|declined|was down)(?: by)? (\d+)%",
        "3dx_share_of_eligible_pct": r"represent(?:ed|ing) (\d+)% of (?:the )?3DEXPERIENCE (?:E|e)ligible software revenue",
        "cloud_sw_growth_cc_pct": r"Cloud software revenue (?:rose|increased|grew|was up|up)(?: by)? (\d+)%",
        "cloud_share_of_software_pct": r"Cloud software revenue[^.]{0,80}?represent(?:ed|ing) (\d+)% of (?:total )?software revenue",
        "licenses_growth_cc_pct": r"Licenses and other software revenue (?:rose|increased|grew|was up|decreased|declined|was down)(?: by)? ([\d.]+)%",
    }
    for k, p in pats.items():
        m = re.search(p, q, re.I)
        if k.endswith("_flat"):
            if m:
                out[k.replace("_flat", "_sw_growth_cc_pct")] = out.get(k.replace("_flat", "_sw_growth_cc_pct"), 0.0)
            continue
        if m and m.group(1):
            val = m.group(1).replace(",", "")
            try:
                v = float(val)
            except ValueError:
                continue
            if k.endswith("_eur_m") and m.lastindex and m.lastindex >= 2 and m.group(2).lower() == "billion":
                v = v * 1000
            if k.endswith("growth_cc_pct"):
                ctx = q[m.start():m.end() + 5].lower()
                if re.search(r"(was down|decreased|declined)", q[m.start():m.end()], re.I):
                    v = -v
            out[k] = v
    return out

def highlights(txt):
    """Summary highlight lines (e.g. '3Q25: Recurring revenue up 9%, driven by strong subscription revenue up 16%')."""
    t = re.sub(r"\s+", " ", txt[:6000])
    out = {}
    m = re.search(r"subscription revenue (?:up|grew|rose|increased)(?: by)? (\d+)%", t, re.I)
    if m:
        out["subscription_growth_cc_pct"] = float(m.group(1))
    m = re.search(r"Recurring (?:software )?revenue (?:up|grew|rose|increased)(?: by)? (\d+)%", t, re.I)
    if m:
        out["recurring_growth_cc_pct"] = float(m.group(1))
    return out

def objectives(txt):
    """FY objectives from the 'Financial Objectives for YYYY' table (2nd column = FY)."""
    L = lines(txt)
    try:
        s0 = next(i for i, l in enumerate(L) if re.match(r"Financial Objectives for 20\d\d", l))
    except StopIteration:
        return {}
    res = {"obj_year": re.search(r"20\d\d", L[s0]).group(0)}
    sec = L[s0:s0 + 70]
    def row(label, pat):
        for i, l in enumerate(sec):
            if l.startswith(label):
                cells = []
                for t in sec[i + 1:i + 6]:
                    if re.search(pat, t):
                        cells.append(t)
                    elif cells:
                        break
                if cells:
                    return cells
        return []
    rev = row("Total Revenue", r"€\s?[\d.]+\s*(?:[-–]|to)\s*€")
    if rev:
        m = re.findall(r"€\s?([\d.,]+)\s*(?:[-–]|to)\s*€\s?([\d.,]+)", rev[-1])
        if m:
            res["fy_rev_low_eur_m"] = round(float(m[0][0]) * 1000, 1)
            res["fy_rev_high_eur_m"] = round(float(m[0][1]) * 1000, 1)
    g = row("Growth ex FX", r"[-–]\s*\(?[\d.]+\)?%")
    if g:
        res["fy_growth_exfx"] = g[-1]
    g2 = row("Growth", r"[-–]\s*\(?[\d.]+\)?%")
    if g2:
        res["fy_growth_reported"] = g2[-1]
    om = row("Operating Margin", r"%\s*[-–]\s*[\d.]+%")
    if om:
        res["fy_op_margin_range"] = om[-1]
    eps = row("EPS Diluted", r"€\s?[\d.]+\s*(?:[-–]|to)\s*€")
    if eps:
        res["fy_eps_range"] = eps[-1]
    epsg = row("Growth", r"[-–]\s*[\d.]+%")
    return res
