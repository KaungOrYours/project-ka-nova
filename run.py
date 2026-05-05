"""
================================================================================
PROJECT KA-NOVA — run.py
Simulation Runner — 300 Runs Across 3 Scenarios

Phase 2 changes:
    - Parallel execution on Linux/RunPod (ProcessPoolExecutor)
    - Sequential execution on Mac (unchanged behaviour)
    - Auto-detects platform — no manual switching needed
    - --workers flag to control parallelism
    - use_llm flag passed through to KaNovaModel

Usage:
    # Mac — sequential (unchanged)
    python3 run.py --test
    python3 run.py --citizens 9500 --steps 50 --runs 300

    # RunPod — parallel (64 workers default)
    python3 run.py --citizens 50000 --steps 50 --runs 100
    python3 run.py --citizens 50000 --steps 50 --runs 100 --workers 128
    python3 run.py --citizens 50000 --steps 50 --runs 100 --use-llm --workers 1
================================================================================
"""

from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import argparse, time, json, traceback, io, platform
from datetime import datetime
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed
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

IS_LINUX = platform.system() == "Linux"


def run_single(run_id, scenario, n_citizens, n_steps, use_llm=False):
    seed = run_id * 100 + ord(scenario)
    old_stdout = sys.stdout
    sys.stdout = io.StringIO()
    try:
        model = KaNovaModel(
            scenario=scenario,
            seed=seed,
            n_citizens=n_citizens,
            use_llm=use_llm,
        )
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
    def __init__(
        self,
        runs_per_scenario=100,
        scenarios=None,
        n_citizens=None,
        n_steps=None,
        use_llm=False,
        workers=None,
    ):
        self.runs_per_scenario = runs_per_scenario
        self.scenarios = scenarios or ["A", "B", "C"]
        self.n_citizens = n_citizens or CONSTITUTION.simulation.CITIZEN_AGENTS
        self.n_steps = n_steps or CONSTITUTION.simulation.TIME_STEPS
        self.use_llm = use_llm
        self.total_runs = self.runs_per_scenario * len(self.scenarios)
        self.successful = 0
        self.failed = 0
        self.errors = []
        self.start_time = None

        # Workers — parallel on Linux, sequential on Mac
        if workers is not None:
            self.workers = workers
        elif IS_LINUX:
            self.workers = 64
        else:
            self.workers = 1

        # LLM forces single worker (GPU shared)
        if self.use_llm and self.workers > 1:
            print("Note: LLM mode forces workers=1 (GPU is shared)")
            self.workers = 1

        for d in SCENARIO_DIRS.values():
            d.mkdir(parents=True, exist_ok=True)
        RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    def run_all(self):
        self.start_time = time.time()
        execution_mode = (
            f"Parallel ({self.workers} workers / {platform.system()})"
            if self.workers > 1
            else f"Sequential ({platform.system()})"
        )

        print("\n" + "=" * 60)
        print("PROJECT KA-NOVA — SIMULATION RUNNER")
        print("=" * 60)
        print(f"Scenarios:         {self.scenarios}")
        print(f"Runs per scenario: {self.runs_per_scenario}")
        print(f"Total runs:        {self.total_runs}")
        print(f"Citizens:          {self.n_citizens:,}")
        print(f"Time steps:        {self.n_steps} years")
        print(f"Execution:         {execution_mode}")
        print(f"Elite Agents:      {'LangChain LLM' if self.use_llm else 'Rule-based (no LLM)'}")
        print(f"Start time:        {datetime.now().strftime('%H:%M:%S')}")
        print("=" * 60 + "\n")

        # Build full task list
        tasks = [
            (run_id, scenario, self.n_citizens, self.n_steps, self.use_llm)
            for scenario in self.scenarios
            for run_id in range(self.runs_per_scenario)
        ]

        all_dfs = []

        if self.workers > 1:
            # ── PARALLEL (RunPod Linux) ───────────────────────────────────
            with ProcessPoolExecutor(max_workers=self.workers) as pool:
                futures = {pool.submit(run_single, *t): t for t in tasks}
                with tqdm(total=self.total_runs, desc="Progress", unit="run") as pbar:
                    for future in as_completed(futures):
                        try:
                            result = future.result()
                        except Exception as e:
                            task = futures[future]
                            result = {
                                "status": "error",
                                "run_id": task[0],
                                "scenario": task[1],
                                "error": str(e),
                                "traceback": traceback.format_exc()
                            }
                        self._process_result(result, all_dfs)
                        elapsed = time.time() - self.start_time
                        completed = self.successful + self.failed
                        if completed > 0:
                            eta = (self.total_runs - completed) * (elapsed / completed)
                            pbar.set_postfix({
                                "ok": self.successful,
                                "err": self.failed,
                                "eta": self._fmt(eta)
                            })
                        pbar.update(1)
        else:
            # ── SEQUENTIAL (Mac) ──────────────────────────────────────────
            with tqdm(total=self.total_runs, desc="Progress", unit="run") as pbar:
                for scenario in self.scenarios:
                    tqdm.write(f"\nScenario {scenario} — {self.runs_per_scenario} runs")
                    for run_id in range(self.runs_per_scenario):
                        result = run_single(
                            run_id, scenario,
                            self.n_citizens, self.n_steps,
                            self.use_llm,
                        )
                        self._process_result(result, all_dfs)
                        elapsed = time.time() - self.start_time
                        completed = self.successful + self.failed
                        if completed > 0:
                            eta = (self.total_runs - completed) * (elapsed / completed)
                            pbar.set_postfix({
                                "s": scenario,
                                "ok": self.successful,
                                "err": self.failed,
                                "eta": self._fmt(eta)
                            })
                        pbar.update(1)

        self._finalize(all_dfs)
        total_time = time.time() - self.start_time
        print(f"\nSimulation complete.")
        print(f"Total time:      {self._fmt(total_time)}")
        print(f"Successful runs: {self.successful}")
        print(f"Failed runs:     {self.failed}")
        print(f"Results saved:   {RESULTS_DIR}/")

    def _process_result(self, result, all_dfs):
        if result["status"] == "success":
            self.successful += 1
            df = result["df"]
            all_dfs.append(df)
            scenario = result["scenario"]
            run_id   = result["run_id"]
            filename = SCENARIO_DIRS[scenario] / f"run_{str(run_id).zfill(3)}.csv"
            df.to_csv(filename, index=False)
        else:
            self.failed += 1
            self.errors.append({
                "run_id":   result["run_id"],
                "scenario": result["scenario"],
                "error":    result["error"]
            })
            tqdm.write(
                f"  ERROR s={result['scenario']} r={result['run_id']}: "
                f"{result['error'][:80]}"
            )

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
            json.dump({
                "timestamp":         datetime.now().isoformat(),
                "platform":          platform.system(),
                "scenarios":         self.scenarios,
                "runs_per_scenario": self.runs_per_scenario,
                "n_citizens":        self.n_citizens,
                "n_steps":           self.n_steps,
                "workers":           self.workers,
                "use_llm":           self.use_llm,
                "successful":        self.successful,
                "failed":            self.failed,
                "errors":            self.errors,
            }, f, indent=2)

    def _compute_summary(self, df):
        kpis = [c for c in [
            "corruption_index", "trust_index", "iig_effectiveness",
            "coup_probability", "ethnic_harmony", "gini_coefficient",
            "employment_rate", "north_star_progress", "stability_index",
            "shame_register_size", "total_ruin_events"
        ] if c in df.columns]

        final_year = df["year"].max()
        final_df   = df[df["year"] == final_year]
        rows = []

        for scenario in self.scenarios:
            s_df = final_df[final_df["scenario"] == scenario]
            for kpi in kpis:
                vals = s_df[kpi].dropna()
                if vals.empty:
                    continue
                rows.append({
                    "scenario": scenario,
                    "kpi":      kpi,
                    "year":     final_year,
                    "mean":     round(vals.mean(), 4),
                    "std":      round(vals.std(), 4),
                    "min":      round(vals.min(), 4),
                    "max":      round(vals.max(), 4),
                    "n":        len(vals)
                })

        if rows:
            summary = pd.DataFrame(rows)
            summary.to_csv(RESULTS_DIR / "summary_statistics.csv", index=False)
            print(f"  Summary:  {RESULTS_DIR}/summary_statistics.csv")
            print("\n" + "=" * 65)
            print(f"RESULTS — KEY KPIs AT YEAR {final_year}")
            print("=" * 65)
            print(f"{'KPI':<28} {'Scenario A':>11} {'Scenario B':>11} {'Scenario C':>11}")
            print("-" * 65)
            for kpi in [
                "corruption_index", "trust_index", "coup_probability",
                "gini_coefficient", "north_star_progress", "iig_effectiveness"
            ]:
                kpi_data = summary[summary["kpi"] == kpi]
                if kpi_data.empty:
                    continue
                row = f"{kpi:<28}"
                for s in ["A", "B", "C"]:
                    sr = kpi_data[kpi_data["scenario"] == s]
                    row += (
                        f"  {sr['mean'].values[0]:.3f}±{sr['std'].values[0]:.3f}"
                        if not sr.empty else f"{'N/A':>11}"
                    )
                print(row)
            print("=" * 65)

    @staticmethod
    def _fmt(s):
        return (
            f"{s:.0f}s"         if s < 60
            else f"{s/60:.1f}m" if s < 3600
            else f"{s/3600:.1f}h"
        )


