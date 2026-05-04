# Project Ka-Nova

**An Agent-Based Simulation of Post-Conflict Governance in Myanmar**

Ka (က) — first letter of the Burmese alphabet, meaning beginning.
Nova — emergence (Latin).
*The emergence of a beginning.*

---

## Overview

Project Ka-Nova is an agent-based simulation (ABM) that stress-tests the Meritocratic Federal Union (MFU) constitution — a theoretically designed governance framework for post-conflict Myanmar — over 50 simulated years.

The central research question:

> *If Myanmar's conflict ended tomorrow and the MFU constitution was implemented — what happens over 50 years?*

Ka-Nova answers this question computationally, comparing three scenarios:

| Scenario | Description |
|---|---|
| **A** | Full MFU with all 18 constitutional articles and 7 safeguards active |
| **B** | MFU without safeguards — loopholes open, institutions vulnerable |
| **C** | Military baseline — current Myanmar trajectory, no MFU rules |

---

## Constitution v7 — Key Parameters

### Merit Formula (Article III — updated v7)

```
M = (Performance × 0.35) + (Education × 0.25) + (Professional Record × 0.20) + (Community Contribution × 0.20)
```

Community Contribution weight doubled from 10% to 20% to lower the entry barrier for rural and trauma-carrier archetypes.

### Three Veto Chambers (Article V — updated v7)

| Chamber | Threshold |
|---|---|
| Congress | 51% simple majority |
| Ethnic Leaders Council | 51% simple majority |
| Analysis Council | **75% qualified supermajority** (was 100% unanimous in v6) |

Analysis Council veto then confirmed by Citizens Assembly of 320 citizens (40 per state, cryptographic lottery, 51% threshold).

### Resource Revenue Split (Article VIII — updated v7)

| Destination | Share |
|---|---|
| State governments | 35% (was 40%) |
| Federal Development Fund | 35% (was 40%) |
| **Direct household transfers** | **30% (was 20%)** |

Community share increased from 20% to 30% as primary Gini reduction mechanism. Transfers go directly to households, bypassing state government.

### Trust Acceleration Trigger (Article VIII — new in v7)

When corruption index stays below 0.20 for 5+ consecutive years:
- Trust growth rate multiplies by **1.5×**
- Models the transition from fear-based compliance to genuine institutional trust

### Other Constitutional Parameters (unchanged)

| Parameter | Value |
|---|---|
| President term | 5 years, single term |
| Chancellor term | 5 years, single term, 5-year cooling-off |
| IIG entry merit | ≥ 0.85 + top 1% civil service |
| IIG Academy | 27 months |
| Constitutional Court | 11 judges, 10-year term, 6/11 majority |
| Total Ruin signatures | 4 bodies, 8/11 court supermajority |
| Constitutional review | Every 10 years, civic lottery |
| PhD tuition | Free + civil service stipend |
| Researcher royalty | 15% of net licensing revenue |
| Gini ECB trigger | > 0.45 |

---

## Agent Architecture

### Population (10,319 total)

| Tier | Type | Count | Description |
|---|---|---|---|
| 1 | Citizens | 9,500 | 7 archetypes, life course, bounded rationality |
| 2 | Officials | ~80 | President, Chancellor, Ministers, Congress, Ethnic Leaders |
| 3 | Oversight | 71 | IIG agents, Constitutional Court, Arbitration Court |
| 4 | Foreign | 100 | Investors, neighbors, international orgs, illicit networks |
| 5 | Institutional | 5 | Central Bank, Dev Fund, Shame Register, Tax System, ECB |

### Seven Citizen Archetypes (v7 — civic weights updated)

| Archetype | Proportion | Key traits |
|---|---|---|
| Civic Champion | 15% | High trust, low corruption tolerance |
| Pragmatic Survivor | 30% | Adapts to any system |
| Ethnic Loyalist | 20% | Primary identity is ethnic group |
| Ambitious Meritocrat | 15% | Believes in merit, high achiever |
| Disillusioned Youth | 10% | Educated, frustrated, emigrates easily |
| Rural Traditionalist | 7% | **v7: civic_contribution raised to 0.65** |
| Trauma Carrier | 3% | **v7: civic_contribution raised to 0.45** |

---

## Twelve Feedback Loops

| Loop | Category | Key effect |
|---|---|---|
| P1 Trust-Legitimacy | Political | 0.70 inertia + **v7: 1.5× acceleration trigger** |
| P2 IIG-Corruption | Political | Effectiveness compounds over time |
| P3 Coup Probability | Political | Branching by scenario |
| P4 Election-Merit | Political | 4-year recertification cycle |
| E1 State Competition | Economic | GDP growth with corruption drag |
| E2 Foreign Investment | Economic | Tech transfer with information lag |
| E3 Resource Revenue | Economic | **v7: 35/35/30 split** — direct household transfers |
| E4 PhD Economy | Economic | S-curve knowledge compounding |
| S1 National Service | Social | Generational ethnic cross-exposure |
| S2 Grievance-Protest | Social | Government response determines outcome |
| S3 Cultural Offense | Social | Random events, harmony dampens over time |
| S4 Shame Register | Social | Non-linear deterrence S-curve |

