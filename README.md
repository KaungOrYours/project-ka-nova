# Project Ka-Nova

An Agent-Based Simulation of Post-Conflict Governance in Myanmar

Ka (က) — first letter of the Burmese alphabet, meaning beginning.
Nova — emergence (Latin).
The emergence of a beginning.

> Academic Disclaimer: This project is created strictly for academic and data science research purposes as part of an MSc Data Science dissertation at the University of Hertfordshire. The MFU framework is a theoretical governance model designed solely for computational simulation and academic analysis. It is not a political manifesto, not a policy proposal, and not a call to action of any kind. No real-world implementation intended. Author respects Myanmar's laws and sovereignty.

---

## What This Project Is

Project Ka-Nova is a Generative Agent-Based Model (GABM) that stress-tests two constitutional frameworks over 50 simulated years:

- Scenario A: The Meritocratic Federal Union (MFU) — a theoretically designed post-conflict constitution for Myanmar
- Scenario C: The 2008 Myanmar Military Constitution — the real constitutional baseline

The central research question:

> If Myanmar's conflict ended tomorrow and the MFU constitution was implemented — what happens over 50 years, compared against the 2008 military constitution?

Ka-Nova answers this computationally. The same simulation engine runs both scenarios. The same external geopolitical shocks hit both scenarios. The difference is entirely constitutional design.

---

## Research Context

This is Paper 1 of a two-paper IEEE Access strategy co-authored with Dr. Md Saifullah Razali (Program Head, PSB Academy Singapore / University of Hertfordshire).

Paper 1 (October 2026): Hybrid GABM architecture and constitutional encoding methodology.
Paper 2 (April 2027): West Germany Basic Law 1949 historical backtesting — validates the methodology against real post-conflict outcomes.

The broader doctoral vision is GUPS (Generative Universal Policy Simulator) — a framework where any policy document can be automatically encoded as computable simulation parameters, run through the Ka-Nova engine, and produce a validated 50-year governance trajectory.

---

## Architecture

Ka-Nova combines three layers:

**Layer 1 — Mesa citizen agents (rule-based)**
11,000 agents at 1:5000 Myanmar population ratio. 56 behavioral combinations: 8 ethnic groups (census-proportional) x 7 archetypes. Each citizen has a 6-layer cognitive architecture: perception, decision, action, learning, social influence, and life course.

**Layer 2 — LLM elite agents (generative)**
7 LLM agents per scenario powered by Ollama Llama 3.2 3B. In Scenario A: Chancellor, President, Senior General, Chief Justice, IIG Director, Finance Minister, CB Governor — operating under civilian supremacy chain of command. In Scenario C: military equivalents with inverted objectives, derived from the 2008 constitution's chain of command. Elite agents deliberate before Mesa agents step each year.

**Layer 3 — External world (NumPy)**
17 evolving country and institution vectors (China, India, USA, EU, ASEAN, UN, IMF, illicit networks, etc.) calibrated from real sanctions and FDI data. 10 stochastic shock types (pandemic, regional conflict, sanctions, oil price shock, etc.) fire with historically calibrated probabilities. Same shock sequence hits both scenarios — no bias. Shocks cascade through the social media amplifier into citizen agents.

**Social media channel**
Regime openness is decided by LLM elite agents, not hardcoded. In Scenario C, internet suppression triggers a VPN floor mechanic: the more the military suppresses, the more citizens learn VPN usage, and the higher the floor rises. Suppression is self-defeating over time — historically accurate for Myanmar post-2021.

**CVES — Constitutional Validation and Error-Suppression**
A 4-layer runtime pipeline that validates every LLM elite decision before it enters the simulation: L1 schema integrity, L2 constitutional constraint mapping, L3 theory alignment against governance benchmarks, L4 statistical plausibility. All violations logged to JSONL. This is the primary methodological contribution for the IEEE paper.

---

## Current State

### Phase 1 — Complete

Rule-based Mesa agents only. 9,500 citizens, 4 simplified states, 300 runs, 50 steps. Run on M2 MacBook Pro. Results archived in `results_phase2/`.

### Phase 2 — Complete

Added LangChain LLM elite agents (Llama 3.2 3B). Scaled to 10,000 citizens, 14 states. Run on RunPod RTX 4090. Results archived in `results_phase2/`.

