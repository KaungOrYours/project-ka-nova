"""
================================================================================
PROJECT KA-NOVA
agents/official.py

Official Agent — Government Officials, Ministers, Chancellor, President
Ka-Nova Simulation Engine v2.0

Phase 2 changes (surgical only — all other classes verbatim from Phase 1):

    CHANGE 1 — ChancellorAgent:
        Added PHASE2_LLM_CONTROLLED = True class flag.
        step() now returns immediately — LangChain EliteAgentLayer handles
        Chancellor logic via engine/elite_agents.py.
        Class shell kept so all imports across the codebase still work.
        _implement_policy() and _command_military_check() preserved but
        not called from step() — EliteAgentLayer writes results to shared_data.

    CHANGE 2 — PresidentAgent:
        Same as ChancellorAgent — PHASE2_LLM_CONTROLLED = True.
        step() returns immediately.
        cast_tiebreaker_vote() preserved — called from chambers.py, not step().
        Class shell kept for import compatibility.

    CHANGE 3 — OfficialPopulation.create_population():
        ChancellorAgent and PresidentAgent instantiated and stored as
        model references (model.chancellor_agent, model.president_agent)
        but NOT added to the returned officials list.
        This means they are NOT added to self.schedule in model._create_agents(),
        so Mesa never calls their step().

All other classes — OfficialAgent, EthnicLeaderAgent, AnalysisCouncilMember,
MinisterAgent, CongressMember — completely unchanged from Phase 1.

Author: Kaung Htet
License: MIT
================================================================================
"""

from __future__ import annotations

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import random
from typing import Optional, Dict, List
from mesa import Agent

from config.constitution import CONSTITUTION
from agents.citizen import CitizenAgent, ARCHETYPES, ETHNIC_GROUPS


# ══════════════════════════════════════════════════════════════════════════════
# ROLE DEFINITIONS — unchanged from Phase 1
# ══════════════════════════════════════════════════════════════════════════════

OFFICIAL_ROLES: Dict[str, Dict] = {
    "president": {
        "merit_min": CONSTITUTION.merit.MERIT_MIN_PUBLIC_OFFICE,
        "term_years": CONSTITUTION.executive.PRESIDENT_TERM,
        "max_terms": CONSTITUTION.executive.PRESIDENT_MAX_TERMS,
        "executive_power": False,
        "tiebreaker": True,
        "removal_chambers": CONSTITUTION.executive.PRESIDENT_REMOVAL_CHAMBERS,
        "cooling_off": 0
    },
    "chancellor": {
        "merit_min": CONSTITUTION.merit.MERIT_MIN_PUBLIC_OFFICE,
        "term_years": CONSTITUTION.executive.CHANCELLOR_TERM,
        "max_terms": CONSTITUTION.executive.CHANCELLOR_MAX_TERMS,
        "executive_power": True,
        "tiebreaker": False,
        "removal_chambers": CONSTITUTION.executive.CHANCELLOR_DISMISSAL_CHAMBERS_REQUIRED,
        "cooling_off": CONSTITUTION.executive.CHANCELLOR_COOLING_OFF
    },
    "minister": {
        "merit_min": CONSTITUTION.executive.MINISTER_MERIT_MIN,
        "term_years": CONSTITUTION.executive.CHANCELLOR_TERM,
        "max_terms": 99,
        "executive_power": True,
        "tiebreaker": False,
        "removal_chambers": 0,
        "cooling_off": 0
    },
    "congress_member": {
        "merit_min": CONSTITUTION.merit.MERIT_MIN_PUBLIC_OFFICE,
        "term_years": CONSTITUTION.chambers.CONGRESS_TERM,
        "max_terms": 99,
        "executive_power": False,
        "tiebreaker": False,
        "removal_chambers": 0,
        "cooling_off": 0
    },
    "ethnic_leader": {
        "merit_min": CONSTITUTION.merit.MERIT_MIN_PUBLIC_OFFICE,
        "term_years": CONSTITUTION.chambers.ETHNIC_TERM,
        "max_terms": CONSTITUTION.chambers.ETHNIC_MAX_TERMS,
        "executive_power": False,
        "tiebreaker": False,
        "removal_chambers": 0,
        "cooling_off": 0
    },
    "analysis_council_member": {
        "merit_min": CONSTITUTION.chambers.ANALYSIS_MERIT_MIN,
        "term_years": CONSTITUTION.chambers.ANALYSIS_TERM,
        "max_terms": 99,
        "executive_power": False,
        "tiebreaker": False,
        "removal_chambers": 0,
        "cooling_off": 0
    }
}


# ══════════════════════════════════════════════════════════════════════════════
# BASE OFFICIAL AGENT — unchanged from Phase 1
# ══════════════════════════════════════════════════════════════════════════════

