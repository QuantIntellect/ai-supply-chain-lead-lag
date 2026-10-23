"""Build data/processed/ir/DSY.PA_kpis.csv (2022Q1..latest reported) from extracted press-release text."""
import sys, os, json
import pandas as pd
sys.path.insert(0, os.path.dirname(__file__))
import fetch_util as fu
from dsy_kpi_parse import summary_table, narrative, highlights, objectives, tofloat

T = "DSY.PA"
TXT = os.path.join(fu.TXT_IR, T)
ev = pd.read_csv(os.path.join(fu.PROC_IR, T + "_events.csv"), dtype=str).fillna("")
rel = {r.fiscal_period: r.event_date for r in ev.itertuples() if r.event_type in ("Q1", "Q2", "Q3", "Q4")}
QEND = {1: "03-31", 2: "06-30", 3: "09-30", 4: "12-31"}

AI = {
 "2022Q1": "AI mainly via Medidata AI (Synthetic Control Arm) and BIOVIA generative therapeutic design; no AI monetization metrics.",
 "2022Q2": "Medidata AI cited among growth drivers; Diota (AR/AI for manufacturing) acquisition. No AI KPIs.",
 "2022Q3": "Acquired StyleSage (AI-powered market intelligence) for CENTRIC PLM; Medidata AI a 'strong driver'.",
 "2022Q4": "Science-based virtual twins feeding 'AI engines'; Renault using 3DEXPERIENCE cloud data science/AI for real-time cost projection.",
 "2023Q1": "CEO: AI 'captured the attention of the world'; positions virtual twins + ML/generative design as existing AI offer. No revenue attribution.",
 "2023Q2": "AI + modeling/simulation + virtual twins theme (life-sciences science events); AI 11x on call; no monetization metrics.",
 "2023Q3": "'Human-centered generative experiences' framing; AI barely mentioned (2x on call).",
 "2023Q4": "Introduced 'Generative Economy' 2040 horizon; AI rhetorical, no revenue attribution.",
 "2024Q1": "Generative AI for faster life-sciences innovation cited; 'Generative Economy' strategy.",
 "2024Q2": "Developing AI-driven use cases across 3 sectors; Medidata AI/Clinical Data Studio in BMS deal. Quarter pre-announced 2024-07-09 (revenue miss, FY cut).",
 "2024Q3": "CEO: virtualizing industrial processes is a prerequisite 'in the age of AI'; 'generative experiences' from installed-base data. No AI KPIs.",
 "2024Q4": "Unveiled 3D UNIV+RSES (virtual twins + AI across lifecycle) and AI-based services with Q4 (2025-02-04); Life Sciences repositioning incl. AI integration.",
 "2025Q1": "Gen-7 / 3D UNIV+RSES as AI-ready IP platform; sovereign infrastructure incl. national AI data centers named a growth domain; High Tech demand for data-center/electronics simulation.",
 "2025Q2": "Headline 'Advancing AI for software-defined industries'; 'AI-driven cloud infrastructure' named a high-growth segment; 'AI is already creating a new growth path' (no figures).",
 "2025Q3": "Launched AI-native categories: Virtual Twin as a Service, Generative Experiences, Virtual Companions (Aura); FY revenue growth cut to 4-6% on Life Sciences/Centric weakness despite AI narrative.",
 "2025Q4": "NVIDIA partnership (virtual twins + accelerated computing, 'Industry World Models'); moving beyond seat-based to value-based pricing for AI solutions; 2026 = 3D UNIV+RSES monetization year. Q4 revenue +1% cc.",
 "2026Q1": "'Clear inflection point as AI redefines operational excellence'; customers moving from experimentation to industrial-scale (agentic) AI deployment; focus on monetization and scale (no AI revenue disclosed).",
 "2026Q2": "3DEXPERIENCE positioned as 'agentic platform' (Virtual Companions, AURA); customers 'increasingly investing in industrial AI' and cloud data prep; ArisGlobal (AI life-sciences platform) acquisition announced 2026-07-23; AI 54x on call.",
}