---

## Project Structure

```
ka-nova/
├── agents/
│   ├── citizen.py          7 archetypes, 5-layer cognitive architecture
│   ├── official.py         Government officials
│   ├── oversight.py        IIG agents, Constitutional Court
│   ├── foreign.py          Investors, neighbors, international orgs
│   └── institutional.py    Central Bank, Dev Fund, Shame Register
├── config/
│   └── constitution.py     All 18 articles as computable parameters
├── feedback/
│   └── loops.py            12 annual feedback loops
├── institutions/
│   ├── chambers.py         Three-chamber voting mechanics
│   ├── court.py            Constitutional Court mechanics
│   └── iig.py              IIG Partnership Council
├── scenarios/
│   ├── run_a.py            Scenario A — full MFU
│   ├── run_b.py            Scenario B — no safeguards
│   └── run_c.py            Scenario C — military baseline
├── analysis/
│   └── kpi.py              Statistical analysis
├── charts/
│   └── visualize.py        Dissertation charts
├── results/                CSV outputs
├── model.py                Main Ka-Nova simulation model
├── run.py                  Simulation runner (300 runs)
└── requirements.txt
```

---

## Installation and Setup

```bash
# Clone
git clone https://github.com/KaungOrYours/project-ka-nova.git
cd project-ka-nova

# Virtual environment — always use this
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Verify constitution loads
python3 config/constitution.py
```

**Every new terminal session:**
```bash
cd ~/Desktop/ka-nova
source venv/bin/activate
```

---

## Running the Simulation

```bash
# Step 1 — Quick test (always run this first)
python3 run.py --test

# Step 2 — Verify calibration and scenario differentiation
python3 run.py --runs 3 --citizens 500 --steps 20

# Step 3 — Full overnight run (dissertation quality)
nohup python3 run.py --citizens 2000 --steps 50 > output.log 2>&1 &

# Step 4 — Full publication run (9500 citizens)
nohup python3 run.py --citizens 9500 --steps 50 > output.log 2>&1 &

# Monitor progress
tail -f output.log
```

---

## After Simulation Completes

```bash
# Check result counts (should be 100 each)
ls results/scenario_a/ | wc -l
ls results/scenario_b/ | wc -l
ls results/scenario_c/ | wc -l

# Run statistical analysis
python3 analysis/kpi.py

# Generate all charts
python3 charts/visualize.py

# Push to GitHub
git add .
git commit -m "feat: add simulation results and analysis"
git push origin main --force
```

---

## Runtime Estimates (M2 MacBook Pro 8GB)

| Citizens | Steps | Runs | Estimate | Quality |
|---|---|---|---|---|
| 200 | 5 | 3 | ~12 seconds | Test only |
| 500 | 10 | 9 | ~30 seconds | Quick verify |
| 2,000 | 50 | 300 | ~90 minutes | Dissertation quality |
| 9,500 | 50 | 300 | ~8-10 hours | Full publication |

---

## Year Zero Baselines (Myanmar calibration targets)

| Indicator | Value | Source |
|---|---|---|
| Corruption Index | 0.72 | Transparency International CPI 2023 |
| Trust Index | 0.22 | World Bank Governance 2022 |
| Gini Coefficient | 0.55 | World Bank 2017 |
| Employment Rate | 0.58 | Myanmar Census 2014 |
| Ethnic Tension | 0.68 | V-Dem Dataset |
| Stability Index | 0.18 | World Bank Political Stability 2022 |
| Coup Risk | 0.45 | Post-2021 estimate |
| Brain Drain Rate | 0.35 | Post-2021 emigration estimate |

---

## Known Issues and Notes

- Always run from project root: `cd ~/Desktop/ka-nova`
- Always activate venv first: `source venv/bin/activate`
- Use `pip install mesa==2.3.0` — never `brew install mesa`
- All `__init__.py` files must exist in every folder
- Sequential execution — no multiprocessing (M2 macOS spawn causes hanging)

---

## Target Publications

- **Primary:** JASSS (Journal of Artificial Societies and Social Simulation)
- **Secondary:** Government Information Quarterly
- **Tertiary:** PLOS ONE

---

## Academic Disclaimer

**This project is created strictly for academic and data science research purposes as part of an MSc Data Science dissertation at the University of Hertfordshire.**

The MFU framework is a **theoretical governance model designed solely for computational simulation and academic analysis**. It is not a political manifesto, not a policy proposal, and not a call to action of any kind.

- No real-world implementation intended
- Not suitable for real-world implementation
- Author respects Myanmar's laws and sovereignty
- All constitutional articles exist exclusively within the Ka-Nova simulation environment

---

## Author

Kaung Htet | MSc Data Science | University of Hertfordshire
GitHub: [KaungOrYours](https://github.com/KaungOrYours/project-ka-nova)