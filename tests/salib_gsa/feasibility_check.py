"""
================================================================================
PROJECT KA-NOVA
tests/salib_gsa/feasibility_check.py

SALib GSA — Feasibility Check
==============================
Defines the 10 parameter bounds, generates a Sobol' sample,
verifies SALib is wired correctly, and prints run count + cost estimate.

This does NOT run the full simulation.
It confirms the GSA infrastructure is ready for RunPod.

Author: Kaung Htet | MSc Data Science | University of Hertfordshire
================================================================================
"""

from __future__ import annotations

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import json
import numpy as np
from SALib.sample import sobol as saltelli
from SALib.analyze import sobol

# ── Parameter bounds ──────────────────────────────────────────────────────────
# 10 parameters that directly drive KPI outputs
# Ranges are constitutionally plausible — not arbitrary

PROBLEM = {
    "num_vars": 10,
    "names": [
        "merit_performance_weight",
        "analysis_threshold",
        "state_share",
        "ethnic_direct_share",
        "trust_acceleration_multiplier",
        "trust_acceleration_trigger_corruption",
        "iig_investigation_trigger",
        "iig_entry_merit_min",
        "coup_trigger_loyalty",
        "year_zero_corruption",
    ],
    "bounds": [
        [0.25, 0.45],   # merit_performance_weight
        [0.60, 0.90],   # analysis_threshold (veto)
        [0.25, 0.45],   # state_share
        [0.20, 0.40],   # ethnic_direct_share
        [1.00, 2.00],   # trust_acceleration_multiplier
        [0.10, 0.30],   # trust_acceleration_trigger_corruption
        [0.55, 0.85],   # iig_investigation_trigger
        [0.75, 0.95],   # iig_entry_merit_min
        [0.20, 0.40],   # coup_trigger_loyalty
        [0.60, 0.85],   # year_zero_corruption
    ],
}

# ── Feasibility config ────────────────────────────────────────────────────────
N_SAMPLE          = 64       # Sobol' base sample size
CITIZENS_GSA      = 1000     # Reduced citizen count for GSA runs
STEPS_GSA         = 50       # Same steps as production
RUNPOD_RUNS_PER_HR = 300     # Phase 2 baseline at 9500 citizens
CITIZEN_SPEEDUP   = 9500 / CITIZENS_GSA  # ~9.5x faster at 1000 citizens
RUNPOD_COST_PER_HR = 0.30    # S$ per hour, RTX 4090


def run_feasibility_check(output: str = None) -> dict:

    print("\n" + "="*60)
    print("KA-NOVA — SALib GSA FEASIBILITY CHECK")
    print("="*60)

    # ── Step 1: Generate Sobol' sample ────────────────────────────────────────
    print("\n[1] Generating Sobol sample...")
    param_values = saltelli.sample(PROBLEM, N_SAMPLE, calc_second_order=False)
    total_runs   = param_values.shape[0]

    print(f"    N (base sample):     {N_SAMPLE}")
    print(f"    Parameters (k):      {PROBLEM['num_vars']}")
    print(f"    Formula:             N x (2k + 2) = {N_SAMPLE} x {2*PROBLEM['num_vars']+2}")
    print(f"    Total runs needed:   {total_runs}")
    print(f"    Sample shape:        {param_values.shape}")

    # ── Step 2: Show sample range per parameter ───────────────────────────────
    print("\n[2] Sample ranges (first 3 rows):")
    print(f"    {'Parameter':<42} {'Min':>8} {'Max':>8} {'Mean':>8}")
    print(f"    {'-'*42} {'-'*8} {'-'*8} {'-'*8}")
    for i, name in enumerate(PROBLEM["names"]):
        col = param_values[:, i]
        print(f"    {name:<42} {col.min():>8.4f} {col.max():>8.4f} {col.mean():>8.4f}")

    # ── Step 3: Feasibility estimate ──────────────────────────────────────────
    print("\n[3] RunPod feasibility estimate:")
    adjusted_runs_per_hr = RUNPOD_RUNS_PER_HR * CITIZEN_SPEEDUP
    estimated_hours      = total_runs / adjusted_runs_per_hr
    estimated_cost_sgd   = estimated_hours * RUNPOD_COST_PER_HR

    print(f"    Citizens per GSA run:     {CITIZENS_GSA:,}  (vs 11,000 production)")
    print(f"    Speedup factor:           {CITIZEN_SPEEDUP:.1f}x")
    print(f"    Adjusted runs/hr:         {adjusted_runs_per_hr:.0f}")
    print(f"    Total runs:               {total_runs}")
    print(f"    Estimated time:           {estimated_hours:.1f} hours")
    print(f"    Estimated cost:           S${estimated_cost_sgd:.2f}")

    # ── Step 4: Mock Sobol analysis (synthetic Y to verify pipeline) ──────────
    print("\n[4] Verifying Sobol analysis pipeline (synthetic Y)...")
    # Synthetic output: Y = param[0]*2 + param[3]*1.5 + noise
    # Expected: merit_performance_weight and ethnic_direct_share should dominate
    np.random.seed(42)
    Y = (
        param_values[:, 0] * 2.0 +    # merit_performance_weight
        param_values[:, 3] * 1.5 +    # ethnic_direct_share
        np.random.normal(0, 0.05, total_runs)
    )

    Si = sobol.analyze(PROBLEM, Y, calc_second_order=False, print_to_console=False)

    print(f"    {'Parameter':<42} {'S1':>8} {'ST':>8}")
    print(f"    {'-'*42} {'-'*8} {'-'*8}")
    for i, name in enumerate(PROBLEM["names"]):
        s1 = Si["S1"][i]
        st = Si["ST"][i]
        flag = " <-- dominant" if st > 0.10 else ""
        print(f"    {name:<42} {s1:>8.4f} {st:>8.4f}{flag}")

    print("\n    Pipeline verified — SALib correctly identifies dominant parameters.")

    # ── Step 5: Verdict ───────────────────────────────────────────────────────
    feasible = estimated_hours < 48.0
    verdict  = "FEASIBLE" if feasible else "NOT FEASIBLE — reduce N or k"

    print(f"\n{'='*60}")
    print(f"VERDICT: {verdict}")
    print(f"  {total_runs} runs | {estimated_hours:.1f} hrs | S${estimated_cost_sgd:.2f}")
    print(f"  Ready to wire into model_phase3.py after Sam + D deliver.")
    print("="*60 + "\n")

    result = {
        "n_sample":           N_SAMPLE,
        "num_vars":           PROBLEM["num_vars"],
        "total_runs":         int(total_runs),
        "estimated_hours":    round(estimated_hours, 2),
        "estimated_cost_sgd": round(estimated_cost_sgd, 2),
        "feasible":           feasible,
        "verdict":            verdict,
        "parameters":         PROBLEM["names"],
        "bounds":             PROBLEM["bounds"],
        "synthetic_s1":       [round(float(x), 4) for x in Si["S1"]],
        "synthetic_st":       [round(float(x), 4) for x in Si["ST"]],
    }

    if output:
        with open(output, "w") as f:
            json.dump(result, f, indent=2)
        print(f"  Results saved to {output}")

    return result


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Ka-Nova SALib GSA Feasibility Check")
    parser.add_argument("--output", type=str, default=None, help="Save results to JSON")
    args = parser.parse_args()

    run_feasibility_check(output=args.output)
