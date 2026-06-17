# Ka-Nova Codebase Knowledge

Factual reference derived from reading every Python file in `ka-nova.zip`. Values, names, and behaviours below are taken directly from the source. Nothing is inferred beyond what the code states.

Repository layout (project Python files only; `venv/`, `__pycache__/`, CSV results excluded):

```
config/constitution.py
config/__init__.py                                   (empty)
config/constitution_2008_encoding/constitution_2008_template.py
config/constitution_2008_encoding/README.md
agents/citizen.py
agents/official.py
agents/oversight.py
agents/foreign.py
agents/institutional.py
agents/__init__.py                                   (empty)
institutions/chambers.py
institutions/court.py
institutions/iig.py
institutions/__init__.py                             (empty)
feedback/loops.py
feedback/__init__.py                                 (empty)
model.py
model_phase3.py
run.py
run_phase3.py
scenarios/run_a.py
scenarios/run_c.py
scenarios/__init__.py                                (empty)
analysis/kpi.py
analysis/__init__.py                                 (empty)
charts/visualize.py
engine/elite_agents.py
engine/external_layer.py
engine/hybrid_engine.py
engine/social_media.py
engine/__init__.py                                   (empty)
archive/model_hybrid.py
```

Non-Python (present, not requested in detail): `README.md`, `LICENSE`, `requirements.txt`, `ka-nova-phase2.html`, `results/`, `results_phase2/`, `results_phase3/`.

---

## TOP-OF-DOCUMENT: WHAT IS MISSING OR BROKEN (read this first)

### Files that the prior documentation expected but DO NOT exist
- **`scenarios/run_b.py` does not exist.** Only `run_a.py` and `run_c.py` are present. Scenario B is still runnable through `run.py` directly (it constructs `KaNovaModel(scenario="B")`), but there is no dedicated B scenario script.
- **`config/constitution_2008.py` does not exist.** The 2008 constitution exists only as a TEMPLATE at `config/constitution_2008_encoding/constitution_2008_template.py`, still containing **17 `???` placeholders**. `model_phase3.py` does `from config.constitution_2008 import CONSTITUTION_2008`, which therefore raises `ImportError`; `CONSTITUTION_2008_AVAILABLE` resolves to `False` and Scenario C in Phase 3 silently falls back to the MFU constitution.
- **`engine/elite_agents_v3.py` does not exist.** `model_phase3.py` tries `from engine.elite_agents_v3 import EliteAgentLayerV3`; this fails, so `ELITE_V3_AVAILABLE = False` and it falls back to `engine.elite_agents.EliteAgentLayer`.

### Files present but not in the prior documentation
- Entire `engine/` package: `elite_agents.py`, `external_layer.py`, `hybrid_engine.py`, `social_media.py`.
- `model_phase3.py`, `run_phase3.py`.
- `config/constitution_2008_encoding/constitution_2008_template.py`.
- `archive/model_hybrid.py`.

### Confirmed-implemented items that prior memory called "unwritten / not simulated"
- **Article 19 (Tatmadaw transition) IS written** in `config/constitution.py` as `TatmadawTransitionConfig` (e.g. `TRUST_GAIN_PER_CLEAN_YEAR = 0.01`), and is applied in `model_phase3._scenario_a_rules()`.
- **Citizens Assembly veto confirmation IS implemented** in `institutions/chambers.py` (`_citizens_assembly_veto_confirmation`, 320-member sample) — though it contains a bug (see below).

### Active bugs / inconsistencies found in code (each detailed in its file section)
1. **Gini stuck ≈0.570 root cause** — `FederalDevFundAgent._calculate_gini` (`agents/institutional.py`) computes Gini from state-level `gdp` shares only; redistribution writes to `budget` / `ethnic_direct_fund`, never to `gdp`, so the Gini metric never moves. A second, competing Gini (`model.get_gini_coefficient`) computes from citizen `income`.
2. **Merit self-test will fail** — `agents/citizen._calculate_merit` docstring and the `__main__` self-test use v6 weights `0.40/0.30/0.20/0.10`, but the live calculation pulls v7 `CONSTITUTION` weights `0.35/0.25/0.20/0.20`. The "Match" assertion in the self-test mismatches.
3. **Citizens Assembly trust read bug** — `chambers._citizens_assembly_veto_confirmation` reads `getattr(citizen, "trust", 0.50)`, but the attribute is `trust_score`; trust therefore always defaults to `0.50`.
4. **IIG post-service restriction no-op** — `iig._enforce_post_service_restrictions` registers IIG agent IDs (20000+) then disqualifies `OfficialAgent`s whose id is in that registry; official IDs start at 10000+, so the sets never overlap and nothing is disqualified.
5. **Two separate feedback-loop implementations** — `feedback/loops.py` (`FeedbackEngine`) is used **only by `model_phase3.py`**. `model.py` (Phase 2) has its OWN inline 12 loops. They are not the same code.
6. **Two coup mechanisms for Scenario C** — `model.py` has built-in Scenario-C coup logic (70% success on `coup_risk > 0.70`); `scenarios/run_c.py` ALSO applies its own coup cycle (`coup_success_probability = 0.55`, every 10 years). Running C via `scenarios/run_c.py` stacks both; running via `run.py` uses only the model's.
7. **`_weighted_memory` docstring mismatch** — `agents/citizen` docstring says weights `[0.50, 0.30, 0.20]`; actual list is `[0.50, 0.30, 0.15, 0.03, 0.02]`.
8. **`SALib` is not implemented** — `analysis/kpi.py` docstring claims "Sensitivity analysis (SALib)"; SALib is never imported. `SensitivityAnalyzer` uses run-to-run variance instead. SALib is commented out in `requirements.txt`.
9. **Calibration target mismatch** — `analysis/kpi.MYANMAR_BASELINES["ethnic_harmony"] = 0.22`, but `model.py` initialises `ethnic_harmony` shared data at `0.35`. Year-zero calibration of that KPI compares against 0.22.
10. **Docstring v6 residue** — Several docstrings still describe the v6 "40/40/20" split and "unanimous (1.00) veto": `feedback/loops.py` (E1, E3), `scenarios/run_a.py`, `institutions/court.py` (500-member review). The executable v7 code uses 35/35/30 and 0.75 veto.
11. **Config vs actual agent counts diverge** (see `config/constitution.py` SimulationConfig vs `model.py` `_create_agents`).
12. **Config states tuple (4) vs actual states (14)** — `SimulationConfig.SIMULATION_STATES` lists 4 names; the live models build 14 states.
13. **`model_phase3` shared-data key mismatch** — `_scenario_a_rules` checks `coup_attempted`; `_scenario_c_rules` writes `coup_succeeded`. The model elsewhere uses `simulation_failed` / `coup_risk`.
14. **`model.py` redundant no-op** — in `_loop_E3_resource_revenue`, the line `agent.income = agent.income`.
15. **`constitution.validate()`** uses the convoluted check `not self.emergency.RIGHTS_UNTOUCHED is False`.

