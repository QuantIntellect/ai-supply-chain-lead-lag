# Siemens AG (SIE.DE): IR notes

Siemens' fiscal year ends Sep 30. Q1 FY2026 covers Oct–Dec 2025 and is coded `2026Q1`. Figures are in EUR million unless stated, as reported in each quarter's own release (not later restatements). "comp" means comparable growth, net of currency translation and portfolio effects. SI = Smart Infrastructure, which holds Siemens' electrification, electrical-products and buildings businesses. DI = Digital Industries.

## Demand narrative 2023–2026 (dated by release)

- **2023-02-08 (evening, ad hoc 19:50 CET):** FY23 outlook raised after a "flying start". Group comp revenue guidance moved from 6–9% to 7–10%, and SI from 8–11% to 9–12%. Q1 group orders were €22.6bn (comp −8% against a huge prior year). SI orders rose +16% comp.
- **2023-05-17:** Q2 FY23 orders were €23.6bn (+15% comp), book-to-bill 1.22. SI orders rose +9% comp and SI revenue +21% comp. In the presentation, Electrification orders were up 34%, with "large orders from data center, semis & power dist. customers" and a record SI backlog of about €16bn. The group guide was raised to 9–11%.
- **2023-08-10:** Q3 FY23 orders rose +15% comp and the group backlog reached €110bn. The release cites "larger contract wins from data center, battery manufacturing and power distribution customers". The presentation adds: "Accelerating use of AI applications drives data center investment". DI orders fell 35% comp (customer destocking). This is the first split between electrification strength and automation weakness.
- **2023-11-16:** Q4 FY23 commentary: "Accelerated adoption of generative AI drives data center investment". Electrification showed a "sharp increase in the U.S. including a number of larger contract wins with data center customers". SI's record backlog was €16.5bn. The FY24 group guide was 4–8% comp.
- **2024-05-16:** Q2 FY24 group orders fell 12% comp and DI's FY24 comp revenue guidance was cut from 0–3% to −8% to −4%. SI orders still rose +10% comp to €6.1bn on "a particularly high level of contracts from data center customers". The presentation says "AI demand is a significant inflection for accelerated data center investment" and notes long-lead electrical supply chains under pressure.
- **2024-08-08:** Q3 FY24 SI orders rose +11% comp, with "Massive AI driven momentum from data center customers". SI backlog hit an all-time high of €18.6bn. Group orders fell 15% comp (DI), book-to-bill 1.05.
- **2024-11-14:** Q4 FY24 Electrification orders rose +31%, "driven by large orders from data center and energy customers". Group orders rose +10% comp and the backlog was €113bn. The FY25 guide was 3–7% comp. An SI Capital Market Event followed on 2024-12-12.
- **2025-02-13:** Q1 FY25 included a multi-year capacity agreement with Compass Datacenters for standardized MV power skids. Electrification orders rose +10% on data center, energy and industry orders. SI orders rose +5% comp.
- **2025-05-15 and 2025-08-07:** These quarters show lumpy data-center orders. SI orders were −3% and −1% comp against prior-year quarters that carried "a particularly large number of contracts from data center customers". "Large data center orders [were] below [the] record prior year quarter", but SI revenue still grew +10% and +9% comp from backlog execution.
- **2025-11-13:** At the ONE Tech strategy day, combined with Q4 FY25 results, "Data Centers and AI factories" was named a target market with an 11% CAGR. U.S. orders rose +18%, "strongly up in Electrification & EP on data center wins". The FY26 guide was 6–8% comp and the mid-term ambition was raised to 6–9%.
- **2026-02-12:** Q1 FY26 SI orders were €7.2bn (+22% comp). Data Center revenue grew about 35%. Siemens and nVent published a liquid-cooling reference architecture for NVIDIA AI data centers. EPS pre PPA guidance was raised to €10.70–11.10.
- **2026-05-13:** Q2 FY26 SI orders rose +35% comp to a record €7.5bn, with "data centers with triple digit growth". Data Center H1 revenue grew more than 45%. Group orders rose +18% comp, book-to-bill 1.22. Siemens also announced a US$165m U.S. investment in AI-infrastructure manufacturing.
- **2026-08-06:** Q3 FY26 group orders were a record €27.9bn (+14% comp), book-to-bill 1.34, backlog €132bn. SI orders were €8.0bn (+42% comp). Data-center orders for the first nine months of FY26 were "up triple-digit" to about €6bn, and data-center revenue grew more than 50% to €3.1bn. Siemens serves 9 of the top 10 data-center providers. EPS guidance was raised to €11.20–11.50.

