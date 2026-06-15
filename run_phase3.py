"""
================================================================================
PROJECT KA-NOVA
run_phase3.py

Phase 3 Simulation Runner
Pod split strategy — each scenario runs on its own RunPod instance.

Usage:
    # Local test
    python3 run_phase3.py --test
    python3 run_phase3.py --scenario A --runs 3 --citizens 500 --steps 10

    # RunPod Pod 1 — Scenario A
    python3 run_phase3.py --scenario A --runs 100 --citizens 11000 --steps 50 --use-llm

    # RunPod Pod 2 — Scenario C
    python3 run_phase3.py --scenario C --runs 100 --citizens 11000 --steps 50 --use-llm

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
import platform
from datetime import datetime
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed

import pandas as pd
import numpy as np
from tqdm import tqdm

from model_phase3 import KaNovaModelPhase3

RESULTS_DIR = Path("results_phase3")
SCENARIO_DIRS = {
    "A": RESULTS_DIR / "scenario_a",
    "C": RESULTS_DIR / "scenario_c",
}

IS_LINUX = platform.system() == "Linux"


def run_single(run_id, scenario, n_citizens, n_steps, use_llm=False):
    """Run one simulation — called by pool workers."""
    import random
    import numpy as np

    seed = run_id * 100 + ord(scenario)
    try:
        model = KaNovaModelPhase3(
            scenario=scenario,
            seed=seed,
            n_citizens=n_citizens,
            use_llm=use_llm,
        )
        for _ in range(n_steps):
            model.step()
            if model.shared_data.get("simulation_failed", False):
                break

        df = model.get_results()
        df["run_id"]   = run_id
        df["scenario"] = scenario
        df["seed"]     = seed
        df["final_year"] = model.current_year
        df["simulation_failed"] = model.shared_data.get("simulation_failed", False)
        df["constitution"] = model.constitution_name

        # External layer shock summary
        shock_count = len(model.external_layer.get_shock_summary())
        df["total_shocks_fired"] = shock_count

        # Social media suppression summary
        sm_summary = model.social_media.get_suppression_summary()
        df["total_shutdowns"]  = sm_summary.get("total_shutdowns", 0)
        df["final_vpn_floor"]  = sm_summary.get("final_vpn_floor", 0.35)
        df["mean_sm_openness"] = sm_summary.get("mean_openness", 1.0)

        return {"status": "success", "run_id": run_id, "scenario": scenario, "df": df}

    except Exception as e:
        return {
            "status":    "error",
            "run_id":    run_id,
            "scenario":  scenario,
            "error":     str(e),
            "traceback": traceback.format_exc()
        }


class KaNovaPhase3Runner:
    """
    Phase 3 runner — single scenario per instance.
    Run two instances simultaneously on two RunPod pods.
    """

    def __init__(
        self,
        scenario: str = "A",
        runs: int = 100,
        n_citizens: int = 11000,
        n_steps: int = 50,
        use_llm: bool = False,
        workers: int = None,
    ):
        assert scenario in ("A", "C"), "Phase 3 only supports scenarios A and C"

        self.scenario   = scenario
        self.runs       = runs
        self.n_citizens = n_citizens
        self.n_steps    = n_steps
        self.use_llm    = use_llm
        self.successful = 0
        self.failed     = 0
        self.errors     = []
        self.start_time = None

        # Workers
        if workers is not None:
            self.workers = workers
        elif IS_LINUX:
            self.workers = 64
        else:
            self.workers = 1

        if use_llm and self.workers > 1:
            print("LLM mode forces workers=1 (GPU shared)")
            self.workers = 1

        for d in SCENARIO_DIRS.values():
            d.mkdir(parents=True, exist_ok=True)
        RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    def run(self):
        self.start_time = time.time()
        execution_mode = (
            f"Parallel ({self.workers} workers)"
            if self.workers > 1
            else "Sequential"
        )

        print("\n" + "=" * 60)
        print("PROJECT KA-NOVA — PHASE 3 RUNNER")
        print("=" * 60)
        print(f"Scenario:          {self.scenario}")
        print(f"Runs:              {self.runs}")
        print(f"Citizens:          {self.n_citizens:,} (1:5000 ratio)")
        print(f"Steps:             {self.n_steps} years")
        print(f"Execution:         {execution_mode}")
        print(f"Elite Agents:      {'LLM v3 (CVES)' if self.use_llm else 'Rule-based fallback'}")
        print(f"Platform:          {platform.system()}")
        print(f"Start time:        {datetime.now().strftime('%H:%M:%S')}")
        print("=" * 60 + "\n")

        tasks = [
            (run_id, self.scenario, self.n_citizens, self.n_steps, self.use_llm)
            for run_id in range(self.runs)
        ]

        all_dfs = []

        if self.workers > 1:
            with ProcessPoolExecutor(max_workers=self.workers) as pool:
                futures = {pool.submit(run_single, *t): t for t in tasks}
                with tqdm(total=self.runs, desc=f"Scenario {self.scenario}", unit="run") as pbar:
                    for future in as_completed(futures):
                        try:
                            result = future.result()
                        except Exception as e:
                            task = futures[future]
                            result = {
                                "status": "error", "run_id": task[0],
                                "scenario": task[1], "error": str(e),
                                "traceback": traceback.format_exc()
                            }
                        self._process_result(result, all_dfs)
                        elapsed = time.time() - self.start_time
                        completed = self.successful + self.failed
                        if completed > 0:
                            eta = (self.runs - completed) * (elapsed / completed)
                            pbar.set_postfix({
                                "ok": self.successful,
                                "err": self.failed,
                                "eta": self._fmt(eta)
                            })
                        pbar.update(1)
        else:
            with tqdm(total=self.runs, desc=f"Scenario {self.scenario}", unit="run") as pbar:
                for task in tasks:
                    result = run_single(*task)
                    self._process_result(result, all_dfs)
                    elapsed = time.time() - self.start_time
                    completed = self.successful + self.failed
                    if completed > 0:
                        eta = (self.runs - completed) * (elapsed / completed)
                        pbar.set_postfix({
                            "ok": self.successful,
                            "err": self.failed,
                            "eta": self._fmt(eta)
                        })
                    pbar.update(1)

        self._finalize(all_dfs)
        total_time = time.time() - self.start_time
        print(f"\nPhase 3 Scenario {self.scenario} complete.")
        print(f"Total time:      {self._fmt(total_time)}")
        print(f"Successful:      {self.successful}")
        print(f"Failed:          {self.failed}")
        print(f"Results saved:   {RESULTS_DIR}/")

    def _process_result(self, result, all_dfs):
        if result["status"] == "success":
            self.successful += 1
            df = result["df"]
            all_dfs.append(df)
            run_id = result["run_id"]
            filename = SCENARIO_DIRS[self.scenario] / f"run_{str(run_id).zfill(3)}.csv"
            df.to_csv(filename, index=False)
        else:
            self.failed += 1
            self.errors.append({
                "run_id":   result["run_id"],
                "scenario": result["scenario"],
                "error":    result["error"]
            })
            tqdm.write(
                f"  ERROR r={result['run_id']}: {result['error'][:80]}"
            )
        self._write_progress(result)

    def _write_progress(self, result):
        """Write progress.json after every run — read by Telegram monitor bot."""
        try:
            elapsed = time.time() - self.start_time
            completed = self.successful + self.failed
            eta_minutes = 0
            if completed > 0 and completed < self.runs:
                eta_seconds = (self.runs - completed) * (elapsed / completed)
                eta_minutes = round(eta_seconds / 60)

            # Pull latest KPIs from result if available
            latest = {}
            if result.get("status") == "success" and result.get("df") is not None:
                df = result["df"]
                last = df.iloc[-1] if len(df) > 0 else None
                if last is not None:
                    latest = {
                        "latest_corruption": round(float(last.get("corruption_index", 0)), 4),
                        "latest_trust":      round(float(last.get("trust_index", 0)), 4),
                        "latest_coup":       round(float(last.get("coup_probability", 0)), 4),
                        "latest_step":       int(last.get("year", 0)),
                    }

            # Count suppressions
            suppression_log = RESULTS_DIR / "suppression_log.jsonl"
            suppression_count = 0
            if suppression_log.exists():
                with open(suppression_log) as f:
                    suppression_count = sum(1 for line in f if line.strip())

            progress = {
                "scenario":          self.scenario,
                "current_run":       completed,
                "total_runs":        self.runs,
                "current_step":      latest.get("latest_step", 0),
                "total_steps":       self.n_steps,
                "eta_minutes":       eta_minutes,
                "ok":                self.successful,
                "err":               self.failed,
                "suppression_count": suppression_count,
                "updated_at":        datetime.now().isoformat(),
                **latest,
            }

            with open(RESULTS_DIR / "progress.json", "w") as f:
                json.dump(progress, f, indent=2)

        except Exception as e:
            pass  # Never crash the simulation for monitoring

    def _finalize(self, all_dfs):
        if not all_dfs:
            print("No results to merge.")
            return

        combined = pd.concat(all_dfs, ignore_index=True)
        combined.to_csv(
            RESULTS_DIR / f"scenario_{self.scenario.lower()}_all.csv", index=False
        )

        # Save run log
        with open(RESULTS_DIR / f"run_log_{self.scenario}.json", "w") as f:
            json.dump({
                "timestamp":   datetime.now().isoformat(),
                "scenario":    self.scenario,
                "runs":        self.runs,
                "n_citizens":  self.n_citizens,
                "n_steps":     self.n_steps,
                "workers":     self.workers,
                "use_llm":     self.use_llm,
                "successful":  self.successful,
                "failed":      self.failed,
                "errors":      self.errors,
            }, f, indent=2)

        # Print KPI summary
        kpis = [
            "corruption_index", "trust_index", "coup_probability",
            "gini_coefficient", "north_star_progress", "iig_effectiveness",
            "vpn_floor", "social_media_openness", "china_influence"
        ]
        final_year = combined["year"].max()
        final_df   = combined[combined["year"] == final_year]

        print(f"\n{'=' * 65}")
        print(f"PHASE 3 RESULTS — SCENARIO {self.scenario} — YEAR {final_year}")
        print(f"{'=' * 65}")
        print(f"{'KPI':<30} {'Mean':>10} {'SD':>8} {'Min':>8} {'Max':>8}")
        print(f"{'-' * 65}")

        for kpi in kpis:
            if kpi not in final_df.columns:
                continue
            vals = final_df[kpi].dropna()
            if vals.empty:
                continue
            print(
                f"{kpi:<30} {vals.mean():>10.4f} {vals.std():>8.4f} "
                f"{vals.min():>8.4f} {vals.max():>8.4f}"
            )
        print(f"{'=' * 65}")

    @staticmethod
    def _fmt(s):
        return (
            f"{s:.0f}s"         if s < 60
            else f"{s/60:.1f}m" if s < 3600
            else f"{s/3600:.1f}h"
        )


def parse_args():
    p = argparse.ArgumentParser(description="Ka-Nova Phase 3 Runner")
    p.add_argument("--test",     action="store_true",
                   help="Quick test: 1 run, 200 citizens, 5 steps")
    p.add_argument("--scenario", choices=["A", "C"], default="A",
                   help="Which scenario to run (one pod = one scenario)")
    p.add_argument("--runs",     type=int, default=100)
    p.add_argument("--citizens", type=int, default=11000)
    p.add_argument("--steps",    type=int, default=50)
    p.add_argument("--workers",  type=int, default=None)
    p.add_argument("--use-llm",  dest="use_llm", action="store_true", default=False)
    return p.parse_args()


if __name__ == "__main__":
    args = parse_args()

    if args.test:
        print("TEST MODE — 1 run, 200 citizens, 5 steps")
        runner = KaNovaPhase3Runner(
            scenario=args.scenario,
            runs=1,
            n_citizens=200,
            n_steps=5,
            use_llm=False,
            workers=1,
        )
    else:
        runner = KaNovaPhase3Runner(
            scenario=args.scenario,
            runs=args.runs,
            n_citizens=args.citizens,
            n_steps=args.steps,
            use_llm=args.use_llm,
            workers=args.workers,
        )

    runner.run()
