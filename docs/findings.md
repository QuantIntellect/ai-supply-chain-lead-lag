# Findings

Numbers are from the run of 23 Oct 2026 (prices through 22 Oct 2026). Full tables: `docs/generated/results.md` and `reports/tables/*.csv`. Definitions: `docs/methodology.md`.

## 1. Same-day co-movement (holds up)

| Relation (reporter → responder) | β since 2023 (t) | β 2015–2022 (t) |
|---|---|---|
| Same layer | 0.062 (9.9) | 0.051 (11.9) |
| Customer reports → its suppliers | 0.061 (5.5) | 0.020 (2.9) |
| Supplier reports → its customers | 0.026 (4.3) | 0.016 (3.6) |
| Unrelated | 0.011 (3.8) | 0.008 (4.8) |

β is the responder's market-adjusted move per 1% market-adjusted move of the reporter on the reporter's reaction session. Customer news now travels up the chain three times more strongly than before 2023. Strongest layer pairs since 2023: foundry & memory → foundry & memory (0.10), AI factories → AI factories (0.09), foundry & memory → chip equipment (0.08), networking → networking (0.08).

Out of sample (fit ≤ 2024, test 2025–26): layer betas predicted responder moves with slope 0.73 (t = 5.3) but correlation only 0.065. Raw pair betas overfit (slope 0.17); shrinking pairs toward their layer (weight n/(n+20)) gives slope 0.47 (t = 6.3). **Use: hedge ratios and exposure sizing around reports, not forecasts.**

Tightest pairs (2015–2026, ≥ 20 releases, by lower 95% bound of the correlation): Lam → Applied Materials (ρ 0.90, β 0.51), Lam → KLA (0.88), STMicro → Infineon (0.85), Dell → HPE (0.86), ASML → ASM International (0.81), ABB → Schneider (0.80), Seagate → WDC (0.81), ASML → BESI (0.77). Forward list for the coming reports: `reports/tables/playbook.csv`.

## 2. Demand cascade in fundamentals (holds up, in sample)

Hyperscaler cash capex (MSFT, GOOGL, AMZN, META, ORCL): $44bn in 2023 Q4 → $182bn in 2026 Q2. Guidance for 2026: Alphabet $180–190bn, Amazon ≈ $220bn, Meta $135–145bn, Microsoft ≈ $175bn (calendar year); Oracle $90–95bn for fiscal 2027; Alphabet says 2027 will be "significantly" higher (quotes in `data/processed/us_notes/hyperscaler_capex_guidance.csv`).

Correlation of quarter-on-quarter changes in YoY growth (capex at t vs supplier revenue at t+k), 2015–2026, peak lead per supplier:

| Lead | Suppliers (peak corr) |
|---|---|
| Supplier leads capex by 1–2Q | LITE 0.58, AMAT 0.29, COHR 0.28, SMCI 0.26, NVDA 0.25, AMD 0.24, AVGO 0.24, MU 0.16, WDC 0.16 |
| Same quarter | TSMC 0.55, ETN 0.35, DELL 0.32, STX 0.30 |
| Capex leads by 1Q | LRCX 0.33, KLAC 0.32 |
| Capex leads by 2Q | FN 0.66, VRT 0.63, MPWR 0.37, CSCO 0.24 |
| Capex leads by 3–4Q | MRVL 0.60, ANET 0.36, CIEN 0.34, PWR 0.22, CRDO 0.46 (+4Q) |

Level correlations are 0.5–0.7 at almost every lead because everything trended up together; only the change-based ordering is evidence. These are in-sample fits on 20–40 quarters.

**Nowcast** (`reports/tables/capex_nowcast.csv`): capex growth jumped +19.6 points in 2026 Q1 and eased (−4.3) in Q2, which implies, for example, Vertiv revenue growth +7.5 pt in 2026 Q3 (residual SD 6.5 pt; last reported growth 24%), Fabrinet +3.9 pt, Monolithic Power +4.9 pt in Q3, and Marvell +14 pt, Ciena +4.0 pt, Arista +3.4 pt in Q4. Whether this beats analyst consensus is untested (no consensus data yet).

## 3. Orders pace (mixed)

- Own lead: Δ order growth → own Δ revenue growth two quarters later, pooled correlation 0.19 (t = 2.3, 11 companies); other lags are weaker, so suggestive.
- Chain lead: European electrification orders index (ABB, Siemens, Siemens Energy, Munters, Vertiv) vs US data-center infrastructure revenue: change correlations 0.33 at 0Q and 0.39 at +3Q. Semicap orders (ASML, ASM, BESI, VAT, Aixtron) vs US semicap revenue: 0.25–0.46 at 0–2Q. Short samples.
- Prices: order acceleration moves the reporter on release day (+0.025% per point, t = 2.3) and its peers beyond the reporter's own move (t = 2.4; 1.8 since 2023), then nothing over 20 days vs the AI basket (t = −0.1). Earlier European order surprises don't predict the later US reporters' reactions (t = 0.6).
- Latest readings (Q3 2026 unless noted): ABB orders +40% (book-to-bill 1.24), Siemens fiscal Q3 +13% (1.34), Siemens Energy fiscal Q3 +8% (1.57), VAT +193% (1.90), Aixtron +122%, BESI +96% (1.21), Munters Q2 +137%, Nokia AI & cloud orders +118%, Schneider data-center demand up triple digits in Q2 and Q3.

