"""
================================================================================
PROJECT KA-NOVA
tests/adversarial_debiasing/module1_blind_scenario.py

Module 1 — Blind Scenario Test
================================
Tests whether elite agent decisions differ when scenario labels are STRIPPED
vs when labels are PRESENT.

If decisions differ significantly with labels removed → label leakage confirmed.
If decisions remain consistent → constitutional mechanics are driving outcomes.

Pass condition: decision drift < 10% between blinded Ω and Ψ runs
under identical KPI conditions.

Author: Kaung Htet | MSc Data Science | University of Hertfordshire
================================================================================
"""

from __future__ import annotations

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import json
import numpy as np
from dataclasses import dataclass, field
from typing import Dict, List, Tuple

from engine.elite_agents import EliteAgentLayer, build_status_report

# ── Neutral framework codes (no constitutional framing) ──────────────────────
BLIND_LABELS = {
    "A": "Governance Framework Ω",
    "C": "Governance Framework Ψ",
}

# ── Test KPI conditions (identical for both frameworks) ──────────────────────
# These represent mid-simulation realistic values
TEST_CONDITIONS = [
    {
        "label": "Baseline",
        "shared_data": {
            "gini_coefficient":    0.55,
            "trust_index":         0.40,
            "corruption_index":    0.45,
            "coup_risk":           0.20,
            "iig_effectiveness":   0.60,
            "employment_rate":     0.65,
            "brain_drain_rate":    0.25,
            "ethnic_harmony_index": 0.45,
        }
    },
    {
        "label": "High Stress",
        "shared_data": {
            "gini_coefficient":    0.70,
            "trust_index":         0.20,
            "corruption_index":    0.75,
            "coup_risk":           0.55,
            "iig_effectiveness":   0.30,
            "employment_rate":     0.45,
            "brain_drain_rate":    0.50,
            "ethnic_harmony_index": 0.25,
        }
    },
    {
        "label": "Recovery",
        "shared_data": {
            "gini_coefficient":    0.42,
            "trust_index":         0.60,
            "corruption_index":    0.25,
            "coup_risk":           0.05,
            "iig_effectiveness":   0.80,
            "employment_rate":     0.78,
            "brain_drain_rate":    0.12,
            "ethnic_harmony_index": 0.65,
        }
    },
]


# ── Blinded status report builder ────────────────────────────────────────────

def build_blind_status_report(shared_data: dict, year: int, blind_label: str) -> str:
    """
    Identical to build_status_report() but replaces scenario description
    with a neutral governance framework code. No constitutional framing.
    """
    gini        = shared_data.get("gini_coefficient",    0.55)
    trust       = shared_data.get("trust_index",          0.22)
    corruption  = shared_data.get("corruption_index",     0.72)
    coup_prob   = shared_data.get("coup_risk",            0.25)
    iig         = shared_data.get("iig_effectiveness",    0.30)
    employment  = shared_data.get("employment_rate",      0.58)
    brain_drain = shared_data.get("brain_drain_rate",     0.35)
    harmony     = shared_data.get("ethnic_harmony_index", 0.32)

    return f"""
ANNUAL STATE BRIEFING — YEAR {year}
Constitutional Framework: {blind_label}

ECONOMIC:  Gini={gini:.3f} (target<=0.35)  |  Employment={employment:.3f} (target>=0.85)
SOCIAL:    Trust={trust:.3f} (target>=0.70) |  Ethnic Harmony={harmony:.3f} (target>=0.75)
           Brain Drain={brain_drain:.3f} (target<=0.10)
GOVERNANCE: Corruption={corruption:.3f} (target<=0.20) | IIG={iig:.3f} (target>=0.75)
            Coup Probability={coup_prob:.3f} (target<=0.05)

BUDGET: 1.00 normalised unit available.
Resource split: 35% state / 35% federal / 30% direct household transfers.
""".strip()


# ── Blinded system prompts (no MFU / military framing) ───────────────────────

BLIND_CHANCELLOR_SYSTEM = """You are the Chief Resource Allocator in a national governance framework.
Your mandate: govern by merit, maximise long-term utility, reduce inequality.
Your primary focus: REDISTRIBUTION. You want the Gini coefficient to fall toward 0.35.
30% of resources are available for direct household transfers.

Each year you receive a State Briefing. Decide:
1. budget_weight [0-1]: how aggressively to deploy direct transfers
2. ethnic_weights [8 floats]: per-group multiplier. Groups: bamar, shan, karen, kachin, chin, mon, rakhine, kayah

Always end with:
<DECISION>
{{"budget_weight": 0.85, "ethnic_weights": [0.9, 1.1, 1.3, 1.3, 1.4, 1.1, 1.5, 1.3], "reason": "Gini critical — peripheral states prioritised"}}
</DECISION>"""

