# Project Ka-Nova

**An Agent-Based Simulation of Post-Conflict Governance in Myanmar**

Ka (က) — first letter of the Burmese alphabet, meaning beginning.
Nova — emergence (Latin).
*The emergence of a beginning.*

> **Academic Disclaimer:** This project is created strictly for academic and data science research purposes as part of an MSc Data Science dissertation at the University of Hertfordshire. The MFU framework is a theoretical governance model designed solely for computational simulation and academic analysis. It is not a political manifesto, not a policy proposal, and not a call to action of any kind. No real-world implementation intended. Author respects Myanmar's laws and sovereignty.

---

## Overview

Project Ka-Nova is an Agent-Based Model (ABM) that stress-tests the **Meritocratic Federal Union (MFU)** constitution — a theoretically designed governance framework for post-conflict Myanmar — over 50 simulated years.

The central research question:

> *If Myanmar's conflict ended tomorrow and the MFU constitution was implemented — what happens over 50 years?*

Ka-Nova answers this question computationally, comparing three scenarios:

| Scenario | Description |
|---|---|
| **A** | Full MFU — all 18 constitutional articles and 7 safeguards active |
| **B** | MFU without safeguards — loopholes open, institutions vulnerable |
| **C** | Military baseline — current Myanmar trajectory, no MFU rules |

---

## Phase 1 — What We Built (Complete ✅)

Phase 1 ran on an **M2 MacBook Pro 8GB** using **Mesa 2.3.0**.

### Scale
- **9,500 citizen agents** across 4 simplified states
- **300 runs** (100 per scenario), 50 years each
- **47.4 hours** total runtime, 0 failures
- Sequential execution only — M2 macOS multiprocessing causes hanging

### Architecture
- All agents implemented as standard Mesa agents
- 10,319 total agents across 5 tiers
- 12 feedback loops (P1–P4, E1–E4, S1–S4)
- 23 KPI reporters via Mesa DataCollector
- Constitution v7 parameters in `config/constitution.py`

### Phase 1 Results (Final — Do Not Re-Run)

| KPI | Scenario A | Scenario B | Scenario C |
|---|---|---|---|
| Corruption Index | **0.186** ± 0.009 | 0.213 ± 0.010 | 0.946 ± 0.001 |
| Trust Index | **0.523** ± 0.019 | 0.514 ± 0.020 | 0.461 ± 0.016 |
| Coup Probability | **0.000** ± 0.000 | 0.000 ± 0.000 | 0.200 ± 0.000 |
| IIG Effectiveness | **1.000** ± 0.000 | 0.992 ± 0.000 | 0.050 ± 0.000 |
| North Star Progress | **0.487** ± 0.005 | 0.475 ± 0.005 | 0.290 ± 0.004 |
| Gini Coefficient | 0.570 ± 0.010 | 0.567 ± 0.009 | 0.571 ± 0.010 ⚠️ |

### Phase 1 Known Bugs (Fixed in Phase 2)

| Bug | Symptom | Root Cause |
|---|---|---|
| Gini deadlock | Stuck at ~0.570 across all scenarios | Community share never reached `agent.household_income` |
| Trust A/B too similar | Gap only 0.009 (small effect) | Safeguards not mechanically wired to trust |
| Ethnic harmony locked | 0.315 identical across all scenarios | S3 loop not wired to reporter |
| Brain drain dead | 0.000 all scenarios | Emigration trigger never fired |
| Stability Year 0 off | Real=0.18, Sim=0.33 | Starting baseline too optimistic |

### Phase 1 Measures of Success

| MoS | Result |
|---|---|
| MoS 4 Sample Sufficiency | PASS — 93.8% stable at 100 runs |
| MoS 5 Scenario Differentiation | PASS — 72.9% significant (p<0.05) |
| MoS 7 Reproducibility | PASS — deterministic seeding |
| MoS 1 Behavioral Validity | PARTIAL — 55.6% KPIs within 10% |
| MoS 6 Internal Consistency | PARTIAL — 79.2% correct direction |
| MoS 8 Calibration | PARTIAL — 55.6% within threshold |

---

## Phase 2 — What's New 

Phase 2 runs on **RunPod RTX 4090 (24GB VRAM)** via Remote SSH from VSCode.

### What Changed — Surgical Upgrades Only

Phase 2 does **not** rewrite Phase 1. Every existing Mesa agent, feedback loop, and institution is preserved. Only 5 targeted changes were made:

