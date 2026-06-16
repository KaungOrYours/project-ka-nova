"""
================================================================================
PROJECT KA-NOVA
model_phase3.py

Phase 3 Model — extends KaNovaModel with:
1. Constitution import switch — MFU (A) vs 2008 Myanmar (C)
2. ExternalLayer — 17 evolving vectors + stochastic shocks
3. SocialMediaChannel — VPN floor, LLM-controlled openness, ethnic networks
4. 56 ethnic-archetype combinations via _calculate_ethnic_archetype_counts
5. elite_agents_v3 import switch (Sam's file — wired when ready)

Architecture:
    Pod 1 (RunPod): python3 run_phase3.py --scenario A
    Pod 2 (RunPod): python3 run_phase3.py --scenario C
    Same external shock seed per run_id — no bias between scenarios.

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
from mesa import Model
from mesa.time import RandomActivation
from mesa.datacollection import DataCollector

# ── Constitution import switch ────────────────────────────────────────────────
# Scenario A: MFU Constitution (v7)
# Scenario C: 2008 Myanmar Military Constitution (D's file — wired when ready)
# model_phase3 resolves this at __init__ time based on scenario argument
from config.constitution import CONSTITUTION as CONSTITUTION_MFU

try:
    from config.constitution_2008 import CONSTITUTION_2008
    CONSTITUTION_2008_AVAILABLE = True
except ImportError:
    CONSTITUTION_2008_AVAILABLE = False
    CONSTITUTION_2008 = None

# ── Agent imports ─────────────────────────────────────────────────────────────
from agents.citizen import CitizenAgent, CitizenPopulation
from agents.official import (
    OfficialAgent, OfficialPopulation, AnalysisCouncilMember
)
from agents.oversight import (
    IIGAgent, OversightPopulation
)
from agents.foreign import ForeignPopulation
from agents.institutional import InstitutionalPopulation

# ── Institution imports ───────────────────────────────────────────────────────
from institutions.chambers import ThreeChamberSystem
from institutions.court import ConstitutionalCourtSystem
from institutions.iig import IIGSystem
from feedback.loops import FeedbackEngine

# ── Phase 3 engine imports ────────────────────────────────────────────────────
from engine.external_layer import ExternalLayer
from engine.social_media import SocialMediaChannel

# ── Elite agent import switch ─────────────────────────────────────────────────
# Phase 3: Sam's elite_agents_v3.py (wired when ready)
# Phase 2 fallback: original elite_agents.py
try:
    from engine.elite_agents_v3 import EliteAgentLayerV3 as EliteAgentLayer
    ELITE_V3_AVAILABLE = True
except ImportError:
    from engine.elite_agents import EliteAgentLayer
    ELITE_V3_AVAILABLE = False


# ── KPI reporter functions (same as model.py) ─────────────────────────────────
def get_corruption_index(m):
    return m.shared_data.get("corruption_index", 0.72)

def get_trust_index(m):
    return m.shared_data.get("trust_index", 0.22)

def get_grievance_index(m):
    return m.shared_data.get("grievance_index", 0.60)

def get_iig_effectiveness(m):
    return m.shared_data.get("iig_effectiveness", 0.30)

def get_coup_probability(m):
    return m.shared_data.get("coup_risk", 0.25)

def get_north_star_progress(m):
    return m.shared_data.get("north_star_progress", 0.0)

def get_gini_coefficient(m):
    return m.shared_data.get("gini_coefficient", 0.55)

def get_ethnic_harmony(m):
    return m.shared_data.get("ethnic_harmony", 0.35)

def get_stability_index(m):
    return m.shared_data.get("stability_index", 0.18)

def get_employment_rate(m):
    return m.shared_data.get("employment_rate", 0.58)

def get_brain_drain_rate(m):
    return m.shared_data.get("brain_drain_rate", 0.35)

def get_vpn_floor(m):
    return m.social_media.vpn_floor if hasattr(m, "social_media") else 0.35

def get_social_media_openness(m):
    sm = m.shared_data.get("social_media", {})
    return sm.get("final_openness", 1.0)

def get_active_shocks(m):
    ext = m.shared_data.get("external", {})
    return len(ext.get("active_shocks", []))

def get_china_influence(m):
    ext = m.shared_data.get("external", {})
    return ext.get("china_influence", 0.75)


class KaNovaModelPhase3(Model):
    """
    Ka-Nova Phase 3 Model.

    Extends Phase 2 architecture with:
    - Constitution import switch (A=MFU, C=2008 Myanmar)
    - ExternalLayer (17 vectors, stochastic shocks)
    - SocialMediaChannel (VPN floor, suppression backfire)
    - 56 ethnic-archetype citizen combinations
    - elite_agents_v3 when Sam's file is ready

    Pod strategy:
        python3 run_phase3.py --scenario A --runs 100  (Pod 1)
        python3 run_phase3.py --scenario C --runs 100  (Pod 2)
    """

    def __init__(
        self,
        scenario: str = "A",
        seed: int = None,
        n_citizens: int = 11000,
        use_llm: bool = False,
    ):
        super().__init__()

        # ── Seed ──────────────────────────────────────────────────────────────
        if seed is not None:
            random.seed(seed)
            np.random.seed(seed)
        self.seed = seed
        self.scenario = scenario

        # ── Constitution switch ───────────────────────────────────────────────
        if scenario == "C" and CONSTITUTION_2008_AVAILABLE:
            self.CONSTITUTION = CONSTITUTION_2008
            self.constitution_name = "2008_myanmar_military"
        else:
            self.CONSTITUTION = CONSTITUTION_MFU
            self.constitution_name = "mfu_v7"
            if scenario == "C" and not CONSTITUTION_2008_AVAILABLE:
                print("WARNING: constitution_2008.py not found — "
                      "Scenario C using rule-based military baseline")

        # ── Configuration ─────────────────────────────────────────────────────
        self.n_citizens = n_citizens
        self.current_year = 0
        self.max_years = CONSTITUTION_MFU.simulation.TIME_STEPS  # Always 50

        # ── Scheduler ─────────────────────────────────────────────────────────
        self.schedule = RandomActivation(self)

        # ── Elite agent layer ─────────────────────────────────────────────────
        self.elite_layer = EliteAgentLayer(use_llm=use_llm)
        if ELITE_V3_AVAILABLE:
            print("Elite agents: v3")
        else:
            print("Elite agents: Phase 2 fallback (elite_agents.py)")

        # ── Phase 3 engines ───────────────────────────────────────────────────
        # Same seed for external layer — both scenarios face identical shocks
        external_seed = seed if seed is not None else 42
        self.external_layer = ExternalLayer(seed=external_seed)
        self.social_media = SocialMediaChannel(
            scenario=scenario, seed=external_seed
        )

        # ── Environment ───────────────────────────────────────────────────────
        self.states = self._initialize_states()

        # ── Shared data ───────────────────────────────────────────────────────
        self.shared_data = self._initialize_shared_data()

        # ── Institutions ──────────────────────────────────────────────────────
        self.chambers = ThreeChamberSystem(self)
        self.court = ConstitutionalCourtSystem(self)
        self.iig_system = IIGSystem(self)
        self.feedback_engine = FeedbackEngine(self)

        # ── Create agents ─────────────────────────────────────────────────────
        self._create_agents_phase3()

        # ── Data collector ────────────────────────────────────────────────────
        self.datacollector = DataCollector(
            model_reporters={
                "year":                  lambda m: m.current_year,
                "scenario":              lambda m: m.scenario,
                "constitution":          lambda m: m.constitution_name,
                "corruption_index":      get_corruption_index,
                "trust_index":           get_trust_index,
                "grievance_index":       get_grievance_index,
                "iig_effectiveness":     get_iig_effectiveness,
                "coup_probability":      get_coup_probability,
                "north_star_progress":   get_north_star_progress,
                "gini_coefficient":      get_gini_coefficient,
                "ethnic_harmony":        get_ethnic_harmony,
                "stability_index":       get_stability_index,
                "employment_rate":       get_employment_rate,
                "brain_drain_rate":      get_brain_drain_rate,
                "vpn_floor":             get_vpn_floor,
                "social_media_openness": get_social_media_openness,
                "active_shocks":         get_active_shocks,
                "china_influence":       get_china_influence,
            }
        )

        self.datacollector.collect(self)

    def _initialize_states(self) -> dict:
        """14 states with year-zero conditions."""
        states = {}
        state_list = [
            "sagaing", "mandalay", "magway", "bago",
            "yangon", "ayeyarwady", "tanintharyi", "shan",
            "kachin", "kayah", "kayin", "chin",
            "mon", "rakhine",
        ]
        for state_id in state_list:
            states[state_id] = {
                "corruption":       random.uniform(0.65, 0.80),
                "trust":            random.uniform(0.15, 0.30),
                "gdp_growth":       random.uniform(-0.02, 0.04),
                "ethnic_tension":   random.uniform(0.50, 0.75),
                "resource_revenue": random.uniform(0.10, 0.40),
                "employment":       random.uniform(0.50, 0.65),
            }
        return states

    def _initialize_shared_data(self) -> dict:
        """Year Zero shared state — real Myanmar baselines."""
        return {
            "corruption_index":     0.72,
            "trust_index":          0.22,
            "grievance_index":      0.60,
            "gini_coefficient":     0.55,
            "employment_rate":      0.58,
            "ethnic_harmony":       0.35,
            "iig_effectiveness":    0.30,
            "coup_risk":            0.25,
            "stability_index":      0.18,
            "brain_drain_rate":     0.35,
            "north_star_progress":  0.0,
            "protest_rate":         0.0,
            "shame_register_size":  0,
            "total_ruin_events":    0,
            "military_loyalty":     0.55,
            "policy_quality":       0.50,
            "rights_violated":      False,
            "simulation_failed":    False,
            "active_ethnic_groups": [
                "Bamar", "Shan", "Karen", "Kachin",
                "Chin", "Mon", "Rakhine", "Kayah"
            ],
            "external":             {},
            "social_media":         {},
            "citizen_information_exposure": 1.0,
            "emigrants":             [],
            "annual_emigrants":      0,
            "bribery_attempts":     [],
            "corruption_reports":   [],
            "tax_evasion_detected": [],
            "tax_revenue":          0.0,
            "phd_graduates":        0,
        }

    def _create_agents_phase3(self):
        """
        Phase 3 agent creation.
        Uses 56 ethnic-archetype combinations via
        CitizenPopulation._calculate_ethnic_archetype_counts().
        """
        from agents.citizen import ETHNIC_ARCHETYPE_PROPORTIONS

        # Tier 1 — Citizens with ethnic-archetype combinations
        assignments = CitizenPopulation._calculate_ethnic_archetype_counts(
            self.n_citizens
        )

        agent_id = 0
        for assignment in assignments:
            state_id = CitizenPopulation._assign_state()
            age = CitizenPopulation._assign_age()
            agent = CitizenAgent(
                unique_id=agent_id,
                model=self,
                archetype=assignment["archetype"],
                state_id=state_id,
                ethnicity=assignment["ethnicity"],
                age=age,
            )
            self.schedule.add(agent)
            agent_id += 1

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
        print(
            f"Ka-Nova Phase 3 initialized: {total} agents | "
            f"scenario={self.scenario} | "
            f"constitution={self.constitution_name} | "
            f"seed={self.seed} | "
            f"LLM={'ON' if self.elite_layer.use_llm else 'OFF'}"
        )

    def step(self):
        """
        Phase 3 step — one simulated year.

        Order:
        0. External layer step — evolve vectors, fire shocks
        1. Social media step — compute citizen information exposure
        2. Elite agents deliberate (read external + social media signals)
        3. Broadcast environment to all agents
        4. All agent steps
        5. Twelve feedback loops
        6. Scenario-specific constitutional rules
        7. Institutions (chambers, court, IIG)
        8. State environment update
        9. Data collection
        10. Year increment
        """

        # ── 0. External layer ─────────────────────────────────────────────────
        self.external_layer.step(
            year=self.current_year,
            shared_data=self.shared_data
        )

        # ── 1. Social media ───────────────────────────────────────────────────
        self.social_media.step(
            year=self.current_year,
            shared_data=self.shared_data,
        )

        # ── 2. Elite agents deliberate ────────────────────────────────────────
        self.elite_layer.step(
            self.shared_data, self.current_year, self.scenario
        )

        # Handle coup signal
        if self.shared_data.get("elite_coup_signal", False):
            if self.scenario == "A":
                self.shared_data["coup_risk"] = max(
                    0.0, self.shared_data.get("coup_risk", 0.25) - 0.05
                )
            else:
                self.shared_data["coup_risk"] = min(
                    1.0, self.shared_data.get("coup_risk", 0.25) + 0.05
                )

        # ── 3. Broadcast environment ──────────────────────────────────────────
        self._broadcast_environment()

        # ── 4. All agents step ────────────────────────────────────────────────
        self.schedule.step()

        # ── 5. Twelve feedback loops ──────────────────────────────────────────
        self.feedback_engine.run_all()

        # ── 6. Scenario constitutional rules ──────────────────────────────────
        self._apply_scenario_rules()

        # ── 7. Institutions ───────────────────────────────────────────────────
        self.chambers.generate_annual_policy(self.current_year)
        self.chambers.process_votes(self.current_year)
        self.iig_system.annual_operations(self.current_year)

        # ── 8. State environment update ───────────────────────────────────────
        self._update_states()

        # ── 9. Data collection ────────────────────────────────────────────────
        self.datacollector.collect(self)

        # ── 10. Year increment ────────────────────────────────────────────────
        self.current_year += 1

    def _broadcast_environment(self):
        """Broadcast current shared_data to all agents as environment signal."""
        env = {
            "corruption":               self.shared_data.get("corruption_index", 0.72),
            "trust":                    self.shared_data.get("trust_index", 0.22),
            "coup_risk":                self.shared_data.get("coup_risk", 0.25),
            "iig_effectiveness":        self.shared_data.get("iig_effectiveness", 0.30),
            "north_star_progress":      self.shared_data.get("north_star_progress", 0.0),
            "citizen_info_exposure":    self.shared_data.get("citizen_information_exposure", 1.0),
            "active_shocks":            self.shared_data.get("external", {}).get("active_shocks", []),
            "china_influence":          self.shared_data.get("external", {}).get("china_influence", 0.75),
            "western_pressure":         self.shared_data.get("external", {}).get("western_pressure", 0.30),
            "internet_shutdown":        self.shared_data.get("internet_shutdown_active", False),
            "social_media_openness":    self.shared_data.get("social_media", {}).get("final_openness", 1.0),
        }
        for state_id, state in self.states.items():
            env.update({
                "ethnic_tension":   state.get("ethnic_tension", 0.60),
                "gdp_growth":       state.get("gdp_growth", 0.02),
                "employment":       state.get("employment", 0.58),
            })
        self.shared_data["environment"] = env

    def _apply_scenario_rules(self):
        """Apply constitutional rules based on active scenario."""
        if self.scenario == "A":
            self._scenario_a_rules()
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

        # Article 19 — Tatmadaw transition trust gain
        transition = CONSTITUTION_MFU.tatmadaw_transition
        if not self.shared_data.get("coup_attempted", False):
            self.shared_data["trust_index"] = min(
                1.0,
                self.shared_data.get("trust_index", 0.22) +
                transition.TRUST_GAIN_PER_CLEAN_YEAR
            )

    def _scenario_c_rules(self):
        """2008 Myanmar Military Constitution rules."""
        import random as _random
        if _random.random() < 0.05:
            self.shared_data["rights_violated"] = True
        self.shared_data["iig_effectiveness"] = max(
            0.05, self.shared_data.get("iig_effectiveness", 0.05) - 0.002
        )
        coup_risk = self.shared_data.get("coup_risk", 0.25)
        if coup_risk > 0.70:
            if _random.random() < 0.70:
                self.shared_data["coup_succeeded"]    = True
                self.shared_data["simulation_failed"] = True
                self.shared_data["failure_year"]      = self.current_year
                self.shared_data["failure_reason"]    = "coup_succeeded_2008_constitution"

    def _update_states(self):
        """Update state-level economic and social variables."""
        for state_id, state in self.states.items():
            corruption = self.shared_data.get("corruption_index", 0.72)
            iig = self.shared_data.get("iig_effectiveness", 0.30)
            fdi = self.shared_data.get("external", {}).get("fdi_level", 0.20)

            state["gdp_growth"] = float(np.clip(
                state["gdp_growth"] +
                (iig * 0.01) -
                (corruption * 0.01) +
                (fdi * 0.005),
                -0.10, 0.15
            ))
            state["corruption"] = float(np.clip(
                state["corruption"] - (iig * 0.005), 0.0, 1.0
            ))

    def get_results(self):
        """Return results DataFrame — same interface as KaNovaModel."""
        return self.datacollector.get_model_vars_dataframe().reset_index()


if __name__ == "__main__":
    print("model_phase3.py — quick test (200 citizens, 5 steps)")
    print()
    for scenario in ["A", "C"]:
        print(f"Testing Scenario {scenario}...")
        model = KaNovaModelPhase3(
            scenario=scenario,
            seed=42,
            n_citizens=200,
            use_llm=False,
        )
        for _ in range(5):
            model.step()
            if model.shared_data.get("simulation_failed"):
                print(f"  Simulation ended early — {model.shared_data.get('failure_reason')}")
                break

        df = model.get_results()
        final = df.iloc[-1]
        print(f"  Year {final['year']}: corruption={final['corruption_index']:.3f} "
              f"trust={final['trust_index']:.3f} "
              f"coup={final['coup_probability']:.3f} "
              f"vpn_floor={final['vpn_floor']:.3f} "
              f"openness={final['social_media_openness']:.3f}")
        print()
    print("model_phase3.py loaded successfully")
