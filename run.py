"""
================================================================================
PROJECT KA-NOVA — run.py
Sequential Simulation Runner — 300 Runs Across 3 Scenarios
Optimized for M2 MacBook Pro. No multiprocessing overhead.
================================================================================
"""

from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import argparse, time, json, traceback, io
from datetime import datetime
from pathlib import Path
import pandas as pd
import numpy as np
from tqdm import tqdm
from config.constitution import CONSTITUTION
from model import KaNovaModel

RESULTS_DIR = Path("results")
SCENARIO_DIRS = {
    "A": RESULTS_DIR / "scenario_a",
    "B": RESULTS_DIR / "scenario_b",
    "C": RESULTS_DIR / "scenario_c"
}

def run_single(run_id, scenario, n_citizens, n_steps):
    seed = run_id * 100 + ord(scenario)
    old_stdout = sys.stdout
    sys.stdout = io.StringIO()
    try:
        model = KaNovaModel(scenario=scenario, seed=seed, n_citizens=n_citizens)
        for _ in range(n_steps):
            model.step()
            if model.shared_data.get("simulation_failed", False):
                break
        sys.stdout = old_stdout
        df = model.get_results()
        df["run_id"] = run_id
        df["scenario"] = scenario
        df["seed"] = seed
        df["final_year"] = model.current_year
        df["simulation_failed"] = model.shared_data.get("simulation_failed", False)
        return {"status": "success", "run_id": run_id, "scenario": scenario, "df": df}
    except Exception as e:
        sys.stdout = old_stdout
        return {"status": "error", "run_id": run_id, "scenario": scenario,
                "error": str(e), "traceback": traceback.format_exc()}