#### 1. Three LLM Elite Agents (`engine/elite_agents.py`)

The **Chancellor**, **President**, and **Senior General** are now driven by **LangChain + Llama 3** instead of Mesa step logic.

Every year, before any Mesa agent steps:
```
Status Report → Chancellor LLM → budget_weight + ethnic_weights
Status Report → President LLM  → budget_weight + ethnic_weights
Status Report → General LLM    → budget_weight + coup_signal (hidden threshold)
         ↓
Weighted combination (50% Chancellor / 30% President / 20% General)
         ↓
Writes to shared_data → all Mesa agents read as environment
```

The **Senior General has a hidden coup threshold**: if `corruption > 0.65 AND trust < 0.30`, he signals `coup_signal=True`. Under Scenario A, institutional checks suppress it. Under Scenario C, they may not.

#### 2. 14 Myanmar States (was 4)

Expanded from 4 simplified states to all 14 actual Myanmar states/regions:

| States | Regions |
|---|---|
| Shan, Kachin, Kayah, Karen, Chin, Mon, Rakhine | Sagaing, Mandalay, Magway, Bago, Yangon, Ayeyarwady, Tanintharyi |

Original 4 Phase 1 states preserved as first entries — all existing agent `state_id` assignments still work.

#### 3. Gini Bug Fix — Article VIII Direct Household Transfer

The Phase 1 community share went into a pool but never reached `agent.household_income`. Fixed using **NumPy vectorised progressive transfer**:

```python
# Bottom 40% of wealth distribution → 1.5× per-capita share
# Top 60%                           → 0.67× per-capita share
# Zero Python loops — O(N log N) vectorised rank-based weighting
incomes     = np.array([a.household_income for a in citizen_agents])
ranks       = np.argsort(np.argsort(incomes))
percentiles = ranks / n
weights     = np.where(percentiles < 0.40, 1.5, 0.67)
transfers   = (weights / weights.sum()) * community_share
```

This is the mechanism designed to bring Gini from 0.570 toward the target of 0.35 over 50 years.

#### 4. Scale: 50,000 Citizens

Citizens scaled from 9,500 to 50,000. Assigned to 14 states proportionally by GDP weight, with ethnic groups assigned per state using Myanmar 2014 census proportions.

#### 5. ChancellorAgent and PresidentAgent Removed from Mesa Scheduler

Class shells preserved in `agents/official.py` so all imports still work, but they are **not added to the Mesa scheduler**. Their `step()` methods are no-ops. `EliteAgentLayer` handles them via LLM.

`cast_tiebreaker_vote()` on `PresidentAgent` is preserved — `chambers.py` still calls it directly on deadlock.

### Phase 2 Architecture

```
run.py --use-llm
    │
    └── KaNovaModel.step() called each year
          │
          ├── 0. EliteAgentLayer.step()          ← NEW (fires before Mesa)
          │     ├── Chancellor LLM  (Llama 3)
          │     ├── President LLM   (Llama 3)
          │     └── Senior General  (Llama 3, hidden coup threshold)
          │     └── Writes decisions to shared_data
          │
          ├── 1. _broadcast_environment()        ← unchanged
          ├── 2. schedule.step()                 ← unchanged
          │     ├── Ministers, Congress          ← Mesa (unchanged)
          │     ├── Ethnic Leaders               ← Mesa (unchanged)
          │     ├── IIG agents, Court judges     ← Mesa (unchanged)
          │     ├── Foreign investors            ← Mesa (unchanged)
          │     └── Institutional agents         ← Mesa (unchanged)
          ├── 3. _propagate_network_effects()    ← unchanged
          ├── 4. _enforce_institutional_rules()  ← unchanged
          ├── 5. _run_feedback_loops()           ← E3 fixed (Gini bug)
          ├── 6. _apply_scenario_rules()         ← unchanged
          ├── 7. _update_state_environments()    ← unchanged
          └── 8. _check_special_events()         ← unchanged
```

### Files Changed in Phase 2

| File | Change |
|---|---|
| `engine/elite_agents.py` | **NEW** — LangChain LLM elite agent layer |
| `engine/__init__.py` | **NEW** — package init |
| `model.py` | 5 surgical diffs — import, `__init__`, shared_data keys, 14 states, `step()` + E3 Gini fix |
| `agents/official.py` | Chancellor + President: `PHASE2_LLM_CONTROLLED=True`, `step()` no-op, removed from scheduler |
| `run.py` | Added `--use-llm` flag, passed to `KaNovaModel()` |
| `requirements.txt` | Added LangChain, openai, polars |

