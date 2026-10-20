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

# ── Constitution registry ─────────────────────────────────────────────────────
# Which constitution module backs a given scenario code, and whether it uses
# a civilian-supremacy or military-guardianship governance chain, now comes
# from config/scenario_registry.py instead of a hardcoded A/C binary (see
# .claude/memory.md bug #11 — the old `self.CONSTITUTION` switch here used to
# be written and never actually read by the 11 modules that import the
# module-level MFU `CONSTITUTION` singleton directly; this registry-driven
# switch is step 1 of making that propagate for real).
#
# CONSTITUTION_MFU is still imported directly here ONLY for self.max_years
# below — the 50-year simulation horizon is a locked experimental-design
# constant shared by every scenario (100 Monte Carlo runs/scenario, 50-year
# horizon), not something any individual constitution's own
# SimulationConfig.TIME_STEPS should be able to vary.
from config.constitution import CONSTITUTION as CONSTITUTION_MFU
from config.scenario_registry import get_scenario, AVAILABLE_SCENARIO_CODES

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
# Bug #16: reused by _initialize_shared_data() to size active_ethnic_groups
# to the active constitution's real ethnic-group count instead of always
# Myanmar's 8 — same resolution logic CVES uses for its own L1/L3 fixes
# (bug #17), imported rather than re-duplicated a third time here.
from engine.cves import _get_ethnic_group_count

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

