"""
================================================================================
PROJECT KA-NOVA
institutions/chambers.py

Three Veto Chambers — Congress, Ethnic Leaders Council, Analysis Council
Ka-Nova Simulation Engine v1.0

The three chambers are the legislative heart of MFU.
All major policy must pass all three simultaneously.
This module manages chamber-level voting mechanics,
deadlock detection, and constitutional review scheduling.

Article 5 — The Three Veto Chambers
Author: Kaung Htet
License: MIT
================================================================================
"""

from __future__ import annotations

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import random
from typing import Dict, List, Optional, Tuple
from config.constitution import CONSTITUTION


class Policy:
    """Represents a policy proposal moving through the three chambers."""

    def __init__(self, policy_id: str, policy_type: str, benefit_score: float,
                 ethnic_impact: Dict = None, evidence_quality: float = 0.50,
                 long_term_benefit: float = 0.50, risk_score: float = 0.30):
        self.id = policy_id
        self.type = policy_type
        self.benefit_score = benefit_score
        self.ethnic_impact = ethnic_impact or {}
        self.evidence_quality = evidence_quality
        self.long_term_benefit = long_term_benefit
        self.risk_score = risk_score
        self.ethnic_balance_score = self._calc_ethnic_balance()

        # Voting state
        self.congress_votes = {"yes": 0, "no": 0, "abstain": 0}
        self.ethnic_votes = {"yes": 0, "no": 0, "abstain": 0}
        self.analysis_votes = {"yes": 0, "no": 0, "abstain": 0}
        self.voted = False
        self.passed = False
        self.implemented = False
        self.veto_time_days = 0

    def _calc_ethnic_balance(self) -> float:
        if not self.ethnic_impact:
            return 0.50
        impacts = list(self.ethnic_impact.values())
        return sum(impacts) / len(impacts) if impacts else 0.50


