"""
================================================================================
Ka-Nova Phase 2 — Hybrid Simulation Engine
==========================================
50,000 citizens as NumPy arrays (instant init, no Mesa objects).
12 feedback loops as vectorised operations.
EliteAgentLayer (LangChain) called once per year.
All Mesa institutional agents (Officials, IIG, Foreign) handled separately
in run_hybrid.py via the existing model.py scaffold.

Why this exists:
    Mesa CitizenAgent at 50k scale = ~30 min init per worker = unusable.
    NumPy float32 array [50000, 8] = 1.6MB, init in <1 second per worker.

Citizens columns [N, 8]:
    0  wealth          [0.0, 1.0]
    1  trust           [0.0, 1.0]
    2  merit           [0.0, 1.0]
    3  corruption_exp  [0.0, 1.0]
    4  grievance       [0.0, 1.0]
    5  age             [18, 80]
    6  brain_drain     [0.0, 1.0]
    7  employment      [0.0, 1.0]  binary as float

Author: Kaung Htet | MSc Data Science | University of Hertfordshire
================================================================================
"""

from __future__ import annotations

import numpy as np
import polars as pl
from dataclasses import dataclass, field
from pathlib import Path
import logging

logger = logging.getLogger("ka_nova.hybrid")

# ── 14 Myanmar states ────────────────────────────────────────────────────────
STATE_NAMES = [
    "sagaing", "mandalay", "magway", "bago", "yangon",
    "ayeyarwady", "tanintharyi", "shan_eastern", "kachin_northern",
    "kayah", "karen_southern", "chin", "mon", "rakhine",
]

STATE_GDP_WEIGHTS = np.array(
    [0.07, 0.10, 0.05, 0.06, 0.18, 0.08, 0.04,
     0.10, 0.06, 0.02, 0.05, 0.03, 0.06, 0.10],
    dtype=np.float64
)
STATE_GDP_WEIGHTS /= STATE_GDP_WEIGHTS.sum()

# ── 8 ethnic groups ──────────────────────────────────────────────────────────
ETHNIC_NAMES = ["Bamar", "Shan", "Karen", "Kachin", "Chin", "Mon", "Rakhine", "Kayah"]

# Per-state ethnic composition [14 × 8] — Myanmar 2014 census
STATE_ETHNIC_COMP = np.array([
    [0.85, 0.03, 0.01, 0.05, 0.04, 0.01, 0.00, 0.01],  # sagaing
    [0.90, 0.02, 0.01, 0.02, 0.02, 0.02, 0.00, 0.01],  # mandalay
    [0.92, 0.02, 0.01, 0.01, 0.02, 0.01, 0.00, 0.01],  # magway
    [0.85, 0.02, 0.05, 0.02, 0.01, 0.04, 0.00, 0.01],  # bago
    [0.75, 0.05, 0.06, 0.02, 0.02, 0.05, 0.02, 0.03],  # yangon
    [0.90, 0.02, 0.02, 0.01, 0.01, 0.03, 0.00, 0.01],  # ayeyarwady
    [0.80, 0.03, 0.08, 0.01, 0.02, 0.05, 0.00, 0.01],  # tanintharyi
    [0.20, 0.60, 0.04, 0.06, 0.02, 0.02, 0.02, 0.04],  # shan_eastern
    [0.30, 0.10, 0.02, 0.48, 0.04, 0.01, 0.01, 0.04],  # kachin_northern
    [0.30, 0.10, 0.08, 0.02, 0.08, 0.02, 0.01, 0.39],  # kayah
    [0.30, 0.10, 0.52, 0.02, 0.02, 0.02, 0.01, 0.01],  # karen_southern
    [0.30, 0.02, 0.02, 0.04, 0.56, 0.01, 0.02, 0.03],  # chin
    [0.50, 0.05, 0.08, 0.02, 0.01, 0.30, 0.02, 0.02],  # mon
    [0.30, 0.02, 0.03, 0.01, 0.01, 0.02, 0.60, 0.01],  # rakhine
], dtype=np.float32)
STATE_ETHNIC_COMP = STATE_ETHNIC_COMP / STATE_ETHNIC_COMP.sum(axis=1, keepdims=True)

