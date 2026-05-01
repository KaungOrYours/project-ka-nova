"""
================================================================================
PROJECT KA-NOVA
agents/foreign.py

Foreign Agents — External Actors Interacting with the Federal Union
Ka-Nova Simulation Engine v1.0

Foreign agents represent the external environment that the MFU must
navigate. They respond to the Union's institutional quality, stability,
and policy signals. They are not subject to MFU constitutional rules
but are affected by them.

Includes:
- ForeignInvestorAgent: capital allocation based on stability signals
- NeighboringStateAgent: trade, border tension, diplomatic relations
- InternationalOrgAgent: aid, conditionality, human rights monitoring
- IllicitNetworkAgent: smuggling, black market, corruption exploitation

Key dynamics:
- Foreign investors respond to IIG effectiveness and corruption index
- Neighboring states respond to ethnic tension and border security
- International orgs respond to rights violations and governance quality
- Illicit networks expand when IIG effectiveness drops

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
from mesa import Agent

from config.constitution import CONSTITUTION


# ══════════════════════════════════════════════════════════════════════════════
# FOREIGN INVESTOR AGENT
# ══════════════════════════════════════════════════════════════════════════════

class ForeignInvestorAgent(Agent):
    """
    Foreign Investor — capital allocation based on MFU institutional signals.

    Responds to:
    - Corruption index (lower = invest more)
    - IIG effectiveness (higher = more confident)
    - Political stability (coup risk = withdraw)
    - Rule of law (Total Ruin Protocol = property rights signal)
    - Sector caps (Article 10.3 — max 49% in strategic sectors)

    Key insight: Foreign investors are the primary signal that MFU
    is working. Net positive FDI by Year 25 = north star on track.
    """

    def __init__(
        self,
        unique_id: int,
        model,
        investor_type: str,
        home_country: str,
        sector: str,
        capital: float
    ):
        super().__init__(unique_id, model)

        # ── IDENTITY ──────────────────────────────────────────────────────────
        self.investor_type = investor_type  # corporate / sovereign / venture
        self.home_country = home_country
        self.sector = sector
        self.is_strategic_sector = sector in CONSTITUTION.economic.STRATEGIC_SECTORS

        # ── CAPITAL ───────────────────────────────────────────────────────────
        self.capital_available = capital
        self.capital_invested = 0.0
        self.capital_withdrawn = 0.0
        self.annual_return = 0.0
        self.cumulative_return = 0.0

        # ── OWNERSHIP COMPLIANCE (Article 10.3) ───────────────────────────────
        self.max_ownership = (
            CONSTITUTION.economic.FOREIGN_CAP_STRATEGIC
            if self.is_strategic_sector
            else CONSTITUTION.economic.FOREIGN_CAP_OPEN
        )
        self.current_ownership_pct = 0.0
        self.compliant = True

        # ── DECISION THRESHOLDS ───────────────────────────────────────────────
        self.risk_tolerance = random.uniform(0.20, 0.80)
        self.corruption_threshold = random.uniform(0.30, 0.60)
        self.stability_threshold = random.uniform(0.40, 0.70)
        self.min_iig_effectiveness = random.uniform(0.30, 0.55)

        # ── INVESTMENT STATE ──────────────────────────────────────────────────
        self.is_invested = False
        self.investment_year = None
        self.years_invested = 0
        self.withdrawal_pending = False
        self.technology_transferred = 0.0  # cumulative tech transfer

        # ── INFORMATION LAG (Article 10 — realistic market behavior) ──────────
        self.perceived_corruption = 0.65    # starts at Myanmar baseline
        self.perceived_stability = 0.30
        self.perceived_rule_of_law = 0.25
        self.information_lag = random.randint(1, 3)  # years behind reality

        # ── TRACKING ──────────────────────────────────────────────────────────
        self.investment_decisions: List[Dict] = []

    # ══════════════════════════════════════════════════════════════════════════
    # MESA STEP
    # ══════════════════════════════════════════════════════════════════════════

    def step(self):
        """Annual foreign investor decision cycle."""

        # 1. Update perceptions (with information lag)
        self._update_perceptions()

        # 2. Investment decision
        if not self.is_invested:
            self._decide_to_invest()
        else:
            self._decide_to_stay_or_withdraw()

        # 3. Technology transfer (if invested)
        if self.is_invested:
            self._transfer_technology()
            self.years_invested += 1

        # 4. Calculate return
        if self.is_invested:
            self._calculate_return()

    # ══════════════════════════════════════════════════════════════════════════
    # PERCEPTION UPDATE
    # ══════════════════════════════════════════════════════════════════════════

    def _update_perceptions(self):
        """
        Update investor's perception of MFU conditions.
        Information lag — investors respond to conditions from 1-3 years ago.
        This creates realistic market overreactions and underreactions.
        """

        lag = self.information_lag
        history = self.model.shared_data.get("annual_history", [])

        if len(history) >= lag:
            past_data = history[-lag]
            self.perceived_corruption = past_data.get(
                "corruption_index", self.perceived_corruption
            )
            self.perceived_stability = past_data.get(
                "stability_index", self.perceived_stability
            )
            self.perceived_rule_of_law = past_data.get(
                "iig_effectiveness", self.perceived_rule_of_law
            )
        else:
            # No history yet — use current with noise
            self.perceived_corruption = max(0.0, min(1.0,
                self.model.shared_data.get("corruption_index", 0.65) +
                random.gauss(0, 0.05)
            ))
            self.perceived_stability = max(0.0, min(1.0,
                1.0 - self.model.shared_data.get("coup_risk", 0.30) +
                random.gauss(0, 0.05)
            ))
            self.perceived_rule_of_law = max(0.0, min(1.0,
                self.model.shared_data.get("iig_effectiveness", 0.40) +
                random.gauss(0, 0.05)
            ))

    # ══════════════════════════════════════════════════════════════════════════
    # INVESTMENT DECISIONS
    # ══════════════════════════════════════════════════════════════════════════

    def _decide_to_invest(self):
        """
        Decision to enter the MFU market.
        Satisficing — invests when conditions exceed personal thresholds.
        """

        conditions_met = (
            self.perceived_corruption < self.corruption_threshold and
            self.perceived_stability > self.stability_threshold and
            self.perceived_rule_of_law > self.min_iig_effectiveness
        )

        if not conditions_met:
            return

        # Additional check — sector-specific
        if self.is_strategic_sector:
            if self.perceived_rule_of_law < 0.50:
                return  # strategic sectors need stronger rule of law

        # Invest
        investment_amount = self.capital_available * random.uniform(0.20, 0.60)
        self.capital_invested = investment_amount
        self.current_ownership_pct = min(
            self.max_ownership,
            random.uniform(0.10, self.max_ownership)
        )
        self.is_invested = True
        self.investment_year = self.model.current_year

        # Update model FDI tracking
        self.model.shared_data["fdi_inflow"] = (
            self.model.shared_data.get("fdi_inflow", 0.0) + investment_amount
        )
        self.model.shared_data["active_foreign_investors"] = (
            self.model.shared_data.get("active_foreign_investors", 0) + 1
        )

        self.investment_decisions.append({
            "type": "invest",
            "amount": investment_amount,
            "sector": self.sector,
            "year": self.model.current_year,
            "perceived_corruption": self.perceived_corruption,
            "perceived_stability": self.perceived_stability
        })

    def _decide_to_stay_or_withdraw(self):
        """
        Annual decision — stay invested or withdraw capital.
        Withdrawal triggered by deteriorating conditions.
        """

        # Withdrawal triggers
        withdraw_triggers = [
            self.perceived_corruption > self.corruption_threshold * 1.30,
            self.perceived_stability < self.stability_threshold * 0.70,
            self.model.shared_data.get("coup_risk", 0.0) > 0.40,
            self.model.shared_data.get("rights_violated", False)
        ]

        if any(withdraw_triggers):
            if random.random() < 0.40:  # not all investors leave immediately
                self._withdraw_investment("conditions_deteriorated")
                return

        # Expand investment if conditions improving
        if (self.perceived_corruption < self.corruption_threshold * 0.70 and
                self.perceived_stability > self.stability_threshold * 1.20):
            expansion = self.capital_available * random.uniform(0.05, 0.15)
            self.capital_invested += expansion
            self.model.shared_data["fdi_inflow"] = (
                self.model.shared_data.get("fdi_inflow", 0.0) + expansion
            )

    def _withdraw_investment(self, reason: str):
        """Withdraw capital from MFU market."""

        self.capital_withdrawn = self.capital_invested
        self.is_invested = False
        self.capital_invested = 0.0
        self.current_ownership_pct = 0.0

        self.model.shared_data["fdi_outflow"] = (
            self.model.shared_data.get("fdi_outflow", 0.0) +
            self.capital_withdrawn
        )
        self.model.shared_data["active_foreign_investors"] = max(
            0,
            self.model.shared_data.get("active_foreign_investors", 0) - 1
        )

        self.investment_decisions.append({
            "type": "withdraw",
            "amount": self.capital_withdrawn,
            "reason": reason,
            "year": self.model.current_year
        })

    # ══════════════════════════════════════════════════════════════════════════
    # TECHNOLOGY TRANSFER (Article 10 — knowledge economy loop)
    # ══════════════════════════════════════════════════════════════════════════

    def _transfer_technology(self):
        """
        Technology transfer to local partners.
        Article 10.3 — 51% local ownership in strategic sectors
        incentivizes knowledge transfer as part of joint ventures.
        Feeds Loop E2 — Foreign Investment to PhD Economy.
        """

        if not self.is_strategic_sector:
            base_transfer = 0.005  # open sectors transfer less
        else:
            # Strategic sectors with local ownership = more transfer
            base_transfer = self.current_ownership_pct * 0.02

        transfer_amount = base_transfer * self.capital_invested * 0.001
        self.technology_transferred += transfer_amount

        # Update state knowledge capital
        for state_id in self.model.states:
            self.model.states[state_id]["knowledge_capital"] = (
                self.model.states[state_id].get("knowledge_capital", 0.0) +
                transfer_amount / len(self.model.states)
            )

    def _calculate_return(self):
        """Calculate annual return on investment."""

        base_return_rate = random.uniform(0.05, 0.15)
        stability_bonus = self.perceived_stability * 0.05
        rule_of_law_bonus = self.perceived_rule_of_law * 0.03

        self.annual_return = self.capital_invested * (
            base_return_rate + stability_bonus + rule_of_law_bonus
        )
        self.cumulative_return += self.annual_return

    def get_state_dict(self) -> Dict:
        return {
            "id": self.unique_id,
            "investor_type": self.investor_type,
            "sector": self.sector,
            "is_strategic": self.is_strategic_sector,
            "capital_invested": round(self.capital_invested, 2),
            "is_invested": self.is_invested,
            "years_invested": self.years_invested,
            "technology_transferred": round(self.technology_transferred, 4),
            "perceived_corruption": round(self.perceived_corruption, 4),
            "perceived_stability": round(self.perceived_stability, 4),
            "compliant": self.compliant
        }

    def __repr__(self) -> str:
        return (
            f"ForeignInvestorAgent(id={self.unique_id}, "
            f"sector={self.sector}, "
            f"invested={self.is_invested}, "
            f"capital={self.capital_invested:.0f})"
        )


# ══════════════════════════════════════════════════════════════════════════════
# NEIGHBORING STATE AGENT
# ══════════════════════════════════════════════════════════════════════════════

class NeighboringStateAgent(Agent):
    """
    Neighboring State — external geopolitical actor.

    Represents Myanmar's neighbors: China, India, Thailand, Bangladesh,
    Laos (simplified to 4 agents for MSc simulation).

    Responds to:
    - MFU ethnic tension (supports insurgents if relations sour)
    - Trade volume (economic incentive for stable relations)
    - Border security (ROE Article 17 affects border dynamics)
    - Scorched earth doctrine (deters invasion attempts)

    Key dynamic: Neighboring states have incentive to maintain stable
    MFU — economic interdependence is the primary peace mechanism.
    """

    def __init__(
        self,
        unique_id: int,
        model,
        country_name: str,
        relationship_score: float,
        trade_volume: float,
        border_tension: float,
        supports_ethnic_groups: List[str]
    ):
        super().__init__(unique_id, model)

        # ── IDENTITY ──────────────────────────────────────────────────────────
        self.country_name = country_name
        self.relationship_score = relationship_score  # 0=hostile, 1=friendly
        self.trade_volume = trade_volume
        self.border_tension = border_tension
        self.supports_ethnic_groups = supports_ethnic_groups

        # ── FOREIGN POLICY ATTRIBUTES ─────────────────────────────────────────
        self.economic_interest = random.uniform(0.30, 0.80)
        self.territorial_interest = random.uniform(0.10, 0.50)
        self.ethnic_solidarity = random.uniform(0.10, 0.60)

        # ── MILITARY POSTURE ──────────────────────────────────────────────────
        self.military_threat_level = 0.0
        self.invasion_probability = 0.0
        self.insurgent_support_level = 0.0

        # ── SANCTIONS CAPACITY ────────────────────────────────────────────────
        self.has_sanctioned = False
        self.sanction_year = None

        # ── TRACKING ──────────────────────────────────────────────────────────
        self.annual_trade_history: List[float] = []
        self.relationship_history: List[float] = []

    # ══════════════════════════════════════════════════════════════════════════
    # MESA STEP
    # ══════════════════════════════════════════════════════════════════════════

    def step(self):
        """Annual neighboring state update."""

        # 1. Update relationship based on MFU conditions
        self._update_relationship()

        # 2. Trade decision
        self._update_trade()

        # 3. Security posture decision
        self._assess_security_posture()

        # 4. Ethnic insurgent support decision
        self._decide_insurgent_support()

        # 5. Sanction decision
        self._decide_sanctions()

        # Track history
        self.annual_trade_history.append(self.trade_volume)
        self.relationship_history.append(self.relationship_score)

    # ══════════════════════════════════════════════════════════════════════════
    # RELATIONSHIP DYNAMICS
    # ══════════════════════════════════════════════════════════════════════════

    def _update_relationship(self):
        """
        Update bilateral relationship score.
        Economic interdependence is primary stabilizer.
        Ethnic tension in border regions is primary destabilizer.
        """

        mfu_stability = self.model.shared_data.get("stability_index", 0.40)
        ethnic_tension = self.model.shared_data.get("ethnic_tension_index", 0.60)
        rights_score = 1.0 - (
            1 if self.model.shared_data.get("rights_violated", False) else 0
        ) * 0.20

        # Economic interdependence improves relations
        trade_effect = min(0.10, self.trade_volume / 10000.0)

        # Ethnic tension in border regions strains relations
        ethnic_effect = -ethnic_tension * self.ethnic_solidarity * 0.10

        # MFU stability improves relations
        stability_effect = mfu_stability * 0.05

        change = trade_effect + ethnic_effect + stability_effect
        self.relationship_score = max(
            0.0, min(1.0, self.relationship_score + change)
        )

    def _update_trade(self):
        """
        Update trade volume based on relationship and MFU economic health.
        """

        mfu_gdp_growth = self.model.shared_data.get("gdp_growth_rate", 0.03)
        stability = self.model.shared_data.get("stability_index", 0.40)

        trade_change = (
            self.relationship_score * 0.05 +
            mfu_gdp_growth * 0.10 +
            stability * 0.05
        ) * self.trade_volume

        # Sanctions reduce trade to zero
        if self.has_sanctioned:
            self.trade_volume = max(0.0, self.trade_volume - self.trade_volume * 0.50)
        else:
            self.trade_volume = max(0.0, self.trade_volume + trade_change)

        self.model.shared_data["total_trade_volume"] = (
            self.model.shared_data.get("total_trade_volume", 0.0) +
            self.trade_volume
        )

    def _assess_security_posture(self):
        """
        Assess military threat level toward MFU.
        Scorched Earth doctrine (Article 17) deters invasion.
        """

        mfu_military_strength = self.model.shared_data.get(
            "military_strength", 0.50
        )

        # Scorched earth deterrence — invasion is too costly
        scorched_earth_deterrence = (
            CONSTITUTION.roe.EXTERNAL_FULL_FORCE *
            mfu_military_strength * 0.80
        )

        # Base threat from territorial interest minus deterrence
        base_threat = (
            self.territorial_interest * 0.30 +
            (1.0 - self.relationship_score) * 0.20
        )

        self.military_threat_level = max(
            0.0,
            base_threat - scorched_earth_deterrence
        )

        # Invasion probability — very low given ROE
        self.invasion_probability = (
            self.military_threat_level * 0.05
        )

        if self.invasion_probability > 0.10:
            self.model.shared_data["external_threat"] = True
            self.model.shared_data["threat_level"] = self.invasion_probability

    def _decide_insurgent_support(self):
        """
        Decide whether to support ethnic insurgent groups.
        Triggered by poor MFU-neighbor relations and ethnic solidarity.
        Article 8.9 — ethnic tension is primary intervention trigger.
        """

        ethnic_tension = self.model.shared_data.get("ethnic_tension_index", 0.60)

        if (self.relationship_score < 0.35 and
                ethnic_tension > 0.65 and
                len(self.supports_ethnic_groups) > 0):

            self.insurgent_support_level = (
                (1.0 - self.relationship_score) *
                self.ethnic_solidarity * 0.50
            )

            # Log insurgent support
            self.model.shared_data.setdefault(
                "external_insurgent_support", []
            ).append({
                "country": self.country_name,
                "support_level": self.insurgent_support_level,
                "ethnic_groups": self.supports_ethnic_groups,
                "year": self.model.current_year
            })
        else:
            self.insurgent_support_level = 0.0

    def _decide_sanctions(self):
        """
        Sanction decision based on rights violations and governance quality.
        Article 2.4 — absolute rights. Rights violations trigger sanctions.
        """

        rights_violated = self.model.shared_data.get("rights_violated", False)
        rights_score = self.model.shared_data.get("rights_score", 1.0)

        if rights_violated and rights_score < 0.50 and not self.has_sanctioned:
            # Sanction probability increases with rights violation severity
            sanction_prob = (1.0 - rights_score) * 0.30
            if random.random() < sanction_prob:
                self.has_sanctioned = True
                self.sanction_year = self.model.current_year
                self.model.shared_data.setdefault(
                    "active_sanctions", []
                ).append({
                    "country": self.country_name,
                    "year": self.model.current_year,
                    "reason": "rights_violations"
                })

        # Lift sanctions if governance improves
        if self.has_sanctioned and rights_score > 0.70:
            self.has_sanctioned = False
            self.model.shared_data.setdefault(
                "lifted_sanctions", []
            ).append({
                "country": self.country_name,
                "year": self.model.current_year
            })

    def get_state_dict(self) -> Dict:
        return {
            "id": self.unique_id,
            "country": self.country_name,
            "relationship_score": round(self.relationship_score, 4),
            "trade_volume": round(self.trade_volume, 2),
            "border_tension": round(self.border_tension, 4),
            "military_threat_level": round(self.military_threat_level, 4),
            "invasion_probability": round(self.invasion_probability, 4),
            "insurgent_support": round(self.insurgent_support_level, 4),
            "has_sanctioned": self.has_sanctioned
        }

    def __repr__(self) -> str:
        return (
            f"NeighboringStateAgent(country={self.country_name}, "
            f"relationship={self.relationship_score:.3f}, "
            f"trade={self.trade_volume:.0f}, "
            f"threat={self.military_threat_level:.3f})"
        )


# ══════════════════════════════════════════════════════════════════════════════
# INTERNATIONAL ORGANIZATION AGENT
# ══════════════════════════════════════════════════════════════════════════════

class InternationalOrgAgent(Agent):
    """
    International Organization — aid, conditionality, monitoring.

    Represents: UN agencies, World Bank, IMF, ASEAN, bilateral donors.

    Responds to:
    - Human rights record (absolute rights violations = aid reduction)
    - Governance quality (merit system = positive signal)
    - Corruption index (IIG effectiveness = positive signal)
    - Transparency (Analysis Council publications = positive signal)

    Key dynamic: International orgs provide legitimacy and capital
    that accelerates north star trajectory. Their withdrawal signals
    global concern and reduces foreign investment confidence.
    """

    def __init__(
        self,
        unique_id: int,
        model,
        org_name: str,
        org_type: str,
        aid_budget: float,
        conditionality_strength: float
    ):
        super().__init__(unique_id, model)

        # ── IDENTITY ──────────────────────────────────────────────────────────
        self.org_name = org_name
        self.org_type = org_type  # development / humanitarian / financial / rights
        self.aid_budget = aid_budget
        self.conditionality_strength = conditionality_strength

        # ── ENGAGEMENT STATE ──────────────────────────────────────────────────
        self.is_engaged = True
        self.current_aid_disbursed = 0.0
        self.aid_suspended = False
        self.suspension_year = None
        self.engagement_score = random.uniform(0.40, 0.70)

        # ── MONITORING ────────────────────────────────────────────────────────
        self.rights_violations_logged: int = 0
        self.governance_assessments: List[Dict] = []
        self.public_statements: List[str] = []

        # ── CONDITIONALITY ────────────────────────────────────────────────────
        self.conditions: List[str] = self._set_conditions()
        self.conditions_met: Dict[str, bool] = {c: False for c in self.conditions}

    # ══════════════════════════════════════════════════════════════════════════
    # MESA STEP
    # ══════════════════════════════════════════════════════════════════════════

    def step(self):
        """Annual international org update."""

        # 1. Monitor MFU conditions
        self._monitor_conditions()

        # 2. Assess conditionality compliance
        self._assess_compliance()

        # 3. Disburse or suspend aid
        self._disburse_aid()

        # 4. Public statement based on assessment
        self._issue_public_statement()

    # ══════════════════════════════════════════════════════════════════════════
    # MONITORING AND AID
    # ══════════════════════════════════════════════════════════════════════════

    def _monitor_conditions(self):
        """Monitor MFU governance and rights conditions."""

        rights_violated = self.model.shared_data.get("rights_violated", False)
        corruption_index = self.model.shared_data.get("corruption_index", 0.65)
        iig_effectiveness = self.model.shared_data.get("iig_effectiveness", 0.40)

        if rights_violated:
            self.rights_violations_logged += 1

        assessment = {
            "year": self.model.current_year,
            "rights_violations": rights_violated,
            "corruption_index": corruption_index,
            "iig_effectiveness": iig_effectiveness,
            "governance_quality": (
                iig_effectiveness * 0.40 +
                (1.0 - corruption_index) * 0.40 +
                self.model.shared_data.get("merit_system_integrity", 0.50) * 0.20
            )
        }
        self.governance_assessments.append(assessment)

        # Update engagement score
        self.engagement_score = (
            assessment["governance_quality"] * 0.60 +
            (0.0 if rights_violated else 0.20) +
            self.model.shared_data.get("stability_index", 0.30) * 0.20
        )

    def _assess_compliance(self):
        """Assess whether MFU meets conditionality requirements."""

        corruption = self.model.shared_data.get("corruption_index", 0.65)
        rights = not self.model.shared_data.get("rights_violated", False)
        merit = self.model.shared_data.get("merit_system_integrity", 0.50)

        self.conditions_met = {
            "corruption_below_threshold": corruption < 0.50,
            "rights_not_violated": rights,
            "merit_system_operational": merit > 0.60,
            "iig_active": self.model.shared_data.get(
                "iig_effectiveness", 0.0
            ) > 0.40,
            "transparency_published": len(
                self.model.shared_data.get("published_methodologies", [])
            ) > 0
        }

        conditions_met_count = sum(self.conditions_met.values())
        total_conditions = len(self.conditions_met)
        compliance_rate = conditions_met_count / total_conditions

        # Suspend aid if compliance too low
        if compliance_rate < 0.40 and not self.aid_suspended:
            self.aid_suspended = True
            self.suspension_year = self.model.current_year
        elif compliance_rate > 0.70 and self.aid_suspended:
            self.aid_suspended = False

    def _disburse_aid(self):
        """Disburse aid based on compliance and engagement."""

        if self.aid_suspended or not self.is_engaged:
            self.current_aid_disbursed = 0.0
            return

        compliance_rate = sum(self.conditions_met.values()) / len(self.conditions_met)
        disbursement = self.aid_budget * compliance_rate * self.engagement_score

        self.current_aid_disbursed = disbursement

        # Add to federal development fund
        self.model.shared_data["federal_dev_fund"] = (
            self.model.shared_data.get("federal_dev_fund", 0.0) +
            disbursement * 0.60  # 60% to federal fund
        )

        # Track total aid
        self.model.shared_data["total_aid_received"] = (
            self.model.shared_data.get("total_aid_received", 0.0) +
            disbursement
        )

    def _issue_public_statement(self):
        """
        Issue public statements based on governance assessment.
        Positive statements improve foreign investor confidence.
        Negative statements reduce FDI probability.
        """

        if not self.governance_assessments:
            return

        latest = self.governance_assessments[-1]
        governance_quality = latest.get("governance_quality", 0.50)

        if governance_quality > 0.70:
            statement = "positive_endorsement"
            # Boosts foreign investor confidence
            self.model.shared_data["intl_confidence_signal"] = min(
                1.0,
                self.model.shared_data.get("intl_confidence_signal", 0.50) + 0.05
            )
        elif governance_quality < 0.35:
            statement = "negative_criticism"
            # Reduces foreign investor confidence
            self.model.shared_data["intl_confidence_signal"] = max(
                0.0,
                self.model.shared_data.get("intl_confidence_signal", 0.50) - 0.08
            )
        else:
            statement = "neutral_monitoring"

        self.public_statements.append({
            "year": self.model.current_year,
            "statement": statement,
            "governance_quality": governance_quality
        })

    def _set_conditions(self) -> List[str]:
        """Set conditionality requirements based on org type."""
        base_conditions = [
            "corruption_below_threshold",
            "rights_not_violated",
            "merit_system_operational"
        ]
        if self.org_type in ["development", "financial"]:
            base_conditions += ["iig_active", "transparency_published"]
        return base_conditions

    def get_state_dict(self) -> Dict:
        return {
            "id": self.unique_id,
            "org_name": self.org_name,
            "org_type": self.org_type,
            "engagement_score": round(self.engagement_score, 4),
            "aid_disbursed": round(self.current_aid_disbursed, 2),
            "aid_suspended": self.aid_suspended,
            "rights_violations_logged": self.rights_violations_logged,
            "conditions_met_count": sum(self.conditions_met.values())
        }

    def __repr__(self) -> str:
        return (
            f"InternationalOrgAgent(org={self.org_name}, "
            f"type={self.org_type}, "
            f"engaged={self.is_engaged}, "
            f"suspended={self.aid_suspended})"
        )


# ══════════════════════════════════════════════════════════════════════════════
# ILLICIT NETWORK AGENT
# ══════════════════════════════════════════════════════════════════════════════

class IllicitNetworkAgent(Agent):
    """
    Illicit Network — smuggling, black market, corruption exploitation.

    Represents: jade smugglers, drug networks, illicit resource traders,
    corrupt business networks exploiting governance gaps.

    Expands when:
    - IIG effectiveness drops (less detection risk)
    - Corruption index rises (normalized environment)
    - State governance quality falls

    Contracts when:
    - Total Ruin Protocol fires (high-profile busts)
    - IIG effectiveness rises
    - Shame Register grows (deterrence)

    Key dynamic: Illicit networks are the primary stress test of the
    MFU's economic governance. They directly exploit the gaps between
    Article 10.12 (no black money) and IIG enforcement capacity.
    """

    def __init__(
        self,
        unique_id: int,
        model,
        network_type: str,
        state_id: str,
        network_size: float,
        resource_type: str
    ):
        super().__init__(unique_id, model)

        # ── IDENTITY ──────────────────────────────────────────────────────────
        self.network_type = network_type  # jade / drugs / resource / financial
        self.state_id = state_id
        self.resource_type = resource_type
        self.network_size = network_size  # 0.0 to 1.0

        # ── OPERATIONS ────────────────────────────────────────────────────────
        self.annual_revenue = network_size * random.uniform(10000, 100000)
        self.tax_evaded = 0.0
        self.is_active = True
        self.detected = False
        self.detection_year = None

        # ── RISK ASSESSMENT ───────────────────────────────────────────────────
        self.risk_tolerance = random.uniform(0.40, 0.80)
        self.iig_evasion_capability = random.uniform(0.20, 0.70)
        self.corruption_of_officials = 0.0

        # ── TRACKING ──────────────────────────────────────────────────────────
        self.years_active = 0
        self.total_revenue: float = 0.0
        self.busts_survived: int = 0

    # ══════════════════════════════════════════════════════════════════════════
    # MESA STEP
    # ══════════════════════════════════════════════════════════════════════════

    def step(self):
        """Annual illicit network update."""

        if not self.is_active:
            return

        # 1. Assess operating environment
        self._assess_risk()

        # 2. Operate (generate illicit revenue)
        self._operate()

        # 3. Attempt to corrupt officials
        self._attempt_official_corruption()

        # 4. Check for IIG detection
        self._check_detection()

        # 5. Expand or contract based on environment
        self._adjust_network_size()

        self.years_active += 1

    # ══════════════════════════════════════════════════════════════════════════
    # OPERATIONS
    # ══════════════════════════════════════════════════════════════════════════

    def _assess_risk(self):
        """Assess operating risk from IIG and governance quality."""

        iig_effectiveness = self.model.shared_data.get("iig_effectiveness", 0.40)
        state_corruption = self.model.states.get(
            self.state_id, {}
        ).get("corruption_level", 0.60)

        # Operating risk
        self.operating_risk = (
            iig_effectiveness * 0.50 +
            (1.0 - state_corruption) * 0.30 +
            len(self.model.shared_data.get("shame_register", [])) * 0.01
        )

        # Too risky — suspend operations
        if self.operating_risk > self.risk_tolerance:
            self.is_active = False

    def _operate(self):
        """Generate illicit revenue — evade tax (Article 10.12 violation)."""

        if not self.is_active:
            return

        # Revenue proportional to network size and environment
        state_corruption = self.model.states.get(
            self.state_id, {}
        ).get("corruption_level", 0.60)

        revenue_multiplier = (
            state_corruption * 0.40 +
            (1.0 - self.model.shared_data.get("iig_effectiveness", 0.40)) * 0.40 +
            self.network_size * 0.20
        )

        self.annual_revenue = self.network_size * 50000 * revenue_multiplier
        self.tax_evaded += self.annual_revenue  # all revenue is tax evasion
        self.total_revenue += self.annual_revenue

        # Update state black economy estimate
        self.model.shared_data["black_economy_volume"] = (
            self.model.shared_data.get("black_economy_volume", 0.0) +
            self.annual_revenue
        )

    def _attempt_official_corruption(self):
        """
        Attempt to bribe officials for protection.
        Feeds corruption score of nearby officials.
        """

        if not self.is_active:
            return

        # Bribery attempt probability based on revenue and network size
        bribe_prob = self.network_size * 0.30

        if random.random() < bribe_prob:
            bribe_amount = self.annual_revenue * 0.10
            self.corruption_of_officials += bribe_amount

            self.model.shared_data.setdefault(
                "illicit_bribery_attempts", []
            ).append({
                "network_id": self.unique_id,
                "state": self.state_id,
                "amount": bribe_amount,
                "year": self.model.current_year
            })

    def _check_detection(self):
        """
        Check if IIG detects the network.
        Detection probability scales with IIG effectiveness.
        Article 10.12 — undeclared income = High Treason = Total Ruin.
        """

        iig_effectiveness = self.model.shared_data.get("iig_effectiveness", 0.40)

        detection_prob = (
            iig_effectiveness * 0.40 *
            (1.0 - self.iig_evasion_capability) *
            self.network_size  # larger networks harder to hide
        )

        if random.random() < detection_prob:
            self.detected = True
            self.detection_year = self.model.current_year
            self.is_active = False

            # Log for IIG prosecution
            self.model.shared_data.setdefault(
                "illicit_networks_detected", []
            ).append({
                "network_id": self.unique_id,
                "network_type": self.network_type,
                "state": self.state_id,
                "revenue_seized": self.annual_revenue,
                "tax_evaded": self.tax_evaded,
                "year": self.model.current_year,
                "years_active": self.years_active
            })

            # Seized funds go to federal development fund
            self.model.shared_data["federal_dev_fund"] = (
                self.model.shared_data.get("federal_dev_fund", 0.0) +
                self.total_revenue * 0.70
            )
        else:
            self.busts_survived += 1

    def _adjust_network_size(self):
        """
        Network expands when IIG is weak, contracts when strong.
        Shame Register creates deterrence effect.
        """

        iig_effectiveness = self.model.shared_data.get("iig_effectiveness", 0.40)
        shame_register_size = len(
            self.model.shared_data.get("shame_register", [])
        )

        # Growth factors
        growth = (
            (1.0 - iig_effectiveness) * 0.05 +
            self.model.states.get(
                self.state_id, {}
            ).get("corruption_level", 0.60) * 0.03
        )

        # Deterrence factors
        deterrence = (
            iig_effectiveness * 0.04 +
            shame_register_size * 0.005
        )

        self.network_size = max(
            0.0,
            min(1.0, self.network_size + growth - deterrence)
        )

        if self.network_size < 0.05:
            self.is_active = False

    def get_state_dict(self) -> Dict:
        return {
            "id": self.unique_id,
            "network_type": self.network_type,
            "state_id": self.state_id,
            "network_size": round(self.network_size, 4),
            "is_active": self.is_active,
            "detected": self.detected,
            "annual_revenue": round(self.annual_revenue, 2),
            "tax_evaded": round(self.tax_evaded, 2),
            "years_active": self.years_active,
            "busts_survived": self.busts_survived
        }

    def __repr__(self) -> str:
        return (
            f"IllicitNetworkAgent(id={self.unique_id}, "
            f"type={self.network_type}, "
            f"size={self.network_size:.3f}, "
            f"active={self.is_active}, "
            f"detected={self.detected})"
        )


# ══════════════════════════════════════════════════════════════════════════════
# FOREIGN AGENT POPULATION FACTORY
# ══════════════════════════════════════════════════════════════════════════════

class ForeignPopulation:
    """Factory for creating all foreign agent populations."""

    @staticmethod
    def create_population(model) -> List:
        """
        Create all foreign agents.
        Foreign Investors (50), Neighboring States (4),
        International Orgs (6), Illicit Networks (40).
        """

        foreign = []
        agent_id = 30000

        # Foreign Investors (50)
        investor_types = ["corporate", "sovereign", "venture"]
        sectors = (
            list(CONSTITUTION.economic.STRATEGIC_SECTORS) +
            list(CONSTITUTION.economic.OPEN_SECTORS)
        )
        countries = ["China", "India", "Thailand", "Singapore",
                     "Japan", "South Korea", "USA", "EU", "Australia"]

        for i in range(50):
            sector = random.choice(sectors)
            foreign.append(ForeignInvestorAgent(
                unique_id=agent_id,
                model=model,
                investor_type=random.choice(investor_types),
                home_country=random.choice(countries),
                sector=sector,
                capital=random.uniform(100000, 10000000)
            ))
            agent_id += 1

        # Neighboring States (4 simplified)
        neighbors = [
            {
                "country_name": "China",
                "relationship_score": 0.50,
                "trade_volume": 500000.0,
                "border_tension": 0.35,
                "supports_ethnic_groups": ["Shan", "Kachin"]
            },
            {
                "country_name": "India",
                "relationship_score": 0.55,
                "trade_volume": 200000.0,
                "border_tension": 0.25,
                "supports_ethnic_groups": ["Chin"]
            },
            {
                "country_name": "Thailand",
                "relationship_score": 0.60,
                "trade_volume": 300000.0,
                "border_tension": 0.20,
                "supports_ethnic_groups": ["Karen", "Shan"]
            },
            {
                "country_name": "Bangladesh",
                "relationship_score": 0.45,
                "trade_volume": 80000.0,
                "border_tension": 0.45,
                "supports_ethnic_groups": []
            }
        ]

        for n in neighbors:
            foreign.append(NeighboringStateAgent(
                unique_id=agent_id,
                model=model,
                **n
            ))
            agent_id += 1

        # International Organizations (6)
        orgs = [
            ("UN_Development", "development", 50000.0, 0.60),
            ("World_Bank", "financial", 200000.0, 0.80),
            ("ASEAN", "regional", 30000.0, 0.40),
            ("UN_Rights", "rights", 20000.0, 0.90),
            ("IMF", "financial", 150000.0, 0.85),
            ("Bilateral_Aid", "development", 80000.0, 0.50)
        ]

        for org_name, org_type, budget, conditionality in orgs:
            foreign.append(InternationalOrgAgent(
                unique_id=agent_id,
                model=model,
                org_name=org_name,
                org_type=org_type,
                aid_budget=budget,
                conditionality_strength=conditionality
            ))
            agent_id += 1

        # Illicit Networks (40)
        network_types = ["jade_smuggling", "drug_network",
                         "resource_extraction", "financial_illicit"]
        states = list(CONSTITUTION.simulation.SIMULATION_STATES)
        resource_types = ["jade", "teak", "rare_earth", "drug", "cash"]

        for i in range(40):
            foreign.append(IllicitNetworkAgent(
                unique_id=agent_id,
                model=model,
                network_type=random.choice(network_types),
                state_id=random.choice(states),
                network_size=random.uniform(0.05, 0.60),
                resource_type=random.choice(resource_types)
            ))
            agent_id += 1

        return foreign


# ══════════════════════════════════════════════════════════════════════════════
# QUICK TEST
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":

    print("Testing Foreign Agents...")

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
                    "gdp": 1000.0,
                    "knowledge_capital": 0.0
                }
                for s in ["bamar_central", "shan_eastern",
                          "karen_southern", "kachin_northern"]
            }
            self.shared_data = {
                "corruption_index": 0.72,
                "stability_index": 0.30,
                "iig_effectiveness": 0.40,
                "coup_risk": 0.20,
                "rights_violated": False,
                "rights_score": 0.70,
                "ethnic_tension_index": 0.65,
                "gdp_growth_rate": 0.02,
                "military_strength": 0.50,
                "shame_register": [],
                "federal_dev_fund": 0.0,
                "fdi_inflow": 0.0,
                "fdi_outflow": 0.0,
                "active_foreign_investors": 0,
                "total_trade_volume": 0.0,
                "black_economy_volume": 0.0,
                "total_aid_received": 0.0,
                "intl_confidence_signal": 0.50,
                "merit_system_integrity": 0.50,
                "published_methodologies": [],
                "annual_history": [],
                "corruption_acts_log": [],
                "active_investigations": [],
                "prosecution_queue": [],
                "illicit_networks_detected": [],
                "illicit_bribery_attempts": [],
                "active_sanctions": []
            }

        class schedule:
            agents = []

    mock = MockModel()

    # Test Foreign Investor
    print("\nForeign Investor test:")
    investor = ForeignInvestorAgent(
        unique_id=0,
        model=mock,
        investor_type="corporate",
        home_country="Singapore",
        sector="technology",
        capital=1000000.0
    )
    print(f"  {investor}")
    print(f"  Max ownership: {investor.max_ownership:.0%} "
          f"(strategic sector: {investor.is_strategic_sector})")

    # Step with poor conditions — should not invest
    investor.step()
    print(f"  Invested after Year 0 (poor conditions): {investor.is_invested}")

    # Improve conditions — should invest
    mock.shared_data["corruption_index"] = 0.25
    mock.shared_data["stability_index"] = 0.75
    mock.shared_data["iig_effectiveness"] = 0.70
    investor._update_perceptions()
    investor._decide_to_invest()
    print(f"  Invested after improvement: {investor.is_invested}")

    # Test Neighboring State
    print("\nNeighboring State test:")
    neighbor = NeighboringStateAgent(
        unique_id=1,
        model=mock,
        country_name="Thailand",
        relationship_score=0.60,
        trade_volume=300000.0,
        border_tension=0.20,
        supports_ethnic_groups=["Karen"]
    )
    print(f"  {neighbor}")
    neighbor.step()
    print(f"  After step - threat: {neighbor.military_threat_level:.4f}")

    # Test International Org
    print("\nInternational Org test:")
    org = InternationalOrgAgent(
        unique_id=2,
        model=mock,
        org_name="World_Bank",
        org_type="financial",
        aid_budget=200000.0,
        conditionality_strength=0.80
    )
    print(f"  {org}")
    org.step()
    print(f"  Aid disbursed: {org.current_aid_disbursed:.2f}")
    print(f"  Aid suspended: {org.aid_suspended}")

    # Test Illicit Network
    print("\nIllicit Network test:")
    network = IllicitNetworkAgent(
        unique_id=3,
        model=mock,
        network_type="jade_smuggling",
        state_id="kachin_northern",
        network_size=0.40,
        resource_type="jade"
    )
    print(f"  {network}")
    network.step()
    print(f"  Revenue: {network.annual_revenue:.2f}")
    print(f"  Active: {network.is_active}")
    print(f"  Detected: {network.detected}")

    # Test population factory
    print("\nForeign Population factory test:")
    mock.shared_data["corruption_index"] = 0.72  # reset
    mock.shared_data["stability_index"] = 0.30
    population = ForeignPopulation.create_population(mock)
    type_dist = {}
    for a in population:
        t = type(a).__name__
        type_dist[t] = type_dist.get(t, 0) + 1
    for t, count in sorted(type_dist.items()):
        print(f"  {t:35s}: {count}")
    print(f"\nTotal foreign agents: {len(population)}")

    print("\nforeign.py loaded successfully")