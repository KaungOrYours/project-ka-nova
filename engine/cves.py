"""
Ka-Nova Phase 3 — CVES (Constitutional Validation and Emergence Score)
========================================================================
4-layer validation pipeline for elite agent decisions.
Imported and called by engine/elite_agents_v3.py after each agent step.

L1 — Structural integrity: XML regex + Pydantic schema, reprompt up to 3 retries
L2 — Constitutional constraint: active scenario constitution check, reprompt on violation
L3 — Consensus + theory alignment: variance check, Acemoglu/Robinson, Lijphart scores
L4 — Statistical plausibility: 3-sigma vs rolling annual_history baseline

Output files:
    results_phase3/cves_violations.jsonl  — L2 violations
    results_phase3/cves_scores.jsonl      — per-decision L1-L4 scores

Author: Samsul Jahith (co-author)
"""

from __future__ import annotations

import json
import logging
import numpy as np
from pathlib import Path
from typing import Callable

logger = logging.getLogger("ka_nova.cves")

try:
    from pydantic import BaseModel, Field, field_validator
    PYDANTIC_AVAILABLE = True
except ImportError:
    PYDANTIC_AVAILABLE = False
    logger.warning("Pydantic not available — L1 schema validation uses lightweight checks")

from config.constitution import CONSTITUTION

RESULTS_DIR = Path("results_phase3")

# L4 behaviour — CONFIRM WITH KAUNG: the two handoff docs conflict on this.
# DEFAULT = "flag" (consistent with emergence claim — outliers may be real).
# Change this one line to "strip" if Kaung says strip-and-failsafe.
L4_MODE = "flag"   # "flag" = log only, keep decision
                    # "strip" = clamp decision to 2-sigma range


# ── Pydantic schema for L1 structural validation ──────────────────────────────
if PYDANTIC_AVAILABLE:
    class AgentDecisionSchema(BaseModel):
        budget_weight:  float = Field(default=0.60)
        ethnic_weights: list  = Field(default_factory=lambda: [1.0] * 8)
        coup_signal:    bool  = False
        reason:         str   = ""

        @field_validator("budget_weight")
        @classmethod
        def clamp_bw(cls, v: float) -> float:
            return float(np.clip(float(v), 0.0, 1.0))

        @field_validator("ethnic_weights")
        @classmethod
        def validate_ew(cls, v: list) -> list:
            if len(v) != 8:
                raise ValueError(f"ethnic_weights must have exactly 8 elements, got {len(v)}")
            return [float(np.clip(w, 0.3, 3.0)) for w in v]
else:
    AgentDecisionSchema = None


# ── JSONL helpers ─────────────────────────────────────────────────────────────
def _write_violation(row: dict) -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    with open(RESULTS_DIR / "cves_violations.jsonl", "a") as f:
        f.write(json.dumps(row) + "\n")


def _write_score(row: dict) -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    with open(RESULTS_DIR / "cves_scores.jsonl", "a") as f:
        f.write(json.dumps(row) + "\n")