### Files Untouched in Phase 2

`agents/citizen.py`, `agents/oversight.py`, `agents/foreign.py`, `agents/institutional.py`, `config/constitution.py`, `feedback/loops.py`, `institutions/chambers.py`, `institutions/court.py`, `institutions/iig.py`, `scenarios/run_a.py`, `scenarios/run_b.py`, `scenarios/run_c.py`, `analysis/kpi.py`, `charts/visualize.py`

---

## Constitution v7 — Key Parameters

### Merit Formula (Article III)
```
M = (Performance × 0.35) + (Education × 0.25) + (Professional Record × 0.20) + (Community Contribution × 0.20)
```
Community Contribution doubled from 10% → 20% to lower entry barrier for rural and trauma-carrier archetypes.

### Three Veto Chambers (Article V)

| Chamber | Threshold |
|---|---|
| Congress | 51% simple majority |
| Ethnic Leaders Council | 51% simple majority |
| Analysis Council | 75% qualified supermajority (was 100% in v6) |

Analysis Council veto confirmed by Citizens Assembly: 320 citizens, 40 per state, cryptographic lottery, 51% threshold.

### Resource Revenue Split (Article VIII)

| Destination | Share |
|---|---|
| State governments | 35% |
| Federal Development Fund | 35% |
| **Direct household transfers** | **30%** ← primary Gini reduction mechanism |

### Trust Acceleration (Article VIII)
When `corruption_index < 0.20` for 5+ consecutive years → trust growth rate × **1.5×**

### Other Parameters

| Parameter | Value |
|---|---|
| President term | 5 years, single term |
| Chancellor term | 5 years, single term, 5-year cooling-off |
| IIG entry merit | ≥ 0.85, top 1% civil service, 27-month academy |
| Constitutional Court | 11 judges, 10-year term, 6/11 majority |
| Gini ECB trigger | > 0.45 |
| PhD tuition | Free + civil service stipend |
| Researcher royalty | 15% net licensing revenue |

---

## Project Structure

```
ka-nova/
├── engine/                      ← NEW in Phase 2
│   ├── __init__.py
│   └── elite_agents.py          ← LangChain LLM Chancellor/President/General
├── agents/
│   ├── citizen.py               7 archetypes, 5-layer cognitive architecture
│   ├── official.py              Officials (Chancellor/President shells → LLM)
│   ├── oversight.py             IIG agents, Constitutional Court
│   ├── foreign.py               Investors, neighbors, international orgs
│   └── institutional.py         Central Bank, Dev Fund, Shame Register
├── config/
│   └── constitution.py          All 18 articles as computable parameters (v7)
├── feedback/
│   └── loops.py                 12 annual feedback loops
├── institutions/
│   ├── chambers.py              Three-chamber voting mechanics
│   ├── court.py                 Constitutional Court mechanics
│   └── iig.py                   IIG Partnership Council
├── scenarios/
│   ├── run_a.py                 Scenario A — full MFU
│   ├── run_b.py                 Scenario B — no safeguards
│   └── run_c.py                 Scenario C — military baseline
├── analysis/
│   └── kpi.py                   Statistical analysis
├── charts/
│   └── visualize.py             Dissertation charts
├── results/                     CSV outputs
├── model.py                     Main simulation model (Phase 2 updated)
├── run.py                       Simulation runner (Phase 2 updated)
└── requirements.txt             Unified Phase 1 + Phase 2 dependencies
```

---

## Installation and Setup

### Mac (Phase 1 / rule-based Phase 2)

```bash
git clone https://github.com/KaungOrYours/project-ka-nova.git
cd project-ka-nova
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Verify
python3 -c "import mesa; print(mesa.__version__)"  # must be 2.3.0
python3 config/constitution.py
```

**Every new terminal:**
```bash
cd ~/Desktop/ka-nova && source venv/bin/activate
```

### RunPod (Phase 2 LLM — RTX 4090)