---

# CONFIG

## `config/constitution.py`
Path: `config/constitution.py`

Imports: `from __future__ import annotations`, `dataclasses` (`dataclass`, `field`), `typing` (`Dict`, `List`, `Tuple`).

Structure: 22 `@dataclass(frozen=True)` config classes + a master `MFUConstitution` class + a module-level singleton `CONSTITUTION = MFUConstitution()`.

### Dataclasses and key parameters (v7 canonical values)
- **`FoundationalConfig`** — state/union identity, founding principles.
- **`RightsConfig`** — `RIGHTS_VIOLATION_TRUST_DROP` (used by feedback P1); rights are absolute / non-suspendable.
- **`MeritConfig`** — merit weights `PERFORMANCE=0.35`, `EDUCATION=0.25`, `PEER_REVIEW=0.20`, `COMMUNITY=0.20`; `MERIT_MIN_PUBLIC_OFFICE = 0.60`; `RECERTIFICATION_INTERVAL = 4` (years); `RECERTIFICATION_FAIL_THRESHOLD = 0.60`.
- **`ExecutiveConfig`** — Chancellor/President terms, cooling-off (Safeguard 1, 5-year).
- **`ChamberConfig`** — three-chamber thresholds: Analysis Council veto `ANALYSIS_THRESHOLD = 0.75` (qualified supermajority); Congress / Ethnic confirm `0.51`.
- **`JudiciaryConfig`** — `JUDGE_COUNT = 11`, `RULING_THRESHOLD = 6`, `JUDGE_TERM = 10`, `COURT_SUPERMAJORITY_FOR_TOTAL_RUIN = 8` (of 11).
- **`IIGConfig`** — `INVESTIGATION_TRIGGER = 0.70`, `ENTRY_MERIT_MIN = 0.85`, `MAX_AGENTS = 600`, `OPEN_INVESTIGATION_THRESHOLD = 0.51`, `PROCEED_PROSECUTION = 0.67`, partner eligibility 5 years.
- **`FederalConfig`** — resource split `STATE_SHARE = 0.35`, `FEDERAL_SHARE = 0.35`, `ETHNIC_DIRECT_SHARE = 0.30`; `GINI_THRESHOLD = 0.45`; `STATE_GDP_CAP`; trust acceleration: `TRUST_ACCELERATION_MULTIPLIER = 1.50`, `TRUST_ACCELERATION_TRIGGER_CORRUPTION = 0.20`, `TRUST_ACCELERATION_TRIGGER_YEARS = 5`.
- **`MilitaryConfig`** — `COUP_TRIGGER_LOYALTY = 0.30`, `COUP_TRIGGER_APPROVAL = 0.20`; National Service: `NS_ETHNIC_EXPOSURE_BOOST`, `NS_LOYALTY_BOOST`; scorched-earth/No-Gun domestic ROE (Article 17).
- **`EconomicConfig`** — Economic Check & Balance triggers; 49% foreign cap (Article 10.3).
- **`ScienceConfig`** — `PHD_KNOWLEDGE_CAPITAL_BOOST`, `RESEARCHER_ROYALTY_RATE` (Article 11; 15% royalty), free tuition + stipend.
- **`AmendmentConfig`** — `CITIZENS_ASSEMBLY_SIZE = 320`; amendment thresholds; 10-year review (Article 12.3).
- **`TransitionConfig`** — transition timeline.
- **`SafeguardConfig`** — 7 safeguards; `ASSEMBLY_SIZE = 500` (NOTE: conflicts with `AmendmentConfig.CITIZENS_ASSEMBLY_SIZE = 320`; chambers/court use 320).
- **`CryptoJusticeConfig`** — blockchain hashing for evidence / shame register.
- **`EmergencyConfig`** — `RIGHTS_UNTOUCHED` flag; 180-day limit (Article 16).
- **`ROEConfig`** — rules of engagement.
- **`PsychConfig`** — psychological health screening (Article 18).
- **`TotalRuinConfig`** / shame register — Total Ruin trigger `corruption > 0.85`.
- **`TatmadawTransitionConfig`** (Article 19, defined line ~1101) — `TRUST_GAIN_PER_CLEAN_YEAR = 0.01` (annual trust gain if no coup). **This is the "Article 19" gap that is in fact written.**
- **`NorthStarConfig`** — 50-year horizon; `TARGET_SEA_GDP_RANK = 3`; `TARGET_CORRUPTION_INDEX = 0.05`.
- **`SimulationConfig`** — `CITIZEN_AGENTS = 9500`, `TIME_STEPS = 50`, `RUNS_PER_SCENARIO = 100`, `TOTAL_RUNS = 300`; year-zero: `YEAR_ZERO_CORRUPTION = 0.72`, `TRUST = 0.22`, `GINI = 0.55`, `EMPLOYMENT = 0.58`, `ETHNIC_TENSION = 0.68`; archetype proportions `civic_champion 0.15, pragmatic_survivor 0.30, ethnic_loyalist 0.20, ambitious_meritocrat 0.15, disillusioned_youth 0.10, rural_traditionalist 0.07, trauma_carrier 0.03`. Also `OFFICIAL_AGENTS`, `OVERSIGHT_AGENTS`, `INSTITUTIONAL_AGENTS`, `SIMULATION_STATES` (tuple of 4), `MULTIPROCESS = True`. **Config agent totals do not match the agents actually created (see model.py).**

### `MFUConstitution`
- `__init__` instantiates every config as an attribute (e.g. `self.merit`, `self.federal`, `self.military`, `self.tatmadaw_transition`, `self.simulation`, …).
- `validate()` — sanity checks; contains the convoluted clause `not self.emergency.RIGHTS_UNTOUCHED is False`.
- `summary()` — prints/returns a constitution summary.
- Module singleton: `CONSTITUTION = MFUConstitution()`.

Bugs / inconsistencies:
- `SafeguardConfig.ASSEMBLY_SIZE = 500` vs `AmendmentConfig.CITIZENS_ASSEMBLY_SIZE = 320` (the latter is what the runtime uses).
- `SimulationConfig.SIMULATION_STATES` = 4 states; runtime uses 14.
- `SimulationConfig` agent counts do not match `model.py` creation.

## `config/constitution_2008_encoding/constitution_2008_template.py`
Path: `config/constitution_2008_encoding/constitution_2008_template.py`

Purpose (from docstring): encode Myanmar's 2008 Military Constitution as a parameter registry mirroring `constitution.py`'s dataclass architecture, for Scenario C. Authored by "Patil Devyani Anil (fourth author)"; architecture owner Kaung Htet. PDF source URL in docstring.

Imports: `from __future__ import annotations`, `dataclasses` (`dataclass`, `field`), `typing` (`Dict`, `List`, `Tuple`).

