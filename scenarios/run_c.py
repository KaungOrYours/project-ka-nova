"""
================================================================================
PROJECT KA-NOVA
scenarios/run_c.py

Scenario C — Military Baseline (Current Myanmar Trajectory)
Ka-Nova Simulation Engine v1.0

Scenario C simulates Myanmar under continued military rule —
the counterfactual baseline against which MFU is measured.

No MFU constitutional rules apply in Scenario C.
This is not a pessimistic scenario — it is a realistic projection
of the current trajectory based on empirical data.

Scenario C characteristics:
    - No merit system — appointment by loyalty and ethnicity
    - No IIG — corruption unchecked
    - No rights protection — violations routine
    - Military controls civilian government
    - No ethnic veto — Bamar centralism dominant
    - Resource revenue captured by military elite
    - No shame register — no institutional deterrence
    - Coup attempts common — political instability chronic
    - Brain drain accelerates — educated flee military rule
    - Foreign investment limited — governance risk too high

Calibrated from:
    - V-Dem Myanmar 2021-2024
    - World Bank Governance Indicators 2023
    - ACLED conflict data 2021-2024
    - Transparency International CPI 2023
    - UN reports on Myanmar situation 2022-2024

Expected outcome:
    Corruption stays above 0.65 throughout.
    Trust declines from 0.22 toward 0.10-0.15 by Year 20.
    Coup attempts every 8-12 years on average.
    Brain drain exceeds 40% of educated population by Year 25.
    North Star progress near zero — no SEA leadership pathway.
    Economic stagnation — GDP growth < 2% annually.

Author: Kaung Htet
License: MIT
================================================================================
"""

from __future__ import annotations

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
import random
import pandas as pd
from pathlib import Path

from config.constitution import CONSTITUTION
from model import KaNovaModel

RESULTS_DIR = Path("results") / "scenario_c"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)


# Scenario C parameters — calibrated from real Myanmar data
SCENARIO_C_PARAMS = {
    # Corruption stays high — no enforcement
    "corruption_floor":          0.60,
    "corruption_drift_annual":   0.005,

    # Trust declines continuously
    "trust_decay_annual":        0.008,
    "trust_floor":               0.08,

    # IIG does not exist
    "iig_effectiveness":         0.02,

    # Rights violated regularly
    "rights_violation_prob":     0.20,

    # Military coup attempts
    "coup_attempt_interval":     10,    # years between coup attempts
    "coup_success_probability":  0.55,  # historical Myanmar base rate

    # Brain drain — educated leave
    "brain_drain_annual":        0.025,

    # Economic stagnation
    "gdp_growth_cap":            0.025,

    # Ethnic tension maintained by divide-and-rule
    "ethnic_tension_floor":      0.65,

    # Foreign investment limited
    "fdi_cap":                   5,     # max active investors
}


