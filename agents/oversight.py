"""
================================================================================
PROJECT KA-NOVA
agents/oversight.py

Oversight Agents — IIG, Constitutional Court, Arbitration Court
Ka-Nova Simulation Engine v1.0

Oversight agents are the accountability layer of the Federal Union.
They do not govern — they watch, investigate, and adjudicate.

Includes:
- IIGAgent: field investigators, forensic accountants, cybersecurity
- IIGDirector: leads the Sentinel, appointed by Constitutional Court
- CourtJudge: Constitutional Court — elected by people, 10-year term
- ArbitrationJudge: Federal Arbitration Court — mixed appointed/elected

Key constitutional constraints:
- IIG reports to Constitutional Court ONLY (Article 7.2)
- IIG agents cannot enter chambers ever (Article 7.9)
- Data held by Court not IIG (Article 7.5)
- Partnership Council votes on major decisions (Article 7.10)
- Court judges serve single 10-year term (Article 6.2)
- Unanimous Analysis Council can be challenged in Court (Safeguard 5)

Author: Kaung Htet
License: MIT
================================================================================
"""

from __future__ import annotations

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import random
import hashlib
from typing import Optional, Dict, List
from mesa import Agent

from config.constitution import CONSTITUTION
from agents.citizen import CitizenAgent, ETHNIC_GROUPS


# ══════════════════════════════════════════════════════════════════════════════
# IIG AGENT
# ══════════════════════════════════════════════════════════════════════════════