class OfficialAgent(CitizenAgent):
    """
    Government Official — extends CitizenAgent with constitutional role.

    Key additions over CitizenAgent:
    - Role-specific powers and constraints
    - Merit examination requirement
    - Corruption opportunity mechanics
    - Term tracking and term limits
    - Psychological screening (Article 18)
    - Removal vulnerability
    - Policy voting behavior
    """

    def __init__(
        self,
        unique_id: int,
        model,
        role: str,
        state_id: str,
        ethnicity: str,
        age: int = 35,
        ministry: str = None
    ):
        archetype = self._assign_archetype_for_role(role)
        super().__init__(
            unique_id=unique_id,
            model=model,
            archetype=archetype,
            state_id=state_id,
            ethnicity=ethnicity,
            age=age
        )

        self.role = role
        self.ministry = ministry
        self.role_config = OFFICIAL_ROLES.get(role, OFFICIAL_ROLES["congress_member"])

        merit_floor = self.role_config["merit_min"]
        if self.merit_score < merit_floor:
            boost = merit_floor - self.merit_score + random.uniform(0.0, 0.15)
            self.productivity = min(1.0, self.productivity + boost * 0.4)
            self.education_level = min(1.0, self.education_level + boost * 0.3)
            self.performance = min(1.0, self.performance + boost * 0.2)
            self.civic_contribution = min(1.0, self.civic_contribution + boost * 0.1)
            self.merit_score = self._calculate_merit()

        self.terms_served = 0
        self.term_remaining = self.role_config["term_years"]
        self.max_terms = self.role_config["max_terms"]
        self.year_appointed = None

        self.corruption_score = self._init_corruption_score()
        self.corruption_opportunities = 0
        self.corruption_acts = 0
        self.bribery_received = 0.0
        self.embezzlement = 0.0
        self.corruption_network = []

        self.ambition = self._init_attr(random.uniform(0.30, 0.85), 0.10)
        self.loyalty_to_chancellor = random.uniform(0.20, 0.80)
        self.coalition_members: List[int] = []

        self.psych_screen_due = True
        self.psych_screen_months = 0
        self.psych_probation = False
        self.psych_probation_months = 0
        self.consultation_sessions_this_month = 0
        self.psych_attendance_record: List[bool] = []

        self.permanently_disqualified = False
        self.disqualification_reason = None
        self.total_ruin_triggered = False

        self.policy_votes: List[Dict] = []
        self.veto_count = 0
        self.approval_rating = random.uniform(0.40, 0.70)

        self.no_confidence_votes = 0
        self.removed_mid_term = False
        self.removal_reason = None

        self.national_service_completed = True
        self.constitutional_loyalty = min(1.0, self.constitutional_loyalty + 0.20)

    # ══════════════════════════════════════════════════════════════════════════
    # MESA STEP — unchanged from Phase 1
    # ══════════════════════════════════════════════════════════════════════════

    def step(self):
        """Annual official agent update cycle."""

        if not self.is_alive or self.permanently_disqualified:
            return

        local_env = self._perceive_environment()
        self.memory.append(local_env)

        self._psych_screening_update()
        self._decide_corruption(local_env)
        self._decide_policy_votes(local_env)
        self._build_coalitions()
        self._update_approval_rating(local_env)
        self._update_term()

        if (self.model.current_year % CONSTITUTION.merit.RECERTIFICATION_INTERVAL == 0
                and self.model.current_year > 0):
            self._merit_recertification()

        self._update_thresholds(local_env)
        self._life_course_update()
        self.merit_score = self._calculate_merit()
        self._update_grievance(local_env)
        self.years_in_system += 1

    # ══════════════════════════════════════════════════════════════════════════
    # CORRUPTION MECHANICS — unchanged from Phase 1
    # ══════════════════════════════════════════════════════════════════════════

    def _decide_corruption(self, env: Dict):
        if self.permanently_disqualified:
            return

        iig_effectiveness = self.model.shared_data.get("iig_effectiveness", 0.50)
        state_corruption = env.get("corruption_level", 0.60)
        shame_deterrent = 0.40 if self.known_shame_register_victim else 0.0

        corrupt_prob = (
            self.corruption_tolerance * 0.25 +
            self.ambition * 0.20 +
            state_corruption * 0.20 +
            (1.0 - self.constitutional_loyalty) * 0.20 +
            (1.0 - iig_effectiveness) * 0.15
        )

        corrupt_prob -= shame_deterrent * 0.30
        corrupt_prob -= self.constitutional_loyalty * 0.15

        if self.psych_probation:
            corrupt_prob += 0.10

        corrupt_prob = max(0.0, min(1.0, corrupt_prob))

        if random.random() < corrupt_prob:
            self._commit_corruption_act()

    def _commit_corruption_act(self):
        if self.role in ["chancellor", "minister"]:
            act_type = random.choice([
                "embezzlement", "bribery_received",
                "merit_subversion", "resource_misappropriation"
            ])
        else:
            act_type = random.choice([
                "bribery_received", "vote_selling", "nepotism"
            ])

        amount = self.income * random.uniform(0.05, 0.50)

        if act_type == "embezzlement":
            self.embezzlement += amount
        elif act_type == "bribery_received":
            self.bribery_received += amount

        self.corruption_score = min(
            1.0, self.corruption_score + random.uniform(0.05, 0.15)
        )
        self.corruption_acts += 1

        self.model.shared_data.setdefault("corruption_acts_log", []).append({
            "official_id": self.unique_id,
            "role": self.role,
            "state": self.state_id,
            "act_type": act_type,
            "amount": amount,
            "corruption_score": self.corruption_score,
            "year": self.model.current_year
        })

        self.has_event_to_broadcast = True
        self.broadcast_signal = {
            "type": "corruption_normalized",
            "corruption_score": self.corruption_score,
            "state": self.state_id
        }

    # ══════════════════════════════════════════════════════════════════════════
    # POLICY VOTING — unchanged from Phase 1
    # ══════════════════════════════════════════════════════════════════════════

    def _decide_policy_votes(self, env: Dict):
        pending_policies = self.model.shared_data.get("pending_policies", [])

        for policy in pending_policies:
            if policy.get("voted", False):
                continue

            vote = self._evaluate_policy(policy, env)
            self.policy_votes.append({
                "policy_id": policy.get("id"),
                "vote": vote,
                "year": self.model.current_year,
                "role": self.role
            })

            policy_votes = self.model.shared_data.setdefault("policy_vote_results", {})
            policy_id = policy.get("id", "unknown")
            if policy_id not in policy_votes:
                policy_votes[policy_id] = {"yes": 0, "no": 0, "abstain": 0}
            policy_votes[policy_id][vote] += 1

    def _evaluate_policy(self, policy: Dict, env: Dict) -> str:
        policy_type = policy.get("type", "general")
        policy_benefit = policy.get("benefit_score", 0.50)
        ethnic_impact = policy.get("ethnic_impact", {}).get(self.ethnicity, 0.0)

        yes_prob = (
            policy_benefit * 0.40 +
            self.merit_score * 0.20 +
            self.constitutional_loyalty * 0.20 +
            ethnic_impact * 0.20
        )

        if self.corruption_score > 0.50:
            yes_prob += random.uniform(-0.20, 0.20)

        if self.role == "analysis_council_member":
            evidence = policy.get("evidence_quality", 0.50)
            yes_prob = evidence * 0.70 + yes_prob * 0.30

        if yes_prob > 0.60:
            return "yes"
        elif yes_prob < 0.35:
            return "no"
        else:
            return "abstain"

    # ══════════════════════════════════════════════════════════════════════════
    # PSYCHOLOGICAL HEALTH SCREENING — unchanged from Phase 1
    # ══════════════════════════════════════════════════════════════════════════

    def _psych_screening_update(self):
        self.psych_screen_months += 12

        screening_interval = CONSTITUTION.psychology.SCREENING_INTERVAL_MONTHS

        if self.psych_screen_months >= screening_interval:
            self.psych_screen_months = 0
            self._conduct_psych_screening()

        if self.psych_probation:
            self.psych_probation_months += 12
            if self.psych_probation_months >= CONSTITUTION.psychology.SEVERE_PROBATION_MONTHS:
                self._complete_probation()

    def _conduct_psych_screening(self):
        psych_score = (
            self.trauma_score * 0.40 +
            (1.0 - self.resilience) * 0.30 +
            self.grievance * 0.20 +
            (self.corruption_score * 0.10)
        )

        review_variation = random.gauss(0, 0.05)
        psych_score = max(0.0, min(1.0, psych_score + review_variation))

        stable_threshold = CONSTITUTION.psychology.OUTCOME_STABLE_THRESHOLD
        severe_threshold = CONSTITUTION.psychology.OUTCOME_SEVERE_THRESHOLD

        if psych_score <= stable_threshold:
            self.psych_status = "stable"
            self.psych_probation = False
        elif psych_score <= severe_threshold:
            self.psych_status = "acceptable"
            self.model.shared_data.setdefault(
                "psych_consultation_required", []
            ).append(self.unique_id)
        else:
            self.psych_status = "severe"
            self._begin_psych_probation()

        self.psych_attendance_record.append(True)

    def _begin_psych_probation(self):
        self.psych_probation = True
        self.psych_probation_months = 0

        self.model.shared_data.setdefault("psych_probation_officials", []).append({
            "official_id": self.unique_id,
            "role": self.role,
            "year": self.model.current_year,
            "trauma_category": self.trauma_category
        })

        self.trust_score = min(1.0, self.trust_score + 0.05)
        self.trauma_score = max(0.0, self.trauma_score - 0.10)
        self.resilience = min(1.0, self.resilience + 0.08)

    def _complete_probation(self):
        self.psych_probation = False
        self.psych_probation_months = 0
        self.psych_status = "stable"

    def stop_treatment(self):
        consequence = CONSTITUTION.psychology.STOP_CONSEQUENCE
        if consequence == "automatic_temporary_disqualification":
            self.psych_probation = True
            self.psych_status = "severe"
            self.model.shared_data.setdefault(
                "voluntary_treatment_stop", []
            ).append(self.unique_id)

    # ══════════════════════════════════════════════════════════════════════════
    # MERIT RECERTIFICATION — unchanged from Phase 1
    # ══════════════════════════════════════════════════════════════════════════

    def _merit_recertification(self):
        self.merit_score = self._calculate_merit()

        if self.merit_score < CONSTITUTION.merit.RECERTIFICATION_FAIL_THRESHOLD:
            self._fail_recertification()
        else:
            self.model.shared_data.setdefault("recertification_passed", []).append({
                "official_id": self.unique_id,
                "role": self.role,
                "merit_score": self.merit_score,
                "year": self.model.current_year
            })

    def _fail_recertification(self):
        failed_count = self.model.shared_data.setdefault(
            f"recert_fails_{self.unique_id}", 0
        )
        self.model.shared_data[f"recert_fails_{self.unique_id}"] = failed_count + 1

        if failed_count >= 1:
            self._permanently_disqualify("two_consecutive_failed_reviews")
        else:
            self.model.shared_data.setdefault("recertification_failed", []).append({
                "official_id": self.unique_id,
                "role": self.role,
                "merit_score": self.merit_score,
                "year": self.model.current_year,
                "vacate_by": self.model.current_year + 1
            })

    # ══════════════════════════════════════════════════════════════════════════
    # DISQUALIFICATION AND REMOVAL — unchanged from Phase 1
    # ══════════════════════════════════════════════════════════════════════════

    def _permanently_disqualify(self, reason: str):
        self.permanently_disqualified = True
        self.disqualification_reason = reason

        self.model.shared_data.setdefault("permanently_disqualified", []).append({
            "official_id": self.unique_id,
            "role": self.role,
            "reason": reason,
            "year": self.model.current_year
        })

    def receive_no_confidence_vote(self, chamber: str):
        self.no_confidence_votes += 1

        required = self.role_config.get("removal_chambers", 2)
        requires_president = CONSTITUTION.executive.CHANCELLOR_DISMISSAL_REQUIRES_PRESIDENT

        if self.no_confidence_votes >= required:
            if self.role == "chancellor":
                president_signs = self.model.shared_data.get(
                    "president_signs_dismissal", False
                )
                if president_signs or not requires_president:
                    self._remove_from_office("no_confidence")
            else:
                self._remove_from_office("no_confidence")

    def _remove_from_office(self, reason: str):
        self.removed_mid_term = True
        self.removal_reason = reason

        self.model.shared_data.setdefault("officials_removed", []).append({
            "official_id": self.unique_id,
            "role": self.role,
            "reason": reason,
            "year": self.model.current_year,
            "merit_score": self.merit_score
        })

    # ══════════════════════════════════════════════════════════════════════════
    # TOTAL RUIN PROTOCOL — unchanged from Phase 1
    # ══════════════════════════════════════════════════════════════════════════

    def trigger_total_ruin(self):
        self.total_ruin_triggered = True

        self.savings = 0.0
        self.income = 0.0

        seized_amount = self.embezzlement + self.bribery_received + self.savings
        self.model.shared_data["federal_dev_fund"] = (
            self.model.shared_data.get("federal_dev_fund", 0.0) + seized_amount
        )

        self._permanently_disqualify("corruption_conviction")

        self.model.shared_data.setdefault("shame_register", []).append({
            "official_id": self.unique_id,
            "name_hash": hash(self.unique_id),
            "role": self.role,
            "offence": self.disqualification_reason,
            "assets_seized": seized_amount,
            "year": self.model.current_year,
            "permanent": True,
            "blockchain_recorded": True
        })

        self.has_event_to_broadcast = True
        self.broadcast_signal = {
            "type": "shame_register",
            "role": self.role,
            "corruption_score": self.corruption_score,
            "year": self.model.current_year
        }

        self.model.shared_data["total_ruin_events"] = (
            self.model.shared_data.get("total_ruin_events", 0) + 1
        )

    # ══════════════════════════════════════════════════════════════════════════
    # COALITION BUILDING — unchanged from Phase 1
    # ══════════════════════════════════════════════════════════════════════════

    def _build_coalitions(self):
        if self.ambition < 0.60:
            return

        all_officials = [
            a for a in self.model.schedule.agents
            if isinstance(a, OfficialAgent) and a.unique_id != self.unique_id
        ]

        for official in random.sample(all_officials, min(3, len(all_officials))):
            compatibility = (
                abs(self.corruption_tolerance - official.corruption_tolerance) < 0.20
                and self.ethnicity == official.ethnicity
            )
            if compatibility and official.unique_id not in self.coalition_members:
                self.coalition_members.append(official.unique_id)

    # ══════════════════════════════════════════════════════════════════════════
    # APPROVAL RATING — unchanged from Phase 1
    # ══════════════════════════════════════════════════════════════════════════

    def _update_approval_rating(self, env: Dict):
        trust = env.get("trust_index", 0.40)
        employment = env.get("employment_rate", 0.58)

        performance_factor = (
            self.merit_score * 0.35 +
            trust * 0.35 +
            employment * 0.30
        )

        if self.corruption_score > 0.40:
            performance_factor -= self.corruption_score * 0.30

        self.approval_rating = (
            self.approval_rating * 0.70 + performance_factor * 0.30
        )
        self.approval_rating = max(0.0, min(1.0, self.approval_rating))

        if self.role == "president":
            self.model.shared_data["president_approval"] = self.approval_rating

    # ══════════════════════════════════════════════════════════════════════════
    # TERM MANAGEMENT — unchanged from Phase 1
    # ══════════════════════════════════════════════════════════════════════════

    def _update_term(self):
        self.term_remaining -= 1

        if self.term_remaining <= 0:
            self.terms_served += 1

            if self.terms_served >= self.max_terms:
                self._complete_term()
            else:
                self.term_remaining = self.role_config["term_years"]
                self.no_confidence_votes = 0

    def _complete_term(self):
        self.model.shared_data.setdefault("officials_term_complete", []).append({
            "official_id": self.unique_id,
            "role": self.role,
            "terms_served": self.terms_served,
            "year": self.model.current_year,
            "merit_score": self.merit_score,
            "approval_rating": self.approval_rating
        })

    # ══════════════════════════════════════════════════════════════════════════
    # INITIALIZATION HELPERS — unchanged from Phase 1
    # ══════════════════════════════════════════════════════════════════════════

    def _init_corruption_score(self) -> float:
        base = self.corruption_tolerance * 0.30 + random.uniform(0.0, 0.15)
        return max(0.0, min(0.50, base))

    @staticmethod
    def _assign_archetype_for_role(role: str) -> str:
        role_archetype_weights = {
            "president": {
                "civic_champion": 0.35,
                "ambitious_meritocrat": 0.30,
                "ethnic_loyalist": 0.20,
                "pragmatic_survivor": 0.15
            },
            "chancellor": {
                "ambitious_meritocrat": 0.40,
                "civic_champion": 0.30,
                "pragmatic_survivor": 0.20,
                "ethnic_loyalist": 0.10
            },
            "minister": {
                "ambitious_meritocrat": 0.35,
                "civic_champion": 0.25,
                "pragmatic_survivor": 0.25,
                "ethnic_loyalist": 0.15
            },
            "congress_member": {
                "pragmatic_survivor": 0.35,
                "ambitious_meritocrat": 0.25,
                "civic_champion": 0.20,
                "ethnic_loyalist": 0.20
            },
            "ethnic_leader": {
                "ethnic_loyalist": 0.50,
                "civic_champion": 0.25,
                "pragmatic_survivor": 0.15,
                "ambitious_meritocrat": 0.10
            },
            "analysis_council_member": {
                "ambitious_meritocrat": 0.50,
                "civic_champion": 0.35,
                "pragmatic_survivor": 0.15
            }
        }

        weights_dict = role_archetype_weights.get(
            role,
            {"pragmatic_survivor": 0.40, "ambitious_meritocrat": 0.35,
             "civic_champion": 0.25}
        )

        archetypes = list(weights_dict.keys())
        weights = list(weights_dict.values())
        return random.choices(archetypes, weights=weights)[0]

    # ══════════════════════════════════════════════════════════════════════════
    # STATE REPORTING — unchanged from Phase 1
    # ══════════════════════════════════════════════════════════════════════════

    def get_state_dict(self) -> Dict:
        base = super().get_state_dict()
        base.update({
            "role": self.role,
            "ministry": self.ministry,
            "corruption_score": round(self.corruption_score, 4),
            "corruption_acts": self.corruption_acts,
            "ambition": round(self.ambition, 4),
            "approval_rating": round(self.approval_rating, 4),
            "terms_served": self.terms_served,
            "term_remaining": self.term_remaining,
            "psych_status": self.psych_status,
            "psych_probation": self.psych_probation,
            "permanently_disqualified": self.permanently_disqualified,
            "total_ruin_triggered": self.total_ruin_triggered,
            "removed_mid_term": self.removed_mid_term,
            "no_confidence_votes": self.no_confidence_votes,
            "coalition_size": len(self.coalition_members)
        })
        return base

    def __repr__(self) -> str:
        return (
            f"OfficialAgent(id={self.unique_id}, "
            f"role={self.role}, "
            f"merit={self.merit_score:.3f}, "
            f"corruption={self.corruption_score:.3f}, "
            f"approval={self.approval_rating:.3f}, "
            f"term_remaining={self.term_remaining})"
        )