Key Phase 2 results at Year 50 (mean, 100 runs per scenario):

| KPI | Scenario A | Scenario C |
|---|---|---|
| Corruption | 0.189 | 0.933 |
| Coup probability | 0.000 | 0.600 |
| IIG effectiveness | 1.000 | 0.050 |
| North Star progress | 0.557 | 0.242 |

Statistical differentiation A vs C: p < 0.001, Cohen's d >= 1.21 across all primary KPIs.

### Phase 3 — In Progress

Architecture upgrades complete. RunPod run pending Sam's elite_agents_v3.py and D's constitution_2008.py.

What changed in Phase 3:

- Scenario B dropped (A vs C is the meaningful comparison)
- Citizens scaled to 11,000 (1:5000 Myanmar ratio)
- 56 ethnic-archetype combinations replacing universal proportions
- 7 LLM elite agents per scenario (was 3) with chain reasoning
- External layer: 17 evolving vectors + 10 stochastic shock types
- Social media channel: VPN floor, LLM-controlled openness, ethnic word-of-mouth
- Constitution import switch: Scenario A reads MFU v7, Scenario C reads 2008 Myanmar constitution
- CVES framework replacing FAIR evaluation
- Pod split strategy: Scenario A on Pod 1, Scenario C on Pod 2 simultaneously

---

## Constitution v7 — Canonical Parameters

All parameters in `config/constitution.py`. v7 is canonical — ignore any v6 references in older documentation.

Merit formula (Article III):
```
M = (Performance x 0.35) + (Education x 0.25) + (Professional Record x 0.20) + (Community x 0.20)
```

Three veto chambers (Article V):

| Chamber | Threshold |
|---|---|
| Congress | 51% |
| Ethnic Leaders Council | 51% |
| Analysis Council | 75% qualified supermajority |

Analysis Council veto confirmed by Citizens Assembly: 320 randomly sampled Mesa citizen agents, 51% threshold.

Resource split (Article VIII):

| Destination | Share |
|---|---|
| State governments | 35% |
| Federal Development Fund | 35% |
| Direct household transfers | 30% |

Article 19 — Tatmadaw transition: Senior General serves 5 years mandatory, active during 2nd quarter of each presidential term. No blanket immunity — war crimes go to law if proven.

---

## Project Structure

```
ka-nova/
├── agents/
│   ├── citizen.py               56 ethnic-archetype combinations, 6-layer cognitive architecture
│   ├── official.py              Officials, Chancellor, President (LLM-controlled in Phase 3)
│   ├── oversight.py             IIG agents, Constitutional Court, Arbitration Court
│   ├── foreign.py               Foreign investors, neighboring states, illicit networks
│   └── institutional.py         Central Bank, Dev Fund, Shame Register, Tax, ECB
├── config/
│   ├── constitution.py          MFU v7 — 19 articles, 40+ parameters
│   ├── constitution_2008.py     2008 Myanmar Military Constitution (Scenario C)
│   └── constitution_2008_encoding/   D's workspace for encoding
├── engine/
│   ├── elite_agents.py          Phase 2 LLM layer (fallback)
│   ├── elite_agents_v3.py       Phase 3 — Sam's file (pending)
│   ├── cves.py                  CVES 4-layer validation pipeline (pending)
│   ├── external_layer.py        17 evolving vectors, 10 shock types
│   ├── social_media.py          VPN floor, suppression backfire, ethnic networks
│   └── hybrid_engine.py         NumPy vectorised citizen operations
├── feedback/
│   └── loops.py                 12 annual feedback loops (P1-P4, E1-E4, S1-S4)
├── institutions/
│   ├── chambers.py              Three-chamber voting + Citizens Assembly veto
│   ├── court.py                 Constitutional Court mechanics
│   └── iig.py                   IIG Partnership Council
├── scenarios/
│   ├── run_a.py                 Scenario A runner
│   └── run_c.py                 Scenario C runner
├── analysis/
│   └── kpi.py                   Statistical analysis, MoS validation
├── charts/
│   └── visualize.py             All dissertation charts
├── results/                     Phase 3 CSV outputs
├── results_phase2/              Phase 2 archived results
├── model.py                     Phase 2 model (reference)
├── model_phase3.py              Phase 3 model (active)
├── run.py                       Phase 2 runner (reference)
└── run_phase3.py                Phase 3 runner (active)
```