def parse_args():
    p = argparse.ArgumentParser(description="Ka-Nova Runner")
    p.add_argument("--test",     action="store_true",
                   help="1 run per scenario, 200 citizens, 5 steps")
    p.add_argument("--scenario", choices=["A", "B", "C"], default=None)
    p.add_argument("--runs",     type=int, default=None)
    p.add_argument("--citizens", type=int, default=None)
    p.add_argument("--steps",    type=int, default=None)
    p.add_argument("--workers",  type=int, default=None,
                   help="Parallel workers. Default: 64 on Linux/RunPod, 1 on Mac")
    p.add_argument("--use-llm",  dest="use_llm", action="store_true", default=False,
                   help="Enable LangChain LLM elite agents (RunPod only)")
    p.add_argument("--no-llm",   dest="use_llm", action="store_false")
    return p.parse_args()


if __name__ == "__main__":
    args = parse_args()

    default_workers = 64 if IS_LINUX else 1
    workers = args.workers if args.workers is not None else default_workers

    if args.test:
        print("TEST MODE — 1 run per scenario, 200 citizens, 5 steps")
        runner = KaNovaRunner(
            runs_per_scenario=1,
            scenarios=["A", "B", "C"],
            n_citizens=200,
            n_steps=5,
            use_llm=False,
            workers=1,
        )
    else:
        runner = KaNovaRunner(
            runs_per_scenario=args.runs     or CONSTITUTION.simulation.RUNS_PER_SCENARIO,
            scenarios=[args.scenario]       if args.scenario else ["A", "B", "C"],
            n_citizens=args.citizens        or CONSTITUTION.simulation.CITIZEN_AGENTS,
            n_steps=args.steps              or CONSTITUTION.simulation.TIME_STEPS,
            use_llm=args.use_llm,
            workers=workers,
        )

    runner.run_all()