# ══════════════════════════════════════════════════════════════════════════════
# CHANCELLOR AGENT
# PHASE 2 CHANGE: LLM-controlled via engine/elite_agents.py
# ══════════════════════════════════════════════════════════════════════════════

class ChancellorAgent(OfficialAgent):
    """
    Chancellor — Executive Head of Government.
    Article 4.4-4.6. Single term, 5 years, elected by three chambers.

    PHASE 2: This agent is controlled by LangChain LLM via EliteAgentLayer.
    step() does nothing — EliteAgentLayer.step() handles all Chancellor logic
    and writes results to model.shared_data before Mesa agents run.

    Class kept as shell so all imports across the codebase still work.
    _implement_policy() and _command_military_check() preserved for
    reference — called by EliteAgentLayer, not by Mesa step().
    """

    # PHASE 2: Flag read by model._create_agents() to skip scheduler
    PHASE2_LLM_CONTROLLED = True

    def __init__(self, unique_id: int, model, state_id: str, ethnicity: str):
        super().__init__(
            unique_id=unique_id,
            model=model,
            role="chancellor",
            state_id=state_id,
            ethnicity=ethnicity,
            age=random.randint(38, 58)
        )
        self.chamber_service_years_ago = random.randint(
            CONSTITUTION.executive.CHANCELLOR_COOLING_OFF, 20
        )

    def step(self):
        """
        PHASE 2: No-op. LangChain EliteAgentLayer handles Chancellor.
        EliteAgentLayer.step() is called at the top of KaNovaModel.step()
        BEFORE Mesa scheduler runs, writing decisions to shared_data.
        """
        return

    def _implement_policy(self):
        """
        Preserved for reference — logic now executed by EliteAgentLayer.
        EliteAgentLayer writes elite_budget_impact to shared_data which
        downstream loops (E3) consume as the policy implementation signal.
        """
        approved = self.model.shared_data.get("approved_policies", [])
        for policy in approved:
            if not policy.get("implemented", False):
                quality = self.merit_score * 0.60 + random.uniform(0.0, 0.20)
                if self.psych_probation:
                    quality *= (
                        1.0 - CONSTITUTION.psychology.TRAUMA_DISTORTION_RANGE[0]
                    )
                self.model.shared_data["policy_quality"] = max(
                    0.0, min(1.0, quality)
                )
                policy["implemented"] = True

    def _command_military_check(self):
        """
        Preserved for reference — coup signal now handled by EliteAgentLayer.
        Senior General's hidden threshold check writes elite_coup_signal
        to shared_data. KaNovaModel.step() reads it before Mesa runs.
        """
        military_loyalty = self.model.shared_data.get("military_loyalty", 0.60)
        coup_loyalty_threshold = CONSTITUTION.military.COUP_TRIGGER_LOYALTY
        coup_approval_threshold = CONSTITUTION.military.COUP_TRIGGER_APPROVAL

        if (military_loyalty < coup_loyalty_threshold and
                self.approval_rating < coup_approval_threshold):
            self.model.shared_data["coup_risk"] = min(
                1.0,
                self.model.shared_data.get("coup_risk", 0.0) + 0.15
            )


