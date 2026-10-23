# BESI.AS — BE Semiconductor Industries (Besi): IR data notes

Collected 2026-10-23. Scripts: `src/ir_agents/semicap/besi_*.py` (plus shared `irlib.py`).

## Sources and access
- **www.besi.com cannot be reached from this machine.** The TLS handshake is refused at the IP level for every client, and WebFetch fails too. Everything from besi.com was taken from **Wayback Machine** captures: the CDX index, then raw `id_` snapshots of press-release year pages, detail pages, call invites, financial-calendar pages and PDF decks. The `source_url` values still point at the original besi.com URLs. To fetch one, prefix it with `https://web.archive.org/web/<ts>id_/`.
- **Euronext Live regulated news** (issuer id 062133: `live.euronext.com/en/listview/company-press-release/062133`). It gives an exact publication timestamp, in Amsterdam local time, for every Besi release from 2018-05-11 to now. It also hosts the official PDF attachment (`/ajax/node/company-press-release/<nid>`). Euronext is the `source_url` for every event from May 2018 onward.
- Besi does not use GlobeNewswire or Business Wire.

## Release-time basis (event_time_local / timing)
- **2018-05 → 2026-10:** the Euronext Live timestamp of each release (Europe/Amsterdam).
  - Results releases are always at 07:00, with a few at 07:01, 07:14 (2025-07-24) and 07:23 (2020-10-22). All are BMO; Euronext Amsterdam opens at 09:00.
- **2015-02 → 2018-04 (13 results releases):** the time Besi stated in its own call-invite press release, issued about one week before each result ("will release results … on <date> at 7.00 a.m. CET").
  - Every one of the 13 invites states 7.00 a.m.
  - This is the documented time for each event, not an inferred convention. It is consistent with the Euronext timestamps of all 34 later releases, all at about 07:00.
- No time was found for these, which are left UNKNOWN:
  - the 2015-09-01 TCB order announcement;
  - the 2015-09-10 Q3-15 guidance cut;
  - the analyst meetings / CMDs of 2015–2020 and 2022–2024.
- The 2021-06-10 analyst meeting is INTRADAY at 16:00, per the financial calendar. The 2025 and 2026 Investor Days are dated by their 07:00 target-model press releases; the presentations themselves started at 13:00.
- **No Besi results release falls after the market close.** AMC count = 0.

## Event calendar (BESI.AS_events.csv), 68 rows, 2015-02-26 → 2026-10-22
- **Q1–Q4 results:** 48 releases, Q4-14 through Q3-26, with no quarter missing. The Q4 release is the combined Q4 + FY release.
- **prelim (2):**
  - 2021-04-06 07:00, Q1-21 orders trading update (€327m);
  - 2026-01-12 08:00, Q4-25 preliminary orders of about €250m.
- **profit_warning (3):**
  - 2015-09-10 (time unknown), Q3-15 revenue guide cut to −28–33% QoQ;
  - 2018-07-03 08:00, Q2-18 revenue guidance cut to +4% after a €28m order cancellation;
  - 2021-12-20 07:00, Shah Alam flood: Q4-21 revenue guide cut to −15–20% QoQ, with Q4-21 orders of €180–190m.
- **trading_update (3), which are order announcements:**
  - 2015-09-01, TCB orders;
  - 2024-05-09 07:40, order for 26 hybrid-bonding systems from a leading logic maker;
  - 2025-05-05 08:00, follow-on order for 5 TCB Next systems (about $20m).
- **CMD (12):** annual June analyst meetings / Capital Markets Days / Investor Days in 2015–2026 (one per year).
  - 2025-06-12: targets raised to revenue €1.5–1.9bn and operating margin 40–55%.
  - 2026-06-18: targets raised to €1.7–2.2bn and 45–55%.
- **Other price-relevant releases** (left out of events.csv because they fit none of its event types; Euronext times):
  - 2020-10-22 07:24, hybrid-bonding joint development agreement with Applied Materials;
  - 2024-11-14 20:00, statement on media reports of a potential strategic combination;
  - 2025-04-15 09:33, Besi notes Applied Materials' purchase of 9% of its shares;
  - 2026-03-13 08:53, a second statement on media reports of a potential strategic combination.

## Documents (BESI.AS_manifest.csv), 63 files
- **Press releases (42):** official Euronext PDF for every results release 2018Q2–2026Q3, plus the prelim, profit-warning, order and investor-day releases.
  - **2020Q1 exception:** Euronext's attachment `Connect_q1-2020.pdf` turned out to be another issuer's file and was discarded. The Besi web page (highlights and outlook only, via Wayback) is used instead.
- **Presentations (21):** the quarterly results "Webinar" decks 2022Q1–2026Q1 from Wayback. For 2026Q2, Investor Presentation August 2026 is used instead, because the Q2-26 webinar deck was not archived. Also included are the CMD 2022 and Investor Day 2024 and 2025 decks.
- **Transcripts:** Besi does not publish call transcripts, only audio webcasts.
- Text extracts are in `data/processed/ir_text/BESI.AS/<period>_<doctype>.txt`.