## 4. Earnings cascade (mixed)

- Same-layer peers' EPS surprises earlier in the season predict the sign of a later reporter's surprise: t = 4.9 in 2015–2022, t = 1.2 since 2023 (magnitude t = 2.4 / 1.3).
- Peers' release-day reactions predict the later reporter's own release-day reaction only faintly since 2023 (t = 1.8, R² < 1%).
- The responder's own sympathy moves on peers' release days do **not** reverse at its own release (H4 rejected; the coefficient is positive).

## 5. What a backtest keeps (not supported)

| Strategy | vs S&P / local index | vs AI basket |
|---|---|---|
| Customer reports (|AR| ≥ 6%) → suppliers, 20 days | +63 bp/trade (t 1.6) fit; +70 bp (t 0.9) hold-out | +3 bp (t 0.1) fit; +4 bp (t 0.1) hold-out |
| Supplier reports → customers, 2 days | −9 bp (t −1.2) | −20 bp (t −3.1) |
| Either direction, 5 days | −20 bp (t −1.6) | −34 bp (t −5.9) |
| Fade same-layer peers, 5 / 20 days | −17 / −19 bp | −18 / −7 bp |

Customer-news momentum (20-day hold, Sharpe after costs, 2016–2026): net long vs index 0.45; dollar-neutral vs AI basket 0.24 (t = 0.8; 2016–22 0.18, 2023–24 −0.62, 2025–26 1.22 with t = 1.65). Holding every name with any customer news: Sharpe 0.96 vs index but −0.04 vs AI basket. The apparent edge was AI-sector exposure.

Combined walk-forward model (dollar-neutral, 5-day horizon, 2019–2026): rank IC 0.015 (t = 3.9); gross 6.0%/yr at 12.3% vol (Sharpe 0.49); net 0.3%/yr (Sharpe 0.03), max drawdown −28%, turnover 19.5%/day, break-even cost ≈ 12 bp one way. By period: net Sharpe 0.42 (2019–22), −0.35 (2023–24), −0.21 (2025–26).

## 6. Other rejected hypotheses

- **TSMC monthly sales (H5):** acceleration or seasonal surprise doesn't predict AI-chip basket returns (all |t| < 1.5, 2015–2026).
- **Keynote mentions:** stocks named in NVIDIA keynote press kits moved +0.30% vs unnamed stocks on the day (t = 0.8; 21 of 32 keynotes have an exact start time); partnership/investment mentions +0.7% (t = 1.6); no follow-through.
- **Intraday continuation** (US after-close report → European/Asian open-to-close): positive (Europe same-layer t = 2.5, Asia linked t = 2.6 since 2023) but measured with US pre-market prices unknown at the European/Asian open, so diagnostic only. A proper test needs after-hours prices (see `docs/next_steps.md`).
- **Hyperscaler capex acceleration → layer baskets:** chips basket +20-day drift t = 2.4 since 2023, other layers |t| < 2; exploratory, one of many layers tested.

## 7. Language on the calls

Mentions per 10,000 spoken words, averaged across all calls: AI 7 (2022) → 58 (2024) → 51 (2026); data center 11 (2022) → 28 (2026); supply-constraint words 3 (2024) → 6 (2026); digestion / push-out words 7 (2022) → 2 (2026). The 2,511 dated demand statements logged by the reading passes (`us_notes/demand_signals_*.csv`) show the 2022–23 slump moving from consumer chips to cloud and then the 2025–26 shortage phase (timeline in `docs/supply_chain_map.md`).

## 8. Caveats

- Survivorship: the universe is today's AI winners; relative tests are less affected.
- Transcript gaps (Motley Fool coverage and rate limits): e.g. NVIDIA Feb 2024 and May–Aug 2025, Meta 2023, Micron 2021–23, Oracle Q1 FY26, Alphabet Q2 2026.
- 27 links are "industry knowledge" (unverified) and 58 customer links were added from call mentions (many single mentions); partner/investment links are excluded from supply tests.
- EPS surprises are from Yahoo; revenue and guidance consensus are not available.
- Some European calendars lack clock times for older years (Infineon 2015–2021, SUSS before mid-2020, Siemens Energy regular releases); those default to 07:00 local.
- The 2025–26 hold-out is under two years.