# ══════════════════════════════════════════════════════════════════════════════
# PRESIDENT AGENT
# PHASE 2 CHANGE: LLM-controlled via engine/elite_agents.py
# ══════════════════════════════════════════════════════════════════════════════

class PresidentAgent(OfficialAgent):
    """
    President — Ceremonial Head of State.
    Article 4.1-4.3. Single term, 5 years, directly elected.
    Holds tiebreaker vote only. No executive power.

    PHASE 2: This agent is controlled by LangChain LLM via EliteAgentLayer.
    step() does nothing — EliteAgentLayer handles all President logic.

    cast_tiebreaker_vote() is preserved and still called by chambers.py
    when a deadlock occurs — this is a constitutional mechanic, not a
    deliberation, so it stays here.

    Class kept as shell so all imports still work.
    """

    # PHASE 2: Flag read by model._create_agents() to skip scheduler
    PHASE2_LLM_CONTROLLED = True

    def __init__(self, unique_id: int, model, state_id: str, ethnicity: str):
        super().__init__(
            unique_id=unique_id,
            model=model,
            role="president",
            state_id=state_id,
            ethnicity=ethnicity,
            age=random.randint(45, 65)
        )
        # President has higher trust and lower ambition — ceremonial role
        self.trust_score = min(1.0, self.trust_score + 0.15)
        self.ambition = max(0.0, self.ambition - 0.20)

    def step(self):
        """
        PHASE 2: No-op. LangChain EliteAgentLayer handles President.
        EliteAgentLayer.step() writes elite_president_trust to shared_data
        which P1 trust loop consumes each year.
        """
        return

    def cast_tiebreaker_vote(self, policy: Dict) -> str:
        """
        Cast tiebreaker vote when chambers deadlock.
        Article 5.8 — President's tiebreaker is final.

        PRESERVED in Phase 2 — this is a constitutional mechanic triggered
        by chambers.py on deadlock, not part of annual LLM deliberation.
        Still called directly by ThreeChamberSystem when needed.
        """
        benefit = policy.get("benefit_score", 0.50)
        ethnic_balance = policy.get("ethnic_balance_score", 0.50)

        score = (
            benefit * 0.50 +
            ethnic_balance * 0.30 +
            self.merit_score * 0.20
        )

        vote = "yes" if score > 0.50 else "no"

        self.model.shared_data["tiebreaker_cast"] = {
            "year": self.model.current_year,
            "policy_id": policy.get("id"),
            "vote": vote,
            "president_id": self.unique_id
        }

        return vote