class IIGAgent(CitizenAgent):
    """
    Independent Intelligence Group Field Agent.

    Article 7 — The Sentinel.
    Entry: NS completion + IIG Academy (27 months) + merit 0.85+
           + top 1% civil service + psych test + background check.

    Key constraints:
    - Cannot enter any chamber ever (permanent — Article 7.9)
    - Data held by Constitutional Court not IIG (Article 7.5)
    - Reports to Court only (Article 7.2)
    - Following orders defense inadmissible (Article 17 core)
    - Partnership Council votes open/close investigations (Article 7.10)
    """

    def __init__(
        self,
        unique_id: int,
        model,
        division: str,
        state_id: str,
        ethnicity: str,
        years_of_service: int = 0
    ):
        super().__init__(
            unique_id=unique_id,
            model=model,
            archetype="civic_champion",  # IIG agents screened for civic loyalty
            state_id=state_id,
            ethnicity=ethnicity,
            age=random.randint(
                CONSTITUTION.iig.ENTRY_MIN_AGE,
                CONSTITUTION.iig.ENTRY_MIN_AGE + 20
            )
        )

        # ── IIG IDENTITY ──────────────────────────────────────────────────────
        self.division = division
        self.years_of_service = years_of_service
        self.is_partner = years_of_service >= CONSTITUTION.iig.PARTNER_ELIGIBILITY_YEARS

        # ── MERIT ENFORCEMENT — IIG entry requires 0.85+ ──────────────────────
        merit_min = CONSTITUTION.iig.ENTRY_MERIT_MIN
        if self.merit_score < merit_min:
            boost = merit_min - self.merit_score + 0.02
            self.productivity = min(1.0, self.productivity + boost * 0.4)
            self.education_level = min(1.0, self.education_level + boost * 0.4)
            self.performance = min(1.0, self.performance + boost * 0.2)
            self.merit_score = self._calculate_merit()

        # ── INTEGRITY ────────────────────────────────────────────────────────
        self.integrity_score = random.uniform(0.82, 0.98)
        self.corruption_tolerance = max(0.0, self.corruption_tolerance - 0.40)
        self.constitutional_loyalty = min(1.0, self.constitutional_loyalty + 0.35)

        # ── INVESTIGATION MECHANICS ───────────────────────────────────────────
        self.active_cases: List[Dict] = []
        self.completed_cases: List[Dict] = []
        self.evidence_collected: List[Dict] = []
        self.caseload = 0
        self.cases_solved = 0
        self.cases_opened = 0
        self.false_positives = 0

        # ── PARTNER STATUS ────────────────────────────────────────────────────
        self.partner_votes: List[Dict] = []
        self.vote_weight = self._calculate_vote_weight()

        # ── CONSTITUTIONAL CONSTRAINTS ────────────────────────────────────────
        self.chamber_eligible = False           # PERMANENT — Article 7.9
        self.chamber_eligible_post_service = False  # PERMANENT
        self.reports_to = "constitutional_court_only"
        self.data_custody = "constitutional_court"  # NOT self

        # ── NATIONAL SERVICE ──────────────────────────────────────────────────
        self.national_service_completed = True  # prerequisite

        # ── POST SERVICE TRACKING ────────────────────────────────────────────
        self.permitted_post_service = CONSTITUTION.iig.PERMITTED_POST_SERVICE

    # ══════════════════════════════════════════════════════════════════════════
    # MESA STEP
    # ══════════════════════════════════════════════════════════════════════════

    def step(self):
        """Annual IIG agent update."""

        if not self.is_alive:
            return

        # 1. Scan for corruption above investigation threshold
        self._scan_for_corruption()

        # 2. Progress active cases
        self._progress_active_cases()

        # 3. Partner Council vote participation
        if self.is_partner:
            self._participate_in_partner_votes()

        # 4. Annual merit update
        self.merit_score = self._calculate_merit()
        self.years_of_service += 1

        # 5. Partner eligibility update
        self.is_partner = (
            self.years_of_service >= CONSTITUTION.iig.PARTNER_ELIGIBILITY_YEARS
        )
        self.vote_weight = self._calculate_vote_weight()

        self.years_in_system += 1

    # ══════════════════════════════════════════════════════════════════════════
    # INVESTIGATION
    # ══════════════════════════════════════════════════════════════════════════

    def _scan_for_corruption(self):
        """
        Scan officials in assigned state for corruption above threshold.
        Article 7.4 — investigation triggers automatically at 0.70.
        IIG does not choose who to investigate — threshold is constitutional.
        """

        trigger = CONSTITUTION.iig.INVESTIGATION_TRIGGER
        corruption_log = self.model.shared_data.get("corruption_acts_log", [])

        for act in corruption_log:
            if act.get("investigated", False):
                continue
            if act.get("state") != self.state_id:
                continue
            if act.get("corruption_score", 0.0) < trigger:
                continue

            # Check if Partnership Council has approved opening investigation
            if self._request_investigation_approval(act):
                self._open_investigation(act)
                act["investigated"] = True

    def _request_investigation_approval(self, act: Dict) -> bool:
        """
        Partnership Council must vote to open formal investigation.
        Article 7.10 — simple majority required.
        Simulated here as probabilistic based on evidence strength.
        """

        evidence_strength = act.get("corruption_score", 0.0)
        threshold = CONSTITUTION.iig.OPEN_INVESTIGATION_THRESHOLD

        # Partners vote based on evidence quality
        partners = self._get_partners()
        if not partners:
            return evidence_strength > threshold

        yes_votes = sum(
            1 for p in partners
            if (p.integrity_score * evidence_strength) > threshold
        )

        approval = yes_votes / len(partners) >= threshold
        return approval

    def _open_investigation(self, act: Dict):
        """
        Open formal investigation.
        Assign functional division agents to case.
        """

        case = {
            "case_id": f"CASE_{self.model.current_year}_{act['official_id']}",
            "target_id": act["official_id"],
            "target_role": act.get("role", "unknown"),
            "act_type": act.get("act_type", "corruption"),
            "corruption_score": act.get("corruption_score", 0.0),
            "evidence": [],
            "year_opened": self.model.current_year,
            "status": "active",
            "assigned_division": self.division,
            "investigating_agent": self.unique_id,
            "blockchain_logged": True,
            "zkp_verified": False,
            "all_signatures_obtained": False
        }

        self.active_cases.append(case)
        self.cases_opened += 1
        self.caseload += 1

        # Log investigation opened
        self.model.shared_data.setdefault(
            "active_investigations", []
        ).append(case)

    def _progress_active_cases(self):
        """
        Progress active investigations.
        Collect evidence, build blockchain record, prepare for prosecution.
        """

        completed = []

        for case in self.active_cases:
            # Collect evidence this year
            evidence = self._collect_evidence(case)
            case["evidence"].append(evidence)

            # Check if evidence sufficient for prosecution
            total_evidence = sum(
                e.get("strength", 0.0) for e in case["evidence"]
            )

            if total_evidence > 2.0:  # sufficient after multiple years
                self._prepare_prosecution(case)
                completed.append(case)

        # Move completed cases
        for case in completed:
            self.active_cases.remove(case)
            self.completed_cases.append(case)
            self.caseload -= 1
            self.cases_solved += 1

    def _collect_evidence(self, case: Dict) -> Dict:
        """
        Collect evidence based on division specialization.
        Article 7.5 — data stored at Constitutional Court, not IIG.
        Layer 1 — Blockchain evidence ledger (Article 15).
        """

        division_strength = {
            "forensic_accounting": random.uniform(0.30, 0.70),
            "cybersecurity": random.uniform(0.25, 0.65),
            "field_investigation": random.uniform(0.20, 0.60),
            "corruption_division": random.uniform(0.25, 0.65),
            "resource_sabotage_division": random.uniform(0.20, 0.60),
            "merit_subversion_division": random.uniform(0.15, 0.55),
            "intelligence_division": random.uniform(0.10, 0.40),
            "investigation_division": random.uniform(0.25, 0.65),
            "prosecution_preparation_division": random.uniform(0.30, 0.70)
        }

        strength = division_strength.get(
            self.division, random.uniform(0.20, 0.50)
        ) * self.integrity_score

        evidence = {
            "evidence_id": f"EV_{self.unique_id}_{self.model.current_year}",
            "case_id": case["case_id"],
            "collecting_agent": self.unique_id,
            "division": self.division,
            "strength": strength,
            "year_collected": self.model.current_year,
            "blockchain_hash": self._generate_hash(case["case_id"]),
            "timestamp": self.model.current_year,
            "admissible": True,  # on blockchain ledger = admissible
            "custody": "constitutional_court"  # Article 7.5
        }

        # Store at Constitutional Court — not IIG
        self.model.shared_data.setdefault(
            "court_evidence_custody", []
        ).append(evidence)

        return evidence

    def _prepare_prosecution(self, case: Dict):
        """
        Prepare evidence package for Constitutional Court prosecutors.
        Article 7.6 — IIG does not prosecute, only hands over.
        Article 15 — Zero-knowledge proof verification.
        Layer 3 — Multi-party digital signatures.
        """

        # Verify zero-knowledge proof (simplified)
        case["zkp_verified"] = case["corruption_score"] > 0.70

        # Check if Total Ruin threshold met
        total_ruin_eligible = (
            case["corruption_score"] > 0.85 and
            case["zkp_verified"] and
            len(case["evidence"]) >= 2
        )

        case["total_ruin_eligible"] = total_ruin_eligible
        case["status"] = "prosecution_ready"

        # Hand over to Court prosecutors
        self.model.shared_data.setdefault(
            "prosecution_queue", []
        ).append({
            "case": case,
            "handed_over_year": self.model.current_year,
            "iig_agent": self.unique_id,
            "total_ruin_eligible": total_ruin_eligible
        })

    # ══════════════════════════════════════════════════════════════════════════
    # PARTNERSHIP COUNCIL
    # ══════════════════════════════════════════════════════════════════════════

    def _participate_in_partner_votes(self):
        """
        Senior agents (5+ years) vote on major decisions.
        Article 7.10 — partnership model.
        """

        pending_votes = self.model.shared_data.get(
            "iig_partner_votes_pending", []
        )

        for vote_item in pending_votes:
            if vote_item.get("voted_by", {}).get(self.unique_id):
                continue

            my_vote = self._cast_partner_vote(vote_item)

            vote_item.setdefault("voted_by", {})[self.unique_id] = my_vote
            vote_item.setdefault("yes_weight", 0.0)
            vote_item.setdefault("total_weight", 0.0)

            if my_vote == "yes":
                vote_item["yes_weight"] += self.vote_weight
            vote_item["total_weight"] += self.vote_weight

    def _cast_partner_vote(self, vote_item: Dict) -> str:
        """
        Cast vote in Partnership Council.
        Evidence quality drives the decision.
        """

        vote_type = vote_item.get("type", "open_investigation")
        evidence_score = vote_item.get("evidence_score", 0.0)

        if vote_type == "open_investigation":
            threshold = CONSTITUTION.iig.OPEN_INVESTIGATION_THRESHOLD
        elif vote_type == "proceed_prosecution":
            threshold = CONSTITUTION.iig.PROCEED_PROSECUTION_THRESHOLD
        else:
            threshold = 0.51

        decision_score = evidence_score * self.integrity_score
        return "yes" if decision_score >= threshold else "no"

    def _get_partners(self) -> List[IIGAgent]:
        """Get all partner-eligible IIG agents from model."""
        return [
            a for a in self.model.schedule.agents
            if isinstance(a, IIGAgent) and a.is_partner
        ]

    def _calculate_vote_weight(self) -> float:
        """
        Vote weight based on role.
        Director: tiebreaker only.
        Division Head: 1.5x.
        Regular partner: 1.0x.
        """

        if self.years_of_service > 15:
            return 1.5  # senior partner — division head level
        return 1.0

    @staticmethod
    def _generate_hash(data: str) -> str:
        """Generate blockchain hash for evidence record."""
        return hashlib.sha256(data.encode()).hexdigest()[:16]

    def get_state_dict(self) -> Dict:
        """Return IIG agent state for KPI tracking."""
        base = super().get_state_dict()
        base.update({
            "agent_type": "iig",
            "division": self.division,
            "years_of_service": self.years_of_service,
            "is_partner": self.is_partner,
            "integrity_score": round(self.integrity_score, 4),
            "caseload": self.caseload,
            "cases_opened": self.cases_opened,
            "cases_solved": self.cases_solved,
            "chamber_eligible": self.chamber_eligible,
            "active_cases_count": len(self.active_cases),
            "completed_cases_count": len(self.completed_cases)
        })
        return base

    def __repr__(self) -> str:
        return (
            f"IIGAgent(id={self.unique_id}, "
            f"division={self.division}, "
            f"service={self.years_of_service}yrs, "
            f"partner={self.is_partner}, "
            f"cases={self.caseload})"
        )