class KaNovaRunner:
    def __init__(self, runs_per_scenario=100, scenarios=None, n_citizens=None, n_steps=None):
        self.runs_per_scenario = runs_per_scenario
        self.scenarios = scenarios or ["A", "B", "C"]
        self.n_citizens = n_citizens or CONSTITUTION.simulation.CITIZEN_AGENTS
        self.n_steps = n_steps or CONSTITUTION.simulation.TIME_STEPS
        self.total_runs = self.runs_per_scenario * len(self.scenarios)
        self.successful = 0
        self.failed = 0
        self.errors = []
        self.start_time = None
        for d in SCENARIO_DIRS.values():
            d.mkdir(parents=True, exist_ok=True)
        RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    def run_all(self):
        self.start_time = time.time()
        print("\n" + "=" * 60)
        print("PROJECT KA-NOVA — SIMULATION RUNNER")
        print("=" * 60)
        print(f"Scenarios:         {self.scenarios}")
        print(f"Runs per scenario: {self.runs_per_scenario}")
        print(f"Total runs:        {self.total_runs}")
        print(f"Citizens:          {self.n_citizens:,}")
        print(f"Time steps:        {self.n_steps} years")
        print(f"Execution:         Sequential (optimized for M2 8GB)")
        print(f"Start time:        {datetime.now().strftime('%H:%M:%S')}")
        print("=" * 60 + "\n")

        all_dfs = []

        with tqdm(total=self.total_runs, desc="Progress", unit="run") as pbar:
            for scenario in self.scenarios:
                tqdm.write(f"\nScenario {scenario} — {self.runs_per_scenario} runs")
                for run_id in range(self.runs_per_scenario):
                    result = run_single(run_id, scenario, self.n_citizens, self.n_steps)
                    if result["status"] == "success":
                        self.successful += 1
                        df = result["df"]
                        all_dfs.append(df)
                        filename = SCENARIO_DIRS[scenario] / f"run_{str(run_id).zfill(3)}.csv"
                        df.to_csv(filename, index=False)
                    else:
                        self.failed += 1
                        self.errors.append({"run_id": run_id, "scenario": scenario, "error": result["error"]})
                        tqdm.write(f"  ERROR s={scenario} r={run_id}: {result['error'][:80]}")

                    elapsed = time.time() - self.start_time
                    completed = self.successful + self.failed
                    if completed > 0:
                        eta = (self.total_runs - completed) * (elapsed / completed)
                        pbar.set_postfix({"s": scenario, "ok": self.successful, "err": self.failed, "eta": self._fmt(eta)})
                    pbar.update(1)

        self._finalize(all_dfs)
        total_time = time.time() - self.start_time
        print(f"\nSimulation complete.")
        print(f"Total time:      {self._fmt(total_time)}")
        print(f"Successful runs: {self.successful}")
        print(f"Failed runs:     {self.failed}")
        print(f"Results saved:   {RESULTS_DIR}/")

    def _finalize(self, all_dfs):
        if not all_dfs:
            print("\nNo results to merge.")
            return
        print(f"\nMerging {len(all_dfs)} results...")
        combined = pd.concat(all_dfs, ignore_index=True)
        combined.to_csv(RESULTS_DIR / "all_results.csv", index=False)
        print(f"  Combined: {RESULTS_DIR}/all_results.csv ({len(combined):,} rows)")
        self._compute_summary(combined)
        with open(RESULTS_DIR / "run_log.json", "w") as f:
            json.dump({"timestamp": datetime.now().isoformat(),
                       "scenarios": self.scenarios, "runs_per_scenario": self.runs_per_scenario,
                       "n_citizens": self.n_citizens, "n_steps": self.n_steps,
                       "successful": self.successful, "failed": self.failed,
                       "errors": self.errors}, f, indent=2)

    def _compute_summary(self, df):
        kpis = [c for c in ["corruption_index","trust_index","iig_effectiveness",
                             "coup_probability","ethnic_harmony","gini_coefficient",
                             "employment_rate","north_star_progress","stability_index",
                             "shame_register_size","total_ruin_events"] if c in df.columns]
        final_year = df["year"].max()
        final_df = df[df["year"] == final_year]
        rows = []
        for scenario in self.scenarios:
            s_df = final_df[final_df["scenario"] == scenario]
            for kpi in kpis:
                vals = s_df[kpi].dropna()
                if vals.empty:
                    continue
                rows.append({"scenario": scenario, "kpi": kpi, "year": final_year,
                             "mean": round(vals.mean(), 4), "std": round(vals.std(), 4),
                             "min": round(vals.min(), 4), "max": round(vals.max(), 4), "n": len(vals)})
        if rows:
            summary = pd.DataFrame(rows)
            summary.to_csv(RESULTS_DIR / "summary_statistics.csv", index=False)
            print(f"  Summary:  {RESULTS_DIR}/summary_statistics.csv")
            print("\n" + "=" * 65)
            print(f"RESULTS — KEY KPIs AT YEAR {final_year}")
            print("=" * 65)
            print(f"{'KPI':<28} {'Scenario A':>11} {'Scenario B':>11} {'Scenario C':>11}")
            print("-" * 65)
            for kpi in ["corruption_index","trust_index","coup_probability",
                        "gini_coefficient","north_star_progress","iig_effectiveness"]:
                kpi_data = summary[summary["kpi"] == kpi]
                if kpi_data.empty:
                    continue
                row = f"{kpi:<28}"
                for s in ["A", "B", "C"]:
                    sr = kpi_data[kpi_data["scenario"] == s]
                    row += f"  {sr['mean'].values[0]:.3f}±{sr['std'].values[0]:.3f}" if not sr.empty else f"{'N/A':>11}"
                print(row)
            print("=" * 65)

    @staticmethod
    def _fmt(s):
        return f"{s:.0f}s" if s < 60 else f"{s/60:.1f}m" if s < 3600 else f"{s/3600:.1f}h"


def parse_args():
    p = argparse.ArgumentParser(description="Ka-Nova Runner")
    p.add_argument("--test", action="store_true", help="1 run per scenario, 200 citizens, 5 steps")
    p.add_argument("--scenario", choices=["A","B","C"], default=None)
    p.add_argument("--runs", type=int, default=None)
    p.add_argument("--citizens", type=int, default=None)
    p.add_argument("--steps", type=int, default=None)
    return p.parse_args()


if __name__ == "__main__":
    args = parse_args()
    if args.test:
        print("TEST MODE — 1 run per scenario, 200 citizens, 5 steps")
        runner = KaNovaRunner(runs_per_scenario=1, scenarios=["A","B","C"], n_citizens=200, n_steps=5)
    else:
        runner = KaNovaRunner(
            runs_per_scenario=args.runs or CONSTITUTION.simulation.RUNS_PER_SCENARIO,
            scenarios=[args.scenario] if args.scenario else ["A","B","C"],
            n_citizens=args.citizens or CONSTITUTION.simulation.CITIZEN_AGENTS,
            n_steps=args.steps or CONSTITUTION.simulation.TIME_STEPS
        )
    runner.run_all()