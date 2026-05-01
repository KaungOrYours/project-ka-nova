"""
================================================================================
PROJECT KA-NOVA
agents/official.py

Official Agent — Government Officials, Ministers, Chancellor, President
Ka-Nova Simulation Engine v1.0

Official agents are citizens who have entered public service.
They inherit all citizen attributes and add:
- Constitutional role with defined powers and constraints
- Merit examination requirement for office
- Corruption decision mechanics
- Term limits and cooling-off periods
- Psychological health screening (Article 18)
- Total Ruin Protocol vulnerability
- Removal mechanics per role

All behavior derives from MFU constitutional parameters.

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
# ROLE DEFINITIONS
# Constitutional roles with powers, constraints, and removal thresholds
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
        "max_terms": 99,  # serves concurrent with chancellor
        "executive_power": True,
        "tiebreaker": False,
        "removal_chambers": 0,  # chancellor removes directly
        "cooling_off": 0
    },
    "congress_member": {
        "merit_min": CONSTITUTION.merit.MERIT_MIN_PUBLIC_OFFICE,
        "term_years": CONSTITUTION.chambers.CONGRESS_TERM,
        "max_terms": 99,  # renewable
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
        "max_terms": 99,  # rotating
        "executive_power": False,
        "tiebreaker": False,
        "removal_chambers": 0,
        "cooling_off": 0
    }
}


# ══════════════════════════════════════════════════════════════════════════════
# BASE OFFICIAL AGENT
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
        # Initialize as citizen first
        archetype = self._assign_archetype_for_role(role)
        super().__init__(
            unique_id=unique_id,
            model=model,
            archetype=archetype,
            state_id=state_id,
            ethnicity=ethnicity,
            age=age
        )

        # ── ROLE ──────────────────────────────────────────────────────────────
        self.role = role
        self.ministry = ministry
        self.role_config = OFFICIAL_ROLES.get(role, OFFICIAL_ROLES["congress_member"])

        # ── MERIT BOOST — officials selected for higher merit ─────────────────
        merit_floor = self.role_config["merit_min"]
        if self.merit_score < merit_floor:
            # Boost to meet minimum — officials are selected for merit
            boost = merit_floor - self.merit_score + random.uniform(0.0, 0.15)
            self.productivity = min(1.0, self.productivity + boost * 0.4)
            self.education_level = min(1.0, self.education_level + boost * 0.3)
            self.performance = min(1.0, self.performance + boost * 0.2)
            self.civic_contribution = min(1.0, self.civic_contribution + boost * 0.1)
            self.merit_score = self._calculate_merit()

        # ── TERM TRACKING ─────────────────────────────────────────────────────
        self.terms_served = 0
        self.term_remaining = self.role_config["term_years"]
        self.max_terms = self.role_config["max_terms"]
        self.year_appointed = None

        # ── CORRUPTION MECHANICS ──────────────────────────────────────────────
        self.corruption_score = self._init_corruption_score()
        self.corruption_opportunities = 0
        self.corruption_acts = 0
        self.bribery_received = 0.0
        self.embezzlement = 0.0
        self.corruption_network = []  # other corrupt officials known to this one

        # ── AMBITION ─────────────────────────────────────────────────────────
        self.ambition = self._init_attr(
            random.uniform(0.30, 0.85), 0.10
        )
        self.loyalty_to_chancellor = random.uniform(0.20, 0.80)
        self.coalition_members: List[int] = []

        # ── PSYCHOLOGICAL HEALTH (Article 18) ─────────────────────────────────
        self.psych_screen_due = True
        self.psych_screen_months = 0        # months since last screen
        self.psych_probation = False
        self.psych_probation_months = 0
        self.consultation_sessions_this_month = 0
        self.psych_attendance_record: List[bool] = []

        # ── DISQUALIFICATION STATUS ───────────────────────────────────────────
        self.permanently_disqualified = False
        self.disqualification_reason = None
        self.total_ruin_triggered = False

        # ── POLICY BEHAVIOR ───────────────────────────────────────────────────
        self.policy_votes: List[Dict] = []
        self.veto_count = 0
        self.approval_rating = random.uniform(0.40, 0.70)

        # ── REMOVAL STATUS ────────────────────────────────────────────────────
        self.no_confidence_votes = 0
        self.removed_mid_term = False
        self.removal_reason = None

        # ── NATIONAL SERVICE — officials must have completed ──────────────────
        self.national_service_completed = True  # prerequisite for office
        self.constitutional_loyalty = min(
            1.0,
            self.constitutional_loyalty + 0.20
        )

    # ══════════════════════════════════════════════════════════════════════════
    # MESA STEP
    # ══════════════════════════════════════════════════════════════════════════

    def step(self):
        """Annual official agent update cycle."""

        if not self.is_alive or self.permanently_disqualified:
            return

        # 1. Perceive environment
        local_env = self._perceive_environment()
        self.memory.append(local_env)

        # 2. Psychological screening check (every 6 months = every 0.5 steps)
        self._psych_screening_update()

        # 3. Corruption decision
        self._decide_corruption(local_env)

        # 4. Policy decisions (vote behavior)
        self._decide_policy_votes(local_env)

        # 5. Coalition building (ambition-driven)
        self._build_coalitions()

        # 6. Update approval rating
        self._update_approval_rating(local_env)

        # 7. Term countdown
        self._update_term()

        # 8. Merit recertification (every 4 years)
        if (self.model.current_year % CONSTITUTION.merit.RECERTIFICATION_INTERVAL == 0
                and self.model.current_year > 0):
            self._merit_recertification()

        # 9. Update adaptive thresholds
        self._update_thresholds(local_env)

        # 10. Life course
        self._life_course_update()

        # 11. Recalculate merit
        self.merit_score = self._calculate_merit()

        # 12. Update grievance
        self._update_grievance(local_env)

        self.years_in_system += 1

    # ══════════════════════════════════════════════════════════════════════════
    # CORRUPTION MECHANICS
    # ══════════════════════════════════════════════════════════════════════════

    def _decide_corruption(self, env: Dict):
        """
        Annual corruption decision for official.

        Factors increasing corruption probability:
        - High ambition + low merit = frustrated entitlement
        - High corruption environment = normalized behavior
        - Low IIG effectiveness = low detection risk
        - Weak loyalty network = no accountability
        - High corruption tolerance (archetype)

        Factors decreasing corruption probability:
        - High constitutional loyalty
        - Known shame register victims in network
        - High IIG effectiveness
        - Low corruption score (track record)
        - Psychological stability
        """

        if self.permanently_disqualified:
            return

        iig_effectiveness = self.model.shared_data.get("iig_effectiveness", 0.50)
        state_corruption = env.get("corruption_level", 0.60)
        shame_deterrent = 0.40 if self.known_shame_register_victim else 0.0

        # Base corruption probability
        corrupt_prob = (
            self.corruption_tolerance * 0.25 +
            self.ambition * 0.20 +
            state_corruption * 0.20 +
            (1.0 - self.constitutional_loyalty) * 0.20 +
            (1.0 - iig_effectiveness) * 0.15
        )

        # Deterrents
        corrupt_prob -= shame_deterrent * 0.30
        corrupt_prob -= self.constitutional_loyalty * 0.15

        # Psychological instability increases corruption risk
        if self.psych_probation:
            corrupt_prob += 0.10

        corrupt_prob = max(0.0, min(1.0, corrupt_prob))

        # Decision
        if random.random() < corrupt_prob:
            self._commit_corruption_act()

    def _commit_corruption_act(self):
        """
        Official commits a corruption act.
        Updates corruption score and logs for IIG detection.
        """

        # Type of corruption based on role
        if self.role in ["chancellor", "minister"]:
            act_type = random.choice([
                "embezzlement",
                "bribery_received",
                "merit_subversion",
                "resource_misappropriation"
            ])
        else:
            act_type = random.choice([
                "bribery_received",
                "vote_selling",
                "nepotism"
            ])

        # Amount
        amount = self.income * random.uniform(0.05, 0.50)

        if act_type == "embezzlement":
            self.embezzlement += amount
        elif act_type == "bribery_received":
            self.bribery_received += amount

        # Update corruption score
        self.corruption_score = min(
            1.0,
            self.corruption_score + random.uniform(0.05, 0.15)
        )
        self.corruption_acts += 1

        # Log for potential IIG detection
        self.model.shared_data.setdefault("corruption_acts_log", []).append({
            "official_id": self.unique_id,
            "role": self.role,
            "state": self.state_id,
            "act_type": act_type,
            "amount": amount,
            "corruption_score": self.corruption_score,
            "year": self.model.current_year
        })

        # Broadcast to corruption network
        self.has_event_to_broadcast = True
        self.broadcast_signal = {
            "type": "corruption_normalized",
            "corruption_score": self.corruption_score,
            "state": self.state_id
        }

    # ══════════════════════════════════════════════════════════════════════════
    # POLICY VOTING
    # ══════════════════════════════════════════════════════════════════════════

    def _decide_policy_votes(self, env: Dict):
        """
        Policy voting decision.
        Based on: merit, loyalty, ethnic interest, public trust.
        """

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

            # Record vote in model
            policy_votes = self.model.shared_data.setdefault(
                "policy_vote_results", {}
            )
            policy_id = policy.get("id", "unknown")
            if policy_id not in policy_votes:
                policy_votes[policy_id] = {"yes": 0, "no": 0, "abstain": 0}
            policy_votes[policy_id][vote] += 1

    def _evaluate_policy(self, policy: Dict, env: Dict) -> str:
        """
        Evaluate a policy and return vote.
        Returns: 'yes', 'no', or 'abstain'
        """

        policy_type = policy.get("type", "general")
        policy_benefit = policy.get("benefit_score", 0.50)
        ethnic_impact = policy.get("ethnic_impact", {}).get(
            self.ethnicity, 0.0
        )

        # Base vote probability
        yes_prob = (
            policy_benefit * 0.40 +
            self.merit_score * 0.20 +
            self.constitutional_loyalty * 0.20 +
            ethnic_impact * 0.20
        )

        # Corruption distorts voting
        if self.corruption_score > 0.50:
            yes_prob += random.uniform(-0.20, 0.20)

        # Analysis Council requires evidence base
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
    # PSYCHOLOGICAL HEALTH SCREENING (Article 18)
    # ══════════════════════════════════════════════════════════════════════════

    def _psych_screening_update(self):
        """
        Biannual psychological screening.
        Article 18 — every 6 months for all public officials.
        """

        self.psych_screen_months += 12  # annual step = 12 months

        screening_interval = CONSTITUTION.psychology.SCREENING_INTERVAL_MONTHS

        if self.psych_screen_months >= screening_interval:
            self.psych_screen_months = 0
            self._conduct_psych_screening()

        # Track probation progress
        if self.psych_probation:
            self.psych_probation_months += 12
            if self.psych_probation_months >= CONSTITUTION.psychology.SEVERE_PROBATION_MONTHS:
                self._complete_probation()

    def _conduct_psych_screening(self):
        """
        Conduct psychological screening with anti-bias protocol.
        Article 18.2 — anonymous review by random Analysis Council psychologist.
        """

        # Calculate psychological health score (0 = healthy, 1 = severe)
        psych_score = (
            self.trauma_score * 0.40 +
            (1.0 - self.resilience) * 0.30 +
            self.grievance * 0.20 +
            (self.corruption_score * 0.10)
        )

        # Anti-bias: anonymized review adds small random variation
        # Simulates independent reviewer without identity knowledge
        review_variation = random.gauss(0, 0.05)
        psych_score = max(0.0, min(1.0, psych_score + review_variation))

        # Determine outcome
        stable_threshold = CONSTITUTION.psychology.OUTCOME_STABLE_THRESHOLD
        severe_threshold = CONSTITUTION.psychology.OUTCOME_SEVERE_THRESHOLD

        if psych_score <= stable_threshold:
            self.psych_status = "stable"
            self.psych_probation = False

        elif psych_score <= severe_threshold:
            self.psych_status = "acceptable"
            # Consultation required — monitored by court (attendance only)
            self.model.shared_data.setdefault(
                "psych_consultation_required", []
            ).append(self.unique_id)

        else:
            self.psych_status = "severe"
            self._begin_psych_probation()

        # Log attendance record (court sees this only)
        self.psych_attendance_record.append(True)

    def _begin_psych_probation(self):
        """
        Begin psychological probation.
        Article 18.4 — peer support, professional treatment, ecotherapy.
        """

        self.psych_probation = True
        self.psych_probation_months = 0

        # Temporary removal from duties if severe
        self.model.shared_data.setdefault(
            "psych_probation_officials", []
        ).append({
            "official_id": self.unique_id,
            "role": self.role,
            "year": self.model.current_year,
            "trauma_category": self.trauma_category
        })

        # Rehabilitation support (Article 18.4)
        # Peer support — reduces isolation
        self.trust_score = min(1.0, self.trust_score + 0.05)

        # Ecotherapy — reduces trauma
        self.trauma_score = max(0.0, self.trauma_score - 0.10)

        # Professional treatment — builds resilience
        self.resilience = min(1.0, self.resilience + 0.08)

    def _complete_probation(self):
        """Complete probation — return to service if fit."""

        self.psych_probation = False
        self.psych_probation_months = 0
        self.psych_status = "stable"

        # Probation does NOT appear on public merit record
        # unless criminal conduct was involved (Article 18.7)

    def stop_treatment(self):
        """
        Official voluntarily stops treatment.
        Article 18.5 — right to stop, but consequence is fixed.
        """

        # Right to stop — but automatic temporary disqualification
        consequence = CONSTITUTION.psychology.STOP_CONSEQUENCE
        if consequence == "automatic_temporary_disqualification":
            self.psych_probation = True
            self.psych_status = "severe"
            self.model.shared_data.setdefault(
                "voluntary_treatment_stop", []
            ).append(self.unique_id)

    # ══════════════════════════════════════════════════════════════════════════
    # MERIT RECERTIFICATION (Article 3.6)
    # ══════════════════════════════════════════════════════════════════════════

    def _merit_recertification(self):
        """
        Every 4 years — merit score recertified.
        Below 0.60 = must vacate within 90 days.
        Results published publicly.
        """

        self.merit_score = self._calculate_merit()

        if self.merit_score < CONSTITUTION.merit.RECERTIFICATION_FAIL_THRESHOLD:
            self._fail_recertification()
        else:
            # Log successful recertification
            self.model.shared_data.setdefault(
                "recertification_passed", []
            ).append({
                "official_id": self.unique_id,
                "role": self.role,
                "merit_score": self.merit_score,
                "year": self.model.current_year
            })

    def _fail_recertification(self):
        """
        Two consecutive failures = permanent disqualification.
        Article 3.5 and 3.6.
        """

        failed_count = self.model.shared_data.setdefault(
            f"recert_fails_{self.unique_id}", 0
        )
        self.model.shared_data[f"recert_fails_{self.unique_id}"] = failed_count + 1

        if failed_count >= 1:
            # Second consecutive failure
            self._permanently_disqualify(
                "two_consecutive_failed_reviews"
            )
        else:
            # First failure — 90 days to improve or vacate
            self.model.shared_data.setdefault(
                "recertification_failed", []
            ).append({
                "official_id": self.unique_id,
                "role": self.role,
                "merit_score": self.merit_score,
                "year": self.model.current_year,
                "vacate_by": self.model.current_year + 1
            })

    # ══════════════════════════════════════════════════════════════════════════
    # DISQUALIFICATION AND REMOVAL
    # ══════════════════════════════════════════════════════════════════════════

    def _permanently_disqualify(self, reason: str):
        """
        Permanent disqualification from all public office.
        Article 3.5 — no appeal, no waiver, no pardon.
        """

        self.permanently_disqualified = True
        self.disqualification_reason = reason

        self.model.shared_data.setdefault(
            "permanently_disqualified", []
        ).append({
            "official_id": self.unique_id,
            "role": self.role,
            "reason": reason,
            "year": self.model.current_year
        })

    def receive_no_confidence_vote(self, chamber: str):
        """
        Receive no-confidence vote from a chamber.
        Chancellor requires 2 of 3 + Presidential signature.
        Article 4.9.
        """

        self.no_confidence_votes += 1

        required = self.role_config.get("removal_chambers", 2)
        requires_president = CONSTITUTION.executive.CHANCELLOR_DISMISSAL_REQUIRES_PRESIDENT

        if self.no_confidence_votes >= required:
            if self.role == "chancellor":
                # Need presidential signature too
                president_signs = self.model.shared_data.get(
                    "president_signs_dismissal", False
                )
                if president_signs or not requires_president:
                    self._remove_from_office("no_confidence")
            else:
                self._remove_from_office("no_confidence")

    def _remove_from_office(self, reason: str):
        """Remove official from their role mid-term."""

        self.removed_mid_term = True
        self.removal_reason = reason

        self.model.shared_data.setdefault(
            "officials_removed", []
        ).append({
            "official_id": self.unique_id,
            "role": self.role,
            "reason": reason,
            "year": self.model.current_year,
            "merit_score": self.merit_score
        })

    # ══════════════════════════════════════════════════════════════════════════
    # TOTAL RUIN PROTOCOL VULNERABILITY (Article 15)
    # ══════════════════════════════════════════════════════════════════════════

    def trigger_total_ruin(self):
        """
        Total Ruin Protocol executed against this official.
        Article 15 — automatic, sequential, irreversible.
        """

        self.total_ruin_triggered = True

        # Step 1 — Assets frozen
        self.savings = 0.0
        self.income = 0.0

        # Step 2-3 — Asset seizure
        seized_amount = self.embezzlement + self.bribery_received + self.savings
        self.model.shared_data["federal_dev_fund"] = (
            self.model.shared_data.get("federal_dev_fund", 0.0) + seized_amount
        )

        # Step 4 — Permanent disqualification
        self._permanently_disqualify("corruption_conviction")

        # Step 5-7 — Shame Register (public, permanent, blockchain)
        self.model.shared_data.setdefault("shame_register", []).append({
            "official_id": self.unique_id,
            "name_hash": hash(self.unique_id),  # anonymized in real system
            "role": self.role,
            "offence": self.disqualification_reason,
            "assets_seized": seized_amount,
            "year": self.model.current_year,
            "permanent": True,
            "blockchain_recorded": True
        })

        # Broadcast shame to all agents — deterrent effect
        self.has_event_to_broadcast = True
        self.broadcast_signal = {
            "type": "shame_register",
            "role": self.role,
            "corruption_score": self.corruption_score,
            "year": self.model.current_year
        }

        # Network effect — nearby officials increase fear of shame
        self.model.shared_data["total_ruin_events"] = (
            self.model.shared_data.get("total_ruin_events", 0) + 1
        )

    # ══════════════════════════════════════════════════════════════════════════
    # COALITION BUILDING
    # ══════════════════════════════════════════════════════════════════════════

    def _build_coalitions(self):
        """
        High-ambition officials build loyalty networks.
        Chancellor capture risk — Safeguard 1.
        """

        if self.ambition < 0.60:
            return

        # Find other officials with compatible interests
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
    # APPROVAL RATING
    # ══════════════════════════════════════════════════════════════════════════

    def _update_approval_rating(self, env: Dict):
        """
        Approval rating — affected by performance, corruption, policy outcomes.
        Used in president removal trigger (Article 4.3).
        """

        trust = env.get("trust_index", 0.40)
        employment = env.get("employment_rate", 0.58)

        performance_factor = (
            self.merit_score * 0.35 +
            trust * 0.35 +
            employment * 0.30
        )

        # Corruption reduces approval
        if self.corruption_score > 0.40:
            performance_factor -= self.corruption_score * 0.30

        # Smooth update
        self.approval_rating = (
            self.approval_rating * 0.70 +
            performance_factor * 0.30
        )
        self.approval_rating = max(0.0, min(1.0, self.approval_rating))

        # Update model shared data for president removal check
        if self.role == "president":
            self.model.shared_data["president_approval"] = self.approval_rating

    # ══════════════════════════════════════════════════════════════════════════
    # TERM MANAGEMENT
    # ══════════════════════════════════════════════════════════════════════════

    def _update_term(self):
        """Track term remaining. Trigger replacement when term expires."""

        self.term_remaining -= 1

        if self.term_remaining <= 0:
            self.terms_served += 1

            if self.terms_served >= self.max_terms:
                # Term limit reached — cannot serve again in this role
                self._complete_term()
            else:
                # Can serve another term — reset
                self.term_remaining = self.role_config["term_years"]
                self.no_confidence_votes = 0

    def _complete_term(self):
        """Complete final term — signal model to replace this official."""

        self.model.shared_data.setdefault(
            "officials_term_complete", []
        ).append({
            "official_id": self.unique_id,
            "role": self.role,
            "terms_served": self.terms_served,
            "year": self.model.current_year,
            "merit_score": self.merit_score,
            "approval_rating": self.approval_rating
        })

    # ══════════════════════════════════════════════════════════════════════════
    # INITIALIZATION HELPERS
    # ══════════════════════════════════════════════════════════════════════════

    def _init_corruption_score(self) -> float:
        """
        Initial corruption score based on archetype.
        High ambition + low constitutional loyalty = higher starting score.
        """

        base = self.corruption_tolerance * 0.30 + random.uniform(0.0, 0.15)
        return max(0.0, min(0.50, base))  # starts below investigation threshold

    @staticmethod
    def _assign_archetype_for_role(role: str) -> str:
        """
        Officials are more likely to be ambitious meritocrats or civic champions.
        Distribution weighted toward higher-merit archetypes.
        """

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
    # STATE REPORTING
    # ══════════════════════════════════════════════════════════════════════════

    def get_state_dict(self) -> Dict:
        """Return official state for KPI tracking."""
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
# SPECIALIZED ROLE SUBCLASSES
# ══════════════════════════════════════════════════════════════════════════════

class ChancellorAgent(OfficialAgent):
    """
    Chancellor — Executive Head of Government.
    Article 4.4-4.6. Single term, 5 years, elected by three chambers.
    Cannot have served in chambers within 5 years (Safeguard 1).
    """

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
            CONSTITUTION.executive.CHANCELLOR_COOLING_OFF,
            20
        )

    def step(self):
        super().step()
        self._implement_policy()
        self._command_military_check()

    def _implement_policy(self):
        """Chancellor implements approved policies."""
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
        Monitor military loyalty.
        Coup trigger check — Article 9.4 and ROE Article 17.
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


class PresidentAgent(OfficialAgent):
    """
    President — Ceremonial Head of State.
    Article 4.1-4.3. Single term, 5 years, directly elected.
    Holds tiebreaker vote only. No executive power.
    """

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

    def cast_tiebreaker_vote(self, policy: Dict) -> str:
        """
        Cast tiebreaker vote when chambers deadlock.
        Article 5.8 — President's tiebreaker is final.
        """

        # President evaluates based on national interest not partisanship
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


class EthnicLeaderAgent(OfficialAgent):
    """
    Ethnic Leader Council Member.
    Article 5.3-5.4. Represents one ethnic group.
    No bloodline relationships with other council members.
    At least one member per group must be under 40.
    """

    def __init__(
        self,
        unique_id: int,
        model,
        ethnicity: str,
        is_youth_representative: bool = False
    ):
        # Ethnic leaders represent their home state
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

        # Ethnic leaders have stronger ethnic loyalty
        self.ethnic_loyalty = min(1.0, self.ethnic_loyalty + 0.20)

    def cast_veto_vote(self, policy: Dict) -> str:
        """
        Cast vote on national policy.
        Ethnic leaders prioritize ethnic group interests.
        Article 5.7 — simple majority required.
        """

        ethnic_impact = policy.get(
            "ethnic_impact", {}
        ).get(self.ethnicity, 0.0)

        national_benefit = policy.get("benefit_score", 0.50)

        # Weighted toward ethnic group impact
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
        """
        After minimum 1 term, ethnic leader may run for President.
        Article 5.4b.
        """

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


class AnalysisCouncilMember(OfficialAgent):
    """
    Analysis Council Technocrat.
    Article 5.5-5.6. Merit-appointed, 6-year rotating term.
    Unanimous vote required (1.00 threshold).
    Must publish methodology 14 days before any veto.
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

        # Analysis Council requires highest merit minimum
        if self.merit_score < CONSTITUTION.chambers.ANALYSIS_MERIT_MIN:
            boost = CONSTITUTION.chambers.ANALYSIS_MERIT_MIN - self.merit_score + 0.05
            self.education_level = min(1.0, self.education_level + boost * 0.5)
            self.productivity = min(1.0, self.productivity + boost * 0.3)
            self.merit_score = self._calculate_merit()

    def cast_analysis_vote(self, policy: Dict) -> str:
        """
        Evidence-based vote — unanimity required for policy to pass.
        Article 5.6 — must publish methodology 14 days before veto.
        Safeguard 5 — transparency mandate.
        """

        evidence_quality = policy.get("evidence_quality", 0.50)
        long_term_benefit = policy.get("long_term_benefit", 0.50)
        risk_score = policy.get("risk_score", 0.50)

        # Pure evidence-based evaluation — no ethnic or political weighting
        analysis_score = (
            evidence_quality * 0.45 +
            long_term_benefit * 0.35 +
            (1.0 - risk_score) * 0.20
        )

        # Unanimous required — one dissenting member blocks
        if analysis_score < 0.70:
            # Would vote no — publish methodology first
            self._publish_methodology(policy, analysis_score)
            return "no"

        return "yes"

    def _publish_methodology(self, policy: Dict, score: float):
        """
        Publish evidence base and methodology before exercising veto.
        Safeguard 5 — citizens can challenge before Constitutional Court.
        """

        self.methodology_published = True
        self.model.shared_data.setdefault(
            "published_methodologies", []
        ).append({
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
# ══════════════════════════════════════════════════════════════════════════════

class OfficialPopulation:
    """Factory for creating the initial official agent population."""

    @staticmethod
    def create_population(model) -> List[OfficialAgent]:
        """
        Create all official agents with correct constitutional composition.
        """

        officials = []
        agent_id = 10000  # start after citizen IDs

        # President (1)
        officials.append(PresidentAgent(
            unique_id=agent_id,
            model=model,
            state_id="bamar_central",
            ethnicity=random.choice(ETHNIC_GROUPS)
        ))
        agent_id += 1

        # Chancellor (1)
        officials.append(ChancellorAgent(
            unique_id=agent_id,
            model=model,
            state_id="bamar_central",
            ethnicity=random.choice(ETHNIC_GROUPS)
        ))
        agent_id += 1

        # Ministers (8 — one per pillar)
        for ministry in CONSTITUTION.executive.MINISTRIES:
            state = random.choice(
                list(CONSTITUTION.simulation.SIMULATION_STATES)
            )
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

        # Ethnic Leaders Council (8 — one per ethnic group)
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
            state = random.choice(
                list(CONSTITUTION.simulation.SIMULATION_STATES)
            )
            ethnicity = random.choice(ETHNIC_GROUPS)
            officials.append(AnalysisCouncilMember(
                unique_id=agent_id,
                model=model,
                state_id=state,
                ethnicity=ethnicity,
                expertise=expertise
            ))
            agent_id += 1

        # Congress Members (variable — simplified to 50)
        for _ in range(50):
            state = random.choice(
                list(CONSTITUTION.simulation.SIMULATION_STATES)
            )
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

    print("Testing OfficialAgent...")

    class MockModel:
        def __init__(self):
            self.current_year = 0
            self.states = {
                s: {
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
                for s in ["bamar_central", "shan_eastern",
                          "karen_southern", "kachin_northern"]
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
                "inheritance_pool": 0.0,
                "federal_dev_fund": 0.0,
                "military_loyalty": 0.60,
                "coup_risk": 0.0,
                "pending_policies": [],
                "approved_policies": [],
                "total_ruin_events": 0
            }

        class schedule:
            agents = []

    mock = MockModel()

    # Test each role
    print("\nRole creation test:")
    roles = [
        ("chancellor", ChancellorAgent),
        ("president", PresidentAgent),
    ]

    for role_name, cls in roles:
        agent = cls(
            unique_id=0,
            model=mock,
            state_id="bamar_central",
            ethnicity="Bamar"
        )
        print(f"  {role_name:30s} | merit={agent.merit_score:.3f} | "
              f"corruption={agent.corruption_score:.3f} | "
              f"approval={agent.approval_rating:.3f}")

    # Test ethnic leader
    print("\nEthnic Leader test:")
    for ethnicity in ETHNIC_GROUPS[:4]:
        leader = EthnicLeaderAgent(
            unique_id=0,
            model=mock,
            ethnicity=ethnicity,
            is_youth_representative=False
        )
        print(f"  {ethnicity:10s} | merit={leader.merit_score:.3f} | "
              f"ethnic_loyalty={leader.ethnic_loyalty:.3f}")

    # Test Analysis Council
    print("\nAnalysis Council test:")
    analyst = AnalysisCouncilMember(
        unique_id=0,
        model=mock,
        state_id="bamar_central",
        ethnicity="Bamar",
        expertise="economics"
    )
    print(f"  Analyst | merit={analyst.merit_score:.3f} | "
          f"min required={CONSTITUTION.chambers.ANALYSIS_MERIT_MIN}")

    # Test population factory
    print("\nPopulation factory test:")
    officials = OfficialPopulation.create_population(mock)
    role_dist = {}
    for o in officials:
        role_dist[o.role] = role_dist.get(o.role, 0) + 1
    for role, count in sorted(role_dist.items()):
        print(f"  {role:30s}: {count}")

    # Test Total Ruin
    print("\nTotal Ruin Protocol test:")
    corrupt_official = ChancellorAgent(0, mock, "bamar_central", "Bamar")
    corrupt_official.corruption_score = 0.90
    corrupt_official.embezzlement = 50000.0
    corrupt_official.trigger_total_ruin()
    print(f"  Permanently disqualified: {corrupt_official.permanently_disqualified}")
    print(f"  Shame register entries:   {len(mock.shared_data['shame_register'])}")
    print(f"  Federal dev fund:         {mock.shared_data['federal_dev_fund']:.2f}")

    print("\nofficial.py loaded successfully")