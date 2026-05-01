# Project Ka-Nova

**An Agent-Based Simulation of Post-Conflict Governance in Myanmar**

Ka (က) — first letter of the Burmese alphabet, meaning beginning.
Nova — emergence (Latin).
*The emergence of a beginning.*

---

## Overview

Project Ka-Nova is an agent-based simulation (ABM) that stress-tests a theoretically designed governance constitution — the Meritocratic Federal Union (MFU) — over 50 simulated years of post-conflict Myanmar.

The central research question:

> *If Myanmar's conflict ended tomorrow and the MFU constitution was implemented — what happens over 50 years?*

Ka-Nova answers this question computationally, comparing three scenarios:

| Scenario | Description |
|---|---|
| **A** | Full MFU with all 18 constitutional articles and 7 safeguards active |
| **B** | MFU without safeguards — loopholes open, institutions vulnerable |
| **C** | Military baseline — current Myanmar trajectory, no MFU rules |

---

## The Constitution as Ruleset

Every agent behavior in Ka-Nova derives directly from a constitutional clause. The MFU Constitution has 18 articles covering:

- Merit system (Article 3) — M = (P×0.40) + (E×0.30) + (PR×0.20) + (C×0.10)
- Three veto chambers (Article 5) — Congress 51%, Ethnic Council 51%, Analysis Council 100%
- Independent Intelligence Group (Article 7) — Partnership model, 9 divisions
- Resource revenue split (Article 8) — 40% state / 40% federal / 20% ethnic communities directly
- Rules of Engagement (Article 17) — No Gun Policy domestic, Scorched Earth external
- Psychological Health Protocol (Article 18) — biannual screening, anti-bias anonymous review
- Cryptographic Justice (Article 15) — blockchain evidence, zero-knowledge proofs, Total Ruin Protocol
- Emergency Powers (Article 16) — 180-day maximum, rights untouched always

---

## Agent Architecture

Ka-Nova uses **Heterogeneous Cognitive Agents** — rule-based agents with multi-dimensional internal states, bounded rationality, and adaptive learning — producing emergent macro-level behavior from micro-level constitutional constraints.

### Agent Population (10,319 total)

| Tier | Type | Count | Description |
|---|---|---|---|
| 1 | Citizens | 9,500 | 7 archetypes, life course modeling, bounded rationality |
| 2 | Officials | ~80 | President, Chancellor, Ministers, Congress, Ethnic Leaders |
| 3 | Oversight | 71 | IIG agents, Constitutional Court, Arbitration Court |
| 4 | Foreign | 100 | Investors, neighboring states, international orgs, illicit networks |
| 5 | Institutional | 5 | Central Bank, Dev Fund, Shame Register, Tax System, ECB |

### Seven Citizen Archetypes

| Archetype | Proportion | Key traits |
|---|---|---|
| Civic Champion | 15% | High trust, low corruption tolerance, protests early |
| Pragmatic Survivor | 30% | Adapts to any system, largest group |
| Ethnic Loyalist | 20% | Primary identity is ethnic group over federal |
| Ambitious Meritocrat | 15% | Believes in merit system, high achiever |
| Disillusioned Youth | 10% | Educated, frustrated, emigrates easily |
| Rural Traditionalist | 7% | Low connectivity, traditional values |
| Trauma Carrier | 3% | Conflict survivor, high trauma, low trust |

### Six Cognitive Layers per Agent

1. **Perception** — bounded, local, recency-biased (political awareness determines information radius)
2. **Decision** — satisficing, not optimizing (stops at first acceptable option)
3. **Action** — affects environment, network, and institutions
4. **Learning** — adaptive thresholds update from experience
5. **Social Influence** — signals propagate through scale-free network
6. **Life Course** — agents age, study, work, retire, and die

---

## Twelve Feedback Loops

| Loop | Type | Category | Primary Effect |
|---|---|---|---|
| P1 Trust-Legitimacy | Negative | Political | Self-correcting stability |
| P2 IIG-Corruption | Negative | Political | Corruption suppression |
| P3 Coup Probability | Negative | Political | Military loyalty maintenance |
| P4 Election-Merit | Negative | Political | Leadership quality cycling |
| E1 State Competition | Positive | Economic | Growth acceleration |
| E2 Foreign Investment | Positive | Economic | Technology transfer |
| E3 Resource Revenue | Negative | Economic | Inequality correction |
| E4 PhD Economy | Positive | Economic | Knowledge compounding |
| S1 National Service | Positive | Social | Ethnic trust building |
| S2 Grievance-Protest | Negative | Social | Political pressure release |
| S3 Cultural Offense | Negative | Social | Ethnic tension dampening |
| S4 Shame Register | Negative | Social | Corruption deterrence |

---

## KPIs (15 indicators)

| KPI | Target Year 50 (Scenario A) |
|---|---|
| Corruption Index | < 0.20 |
| Trust Index | > 0.70 |
| Coup Probability | < 0.05 |
| Ethnic Harmony | > 0.75 |
| Gini Coefficient | < 0.35 |
| Employment Rate | > 0.85 |
| Knowledge Capital | Top 2 SEA |
| Brain Drain Rate | < 0.10 (net positive) |
| IIG Effectiveness | > 0.75 |
| Tax Compliance | > 0.90 |
| Shame Register Size | Growing (deterrence) |
| Foreign Investors | > 40 active |
| North Star Progress | > 0.80 |
| Stability Index | > 0.75 |
| Total Ruin Events | Peak years 5-15, decline after |

