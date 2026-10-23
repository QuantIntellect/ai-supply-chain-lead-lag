# Methodology

Definitions used everywhere in the code. Keep them consistent in new work.

## 1. Universe and layers

`config/universe.csv` holds 96 companies. Layers (column `layer`), ordered roughly upstream to downstream:

| layer | meaning | five-layer cake |
|---|---|---|
| SEMICAP | chip equipment and components (ASML, AMAT, LRCX, KLAC, ASM, BESI, VAT, Aixtron, SUSS, Soitec, TEL, Advantest, Teradyne) | Chips |
| FOUNDRY_MEM | foundry and memory / storage (TSMC, Micron, SK Hynix, Samsung, WDC, STX, SanDisk) | Chips |
| CHIPS | GPUs, ASICs, CPUs, connectivity, power ICs (NVIDIA, AMD, Broadcom, Marvell, Intel, Arm, Infineon, STM…) | Chips |
| NETWORK | switching and optics (Arista, Cisco, Ciena, Coherent, Lumentum, Fabrinet, Nokia) | Infrastructure |
| SYSTEMS | servers / ODMs / EMS (Dell, HPE, Super Micro, Celestica, Jabil, Foxconn, Quanta, Wistron, Wiwynn) | Infrastructure |
| ENERGY | generation, grid equipment, cables (GE Vernova, Constellation, Vistra, Siemens Energy, Rolls-Royce, Prysmian…) | Energy |
| DCINFRA | data-center power and cooling, electrification (Vertiv, Eaton, Schneider, Siemens, ABB, Legrand…) | Energy (as on the Berlin slide) |
| AIFACTORY | neoclouds, data-center developers / REITs, Deutsche Telekom (CoreWeave, Nebius, IREN, Equinix…) | Infrastructure |
| HYPERSCALER | Microsoft, Alphabet, Amazon, Meta, Oracle | Infrastructure |
| APPS | software / services (SAP, Dassault, Capgemini, Palantir, ServiceNow, Salesforce, Adobe, Snowflake) | Applications |

Asian names (`tradeable = 0`) act as reporters and references but are excluded from trading tests. `history_start` removes price history that belongs to a SPAC shell, tracking stock or unrelated predecessor.

## 2. Events: release times and reaction sessions

`src/events.py` builds one row per earnings release (`events.parquet`), choosing the time stamp source in this priority:

1. **European IR calendars** (`data/processed/ir/<T>_events.csv`), collected per company from regulatory announcement stamps (RNS, EQS, AMF, SDIR, GlobeNewswire, Nasdaq Nordic). A missing clock time becomes 07:00 local for "BMO" and 18:00 for "AMC".
2. **SEC 8-K item 2.02** filings, using the authoritative ET "Accepted" stamp from the filing index page. Multiple 2.02 filings within 3 days collapse to the first.
3. **Yahoo earnings dates**, only where neither exists, snapped to the highest abnormal-volume session within ±2 sessions and assigned an exchange-typical release time (`default_release_ts`).

For any stock B and release time τ, the **reaction session** is the first session on B's own exchange whose close is after τ (`Calendar.reaction_day`). If τ falls inside B's session, the reaction is "partial" and spans that session and the next. Exchange hours are in `panel.EXCHANGES`.

## 3. Returns

- `ret`: close-to-close adjusted return per ticker on its own trading calendar.
- `abret` (**market-model abnormal return**): r − β·r_index, where the index is SPY (US), STOXX 600 (Europe), TAIEX, KOSPI or Nikkei, and β is a 250-day rolling beta lagged 21 days, clipped to [0, 3].
- `abret_ind` (**AI-basket abnormal return**): the same, with the equal-weight return of the region's tradeable universe as the benchmark. Use it to separate information from AI-sector exposure.
- `abvol`: volume / trailing 60-day median volume (used to validate event dates).

## 4. Spillover panel (`spill.py` → `spill.parquet`)

One row per (reporter event A, responder B):