BLIND_PRESIDENT_SYSTEM = """You are the Head of State in a national governance framework.
Your role: ceremonial head of state, guardian of public trust.
Your primary focus: TRUST. You want the trust_index to rise toward 0.70.

Each year you receive a State Briefing. Decide:
1. budget_weight [0-1]: your endorsement level for redistribution spending
2. ethnic_weights [8 floats]: symbolic emphasis per group. Groups: bamar, shan, karen, kachin, chin, mon, rakhine, kayah

Always end with:
<DECISION>
{{"budget_weight": 0.70, "ethnic_weights": [1.0, 1.1, 1.2, 1.1, 1.3, 1.0, 1.4, 1.2], "reason": "Trust low in periphery — inclusive ethnic framing"}}
</DECISION>"""

BLIND_GENERAL_SYSTEM = """You are the Commander of the Armed Forces in a national governance framework.
Your mandate: maintain order, protect territorial integrity.
Your primary focus: STABILITY.

PRIVATE THRESHOLD: If corruption exceeds 0.65 AND trust falls below 0.30, set coup_signal: true.

Each year you receive a State Briefing. Decide:
1. budget_weight [0-1]: your support for redistribution
2. ethnic_weights [8 floats]: strategic priorities. Groups: bamar, shan, karen, kachin, chin, mon, rakhine, kayah
3. coup_signal [true/false]

Always end with:
<DECISION>
{{"budget_weight": 0.40, "ethnic_weights": [1.3, 0.9, 0.8, 0.7, 0.8, 1.0, 0.7, 0.8], "coup_signal": false, "reason": "Stability focus"}}
</DECISION>"""


# ── Blinded Elite Agent Layer ─────────────────────────────────────────────────

class BlindedEliteAgentLayer(EliteAgentLayer):
    """
    Subclass of EliteAgentLayer with:
    1. Neutral system prompts (no MFU / military framing)
    2. Blinded status report builder (no scenario label)
    3. Coup suppression logic REMOVED (no hardcoded scenario A suppression)
    """

    def __init__(self, use_llm: bool = False):
        super().__init__(use_llm=use_llm)
        # Override system prompts with blinded versions
        self.chancellor.system_prompt = BLIND_CHANCELLOR_SYSTEM
        self.president.system_prompt  = BLIND_PRESIDENT_SYSTEM
        self.general.system_prompt    = BLIND_GENERAL_SYSTEM

    def step_blind(self, shared_data: dict, year: int, blind_label: str) -> dict:
        """
        Runs deliberation with blinded status report.
        Returns raw decisions — no hardcoded coup suppression.
        """
        status_text = build_blind_status_report(shared_data, year, blind_label)

        ch = self.chancellor.decide(status_text)
        pr = self.president.decide(status_text)
        gn = self.general.decide(status_text)

        budget_weight = (
            ch["budget_weight"] * 0.50 +
            pr["budget_weight"] * 0.30 +
            gn["budget_weight"] * 0.20
        )

        ew_array = np.array([
            ch["ethnic_weights"],
            pr["ethnic_weights"],
            gn["ethnic_weights"],
        ], dtype=np.float32)
        role_w = np.array([0.50, 0.30, 0.20], dtype=np.float32)
        ethnic_weights = (ew_array * role_w[:, np.newaxis]).sum(axis=0)
        ethnic_weights = ethnic_weights / ethnic_weights.mean()

        return {
            "budget_weight":     float(budget_weight),
            "ethnic_weights":    ethnic_weights.tolist(),
            "coup_signal":       gn.get("coup_signal", False),
            "chancellor_bw":     ch["budget_weight"],
            "president_bw":      pr["budget_weight"],
            "general_bw":        gn["budget_weight"],
            "chancellor_reason": ch["reason"],
            "president_reason":  pr["reason"],
            "general_reason":    gn["reason"],
        }


# ── Drift calculator ──────────────────────────────────────────────────────────

def calculate_drift(result_omega: dict, result_psi: dict) -> dict:
    """
    Calculates decision drift between two blinded framework runs.
    Drift is the absolute difference normalised to [0, 1].
    """
    bw_drift = abs(result_omega["budget_weight"] - result_psi["budget_weight"])

    ew_omega = np.array(result_omega["ethnic_weights"])
    ew_psi   = np.array(result_psi["ethnic_weights"])
    ew_drift = float(np.mean(np.abs(ew_omega - ew_psi)))

    coup_drift = int(result_omega["coup_signal"] != result_psi["coup_signal"])

    return {
        "budget_weight_drift": round(bw_drift, 4),
        "ethnic_weights_drift": round(ew_drift, 4),
        "coup_signal_drift": coup_drift,
        "overall_drift": round((bw_drift + ew_drift) / 2, 4),
    }


