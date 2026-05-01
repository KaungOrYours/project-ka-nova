"""
================================================================================
PROJECT KA-NOVA
scenarios/run_b.py

Scenario B — MFU Without Safeguards (Loopholes Open)
Ka-Nova Simulation Engine v1.0

Scenario B tests what happens when MFU institutions exist but the
seven constitutional safeguards are disabled. This reveals whether
the safeguards are structurally necessary or merely symbolic.

Safeguards DISABLED in Scenario B:
    - Chancellor cooling-off NOT enforced (Safeguard 1 off)
    - Merit exam CAN be manipulated (Safeguard 2 off)
    - Ethnic Council youth mandate NOT enforced (Safeguard 3 off)
    - IIG Director CAN serve multiple terms (Safeguard 4 off)
    - Analysis Council veto methodology NOT published (Safeguard 5 off)
    - Rights CAN be temporarily suspended (Safeguard 6 off)
    - 10-year constitutional review NOT mandatory (Safeguard 7 off)

Constitutional rules STILL active in Scenario B:
    - Basic merit system exists (but can be gamed)
    - IIG exists (but director can be captured)
    - Three chambers exist (but Analysis Council can be manipulated)
    - Total Ruin Protocol exists (but rarely triggered)
    - Resource split exists (but enforcement weaker)

Expected outcome:
    Corruption gradually increases as institutional capture occurs.
    Trust peaks around Year 10 then declines as loopholes exploited.
    Coup probability rises in Years 15-25 as institutions weaken.
    North Star progress stalls after Year 20.
    System collapse probability ~40% by Year 35.

Author: Kaung Htet
License: MIT
================================================================================
"""

from __future__ import annotations

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
import pandas as pd
from pathlib import Path

from config.constitution import CONSTITUTION
from model import KaNovaModel

RESULTS_DIR = Path("results") / "scenario_b"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)


# Scenario B modifications — safeguards disabled
SCENARIO_B_OVERRIDES = {
    # Safeguard 1 off — chancellor can come directly from chambers
    "chancellor_cooling_off":           0,

    # Safeguard 2 off — merit exams can be manipulated
    "exam_manipulation_probability":    0.15,

    # Safeguard 4 off — IIG director can be reappointed
    "iig_director_renewable":           True,

    # Safeguard 5 off — no mandatory methodology publication
    "analysis_publish_before_veto":     False,

    # Safeguard 6 off — rights can be suspended
    "rights_suspendable":               True,

    # Safeguard 7 off — no mandatory constitutional review
    "constitutional_review_mandatory":  False,

    # IIG effectiveness decays faster without oversight
    "iig_effectiveness_decay":          0.008,

    # Corruption tolerance rises faster without deterrence
    "corruption_tolerance_drift":       0.015
}


def run_scenario_b(
    run_id: int = 0,
    n_citizens: int = None,
    n_steps: int = None,
    seed: int = None,
    verbose: bool = True
) -> pd.DataFrame:
    """
    Run one complete Scenario B simulation.

    Args:
        run_id:     Run identifier for file naming
        n_citizens: Number of citizen agents
        n_steps:    Number of time steps
        seed:       Random seed
        verbose:    Print progress

    Returns:
        DataFrame of KPI results across all time steps
    """

    n_citizens = n_citizens or CONSTITUTION.simulation.CITIZEN_AGENTS
    n_steps    = n_steps    or CONSTITUTION.simulation.TIME_STEPS
    seed       = seed       or (run_id * 100 + ord("B"))

    if verbose:
        print(f"\nScenario B — Run {run_id} (No Safeguards)")
        print(f"  Citizens:   {n_citizens:,}")
        print(f"  Time steps: {n_steps} years")
        print(f"  Seed:       {seed}")
        print(f"  Safeguards: DISABLED")

    start = time.time()

    model = KaNovaModel(
        scenario="B",
        seed=seed,
        n_citizens=n_citizens
    )

    # Apply Scenario B overrides
    _apply_b_overrides(model)

    for step in range(n_steps):
        model.step()

        # Apply Scenario B specific decay each year
        _apply_annual_decay(model)

        if verbose and (step + 1) % 10 == 0:
            print(f"  Year {step + 1:2d} | "
                  f"Corruption: {model.shared_data.get('corruption_index', 0):.3f} | "
                  f"Trust: {model.shared_data.get('trust_index', 0):.3f} | "
                  f"IIG: {model.shared_data.get('iig_effectiveness', 0):.3f} | "
                  f"Coup Risk: {model.shared_data.get('coup_risk', 0):.3f}")

        if model.shared_data.get("simulation_failed", False):
            if verbose:
                print(f"  System FAILED at Year {step + 1}: "
                      f"{model.shared_data.get('failure_reason')}")
            break

    elapsed = time.time() - start

    df = model.get_results()
    df["run_id"]          = run_id
    df["scenario"]        = "B"
    df["seed"]            = seed
    df["safeguards_on"]   = False
    df["system_failed"]   = model.shared_data.get("simulation_failed", False)

    filename = RESULTS_DIR / f"run_{str(run_id).zfill(3)}.csv"
    df.to_csv(filename, index=False)

    if verbose:
        failed = model.shared_data.get("simulation_failed", False)
        print(f"\nScenario B Run {run_id} complete ({elapsed:.1f}s)")
        print(f"  System failed:       {'YES' if failed else 'NO'}")
        print(f"  Final corruption:    {df['corruption_index'].iloc[-1]:.3f}")
        print(f"  Final trust:         {df['trust_index'].iloc[-1]:.3f}")
        print(f"  Final north star:    {df['north_star_progress'].iloc[-1]:.3f}")
        print(f"  Final coup risk:     {df['coup_probability'].iloc[-1]:.3f}")
        print(f"  Saved: {filename}")

    return df


