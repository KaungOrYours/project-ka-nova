"""
================================================================================
PROJECT KA-NOVA
model.py — Phase 2

Ka-Nova Main Simulation Model
Ka-Nova Simulation Engine v2.0

Phase 2 changes (surgical only — all Phase 1 logic preserved verbatim):
    DIFF 1 — Import EliteAgentLayer
    DIFF 2 — __init__ signature: add use_llm=False param + self.elite_layer init
    DIFF 3 — _initialize_shared_data: add 4 elite keys only
    DIFF 4 — _initialize_states: expand 4 → 14 states (same dict structure)
    DIFF 5 — step(): add elite deliberation block at top
             _loop_E3_resource_revenue: NumPy vectorised Gini fix

Everything else is Phase 1 model.py verbatim.

Architecture:
    - 50,000 citizens (scaled from 9,500)
    - 14 Myanmar states (scaled from 4)
    - 3 LLM elite agents via EliteAgentLayer (NEW)
    - ~316 Mesa agents unchanged
    - 12 feedback loops (unchanged)
    - 3 comparison scenarios (unchanged)
    - 50 time steps / years (unchanged)

RunPod path: /workspace/ka-nova
Mac path:    ~/Desktop/ka-nova

Author: Kaung Htet
License: MIT
================================================================================
"""

from __future__ import annotations

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import random
import numpy as np
from typing import Dict, List, Optional

from mesa import Model
from mesa.time import RandomActivation
from mesa.datacollection import DataCollector

from config.constitution import CONSTITUTION
from agents.citizen import CitizenAgent, CitizenPopulation
from agents.official import (
    OfficialAgent, OfficialPopulation,
    ChancellorAgent, PresidentAgent,
    EthnicLeaderAgent, AnalysisCouncilMember
)
from agents.oversight import (
    IIGAgent, IIGDirector, CourtJudge,
    ArbitrationJudge, OversightPopulation
)
from agents.foreign import (
    ForeignInvestorAgent, NeighboringStateAgent,
    InternationalOrgAgent, IllicitNetworkAgent,
    ForeignPopulation
)
from agents.institutional import (
    CentralBankAgent, FederalDevFundAgent,
    NationalShameRegisterAgent, TaxSystemAgent,
    EconomicCheckBalanceAgent, InstitutionalPopulation
)

# ── DIFF 1: Phase 2 — EliteAgentLayer (3 LLM agents only) ────────────────────
# Chancellor, President, Senior General driven by LangChain LLM.
# All other agents above remain standard Mesa agents — unchanged.
from engine.elite_agents import EliteAgentLayer


# ══════════════════════════════════════════════════════════════════════════════
# KPI COLLECTOR FUNCTIONS
# Unchanged from Phase 1 — called by Mesa DataCollector every time step
# ══════════════════════════════════════════════════════════════════════════════

def get_corruption_index(model):
    officials = [a for a in model.schedule.agents if isinstance(a, OfficialAgent)]
    if not officials:
        return 0.0
    return sum(a.corruption_score for a in officials) / len(officials)

def get_trust_index(model):
    citizens = [a for a in model.schedule.agents
                if isinstance(a, CitizenAgent) and not isinstance(a, OfficialAgent)]
    if not citizens:
        return 0.0
    return sum(a.trust_score for a in citizens) / len(citizens)

def get_grievance_index(model):
    citizens = [a for a in model.schedule.agents
                if isinstance(a, CitizenAgent) and not isinstance(a, OfficialAgent)]
    if not citizens:
        return 0.0
    return sum(a.grievance for a in citizens) / len(citizens)

def get_merit_system_integrity(model):
    officials = [a for a in model.schedule.agents if isinstance(a, OfficialAgent)]
    if not officials:
        return 0.0
    clean = sum(1 for a in officials if a.corruption_score < 0.40)
    return clean / len(officials)

def get_iig_effectiveness(model):
    return model.shared_data.get("iig_effectiveness", 0.0)

def get_coup_probability(model):
    return model.shared_data.get("coup_risk", 0.0)

def get_ethnic_harmony_index(model):
    citizens = [a for a in model.schedule.agents
                if isinstance(a, CitizenAgent) and not isinstance(a, OfficialAgent)]
    if not citizens:
        return 0.0
    return sum(a.ethnic_cross_exposure for a in citizens) / len(citizens)

def get_gini_coefficient(model):
    citizens = [a for a in model.schedule.agents
                if isinstance(a, CitizenAgent) and not isinstance(a, OfficialAgent)
                and a.income > 0 and a.is_alive and not a.has_emigrated]
    if len(citizens) < 10:
        return model.shared_data.get("gini_coefficient", 0.55)
    incomes = sorted([a.income for a in citizens])
    n = len(incomes)
    total = sum(incomes)
    if total <= 0:
        return model.shared_data.get("gini_coefficient", 0.55)
    numerator = sum((2 * (i + 1) - n - 1) * incomes[i] for i in range(n))
    gini = abs(numerator) / (n * total)
    gini = max(0.0, min(1.0, gini))
    model.shared_data["gini_coefficient"] = gini
    return gini

def get_employment_rate(model):
    citizens = [a for a in model.schedule.agents
                if isinstance(a, CitizenAgent) and not isinstance(a, OfficialAgent)
                and a.age >= 18 and a.age <= 65]
    if not citizens:
        return 0.0
    employed = sum(1 for a in citizens if a.employment_status == "employed")
    return employed / len(citizens)

def get_phd_output(model):
    return model.shared_data.get("phd_graduates", 0)

def get_knowledge_capital(model):
    states = model.states.values()
    if not states:
        return 0.0
    return sum(s.get("knowledge_capital", 0.0) for s in states)

def get_brain_drain_rate(model):
    annual = model.shared_data.get("annual_emigrants", 0)
    total = model.shared_data.get("total_citizens", 9500)
    return annual / max(1, total)

def get_tax_compliance_rate(model):
    return model.shared_data.get("tax_compliance_rate", 0.90)

def get_shame_register_size(model):
    return model.shared_data.get("shame_register_size", 0)

def get_active_foreign_investors(model):
    return model.shared_data.get("active_foreign_investors", 0)

def get_stability_index(model):
    return model.shared_data.get("stability_index", 0.30)

def get_north_star_progress(model):
    corruption = 1.0 - model.shared_data.get("corruption_index", 0.65)
    trust = model.shared_data.get("trust_index", 0.30)
    knowledge = min(1.0, model.shared_data.get("knowledge_capital_index", 0.0))
    employment = model.shared_data.get("employment_rate", 0.58)
    harmony = model.shared_data.get("ethnic_harmony_index", 0.30)
    return (corruption * 0.25 + trust * 0.20 + knowledge * 0.20 +
            employment * 0.20 + harmony * 0.15)

def get_total_ruin_events(model):
    return model.shared_data.get("total_ruin_events", 0)

def get_fdi_net(model):
    return (model.shared_data.get("fdi_inflow", 0.0) -
            model.shared_data.get("fdi_outflow", 0.0))

def get_inflation_rate(model):
    return model.shared_data.get("inflation_rate", 0.08)

def get_psych_probation_count(model):
    officials = [a for a in model.schedule.agents if isinstance(a, OfficialAgent)]
    return sum(1 for a in officials if a.psych_probation)


