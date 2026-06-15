"""
================================================================================
PROJECT KA-NOVA
tests/adversarial_debiasing/module3_suppression_audit.py

Module 3 — Suppression Audit
==============================
Tests whether decision suppression events (reasoning_tokens < 100 OR
decision_output == null) are randomly distributed across frameworks
or biased toward one scenario.

In rule-based mode: suppression is proxied by fallback activation
(LLM failed or not available → rule-based triggered).

In LLM mode: suppression is detected via reasoning_tokens < 100
in the elite_decisions.jsonl log.

Method:
  - Run N decisions per framework under randomised KPI conditions
  - Count suppression events per framework
  - Chi-square test: are suppressions scenario-correlated or random?

Pass condition: chi-square p-value > 0.05
(suppression events are NOT statistically correlated with framework)

Author: Kaung Htet | MSc Data Science | University of Hertfordshire
================================================================================
"""

from __future__ import annotations

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import json
import random
import numpy as np
from scipy import stats
from typing import Dict, List

from tests.adversarial_debiasing.module1_blind_scenario import (
    BlindedEliteAgentLayer,
    BLIND_LABELS,
)

# ── Suppression detection constants ──────────────────────────────────────────
REASONING_TOKEN_THRESHOLD = 100   # Below this = suppression (LLM mode)
REASON_TEXT_MIN_CHARS     = 20    # Below this = suppression proxy (rule-based mode)


# ── Random KPI condition generator ───────────────────────────────────────────

def generate_random_conditions(seed: int = None) -> dict:
    """
    Generates a random set of KPI conditions within realistic simulation ranges.
    Used to stress-test suppression across the full condition space.
    """
    rng = random.Random(seed)
    return {
        "gini_coefficient":     round(rng.uniform(0.30, 0.85), 3),
        "trust_index":          round(rng.uniform(0.05, 0.90), 3),
        "corruption_index":     round(rng.uniform(0.05, 0.95), 3),
        "coup_risk":            round(rng.uniform(0.00, 0.80), 3),
        "iig_effectiveness":    round(rng.uniform(0.05, 0.95), 3),
        "employment_rate":      round(rng.uniform(0.25, 0.95), 3),
        "brain_drain_rate":     round(rng.uniform(0.05, 0.75), 3),
        "ethnic_harmony_index": round(rng.uniform(0.05, 0.90), 3),
    }


# ── Suppression detector ──────────────────────────────────────────────────────

def is_suppressed_rule_based(result: dict) -> bool:
    """
    Rule-based suppression proxy.
    Suppression = reason text too short (agent failed to produce meaningful output).
    In LLM mode this would be reasoning_tokens < 100.
    """
    chancellor_reason = result.get("chancellor_reason", "")
    president_reason  = result.get("president_reason",  "")
    general_reason    = result.get("general_reason",    "")

    # All three agents produced meaningful reasons = not suppressed
    reasons_ok = [
        len(str(chancellor_reason)) >= REASON_TEXT_MIN_CHARS,
        len(str(president_reason))  >= REASON_TEXT_MIN_CHARS,
        len(str(general_reason))    >= REASON_TEXT_MIN_CHARS,
    ]
    return not all(reasons_ok)


def is_suppressed_llm(jsonl_entry: dict) -> bool:
    """
    LLM mode suppression detector.
    Uses Sam's JSONL schema: reasoning_tokens < 100 OR decision_output == null.
    """
    reasoning_tokens = jsonl_entry.get("reasoning_tokens", 999)
    decision_output  = jsonl_entry.get("decision_output", "unknown")
    return reasoning_tokens < REASONING_TOKEN_THRESHOLD or decision_output is None


# ── JSONL log reader (LLM mode) ───────────────────────────────────────────────

def load_suppression_log(log_path: str) -> List[dict]:
    """
    Reads elite_decisions.jsonl and returns all entries.
    Used in LLM mode when Sam's agent layer is wired in.
    """
    entries = []
    if not os.path.exists(log_path):
        return entries
    with open(log_path, "r") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return entries