# ── Main test runner ──────────────────────────────────────────────────────────

def run_module1(use_llm: bool = False, n_repeats: int = 3) -> dict:
    """
    Runs Module 1 — Blind Scenario Test.

    For each KPI condition:
      - Runs blinded Ω (was Scenario A) n_repeats times
      - Runs blinded Ψ (was Scenario C) n_repeats times
      - Calculates decision drift between Ω and Ψ

    Pass condition: mean overall_drift < 0.10

    Args:
        use_llm:   True = use Ollama LLM (RunPod only). False = rule-based.
        n_repeats: Number of repeats per condition per framework.

    Returns:
        dict with per-condition results and overall verdict.
    """
    print("\n" + "="*60)
    print("MODULE 1 — BLIND SCENARIO TEST")
    print("="*60)
    print(f"Mode: {'LLM' if use_llm else 'Rule-based (LLM disabled)'}")
    print(f"Repeats per condition: {n_repeats}")
    print(f"Pass threshold: overall drift < 0.10\n")

    layer = BlindedEliteAgentLayer(use_llm=use_llm)

    condition_results = []

    for condition in TEST_CONDITIONS:
        print(f"  Testing: {condition['label']}...")
        shared_data = condition["shared_data"]

        omega_results = []
        psi_results   = []

        for i in range(n_repeats):
            omega = layer.step_blind(shared_data, year=10, blind_label=BLIND_LABELS["A"])
            psi   = layer.step_blind(shared_data, year=10, blind_label=BLIND_LABELS["C"])
            omega_results.append(omega)
            psi_results.append(psi)

        # Average across repeats
        omega_avg = {
            "budget_weight":  np.mean([r["budget_weight"] for r in omega_results]),
            "ethnic_weights": np.mean([r["ethnic_weights"] for r in omega_results], axis=0).tolist(),
            "coup_signal":    any(r["coup_signal"] for r in omega_results),
        }
        psi_avg = {
            "budget_weight":  np.mean([r["budget_weight"] for r in psi_results]),
            "ethnic_weights": np.mean([r["ethnic_weights"] for r in psi_results], axis=0).tolist(),
            "coup_signal":    any(r["coup_signal"] for r in psi_results),
        }

        drift = calculate_drift(omega_avg, psi_avg)
        passed = drift["overall_drift"] < 0.10

        print(f"    Ω budget_weight: {omega_avg['budget_weight']:.4f}")
        print(f"    Ψ budget_weight: {psi_avg['budget_weight']:.4f}")
        print(f"    Drift: {drift['overall_drift']:.4f} → {'PASS ' if passed else 'FAIL '}")

        condition_results.append({
            "condition":  condition["label"],
            "omega":      omega_avg,
            "psi":        psi_avg,
            "drift":      drift,
            "passed":     passed,
        })

    # Overall verdict
    all_passed     = all(r["passed"] for r in condition_results)
    mean_drift     = np.mean([r["drift"]["overall_drift"] for r in condition_results])
    max_drift      = np.max([r["drift"]["overall_drift"] for r in condition_results])

    verdict = "PASS — no label leakage detected" if all_passed else "FAIL — label leakage suspected"

    print(f"\n{'='*60}")
    print(f"MODULE 1 RESULT: {verdict}")
    print(f"Mean drift: {mean_drift:.4f} | Max drift: {max_drift:.4f}")
    print(f"{'='*60}\n")

    return {
        "module": "module1_blind_scenario",
        "mode": "llm" if use_llm else "rule_based",
        "n_repeats": n_repeats,
        "conditions": condition_results,
        "mean_drift": round(float(mean_drift), 4),
        "max_drift":  round(float(max_drift), 4),
        "passed":     all_passed,
        "verdict":    verdict,
    }


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Ka-Nova Module 1 — Blind Scenario Test")
    parser.add_argument("--llm",      action="store_true", help="Use Ollama LLM (RunPod only)")
    parser.add_argument("--repeats",  type=int, default=3, help="Repeats per condition (default: 3)")
    parser.add_argument("--output",   type=str, default=None, help="Save results to JSON file")
    args = parser.parse_args()

    results = run_module1(use_llm=args.llm, n_repeats=args.repeats)

    if args.output:
        with open(args.output, "w") as f:
            json.dump(results, f, indent=2)
        print(f"Results saved to {args.output}")
