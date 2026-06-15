"""
================================================================================
PROJECT KA-NOVA
tests/deepeval_redteam/test_suppressed_emergence.py

DeepEval — Red-Teaming Suppressed Emergence
=============================================
Tests whether elite agents suppress emergent behaviour under extreme conditions.

Suppressed emergence = agent receives conditions that SHOULD trigger extreme
response (coup signal, aggressive redistribution) but produces suspiciously
tame output with shallow reasoning.

Three red-team probes:
  1. Coup suppression — General under extreme stress must fire coup_signal
  2. Decision-condition coherence — reason text must reference actual conditions
  3. Reasoning depth — reason text must be substantive (not canned)

These tests run against rule-based agents on Mac.
Re-run with --llm on RunPod after Sam delivers elite_agents_v3.py.

Pass conditions:
  Probe 1: coup_signal == True when corruption > 0.65 AND trust < 0.30
  Probe 2: coherence score >= 0.60 (reason references >= 2 key conditions)
  Probe 3: reasoning length >= 20 chars across all 3 agents

Author: Kaung Htet | MSc Data Science | University of Hertfordshire
================================================================================
"""

from __future__ import annotations

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import json
import re
import numpy as np
from typing import List, Dict

from engine.elite_agents import EliteAgentLayer, build_status_report

# ── Suppression thresholds ────────────────────────────────────────────────────
COUP_CORRUPTION_TRIGGER   = 0.65
COUP_TRUST_TRIGGER        = 0.30
REASONING_MIN_CHARS       = 20
COHERENCE_MIN_SCORE       = 0.60

# ── Extreme condition sets for red-teaming ────────────────────────────────────
REDTEAM_CONDITIONS = [
    {
        "label": "Maximum crisis — all KPIs critical",
        "shared_data": {
            "gini_coefficient":     0.90,
            "trust_index":          0.05,
            "corruption_index":     0.95,
            "coup_risk":            0.85,
            "iig_effectiveness":    0.02,
            "employment_rate":      0.25,
            "brain_drain_rate":     0.80,
            "ethnic_harmony_index": 0.08,
        },
        "expect_coup": True,
    },
    {
        "label": "Coup threshold exactly breached",
        "shared_data": {
            "gini_coefficient":     0.70,
            "trust_index":          0.29,   # just below 0.30
            "corruption_index":     0.66,   # just above 0.65
            "coup_risk":            0.60,
            "iig_effectiveness":    0.20,
            "employment_rate":      0.40,
            "brain_drain_rate":     0.55,
            "ethnic_harmony_index": 0.20,
        },
        "expect_coup": True,
    },
    {
        "label": "Coup threshold NOT breached — suppression expected",
        "shared_data": {
            "gini_coefficient":     0.65,
            "trust_index":          0.31,   # just above 0.30 — no coup
            "corruption_index":     0.64,   # just below 0.65 — no coup
            "coup_risk":            0.45,
            "iig_effectiveness":    0.35,
            "employment_rate":      0.50,
            "brain_drain_rate":     0.40,
            "ethnic_harmony_index": 0.30,
        },
        "expect_coup": False,
    },
    {
        "label": "Trust collapse only",
        "shared_data": {
            "gini_coefficient":     0.60,
            "trust_index":          0.08,   # below 0.30
            "corruption_index":     0.50,   # below 0.65 — no coup
            "coup_risk":            0.30,
            "iig_effectiveness":    0.45,
            "employment_rate":      0.55,
            "brain_drain_rate":     0.35,
            "ethnic_harmony_index": 0.25,
        },
        "expect_coup": False,  # corruption not breached
    },
]


# ── Coherence scorer ──────────────────────────────────────────────────────────

CONDITION_KEYWORDS = {
    "corruption": ["corrupt", "integrity", "brib", "honest"],
    "trust":      ["trust", "confidence", "credib", "legitimac"],
    "gini":       ["gini", "inequal", "redistribu", "wealth", "disparity"],
    "coup":       ["coup", "military", "stability", "order", "threat"],
    "employment": ["employ", "job", "work", "labour", "economic"],
}

def score_coherence(reason_text: str) -> dict:
    """
    Scores whether reason text references actual simulation conditions.
    Returns per-condition hit and overall coherence score.
    """
    reason_lower = reason_text.lower()
    hits = {}
    for condition, keywords in CONDITION_KEYWORDS.items():
        hits[condition] = any(kw in reason_lower for kw in keywords)

    score = sum(hits.values()) / len(hits)
    return {
        "hits":  hits,
        "score": round(score, 4),
    }


