# AI Supply-Chain Lead-Lag

How the listed companies in NVIDIA's "five-layer cake" (energy → chips → infrastructure / AI factories → models → applications) move when one of them reports earnings, what their filings and calls say about demand, and which of those patterns survive a proper backtest.

The study started from Jensen Huang's GTC Berlin keynote (21 Oct 2026) and its "Building Europe's AI Economy" slide, then widened to the global listed supply chain: **96 companies** (61 US, 24 Europe, 11 Asian reference names), **300 supply / partner links**, **4,131 earnings releases** with exact release times, **1,212 call transcripts**, **4,071 SEC documents**, **2,154 European investor-relations documents**, **454 NVIDIA keynote documents** from 32 keynotes, TSMC monthly sales and daily prices from June 2014 to 22 Oct 2026.

- **Report:** `reports/ai_supply_chain_lead_lag.html` (self-contained page; open it in a browser).
- **Handoff for agents:** [`AGENTS.md`](AGENTS.md).
- **Chronological work log:** [`PROGRESS.md`](PROGRESS.md).

## Findings (run of 23 Oct 2026)

| Status | Finding | Evidence |
|---|---|---|
| Holds up | Peers and suppliers move together on release day | Same-layer peers move 0.062% per 1% of the reporter's move (t = 9.9); suppliers move 0.061% on a customer's report (t = 5.5), three times the pre-2023 0.020%. Layer betas fitted through 2024 held in 2025–26 (slope 0.73, t = 5.3). |
| Holds up | Hyperscaler capex reaches suppliers in a fixed order | Chip revenue (NVIDIA, AMD, Broadcom) accelerates about a quarter before capex does; optics, network silicon, power and cooling follow 2–3 quarters after it (Vertiv +2Q ρ 0.63, Fabrinet +2Q ρ 0.66, Marvell +3Q ρ 0.60, Arista +3Q, Ciena +3Q). |
| Mixed | Orders lead revenue | Order acceleration shows up in own revenue growth two quarters later (t = 2.3, best of five lags); group order indices lead US group revenue by 0–3 quarters. |
| Mixed | Earnings surprises cascade, prices barely do | Peers' EPS surprises predicted a later reporter's surprise before 2023 (t = 4.9), weaker since (t = 1.2–1.3); peers' price reactions predict a later reporter's own reaction only faintly (t = 1.8). |
| Not supported | Drift along supply links after a report | Suppliers after a big customer report: +63 bp/trade vs S&P 500 but +3 bp vs an AI-stock basket (t = 0.1). Dollar-neutral customer momentum: Sharpe 0.24 (t = 0.8), 2016–2026. |
| Not supported | Trading on order surprises after the release | Priced on the day (reporter t = 2.3, peers t = 2.4), no follow-through over 20 days (t = −0.1). |
| Not supported | TSMC monthly sales, keynote mentions | TSMC monthly surprises don't predict AI-chip returns (all \|t\| < 1.5). Stocks named in NVIDIA keynotes moved +0.3% on the day (t = 0.8, 21 timed keynotes). |

The combined walk-forward model (all features, dollar-neutral, 5-day horizon) has a real but tiny signal: rank IC 0.015 (t = 3.9), gross Sharpe 0.49, net Sharpe 0.03 after costs, break-even cost about 12 bp per trade one way. **The useful output is a map, not a trading signal**: same-day hedge ratios around each report, and a capex/orders-driven revenue nowcast. See [`docs/findings.md`](docs/findings.md) and [`docs/trading_desk_plan.md`](docs/trading_desk_plan.md).

## Repository layout

```
config/            universe.csv (companies, layers), edges.csv (links), edges_v1.csv (pre-merge), private_companies.csv (Berlin slide)
src/               pipeline scripts (fetch → process → analyze → report); see AGENTS.md for the DAG
src/ir_agents/     one-off collectors that built the European IR calendars / KPIs (data/processed/ir)
src/keynotes/      one-off collectors that built the NVIDIA keynote corpus (data/processed/keynotes)
data/processed/    derived datasets (small ones in git; large / third-party text local only)
data/raw/          raw downloads (local only, untrusted, 5.7 GB)
reports/           report HTML, template, report_data.json, tables/*.csv (every number in the report)
docs/              methodology, findings, data sources, next steps, desk plan; docs/generated/* is rebuilt from data
run_all.sh         rebuild every analysis + report + generated docs from local data (~4 minutes, no network)
```

## Quickstart

```bash
uv venv .venv --python 3.11 && uv pip install --python .venv/bin/python -r requirements.txt
./run_all.sh                       # needs the local data files (see data policy)
open reports/ai_supply_chain_lead_lag.html
```

Run Python as `.venv/bin/python -I src/<script>.py` (isolated mode, see AGENTS.md). Rebuilding from an empty `data/` folder means running the fetch scripts first; the order is in [`docs/data_sources.md`](docs/data_sources.md).

## Data policy

In git: code, config, docs, report, every result table, and the small derived datasets (events, filings index, XBRL fundamentals, TSMC monthly, orders panel, European IR calendars / KPIs / notes, US call notes and demand signals, keynote metadata and mentions).

Local only (in `.gitignore`), rebuilt by scripts: `data/raw/` (5.7 GB of raw downloads), full-text transcripts, SEC and IR document text, call digests and keynote texts (third-party copyrighted text), price files and daily panels, and the large intermediate panels (`spill.parquet`, `network_features.parquet`). Motley Fool rate-limits transcript downloads (HTTP 429), so the transcript corpus is slow to rebuild.

## Documents

- [`docs/methodology.md`](docs/methodology.md): event timing, abnormal returns, every test and backtest design
- [`docs/findings.md`](docs/findings.md): results with numbers, rejected hypotheses, caveats
- [`docs/supply_chain_map.md`](docs/supply_chain_map.md): the five layers, the Berlin slide, links, the 2022–2026 demand timeline
- [`docs/data_sources.md`](docs/data_sources.md): every source, the script that fetches it, coverage and known gaps
- [`docs/trading_desk_plan.md`](docs/trading_desk_plan.md): how to turn this into an automated desk and what to expect
- [`docs/next_steps.md`](docs/next_steps.md): prioritized research backlog with acceptance criteria
- [`docs/generated/`](docs/generated): data dictionary, universe, links, private companies, result tables (generated)
