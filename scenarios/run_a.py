"""
================================================================================
PROJECT KA-NOVA
scenarios/run_a.py

Scenario A — Full MFU with All Safeguards
Ka-Nova Simulation Engine v1.0

Scenario A is the control condition — the complete MFU constitution
with all 18 articles and 7 safeguards fully enforced.

Constitutional rules active in Scenario A:
    - Merit system with 4-year recertification (Article 3)
    - Chancellor 5-year cooling-off (Safeguard 1)
    - Analysis Council unanimous veto (Article 5.7)
    - IIG Partnership model (Article 7.10)
    - 40/40/20 resource split (Article 8.6)
    - No Gun Policy domestic ROE (Article 17)
    - Psychological health screening (Article 18)
    - Total Ruin Protocol (Article 15)
    - National Shame Register (Article 15)
    - Rights absolute — non-suspendable (Article 2.4)
    - Economic Check and Balance (Article 10.8)
    - Emergency Powers 180-day limit (Article 16)
    - 10-year constitutional review (Article 12.3)

Expected outcome:
    Corruption drops below 0.20 by Year 20-25.
    Trust rises above 0.60 by Year 15.
    Coup probability near zero by Year 10.
    North Star progress > 0.80 by Year 50.

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

RESULTS_DIR = Path("results") / "scenario_a"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)


def run_scenario_a(
    run_id: int = 0,
    n_citizens: int = None,
    n_steps: int = None,
    seed: int = None,
    verbose: bool = True
) -> pd.DataFrame:
    """
    Run one complete Scenario A simulation.

    Args:
        run_id:     Run identifier for file naming
        n_citizens: Number of citizen agents (default from constitution)
        n_steps:    Number of time steps (default 50)
        seed:       Random seed for reproducibility
        verbose:    Print progress

    Returns:
        DataFrame of KPI results across all time steps
    """

    n_citizens = n_citizens or CONSTITUTION.simulation.CITIZEN_AGENTS
    n_steps    = n_steps    or CONSTITUTION.simulation.TIME_STEPS
    seed       = seed       or (run_id * 100 + ord("A"))

    if verbose:
        print(f"\nScenario A — Run {run_id}")
        print(f"  Citizens:   {n_citizens:,}")
        print(f"  Time steps: {n_steps} years")
        print(f"  Seed:       {seed}")

    start = time.time()

    model = KaNovaModel(
        scenario="A",
        seed=seed,
        n_citizens=n_citizens
    )

    for step in range(n_steps):
        model.step()

        if verbose and (step + 1) % 10 == 0:
            print(f"  Year {step + 1:2d} | "
                  f"Corruption: {model.shared_data.get('corruption_index', 0):.3f} | "
                  f"Trust: {model.shared_data.get('trust_index', 0):.3f} | "
                  f"IIG: {model.shared_data.get('iig_effectiveness', 0):.3f} | "
                  f"Coup Risk: {model.shared_data.get('coup_risk', 0):.3f}")

        if model.shared_data.get("simulation_failed", False):
            if verbose:
                print(f"  Simulation ended at Year {step + 1}: "
                      f"{model.shared_data.get('failure_reason')}")
            break

    elapsed = time.time() - start

    df = model.get_results()
    df["run_id"]   = run_id
    df["scenario"] = "A"
    df["seed"]     = seed

    filename = RESULTS_DIR / f"run_{str(run_id).zfill(3)}.csv"
    df.to_csv(filename, index=False)

    if verbose:
        print(f"\nScenario A Run {run_id} complete ({elapsed:.1f}s)")
        print(f"  Final corruption:    {df['corruption_index'].iloc[-1]:.3f}")
        print(f"  Final trust:         {df['trust_index'].iloc[-1]:.3f}")
        print(f"  Final north star:    {df['north_star_progress'].iloc[-1]:.3f}")
        print(f"  Final coup risk:     {df['coup_probability'].iloc[-1]:.3f}")
        print(f"  Total Ruin events:   {df['total_ruin_events'].iloc[-1]:.0f}")
        print(f"  Shame Register size: {df['shame_register_size'].iloc[-1]:.0f}")
        print(f"  Saved: {filename}")

    return df


if __name__ == "__main__":

    import argparse

    parser = argparse.ArgumentParser(description="Ka-Nova Scenario A Runner")
    parser.add_argument("--runs",     type=int, default=1)
    parser.add_argument("--citizens", type=int, default=None)
    parser.add_argument("--steps",    type=int, default=None)
    parser.add_argument("--quiet",    action="store_true")
    args = parser.parse_args()

    print(f"Scenario A — Full MFU with All Safeguards")
    print(f"Runs: {args.runs}")

    all_dfs = []
    for run_id in range(args.runs):
        df = run_scenario_a(
            run_id=run_id,
            n_citizens=args.citizens,
            n_steps=args.steps,
            verbose=not args.quiet
        )
        all_dfs.append(df)

    if len(all_dfs) > 1:
        combined = pd.concat(all_dfs, ignore_index=True)
        out_path = RESULTS_DIR / "scenario_a_combined.csv"
        combined.to_csv(out_path, index=False)
        print(f"\nCombined results: {out_path}")
        print(f"Final year means:")
        final = combined[combined["year"] == combined["year"].max()]
        for kpi in ["corruption_index","trust_index","coup_probability",
                    "north_star_progress","ethnic_harmony"]:
            if kpi in final.columns:
                print(f"  {kpi:<25}: {final[kpi].mean():.4f} "
                      f"(±{final[kpi].std():.4f})")