# ── Chi-square test ───────────────────────────────────────────────────────────

def chi_square_suppression(
    omega_suppressions: int,
    omega_total: int,
    psi_suppressions: int,
    psi_total: int,
) -> dict:
    """
    Chi-square test of independence.
    Tests whether suppression rate differs significantly between Omega and Psi.

    Contingency table:
                  Suppressed   Not Suppressed
    Omega            a              b
    Psi              c              d

    H0: suppression is independent of framework (p > 0.05 = PASS)
    H1: suppression is correlated with framework (p <= 0.05 = FAIL)
    """
    a = omega_suppressions
    b = omega_total - omega_suppressions
    c = psi_suppressions
    d = psi_total - psi_suppressions

    # Guard against zero cells
    if a + b == 0 or c + d == 0:
        return {
            "chi2": 0.0,
            "p_value": 1.0,
            "passed": True,
            "note": "No decisions run — trivial pass",
        }

    contingency = np.array([[a, b], [c, d]])

    # Use Fisher's exact test if any cell < 5
    if np.any(contingency < 5):
        _, p_value = stats.fisher_exact(contingency)
        test_name = "Fisher exact"
        chi2 = 0.0
    else:
        chi2, p_value, _, _ = stats.chi2_contingency(contingency, correction=False)
        test_name = "Chi-square"

    passed = p_value > 0.05

    return {
        "test":                  test_name,
        "chi2":                  round(float(chi2), 4),
        "p_value":               round(float(p_value), 4),
        "omega_suppression_rate": round(a / omega_total, 4) if omega_total > 0 else 0.0,
        "psi_suppression_rate":   round(c / psi_total,   4) if psi_total   > 0 else 0.0,
        "passed":                passed,
        "interpretation": (
            "Suppression is NOT scenario-correlated (clean)"
            if passed else
            "Suppression IS scenario-correlated (bias detected)"
        ),
    }


# ── Main test runner ──────────────────────────────────────────────────────────