# ══════════════════════════════════════════════════════════════════════════════
# ETHNIC LEADER AGENT — unchanged from Phase 1
# ══════════════════════════════════════════════════════════════════════════════

class EthnicLeaderAgent(OfficialAgent):
    """
    Ethnic Leader Council Member.
    Article 5.3-5.4. Represents one ethnic group.
    Unchanged from Phase 1 — stays in Mesa scheduler.
    """

    def __init__(
        self,
        unique_id: int,
        model,
        ethnicity: str,
        is_youth_representative: bool = False
    ):
        state_map = {
            "Bamar": "bamar_central", "Mon": "bamar_central",
            "Shan": "shan_eastern", "Kayah": "shan_eastern",
            "Karen": "karen_southern", "Rakhine": "karen_southern",
            "Kachin": "kachin_northern", "Chin": "kachin_northern"
        }
        state_id = state_map.get(ethnicity, "bamar_central")

        age = (
            random.randint(25, 39)
            if is_youth_representative
            else random.randint(40, 65)
        )

        super().__init__(
            unique_id=unique_id,
            model=model,
            role="ethnic_leader",
            state_id=state_id,
            ethnicity=ethnicity,
            age=age
        )

        self.is_youth_representative = is_youth_representative
        self.ethnic_group_represented = ethnicity
        self.veto_history: List[Dict] = []
        self.presidential_candidate = False
        self.ethnic_loyalty = min(1.0, self.ethnic_loyalty + 0.20)

    def cast_veto_vote(self, policy: Dict) -> str:
        ethnic_impact = policy.get("ethnic_impact", {}).get(self.ethnicity, 0.0)
        national_benefit = policy.get("benefit_score", 0.50)

        score = (
            ethnic_impact * 0.55 +
            national_benefit * 0.30 +
            self.constitutional_loyalty * 0.15
        )

        vote = "yes" if score > 0.50 else "no"

        self.veto_history.append({
            "policy_id": policy.get("id"),
            "vote": vote,
            "ethnic_impact": ethnic_impact,
            "year": self.model.current_year
        })

        return vote

    def consider_presidential_run(self) -> bool:
        eligible = (
            self.terms_served >= CONSTITUTION.chambers.ETHNIC_PRESIDENTIAL_MIN_TERMS
            and self.ambition > 0.70
            and self.merit_score > 0.65
            and not self.permanently_disqualified
        )

        if eligible and random.random() < 0.10:
            self.presidential_candidate = True
            return True
        return False


