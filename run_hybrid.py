"""
================================================================================
Ka-Nova Phase 2 — Hybrid Runner
================================
Uses HybridKaNovaModel:
    Citizens (50k)    → NumPy arrays  (instant init, <1s per worker)
    Government (~256) → Mesa agents   (full IIG, Court, Shame Register)
    Elites (3)        → LangChain LLM (Chancellor, President, General)

Usage (RunPod):
    python3 run_hybrid.py --test
    python3 run_hybrid.py --citizens 50000 --steps 50 --runs 100 --workers 100
    python3 run_hybrid.py --citizens 50000 --steps 50 --runs 100 --workers 1 --use-llm
================================================================================
"""

from __future__ import annotations

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import argparse
import io
import json
import platform
import time
import traceback
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path

import pandas as pd
from tqdm import tqdm

from model_hybrid import HybridKaNovaModel

IS_LINUX    = platform.system() == "Linux"
RESULTS_DIR = Path("results_hybrid")
SCENARIOS   = ["A", "B", "C"]


def run_single(run_id, scenario, n_citizens, n_steps, use_llm=False):
    seed = run_id * 100 + ord(scenario)
    old_stdout = sys.stdout
    sys.stdout = io.StringIO()
    try:
        model = HybridKaNovaModel(
            scenario=scenario, seed=seed,
            n_citizens=n_citizens, use_llm=use_llm,
        )
        for _ in range(n_steps):
            model.step()
            if model.shared_data.get("simulation_failed", False):
                break
        sys.stdout = old_stdout
        df = model.get_results()
        df["run_id"]   = run_id
        df["scenario"] = scenario
        df["seed"]     = seed
        return {"status": "success", "run_id": run_id, "scenario": scenario, "df": df}
    except Exception as e:
        sys.stdout = old_stdout
        return {"status": "error", "run_id": run_id, "scenario": scenario,
                "error": str(e), "traceback": traceback.format_exc()}


