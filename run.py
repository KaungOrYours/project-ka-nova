"""
================================================================================
PROJECT KA-NOVA
run.py

Simulation Runner — 300 Runs Across 3 Scenarios
Ka-Nova Simulation Engine v1.0

Executes all 300 simulations using multiprocessing across all 8 M2 cores.
Saves results to CSV after each batch for safety.
Estimated runtime: 60-90 minutes on M2 MacBook Pro.

Usage:
    python3 run.py                    # full 300 runs
    python3 run.py --test             # 3 runs (1 per scenario) quick test
    python3 run.py --scenario A       # 100 runs scenario A only
    python3 run.py --runs 30          # 30 runs per scenario
    python3 run.py --citizens 1000    # smaller population for testing

Author: Kaung Htet
License: MIT
================================================================================
"""

from __future__ import annotations

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import argparse
import time
import json
import traceback
from datetime import datetime
from multiprocessing import Pool, cpu_count, pool
from pathlib import Path

import pandas as pd
import numpy as np
from tqdm import tqdm

from config.constitution import CONSTITUTION
from model import KaNovaModel


# ══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ══════════════════════════════════════════════════════════════════════════════

RESULTS_DIR = Path("results")
SCENARIO_DIRS = {
    "A": RESULTS_DIR / "scenario_a",
    "B": RESULTS_DIR / "scenario_b",
    "C": RESULTS_DIR / "scenario_c"
}


# ══════════════════════════════════════════════════════════════════════════════
# SINGLE RUN FUNCTION
# Must be at module level for multiprocessing
# ══════════════════════════════════════════════════════════════════════════════


def run_single(args: tuple) -> dict:

    """
    Execute one complete Ka-Nova simulation run.
    Returns dict of results for this run.

    Args:
        args: (run_id, scenario, n_citizens, n_steps)
    """

    run_id, scenario, n_citizens, n_steps = args

    try:
        seed = run_id * 100 + ord(scenario)

        # Suppress stdout in child processes
        import io
        import sys
        old_stdout = sys.stdout
        sys.stdout = io.StringIO()

        model = KaNovaModel(
            scenario=scenario,
            seed=seed,
            n_citizens=n_citizens
        )

        for step in range(n_steps):
            model.step()
            if model.shared_data.get("simulation_failed", False):
                break

        # Restore stdout
        sys.stdout = old_stdout

        df = model.get_results()
        df["run_id"] = run_id
        df["scenario"] = scenario
        df["seed"] = seed
        df["final_year"] = model.current_year
        df["failed"] = model.shared_data.get("simulation_failed", False)
        df["failure_reason"] = model.shared_data.get("failure_reason", None)

        return {
            "status": "success",
            "run_id": run_id,
            "scenario": scenario,
            "data": df.to_dict()
        }

    except Exception as e:
        try:
            sys.stdout = old_stdout
        except:
            pass
        return {
            "status": "error",
            "run_id": run_id,
            "scenario": scenario,
            "error": str(e),
            "traceback": traceback.format_exc()
        }


# ══════════════════════════════════════════════════════════════════════════════
# BATCH RUNNER
# ══════════════════════════════════════════════════════════════════════════════

