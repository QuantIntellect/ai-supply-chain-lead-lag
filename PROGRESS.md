# AI supply-chain lead-lag project — progress log

Goal (user): map the AI supply chain (NVIDIA "five-layer cake": Energy → Chips → Infrastructure/AI factories → Models → Applications),
collect every company's reports / calls, find demand and order patterns between companies, measure how each stock moves after
other companies report, and backtest whether that predicts prices (financial model).

## Layout
- `config/universe.csv` – 100 tickers (US, EU, Asia signal-only), layer, Berlin-slide flag
- `config/edges.csv` – supplier→customer / partner / investor edges with evidence + confidence (many "industry knowledge", to verify)
- `config/private_companies.csv` – (keynote agent) private companies on the GTC Berlin slide
- `src/` – all code (run with `.venv/bin/python -I src/<script>.py`)
  - `fetch_prices.py` → `data/processed/prices/prices_long.parquet` (yfinance daily OHLCV 2014-06 → 2026-10-22)
  - `panel.py` → `data/processed/panel/*.parquet` (ret, overnight, intraday, market-model abret, beta, abvol)
  - `fetch_edgar.py` → `edgar_filings.parquet`; `edgar_index.py 8k|6k` → accepted ET times + exhibit tables
    (NB: submissions-JSON acceptanceDateTime is unreliable; index-page "Accepted" is authoritative)
  - `fetch_earnings_dates.py` → `yahoo_earnings_dates.parquet` (dates + EPS est/actual/surprise)
  - `events.py` → `events.parquet` (priority: IR agent calendars > EDGAR 8-K 2.02 > Yahoo validated by abnormal volume)
  - `fetch_xbrl.py` → `fundamentals_q.parquet` (revenue, capex, RPO, inventory … quarterly, US-GAAP filers)
  - `fetch_fool.py` → `data/processed/transcripts/<T>/*.txt` (Motley Fool call transcripts; 1,212 matched URLs)
  - `spill.py` → `spill.parquet` (responder × reporter-event panel, cross-time-zone reaction sessions)
  - `analyze_spill.py` → `reports/tables/spill_*.csv`
- Background agents write: `data/processed/ir/<T>_{events,kpis,manifest}.csv`, `<T>_notes.md` (24 EU names, 5 agents);
  `data/processed/keynotes/*` + `config/private_companies.csv` (keynote agent)

