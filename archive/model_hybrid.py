"""
================================================================================
Ka-Nova Phase 2 — Hybrid Model
================================
Combines:
    Citizens (50k)    → NumPy float32 arrays  (instant init, vectorised update)
    Government (~256) → Mesa agents            (full institutional mechanics)
    Elites (3)        → LangChain LLM          (Chancellor, President, General)

Why this is better than pure Mesa at 50k:
    Mesa 50k citizens init:  ~30 minutes per worker
    NumPy 50k citizens init: <1 second per worker

Why this is better than pure hybrid_engine.py:
    hybrid_engine.py has no Mesa agents — IIG, Court, Shame Register, Total Ruin
    are all just scalar approximations. This model has the full institutional
    mechanics running as Mesa agents every step.

Architecture per step:
    1. EliteAgentLayer.step()          LLM deliberation → shared_data
    2. update_citizens()               NumPy vectorised citizen update
    3. Mesa schedule.step()            ~256 gov agents step normally
    4. _enforce_institutional_rules()  IIG triggers, Total Ruin, coup detection
    5. _run_feedback_loops()           12 loops (scalar + vectorised)
    6. _apply_scenario_rules()         Scenario A/B/C modifiers
    7. recompute_kpis()                KPIs from NumPy arrays
    8. datacollector.collect()

Author: Kaung Htet | MSc Data Science | University of Hertfordshire
================================================================================
"""

from __future__ import annotations

import random
import numpy as np
import logging
from mesa import Model
from mesa.time import RandomActivation
from mesa.datacollection import DataCollector

from config.constitution import CONSTITUTION
from agents.official import (
    OfficialAgent, OfficialPopulation,
    ChancellorAgent, PresidentAgent, EthnicLeaderAgent, AnalysisCouncilMember
)
from agents.oversight import (
    IIGAgent, IIGDirector, CourtJudge,
    ArbitrationJudge, OversightPopulation
)
from agents.foreign import (
    ForeignInvestorAgent, NeighboringStateAgent,
    InternationalOrgAgent, IllicitNetworkAgent, ForeignPopulation
)
from agents.institutional import (
    CentralBankAgent, FederalDevFundAgent,
    NationalShameRegisterAgent, TaxSystemAgent,
    EconomicCheckBalanceAgent, InstitutionalPopulation
)
from engine.elite_agents import EliteAgentLayer
from engine.hybrid_engine import (
    init_population, update_citizens, apply_feedback_loops,
    recompute_kpis, SCENARIO_MODS, TRUST_ACCEL_CORR_CEIL, TRUST_ACCEL_MIN_YEARS,
)

logger = logging.getLogger("ka_nova.hybrid_model")