def get_institution_effectiveness(m):
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

        # ── Constitution switch (registry-driven) ─────────────────────────────
        # get_scenario() raises a clear, loud error (KeyError for an unknown
        # code, ImportError for a known-but-not-yet-encoded code) rather than
        # silently falling back to MFU — the old fallback-with-warning here
        # was flagged in .claude/MINDMAP.md as "worth hardening before the
        # reproducibility package ships." For A and C (both fully encoded)
        # this is a no-behaviour-change swap.
        entry = get_scenario(scenario)
        self.CONSTITUTION       = entry.constitution
        self.chain_type         = entry.chain_type    # "civilian" | "military"
        self.constitution_name  = entry.slug           # unchanged literal
                                                         # strings for A/C:
                                                         # "mfu_v7" /
                                                         # "2008_myanmar_military"
        self.constitution_label = entry.label

        # ── Configuration ─────────────────────────────────────────────────────
        self.n_citizens = n_citizens
        self.current_year = 0
        self.max_years = CONSTITUTION_MFU.simulation.TIME_STEPS  # Always 50

        # ── Scheduler ─────────────────────────────────────────────────────────
        self.schedule = RandomActivation(self)

        # ── Elite agent layer ─────────────────────────────────────────────────
        # Bug #13: thread the active constitution/chain_type/scenario
        # through so CVES validates every decision against the scenario's
        # OWN constitution (self.CONSTITUTION, set above by the registry),
        # not always the MFU singleton it used to default to regardless of
        # scenario. See engine/elite_agents_v3.py / engine/cves.py.
        self.elite_layer = EliteAgentLayer(
            use_llm=use_llm,
            constitution=self.CONSTITUTION,
            chain_type=self.chain_type,
            scenario=self.scenario,
        )
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
                "iig_effectiveness":     get_institution_effectiveness,
                "institution_label":     lambda m: "iig_effectiveness" if m.chain_type == "civilian" else "intel_effectiveness",
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
        """
        States with year-zero conditions, read from the active constitution
        (bug #16) instead of Myanmar's 14 hardcoded state names and
        Myanmar-shaped random ranges regardless of scenario.

        State list: kept as Myanmar's 14 hardcoded names, NOT swapped to
        self.CONSTITUTION.simulation.SIMULATION_STATES, despite that field
        existing on every constitution module. Reason, found while testing
        this fix against Pakistan: agents/citizen.py's
        CitizenPopulation._assign_state() (a @staticmethod with no
        constitution access) independently hardcodes this exact same
        14-Myanmar-name list to assign every citizen's state_id, for every
        scenario, and agents/citizen.py is out of scope here (not one of
        this task's owned files). Swapping ONLY this dict's keys to
        Pakistan's/Chile's/etc.'s own SIMULATION_STATES names produces a
        live KeyError the first time any citizen agent (assigned a
        Myanmar-named state_id by citizen.py) looks itself up in
        self.states (confirmed by a real crash: `ERROR r=0: 'yangon'` when
        testing Scenario PK). This is the SAME already-flagged, deliberately-
        deferred architectural question noted in .claude/memory.md bug #11's
        correction ("constitution_2008.py's archetype distribution and
        14-state list were deliberately kept identical to MFU... flag to
        Kaung whether that separate question needs its own task") — population
        composition (which states exist, how citizens map to them) is a
        distinct research question from year-zero VALUES, deliberately kept
        Myanmar-shaped for every scenario until Kaung decides otherwise, not
        something to silently change scenario-by-scenario inside this
        narrower bug #16 fix. Only the per-state random VALUES below are
        made constitution-aware; the state KEYS are not.

        Random ranges: centred on the constitution's own
        SimulationConfig.YEAR_ZERO_CORRUPTION/TRUST/ETHNIC_TENSION/
        EMPLOYMENT, using the SAME range widths the old Myanmar-only
        literals implied (corruption/trust/employment ±0.075,
        ethnic_tension ±0.125), rather than Myanmar's fixed centres
        (corruption~0.725, trust~0.225, ethnic_tension~0.625,
        employment~0.575) for every scenario. MFU and 2008 Myanmar's own
        YEAR_ZERO_CORRUPTION/TRUST/EMPLOYMENT (0.72/0.22/0.58) are close to
        but not bit-identical to the old literal centres, so this is a
        small (not zero) change to Scenario A/C's year-zero state draws —
        see .claude/memory.md bug #16 for the measured before/after sizes.
        gdp_growth and resource_revenue have no YEAR_ZERO_* counterpart in
        any constitution module, so those two ranges are left exactly as
        they were (no encoded value exists to read instead).
        """
        sim = self.CONSTITUTION.simulation
        # NOT sim.SIMULATION_STATES — see docstring above (agents/citizen.py
        # coupling, out of this fix's scope).
        state_list = [
            "sagaing", "mandalay", "magway", "bago",
            "yangon", "ayeyarwady", "tanintharyi", "shan",
            "kachin", "kayah", "kayin", "chin",
            "mon", "rakhine",
        ]

        corruption_base = sim.YEAR_ZERO_CORRUPTION
        trust_base       = sim.YEAR_ZERO_TRUST
        ethnic_base      = sim.YEAR_ZERO_ETHNIC_TENSION
        employment_base  = sim.YEAR_ZERO_EMPLOYMENT

        states = {}
        for state_id in state_list:
            states[state_id] = {
                "corruption":       random.uniform(corruption_base - 0.075, corruption_base + 0.075),
                "trust":            random.uniform(trust_base - 0.075, trust_base + 0.075),
                "gdp_growth":       random.uniform(-0.02, 0.04),
                "ethnic_tension":   random.uniform(ethnic_base - 0.125, ethnic_base + 0.125),
                "resource_revenue": random.uniform(0.10, 0.40),
                "employment":       random.uniform(employment_base - 0.075, employment_base + 0.075),
            }
        return states

    def _initialize_shared_data(self) -> dict:
        """
        Year Zero shared state (bug #16) — read from the active
        constitution's SimulationConfig.YEAR_ZERO_* fields instead of
        hardcoded Myanmar literals for every scenario. MFU's own
        SimulationConfig predates YEAR_ZERO_COUP_RISK/YEAR_ZERO_STABILITY
        (only 2008 Myanmar and the 5 new constitutions define them), so
        those two fall back to the original literals (0.25/0.18) via
        getattr when absent — a no-op for Scenario A specifically.

        Fields with NO YEAR_ZERO_* counterpart in any constitution module
        (grievance_index, employment_rate, iig_effectiveness,
        brain_drain_rate, military_loyalty, policy_quality, ethnic_harmony
        — the last confirmed a dead/never-written key independently, see
        .claude/memory.md bug #3's side note) are left as the same
        literals as before; there is no encoded value to read instead, and
        inventing one would be guessing, not fixing.
        """
        sim = self.CONSTITUTION.simulation
        n_ethnic = _get_ethnic_group_count(self.CONSTITUTION)
        if n_ethnic == 8:
            # Real Myanmar names — unchanged for Scenario A (MFU, via the
            # ChamberConfig.ETHNIC_SEATS=8 fallback) and Scenario C (2008
            # Myanmar, via FederalConfig.ETHNIC_GROUPS=8). No other
            # encoded constitution currently resolves to 8.
            active_ethnic_groups = [
                "Bamar", "Shan", "Karen", "Kachin",
                "Chin", "Mon", "Rakhine", "Kayah"
            ]
        else:
            # No real ethnic-group names are encoded for the other 5
            # constitutions (only a count), so generic placeholder labels
            # of the correct LENGTH are used rather than borrowing
            # Myanmar's 8 real names — see bug #17 in .claude/memory.md.
            active_ethnic_groups = [f"ethnic_group_{i}" for i in range(n_ethnic)]

        return {
            "corruption_index":     sim.YEAR_ZERO_CORRUPTION,
            "trust_index":          sim.YEAR_ZERO_TRUST,
            "grievance_index":      0.60,
            "gini_coefficient":     sim.YEAR_ZERO_GINI,
            "employment_rate":      sim.YEAR_ZERO_EMPLOYMENT,
            "ethnic_harmony":       0.35,
            "iig_effectiveness":    0.30,
            "coup_risk":            getattr(sim, "YEAR_ZERO_COUP_RISK", 0.25),
            "stability_index":      getattr(sim, "YEAR_ZERO_STABILITY", 0.18),
            "brain_drain_rate":     0.35,
            "north_star_progress":  0.0,
            "protest_rate":         0.0,
            "shame_register_size":  0,
            "total_ruin_events":    0,
            "military_loyalty":     0.55,
            "policy_quality":       0.50,
            "rights_violated":      False,
            "simulation_failed":    False,
            "active_ethnic_groups": active_ethnic_groups,
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
            if self.chain_type == "civilian":
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
        # Bug #12 fix: ConstitutionalCourtSystem.annual_session() was fully
        # implemented (Total Ruin certification, rights-complaint
        # processing, methodology challenges, emergency certification, the
        # 10-year constitutional review) but never called anywhere in this
        # loop — the entire judicial layer was dead code for every
        # scenario. Judicial constraint is a core axis in the comparative
        # design (V-Dem judicial-constraints-on-the-executive index is a
        # cited validation point for several of the 7 constitutions), so a
        # mechanically inert judiciary undermined that argument across the
        # board, not just for new scenarios. See court.py's
        # REVIEW_INTERVAL == 0 guard (added alongside this call site) for
        # why this is now safe to call for every constitution, including
        # the several that encode no mandatory review cycle.
        self.court.annual_session(self.current_year)

        # ── 8. State environment update ───────────────────────────────────────
        self._update_states()

        # ── 8b. North-star composite KPI ──────────────────────────────────────
        # Computed last, after every other metric has taken its final value
        # for the year, so it reflects the year's settled state rather than
        # a mid-step snapshot.
        self._update_north_star_progress()

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
        """
        Apply chain-type rules (civilian-supremacy vs military-guardianship
        governance chain), read from the scenario registry rather than a
        literal scenario-code check — this is what lets SK/TH/PK/CL/DE plug
        into the same two branches as A/C once their constitution modules
        exist, with zero new code here. Bias lives only in each
        constitution's own parameter values (thresholds, probabilities,
        bonuses — all read fresh via self.CONSTITUTION, never hardcoded in
        this dispatch), per the engine-symmetry principle.
        """
        if self.chain_type == "civilian":
            self._civilian_chain_rules()
        else:
            self._military_chain_rules()

    def _civilian_chain_rules(self):
        """Civilian-supremacy governance chain (A/MFU and future civilian-chain comparators)."""
        self.shared_data["rights_violated"] = False
        # IIG effectiveness floor — institution is operational even before cases open
        current_iig = self.shared_data.get("iig_effectiveness", 0.30)
        year_bonus = 0.01 * (self.current_year / self.max_years)
        floor = min(0.30 + year_bonus, 0.40)
        self.shared_data["iig_effectiveness"] = max(floor, min(1.0, current_iig + year_bonus))
        shame_size = self.shared_data.get("shame_register_size", 0)
        if shame_size > 5:
            for agent in self.schedule.agents:
                if isinstance(agent, OfficialAgent):
                    agent.corruption_tolerance = max(
                        0.0, agent.corruption_tolerance - 0.005
                    )

        # Shared coup-attempt/success roll (bug #6 fix — see
        # _coup_risk_check docstring). Must run BEFORE the Article 19 /
        # transition trust-gain check below, same year, same order the old
        # _scenario_a_rules() implicitly assumed.
        self._coup_risk_check()

        # Article 19 — Tatmadaw transition trust gain, gated on no coup
        # attempt THIS year. self.CONSTITUTION.tatmadaw_transition is read
        # from whichever constitution the active run actually uses (fixed
        # from the old hardcoded CONSTITUTION_MFU.tatmadaw_transition read,
        # which — given bug #11 — made no practical difference for
        # Scenario A, but would have been silently wrong for any other
        # civilian-chain scenario). Every civilian-chain constitution module
        # must define a `tatmadaw_transition` section with at least
        # TRUST_GAIN_PER_CLEAN_YEAR (see field-contract note for SK/CL/DE).
        transition = self.CONSTITUTION.tatmadaw_transition
        if not self.shared_data.get("coup_attempted", False):
            self.shared_data["trust_index"] = min(
                1.0,
                self.shared_data.get("trust_index", 0.22) +
                transition.TRUST_GAIN_PER_CLEAN_YEAR
            )

    def _military_chain_rules(self):
        """Military-guardianship governance chain (C/2008 Myanmar and future military-chain comparators)."""
        import random as _random
        if _random.random() < 0.05:
            self.shared_data["rights_violated"] = True

        # IIG-equivalent floor/decay — bug #14 fix. Previously hardcoded as
        # literal numbers (0.05 floor, -0.002 annual decay) for EVERY
        # military-chain scenario regardless of constitution, silently
        # overriding each country's deliberately-sourced anti-corruption
        # parameters (e.g. Thailand's real, entrenched NACC
        # EFFECTIVENESS_FLOOR=0.25, chosen specifically per the realism
        # requirement to NOT copy Myanmar's near-zero 0.05 floor). Now reads
        # self.CONSTITUTION.iig.EFFECTIVENESS_FLOOR, which every encoded
        # constitution's IIGConfig defines (confirmed in constitution.py,
        # constitution_2008.py, constitution_thailand.py).
        #
        # No constitution currently defines a corresponding decay-rate
        # field under EFFECTIVENESS_DECAY_RATE or any similar name
        # (verified against constitution_2008.py and constitution_thailand.py
        # IIGConfig sections — neither has one), so the decay rate falls
        # back to the original hardcoded -0.002/year unless/until a
        # constitution author adds that field. This is a real gap in the
        # field contract, not silently papered over: flagged here and in
        # the task report for senior-researcher/whoever encodes future
        # military-chain constitutions to add if the decay RATE (not just
        # the floor) needs to differ by country.
        floor = self.CONSTITUTION.iig.EFFECTIVENESS_FLOOR
        decay = getattr(self.CONSTITUTION.iig, "EFFECTIVENESS_DECAY_RATE", -0.002)
        self.shared_data["iig_effectiveness"] = max(
            floor, self.shared_data.get("iig_effectiveness", floor) + decay
        )
        self._coup_risk_check()

    def _coup_risk_check(self):
        """
        Shared coup-attempt/success roll for BOTH chain types (fixes bug #6:
        `coup_attempted` used to be read-only in the old _scenario_a_rules()
        and never written anywhere in the file; `coup_succeeded` was
        write-only in the old _scenario_c_rules(). Unifying the mechanic
        here makes both keys real and symmetric across chain types —
        the SAME 0.70 risk threshold / 70% success-conditional roll applies
        to every scenario; only each constitution's own coup_risk
        trajectory (itself driven by that constitution's military-config
        thresholds elsewhere in the pipeline) determines whether this ever
        actually fires. This is why Scenario A's locked coup probability
        stays at 0.0000 — not because this check is skipped for it, but
        because MFU's parameters never drive coup_risk above 0.70.

        coup_attempted is reset to False every year it does not trigger, so
        it reads as "an attempt happened THIS year," not "ever happened."
        """
        import random as _random
        coup_risk = self.shared_data.get("coup_risk", 0.25)
        if coup_risk > 0.70:
            self.shared_data["coup_attempted"] = True
            if _random.random() < 0.70:
                self.shared_data["coup_succeeded"]    = True
                self.shared_data["simulation_failed"] = True
                self.shared_data["failure_year"]      = self.current_year
                self.shared_data["failure_reason"]    = f"coup_succeeded_{self.constitution_name}"
        else:
            self.shared_data["coup_attempted"] = False

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
            if self.chain_type == "civilian":
                # Civilian-supremacy chain: IIG actively reduces corruption
                state["corruption"] = float(np.clip(
                    state["corruption"] - (iig * 0.02), 0.0, 1.0
                ))
            else:
                # Military-guardianship chain: no accountability, corruption drifts up
                state["corruption"] = float(np.clip(
                    state["corruption"] + 0.01, 0.0, 1.0
                ))

        # Aggregate state corruption back into shared_data
        if self.states:
            avg_corruption = sum(s["corruption"] for s in self.states.values()) / len(self.states)
            self.shared_data["corruption_index"] = round(float(avg_corruption), 4)

        # IIG effectiveness floor — enforce after all other writes
        if self.chain_type == "civilian":
            year_bonus = 0.01 * (self.current_year / max(1, self.max_years))
            floor = min(0.30 + year_bonus, 0.40)
            current = self.shared_data.get("iig_effectiveness", 0.30)
            if current < floor:
                self.shared_data["iig_effectiveness"] = floor

    def _update_north_star_progress(self):
        """
        Compute and write shared_data["north_star_progress"] for this year.

        Historically this key was seeded once at Year Zero (0.0) and read in
        several places (_broadcast_environment, feedback/loops.py's loop
        summary, the datacollector) but never actually recomputed — a
        missing write path, not a formula bug (see .claude/MINDMAP.md #3).

        Formula: reuses the composite weights from the Phase 2 legacy
        engine (engine/hybrid_engine.py:300-312, recompute_kpis), which is
        the only prior formula definition in the codebase and is what the
        README's Phase 2 table (North Star progress 0.557 vs 0.242) already
        reports. config/constitution.py's NorthStarConfig and
        config/constitution_2008.py's NorthStarConfig both define only
        decade targets/metadata (TARGET_CORRUPTION_INDEX, PROGRESS_METRIC
        label, etc.) — neither contains an actual formula, so there was
        nothing formula-wise to "wire in" from the constitution layer
        itself; the composite below is the project's own pre-existing
        design, just finally connected to the live shared_data pipeline.

        Weights (sum to 1.0, unchanged from the Phase 2 source):
            (1 - corruption_index)        * 0.20
          + trust_index                   * 0.15
          + (1 - coup_risk)               * 0.15
          + iig_effectiveness             * 0.15
          + min(gdp_growth_rate*5.0, 1.0) * 0.15
          + ethnic_harmony_component      * 0.10
          + (1 - gini_coefficient)        * 0.10

        One judgment call: ethnic harmony. shared_data["ethnic_harmony"]
        (the key the datacollector/elite-agent layer reads) is seeded at
        0.35 and never written anywhere in the live Phase 3 pipeline — a
        separate dead-key gap from this one, out of scope to fix here.
        shared_data["ethnic_harmony_index"] IS written every year by
        feedback/loops.py's S1 loop (national-service cross-exposure), so
        it is used here (with a fallback chain) to keep this composite a
        real trajectory rather than silently averaging in a frozen
        constant.
        """
        corruption  = self.shared_data.get("corruption_index", 0.72)
        trust       = self.shared_data.get("trust_index", 0.22)
        coup_risk   = self.shared_data.get("coup_risk", 0.25)
        iig         = self.shared_data.get("iig_effectiveness", 0.30)
        gdp_growth  = self.shared_data.get("gdp_growth_rate", 0.0)
        harmony     = self.shared_data.get(
            "ethnic_harmony_index", self.shared_data.get("ethnic_harmony", 0.35)
        )
        gini        = self.shared_data.get("gini_coefficient", 0.55)

        north_star = (
            (1.0 - corruption) * 0.20
            + trust * 0.15
            + (1.0 - coup_risk) * 0.15
            + iig * 0.15
            + min(gdp_growth * 5.0, 1.0) * 0.15
            + harmony * 0.10
            + (1.0 - gini) * 0.10
        )
        self.shared_data["north_star_progress"] = round(
            float(np.clip(north_star, 0.0, 1.0)), 4
        )

    def get_results(self):
        """Return results DataFrame — same interface as KaNovaModel."""
        return self.datacollector.get_model_vars_dataframe().reset_index()


if __name__ == "__main__":
    print("model_phase3.py — quick test (200 citizens, 5 steps)")
    print()
    for scenario in AVAILABLE_SCENARIO_CODES:  # currently ["A", "C"]; grows
                                                # automatically as SK/TH/PK/CL/DE
                                                # get encoded
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
