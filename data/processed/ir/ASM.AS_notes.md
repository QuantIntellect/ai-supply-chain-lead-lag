# ASM International (ASM.AS) — IR notes

Built by `src/ir_agents/semicap/asm_*.py` (gnw → special → download → events → manifest → kpis). Conventions follow `src/ir_agents/semicap/irlib.py`.

## Release calendar (`ASM.AS_events.csv`)
- **58 events, 2015-03-04 → 2026-07-28:** 47 scheduled quarterly releases (2014Q4 → 2026Q2; the Q4 release carries the full-year figures and is labelled `Q4`), 4 `prelim`, 3 `trading_update`, 1 `profit_warning` and 3 `CMD` (Investor Days).
- **Timezone:** Europe/Amsterdam (Euronext Amsterdam).
- **Timing classes:** 51 AMC, 7 BMO, no UNKNOWN.

**Where the times come from**

| Period | Source of HH:MM | Time |
|---|---|---|
| 2018Q4 → 2026Q2 | The press-release header states the time ("6 p.m. CET"). The GlobeNewswire (GNW) wire stamp agrees to the minute (2025Q1 was stamped 18:01). | 18:00 |
| 2016Q1 → 2018Q3 | No time in the header, so the GNW stamp is used. ASM's own pre-notices said "at approximately 18:00 CET". | 17:45–18:15 |
| 2015-03-04 → 2016-02-23 (2014Q4–2015Q4) | ASM still had a Nasdaq listing then. Its notices said results come "at approximately 00:00 (midnight) CET" (6 p.m. US ET). GNW stamps are 23:58 local on the date shown. | 23:58, AMC; the market reaction falls on the next trading day |

- **Unscheduled releases:** the header states the time and it matches the GNW stamp. They went out at 17:45 (AMC) or 07:45/08:00 (BMO).
- **GNW timestamps:** GNW shows times in US Eastern; they were converted to Europe/Amsterdam with zoneinfo, so DST is handled. The full GNW list is cached in the scratchpad (`gnw_all.csv`, 963 releases from 2000 to 2026).
- **`source_url`:** the GNW release URL, because it carries the timestamp. The asm.com PDF URLs are in the manifest.

**Unscheduled events and how they were classified**

| Date | Time | Type | Content |
|---|---|---|---|
| 2020-01-14 | 17:45 | prelim 2019Q4 | Q4 orders slightly above €370m vs €290–310m guidance |
| 2021-07-01 | 17:45 | prelim 2021Q2 | Q2 orders slightly above €500m vs €420–440m guidance |
| 2021-09-28 | 07:45 | CMD | Investor Day |
| 2021-09-28 | 07:45 | trading_update 2021Q3 | Same release as the Investor Day: Q3 orders now expected above €600m vs €510–530m guidance |
| 2022-11-28 | 17:45 | trading_update 2022Q4 | China export-control hit cut to 15–25% of China sales; Q4 sales guidance raised to €630–660m from €600–630m |
| 2023-01-17 | 17:45 | prelim 2022Q4 | Revenue about €720m and orders about €820m |
| 2023-09-26 | 07:45 | CMD | Investor Day: 2025 target raised, 2027 target introduced |
| 2024-12-04 | 08:00 | trading_update 2024Q4 | New US export rules; Q4 2024 and FY2025 guidance reiterated |
| 2025-09-23 | 07:45 | CMD | Investor Day: 2030 target |
| 2025-09-23 | 07:45 | profit_warning 2025Q4 | Same release as the Investor Day: "outlook H2 2025 lowered", Q4 revenue below earlier expectations |
| 2026-01-19 | 08:00 | prelim 2025Q4 | Bookings about €800m and revenue €698m, both above guidance |

- **Investor Day timing:** each Investor Day has two rows (CMD plus the guidance row) with the same timestamp. Deduplicate them if you need one event per date. The time recorded is when the press release went out. The 2025 Investor Day sessions themselves ran from 14:30 to 18:00 CET.
- **Left out on purpose:**
  - Technology seminars (SEMICON West / IEDM, 2015–2019), which carried no financial updates.
  - Releases about the ASMPT stake (stake sales in 2017; 2018-09-28; 2024-10-14 at 13:00; 2024-11-12).
  - AGM, buyback and management-change releases.
- **Not yet happened:** Q3 2026 results are scheduled for **2026-10-27, about 18:00 CET** (GNW notice of 2026-10-06; call on 2026-10-28 at 15:00 CET). This falls after today, so it is not in the CSV.