## Pending merges
- When IR agents finish: rerun `events.py` → `spill.py` → `analyze_spill.py` (events.py already reads ir/*_events.csv)
- 6-K index crawl (`edgar_index.py 6k`) → foreign filers' exhibits (TSMC monthly revenue etc.)

## Known gaps / caveats
- No event dates yet for RR.L, NEX.PA, SU.PA, SOI.PA, VACN.SW, CAP.PA (await IR agents)
- YouTube transcript of the keynote blocked (bot check) → keynote record = NVIDIA blogs/press kits
- COHR pre-2022-07 history is II-VI; WULF pre-2021 is IKONICS → AI-era analysis only for those
- US BMO releases fall mid-session for EU responders (partial sessions) → use CAR[t0,t0+1] or drop

## Pre-registered hypotheses (fit ≤ 2024-12-31, test out-of-sample 2025-01-01 → 2026-10-22)
- H1 Sympathy-map stability: pair betas (AR_B on A's release day ~ AR_A) estimated ≤2024 predict 2025-26 sympathy moves (OOS corr > 0).
- H2 Supply-chain drift: after a customer's release, its suppliers' CAR[+1,+20] has the sign of the customer's AR (controlling for supplier day-0 move);
     after a supplier's release, customers' CAR[+1,+2] has the sign of the supplier's AR. Tradeable net of ~20 bp round trip?
- H3 Cascade (fundamentals): a late announcer's EPS-surprise sign is positively predicted by earlier same-season reactions/surprises of its edge-linked and same-layer companies.
- H4 Cascade (prices): a late announcer's own release-day AR is negatively related to the sympathy CAR it accumulated on peers' release days (already priced in).
- H5 Nowcast: TSMC monthly revenue YoY acceleration predicts AI-chip basket returns over the next 20 sessions and NVDA's next-quarter revenue growth.

## Results so far (2026-10-23)
- Event calendar: 3,735 events / 92 tickers; EDGAR events median abnormal volume 2.8x (timing verified).
- Pooled AI-era (2023+) sympathy betas small (0.02–0.10); same-layer 0.063 (t=10), customer→supplier 0.075 (t=5.9, vs 0.029 pre-2023).
- Drift: supplier-news → customer CAR[+1,+2] g=0.03 (t=2.8); customer-news → supplier CAR[+1,+20] g=0.10 (t=2.2, ctrl own day-0);
  same-layer peers reverse over 5–20d in AI era (pre-AI: continuation). Generic day-0 reversal exists in "other" too (not supply-chain-specific).

## Results (cont.)
- Look-ahead fix: cross-time-zone drift now starts at first responder close after reporter's reaction close (entry_lag, entry_date in spill).
- Robust after fix: US reporter -> Asian edge partners drift CAR[+1,+20] g=0.16 (AI t=2.2; pre t=3.8). US same-layer peers reverse in AI era (k5 -0.044 t=-2.2; k20 -0.084 t=-2.5).
- Cascade (cascade.py): peers' EPS surprises predict B's surprise (pre t=3.0/4.8; AI weak); symp_car POSITIVE (not reversal) -> H4 rejected; pre_car & last_ar predict surprise sign.
- H1: layer betas calibrate OOS (slope 0.87, t=5.7) but explain little overall (corr 0.07); raw pair betas overfit (slope 0.22) -> shrink.
- Fundamentals: hyperscaler cash capex 44bn (23Q4) -> 181bn (26Q2). capex YoY leads supplier revenue YoY: optics/network 2-3Q (CIEN .68@3, LITE .69@2, MRVL .65@3, CRDO .67@2, CSCO .60@3),
  power/cooling 2-4Q (VRT .57@2, ETN .33@2, PWR .40@4, FN .43@4); chips/memory coincident or leading (NVDA leads capex by ~2Q).
- H5 rejected: TSMC monthly revenue surprises don't predict AI-chip basket returns (|t|<1.5 all specs).
- Event backtests (backtest_events.py): H2a customer-news->suppliers 20d theta=6%: +74bp/trade net train (t=1.45), +109bp OOS 2025-26 (t=1.04) -> right sign, not significant.
  H2b supplier-news->customers 2d: fails. Same-layer reversal: inconsistent.
- Daily network model (network_model.py, walk-forward 4y window): full-model IC 0.013 (t=3.2, 2019-26) but net Sharpe ~0 at 5d rebalancing (turnover 20%/day).
  Stable coefficient: customer-news features positive every year. Fixed customer-momentum signal, 20d hold: net Sharpe 0.08 (2016-22), 0.65 (2023-24), 1.05 (2025-26), all 0.38 (t=1.3).

## State at ~02:40 (2026-10-23)
- Done agents: EU electrical (SU.PA, SIE.DE, ABBN.SW, LR.PA, MTRS.ST). Running: EU semicap, EU chips/Nokia, EU energy, EU software, keynotes, US digest readers (semis; cloud/power/apps)
- New: tsmc_monthly.csv (153 months), transcript_features.parquet + capex_statements.csv (transcripts_nlp.py),
  digests/<T>.md (digests.py), press_release_kpis.csv (press_release_kpis.py), customer_concentration.py (run after docs)
- Background: fetch_fool.py (older transcripts), fetch_edgar_docs.py (4,075 EDGAR docs: 8-K EX-99, 6-K exhibits, 10-K/20-F)
- Exploratory capex_signal.py: AI-era hyperscaler capex acceleration -> CHIPS basket CAR[+1,+20] t=2.4 (others ~1.6)
- Report: plain HTML research page (not Dashboard type: narrative with many inline numbers). Build src/report_data.py -> JSON -> HTML.
- FINAL RERUN ORDER once agents finish: events.py -> spill.py -> analyze_spill.py -> pair_map.py -> cascade.py -> backtest_events.py
  -> network_model.py -> transcripts_nlp.py -> customer_concentration.py -> press_release_kpis.py -> report_data.py
- Edge fix: partner/investment edges excluded from supply relations (spill, cascade). Customer momentum H20 net Sharpe: -0.03 (16-22), 0.61 (23-24), 0.91 (25-26); all 0.28 (t=0.94).
- Intraday continuation (US after-close reporters, signal = reporter overnight gap): EU same-layer b=0.029 (t=2.5 AI; 0.021 t=2.4 pre), EU edge 0.044 (t=1.6);
  Asia edge 0.053 (t=2.6), Asia same-layer 0.049 (t=3.3) AI era; US responders ~0. Caveat: gap includes pre-market info after Asia close (small look-ahead).

## Final state (2026-10-23 ~03:30)
- Advisor review applied: dollar-neutral + AI-basket benchmark variants (customer momentum edge = sector beta), fixed-fraction event sizing,
  history_start cuts (SPAC/predecessors), playbook n>=14 ranked by corr CI low, intraday result relabelled diagnostic-only,
  orders-pace tests (orders_panel.py), first-difference capex lead-lag + nowcast (fundamentals_leadlag.py), keynote_effect.py.
- Edges: merge_relations.py folds 655 call-stated relations (us_notes) into config/edges.csv (151 -> 300; original kept as edges_v1.csv).
- Transcript dates corrected with us_notes/call_date_map_*.csv (196 files), 14 duplicates dropped.
- Report: reports/template.html + reports/report_data.json -> src/build_report.py -> reports/ai_supply_chain_lead_lag.html
- Headline: same-day sympathy map robust & OOS-stable; capex->supplier revenue ordering (chips -1Q, optics/power +2..+3Q);
  orders lead revenue (noisy); no post-print drift alpha after AI-basket adjustment & costs; TSMC monthly and keynote mentions: no effect.

## Repository (2026-10-23)
- Git repo initialised (branch `main`). Docs: README.md (humans), AGENTS.md (agent handoff; CLAUDE.md imports it), docs/*.md,
  docs/generated/* (rebuilt by src/build_docs.py at the end of run_all.sh).
- common.ROOT is now the repo root (override with AIMAPPING_ROOT); run_all.sh runs from its own folder and also rebuilds the report and docs.
- .gitignore keeps raw downloads, third-party full text (transcripts, filings, IR text, digests, keynote text) and large regenerable
  panels out of git. Collector scripts in src/ir_agents and src/keynotes still contain absolute paths of the original machine.
