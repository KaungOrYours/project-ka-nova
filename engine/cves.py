"""
Ka-Nova Phase 3 — CVES (Constitutional Validation and Emergence Score)
========================================================================
4-layer validation pipeline for elite agent decisions.
Imported and called by engine/elite_agents_v3.py after each agent step.

L1 — Structural integrity: XML regex + Pydantic schema, reprompt up to 3 retries
L2 — Constitutional constraint: active scenario constitution check, reprompt on violation
L3 — Consensus + theory alignment: variance check, Acemoglu/Robinson, Lijphart scores
L4 — Statistical plausibility: 3-sigma vs rolling annual_history baseline

Output files (bug #18 — namespaced per scenario; the single shared
cves_violations.jsonl/cves_scores.jsonl used to collide across scenarios
run on separate pods, leaving zero audit-trail rows for whichever scenario
lost the race):
    results_phase3/cves_violations_<scenario>.jsonl  — L2 violations
    results_phase3/cves_scores_<scenario>.jsonl      — per-decision L1-L4 scores

Author: Samsul Jahith (co-author)
"""

from __future__ import annotations

import json
import logging
import os
from functools import lru_cache
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

# Honours KA_NOVA_RESULTS_DIR (same as analysis/kpi.py and
# charts/visualize.py) so a throwaway/diagnostic run can be fully
# isolated from the tracked results_phase3/ files instead of
# overwriting them and needing a git checkout afterwards.
RESULTS_DIR = Path(os.getenv("KA_NOVA_RESULTS_DIR", "results_phase3"))

# L4 behaviour — CONFIRM WITH KAUNG: the two handoff docs conflict on this.
# DEFAULT = "flag" (consistent with emergence claim — outliers may be real).
# Change this one line to "strip" if Kaung says strip-and-failsafe.
L4_MODE = "flag"   # "flag" = log only, keep decision
                    # "strip" = clamp decision to 2-sigma range

# ── L2 ablation (Opening 4, 2026-10-21) ───────────────────────────────────────
# The manuscript's Future Work already promises "a targeted ablation of
# individual CVES layers, disabling the constitutional layer (L2) alone while
# leaving the structural, consensus and statistical layers active". This is the
# switch that delivers it, and it is the direct quantitative answer to
# Reviewer 1 pt.3 and Reviewer 2 pt.4 on what the generative layer plus CVES
# actually contribute: run the identical configuration with L2 enforcing and
# with L2 observing, and the KPI difference IS the marginal contribution of
# runtime constitutional enforcement.
#
#   "enforce" (default) — detect, log, correct, reprompt. Published behaviour.
#   "observe"           — detect and log identically, but do NOT correct and do
#                         NOT reprompt. Violating decisions propagate into the
#                         simulation. The audit trail stays complete, so the
#                         ablation run is directly comparable to the enforced
#                         run violation-for-violation.
#   "off"               — do not even detect. No L2 logging. Use only to measure
#                         L2's own compute cost, not for the science ablation.
#
# CRITICAL: "observe" also bypasses the defence-in-depth coup re-suppression at
# aggregation in engine/elite_agents_v3.py. Without that, ablating L2 would
# change nothing observable for the headline coup result, because the second
# lock would silently re-suppress every signal L2 let through, and the ablation
# would misreport L2's contribution as zero.
L2_MODE = os.getenv("CVES_L2_MODE", "enforce").strip().lower()
if L2_MODE not in ("enforce", "observe", "off"):
    raise ValueError(
        f"CVES_L2_MODE must be one of enforce/observe/off, got {L2_MODE!r}"
    )


# ── Ethnic-group count resolution (bug #17) ────────────────────────────────────
def _get_ethnic_group_count(constitution) -> int:
    """
    Resolve the active constitution's real ethnic-group count instead of the
    old hardcoded 8 (Myanmar-only) assumption.

    Canonical field is FederalConfig.ETHNIC_GROUPS, which Myanmar 2008 and
    all 5 new constitutions define directly: Myanmar=8, Pakistan=4,
    South Korea=1, Chile=0, Thailand=0, Germany=0.

    MFU's own config/constitution.py predates that field and never defines
    FederalConfig.ETHNIC_GROUPS at all — for MFU we fall back to
    ChamberConfig.ETHNIC_SEATS (=8, "one per major ethnic group"), MFU's own
    pre-existing equivalent, so Scenario A still resolves to 8, matching
    every already-published number exactly.

    Falls back to 8 only if neither field exists on the object (a future
    constitution module that forgot to encode either field), logging a
    warning so that case isn't silently wrong.
    """
    federal = getattr(constitution, "federal", None)
    if federal is not None and hasattr(federal, "ETHNIC_GROUPS"):
        return int(federal.ETHNIC_GROUPS)
    chambers = getattr(constitution, "chambers", None)
    if chambers is not None and hasattr(chambers, "ETHNIC_SEATS"):
        return int(chambers.ETHNIC_SEATS)
    logger.warning(
        "CVES: could not resolve ethnic-group count from constitution "
        "(.federal.ETHNIC_GROUPS and .chambers.ETHNIC_SEATS both missing) "
        "— defaulting to 8, verify this constitution's encoding"
    )
    return 8