Dataclasses (all `@dataclass(frozen=True)`, mirroring `constitution.py`): `FoundationalConfig`, `RightsConfig`, `MeritConfig` (commented "NO MERIT SYSTEM IN 2008"), `ExecutiveConfig`, `ChamberConfig`, `JudiciaryConfig` (`CONSTITUTIONAL_TRIBUNAL_SIZE = 9`, Section 320), `IIGConfig` (commented "NO IIG IN 2008"), `FederalConfig`, `MilitaryConfig` (commented "DEFINING CHAPTER"), `EconomicConfig`, `ScienceConfig`, `AmendmentConfig`, `TransitionConfig`, `SafeguardConfig` (commented "NO SAFEGUARDS EQUIVALENT"), `CryptoJusticeConfig`, `EmergencyConfig` (rights CAN be suspended), `ROEConfig`, `PsychConfig`, `NorthStarConfig`, `SimulationConfig` (`CONSTITUTIONAL_FRAMEWORK = "2008_myanmar_military_constitution"`). Master: `Myanmar2008Constitution`; singleton `CONSTITUTION_2008 = Myanmar2008Constitution()`. `__main__` prints "loaded successfully".

Bugs / inconsistencies:
- **17 `???` placeholders remain unfilled.**
- File is at `config/constitution_2008_encoding/constitution_2008_template.py`, not at `config/constitution_2008.py`, so `model_phase3`'s import fails.

---

# AGENTS (Tier 1–5)

## `agents/citizen.py`
Path: `agents/citizen.py`

Imports: `random`, `math`, `collections.deque`, `typing`, `mesa.Agent`, `from config.constitution import CONSTITUTION`.

Module-level data:
- `ARCHETYPES` — 7 archetypes with behavioural parameters.
- `ETHNIC_GROUPS` — 8 groups.
- `SIMULATION_STATES` — 14-key dict of states with weights.
- `ETHNIC_ARCHETYPE_PROPORTIONS` — 8×7 matrix (56 combinations), asserted to sum to 1.0.

### `CitizenAgent(Agent)`
Five-layer agent (perception / decision / action / learning / life-course). Key attributes include `trust_score`, `grievance`, `merit_score`, `corruption_score`, `income`, `is_alive`, `has_emigrated`, `is_protesting`, `is_phd_candidate`, `national_service_completed`, `ethnic_cross_exposure`, `constitutional_loyalty`, `age`, `ethnicity`, `state_id`, `archetype`.

Methods (purpose):
- `step` — runs perceive → decide → act → learn → life-course.
- `_perceive_environment` — reads `shared_data`/environment signals.
- `_weighted_memory` — recency-weighted memory. **Docstring says weights `[0.50,0.30,0.20]`; actual list `[0.50,0.30,0.15,0.03,0.02]`.**
- `_make_decisions` and sub-deciders: `_decide_tax_compliance`, `_decide_protest`, `_decide_emigration`, `_decide_bribery`, `_decide_report_corruption`, `_decide_phd_application`.
- `_execute_actions` and sub-actions: `_pay_tax`, `_calculate_progressive_tax`, `_work`, `_progress_phd`, `_execute_protest`.
- `_begin_national_service`.
- `_update_thresholds`, `_update_grievance`.
- `_life_course_update`, `_die`.
- `_calculate_merit` — pulls v7 weights from `CONSTITUTION.merit`. **Docstring + `__main__` self-test use v6 `0.40/0.30/0.20/0.10`; the self-test "Match" assertion fails.**
- `_check_tax_exempt`.
- `receive_signal`, `observe_*`.
- `is_public_office_eligible`, `is_iig_academy_eligible`.
- `get_state_dict`.

### `CitizenPopulation` (factory)
- `create_population(n=9500)` — uses the universal `_calculate_archetype_counts` (NOT the ethnic-specific path).
- `_calculate_archetype_counts` — archetype counts from proportions.
- `_calculate_ethnic_archetype_counts` — 56-combination counts (census-based, Bamar 0.68 etc.). **Defined but NOT used by `create_population`; only `model_phase3._create_agents_phase3()` calls it.**
- `_assign_state` — 14 states with weights.
- `_assign_ethnicity` — per-state census composition.
- `_assign_age` — Myanmar population pyramid.

Bugs / inconsistencies: `_calculate_merit` self-test mismatch; `_weighted_memory` docstring mismatch; ethnic-archetype path unused at Phase-2 population creation.

## `agents/official.py`
Path: `agents/official.py` (header "v2.0")

Imports: `sys`/`os` path hack, `random`, `typing`, `mesa.Agent`, `from config.constitution import CONSTITUTION`, citizen imports. Module dict `OFFICIAL_ROLES` (6 roles).

### `OfficialAgent(CitizenAgent)`
Corruption, policy voting, psychological screening, recertification, disqualification, total-ruin exposure, coalition, approval rating, term mechanics. Attributes include `corruption_score`, `corruption_tolerance`, `merit_score`, `approval_rating`, `known_shame_register_victim`, `psych_probation`. Methods include `_calculate_merit` (inherited/overridden), `_fail_recertification`, corruption/coalition/approval updates.

### `ChancellorAgent` / `PresidentAgent`
- Both set `PHASE2_LLM_CONTROLLED = True`; their `step()` is a no-op (decisions come from `EliteAgentLayer`).
- **Stored on the model as `model.chancellor_agent` / `model.president_agent`; NOT added to the Mesa scheduler.**
- `PresidentAgent.cast_tiebreaker_vote`; `ChancellorAgent._implement_policy`, `_command_military_check` preserved.

### `EthnicLeaderAgent`
- `cast_veto_vote`, `consider_presidential_run`.

### `AnalysisCouncilMember`
- `cast_analysis_vote` (votes "no" when quality `< 0.70`), `_publish_methodology`.

### `OfficialPopulation` (factory)
- `create_population(model)` — IDs from 10000. Creates 8 ministers + 8 ethnic leaders + 10 analysis-council + 50 congress (= 76 scheduled), plus President + Chancellor stored on the model (not scheduled).

## `agents/oversight.py`
Path: `agents/oversight.py`

Imports: standard + `hashlib`, citizen import, `CONSTITUTION`.

### `IIGAgent(CitizenAgent)`
- Entry merit `0.85`, integrity 0.82–0.98, `chamber_eligible = False` permanently. Methods: scan, investigate, evidence (blockchain hash via `hashlib`), prosecution, partner vote. Counters `cases_opened`, `cases_solved`.

### `IIGDirector(IIGAgent)`
- 6-year term, `vote_weight = 0` (tiebreaker only). `_oversee_all_divisions` sets `iig_effectiveness = solved/opened`.

### `CourtJudge(CitizenAgent)`
- 10-year term, independence 0.75–0.98. Methods: `_review_prosecution_queue`, `_check_total_ruin_conditions`, `_count_court_votes`, `_certify_total_ruin`, `_review_methodology_challenges`, `_review_rights_complaints`, `_review_emergency_requests`, `_update_independence`.