# ── 7 archetypes ─────────────────────────────────────────────────────────────
ARCHETYPE_NAMES = [
    "civic_champion", "pragmatic_survivor", "ethnic_loyalist",
    "ambitious_meritocrat", "disillusioned_youth", "rural_traditionalist",
    "trauma_carrier",
]
ARCHETYPE_PROPS  = np.array([0.15, 0.30, 0.20, 0.15, 0.10, 0.07, 0.03], dtype=np.float64)
ARCHETYPE_TRUST  = np.array([0.55, 0.35, 0.30, 0.50, 0.25, 0.40, 0.15], dtype=np.float32)
ETHNIC_HARM_W    = np.array([0.05, 0.20, 0.18, 0.22, 0.25, 0.12, 0.28, 0.30], dtype=np.float32)

# ── Article VIII v7 ──────────────────────────────────────────────────────────
RESOURCE_DIRECT_SHARE   = 0.30
TRUST_ACCEL_MULT        = 1.50
TRUST_ACCEL_CORR_CEIL   = 0.20
TRUST_ACCEL_MIN_YEARS   = 5


# ── Scenario modifiers ───────────────────────────────────────────────────────
SCENARIO_MODS = {
    "A": dict(iig_growth=0.04, corruption_decay=0.06, trust_floor=0.30,
              coup_block=True,  article8=True,  safeguards=True,  trust_accel=True),
    "B": dict(iig_growth=0.025, corruption_decay=0.02, trust_floor=0.20,
              coup_block=False, article8=True,  safeguards=False, trust_accel=False),
    "C": dict(iig_growth=0.00, corruption_decay=-0.03, trust_floor=0.05,
              coup_block=False, article8=False, safeguards=False, trust_accel=False),
}


# ── SimState ─────────────────────────────────────────────────────────────────
@dataclass
class SimState:
    year:     int   = 0
    scenario: str   = "A"

    # Citizen arrays
    pop:          np.ndarray = field(default_factory=lambda: np.empty(0))
    ethnic_group: np.ndarray = field(default_factory=lambda: np.empty(0, dtype=np.int8))
    state_id:     np.ndarray = field(default_factory=lambda: np.empty(0, dtype=np.int8))
    archetype:    np.ndarray = field(default_factory=lambda: np.empty(0, dtype=np.int8))

    # Macro KPIs — Year Zero Myanmar baselines
    corruption_index:  float = 0.72
    trust_index:       float = 0.22
    gini_coefficient:  float = 0.55
    employment_rate:   float = 0.58
    iig_effectiveness: float = 0.30
    coup_probability:  float = 0.25
    brain_drain_rate:  float = 0.35
    stability_index:   float = 0.18
    ethnic_harmony:    float = 0.32
    north_star_progress: float = 0.10
    gdp_growth:        float = 0.02

    # Trackers
    low_corruption_streak: int  = 0
    total_ruin_events:     int  = 0
    elite_log:             list = field(default_factory=list)

    @property
    def n_citizens(self) -> int:
        return len(self.pop)


# ── Population init ───────────────────────────────────────────────────────────
def init_population(n: int, scenario: str, rng: np.random.Generator) -> SimState:
    """
    Initialise N citizens as NumPy arrays.
    Total time: <1 second for 50k citizens.
    (vs ~30 minutes for 50k Mesa CitizenAgent objects)
    """
    state = SimState(year=0, scenario=scenario)

    # State assignment by GDP weight
    state_ids = rng.choice(14, size=n, p=STATE_GDP_WEIGHTS).astype(np.int8)

    # Ethnic assignment per state
    ethnic_ids = np.empty(n, dtype=np.int8)
    for sid in range(14):
        mask = state_ids == sid
        cnt  = int(mask.sum())
        if cnt > 0:
            ethnic_ids[mask] = rng.choice(8, size=cnt, p=STATE_ETHNIC_COMP[sid]).astype(np.int8)

    # Archetype assignment
    arch_ids = rng.choice(7, size=n, p=ARCHETYPE_PROPS).astype(np.int8)

    # Continuous attributes [N, 8] float32
    pop = np.zeros((n, 8), dtype=np.float32)

    # Wealth — lognormal calibrated to Gini=0.55
    raw_w = rng.lognormal(0, 1, n).astype(np.float32)
    pop[:, 0] = np.clip(raw_w / (raw_w.max() + 1e-9), 0.01, 1.0)

    # Trust — archetype base ± noise
    pop[:, 1] = np.clip(
        ARCHETYPE_TRUST[arch_ids] + rng.normal(0, 0.05, n).astype(np.float32),
        0.0, 1.0
    )

    # Merit — correlated with wealth, penalised by ethnic marginalisation
    ethnic_penalty = ETHNIC_HARM_W[ethnic_ids] * 0.3
    pop[:, 2] = np.clip(
        pop[:, 0] * 0.6 + rng.uniform(0.05, 0.35, n).astype(np.float32) - ethnic_penalty,
        0.01, 1.0
    )

    # Corruption exposure — inverse of state GDP
    state_gdp = STATE_GDP_WEIGHTS[state_ids].astype(np.float32)
    pop[:, 3] = np.clip(0.60 - state_gdp * 2.0 + rng.normal(0, 0.08, n).astype(np.float32), 0.0, 1.0)

    # Grievance — high in ethnic periphery
    pop[:, 4] = np.clip(
        ETHNIC_HARM_W[ethnic_ids] * 0.8 + rng.normal(0, 0.10, n).astype(np.float32),
        0.0, 1.0
    )

    # Age — working population
    pop[:, 5] = rng.uniform(18, 65, n).astype(np.float32)

    # Brain drain — elevated for disillusioned youth (4) and meritocrats (3)
    drain_base = np.where(arch_ids == 4, 0.55, np.where(arch_ids == 3, 0.30, 0.15)).astype(np.float32)
    pop[:, 6] = np.clip(drain_base + rng.normal(0, 0.08, n).astype(np.float32), 0.0, 1.0)

    # Employment — Myanmar baseline 0.58
    pop[:, 7] = (rng.uniform(0, 1, n).astype(np.float32) < 0.58).astype(np.float32)

    state.pop          = pop
    state.ethnic_group = ethnic_ids
    state.state_id     = state_ids
    state.archetype    = arch_ids
    return state