## Documents (`ASM.AS_manifest.csv`, 77 files)
- **Press releases:** 46 quarterly releases (PDF) covering 2015Q1–2026Q2, from the asm.com results center (`/downloads/...` links redirect to `/media/...pdf`).
- **Presentations:** 22 investor presentations (PDF) covering 2021Q1–2026Q2.
  - Each presentation's cover is dated on the results day, so `pub_date` is the release date.
  - The 2023Q3 deck is not linked on asm.com any more. It came from the Wayback Machine; that copy is truncated at 1 MiB, but pymupdf recovered the text of all 47 pages.
- **Special releases:** 9 releases (HTML from GNW) under `data/raw/ir/ASM.AS/special/`.
- **Text files:** `data/processed/ir_text/ASM.AS/<period>_{press_release,presentation,prelim,guidance_update,investor_day,export_update}.txt`.
- **Transcripts:** ASM does not publish call transcripts. It only offers Chorus Call webcasts, so there are no transcripts.
- **Not downloaded:** older presentations (before 2021) and the Investor Day slide decks.

## KPIs (`ASM.AS_kpis.csv`, 46 rows, 2015Q1–2026Q2)
All money is EUR million. The values are parsed from the "Financial highlights" table, the "Bookings" table and the "Outlook" section of each release.

**Orders, book-to-bill and backlog**
- `orders` is ASM's "new orders" (bookings) as reported, including FX and acquisitions.
- **2019 settlement effects:**
  - 2019Q2 includes €103m from the patent settlement; excluding it, orders were €270m and sales €260m.
  - 2019Q4 includes €56m from the arbitration settlement; excluding it, orders were €373m and sales €345m.
  - Both are recorded in `extra_json`.
- **Book-to-bill:** taken as stated in the release. Where a release did not state it, it is computed as orders / revenue and flagged in `extra_json`.
- **Backlog:** the end-of-quarter value from the bookings table.
- **ASM stopped disclosing quarterly bookings and backlog from Q1 2026.** Its Q4 2025 release says backlog will be reported only at year-end. So `orders`, `book_to_bill` and `backlog` are blank for 2026Q1 and 2026Q2. That is a disclosure change, not a gap in collection.

**Gross margin**
- Reported (IFRS) gross margin.
- 2022Q4–2023Q4 releases headline a "normalized" margin (excluding the effects of the LPE acquisition). For 2023Q1–2023Q4 the reported margin was taken from the comparison column of the following year's release (flagged in `extra_json`). 2022Q4's own release shows the reported margin (46.4%).

**Guidance**
- `guidance_rev_low` and `guidance_rev_high` are next-quarter revenue ranges in EUR. The way ASM states guidance changed over time:

| Release | How guidance was given | What the columns hold |
|---|---|---|
| 2015Q1 → 2024Q4 | Explicit € ranges | The range as stated |
| 2025Q1 | Growth rate only: Q2 2025 +1% to +6% quarter on quarter (constant currency); FY2025 +10–20% | EUR columns blank; percentages in `extra_json` |
| 2025Q2 | Growth rate only: Q3 2025 0% to −5% quarter on quarter (constant currency) | EUR columns blank; percentages in `extra_json` |
| 2025Q3 | € range again: €630–660m | The range as stated |
| 2025Q4 → 2026Q2 | Midpoint ± a stated % (€830m ±4%; €980m ±5%; €1,100m ±5%) | Low and high derived arithmetically from midpoint and %, flagged |

- Order guidance (pre-2023) and € billion multi-year targets are in `extra_json`.

**Other fields**
- `revenue_yoy_pct` and `orders_yoy_pct` are computed from the comparison columns of the same release (as reported, not at constant currency).
- `ai_dc_notes` comes from two sources:
  - 2022Q1–2026Q2: written by hand from the release text (`src/ir_agents/semicap/asm_kpi_overrides.json`).
  - 2015–2021: sentences extracted automatically by keyword, tagged [AI], [GAA], [HBM], [China], [AdvPkg] and [Memory]. These are noisy; some [China] hits come from ASMPT segment boilerplate.

## Demand narrative 2023–2026
- **2022 context:**
  - 2022-10-25: Q3 bookings and backlog were reduced to remove China orders hit by the October 7 US export rules.
  - 2022-11-28: the China hit was cut to 15–25% of China sales and Q4 guidance was raised to €630–660m.