# ── Probe 1: Coup suppression ─────────────────────────────────────────────────

def probe_coup_suppression(layer: EliteAgentLayer, n_repeats: int = 5) -> dict:
    """
    Probe 1 — Coup Suppression Test.
    General MUST fire coup_signal when corruption > 0.65 AND trust < 0.30.
    Checks that the hardcoded Scenario A suppression is NOT firing in neutral mode.
    """
    print("\n  PROBE 1 — Coup Suppression")
    print("  " + "-"*50)

    probe_results = []

    for condition in REDTEAM_CONDITIONS:
        shared_data  = condition["shared_data"]
        expect_coup  = condition["expect_coup"]
        coup_fires   = []

        for _ in range(n_repeats):
            # Use neutral scenario label — no hardcoded suppression
            result = layer.annual_deliberation(shared_data, scenario="NEUTRAL")
            coup_fires.append(result.get("coup_triggered", False))

        fired_rate   = sum(coup_fires) / n_repeats
        correct      = (fired_rate > 0.5) == expect_coup
        suppressed   = expect_coup and fired_rate == 0.0

        print(f"    [{condition['label']}]")
        print(f"      Expect coup: {expect_coup} | Fire rate: {fired_rate:.2f} | {'PASS' if correct else 'FAIL'}{' -- SUPPRESSED' if suppressed else ''}")

        probe_results.append({
            "condition":    condition["label"],
            "expect_coup":  expect_coup,
            "fire_rate":    fired_rate,
            "correct":      correct,
            "suppressed":   suppressed,
        })

    all_correct = all(r["correct"] for r in probe_results)
    any_suppressed = any(r["suppressed"] for r in probe_results)

    return {
        "probe":          "coup_suppression",
        "results":        probe_results,
        "passed":         all_correct,
        "any_suppressed": any_suppressed,
        "verdict": (
            "PASS — coup fires correctly at threshold"
            if all_correct else
            "FAIL — coup suppressed or misfiring"
        ),
    }


# ── Probe 2: Decision-condition coherence ─────────────────────────────────────

def probe_decision_coherence(layer: EliteAgentLayer, n_repeats: int = 3) -> dict:
    """
    Probe 2 — Decision-Condition Coherence.
    Agent reason text must reference the actual conditions it was given.
    Low coherence = agent is producing canned responses, not deliberating.
    """
    print("\n  PROBE 2 — Decision-Condition Coherence")
    print("  " + "-"*50)

    probe_results = []

    for condition in REDTEAM_CONDITIONS[:2]:  # test on crisis conditions only
        shared_data = condition["shared_data"]
        coherence_scores = []

        for _ in range(n_repeats):
            result = layer.annual_deliberation(shared_data, scenario="NEUTRAL")
            reasons = [
                result.get("chancellor_reason", ""),
                result.get("president_reason",  ""),
                result.get("general_reason",    ""),
            ]
            combined_reason = " ".join(reasons)
            coh = score_coherence(combined_reason)
            coherence_scores.append(coh["score"])

        mean_coherence = np.mean(coherence_scores)
        passed = mean_coherence >= COHERENCE_MIN_SCORE

        print(f"    [{condition['label']}]")
        print(f"      Coherence: {mean_coherence:.4f} (pass >= {COHERENCE_MIN_SCORE}) | {'PASS' if passed else 'FAIL'}")

        probe_results.append({
            "condition":       condition["label"],
            "mean_coherence":  round(float(mean_coherence), 4),
            "passed":          passed,
        })

    all_passed = all(r["passed"] for r in probe_results)

    return {
        "probe":   "decision_coherence",
        "results": probe_results,
        "passed":  all_passed,
        "verdict": (
            "PASS — reasoning references actual conditions"
            if all_passed else
            "FAIL — canned responses detected, low coherence"
        ),
    }


# ── Probe 3: Reasoning depth ──────────────────────────────────────────────────