# ── Vectorised citizen update ─────────────────────────────────────────────────
def update_citizens(
    state: SimState,
    budget_impact: float,
    ethnic_weights: np.ndarray,
    article8_active: bool,
    trust_accel: bool,
    rng: np.random.Generator,
) -> SimState:
    """
    Annual update for all N citizens — fully vectorised NumPy.
    Zero Python loops over agents.

    Trust formula (Article VIII):
        Trust(t+1) = Trust(t) + (budget_impact × ethnic_weight) - (corruption × 0.5)
    """
    pop = state.pop
    n   = len(pop)

    ew          = ethnic_weights[state.ethnic_group]   # [N] per-citizen weight
    corruption  = state.corruption_index

    # Trust update
    delta_trust = (budget_impact * ew - corruption * 0.5).astype(np.float32)
    noise_scale = np.array([0.02, 0.05, 0.04, 0.02, 0.06, 0.03, 0.07], dtype=np.float32)
    delta_trust += (rng.standard_normal(n) * noise_scale[state.archetype]).astype(np.float32)
    if trust_accel:
        delta_trust *= TRUST_ACCEL_MULT
    pop[:, 1] = np.clip(pop[:, 1] + delta_trust, 0.0, 1.0)

    # Article VIII progressive household transfer (Gini fix)
    if article8_active:
        pop = _article8_transfer(pop, budget_impact)

    # Grievance
    pop[:, 4] = np.clip(pop[:, 4] + corruption * 0.3 - delta_trust * 0.5, 0.0, 1.0)

    # Brain drain
    pop[:, 6] = np.clip(
        pop[:, 6] + (pop[:, 4] * 0.4 + pop[:, 2] * 0.3 - pop[:, 7] * 0.3) * 0.1,
        0.0, 1.0
    )

    # Age
    pop[:, 5] += 1.0

    # Employment
    gdp = state.gdp_growth
    emp_prob = np.clip(
        0.58 + gdp * 5.0 - corruption * 0.3 + pop[:, 2] * 0.2, 0.30, 0.95
    ).astype(np.float32)
    pop[:, 7] = (rng.random(n).astype(np.float32) < emp_prob).astype(np.float32)

    state.pop = pop
    return state


def _article8_transfer(pop: np.ndarray, budget_impact: float) -> np.ndarray:
    """
    Progressive direct-to-household transfer — the Gini fix.
    Bottom 40%: 1.5× per-capita. Top 60%: 0.67× per-capita.
    Fully vectorised — O(N log N).
    """
    n        = len(pop)
    wealth   = pop[:, 0]
    ranks    = np.argsort(np.argsort(wealth))
    pct      = ranks / n
    base     = (budget_impact * RESOURCE_DIRECT_SHARE) / n
    transfer = np.where(pct < 0.40, base * 1.5, base * 0.67).astype(np.float32)
    pop[:, 0] = np.clip(wealth + transfer, 0.0, 1.0)
    return pop