def run_scenario_c(
    run_id: int = 0,
    n_citizens: int = None,
    n_steps: int = None,
    seed: int = None,
    verbose: bool = True
) -> pd.DataFrame:
    """
    Run one complete Scenario C simulation.

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
    seed       = seed       or (run_id * 100 + ord("C"))

    if verbose:
        print(f"\nScenario C — Run {run_id} (Military Baseline)")
        print(f"  Citizens:   {n_citizens:,}")
        print(f"  Time steps: {n_steps} years")
        print(f"  Seed:       {seed}")
        print(f"  Mode:       Military rule — no MFU rules")

    start = time.time()

    model = KaNovaModel(
        scenario="C",
        seed=seed,
        n_citizens=n_citizens
    )

    # Apply Scenario C starting conditions
    _apply_c_initial_conditions(model)

    coup_years = []
    successful_coups = 0

    for step in range(n_steps):
        model.step()

        # Apply Scenario C annual mechanics
        _apply_c_annual_mechanics(model, step)

        # Check coup attempt cycle
        if step > 0 and step % SCENARIO_C_PARAMS["coup_attempt_interval"] == 0:
            coup_result = _attempt_coup(model, step, seed)
            if coup_result == "attempted":
                coup_years.append(step)
            elif coup_result == "succeeded":
                coup_years.append(step)
                successful_coups += 1

        if verbose and (step + 1) % 10 == 0:
            print(f"  Year {step + 1:2d} | "
                  f"Corruption: {model.shared_data.get('corruption_index', 0):.3f} | "
                  f"Trust: {model.shared_data.get('trust_index', 0):.3f} | "
                  f"Coup Risk: {model.shared_data.get('coup_risk', 0):.3f} | "
                  f"Brain Drain: {model.shared_data.get('brain_drain_rate', 0):.3f}")

    elapsed = time.time() - start

    df = model.get_results()
    df["run_id"]           = run_id
    df["scenario"]         = "C"
    df["seed"]             = seed
    df["coup_count"]       = len(coup_years)
    df["successful_coups"] = successful_coups
    df["coup_years"]       = str(coup_years)

    filename = RESULTS_DIR / f"run_{str(run_id).zfill(3)}.csv"
    df.to_csv(filename, index=False)

    if verbose:
        print(f"\nScenario C Run {run_id} complete ({elapsed:.1f}s)")
        print(f"  Coup attempts:       {len(coup_years)} at years {coup_years}")
        print(f"  Successful coups:    {successful_coups}")
        print(f"  Final corruption:    {df['corruption_index'].iloc[-1]:.3f}")
        print(f"  Final trust:         {df['trust_index'].iloc[-1]:.3f}")
        print(f"  Final brain drain:   {df['brain_drain_rate'].iloc[-1]:.3f}")
        print(f"  Final north star:    {df['north_star_progress'].iloc[-1]:.3f}")
        print(f"  Saved: {filename}")

    return df


def _apply_c_initial_conditions(model: KaNovaModel):
    """Set Scenario C starting conditions — military rule baseline."""

    from agents.official import OfficialAgent

    # IIG does not exist in military baseline
    model.shared_data["iig_effectiveness"] = SCENARIO_C_PARAMS["iig_effectiveness"]

    # No shame register deterrence
    model.shared_data["corruption_deterrence"] = 0.0

    # No merit system — appointments by loyalty
    for agent in model.schedule.agents:
        if isinstance(agent, OfficialAgent):
            agent.corruption_tolerance = min(
                1.0, agent.corruption_tolerance + 0.20
            )
            agent.constitutional_loyalty = max(
                0.0, agent.constitutional_loyalty - 0.30
            )

    # Military controls all states
    for state in model.states.values():
        state["military_presence"] = 0.85
        state["ethnic_tension"] = max(
            SCENARIO_C_PARAMS["ethnic_tension_floor"],
            state.get("ethnic_tension", 0.65)
        )

    # High coup risk from start
    model.shared_data["coup_risk"] = 0.35
    model.shared_data["military_loyalty"] = 0.45


def _apply_c_annual_mechanics(model: KaNovaModel, year: int):
    """Apply Scenario C annual mechanics — military rule dynamics."""

    from agents.official import OfficialAgent
    from agents.citizen import CitizenAgent

    # Corruption drifts upward — no enforcement
    current_corruption = model.shared_data.get("corruption_index", 0.65)
    model.shared_data["corruption_index"] = min(
        0.95,
        max(
            SCENARIO_C_PARAMS["corruption_floor"],
            current_corruption + SCENARIO_C_PARAMS["corruption_drift_annual"]
        )
    )

    # Trust decays continuously
    current_trust = model.shared_data.get("trust_index", 0.22)
    model.shared_data["trust_index"] = max(
        SCENARIO_C_PARAMS["trust_floor"],
        current_trust - SCENARIO_C_PARAMS["trust_decay_annual"]
    )

    # Rights violations routine
    if random.random() < SCENARIO_C_PARAMS["rights_violation_prob"]:
        model.shared_data["rights_violated"] = True

    # GDP growth capped by instability
    for state in model.states.values():
        state["gdp_growth"] = min(
            SCENARIO_C_PARAMS["gdp_growth_cap"],
            state.get("gdp_growth", 0.02)
        )
        state["gdp"] = state.get("gdp", 100.0) * (
            1.0 + state.get("gdp_growth", 0.01)
        )

    # Ethnic tension maintained — divide and rule
    for state in model.states.values():
        state["ethnic_tension"] = max(
            SCENARIO_C_PARAMS["ethnic_tension_floor"],
            state.get("ethnic_tension", 0.65)
        )

    # Brain drain accelerates
    current_drain = model.shared_data.get("brain_drain_rate", 0.35)
    model.shared_data["brain_drain_rate"] = min(
        0.70,
        current_drain + SCENARIO_C_PARAMS["brain_drain_annual"]
    )

    # FDI stays low — governance risk
    model.shared_data["active_foreign_investors"] = min(
        model.shared_data.get("active_foreign_investors", 3),
        SCENARIO_C_PARAMS["fdi_cap"]
    )

    # Official corruption grows unchecked
    for agent in model.schedule.agents:
        if isinstance(agent, OfficialAgent):
            if random.random() < 0.15:
                agent.corruption_score = min(
                    1.0, agent.corruption_score + 0.03
                )

    # Knowledge capital stagnates — brain drain
    for state in model.states.values():
        state["knowledge_capital"] = max(
            0.0,
            state.get("knowledge_capital", 0.0) - 0.001
        )

    # Grievance rises continuously
    if hasattr(model, "citizen_array"):
        import numpy as np
        model.citizen_array["grievance"] = np.clip(
            model.citizen_array["grievance"] + 0.008,
            0.0, 1.0
        )


def _attempt_coup(model: KaNovaModel, year: int, seed: int) -> str:
    """
    Attempt a coup event.
    Based on historical Myanmar coup frequency and success rates.
    Returns: 'none', 'attempted', or 'succeeded'
    """

    coup_prob = SCENARIO_C_PARAMS["coup_success_probability"]
    military_loyalty = model.shared_data.get("military_loyalty", 0.45)
    trust = model.shared_data.get("trust_index", 0.15)

    # Lower loyalty = more likely internal coup attempt
    attempt_prob = (1.0 - military_loyalty) * 0.60 + (1.0 - trust) * 0.40

    if random.random() > attempt_prob:
        return "none"

    model.shared_data["coup_risk"] = min(1.0, coup_prob)

    if random.random() < coup_prob:
        # Coup succeeds — reset some metrics
        model.shared_data["trust_index"] = max(
            0.05,
            model.shared_data.get("trust_index", 0.15) - 0.10
        )
        model.shared_data["coup_risk"] = 0.20  # resets after success
        model.shared_data["military_loyalty"] = 0.60  # new junta has control

        # Economic disruption
        for state in model.states.values():
            state["gdp_growth"] = -0.05  # economic contraction
            state["resource_revenue"] = state.get("resource_revenue", 0.0) * 0.80

        model.shared_data.setdefault("coup_events", []).append({
            "year": year,
            "result": "succeeded",
            "trust_before": model.shared_data.get("trust_index", 0.15) + 0.10
        })
        return "succeeded"

    else:
        # Coup attempted but failed
        model.shared_data["coup_risk"] = min(
            1.0, model.shared_data.get("coup_risk", 0.35) + 0.10
        )
        model.shared_data.setdefault("coup_events", []).append({
            "year": year,
            "result": "failed_attempt"
        })
        return "attempted"


if __name__ == "__main__":

    import argparse

    parser = argparse.ArgumentParser(description="Ka-Nova Scenario C Runner")
    parser.add_argument("--runs",     type=int, default=1)
    parser.add_argument("--citizens", type=int, default=None)
    parser.add_argument("--steps",    type=int, default=None)
    parser.add_argument("--quiet",    action="store_true")
    args = parser.parse_args()

    print(f"Scenario C — Military Baseline (Current Myanmar Trajectory)")
    print(f"Runs: {args.runs}")

    all_dfs = []
    total_coups = 0

    for run_id in range(args.runs):
        df = run_scenario_c(
            run_id=run_id,
            n_citizens=args.citizens,
            n_steps=args.steps,
            verbose=not args.quiet
        )
        all_dfs.append(df)
        if "coup_count" in df.columns:
            total_coups += df["coup_count"].iloc[0]

    print(f"\nScenario C Summary ({args.runs} runs):")
    print(f"  Total coup attempts: {total_coups}")
    print(f"  Avg per run:         {total_coups / max(1, args.runs):.1f}")

    if len(all_dfs) > 1:
        combined = pd.concat(all_dfs, ignore_index=True)
        out_path = RESULTS_DIR / "scenario_c_combined.csv"
        combined.to_csv(out_path, index=False)
        print(f"  Combined results: {out_path}")
        final = combined[combined["year"] == combined["year"].max()]
        print(f"  Final year means:")
        for kpi in ["corruption_index","trust_index","coup_probability",
                    "north_star_progress","brain_drain_rate"]:
            if kpi in final.columns:
                print(f"    {kpi:<25}: {final[kpi].mean():.4f} "
                      f"(±{final[kpi].std():.4f})")