rows = []
for p in sorted(rel):
    if p < "2022Q1":
        continue
    fp = os.path.join(TXT, p + "_press_release.txt")
    if not os.path.exists(fp):
        continue
    t = open(fp, encoding="utf-8").read()
    st, n, h, o = summary_table(t), narrative(t), highlights(t), objectives(t)
    rev = st.get("rev", [])
    cur, prior = (tofloat(rev[0]) if len(rev) > 0 else None), (tofloat(rev[1]) if len(rev) > 1 else None)
    yoy = round((cur / prior - 1) * 100, 1) if cur and prior else None
    sw = st.get("sw", []); om = st.get("om", []); eps = st.get("eps", [])
    extra = {"basis": "non-IFRS; segment/product growth rates in constant currency (cc) as stated in press release",
             "rev_growth_cc_pct": tofloat(rev[3]) if len(rev) > 3 else None,
             "rev_growth_reported_stated": rev[2] if len(rev) > 2 else None,
             "rev_prior_year_eur_m": prior,
             "software_rev_eur_m": tofloat(sw[0]) if sw else None,
             "software_growth_cc_pct": tofloat(sw[3]) if len(sw) > 3 else None,
             "op_margin_nonifrs_pct": tofloat(om[0]) if om else None,
             "op_margin_nonifrs_prior_pct": tofloat(om[1]) if len(om) > 1 else None,
             "eps_diluted_nonifrs_eur": tofloat(eps[0]) if eps else None,
             "eps_growth_cc_pct": tofloat(eps[3]) if len(eps) > 3 else None}
    extra.update(h); extra.update(n)
    if o:
        extra["guidance_fy_year"] = o.get("obj_year")
        extra["guidance_fy_growth_exfx"] = o.get("fy_growth_exfx")
        extra["guidance_fy_op_margin"] = o.get("fy_op_margin_range")
        extra["guidance_fy_eps"] = o.get("fy_eps_range")
    extra = {k: v for k, v in extra.items() if v is not None}
    g = ""
    if o:
        parts = []
        if o.get("fy_rev_low_eur_m"):
            parts.append("revenue EUR %.3f-%.3fbn" % (o["fy_rev_low_eur_m"] / 1000, o["fy_rev_high_eur_m"] / 1000))
        if o.get("fy_growth_exfx"):
            parts.append("growth ex FX %s" % o["fy_growth_exfx"])
        if o.get("fy_growth_reported"):
            parts.append("reported %s" % o["fy_growth_reported"])
        if o.get("fy_op_margin_range"):
            parts.append("op margin %s" % o["fy_op_margin_range"])
        if o.get("fy_eps_range"):
            parts.append("EPS %s" % o["fy_eps_range"])
        g = "FY%s non-IFRS objectives: " % o.get("obj_year") + "; ".join(parts)
    y, q = int(p[:4]), int(p[-1])
    rows.append({"ticker": T, "fiscal_period": p, "period_end": "%d-%s" % (y, QEND[q]), "release_date": rel[p],
                 "currency": "EUR", "unit": "EUR m", "revenue": cur, "revenue_yoy_pct": yoy,
                 "orders": "", "orders_yoy_pct": "", "book_to_bill": "", "backlog": "", "gross_margin_pct": "",
                 "guidance_text": g, "guidance_rev_low": o.get("fy_rev_low_eur_m", ""), "guidance_rev_high": o.get("fy_rev_high_eur_m", ""),
                 "ai_dc_notes": AI.get(p, ""), "extra_json": json.dumps(extra, ensure_ascii=False),
                 "source_doc": "data/raw/ir/DSY.PA/%s_press_release.pdf" % p})
df = pd.DataFrame(rows).sort_values("fiscal_period", ascending=False)
df.to_csv(os.path.join(fu.PROC_IR, T + "_kpis.csv"), index=False)
print(df[["fiscal_period", "release_date", "revenue", "revenue_yoy_pct", "guidance_rev_low", "guidance_rev_high"]].to_string())