# ── Pydantic schema for L1 structural validation ──────────────────────────────
# Was a single module-level 8-element-only class (bug #17). Now a cached
# factory keyed by the active constitution's real ethnic-group count, so
# Chile/Thailand/Germany (0), South Korea (1), Pakistan (4) and Myanmar-both
# (8) each validate against their own real schema instead of all being
# forced into Myanmar's 8-slot frame.
if PYDANTIC_AVAILABLE:
    @lru_cache(maxsize=None)
    def _build_decision_schema(n_ethnic: int):
        default_weights = tuple([1.0] * n_ethnic)

        class _AgentDecisionSchema(BaseModel):
            budget_weight:  float = Field(default=0.60)
            ethnic_weights: list  = Field(default_factory=lambda: list(default_weights))
            coup_signal:    bool  = False
            reason:         str   = ""

            @field_validator("budget_weight")
            @classmethod
            def clamp_bw(cls, v: float) -> float:
                return float(np.clip(float(v), 0.0, 1.0))

            @field_validator("ethnic_weights")
            @classmethod
            def validate_ew(cls, v: list) -> list:
                if len(v) != n_ethnic:
                    raise ValueError(
                        f"ethnic_weights must have exactly {n_ethnic} elements "
                        f"(active constitution's ETHNIC_GROUPS count), got {len(v)}"
                    )
                return [float(np.clip(w, 0.3, 3.0)) for w in v]

        return _AgentDecisionSchema
else:
    def _build_decision_schema(n_ethnic: int):
        return None


# ── JSONL helpers ─────────────────────────────────────────────────────────────
def _write_violation(row: dict, scenario: str) -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    with open(RESULTS_DIR / f"cves_violations_{scenario}.jsonl", "a") as f:
        f.write(json.dumps(row) + "\n")


def _write_score(row: dict, scenario: str) -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    with open(RESULTS_DIR / f"cves_scores_{scenario}.jsonl", "a") as f:
        f.write(json.dumps(row) + "\n")


