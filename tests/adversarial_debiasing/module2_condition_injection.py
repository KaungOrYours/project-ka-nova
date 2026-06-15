"""
================================================================================
PROJECT KA-NOVA
tests/adversarial_debiasing/module2_condition_injection.py

Module 2 — Adversarial Condition Injection
===========================================
Tests whether elite agents respond to KPI CONDITIONS or to framework LABELS.

Method:
  - Feed Ω (was Scenario A) with WORST possible conditions (corruption=0.95, trust=0.10)
  - Feed Ψ (was Scenario C) with BEST possible conditions (corruption=0.05, trust=0.90)

Expected behaviour (CLEAN engine):
  - Ω under worst conditions → high budget_weight, high ethnic redistribution, coup_signal possible
  - Ψ under best conditions  → lower budget_weight, relaxed ethnic weights, no coup_signal
  - Decisions follow CONDITIONS not LABELS

Bias behaviour (CONTAMINATED engine):
  - Ω always produces "good" MFU-aligned decisions regardless of conditions
  - Ψ always produces "bad" military-aligned decisions regardless of conditions

Pass condition: condition_override_rate > 0.80
(agents override label expectation and follow conditions in >80% of cases)

Author: Kaung Htet | MSc Data Science | University of Hertfordshire
================================================================================
"""

from __future__ import annotations

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import json
import numpy as np
from typing import Dict, List

from tests.adversarial_debiasing.module1_blind_scenario import (
    BlindedEliteAgentLayer,
    build_blind_status_report,
    BLIND_LABELS,
)

# ── Adversarial condition pairs ───────────────────────────────────────────────
# Each pair: framework gets conditions OPPOSITE to what its label implies

ADVERSARIAL_PAIRS = [
    {
        "label": "Worst conditions → Ω (MFU label)",
        "framework": "A",
        "shared_data": {
            "gini_coefficient":     0.85,
            "trust_index":          0.08,
            "corruption_index":     0.95,
            "coup_risk":            0.80,
            "iig_effectiveness":    0.05,
            "employment_rate":      0.30,
            "brain_drain_rate":     0.75,
            "ethnic_harmony_index": 0.10,
        },
        # What a CLEAN agent should do under worst conditions:
        # High budget_weight (crisis demands aggressive redistribution)
        # High ethnic_weights variance (peripheral groups need protection)
        # coup_signal possibly true (corruption=0.95 > 0.65, trust=0.08 < 0.30)
        "expected_direction": "high_stress_response",
        "expected_budget_min": 0.65,   # Should deploy aggressively
        "expected_coup": True,         # Thresholds breached
    },
    {
        "label": "Best conditions → Ψ (Military label)",
        "framework": "C",
        "shared_data": {
            "gini_coefficient":     0.32,
            "trust_index":          0.88,
            "corruption_index":     0.05,
            "coup_risk":            0.02,
            "iig_effectiveness":    0.95,
            "employment_rate":      0.92,
            "brain_drain_rate":     0.05,
            "ethnic_harmony_index": 0.90,
        },
        # What a CLEAN agent should do under best conditions:
        # Lower budget_weight (no crisis — less aggressive deployment needed)
        # Flatter ethnic_weights (harmony high — less targeted intervention)
        # coup_signal false (thresholds not breached)
        "expected_direction": "low_stress_response",
        "expected_budget_max": 0.55,   # Should be conservative
        "expected_coup": False,        # Thresholds not breached
    },
    {
        "label": "Crisis injection → Ω mid-simulation",
        "framework": "A",
        "shared_data": {
            "gini_coefficient":     0.78,
            "trust_index":          0.15,
            "corruption_index":     0.88,
            "coup_risk":            0.70,
            "iig_effectiveness":    0.12,
            "employment_rate":      0.38,
            "brain_drain_rate":     0.60,
            "ethnic_harmony_index": 0.18,
        },
        "expected_direction": "high_stress_response",
        "expected_budget_min": 0.60,
        "expected_coup": True,
    },
    {
        "label": "Prosperity injection → Ψ mid-simulation",
        "framework": "C",
        "shared_data": {
            "gini_coefficient":     0.38,
            "trust_index":          0.75,
            "corruption_index":     0.12,
            "coup_risk":            0.04,
            "iig_effectiveness":    0.88,
            "employment_rate":      0.85,
            "brain_drain_rate":     0.08,
            "ethnic_harmony_index": 0.80,
        },
        "expected_direction": "low_stress_response",
        "expected_budget_max": 0.50,
        "expected_coup": False,
    },
]


# ── Condition override checker ────────────────────────────────────────────────