# ══════════════════════════════════════════════════════════════════════════════
# IIG DIRECTOR
# ══════════════════════════════════════════════════════════════════════════════

class IIGDirector(IIGAgent):
    """
    IIG Director — appointed by Constitutional Court.
    Article 7.3 — 6-year single non-renewable term.
    Chairs Partnership Council — tiebreaker vote only.
    Outlasts Chancellor and President by design.
    """

    def __init__(self, unique_id: int, model, state_id: str, ethnicity: str):
        super().__init__(
            unique_id=unique_id,
            model=model,
            division="investigation_division",
            state_id=state_id,
            ethnicity=ethnicity,
            years_of_service=random.randint(5, 15)  # promoted from within
        )

        self.term_remaining = CONSTITUTION.iig.DIRECTOR_TERM
        self.term_renewable = CONSTITUTION.iig.DIRECTOR_RENEWABLE  # False
        self.appointed_by = "constitutional_court"
        self.is_partner = True
        self.vote_weight = 0.0  # tiebreaker only — not regular vote

        # Director has highest integrity requirement
        self.integrity_score = min(1.0, self.integrity_score + 0.05)

    def step(self):
        """Director annual update."""
        super().step()
        self._oversee_all_divisions()
        self._term_update()

    def _oversee_all_divisions(self):
        """
        Director oversees all nine divisions.
        Cannot unilaterally open or close investigations — must go through
        Partnership Council vote.
        """

        total_cases = sum(
            len(a.active_cases)
            for a in self.model.schedule.agents
            if isinstance(a, IIGAgent)
        )

        self.model.shared_data["iig_total_active_cases"] = total_cases
        self.model.shared_data["iig_director_id"] = self.unique_id

        # IIG effectiveness metric
        all_iig = [
            a for a in self.model.schedule.agents
            if isinstance(a, IIGAgent)
        ]
        if all_iig:
            total_solved = sum(a.cases_solved for a in all_iig)
            total_opened = sum(a.cases_opened for a in all_iig) or 1
            effectiveness = total_solved / total_opened
            self.model.shared_data["iig_effectiveness"] = min(1.0, effectiveness)

    def cast_tiebreaker_vote(self, vote_item: Dict) -> str:
        """
        Director casts tiebreaker only when Partnership Council is tied.
        Article 7.10 — director chairs but holds tiebreaker vote only.
        """

        yes_weight = vote_item.get("yes_weight", 0.0)
        total_weight = vote_item.get("total_weight", 1.0)
        ratio = yes_weight / total_weight

        # Tiebreaker — only called when exactly 50/50
        if abs(ratio - 0.50) < 0.05:
            evidence_score = vote_item.get("evidence_score", 0.0)
            return "yes" if evidence_score > 0.65 else "no"
        return "abstain"

    def _term_update(self):
        """Track director term. Cannot be renewed."""
        self.term_remaining -= 1
        if self.term_remaining <= 0:
            self.model.shared_data["iig_director_term_complete"] = {
                "director_id": self.unique_id,
                "year": self.model.current_year,
                "cases_solved": self.cases_solved
            }

    def __repr__(self) -> str:
        return (
            f"IIGDirector(id={self.unique_id}, "
            f"term_remaining={self.term_remaining}, "
            f"effectiveness={self.model.shared_data.get('iig_effectiveness', 0):.3f})"
        )


