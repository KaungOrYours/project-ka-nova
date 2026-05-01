"""
================================================================================
PROJECT KA-NOVA — agents/institutional.py
Institutional Agents — Automated Constitutional Mechanics
================================================================================
"""

from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import random, hashlib
from typing import Dict, List
from mesa import Agent
from config.constitution import CONSTITUTION


class CentralBankAgent(Agent):
    """Fully independent central bank. Article 10.5. Taylor Rule interest rates."""
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.independent = True
        self.political_direction_accepted = False
        self.interest_rate = 0.08
        self.inflation_rate = 0.12
        self.target_inflation = 0.04
        self.gdp_growth_rate = 0.02
        self.exchange_rate_index = 1.0
        self.foreign_reserve = 1000000.0
        self.annual_reports = []
        self.years_independent = 0

    def step(self):
        self._read_conditions()
        self._set_interest_rate()
        self._update_inflation()
        self._update_exchange_rate()
        self._publish_report()
        self.years_independent += 1

    def _read_conditions(self):
        states = list(self.model.states.values())
        if states:
            self.gdp_growth_rate = sum(s.get("gdp_growth", 0.02) for s in states) / len(states)

    def _set_interest_rate(self):
        inflation_gap = self.inflation_rate - self.target_inflation
        output_gap = self.gdp_growth_rate - 0.05
        taylor = self.target_inflation + 1.5 * inflation_gap + 0.5 * output_gap
        self.interest_rate = max(0.01, min(0.25, self.interest_rate + (taylor - self.interest_rate) * 0.30))
        self.model.shared_data["interest_rate"] = self.interest_rate

    def _update_inflation(self):
        money_effect = random.gauss(0, 0.01)
        gdp_effect = -self.gdp_growth_rate * 0.20
        self.inflation_rate = max(0.0, min(0.30, self.inflation_rate + money_effect + gdp_effect))
        self.model.shared_data["inflation_rate"] = self.inflation_rate

    def _update_exchange_rate(self):
        stability = self.model.shared_data.get("stability_index", 0.30)
        change = stability * 0.02 - self.inflation_rate * 0.30
        self.exchange_rate_index = max(0.30, min(3.0, self.exchange_rate_index + change))
        self.model.shared_data["exchange_rate"] = self.exchange_rate_index

    def _publish_report(self):
        report = {
            "year": self.model.current_year,
            "interest_rate": round(self.interest_rate, 4),
            "inflation_rate": round(self.inflation_rate, 4),
            "gdp_growth": round(self.gdp_growth_rate, 4),
            "exchange_rate": round(self.exchange_rate_index, 4),
            "chambers_can_direct": False
        }
        self.annual_reports.append(report)
        self.model.shared_data["central_bank_report"] = report

    def get_state_dict(self):
        return {"id": self.unique_id, "agent_type": "central_bank",
                "interest_rate": round(self.interest_rate, 4),
                "inflation_rate": round(self.inflation_rate, 4),
                "exchange_rate": round(self.exchange_rate_index, 4),
                "years_independent": self.years_independent}

    def __repr__(self):
        return f"CentralBankAgent(rate={self.interest_rate:.3f}, inflation={self.inflation_rate:.3f})"