class HybridKaNovaModel(Model):
    """
    Ka-Nova Hybrid Model.
    Citizens = NumPy arrays. Government = Mesa agents.
    """

    def __init__(
        self,
        scenario:   str  = "A",
        seed:       int  = None,
        n_citizens: int  = 50_000,
        use_llm:    bool = False,
    ):
        super().__init__()

        # ── Seed ──────────────────────────────────────────────────────────────
        if seed is not None:
            random.seed(seed)
            np.random.seed(seed)
        self.seed       = seed
        self.scenario   = scenario
        self.n_citizens = n_citizens
        self.current_year = 0
        self.max_years  = CONSTITUTION.simulation.TIME_STEPS
        self.rng        = np.random.default_rng(seed)
        self.mods       = SCENARIO_MODS[scenario]

        self.states = {
            "bamar_central":   {"gdp": 400.0, "gdp_growth": 0.02, "resource_revenue": 50000.0, "budget": 10000.0, "corruption_level": 0.75, "employment_rate": 0.60, "trust_index": 0.22, "ethnic_tension": 0.55, "infrastructure": 0.45, "knowledge_capital": 0.0, "protest_activity": 0.0, "iig_activity": 0.0, "merit_integrity": 0.40, "military_presence": 0.60, "ethnic_direct_fund": 0.0, "public_services": 0.40},
            "mandalay":        {"gdp": 420.0, "gdp_growth": 0.025, "resource_revenue": 45000.0, "budget": 11000.0, "corruption_level": 0.72, "employment_rate": 0.62, "trust_index": 0.23, "ethnic_tension": 0.48, "infrastructure": 0.50, "knowledge_capital": 0.0, "protest_activity": 0.0, "iig_activity": 0.0, "merit_integrity": 0.42, "military_presence": 0.55, "ethnic_direct_fund": 0.0, "public_services": 0.45},
            "magway":          {"gdp": 195.0, "gdp_growth": 0.012, "resource_revenue": 28000.0, "budget": 5500.0, "corruption_level": 0.74, "employment_rate": 0.56, "trust_index": 0.19, "ethnic_tension": 0.50, "infrastructure": 0.34, "knowledge_capital": 0.0, "protest_activity": 0.0, "iig_activity": 0.0, "merit_integrity": 0.36, "military_presence": 0.60, "ethnic_direct_fund": 0.0, "public_services": 0.33},
            "bago":            {"gdp": 245.0, "gdp_growth": 0.018, "resource_revenue": 32000.0, "budget": 6500.0, "corruption_level": 0.73, "employment_rate": 0.59, "trust_index": 0.21, "ethnic_tension": 0.55, "infrastructure": 0.40, "knowledge_capital": 0.0, "protest_activity": 0.0, "iig_activity": 0.0, "merit_integrity": 0.38, "military_presence": 0.58, "ethnic_direct_fund": 0.0, "public_services": 0.38},
            "yangon":          {"gdp": 750.0, "gdp_growth": 0.040, "resource_revenue": 90000.0, "budget": 20000.0, "corruption_level": 0.68, "employment_rate": 0.68, "trust_index": 0.26, "ethnic_tension": 0.45, "infrastructure": 0.65, "knowledge_capital": 0.0, "protest_activity": 0.0, "iig_activity": 0.0, "merit_integrity": 0.48, "military_presence": 0.45, "ethnic_direct_fund": 0.0, "public_services": 0.60},
            "ayeyarwady":      {"gdp": 310.0, "gdp_growth": 0.016, "resource_revenue": 38000.0, "budget": 7500.0, "corruption_level": 0.75, "employment_rate": 0.58, "trust_index": 0.20, "ethnic_tension": 0.50, "infrastructure": 0.36, "knowledge_capital": 0.0, "protest_activity": 0.0, "iig_activity": 0.0, "merit_integrity": 0.37, "military_presence": 0.58, "ethnic_direct_fund": 0.0, "public_services": 0.35},
            "tanintharyi":     {"gdp": 155.0, "gdp_growth": 0.014, "resource_revenue": 22000.0, "budget": 4500.0, "corruption_level": 0.74, "employment_rate": 0.55, "trust_index": 0.19, "ethnic_tension": 0.58, "infrastructure": 0.30, "knowledge_capital": 0.0, "protest_activity": 0.0, "iig_activity": 0.0, "merit_integrity": 0.35, "military_presence": 0.62, "ethnic_direct_fund": 0.0, "public_services": 0.30},
            "shan_eastern":    {"gdp": 250.0, "gdp_growth": 0.010, "resource_revenue": 80000.0, "budget": 5000.0, "corruption_level": 0.78, "employment_rate": 0.55, "trust_index": 0.18, "ethnic_tension": 0.72, "infrastructure": 0.30, "knowledge_capital": 0.0, "protest_activity": 0.0, "iig_activity": 0.0, "merit_integrity": 0.35, "military_presence": 0.70, "ethnic_direct_fund": 0.0, "public_services": 0.30},
            "kachin_northern": {"gdp": 170.0, "gdp_growth": 0.010, "resource_revenue": 40000.0, "budget": 3000.0, "corruption_level": 0.80, "employment_rate": 0.53, "trust_index": 0.15, "ethnic_tension": 0.78, "infrastructure": 0.25, "knowledge_capital": 0.0, "protest_activity": 0.0, "iig_activity": 0.0, "merit_integrity": 0.32, "military_presence": 0.75, "ethnic_direct_fund": 0.0, "public_services": 0.25},
            "kayah":           {"gdp": 75.0,  "gdp_growth": 0.008, "resource_revenue": 12000.0, "budget": 1800.0, "corruption_level": 0.77, "employment_rate": 0.51, "trust_index": 0.14, "ethnic_tension": 0.80, "infrastructure": 0.22, "knowledge_capital": 0.0, "protest_activity": 0.0, "iig_activity": 0.0, "merit_integrity": 0.30, "military_presence": 0.78, "ethnic_direct_fund": 0.0, "public_services": 0.22},
            "karen_southern":  {"gdp": 180.0, "gdp_growth": 0.010, "resource_revenue": 30000.0, "budget": 4000.0, "corruption_level": 0.72, "employment_rate": 0.56, "trust_index": 0.20, "ethnic_tension": 0.68, "infrastructure": 0.28, "knowledge_capital": 0.0, "protest_activity": 0.0, "iig_activity": 0.0, "merit_integrity": 0.38, "military_presence": 0.65, "ethnic_direct_fund": 0.0, "public_services": 0.28},
            "chin":            {"gdp": 90.0,  "gdp_growth": 0.007, "resource_revenue": 8000.0,  "budget": 1500.0, "corruption_level": 0.76, "employment_rate": 0.50, "trust_index": 0.14, "ethnic_tension": 0.75, "infrastructure": 0.20, "knowledge_capital": 0.0, "protest_activity": 0.0, "iig_activity": 0.0, "merit_integrity": 0.30, "military_presence": 0.72, "ethnic_direct_fund": 0.0, "public_services": 0.20},
            "mon":             {"gdp": 230.0, "gdp_growth": 0.016, "resource_revenue": 28000.0, "budget": 5500.0, "corruption_level": 0.73, "employment_rate": 0.58, "trust_index": 0.21, "ethnic_tension": 0.62, "infrastructure": 0.38, "knowledge_capital": 0.0, "protest_activity": 0.0, "iig_activity": 0.0, "merit_integrity": 0.38, "military_presence": 0.60, "ethnic_direct_fund": 0.0, "public_services": 0.36},
            "rakhine":         {"gdp": 160.0, "gdp_growth": 0.008, "resource_revenue": 35000.0, "budget": 3500.0, "corruption_level": 0.82, "employment_rate": 0.50, "trust_index": 0.12, "ethnic_tension": 0.88, "infrastructure": 0.22, "knowledge_capital": 0.0, "protest_activity": 0.0, "iig_activity": 0.0, "merit_integrity": 0.28, "military_presence": 0.82, "ethnic_direct_fund": 0.0, "public_services": 0.22},
        }


        # ── Mesa scheduler (government agents only — no citizens) ─────────────
        self.schedule = RandomActivation(self)

        # ── Shared data (Mesa agents read/write this as environment) ──────────
        self.shared_data = self._init_shared_data()

        # ── Elite Agent Layer (3 LLM agents) ─────────────────────────────────
        self.elite_layer = EliteAgentLayer(use_llm=use_llm)

        # ── NumPy citizen population (replaces Mesa CitizenAgent) ─────────────
        self.sim_state = init_population(n_citizens, scenario, self.rng)

        # ── Mesa government agents (~256 total) ───────────────────────────────
        self._create_gov_agents()

        # ── DataCollector ─────────────────────────────────────────────────────
        self.datacollector = DataCollector(
            model_reporters={
                "year":                  lambda m: m.current_year,
                "scenario":              lambda m: m.scenario,
                "corruption_index":      lambda m: m.shared_data["corruption_index"],
                "trust_index":           lambda m: m.shared_data["trust_index"],
                "gini_coefficient":      lambda m: m.shared_data["gini_coefficient"],
                "coup_probability":      lambda m: m.shared_data["coup_risk"],
                "iig_effectiveness":     lambda m: m.shared_data["iig_effectiveness"],
                "employment_rate":       lambda m: m.shared_data["employment_rate"],
                "brain_drain_rate":      lambda m: m.shared_data["brain_drain_rate"],
                "ethnic_harmony":        lambda m: m.shared_data["ethnic_harmony_index"],
                "north_star_progress":   lambda m: m.shared_data["north_star_progress"],
                "stability_index":       lambda m: m.shared_data["stability_index"],
                "gdp_growth":            lambda m: m.shared_data["gdp_growth_rate"],
                "shame_register_size":   lambda m: m.shared_data["shame_register_size"],
                "total_ruin_events":     lambda m: m.shared_data["total_ruin_events"],
                "elite_budget_impact":   lambda m: m.shared_data.get("elite_budget_impact", 0.07),
                "elite_coup_signal":     lambda m: m.shared_data.get("elite_coup_signal", False),
                "active_foreign_investors": lambda m: m.shared_data.get("active_foreign_investors", 0),
            }
        )

        # Collect Year 0 baseline
        self._sync_shared_data_from_sim_state()
        self.datacollector.collect(self)

        logger.info(
            f"HybridKaNovaModel: Scenario={scenario} | "
            f"{n_citizens:,} NumPy citizens | "
            f"{len(self.schedule.agents)} Mesa gov agents | "
            f"LLM={'ON' if use_llm else 'OFF'}"
        )

    # ── Shared data init ──────────────────────────────────────────────────────

    def _init_shared_data(self) -> dict:
        return {
            # Year Zero Myanmar baselines
            "corruption_index":      0.72,
            "trust_index":           0.22,
            "gini_coefficient":      0.55,
            "employment_rate":       0.58,
            "ethnic_tension_index":  0.68,
            "ethnic_harmony_index":  0.22,
            "stability_index":       0.18,
            "iig_effectiveness":     0.05,
            "coup_risk":             0.45,
            "brain_drain_rate":      0.35,
            "military_loyalty":      0.55,
            "policy_quality":        0.20,
            "merit_system_integrity": 0.30,
            "gdp_growth_rate":       0.02,
            "north_star_progress":   0.10,

            # Economic
            "poverty_line":          1000.0,
            "tax_revenue":           0.0,
            "federal_dev_fund":      0.0,
            "fdi_inflow":            0.0,
            "fdi_outflow":           0.0,
            "active_foreign_investors": 0,
            "inflation_rate":        0.12,
            "gdp_growth_rate":       0.02,

            # IIG / institutional
            "iig_total_active_cases": 0,
            "shame_register":        [],
            "shame_register_size":   0,
            "shame_register_signal": {},
            "total_ruin_events":     0,
            "total_ruin_certified":  [],

            # Population
            "total_citizens":        self.n_citizens,
            "annual_emigrants":      0,
            "low_corruption_streak": 0,
            "phd_graduates":         0,
            "knowledge_capital_index": 0.0,
            "tax_compliance_rate":   0.90,

            # Elite agent outputs (written before Mesa steps)
            "elite_budget_impact":   0.07,
            "elite_ethnic_weights":  [1.0] * 8,
            "elite_coup_signal":     False,
            "elite_decisions_log":   [],

            # Logs
            "corruption_acts_log":   [],
            "pending_policies":      [],
            "approved_policies":     [],
            "rights_violated":       False,
            "network_protest_rate":  0.0,
            "bribery_attempts":      [],
            "corruption_reports":    [],
            "high_treason_referrals": [],
            "active_investigations": [],
            "prosecution_queue":     [],
            "permanently_disqualified": [],
            "officials_removed":     [],
            "officials_term_complete": [],
            "ecb_active":            False,
            "ecb_interventions_total": 0,
            "psych_probation_officials": [],
            "annual_history":        [],
            "simulation_failed":     False,
            "failure_reason":        None,
        }

    # ── Government agent creation ─────────────────────────────────────────────

    def _create_gov_agents(self):
        """
        Create only the ~256 government Mesa agents.
        No CitizenAgent created — citizens are NumPy arrays in self.sim_state.
        """
        # Officials (~80): Chancellor/President stored as model refs (LLM controlled)
        officials = OfficialPopulation.create_population(self)
        for agent in officials:
            self.schedule.add(agent)

        # Oversight (71)
        oversight = OversightPopulation.create_population(self)
        for agent in oversight:
            self.schedule.add(agent)

        # Foreign (100)
        foreign = ForeignPopulation.create_population(self)
        for agent in foreign:
            self.schedule.add(agent)

        # Institutional (5)
        institutional = InstitutionalPopulation.create_population(self)
        for agent in institutional:
            self.schedule.add(agent)

        total = len(self.schedule.agents)
        print(f"HybridKaNovaModel: {total} Mesa gov agents | "
              f"{self.n_citizens:,} NumPy citizens | "
              f"scenario={self.scenario} seed={self.seed}")

    # ── Main step ─────────────────────────────────────────────────────────────

    def step(self):
        """
        One year of simulation.

        Order:
            1. Elite LLM agents deliberate → write to shared_data
            2. NumPy citizen update (vectorised, <50ms for 50k)
            3. Mesa government agents step (~256 agents, fast)
            4. Institutional enforcement (IIG, Total Ruin, coup)
            5. Feedback loops (12 loops)
            6. Scenario rules (A/B/C modifiers)
            7. State environment update
            8. Sync KPIs → shared_data
            9. DataCollector
        """
        self.shared_data["year"] = self.current_year

        # ── 1. Elite agents deliberate ────────────────────────────────────────
        self.elite_layer.step(self.shared_data, self.current_year, self.scenario)

        # Handle coup signal
        if self.shared_data.get("elite_coup_signal", False):
            if self.mods["coup_block"]:
                self.shared_data["coup_risk"] = max(
                    0.0, self.shared_data["coup_risk"] - 0.05
                )
            else:
                self.shared_data["coup_risk"] = min(
                    1.0, self.shared_data["coup_risk"] + 0.05
                )
        elif self.mods["coup_block"]:
            self.shared_data["coup_risk"] = 0.0

        # ── 2. NumPy citizen update ───────────────────────────────────────────
        budget_impact  = float(self.shared_data.get("elite_budget_impact", 0.07))
        ethnic_weights = np.array(
            self.shared_data.get("elite_ethnic_weights", [1.0]*8), dtype=np.float32
        )
        trust_accel = (
            self.mods["trust_accel"]
            and self.shared_data.get("low_corruption_streak", 0) >= TRUST_ACCEL_MIN_YEARS
        )
        self.sim_state = update_citizens(
            self.sim_state, budget_impact, ethnic_weights,
            self.mods["article8"], trust_accel, self.rng
        )

        # ── 3. Mesa government agents step ────────────────────────────────────
        self.schedule.step()

        # ── 4. Institutional enforcement ──────────────────────────────────────
        self._enforce_iig_triggers()
        self._enforce_total_ruin()
        self._enforce_coup_detection()
        self._enforce_rights_protections()

        # ── 5. Feedback loops ─────────────────────────────────────────────────
        self._run_feedback_loops()

        # ── 6. Scenario rules ─────────────────────────────────────────────────
        self._apply_scenario_rules()

        # ── 7. Sync population KPIs → shared_data ────────────────────────────
        self.sim_state = apply_feedback_loops(
            self.sim_state,
            self.mods,
            self.rng
        )
        self.sim_state = recompute_kpis(self.sim_state)
        self._sync_shared_data_from_sim_state()

        # ── 8. Trust acceleration tracker ────────────────────────────────────
        if self.shared_data["corruption_index"] < TRUST_ACCEL_CORR_CEIL:
            self.shared_data["low_corruption_streak"] = (
                self.shared_data.get("low_corruption_streak", 0) + 1
            )
        else:
            self.shared_data["low_corruption_streak"] = 0

        # ── 9. Annual history snapshot ────────────────────────────────────────
        self.shared_data["annual_history"].append({
            "year":             self.current_year,
            "corruption_index": self.shared_data["corruption_index"],
            "trust_index":      self.shared_data["trust_index"],
            "gini_coefficient": self.shared_data["gini_coefficient"],
        })
        if len(self.shared_data["annual_history"]) > 10:
            self.shared_data["annual_history"].pop(0)

        # ── 10. Collect KPIs ──────────────────────────────────────────────────
        self.datacollector.collect(self)
        self.current_year += 1

        # ── 11. Reset annual counters ─────────────────────────────────────────
        self.shared_data["fdi_inflow"]         = 0.0
        self.shared_data["fdi_outflow"]        = 0.0
        self.shared_data["annual_emigrants"]   = 0
        self.shared_data["rights_violated"]    = False
        self.shared_data["phd_graduates"]      = 0

    # ── Sync sim_state KPIs → shared_data ────────────────────────────────────

    def _sync_shared_data_from_sim_state(self):
        """Push NumPy-computed KPIs into shared_data for Mesa agents to read."""
        ss = self.sim_state
        sd = self.shared_data
        sd["trust_index"]          = float(ss.trust_index) if ss.trust_index > 0 else float(ss.pop[:, 1].mean()) if len(ss.pop) > 0 else 0.22
        sd["gini_coefficient"]     = ss.gini_coefficient
        sd["employment_rate"]      = ss.employment_rate
        sd["brain_drain_rate"]     = ss.brain_drain_rate
        sd["ethnic_harmony_index"] = ss.ethnic_harmony
        sd["north_star_progress"]  = ss.north_star_progress
        sd["stability_index"]      = ss.stability_index
        sd["gdp_growth_rate"]      = ss.gdp_growth
        # Corruption comes from Mesa officials (more accurate)
        # but use sim_state as fallback
        # Compute corruption from Mesa officials (more accurate than sim_state)
        officials = [a for a in self.schedule.agents if isinstance(a, OfficialAgent)]
        if officials:
            sd["corruption_index"] = min(1.0, sum(a.corruption_score for a in officials) / len(officials))
        else:
            sd["corruption_index"] = ss.corruption_index
        # Also sync to sim_state so feedback loops use correct value
        ss.corruption_index = sd["corruption_index"]

    # ── Institutional enforcement (from Phase 1 model.py, unchanged) ──────────

    def _enforce_iig_triggers(self):
        trigger = CONSTITUTION.iig.INVESTIGATION_TRIGGER
        log = self.shared_data.get("corruption_acts_log", [])
        above = [a for a in log
                 if a.get("corruption_score", 0.0) >= trigger
                 and not a.get("investigated", False)]
        if above:
            self.shared_data["iig_trigger_count"] = (
                self.shared_data.get("iig_trigger_count", 0) + len(above)
            )

    def _enforce_total_ruin(self):
        for cert in self.shared_data.get("total_ruin_certified", []):
            if cert.get("executed", False):
                continue
            target_id = cert.get("target_id")
            for agent in self.schedule.agents:
                if (isinstance(agent, OfficialAgent) and
                        agent.unique_id == target_id and
                        not agent.total_ruin_triggered):
                    agent.trigger_total_ruin()
                    self.shared_data["total_ruin_events"] = (
                        self.shared_data.get("total_ruin_events", 0) + 1
                    )
            cert["executed"] = True

    def _enforce_coup_detection(self):
        military_loyalty    = self.shared_data.get("military_loyalty", 0.55)
        chancellor_approval = 0.50
        chancellors = [a for a in self.schedule.agents if isinstance(a, ChancellorAgent)]
        if chancellors:
            chancellor_approval = chancellors[0].approval_rating

        if (military_loyalty < CONSTITUTION.military.COUP_TRIGGER_LOYALTY and
                chancellor_approval < CONSTITUTION.military.COUP_TRIGGER_APPROVAL):
            coup_risk = (
                (CONSTITUTION.military.COUP_TRIGGER_LOYALTY - military_loyalty) * 0.50 +
                (CONSTITUTION.military.COUP_TRIGGER_APPROVAL - chancellor_approval) * 0.50
            )
            self.shared_data["coup_risk"] = min(1.0, coup_risk)
            if self.shared_data["coup_risk"] > 0.60:
                self._attempt_coup()
        else:
            self.shared_data["coup_risk"] = max(
                0.0, self.shared_data.get("coup_risk", 0.0) - 0.02
            )

    def _attempt_coup(self):
        if self.scenario == "A":
            self.shared_data["coup_risk"] = max(
                0.0, self.shared_data["coup_risk"] - 0.30
            )
        elif self.scenario == "B":
            if random.random() < 0.40:
                self.shared_data["simulation_failed"] = True
                self.shared_data["failure_reason"]    = "coup_succeeded_no_safeguards"
        elif self.scenario == "C":
            if random.random() < 0.70:
                self.shared_data["simulation_failed"] = True
                self.shared_data["failure_reason"]    = "military_baseline_coup"

    def _enforce_rights_protections(self):
        if self.shared_data.get("rights_violated", False):
            self.shared_data["trust_index"] = max(
                0.0, self.shared_data.get("trust_index", 0.22) - 0.15
            )

    # ── Feedback loops ────────────────────────────────────────────────────────

    def _run_feedback_loops(self):
        self._loop_P1_trust()
        self._loop_P2_iig_corruption()
        self._loop_P3_coup()
        self._loop_P4_merit()
        self._loop_E1_gdp()
        self._loop_E2_fdi()
        self._loop_E4_phd()
        self._loop_S2_protest()
        self._loop_S4_shame()

    def _loop_P1_trust(self):
        performance   = self.shared_data.get("policy_quality", 0.35)
        current_trust = self.shared_data.get("trust_index", 0.22)
        new_trust     = current_trust * 0.70 + performance * 0.30
        corruption    = self.shared_data.get("corruption_index", 1.0)

        if corruption < CONSTITUTION.federal.TRUST_ACCELERATION_TRIGGER_CORRUPTION:
            streak = self.shared_data.get("low_corruption_streak", 0) + 1
        else:
            streak = 0
        self.shared_data["low_corruption_streak"] = streak

        if streak >= CONSTITUTION.federal.TRUST_ACCELERATION_TRIGGER_YEARS:
            growth = new_trust - current_trust
            if growth > 0:
                new_trust = current_trust + growth * CONSTITUTION.federal.TRUST_ACCELERATION_MULTIPLIER

        self.shared_data["trust_index"] = max(0.0, min(1.0, new_trust))

    def _loop_P2_iig_corruption(self):
        iig_agents = [a for a in self.schedule.agents if isinstance(a, IIGAgent)]
        if not iig_agents:
            return
        total_solved = sum(a.cases_solved for a in iig_agents)
        total_opened = sum(a.cases_opened for a in iig_agents) or 1
        effectiveness = min(1.0, total_solved / total_opened)
        self.shared_data["iig_effectiveness"] = (
            self.shared_data.get("iig_effectiveness", 0.30) * 0.70 +
            effectiveness * 0.30
        )
        if effectiveness > 0.60:
            for agent in self.schedule.agents:
                if isinstance(agent, OfficialAgent):
                    agent.corruption_score = max(
                        0.0, agent.corruption_score - effectiveness * 0.02
                    )

    def _loop_P3_coup(self):
        constitutional_commitment = (
            1.0 if self.scenario == "A" else
            0.70 if self.scenario == "B" else 0.30
        )
        trust = self.shared_data.get("trust_index", 0.22)
        self.shared_data["military_loyalty"] = min(
            1.0, 0.55 * 0.40 + constitutional_commitment * 0.40 + trust * 0.20
        )

    def _loop_P4_merit(self):
        if self.current_year % CONSTITUTION.merit.RECERTIFICATION_INTERVAL == 0:
            officials = [a for a in self.schedule.agents if isinstance(a, OfficialAgent)]
            if officials:
                avg_merit = sum(a.merit_score for a in officials) / len(officials)
                self.shared_data["merit_system_integrity"] = avg_merit
                self.shared_data["policy_quality"] = min(
                    1.0, avg_merit * 0.80 + random.uniform(0.0, 0.10)
                )

    def _loop_E1_gdp(self):
        corruption = self.shared_data.get("corruption_index", 0.72)
        iig        = self.shared_data.get("iig_effectiveness", 0.30)
        gini       = self.shared_data.get("gini_coefficient", 0.55)
        gdp = float(np.clip(
            0.045 - corruption * 0.03 + iig * 0.02 + (1.0 - gini) * 0.01,
            -0.02, 0.12
        ))
        self.shared_data["gdp_growth_rate"] = gdp
        self.sim_state.gdp_growth = gdp

    def _loop_E2_fdi(self):
        active = self.shared_data.get("active_foreign_investors", 0)
        if active > 0:
            self.shared_data["knowledge_capital_index"] = min(
                1.0,
                self.shared_data.get("knowledge_capital_index", 0.0) + active * 0.001
            )

    def _loop_E4_phd(self):
        phd = self.shared_data.get("phd_graduates", 0)
        if phd > 0:
            self.shared_data["knowledge_capital_index"] = min(
                1.0,
                self.shared_data.get("knowledge_capital_index", 0.0) + phd * 0.002
            )

    def _loop_S2_protest(self):
        protest_rate = self.shared_data.get("network_protest_rate", 0.0)
        if protest_rate > 0.10:
            self.shared_data["trust_index"] = max(
                0.0, self.shared_data.get("trust_index", 0.22) - 0.05
            )

    def _loop_S4_shame(self):
        shame_size = self.shared_data.get("shame_register_size", 0)
        if shame_size > 0:
            deterrence = min(0.40, shame_size * 0.01)
            self.shared_data["corruption_deterrence"] = deterrence

    # ── Scenario rules ────────────────────────────────────────────────────────

    def _apply_scenario_rules(self):
        if self.scenario == "A":
            self.shared_data["rights_violated"] = False
            self.shared_data["iig_effectiveness"] = min(
                1.0,
                self.shared_data.get("iig_effectiveness", 0.30) +
                0.01 * (self.current_year / self.max_years)
            )
            shame_size = self.shared_data.get("shame_register_size", 0)
            if shame_size > 5:
                for agent in self.schedule.agents:
                    if isinstance(agent, OfficialAgent):
                        agent.corruption_tolerance = max(
                            0.0, agent.corruption_tolerance - 0.005
                        )

        elif self.scenario == "B":
            if random.random() < 0.05:
                self.shared_data["rights_violated"] = True
            self.shared_data["iig_effectiveness"] = max(
                0.10, self.shared_data.get("iig_effectiveness", 0.30) - 0.008
            )
            self.shared_data["policy_quality"] = max(
                0.20, self.shared_data.get("policy_quality", 0.50) - 0.003
            )
            self.shared_data["trust_index"] = max(
                0.0, self.shared_data.get("trust_index", 0.40) - 0.005
            )
            for agent in self.schedule.agents:
                if isinstance(agent, OfficialAgent):
                    agent.corruption_tolerance = min(
                        1.0, agent.corruption_tolerance + 0.015
                    )

        elif self.scenario == "C":
            if random.random() < 0.20:
                self.shared_data["rights_violated"] = True
            self.shared_data["iig_effectiveness"] = 0.05
            self.shared_data["trust_index"] = max(
                0.08, self.shared_data.get("trust_index", 0.22) - 0.015
            )
            self.shared_data["policy_quality"] = max(
                0.10, self.shared_data.get("policy_quality", 0.20) - 0.005
            )
            self.shared_data["coup_risk"] = min(
                0.60, self.shared_data.get("coup_risk", 0.25) + 0.015
            )
            for agent in self.schedule.agents:
                if isinstance(agent, OfficialAgent):
                    agent.corruption_score = min(
                        0.95, agent.corruption_score + random.uniform(0.01, 0.04)
                    )

    # ── Utility ───────────────────────────────────────────────────────────────

    def get_results(self):
        return self.datacollector.get_model_vars_dataframe()

    def summary(self) -> str:
        sd = self.shared_data
        return (
            f"HybridKaNovaModel Year {self.current_year} | Scenario {self.scenario}\n"
            f"  Corruption:  {sd.get('corruption_index', 0):.3f}\n"
            f"  Trust:       {sd.get('trust_index', 0):.3f}\n"
            f"  Gini:        {sd.get('gini_coefficient', 0):.3f}\n"
            f"  IIG:         {sd.get('iig_effectiveness', 0):.3f}\n"
            f"  Coup Risk:   {sd.get('coup_risk', 0):.3f}\n"
            f"  North Star:  {sd.get('north_star_progress', 0):.3f}\n"
            f"  Shame Reg:   {sd.get('shame_register_size', 0)}\n"
            f"  Total Ruin:  {sd.get('total_ruin_events', 0)}"
        )