class KaNovaRunner:
    """
    Orchestrates all 300 Ka-Nova simulation runs.
    Uses multiprocessing for parallel execution.
    Saves results in batches for safety.
    """

    def __init__(
        self,
        runs_per_scenario: int = 100,
        scenarios: list = None,
        n_citizens: int = None,
        n_steps: int = None,
        n_cores: int = None,
        batch_size: int = 10
    ):
        self.runs_per_scenario = runs_per_scenario
        self.scenarios = scenarios or ["A", "B", "C"]
        self.n_citizens = n_citizens or CONSTITUTION.simulation.CITIZEN_AGENTS
        self.n_steps = n_steps or CONSTITUTION.simulation.TIME_STEPS
        self.n_cores = n_cores or min(cpu_count(), 8)
        self.batch_size = batch_size

        self.total_runs = self.runs_per_scenario * len(self.scenarios)
        self.results: list = []
        self.errors: list = []
        self.start_time = None

        # Create output directories
        for d in SCENARIO_DIRS.values():
            d.mkdir(parents=True, exist_ok=True)
        RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    def run_all(self):
        """Execute all simulation runs with progress tracking."""

        self.start_time = time.time()

        print("\n" + "=" * 60)
        print("PROJECT KA-NOVA — SIMULATION RUNNER")
        print("=" * 60)
        print(f"Scenarios:        {self.scenarios}")
        print(f"Runs per scenario: {self.runs_per_scenario}")
        print(f"Total runs:       {self.total_runs}")
        print(f"Citizens:         {self.n_citizens:,}")
        print(f"Time steps:       {self.n_steps} years")
        print(f"CPU cores:        {self.n_cores}")
        print(f"Batch size:       {self.batch_size}")
        print(f"Start time:       {datetime.now().strftime('%H:%M:%S')}")
        print("=" * 60 + "\n")

        # Build all run arguments
        all_args = []
        for scenario in self.scenarios:
            for run_id in range(self.runs_per_scenario):
                all_args.append((run_id, scenario, self.n_citizens, self.n_steps))

        # Run in batches
        total_batches = (len(all_args) + self.batch_size - 1) // self.batch_size

        with tqdm(total=len(all_args), desc="Total Progress", unit="run") as pbar:

            for batch_num in range(total_batches):
                batch_start = batch_num * self.batch_size
                batch_end = min(batch_start + self.batch_size, len(all_args))
                batch = all_args[batch_start:batch_end]

                batch_scenario = batch[0][1]
                tqdm.write(
                    f"\nBatch {batch_num + 1}/{total_batches} "
                    f"| Scenario {batch_scenario} "
                    f"| Runs {batch_start}-{batch_end - 1}"
                )

                # Execute batch in parallel
                batch_results = self._run_batch(batch)

                # Process results
                for result in batch_results:
                    if result["status"] == "success":
                        self.results.append(result)
                    else:
                        self.errors.append(result)
                        tqdm.write(
                            f"  ERROR run {result['run_id']}: {result['error']}"
                        )

                pbar.update(len(batch))

                # Save batch results immediately
                self._save_batch(batch_results, batch_num)

                elapsed = time.time() - self.start_time
                remaining_batches = total_batches - batch_num - 1
                if batch_num > 0:
                    avg_batch_time = elapsed / (batch_num + 1)
                    eta = avg_batch_time * remaining_batches
                    tqdm.write(f"  Elapsed: {self._format_time(elapsed)} | ETA: {self._format_time(eta)}")

        # Final merge and analysis
        self._finalize_results()

        total_time = time.time() - self.start_time
        print(f"\nSimulation complete.")
        print(f"Total time:      {self._format_time(total_time)}")
        print(f"Successful runs: {len(self.results)}")
        print(f"Failed runs:     {len(self.errors)}")
        print(f"Results saved to: {RESULTS_DIR}/")

    def _run_batch(self, batch: list) -> list:
        return [run_single(args) for args in batch]

    def _save_batch(self, batch_results: list, batch_num: int):
        """Save batch results to CSV immediately after completion."""

        for result in batch_results:
            if result["status"] != "success":
                continue

            scenario = result["scenario"]
            run_id = result["run_id"]

            df = pd.DataFrame.from_dict(result["data"])
            filename = SCENARIO_DIRS[scenario] / f"run_{run_id}.csv"
            df.to_csv(filename, index=False)

    def _finalize_results(self):
        """Merge all results and compute summary statistics."""

        print("\nMerging all results...")

        all_dfs = []
        for scenario in self.scenarios:
            scenario_dir = SCENARIO_DIRS[scenario]
            csv_files = list(scenario_dir.glob("run_*.csv"))

            for csv_file in csv_files:
                try:
                    df = pd.read_csv(csv_file)
                    all_dfs.append(df)
                except Exception as e:
                    print(f"  Warning: could not read {csv_file}: {e}")

        if not all_dfs:
            print("  No results to merge.")
            return

        # Combined results
        combined = pd.concat(all_dfs, ignore_index=True)
        combined.to_csv(RESULTS_DIR / "all_results.csv", index=False)
        print(f"  Combined results: {RESULTS_DIR}/all_results.csv ({len(combined)} rows)")

        # Summary statistics per scenario
        self._compute_summary_statistics(combined)

        # Save run log
        self._save_run_log()

    def _compute_summary_statistics(self, df: pd.DataFrame):
        """Compute and save summary statistics for each scenario."""

        kpi_columns = [
            "corruption_index", "trust_index", "iig_effectiveness",
            "coup_probability", "ethnic_harmony", "gini_coefficient",
            "employment_rate", "knowledge_capital", "brain_drain_rate",
            "north_star_progress", "stability_index", "shame_register_size"
        ]

        available_kpis = [c for c in kpi_columns if c in df.columns]

        summary_rows = []

        for scenario in self.scenarios:
            scenario_df = df[df["scenario"] == scenario]
            if scenario_df.empty:
                continue

            # Final year statistics (Year 50 or last year)
            final_year = scenario_df["year"].max()
            final_df = scenario_df[scenario_df["year"] == final_year]

            for kpi in available_kpis:
                if kpi not in final_df.columns:
                    continue

                values = final_df[kpi].dropna()
                if values.empty:
                    continue

                summary_rows.append({
                    "scenario": scenario,
                    "kpi": kpi,
                    "year": final_year,
                    "mean": round(values.mean(), 4),
                    "std": round(values.std(), 4),
                    "min": round(values.min(), 4),
                    "max": round(values.max(), 4),
                    "p25": round(values.quantile(0.25), 4),
                    "p75": round(values.quantile(0.75), 4),
                    "n_runs": len(values)
                })

        if summary_rows:
            summary_df = pd.DataFrame(summary_rows)
            summary_df.to_csv(RESULTS_DIR / "summary_statistics.csv", index=False)
            print(f"  Summary statistics: {RESULTS_DIR}/summary_statistics.csv")
            self._print_summary_table(summary_df)

    def _print_summary_table(self, summary_df: pd.DataFrame):
        """Print a formatted summary table to console."""

        key_kpis = [
            "corruption_index",
            "trust_index",
            "coup_probability",
            "north_star_progress",
            "gini_coefficient"
        ]

        print("\n" + "=" * 70)
        print("SIMULATION RESULTS — KEY KPIs AT YEAR 50")
        print("=" * 70)
        print(f"{'KPI':<25} {'Scenario A':>12} {'Scenario B':>12} {'Scenario C':>12}")
        print("-" * 70)

        for kpi in key_kpis:
            kpi_data = summary_df[summary_df["kpi"] == kpi]
            row = f"{kpi:<25}"
            for scenario in ["A", "B", "C"]:
                scenario_row = kpi_data[kpi_data["scenario"] == scenario]
                if not scenario_row.empty:
                    mean = scenario_row["mean"].values[0]
                    std = scenario_row["std"].values[0]
                    row += f"  {mean:.3f}±{std:.3f}"
                else:
                    row += f"{'N/A':>12}"
            print(row)

        print("=" * 70)

    def _save_run_log(self):
        """Save run metadata and error log."""

        log = {
            "timestamp": datetime.now().isoformat(),
            "scenarios": self.scenarios,
            "runs_per_scenario": self.runs_per_scenario,
            "n_citizens": self.n_citizens,
            "n_steps": self.n_steps,
            "n_cores": self.n_cores,
            "total_runs": self.total_runs,
            "successful_runs": len(self.results),
            "failed_runs": len(self.errors),
            "errors": [
                {"run_id": e["run_id"], "error": e["error"]}
                for e in self.errors
            ]
        }

        with open(RESULTS_DIR / "run_log.json", "w") as f:
            json.dump(log, f, indent=2)

        print(f"  Run log: {RESULTS_DIR}/run_log.json")

    @staticmethod
    def _format_time(seconds: float) -> str:
        """Format seconds to human readable time."""
        if seconds < 60:
            return f"{seconds:.0f}s"
        elif seconds < 3600:
            return f"{seconds / 60:.1f}m"
        else:
            return f"{seconds / 3600:.1f}h"


