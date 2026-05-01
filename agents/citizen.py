"""
================================================================================
PROJECT KA-NOVA
agents/citizen.py

Citizen Agent — Heterogeneous Cognitive Agent Implementation
Ka-Nova Simulation Engine v1.0

The citizen agent is the foundational unit of Ka-Nova. Every citizen has:
- A unique archetype determining baseline behavioral tendencies
- A life course that evolves annually from birth to death
- Bounded rationality — decisions based on limited local information
- Adaptive thresholds that update from experience
- Social influence capacity through network connections
- Constitutional obligations (National Service, tax, merit system)

All behavior derives from MFU constitutional parameters.
No hardcoded values — everything references CONSTITUTION.

Author: Kaung Htet
License: MIT
================================================================================
"""


from __future__ import annotations
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import random
import math
from collections import deque
from typing import Optional, Dict, List
from mesa import Agent

from config.constitution import CONSTITUTION


# ══════════════════════════════════════════════════════════════════════════════
# ARCHETYPE DEFINITIONS
# Seven distinct behavioral phenotypes — initialized at agent creation
# ══════════════════════════════════════════════════════════════════════════════

ARCHETYPES: Dict[str, Dict] = {
    "civic_champion": {
        "description": "Highly engaged, high merit, low corruption tolerance",
        "trust_score": 0.75,
        "civic_contribution": 0.85,
        "corruption_tolerance": 0.10,
        "protest_threshold": 0.50,
        "emigration_threshold": 0.90,
        "political_awareness": 0.80,
        "risk_appetite": 0.60,
        "resilience": 0.80,
        "proportion": 0.15
    },
    "pragmatic_survivor": {
        "description": "Adapts to whatever system exists, largest group",
        "trust_score": 0.45,
        "civic_contribution": 0.40,
        "corruption_tolerance": 0.55,
        "protest_threshold": 0.75,
        "emigration_threshold": 0.60,
        "political_awareness": 0.40,
        "risk_appetite": 0.30,
        "resilience": 0.60,
        "proportion": 0.30
    },
    "ethnic_loyalist": {
        "description": "Primary identity is ethnic group over federal identity",
        "trust_score": 0.40,
        "civic_contribution": 0.50,
        "corruption_tolerance": 0.35,
        "protest_threshold": 0.60,
        "emigration_threshold": 0.70,
        "political_awareness": 0.55,
        "risk_appetite": 0.45,
        "resilience": 0.65,
        "ethnic_cross_exposure": 0.15,
        "ethnic_loyalty": 0.90,
        "proportion": 0.20
    },
    "ambitious_meritocrat": {
        "description": "Believes in the merit system, high achiever",
        "trust_score": 0.65,
        "civic_contribution": 0.70,
        "corruption_tolerance": 0.15,
        "protest_threshold": 0.55,
        "emigration_threshold": 0.75,
        "political_awareness": 0.80,
        "risk_appetite": 0.70,
        "resilience": 0.75,
        "proportion": 0.15
    },
    "disillusioned_youth": {
        "description": "Young, educated, frustrated, emigrates easily",
        "trust_score": 0.30,
        "civic_contribution": 0.35,
        "corruption_tolerance": 0.25,
        "protest_threshold": 0.45,
        "emigration_threshold": 0.45,
        "political_awareness": 0.65,
        "risk_appetite": 0.65,
        "resilience": 0.45,
        "proportion": 0.10
    },
    "rural_traditionalist": {
        "description": "Low connectivity, traditional values, low awareness",
        "trust_score": 0.35,
        "civic_contribution": 0.55,
        "corruption_tolerance": 0.50,
        "protest_threshold": 0.80,
        "emigration_threshold": 0.85,
        "political_awareness": 0.20,
        "risk_appetite": 0.20,
        "resilience": 0.70,
        "ethnic_cross_exposure": 0.10,
        "proportion": 0.07
    },
    "trauma_carrier": {
        "description": "Conflict survivor, high trauma, low trust",
        "trust_score": 0.20,
        "civic_contribution": 0.30,
        "corruption_tolerance": 0.40,
        "protest_threshold": 0.35,
        "emigration_threshold": 0.40,
        "political_awareness": 0.50,
        "risk_appetite": 0.35,
        "resilience": 0.30,
        "trauma_score": 0.75,
        "proportion": 0.03
    }
}

# Ethnic groups in simulation
ETHNIC_GROUPS = ["Bamar", "Shan", "Karen", "Kachin", "Chin", "Mon", "Rakhine", "Kayah"]

# State assignments for simplified 4-state simulation
SIMULATION_STATES = {
    "bamar_central": ["Bamar", "Mon"],
    "shan_eastern":  ["Shan", "Kayah"],
    "karen_southern": ["Karen", "Rakhine"],
    "kachin_northern": ["Kachin", "Chin"]
}


# ══════════════════════════════════════════════════════════════════════════════
# CITIZEN AGENT
# ══════════════════════════════════════════════════════════════════════════════