- **2023-01-17 (prelim):** Q4 2022 revenue was about €720m, beating the €630–660m guidance as supply chains improved. Orders were about €820m, helped by exceptional power/analog (LPE silicon carbide) intake.
- **2023-04-25:**
  - Q1 2023 orders were €647m, down 6% year on year at constant currency, and softened toward quarter-end.
  - Memory demand was weak.
  - There were push-outs in leading-edge logic/foundry ("softer end-market conditions and some delays in new customer fab readiness"), which ASM flagged would hit Q2 and Q3 orders.
- **2023-07-25:** order trough. Q2 2023 orders were €486m (−48% year on year, book-to-bill 0.7), reflecting push-outs and backlog normalising.
- **2023-09-26 (Investor Day):**
  - The 2025 revenue target was raised to €3.0–3.6bn from €2.8–3.4bn.
  - A new 2027 target of €4.0–5.0bn was set.
  - On 2023-10-24, ASM said the first meaningful GAA orders, expected in Q4 2023, were partly booked in Q3 already.
- **2024-02-27:** Q4 2023 bookings were €678m, "slightly better than expected", driven by GAA pilot-line orders and continued strength in China.
- **2024-04-23 and 2024-07-23:** the GAA and HBM inflection.
  - Q1 2024 orders were €698m (+10% at constant currency), driven by GAA 2nm orders and a strong rise in HBM-related DRAM orders.
  - Q2 2024 orders were €755m (+56% at constant currency), "mainly driven by strong demand for GAA and HBM".
- **2024-10-29:** headline "AI-related demand drives robust growth in bookings and revenue".
  - Q3 2024 orders were €815m (+30%).
  - FY2025 revenue was guided to €3.2–3.6bn.
  - China sales were expected to fall in H2 2024 and again in H1 2025.
- **2024-12-04:** new US export controls were judged "largely in line with previous assumptions". Q4 2024 guidance (€770–810m) and the 2025 range of €3.2–3.6bn were reiterated.
- **2025-02-25:** Q4 2024 orders were €731m (+8%). GAA orders rose strongly from Q3 to Q4, but a drop in China demand offset them.
- **2025-04-29:**
  - Q1 2025 orders were €834m (+14% at constant currency), driven by GAA 2nm, HBM DRAM and solid China demand.
  - Amid tariff uncertainty, ASM switched to growth-rate guidance: FY2025 +10–20% at constant currency, "reasonable visibility" on the low end.
- **2025-07-22:**
  - Q2 2025 orders were €703m (−4% at constant currency) because of the timing of advanced logic/foundry orders.
  - H2 2025 revenue was guided at about the same level as H1, and Q3 at 0% to −5% quarter on quarter.
- **2025-09-23 (Investor Day and profit warning):**
  - Q4 2025 revenue was guided below earlier expectations on lower-than-expected leading-edge logic/foundry demand.
  - A 2030 target of more than €5.7bn was set.
  - The 2027 target was adjusted for currency to €3.7–4.6bn.
- **2025-10-28:**
  - Q3 2025 orders were €637m (−17% at constant currency) after strong China orders in H1 faded.
  - Advanced logic/foundry orders rose quarter on quarter, but less than first expected.
  - Q4 was guided at €630–660m.
- **2026-01-19 (prelim):**
  - Q4 2025 bookings were about €800m, against an indication of slightly above €637m. Revenue was €698m, above the €630–660m guide.
  - The beat came from a quarter-end rebound in China plus solid advanced logic/foundry orders.
  - The final figure on 2026-03-03 was €803m.
- **2026-04-21 and 2026-07-28:**
  - "AI-led demand accelerated further."
  - Q2 2026 revenue was a record €1,003m.
  - Q3 2026 is guided at €1,100m ±5%, with H2 more than 20% above H1.
  - Citing strong H1 2026 order intake, ASM now expects 2027 revenue to exceed the top of the €3.7–4.6bn range.
  - Quarterly order figures are no longer disclosed.

## Gaps
- 2026Q3 has not been released yet (due 2026-10-27).
- There are no transcripts, because ASM does not publish them.
- Orders and backlog are not disclosed from 2026Q1.
- 2025Q1 and 2025Q2 guidance was growth-rate only, so the EUR range columns are blank for those quarters.
- The 2023Q3 deck is a truncated Wayback copy.