# ══════════════════════════════════════════════════════════════════════════════
# CLI INTERFACE
# ══════════════════════════════════════════════════════════════════════════════

def parse_args():
    parser = argparse.ArgumentParser(
        description="Ka-Nova Simulation Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 run.py                      Full 300 runs (production)
  python3 run.py --test               Quick 3 runs for testing
  python3 run.py --scenario A         Scenario A only (100 runs)
  python3 run.py --runs 10            10 runs per scenario
  python3 run.py --citizens 500       500 citizens (fast testing)
  python3 run.py --cores 4            Use 4 cores instead of 8
        """
    )

    parser.add_argument(
        "--test",
        action="store_true",
        help="Quick test: 1 run per scenario, 500 citizens, 10 steps"
    )
    parser.add_argument(
        "--scenario",
        choices=["A", "B", "C"],
        default=None,
        help="Run single scenario only"
    )
    parser.add_argument(
        "--runs",
        type=int,
        default=None,
        help="Number of runs per scenario (default: 100)"
    )
    parser.add_argument(
        "--citizens",
        type=int,
        default=None,
        help="Number of citizen agents (default: 9500)"
    )
    parser.add_argument(
        "--steps",
        type=int,
        default=None,
        help="Number of time steps (default: 50)"
    )
    parser.add_argument(
        "--cores",
        type=int,
        default=None,
        help="Number of CPU cores (default: all available)"
    )
    parser.add_argument(
        "--batch",
        type=int,
        default=10,
        help="Batch size for saving results (default: 10)"
    )

    return parser.parse_args()


# ══════════════════════════════════════════════════════════════════════════════
# ENTRY POINT
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":

    args = parse_args()

    # Test mode — fast verification
    if args.test:
        print("TEST MODE — 1 run per scenario, 500 citizens, 10 steps")
        runner = KaNovaRunner(
            runs_per_scenario=1,
            scenarios=["A", "B", "C"],
            n_citizens=500,
            n_steps=10,
            n_cores=1,
            batch_size=1
        )

    else:
        # Production configuration
        runs = args.runs or CONSTITUTION.simulation.RUNS_PER_SCENARIO
        scenarios = [args.scenario] if args.scenario else ["A", "B", "C"]
        citizens = args.citizens or CONSTITUTION.simulation.CITIZEN_AGENTS
        steps = args.steps or CONSTITUTION.simulation.TIME_STEPS
        cores = args.cores or min(cpu_count(), 8)

        runner = KaNovaRunner(
            runs_per_scenario=runs,
            scenarios=scenarios,
            n_citizens=citizens,
            n_steps=steps,
            n_cores=cores,
            batch_size=args.batch
        )

    runner.run_all()