class CitizenAgent(Agent):
    """
    Heterogeneous Cognitive Agent representing one citizen of the Federal Union.

    Architecture:
        Layer 1 — Perception: bounded, local, recency-biased
        Layer 2 — Decision:   satisficing, not optimizing
        Layer 3 — Action:     affects environment, network, institutions
        Layer 4 — Learning:   adaptive thresholds from experience
        Layer 5 — Life Course: evolves annually birth to death
    """

    def __init__(
        self,
        unique_id: int,
        model,
        archetype: str,
        state_id: str,
        ethnicity: str,
        age: int = None
    ):
        super().__init__(unique_id, model)

        # ── IDENTITY ──────────────────────────────────────────────────────────
        self.archetype = archetype
        self.state_id = state_id
        self.ethnicity = ethnicity
        self.age = age if age is not None else random.randint(0, 65)
        self.religion = self._assign_religion()
        self.is_alive = True

        # ── ARCHETYPE BASELINE ────────────────────────────────────────────────
        base = ARCHETYPES[archetype].copy()
        noise = 0.05  # Gaussian noise for individual variation

        # ── MERIT COMPONENTS (Article 3.2) ────────────────────────────────────
        self.productivity = self._init_attr(
            base.get("productivity", random.uniform(0.20, 0.70)), noise
        )
        self.education_level = self._init_education()
        self.performance = self._init_attr(
            random.uniform(0.20, 0.65), noise
        )
        self.civic_contribution = self._init_attr(
            base.get("civic_contribution", 0.40), noise
        )
        self.merit_score = self._calculate_merit()

        # ── ECONOMIC ──────────────────────────────────────────────────────────
        self.income = self._init_income()
        self.savings = self.income * random.uniform(0.05, 0.30)
        self.debt = self.income * random.uniform(0.0, 0.50)
        self.tax_compliance = self._init_attr(
            1.0 - base.get("corruption_tolerance", 0.40) * 0.5, noise
        )
        self.employment_status = self._init_employment()

        # ── POLITICAL / SOCIAL ────────────────────────────────────────────────
        self.trust_score = self._init_attr(base.get("trust_score", 0.40), noise)
        self.grievance = self._init_grievance()
        self.political_awareness = self._init_attr(
            base.get("political_awareness", 0.40), noise
        )
        self.ethnic_cross_exposure = self._init_attr(
            base.get("ethnic_cross_exposure", 0.30), noise
        )
        self.ethnic_loyalty = base.get("ethnic_loyalty", 0.50)
        self.constitutional_loyalty = 0.30  # starts low, built through NS

        # ── PSYCHOLOGICAL (Article 18) ────────────────────────────────────────
        self.trauma_score = self._init_attr(
            base.get("trauma_score", random.uniform(0.0, 0.30)), noise
        )
        self.trauma_category = self._assign_trauma_category()
        self.resilience = self._init_attr(base.get("resilience", 0.55), noise)
        self.psych_status = "stable"  # stable / acceptable / severe

        # ── BEHAVIORAL THRESHOLDS (adaptive) ──────────────────────────────────
        self.protest_threshold = self._init_attr(
            base.get("protest_threshold", 0.70), noise
        )
        self.emigration_threshold = self._init_attr(
            base.get("emigration_threshold", 0.70), noise
        )
        self.corruption_tolerance = self._init_attr(
            base.get("corruption_tolerance", 0.40), noise
        )
        self.risk_appetite = self._init_attr(
            base.get("risk_appetite", 0.40), noise
        )

        # ── LIFE STATUS FLAGS ─────────────────────────────────────────────────
        self.national_service_completed = False
        self.national_service_track = None        # civilian / military
        self.national_service_year = None
        self.is_student = self._init_student_status()
        self.is_phd_candidate = False
        self.phd_years_remaining = 0
        self.has_emigrated = False
        self.is_protesting = False
        self.corruption_detected = False

        # ── TAX STATUS (Article 10.10) ────────────────────────────────────────
        self.tax_exempt = self._check_tax_exempt()
        self.declared_all_income = True           # starts compliant
        self.tax_evasion_detected = False

        # ── MEMORY (recency-biased, last 5 years) ─────────────────────────────
        self.memory = deque(maxlen=5)

        # ── NETWORK ───────────────────────────────────────────────────────────
        self.network_size = random.randint(5, 50)
        self.influence_radius = self.political_awareness * 10
        self.known_shame_register_victim = False

        # ── BROADCAST SIGNAL (for network propagation) ────────────────────────
        self.has_event_to_broadcast = False
        self.broadcast_signal = {}

        # ── TRACKING ──────────────────────────────────────────────────────────
        self.years_in_system = 0
        self.lifetime_tax_paid = 0.0
        self.lifetime_civic_actions = 0

    # ══════════════════════════════════════════════════════════════════════════
    # MESA STEP METHOD — called every time step (year)
    # ══════════════════════════════════════════════════════════════════════════

    def step(self):
        """
        Annual update cycle for one citizen agent.
        Order matters — perception before decision before action.
        """

        if not self.is_alive or self.has_emigrated:
            return

        # 1. Perceive local environment (bounded — not omniscient)
        local_env = self._perceive_environment()

        # 2. Store in memory (recency-biased)
        self.memory.append(local_env)

        # 3. Make decisions (satisficing)
        self._make_decisions(local_env)

        # 4. Execute actions
        self._execute_actions(local_env)

        # 5. Update adaptive thresholds from this year's experience
        self._update_thresholds(local_env)

        # 6. Life course update
        self._life_course_update()

        # 7. Recalculate merit score
        self.merit_score = self._calculate_merit()

        # 8. Update tax exempt status
        self.tax_exempt = self._check_tax_exempt()

        # 9. Increment counter
        self.years_in_system += 1

    # ══════════════════════════════════════════════════════════════════════════
    # LAYER 1 — PERCEPTION (bounded rationality)
    # ══════════════════════════════════════════════════════════════════════════

    def _perceive_environment(self) -> Dict:
        """
        Agent observes local environment.
        Political awareness determines how much the agent sees.
        Low awareness = higher information asymmetry.
        """

        state = self.model.states.get(self.state_id, {})

        # Base perception — everyone sees this
        perception = {
            "corruption_level": state.get("corruption_level", 0.65),
            "employment_rate": state.get("employment_rate", 0.58),
            "trust_index": state.get("trust_index", 0.30),
            "ethnic_tension": state.get("ethnic_tension", 0.60),
            "gdp_growth": state.get("gdp_growth", 0.03),
            "resource_revenue_received": state.get("resource_revenue", 0.0),
            "year": self.model.current_year
        }

        # Additional perception based on political awareness
        if self.political_awareness > 0.50:
            perception["iig_activity"] = state.get("iig_activity", 0.0)
            perception["merit_system_integrity"] = state.get(
                "merit_integrity", 0.70
            )
            perception["protest_activity"] = state.get("protest_activity", 0.0)

        if self.political_awareness > 0.75:
            perception["federal_policy_quality"] = self.model.shared_data.get(
                "policy_quality", 0.50
            )
            perception["national_shame_register_size"] = len(
                self.model.shared_data.get("shame_register", [])
            )

        # Add noise — imperfect observation
        for key in ["corruption_level", "employment_rate", "trust_index"]:
            if key in perception:
                noise = random.gauss(0, 0.05)
                perception[key] = max(0.0, min(1.0, perception[key] + noise))

        return perception

    def _weighted_memory(self) -> Dict:
        """
        Recency-biased memory — recent years weighted more than older years.
        Weights: [0.50, 0.30, 0.20] for last 3 years if available.
        """

        if not self.memory:
            return {}

        memory_list = list(self.memory)
        weights = [0.50, 0.30, 0.15, 0.03, 0.02][:len(memory_list)]
        weights = weights[::-1]  # most recent = highest weight
        total_weight = sum(weights)

        weighted = {}
        keys = ["corruption_level", "employment_rate", "trust_index"]

        for key in keys:
            values = [m.get(key, 0.5) for m in memory_list]
            if values:
                weighted[key] = sum(
                    v * w for v, w in zip(values, weights)
                ) / total_weight

        return weighted

    # ══════════════════════════════════════════════════════════════════════════
    # LAYER 2 — DECISION (satisficing, not optimizing)
    # ══════════════════════════════════════════════════════════════════════════

    def _make_decisions(self, env: Dict):
        """
        Agent makes annual decisions based on weighted perception.
        Satisficing: stops at first acceptable option, not best option.
        """

        weighted = self._weighted_memory()
        perceived_corruption = weighted.get("corruption_level", env["corruption_level"])
        perceived_employment = weighted.get("employment_rate", env["employment_rate"])
        perceived_trust = weighted.get("trust_index", env["trust_index"])

        # Decision 1 — Tax compliance (Article 10.12)
        self._decide_tax_compliance(perceived_corruption)

        # Decision 2 — Protest (Article 2.1 — right to assembly)
        self._decide_protest(env)

        # Decision 3 — Emigration
        self._decide_emigration(perceived_employment, perceived_trust)

        # Decision 4 — Bribery attempt
        self._decide_bribery(perceived_corruption)

        # Decision 5 — Report corruption (if witnessed)
        self._decide_report_corruption(perceived_corruption, perceived_trust)

        # Decision 6 — PhD application (high merit citizens)
        self._decide_phd_application()

        # Decision 7 — National Service (age 18)
        if self.age == 18 and not self.national_service_completed:
            self._begin_national_service()

    def _decide_tax_compliance(self, perceived_corruption: float):
        """
        Tax evasion decision.
        Higher corruption environment = higher evasion temptation.
        But: shame register knowledge reduces evasion probability.
        """

        # Base evasion probability
        evasion_prob = (
            self.corruption_tolerance * 0.40 +
            perceived_corruption * 0.30 +
            (1.0 - self.constitutional_loyalty) * 0.20 +
            (1.0 - self.trust_score) * 0.10
        )

        # Shame register deterrent
        if self.known_shame_register_victim:
            evasion_prob *= 0.50

        # IIG activity deterrent
        iig_activity = self.model.shared_data.get("iig_effectiveness", 0.50)
        evasion_prob *= (1.0 - iig_activity * 0.40)

        # Decision
        if (not self.tax_exempt and
                random.random() < evasion_prob and
                self.income > 0):
            self.declared_all_income = False
        else:
            self.declared_all_income = True

    def _decide_protest(self, env: Dict):
        """
        Protest decision based on grievance exceeding personal threshold.
        Contagion from network neighbors included.
        """

        # Check if grievance exceeds personal threshold
        base_protest = self.grievance > self.protest_threshold

        # Network contagion — if neighbors protesting, threshold lowers
        network_protest_rate = self.model.shared_data.get(
            "network_protest_rate", 0.0
        )
        contagion_effect = network_protest_rate * (1.0 - self.protest_threshold)

        if base_protest or random.random() < contagion_effect:
            if self.political_awareness > 0.20:  # needs minimum awareness
                self.is_protesting = True
                self.has_event_to_broadcast = True
                self.broadcast_signal = {
                    "type": "protest",
                    "grievance": self.grievance,
                    "state": self.state_id
                }
        else:
            self.is_protesting = False

    def _decide_emigration(self, employment: float, trust: float):
        """
        Emigration decision. Satisficing — leaves when conditions bad enough.
        PhD graduates and high-merit agents are more mobile.
        """

        # Emigration pressure composite
        emigration_pressure = (
            (1.0 - employment) * 0.35 +
            (1.0 - trust) * 0.25 +
            self.grievance * 0.25 +
            self.trauma_score * 0.15
        )

        # High merit agents have more options abroad
        if self.merit_score > 0.70:
            emigration_pressure *= 1.20

        # PhD graduates most mobile
        if self.is_phd_candidate:
            emigration_pressure *= 1.30

        # Ethnic loyalists less likely to leave
        if self.archetype == "ethnic_loyalist":
            emigration_pressure *= 0.70

        # Decision — satisficing threshold
        if emigration_pressure > self.emigration_threshold:
            if random.random() < 0.30:  # not everyone acts immediately
                self.has_emigrated = True
                self.model.shared_data["emigrants"].append(self.unique_id)

    def _decide_bribery(self, perceived_corruption: float):
        """
        Decision to attempt bribery of an official.
        Only occurs if corruption environment is permissive.
        """

        if perceived_corruption < 0.40:
            return  # clean environment — bribery too risky

        bribery_prob = (
            self.corruption_tolerance * 0.50 +
            perceived_corruption * 0.30 +
            (1.0 - self.trust_score) * 0.20
        )

        if random.random() < bribery_prob * 0.15:  # rare — not everyone
            self.model.shared_data["bribery_attempts"].append({
                "citizen_id": self.unique_id,
                "state": self.state_id,
                "year": self.model.current_year
            })

    def _decide_report_corruption(self, corruption: float, trust: float):
        """
        Decision to report witnessed corruption to IIG.
        Requires: high enough trust in institutions AND witnessed corruption.
        """

        # Only report if trust in system is reasonable
        if trust < 0.30:
            return

        # Probability of reporting witnessed corruption
        if (corruption > 0.50 and
                self.trust_score > 0.45 and
                self.political_awareness > 0.40):

            report_prob = (
                self.civic_contribution * 0.40 +
                self.constitutional_loyalty * 0.30 +
                self.trust_score * 0.30
            )

            if random.random() < report_prob * 0.20:
                self.model.shared_data["corruption_reports"].append({
                    "reporter_id": self.unique_id,
                    "state": self.state_id,
                    "year": self.model.current_year
                })

    def _decide_phd_application(self):
        """
        High-merit citizens may apply to PhD programs.
        Article 11.1 — free tuition + stipend.
        """

        if (self.is_phd_candidate or
                self.is_student or
                self.age < 22 or
                self.age > 35):
            return

        if (self.merit_score > 0.80 and
                not self.national_service_completed):
            return  # must complete NS first

        if self.merit_score > 0.80:
            apply_prob = (self.merit_score - 0.80) * 3.0  # 0 to 0.6
            if random.random() < apply_prob * 0.30:
                self.is_phd_candidate = True
                self.is_student = True
                self.phd_years_remaining = 4
                self.tax_exempt = True  # stipend is research grant

    # ══════════════════════════════════════════════════════════════════════════
    # LAYER 3 — ACTION
    # ══════════════════════════════════════════════════════════════════════════

    def _execute_actions(self, env: Dict):
        """Execute decisions — affects environment, network, institutions."""

        # Pay tax (if not evading)
        self._pay_tax()

        # Work — contribute to state GDP
        self._work()

        # PhD progress
        if self.is_phd_candidate:
            self._progress_phd()

        # Protest action
        if self.is_protesting:
            self._execute_protest()

    def _pay_tax(self):
        """
        Calculate and pay income tax.
        Article 10.9-10.12 — progressive brackets, no profession exemptions.
        """

        if self.tax_exempt or self.income <= 0:
            self.lifetime_tax_paid += 0
            return

        if not self.declared_all_income:
            # Tax evasion — flagged for IIG
            self.tax_evasion_detected = random.random() < (
                self.model.shared_data.get("iig_effectiveness", 0.50) * 0.30
            )
            if self.tax_evasion_detected:
                self.model.shared_data["tax_evasion_detected"].append({
                    "citizen_id": self.unique_id,
                    "income": self.income,
                    "year": self.model.current_year
                })
            return

        # Calculate tax using progressive brackets
        poverty_line = self.model.shared_data.get("poverty_line", 1000.0)
        tax = self._calculate_progressive_tax(self.income, poverty_line)

        # Pay
        self.income -= tax
        self.lifetime_tax_paid += tax
        self.model.shared_data["tax_revenue"] += tax

    def _calculate_progressive_tax(self, income: float, poverty_line: float) -> float:
        """
        Apply progressive tax brackets from Article 10.9.
        Brackets are multiples of poverty line.
        """

        if income <= poverty_line:
            return 0.0

        brackets = CONSTITUTION.economic.TAX_BRACKETS
        taxable = income
        tax = 0.0

        for (low_mult, high_mult, rate) in brackets:
            bracket_low = poverty_line * low_mult
            bracket_high = (poverty_line * high_mult
                            if high_mult != float('inf')
                            else float('inf'))

            if taxable <= bracket_low:
                break

            income_in_bracket = min(taxable, bracket_high) - bracket_low
            if income_in_bracket > 0:
                tax += income_in_bracket * rate

        return tax

    def _work(self):
        """
        Work action — contributes to state GDP and updates productivity.
        Employment status affects contribution.
        """

        if self.employment_status == "employed" and not self.has_emigrated:
            gdp_contribution = self.productivity * self.income * 0.001
            self.model.states[self.state_id]["gdp"] = (
                self.model.states[self.state_id].get("gdp", 100.0) +
                gdp_contribution
            )

            # Slight productivity growth through experience
            self.productivity = min(1.0, self.productivity + 0.005)

    def _progress_phd(self):
        """
        Annual PhD progress. Graduate and boost knowledge capital.
        Article 11.1 — funded, stipend, accommodation.
        """

        self.phd_years_remaining -= 1

        if self.phd_years_remaining <= 0:
            # Graduation
            self.is_phd_candidate = False
            self.is_student = False
            self.education_level = min(1.0, self.education_level + 0.25)
            self.merit_score = self._calculate_merit()
            self.tax_exempt = False  # no longer on stipend

            # Boost state knowledge capital
            self.model.states[self.state_id]["knowledge_capital"] = (
                self.model.states[self.state_id].get("knowledge_capital", 0.0) +
                CONSTITUTION.science.PHD_KNOWLEDGE_CAPITAL_BOOST
            )
            self.model.shared_data["phd_graduates"] += 1

    def _execute_protest(self):
        """
        Protest action — affects state stability and trust.
        Triggers government response decision.
        """

        state = self.model.states.get(self.state_id, {})
        state["protest_activity"] = min(
            1.0,
            state.get("protest_activity", 0.0) + 0.01
        )
        self.lifetime_civic_actions += 1

    # ══════════════════════════════════════════════════════════════════════════
    # NATIONAL SERVICE (Article 9.5 + Article 2.6)
    # ══════════════════════════════════════════════════════════════════════════

    def _begin_national_service(self):
        """
        National Service at age 18 — mandatory constitutional obligation.
        Merit score determines track assignment.
        Track assignment does NOT determine citizenship quality.
        """

        self.national_service_year = self.model.current_year
        threshold = CONSTITUTION.military.NS_CIVILIAN_TRACK_THRESHOLD

        if self.merit_score >= threshold:
            self.national_service_track = "civilian"
        else:
            self.national_service_track = "military"

        # Constitutional boosts from service (Article 9.5)
        self.constitutional_loyalty = min(
            1.0,
            self.constitutional_loyalty +
            CONSTITUTION.military.NS_LOYALTY_BOOST
        )
        self.ethnic_cross_exposure = min(
            1.0,
            self.ethnic_cross_exposure +
            CONSTITUTION.military.NS_ETHNIC_EXPOSURE_BOOST
        )
        self.civic_contribution = min(
            1.0,
            self.civic_contribution +
            CONSTITUTION.military.NS_CIVIC_CONTRIBUTION_BOOST
        )

        self.national_service_completed = True

        # Eligible for IIG Academy after NS (Article 7.0.1)
        self.iig_academy_eligible = (
            self.merit_score >= CONSTITUTION.iig.ENTRY_MERIT_MIN
        )

    # ══════════════════════════════════════════════════════════════════════════
    # LAYER 4 — ADAPTIVE THRESHOLDS
    # ══════════════════════════════════════════════════════════════════════════

    def _update_thresholds(self, env: Dict):
        """
        Thresholds adapt based on this year's experience.
        This is the learning mechanism — agents update from outcomes.
        """

        corruption = env.get("corruption_level", 0.50)
        employment = env.get("employment_rate", 0.60)
        trust = env.get("trust_index", 0.40)

        # Witnessing unpunished corruption lowers corruption threshold
        # "Everyone does it" mentality develops
        if corruption > 0.60 and not self.corruption_detected:
            self.corruption_tolerance = min(
                1.0, self.corruption_tolerance + 0.02
            )

        # Seeing Total Ruin / Shame Register raises corruption threshold
        if self.known_shame_register_victim:
            self.corruption_tolerance = max(
                0.0, self.corruption_tolerance - 0.05
            )
            self.protest_threshold = min(
                1.0, self.protest_threshold + 0.02
            )

        # National Service builds civic loyalty
        if self.national_service_completed:
            self.protest_threshold = max(
                0.30, self.protest_threshold - 0.01
            )

        # Poor employment raises emigration pressure
        if employment < 0.60:
            self.emigration_threshold = max(
                0.20, self.emigration_threshold - 0.02
            )

        # Good governance restores trust
        if trust > 0.60:
            self.trust_score = min(1.0, self.trust_score + 0.03)
            self.grievance = max(0.0, self.grievance - 0.02)

        # Update grievance from this year's experience
        self._update_grievance(env)

    def _update_grievance(self, env: Dict):
        """
        Grievance updates based on rights violations, corruption, unemployment.
        Grievance is the primary driver of protest and emigration.
        """

        corruption = env.get("corruption_level", 0.50)
        employment = env.get("employment_rate", 0.60)
        trust = env.get("trust_index", 0.40)
        ethnic_tension = env.get("ethnic_tension", 0.50)

        # Grievance drivers
        grievance_change = (
            corruption * 0.25 +
            (1.0 - employment) * 0.30 +
            (1.0 - trust) * 0.25 +
            ethnic_tension * self.ethnic_loyalty * 0.20
        ) * 0.10  # annual increment

        # Resilience dampens grievance accumulation
        grievance_change *= (1.0 - self.resilience * 0.50)

        # Rights violation — major grievance spike (Article 2.4)
        if self.model.shared_data.get("rights_violated", False):
            grievance_change += CONSTITUTION.rights.RIGHTS_VIOLATION_GRIEVANCE_SPIKE

        # Good governance reduces grievance
        if trust > 0.65 and employment > 0.80:
            grievance_change -= 0.05

        self.grievance = max(0.0, min(1.0, self.grievance + grievance_change))

    # ══════════════════════════════════════════════════════════════════════════
    # LAYER 5 — LIFE COURSE
    # ══════════════════════════════════════════════════════════════════════════

    def _life_course_update(self):
        """
        Annual life course progression.
        Agents age, change education, career stage, and eventually die.
        """

        self.age += 1

        # Student status by age
        if 6 <= self.age <= 17:
            self.is_student = True
            self.tax_exempt = True
            self.education_level = min(
                0.50, self.education_level + 0.04
            )

        elif self.age == 18:
            self.is_student = False
            self.tax_exempt = False

        elif 19 <= self.age <= 22 and self.merit_score > 0.55:
            # University period
            self.is_student = True
            self.education_level = min(
                0.75, self.education_level + 0.06
            )

        elif self.age == 23:
            self.is_student = False
            self.employment_status = "employed"

        # Productivity lifecycle
        if 25 <= self.age <= 45:
            self.productivity = min(1.0, self.productivity + 0.01)
        elif 46 <= self.age <= 60:
            pass  # peak — stable
        elif self.age > 60:
            self.productivity = max(0.20, self.productivity - 0.01)

        # Influence grows with age and experience
        if self.age > 40:
            self.influence_radius = min(
                20.0, self.influence_radius + 0.20
            )

        # Retirement
        if self.age >= 65:
            self.employment_status = "retired"
            self.civic_contribution = min(
                1.0, self.civic_contribution + 0.02
            )

        # Death — stochastic life expectancy
        life_expectancy = random.gauss(72, 8)
        if self.age >= life_expectancy:
            self._die()

    def _die(self):
        """Agent death — transfer wealth, remove from model."""
        self.is_alive = False
        # Savings transfer to next generation (simplified)
        self.model.shared_data["inheritance_pool"] = (
            self.model.shared_data.get("inheritance_pool", 0.0) +
            self.savings * 0.70
        )

    # ══════════════════════════════════════════════════════════════════════════
    # MERIT CALCULATION (Article 3.2)
    # ══════════════════════════════════════════════════════════════════════════

    def _calculate_merit(self) -> float:
        """
        M = (Productivity * 0.40) + (Education * 0.30)
            + (Performance * 0.20) + (Civic * 0.10)
        All components: 0.0 to 1.0
        Result: 0.0 to 1.0
        """

        c = CONSTITUTION.merit
        merit = (
            self.productivity * c.PRODUCTIVITY_WEIGHT +
            self.education_level * c.EDUCATION_WEIGHT +
            self.performance * c.PERFORMANCE_WEIGHT +
            self.civic_contribution * c.CIVIC_WEIGHT
        )
        return max(0.0, min(1.0, merit))

    # ══════════════════════════════════════════════════════════════════════════
    # TAX EXEMPTION CHECK (Article 10.10)
    # ══════════════════════════════════════════════════════════════════════════

    def _check_tax_exempt(self) -> bool:
        """
        Three exempt categories only — no profession exemptions.
        Article 10.10: under 18, active student, PhD stipend.
        """

        if self.age < 18:
            return True
        if self.is_student and not self.is_phd_candidate:
            return True
        if self.is_phd_candidate:
            return True  # stipend is research grant not salary
        return False

    # ══════════════════════════════════════════════════════════════════════════
    # INITIALIZATION HELPERS
    # ══════════════════════════════════════════════════════════════════════════

    @staticmethod
    def _init_attr(base: float, noise: float) -> float:
        """Initialize attribute with Gaussian noise for individual variation."""
        value = random.gauss(base, noise)
        return max(0.0, min(1.0, value))

    def _init_income(self) -> float:
        """Initialize income based on age and education level."""
        base_income = 1000.0  # base annual units
        age_factor = min(2.0, self.age / 30.0) if self.age > 0 else 0.5
        education_factor = 1.0 + self.education_level * 1.5
        return base_income * age_factor * education_factor * random.uniform(0.8, 1.2)

    def _init_education(self) -> float:
        """Initialize education level based on age."""
        if self.age < 6:
            return 0.0
        elif self.age < 12:
            return random.uniform(0.05, 0.20)
        elif self.age < 18:
            return random.uniform(0.20, 0.45)
        elif self.age < 23:
            return random.uniform(0.40, 0.65)
        else:
            return random.uniform(0.45, 0.85)

    def _init_grievance(self) -> float:
        """Initial grievance — Myanmar Year Zero conditions."""
        base = 0.55  # high starting grievance — post-conflict
        noise = random.gauss(0, 0.10)
        return max(0.0, min(1.0, base + noise))

    def _init_employment(self) -> str:
        """Initial employment status based on age."""
        if self.age < 16:
            return "student"
        elif self.age < 18:
            return "student"
        elif self.age > 65:
            return "retired"
        else:
            # Year Zero employment rate ~58%
            return "employed" if random.random() < 0.58 else "unemployed"

    def _init_student_status(self) -> bool:
        """Student if between 6-22 years old."""
        return 6 <= self.age <= 22

    def _assign_religion(self) -> str:
        """Assign religion based on ethnicity distribution."""
        religion_map = {
            "Bamar": ["Buddhist"] * 89 + ["Christian"] * 4 + ["Muslim"] * 4 + ["Other"] * 3,
            "Karen": ["Buddhist"] * 40 + ["Christian"] * 45 + ["Other"] * 15,
            "Kachin": ["Christian"] * 90 + ["Buddhist"] * 8 + ["Other"] * 2,
            "Chin": ["Christian"] * 85 + ["Buddhist"] * 10 + ["Other"] * 5,
            "Shan": ["Buddhist"] * 80 + ["Christian"] * 10 + ["Other"] * 10,
            "Mon": ["Buddhist"] * 92 + ["Other"] * 8,
            "Rakhine": ["Buddhist"] * 90 + ["Muslim"] * 5 + ["Other"] * 5,
            "Kayah": ["Christian"] * 60 + ["Buddhist"] * 30 + ["Other"] * 10
        }
        options = religion_map.get(self.ethnicity, ["Buddhist"] * 100)
        return random.choice(options)

    def _assign_trauma_category(self) -> Optional[str]:
        """Assign trauma category based on archetype and ethnicity."""
        if self.trauma_score < 0.20:
            return None

        if self.archetype == "trauma_carrier":
            return random.choice([
                "warfare_conflict",
                "family_domestic_abuse",
                "environmental_displacement"
            ])

        if self.trauma_score > 0.40:
            return random.choice(
                CONSTITUTION.psychology.TRAUMA_CATEGORIES
            )

        return None

    # ══════════════════════════════════════════════════════════════════════════
    # SOCIAL INFLUENCE — NETWORK SIGNAL RECEPTION
    # ══════════════════════════════════════════════════════════════════════════

    def receive_signal(self, signal: Dict, distance: int = 1):
        """
        Receive influence from network neighbors.
        Effect diminishes with distance.
        Ethnic similarity amplifies effect.
        """

        # Influence diminishes with network distance
        distance_decay = 1.0 / (distance * 2)

        signal_type = signal.get("type")

        if signal_type == "protest":
            # Protest contagion
            sender_grievance = signal.get("grievance", 0.50)
            contagion = sender_grievance * distance_decay * 0.15
            self.grievance = min(1.0, self.grievance + contagion)

        elif signal_type == "shame_register":
            # Shame register deterrent effect
            self.known_shame_register_victim = True
            self.corruption_tolerance = max(
                0.0,
                self.corruption_tolerance -
                CONSTITUTION.crypto_justice.SHAME_REGISTER_CORRUPTION_REDUCTION
                * distance_decay
            )

        elif signal_type == "emigration":
            # Emigration contagion — especially among same archetype
            if signal.get("archetype") == self.archetype:
                self.emigration_threshold = max(
                    0.20,
                    self.emigration_threshold - 0.03 * distance_decay
                )

        elif signal_type == "trust_recovery":
            # Positive signals — IIG bust, government success
            self.trust_score = min(
                1.0,
                self.trust_score + 0.05 * distance_decay
            )

    def observe_shame_register_update(self, case: Dict):
        """
        Called when Total Ruin Protocol executes on any official.
        Creates fear-of-shame effect across all citizen agents.
        """

        self.known_shame_register_victim = True
        self.corruption_tolerance = max(
            0.0,
            self.corruption_tolerance * (
                1.0 - CONSTITUTION.crypto_justice.SHAME_REGISTER_CORRUPTION_REDUCTION
            )
        )

    def observe_environment(self, shared_data: Dict):
        """Called by model broadcaster — agent reads shared state."""
        # Poverty line update for tax calculation
        if "poverty_line" in shared_data:
            self.model.shared_data["poverty_line"] = shared_data["poverty_line"]

    # ══════════════════════════════════════════════════════════════════════════
    # UTILITY METHODS
    # ══════════════════════════════════════════════════════════════════════════

    def is_public_office_eligible(self) -> bool:
        """
        Check eligibility for public office.
        Article 3.2a — merit minimum 0.60.
        Article 3.5 — no disqualifications.
        Article 9.5 — national service completed.
        """

        return (
            self.merit_score >= CONSTITUTION.merit.MERIT_MIN_PUBLIC_OFFICE and
            not self.corruption_detected and
            self.national_service_completed and
            self.is_alive and
            not self.has_emigrated
        )

    def is_iig_academy_eligible(self) -> bool:
        """
        IIG Academy eligibility check.
        Article 7.0.1 — all four conditions must be met.
        """

        return (
            self.national_service_completed and
            self.merit_score >= CONSTITUTION.iig.ENTRY_MERIT_MIN and
            self.age >= CONSTITUTION.iig.ENTRY_MIN_AGE and
            not self.corruption_detected
        )

    def get_state_dict(self) -> Dict:
        """
        Return current agent state as dictionary.
        Used by DataCollector for KPI tracking.
        """

        return {
            "id": self.unique_id,
            "archetype": self.archetype,
            "age": self.age,
            "ethnicity": self.ethnicity,
            "state_id": self.state_id,
            "merit_score": round(self.merit_score, 4),
            "trust_score": round(self.trust_score, 4),
            "grievance": round(self.grievance, 4),
            "corruption_tolerance": round(self.corruption_tolerance, 4),
            "trauma_score": round(self.trauma_score, 4),
            "income": round(self.income, 2),
            "tax_exempt": self.tax_exempt,
            "declared_all_income": self.declared_all_income,
            "employment_status": self.employment_status,
            "national_service_completed": self.national_service_completed,
            "national_service_track": self.national_service_track,
            "is_phd_candidate": self.is_phd_candidate,
            "has_emigrated": self.has_emigrated,
            "is_protesting": self.is_protesting,
            "is_alive": self.is_alive,
            "constitutional_loyalty": round(self.constitutional_loyalty, 4),
            "ethnic_cross_exposure": round(self.ethnic_cross_exposure, 4),
            "years_in_system": self.years_in_system
        }

    def __repr__(self) -> str:
        return (
            f"CitizenAgent(id={self.unique_id}, "
            f"archetype={self.archetype}, "
            f"age={self.age}, "
            f"ethnicity={self.ethnicity}, "
            f"merit={self.merit_score:.3f}, "
            f"grievance={self.grievance:.3f})"
        )


