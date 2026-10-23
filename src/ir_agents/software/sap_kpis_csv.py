"""Write SAP.DE_kpis.csv from parsed statements + release dates + curated AI/demand notes
(notes paraphrase/quote the quarterly statements and results presentations)."""
import sys, os, json, csv
sys.path.insert(0, os.path.dirname(__file__))
import fetch_util as fu

T = "SAP.DE"
RAW = os.path.join(fu.RAW_IR, T)
OUT = os.path.join(fu.PROC_IR, "%s_kpis.csv" % T)
COLS = ["ticker", "fiscal_period", "period_end", "release_date", "currency", "unit", "revenue", "revenue_yoy_pct",
        "orders", "orders_yoy_pct", "book_to_bill", "backlog", "gross_margin_pct", "guidance_text", "guidance_rev_low",
        "guidance_rev_high", "ai_dc_notes", "extra_json", "source_doc"]

NOTES = {
 "2022Q1": "No AI-specific commentary. Demand: S/4HANA current cloud backlog +86% (+79% cc); exit from Russia/Belarus; FY22 non-IFRS op-profit outlook lowered.",
 "2022Q2": "No AI-specific commentary. Cloud revenue became largest revenue stream; S/4HANA CCB +100%; FY22 op-profit outlook cut (Ukraine war, license decline).",
 "2022Q3": "No AI-specific commentary. CCB +38% (+26% cc) to EUR 11.27bn; S/4HANA CCB +108%; 'transformation reached an important inflection point'.",
 "2022Q4": "No AI-specific commentary. Return to operating-profit growth in Q4; planned Qualtrics divestment.",
 "2023Q1": "No AI-specific commentary. Qualtrics reported as discontinued operation (CCB/cloud base restated).",
 "2023Q2": "First AI framing: CEO sees 'significant opportunities ahead, in particular through the transformative power of AI'; SAP Business AI positioned as premium offering expanding the market.",
 "2023Q3": "CEO cites latest SAP Business AI capabilities (Joule copilot introduced Sep-2023) as innovation driver; cloud gross margin expansion.",
 "2023Q4": "CCB +27% on 'stellar order entry'. Jan-2024 transformation program (~8,000 positions) to shift investment to strategic growth areas, 'above all Business AI'; Ambition 2025 updated.",
 "2024Q1": "CEO: growth drivers are 'Business AI, cross-selling across our cloud portfolio, and winning new customers'; transformation program refocuses investment on Business AI.",
 "2024Q2": "CEO: 'Business AI enabling many deals'; investing to be the leader in Business AI; 2025 op-profit ambition raised.",
 "2024Q3": "'A significant part of our cloud deals in Q3 included AI use cases'; SAP Knowledge Graph announced; FY24 outlook raised.",
 "2024Q4": "Half of Q4 cloud order entry included AI; total cloud backlog EUR 63.3bn (+40%); 2025 outlook implies cloud revenue +26-28% cc; CEO expects revenue growth to accelerate through 2027 on data + Business AI.",
 "2025Q1": "SAP Business Data Cloud launched 13-Feb-2025 as data foundation for AI; 'AI-powered portfolio'; outlook maintained despite elevated macro/tariff uncertainty.",
 "2025Q2": "Joule available 'everywhere and for everything'; Business Data Cloud described as 'powerful accelerator of AI'.",
 "2025Q3": "Customers adopting Business Suite incl. Business Data Cloud and AI 'at accelerated pace'; FY25 cloud revenue now guided to lower end of range, op profit to upper end.",
 "2025Q4": "Business AI included in two thirds of Q4 cloud order entry; 90% of the 50 largest Q4 deals included Data or AI; total cloud backlog EUR 77.3bn (+30%).",
 "2026Q1": "CEO: momentum in Business AI 'delivering real outcomes'; Reltio acquisition (make enterprise data AI-ready) announced 27-Mar-2026; outlook assumes Middle East de-escalation; total revenue growth now seen similar to 2025 (accelerating in 2027).",
 "2026Q2": "Autonomous Enterprise strategy (12-May-2026): Autonomous Suite + Business AI Platform + Joule agents; CCB +26% cc.",
 "2026Q3": "Joule Work adoption (>110k desktop users); customers 'investing in the technology behind it - from the cloud and data foundation to our Business AI'; first EUR 10bn+ revenue quarter; FY26 cloud revenue guided to upper end.",
}
GUIDE_OVERRIDE = {
 "2025Q3": "FY2025 outlook: cloud rev EUR 21.60-21.90bn cc (now towards lower end); cloud+software rev EUR 33.10-33.60bn cc; non-IFRS op profit EUR 10.30-10.60bn cc (now towards upper end); FCF raised",
 "2026Q3": "FY2026 outlook: cloud rev EUR 25.80-26.20bn cc (towards upper end); cloud+software rev EUR 36.30-36.80bn cc (towards upper end); non-IFRS op profit EUR 11.90-12.30bn cc; FCF ~EUR 10bn",
}
EXTRA = {"2024Q4": {"total_cloud_backlog_bn": 63.3, "tcb_yoy": 40}, "2025Q4": {"total_cloud_backlog_bn": 77.29, "tcb_yoy": 30}}

def main():
    parsed = json.load(open(os.path.join(RAW, "kpis_parsed.json")))
    ev = {}
    with open(os.path.join(fu.PROC_IR, "%s_events.csv" % T)) as f:
        for r in csv.DictReader(f):
            if r["event_type"] in ("Q1", "Q2", "Q3", "Q4"):
                ev[r["fiscal_period"]] = r["event_date"]
    rows = []
    for p in parsed:
        per = p["fiscal_period"]
        ex = json.loads(p["extra_json"])
        ex.update(EXTRA.get(per, {}))
        rec = {c: "" for c in COLS}
        rec.update({"ticker": T, "fiscal_period": per, "period_end": p["period_end"], "release_date": ev.get(per, ""),
                    "currency": "EUR", "unit": "EUR m", "revenue": p.get("revenue", ""),
                    "revenue_yoy_pct": p.get("revenue_yoy_pct", ""), "backlog": p.get("backlog", ""),
                    "gross_margin_pct": p.get("gross_margin_pct", ""),
                    "guidance_text": GUIDE_OVERRIDE.get(per, p.get("guidance_text", "")),
                    # SAP gives no total-revenue range: keep guidance_rev_* blank (C&S range is in extra_json guide_cs_rev_*)
                    "guidance_rev_low": "", "guidance_rev_high": "",
                    "ai_dc_notes": NOTES.get(per, ""), "extra_json": json.dumps(ex, ensure_ascii=False),
                    "source_doc": "data/raw/ir/SAP.DE/sap-%s-q%s-statement.pdf" % (per[:4], per[-1])})
        ex["backlog_definition"] = "backlog = current cloud backlog (CCB, EUR m); orders not disclosed by SAP"
        rec["extra_json"] = json.dumps(ex, ensure_ascii=False)
        rows.append(rec)
    rows.sort(key=lambda r: r["fiscal_period"])
    with open(OUT, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLS)
        w.writeheader()
        for r in rows:
            w.writerow(r)
    print(len(rows), "rows ->", OUT)

if __name__ == "__main__":
    main()