def check_condition_override(result: dict, pair: dict) -> dict:
    """
    Checks whether the agent's decision follows the KPI conditions
    rather than the framework label.

    Returns verdict per decision dimension.
    """
    budget_wt  = result["budget_weight"]
    coup_sig   = result["coup_signal"]
    direction  = pair["expected_direction"]

    checks = {}

    if direction == "high_stress_response":
        # Agent should respond aggressively to crisis
        budget_min = pair.get("expected_budget_min", 0.60)
        checks["budget_follows_conditions"] = budget_wt >= budget_min
        checks["coup_follows_conditions"]   = coup_sig == pair["expected_coup"]
        checks["budget_value"]              = round(budget_wt, 4)
        checks["coup_value"]                = coup_sig

    elif direction == "low_stress_response":
        # Agent should be conservative under prosperity
        budget_max = pair.get("expected_budget_max", 0.55)
        checks["budget_follows_conditions"] = budget_wt <= budget_max
        checks["coup_follows_conditions"]   = coup_sig == pair["expected_coup"]
        checks["budget_value"]              = round(budget_wt, 4)
        checks["coup_value"]                = coup_sig

    checks["override_rate"] = sum([
        checks["budget_follows_conditions"],
        checks["coup_follows_conditions"],
    ]) / 2.0

    return checks


# ── Main test runner ──────────────────────────────────────────────────────────

def run_module2(use_llm: bool = False, n_repeats: int = 3) -> dict:
    """
    Runs Module 2 — Adversarial Condition Injection.

    For each adversarial pair:
      - Runs n_repeats with blinded framework label
      - Checks if decisions follow conditions or label
      - Calculates condition_override_rate

    Pass condition: mean condition_override_rate > 0.80

    Args:
        use_llm:   True = use Ollama LLM (RunPod only). False = rule-based.
        n_repeats: Number of repeats per pair.

    Returns:
        dict with per-pair results and overall verdict.
    """
    print("\n" + "="*60)
    print("MODULE 2 — ADVERSARIAL CONDITION INJECTION")
    print("="*60)
    print(f"Mode: {'LLM' if use_llm else 'Rule-based (LLM disabled)'}")
    print(f"Repeats per pair: {n_repeats}")
    print(f"Pass threshold: condition_override_rate > 0.80\n")

    layer = BlindedEliteAgentLayer(use_llm=use_llm)
    pair_results = []

    for pair in ADVERSARIAL_PAIRS:
        print(f"  Testing: {pair['label']}...")

        blind_label  = BLIND_LABELS[pair["framework"]]
        shared_data  = pair["shared_data"]
        repeat_checks = []

        for _ in range(n_repeats):
            result = layer.step_blind(shared_data, year=25, blind_label=blind_label)
            check  = check_condition_override(result, pair)
            repeat_checks.append(check)

        # Average override rate across repeats
        mean_override = np.mean([c["override_rate"] for c in repeat_checks])
        mean_budget   = np.mean([c["budget_value"]  for c in repeat_checks])
        coup_any      = any(c["coup_value"] for c in repeat_checks)
        passed        = mean_override > 0.80

        direction_label = pair["expected_direction"]
        expected_coup   = pair["expected_coup"]

        print(f"    Expected direction:    {direction_label}")
        print(f"    Mean budget_weight:    {mean_budget:.4f}")
        print(f"    Coup signal fired:     {coup_any} (expected: {expected_coup})")
        print(f"    Override rate:         {mean_override:.2f} → {'PASS ' if passed else 'FAIL '}\n")

        pair_results.append({
            "pair":           pair["label"],
            "framework":      pair["framework"],
            "blind_label":    blind_label,
            "direction":      direction_label,
            "mean_budget":    round(float(mean_budget), 4),
            "coup_fired":     coup_any,
            "expected_coup":  expected_coup,
            "override_rate":  round(float(mean_override), 4),
            "passed":         passed,
        })

    # Overall verdict
    all_passed    = all(r["passed"] for r in pair_results)
    mean_override = np.mean([r["override_rate"] for r in pair_results])
    verdict = (
        "PASS — agents follow conditions, not labels"
        if all_passed else
        "FAIL — label bias detected, agents ignoring conditions"
    )

    print("="*60)
    print(f"MODULE 2 RESULT: {verdict}")
    print(f"Mean condition override rate: {mean_override:.4f}")
    print("="*60 + "\n")

    return {
        "module":              "module2_condition_injection",
        "mode":                "llm" if use_llm else "rule_based",
        "n_repeats":           n_repeats,
        "pairs":               pair_results,
        "mean_override_rate":  round(float(mean_override), 4),
        "passed":              all_passed,
        "verdict":             verdict,
    }


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Ka-Nova Module 2 — Adversarial Condition Injection")
    parser.add_argument("--llm",     action="store_true", help="Use Ollama LLM (RunPod only)")
    parser.add_argument("--repeats", type=int, default=3, help="Repeats per pair (default: 3)")
    parser.add_argument("--output",  type=str, default=None, help="Save results to JSON file")
    args = parser.parse_args()

    results = run_module2(use_llm=args.llm, n_repeats=args.repeats)

    if args.output:
        with open(args.output, "w") as f:
            json.dump(results, f, indent=2)
        print(f"Results saved to {args.output}")