## Sources and method

- **Release dates:**
  - FY16 onward: datelines of the earnings release and press release PDFs listed on the IR financial-results and archive pages.
  - FY15: presentation filenames (yymmdd) plus the FY15 earnings releases (en-gb archive).
  - Every date was cross-checked against the press.siemens.com results event pages and against Yahoo (all 47 Yahoo dates in 2015–2026 match within ±1 day).
- **Timing:**
  - Exact 07:00 times for 2025Q1–2026Q3 come from the press.siemens.com event pages, either as a stated "(7:00 a.m. CET/CEST)" or as the 'Save the date' start time on the 2025+ pages.
  - Every other regular release is BMO. The evidence is the earnings release's own line "Starting today at HH:MM a.m., the press conference…": the press call started at or before 09:00, so the release came earlier that morning. The HH:MM is left blank because the exact release time is not published.
  - Q1 FY16, Q1 FY17 and Q1 FY23 were published the evening before the AGM, together with an ad hoc, so they are AMC.
  - Ad hoc times are EQS-News timestamps from the Siemens IR feed (`irpages2.eqs.com … type=adhoc`), converted from UTC to Europe/Berlin.
- **KPIs:** from Siemens' quarterly "Financial Results" Excel files:
  - Segment sheet: Siemens continuing operations; DI and SI orders, revenue, comp growth and margin.
  - Income statement: gross margin = gross profit / revenue.
  - Book-to-bill, order backlog (€bn, stored ×1000 in `backlog`) and the outlook come from regex over the earnings-release text.
  - `guidance_rev_low/high` = FY Group comparable revenue growth % (FY22Q1 was qualitative: "mid-single-digit").
  - The 2022Q3 EPS guide of €5.33–5.73 includes the Siemens Energy impairment (€8.70–9.10 excluding it).
- **Event types:**
  - `prelim`: ad hoc guidance raises or preliminary results, 2016-01-25, 2017-01-31, 2021-01-21 and 2023-02-08. Three of these coincide with the AMC Q1 release.
  - `profit_warning`: 2022-06-30, the ~€2.8bn non-cash impairment of the Siemens Energy stake (net income/EPS).
  - `CMD`: 2016-06-29, 2019-05-08, 2021-06-24, 2024-12-12 (SI) and 2025-11-13 (ONE Tech, 08:30 CET start).

## Gaps and confounders

- Siemens does not publish its own call transcripts, only webcasts. CEO/CFO speech PDFs exist for annual press conferences but were not collected.
- The half-year report is published together with the Q2 release, so it is not a separate event.
- CMD times are unknown except for 2025-11-13.
- These ad hocs are not in the event types but sit next to results events:
  - 2018-08-01 18:26 CEST: Vision 2020+, the evening before Q3 FY18.
  - 2019-05-07 17:45 CEST: portfolio refocus / Gas & Power spin, before Q2 FY19 and the CMD.
  - 2024-10-30 21:32 CET: Altair acquisition.
  - 2025-04-02 20:20 CEST: Dotmatics acquisition.
  - 2025-11-12 18:49 CET: Healthineers deconsolidation, the evening before Q4 FY25.
- Q4 FY26 results are scheduled for 2026-11-12, after today.
