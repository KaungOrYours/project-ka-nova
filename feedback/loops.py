"""
================================================================================
PROJECT KA-NOVA
feedback/loops.py

Twelve Annual Feedback Loops
Ka-Nova Simulation Engine v1.0

Feedback loops are the nervous system of Ka-Nova.
Every loop runs once per time step (year).
Each loop reads last year's outputs and adjusts agent behavior.

Loop categories:
    Political (P1-P4): trust, IIG, coup risk, merit cycling
    Economic  (E1-E4): state competition, FDI, resources, PhD economy
    Social    (S1-S4): national service, protest, ethnic tension, shame

All loops operate on the model's shared_data and agent attributes.
No loop can override constitutional constraints.
Rights violations (Article 2.4) always take priority over loop outputs.

Author: Kaung Htet
License: MIT
================================================================================
"""

from __future__ import annotations

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import random
import numpy as np
from typing import TYPE_CHECKING

from config.constitution import CONSTITUTION

if TYPE_CHECKING:
    from model import KaNovaModel


# ══════════════════════════════════════════════════════════════════════════════
# FEEDBACK ENGINE
# ══════════════════════════════════════════════════════════════════════════════

class FeedbackEngine:
    """
    Runs all 12 annual feedback loops for the Ka-Nova simulation.

    Called once per time step from model.step().
    Reads shared_data and agent attributes.
    Writes back to shared_data and agent attributes.

    Loop execution order matters:
        Political loops run first — they set governance quality signals
        Economic loops run second — they respond to governance signals
        Social loops run last — they respond to both governance and economics
    """

    def __init__(self, model: "KaNovaModel"):
        self.model = model
        self.year = 0

        # Loop history for diagnostics
        self.loop_history = {
            f"P{i}": [] for i in range(1, 5)
        }
        self.loop_history.update({
            f"E{i}": [] for i in range(1, 5)
        })
        self.loop_history.update({
            f"S{i}": [] for i in range(1, 5)
        })

    def run_all(self):
        """
        Execute all 12 feedback loops in correct order.
        Called every time step from model.step().
        """

        self.year = self.model.current_year

        # POLITICAL LOOPS
        p1 = self.loop_P1_trust_legitimacy()
        p2 = self.loop_P2_iig_corruption()
        p3 = self.loop_P3_coup_probability()
        p4 = self.loop_P4_election_merit()

        # ECONOMIC LOOPS
        e1 = self.loop_E1_state_competition()
        e2 = self.loop_E2_foreign_investment()
        e3 = self.loop_E3_resource_revenue()
        e4 = self.loop_E4_phd_economy()

        # SOCIAL LOOPS
        s1 = self.loop_S1_national_service()
        s2 = self.loop_S2_grievance_protest()
        s3 = self.loop_S3_cultural_offense()
        s4 = self.loop_S4_shame_register()

        # Record loop outputs for diagnostics
        self._record_outputs(p1, p2, p3, p4, e1, e2, e3, e4, s1, s2, s3, s4)

    # ══════════════════════════════════════════════════════════════════════════
    # POLITICAL LOOPS
    # ══════════════════════════════════════════════════════════════════════════

    def loop_P1_trust_legitimacy(self) -> dict:
        """
        P1 — Trust drives legitimacy drives stability.
        v7: Trust acceleration when corruption < 0.20 for 5+ consecutive years.
        Models fear-based compliance transitioning to genuine institutional trust.
        """

        m = self.model
        performance = m.shared_data.get("policy_quality", 0.35)
        current_trust = m.shared_data.get("trust_index", 0.22)
        rights_ok = not m.shared_data.get("rights_violated", False)

        # Scenario-aware trust dynamics
        # Scenario C (military): fear-compliance produces low but non-zero trust.
        # The full MFU rights violation penalty (0.20) applies only in A/B where
        # rights violations are constitutional shocks. In C, repression is the
        # baseline — penalty is smaller and a floor enforces fear-compliance trust.
        if m.scenario == "C":
            rights_penalty = 0.0 if rights_ok else 0.04   # chronic low-level erosion
            trust_floor    = 0.10                           # fear-compliance floor
            performance_c  = min(performance, 0.25)         # military policy quality capped
            new_trust = (
                current_trust * 0.80 +
                performance_c * 0.20
            ) - rights_penalty
            new_trust = max(trust_floor, new_trust)
        else:
            rights_penalty = 0.0 if rights_ok else CONSTITUTION.rights.RIGHTS_VIOLATION_TRUST_DROP
            # Trust update — recency-biased
            new_trust = (
                current_trust * 0.70 +
                performance * 0.25 +
                (0.05 if rights_ok else 0.0)
            ) - rights_penalty

        # v7 — Trust acceleration trigger (Article VIII)
        corruption = m.shared_data.get("corruption_index", 1.0)
        if corruption < CONSTITUTION.federal.TRUST_ACCELERATION_TRIGGER_CORRUPTION:
            streak = m.shared_data.get("low_corruption_streak", 0) + 1
        else:
            streak = 0
        m.shared_data["low_corruption_streak"] = streak

        if streak >= CONSTITUTION.federal.TRUST_ACCELERATION_TRIGGER_YEARS:
            growth = new_trust - current_trust
            if growth > 0:
                new_trust = current_trust + growth * CONSTITUTION.federal.TRUST_ACCELERATION_MULTIPLIER

        new_trust = max(0.0, min(1.0, new_trust))
        m.shared_data["trust_index"] = new_trust

        # Legitimacy derives from trust
        legitimacy = new_trust * 0.70 + performance * 0.30
        m.shared_data["legitimacy_index"] = max(0.0, min(1.0, legitimacy))

        # Stability from legitimacy + no rights violations
        stability = (
            legitimacy * 0.50 +
            (1.0 - m.shared_data.get("coup_risk", 0.25)) * 0.30 +
            (0.20 if rights_ok else 0.0)
        )
        m.shared_data["stability_index"] = max(0.0, min(1.0, stability))

        # Update citizen trust scores via vectorized operation
        if hasattr(m, "citizen_array"):
            m.citizen_array["trust"] = (
                m.citizen_array["trust"] * 0.70 + performance * 0.30
            )
            np.clip(m.citizen_array["trust"], 0.0, 1.0,
                    out=m.citizen_array["trust"])
        else:
            from agents.citizen import CitizenAgent
            from agents.official import OfficialAgent
            for agent in m.schedule.agents:
                if isinstance(agent, CitizenAgent) and not isinstance(agent, OfficialAgent):
                    agent.trust_score = max(0.0, min(1.0,
                        agent.trust_score * 0.70 + performance * 0.30 - rights_penalty
                    ))

        return {
            "loop": "P1",
            "trust": new_trust,
            "legitimacy": legitimacy,
            "stability": stability,
            "rights_penalty": rights_penalty
        }

    def loop_P2_iig_corruption(self) -> dict:
        """
        P2 — IIG effectiveness drives corruption down.

        Direction: NEGATIVE (self-correcting)
        High IIG effectiveness → more arrests → less corruption → cleaner officials
        Low IIG effectiveness → corruption normalized → more corruption acts

        Key dynamic: IIG effectiveness compounds over time.
        Once corruption drops below 0.40, IIG caseload drops,
        freeing agents to tackle harder cases at higher levels.
        This is the institutional maturity curve.
        """

        m = self.model
        from agents.oversight import IIGAgent

        # Calculate current IIG effectiveness from case outcomes
        iig_agents = [a for a in m.schedule.agents if isinstance(a, IIGAgent)]

        if iig_agents:
            total_solved = sum(a.cases_solved for a in iig_agents)
            total_opened = sum(a.cases_opened for a in iig_agents)
            if total_opened > 0 and total_solved > 0:
                raw_effectiveness = total_solved / total_opened
                # Smooth effectiveness update only when cases are being solved
                current_effectiveness = m.shared_data.get("iig_effectiveness", 0.30)
                new_effectiveness = (
                    current_effectiveness * 0.60 +
                    raw_effectiveness * 0.40
                )
            else:
                # No solved cases yet — preserve current value
                new_effectiveness = m.shared_data.get("iig_effectiveness", 0.30)
        else:
            new_effectiveness = m.shared_data.get("iig_effectiveness", 0.30)

        # Scenario modifier
        if m.scenario == "B":
            new_effectiveness *= 0.85  # no safeguards = IIG weaker
        elif m.scenario == "C":
            new_effectiveness = min(0.10, new_effectiveness)  # no IIG

        new_effectiveness = max(0.0, min(1.0, new_effectiveness))
        m.shared_data["iig_effectiveness"] = new_effectiveness

        # Effectiveness reduces corruption scores in officials
        if new_effectiveness > 0.50:
            from agents.official import OfficialAgent
            reduction = new_effectiveness * 0.03
            for agent in m.schedule.agents:
                if isinstance(agent, OfficialAgent):
                    agent.corruption_score = max(
                        0.0, agent.corruption_score - reduction
                    )

        # IIG activity signal to states
        for state_id in m.states:
            m.states[state_id]["iig_activity"] = new_effectiveness * 0.80

        # Update corruption index
        from agents.official import OfficialAgent
        officials = [a for a in m.schedule.agents if isinstance(a, OfficialAgent)]
        if officials:
            avg_corruption = sum(a.corruption_score for a in officials) / len(officials)
            m.shared_data["corruption_index"] = avg_corruption
        else:
            # Decay corruption slowly without IIG
            m.shared_data["corruption_index"] = min(
                1.0,
                m.shared_data.get("corruption_index", 0.65) + 0.01
            )

        return {
            "loop": "P2",
            "iig_effectiveness": new_effectiveness,
            "corruption_index": m.shared_data.get("corruption_index", 0.65),
            "iig_agents": len(iig_agents),
            "cases_solved": sum(a.cases_solved for a in iig_agents)
        }

    def loop_P3_coup_probability(self) -> dict:
        """
        P3 — Military loyalty determines coup risk.

        Direction: NEGATIVE (self-correcting under MFU)
        High loyalty → low coup risk → civilian command maintained
        Low loyalty → coup risk rises → constitutional safeguards activate

        Key dynamic: Military loyalty is driven by:
        - Constitutional commitment (scenario A = high)
        - Chancellor approval rating
        - National Service creating loyalty bonds
        - IIG monitoring of military corruption

        Scorched Earth ROE (Article 17) maintains external deterrence
        independently of domestic coup risk.
        """

        m = self.model
        from agents.official import ChancellorAgent

        # Get chancellor approval
        chancellors = [a for a in m.schedule.agents if isinstance(a, ChancellorAgent)]
        chancellor_approval = chancellors[0].approval_rating if chancellors else 0.45

        # Constitutional commitment by scenario
        const_commitment = {
            "A": 0.80,
            "B": 0.55,
            "C": 0.25
        }.get(m.scenario, 0.50)

        # Trust feeds military loyalty
        trust = m.shared_data.get("trust_index", 0.22)
        ns_effect = m.shared_data.get("ns_loyalty_cumulative", 0.0)

        # Military loyalty calculation
        new_loyalty = min(1.0,
            const_commitment * 0.40 +
            chancellor_approval * 0.25 +
            trust * 0.20 +
            ns_effect * 0.15
        )

        m.shared_data["military_loyalty"] = new_loyalty

        # Coup risk — inverse of loyalty with threshold
        coup_threshold_loyalty = CONSTITUTION.military.COUP_TRIGGER_LOYALTY
        coup_threshold_approval = CONSTITUTION.military.COUP_TRIGGER_APPROVAL

        if (new_loyalty < coup_threshold_loyalty and
                chancellor_approval < coup_threshold_approval):
            # Coup risk rises
            coup_risk = (
                (coup_threshold_loyalty - new_loyalty) * 0.60 +
                (coup_threshold_approval - chancellor_approval) * 0.40
            )
            m.shared_data["coup_risk"] = min(
                1.0, m.shared_data.get("coup_risk", 0.25) + coup_risk * 0.20
            )
        else:
            # Coup risk decays
            m.shared_data["coup_risk"] = max(
                0.0, m.shared_data.get("coup_risk", 0.25) - 0.02
            )

        return {
            "loop": "P3",
            "military_loyalty": new_loyalty,
            "coup_risk": m.shared_data["coup_risk"],
            "chancellor_approval": chancellor_approval,
            "const_commitment": const_commitment
        }

    def loop_P4_election_merit(self) -> dict:
        """
        P4 — Merit recertification cycles leadership quality.

        Direction: NEGATIVE (self-correcting)
        High merit officials → good policy → trust rises → more merit candidates
        Low merit/corrupt officials → bad policy → trust falls → crisis

        Key dynamic: Every 4 years, merit recertification fires.
        Officials below 0.60 are removed.
        New candidates come from citizen pool — highest merit eligible.
        This creates leadership quality cycling that mirrors electoral cycles.
        """

        m = self.model
        from agents.official import OfficialAgent

        officials = [a for a in m.schedule.agents if isinstance(a, OfficialAgent)]

        if not officials:
            return {"loop": "P4", "avg_merit": 0.0, "recert_year": False}

        # Recalculate merit for all officials
        for official in officials:
            official.merit_score = official._calculate_merit()

        avg_merit = sum(a.merit_score for a in officials) / len(officials)
        m.shared_data["merit_system_integrity"] = avg_merit

        # Merit drives policy quality
        policy_quality = min(1.0,
            avg_merit * 0.70 +
            m.shared_data.get("iig_effectiveness", 0.30) * 0.20 +
            random.uniform(0.0, 0.10)
        )
        m.shared_data["policy_quality"] = policy_quality

        # Recertification year — every 4 years
        recert_year = (
            self.year % CONSTITUTION.merit.RECERTIFICATION_INTERVAL == 0 and
            self.year > 0
        )

        if recert_year:
            disqualified = 0
            for official in officials:
                if official.merit_score < CONSTITUTION.merit.RECERTIFICATION_FAIL_THRESHOLD:
                    official._fail_recertification()
                    disqualified += 1

            m.shared_data["recertification_disqualified"] = disqualified

        return {
            "loop": "P4",
            "avg_merit": avg_merit,
            "policy_quality": policy_quality,
            "recert_year": recert_year,
            "officials_count": len(officials)
        }

    # ══════════════════════════════════════════════════════════════════════════
    # ECONOMIC LOOPS
    # ══════════════════════════════════════════════════════════════════════════

    def loop_E1_state_competition(self) -> dict:
        """
        E1 — State competition drives growth.

        Direction: POSITIVE (self-reinforcing)
        States compete for investment and talent.
        Higher performing states attract more resources.
        Federal Development Fund redistributes to prevent dominance.
        Economic Check & Balance caps at 40% GDP share.

        Key dynamic: Competition without redistribution = dominance.
        Competition WITH redistribution = innovation pressure.
        The 40/40/20 split is the constitutional correction mechanism.
        """

        m = self.model
        states = m.states

        total_gdp = sum(s.get("gdp", 100.0) for s in states.values())
        if total_gdp <= 0:
            return {"loop": "E1", "total_gdp": 0, "gdp_growth": 0}

        for state_id, state in states.items():
            # Growth factors
            budget_boost = state.get("budget", 0.0) * 0.0001
            knowledge_boost = state.get("knowledge_capital", 0.0) * 0.002
            infrastructure_boost = state.get("infrastructure", 0.30) * 0.005
            base_growth = state.get("gdp_growth", 0.01)

            # Corruption drag
            corruption_drag = state.get("corruption_level", 0.60) * 0.010

            # IIG activity reduces corruption drag
            iig_correction = state.get("iig_activity", 0.0) * corruption_drag * 0.50

            # Net growth rate
            growth_rate = max(
                -0.05,  # max 5% contraction
                base_growth + budget_boost + knowledge_boost +
                infrastructure_boost - corruption_drag + iig_correction
            )

            # Apply growth
            old_gdp = state.get("gdp", 100.0)
            state["gdp"] = old_gdp * (1.0 + growth_rate)
            state["gdp_growth"] = growth_rate

        # National GDP metrics
        new_total_gdp = sum(s.get("gdp", 100.0) for s in states.values())
        national_growth = (new_total_gdp - total_gdp) / max(1, total_gdp)
        m.shared_data["gdp_growth_rate"] = national_growth
        m.shared_data["total_gdp"] = new_total_gdp

        # State GDP shares for ECB monitoring
        gdp_shares = {
            sid: s.get("gdp", 100.0) / max(1, new_total_gdp)
            for sid, s in states.items()
        }
        m.shared_data["state_gdp_shares"] = gdp_shares

        # Annual state ranking
        ranked = sorted(gdp_shares.items(), key=lambda x: x[1], reverse=True)
        m.shared_data["state_ranking"] = ranked

        return {
            "loop": "E1",
            "total_gdp": new_total_gdp,
            "gdp_growth": national_growth,
            "top_state": ranked[0][0] if ranked else None,
            "top_state_share": ranked[0][1] if ranked else 0.0
        }

    def loop_E2_foreign_investment(self) -> dict:
        """
        E2 — Foreign investment drives technology transfer to knowledge economy.

        Direction: POSITIVE (self-reinforcing)
        Stable governance + low corruption → FDI inflows
        FDI → technology transfer → knowledge capital rises
        Knowledge capital → higher productivity → more FDI attracted

        Key dynamic: Information lag (1-3 years) creates realistic
        market overreactions. Investors respond to past conditions,
        not current ones. This produces boom-bust FDI cycles
        that mirror real emerging market behavior.

        Article 10.3 — 49% foreign cap in strategic sectors
        forces technology transfer through joint ventures.
        """

        m = self.model
        from agents.foreign import ForeignInvestorAgent

        investors = [a for a in m.schedule.agents if isinstance(a, ForeignInvestorAgent)]

        active_count = sum(1 for a in investors if a.is_invested)
        total_fdi_in = sum(a.capital_invested for a in investors if a.is_invested)
        total_tech_transfer = sum(a.technology_transferred for a in investors)

        m.shared_data["active_foreign_investors"] = active_count
        m.shared_data["fdi_stock"] = total_fdi_in

        # Technology transfer boosts knowledge capital in all states
        if active_count > 0:
            tech_per_state = total_tech_transfer * 0.001 / max(1, len(m.states))
            for state in m.states.values():
                state["knowledge_capital"] = (
                    state.get("knowledge_capital", 0.0) + tech_per_state
                )

        # International confidence signal feeds into FDI probability
        confidence = m.shared_data.get("intl_confidence_signal", 0.30)
        iig_effectiveness = m.shared_data.get("iig_effectiveness", 0.30)
        stability = m.shared_data.get("stability_index", 0.30)

        # Composite investment attractiveness
        attractiveness = (
            (1.0 - m.shared_data.get("corruption_index", 0.65)) * 0.35 +
            stability * 0.30 +
            iig_effectiveness * 0.20 +
            confidence * 0.15
        )
        m.shared_data["investment_attractiveness"] = attractiveness

        return {
            "loop": "E2",
            "active_investors": active_count,
            "fdi_stock": total_fdi_in,
            "tech_transfer": total_tech_transfer,
            "attractiveness": attractiveness
        }

    def loop_E3_resource_revenue(self) -> dict:
        """
        E3 — Resource revenue split reduces inequality.

        Direction: NEGATIVE (self-correcting)
        Resource wealth → 40/40/20 split → redistribution → Gini falls
        If Gini exceeds 0.45 → ECB triggers → structural remedy

        Key dynamic: The 20% direct ethnic community payment
        bypasses state government entirely. Even if the state
        is corrupt, communities receive their share.
        This is the most ethnically significant economic clause.
        """

        m = self.model
        states = m.states

        total_resource_revenue = sum(
            s.get("resource_revenue", 0.0) for s in states.values()
        )

        # Resource revenue grows with stability and investment
        stability = m.shared_data.get("stability_index", 0.30)
        attractiveness = m.shared_data.get("investment_attractiveness", 0.30)

        revenue_growth = (
            stability * 0.03 +
            attractiveness * 0.02 +
            random.gauss(0.01, 0.005)  # natural variation
        )

        for state in states.values():
            state["resource_revenue"] = max(
                0.0,
                state.get("resource_revenue", 0.0) * (1.0 + revenue_growth)
            )

        # Gini check — feeds ECB trigger
        gini = m.shared_data.get("gini_coefficient", 0.55)

        if gini > CONSTITUTION.federal.GINI_THRESHOLD:
            # Automatic ECB trigger — redistribution pressure
            m.shared_data.setdefault("ecb_triggers", []).append({
                "type": "inequality_threshold",
                "gini": gini,
                "year": self.year
            })
            # Reduce resource revenue in dominant state to correct
            ranked = m.shared_data.get("state_ranking", [])
            if ranked:
                dominant_state_id = ranked[0][0]
                if ranked[0][1] > CONSTITUTION.federal.STATE_GDP_CAP:
                    states[dominant_state_id]["resource_revenue"] *= 0.95

        return {
            "loop": "E3",
            "total_resource_revenue": total_resource_revenue,
            "revenue_growth": revenue_growth,
            "gini": gini,
            "ecb_triggered": gini > CONSTITUTION.federal.GINI_THRESHOLD
        }

    def loop_E4_phd_economy(self) -> dict:
        """
        E4 — PhD graduates compound knowledge capital (North Star loop).

        Direction: POSITIVE (self-reinforcing — S-curve)
        PhD programs → graduates → knowledge capital rises
        Knowledge capital → innovation → FDI attracted → more PhDs funded
        After critical mass (~Year 20) → exponential compounding

        Key insight: This is the slowest but most powerful loop.
        It takes 15-25 years to compound meaningfully.
        The S-curve emergence is Ka-Nova's primary north star finding.

        Article 11.1 — free tuition + stipend removes access barrier.
        Article 11.3 — 15% royalty incentivizes researcher retention.
        This combination is the anti-brain-drain mechanism.
        """

        m = self.model
        from agents.citizen import CitizenAgent
        from agents.official import OfficialAgent

        # Count PhD graduates this year
        phd_grads = m.shared_data.get("phd_graduates", 0)

        # PhD candidates in pipeline
        phd_candidates = [
            a for a in m.schedule.agents
            if isinstance(a, CitizenAgent) and
            not isinstance(a, OfficialAgent) and
            a.is_phd_candidate
        ]

        # Knowledge capital accumulation
        knowledge_boost = phd_grads * CONSTITUTION.science.PHD_KNOWLEDGE_CAPITAL_BOOST
        current_knowledge = m.shared_data.get("knowledge_capital_index", 0.0)
        new_knowledge = min(1.0, current_knowledge + knowledge_boost * 0.01)
        m.shared_data["knowledge_capital_index"] = new_knowledge

        # State-level knowledge
        total_state_knowledge = sum(
            s.get("knowledge_capital", 0.0) for s in m.states.values()
        )
        m.shared_data["total_knowledge_capital"] = total_state_knowledge

        # Brain drain check — high knowledge + low stability = emigration
        stability = m.shared_data.get("stability_index", 0.30)
        if stability < 0.40 and new_knowledge > 0.20:
            brain_drain_risk = (0.40 - stability) * 0.30
            m.shared_data["brain_drain_risk"] = brain_drain_risk
        else:
            m.shared_data["brain_drain_risk"] = 0.0

        # Brain drain rate from emigrants
        emigrants = len(m.shared_data.get("emigrants", []))
        total_citizens = m.shared_data.get("total_citizens", 9500)
        brain_drain_rate = emigrants / max(1, total_citizens)
        m.shared_data["brain_drain_rate"] = brain_drain_rate

        # Royalty mechanism — reduces emigration among PhD graduates
        if CONSTITUTION.science.RESEARCHER_ROYALTY_RATE > 0:
            royalty_retention = CONSTITUTION.science.RESEARCHER_ROYALTY_RATE * 0.50
            m.shared_data["phd_retention_bonus"] = royalty_retention

        return {
            "loop": "E4",
            "phd_graduates_this_year": phd_grads,
            "phd_candidates": len(phd_candidates),
            "knowledge_capital": new_knowledge,
            "brain_drain_rate": brain_drain_rate,
            "total_state_knowledge": total_state_knowledge
        }

    # ══════════════════════════════════════════════════════════════════════════
    # SOCIAL LOOPS
    # ══════════════════════════════════════════════════════════════════════════

    def loop_S1_national_service(self) -> dict:
        """
        S1 — National Service builds ethnic cross-exposure and civic loyalty.

        Direction: POSITIVE (slow compounding over generations)
        NS completion → ethnic cross-exposure rises → inter-ethnic trust rises
        → fewer ethnic tension events → fewer Council vetoes → better policy

        Key dynamic: This is a generational loop. Effects compound
        over 20-30 years as NS cohorts age into influential positions.
        The first generation of MFU NS graduates reaches leadership age
        around Year 20 — correlating with the north star acceleration.

        Article 9.5 — both civilian and military tracks create same exposure.
        Mixed units across ethnic lines is constitutionally mandated.
        """

        m = self.model
        from agents.citizen import CitizenAgent
        from agents.official import OfficialAgent

        # Citizens completing NS this year (turning 19 after Year 0)
        ns_completers = [
            a for a in m.schedule.agents
            if isinstance(a, CitizenAgent) and
            not isinstance(a, OfficialAgent) and
            a.national_service_completed and
            a.age == 19
        ]

        # Cross-exposure boost
        for agent in ns_completers:
            agent.ethnic_cross_exposure = min(
                1.0,
                agent.ethnic_cross_exposure +
                CONSTITUTION.military.NS_ETHNIC_EXPOSURE_BOOST
            )
            agent.constitutional_loyalty = min(
                1.0,
                agent.constitutional_loyalty +
                CONSTITUTION.military.NS_LOYALTY_BOOST
            )

        # Cumulative NS loyalty effect on military
        ns_cumulative = m.shared_data.get("ns_loyalty_cumulative", 0.0)
        ns_cumulative = min(0.30, ns_cumulative + len(ns_completers) * 0.0001)
        m.shared_data["ns_loyalty_cumulative"] = ns_cumulative

        # Ethnic cross-exposure reduces tension in all states
        if ns_completers:
            for state in m.states.values():
                state["ethnic_tension"] = max(
                    0.0,
                    state.get("ethnic_tension", 0.60) - 0.005
                )

        # Average cross-exposure across all citizens
        all_citizens = [
            a for a in m.schedule.agents
            if isinstance(a, CitizenAgent) and
            not isinstance(a, OfficialAgent)
        ]
        if all_citizens:
            avg_exposure = sum(
                a.ethnic_cross_exposure for a in all_citizens
            ) / len(all_citizens)
            m.shared_data["ethnic_harmony_index"] = avg_exposure

        return {
            "loop": "S1",
            "ns_completers": len(ns_completers),
            "ns_cumulative_loyalty": ns_cumulative,
            "ethnic_harmony": m.shared_data.get("ethnic_harmony_index", 0.22)
        }

    def loop_S2_grievance_protest(self) -> dict:
        """
        S2 — Grievance drives protest. Government response determines outcome.

        Direction: NEGATIVE (self-correcting IF government responds)
        High grievance → protest → government must respond
        If addressed: grievance halved → trust partially restored
        If suppressed: grievance doubled → legitimacy collapses → coup risk rises

        Key dynamic: This loop has a BRANCHING POINT.
        The government's response to protest determines whether
        the loop stabilizes (negative feedback) or amplifies
        (positive feedback toward collapse).
        Under Scenario A — MFU rights protection prevents suppression.
        Under Scenario C — suppression is the default response.
        """

        m = self.model
        from agents.citizen import CitizenAgent
        from agents.official import OfficialAgent

        # Count protesters
        if hasattr(m, "citizen_array"):
            protest_threshold = 0.70
            protesters = np.sum(
                m.citizen_array["grievance"] > protest_threshold
            )
            protest_rate = protesters / max(1, len(m.citizen_array["grievance"]))
        else:
            all_citizens = [
                a for a in m.schedule.agents
                if isinstance(a, CitizenAgent) and
                not isinstance(a, OfficialAgent) and
                a.is_alive and not a.has_emigrated
            ]
            protesters = sum(1 for a in all_citizens if a.is_protesting)
            protest_rate = protesters / max(1, len(all_citizens))

        m.shared_data["network_protest_rate"] = protest_rate
        m.shared_data["protest_rate"] = protest_rate

        # Government response
        if protest_rate > 0.05:
            for state in m.states.values():
                state["protest_activity"] = min(1.0, protest_rate * 2.0)

            # Scenario determines response
            if m.scenario == "A":
                # MFU — rights protected, government must address grievances
                # Policy response reduces grievance
                if hasattr(m, "citizen_array"):
                    m.citizen_array["grievance"] = np.clip(
                        m.citizen_array["grievance"] * 0.90,
                        0.0, 1.0
                    )
                m.shared_data["trust_index"] = max(
                    0.0,
                    m.shared_data.get("trust_index", 0.22) - 0.02
                )

            elif m.scenario == "B":
                # No safeguards — may suppress
                if random.random() < 0.40:
                    # Suppression — grievance worsens
                    if hasattr(m, "citizen_array"):
                        m.citizen_array["grievance"] = np.clip(
                            m.citizen_array["grievance"] * 1.10,
                            0.0, 1.0
                        )
                    m.shared_data["coup_risk"] = min(
                        1.0,
                        m.shared_data.get("coup_risk", 0.25) + 0.05
                    )
                    m.shared_data["rights_violated"] = True

            elif m.scenario == "C":
                # Military — suppression is default
                if hasattr(m, "citizen_array"):
                    m.citizen_array["grievance"] = np.clip(
                        m.citizen_array["grievance"] * 1.15,
                        0.0, 1.0
                    )
                m.shared_data["rights_violated"] = True
                # Floor at 0.10 — fear-compliance trust, not zero collapse
                m.shared_data["trust_index"] = max(
                    0.10,
                    m.shared_data.get("trust_index", 0.22) - 0.05
                )

        # Update grievance from economic conditions
        # ── Recalculate employment_rate from actual citizen states ────────
        if hasattr(m, "schedule") and m.schedule.agents:
            from agents.citizen import CitizenAgent
            citizens = [a for a in m.schedule.agents if isinstance(a, CitizenAgent) and a.is_alive and not a.has_emigrated]
            if citizens:
                employed = sum(1 for c in citizens if c.employment_status == "employed")
                m.shared_data["employment_rate"] = round(employed / len(citizens), 4)
        employment = m.shared_data.get("employment_rate", 0.58)
        corruption = m.shared_data.get("corruption_index", 0.65)
        gini = m.shared_data.get("gini_coefficient", 0.55)

        grievance_pressure = (
            corruption * 0.30 +
            (1.0 - employment) * 0.40 +
            (gini - 0.35) * 0.30
        ) * 0.05

        if hasattr(m, "citizen_array"):
            m.citizen_array["grievance"] = np.clip(
                m.citizen_array["grievance"] + grievance_pressure,
                0.0, 1.0
            )
            avg_grievance = float(np.mean(m.citizen_array["grievance"]))
        else:
            avg_grievance = 0.55

        m.shared_data["grievance_index"] = avg_grievance

        return {
            "loop": "S2",
            "protest_rate": protest_rate,
            "avg_grievance": avg_grievance,
            "scenario_response": m.scenario
        }

    def loop_S3_cultural_offense(self) -> dict:
        """
        S3 — Cultural offenses raise ethnic tension.

        Direction: NEGATIVE (dampening IF IIG and courts respond)
        Cultural offense → ethnic tension → Council vetoes increase
        → policy deadlocks → government effectiveness drops
        → economic slowdown → grievance rises

        IIG investigates cultural offense as merit subversion.
        Constitutional Court strikes down discriminatory policies.
        National Service cross-exposure is the long-term dampener.

        Key dynamic: Ethnic tension feeds back into Loop S2
        and Loop P1. A cultural offense cascade can derail
        otherwise stable governance — this is historically accurate
        for Myanmar and is a key stress test scenario.
        """

        m = self.model

        # Ethnic tension from all states
        state_tensions = [
            s.get("ethnic_tension", 0.60) for s in m.states.values()
        ]
        avg_tension = sum(state_tensions) / max(1, len(state_tensions))
        m.shared_data["ethnic_tension_index"] = avg_tension

        # Random cultural offense event (low probability)
        offense_probability = avg_tension * 0.05
        if random.random() < offense_probability:
            # Cultural offense occurs
            offended_state = random.choice(list(m.states.keys()))
            m.states[offended_state]["ethnic_tension"] = min(
                1.0,
                m.states[offended_state].get("ethnic_tension", 0.60) + 0.08
            )
            m.shared_data.setdefault("cultural_offense_events", []).append({
                "state": offended_state,
                "year": self.year
            })

            # Ethnic tension feeds into grievance
            if hasattr(m, "citizen_array"):
                m.citizen_array["grievance"] = np.clip(
                    m.citizen_array["grievance"] + 0.03,
                    0.0, 1.0
                )

        # Cross-exposure dampens tension over time
        harmony = m.shared_data.get("ethnic_harmony_index", 0.22)
        if harmony > 0.50:
            for state in m.states.values():
                state["ethnic_tension"] = max(
                    0.10,
                    state.get("ethnic_tension", 0.60) - harmony * 0.02
                )

        # IIG investigation of cultural offense
        if len(m.shared_data.get("cultural_offense_events", [])) > 0:
            m.shared_data["iig_effectiveness"] = min(
                1.0,
                m.shared_data.get("iig_effectiveness", 0.30) + 0.01
            )

        return {
            "loop": "S3",
            "avg_ethnic_tension": avg_tension,
            "offense_occurred": random.random() < offense_probability,
            "harmony": harmony
        }

    def loop_S4_shame_register(self) -> dict:
        """
        S4 — National Shame Register creates compounding deterrence.

        Direction: NEGATIVE (compounding deterrence)
        Total Ruin conviction → Shame Register entry →
        corruption tolerance drops across all officials →
        fewer corruption acts → fewer IIG cases →
        IIG resources redirect to harder cases →
        higher-level corruption detected →
        Shame Register grows → deterrence compounds

        Key dynamic: The deterrence effect is non-linear.
        First 5 entries: minimal effect.
        10-20 entries: noticeable corruption decline.
        30+ entries: systemic behavioral change.
        This S-curve matches empirical data from ICAC Hong Kong.

        The Shame Register is also culturally powerful for Myanmar —
        a high-context society where face and reputation are
        significant behavioral drivers.
        """

        m = self.model
        from agents.official import OfficialAgent

        shame_size = m.shared_data.get("shame_register_size", 0)

        if shame_size == 0:
            return {
                "loop": "S4",
                "shame_size": 0,
                "deterrence_effect": 0.0,
                "corruption_reduction": 0.0
            }

        # Deterrence effect — non-linear, S-curve
        # Minimal effect below 5 entries
        # Accelerates between 10-30 entries
        # Plateaus above 50 entries
        if shame_size < 5:
            deterrence = shame_size * 0.01
        elif shame_size < 30:
            deterrence = 0.05 + (shame_size - 5) * 0.015
        else:
            deterrence = min(0.40, 0.425 + (shame_size - 30) * 0.002)

        m.shared_data["corruption_deterrence"] = deterrence

        # Apply deterrence to all officials
        officials = [a for a in m.schedule.agents if isinstance(a, OfficialAgent)]
        corruption_before = sum(a.corruption_score for a in officials)

        for official in officials:
            if official.known_shame_register_victim:
                official.corruption_tolerance = max(
                    0.0,
                    official.corruption_tolerance - deterrence * 0.05
                )
                official.corruption_score = max(
                    0.0,
                    official.corruption_score - deterrence * 0.02
                )

        corruption_after = sum(a.corruption_score for a in officials)
        corruption_reduction = max(
            0.0,
            (corruption_before - corruption_after) / max(1, len(officials))
        )

        # Shame register also deters illicit networks
        from agents.foreign import IllicitNetworkAgent
        for agent in m.schedule.agents:
            if isinstance(agent, IllicitNetworkAgent) and agent.is_active:
                # Fear of Total Ruin reduces network size
                agent.network_size = max(
                    0.0,
                    agent.network_size - deterrence * 0.03
                )

        return {
            "loop": "S4",
            "shame_size": shame_size,
            "deterrence_effect": deterrence,
            "corruption_reduction": corruption_reduction,
            "officials_affected": len(officials)
        }

    # ══════════════════════════════════════════════════════════════════════════
    # DIAGNOSTICS
    # ══════════════════════════════════════════════════════════════════════════

    def _record_outputs(self, p1, p2, p3, p4, e1, e2, e3, e4, s1, s2, s3, s4):
        """Record loop outputs for diagnostic analysis."""

        outputs = [p1, p2, p3, p4, e1, e2, e3, e4, s1, s2, s3, s4]
        for output in outputs:
            loop_id = output.get("loop", "unknown")
            if loop_id in self.loop_history:
                self.loop_history[loop_id].append({
                    "year": self.year,
                    **{k: v for k, v in output.items()
                       if k != "loop" and isinstance(v, (int, float, bool))}
                })

    def get_loop_summary(self) -> dict:
        """Return summary of loop outputs for current year."""

        return {
            "year": self.year,
            "trust": self.model.shared_data.get("trust_index", 0.0),
            "corruption": self.model.shared_data.get("corruption_index", 0.0),
            "iig_effectiveness": self.model.shared_data.get("iig_effectiveness", 0.0),
            "coup_risk": self.model.shared_data.get("coup_risk", 0.0),
            "stability": self.model.shared_data.get("stability_index", 0.0),
            "gdp_growth": self.model.shared_data.get("gdp_growth_rate", 0.0),
            "knowledge_capital": self.model.shared_data.get("knowledge_capital_index", 0.0),
            "ethnic_harmony": self.model.shared_data.get("ethnic_harmony_index", 0.0),
            "protest_rate": self.model.shared_data.get("protest_rate", 0.0),
            "grievance": self.model.shared_data.get("grievance_index", 0.0),
            "shame_size": self.model.shared_data.get("shame_register_size", 0),
            "deterrence": self.model.shared_data.get("corruption_deterrence", 0.0),
            "north_star": self.model.shared_data.get("north_star_progress", 0.0)
        }

    def get_loop_history_df(self):
        """Return loop history as DataFrame for analysis."""

        import pandas as pd
        rows = []
        for loop_id, history in self.loop_history.items():
            for record in history:
                rows.append({"loop": loop_id, **record})
        return pd.DataFrame(rows) if rows else pd.DataFrame()