```bash
# 1. Connect via VSCode Remote SSH
# Extensions → Remote-SSH → Connect to Host → runpod-ka-nova

# 2. Clone repo on RunPod
cd /workspace
git clone https://github.com/KaungOrYours/project-ka-nova.git ka-nova
cd ka-nova
pip install -r requirements.txt

# 3. Start LLM server — Option A: Ollama (simpler)
curl -fsSL https://ollama.com/install.sh | sh
ollama serve &
ollama pull llama3:8b
export ELITE_LLM_BASE_URL="http://localhost:11434/v1"
export ELITE_LLM_API_KEY="ollama"
export ELITE_LLM_MODEL="llama3:8b"

# 3. Start LLM server — Option B: vLLM (faster for large runs)
pip install vllm
python -m vllm.entrypoints.openai.api_server \
  --model meta-llama/Meta-Llama-3-8B-Instruct \
  --port 8000 &
export ELITE_LLM_BASE_URL="http://localhost:8000/v1"
export ELITE_LLM_API_KEY="EMPTY"
export ELITE_LLM_MODEL="meta-llama/Meta-Llama-3-8B-Instruct"
```

---

## Running the Simulation

```bash
# Always activate venv first
source venv/bin/activate

# Mac — quick test (no LLM, always run this first)
python3 run.py --test

# Mac — Phase 1 style (rule-based elite agents)
python3 run.py --citizens 9500 --steps 50 --runs 300

# Mac — Phase 2 scale, rule-based overnight
nohup python3 run.py --citizens 50000 --steps 50 --runs 100 > output.log 2>&1 &

# RunPod — Phase 2 full with LLM (statistical runs)
nohup python3 run.py --citizens 50000 --steps 50 --runs 100 --use-llm > output.log 2>&1 &

# RunPod — LLM probe run (for dissertation dialogue examples)
python3 run.py --citizens 50000 --steps 50 --runs 10 --use-llm

# Monitor
tail -f output.log
```

---

## After Simulation Completes

```bash
ls results/scenario_a/ | wc -l   # should be 100
python3 analysis/kpi.py
python3 charts/visualize.py
git add . && git commit -m "feat: phase 2 results" && git push origin main --force
```

---

## Runtime Estimates

### Mac M2 8GB (no LLM)

| Citizens | Steps | Runs | Estimate |
|---|---|---|---|
| 200 | 5 | 3 | ~12 seconds (test) |
| 9,500 | 50 | 300 | ~47 hours (Phase 1) |
| 50,000 | 50 | 100 | ~12 hours (Phase 2 rule-based) |

### RunPod RTX 4090

| Citizens | Steps | Runs | LLM | Estimate |
|---|---|---|---|---|
| 50,000 | 50 | 100 | No | ~2 hours |
| 50,000 | 50 | 10 | Yes (8B) | ~1 hour (probe run) |
| 50,000 | 50 | 100 | Yes (8B) | ~6 hours |

> **Dissertation recommendation:** 100 runs `--no-llm` for statistical power. 10 runs `--use-llm` separately for LLM dialogue examples in dissertation write-up.

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
| Coup Risk | 0.45 | Post-2021 estimate |
| Brain Drain Rate | 0.35 | Post-2021 emigration estimate |

---

## Seven Constitutional Safeguards

| Safeguard | Description |
|---|---|
| S.1 | Chancellor 5-year cooling-off before re-eligibility |
| S.2 | Merit exam independence — rotating Analysis Council panel |
| S.3 | Ethnic Council youth mandate — at least one member under 40 |
| S.4 | IIG single term + data sovereignty — Court holds all data |
| S.5 | Analysis Council transparency — publish methodology 14 days before veto |
| S.6 | Rights absolute — `rights_suspendable = False`, no mechanism exists |
| S.7 | Generational renewal — mandatory 10-year Citizens Assembly review |

---

## Known Issues

| Issue | Status |
|---|---|
| `mesa==2.3.0` via pip only — never `brew install mesa` | ⚠️ Always check |
| All `__init__.py` files must exist in every folder | ⚠️ Required |
| Sequential execution on Mac — no multiprocessing | By design |
| Article 19 (Tatmadaw transition) not yet written | Pending |
| Citizens Assembly veto confirmation not wired in chambers.py | Pending |

---

## Target Publications

- **Primary:** JASSS (Journal of Artificial Societies and Social Simulation)
- **Secondary:** Government Information Quarterly
- **Tertiary:** PLOS ONE

---

## Author

Kaung Htet | MSc Data Science | University of Hertfordshire
GitHub: [KaungOrYours](https://github.com/KaungOrYours/project-ka-nova)
Deadline: December 2026