## KPIs (BESI.AS_kpis.csv), 34 quarters, 2018Q2 → 2026Q3, EUR million
- **Revenue and orders** come from the release's summary table. YoY % is taken from the stated vs-prior-year-quarter column. The QoQ % and the prior-year values are in `extra_json`.
- **Orders** are Besi's reported orders (bookings). Besi gives no numeric backlog, so `backlog` is blank.
- **Book-to-bill** is the stated "Book to Bill Ratio" row for 2018Q2–2023Q4. From 2024Q1 it is computed as orders/revenue, flagged in `extra_json.book_to_bill_source`.
- **Gross margin** is as reported.
- **Guidance** is always the next-quarter revenue % change vs the reported quarter plus a gross-margin range. `guidance_rev_low` and `guidance_rev_high` are therefore blank, because no absolute EUR range is ever stated. The parsed values go in `extra_json`:
  - `guide_rev_qoq_pct_low/high` and `guide_gm_low/high`;
  - `guide_rev_implied_eur_m`, an implied EUR range derived as reported revenue × (1 + %), labelled as derived.
- **China:** China orders (€m and % of orders) appear in `extra_json` for 2024Q1 onward. Earlier releases show only Asia Pacific vs EU/USA.
- **ai_dc_notes** holds keyword sentences (AI, data center, 2.5D/3D, hybrid bonding, HBM, photonics, China, subcontractors) taken from the highlights and the CEO comment.
- **Gaps:**
  - no KPI rows before 2018Q2; the 2015–2018Q1 releases exist only as Wayback HTML and were not parsed;
  - 2020Q1 has no stated book-to-bill (computed instead) and no YoY columns beyond those stated in its highlights.

## Demand narrative 2023–2026 (dated by release)
- **2023-02-22 (Q4-22):** Orders recovered to €180.5m (+44.1% QoQ) on high-end smartphone and hybrid-bonding bookings, but were −10.9% YoY as mainstream computing and automotive weakened. Q1-23 revenue was guided −0–10% "as industry downturn continues".
- **2023-07-27 (Q2-23):** Cycle trough. Orders fell to €112.6m (−20.7% QoQ, −26.5% YoY) after the mobile ramp ended, with broad weakness in computing. Q3-23 revenue was guided −20–30%.
- **2023-10-26 (Q3-23):** First AI-led turn. Orders rose 13.1% QoQ to €127.3m on computing, hybrid-bonding and photonics orders. Q4-23 revenue was guided +15–25% on computing shipments.
- **2024-02-22 (Q4-23):** Orders reached €166.4m (book-to-bill 1.04). The CEO cited "leadership position in advanced packaging for next generation AI". The hybrid-bonding installed base passed 40 systems, and customers grew from 3 to 9 across logic and memory. Q1-24 was guided −5–15%.
- **2024-04-25 (Q1-24):** Orders fell 23.3% QoQ to €127.7m on "a pause in demand for 2.5D and 3D applications following strong H2-23". Revenue was nonetheless +9.7% YoY on 2.5D/3D AI.
- **2024-05-09 → 2024-07-25 (Q2-24):** An order for 26 hybrid-bonding systems from a leading logic maker (announced 07:40 on 05-09) lifted Q2-24 orders to €185.2m (+45% QoQ, +64.5% YoY) on hybrid bonding, photonics and 2.5D AI.
- **2024-10-24 (Q3-24):** Orders were €151.8m (−18% QoQ, +19% YoY): AI strength against weak automotive and China demand. Q4-24 was guided flat ±10%, partly because a customer delayed shipments of hybrid-bonding systems (a push-out).
- **2025-02-20 (Q4-24):** Orders were €121.9m (−26.7% YoY) as HPC and mainstream bookings fell. AI applications were about 50% of FY24 orders. Q1-25 revenue was guided −0–10%.
- **2025-04-23 (Q1-25):** Orders were €131.9m (+8.2% QoQ) on Asian subcontractor bookings for AI data centers. Hybrid-bonding orders came from **two leading memory producers for HBM4**, plus follow-on logic orders from a leading Asian foundry.
- **2025-07-24 (Q2-25):** Orders were €128.0m (−30.9% YoY), with trade-tension caution among customers. Q3 revenue was guided −5–15%, but Besi said orders would "increase significantly" on hybrid bonding and AI 2.5D die attach.
- **2025-10-23 (Q3-25):** Upturn. Orders rose 36.5% QoQ to €174.7m (book-to-bill 1.32) on Asian subcontractors' 2.5D data-center and photonics bookings. Q4-25 revenue was guided +15–25%.
- **2026-01-12 (prelim, 08:00):** Q4-25 orders were about €250m (+43% QoQ, +105% YoY), and H2-25 orders about €425m (+63% vs H1-25). Drivers were 2.5D data-center bookings, photonics capacity and the expected hybrid-bonding orders.
- **2026-04-23 (Q1-26):** Orders were €269.7m (more than double YoY) as hybrid-bonding bookings came from multiple customers. Q2-26 revenue was guided +30–40%.
- **2026-06-18 (Investor Day):** The long-term model was raised to revenue €1.7–2.2bn and operating margin 45–55%. That followed €1.5–1.9bn in June 2025 and "€1bn+++" in 2024.
- **2026-10-22 (Q3-26):** Revenue was €283.4m (+113.6% YoY) and orders €342.6m (+96% YoY); LTM orders reached €1.2bn on hybrid bonding, data center and AI mainstream computing including power. Q4-26 was guided flat ±5% because customers asked for delivery dates aligned with their H1-27 capacity plans (a timing push).