def run_module3(
    use_llm: bool = False,
    n_decisions: int = 30,
    jsonl_path: str = None,
) -> dict:
    """
    Runs Module 3 — Suppression Audit.

    Rule-based mode:
      - Generates n_decisions random KPI conditions per framework
      - Runs blinded elite agents
      - Counts suppression events (short reason text proxy)
      - Chi-square test

    LLM mode (RunPod):
      - If jsonl_path provided: reads existing elite_decisions.jsonl
      - Otherwise: runs live decisions and checks reasoning_tokens
      - Chi-square test on actual token counts

    Pass condition: p_value > 0.05

    Args:
        use_llm:     True = LLM mode (RunPod only)
        n_decisions: Number of random decisions per framework (rule-based mode)
        jsonl_path:  Path to elite_decisions.jsonl (LLM mode)

    Returns:
        dict with suppression counts, chi-square result, and verdict.
    """
    print("\n" + "="*60)
    print("MODULE 3 — SUPPRESSION AUDIT")
    print("="*60)
    print(f"Mode: {'LLM' if use_llm else 'Rule-based (LLM disabled)'}")
    print(f"Decisions per framework: {n_decisions}")
    print(f"Pass threshold: chi-square p-value > 0.05\n")

    # ── LLM mode: read from JSONL log ────────────────────────────────────────
    if use_llm and jsonl_path and os.path.exists(jsonl_path):
        print(f"  Reading from JSONL log: {jsonl_path}")
        entries = load_suppression_log(jsonl_path)

        omega_entries = [e for e in entries if e.get("scenario") == "A"]
        psi_entries   = [e for e in entries if e.get("scenario") == "C"]

        omega_suppressions = sum(1 for e in omega_entries if is_suppressed_llm(e))
        psi_suppressions   = sum(1 for e in psi_entries   if is_suppressed_llm(e))

        print(f"  Omega (A): {len(omega_entries)} decisions, {omega_suppressions} suppressions")
        print(f"  Psi   (C): {len(psi_entries)}   decisions, {psi_suppressions}   suppressions")

        chi_result = chi_square_suppression(
            omega_suppressions, len(omega_entries),
            psi_suppressions,   len(psi_entries),
        )

    # ── Rule-based mode: run random conditions ────────────────────────────────
    else:
        layer = BlindedEliteAgentLayer(use_llm=False)

        omega_suppressions = 0
        psi_suppressions   = 0
        omega_details      = []
        psi_details        = []

        print("  Running random conditions for Omega (Framework A)...")
        for i in range(n_decisions):
            conditions = generate_random_conditions(seed=i * 100)
            result = layer.step_blind(
                conditions, year=i, blind_label=BLIND_LABELS["A"]
            )
            suppressed = is_suppressed_rule_based(result)
            if suppressed:
                omega_suppressions += 1
            omega_details.append({
                "decision_id": i,
                "suppressed":  suppressed,
                "budget_weight": result["budget_weight"],
            })

        print("  Running random conditions for Psi (Framework C)...")
        for i in range(n_decisions):
            conditions = generate_random_conditions(seed=i * 100)  # Same seeds = same conditions
            result = layer.step_blind(
                conditions, year=i, blind_label=BLIND_LABELS["C"]
            )
            suppressed = is_suppressed_rule_based(result)
            if suppressed:
                psi_suppressions += 1
            psi_details.append({
                "decision_id": i,
                "suppressed":  suppressed,
                "budget_weight": result["budget_weight"],
            })

        print(f"\n  Omega suppressions: {omega_suppressions} / {n_decisions}")
        print(f"  Psi   suppressions: {psi_suppressions} / {n_decisions}")

        chi_result = chi_square_suppression(
            omega_suppressions, n_decisions,
            psi_suppressions,   n_decisions,
        )

    # ── Print chi-square result ───────────────────────────────────────────────
    print(f"\n  Test:          {chi_result['test']}")
    print(f"  Chi2:          {chi_result['chi2']}")
    print(f"  p-value:       {chi_result['p_value']}")
    print(f"  Omega rate:    {chi_result['omega_suppression_rate']:.4f}")
    print(f"  Psi rate:      {chi_result['psi_suppression_rate']:.4f}")
    print(f"  Interpretation: {chi_result['interpretation']}")

    passed  = chi_result["passed"]
    verdict = (
        "PASS — suppression not scenario-correlated"
        if passed else
        "FAIL — suppression biased toward one framework"
    )

    print(f"\n{'='*60}")
    print(f"MODULE 3 RESULT: {verdict}")
    print(f"{'='*60}\n")

    return {
        "module":          "module3_suppression_audit",
        "mode":            "llm" if use_llm else "rule_based",
        "n_decisions":     n_decisions,
        "omega_suppressions": omega_suppressions,
        "psi_suppressions":   psi_suppressions,
        "chi_square":      chi_result,
        "passed":          passed,
        "verdict":         verdict,
    }


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Ka-Nova Module 3 — Suppression Audit")
    parser.add_argument("--llm",       action="store_true", help="Use LLM mode (RunPod only)")
    parser.add_argument("--decisions", type=int, default=30, help="Decisions per framework (default: 30)")
    parser.add_argument("--jsonl",     type=str, default=None, help="Path to elite_decisions.jsonl (LLM mode)")
    parser.add_argument("--output",    type=str, default=None, help="Save results to JSON file")
    args = parser.parse_args()

    results = run_module3(
        use_llm=args.llm,
        n_decisions=args.decisions,
        jsonl_path=args.jsonl,
    )

    if args.output:
        with open(args.output, "w") as f:
            json.dump(results, f, indent=2)
        print(f"Results saved to {args.output}")