# ══════════════════════════════════════════════════════════════════════════════
# ANALYSIS COUNCIL MEMBER — unchanged from Phase 1
# ══════════════════════════════════════════════════════════════════════════════

class AnalysisCouncilMember(OfficialAgent):
    """
    Analysis Council Technocrat.
    Article 5.5-5.6. Merit-appointed, 6-year rotating term.
    Unchanged from Phase 1 — stays in Mesa scheduler.
    """

    def __init__(
        self,
        unique_id: int,
        model,
        state_id: str,
        ethnicity: str,
        expertise: str = "economics"
    ):
        super().__init__(
            unique_id=unique_id,
            model=model,
            role="analysis_council_member",
            state_id=state_id,
            ethnicity=ethnicity,
            age=random.randint(35, 55)
        )

        self.expertise = expertise
        self.evidence_base: List[Dict] = []
        self.methodology_published = False
        self.publish_days_before_veto = (
            CONSTITUTION.safeguards.ANALYSIS_PUBLISH_BEFORE_VETO_DAYS
        )

        if self.merit_score < CONSTITUTION.chambers.ANALYSIS_MERIT_MIN:
            boost = CONSTITUTION.chambers.ANALYSIS_MERIT_MIN - self.merit_score + 0.05
            self.education_level = min(1.0, self.education_level + boost * 0.5)
            self.productivity = min(1.0, self.productivity + boost * 0.3)
            self.merit_score = self._calculate_merit()

    def cast_analysis_vote(self, policy: Dict) -> str:
        evidence_quality = policy.get("evidence_quality", 0.50)
        long_term_benefit = policy.get("long_term_benefit", 0.50)
        risk_score = policy.get("risk_score", 0.50)

        analysis_score = (
            evidence_quality * 0.45 +
            long_term_benefit * 0.35 +
            (1.0 - risk_score) * 0.20
        )

        if analysis_score < 0.70:
            self._publish_methodology(policy, analysis_score)
            return "no"

        return "yes"

    def _publish_methodology(self, policy: Dict, score: float):
        self.methodology_published = True
        self.model.shared_data.setdefault("published_methodologies", []).append({
            "member_id": self.unique_id,
            "policy_id": policy.get("id"),
            "score": score,
            "evidence_base": self.evidence_base,
            "expertise": self.expertise,
            "publish_year": self.model.current_year,
            "veto_eligible_after": (
                self.model.current_year +
                (self.publish_days_before_veto / 365)
            )
        })


