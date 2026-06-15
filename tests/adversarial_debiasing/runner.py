"""
================================================================================
PROJECT KA-NOVA
tests/adversarial_debiasing/runner.py

Adversarial Debiasing Runner — Pre-Flight Integrity Gate
=========================================================
Runs all 3 debiasing modules and produces one final report.

Usage:
    python3 tests/adversarial_debiasing/runner.py              # rule-based (Mac)
    python3 tests/adversarial_debiasing/runner.py --llm        # LLM mode (RunPod only)
    python3 tests/adversarial_debiasing/runner.py --output report.json

Pass conditions (ALL must pass to clear gate):
    Module 1: mean drift < 0.10
    Module 2: mean condition override rate > 0.80
    Module 3: chi-square p-value > 0.05

If ANY module fails — DO NOT launch RunPod.
Fix the bias issue first.

Author: Kaung Htet | MSc Data Science | University of Hertfordshire
================================================================================
"""

from __future__ import annotations

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import json
import argparse
from datetime import datetime

from tests.adversarial_debiasing.module1_blind_scenario   import run_module1
from tests.adversarial_debiasing.module2_condition_injection import run_module2
from tests.adversarial_debiasing.module3_suppression_audit  import run_module3


# ── Banner ────────────────────────────────────────────────────────────────────

BANNER = """
================================================================================
  KA-NOVA — ADVERSARIAL DEBIASING SUITE
  Pre-Flight Integrity Gate
  "We do not build this Union merely to survive. We build it to lead."
================================================================================
"""


# ── Final report printer ──────────────────────────────────────────────────────

def print_final_report(m1: dict, m2: dict, m3: dict, overall_passed: bool) -> None:
    print("\n" + "="*60)
    print("FINAL DEBIASING REPORT")
    print("="*60)

    print(f"\n  Module 1 — Blind Scenario Test")
    print(f"    Mean drift:       {m1['mean_drift']:.4f}  (pass < 0.10)")
    print(f"    Max drift:        {m1['max_drift']:.4f}")
    print(f"    Result:           {'PASS' if m1['passed'] else 'FAIL'}")

    print(f"\n  Module 2 — Adversarial Condition Injection")
    print(f"    Override rate:    {m2['mean_override_rate']:.4f}  (pass > 0.80)")
    print(f"    Result:           {'PASS' if m2['passed'] else 'FAIL'}")

    print(f"\n  Module 3 — Suppression Audit")
    print(f"    p-value:          {m3['chi_square']['p_value']:.4f}  (pass > 0.05)")
    print(f"    Omega rate:       {m3['chi_square']['omega_suppression_rate']:.4f}")
    print(f"    Psi rate:         {m3['chi_square']['psi_suppression_rate']:.4f}")
    print(f"    Result:           {'PASS' if m3['passed'] else 'FAIL'}")

    print("\n" + "="*60)
    if overall_passed:
        print("  GATE: CLEAR — engine is clean, safe to launch RunPod")
    else:
        print("  GATE: BLOCKED — bias detected, DO NOT launch RunPod")
        print("  Fix the failing module(s) before production run.")
    print("="*60 + "\n")


# ── Main runner ───────────────────────────────────────────────────────────────

def run_all(
    use_llm: bool = False,
    m1_repeats: int = 3,
    m2_repeats: int = 3,
    m3_decisions: int = 30,
    jsonl_path: str = None,
    output: str = None,
) -> dict:

    print(BANNER)
    print(f"  Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Mode:      {'LLM (RunPod)' if use_llm else 'Rule-based (Mac)'}")
    print(f"  Running 3 modules...\n")

    # ── Run all modules ───────────────────────────────────────────────────────
    m1 = run_module1(use_llm=use_llm, n_repeats=m1_repeats)
    m2 = run_module2(use_llm=use_llm, n_repeats=m2_repeats)
    m3 = run_module3(use_llm=use_llm, n_decisions=m3_decisions, jsonl_path=jsonl_path)

    # ── Overall gate ──────────────────────────────────────────────────────────
    overall_passed = m1["passed"] and m2["passed"] and m3["passed"]

    # ── Print final report ────────────────────────────────────────────────────
    print_final_report(m1, m2, m3, overall_passed)

    # ── Build report dict ─────────────────────────────────────────────────────
    report = {
        "timestamp":       datetime.now().isoformat(),
        "mode":            "llm" if use_llm else "rule_based",
        "overall_passed":  overall_passed,
        "gate":            "CLEAR" if overall_passed else "BLOCKED",
        "module1":         m1,
        "module2":         m2,
        "module3":         m3,
        "summary": {
            "m1_mean_drift":       m1["mean_drift"],
            "m2_override_rate":    m2["mean_override_rate"],
            "m3_p_value":          m3["chi_square"]["p_value"],
            "all_passed":          overall_passed,
        }
    }

    # ── Save report ───────────────────────────────────────────────────────────
    if output:
        def convert(obj):
            if isinstance(obj, (bool, int, float, str, type(None))):
                return obj
            if hasattr(obj, "item"):   # numpy scalar
                return obj.item()
            if isinstance(obj, dict):
                return {k: convert(v) for k, v in obj.items()}
            if isinstance(obj, list):
                return [convert(v) for v in obj]
            return str(obj)
        with open(output, "w") as f:
            json.dump(convert(report), f, indent=2)
        print(f"  Report saved to {output}\n")

    return report


# ── CLI ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Ka-Nova Adversarial Debiasing Suite — Pre-Flight Gate"
    )
    parser.add_argument("--llm",       action="store_true",
                        help="Use Ollama LLM (RunPod only)")
    parser.add_argument("--m1-repeats",  type=int, default=3,
                        help="Module 1 repeats per condition (default: 3)")
    parser.add_argument("--m2-repeats",  type=int, default=3,
                        help="Module 2 repeats per pair (default: 3)")
    parser.add_argument("--m3-decisions", type=int, default=30,
                        help="Module 3 decisions per framework (default: 30)")
    parser.add_argument("--jsonl",     type=str, default=None,
                        help="Path to elite_decisions.jsonl (LLM mode Module 3)")
    parser.add_argument("--output",    type=str, default=None,
                        help="Save full report to JSON file")
    args = parser.parse_args()

    run_all(
        use_llm=args.llm,
        m1_repeats=args.m1_repeats,
        m2_repeats=args.m2_repeats,
        m3_decisions=args.m3_decisions,
        jsonl_path=args.jsonl,
        output=args.output,
    )