def _apply_b_overrides(model: KaNovaModel):
    """Apply Scenario B specific overrides to model at initialization."""

    from agents.official import OfficialAgent

    # IIG director can be reappointed — remove term limit
    for agent in model.schedule.agents:
        from agents.oversight import IIGDirector
        if isinstance(agent, IIGDirector):
            agent.term_remaining = 999  # effectively no term limit

    # Rights can be violated — remove hard protection
    model.shared_data["rights_hard_protected"] = False

    # No mandatory constitutional review
    model.shared_data["constitutional_review_mandatory"] = False

    # Corruption tolerance starts slightly higher — no cooling-off enforcement
    for agent in model.schedule.agents:
        if isinstance(agent, OfficialAgent):
            agent.corruption_tolerance = min(
                1.0, agent.corruption_tolerance + 0.05
            )


def _apply_annual_decay(model: KaNovaModel):
    """Apply Scenario B specific annual decay — institutional erosion."""

    from agents.official import OfficialAgent

    # IIG effectiveness decays without Analysis Council oversight
    model.shared_data["iig_effectiveness"] = max(
        0.05,
        model.shared_data.get("iig_effectiveness", 0.30) -
        SCENARIO_B_OVERRIDES["iig_effectiveness_decay"]
    )

    # Corruption tolerance drifts upward — normalization effect
    for agent in model.schedule.agents:
        if isinstance(agent, OfficialAgent):
            agent.corruption_tolerance = min(
                1.0,
                agent.corruption_tolerance +
                SCENARIO_B_OVERRIDES["corruption_tolerance_drift"] * 0.10
            )

    # Analysis Council veto integrity erodes
    model.shared_data["merit_system_integrity"] = max(
        0.20,
        model.shared_data.get("merit_system_integrity", 0.60) - 0.003
    )


if __name__ == "__main__":

    import argparse

    parser = argparse.ArgumentParser(description="Ka-Nova Scenario B Runner")
    parser.add_argument("--runs",     type=int, default=1)
    parser.add_argument("--citizens", type=int, default=None)
    parser.add_argument("--steps",    type=int, default=None)
    parser.add_argument("--quiet",    action="store_true")
    args = parser.parse_args()

    print(f"Scenario B — MFU Without Safeguards")
    print(f"Runs: {args.runs}")

    all_dfs = []
    failure_count = 0

    for run_id in range(args.runs):
        df = run_scenario_b(
            run_id=run_id,
            n_citizens=args.citizens,
            n_steps=args.steps,
            verbose=not args.quiet
        )
        all_dfs.append(df)
        if df["system_failed"].any():
            failure_count += 1

    print(f"\nScenario B Summary:")
    print(f"  System failures: {failure_count}/{args.runs} runs "
          f"({failure_count/max(1,args.runs):.1%})")

    if len(all_dfs) > 1:
        combined = pd.concat(all_dfs, ignore_index=True)
        out_path = RESULTS_DIR / "scenario_b_combined.csv"
        combined.to_csv(out_path, index=False)
        print(f"  Combined results: {out_path}")
        final = combined[combined["year"] == combined["year"].max()]
        print(f"  Final year means:")
        for kpi in ["corruption_index","trust_index","coup_probability",
                    "north_star_progress","iig_effectiveness"]:
            if kpi in final.columns:
                print(f"    {kpi:<25}: {final[kpi].mean():.4f} "
                      f"(±{final[kpi].std():.4f})")