### `ArbitrationJudge(CitizenAgent)`
- Elected/merit-based; `_resolve_disputes`.

### `OversightPopulation` (factory)
- `create_population(model)` — IDs from 20000. Creates 1 IIG director + 49 IIG agents + 11 judges + 10 arbitration judges = **71**.

Bug: `CourtJudge._certify_total_ruin` does not check `not total_ruin_triggered` (model and `ConstitutionalCourtSystem` do), creating a double-processing risk for the prosecution/total-ruin queue.

## `agents/foreign.py`
Path: `agents/foreign.py`

Imports: standard, `CONSTITUTION`.

### `ForeignInvestorAgent`
- Perception lag 1–3 years; invest / withdraw / tech-transfer / return. Attributes `is_invested`, `capital_invested`, `technology_transferred`.

### `NeighboringStateAgent`
- Relationship / trade / security (scorched-earth deterrence) / insurgent support / sanctions.

### `InternationalOrgAgent`
- Monitor / conditionality / aid disburse–suspend / public statements.

### `IllicitNetworkAgent`
- Risk / operate / corrupt officials / detection / adjust `network_size`. Attribute `is_active`.

### `ForeignPopulation` (factory)
- `create_population(model)` — IDs from 30000. 50 investors + 4 named neighbours (China, India, Thailand, Bangladesh) + 6 orgs (UN_Development, World_Bank, ASEAN, UN_Rights, IMF, Bilateral_Aid) + 40 illicit = **100**.

## `agents/institutional.py`
Path: `agents/institutional.py`

Imports: standard, `CONSTITUTION`.

### `CentralBankAgent`
- Taylor-rule monetary policy: interest / inflation / exchange rate.

### `FederalDevFundAgent`
- Resource split; `_calculate_gini` (state-`gdp` basis); `_check_triggers` (Economic Check & Balance).
- **Docstring says "40/40/20"; actual code uses v7 0.35/0.35/0.30.**
- **Root cause of the stuck-Gini bug: `_calculate_gini` reads state `gdp` shares only; redistribution writes to `budget` / `ethnic_direct_fund`, never to `gdp`.**

### `NationalShameRegisterAgent`
- Blockchain-style chain; deterrence reduces officials' `corruption_tolerance`.

### `TaxSystemAgent`
- Poverty line, minimum wage, evasion → `high_treason_referrals`.

### `EconomicCheckBalanceAgent`
- 3 triggers / 3 enforcers.

### `InstitutionalPopulation` (factory)
- `create_population(model)` — IDs from 40000. **5 agents**: CentralBank, FederalDevFund, NationalShameRegister, TaxSystem, EconomicCheckBalance.

---

# INSTITUTIONS

## `institutions/chambers.py`
Path: `institutions/chambers.py`

### `Policy`
- Data object representing a submitted policy (quality, sponsor, votes).

### `ThreeChamberSystem`
- `submit_policy`, `process_votes`, `_tally_chamber`, `_tally_analysis` (0.75 threshold + Citizens Assembly confirm at 0.51 + escalation after 90 days), `_citizens_assembly_veto_confirmation` (320-member sample), `_check_deadlock` (3+ deadlocks → court), `generate_annual_policy`.

Bug: `_citizens_assembly_veto_confirmation` reads `getattr(citizen, "trust", 0.50)`; the attribute is `trust_score`, so trust always defaults to `0.50`.

## `institutions/court.py`
Path: `institutions/court.py`

### `ConstitutionalCourtSystem`
- `annual_session` processes: prosecution queue (8/11 supermajority), rights complaints, methodology challenges, emergency certification, IIG data custody, `_conduct_constitutional_review`.
- Checks `not total_ruin_triggered` before processing.

Bug: `_conduct_constitutional_review` docstring says 500 members but uses `CITIZENS_ASSEMBLY_SIZE = 320`.

## `institutions/iig.py`
Path: `institutions/iig.py`

### `PartnershipCouncil`
- `get_partners`, `vote` (quorum 60%; thresholds open 0.51 / prosecute 0.67).

### `IIGSystem`
- 9 divisions; `_process_tip_pipeline`, `_enforce_post_service_restrictions`, `_update_effectiveness`, `annual_operations`.

Bug: `_enforce_post_service_restrictions` registers IIG agent IDs (20000+) then disqualifies officials whose id is in the registry; official IDs are 10000+, so the two sets never overlap (no-op).

---

# FEEDBACK

## `feedback/loops.py`
Path: `feedback/loops.py` (header "v1.0")

Imports: `sys`/`os` path hack, `random`, `numpy`, `typing.TYPE_CHECKING`, `from config.constitution import CONSTITUTION`. `TYPE_CHECKING` import of `KaNovaModel`.

**Used only by `model_phase3.py`** (`self.feedback_engine = FeedbackEngine(self)`). `model.py` does NOT import this — it has its own inline loops.

### `FeedbackEngine`
- `__init__(model)` — builds `loop_history` dict for P1–P4, E1–E4, S1–S4.
- `run_all()` — runs all 12 loops in order P→E→S, then `_record_outputs`.
- **Political:** `loop_P1_trust_legitimacy` (v7 trust acceleration via `CONSTITUTION.federal.TRUST_ACCELERATION_*`, supports vectorised `citizen_array` path), `loop_P2_iig_corruption` (effectiveness = solved/opened; B ×0.85, C capped at 0.10), `loop_P3_coup_probability` (military loyalty from const-commitment A 0.80/B 0.55/C 0.25), `loop_P4_election_merit` (recert every `RECERTIFICATION_INTERVAL` years).
- **Economic:** `loop_E1_state_competition` (**docstring "40/40/20 / 40% cap"**), `loop_E2_foreign_investment`, `loop_E3_resource_revenue` (**docstring "40/40/20"**; ECB trigger when `gini > GINI_THRESHOLD`), `loop_E4_phd_economy` (`PHD_KNOWLEDGE_CAPITAL_BOOST`, `RESEARCHER_ROYALTY_RATE`).
- **Social:** `loop_S1_national_service` (NS exposure/loyalty boosts), `loop_S2_grievance_protest` (branching on scenario; A reduces grievance, B 40% suppression chance, C always suppresses), `loop_S3_cultural_offense`, `loop_S4_shame_register` (S-curve deterrence: <5 minimal, 10–30 accelerating, 30+ plateau ≤0.40).
- `_record_outputs`, `get_loop_summary`, `get_loop_history_df` (pandas).
- `__main__` — mock model self-test with 4 states (`bamar_central`, `shan_eastern`, `karen_southern`, `kachin_northern`).

---

# MODELS

## `model.py`
Path: `model.py` (header "Phase 2")

Imports: `mesa` (`Model`, `RandomActivation`, `DataCollector`), `numpy`, `random`, all agent factories, `from engine.elite_agents import EliteAgentLayer`, `CONSTITUTION`.

28 module-level KPI reporter functions (`get_corruption_index` … `get_psych_probation_count`).