# ══════════════════════════════════════════════════════════════════════════════
# CITIZEN POPULATION FACTORY
# ══════════════════════════════════════════════════════════════════════════════

class CitizenPopulation:
    """
    Factory class for creating the initial citizen population.
    Ensures correct archetype distribution and ethnic composition.
    """

    @staticmethod
    def create_population(model, n: int = 9500) -> List[CitizenAgent]:
        """
        Create n citizen agents with correct archetype and ethnic distribution.
        Uses constitution archetype proportions.
        """

        citizens = []
        archetype_counts = CitizenPopulation._calculate_archetype_counts(n)
        agent_id = 0

        for archetype, count in archetype_counts.items():
            for _ in range(count):
                state_id = CitizenPopulation._assign_state()
                ethnicity = CitizenPopulation._assign_ethnicity(state_id)
                age = CitizenPopulation._assign_age()

                agent = CitizenAgent(
                    unique_id=agent_id,
                    model=model,
                    archetype=archetype,
                    state_id=state_id,
                    ethnicity=ethnicity,
                    age=age
                )
                citizens.append(agent)
                agent_id += 1

        return citizens

    @staticmethod
    def _calculate_archetype_counts(n: int) -> Dict[str, int]:
        """Calculate exact agent counts per archetype."""
        proportions = CONSTITUTION.simulation.ARCHETYPES
        counts = {}
        total = 0

        for archetype, proportion in proportions.items():
            count = round(n * proportion)
            counts[archetype] = count
            total += count

        # Adjust for rounding — add remainder to largest group
        remainder = n - total
        largest = max(counts, key=counts.get)
        counts[largest] += remainder

        return counts

    @staticmethod
    def _assign_state() -> str:
        """Assign state based on population distribution."""
        states = list(CONSTITUTION.simulation.SIMULATION_STATES)
        weights = [0.40, 0.25, 0.20, 0.15]  # Bamar central largest
        return random.choices(states, weights=weights)[0]

    @staticmethod
    def _assign_ethnicity(state_id: str) -> str:
        """Assign ethnicity based on state composition."""
        state_ethnic_map = {
            "bamar_central": ["Bamar"] * 75 + ["Mon"] * 25,
            "shan_eastern": ["Shan"] * 70 + ["Kayah"] * 30,
            "karen_southern": ["Karen"] * 65 + ["Rakhine"] * 35,
            "kachin_northern": ["Kachin"] * 60 + ["Chin"] * 40
        }
        options = state_ethnic_map.get(
            state_id,
            ETHNIC_GROUPS
        )
        return random.choice(options)

    @staticmethod
    def _assign_age() -> int:
        """
        Assign age with Myanmar population pyramid.
        Young population — skewed toward 0-35.
        """

        # Myanmar age distribution (approximate)
        age_groups = [
            (0, 14, 0.28),
            (15, 29, 0.27),
            (30, 44, 0.20),
            (45, 59, 0.14),
            (60, 80, 0.11)
        ]

        r = random.random()
        cumulative = 0.0

        for (low, high, prob) in age_groups:
            cumulative += prob
            if r <= cumulative:
                return random.randint(low, high)

        return random.randint(0, 80)