# ══════════════════════════════════════════════════════════════════════════════
# OFFICIAL POPULATION FACTORY
# PHASE 2 CHANGE: Chancellor and President NOT added to returned list
# ══════════════════════════════════════════════════════════════════════════════

class OfficialPopulation:
    """Factory for creating the initial official agent population."""

    @staticmethod
    def create_population(model) -> List[OfficialAgent]:
        """
        Create all official agents.

        PHASE 2 CHANGE: ChancellorAgent and PresidentAgent are instantiated
        and stored as model.chancellor_agent and model.president_agent
        for reference (chambers.py uses them for tiebreaker votes etc.)
        but they are NOT added to the returned list, so model._create_agents()
        never adds them to self.schedule.
        Mesa never calls their step() — EliteAgentLayer handles them.

        All other officials returned and added to scheduler as normal.
        """

        officials = []
        agent_id = 10000

        # ── PHASE 2: Instantiate but DO NOT add to officials list ─────────────
        # Stored on model for direct reference by chambers.py, court.py etc.
        president = PresidentAgent(
            unique_id=agent_id,
            model=model,
            state_id="bamar_central",
            ethnicity=random.choice(ETHNIC_GROUPS)
        )
        model.president_agent = president   # accessible as model.president_agent
        agent_id += 1

        chancellor = ChancellorAgent(
            unique_id=agent_id,
            model=model,
            state_id="bamar_central",
            ethnicity=random.choice(ETHNIC_GROUPS)
        )
        model.chancellor_agent = chancellor  # accessible as model.chancellor_agent
        agent_id += 1
        # ── NOT appended to officials — Mesa never steps them ─────────────────

        # ── All agents below: unchanged from Phase 1, added to scheduler ──────

        # Ministers (8)
        for ministry in CONSTITUTION.executive.MINISTRIES:
            state = random.choice(list(CONSTITUTION.simulation.SIMULATION_STATES))
            ethnicity = random.choice(ETHNIC_GROUPS)
            officials.append(OfficialAgent(
                unique_id=agent_id,
                model=model,
                role="minister",
                state_id=state,
                ethnicity=ethnicity,
                ministry=ministry
            ))
            agent_id += 1

        # Ethnic Leaders Council (8)
        ethnic_groups = ETHNIC_GROUPS.copy()
        youth_index = random.randint(0, len(ethnic_groups) - 1)

        for i, ethnicity in enumerate(ethnic_groups):
            is_youth = (i == youth_index)
            officials.append(EthnicLeaderAgent(
                unique_id=agent_id,
                model=model,
                ethnicity=ethnicity,
                is_youth_representative=is_youth
            ))
            agent_id += 1

        # Analysis Council Members (10)
        expertise_areas = [
            "economics", "law", "data_science", "public_health",
            "environmental_science", "military_strategy",
            "ethnic_studies", "technology", "finance", "sociology"
        ]
        for expertise in expertise_areas:
            state = random.choice(list(CONSTITUTION.simulation.SIMULATION_STATES))
            ethnicity = random.choice(ETHNIC_GROUPS)
            officials.append(AnalysisCouncilMember(
                unique_id=agent_id,
                model=model,
                state_id=state,
                ethnicity=ethnicity,
                expertise=expertise
            ))
            agent_id += 1

        # Congress Members (50)
        for _ in range(50):
            state = random.choice(list(CONSTITUTION.simulation.SIMULATION_STATES))
            ethnicity = random.choice(ETHNIC_GROUPS)
            officials.append(OfficialAgent(
                unique_id=agent_id,
                model=model,
                role="congress_member",
                state_id=state,
                ethnicity=ethnicity,
                age=random.randint(28, 60)
            ))
            agent_id += 1

        return officials