# ══════════════════════════════════════════════════════════════════════════════
# CONSTITUTIONAL COURT JUDGE
# ══════════════════════════════════════════════════════════════════════════════

class CourtJudge(CitizenAgent):
    """
    Constitutional Court Judge.
    Article 6 — elected by the people, 10-year single term.
    11 judges total — odd number prevents ties.
    Ruling threshold: 6 of 11 majority.

    The most stable institution in Ka-Nova.
    Judges outlast every elected official by design.
    They provide institutional memory across two presidential cycles.
    """

    def __init__(
        self,
        unique_id: int,
        model,
        state_id: str,
        ethnicity: str,
        judge_number: int  # 1-11
    ):
        super().__init__(
            unique_id=unique_id,
            model=model,
            archetype="civic_champion",
            state_id=state_id,
            ethnicity=ethnicity,
            age=random.randint(45, 62)
        )

        # ── JUDICIAL IDENTITY ─────────────────────────────────────────────────
        self.judge_number = judge_number
        self.term_remaining = CONSTITUTION.judiciary.JUDGE_TERM
        self.max_terms = CONSTITUTION.judiciary.JUDGE_MAX_TERMS
        self.terms_served = 0

        # ── INDEPENDENCE ──────────────────────────────────────────────────────
        self.independence_score = random.uniform(0.75, 0.98)
        self.corruption_tolerance = max(0.0, self.corruption_tolerance - 0.50)
        self.constitutional_loyalty = min(1.0, self.constitutional_loyalty + 0.40)

        # ── JUDICIAL RECORD ───────────────────────────────────────────────────
        self.cases_adjudicated: List[Dict] = []
        self.total_ruin_certified: int = 0
        self.rights_violations_ruled: int = 0
        self.policy_vetoes_reviewed: int = 0
        self.emergency_certifications: int = 0
        self.removal_attempts_blocked: int = 0

        # ── BUDGET — constitutionally fixed ───────────────────────────────────
        self.budget_protected = CONSTITUTION.judiciary.BUDGET_FIXED
        self.political_interference = False

        # ── REMOVAL THRESHOLD — hardest in system ─────────────────────────────
        # Requires: 2 chambers + President + Chancellor
        self.removal_votes_chambers = 0
        self.removal_president_sign = False
        self.removal_chancellor_sign = False

    # ══════════════════════════════════════════════════════════════════════════
    # MESA STEP
    # ══════════════════════════════════════════════════════════════════════════

    def step(self):
        """Annual judge update."""

        if not self.is_alive:
            return

        # 1. Review prosecution queue — certify Total Ruin
        self._review_prosecution_queue()

        # 2. Review policy challenges (Safeguard 5)
        self._review_methodology_challenges()

        # 3. Review rights violation complaints
        self._review_rights_complaints()

        # 4. Emergency power certification
        self._review_emergency_requests()

        # 5. Term update
        self._term_update()

        # 6. Independence drift — very slow natural drift
        self._update_independence()

        self.years_in_system += 1

    # ══════════════════════════════════════════════════════════════════════════
    # ADJUDICATION
    # ══════════════════════════════════════════════════════════════════════════

    def _review_prosecution_queue(self):
        """
        Review IIG prosecution packages.
        Article 15 — certify Total Ruin Protocol when conditions met.
        Requires 8 of 11 judge supermajority for Total Ruin.
        """

        queue = self.model.shared_data.get("prosecution_queue", [])

        for item in queue:
            if item.get("court_reviewed", False):
                continue

            case = item.get("case", {})
            total_ruin_eligible = item.get("total_ruin_eligible", False)

            if total_ruin_eligible:
                # Check all Total Ruin trigger conditions (Article 15)
                conditions_met = self._check_total_ruin_conditions(case)

                if conditions_met:
                    # Count judge votes across all court judges
                    court_votes = self._count_court_votes_for_total_ruin(case)

                    supermajority = CONSTITUTION.crypto_justice.COURT_SUPERMAJORITY_FOR_TOTAL_RUIN
                    if court_votes >= supermajority:
                        self._certify_total_ruin(case)
                        self.total_ruin_certified += 1

            item["court_reviewed"] = True

            self.cases_adjudicated.append({
                "case_id": case.get("case_id"),
                "year": self.model.current_year,
                "total_ruin": total_ruin_eligible,
                "judge_id": self.unique_id
            })

    def _check_total_ruin_conditions(self, case: Dict) -> bool:
        """
        Verify all six Total Ruin trigger conditions.
        Article 15 — ALL must be true simultaneously.
        """

        conditions = [
            case.get("corruption_score", 0.0) > 0.85,
            len(case.get("evidence", [])) > 0,
            case.get("zkp_verified", False),
            case.get("status") == "prosecution_ready",
            True,  # appeal window — simplified as always expired for test
            True   # signatures — simplified, verified by court
        ]

        return all(conditions)

    def _count_court_votes_for_total_ruin(self, case: Dict) -> int:
        """
        Count how many of 11 judges would vote yes for Total Ruin.
        Each judge evaluates independently.
        """

        all_judges = [
            a for a in self.model.schedule.agents
            if isinstance(a, CourtJudge)
        ]

        if not all_judges:
            return 0

        yes_votes = 0
        for judge in all_judges:
            evidence_strength = case.get("corruption_score", 0.0)
            judge_threshold = 0.85 * judge.independence_score
            if evidence_strength > judge_threshold:
                yes_votes += 1

        return yes_votes

    def _certify_total_ruin(self, case: Dict):
        """
        Certify Total Ruin Protocol — triggers automatic execution.
        Article 15 — sequential 7-step consequence.
        """

        target_id = case.get("target_id")

        # Find and execute against target official
        for agent in self.model.schedule.agents:
            from agents.official import OfficialAgent
            if (isinstance(agent, OfficialAgent) and
                    agent.unique_id == target_id):
                agent.trigger_total_ruin()
                break

        self.model.shared_data.setdefault(
            "total_ruin_certified", []
        ).append({
            "case_id": case.get("case_id"),
            "target_id": target_id,
            "certifying_judge": self.unique_id,
            "year": self.model.current_year,
            "blockchain_recorded": True
        })

    def _review_methodology_challenges(self):
        """
        Review citizen challenges to Analysis Council methodology.
        Safeguard 5 — citizens can challenge before Constitutional Court.
        """

        challenges = self.model.shared_data.get(
            "methodology_challenges", []
        )

        for challenge in challenges:
            if challenge.get("reviewed", False):
                continue

            methodology_score = challenge.get("methodology_quality", 0.50)
            challenge_merit = challenge.get("challenge_strength", 0.50)

            # Judge evaluates if methodology was flawed
            if challenge_merit > methodology_score * 1.20:
                # Methodology flawed — veto suspended
                challenge["ruling"] = "methodology_flawed_veto_suspended"
                self.model.shared_data.setdefault(
                    "suspended_vetoes", []
                ).append(challenge.get("policy_id"))
            else:
                challenge["ruling"] = "methodology_valid"

            challenge["reviewed"] = True
            self.policy_vetoes_reviewed += 1

    def _review_rights_complaints(self):
        """
        Review citizen complaints about rights violations.
        Article 2.4 — all six rights are absolute.
        Any rights violation is void ab initio.
        """

        complaints = self.model.shared_data.get("rights_complaints", [])

        for complaint in complaints:
            if complaint.get("reviewed", False):
                continue

            violation_type = complaint.get("type")
            is_fundamental = violation_type in CONSTITUTION.rights.FUNDAMENTAL_RIGHTS

            if is_fundamental:
                # Rights violation — strike down immediately
                complaint["ruling"] = "rights_violation_void_ab_initio"
                self.rights_violations_ruled += 1

                # Trigger IIG investigation of violating authority
                self.model.shared_data.setdefault(
                    "iig_rights_investigations", []
                ).append({
                    "complaint_id": complaint.get("id"),
                    "violating_authority": complaint.get("authority"),
                    "year": self.model.current_year
                })

            complaint["reviewed"] = True

    def _review_emergency_requests(self):
        """
        Certify State of Emergency declarations.
        Article 16 — rights remain untouched during emergency.
        Court certifies emergency does not violate constitutional constraints.
        """

        emergency_requests = self.model.shared_data.get(
            "emergency_declarations", []
        )

        for request in emergency_requests:
            if request.get("court_certified", False):
                continue

            # Verify emergency does not touch fundamental rights
            touches_rights = request.get("touches_rights", False)
            valid_scenario = request.get("scenario") in (
                CONSTITUTION.emergency.TRIGGER_SCENARIOS
            )

            if not touches_rights and valid_scenario:
                request["court_certified"] = True
                self.emergency_certifications += 1
            else:
                request["court_certified"] = False
                request["court_rejection_reason"] = "touches_rights_or_invalid_scenario"

    def _term_update(self):
        """10-year single term. Cannot be renewed."""
        self.term_remaining -= 1
        if self.term_remaining <= 0:
            self.model.shared_data.setdefault(
                "judge_terms_complete", []
            ).append({
                "judge_id": self.unique_id,
                "judge_number": self.judge_number,
                "year": self.model.current_year,
                "cases_adjudicated": len(self.cases_adjudicated),
                "total_ruin_certified": self.total_ruin_certified
            })

    def _update_independence(self):
        """
        Very slow natural drift in judicial independence.
        Political pressure resistance — protected by budget guarantee.
        """

        # Political pressure occasionally attempts to influence
        political_pressure = self.model.shared_data.get(
            "judicial_pressure", 0.0
        )

        if political_pressure > 0.50:
            # Resist pressure — independence drifts slightly
            drift = political_pressure * 0.02 * (1.0 - self.independence_score)
            self.independence_score = max(
                0.60,
                self.independence_score - drift
            )
            self.removal_attempts_blocked += 1

    def get_state_dict(self) -> Dict:
        """Return judge state for KPI tracking."""
        base = super().get_state_dict()
        base.update({
            "agent_type": "court_judge",
            "judge_number": self.judge_number,
            "independence_score": round(self.independence_score, 4),
            "term_remaining": self.term_remaining,
            "cases_adjudicated": len(self.cases_adjudicated),
            "total_ruin_certified": self.total_ruin_certified,
            "rights_violations_ruled": self.rights_violations_ruled,
            "emergency_certifications": self.emergency_certifications
        })
        return base

    def __repr__(self) -> str:
        return (
            f"CourtJudge(id={self.unique_id}, "
            f"judge={self.judge_number}, "
            f"independence={self.independence_score:.3f}, "
            f"term_remaining={self.term_remaining})"
        )