# ══════════════════════════════════════════════════════════════════════════════
# KA-NOVA MODEL
# ══════════════════════════════════════════════════════════════════════════════

class KaNovaModel(Model):
    """
    Ka-Nova Main Simulation Model.

    Simulates the Federal Union of Myanmar under MFU constitutional rules
    over 50 time steps (years), starting from post-conflict Year Zero.

    Three scenarios:
        A: Full MFU with all safeguards active
        B: MFU without safeguards (loopholes open)
        C: Military baseline (current Myanmar trajectory)

    Parameters:
        scenario (str): 'A', 'B', or 'C'
        seed (int): random seed for reproducibility
        n_citizens (int): number of citizen agents
        use_llm (bool): False = rule-based elite agents (Mac local)
                        True  = LangChain LLM elite agents (RunPod)
    """

    # ── DIFF 2: add use_llm param ─────────────────────────────────────────────
    def __init__(
        self,
        scenario: str = "A",
        seed: int = None,
        n_citizens: int = None,
        use_llm: bool = False,
    ):
        super().__init__()

        # ── SEED ──────────────────────────────────────────────────────────────
        if seed is not None:
            random.seed(seed)
            np.random.seed(seed)
        self.seed = seed
        self.scenario = scenario

        # ── CONFIGURATION ─────────────────────────────────────────────────────
        self.n_citizens = n_citizens or CONSTITUTION.simulation.CITIZEN_AGENTS
        self.current_year = 0
        self.max_years = CONSTITUTION.simulation.TIME_STEPS

        # ── SCHEDULER ────────────────────────────────────────────────────────
        self.schedule = RandomActivation(self)

        # ── DIFF 2 (cont): EliteAgentLayer — 3 LLM agents only ───────────────
        # All Mesa agents below are unchanged from Phase 1.
        # On Mac:    use_llm=False → deterministic rule-based (no LLM needed)
        # On RunPod: use_llm=True  → LangChain Llama 3 on localhost:11434
        self.elite_layer = EliteAgentLayer(use_llm=use_llm)

        # ── ENVIRONMENT — DIFF 4: 14 STATES ──────────────────────────────────
        self.states = self._initialize_states()

        # ── SHARED DATA ───────────────────────────────────────────────────────
        self.shared_data = self._initialize_shared_data()

        # ── CREATE ALL AGENTS ─────────────────────────────────────────────────
        self._create_agents()

        # ── DATA COLLECTOR ────────────────────────────────────────────────────
        self.datacollector = DataCollector(
            model_reporters={
                "year":                  lambda m: m.current_year,
                "scenario":              lambda m: m.scenario,
                "corruption_index":      get_corruption_index,
                "trust_index":           get_trust_index,
                "grievance_index":       get_grievance_index,
                "merit_integrity":       get_merit_system_integrity,
                "iig_effectiveness":     get_iig_effectiveness,
                "coup_probability":      get_coup_probability,
                "ethnic_harmony":        get_ethnic_harmony_index,
                "gini_coefficient":      get_gini_coefficient,
                "employment_rate":       get_employment_rate,
                "phd_output":            get_phd_output,
                "knowledge_capital":     get_knowledge_capital,
                "brain_drain_rate":      get_brain_drain_rate,
                "tax_compliance":        get_tax_compliance_rate,
                "shame_register_size":   get_shame_register_size,
                "foreign_investors":     get_active_foreign_investors,
                "stability_index":       get_stability_index,
                "north_star_progress":   get_north_star_progress,
                "total_ruin_events":     get_total_ruin_events,
                "fdi_net":               get_fdi_net,
                "inflation_rate":        get_inflation_rate,
                "psych_probation_count": get_psych_probation_count,
            }
        )

        # Apply Year Zero calibration
        self._apply_year_zero_calibration()

        # Collect Year 0 baseline
        self.datacollector.collect(self)

    # ══════════════════════════════════════════════════════════════════════════
    # INITIALIZATION
    # ══════════════════════════════════════════════════════════════════════════

    def _initialize_states(self) -> Dict:
        """
        DIFF 4: 14 actual Myanmar states/regions.
        Original 4 Phase 1 states kept as first entries — same key names,
        same dict structure — so all existing agent state_id assignments work.
        10 new states appended with identical key structure.
        """

        return {
            # ── Original 4 Phase 1 states — PRESERVED verbatim ───────────────
            "bamar_central": {
                "gdp": 400.0,
                "gdp_growth": 0.02,
                "resource_revenue": 50000.0,
                "budget": 10000.0,
                "corruption_level": 0.75,
                "employment_rate": 0.60,
                "trust_index": 0.22,
                "ethnic_tension": 0.55,
                "infrastructure": 0.45,
                "knowledge_capital": 0.0,
                "protest_activity": 0.0,
                "iig_activity": 0.0,
                "merit_integrity": 0.40,
                "military_presence": 0.60,
                "ethnic_direct_fund": 0.0,
                "public_services": 0.40
            },
            "shan_eastern": {
                "gdp": 250.0,
                "gdp_growth": 0.01,
                "resource_revenue": 80000.0,
                "budget": 5000.0,
                "corruption_level": 0.78,
                "employment_rate": 0.55,
                "trust_index": 0.18,
                "ethnic_tension": 0.72,
                "infrastructure": 0.30,
                "knowledge_capital": 0.0,
                "protest_activity": 0.0,
                "iig_activity": 0.0,
                "merit_integrity": 0.35,
                "military_presence": 0.70,
                "ethnic_direct_fund": 0.0,
                "public_services": 0.30
            },
            "karen_southern": {
                "gdp": 180.0,
                "gdp_growth": 0.01,
                "resource_revenue": 30000.0,
                "budget": 4000.0,
                "corruption_level": 0.72,
                "employment_rate": 0.56,
                "trust_index": 0.20,
                "ethnic_tension": 0.68,
                "infrastructure": 0.28,
                "knowledge_capital": 0.0,
                "protest_activity": 0.0,
                "iig_activity": 0.0,
                "merit_integrity": 0.38,
                "military_presence": 0.65,
                "ethnic_direct_fund": 0.0,
                "public_services": 0.28
            },
            "kachin_northern": {
                "gdp": 170.0,
                "gdp_growth": 0.01,
                "resource_revenue": 40000.0,
                "budget": 3000.0,
                "corruption_level": 0.80,
                "employment_rate": 0.53,
                "trust_index": 0.15,
                "ethnic_tension": 0.78,
                "infrastructure": 0.25,
                "knowledge_capital": 0.0,
                "protest_activity": 0.0,
                "iig_activity": 0.0,
                "merit_integrity": 0.32,
                "military_presence": 0.75,
                "ethnic_direct_fund": 0.0,
                "public_services": 0.25
            },
            # ── 10 new Phase 2 states — same dict structure ───────────────────
            "mandalay": {
                "gdp": 420.0,
                "gdp_growth": 0.025,
                "resource_revenue": 45000.0,
                "budget": 11000.0,
                "corruption_level": 0.72,
                "employment_rate": 0.62,
                "trust_index": 0.23,
                "ethnic_tension": 0.48,
                "infrastructure": 0.50,
                "knowledge_capital": 0.0,
                "protest_activity": 0.0,
                "iig_activity": 0.0,
                "merit_integrity": 0.42,
                "military_presence": 0.55,
                "ethnic_direct_fund": 0.0,
                "public_services": 0.45
            },
            "yangon": {
                "gdp": 750.0,
                "gdp_growth": 0.040,
                "resource_revenue": 90000.0,
                "budget": 20000.0,
                "corruption_level": 0.68,
                "employment_rate": 0.68,
                "trust_index": 0.26,
                "ethnic_tension": 0.45,
                "infrastructure": 0.65,
                "knowledge_capital": 0.0,
                "protest_activity": 0.0,
                "iig_activity": 0.0,
                "merit_integrity": 0.48,
                "military_presence": 0.45,
                "ethnic_direct_fund": 0.0,
                "public_services": 0.60
            },
            "magway": {
                "gdp": 195.0,
                "gdp_growth": 0.012,
                "resource_revenue": 28000.0,
                "budget": 5500.0,
                "corruption_level": 0.74,
                "employment_rate": 0.56,
                "trust_index": 0.19,
                "ethnic_tension": 0.50,
                "infrastructure": 0.34,
                "knowledge_capital": 0.0,
                "protest_activity": 0.0,
                "iig_activity": 0.0,
                "merit_integrity": 0.36,
                "military_presence": 0.60,
                "ethnic_direct_fund": 0.0,
                "public_services": 0.33
            },
            "bago": {
                "gdp": 245.0,
                "gdp_growth": 0.018,
                "resource_revenue": 32000.0,
                "budget": 6500.0,
                "corruption_level": 0.73,
                "employment_rate": 0.59,
                "trust_index": 0.21,
                "ethnic_tension": 0.55,
                "infrastructure": 0.40,
                "knowledge_capital": 0.0,
                "protest_activity": 0.0,
                "iig_activity": 0.0,
                "merit_integrity": 0.38,
                "military_presence": 0.58,
                "ethnic_direct_fund": 0.0,
                "public_services": 0.38
            },
            "ayeyarwady": {
                "gdp": 310.0,
                "gdp_growth": 0.016,
                "resource_revenue": 38000.0,
                "budget": 7500.0,
                "corruption_level": 0.75,
                "employment_rate": 0.58,
                "trust_index": 0.20,
                "ethnic_tension": 0.50,
                "infrastructure": 0.36,
                "knowledge_capital": 0.0,
                "protest_activity": 0.0,
                "iig_activity": 0.0,
                "merit_integrity": 0.37,
                "military_presence": 0.58,
                "ethnic_direct_fund": 0.0,
                "public_services": 0.35
            },
            "tanintharyi": {
                "gdp": 155.0,
                "gdp_growth": 0.014,
                "resource_revenue": 22000.0,
                "budget": 4500.0,
                "corruption_level": 0.74,
                "employment_rate": 0.55,
                "trust_index": 0.19,
                "ethnic_tension": 0.58,
                "infrastructure": 0.30,
                "knowledge_capital": 0.0,
                "protest_activity": 0.0,
                "iig_activity": 0.0,
                "merit_integrity": 0.35,
                "military_presence": 0.62,
                "ethnic_direct_fund": 0.0,
                "public_services": 0.30
            },
            "kayah": {
                "gdp": 75.0,
                "gdp_growth": 0.008,
                "resource_revenue": 12000.0,
                "budget": 1800.0,
                "corruption_level": 0.77,
                "employment_rate": 0.51,
                "trust_index": 0.14,
                "ethnic_tension": 0.80,
                "infrastructure": 0.22,
                "knowledge_capital": 0.0,
                "protest_activity": 0.0,
                "iig_activity": 0.0,
                "merit_integrity": 0.30,
                "military_presence": 0.78,
                "ethnic_direct_fund": 0.0,
                "public_services": 0.22
            },
            "chin": {
                "gdp": 90.0,
                "gdp_growth": 0.007,
                "resource_revenue": 8000.0,
                "budget": 1500.0,
                "corruption_level": 0.76,
                "employment_rate": 0.50,
                "trust_index": 0.14,
                "ethnic_tension": 0.75,
                "infrastructure": 0.20,
                "knowledge_capital": 0.0,
                "protest_activity": 0.0,
                "iig_activity": 0.0,
                "merit_integrity": 0.30,
                "military_presence": 0.72,
                "ethnic_direct_fund": 0.0,
                "public_services": 0.20
            },
            "mon": {
                "gdp": 230.0,
                "gdp_growth": 0.016,
                "resource_revenue": 28000.0,
                "budget": 5500.0,
                "corruption_level": 0.73,
                "employment_rate": 0.58,
                "trust_index": 0.21,
                "ethnic_tension": 0.62,
                "infrastructure": 0.38,
                "knowledge_capital": 0.0,
                "protest_activity": 0.0,
                "iig_activity": 0.0,
                "merit_integrity": 0.38,
                "military_presence": 0.60,
                "ethnic_direct_fund": 0.0,
                "public_services": 0.36
            },
            "rakhine": {
                "gdp": 160.0,
                "gdp_growth": 0.008,
                "resource_revenue": 35000.0,
                "budget": 3500.0,
                "corruption_level": 0.82,
                "employment_rate": 0.50,
                "trust_index": 0.12,
                "ethnic_tension": 0.88,
                "infrastructure": 0.22,
                "knowledge_capital": 0.0,
                "protest_activity": 0.0,
                "iig_activity": 0.0,
                "merit_integrity": 0.28,
                "military_presence": 0.82,
                "ethnic_direct_fund": 0.0,
                "public_services": 0.22
            },
        }

    def _initialize_shared_data(self) -> Dict:
        """
        Initialize global shared data store.
        DIFF 3: 4 elite keys added at bottom — all other keys unchanged.
        """

        return {
            # ── Economic (unchanged) ──────────────────────────────────────────
            "poverty_line": 1000.0,
            "tax_revenue": 0.0,
            "total_tax_revenue": 0.0,
            "federal_dev_fund": 0.0,
            "fdi_inflow": 0.0,
            "fdi_outflow": 0.0,
            "active_foreign_investors": 0,
            "total_trade_volume": 0.0,
            "black_economy_volume": 0.0,
            "total_aid_received": 0.0,
            "interest_rate": 0.08,
            "inflation_rate": 0.12,
            "exchange_rate": 1.0,
            "federal_minimum_wage": 800.0,
            "gdp_growth_rate": 0.02,
            "gini_coefficient": 0.55,
            "total_ruin_seizures_this_year": 0.0,

            # ── Governance (unchanged) ────────────────────────────────────────
            "corruption_index": 0.72,
            "trust_index": 0.22,
            "stability_index": 0.30,
            "merit_system_integrity": 0.40,
            "iig_effectiveness": 0.30,
            "policy_quality": 0.35,
            "rights_violated": False,
            "rights_score": 0.70,
            "intl_confidence_signal": 0.30,

            # ── Military (unchanged) ──────────────────────────────────────────
            "military_loyalty": 0.55,
            "military_strength": 0.50,
            "coup_risk": 0.25,
            "external_threat": False,
            "threat_level": 0.0,

            # ── Social (unchanged) ────────────────────────────────────────────
            "ethnic_tension_index": 0.68,
            "ethnic_harmony_index": 0.22,
            "network_protest_rate": 0.0,

            # ── IIG (unchanged) ───────────────────────────────────────────────
            "iig_total_active_cases": 0,
            "iig_director_id": None,
            "shame_register": [],
            "shame_register_size": 0,
            "shame_register_signal": {},
            "shame_register_stats": {},
            "total_ruin_events": 0,

            # ── Population (unchanged) ────────────────────────────────────────
            "total_citizens": self.n_citizens,
            "emigrants": [],
            "annual_emigrants": 0,
            "low_corruption_streak": 0,
            "phd_graduates": 0,
            "knowledge_capital_index": 0.0,
            "employment_rate": 0.58,
            "tax_compliance_rate": 0.90,

            # ── Logs (unchanged) ──────────────────────────────────────────────
            "corruption_acts_log": [],
            "bribery_attempts": [],
            "corruption_reports": [],
            "tax_evasion_detected": [],
            "illicit_networks_detected": [],
            "illicit_bribery_attempts": [],
            "high_treason_referrals": [],
            "min_wage_violations": [],
            "active_investigations": [],
            "prosecution_queue": [],
            "court_evidence_custody": [],
            "iig_partner_votes_pending": [],
            "pending_policies": [],
            "approved_policies": [],
            "pending_disputes": [],
            "rights_complaints": [],
            "emergency_declarations": [],
            "methodology_challenges": [],
            "active_sanctions": [],
            "external_insurgent_support": [],
            "analysis_diagnoses": [],
            "ecb_triggers": [],
            "ecb_active": False,
            "ecb_interventions_total": 0,
            "psych_consultation_required": [],
            "psych_probation_officials": [],
            "officials_removed": [],
            "officials_term_complete": [],
            "permanently_disqualified": [],
            "total_ruin_certified": [],
            "inheritance_pool": 0.0,
            "annual_history": [],

            # ── DIFF 3: Phase 2 elite agent outputs ───────────────────────────
            # Written by EliteAgentLayer.step() before Mesa agents run.
            # All Mesa agents can read these from shared_data as normal env.
            "elite_budget_impact":  0.07,        # float [0.0, 0.15]
            "elite_ethnic_weights": [1.0] * 8,   # per-group multiplier, len=8
            "elite_coup_signal":    False,        # Senior General threshold flag
            "elite_decisions_log":  [],           # full log for dissertation analysis
        }

    def _create_agents(self):
        """Create all agents and add to scheduler. Unchanged from Phase 1."""

        # Tier 1 — Citizens
        citizens = CitizenPopulation.create_population(self, self.n_citizens)
        for agent in citizens:
            self.schedule.add(agent)

        # Tier 2 — Officials
        officials = OfficialPopulation.create_population(self)
        for agent in officials:
            self.schedule.add(agent)

        # Tier 3 — Oversight
        oversight = OversightPopulation.create_population(self)
        for agent in oversight:
            self.schedule.add(agent)

        # Tier 4 — Foreign
        foreign = ForeignPopulation.create_population(self)
        for agent in foreign:
            self.schedule.add(agent)

        # Tier 5 — Institutional
        institutional = InstitutionalPopulation.create_population(self)
        for agent in institutional:
            self.schedule.add(agent)

        total = len(self.schedule.agents)
        print(f"Ka-Nova initialized: {total} agents | scenario={self.scenario} | "
              f"seed={self.seed} | LLM={'ON' if self.elite_layer.use_llm else 'OFF (rule-based)'}")

    # ══════════════════════════════════════════════════════════════════════════
    # YEAR ZERO CALIBRATION — unchanged from Phase 1
    # ══════════════════════════════════════════════════════════════════════════

    def _apply_year_zero_calibration(self):
        """
        Force Year Zero agent attributes to match real Myanmar baselines.
        Calibrated from: Transparency International CPI, World Bank, V-Dem.
        Unchanged from Phase 1.
        """

        for agent in self.schedule.agents:
            if isinstance(agent, OfficialAgent):
                agent.corruption_score = random.gauss(0.65, 0.08)
                agent.corruption_score = max(0.40, min(0.90, agent.corruption_score))
                agent.constitutional_loyalty = random.gauss(0.25, 0.08)
                agent.constitutional_loyalty = max(0.05, min(0.50, agent.constitutional_loyalty))

            if isinstance(agent, CitizenAgent) and not isinstance(agent, OfficialAgent):
                agent.trust_score = random.gauss(0.22, 0.08)
                agent.trust_score = max(0.05, min(0.45, agent.trust_score))
                agent.grievance = random.gauss(0.62, 0.10)
                agent.grievance = max(0.35, min(0.85, agent.grievance))
                agent.employment_status = (
                    "employed" if random.random() < 0.58 else "unemployed"
                )
                agent.emigration_threshold = random.gauss(0.45, 0.10)
                agent.emigration_threshold = max(0.20, min(0.70, agent.emigration_threshold))

        self.shared_data["corruption_index"]    = 0.72
        self.shared_data["trust_index"]          = 0.22
        self.shared_data["gini_coefficient"]     = 0.55
        self.shared_data["employment_rate"]      = 0.58
        self.shared_data["ethnic_tension_index"] = 0.68
        self.shared_data["stability_index"]      = 0.18
        self.shared_data["iig_effectiveness"]    = 0.05
        self.shared_data["coup_risk"]            = 0.45
        self.shared_data["brain_drain_rate"]     = 0.35
        self.shared_data["ethnic_harmony_index"] = 0.22
        self.shared_data["military_loyalty"]     = 0.55
        self.shared_data["policy_quality"]       = 0.20
        self.shared_data["merit_system_integrity"] = 0.30
        self.shared_data["gdp_growth_rate"]      = 0.02

        state_corruption = {
            "bamar_central":  0.75,
            "shan_eastern":   0.78,
            "karen_southern": 0.72,
            "kachin_northern": 0.80,
            "mandalay":   0.72, "yangon":     0.68, "magway":      0.74,
            "bago":       0.73, "ayeyarwady": 0.75, "tanintharyi": 0.74,
            "kayah":      0.77, "chin":       0.76, "mon":         0.73,
            "rakhine":    0.82,
        }
        state_trust = {
            "bamar_central":  0.22,
            "shan_eastern":   0.18,
            "karen_southern": 0.20,
            "kachin_northern": 0.15,
            "mandalay":   0.23, "yangon":     0.26, "magway":      0.19,
            "bago":       0.21, "ayeyarwady": 0.20, "tanintharyi": 0.19,
            "kayah":      0.14, "chin":       0.14, "mon":         0.21,
            "rakhine":    0.12,
        }
        for state_id, state in self.states.items():
            state["corruption_level"] = state_corruption.get(state_id, 0.72)
            state["trust_index"]      = state_trust.get(state_id, 0.20)
            state["ethnic_tension"]   = random.gauss(0.70, 0.05)
            state["employment_rate"]  = random.gauss(0.57, 0.03)

    # ══════════════════════════════════════════════════════════════════════════
    # MAIN STEP — ONE YEAR
    # ══════════════════════════════════════════════════════════════════════════

    def step(self):
        """
        Execute one time step (one year).

        Order of operations:
        0. PHASE 2 DIFF 5: Elite agents deliberate → write to shared_data  ← NEW
        1. Pre-step environment broadcast
        2. All agent steps (randomized order)
        3. Network effects propagation
        4. Institutional rules enforcement
        5. Twelve feedback loops
        6. Scenario-specific modifications
        7. State environment update
        8. Special events (elections, reviews, coups)
        9. Annual history snapshot
        10. Data collection
        11. Year increment
        12. Reset annual counters
        """

        # ── DIFF 5: Elite agents deliberate BEFORE Mesa agents step ──────────
        # Chancellor, President, Senior General read current KPIs and decide:
        #   elite_budget_impact   → Article VIII transfer size this year
        #   elite_ethnic_weights  → per-group weighting (len=8)
        #   elite_coup_signal     → Senior General hidden threshold check
        # All written into shared_data. Mesa agents read them as environment.
        self.elite_layer.step(self.shared_data, self.current_year, self.scenario)

        # Handle coup signal from Senior General
        if self.shared_data.get("elite_coup_signal", False):
            if self.scenario == "A":
                # Full MFU — institutional safeguards suppress coup attempt
                self.shared_data["coup_risk"] = max(
                    0.0, self.shared_data.get("coup_risk", 0.25) - 0.05
                )
            else:
                # Scenario B/C — no full safeguards, coup risk escalates
                self.shared_data["coup_risk"] = min(
                    1.0, self.shared_data.get("coup_risk", 0.25) + 0.05
                )
        # ── End DIFF 5 addition ───────────────────────────────────────────────

        # 1. Broadcast environment to all agents
        self._broadcast_environment()

        # 2. All agents step
        self.schedule.step()

        # 3. Network effects
        self._propagate_network_effects()

        # 4. Institutional enforcement
        self._enforce_institutional_rules()

        # 5. Run 12 feedback loops
        self._run_feedback_loops()

        # 6. Scenario modifications
        self._apply_scenario_rules()

        # 7. Update state environments
        self._update_state_environments()

        # 8. Special events (elections, reviews, coups)
        self._check_special_events()

        # 9. Snapshot annual history
        self._snapshot_annual_history()

        # 10. Collect KPIs
        self.datacollector.collect(self)

        # 11. Increment year
        self.current_year += 1

        # 12. Reset annual counters
        self._reset_annual_counters()

    # ══════════════════════════════════════════════════════════════════════════
    # ENVIRONMENT BROADCAST — unchanged from Phase 1
    # ══════════════════════════════════════════════════════════════════════════

    def _broadcast_environment(self):
        """
        Broadcast current environment state to all agents.
        Mechanism 2 — Environment Signaling.
        """
        self.shared_data["corruption_index"] = self._calculate_corruption_index()
        self.shared_data["stability_index"]  = self._calculate_stability_index()
        self.shared_data["ethnic_tension_index"] = self._calculate_ethnic_tension()
        self.shared_data["employment_rate"]  = self._calculate_employment_rate()

    def _calculate_corruption_index(self) -> float:
        officials = [a for a in self.schedule.agents if isinstance(a, OfficialAgent)]
        if not officials:
            return 0.65
        return min(1.0, sum(a.corruption_score for a in officials) / len(officials))

    def _calculate_stability_index(self) -> float:
        coup_risk = self.shared_data.get("coup_risk", 0.25)
        rights_ok = 0.0 if self.shared_data.get("rights_violated", False) else 0.20
        trust = self.shared_data.get("trust_index", 0.22)
        iig = self.shared_data.get("iig_effectiveness", 0.30)
        return max(0.0, min(1.0, (1.0 - coup_risk) * 0.40 + rights_ok + trust * 0.25 + iig * 0.15))

    def _calculate_ethnic_tension(self) -> float:
        tensions = [s.get("ethnic_tension", 0.60) for s in self.states.values()]
        return sum(tensions) / len(tensions) if tensions else 0.60

    def _calculate_employment_rate(self) -> float:
        citizens = [
            a for a in self.schedule.agents
            if isinstance(a, CitizenAgent) and not isinstance(a, OfficialAgent)
            and 18 <= a.age <= 65 and a.is_alive and not a.has_emigrated
        ]
        if not citizens:
            return 0.58
        employed = sum(1 for a in citizens if a.employment_status == "employed")
        return employed / len(citizens)

    # ══════════════════════════════════════════════════════════════════════════
    # NETWORK EFFECTS — unchanged from Phase 1
    # ══════════════════════════════════════════════════════════════════════════

    def _propagate_network_effects(self):
        """
        Propagate signals through agent networks.
        Mechanism 3 — Network Communication.
        """
        broadcasting = [
            a for a in self.schedule.agents
            if hasattr(a, "has_event_to_broadcast") and a.has_event_to_broadcast
        ]

        for broadcaster in broadcasting:
            signal = broadcaster.broadcast_signal
            if not signal:
                continue
            all_agents = list(self.schedule.agents)
            sample_size = min(50, len(all_agents))
            neighbors = random.sample(all_agents, sample_size)
            for neighbor in neighbors:
                if hasattr(neighbor, "receive_signal"):
                    neighbor.receive_signal(signal, distance=1)
            broadcaster.has_event_to_broadcast = False

        if self.shared_data.get("shame_register_signal"):
            for agent in self.schedule.agents:
                if isinstance(agent, OfficialAgent) and hasattr(agent, "observe_shame_register_update"):
                    for entry in self.shared_data.get("total_ruin_certified", []):
                        agent.observe_shame_register_update(entry)

    # ══════════════════════════════════════════════════════════════════════════
    # INSTITUTIONAL RULES ENFORCEMENT — unchanged from Phase 1
    # ══════════════════════════════════════════════════════════════════════════

    def _enforce_institutional_rules(self):
        """
        Enforce constitutional rules automatically.
        Mechanism 4 — Institutional Rules.
        """
        self._enforce_iig_triggers()
        self._enforce_total_ruin()
        self._enforce_coup_detection()
        self._enforce_rights_protections()
        self._enforce_merit_disqualifications()

    def _enforce_iig_triggers(self):
        """Article 7.4 — trigger at 0.70 corruption score."""
        trigger = CONSTITUTION.iig.INVESTIGATION_TRIGGER
        log = self.shared_data.get("corruption_acts_log", [])
        above_threshold = [
            act for act in log
            if act.get("corruption_score", 0.0) >= trigger
            and not act.get("investigated", False)
        ]
        if above_threshold:
            self.shared_data["iig_trigger_count"] = (
                self.shared_data.get("iig_trigger_count", 0) + len(above_threshold)
            )

    def _enforce_total_ruin(self):
        """Article 15 — automatic execution, no discretion."""
        for certification in self.shared_data.get("total_ruin_certified", []):
            if certification.get("executed", False):
                continue
            target_id = certification.get("target_id")
            for agent in self.schedule.agents:
                if (isinstance(agent, OfficialAgent) and
                        agent.unique_id == target_id and
                        not agent.total_ruin_triggered):
                    agent.trigger_total_ruin()
                    self.shared_data["total_ruin_events"] = (
                        self.shared_data.get("total_ruin_events", 0) + 1
                    )
            certification["executed"] = True

    def _enforce_coup_detection(self):
        """Article 9.4 — coup trigger conditions."""
        military_loyalty = self.shared_data.get("military_loyalty", 0.55)
        chancellor_approval = 0.50
        chancellors = [a for a in self.schedule.agents if isinstance(a, ChancellorAgent)]
        if chancellors:
            chancellor_approval = chancellors[0].approval_rating

        coup_threshold_loyalty  = CONSTITUTION.military.COUP_TRIGGER_LOYALTY
        coup_threshold_approval = CONSTITUTION.military.COUP_TRIGGER_APPROVAL

        if (military_loyalty < coup_threshold_loyalty and
                chancellor_approval < coup_threshold_approval):
            coup_risk = (
                (coup_threshold_loyalty  - military_loyalty)  * 0.50 +
                (coup_threshold_approval - chancellor_approval) * 0.50
            )
            self.shared_data["coup_risk"] = min(1.0, coup_risk)
            if self.shared_data["coup_risk"] > 0.60:
                self._attempt_coup()
        else:
            self.shared_data["coup_risk"] = max(
                0.0, self.shared_data.get("coup_risk", 0.0) - 0.02
            )

    def _attempt_coup(self):
        """Coup attempt — branching by scenario."""
        if self.scenario == "A":
            self.shared_data["coup_attempt_year"] = self.current_year
            self.shared_data["coup_blocked_by_constitution"] = True
            self.shared_data["coup_risk"] = max(
                0.0, self.shared_data["coup_risk"] - 0.30
            )
            self.shared_data["trust_index"] = max(
                0.0, self.shared_data.get("trust_index", 0.30) - 0.10
            )
        elif self.scenario == "B":
            if random.random() < 0.40:
                self.shared_data["coup_succeeded"]    = True
                self.shared_data["simulation_failed"] = True
                self.shared_data["failure_year"]      = self.current_year
                self.shared_data["failure_reason"]    = "coup_succeeded_no_safeguards"
        elif self.scenario == "C":
            if random.random() < 0.70:
                self.shared_data["coup_succeeded"]    = True
                self.shared_data["simulation_failed"] = True
                self.shared_data["failure_year"]      = self.current_year
                self.shared_data["failure_reason"]    = "military_baseline_coup"

    def _enforce_rights_protections(self):
        """Article 2.4 — all six rights are absolute and non-suspendable."""
        if self.shared_data.get("rights_violated", False):
            for agent in self.schedule.agents:
                if isinstance(agent, CitizenAgent):
                    agent.grievance = min(
                        1.0,
                        agent.grievance + CONSTITUTION.rights.RIGHTS_VIOLATION_GRIEVANCE_SPIKE
                    )
                    agent.trust_score = max(
                        0.0,
                        agent.trust_score - CONSTITUTION.rights.RIGHTS_VIOLATION_TRUST_DROP
                    )
            self.shared_data["trust_index"] = max(
                0.0, self.shared_data.get("trust_index", 0.30) - 0.15
            )

    def _enforce_merit_disqualifications(self):
        """Article 3.5 — permanent, no appeal."""
        for agent in self.schedule.agents:
            if isinstance(agent, OfficialAgent):
                if agent.permanently_disqualified and not agent.removed_mid_term:
                    agent._remove_from_office("permanent_disqualification")

    # ══════════════════════════════════════════════════════════════════════════
    # TWELVE FEEDBACK LOOPS
    # ══════════════════════════════════════════════════════════════════════════

    def _run_feedback_loops(self):
        """Run all 12 constitutional feedback loops annually."""
        self._loop_P1_trust_legitimacy()
        self._loop_P2_iig_corruption()
        self._loop_P3_coup_probability()
        self._loop_P4_election_merit()
        self._loop_E1_state_competition()
        self._loop_E2_foreign_investment()
        self._loop_E3_resource_revenue()
        self._loop_E4_phd_economy()
        self._loop_S1_national_service()
        self._loop_S2_grievance_protest()
        self._loop_S3_cultural_offense()
        self._loop_S4_shame_register()

    def _loop_P1_trust_legitimacy(self):
        """
        P1 — Trust drives legitimacy drives stability.
        v7: Trust acceleration when corruption < 0.20 for 5+ consecutive years.
        Unchanged from Phase 1.
        """
        performance = self.shared_data.get("policy_quality", 0.35)
        current_trust = self.shared_data.get("trust_index", 0.22)
        new_trust = current_trust * 0.70 + performance * 0.30

        corruption = self.shared_data.get("corruption_index", 1.0)
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

        for agent in self.schedule.agents:
            if isinstance(agent, CitizenAgent) and not isinstance(agent, OfficialAgent):
                agent.trust_score = agent.trust_score * 0.70 + performance * 0.30

    def _loop_P2_iig_corruption(self):
        """P2 — IIG effectiveness drives corruption down. Unchanged."""
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

    def _loop_P3_coup_probability(self):
        """P3 — Military loyalty determines coup risk. Unchanged."""
        base_loyalty = 0.55
        constitutional_commitment = (
            1.0 if self.scenario == "A" else
            0.70 if self.scenario == "B" else
            0.30
        )
        trust = self.shared_data.get("trust_index", 0.22)
        self.shared_data["military_loyalty"] = min(
            1.0,
            base_loyalty * 0.40 + constitutional_commitment * 0.40 + trust * 0.20
        )

    def _loop_P4_election_merit(self):
        """P4 — Merit recertification improves leadership quality. Unchanged."""
        if self.current_year % CONSTITUTION.merit.RECERTIFICATION_INTERVAL == 0:
            officials = [a for a in self.schedule.agents if isinstance(a, OfficialAgent)]
            if officials:
                avg_merit = sum(a.merit_score for a in officials) / len(officials)
                self.shared_data["merit_system_integrity"] = avg_merit
                self.shared_data["policy_quality"] = min(
                    1.0, avg_merit * 0.80 + random.uniform(0.0, 0.10)
                )

    def _loop_E1_state_competition(self):
        """E1 — State competition drives growth. Unchanged."""
        for state_id, state in self.states.items():
            base_growth    = state.get("gdp_growth", 0.01)
            budget_boost   = state.get("budget", 0.0) * 0.0001
            knowledge_boost = state.get("knowledge_capital", 0.0) * 0.002
            new_growth     = base_growth + budget_boost + knowledge_boost
            state["gdp"]   = state.get("gdp", 100.0) * (1.0 + new_growth)
            state["gdp_growth"] = min(0.12, new_growth)
        self.shared_data["gdp_growth_rate"] = (
            sum(s.get("gdp_growth", 0.01) for s in self.states.values()) /
            len(self.states)
        )

    def _loop_E2_foreign_investment(self):
        """E2 — FDI drives technology transfer. Unchanged."""
        active_investors = self.shared_data.get("active_foreign_investors", 0)
        if active_investors > 0:
            tech_transfer = active_investors * 0.005
            for state in self.states.values():
                state["knowledge_capital"] = (
                    state.get("knowledge_capital", 0.0) + tech_transfer
                )

    def _loop_E3_resource_revenue(self):
        """
        E3 — Resource revenue split reduces inequality.

        DIFF 5 — GINI BUG FIX:
        Phase 1 bug: community share went into a pool, never reached
        agent.household_income, so Gini reporter saw no change → stuck at 0.570.

        Fix: community share now distributed directly to agent.household_income
        using NumPy vectorised rank-based progressive weighting.
        Bottom 40% of income distribution gets 1.5× per-capita share.
        Top 60% gets 0.67× per-capita share.
        No Python loop for the arithmetic — only one assignment loop at the end.

        Only active in Scenario A and B (Article VIII).
        Scenario C has no direct transfers — military captures revenue.
        """
        gini = self.shared_data.get("gini_coefficient", 0.55)
        if gini > CONSTITUTION.federal.GINI_THRESHOLD:
            for state in self.states.values():
                state["resource_revenue"] = (
                    state.get("resource_revenue", 0.0) * 0.98
                )

        # ── PHASE 2 GINI FIX: NumPy vectorised direct household transfer ─────
        if self.scenario in ("A", "B"):
            budget_impact = self.shared_data.get("elite_budget_impact", 0.07)
            total_revenue = sum(
                s.get("resource_revenue", 0.0) for s in self.states.values()
            )
            community_share = (
                total_revenue
                * CONSTITUTION.federal.RESOURCE_SPLIT_COMMUNITY
                * budget_impact
            )

            # Collect living, non-emigrated citizens once
            citizen_agents = [
                a for a in self.schedule.agents
                if isinstance(a, CitizenAgent)
                and not isinstance(a, OfficialAgent)
                and a.is_alive
                and not a.has_emigrated
            ]

            if citizen_agents and community_share > 0:
                n = len(citizen_agents)

                # Pull incomes into NumPy array — single allocation
                incomes = np.array(
                    [a.household_income for a in citizen_agents],
                    dtype=np.float64
                )

                # Rank-based progressive weights — fully vectorised, O(N log N)
                ranks      = np.argsort(np.argsort(incomes))   # stable rank
                percentiles = ranks / n                         # [0, 1)
                weights    = np.where(percentiles < 0.40, 1.5, 0.67)

                # Normalise so total transfer == community_share exactly
                weights    = weights / weights.sum()
                transfers  = weights * community_share          # NumPy broadcast

                # Write back — arithmetic already done above, this is O(N) assignment only
                for agent, transfer in zip(citizen_agents, transfers):
                    agent.household_income = max(0.0, agent.household_income + transfer)
                    agent.income           = agent.household_income   # keep in sync

    def _loop_E4_phd_economy(self):
        """E4 — PhD graduates compound knowledge capital. Unchanged."""
        phd_graduates = self.shared_data.get("phd_graduates", 0)
        if phd_graduates > 0:
            knowledge_boost = phd_graduates * CONSTITUTION.science.PHD_KNOWLEDGE_CAPITAL_BOOST
            self.shared_data["knowledge_capital_index"] = min(
                1.0,
                self.shared_data.get("knowledge_capital_index", 0.0) +
                knowledge_boost * 0.01
            )

    def _loop_S1_national_service(self):
        """S1 — National service builds ethnic cross-exposure. Unchanged."""
        ns_graduates = [
            a for a in self.schedule.agents
            if isinstance(a, CitizenAgent) and
            a.national_service_completed and
            a.age == 19
        ]
        if ns_graduates:
            for agent in ns_graduates:
                agent.ethnic_cross_exposure = min(
                    1.0,
                    agent.ethnic_cross_exposure +
                    CONSTITUTION.military.NS_ETHNIC_EXPOSURE_BOOST
                )
            for state in self.states.values():
                state["ethnic_tension"] = max(
                    0.0, state.get("ethnic_tension", 0.60) - 0.01
                )

    def _loop_S2_grievance_protest(self):
        """S2 — Grievance drives protest. Unchanged."""
        protesters = [
            a for a in self.schedule.agents
            if isinstance(a, CitizenAgent) and a.is_protesting
        ]
        protest_rate = len(protesters) / max(1, self.n_citizens)
        self.shared_data["network_protest_rate"] = protest_rate
        if protest_rate > 0.10:
            self.shared_data["trust_index"] = max(
                0.0, self.shared_data.get("trust_index", 0.22) - 0.05
            )
            for state in self.states.values():
                state["protest_activity"] = protest_rate

    def _loop_S3_cultural_offense(self):
        """S3 — Cultural offenses raise ethnic tension. Unchanged."""
        ethnic_tension = self.shared_data.get("ethnic_tension_index", 0.68)
        if ethnic_tension > 0.70:
            for state in self.states.values():
                state["ethnic_tension"] = min(
                    1.0, state.get("ethnic_tension", 0.60) + 0.01
                )
        elif ethnic_tension < 0.40:
            for state in self.states.values():
                state["ethnic_tension"] = max(
                    0.0, state.get("ethnic_tension", 0.60) - 0.01
                )

    def _loop_S4_shame_register(self):
        """S4 — Shame register creates compounding deterrence. Unchanged."""
        shame_size = self.shared_data.get("shame_register_size", 0)
        if shame_size > 0:
            deterrence = min(0.40, shame_size * 0.01)
            self.shared_data["corruption_deterrence"] = deterrence

    # ══════════════════════════════════════════════════════════════════════════
    # SCENARIO RULES — unchanged from Phase 1
    # ══════════════════════════════════════════════════════════════════════════

    def _apply_scenario_rules(self):
        if self.scenario == "A":
            self._scenario_a_rules()
        elif self.scenario == "B":
            self._scenario_b_rules()
        elif self.scenario == "C":
            self._scenario_c_rules()

    def _scenario_a_rules(self):
        """Full MFU — all constitutional safeguards enforced."""
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

    def _scenario_b_rules(self):
        """MFU without safeguards — loopholes open."""
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
                if random.random() < 0.03:
                    agent.corruption_score = min(
                        1.0, agent.corruption_score + 0.02
                    )

    def _scenario_c_rules(self):
        """Military baseline — no MFU constitutional rules."""
        if random.random() < 0.20:
            self.shared_data["rights_violated"] = True
        self.shared_data["iig_effectiveness"] = 0.05
        current_trust = self.shared_data.get("trust_index", 0.22)
        self.shared_data["trust_index"] = max(
            0.08, current_trust - 0.015
        )
        self.shared_data["policy_quality"] = max(
            0.10, self.shared_data.get("policy_quality", 0.20) - 0.005
        )
        self.shared_data["coup_risk"] = min(
            0.60, self.shared_data.get("coup_risk", 0.25) + 0.015
        )
        for state in self.states.values():
            state["ethnic_tension"] = min(
                0.90, state.get("ethnic_tension", 0.68) + 0.005
            )
        for agent in self.schedule.agents:
            if isinstance(agent, OfficialAgent):
                agent.corruption_score = min(
                    0.95, agent.corruption_score + random.uniform(0.01, 0.04)
                )
        for agent in self.schedule.agents:
            if isinstance(agent, CitizenAgent) and not isinstance(agent, OfficialAgent):
                agent.trust_score = max(
                    0.05, agent.trust_score - random.gauss(0.015, 0.005)
                )
                agent.grievance = min(
                    1.0, agent.grievance + random.gauss(0.010, 0.003)
                )

    # ══════════════════════════════════════════════════════════════════════════
    # STATE ENVIRONMENT UPDATE — unchanged from Phase 1
    # ══════════════════════════════════════════════════════════════════════════

    def _update_state_environments(self):
        """Update state environment variables from agent actions."""
        for state_id, state in self.states.items():
            iig_in_state = [
                a for a in self.schedule.agents
                if isinstance(a, IIGAgent) and a.state_id == state_id
            ]
            state["iig_activity"] = min(
                1.0, len([a for a in iig_in_state if a.active_cases]) * 0.10
            )
            officials_in_state = [
                a for a in self.schedule.agents
                if isinstance(a, OfficialAgent) and a.state_id == state_id
            ]
            if officials_in_state:
                state["corruption_level"] = (
                    sum(a.corruption_score for a in officials_in_state) /
                    len(officials_in_state)
                )
            workers = [
                a for a in self.schedule.agents
                if isinstance(a, CitizenAgent) and
                a.state_id == state_id and
                a.employment_status == "employed"
            ]
            total_working_age = [
                a for a in self.schedule.agents
                if isinstance(a, CitizenAgent) and
                a.state_id == state_id and
                18 <= a.age <= 65
            ]
            if total_working_age:
                state["employment_rate"] = len(workers) / len(total_working_age)
            state["protest_activity"] = max(
                0.0, state.get("protest_activity", 0.0) - 0.05
            )

    # ══════════════════════════════════════════════════════════════════════════
    # SPECIAL EVENTS — unchanged from Phase 1
    # ══════════════════════════════════════════════════════════════════════════

    def _check_special_events(self):
        """Check for constitutionally scheduled events."""
        if self.current_year % CONSTITUTION.executive.PRESIDENT_TERM == 1:
            self.shared_data["election_year"] = True
        if (self.current_year - 2) % CONSTITUTION.executive.CHANCELLOR_TERM == 0:
            self.shared_data["chancellor_election_year"] = True
        if self.current_year % CONSTITUTION.merit.RECERTIFICATION_INTERVAL == 0:
            self.shared_data["recertification_year"] = True
        if (self.current_year > 0 and
                self.current_year % CONSTITUTION.amendment.REVIEW_INTERVAL == 0):
            self._constitutional_review()
        emergency_year = self.shared_data.get("emergency_start_year")
        if emergency_year:
            if self.current_year - emergency_year >= (
                CONSTITUTION.emergency.MAX_DURATION_DAYS / 365
            ):
                self.shared_data["emergency_active"] = False
                self.shared_data["emergency_start_year"] = None

    def _constitutional_review(self):
        """
        Mandatory 10-year constitutional review.
        Article 12.3 — Citizens Assembly by civic lottery.
        """
        self.shared_data["constitutional_review_year"] = self.current_year
        self.shared_data["citizens_assembly_active"] = True
        eligible_citizens = [
            a for a in self.schedule.agents
            if isinstance(a, CitizenAgent) and
            not isinstance(a, OfficialAgent) and
            a.age >= 18 and a.is_alive and not a.has_emigrated
        ]
        assembly_size = min(
            CONSTITUTION.amendment.CITIZENS_ASSEMBLY_SIZE,
            len(eligible_citizens)
        )
        if eligible_citizens:
            assembly = random.sample(eligible_citizens, assembly_size)
            assembly_support = sum(
                1 for a in assembly if a.trust_score > 0.50
            ) / assembly_size
            self.shared_data["constitutional_review_result"] = {
                "year": self.current_year,
                "assembly_size": assembly_size,
                "support_rate": assembly_support,
                "system_reaffirmed": assembly_support > 0.50
            }

    # ══════════════════════════════════════════════════════════════════════════
    # HISTORY AND RESET — unchanged from Phase 1
    # ══════════════════════════════════════════════════════════════════════════

    def _snapshot_annual_history(self):
        """Snapshot key metrics for information lag calculations."""
        snapshot = {
            "year":              self.current_year,
            "corruption_index":  self.shared_data.get("corruption_index", 0.65),
            "trust_index":       self.shared_data.get("trust_index", 0.22),
            "stability_index":   self.shared_data.get("stability_index", 0.30),
            "iig_effectiveness": self.shared_data.get("iig_effectiveness", 0.30),
            "employment_rate":   self.shared_data.get("employment_rate", 0.58),
            "gini_coefficient":  self.shared_data.get("gini_coefficient", 0.55),
            "gdp_growth_rate":   self.shared_data.get("gdp_growth_rate", 0.02),
        }
        self.shared_data["annual_history"].append(snapshot)
        if len(self.shared_data["annual_history"]) > 10:
            self.shared_data["annual_history"].pop(0)

    def _reset_annual_counters(self):
        """Reset annual flow counters for next year."""
        self.shared_data["fdi_inflow"]                   = 0.0
        self.shared_data["fdi_outflow"]                  = 0.0
        self.shared_data["total_aid_received"]           = 0.0
        self.shared_data["phd_graduates"]                = 0
        self.shared_data["rights_violated"]              = False
        self.shared_data["annual_emigrants"]             = 0
        self.shared_data["election_year"]                = False
        self.shared_data["chancellor_election_year"]     = False
        self.shared_data["recertification_year"]         = False
        self.shared_data["citizens_assembly_active"]     = False
        self.shared_data["total_ruin_seizures_this_year"] = 0.0

    # ══════════════════════════════════════════════════════════════════════════
    # UTILITY — unchanged from Phase 1
    # ══════════════════════════════════════════════════════════════════════════

    def run(self, steps: int = None):
        """Run the simulation for n steps."""
        steps = steps or self.max_years
        for _ in range(steps):
            if self.shared_data.get("simulation_failed", False):
                print(f"Simulation ended early: year={self.current_year}, "
                      f"reason={self.shared_data.get('failure_reason')}")
                break
            self.step()

    def get_results(self):
        """Return collected KPI data as DataFrame."""
        return self.datacollector.get_model_vars_dataframe()

    def summary(self) -> str:
        """Return current state summary."""
        return (
            f"Ka-Nova Year {self.current_year} | Scenario {self.scenario}\n"
            f"  Corruption:   {self.shared_data.get('corruption_index', 0):.3f}\n"
            f"  Trust:        {self.shared_data.get('trust_index', 0):.3f}\n"
            f"  IIG Effect:   {self.shared_data.get('iig_effectiveness', 0):.3f}\n"
            f"  Coup Risk:    {self.shared_data.get('coup_risk', 0):.3f}\n"
            f"  Gini:         {self.shared_data.get('gini_coefficient', 0):.3f}\n"
            f"  Shame Reg:    {self.shared_data.get('shame_register_size', 0)}\n"
            f"  Total Ruin:   {self.shared_data.get('total_ruin_events', 0)}\n"
            f"  FDI Active:   {self.shared_data.get('active_foreign_investors', 0)}\n"
            f"  Elite Budget: {self.shared_data.get('elite_budget_impact', 0):.3f}\n"
            f"  North Star:   {get_north_star_progress(self):.3f}"
        )


# ══════════════════════════════════════════════════════════════════════════════
# QUICK TEST
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":

    print("Testing Ka-Nova Model Phase 2...")
    print("Initializing Scenario A (Full MFU, rule-based elite agents)...\n")

    model = KaNovaModel(scenario="A", seed=42, n_citizens=500, use_llm=False)

    print(f"\nRunning 5 time steps...")
    for year in range(5):
        model.step()
        print(f"\n{model.summary()}")

    results = model.get_results()
    print(f"\nKPI columns collected: {list(results.columns)}")
    print(f"Rows (time steps): {len(results)}")
    print(f"\nmodel.py Phase 2 loaded successfully")