# ══════════════════════════════════════════════════════════════════════════════
# QUICK TEST
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":

    print("Testing OfficialAgent Phase 2...")

    class MockSchedule:
        agents = []

    class MockModel:
        def __init__(self):
            self.current_year = 0
            self.schedule = MockSchedule()
            self.states = {
                s: {
                    "corruption_level": 0.72, "employment_rate": 0.58,
                    "trust_index": 0.22, "ethnic_tension": 0.65,
                    "gdp_growth": 0.02, "resource_revenue": 100.0,
                    "gdp": 1000.0, "knowledge_capital": 0.0,
                    "protest_activity": 0.0, "iig_activity": 0.0,
                    "merit_integrity": 0.50
                }
                for s in ["bamar_central", "shan_eastern",
                          "karen_southern", "kachin_northern"]
            }
            self.shared_data = {
                "poverty_line": 1000.0, "tax_revenue": 0.0,
                "shame_register": [], "emigrants": [],
                "bribery_attempts": [], "corruption_reports": [],
                "tax_evasion_detected": [], "phd_graduates": 0,
                "rights_violated": False, "network_protest_rate": 0.0,
                "iig_effectiveness": 0.40, "policy_quality": 0.40,
                "inheritance_pool": 0.0, "federal_dev_fund": 0.0,
                "military_loyalty": 0.60, "coup_risk": 0.0,
                "pending_policies": [], "approved_policies": [],
                "total_ruin_events": 0
            }

    mock = MockModel()

    # Verify PHASE2_LLM_CONTROLLED flag
    print(f"\nPhase 2 LLM flags:")
    print(f"  ChancellorAgent.PHASE2_LLM_CONTROLLED = {ChancellorAgent.PHASE2_LLM_CONTROLLED}")
    print(f"  PresidentAgent.PHASE2_LLM_CONTROLLED  = {PresidentAgent.PHASE2_LLM_CONTROLLED}")

    # Verify step() is no-op
    ch = ChancellorAgent(10001, mock, "bamar_central", "Bamar")
    pr = PresidentAgent(10000, mock, "bamar_central", "Bamar")
    ch.step()
    pr.step()
    print(f"\n  Chancellor step() → no-op ✓")
    print(f"  President step()  → no-op ✓")

    # Verify population factory doesn't add them to list
    officials = OfficialPopulation.create_population(mock)
    roles_in_list = [o.role for o in officials]
    print(f"\nOfficialPopulation.create_population() roles:")
    for role, count in sorted(
        {r: roles_in_list.count(r) for r in set(roles_in_list)}.items()
    ):
        print(f"  {role:30s}: {count}")
    print(f"\n  'chancellor' in list: {'chancellor' in roles_in_list}  ← should be False")
    print(f"  'president'  in list: {'president'  in roles_in_list}  ← should be False")
    print(f"  model.chancellor_agent set: {hasattr(mock, 'chancellor_agent')}  ← should be True")
    print(f"  model.president_agent  set: {hasattr(mock, 'president_agent')}   ← should be True")

    # President tiebreaker still works
    test_policy = {"id": "test_001", "benefit_score": 0.75, "ethnic_balance_score": 0.60}
    tiebreaker_vote = mock.president_agent.cast_tiebreaker_vote(test_policy)
    print(f"\n  President tiebreaker vote: {tiebreaker_vote}  ← still works ✓")

    print("\nofficial.py Phase 2 loaded successfully")