class FederalDevFundAgent(Agent):
    """Resource revenue distribution. Article 8.6 — 40/40/20 constitutional split."""
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.state_share = CONSTITUTION.federal.RESOURCE_STATE_SHARE
        self.federal_share = CONSTITUTION.federal.RESOURCE_FEDERAL_DEV_SHARE
        self.ethnic_share = CONSTITUTION.federal.RESOURCE_ETHNIC_DIRECT_SHARE
        self.fund_balance = 0.0
        self.total_received = 0.0
        self.total_distributed = 0.0
        self.gini_coefficient = 0.55
        self.state_gdp_shares = {}
        self.annual_distributions = []

    def step(self):
        self._collect_resource_revenue()
        self._distribute_federal_share()
        self._collect_external_sources()
        self._calculate_gini()
        self._check_triggers()
        self._record_distribution()

    def _collect_resource_revenue(self):
        for state_id, state_data in self.model.states.items():
            revenue = state_data.get("resource_revenue", 0.0)
            if revenue <= 0:
                continue
            state_data["budget"] = state_data.get("budget", 0.0) + revenue * self.state_share
            self.fund_balance += revenue * self.federal_share
            state_data["ethnic_direct_fund"] = (
                state_data.get("ethnic_direct_fund", 0.0) + revenue * self.ethnic_share
            )
            self.total_received += revenue

    def _distribute_federal_share(self):
        states = self.model.states
        if not states or self.fund_balance <= 0:
            return
        per_state = self.fund_balance / len(states)
        for state_data in states.values():
            state_data["budget"] = state_data.get("budget", 0.0) + per_state
            self.total_distributed += per_state
        self.fund_balance = 0.0

    def _collect_external_sources(self):
        seizures = self.model.shared_data.get("total_ruin_seizures_this_year", 0.0)
        if seizures > 0:
            self.fund_balance += seizures
            self.total_received += seizures
            self.model.shared_data["total_ruin_seizures_this_year"] = 0.0

    def _calculate_gini(self):
        states = self.model.states
        if not states:
            return
        total_gdp = sum(s.get("gdp", 100.0) for s in states.values())
        if total_gdp <= 0:
            return
        shares = sorted([s.get("gdp", 100.0) / total_gdp for s in states.values()])
        n = len(shares)
        numerator = sum((2 * (i + 1) - n - 1) * shares[i] for i in range(n))
        self.gini_coefficient = min(1.0, max(0.0, abs(numerator) / (n * sum(shares))))
        self.model.shared_data["gini_coefficient"] = self.gini_coefficient
        for state_id, state_data in states.items():
            self.state_gdp_shares[state_id] = state_data.get("gdp", 100.0) / total_gdp

    def _check_triggers(self):
        triggers = []
        for state_id, share in self.state_gdp_shares.items():
            if share > CONSTITUTION.federal.STATE_GDP_CAP:
                triggers.append({"type": "state_gdp_dominance", "state_id": state_id, "gdp_share": share})
        if self.gini_coefficient > CONSTITUTION.federal.GINI_THRESHOLD:
            triggers.append({"type": "inequality_threshold", "gini": self.gini_coefficient})
        if triggers:
            self.model.shared_data["ecb_triggers"] = triggers
            self.model.shared_data["ecb_active"] = True

    def _record_distribution(self):
        record = {"year": self.model.current_year,
                  "total_received": round(self.total_received, 2),
                  "total_distributed": round(self.total_distributed, 2),
                  "gini_coefficient": round(self.gini_coefficient, 4)}
        self.annual_distributions.append(record)
        self.model.shared_data["dev_fund_report"] = record

    def get_state_dict(self):
        return {"id": self.unique_id, "agent_type": "federal_dev_fund",
                "fund_balance": round(self.fund_balance, 2),
                "total_received": round(self.total_received, 2),
                "gini_coefficient": round(self.gini_coefficient, 4)}

    def __repr__(self):
        return f"FederalDevFundAgent(balance={self.fund_balance:.0f}, gini={self.gini_coefficient:.3f})"


class NationalShameRegisterAgent(Agent):
    """Public permanent blockchain record. Article 15 — unerasable, irremovable."""
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.entries = []
        self.entry_count = 0
        self.total_assets_recorded = 0.0
        self.blockchain_chain = []
        self.corruption_reduction_achieved = 0.0
        self.genesis_hash = hashlib.sha256(b"KA_NOVA_GENESIS").hexdigest()[:16]

    def step(self):
        self._process_new_entries()
        self._broadcast_deterrence()
        self._publish_statistics()

    def _process_new_entries(self):
        for entry in self.model.shared_data.get("shame_register", []):
            if entry.get("registered", False):
                continue
            entry_hash = hashlib.sha256(
                f"{entry.get('official_id')}_{entry.get('year')}".encode()
            ).hexdigest()[:16]
            prev = self.blockchain_chain[-1] if self.blockchain_chain else self.genesis_hash
            block = hashlib.sha256(f"{entry_hash}_{prev}".encode()).hexdigest()[:16]
            self.blockchain_chain.append(block)
            self.entries.append({
                "entry_id": self.entry_count + 1,
                "official_id": entry.get("official_id"),
                "role": entry.get("role"),
                "offence": entry.get("offence"),
                "assets_seized": entry.get("assets_seized", 0.0),
                "conviction_year": entry.get("year"),
                "blockchain_hash": block,
                "permanent": True,
                "expungeable": False
            })
            self.entry_count += 1
            self.total_assets_recorded += entry.get("assets_seized", 0.0)
            entry["registered"] = True

    def _broadcast_deterrence(self):
        if self.entry_count == 0:
            return
        self.model.shared_data["shame_register_size"] = self.entry_count
        reduction = (
            CONSTITUTION.crypto_justice.SHAME_REGISTER_CORRUPTION_REDUCTION *
            0.05 * (self.entry_count ** 0.5)
        )
        self.corruption_reduction_achieved = min(0.40, reduction)
        from agents.official import OfficialAgent
        for agent in self.model.schedule.agents:
            if isinstance(agent, OfficialAgent):
                agent.corruption_tolerance = max(
                    0.0, agent.corruption_tolerance - reduction * 0.10
                )

    def _publish_statistics(self):
        self.model.shared_data["shame_register_stats"] = {
            "year": self.model.current_year,
            "total_entries": self.entry_count,
            "total_assets_seized": round(self.total_assets_recorded, 2),
            "blockchain_length": len(self.blockchain_chain),
            "deterrence_effect": round(self.corruption_reduction_achieved, 4),
            "expungeable": False
        }

    def get_state_dict(self):
        return {"id": self.unique_id, "agent_type": "shame_register",
                "entry_count": self.entry_count,
                "total_assets_recorded": round(self.total_assets_recorded, 2),
                "blockchain_length": len(self.blockchain_chain),
                "corruption_reduction": round(self.corruption_reduction_achieved, 4)}

    def __repr__(self):
        return f"NationalShameRegisterAgent(entries={self.entry_count}, deterrence={self.corruption_reduction_achieved:.4f})"