class HybridRunner:

    def __init__(self, runs_per_scenario=100, scenarios=None, n_citizens=50_000,
                 n_steps=50, use_llm=False, workers=None):
        self.runs_per_scenario = runs_per_scenario
        self.scenarios  = scenarios or SCENARIOS
        self.n_citizens = n_citizens
        self.n_steps    = n_steps
        self.use_llm    = use_llm
        self.total_runs = runs_per_scenario * len(self.scenarios)
        self.successful = 0
        self.failed     = 0
        self.errors     = []

        if workers is not None:
            self.workers = workers
        elif IS_LINUX:
            self.workers = 100
        else:
            self.workers = 1

        if use_llm and self.workers > 1:
            print("Note: LLM mode forces workers=1")
            self.workers = 1

        RESULTS_DIR.mkdir(parents=True, exist_ok=True)
        for sc in self.scenarios:
            (RESULTS_DIR / f"scenario_{sc.lower()}").mkdir(parents=True, exist_ok=True)

    def run_all(self):
        t0   = time.time()
        mode = (f"Parallel ({self.workers} workers)" if self.workers > 1
                else "Sequential")

        print("\n" + "=" * 65)
        print("KA-NOVA PHASE 2 — HYBRID RUNNER")
        print("=" * 65)
        print(f"Engine:            NumPy citizens + Mesa gov agents")
        print(f"Scenarios:         {self.scenarios}")
        print(f"Runs per scenario: {self.runs_per_scenario}")
        print(f"Total runs:        {self.total_runs}")
        print(f"Citizens:          {self.n_citizens:,} (NumPy)")
        print(f"Gov agents:        ~256 (Mesa)")
        print(f"Time steps:        {self.n_steps} years")
        print(f"Execution:         {mode}")
        print(f"Elite Agents:      {'LangChain LLM' if self.use_llm else 'Rule-based (no LLM)'}")
        print(f"Start time:        {datetime.now().strftime('%H:%M:%S')}")
        print("=" * 65 + "\n")

        tasks = [
            (run_id, sc, self.n_citizens, self.n_steps, self.use_llm)
            for sc in self.scenarios
            for run_id in range(self.runs_per_scenario)
        ]

        all_dfs = []

        if self.workers > 1:
            with ProcessPoolExecutor(max_workers=self.workers) as pool:
                futures = {pool.submit(run_single, *t): t for t in tasks}
                with tqdm(total=self.total_runs, desc="Progress", unit="run") as pbar:
                    for future in as_completed(futures):
                        try:
                            result = future.result()
                        except Exception as e:
                            task = futures[future]
                            result = {"status": "error", "run_id": task[0],
                                      "scenario": task[1], "error": str(e)}
                        self._handle(result, all_dfs)
                        elapsed   = time.time() - t0
                        completed = self.successful + self.failed
                        if completed > 0:
                            eta = (self.total_runs - completed) * (elapsed / completed)
                            pbar.set_postfix({"ok": self.successful, "err": self.failed,
                                              "eta": self._fmt(eta)})
                        pbar.update(1)
        else:
            with tqdm(total=self.total_runs, desc="Progress", unit="run") as pbar:
                for sc in self.scenarios:
                    tqdm.write(f"\nScenario {sc} — {self.runs_per_scenario} runs")
                    for run_id in range(self.runs_per_scenario):
                        result = run_single(run_id, sc, self.n_citizens,
                                            self.n_steps, self.use_llm)
                        self._handle(result, all_dfs)
                        elapsed   = time.time() - t0
                        completed = self.successful + self.failed
                        if completed > 0:
                            eta = (self.total_runs - completed) * (elapsed / completed)
                            pbar.set_postfix({"s": sc, "ok": self.successful,
                                              "err": self.failed, "eta": self._fmt(eta)})
                        pbar.update(1)

        self._finalize(all_dfs, t0)

    def _handle(self, result, all_dfs):
        if result["status"] == "success":
            self.successful += 1
            df = result["df"]
            sc = result["scenario"]
            ri = result["run_id"]
            all_dfs.append(df)
            fname = RESULTS_DIR / f"scenario_{sc.lower()}" / f"run_{ri:03d}.csv"
            df.to_csv(fname, index=False)
        else:
            self.failed += 1
            self.errors.append(result)
            tqdm.write(f"  ERROR s={result['scenario']} r={result['run_id']}: "
                       f"{result.get('error','?')[:80]}")

    def _finalize(self, all_dfs, t0):
        total_time = time.time() - t0
        print(f"\nSimulation complete.")
        print(f"Total time:      {self._fmt(total_time)}")
        print(f"Successful runs: {self.successful}")
        print(f"Failed runs:     {self.failed}")

        if not all_dfs:
            print("No results.")
            return

        combined = pd.concat(all_dfs, ignore_index=True)
        combined.to_csv(RESULTS_DIR / "all_results.csv", index=False)
        print(f"Combined:        {RESULTS_DIR}/all_results.csv ({len(combined):,} rows)")

        final = combined[combined["year"] == combined["year"].max()]
        kpis  = ["corruption_index", "trust_index", "coup_probability",
                 "gini_coefficient", "north_star_progress", "iig_effectiveness"]

        print("\n" + "=" * 65)
        print(f"RESULTS — KEY KPIs AT YEAR {int(combined['year'].max())}")
        print("=" * 65)
        print(f"{'KPI':<28} {'Scenario A':>11} {'Scenario B':>11} {'Scenario C':>11}")
        print("-" * 65)
        for kpi in kpis:
            if kpi not in final.columns:
                continue
            row = f"{kpi:<28}"
            for sc in ["A", "B", "C"]:
                vals = final[final["scenario"] == sc][kpi].dropna()
                row += (f"  {vals.mean():.3f}±{vals.std():.3f}"
                        if len(vals) > 0 else f"{'N/A':>11}")
            print(row)
        print("=" * 65)

        with open(RESULTS_DIR / "run_log.json", "w") as f:
            json.dump({
                "timestamp":         datetime.now().isoformat(),
                "engine":            "hybrid_numpy_mesa",
                "n_citizens":        self.n_citizens,
                "n_steps":           self.n_steps,
                "runs_per_scenario": self.runs_per_scenario,
                "workers":           self.workers,
                "use_llm":           self.use_llm,
                "successful":        self.successful,
                "failed":            self.failed,
            }, f, indent=2)

        print(f"Results saved:   {RESULTS_DIR}/")

    @staticmethod
    def _fmt(s):
        return (f"{s:.0f}s" if s < 60
                else f"{s/60:.1f}m" if s < 3600
                else f"{s/3600:.1f}h")


def parse_args():
    p = argparse.ArgumentParser(description="Ka-Nova Hybrid Runner")
    p.add_argument("--test",     action="store_true",
                   help="Quick test: 1 run per scenario, 500 citizens, 5 steps")
    p.add_argument("--citizens", type=int, default=50_000)
    p.add_argument("--steps",    type=int, default=50)
    p.add_argument("--runs",     type=int, default=100)
    p.add_argument("--workers",  type=int, default=None)
    p.add_argument("--scenario", choices=["A","B","C"], default=None)
    p.add_argument("--use-llm",  dest="use_llm", action="store_true", default=False)
    p.add_argument("--no-llm",   dest="use_llm", action="store_false")
    return p.parse_args()


if __name__ == "__main__":
    args    = parse_args()
    workers = args.workers if args.workers is not None else (100 if IS_LINUX else 1)

    if args.test:
        print("TEST MODE — 1 run/scenario, 500 citizens, 5 steps")
        runner = HybridRunner(runs_per_scenario=1, scenarios=["A","B","C"],
                              n_citizens=500, n_steps=5, use_llm=False, workers=1)
    else:
        runner = HybridRunner(
            runs_per_scenario=args.runs,
            scenarios=[args.scenario] if args.scenario else SCENARIOS,
            n_citizens=args.citizens,
            n_steps=args.steps,
            use_llm=args.use_llm,
            workers=workers,
        )

    runner.run_all()