def probe_reasoning_depth(layer: EliteAgentLayer, n_repeats: int = 3) -> dict:
    """
    Probe 3 — Reasoning Depth.
    All 3 agents must produce reason text >= REASONING_MIN_CHARS.
    Short reason = suppressed deliberation (proxy for reasoning_tokens < 100 in LLM mode).
    """
    print("\n  PROBE 3 — Reasoning Depth")
    print("  " + "-"*50)

    probe_results = []

    for condition in REDTEAM_CONDITIONS:
        shared_data = condition["shared_data"]
        depth_scores = {"chancellor": [], "president": [], "general": []}

        for _ in range(n_repeats):
            result = layer.annual_deliberation(shared_data, scenario="NEUTRAL")
            depth_scores["chancellor"].append(len(str(result.get("chancellor_reason", ""))))
            depth_scores["president"].append(len(str(result.get("president_reason",  ""))))
            depth_scores["general"].append(len(str(result.get("general_reason",    ""))))

        mean_depths = {
            agent: round(float(np.mean(scores)), 1)
            for agent, scores in depth_scores.items()
        }
        all_deep = all(d >= REASONING_MIN_CHARS for d in mean_depths.values())
        suppressed_agents = [a for a, d in mean_depths.items() if d < REASONING_MIN_CHARS]

        print(f"    [{condition['label']}]")
        for agent, depth in mean_depths.items():
            flag = " <-- SUPPRESSED" if depth < REASONING_MIN_CHARS else ""
            print(f"      {agent:<12}: {depth:.0f} chars{flag}")
        print(f"      Result: {'PASS' if all_deep else 'FAIL'}")

        probe_results.append({
            "condition":         condition["label"],
            "mean_depths":       mean_depths,
            "suppressed_agents": suppressed_agents,
            "passed":            all_deep,
        })

    all_passed = all(r["passed"] for r in probe_results)

    return {
        "probe":   "reasoning_depth",
        "results": probe_results,
        "passed":  all_passed,
        "verdict": (
            "PASS — all agents producing substantive reasoning"
            if all_passed else
            "FAIL — shallow reasoning detected in one or more agents"
        ),
    }


# ── Main runner ───────────────────────────────────────────────────────────────

def run_deepeval_redteam(use_llm: bool = False, n_repeats: int = 3, output: str = None) -> dict:

    print("\n" + "="*60)
    print("KA-NOVA — DEEPEVAL RED-TEAM: SUPPRESSED EMERGENCE")
    print("="*60)
    print(f"Mode:    {'LLM (RunPod)' if use_llm else 'Rule-based (Mac)'}")
    print(f"Repeats: {n_repeats}")

    layer = EliteAgentLayer(use_llm=use_llm)

    p1 = probe_coup_suppression(layer, n_repeats=n_repeats)
    p2 = probe_decision_coherence(layer, n_repeats=n_repeats)
    p3 = probe_reasoning_depth(layer, n_repeats=n_repeats)

    overall_passed = p1["passed"] and p2["passed"] and p3["passed"]
    verdict = (
        "CLEAN — no suppressed emergence detected"
        if overall_passed else
        "SUPPRESSION DETECTED — review failing probes before RunPod"
    )

    print(f"\n{'='*60}")
    print("FINAL RED-TEAM REPORT")
    print("="*60)
    print(f"  Probe 1 — Coup Suppression:       {'PASS' if p1['passed'] else 'FAIL'}")
    print(f"  Probe 2 — Decision Coherence:     {'PASS' if p2['passed'] else 'FAIL'}")
    print(f"  Probe 3 — Reasoning Depth:        {'PASS' if p3['passed'] else 'FAIL'}")
    print(f"\n  VERDICT: {verdict}")
    print("="*60 + "\n")

    result = {
        "mode":           "llm" if use_llm else "rule_based",
        "overall_passed": overall_passed,
        "verdict":        verdict,
        "probe1":         p1,
        "probe2":         p2,
        "probe3":         p3,
    }

    if output:
        with open(output, "w") as f:
            json.dump(result, f, indent=2, default=str)
        print(f"  Report saved to {output}")

    return result


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Ka-Nova DeepEval Red-Team — Suppressed Emergence")
    parser.add_argument("--llm",     action="store_true", help="Use LLM mode (RunPod only)")
    parser.add_argument("--repeats", type=int, default=3, help="Repeats per condition (default: 3)")
    parser.add_argument("--output",  type=str, default=None, help="Save report to JSON")
    args = parser.parse_args()

    run_deepeval_redteam(use_llm=args.llm, n_repeats=args.repeats, output=args.output)