class TaxSystemAgent(Agent):
    """Progressive tax collection. Articles 10.9-10.12. Dynamic poverty line."""
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.poverty_line = 1000.0
        self.federal_minimum_wage = 800.0
        self.annual_revenue = 0.0
        self.total_revenue = 0.0
        self.compliance_rate = 0.90
        self.evasion_detected_count = 0
        self.poverty_line_history = []

    def step(self):
        self._calculate_poverty_line()
        self._update_minimum_wage()
        self._process_evasion()
        self._update_revenue()

    def _calculate_poverty_line(self):
        gdp_growth = self.model.shared_data.get("gdp_growth_rate", 0.02)
        employment = self.model.shared_data.get("employment_rate", 0.58)
        vacancy = max(0.0, employment - 0.70)
        adjustment = gdp_growth * 0.30 + vacancy * 0.30 + 0.02 * 0.40
        target = self.poverty_line * (1.0 + adjustment)
        self.poverty_line = max(500.0, min(5000.0, self.poverty_line * 0.70 + target * 0.30))
        self.poverty_line_history.append(self.poverty_line)
        self.model.shared_data["poverty_line"] = self.poverty_line

    def _update_minimum_wage(self):
        inflation = self.model.shared_data.get("inflation_rate", 0.08)
        self.federal_minimum_wage *= (1.0 + inflation * 0.50)
        self.model.shared_data["federal_minimum_wage"] = self.federal_minimum_wage
        self.model.shared_data["min_wage_by_age"] = {
            "16_18": self.federal_minimum_wage * 0.60,
            "18_21": self.federal_minimum_wage * 0.80,
            "21_25": self.federal_minimum_wage * 0.90,
            "25_plus": self.federal_minimum_wage
        }

    def _process_evasion(self):
        cases = self.model.shared_data.get("tax_evasion_detected", [])
        for case in cases:
            if not case.get("processed", False):
                self.evasion_detected_count += 1
                self.model.shared_data.setdefault("high_treason_referrals", []).append({
                    "type": "tax_evasion",
                    "citizen_id": case.get("citizen_id"),
                    "year": self.model.current_year,
                    "article": "10.12"
                })
                case["processed"] = True
        total = self.model.shared_data.get("total_citizens", 9500)
        self.compliance_rate = max(0.0, 1.0 - self.evasion_detected_count / max(1, total))
        self.model.shared_data["tax_compliance_rate"] = self.compliance_rate

    def _update_revenue(self):
        self.annual_revenue = self.model.shared_data.get("tax_revenue", 0.0)
        self.total_revenue += self.annual_revenue
        self.model.shared_data["tax_revenue"] = 0.0
        self.model.shared_data["total_tax_revenue"] = self.total_revenue

    def get_state_dict(self):
        return {"id": self.unique_id, "agent_type": "tax_system",
                "poverty_line": round(self.poverty_line, 2),
                "federal_minimum_wage": round(self.federal_minimum_wage, 2),
                "annual_revenue": round(self.annual_revenue, 2),
                "compliance_rate": round(self.compliance_rate, 4)}

    def __repr__(self):
        return f"TaxSystemAgent(poverty_line={self.poverty_line:.0f}, compliance={self.compliance_rate:.3f})"


