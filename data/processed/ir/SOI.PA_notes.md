# Soitec (SOI.PA) — IR notes

## Demand narrative 2023–2026 (from Soitec releases; fiscal year ends 31 March)
- **2022-10-26, Q2 FY23:** strong growth in Photonics-SOI (data transceivers) and Imager-SOI.
- **2023-04-26, Q4 FY23:** Photonics-SOI sales support "high speed connectivity solutions for Artificial Intelligence".
- **2023-07-25, Q1 FY24:** revenue EUR 157m (-23%). An inventory correction in the smartphone market hits Mobile Communications.
- **2023-11-15, H1 FY24:** demand for Edge AI chips from Smart devices continues, but Photonics-SOI sales into cloud and data centers decline.
- **2024-11-20, H1 FY25:** RF-SOI inventory correction and weak automotive, partly offset by POI penetration and the "fast-growing data center market".
- **2025-05-27, FY25:** Photonics-SOI "gaining traction … to equip the next generation of AI Datacenters".
- **2025-07-22, Q1 FY26:** RF-SOI correction, weak automotive and the Imager-SOI phase-out, against "strong momentum in Photonics-SOI".
- **2025-11-19, H1 FY26:** revenue EUR 231m (-29% organic). AI-related products perform strongly.
- **2026-02-03, Q3 FY26:** revenue EUR 160m (-29% reported). Edge & Cloud AI revenue is EUR 54m (+27% at constant FX and scope).
- **2026-07-22, Q1 FY27:** revenue EUR 113m (+23% at constant currency and scope), published ahead of schedule. Photonics-SOI sales double y-o-y on AI data-center transceivers, and the 300mm Singapore fab is qualified for Photonics-SOI.
- **2026-09-02, trading update:** the Q2 FY27 revenue guidance and the Photonics-SOI outlook are raised on accelerating demand. A capital-markets transaction, "Project Signal", followed on 2026-09-17/18 and is not in the events file.

## Methods and conventions
- **Fiscal year** ends 31 March: FY2027Q1 is Apr–Jun 2026; H1 is Apr–Sep. Home market is Euronext Paris (Europe/Paris, cut-offs 09:00 / 17:35).
- **Event dates** are the datelines of the press-release PDFs on Soitec's regulated-information page.
- **Timing:** every release from FY17 to FY27 carries an "Agenda: … due to be published on <date>, after market close" statement, so all regular rows are AMC with a blank time. No HH:MM is published.
  - Exception: the 2026 targets release of 2021-06-10 was issued "before market opens" (BMO, labelled CMD).
- **2015–16 rows:** Q2, H1, Q3, prelim and FY for FY2016 come from soitec.com and AMF (DILA) archive links. Their timing is UNKNOWN.
- **FY2024 results:** dated 2024-05-22 (AMC) from the Q3 FY24 release agenda, because the FY24 press release itself is not on the IR page.
- **Gaps:** releases from 2015-01 to 2015-09 (Q3 FY15 revenue, FY15 results, Q1 FY16 revenue) and possibly the Q2 FY17 revenue release (Oct 2016) are missing. Standalone guidance updates other than 2026-09-02 were not searched systematically.
- **Not yet published:** H1 FY27 results (scheduled 2026-11-18, after market close).
- **Docs:** 20 press releases from FY2022Q4 onward are in the manifest; older PDFs back to 2016 are also downloaded in `data/raw/ir/SOI.PA`. Presentations and transcripts were not collected.
- **KPIs:**
  - Regex; coverage is partial.
  - Revenue is the headline figure for the period named in the release. Rows from FY releases are relabelled Q4 when the extracted figure is Q4 revenue, and H1 rows are relabelled Q2 likewise.
  - YoY is the reported change; the constant-FX change is in `extra_json`.
  - Soitec gives no quarterly gross margin; EBITDA margin is in `extra_json` where found.
