"""
================================================================================
PROJECT KA-NOVA
institutions/iig.py

Independent Intelligence Group — Institution-Level Mechanics
Ka-Nova Simulation Engine v1.0

The IIG is the Sentinel of the Federal Union.
This module manages institution-level IIG mechanics:
- Partnership Council voting
- Nine-division coordination
- Investigation pipeline management
- Data custody enforcement
- Post-service restriction tracking

Article 7 — The Independent Intelligence Group
Article 7.10 — Partnership Model
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


class PartnershipCouncil:
    """
    IIG Partnership Council — senior agents vote on major decisions.
    Article 7.10 — partner model like a law firm.

    Open investigation:    simple majority (0.51)
    Proceed to prosecution: 2/3 majority (0.67)
    Budget decisions:      2/3 majority
    Director recommendation: 2/3 majority
    Quorum:                60% of all partners must vote
    """

    def __init__(self, model):
        self.model = model
        self.vote_history: List[Dict] = []

    def get_partners(self) -> list:
        """Get all senior IIG agents eligible to vote."""
        from agents.oversight import IIGAgent
        return [
            a for a in self.model.schedule.agents
            if isinstance(a, IIGAgent) and a.is_partner
        ]

    def vote(self, motion_type: str, motion_data: Dict) -> bool:
        """
        Conduct a partnership vote.
        Returns True if motion passes, False otherwise.
        """
        partners = self.get_partners()

        if not partners:
            return True  # no partners yet — auto pass

        # Check quorum
        quorum_required = max(
            1,
            int(len(partners) * CONSTITUTION.iig.PARTNERSHIP_COUNCIL_QUORUM)
        )

        # Simulate voting
        voting_partners = random.sample(
            partners, min(len(partners), max(quorum_required, len(partners)))
        )

        if len(voting_partners) < quorum_required:
            return False  # no quorum

        # Threshold by motion type
        thresholds = {
            "open_investigation": CONSTITUTION.iig.OPEN_INVESTIGATION_THRESHOLD,
            "proceed_prosecution": CONSTITUTION.iig.PROCEED_PROSECUTION_THRESHOLD,
            "budget": CONSTITUTION.iig.PROCEED_PROSECUTION_THRESHOLD,
            "director_recommendation": CONSTITUTION.iig.PROCEED_PROSECUTION_THRESHOLD
        }
        threshold = thresholds.get(motion_type, 0.51)

        yes_weight = sum(
            p.vote_weight for p in voting_partners
            if self._agent_votes_yes(p, motion_data)
        )
        total_weight = sum(p.vote_weight for p in voting_partners)

        ratio = yes_weight / max(0.001, total_weight)
        passed = ratio >= threshold

        self.vote_history.append({
            "motion_type": motion_type,
            "year": self.model.current_year,
            "partners_voting": len(voting_partners),
            "yes_ratio": round(ratio, 4),
            "threshold": threshold,
            "passed": passed
        })

        return passed

    def _agent_votes_yes(self, agent, motion_data: Dict) -> bool:
        """Agent votes yes based on evidence quality and integrity."""
        evidence_score = motion_data.get("evidence_score", 0.50)
        return (evidence_score * agent.integrity_score) > 0.50


class IIGSystem:
    """
    IIG Institution-Level System.
    Coordinates all nine divisions and manages investigation pipeline.
    """

    def __init__(self, model):
        self.model = model
        self.partnership_council = PartnershipCouncil(model)

        # Nine divisions
        self.divisions = {
            # Functional
            "forensic_accounting": [],
            "cybersecurity": [],
            "field_investigation": [],
            # Mandate
            "corruption_division": [],
            "resource_sabotage_division": [],
            "merit_subversion_division": [],
            # Operational
            "intelligence_division": [],
            "investigation_division": [],
            "prosecution_preparation_division": []
        }

        self.total_cases_opened = 0
        self.total_cases_solved = 0
        self.total_prosecutions = 0
        self.post_service_registry: List[int] = []  # former IIG agents

    def annual_operations(self, year: int):
        """Run annual IIG operations."""

        self._assign_agents_to_divisions()
        self._process_tip_pipeline()
        self._enforce_post_service_restrictions()
        self._update_effectiveness()

    def _assign_agents_to_divisions(self):
        """Assign IIG agents to their divisions."""
        from agents.oversight import IIGAgent, IIGDirector

        for division in self.divisions:
            self.divisions[division] = []

        for agent in self.model.schedule.agents:
            if isinstance(agent, IIGAgent) and not isinstance(agent, IIGDirector):
                div = agent.division
                if div in self.divisions:
                    self.divisions[div].append(agent)

    def _process_tip_pipeline(self):
        """
        Process corruption tips through the investigation pipeline.
        Intelligence Division assesses → Partnership Council votes →
        Investigation Division assigns → Prosecution Prep hands over to Court.
        """
        corruption_log = self.model.shared_data.get("corruption_acts_log", [])
        trigger = CONSTITUTION.iig.INVESTIGATION_TRIGGER

        new_cases = [
            act for act in corruption_log
            if act.get("corruption_score", 0.0) >= trigger
            and not act.get("investigated", False)
        ]

        for case in new_cases:
            evidence_score = case.get("corruption_score", 0.70)
            if self.partnership_council.vote(
                "open_investigation",
                {"evidence_score": evidence_score}
            ):
                case["investigated"] = True
                self.total_cases_opened += 1
                self.model.shared_data.setdefault(
                    "active_investigations", []
                ).append({
                    "case_id": f"IIG_{self.model.current_year}_{case.get('official_id')}",
                    "target_id": case.get("official_id"),
                    "corruption_score": evidence_score,
                    "year_opened": self.model.current_year
                })

    def _enforce_post_service_restrictions(self):
        """
        Article 7.9 — Former IIG agents cannot enter chambers.
        Track and enforce permanently.
        """
        from agents.oversight import IIGAgent
        from agents.official import OfficialAgent

        # Register all current IIG agents
        for agent in self.model.schedule.agents:
            if isinstance(agent, IIGAgent):
                if agent.unique_id not in self.post_service_registry:
                    self.post_service_registry.append(agent.unique_id)

        # Enforce — former IIG cannot be in chambers
        for agent in self.model.schedule.agents:
            if (isinstance(agent, OfficialAgent) and
                    agent.unique_id in self.post_service_registry):
                if agent.role in ["congress_member", "ethnic_leader",
                                   "analysis_council_member"]:
                    agent._permanently_disqualify(
                        "former_iig_chamber_ineligible"
                    )

    def _update_effectiveness(self):
        """Update IIG effectiveness metric."""
        from agents.oversight import IIGAgent

        all_iig = [a for a in self.model.schedule.agents
                   if isinstance(a, IIGAgent)]

        if not all_iig:
            return

        total_solved = sum(a.cases_solved for a in all_iig)
        total_opened = sum(a.cases_opened for a in all_iig)
        self.total_cases_solved = total_solved
        self.total_cases_opened = total_opened

        if total_opened > 0:
            effectiveness = total_solved / max(1, total_opened)
            self.model.shared_data["iig_effectiveness"] = min(1.0, effectiveness)
        elif self.model.scenario == "A":
            # IIG exists and is operational even before cases open
            # Floor rises slowly to reflect institutional presence
            current = self.model.shared_data.get("iig_effectiveness", 0.30)
            self.model.shared_data["iig_effectiveness"] = min(0.40, current + 0.01)

    def get_summary(self) -> Dict:
        return {
            "total_cases_opened": self.total_cases_opened,
            "total_cases_solved": self.total_cases_solved,
            "solve_rate": round(
                self.total_cases_solved / max(1, self.total_cases_opened), 4
            ),
            "total_prosecutions": self.total_prosecutions,
            "partner_count": len(self.partnership_council.get_partners()),
            "post_service_registry_size": len(self.post_service_registry),
            "division_sizes": {
                div: len(agents)
                for div, agents in self.divisions.items()
            }
        }


if __name__ == "__main__":
    print("institutions/iig.py loaded successfully")
    print(f"IIG entry merit:         {CONSTITUTION.iig.ENTRY_MERIT_MIN}")
    print(f"Academy duration:        {CONSTITUTION.iig.ACADEMY_DURATION_MONTHS} months")
    print(f"Investigation trigger:   {CONSTITUTION.iig.INVESTIGATION_TRIGGER}")
    print(f"Partner eligibility:     {CONSTITUTION.iig.PARTNER_ELIGIBILITY_YEARS} years")
    print(f"Open invest threshold:   {CONSTITUTION.iig.OPEN_INVESTIGATION_THRESHOLD}")
    print(f"Prosecution threshold:   {CONSTITUTION.iig.PROCEED_PROSECUTION_THRESHOLD}")
    print(f"Max agents:              {CONSTITUTION.iig.MAX_AGENTS}")
    print(f"Chamber eligible:        {CONSTITUTION.iig.CHAMBER_ELIGIBLE_POST_SERVICE}")