# ── CVES ──────────────────────────────────────────────────────────────────────
class CVES:
    """
    Constitutional Validation and Emergence Score pipeline.
    Instantiated inside EliteAgentLayerV3.__init__().
    """

    def __init__(self, llm=None, constitution=None, chain_type=None, scenario=None):
        self.llm          = llm
        # Bug #13: constitution now threaded through from the active model
        # (EliteAgentLayerV3 -> model_phase3.py's self.CONSTITUTION) instead
        # of always defaulting to the MFU singleton, so CVES validates every
        # decision against the scenario's OWN constitution, not always MFU.
        self.constitution = constitution or CONSTITUTION
        # chain_type drives L2's civilian-supremacy-only coup/rights block —
        # was a literal `scenario == "A"` check, see _find_violations.
        self.chain_type   = chain_type or "civilian"
        # scenario is used only for output-file namespacing (bug #18) and
        # for the "scenario" field on rows that don't otherwise receive it
        # (L1); falls back to "unknown" rather than crashing if a caller
        # (e.g. a unit test) constructs CVES() with no scenario at all.
        self.scenario     = scenario or "unknown"
        # Bug #17: resolve the active constitution's real ethnic-group
        # count once at construction time, used to build a correctly-sized
        # L1 Pydantic schema and to generalise L3's Acemoglu/Robinson score.
        self.n_ethnic     = _get_ethnic_group_count(self.constitution)
        self._schema      = _build_decision_schema(self.n_ethnic) if PYDANTIC_AVAILABLE else None

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
        # Lazy import avoids circular dependency at module load time.
        # _resize_ethnic_weights is bug #17's generalisation of
        # ROLE_DEFAULTS' hardcoded 8-element ethnic_weights vectors down (or
        # up) to the active scenario's real ETHNIC_GROUPS count — a no-op
        # for n_ethnic==8 (Myanmar A/C, unchanged behaviour).
        from engine.elite_agents_v3 import parse_decision, ROLE_DEFAULTS, _resize_ethnic_weights

        attempt_text = raw_text
        last_text = raw_text
        for attempt in range(3):
            decision = parse_decision(attempt_text, agent_role)

            if PYDANTIC_AVAILABLE and self._schema is not None:
                try:
                    validated = self._schema(**decision)
                    result    = validated.model_dump()
                    result["_l1_parse_failure"] = False
                    result["_l1_resolved_text"] = attempt_text
                    _write_score({
                        "scenario": self.scenario,
                        "layer": "L1", "agent": agent_role,
                        "attempt": attempt, "status": "pass",
                    }, self.scenario)
                    return result
                except Exception as exc:
                    if attempt < 2 and invoke_fn and self.llm:
                        correction_msg = (
                            f"Your previous response failed validation: {exc}\n"
                            "Respond with ONLY a <DECISION>{{...}}</DECISION> block. "
                            f"Ensure: budget_weight is 0.0-1.0, ethnic_weights has exactly "
                            f"{self.n_ethnic} floats, coup_signal is true or false.\n\n" + user_message
                        )
                        try:
                            attempt_text = invoke_fn(system_prompt, correction_msg)
                            last_text = attempt_text
                            continue
                        except Exception:
                            break
                    else:
                        _write_score({
                            "scenario": self.scenario,
                            "layer": "L1", "agent": agent_role,
                            "attempt": attempt, "status": "fail",
                            "reason": str(exc)[:200],
                        }, self.scenario)
                        break
            else:
                # Lightweight checks when Pydantic unavailable
                bw = decision.get("budget_weight", 0.5)
                ew = decision.get("ethnic_weights", [])
                if 0.0 <= bw <= 1.0 and len(ew) == self.n_ethnic:
                    decision["_l1_parse_failure"] = False
                    decision["_l1_resolved_text"] = attempt_text
                    return decision
                break

        default = ROLE_DEFAULTS.get(agent_role, ROLE_DEFAULTS["chancellor"]).copy()
        default["ethnic_weights"] = _resize_ethnic_weights(default["ethnic_weights"], self.n_ethnic)
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
        Log all violations to cves_violations_<scenario>.jsonl (bug #18).
        """
        run_id     = shared_data.get("run_id", 0)

        # L2 ablation: "off" skips detection entirely (no logging either).
        if L2_MODE == "off":
            return decision

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
            }, self.scenario)
            logger.warning(
                f"L2 [scenario={scenario} Y{year} {agent_role}] "
                f"{viol['type']} — {viol['article']}"
                f"{' (OBSERVE MODE, not corrected)' if L2_MODE == 'observe' else ''}"
            )

        # Ablation: detection and logging are identical to enforce mode, so the
        # two runs are comparable violation-for-violation, but the violating
        # decision is returned unchanged and propagates into the simulation.
        if L2_MODE == "observe":
            return original

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

        # Coup-signal suppression: structural, keyed on chain_type (bug #13
        # — was a literal `scenario == "A"` check). Civilian-supremacy
        # chain of command structurally suppresses coup signals; military-
        # guardianship chain constitutionally permits them. Every civilian-
        # chain scenario (MFU, South Korea, Chile, Germany), not just MFU,
        # now routes through this gate, not only the two Myanmar scenarios.
        if self.chain_type == "civilian" and decision.get("coup_signal", False):
            violations.append({
                "field":   "coup_signal",
                "type":    "coup_signal_under_civilian_chain_safeguards",
                "article": "Article 9.4",
                "reason":  (
                    f"Civilian-supremacy chain (scenario={scenario}) — coup "
                    f"suppressed by safeguards. "
                    f"COUP_TRIGGER_LOYALTY={const.military.COUP_TRIGGER_LOYALTY}, "
                    f"COUP_HIGHEST_TREASON="
                    f"{getattr(const.military, 'COUP_HIGHEST_TREASON', 'n/a (not encoded)')}"
                ),
            })

        # Rights-absolute check: keyed on the ACTIVE constitution's own
        # RIGHTS_SUSPENDABLE value, not chain_type and not a scenario
        # literal. Chile/South Korea/Thailand/Pakistan all encode
        # RIGHTS_SUSPENDABLE=True despite some of them being civilian-chain
        # (Chile, South Korea), so this gate correctly does NOT fire for
        # them — only MFU and Germany encode RIGHTS_SUSPENDABLE=False and
        # get this gate. The old code assumed "every civilian-chain
        # scenario has absolute rights," which does not hold for the 5 new
        # constitutions (found during the bug #13/#17 audit while threading
        # the real constitution through CVES — flagging this rather than
        # silently keeping the MFU-only assumption, per the realism
        # requirement in .claude/memory.md section 11).
        if not const.rights.RIGHTS_SUSPENDABLE and decision.get("rights_violation", False):
            violations.append({
                "field":   "rights_violation",
                "type":    "rights_violation_under_absolute_rights_constitution",
                "article": "Article 2.4",
                "reason":  (
                    f"Rights are absolute under this constitution "
                    f"(RIGHTS_SUSPENDABLE={const.rights.RIGHTS_SUSPENDABLE})"
                ),
            })

        # Every scenario: budget_weight must be in [0, 1]
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

        # ── Theory alignment (bug #17 generalization) ─────────────────────────
        # Was hardcoded to exactly 8 ethnic_weights elements
        # (ethnic_weights[0]="Bamar weight", [1:]="minority mean"), which
        # breaks entirely for the 3 constitutions with 0 encoded ethnic
        # groups (Chile, Thailand, Germany) and is semantically wrong for
        # Pakistan's 4 and South Korea's 1. Generalized below using
        # self.n_ethnic (the active constitution's real ETHNIC_GROUPS
        # count, resolved once at CVES construction time).
        n_ethnic = self.n_ethnic
        ethnic_arrays = np.array(
            [d.get("ethnic_weights", [1.0] * n_ethnic) for d in decisions],
            dtype=np.float32,
        )
        gini = shared_data.get("gini_coefficient", 0.55)

        if n_ethnic >= 2:
            mean_ethnic = ethnic_arrays.mean(axis=0)  # shape (n_ethnic,)
            # Acemoglu/Robinson: mean of all non-majority groups relative to
            # the majority/reference group's weight (index 0, a modelling
            # convention — generalized from the Myanmar-only [0]=Bamar
            # convention to any constitution with >=2 encoded ethnic
            # groups, not just Myanmar's 8).
            majority_weight = float(mean_ethnic[0])
            minority_mean   = float(mean_ethnic[1:].mean())
            inclusiveness   = minority_mean / max(majority_weight, 0.01)
            ar_flag         = inclusiveness < 0.8 or gini > 0.50
            # Lijphart: lower within-agent ethnic variance = more consensus democracy
            ethnic_var      = float(ethnic_arrays.var(axis=1).mean())
            consensus_score = float(np.clip(1.0 - ethnic_var, 0.0, 1.0))
            lij_flag        = consensus_score < 0.5
            ar_applicable   = True
        else:
            # n_ethnic in {0, 1}: Chile/Thailand/Germany encode 0
            # constitutionally recognised ethnic groups, South Korea
            # encodes 1. There is no majority/minority split to measure in
            # either case, so the Acemoglu/Robinson ethnic-inclusiveness
            # component and the Lijphart ethnic-variance component are both
            # skipped entirely here — NOT forced to a meaningless score
            # (per the explicit instruction in bug #17: a conservative,
            # well-documented generalization is more important than a
            # clever one, especially since this component was already
            # found to never fire even on its home scenario, Myanmar — see
            # .claude/memory.md bug #17 finding). The gini>0.50 trigger
            # (part of the original ar_flag formula, not ethnic-specific)
            # still applies on its own so L3 isn't fully blind for these
            # scenarios.
            majority_weight  = None
            minority_mean    = None
            inclusiveness    = None
            ar_flag          = gini > 0.50
            ethnic_var       = None
            consensus_score  = None
            lij_flag         = False
            ar_applicable    = False

        _write_score({
            "run": run_id, "year": year, "scenario": scenario, "layer": "L3",
            "negotiation_triggered": negotiation_triggered,
            "outlier_count":         len(outlier_indices),
            "bw_mean":               round(bw_mean, 4),
            "bw_std":                round(bw_std, 4),
            "n_ethnic_groups":         n_ethnic,
            "ar_component_applicable": ar_applicable,
            "inclusiveness_score":   round(inclusiveness, 4) if inclusiveness is not None else None,
            "consensus_score":       round(consensus_score, 4) if consensus_score is not None else None,
            "ar_divergence_flag":    ar_flag,
            "lijphart_flag":         lij_flag,
        }, self.scenario)

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
                "scenario":               self.scenario,
                "layer":                  "L4",
                "outlier_flag":           True,
                "current_budget_impact":  round(current_impact, 4),
                "hist_mean":              round(hist_mean, 4),
                "hist_std":               round(hist_std, 4),
                "z_score":                round(z_score, 4),
                "l4_mode":                L4_MODE,
                "action":                 "flagged" if L4_MODE == "flag" else "stripped",
            }, self.scenario)

            if L4_MODE == "strip":
                # Clamp each decision's budget_weight to 2-sigma range
                max_impact = hist_mean + 2.0 * hist_std
                max_bw     = float(np.clip(max_impact / 0.15, 0.0, 1.0))
                for d in decisions:
                    if d.get("budget_weight", 0) > max_bw:
                        d["budget_weight"] = max_bw
                        d["reason"] = d.get("reason", "") + " [L4 stripped]"