---

## Setup

```bash
git clone https://github.com/KaungOrYours/project-ka-nova.git
cd project-ka-nova
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

python3 -c "import mesa; print(mesa.__version__)"
python3 config/constitution.py
```

Every new terminal:
```bash
cd ~/Desktop/ka-nova && source venv/bin/activate
```

Note: Mesa 2.3.0 via pip only. Never use brew install mesa — that installs a 3D graphics library, not the agent-based modeling framework.

---

## Running Phase 3

```bash
source venv/bin/activate

python3 run_phase3.py --test --scenario A
python3 run_phase3.py --test --scenario C

python3 run_phase3.py --scenario A --runs 5 --citizens 500 --steps 10

python3 run_phase3.py --scenario A --runs 100 --citizens 11000 --steps 50 --use-llm
python3 run_phase3.py --scenario C --runs 100 --citizens 11000 --steps 50 --use-llm
```

RunPod pod strategy: Pod 1 runs Scenario A, Pod 2 runs Scenario C simultaneously. Same external shock seed per run_id ensures both scenarios face identical geopolitical events.

Estimated runtime per pod (RTX 4090, 100 runs, 11,000 citizens, 50 steps, 7 LLM elites):
- Approximately 24-30 hours per pod
- Budget: approximately S$12-18 per pod at $0.34-0.50/hr

---

## Runtime Estimates

| Platform | Citizens | Steps | Runs | LLM | Estimate |
|---|---|---|---|---|---|
| M2 MacBook Pro | 200 | 5 | 1 | No | Under 1 second |
| M2 MacBook Pro | 500 | 10 | 3 | No | Under 5 seconds |
| RunPod RTX 4090 | 11,000 | 50 | 100 | Yes (7 agents) | 24-30 hours |

---

## Team

| Role | Person | Responsibility |
|---|---|---|
| First Author / Architect | Kaung Htet | Simulation architecture, codebase, constitution, results, lead writing |
| Senior Author | Dr. Md Saifullah Razali | LLM evaluation oversight, IEEE Access submission strategy, doctoral co-supervision |
| Third Author | Samsul Jahith S | CVES framework — elite_agents_v3.py, all 4 layers, JSONL logging, Section 4.3 |
| Fourth Author | Patil Devyani Anil | Literature review, Sections 2-3, 2008 constitution encoding, empirical calibration |

---

## Seven Citizen Archetypes

| Archetype | Universal Proportion | Behavioral Profile |
|---|---|---|
| civic_champion | 15% | High trust, low corruption tolerance, protests early |
| pragmatic_survivor | 30% | Adapts to any system, largest group |
| ethnic_loyalist | 20% | Primary identity is ethnic group over federal |
| ambitious_meritocrat | 15% | Believes in merit, high achiever |
| disillusioned_youth | 10% | Educated, frustrated, emigrates easily |
| rural_traditionalist | 7% | Low connectivity, traditional values |
| trauma_carrier | 3% | Conflict survivor, high trauma, low trust |

In Phase 3, each ethnic group has its own archetype proportions calibrated from V-Dem, ACLED, and Human Rights Watch data — 56 combinations total. Kayah ethnic group (~55 agents at 1:5000 ratio) is acknowledged as statistically thin in the paper limitations section.

---

## Year Zero Baselines

| Indicator | Value | Source |
|---|---|---|
| Corruption Index | 0.72 | Transparency International CPI 2023 |
| Trust Index | 0.22 | World Bank Governance 2022 |
| Gini Coefficient | 0.55 | World Bank 2017 |
| Employment Rate | 0.58 | Myanmar Census 2014 |
| Ethnic Tension | 0.68 | V-Dem Dataset |
| Stability Index | 0.18 | World Bank Political Stability 2022 |
| Coup Risk | 0.25 | Post-2021 estimate |
| Brain Drain Rate | 0.35 | Post-2021 emigration estimate |

---

## Publication Target

Primary: IEEE Access (Submit October 1, 2026)
Secondary: IEEE Transactions on Computational Social Systems

---

## Author

Kaung Htet | MSc Data Science | University of Hertfordshire | PSB Academy Singapore
GitHub: https://github.com/KaungOrYours/project-ka-nova
Dissertation deadline: December 2026
