# NVIDIA's "AI is a five-layer cake": what each layer is and who NVIDIA puts in it

Built 2026-10-23 from the keynote corpus in `data/processed/keynotes/text/`. Sources, in date order:

| Date | Source | Local text |
|---|---|---|
| 2026-01-21 | Davos: Huang in conversation with BlackRock CEO Larry Fink (WEF Annual Meeting), [blog](https://blogs.nvidia.com/blog/davos-wef-blackrock-ceo-larry-fink-jensen-huang/) | `text/davos_2026/blog_davos-wef-blackrock-ceo-larry-fink-jensen-huang.txt` |
| 2026-03-10 | Jensen Huang essay, ["AI Is a 5-Layer Cake"](https://blogs.nvidia.com/blog/ai-5-layer-cake/) | `text/davos_2026/blog_ai-5-layer-cake.txt` |
| 2026-03-16 | GTC 2026 keynote: "This conference is going to cover every single layer of the five-layer cake" ([live blog](https://blogs.nvidia.com/blog/gtc-2026-news/)) | `text/gtc_2026/blog_gtc-2026-news.txt` |
| 2026-06-08 | Seoul partner reception: about 200 Korean partners "from every part of the Korea AI ecosystem, corresponding to the five-layer cake" ([blog](https://blogs.nvidia.com/blog/korea-ecosystem-2026/)) | `data/raw/keynotes/_probe/korea-ecosystem-2026.html` |
| 2026-10-21 | GTC Berlin keynote ([live blog](https://blogs.nvidia.com/blog/gtc-berlin-2026-keynote/)), the slide "Building Europe's AI Economy", the press kit and the news hub (Dublin panel) | `text/gtc_berlin_2026/*.txt` |

## The framework

- **Davos (Jan 2026).** Huang described AI as "a five-layer cake" spanning "energy, chips and computing infrastructure, cloud data centers, AI models and, ultimately, the application layer". He called it "the largest infrastructure buildout in human history". Each layer must be built and operated, so the buildout creates jobs across the economy: plumbers, electricians, construction workers, steelworkers and network technicians. "This layer on top [applications], ultimately, is where economic benefit will happen." He said 2025 was the largest year for VC (>$100B), mostly into AI-native startups that "are building the application layer above … and they're going to need infrastructure". He also said "AI is infrastructure" that every country should build ("national intelligence"). Fink's question was whether the world is investing enough, not whether there is a bubble.
- **Essay (Mar 2026).** The canonical chain is **Energy → chips → infrastructure → models → applications**. "Every successful application pulls on every layer beneath it, all the way down to the power plant." The world is "a few hundred billion dollars into" the buildout and "trillions of dollars of infrastructure still need to be built." Open models such as DeepSeek-R1 "activate demand across the entire stack."
- **GTC Berlin keynote (Oct 21 2026).** "Energy powers advanced computers that are part of an AI factory, which generates tokens and digital intelligence from the models that run on it, which are then integrated into every application." Also: "Long before the AI models emerge, the infrastructure has to exist." Huang said Europe should be "producing the AI," not just consuming it. NVIDIA cited nearly $10B committed to Europe's ecosystem and 12,000+ partners.

## Layer by layer

### 1. Energy
- **What NVIDIA says.** Energy is "the foundation" and "the binding constraint on how much intelligence the system can produce" (essay). "Intelligence generated in real time requires power generated in real time." In Berlin the energy pitch is efficiency: the DSX AI Factory platform delivers "the same AI output with up to 30% less power" and "up to 100%" less cooling water. DSX MaxLPS fits more GPUs within a fixed power budget: Nscale reported +37% GPUs and about +50% throughput, and Lambda reported +24% token throughput. DSX Flex makes AI factories flexible grid loads.
- **Companies NVIDIA places here.**
  - *Berlin slide (Energy):* Rolls-Royce SMR (subsidiary of **RR.L**), **Schneider Electric (SU.PA)**, **Siemens (SIE.DE)**, **Siemens Energy (ENR.DE)**.
  - *Berlin DSX release, "energy and cooling providers":* ABB (ABBN.SW), Eaton (ETN), GE Vernova (GEV), Hitachi Energy (6501.T), Schneider Electric, Siemens Energy, Trane Technologies (TT) and Vertiv (VRT). AVEVA (Schneider), Dassault Systèmes (DSY.PA), Siemens, PTC and Procore provide design and operations software. GE Vernova, Hitachi Energy and Siemens Energy collaborate on grid integration and power digital twins.
  - *Davos:* no companies named. The examples are trades and jobs (electricians, plumbers, pipefitters).

### 2. Chips / Compute
- **What NVIDIA says.** Chips are "processors designed to transform energy into computation efficiently at massive scale," needing parallelism, high-bandwidth memory and fast interconnects. "Progress at the chip layer determines how fast AI can scale and how affordable intelligence becomes." In Berlin, Vera Rubin is "in full production" and extends NVIDIA's platform to "process the entire AI agent", including Vera CPUs, BlueField-4 and the Groq 3 LPX inference racks. Huang: "Demand is extraordinary. Capacity is the constraint."
- **Companies NVIDIA places here.**
  - *Berlin slide (Compute):* **NVIDIA (NVDA)** only.
  - *Berlin supply-chain release:* Amkor (AMKR), IBIDEN (4062.T), King Yuan Electronics/KYEC (2449.TW), Samsung Electro-Mechanics (009150.KS), SPIL (ASE, 3711.TW) and Unimicron (3037.TW). They are expanding substrates, advanced packaging, testing and optical engines.
  - *Elsewhere in the corpus:* TSMC (TSM/2330.TW) appears in 20 docs (cuLitho, silicon-photonics ecosystem, Blackwell manufacturing). SK hynix signed a multiyear memory partnership in Korea in June 2026. The silicon-photonics list includes Coherent, Corning, Fabrinet, Lumentum, Browave, SENKO, SPIL and Sumitomo Electric. Hyperscaler and partner CPUs come in via NVLink Fusion (Fujitsu, Qualcomm).

### 3. Infrastructure / AI factories (Davos: "cloud data centers")
- **What NVIDIA says.** This layer covers "land, power delivery, cooling, construction, networking and the systems that orchestrate tens of thousands of processors into one machine. These systems are AI factories … designed to manufacture intelligence" (essay). In Berlin, the **DSX POD** reference design ships complete Vera Rubin AI factories in modular containers. It cuts on-site deployment "from six months to just 14 days" ("a complete transformation of the world supply chain"). Sovereign capacity close to Europe's data is the main theme.
- **Companies NVIDIA places here.**
  - *Berlin slide (AI Factories):* Bull, **Deutsche Telekom (DTE.DE)**, Firebird, Mistral AI (Mistral Compute), **Nebius (NBIS)**, Nscale, **Nokia (NOKIA.HE)**, Radiant (Brookfield's AI cloud) and Volta. The private companies are profiled in `config/private_companies.csv`.
  - *Berlin DSX POD builders:* Anduril, Armada, Bull, Crusoe, DayOne, Dell (DELL), Delta Electronics (2308.TW), Eaton (ETN), Foxconn/Ingrasys (2317.TW), GIGABYTE (2376.TW), HPE (HPE), Lenovo (0992.HK), Pegatron (4938.TW), QCT (2382.TW), Schneider Electric (SU.PA), Vertiv (VRT) and Wistron (3231.TW).
  - *Berlin AI clouds:*
    - DSX OS: Aleria, Cassava, CoreWeave (CRWV), Crusoe, Firmus, Firebird, G42, GMI Cloud, IREN (IREN), Lambda, Nebius, Nscale, Radiant, Sharon AI and Volta.
    - OpenShell: the clouds above plus DigitalOcean (DOCN), Fireworks, Baseten, Lightning AI, Oracle OCI (ORCL) and Verda.
    - Google Cloud (GOOGL) announced general availability of Vera Rubin A5X instances.
    - Deutsche Telekom runs an Industrial AI Cloud and runs AI-RAN pilots with Nokia. Nokia, BT, Elisa and T-Mobile frame telecom networks as "distributed intelligence platforms".
  - *Korea (Jun 2026):* NAVER is building a full-stack DSX AI factory. SK Telecom, SK Group, LG Group, Hyundai Motor Group and Doosan are building AI factories.

### 4. Models
- **What NVIDIA says.** Models span "language, biology, chemistry, physics, finance, medicine and the physical world"; "language models are only one category" (essay). Open models are critical: "most of the world's models are free". In Berlin, NVIDIA open models (Nemotron, Cosmos, GR00T, Alpamayo, Earth-2, BioNeMo/Proteina) are positioned as the base for sovereign, domain-specific AI, together with the **Nemotron Coalition**.
- **Companies NVIDIA places here.**
  - *Berlin slide (Models):* Aleph Alpha (merging into Cohere), Advanced Machine Intelligence (AMI Labs, Yann LeCun), Black Forest Labs, **Ineffable Intelligence** (David Silver; this is our identification of the hard-to-read logo) and Mistral AI. All are private.
  - *Berlin docs:*
    - Mistral Large 4 was trained on 3,800 Grace Blackwell GPUs, and Vera Rubin is planned for 2027.
    - Nemotron Coalition European partners are Black Forest Labs, H Company and Mistral.
    - Ineffable was the first customer of Google Cloud A5X (Vera Rubin).
    - Recursive Superintelligence released the Recursive Flint local coding model.
    - Post-training partners include AgileRL, Distil Labs, Multiverse Computing, Nebius, CoreWeave, Google Cloud and Scale AI.
  - *Listed exposure:* there are no listed pure-plays. Exposure comes through investors (NVDA, GOOGL, MSFT, AMZN, ASML.AS for Mistral, SAP.DE for Aleph Alpha and n8n, Samsung) and through hosting clouds. See `public_links` in `config/private_companies.csv`.

### 5. Applications
- **What NVIDIA says.** "At the top are applications, where economic value is created": drug discovery, industrial robotics, legal copilots, self-driving cars and humanoid robots ("same stack, different outcomes"). At Davos the examples were financial services, healthcare and manufacturing, with Abridge's clinical documentation cited for nursing. In the Berlin news hub, NVIDIA's Deepu Talla (Dublin International AI Summit panel, pre-Berlin tour) said Europe can play in all layers but "the most important layer for European nations to focus on is applications." He called physical AI the big opportunity because about 70% of GDP is in the physical world. Huang opened Berlin by naming L'Oréal (OR.PA), Revolut, Spotify (SPOT), Merck, Vodafone (VOD.L), Zara/Inditex (ITX.MC), Porsche (P911.DE), Nestlé (NESN.SW) and HSBC (HSBA.L) as European companies working with NVIDIA.
- **Companies NVIDIA places here.**
  - *Berlin slide (Applications):* 29 companies, all private.
    - Robotics and physical AI: AgileRL, Agile Robots, Wandelbots (the "AWbotics"-looking logo), Humanoid, MicroAGI, NEURA Robotics, Oxa and Wayve.
    - Health and bio: Avelios, Basecamp Research, Latent Labs and Prima Mente.
    - Generative and agent apps: Black Forest Labs, Cursive, DeepL, distil labs, ElevenLabs, Gradium, H Company, inherent (Inherent Laboratories), Langdock, Legora, Lovable, n8n, Recursive (Recursive Superintelligence) and Synthesia.
    - Engineering and defence: Helsing, Multiverse Computing and PhysicsX.
  - *Listed application-layer names in Berlin docs:*
    - Enterprise and industrial software: SAP (SAP.DE), Siemens (SIE.DE), Dassault Systèmes (DSY.PA), ServiceNow (NOW), Salesforce (CRM), Palantir (PLTR) and Adobe (ADBE).
    - Mobility: Volvo Cars (VOLCAR-B.ST), Mercedes-Benz (MBG.DE) and other Hyperion automakers.
    - Healthcare: Siemens Healthineers (SHL.DE) and others (see the healthcare release).
    - Robotics: ABB Robotics (ABBN.SW), KUKA (Midea), Hexagon Robotics (HEXA-B.ST), Universal Robots (TER) and Schaeffler (SHA.DE).

## Mapping to the project universe

`config/universe.csv` uses the same layers (`cake_layer`): Energy, Chips, Infrastructure and Applications. There is no listed Models layer. The public companies on the Berlin slide are already flagged `berlin_slide=1`:

| Layer | Universe tickers on the slide |
|---|---|
| Energy | ENR.DE, RR.L (via Rolls-Royce SMR), SU.PA, SIE.DE |
| Compute | NVDA |
| AI factories | DTE.DE, NBIS, NOKIA.HE |

All other slide companies are private and are profiled in `config/private_companies.csv`.

## Caveats
- The slide is an image. Its contents come from the project brief and are stored as a pseudo-document in `text/gtc_berlin_2026/slide_building-europes-ai-economy.txt`. Two logos were identified by inference: Wandelbots for the "AWbotics"-looking logo, and Ineffable Intelligence for the unreadable Models logo, supported by NVIDIA's Berlin news hub.
- The Davos post is a blog recap, not a transcript. The clock time of the session was not found. Bloomberg places it on Wednesday Jan 21 2026.
