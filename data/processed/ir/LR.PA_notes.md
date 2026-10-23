# Legrand (LR.PA): IR notes

## Demand narrative, 2023–2026 (from Legrand's own releases)

- **2023-02-09 (FY22, 07:00 BMO)**: 2022 sales rose 19.2% (organic +9.7%; Q4 organic +8.5%). The FY23 target pointed to normalisation: sales growth of +2% to +6% at constant FX, of which about +3% from acquisitions.
- **2023-07-31 (H1-23)**: FY23 sales target raised to +5% to +8% (excluding Russia). Growth "buoyed by faster-expanding segments incl. energy efficiency, connected products and datacenters". Q2 organic was only +2.0%.
- **2023-11-08 (9M-23)**: Q3 organic +1.8%. The FY23 target was narrowed to about +5% (organic +2.5% to +3.5%). Acquired ZPE Systems (datacenter).
- **2024-02-15 (FY23)**: Q4-23 organic 0.0%. Datacenters "now represent 15% of total sales". FY24 target: low single-digit sales growth.
- **2024-05-03 (Q1-24)**: Organic −5.4% "in contracting markets excluding datacenters". This is the weakest quarter in the 2022–26 series.
- **2024-07-31 (H1-24)**: Q2 organic turned positive at +1.5%, with North & Central America at +5.8%, "notably from datacenter business". Three DC acquisitions in H1 (Netrack, Davenham, Vass).
- **2024-09-24 (CMD, London)**: 2030 ambition of €12–15bn sales. Energy- and digital-transition solutions, including datacenters, were 46% of 2023 revenue.
- **2025-02-13 (FY24)**: Datacenters were about 20% of sales (proforma) and grew organically by close to +15% in 2024. Q4-24 organic +6.2%. FY25 target: +6% to +10% sales growth excluding FX.
- **2025-05-07 (Q1-25)**: Q1 organic +7.6%, with "accelerating organic growth in datacenters".
- **2025-07-17 (pre-release, 07:30 BMO)**: H1 sales +15% excluding FX. Q2 organic +10.1%, "largely fueled by continued strong growth in datacenter activity". The FY25 target was raised to +10% to +12% (previously +6% to +10%), two weeks before the H1 results. The **2025-07-31** H1 release then gave datacenters at 24% of H1 sales.
- **2025-11-06 (9M-25)**: Q3 organic +6.7% (9M +8.2%), "driven by strong momentum in datacenters". Four DC acquisitions year to date.
- **2026-02-12 (FY25)**: Datacenters reached €2.4bn, or 26% of 2025 sales (against €0.7bn in 2020). Q4-25 organic +6.2%. FY26 target: +10% to +15% excluding FX (organic +4% to +7%, acquisitions +6% to +8%).
- **2026-05-07 (Q1-26)**: Sales +18% excluding FX (organic +9.3%), "driven by datacenters and acquisitions".
- **2026-07-29 (H1-26)**: Q2 organic +10.4%. FY26 target raised to +16% to +19% (organic +8% to +10%, previously +4% to +7%), driven by datacenters and energy-transition offerings.
- **2026-09-28 18:00 (AMC; CMD in Singapore on 09-29, alongside Data Centre World Asia)**: Data-center sales will exceed €3bn in 2026, or 32% of sales. The mix is critical power 35%, physical compute infrastructure 25%, monitoring/management/control 25%, advanced cooling 5%. The upgraded 2027–30 ambition is an organic CAGR of +6% to +8%, about +5% a year from acquisitions, and an adjusted operating margin of 21% to 22%.

## Sources and method