### `KaNovaModel(Model)`
- `__init__(scenario, seed, n_citizens, use_llm=False)`. Builds scheduler `RandomActivation`, `EliteAgentLayer`, states, shared data, agents, DataCollector. `__main__` test runs scenario A, seed 42, `n_citizens=500`.
- `_initialize_states` — **14 states** (full per-state dicts).
- `_initialize_shared_data` — large dict; includes `elite_budget_impact = 0.07`, `elite_ethnic_weights = [1.0]*8`, `elite_coup_signal = False`, `elite_decisions_log`, `ethnic_harmony` defaulted around `0.35` in the model path.
- `_create_agents` — adds the 5 tiers to the scheduler (citizens 9500 + officials 76 + oversight 71 + foreign 100 + institutional 5). President/Chancellor stored on model, not scheduled.
- `_apply_year_zero_calibration` — corruption 0.72 / trust 0.22 / gini 0.55 / stability 0.18 / iig 0.05 / coup 0.45 + per-state corruption & trust tables for 14 states.
- `step()` order: `elite_layer.step` → coup-signal handling (A suppresses, else escalates) → broadcast → `schedule.step` → network effects → institutional enforcement (`_enforce_iig_triggers`, `_enforce_total_ruin`, `_enforce_coup_detection`/`_attempt_coup` [A blocked; C 70% success → `simulation_failed`], `_enforce_rights`, `_enforce_merit_disqual`) → 12 inline feedback loops (P1 trust w/ v7 1.5× accel, P2 iig-corruption, P3 coup, P4 election-merit, E1 state-competition, E2 FDI, E3 resource-revenue [NumPy rank-weighted Gini "fix", scenario A only], E4 phd, S1 NS, S2 grievance-protest, S3 cultural, S4 shame) → scenario rules (A safeguards / C decay + rights violations) → state env update → special events (elections / recert / 10-yr review) → snapshot → collect → year++ → reset counters.
- `_loop_E3_resource_revenue` — contains a "PHASE 2 GINI FIX" adding NumPy rank-weighted transfers to `agent.income` only in scenario A, gated on `gini > GINI_THRESHOLD (0.45)`; contains the redundant line `agent.income = agent.income`.
- `get_gini_coefficient` (model reporter) — Gini from **citizen `income`** (a different basis than `FederalDevFundAgent._calculate_gini`, which uses state `gdp`).
- `run()`, `get_results()`, `summary()`.

Bugs / inconsistencies: two competing Gini computations; the `agent.income = agent.income` no-op; config-vs-actual agent counts; config 4 states vs 14 built.

## `model_phase3.py`
Path: `model_phase3.py`

Imports: `sys`/`os` path hack, `random`, `numpy`, `mesa` (`Model`, `RandomActivation`, `DataCollector`); `from config.constitution import CONSTITUTION as CONSTITUTION_MFU`; `try: from config.constitution_2008 import CONSTITUTION_2008` (fails → unavailable); agent factories incl. `AnalysisCouncilMember`, `IIGAgent`; `ThreeChamberSystem`, `ConstitutionalCourtSystem`, `IIGSystem`, `FeedbackEngine`; `ExternalLayer`, `SocialMediaChannel`; `try: from engine.elite_agents_v3 import EliteAgentLayerV3 as EliteAgentLayer` (fails → falls back to `engine.elite_agents.EliteAgentLayer`).

KPI reporters (same as model.py) plus `get_vpn_floor`, `get_social_media_openness`, `get_active_shocks`, `get_china_influence`.

### `KaNovaModelPhase3(Model)`
- `__init__(scenario="A", seed=None, n_citizens=11000, use_llm=False)`. **Default `n_citizens = 11000`.** Constitution switch (C uses 2008 if available, else MFU with warning). Builds `EliteAgentLayer`, `ExternalLayer(seed=external_seed)`, `SocialMediaChannel(scenario, seed)`, states, shared data, institutions incl. `FeedbackEngine`, agents, DataCollector. `max_years = CONSTITUTION_MFU.simulation.TIME_STEPS` (50).
- `_initialize_states` — **14 states** (`bamar_central`, `mandalay`, `magway`, `bago`, `yangon`, `ayeyarwady`, `tanintharyi`, `shan_eastern`, `kachin_northern`, `kayah`, `karen_southern`, `chin`, `mon`, `rakhine`) with random year-zero ranges.
- `_initialize_shared_data` — Myanmar baselines; `active_ethnic_groups` 8 groups; `external`/`social_media` placeholders.
- `_create_agents_phase3` — Tier 1 citizens built via `CitizenPopulation._calculate_ethnic_archetype_counts(n)` (the 56-combination path); Tiers 2–5 via their factories.
- `step()` order: 0 external layer → 1 social media → 2 elite deliberation (+coup-signal handling: A reduces `coup_risk`, else raises) → 3 broadcast → 4 schedule.step → 5 `feedback_engine.run_all()` → 6 scenario rules → 7 institutions (`chambers.generate_annual_policy`, `chambers.process_votes`, `iig_system.annual_operations`) → 8 state update → 9 collect → 10 year++.
- `_apply_scenario_rules` → `_scenario_a_rules` / `_scenario_c_rules` (**no B branch**).
- `_scenario_a_rules` — applies Article 19: `transition.TRUST_GAIN_PER_CLEAN_YEAR` when `not coup_attempted`.
- `_scenario_c_rules` — random rights violations; iig decay; if `coup_risk > 0.70` then 70% chance sets `coup_succeeded` + `simulation_failed`.
- `get_results()`.
- `__main__` — quick test, 200 citizens, 5 steps, scenarios A and C.

Bugs / inconsistencies: failing 2008/v3 imports (fallbacks); `_scenario_a_rules` reads `coup_attempted` while `_scenario_c_rules` writes `coup_succeeded` (key mismatch); no Scenario B handling.

## `archive/model_hybrid.py`
Path: `archive/model_hybrid.py` (header "Phase 2 — Hybrid Model")

Imports: `random`, `numpy`, `logging`, `mesa` (`Model`, `RandomActivation`, `DataCollector`); `CONSTITUTION`; full agent classes from official/oversight/foreign/institutional; `from engine.elite_agents import EliteAgentLayer`; `from engine.hybrid_engine import init_population, update_citizens, apply_feedback_loops, recompute_kpis, SCENARIO_MODS, TRUST_ACCEL_CORR_CEIL, TRUST_ACCEL_MIN_YEARS`.