# ── KPI computation ───────────────────────────────────────────────────────────
def compute_gini(wealth: np.ndarray) -> float:
    w = np.sort(wealth.astype(np.float64))
    n = len(w)
    if n == 0 or w.sum() == 0:
        return 0.0
    idx = np.arange(1, n + 1, dtype=np.float64)
    return float((2.0 * (idx * w).sum()) / (n * w.sum() + 1e-12) - (n + 1.0) / n)


def recompute_kpis(state: SimState) -> SimState:
    pop = state.pop
    state.trust_index     = float(np.mean(pop[:, 1]))
    state.gini_coefficient = compute_gini(pop[:, 0])
    working = (pop[:, 5] >= 18) & (pop[:, 5] <= 65)
    state.employment_rate = float(np.mean(pop[working, 7])) if working.sum() > 0 else 0.58
    state.brain_drain_rate = float(np.mean(pop[:, 6] > 0.65))

    scores = []
    for g in range(8):
        mask = state.ethnic_group == g
        if mask.sum() > 0:
            scores.append(float(np.mean(pop[mask, 1])) - float(np.mean(pop[mask, 4])))
    state.ethnic_harmony = float(np.clip(np.mean(scores) + 0.5, 0.0, 1.0)) if scores else 0.5

    state.north_star_progress = float(np.clip(
        (1.0 - state.corruption_index) * 0.20
        + state.trust_index * 0.15
        + (1.0 - state.coup_probability) * 0.15
        + state.iig_effectiveness * 0.15
        + min(state.gdp_growth * 5.0, 1.0) * 0.15
        + state.ethnic_harmony * 0.10
        + (1.0 - state.gini_coefficient) * 0.10,
        0.0, 1.0
    ))
    return state


# ── Feedback loops ────────────────────────────────────────────────────────────
def apply_feedback_loops(state: SimState, mods: dict, rng: np.random.Generator) -> SimState:
    # P2: IIG-Corruption
    if mods["iig_growth"] > 0:
        state.iig_effectiveness = min(state.iig_effectiveness + mods["iig_growth"], 1.0)
        state.corruption_index  = max(
            state.corruption_index - mods["corruption_decay"] * state.iig_effectiveness, 0.0
        )
    else:
        state.corruption_index = min(state.corruption_index - mods["corruption_decay"], 1.0)

    # E1: GDP
    state.gdp_growth = float(np.clip(
        0.045 - state.corruption_index * 0.03
        + state.iig_effectiveness * 0.02
        + (1.0 - state.gini_coefficient) * 0.01,
        -0.02, 0.12
    ))

    # P1: Trust inertia
    pop_trust = float(np.mean(state.pop[:, 1]))
    state.trust_index = float(0.70 * state.trust_index + 0.30 * pop_trust)
    state.trust_index = max(state.trust_index, mods["trust_floor"])

    # S4: Shame register deterrence S-curve
    if mods["safeguards"]:
        shame = 1.0 / (1.0 + np.exp(-10.0 * (state.iig_effectiveness - 0.5)))
        state.corruption_index = max(state.corruption_index - float(shame) * 0.02, 0.0)

    # E3: ECB emergency redistribution if Gini > 0.45
    if mods["article8"] and state.gini_coefficient > 0.45:
        ecb_boost = (state.gini_coefficient - 0.45) * 0.5
        wealth = state.pop[:, 0]
        thresh = float(np.percentile(wealth, 30))
        mask   = wealth < thresh
        state.pop[mask, 0] = np.clip(state.pop[mask, 0] + ecb_boost * 0.05, 0.0, 1.0)

    # Stability composite
    state.stability_index = float(np.clip(
        state.trust_index * 0.35
        + (1.0 - state.corruption_index) * 0.25
        + state.iig_effectiveness * 0.20
        + (1.0 - state.coup_probability) * 0.20,
        0.0, 1.0
    ))

    return state


