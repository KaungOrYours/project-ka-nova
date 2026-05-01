"""
================================================================================
PROJECT KA-NOVA
institutions/court.py

Constitutional Court System — Institution-Level Mechanics
Ka-Nova Simulation Engine v1.0

The Constitutional Court is the supreme guardian of the Federal Union.
It adjudicates Total Ruin certifications, rights complaints,
methodology challenges, and emergency power requests.

Article 6 — The Constitutional Court
Article 15 — Cryptographic Justice Protocol
Author: Kaung Htet
License: MIT
================================================================================
"""

from __future__ import annotations

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import random
from typing import Dict, List, Optional
from config.constitution import CONSTITUTION


class ConstitutionalCourtSystem:
    """
    Manages Constitutional Court institution-level mechanics.
    Works alongside individual CourtJudge agents.

    Responsibilities:
    - Certify Total Ruin Protocol (8 of 11 supermajority)
    - Strike down rights violations
    - Review Analysis Council methodology challenges
    - Certify emergency powers
    - Oversee IIG operations
    - Manage 10-year constitutional review
    """

    def __init__(self, model):
        self.model = model
        self.total_ruin_certifications = 0
        self.rights_violations_struck = 0
        self.emergency_certifications = 0
        self.methodology_challenges_reviewed = 0
        self.annual_case_log: List[Dict] = []
        self.iig_data_custody: List[Dict] = []

    def annual_session(self, year: int):
        """Run annual court session — process all pending matters."""

        self._process_prosecution_queue()
        self._process_rights_complaints()
        self._process_methodology_challenges()
        self._process_emergency_requests()
        self._maintain_iig_data_custody()

        if year > 0 and year % CONSTITUTION.amendment.REVIEW_INTERVAL == 0:
            self._conduct_constitutional_review(year)

        self._log_annual_activity(year)

    def _process_prosecution_queue(self):
        """
        Certify Total Ruin Protocol for qualifying cases.
        Article 15 — requires 8 of 11 judge supermajority.
        """
        from agents.oversight import CourtJudge

        judges = [a for a in self.model.schedule.agents
                  if isinstance(a, CourtJudge)]

        queue = self.model.shared_data.get("prosecution_queue", [])

        for item in queue:
            if item.get("court_reviewed", False):
                continue

            case = item.get("case", {})
            corruption_score = case.get("corruption_score", 0.0)

            if not item.get("total_ruin_eligible", False):
                item["court_reviewed"] = True
                continue

            # Count votes
            yes_votes = sum(
                1 for j in judges
                if corruption_score > (0.85 * j.independence_score)
            )

            supermajority = CONSTITUTION.crypto_justice.COURT_SUPERMAJORITY_FOR_TOTAL_RUIN

            if yes_votes >= supermajority:
                self._certify_total_ruin(case)

            item["court_reviewed"] = True

    def _certify_total_ruin(self, case: Dict):
        """Execute Total Ruin Protocol certification."""
        from agents.official import OfficialAgent

        target_id = case.get("target_id")
        for agent in self.model.schedule.agents:
            if isinstance(agent, OfficialAgent) and agent.unique_id == target_id:
                if not agent.total_ruin_triggered:
                    agent.trigger_total_ruin()
                    self.total_ruin_certifications += 1
                    self.model.shared_data["total_ruin_events"] = (
                        self.model.shared_data.get("total_ruin_events", 0) + 1
                    )
                break

        self.model.shared_data.setdefault("total_ruin_certified", []).append({
            "case_id": case.get("case_id"),
            "target_id": target_id,
            "year": self.model.current_year,
            "blockchain_recorded": True
        })

    def _process_rights_complaints(self):
        """Strike down any rights violations immediately."""
        complaints = self.model.shared_data.get("rights_complaints", [])
        for complaint in complaints:
            if complaint.get("reviewed", False):
                continue
            violation = complaint.get("type", "")
            if violation in CONSTITUTION.rights.FUNDAMENTAL_RIGHTS:
                complaint["ruling"] = "void_ab_initio"
                self.rights_violations_struck += 1
                self.model.shared_data.setdefault(
                    "iig_rights_investigations", []
                ).append({
                    "complaint_id": complaint.get("id"),
                    "year": self.model.current_year
                })
            complaint["reviewed"] = True

    def _process_methodology_challenges(self):
        """Review citizen challenges to Analysis Council vetoes."""
        challenges = self.model.shared_data.get("methodology_challenges", [])
        for challenge in challenges:
            if challenge.get("reviewed", False):
                continue
            quality = challenge.get("methodology_quality", 0.50)
            strength = challenge.get("challenge_strength", 0.50)
            if strength > quality * 1.20:
                challenge["ruling"] = "methodology_flawed"
                self.model.shared_data.setdefault(
                    "suspended_vetoes", []
                ).append(challenge.get("policy_id"))
            else:
                challenge["ruling"] = "methodology_valid"
            challenge["reviewed"] = True
            self.methodology_challenges_reviewed += 1

    def _process_emergency_requests(self):
        """Certify or reject emergency power declarations."""
        requests = self.model.shared_data.get("emergency_declarations", [])
        for req in requests:
            if req.get("court_certified", False):
                continue
            touches_rights = req.get("touches_rights", False)
            valid_scenario = req.get("scenario") in (
                CONSTITUTION.emergency.TRIGGER_SCENARIOS
            )
            req["court_certified"] = not touches_rights and valid_scenario
            if req["court_certified"]:
                self.emergency_certifications += 1
            req["reviewed"] = True

    def _maintain_iig_data_custody(self):
        """
        Maintain IIG data custody — all evidence held by Court not IIG.
        Article 7.5 — data sovereignty.
        """
        new_evidence = self.model.shared_data.get("court_evidence_custody", [])
        self.iig_data_custody.extend(new_evidence)
        self.model.shared_data["court_evidence_custody"] = []
        self.model.shared_data["total_evidence_in_custody"] = len(self.iig_data_custody)

    def _conduct_constitutional_review(self, year: int):
        """
        10-year mandatory constitutional review.
        Article 12.3 — Citizens Assembly by civic lottery (500 members).
        """
        from agents.citizen import CitizenAgent
        from agents.official import OfficialAgent

        eligible = [
            a for a in self.model.schedule.agents
            if isinstance(a, CitizenAgent) and
            not isinstance(a, OfficialAgent) and
            a.age >= 18 and a.is_alive and not a.has_emigrated
        ]

        assembly_size = min(
            CONSTITUTION.amendment.CITIZENS_ASSEMBLY_SIZE,
            len(eligible)
        )

        if eligible:
            assembly = random.sample(eligible, assembly_size)
            support = sum(1 for a in assembly if a.trust_score > 0.50)
            support_rate = support / assembly_size

            self.model.shared_data["constitutional_review_result"] = {
                "year": year,
                "assembly_size": assembly_size,
                "support_rate": round(support_rate, 4),
                "system_reaffirmed": support_rate > 0.50
            }

    def _log_annual_activity(self, year: int):
        self.annual_case_log.append({
            "year": year,
            "total_ruin_certifications": self.total_ruin_certifications,
            "rights_violations_struck": self.rights_violations_struck,
            "emergency_certifications": self.emergency_certifications,
            "methodology_challenges": self.methodology_challenges_reviewed,
            "evidence_in_custody": len(self.iig_data_custody)
        })

    def get_summary(self) -> Dict:
        return {
            "total_ruin_certifications": self.total_ruin_certifications,
            "rights_violations_struck": self.rights_violations_struck,
            "emergency_certifications": self.emergency_certifications,
            "methodology_challenges_reviewed": self.methodology_challenges_reviewed,
            "evidence_in_custody": len(self.iig_data_custody)
        }


if __name__ == "__main__":
    print("institutions/court.py loaded successfully")
    print(f"Judge count:         {CONSTITUTION.judiciary.JUDGE_COUNT}")
    print(f"Ruling threshold:    {CONSTITUTION.judiciary.RULING_THRESHOLD} of {CONSTITUTION.judiciary.JUDGE_COUNT}")
    print(f"Total Ruin super:    {CONSTITUTION.crypto_justice.COURT_SUPERMAJORITY_FOR_TOTAL_RUIN} of {CONSTITUTION.judiciary.JUDGE_COUNT}")