### `HybridKaNovaModel(Model)`
- `__init__(scenario="A", seed=None, n_citizens=50_000, use_llm=False)`. Citizens as NumPy arrays (via `init_population`); ~256 Mesa government agents; 3 LLM elites. **14 states** with full dicts (each includes `ethnic_direct_fund`, `public_services`, `merit_integrity`, `military_presence`).
- DataCollector reporters include `elite_budget_impact`, `elite_coup_signal`, `active_foreign_investors`.
- `_init_shared_data`, `_create_gov_agents` (no citizens scheduled), `step()` (elite → NumPy citizen update → Mesa step → institutional enforcement → loops → scenario rules → recompute KPIs → collect), `_sync_shared_data_from_sim_state`, enforcement methods (`_enforce_iig_triggers`, `_enforce_total_ruin`, `_enforce_coup_detection`, `_attempt_coup`, `_enforce_rights_protections`), inline loops (`_loop_P1_trust`, `_loop_P2_iig_corruption`, `_loop_P3_coup`, `_loop_P4_merit`, `_loop_E1_gdp`, `_loop_E2_fdi`, `_loop_E4_phd`, `_loop_S2_protest`, `_loop_S4_shame` — **9 loops, not 12; E3, S1, S3 absent**), `_apply_scenario_rules`, `get_results`, `summary`.

Status: archived; not referenced by any runner.

---

# ENGINE (Phase 2/3 infrastructure)

## `engine/elite_agents.py`
Path: `engine/elite_agents.py`

Imports: `os`, `re`, `json`, `logging`, `numpy`; `dataclasses`; LangChain (`ChatPromptTemplate`, `StrOutputParser`, `ChatOpenAI`) in a `try/except` → `LANGCHAIN_AVAILABLE`.

Config (env-driven): `ELITE_LLM_BASE_URL` (default `http://localhost:11434/v1`), `ELITE_LLM_API_KEY` (default `ollama`), `ELITE_LLM_MODEL` (**default `llama3`**), `ELITE_LLM_TEMP` (0.4). Hidden coup thresholds: `COUP_CORRUPTION_TRIGGER = 0.65`, `COUP_TRUST_TRIGGER = 0.30` (**differ from `CONSTITUTION.military` 0.30/0.20**). `ETHNIC_GROUP_NAMES` (8).

Functions: `build_status_report(shared_data, year, scenario)` (status string; mentions "35% / 35% / 30%"), `parse_decision(response_text, agent_role)` (parses `<DECISION>` JSON; clamps budget_weight 0–1, ethnic_weights 0.3–3.0). System prompts: `CHANCELLOR_SYSTEM` (focus redistribution / Gini→0.35), `PRESIDENT_SYSTEM` (focus trust→0.70), `GENERAL_SYSTEM` (focus stability; private coup threshold corruption>0.65 AND trust<0.30).

### `EliteAgent` (`@dataclass`)
- `role`, `system_prompt`, `llm`. `decide(status_report)` (LLM or rule-based fallback); `_rule_based(status_text)`.

### `EliteAgentLayer`
- `ROLE_WEIGHTS = {chancellor 0.50, president 0.30, general 0.20}`.
- `__init__(use_llm=False)` builds 3 `EliteAgent`s.
- `step(shared_data, year, scenario)` — each decides; weighted budget; ethnic weights normalised to mean 1.0; coup signal (general only, suppressed in A); `budget_impact = clip(budget_weight*0.15, 0, 0.15)`; writes `elite_budget_impact`, `elite_ethnic_weights`, `elite_coup_signal`, appends `elite_decisions_log`.
- `get_fallback_allocation()` (budget_impact 0.07, weights [1]*8), `annual_deliberation(status_report, scenario)` (legacy compatibility).

## `engine/external_layer.py`
Path: `engine/external_layer.py`

Imports: `random`, `numpy`, `dataclasses`, `typing`.

`SHOCK_EVENTS` (10 types: pandemic, regional_conflict, global_recession, natural_disaster, sanctions, oil_price_shock, fdi_boom [positive], coup_in_neighbor, technology_leap [positive], internet_shutdown_pressure) each with probability, duration, intensity range, affected vectors, social-media amp, trust/corruption impact. `INITIAL_VECTORS` and `VECTOR_DRIFT` — **17 vectors** (china 0.75, india, thailand, bangladesh, usa, eu, asean, un_agencies, imf_world_bank, foreign_investors, global_economy, china_proxy_1/2/3, illicit_network_1/2/3).

### `ActiveShock` (`@dataclass`)
- Fields incl. `name`, `year_started`, `duration`, `intensity`, `affected_vectors`, `positive`; property `is_positive`.

### `ExternalLayer`
- `__init__(seed=42)`; `step(year, shared_data)` (drift → fire shocks → apply effects → expire → write `shared_data["external"]` summary incl. `china_influence`, `western_pressure`, `fdi_level`, `illicit_pressure`, `regional_stability`, `un_pressure`, `social_media_signal`, `trust_impact`, `corruption_impact`); `get_china_veto_probability()` (≤0.95), `get_shock_summary()`, `get_vector_trajectory()`. `__main__` runs a 10-year test.

Note: header docstring says "17 population-weighted … vectors" — count is 17 (consistent).

## `engine/social_media.py`
Path: `engine/social_media.py`

Imports: `numpy`, `dataclasses`, `typing`.

Constants: `VPN_FLOOR_INITIAL = 0.35`, `VPN_FLOOR_MAX = 0.70`, `VPN_FLOOR_RISE_PER_SHUTDOWN = 0.01`, `ETHNIC_NETWORK_BONUS = 0.10`, `SHUTDOWN_TRIGGER = 0.15`, `OPENNESS_SCENARIO_A = 1.00`, `OPENNESS_SCENARIO_C_DEFAULT = 0.10`.

### `SocialMediaState` (`@dataclass`)
- Annual channel state fields (raw/effective/final openness, vpn_floor, information_speed, citizen_exposure, shock_amplification, shutdown_attempted, ethnic_network_active).

### `SocialMediaChannel`
- `__init__(scenario, seed=42)`; `step(year, shared_data)` (reads `elite_internet_decision`, `protest_rate`, `external.social_media_signal`; in C, protest>0.15 triggers shutdown, raises VPN floor; applies ethnic-network bonus; classifies speed fast/moderate/slow/suppressed; writes `social_media` + `citizen_information_exposure`); `get_vpn_trajectory()`, `get_suppression_summary()`. `__main__` runs A and C 15-year tests.

## `engine/hybrid_engine.py`
Path: `engine/hybrid_engine.py` (header "Phase 2 — Hybrid Simulation Engine", "50,000 citizens as NumPy arrays")

Imports: `numpy`, **`polars`**, `dataclasses`, `pathlib`, `logging`.

Module data: `STATE_NAMES` (14 real admin divisions: sagaing, mandalay, magway, bago, yangon, ayeyarwady, tanintharyi, shan_eastern, kachin_northern, kayah, karen_southern, chin, mon, rakhine), `STATE_GDP_WEIGHTS` (normalised), `ETHNIC_NAMES` (8), `STATE_ETHNIC_COMP` (14×8 census, row-normalised), `ARCHETYPE_NAMES` (7), `ARCHETYPE_PROPS` (= constitution proportions), `ARCHETYPE_TRUST`, `ETHNIC_HARM_W`. Article VIII v7 constants: `RESOURCE_DIRECT_SHARE = 0.30`, `TRUST_ACCEL_MULT = 1.50`, `TRUST_ACCEL_CORR_CEIL = 0.20`, `TRUST_ACCEL_MIN_YEARS = 5`. `SCENARIO_MODS` for A/B/C (iig_growth, corruption_decay, trust_floor, coup_block, article8, safeguards, trust_accel).