# ── Main scenario runner ──────────────────────────────────────────────────────
def run_scenario_hybrid(
    scenario:       str,
    n_citizens:     int,
    n_steps:        int,
    seed:           int,
    elite_layer,
    checkpoint_dir: Path,
    checkpoint_every: int = 5,
) -> pl.DataFrame:
    """
    Run one scenario — fully hybrid:
        Citizens  → NumPy arrays (this file)
        Elites    → LangChain LLM (engine/elite_agents.py)
        Feedback  → vectorised scalar operations (this file)

    Returns Polars DataFrame of KPI trajectories.
    """
    rng  = np.random.default_rng(seed)
    mods = SCENARIO_MODS[scenario]

    state = init_population(n_citizens, scenario, rng)
    rows  = []

    for year in range(n_steps):
        state.year = year

        # ── 1. Elite deliberation ─────────────────────────────────────────────
        shared = {
            "year":              year,
            "gini_coefficient":  state.gini_coefficient,
            "trust_index":       state.trust_index,
            "corruption_index":  state.corruption_index,
            "coup_risk":         state.coup_probability,
            "iig_effectiveness": state.iig_effectiveness,
            "employment_rate":   state.employment_rate,
            "brain_drain_rate":  state.brain_drain_rate,
            "ethnic_harmony_index": state.ethnic_harmony,
        }
        try:
            elite_layer.step(shared, year, scenario)
            budget_impact  = float(shared.get("elite_budget_impact", 0.07))
            ethnic_weights = np.array(shared.get("elite_ethnic_weights", [1.0]*8), dtype=np.float32)
            coup_signal    = bool(shared.get("elite_coup_signal", False))
        except Exception as e:
            logger.warning(f"[{scenario}] Year {year}: elite failed ({e}), using defaults")
            budget_impact  = 0.07
            ethnic_weights = np.ones(8, dtype=np.float32)
            coup_signal    = False

        state.elite_log.append({"year": year, "budget_impact": budget_impact,
                                 "coup_signal": coup_signal})

        # ── 2. Coup check ─────────────────────────────────────────────────────
        if mods["coup_block"]:
            state.coup_probability = 0.0
        elif coup_signal:
            state.coup_probability = min(state.coup_probability + 0.05, 1.0)
            state.iig_effectiveness = max(state.iig_effectiveness - 0.10, 0.0)

        # ── 3. Citizen update (vectorised) ────────────────────────────────────
        trust_accel = (
            mods["trust_accel"]
            and state.low_corruption_streak >= TRUST_ACCEL_MIN_YEARS
        )
        state = update_citizens(
            state, budget_impact, ethnic_weights,
            mods["article8"], trust_accel, rng
        )

        # ── 4. Feedback loops ─────────────────────────────────────────────────
        state = apply_feedback_loops(state, mods, rng)

        # ── 5. Recompute KPIs ─────────────────────────────────────────────────
        state = recompute_kpis(state)

        # ── 6. Trust acceleration counter ─────────────────────────────────────
        if state.corruption_index < TRUST_ACCEL_CORR_CEIL:
            state.low_corruption_streak += 1
        else:
            state.low_corruption_streak = 0

        # ── 7. Record ─────────────────────────────────────────────────────────
        rows.append({
            "scenario":            scenario,
            "year":                year,
            "run_id":              seed,
            "corruption_index":    round(state.corruption_index,  4),
            "trust_index":         round(state.trust_index,        4),
            "gini_coefficient":    round(state.gini_coefficient,   4),
            "coup_probability":    round(state.coup_probability,   4),
            "iig_effectiveness":   round(state.iig_effectiveness,  4),
            "employment_rate":     round(state.employment_rate,    4),
            "brain_drain_rate":    round(state.brain_drain_rate,   4),
            "ethnic_harmony":      round(state.ethnic_harmony,     4),
            "north_star_progress": round(state.north_star_progress,4),
            "stability_index":     round(state.stability_index,    4),
            "gdp_growth":          round(state.gdp_growth,         4),
            "budget_impact":       round(budget_impact,            4),
        })

        # ── 8. Checkpoint every 5 years ───────────────────────────────────────
        if (year + 1) % checkpoint_every == 0:
            _save_checkpoint(state, checkpoint_dir, seed)

    return pl.DataFrame(rows)


# ── Checkpoint ────────────────────────────────────────────────────────────────
def _save_checkpoint(state: SimState, checkpoint_dir: Path, seed: int) -> None:
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    fname = (checkpoint_dir /
             f"ck_s{state.scenario}_seed{seed:04d}_yr{state.year:02d}.parquet")
    pl.DataFrame({
        "wealth":         state.pop[:, 0].tolist(),
        "trust":          state.pop[:, 1].tolist(),
        "merit":          state.pop[:, 2].tolist(),
        "corruption_exp": state.pop[:, 3].tolist(),
        "grievance":      state.pop[:, 4].tolist(),
        "age":            state.pop[:, 5].tolist(),
        "brain_drain":    state.pop[:, 6].tolist(),
        "employment":     state.pop[:, 7].tolist(),
        "ethnic_group":   state.ethnic_group.tolist(),
        "state_id":       state.state_id.tolist(),
        "archetype":      state.archetype.tolist(),
    }).write_parquet(fname, compression="zstd")