# ══════════════════════════════════════════════════════════════════════════════
# ARBITRATION JUDGE
# ══════════════════════════════════════════════════════════════════════════════

class ArbitrationJudge(CitizenAgent):
    """
    Federal Arbitration Court Judge.
    Article 6.8 — handles all federal civil disputes.
    Mixed composition: half elected by state legislatures, half merit-appointed.
    Appeals escalate to Constitutional Court.
    """

    def __init__(
        self,
        unique_id: int,
        model,
        state_id: str,
        ethnicity: str,
        appointment_type: str  # elected or merit_appointed
    ):
        super().__init__(
            unique_id=unique_id,
            model=model,
            archetype="ambitious_meritocrat",
            state_id=state_id,
            ethnicity=ethnicity,
            age=random.randint(40, 60)
        )

        self.appointment_type = appointment_type
        self.specialization = random.choice([
            "interstate_disputes",
            "investor_state",
            "commercial_disputes"
        ])
        self.cases_resolved: List[Dict] = []
        self.cases_appealed: int = 0
        self.independence_score = random.uniform(0.65, 0.90)

    def step(self):
        """Annual arbitration judge update."""

        if not self.is_alive:
            return

        self._resolve_disputes()
        self.years_in_system += 1

    def _resolve_disputes(self):
        """
        Resolve pending federal civil disputes.
        Article 6.8 — jurisdiction over interstate, investor-state, commercial.
        """

        disputes = self.model.shared_data.get("pending_disputes", [])

        for dispute in disputes:
            if dispute.get("resolved", False):
                continue
            if dispute.get("type") != self.specialization:
                continue

            # Resolve based on merit and evidence
            resolution = self._evaluate_dispute(dispute)
            dispute["resolved"] = True
            dispute["resolution"] = resolution
            dispute["arbitrator_id"] = self.unique_id

            self.cases_resolved.append(dispute)

            # Check if resolution will be appealed
            loser_satisfaction = resolution.get("loser_satisfaction", 0.50)
            if loser_satisfaction < 0.30:
                self.cases_appealed += 1
                self.model.shared_data.setdefault(
                    "constitutional_court_appeals", []
                ).append({
                    "original_case": dispute,
                    "arbitrator_id": self.unique_id,
                    "year": self.model.current_year
                })

    def _evaluate_dispute(self, dispute: Dict) -> Dict:
        """Evaluate and resolve a federal dispute."""

        claimant_strength = dispute.get("claimant_strength", 0.50)
        respondent_strength = dispute.get("respondent_strength", 0.50)

        # Independence affects impartiality
        impartiality = self.independence_score
        noise = random.gauss(0, 0.05)

        adjusted_claimant = claimant_strength * impartiality + noise
        adjusted_respondent = respondent_strength * impartiality - noise

        if adjusted_claimant > adjusted_respondent:
            winner = "claimant"
            loser_satisfaction = adjusted_respondent
        else:
            winner = "respondent"
            loser_satisfaction = adjusted_claimant

        return {
            "winner": winner,
            "loser_satisfaction": loser_satisfaction,
            "year": self.model.current_year
        }

    def __repr__(self) -> str:
        return (
            f"ArbitrationJudge(id={self.unique_id}, "
            f"type={self.appointment_type}, "
            f"spec={self.specialization}, "
            f"cases={len(self.cases_resolved)})"
        )


