# The supply-chain map

## Five-layer cake

At GTC Berlin (21 Oct 2026, Tempodrom) Jensen Huang described AI as a five-layer cake: energy powers chips, chips fill AI factories, factories run models, and models power applications. The same framing appeared at Davos in January 2026 ("the largest infrastructure buildout in human history"). The keynote record and NVIDIA's per-layer framing are in `data/processed/keynotes/five_layer_cake.md`.

The "Building Europe's AI Economy" slide placed these companies in each layer:

| Layer | Listed (tracked here) | Private (`config/private_companies.csv`) |
|---|---|---|
| Energy | Schneider Electric (SU.PA), Siemens (SIE.DE), Siemens Energy (ENR.DE), Rolls-Royce (RR.L, via Rolls-Royce SMR) | Rolls-Royce SMR |
| Compute | NVIDIA (NVDA) | |
| AI factories | Deutsche Telekom (DTE.DE), Nebius (NBIS), Nokia (NOKIA.HE) | Bull, Firebird, Mistral AI (compute), Nscale, Radiant (Brookfield), Volta Infra |
| Models | | Aleph Alpha, Advanced Machine Intelligence, Black Forest Labs, Ineffable Intelligence, Mistral AI |
| Applications | | AgileRL, Agile Robots, Wandelbots, Avelios, Basecamp Research, Black Forest Labs, Cursive, DeepL, distil labs, ElevenLabs, Gradium, Helsing, H Company, Humanoid, Inherent, Langdock, Latent Labs, Legora, Lovable, MicroAGI, Multiverse Computing, n8n, NEURA Robotics, Oxa, PhysicsX, Prima Mente, Recursive, Synthesia, Wayve |

Because most of the slide is private, the study extends it to the listed global chain: 96 companies in ten layers (`docs/generated/universe.md`).

## Links

`config/edges.csv` has 300 directed links: hand-built supply links with evidence and confidence (10-K/20-F customer concentration, company statements, keynote announcements, industry knowledge), 58 customer relationships, 85 partnerships and 6 equity stakes stated on earnings calls, plus the hand-built stakes (NVIDIA in Intel and Nokia; SoftBank in Arm). 27 links rest on industry knowledge only. Full list: `docs/generated/edges.md`.

Customer concentration from the latest annual reports (`data/processed/customer_concentration.csv`): NVIDIA's largest direct customer was 22% of fiscal-2026 revenue and the second 14%; Meta and Microsoft were each over 10% of Arista's revenue; Credo's top 10 customers were about 90%; Celestica's top 10 customers were 73% of 2024 revenue and its HPS (hyperscale) segment 41% of 2025 revenue; CoreWeave's committed contracts were 98% of 2025 revenue.

## Demand timeline 2022–2026

From the dated call notes (`data/processed/us_notes/*_notes.md`, `data/processed/ir/*_notes.md`):

| When | What happened |
|---|---|
| Jul 2022 | Downturn starts in consumer chips: TSMC, Seagate, Lam, Intel and KLA cut outlooks between 14 and 28 July. |
| Jul 2022 – Aug 2023 | Cloud digestion: Azure growth 40% → 31%, AWS 33% → 12%, Google holds 2023 capex flat; WDC (Oct 2022), Marvell (Dec 2022), AMD (Jan 2023), Arista and Cisco (May–Jul 2023) follow. |
| Mar – Oct 2023 | AI turn: Broadcom quantifies AI networking (2 Mar), NVIDIA guides $11bn (24 May), Microsoft accelerates investment (Jul), TSMC flags a CoWoS shortage (20 Jul); Marvell, Lam, KLA, Coherent within two quarters; AMD 31 Oct. |
| Oct 2023 – Sep 2024 | AI crowds out non-AI spending (Seagate, Intel); Broadcom's non-AI business bottoms in Sep 2024. |
| Jan – Apr 2024 | Memory and storage lead the equipment recovery: Lam, WDC, Applied Materials, KLA. |
| Jul 2024 onward | Cloud capacity short of demand on nearly every hyperscaler call (one easing call, Microsoft Jan 2025, reversed by Oct 2025). |
| Oct – Dec 2025 | Shortage: NVIDIA "clouds are sold out" (19 Nov), Broadcom $73bn AI backlog (11 Dec), Micron HBM sold out (17 Dec); multi-year supply contracts follow (Micron, SanDisk). |
| Dec 2025 – 2026 | Frontier-lab backlogs: Oracle RPO $130bn (Mar 2025) → $638bn, Microsoft $678bn (45% OpenAI), Amazon $496bn, Alphabet $462bn, CoreWeave $104bn. |
| 2026 | Bottleneck moves to power and components: GE Vernova gas pipeline 55 → 100 GW with 2029–30 nearly sold; memory is the binding constraint for Dell, HPE, Super Micro; GPU rental renewals price higher; Schneider data-center demand triple-digit growth Q2–Q3; ABB orders +40% Q3. |
| Oct 2026 | Mixed: Meta narrows 2026 capex to $135–145bn with no 2027 number (21 Oct); nVent orders slowed (Jul); ASML guides 2026 to €44–45bn with customers raising forecasts and asking for 2029–30 slots (14 Oct); Lam sees 2027 WFE above $200bn (21 Oct). |