- **Release dates**: taken from the "Financial presentations" and "Regular information" lists on legrand.com/en/investors-and-shareholders/regulated-information/<year> (2015–2026).
- **Release times**: taken from the French AMF regulated-information feed (info-financiere.gouv.fr OpenDataSoft API, dataset `flux-amf-new-prod`, ISIN FR0010307819).
  - Field `uin_dat_amf` is UTC. Paris time = `uin_dat_amf` + `timezone_uin_dat_amf`. Before 2017 the feed always used a +01:00 offset, so 2015–16 summer stamps also convert this way.
  - The press-release deposit (types 001xxx/005xxx) is preferred. Report deposits are used only if earlier than 09:00.
  - Cross-checks against the legrand.com newsroom JSON-LD `datePublished` (Paris time) match the AMF times for 2018-07, 2019-07, 2026-05, 2026-07 and 2026-09.
  - Newsroom stamps from 2017 are shifted forward by the UTC offset (2017-05-10: news 09:30 vs AMF 07:32; 2017-07-31: news 09:30 vs AMF 07:30). The FY16 release (2017-02-09, not in the AMF feed as a press release) is therefore set to 07:30 = news 08:30 − 1h.
  - 2018-07-31 and 2020-03-26 times come from the newsroom (07:30).
- **Event types**: Q1, H1 (fiscal_period YYYYQ2), Q3 (9-month results) and FY (YYYYQ4). Other events:
  - `prelim`: the 2025-07-17 H1 sales pre-release with a guidance raise.
  - `profit_warning`: 2020-03-26, suspension of the FY20 targets (Covid).
  - `CMD`: 2016-06-30 (US Investor Day; release at 22:54 Paris), 2019-06-12, 2021-09-22, 2022-03-29 (ESG CMD), 2024-09-24, 2025-03-25 (CSR CMD) and 2026-09-28 (release the evening before the Singapore CMD).
- **Excluded**: legal and other non-results releases (2018-09-11 premises search, 2022-10-20 indictment, 2023 Russia exit, 2024-10 French competition decision), acquisitions, and bond releases.
- **KPIs** (one row per quarter, 2019Q1–2026Q2; the 2019–2021 rows are auto-parsed figures only, with no guidance or DC notes transcribed):
  - Quarterly sales = difference of the cumulative 3M/6M/9M/12M consolidated sales in consecutive releases. Prior-year quarters come from the prior-year columns, so `revenue_yoy_pct` is computed, not stated.
  - Quarter-alone organic growth comes from each release's "changes in sales by destination at constant scope and FX" table (`extra_json.organic_growth_q_pct`).
  - Adjusted operating margin is cumulative (3M/H1/9M/FY), in `extra_json`.
  - `guidance_rev_low`/`guidance_rev_high` hold the FY **sales-growth % excluding FX** (Legrand's headline metric), not revenue levels. Organic and margin ranges are in `extra_json`.
- **Docs** (101 PDFs): results press releases and slideshows for 2015Q1–2026Q2 (the FY2014 and 2015 releases are official AMF copies), plus the 2025-07 pre-release, CMD 2024 and 2026 releases and decks, and the Covid release. Text is in data/processed/ir_text/LR.PA/.

## Gaps
- Missing documents: the 9M-2016 press release (the website links the 9M-2017 file; only the financial statements are kept) and the H1-2018 release and slides (no link).
- Event `source_url` cites the AMF deposit PDF that carries the timestamp for 52 of the 56 events; the others cite the newsroom page or the release PDF.

- **No order intake, backlog or book-to-bill**: Legrand does not report them.
- **No gross margin**: not extracted, since Legrand headlines the adjusted operating margin.
- **No call transcripts**: Legrand publishes webcasts only.
- **9M-2026 not yet out**: results are scheduled for early November 2026 (Yahoo shows 2026-11-05), so there is no 2026Q3 KPI or event row.
- **2019-06-12 Investor Day**: no AMF record, so the time is UNKNOWN.
- **Presentation text**: several slideshows (2024Q3 and 2025Q1–Q3) are image-based and yield almost no text.
- **Datacenter share**: only reported at certain dates (15% FY23, ~20% FY24, 24% H1-25, 26% FY25, 32% 2026E at the CMD). It is not a consistent quarterly series.