- `arA`: reporter's abnormal return on its own reaction session (winsorised at 1/99% in the regressions).
- `ar0`: B's abnormal return on its reaction session (two sessions if partial).
- `entry_date`: B's first close at or after the close of A's reaction session. All drift windows start here, so no foreign price is used before A's move is knowable.
- `car_1_k`: B's cumulative abnormal return over k sessions after `entry_date` (k = 1, 2, 5, 10, 20, 40).
- `rel`: `A_supplies_B`, `B_supplies_A` (from supply edges, partner/investment links excluded), `same_layer`, or `other`.
- Contamination: `own_near` (B reported within ±1 day) rows are dropped everywhere; `own_in_30` (B reports within 30 days after) rows are dropped from drift tests.

## 5. Tests

| Test | Specification | Script |
|---|---|---|
| Sympathy map | ar0 = a + b·arA by layer pair and by relation; SEs clustered by reporter reaction date | `analyze_spill.py` |
| H1 stability | fit pair / layer / shrunk betas on ≤ 2024, predict 2025–26 ar0; slope, correlation, sign hit rate | `pair_map.py` |
| Drift | car_1_k = a + g·arA (+ c·ar0), by relation and region pair | `analyze_spill.py`, `customer_momentum.py` |
| Cascade | B's own release AR and EPS-surprise sign on prior-60-day peer features (edge / layer / up / downstream reporters' AR and surprises, B's sympathy CAR, pre-event CAR, last own AR); SEs clustered by week | `cascade.py` |
| Capex lead-lag | corr(Δ hyperscaler capex YoY at t, Δ supplier revenue YoY at t+k), k = −2…4, 2015–2026; level correlations kept only as a common-trend caveat | `fundamentals_leadlag.py` |
| Nowcast | per supplier with peak lead k ≥ 1 and corr ≥ 0.3: OLS of Δrevenue growth on Δcapex growth k quarters earlier; prediction for the next k quarters with residual SD | `fundamentals_leadlag.py` |
| Orders pace | (A) Δorders YoY → own Δrevenue YoY at t+k, pooled within-company z-scores; (B) group orders index → US group revenue; (C) orders acceleration → own release AR, peers' same-day AR beyond reporter AR, peers' 20-day CAR vs AI basket, later US reporters' AR | `orders_panel.py` |
| TSMC monthly (H5) | monthly revenue YoY acceleration and seasonal MoM surprise → AI-chip basket AR same day and next 5 / 20 sessions; HAC SEs | `fundamentals_leadlag.py` |
| Keynote mentions | named vs not-named tradeable stocks: AR on the keynote reaction session and next 5 sessions, vs index and vs AI basket; clustered by keynote | `keynote_effect.py` |
| Text features | mentions per 10k spoken words for AI, data center, constraint, orders, digestion lexicons; tone = (pos − neg)/(pos + neg) | `transcripts_nlp.py` |

## 6. Backtests

**Event strategies** (`backtest_events.py`): trade responder B at `entry_date` close in direction ±sign(arA), hold k sessions, P&L = abnormal return (vs index, and separately vs AI basket) minus round-trip cost (20 bp US, 30 bp EU, 40 bp Asia). The |arA| threshold θ is chosen on 2015–2024 (best mean net, ≥ 200 trades) and held fixed for 2025–26. Each trade uses 1/20 of the book (fixed fraction), so the daily series and its Sharpe reflect a real book with varying exposure. Per-trade t-stats are clustered by reporter date.

**Combined model** (`network_model.py`): daily features per stock = sums of recent release reactions of its customers, suppliers, same-layer and other companies in age buckets (0, 1–4, 5–19 sessions), its own last reactions (1–4, 5–19, 20–59) and its own AR over 1 / 5 / 20 days. Target: next 5-session AR. Walk-forward OLS refit each year on the previous 4 years (2019–2026 out of sample). Book: weights ∝ prediction, demeaned across live names (dollar-neutral), gross 1, 1/5 rebalanced daily, costs 10 bp (US) / 15 bp (EU) per unit turnover.

**Customer momentum** (`customer_momentum.py`): fixed rule, signal = sum of customers' release reactions over the last 20 sessions. Six variants: net-long vs dollar-neutral, vs index vs vs AI basket, and a baseline that holds every name with any customer news.

## 7. Costs, inference and hold-out

- Hold-out: fit through 2024, test 2025-01-01 to 2026-10-22.
- About 60 regression specifications were run. With that many, three or four will clear |t| > 2 by chance; conclusions rest on effects that hold in both periods or under both benchmarks.
- Hypotheses were written down after the first pooled regressions, so they are "primary", not formally pre-registered.