class ThreeChamberSystem:
    """
    Manages the three-chamber veto system.
    Article 5 — Congress, Ethnic Leaders Council, Analysis Council.

    All three must approve for policy to pass.
    Deadlock → President tiebreaker.
    Analysis Council has 90-day veto time limit.
    """

    def __init__(self, model):
        self.model = model
        self.pending_policies: List[Policy] = []
        self.passed_policies: List[Policy] = []
        self.failed_policies: List[Policy] = []
        self.deadlock_count = 0
        self.tiebreaker_count = 0
        self.veto_count = {
            "congress": 0,
            "ethnic": 0,
            "analysis": 0
        }

    def submit_policy(self, policy: Policy):
        """Submit a policy for three-chamber review."""
        self.pending_policies.append(policy)
        self.model.shared_data.setdefault("pending_policies", []).append({
            "id": policy.id,
            "type": policy.type,
            "benefit_score": policy.benefit_score,
            "ethnic_impact": policy.ethnic_impact,
            "evidence_quality": policy.evidence_quality,
            "long_term_benefit": policy.long_term_benefit,
            "risk_score": policy.risk_score,
            "ethnic_balance_score": policy.ethnic_balance_score,
            "voted": False
        })

    def process_votes(self, year: int):
        """Process all pending policy votes for this year."""

        from agents.official import OfficialAgent, AnalysisCouncilMember
        from agents.official import EthnicLeaderAgent

        congress_members = [
            a for a in self.model.schedule.agents
            if isinstance(a, OfficialAgent) and a.role == "congress_member"
        ]
        ethnic_leaders = [
            a for a in self.model.schedule.agents
            if isinstance(a, EthnicLeaderAgent)
        ]
        analysis_members = [
            a for a in self.model.schedule.agents
            if isinstance(a, AnalysisCouncilMember)
        ]

        for policy in self.pending_policies[:]:
            if policy.voted:
                continue

            # Congress vote
            congress_result = self._tally_chamber(
                congress_members, policy, "congress"
            )

            # Ethnic Leaders Council vote
            ethnic_result = self._tally_chamber(
                ethnic_leaders, policy, "ethnic"
            )

            # Analysis Council vote (0.75 qualified supermajority + Citizens Assembly)
            analysis_result = self._tally_analysis(
                analysis_members, policy
            )

            # Policy passes only if all three approve
            all_pass = (
                congress_result >= CONSTITUTION.chambers.CONGRESS_THRESHOLD and
                ethnic_result >= CONSTITUTION.chambers.ETHNIC_THRESHOLD and
                analysis_result >= CONSTITUTION.chambers.ANALYSIS_THRESHOLD
            )

            policy.voted = True
            policy.passed = all_pass

            if all_pass:
                self.passed_policies.append(policy)
                self.model.shared_data.setdefault("approved_policies", []).append({
                    "id": policy.id,
                    "implemented": False,
                    "benefit_score": policy.benefit_score
                })
            else:
                self.failed_policies.append(policy)
                if congress_result < CONSTITUTION.chambers.CONGRESS_THRESHOLD:
                    self.veto_count["congress"] += 1
                if ethnic_result < CONSTITUTION.chambers.ETHNIC_THRESHOLD:
                    self.veto_count["ethnic"] += 1
                if analysis_result < CONSTITUTION.chambers.ANALYSIS_THRESHOLD:
                    self.veto_count["analysis"] += 1

            self.pending_policies.remove(policy)

        # Check for deadlock
        self._check_deadlock()

    def _tally_chamber(self, members: List, policy: Policy,
                       chamber: str) -> float:
        """Tally votes for Congress or Ethnic Council."""
        if not members:
            return 0.0

        yes_votes = 0
        for member in members:
            if hasattr(member, "cast_veto_vote"):
                vote = member.cast_veto_vote({"id": policy.id,
                    "benefit_score": policy.benefit_score,
                    "ethnic_impact": policy.ethnic_impact,
                    "ethnic_balance_score": policy.ethnic_balance_score})
            else:
                vote = member._evaluate_policy(
                    {"id": policy.id, "benefit_score": policy.benefit_score,
                     "ethnic_impact": policy.ethnic_impact}, {}
                )
            if vote == "yes":
                yes_votes += 1

        return yes_votes / len(members)

    def _tally_analysis(self, members: List, policy: Policy) -> float:
        """
        Analysis Council vote — 0.75 qualified supermajority required (v7).
        Article 5.7 — 75% qualified supermajority threshold.
        Safeguard 5 — methodology published 14 days before veto.
        """
        if not members:
            return 1.0  # no council = passes by default

        yes_votes = 0
        for member in members:
            if hasattr(member, "cast_analysis_vote"):
                vote = member.cast_analysis_vote({
                    "id": policy.id,
                    "evidence_quality": policy.evidence_quality,
                    "long_term_benefit": policy.long_term_benefit,
                    "risk_score": policy.risk_score
                })
            else:
                score = (policy.evidence_quality * 0.50 +
                         policy.long_term_benefit * 0.30 +
                         (1.0 - policy.risk_score) * 0.20)
                vote = "yes" if score >= 0.70 else "no"

            if vote == "yes":
                yes_votes += 1

        ratio = yes_votes / len(members) if members else 1.0

        if ratio < CONSTITUTION.chambers.ANALYSIS_THRESHOLD:
            # Analysis Council vetoed — Citizens Assembly must confirm at 51%
            policy.veto_time_days += 365
            if policy.veto_time_days >= CONSTITUTION.chambers.ANALYSIS_VETO_TIME_LIMIT:
                # Time limit expired — escalate to Constitutional Court
                self.model.shared_data.setdefault(
                    "analysis_veto_escalations", []
                ).append({"policy_id": policy.id,
                          "year": self.model.current_year})
                return 0.0

            # Citizens Assembly confirmation vote
            assembly_result = self._citizens_assembly_veto_confirmation(policy)
            if assembly_result >= 0.51:
                # Assembly confirms veto — policy blocked
                self.model.shared_data.setdefault(
                    "citizens_assembly_vetoes", []
                ).append({
                    "policy_id": policy.id,
                    "year": self.model.current_year,
                    "assembly_support": assembly_result,
                    "analysis_ratio": ratio
                })
                return 0.0
            else:
                # Assembly rejects veto — policy passes
                self.model.shared_data.setdefault(
                    "citizens_assembly_overrides", []
                ).append({
                    "policy_id": policy.id,
                    "year": self.model.current_year,
                    "assembly_support": assembly_result,
                    "analysis_ratio": ratio
                })
                return 1.0

        return ratio  # qualified supermajority passed

    def _citizens_assembly_veto_confirmation(self, policy: Policy) -> float:
        """
        Citizens Assembly veto confirmation.
        MFU Constitution v7 — 320 randomly sampled Mesa citizen agents vote
        on whether to confirm the Analysis Council veto at 51% threshold.

        Citizens vote based on trust, grievance, and policy benefit score.
        Emergence — real Mesa agents deciding, not statistical approximation.
        """
        from agents.citizen import CitizenAgent

        all_citizens = [
            a for a in self.model.schedule.agents
            if isinstance(a, CitizenAgent)
        ]

        if not all_citizens:
            return 0.0

        # Randomly sample 320 citizens (v7 canonical)
        assembly_size = CONSTITUTION.simulation.CITIZENS_ASSEMBLY_SIZE  # 320
        sample = random.sample(all_citizens, min(assembly_size, len(all_citizens)))

        yes_votes = 0
        for citizen in sample:
            trust = getattr(citizen, "trust", 0.50)
            grievance = getattr(citizen, "grievance", 0.30)
            # Higher grievance + lower trust = more likely to confirm veto
            veto_support = (grievance * 0.60) + ((1.0 - trust) * 0.40)
            # Direct policy benefit reduces veto support
            veto_support -= policy.benefit_score * 0.30
            if veto_support > 0.50:
                yes_votes += 1

        result = yes_votes / len(sample)

        # Log to shared_data for KPI tracking
        self.model.shared_data["last_assembly_vote"] = {
            "policy_id": policy.id,
            "year": self.model.current_year,
            "sample_size": len(sample),
            "veto_support": result
        }

        return result

    def _check_deadlock(self):
        """
        Check for engineered deadlocks.
        Article 5.8b — 3+ deadlocks per session triggers Court review.
        """
        if self.deadlock_count >= 3:
            self.model.shared_data["deadlock_review_triggered"] = True
            self.model.shared_data.setdefault(
                "methodology_challenges", []
            ).append({
                "type": "engineered_deadlock",
                "year": self.model.current_year,
                "methodology_quality": 0.40,
                "challenge_strength": 0.70
            })
            self.deadlock_count = 0

    def generate_annual_policy(self, year: int):
        """Generate one policy proposal per year for chambers to vote on."""
        policy = Policy(
            policy_id=f"POL_{year}_{random.randint(1000, 9999)}",
            policy_type=random.choice([
                "major_legislation", "national_budget",
                "administrative_orders", "economic_policy"
            ]),
            benefit_score=random.uniform(0.30, 0.85),
            ethnic_impact={
                "Bamar": random.uniform(0.30, 0.80),
                "Shan": random.uniform(0.30, 0.80),
                "Karen": random.uniform(0.30, 0.80),
                "Kachin": random.uniform(0.30, 0.80)
            },
            evidence_quality=random.uniform(0.40, 0.90),
            long_term_benefit=random.uniform(0.35, 0.85),
            risk_score=random.uniform(0.10, 0.60)
        )
        self.submit_policy(policy)
        return policy

    def get_summary(self) -> Dict:
        return {
            "passed_policies": len(self.passed_policies),
            "failed_policies": len(self.failed_policies),
            "pending_policies": len(self.pending_policies),
            "veto_count": self.veto_count,
            "deadlock_count": self.deadlock_count,
            "tiebreaker_count": self.tiebreaker_count
        }


if __name__ == "__main__":
    print("institutions/chambers.py loaded successfully")
    print(f"Congress threshold:  {CONSTITUTION.chambers.CONGRESS_THRESHOLD}")
    print(f"Ethnic threshold:    {CONSTITUTION.chambers.ETHNIC_THRESHOLD}")
    print(f"Analysis threshold:  {CONSTITUTION.chambers.ANALYSIS_THRESHOLD}")
    print(f"Veto time limit:     {CONSTITUTION.chambers.ANALYSIS_VETO_TIME_LIMIT} days")