# ── CVES ──────────────────────────────────────────────────────────────────────
class CVES:
    """
    Constitutional Validation and Emergence Score pipeline.
    Instantiated inside EliteAgentLayerV3.__init__().
    """

    def __init__(self, llm=None, constitution=None):
        self.llm          = llm
        self.constitution = constitution or CONSTITUTION

    # ── L1: Structural integrity ───────────────────────────────────────────────
    def l1_parse(
        self,
        raw_text:     str,
        agent_role:   str,
        system_prompt:str,
        user_message: str,
        invoke_fn:    Callable[[str, str], str] | None = None,
    ) -> dict:
        """
        Parse and validate LLM output.
        On schema failure: reprompt up to 3 times. Returns defaults on persistent failure.

        Returns a dict with the decision fields plus:
            _l1_parse_failure: bool — True if all retries failed (recoverable structural issue)
            _l1_resolved_text: str  — the final raw text that was successfully parsed (or last attempt)
        """
        # Lazy import avoids circular dependency at module load time
        from engine.elite_agents_v3 import parse_decision, ROLE_DEFAULTS

        attempt_text = raw_text
        last_text = raw_text
        for attempt in range(3):
            decision = parse_decision(attempt_text, agent_role)

            if PYDANTIC_AVAILABLE and AgentDecisionSchema is not None:
                try:
                    validated = AgentDecisionSchema(**decision)
                    result    = validated.model_dump()
                    result["_l1_parse_failure"] = False
                    result["_l1_resolved_text"] = attempt_text
                    _write_score({
                        "layer": "L1", "agent": agent_role,
                        "attempt": attempt, "status": "pass",
                    })
                    return result
                except Exception as exc:
                    if attempt < 2 and invoke_fn and self.llm:
                        correction_msg = (
                            f"Your previous response failed validation: {exc}\n"
                            "Respond with ONLY a <DECISION>{{...}}</DECISION> block. "
                            "Ensure: budget_weight is 0.0-1.0, ethnic_weights has exactly 8 floats, "
                            "coup_signal is true or false.\n\n" + user_message
                        )
                        try:
                            attempt_text = invoke_fn(system_prompt, correction_msg)
                            last_text = attempt_text
                            continue
                        except Exception:
                            break
                    else:
                        _write_score({
                            "layer": "L1", "agent": agent_role,
                            "attempt": attempt, "status": "fail",
                            "reason": str(exc)[:200],
                        })
                        break
            else:
                # Lightweight checks when Pydantic unavailable
                bw = decision.get("budget_weight", 0.5)
                ew = decision.get("ethnic_weights", [])
                if 0.0 <= bw <= 1.0 and len(ew) == 8:
                    decision["_l1_parse_failure"] = False
                    decision["_l1_resolved_text"] = attempt_text
                    return decision
                break

        default = ROLE_DEFAULTS.get(agent_role, ROLE_DEFAULTS["chancellor"]).copy()
        default["reason"] = "L1 parse failed — role default applied"
        default["_l1_parse_failure"] = True
        default["_l1_resolved_text"] = last_text
        return default

    # ── L2: Constitutional constraint ─────────────────────────────────────────
    def l2_constitutional(
        self,
        decision:      dict,
        raw_text:      str,
        agent_role:    str,
        scenario:      str,
        year:          int,
        shared_data:   dict,
        system_prompt: str,
        user_message:  str,
        invoke_fn:     Callable[[str, str], str] | None = None,
    ) -> dict:
        """
        Check decision against the active scenario's constitution.
        On violation: raise flag, inject breached article, reprompt once.
        Log all violations to cves_violations.jsonl.
        """
        run_id     = shared_data.get("run_id", 0)
        violations = self._find_violations(decision, scenario, shared_data)

        if not violations:
            return decision

        original  = dict(decision)
        corrected = dict(decision)

        for viol in violations:
            if viol["field"] == "coup_signal":
                corrected["coup_signal"] = False
            elif viol["field"] == "budget_weight":
                corrected["budget_weight"] = float(
                    np.clip(decision.get("budget_weight", 0.5), 0.0, 1.0)
                )

            _write_violation({
                "year":            year,
                "scenario":        scenario,
                "agent":           agent_role,
                "layer":           "L2",
                "violation_type":  viol["type"],
                "original_output": {
                    "coup_signal":   original.get("coup_signal"),
                    "budget_weight": round(original.get("budget_weight", 0.5), 4),
                },
                "corrected_output": {
                    "coup_signal":   corrected.get("coup_signal"),
                    "budget_weight": round(corrected.get("budget_weight", 0.5), 4),
                },
                "article_injected": viol["article"],
                "reason":           viol["reason"],
            })
            logger.warning(
                f"L2 [scenario={scenario} Y{year} {agent_role}] "
                f"{viol['type']} — {viol['article']}"
            )

        # Reprompt once with injected article if LLM available
        if invoke_fn and self.llm and violations:
            articles = "; ".join(v["article"] for v in violations)
            reasons  = "; ".join(v["reason"]  for v in violations)
            correction_msg = (
                f"CONSTITUTIONAL VIOLATION DETECTED.\n"
                f"Your decision violated: {articles}\n"
                f"Reason: {reasons}\n"
                f"Revise your decision to comply with the constitutional constraints.\n\n"
                + user_message
            )
            try:
                from engine.elite_agents_v3 import parse_decision
                revised_raw  = invoke_fn(system_prompt, correction_msg)
                revised      = parse_decision(revised_raw, agent_role)
                if not self._find_violations(revised, scenario, shared_data):
                    return revised
            except Exception as e:
                logger.warning(f"L2 reprompt failed ({e}) — applying corrected defaults")

        return corrected

    def _find_violations(
        self, decision: dict, scenario: str, shared_data: dict
    ) -> list[dict]:
        """Return list of constitutional violations in the decision."""
        violations = []
        const = self.constitution

        if scenario == "A":
            # Article 9.4: coup is highest treason under MFU
            if decision.get("coup_signal", False):
                violations.append({
                    "field":   "coup_signal",
                    "type":    "coup_signal_under_mfu_safeguards",
                    "article": "Article 9.4",
                    "reason":  (
                        f"MFU Scenario A — coup suppressed by safeguards. "
                        f"COUP_TRIGGER_LOYALTY={const.military.COUP_TRIGGER_LOYALTY}, "
                        f"COUP_HIGHEST_TREASON={const.military.COUP_HIGHEST_TREASON}"
                    ),
                })
            # Article 2.4: rights are absolute, never suspendable
            if decision.get("rights_violation", False):
                violations.append({
                    "field":   "rights_violation",
                    "type":    "rights_violation_under_mfu",
                    "article": "Article 2.4",
                    "reason":  (
                        f"Rights are absolute (RIGHTS_SUSPENDABLE="
                        f"{const.rights.RIGHTS_SUSPENDABLE})"
                    ),
                })
        # Scenario C: military constitution — coup is constitutionally permitted, no L2 block

        # Both scenarios: budget_weight must be in [0, 1]
        bw = decision.get("budget_weight", 0.5)
        if not (0.0 <= float(bw) <= 1.0):
            violations.append({
                "field":   "budget_weight",
                "type":    "budget_weight_out_of_range",
                "article": "Article 8.6",
                "reason":  f"budget_weight={bw:.3f} outside [0, 1]",
            })

        return violations

    # ── L3: Consensus + theory alignment ──────────────────────────────────────
    def l3_ensemble(
        self,
        decisions:   list[dict],
        scenario:    str,
        year:        int,
        shared_data: dict,
    ) -> None:
        """
        (a) Variance check: outlier agent → structured negotiation (clamp to 1.5-sigma).
        (b) Theory alignment: Acemoglu/Robinson inclusiveness, Lijphart consensus democracy.
        """
        run_id = shared_data.get("run_id", 0)

        budget_weights = [d.get("budget_weight", 0.5) for d in decisions]
        bw_arr  = np.array(budget_weights)
        bw_mean = float(bw_arr.mean())
        bw_std  = float(bw_arr.std()) if len(bw_arr) > 1 else 0.0

        # Outlier: more than 2 SD from mean in either direction
        outlier_indices = [
            i for i, bw in enumerate(budget_weights)
            if abs(bw - bw_mean) > 2.0 * bw_std and bw_std > 1e-6
        ]
        negotiation_triggered = len(outlier_indices) > 0

        if negotiation_triggered:
            logger.info(
                f"L3 Y{year} scenario={scenario}: {len(outlier_indices)} outlier(s) — "
                f"negotiation loop triggered (clamping to 1.5-sigma)"
            )
            for i in outlier_indices:
                clamped = float(np.clip(
                    decisions[i]["budget_weight"],
                    bw_mean - 1.5 * bw_std,
                    bw_mean + 1.5 * bw_std,
                ))
                decisions[i]["budget_weight"] = clamped
                decisions[i]["reason"] = decisions[i].get("reason", "") + " [L3 negotiated]"

        # ── Theory alignment ──────────────────────────────────────────────────
        ethnic_arrays = np.array(
            [d.get("ethnic_weights", [1.0] * 8) for d in decisions],
            dtype=np.float32,
        )
        mean_ethnic   = ethnic_arrays.mean(axis=0)  # shape (8,)
        # Acemoglu/Robinson: minority mean / Bamar weight > 1 = inclusive
        minority_mean     = float(mean_ethnic[1:].mean())
        bamar_weight      = float(mean_ethnic[0])
        inclusiveness     = minority_mean / max(bamar_weight, 0.01)
        # Lijphart: lower within-agent ethnic variance = more consensus democracy
        ethnic_var        = float(ethnic_arrays.var(axis=1).mean())
        consensus_score   = float(np.clip(1.0 - ethnic_var, 0.0, 1.0))

        gini      = shared_data.get("gini_coefficient", 0.55)
        ar_flag   = inclusiveness < 0.8 or gini > 0.50
        lij_flag  = consensus_score < 0.5

        _write_score({
            "run": run_id, "year": year, "scenario": scenario, "layer": "L3",
            "negotiation_triggered": negotiation_triggered,
            "outlier_count":         len(outlier_indices),
            "bw_mean":               round(bw_mean, 4),
            "bw_std":                round(bw_std, 4),
            "inclusiveness_score":   round(inclusiveness, 4),
            "consensus_score":       round(consensus_score, 4),
            "ar_divergence_flag":    ar_flag,
            "lijphart_flag":         lij_flag,
        })

    # ── L4: Statistical plausibility ──────────────────────────────────────────
    def l4_statistical(
        self,
        decisions:   list[dict],
        shared_data: dict,
        year:        int,
    ) -> None:
        """
        Compare combined budget impact against 3-sigma rolling baseline.
        L4_MODE="flag" logs the outlier and keeps the decision (emergence may be real).
        L4_MODE="strip" clamps to 2-sigma range (apply only if Kaung confirms).
        """
        run_id  = shared_data.get("run_id", 0)
        history = shared_data.get("annual_history", [])
        if len(history) < 3:
            return  # Need at least 3 data points for meaningful baseline

        mean_bw            = float(np.mean([d.get("budget_weight", 0.5) for d in decisions]))
        current_impact     = float(np.clip(mean_bw * 0.15, 0.0, 0.15))
        historical_impacts = [h.get("elite_budget_impact", 0.0) for h in history]

        hist_arr  = np.array(historical_impacts)
        hist_mean = float(hist_arr.mean())
        hist_std  = float(hist_arr.std())

        if hist_std < 1e-6:
            return  # No variance — skip

        z_score = abs(current_impact - hist_mean) / hist_std
        is_outlier = z_score > 3.0

        if is_outlier:
            logger.info(
                f"L4 Y{year}: budget_impact={current_impact:.4f} "
                f"hist_mean={hist_mean:.4f} hist_std={hist_std:.4f} z={z_score:.2f} "
                f"— {'flagged' if L4_MODE == 'flag' else 'stripped'}"
            )
            _write_score({
                "run":                    run_id,
                "year":                   year,
                "layer":                  "L4",
                "outlier_flag":           True,
                "current_budget_impact":  round(current_impact, 4),
                "hist_mean":              round(hist_mean, 4),
                "hist_std":               round(hist_std, 4),
                "z_score":                round(z_score, 4),
                "l4_mode":                L4_MODE,
                "action":                 "flagged" if L4_MODE == "flag" else "stripped",
            })

            if L4_MODE == "strip":
                # Clamp each decision's budget_weight to 2-sigma range
                max_impact = hist_mean + 2.0 * hist_std
                max_bw     = float(np.clip(max_impact / 0.15, 0.0, 1.0))
                for d in decisions:
                    if d.get("budget_weight", 0) > max_bw:
                        d["budget_weight"] = max_bw
                        d["reason"] = d.get("reason", "") + " [L4 stripped]"