class EconomicCheckBalanceAgent(Agent):
    """Article 10.8 — three automatic triggers, three simultaneous enforcers."""
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.state_gdp_cap = CONSTITUTION.federal.STATE_GDP_CAP
        self.sector_monopoly_cap = CONSTITUTION.federal.SECTOR_MONOPOLY_CAP
        self.gini_threshold = CONSTITUTION.federal.GINI_THRESHOLD
        self.active_interventions = []
        self.completed_interventions = []
        self.intervention_count = 0
        self.warnings_issued = []
        self.remedies_ordered = []

    def step(self):
        triggers = self._check_triggers()
        self._issue_warnings()
        if triggers:
            self._activate_enforcers(triggers)
        self._progress_interventions()
        self.model.shared_data["ecb_interventions_total"] = self.intervention_count

    def _check_triggers(self):
        triggers = self.model.shared_data.get("ecb_triggers", [])
        self.model.shared_data["ecb_triggers"] = []
        return triggers

    def _issue_warnings(self):
        gini = self.model.shared_data.get("gini_coefficient", 0.55)
        if self.gini_threshold * 0.90 < gini < self.gini_threshold:
            self.warnings_issued.append({
                "type": "gini_approaching",
                "value": gini,
                "year": self.model.current_year
            })

    def _activate_enforcers(self, triggers):
        for trigger in triggers:
            intervention = {
                "id": self.intervention_count + 1,
                "trigger": trigger,
                "year": self.model.current_year,
                "status": "active",
                "enforcers": ["analysis_council", "arbitration_court", "iig"]
            }
            # Enforcer 1 — Analysis Council
            self.model.shared_data.setdefault("analysis_diagnoses", []).append({
                "trigger": trigger["type"],
                "published": True,
                "year": self.model.current_year
            })
            # Enforcer 2 — Arbitration Court remedy
            remedy = {"trigger": trigger["type"], "binding": True, "year": self.model.current_year}
            self.remedies_ordered.append(remedy)
            intervention["remedy"] = remedy
            # Enforcer 3 — IIG investigation
            self.model.shared_data.setdefault("iig_ecb_investigations", []).append({
                "trigger": trigger,
                "year": self.model.current_year,
                "automatic": True
            })
            self.active_interventions.append(intervention)
            self.intervention_count += 1

    def _progress_interventions(self):
        completed = [
            i for i in self.active_interventions
            if self.model.current_year - i["year"] >= 2
        ]
        for i in completed:
            i["status"] = "completed"
            self.active_interventions.remove(i)
            self.completed_interventions.append(i)

    def get_state_dict(self):
        return {"id": self.unique_id, "agent_type": "economic_check_balance",
                "intervention_count": self.intervention_count,
                "active_interventions": len(self.active_interventions),
                "warnings_issued": len(self.warnings_issued)}

    def __repr__(self):
        return f"EconomicCheckBalanceAgent(interventions={self.intervention_count}, active={len(self.active_interventions)})"


class InstitutionalPopulation:
    """Factory — creates all five institutional agents."""

    @staticmethod
    def create_population(model):
        institutions = []
        agent_id = 40000
        institutions.append(CentralBankAgent(agent_id, model)); agent_id += 1
        institutions.append(FederalDevFundAgent(agent_id, model)); agent_id += 1
        institutions.append(NationalShameRegisterAgent(agent_id, model)); agent_id += 1
        institutions.append(TaxSystemAgent(agent_id, model)); agent_id += 1
        institutions.append(EconomicCheckBalanceAgent(agent_id, model)); agent_id += 1
        return institutions


if __name__ == "__main__":
    print("Testing Institutional Agents...")

    class MockSchedule:
        agents = []

    class MockModel:
        def __init__(self):
            self.current_year = 0
            self.schedule = MockSchedule()
            self.states = {
                s: {"gdp": gdp, "gdp_growth": 0.02, "resource_revenue": rev,
                    "budget": 0.0, "ethnic_direct_fund": 0.0}
                for s, gdp, rev in [
                    ("bamar_central", 400.0, 50000.0),
                    ("shan_eastern", 250.0, 80000.0),
                    ("karen_southern", 180.0, 30000.0),
                    ("kachin_northern", 170.0, 40000.0)
                ]
            }
            self.shared_data = {
                "poverty_line": 1000.0, "tax_revenue": 500000.0,
                "shame_register": [], "fdi_inflow": 100000.0, "fdi_outflow": 20000.0,
                "employment_rate": 0.58, "gdp_growth_rate": 0.02,
                "inflation_rate": 0.08, "stability_index": 0.30,
                "gini_coefficient": 0.55, "federal_dev_fund": 0.0,
                "total_ruin_seizures_this_year": 0.0,
                "tax_evasion_detected": [], "ecb_triggers": [],
                "ecb_active": False, "total_citizens": 9500
            }

    mock = MockModel()
    institutions = InstitutionalPopulation.create_population(mock)

    for inst in institutions:
        inst.step()
        print(f"  {inst}")

    print(f"\nGini after distribution: {mock.shared_data.get('gini_coefficient', 0):.4f}")
    print(f"Poverty line: {mock.shared_data.get('poverty_line', 0):.2f}")
    print(f"Interest rate: {mock.shared_data.get('interest_rate', 0):.4f}")
    print(f"Tax revenue processed: {mock.shared_data.get('total_tax_revenue', 0):.2f}")
    print("\ninstitutional.py loaded successfully")