---

## Measures of Success (8 validation criteria)

| MoS | What it tests |
|---|---|
| Behavioral Validity | Agent behavior matches Myanmar baseline data |
| Emergence Validity | System patterns emerge from rules, not programming |
| Sensitivity Analysis | Results stable under ±10% parameter variation |
| Sample Sufficiency | 100 runs achieves variance stabilization |
| Scenario Differentiation | A vs B vs C statistically significant (p < 0.05) |
| Internal Consistency | Feedback loops produce expected directional effects |
| Reproducibility | Same seed = same results ±2% |
| Calibration | Year Zero matches V-Dem, World Bank, TI baselines |

---

## The North Star

> *"We do not build this Union merely to survive. We build it to lead. Within the lifetime of our children, Myanmar will be the intellectual and economic capital of Southeast Asia — not despite our complexity, but because of it."*

| Decade | Goal |
|---|---|
| 2025–2035 | Survive — build institutions, stop bleeding talent |
| 2035–2045 | Compete — states racing, PhD economy emerging |
| 2045–2055 | Lead — Myanmar exports governance models and technology |
| 2055–2075 | Dominate — proof that post-conflict federalism works for 55 million |

---

## Project Structure

```
ka-nova/
├── agents/
│   ├── citizen.py          Heterogeneous cognitive citizen agents
│   ├── official.py         Government officials, Chancellor, President
│   ├── oversight.py        IIG agents, Constitutional Court judges
│   ├── foreign.py          Investors, neighbors, international orgs
│   └── institutional.py    Central Bank, Dev Fund, Shame Register
├── config/
│   └── constitution.py     All 18 articles as computable parameters
├── feedback/
│   └── loops.py            12 annual feedback loops
├── scenarios/
│   ├── run_a.py            Scenario A — full MFU
│   ├── run_b.py            Scenario B — no safeguards
│   └── run_c.py            Scenario C — military baseline
├── analysis/
│   └── kpi.py              Statistical analysis and significance tests
├── results/
│   ├── scenario_a/         100 CSV files per run
│   ├── scenario_b/
│   ├── scenario_c/
│   ├── all_results.csv     Combined 300-run dataset
│   └── summary_statistics.csv
├── charts/
│   ├── kpi/                KPI trajectory charts
│   ├── feedback/           Feedback loop visualizations
│   └── comparison/         Scenario A vs B vs C comparison charts
├── model.py                Main Ka-Nova simulation model
├── run.py                  Simulation runner (300 runs)
└── requirements.txt        Python dependencies
```

---

## Installation

```bash
# Clone repository
git clone https://github.com/KaungOrYours/project-ka-nova.git
cd project-ka-nova

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Verify constitution loads correctly
python3 config/constitution.py
```

---

## Usage

```bash
# Quick test — 1 run per scenario, 500 citizens, 10 steps
python3 run.py --test

# Single scenario
python3 run.py --scenario A

# Custom run
python3 run.py --runs 10 --citizens 1000 --steps 20

# Full dissertation run — 300 runs, 50 years
python3 run.py
```

---

## Requirements

```
mesa==2.3.0
numpy==1.26.4
pandas==2.2.1
matplotlib==3.8.3
seaborn==0.13.2
networkx==3.2.1
scipy==1.12.0
tqdm==4.66.2
plotly==5.20.0
SALib==1.4.7
```

Tested on: Apple M2 MacBook Pro 8GB, macOS, Python 3.11

---

## Year Zero Starting Conditions

Calibrated from Myanmar Census 2014, V-Dem Dataset, World Bank Governance Indicators, and Transparency International CPI:

| Indicator | Value | Source |
|---|---|---|
| Corruption Index | 0.72 | Transparency International |
| Trust Index | 0.22 | World Bank |
| Gini Coefficient | 0.55 | World Bank |
| Employment Rate | 0.58 | Myanmar Census 2014 |
| Ethnic Tension | 0.68 | V-Dem |
| IIG Effectiveness | 0.30 | Baseline (no IIG exists yet) |
| Military Loyalty | 0.55 | Estimated |

---

## Academic Context

**Target journals:** JASSS (primary), Government Information Quarterly, PLOS ONE

**Paper title:** Stress-Testing a Meritocratic Federal Governance Framework: An Agent-Based Simulation of Post-Conflict Institutional Resilience

**Research question:** Does the MFU constitutional framework produce the institutional conditions for Southeast Asian economic and intellectual dominance within 50 years?

**Novel contributions:**
- Constitutional rules as agent behavioral constraints (first in ABM literature)
- Psychological health protocol as governance quality determinant
- Cryptographic justice mechanics in simulation
- Post-conflict multi-ethnic federal ABM for Myanmar

---

## Author

Kaung Htet
MSc Data Science — University of Hertfordshire
GitHub: [KaungOrYours](https://github.com/KaungOrYours)

---

## License

MIT License — see LICENSE file for details.

---

*Ka-Nova is not just a simulation. It is a computational argument that Myanmar can lead Southeast Asia — if the institutions are right.*