# ══════════════════════════════════════════════════════════════════════════════
# OVERSIGHT POPULATION FACTORY
# ══════════════════════════════════════════════════════════════════════════════

class OversightPopulation:
    """Factory for creating all oversight agent populations."""

    @staticmethod
    def create_population(model) -> List:
        """
        Create all oversight agents.
        IIG (50), Constitutional Court (11), Arbitration Court (10).
        """

        oversight = []
        agent_id = 20000  # start after official IDs

        # IIG Director (1)
        director = IIGDirector(
            unique_id=agent_id,
            model=model,
            state_id="bamar_central",
            ethnicity=random.choice(ETHNIC_GROUPS)
        )
        oversight.append(director)
        agent_id += 1

        # IIG Agents (49 — distributed across nine divisions)
        all_divisions = (
            list(CONSTITUTION.iig.FUNCTIONAL_DIVISIONS) +
            list(CONSTITUTION.iig.MANDATE_DIVISIONS) +
            list(CONSTITUTION.iig.OPERATIONAL_DIVISIONS)
        )

        states = list(CONSTITUTION.simulation.SIMULATION_STATES)

        for i in range(49):
            division = all_divisions[i % len(all_divisions)]
            state = random.choice(states)
            ethnicity = random.choice(ETHNIC_GROUPS)
            years = random.randint(0, 12)

            agent = IIGAgent(
                unique_id=agent_id,
                model=model,
                division=division,
                state_id=state,
                ethnicity=ethnicity,
                years_of_service=years
            )
            oversight.append(agent)
            agent_id += 1

        # Constitutional Court — 11 judges (Article 6.1)
        judge_count = CONSTITUTION.judiciary.JUDGE_COUNT
        ethnic_distribution = ETHNIC_GROUPS[:judge_count]

        for i in range(judge_count):
            ethnicity = ethnic_distribution[i % len(ethnic_distribution)]
            state = random.choice(states)

            judge = CourtJudge(
                unique_id=agent_id,
                model=model,
                state_id=state,
                ethnicity=ethnicity,
                judge_number=i + 1
            )
            # Stagger terms so not all expire at once
            judge.term_remaining = random.randint(1, 10)
            oversight.append(judge)
            agent_id += 1

        # Federal Arbitration Court — 10 judges (Article 6.8)
        for i in range(10):
            appointment_type = (
                "elected" if i < 5 else "merit_appointed"
            )
            state = random.choice(states)
            ethnicity = random.choice(ETHNIC_GROUPS)

            judge = ArbitrationJudge(
                unique_id=agent_id,
                model=model,
                state_id=state,
                ethnicity=ethnicity,
                appointment_type=appointment_type
            )
            oversight.append(judge)
            agent_id += 1

        return oversight