# ══════════════════════════════════════════════════════════════════════════════
# QUICK TEST
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":

    print("Testing FeedbackEngine...")

    class MockCitizenAgent:
        def __init__(self, i):
            self.unique_id = i
            self.trust_score = 0.30
            self.grievance = 0.55
            self.is_protesting = False
            self.is_alive = True
            self.has_emigrated = False
            self.ethnic_cross_exposure = 0.25
            self.constitutional_loyalty = 0.30
            self.national_service_completed = True
            self.age = 25
            self.is_phd_candidate = False

        def _calculate_merit(self):
            return 0.55

    class MockOfficialAgent(MockCitizenAgent):
        def __init__(self, i):
            super().__init__(i)
            self.corruption_score = 0.45
            self.merit_score = 0.65
            self.corruption_tolerance = 0.35
            self.known_shame_register_victim = True
            self.approval_rating = 0.50
            self.psych_probation = False

        def _calculate_merit(self):
            return 0.65

        def _fail_recertification(self):
            pass

    class MockChancellorAgent(MockOfficialAgent):
        pass

    class MockSchedule:
        def __init__(self):
            self.agents = (
                [MockCitizenAgent(i) for i in range(50)] +
                [MockOfficialAgent(i + 50) for i in range(10)] +
                [MockChancellorAgent(999)]
            )

    class MockModel:
        def __init__(self):
            self.current_year = 5
            self.scenario = "A"
            self.schedule = MockSchedule()
            self.states = {
                s: {
                    "gdp": gdp, "gdp_growth": 0.02,
                    "resource_revenue": 50000.0,
                    "budget": 10000.0,
                    "corruption_level": 0.60,
                    "ethnic_tension": 0.55,
                    "knowledge_capital": 0.05,
                    "infrastructure": 0.35,
                    "iig_activity": 0.30,
                    "protest_activity": 0.0
                }
                for s, gdp in [
                    ("bamar_central", 400.0),
                    ("shan_eastern", 250.0),
                    ("karen_southern", 180.0),
                    ("kachin_northern", 170.0)
                ]
            }
            self.shared_data = {
                "trust_index": 0.35,
                "corruption_index": 0.55,
                "iig_effectiveness": 0.45,
                "coup_risk": 0.15,
                "stability_index": 0.45,
                "policy_quality": 0.50,
                "legitimacy_index": 0.45,
                "rights_violated": False,
                "gini_coefficient": 0.42,
                "gdp_growth_rate": 0.03,
                "employment_rate": 0.65,
                "ethnic_harmony_index": 0.35,
                "ethnic_tension_index": 0.50,
                "shame_register_size": 8,
                "shame_register": [],
                "phd_graduates": 3,
                "knowledge_capital_index": 0.08,
                "emigrants": [],
                "total_citizens": 50,
                "network_protest_rate": 0.02,
                "military_loyalty": 0.65,
                "ns_loyalty_cumulative": 0.05,
                "intl_confidence_signal": 0.55,
                "investment_attractiveness": 0.50,
                "active_foreign_investors": 12,
                "fdi_stock": 500000.0,
                "ecb_triggers": [],
                "north_star_progress": 0.45,
                "state_ranking": [],
                "state_gdp_shares": {}
            }

            # Monkey-patch agent types
            import agents.citizen as ca
            import agents.official as oa
            import agents.oversight as ova
            import agents.foreign as fa

            for agent in self.schedule.agents[:50]:
                agent.__class__ = ca.CitizenAgent

            for agent in self.schedule.agents[50:60]:
                agent.__class__ = oa.OfficialAgent

            self.schedule.agents[60].__class__ = oa.ChancellorAgent

    mock = MockModel()
    engine = FeedbackEngine(mock)

    print("\nRunning all 12 feedback loops...")
    engine.run_all()

    summary = engine.get_loop_summary()
    print("\nLoop Summary (Year 5):")
    for k, v in summary.items():
        if isinstance(v, float):
            print(f"  {k:<25}: {v:.4f}")
        else:
            print(f"  {k:<25}: {v}")

    print(f"\nLoop history entries:")
    for loop_id, history in engine.loop_history.items():
        print(f"  {loop_id}: {len(history)} records")

    print("\nfeedback/loops.py loaded successfully")