Citizen array columns `[N,8]`: 0 wealth, 1 trust, 2 merit, 3 corruption_exp, 4 grievance, 5 age, 6 brain_drain, 7 employment.

### `SimState` (`@dataclass`)
- Year/scenario, citizen arrays (`pop`, `ethnic_group`, `state_id`, `archetype`), macro KPIs (year-zero baselines), trackers (`low_corruption_streak`, `total_ruin_events`, `elite_log`); property `n_citizens`.

Functions:
- `init_population(n, scenario, rng)` — vectorised init (lognormal wealth calibrated to Gini 0.55, archetype-based trust, etc.).
- `update_citizens(state, budget_impact, ethnic_weights, article8_active, trust_accel, rng)` — vectorised annual update; trust formula `Trust(t+1)=Trust+budget_impact·ethnic_weight − corruption·0.5`; `_article8_transfer` (progressive: bottom 40% ×1.5, top 60% ×0.67 — the NumPy "Gini fix").
- `compute_gini(wealth)`, `recompute_kpis(state)`, `apply_feedback_loops(state, mods, rng)` (P2 iig-corruption, E1 gdp, P1 trust inertia, S4 shame S-curve, E3 ECB redistribution if gini>0.45, stability composite).
- `run_scenario_hybrid(...)` — returns a Polars DataFrame; `_save_checkpoint(...)` writes Parquet (zstd) every 5 years.
- `__main__` self-test.

---

# RUNNERS

## `run.py`
Path: `run.py` (header "Phase 2 … 300 Runs")

Imports: `sys`/`os`, `argparse`, `time`, `json`, `traceback`, `io`, `platform`, `datetime`, `pathlib`, `concurrent.futures` (`ProcessPoolExecutor`, `as_completed`), `pandas`, `numpy`, `tqdm`, `CONSTITUTION`, `from model import KaNovaModel`.

`RESULTS_DIR = results/`; `SCENARIO_DIRS` = scenario_a/b/c. `IS_LINUX` platform flag.

- `run_single(run_id, scenario, n_citizens, n_steps, use_llm=False)` — `seed = run_id*100 + ord(scenario)`; runs a model; returns df / error dict.
- `KaNovaRunner` — `__init__` default `scenarios=["A","C"]`, citizens/steps default from constitution; workers default 64 on Linux else 1; LLM forces workers=1. `run_all` (parallel on Linux else sequential), `_process_result` (writes `run_NNN.csv`), `_finalize` (all_results.csv + run_log.json + `_compute_summary`), `_compute_summary` (final-year mean±std across A/B/C), `_fmt`.
- `parse_args` — `--test`, `--scenario {A,C}`, `--runs`, `--citizens`, `--steps`, `--workers`, `--use-llm/--no-llm`.
- `__main__` — `--test` = 1 run/scenario, 200 citizens, 5 steps; otherwise `scenarios=[args.scenario]` or **`["A","B","C"]`** by default (so a default full run DOES include B even though `--scenario` only allows A/C and no run_b.py exists).

## `run_phase3.py`
Path: `run_phase3.py`

Imports: same families as run.py + `from model_phase3 import KaNovaModelPhase3`.

`RESULTS_DIR = results_phase3/`; `SCENARIO_DIRS` = scenario_a/scenario_c only.

- `run_single(...)` — `seed = run_id*100 + ord(scenario)`; attaches shock count, shutdown count, vpn floor, mean openness to df.
- `KaNovaPhase3Runner(scenario="A", runs=100, n_citizens=11000, n_steps=50, use_llm=False, workers=None)` — `assert scenario in ("A","C")` ("Phase 3 only supports A and C"). One scenario per instance (pod split). `run`, `_process_result`, `_finalize` (per-scenario combined CSV + run_log_{scenario}.json + KPI summary incl. vpn/openness/china), `_fmt`.
- `parse_args` — `--test`, `--scenario {A,C}` (default A), `--runs` (100), `--citizens` (11000), `--steps` (50), `--workers`, `--use-llm`.
- `__main__` — `--test` = 1 run, 200 citizens, 5 steps.

## `scenarios/run_a.py`
Path: `scenarios/run_a.py` (header "v1.0")

Imports: `sys`/`os`, `time`, `pandas`, `pathlib`, `CONSTITUTION`, `from model import KaNovaModel`. `RESULTS_DIR = results/scenario_a`.

- `run_scenario_a(run_id=0, n_citizens=None, n_steps=None, seed=None, verbose=True)` — defaults from constitution; `seed = run_id*100 + ord("A")`; builds `KaNovaModel(scenario="A")`; loops `n_steps`; breaks on `simulation_failed`; writes `run_NNN.csv`; returns df.
- `__main__` — `--runs/--citizens/--steps/--quiet`; combines runs into `scenario_a_combined.csv`.

Docstring lists v6-style rules: "40/40/20 resource split (Article 8.6)" and "Analysis Council unanimous veto (Article 5.7)". Executable behaviour comes from `KaNovaModel` (v7).

## `scenarios/run_c.py`
Path: `scenarios/run_c.py` (header "v1.0")

Imports: `sys`/`os`, `time`, `random`, `pandas`, `pathlib`, `CONSTITUTION`, `from model import KaNovaModel`. `RESULTS_DIR = results/scenario_c`.

`SCENARIO_C_PARAMS`: `corruption_floor 0.60`, `corruption_drift_annual 0.005`, `trust_decay_annual 0.008`, `trust_floor 0.08`, `iig_effectiveness 0.02`, `rights_violation_prob 0.20`, `coup_attempt_interval 10`, `coup_success_probability 0.55`, `brain_drain_annual 0.025`, `gdp_growth_cap 0.025`, `ethnic_tension_floor 0.65`, `fdi_cap 5`.

- `run_scenario_c(...)` — builds `KaNovaModel(scenario="C")`; `_apply_c_initial_conditions`; each year `_apply_c_annual_mechanics` and (every 10 years) `_attempt_coup`; records `coup_count`, `successful_coups`, `coup_years`.
- `_apply_c_initial_conditions(model)` — iig 0.02, corruption_deterrence 0, raises official corruption_tolerance / lowers loyalty, military_presence 0.85, ethnic tension floor, coup_risk 0.35, military_loyalty 0.45.
- `_apply_c_annual_mechanics(model, year)` — corruption drift, trust decay, random rights violations, GDP cap, ethnic tension floor, brain-drain rise, FDI cap, random official corruption rise, knowledge stagnation, grievance rise.
- `_attempt_coup(model, year, seed)` — `attempt_prob = (1−loyalty)·0.60 + (1−trust)·0.40`; success prob `coup_success_probability (0.55)`; returns "none"/"attempted"/"succeeded".
- `__main__` — `--runs/--citizens/--steps/--quiet`; aggregates coup counts; `scenario_c_combined.csv`.