# ══════════════════════════════════════════════════════════════════════════════
# QUICK TEST
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":

    print("Testing CitizenAgent...")

    # Minimal mock model for testing
    class MockModel:
        def __init__(self):
            self.current_year = 0
            self.states = {
                "bamar_central": {
                    "corruption_level": 0.72,
                    "employment_rate": 0.58,
                    "trust_index": 0.22,
                    "ethnic_tension": 0.65,
                    "gdp_growth": 0.02,
                    "resource_revenue": 100.0,
                    "gdp": 1000.0,
                    "knowledge_capital": 0.0,
                    "protest_activity": 0.0,
                    "iig_activity": 0.0,
                    "merit_integrity": 0.50
                }
            }
            self.shared_data = {
                "poverty_line": 1000.0,
                "tax_revenue": 0.0,
                "shame_register": [],
                "emigrants": [],
                "bribery_attempts": [],
                "corruption_reports": [],
                "tax_evasion_detected": [],
                "phd_graduates": 0,
                "rights_violated": False,
                "network_protest_rate": 0.0,
                "iig_effectiveness": 0.40,
                "policy_quality": 0.40,
                "inheritance_pool": 0.0
            }

    mock = MockModel()

    # Test each archetype
    print("\nArchetype creation test:")
    for archetype in ARCHETYPES.keys():
        agent = CitizenAgent(
            unique_id=0,
            model=mock,
            archetype=archetype,
            state_id="bamar_central",
            ethnicity="Bamar",
            age=30
        )
        print(f"  {archetype:25s} | merit={agent.merit_score:.3f} | "
              f"grievance={agent.grievance:.3f} | "
              f"trust={agent.trust_score:.3f}")

    # Test population factory
    print("\nPopulation factory test (100 agents):")
    citizens = CitizenPopulation.create_population(mock, n=100)
    archetype_dist = {}
    for c in citizens:
        archetype_dist[c.archetype] = archetype_dist.get(c.archetype, 0) + 1
    for k, v in sorted(archetype_dist.items()):
        print(f"  {k:25s}: {v}")

    # Test step
    print("\nStep test (10 years):")
    test_agent = citizens[0]
    for year in range(10):
        mock.current_year = year
        test_agent.step()

    print(f"  Agent after 10 years: {test_agent}")
    print(f"  Tax exempt: {test_agent.tax_exempt}")
    print(f"  NS completed: {test_agent.national_service_completed}")
    print(f"  Merit: {test_agent.merit_score:.4f}")
    print(f"  Grievance: {test_agent.grievance:.4f}")

    # Test merit formula
    print("\nMerit formula validation:")
    agent = CitizenAgent(0, mock, "ambitious_meritocrat", "bamar_central", "Bamar", 30)
    agent.productivity = 0.80
    agent.education_level = 0.70
    agent.performance = 0.75
    agent.civic_contribution = 0.60
    expected = 0.80*0.40 + 0.70*0.30 + 0.75*0.20 + 0.60*0.10
    calculated = agent._calculate_merit()
    print(f"  Expected:   {expected:.4f}")
    print(f"  Calculated: {calculated:.4f}")
    print(f"  Match: {abs(expected - calculated) < 1e-9}")

    print("\ncitizen.py loaded successfully")