# ══════════════════════════════════════════════════════════════════════════════
# QUICK TEST
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":

    print("Testing Oversight Agents...")

    class MockSchedule:
        def __init__(self):
            self.agents = []

    class MockModel:
        def __init__(self):
            self.current_year = 0
            self.schedule = MockSchedule()
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
                "total_ruin_events": 0,
                "corruption_acts_log": [],
                "prosecution_queue": [],
                "active_investigations": [],
                "court_evidence_custody": [],
                "iig_partner_votes_pending": [],
                "pending_disputes": [],
                "rights_complaints": [],
                "emergency_declarations": [],
                "methodology_challenges": [],
                "iig_total_active_cases": 0,
                "judicial_pressure": 0.0
            }

    mock = MockModel()

    # Test IIG Agent
    print("\nIIG Agent test:")
    iig = IIGAgent(
        unique_id=0,
        model=mock,
        division="forensic_accounting",
        state_id="bamar_central",
        ethnicity="Bamar",
        years_of_service=3
    )
    print(f"  IIG Agent: {iig}")
    print(f"  Chamber eligible: {iig.chamber_eligible}")
    print(f"  Reports to: {iig.reports_to}")
    print(f"  Merit: {iig.merit_score:.3f} (min required: {CONSTITUTION.iig.ENTRY_MERIT_MIN})")
    print(f"  Integrity: {iig.integrity_score:.3f}")

    # Test IIG Director
    print("\nIIG Director test:")
    director = IIGDirector(
        unique_id=1,
        model=mock,
        state_id="bamar_central",
        ethnicity="Shan"
    )
    print(f"  Director: {director}")
    print(f"  Term remaining: {director.term_remaining}")
    print(f"  Vote weight (tiebreaker only): {director.vote_weight}")

    # Test Court Judge
    print("\nConstitutional Court Judge test:")
    for i in range(1, 4):
        judge = CourtJudge(
            unique_id=i + 100,
            model=mock,
            state_id="bamar_central",
            ethnicity=ETHNIC_GROUPS[i],
            judge_number=i
        )
        mock.schedule.agents.append(judge)
        print(f"  Judge {i}: independence={judge.independence_score:.3f}, "
              f"term={judge.term_remaining}")

    # Test Total Ruin certification
    print("\nTotal Ruin certification test:")
    test_case = {
        "case_id": "CASE_TEST_001",
        "target_id": 999,
        "corruption_score": 0.90,
        "evidence": [{"strength": 1.5}, {"strength": 1.2}],
        "zkp_verified": True,
        "status": "prosecution_ready"
    }
    mock.shared_data["prosecution_queue"].append({
        "case": test_case,
        "total_ruin_eligible": True,
        "court_reviewed": False,
        "handed_over_year": 0
    })

    judge_test = mock.schedule.agents[0]
    conditions = judge_test._check_total_ruin_conditions(test_case)
    votes = judge_test._count_court_votes_for_total_ruin(test_case)
    print(f"  Conditions met: {conditions}")
    print(f"  Court votes for Total Ruin: {votes} of {CONSTITUTION.judiciary.JUDGE_COUNT}")
    print(f"  Supermajority required: {CONSTITUTION.crypto_justice.COURT_SUPERMAJORITY_FOR_TOTAL_RUIN}")

    # Test Arbitration Judge
    print("\nArbitration Judge test:")
    arb = ArbitrationJudge(
        unique_id=200,
        model=mock,
        state_id="shan_eastern",
        ethnicity="Shan",
        appointment_type="merit_appointed"
    )
    print(f"  {arb}")

    # Test population factory
    print("\nOversight Population factory test:")
    oversight = OversightPopulation.create_population(mock)
    type_dist = {}
    for a in oversight:
        t = type(a).__name__
        type_dist[t] = type_dist.get(t, 0) + 1
    for t, count in sorted(type_dist.items()):
        print(f"  {t:30s}: {count}")

    print(f"\nTotal oversight agents: {len(oversight)}")
    print("\noversight.py loaded successfully")