Bug / inconsistency: this script applies its OWN coup mechanics on top of `model.py`'s built-in Scenario-C coup logic (70% success on `coup_risk>0.70`). The two coexist when C is run via this script.

---

# ANALYSIS & CHARTS

## `analysis/kpi.py`
Path: `analysis/kpi.py` (header "v1.0")

Imports: `sys`/`os`, `warnings`, `pathlib`, `typing`, `numpy`, `pandas`, `scipy.stats` (`mannwhitneyu`, `kruskal`, `shapiro`, `ttest_ind`, `pearsonr`), `CONSTITUTION`.

Module data: `KPI_COLUMNS` (16 KPIs incl. `tax_compliance`, `inflation_rate`, `foreign_investors`), `MYANMAR_BASELINES` (corruption 0.72, trust 0.22, gini 0.55, employment 0.58, **ethnic_harmony 0.22**, stability 0.18, iig 0.05, coup 0.45, brain_drain 0.35), `NORTH_STAR_TARGETS` (corruption 0.20, trust 0.70, coup 0.05, ethnic_harmony 0.75, gini 0.35, employment 0.85, brain_drain 0.10, iig 0.75, stability 0.75, north_star_progress 0.80), `SIGNIFICANCE_LEVEL = 0.05`.

Classes:
- `ResultsLoader` — `load` (all_results.csv or individual files), `_load_individual_files` (A/B/C dirs), `_validate`, `_summarize`, `get_final_year`, `get_year`, `get_scenario`.
- `DescriptiveStats` — `compute_all` (final-year stats), `compute_trajectories`.
- `StatisticalTests` (MoS 5) — `run_all_tests` (pairwise A–B, A–C, B–C), `_compare` (Mann-Whitney U primary; t-test if both Shapiro-normal; Cohen's d), `_print_significant`, `kruskal_wallis_test`.
- `CalibrationValidator` (MoS 8) — `validate_year_zero` (<10% error vs `MYANMAR_BASELINES`), `_get_source`.
- `NorthStarAnalyzer` — `compute_progress`, `check_milestone_achievement` (decade milestones at years 10/20/35/50).
- `SensitivityAnalyzer` (claims MoS 3) — `compute_variance_stability` (MoS 4, running-mean stability), `compute_internal_consistency` (MoS 6, expected feedback correlation directions).
- `PublicationTables` — `table_1_scenario_comparison`, `table_2_mos_summary`.
- `KPIAnalysis` — `run_full_analysis` (6-stage pipeline).
- `__main__` — `--results`, `--quick`.

Bugs / inconsistencies: docstring promises SALib sensitivity analysis but SALib is never imported/used; `MYANMAR_BASELINES["ethnic_harmony"] = 0.22` vs model's 0.35 init.

## `charts/visualize.py`
Path: `charts/visualize.py` (header "v1.0")

Imports: `sys`/`os`, `warnings`, `argparse`, `pathlib`, `numpy`, `pandas`, `matplotlib` (`Agg` backend, `pyplot`, `patches`, `GridSpec`), `seaborn`.

Style: `SCENARIO_COLORS` (A teal #1D9E75, B gold #C9A84C, C red #8B1A1A), `SCENARIO_LABELS`, `SCENARIO_LINESTYLES`, `DPI = 300`, figure-size constants, `set_style()`, `add_watermark(fig)`. Loader: `load_results()` (all_results.csv), `get_trajectories(df)`.

Classes:
- `KPITrajectoryCharts` — `KPI_META` (15 KPIs with title/ylabel/lower-is-better); `plot_all`, `plot_single`.
- `ScenarioComparisonCharts` — `plot_all`, `plot_key_kpis_grid`, `plot_violin_comparison`, `plot_scenario_radar`.
- `FeedbackLoopCharts` — `plot_all`, `plot_correlation_heatmaps`, `plot_loop_interactions`.
- `NorthStarChart` — `plot_all`, `plot_composite_trajectory`, `plot_decade_milestones`.
- `CalibrationChart` — `plot`.
- `SummaryDashboard` — `plot`, `_plot_mini_trajectory`, `_plot_final_comparison_bar`.
- `ChartRunner` — `run_all`, `run_single(chart_type)`.
- `__main__` — `--chart` selector.

Output dirs: `charts/kpi`, `charts/feedback`, `charts/comparison`. All charts saved as 300-DPI PNG.

---

# CROSS-CUTTING FACTS

### Agent IDs and tier counts (as actually created, Phase 2 `model.py`)
- Tier 1 Citizens — 9,500 (IDs 0–9,499), 7 archetypes.
- Tier 2 Officials — 76 scheduled (8 ministers + 8 ethnic leaders + 10 analysis council + 50 congress), IDs 10000+; President + Chancellor stored on model, not scheduled.
- Tier 3 Oversight — 71 (1 IIG director + 49 IIG + 11 judges + 10 arbitration), IDs 20000+.
- Tier 4 Foreign — 100 (50 investors + 4 neighbours + 6 orgs + 40 illicit), IDs 30000+.
- Tier 5 Institutional — 5, IDs 40000+.

### States
- `model.py`, `model_phase3.py`, `engine/hybrid_engine.py`, `archive/model_hybrid.py` all use **14 states**. `SimulationConfig.SIMULATION_STATES` (config) lists only 4. State naming differs between files (`bamar_central` in models vs `sagaing`/`mandalay`/… in hybrid_engine).

### Seeding
- All runners: `seed = run_id * 100 + ord(scenario)` (`A`=65, `B`=66, `C`=67).

### Two model lineages
- **Phase 2:** `model.py` (Mesa citizens, inline 12 loops) → run by `run.py`, `scenarios/run_a.py`, `scenarios/run_c.py`. Elite layer: `engine/elite_agents.py`.
- **Phase 3:** `model_phase3.py` (Mesa citizens via 56-combination path, `FeedbackEngine`, `ExternalLayer`, `SocialMediaChannel`) → run by `run_phase3.py`. Default 11,000 citizens, A/C only.
- **Hybrid (archived):** `archive/model_hybrid.py` + `engine/hybrid_engine.py` (NumPy citizens, Polars/Parquet, 9 loops). Not wired to any active runner.

### requirements.txt (dependencies present)
mesa==2.3.0, numpy, pandas, polars, scipy, matplotlib, seaborn, plotly, tqdm, langchain stack (+ langchain-openai, openai), cryptography, statsmodels, pingouin, python-dotenv, pydantic, typing-extensions. **SALib is commented out** ("Phase 3 planned"). Comment warns: never `brew install mesa`; use `pip install mesa==2.3.0`.
