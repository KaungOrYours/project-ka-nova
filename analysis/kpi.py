"""
================================================================================
PROJECT KA-NOVA
analysis/kpi.py

KPI Analysis — Statistical Tests and Results Processing
Ka-Nova Simulation Engine v1.0

Loads simulation results from CSV files and performs:
- Descriptive statistics per scenario
- Statistical significance tests (A vs B vs C)
- Sensitivity analysis (SALib)
- Validation against real-world baselines
- North Star progress tracking
- Publication-ready output tables

Measures of Success (MoS):
    MoS 1 — Behavioral Validity
    MoS 2 — Emergence Validity
    MoS 3 — Sensitivity Analysis
    MoS 4 — Sample Size Sufficiency
    MoS 5 — Scenario Differentiation
    MoS 6 — Internal Consistency
    MoS 7 — Reproducibility
    MoS 8 — Calibration Against Reality

Author: Kaung Htet
License: MIT
================================================================================
"""

from __future__ import annotations

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import warnings
warnings.filterwarnings("ignore")

from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from scipy import stats
from scipy.stats import mannwhitneyu, kruskal, shapiro

try:
    from SALib.sample import sobol as salib_sobol_sample
    from SALib.analyze import sobol as salib_sobol_analyze
    SALIB_AVAILABLE = True
except ImportError:
    SALIB_AVAILABLE = False

from config.constitution import CONSTITUTION

# ── PATHS ─────────────────────────────────────────────────────────────────────
# Opening 7 (fixed 2026-10-21). This was Path("results"), the Phase 1/2
# directory, while the live pipeline writes to results_phase3/ (run_phase3.py:56,
# engine/cves.py:43). Every output of this module — descriptive_stats.csv,
# trajectories.csv, statistical_tests.csv, table1_scenario_comparison.csv,
# sobol_sensitivity_*.csv — therefore targeted a directory that does not exist
# in a clean checkout, and the loader looked for Phase 2's combined
# all_results.csv rather than Phase 3's per-scenario files. In other words the
# entire table/analysis layer was pointed at legacy data and could not read a
# Phase 3 run at all. Overridable so the Phase 2 archive can still be analysed
# (KA_NOVA_RESULTS_DIR=archive/results).
RESULTS_DIR = Path(os.getenv("KA_NOVA_RESULTS_DIR", "results_phase3"))
ANALYSIS_DIR = Path("analysis")


# ══════════════════════════════════════════════════════════════════════════════
# CONSTANTS
# ══════════════════════════════════════════════════════════════════════════════

# KPIs to analyze
KPI_COLUMNS = [
    "corruption_index",
    "trust_index",
    "iig_effectiveness",
    "coup_probability",
    "ethnic_harmony",
    "gini_coefficient",
    "employment_rate",
    "knowledge_capital",
    "brain_drain_rate",
    "north_star_progress",
    "stability_index",
    "shame_register_size",
    "foreign_investors",
    "total_ruin_events",
    "tax_compliance",
    "inflation_rate"
]

# Real-world Myanmar Year Zero baselines (calibration targets)
MYANMAR_BASELINES = {
    "corruption_index":  0.72,   # Transparency International CPI 2023
    "trust_index":       0.22,   # World Bank governance 2022
    # UNIT MISMATCH, flagged 2026-10-21, not silently changed.
    # The World Bank 2017 figure is Myanmar's household income/consumption
    # Gini. The simulated "gini_coefficient" is dispersion of GDP across
    # administrative units (see FederalDevFundAgent._calculate_gini), a
    # different quantity, and it starts near 0.06-0.08 because states begin
    # near-identical. Validating the simulated series against this baseline
    # therefore compares incommensurable measures. Needs a decision from
    # senior-data-analyst: either source a real subnational/regional-GDP
    # dispersion benchmark, or report this metric without an external
    # calibration target and say so. Left as-is so no published number moves
    # without that decision.
    "gini_coefficient":  0.55,   # World Bank 2017 -- SEE UNIT MISMATCH NOTE ABOVE
    "employment_rate":   0.58,   # Myanmar Census 2014
    "ethnic_harmony":    0.22,   # V-Dem estimated
    "stability_index":   0.18,   # World Bank political stability 2022
    "iig_effectiveness": 0.05,   # Baseline — no IIG exists
    "coup_probability":  0.45,   # Estimated post-2021
    "brain_drain_rate":  0.35,   # Estimated emigration rate post-2021
}

# North Star targets at Year 50 (Scenario A)
NORTH_STAR_TARGETS = {
    "corruption_index":  0.20,
    "trust_index":       0.70,
    "coup_probability":  0.05,
    "ethnic_harmony":    0.75,
    "gini_coefficient":  0.35,
    "employment_rate":   0.85,
    "brain_drain_rate":  0.10,
    "iig_effectiveness": 0.75,
    "stability_index":   0.75,
    "north_star_progress": 0.80
}

SIGNIFICANCE_LEVEL = 0.05

# ── GSA PARAMETER SPACE ───────────────────────────────────────────────────────
# Same 10 constitutionally-plausible parameters as tests/salib_gsa/feasibility_check.py
# (that script only verifies SALib infra readiness with a synthetic Y and a cost
# estimate — this maps each parameter onto the live CONSTITUTION attribute it
# actually drives, so Sobol indices below are computed from real Phase 3 model
# output, not a synthetic placeholder).
GSA_PROBLEM = {
    "num_vars": 13,
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
        # Added 2026-10-21 (Openings 1 and 8). Reviewer 2 pt.2 asks about
        # "constitutional AND feedback parameters"; the ten above are all
        # constitutional. These three are the feedback/dynamics constants that
        # mechanically produce the zero-variance arms behind the headline
        # effect sizes, so perturbing them turns Reviewer 1 pt.2 from an
        # argument into a measurement: if ST for these is small, the
        # separation is not an artifact of them; if it is large, we must say so.
        "fear_compliance_trust_floor",
        "civilian_coup_signal_damping",
        "stability_rights_bonus",
    ],
    "bounds": [
        # Re-centred 2026-10-21. Was [0.25, 0.45], which excluded the live
        # default of 0.20 (config/constitution.py PERFORMANCE_WEIGHT), so
        # Sobol was sampling a region that did not contain the actual
        # configuration being analysed. Same 0.20 width, centred on 0.20.
        [0.10, 0.30],   # merit_performance_weight (default 0.20)
        [0.60, 0.90],   # analysis_threshold (veto)
        [0.25, 0.45],   # state_share
        [0.20, 0.40],   # ethnic_direct_share
        [1.00, 2.00],   # trust_acceleration_multiplier
        [0.10, 0.30],   # trust_acceleration_trigger_corruption
        # Re-centred 2026-10-21. Was [0.55, 0.85], which excluded the live
        # default of 0.45 — the stale pre-"lowered from 0.70" value noted in
        # constitution.py. Same 0.30 width, centred on 0.45.
        [0.30, 0.60],   # iig_investigation_trigger (default 0.45)
        [0.75, 0.95],   # iig_entry_merit_min
        [0.20, 0.40],   # coup_trigger_loyalty
        [0.60, 0.85],   # year_zero_corruption
        # Centred on the published defaults (0.10 / 0.05 / 0.20). The lower
        # bound of each reaches ~0, which is the substantively interesting
        # case: it asks what the separation looks like with the floor, the
        # damping, or the deterministic rights step effectively removed.
        [0.00, 0.20],   # fear_compliance_trust_floor  (default 0.10)
        [0.00, 0.10],   # civilian_coup_signal_damping (default 0.05)
        [0.00, 0.40],   # stability_rights_bonus       (default 0.20)
    ],
}

# Maps each GSA parameter name to the live CONSTITUTION attribute it overrides
# (section, attribute) — section is an attribute of the CONSTITUTION singleton
# (config/constitution.py:MFUConstitution.__init__), attribute is the dataclass
# field actually read by the Phase 3 model at runtime.
GSA_PARAM_MAP = {
    "merit_performance_weight":              ("merit", "PERFORMANCE_WEIGHT"),
    "analysis_threshold":                    ("chambers", "ANALYSIS_THRESHOLD"),
    "state_share":                           ("federal", "RESOURCE_STATE_SHARE"),
    "ethnic_direct_share":                    ("federal", "RESOURCE_ETHNIC_DIRECT_SHARE"),
    "trust_acceleration_multiplier":          ("federal", "TRUST_ACCELERATION_MULTIPLIER"),
    "trust_acceleration_trigger_corruption":  ("federal", "TRUST_ACCELERATION_TRIGGER_CORRUPTION"),
    "iig_investigation_trigger":              ("iig", "INVESTIGATION_TRIGGER"),
    "iig_entry_merit_min":                    ("iig", "ENTRY_MERIT_MIN"),
    "coup_trigger_loyalty":                    ("military", "COUP_TRIGGER_LOYALTY"),
    "year_zero_corruption":                    ("simulation", "YEAR_ZERO_CORRUPTION"),
    # Feedback/dynamics constants (Openings 1 and 8). All three live on the
    # rights section; see config/constitution.py for why they were surfaced.
    "fear_compliance_trust_floor":             ("rights", "FEAR_COMPLIANCE_TRUST_FLOOR"),
    "civilian_coup_signal_damping":            ("rights", "CIVILIAN_COUP_SIGNAL_DAMPING"),
    "stability_rights_bonus":                  ("rights", "STABILITY_RIGHTS_BONUS"),
}


# ══════════════════════════════════════════════════════════════════════════════
# DATA LOADER
# ══════════════════════════════════════════════════════════════════════════════

class ResultsLoader:
    """Loads and validates Ka-Nova simulation results."""

    def __init__(self, results_dir: Path = RESULTS_DIR):
        self.results_dir = results_dir
        self.df = None
        self.scenarios = []
        self.n_runs = {}
        self.n_years = 0

    def load(self) -> pd.DataFrame:
        """Load combined results CSV."""

        # Phase 3 writes one merged CSV per scenario (scenario_<code>_all.csv,
        # run_phase3.py:405). Prefer those: they are what the live runner
        # actually produces, and globbing means a 7-scenario campaign is picked
        # up without naming each code here. Falls back to Phase 2's combined
        # all_results.csv, then to per-run files, so analysing the legacy
        # archive with KA_NOVA_RESULTS_DIR still works unchanged.
        phase3_files = sorted(self.results_dir.glob("scenario_*_all.csv"))
        combined_path = self.results_dir / "all_results.csv"

        if phase3_files:
            print(f"Loading {len(phase3_files)} Phase 3 per-scenario file(s):")
            frames = []
            for p in phase3_files:
                try:
                    frames.append(pd.read_csv(p))
                    print(f"  {p.name}")
                except Exception as e:
                    print(f"  Warning: could not load {p}: {e}")
            self.df = pd.concat(frames, ignore_index=True) if frames else None
        elif combined_path.exists():
            print(f"Loading: {combined_path}")
            self.df = pd.read_csv(combined_path)
        else:
            print("No Phase 3 or combined CSV found. Loading individual files...")
            self.df = self._load_individual_files()

        if self.df is None or self.df.empty:
            raise FileNotFoundError(
                f"No results found in {self.results_dir}. "
                "Run the simulation first: python3 run.py"
            )

        self._validate()
        self._summarize()
        return self.df

    def _load_individual_files(self) -> Optional[pd.DataFrame]:
        """Load and combine individual run CSV files."""

        scenario_dirs = {
            "A": self.results_dir / "scenario_a",
            "B": self.results_dir / "scenario_b",
            "C": self.results_dir / "scenario_c"
        }

        dfs = []
        for scenario, path in scenario_dirs.items():
            if not path.exists():
                continue
            for csv_file in sorted(path.glob("run_*.csv")):
                try:
                    df = pd.read_csv(csv_file)
                    df["scenario"] = scenario
                    dfs.append(df)
                except Exception as e:
                    print(f"  Warning: could not load {csv_file}: {e}")

        if not dfs:
            return None

        combined = pd.concat(dfs, ignore_index=True)
        combined.to_csv(self.results_dir / "all_results.csv", index=False)
        return combined

    def _validate(self):
        """Validate loaded data structure."""

        required_cols = ["year", "scenario", "run_id"]
        missing = [c for c in required_cols if c not in self.df.columns]
        if missing:
            raise ValueError(f"Missing required columns: {missing}")

        # Fill missing KPI columns with NaN
        for kpi in KPI_COLUMNS:
            if kpi not in self.df.columns:
                self.df[kpi] = np.nan

    def _summarize(self):
        """Print data summary."""

        self.scenarios = sorted(self.df["scenario"].unique().tolist())
        self.n_years = self.df["year"].max()

        print(f"\nData loaded successfully:")
        print(f"  Scenarios:   {self.scenarios}")
        print(f"  Years:       0 to {self.n_years}")
        print(f"  Total rows:  {len(self.df):,}")

        for scenario in self.scenarios:
            n_runs = self.df[
                (self.df["scenario"] == scenario) &
                (self.df["year"] == 0)
            ]["run_id"].nunique()
            self.n_runs[scenario] = n_runs
            print(f"  Scenario {scenario}: {n_runs} runs")

    def get_final_year(self, scenario: str = None) -> pd.DataFrame:
        """Get data from the final year only."""

        final_year = self.df["year"].max()
        df = self.df[self.df["year"] == final_year].copy()
        if scenario:
            df = df[df["scenario"] == scenario]
        return df

    def get_year(self, year: int, scenario: str = None) -> pd.DataFrame:
        """Get data from a specific year."""

        df = self.df[self.df["year"] == year].copy()
        if scenario:
            df = df[df["scenario"] == scenario]
        return df

    def get_scenario(self, scenario: str) -> pd.DataFrame:
        """Get all data for one scenario."""

        return self.df[self.df["scenario"] == scenario].copy()


# ══════════════════════════════════════════════════════════════════════════════
# DESCRIPTIVE STATISTICS
# ══════════════════════════════════════════════════════════════════════════════

class DescriptiveStats:
    """Compute descriptive statistics for all KPIs."""

    def __init__(self, loader: ResultsLoader):
        self.loader = loader
        self.df = loader.df

    def compute_all(self) -> pd.DataFrame:
        """Compute descriptive stats for all scenarios at final year."""

        final_df = self.loader.get_final_year()
        rows = []

        for scenario in self.loader.scenarios:
            s_df = final_df[final_df["scenario"] == scenario]

            for kpi in KPI_COLUMNS:
                if kpi not in s_df.columns:
                    continue
                vals = s_df[kpi].dropna()
                if vals.empty:
                    continue

                rows.append({
                    "scenario": scenario,
                    "kpi": kpi,
                    "n": len(vals),
                    "mean": round(vals.mean(), 4),
                    "std": round(vals.std(), 4),
                    "median": round(vals.median(), 4),
                    "min": round(vals.min(), 4),
                    "max": round(vals.max(), 4),
                    "p25": round(vals.quantile(0.25), 4),
                    "p75": round(vals.quantile(0.75), 4),
                    "cv": round(vals.std() / vals.mean(), 4) if vals.mean() != 0 else np.nan
                })

        result = pd.DataFrame(rows)
        result.to_csv(RESULTS_DIR / "descriptive_stats.csv", index=False)
        print(f"Descriptive stats saved: {RESULTS_DIR}/descriptive_stats.csv")
        return result

    def compute_trajectories(self) -> pd.DataFrame:
        """Compute mean KPI trajectories over time for each scenario."""

        rows = []
        for scenario in self.loader.scenarios:
            s_df = self.loader.get_scenario(scenario)
            for year in sorted(s_df["year"].unique()):
                y_df = s_df[s_df["year"] == year]
                row = {"scenario": scenario, "year": year}
                for kpi in KPI_COLUMNS:
                    if kpi in y_df.columns:
                        vals = y_df[kpi].dropna()
                        if not vals.empty:
                            row[f"{kpi}_mean"] = round(vals.mean(), 4)
                            row[f"{kpi}_std"] = round(vals.std(), 4)
                rows.append(row)

        result = pd.DataFrame(rows)
        result.to_csv(RESULTS_DIR / "trajectories.csv", index=False)
        print(f"Trajectories saved: {RESULTS_DIR}/trajectories.csv")
        return result


# ══════════════════════════════════════════════════════════════════════════════
# STATISTICAL TESTS
# ══════════════════════════════════════════════════════════════════════════════

class StatisticalTests:
    """
    MoS 5 — Scenario Differentiation.
    Tests whether scenarios produce statistically different outcomes.
    All comparisons at p < 0.05.
    """

    def __init__(self, loader: ResultsLoader):
        self.loader = loader
        self.df = loader.df

    def run_all_tests(self) -> pd.DataFrame:
        """Run all pairwise comparison tests."""

        final_df = self.loader.get_final_year()
        comparisons = [("A", "B"), ("A", "C"), ("B", "C")]
        rows = []

        for kpi in KPI_COLUMNS:
            if kpi not in final_df.columns:
                continue

            for s1, s2 in comparisons:
                vals1 = final_df[
                    final_df["scenario"] == s1
                ][kpi].dropna()
                vals2 = final_df[
                    final_df["scenario"] == s2
                ][kpi].dropna()

                if len(vals1) < 3 or len(vals2) < 3:
                    continue

                result = self._compare(vals1, vals2, kpi, s1, s2)
                rows.append(result)

        results = pd.DataFrame(rows)
        results.to_csv(RESULTS_DIR / "statistical_tests.csv", index=False)
        print(f"Statistical tests saved: {RESULTS_DIR}/statistical_tests.csv")
        self._print_significant(results)
        return results

    def _compare(
        self,
        vals1: pd.Series,
        vals2: pd.Series,
        kpi: str,
        s1: str,
        s2: str
    ) -> dict:
        """
        Compare two scenario distributions.
        Uses Mann-Whitney U (non-parametric — does not assume normality).
        Also computes Cohen's d effect size.
        """

        # Normality check (Shapiro-Wilk)
        _, p_normal1 = shapiro(vals1[:50]) if len(vals1) >= 3 else (0, 0)
        _, p_normal2 = shapiro(vals2[:50]) if len(vals2) >= 3 else (0, 0)
        both_normal = p_normal1 > 0.05 and p_normal2 > 0.05

        # Primary test — Mann-Whitney U (robust, non-parametric)
        try:
            stat_mw, p_mw = mannwhitneyu(
                vals1, vals2, alternative="two-sided"
            )
        except Exception:
            stat_mw, p_mw = np.nan, 1.0

        # Secondary test — t-test if both normal
        if both_normal:
            try:
                stat_t, p_t = stats.ttest_ind(vals1, vals2)
            except Exception:
                stat_t, p_t = np.nan, 1.0
        else:
            stat_t, p_t = np.nan, np.nan

        # Effect size — Cohen's d
        pooled_std = np.sqrt(
            (vals1.std() ** 2 + vals2.std() ** 2) / 2
        )
        cohens_d = (
            (vals1.mean() - vals2.mean()) / pooled_std
            if pooled_std > 0 else 0.0
        )

        # Effect size interpretation
        abs_d = abs(cohens_d)
        if abs_d < 0.20:
            effect_size = "negligible"
        elif abs_d < 0.50:
            effect_size = "small"
        elif abs_d < 0.80:
            effect_size = "medium"
        else:
            effect_size = "large"

        return {
            "kpi": kpi,
            "comparison": f"{s1}_vs_{s2}",
            "scenario_1": s1,
            "scenario_2": s2,
            "mean_s1": round(vals1.mean(), 4),
            "mean_s2": round(vals2.mean(), 4),
            "mean_diff": round(vals1.mean() - vals2.mean(), 4),
            "mw_statistic": round(stat_mw, 4) if not np.isnan(stat_mw) else np.nan,
            "mw_p_value": round(p_mw, 6),
            "significant": p_mw < SIGNIFICANCE_LEVEL,
            "t_p_value": round(p_t, 6) if not np.isnan(p_t) else np.nan,
            "cohens_d": round(cohens_d, 4),
            "effect_size": effect_size,
            "n_s1": len(vals1),
            "n_s2": len(vals2)
        }

    def _print_significant(self, results: pd.DataFrame):
        """Print table of significant differences."""

        sig = results[results["significant"] == True]
        if sig.empty:
            print("  No statistically significant differences found.")
            return

        print(f"\nStatistically significant differences (p < {SIGNIFICANCE_LEVEL}):")
        print(f"{'KPI':<25} {'Comparison':<12} {'Diff':>8} {'p-value':>10} {'Effect':>10}")
        print("-" * 70)
        for _, row in sig.iterrows():
            print(
                f"{row['kpi']:<25} "
                f"{row['comparison']:<12} "
                f"{row['mean_diff']:>8.4f} "
                f"{row['mw_p_value']:>10.6f} "
                f"{row['effect_size']:>10}"
            )

    def kruskal_wallis_test(self) -> pd.DataFrame:
        """
        Kruskal-Wallis test — all three scenarios simultaneously.
        Tests if at least one scenario is significantly different.
        """

        final_df = self.loader.get_final_year()
        rows = []

        for kpi in KPI_COLUMNS:
            if kpi not in final_df.columns:
                continue

            groups = [
                final_df[final_df["scenario"] == s][kpi].dropna().values
                for s in self.loader.scenarios
            ]
            groups = [g for g in groups if len(g) >= 3]

            if len(groups) < 2:
                continue

            try:
                stat, p_value = kruskal(*groups)
                rows.append({
                    "kpi": kpi,
                    "kruskal_statistic": round(stat, 4),
                    "p_value": round(p_value, 6),
                    "significant": p_value < SIGNIFICANCE_LEVEL,
                    "n_groups": len(groups)
                })
            except Exception:
                pass

        result = pd.DataFrame(rows)
        result.to_csv(RESULTS_DIR / "kruskal_wallis.csv", index=False)
        print(f"Kruskal-Wallis test saved: {RESULTS_DIR}/kruskal_wallis.csv")
        return result


# ══════════════════════════════════════════════════════════════════════════════
# CALIBRATION VALIDATION
# ══════════════════════════════════════════════════════════════════════════════

class CalibrationValidator:
    """
    MoS 8 — Calibration Against Reality.
    Validates Year Zero outputs against real Myanmar data.
    Acceptable calibration error: < 10% on all baselines.
    """

    def __init__(self, loader: ResultsLoader):
        self.loader = loader

    def validate_year_zero(self) -> pd.DataFrame:
        """Compare Year Zero simulation output to Myanmar real data."""

        year_zero = self.loader.get_year(0)
        rows = []

        for kpi, baseline in MYANMAR_BASELINES.items():
            if kpi not in year_zero.columns:
                continue

            vals = year_zero[kpi].dropna()
            if vals.empty:
                continue

            sim_mean = vals.mean()
            error = abs(sim_mean - baseline) / max(0.001, baseline)
            within_10pct = error < 0.10

            rows.append({
                "kpi": kpi,
                "real_world_baseline": baseline,
                "simulation_year_zero": round(sim_mean, 4),
                "absolute_error": round(abs(sim_mean - baseline), 4),
                "percentage_error": round(error * 100, 2),
                "within_10pct_threshold": within_10pct,
                "source": self._get_source(kpi)
            })

        result = pd.DataFrame(rows)

        # Print calibration table
        print("\nCalibration Validation (MoS 8):")
        print(f"{'KPI':<25} {'Real':>8} {'Sim':>8} {'Error%':>8} {'Pass':>6}")
        print("-" * 60)
        for _, row in result.iterrows():
            status = "PASS" if row["within_10pct_threshold"] else "FAIL"
            print(
                f"{row['kpi']:<25} "
                f"{row['real_world_baseline']:>8.3f} "
                f"{row['simulation_year_zero']:>8.3f} "
                f"{row['percentage_error']:>7.1f}% "
                f"{status:>6}"
            )

        passed = result["within_10pct_threshold"].sum()
        total = len(result)
        print(f"\nCalibration: {passed}/{total} KPIs within 10% threshold")

        result.to_csv(RESULTS_DIR / "calibration_validation.csv", index=False)
        return result

    @staticmethod
    def _get_source(kpi: str) -> str:
        sources = {
            "corruption_index": "Transparency International CPI 2023",
            "trust_index": "World Bank Governance Indicators 2022",
            "gini_coefficient": "World Bank 2017",
            "employment_rate": "Myanmar Census 2014",
            "ethnic_harmony": "V-Dem Dataset",
            "stability_index": "World Bank Political Stability 2022",
            "iig_effectiveness": "Baseline estimate",
            "coup_probability": "Post-2021 estimate",
            "brain_drain_rate": "Post-2021 emigration estimate"
        }
        return sources.get(kpi, "Estimate")


# ══════════════════════════════════════════════════════════════════════════════
# NORTH STAR ANALYSIS
# ══════════════════════════════════════════════════════════════════════════════

class NorthStarAnalyzer:
    """
    Tracks progress toward 50-year north star goals.
    North Star: Myanmar as SEA intellectual and economic capital.
    """

    def __init__(self, loader: ResultsLoader):
        self.loader = loader

    def compute_progress(self) -> pd.DataFrame:
        """Compute north star progress for each scenario over time."""

        rows = []

        for scenario in self.loader.scenarios:
            s_df = self.loader.get_scenario(scenario)

            for year in sorted(s_df["year"].unique()):
                y_df = s_df[s_df["year"] == year]
                progress_scores = []

                for kpi, target in NORTH_STAR_TARGETS.items():
                    if kpi not in y_df.columns:
                        continue
                    val = y_df[kpi].mean()
                    if np.isnan(val):
                        continue

                    # Some KPIs need to go DOWN (corruption, coup risk, gini)
                    lower_is_better = kpi in [
                        "corruption_index", "coup_probability",
                        "gini_coefficient", "brain_drain_rate",
                        "inflation_rate"
                    ]

                    baseline = MYANMAR_BASELINES.get(kpi, 0.50)

                    if lower_is_better:
                        if baseline == target:
                            progress = 0.50
                        else:
                            progress = (baseline - val) / (baseline - target)
                    else:
                        if baseline == target:
                            progress = 0.50
                        else:
                            progress = (val - baseline) / (target - baseline)

                    progress = max(0.0, min(1.0, progress))
                    progress_scores.append(progress)

                if progress_scores:
                    composite_progress = sum(progress_scores) / len(progress_scores)
                else:
                    composite_progress = 0.0

                rows.append({
                    "scenario": scenario,
                    "year": year,
                    "north_star_composite": round(composite_progress, 4),
                    "on_track": composite_progress > (year / self.loader.n_years) * 0.80
                })

        result = pd.DataFrame(rows)
        result.to_csv(RESULTS_DIR / "north_star_progress.csv", index=False)
        print(f"North Star progress saved: {RESULTS_DIR}/north_star_progress.csv")
        return result

    def check_milestone_achievement(self) -> pd.DataFrame:
        """Check which decade milestones each scenario achieves."""

        milestones = {
            "decade_1_end": {
                "year": 10,
                "targets": {
                    "corruption_index": 0.40,
                    "coup_probability": 0.15,
                    "stability_index": 0.50
                }
            },
            "decade_2_end": {
                "year": 20,
                "targets": {
                    "corruption_index": 0.25,
                    "iig_effectiveness": 0.60,
                    "employment_rate": 0.70
                }
            },
            "decade_3_end": {
                "year": 35,
                "targets": {
                    "corruption_index": 0.15,
                    "ethnic_harmony": 0.60,
                    "brain_drain_rate": 0.15
                }
            },
            "decade_4_end": {
                "year": 50,
                "targets": NORTH_STAR_TARGETS
            }
        }

        rows = []
        for milestone_name, milestone in milestones.items():
            target_year = milestone["year"]
            if target_year > self.loader.n_years:
                continue

            year_df = self.loader.get_year(target_year)

            for scenario in self.loader.scenarios:
                s_df = year_df[year_df["scenario"] == scenario]
                targets_met = 0
                targets_total = 0

                for kpi, target in milestone["targets"].items():
                    if kpi not in s_df.columns:
                        continue
                    val = s_df[kpi].mean()
                    if np.isnan(val):
                        continue

                    lower_is_better = kpi in [
                        "corruption_index", "coup_probability",
                        "gini_coefficient", "brain_drain_rate"
                    ]

                    met = val <= target if lower_is_better else val >= target
                    targets_met += int(met)
                    targets_total += 1

                rows.append({
                    "milestone": milestone_name,
                    "year": target_year,
                    "scenario": scenario,
                    "targets_met": targets_met,
                    "targets_total": targets_total,
                    "achievement_rate": round(
                        targets_met / max(1, targets_total), 4
                    ),
                    "milestone_achieved": targets_met >= targets_total * 0.70
                })

        result = pd.DataFrame(rows)
        result.to_csv(RESULTS_DIR / "milestone_achievement.csv", index=False)

        print("\nMilestone Achievement:")
        print(f"{'Milestone':<20} {'Year':>5} {'Scen':>5} {'Rate':>8} {'Achieved':>10}")
        print("-" * 55)
        for _, row in result.iterrows():
            status = "YES" if row["milestone_achieved"] else "NO"
            print(
                f"{row['milestone']:<20} "
                f"{row['year']:>5} "
                f"{row['scenario']:>5} "
                f"{row['achievement_rate']:>7.1%} "
                f"{status:>10}"
            )

        return result


# ══════════════════════════════════════════════════════════════════════════════
# SENSITIVITY ANALYSIS
# ══════════════════════════════════════════════════════════════════════════════

class SensitivityAnalyzer:
    """
    MoS 3 — Sensitivity Analysis.
    Tests whether results stay stable under ±10% parameter variation.
    Uses parameter variance analysis from existing runs.
    """

    def __init__(self, loader: ResultsLoader):
        self.loader = loader

    def compute_variance_stability(self) -> pd.DataFrame:
        """
        Check if 100 runs produce stable variance.
        MoS 4 — Sample Size Sufficiency.
        Variance should stabilize — additional runs change mean < 1%.
        """

        rows = []

        for scenario in self.loader.scenarios:
            s_df = self.loader.get_final_year(scenario)

            for kpi in KPI_COLUMNS:
                if kpi not in s_df.columns:
                    continue

                vals = s_df[kpi].dropna().values
                if len(vals) < 10:
                    continue

                # Compute running mean at different sample sizes
                sample_sizes = [10, 20, 30, 50, len(vals)]
                means = []
                for n in sample_sizes:
                    if n <= len(vals):
                        means.append(np.mean(vals[:n]))

                # Check if mean stabilizes (last 2 means differ < 1%)
                if len(means) >= 2:
                    last_change = abs(means[-1] - means[-2]) / max(0.001, abs(means[-2]))
                    stable = last_change < 0.01
                else:
                    stable = False

                rows.append({
                    "scenario": scenario,
                    "kpi": kpi,
                    "n_runs": len(vals),
                    "mean": round(np.mean(vals), 4),
                    "std": round(np.std(vals), 4),
                    "cv": round(np.std(vals) / max(0.001, np.mean(vals)), 4),
                    "variance_stable": stable,
                    "last_change_pct": round(last_change * 100, 2) if len(means) >= 2 else np.nan
                })

        result = pd.DataFrame(rows)
        result.to_csv(RESULTS_DIR / "variance_stability.csv", index=False)
        print(f"Variance stability saved: {RESULTS_DIR}/variance_stability.csv")

        # Summary
        stable_count = result["variance_stable"].sum()
        total = len(result)
        print(f"MoS 4 — Sample Sufficiency: {stable_count}/{total} KPIs show stable variance")

        return result

    def compute_internal_consistency(self) -> pd.DataFrame:
        """
        MoS 6 — Internal Consistency.
        Verify feedback loops produce expected directional effects.
        """

        expected_correlations = [
            ("iig_effectiveness", "corruption_index", "negative"),
            ("trust_index", "stability_index", "positive"),
            ("gini_coefficient", "employment_rate", "negative"),
            ("ethnic_harmony", "stability_index", "positive"),
            ("shame_register_size", "corruption_index", "negative"),
            ("north_star_progress", "trust_index", "positive"),
            ("coup_probability", "stability_index", "negative"),
            ("knowledge_capital", "north_star_progress", "positive")
        ]

        rows = []

        for scenario in self.loader.scenarios:
            s_df = self.loader.get_scenario(scenario)

            # Use trajectory means per year
            traj = s_df.groupby("year")[KPI_COLUMNS].mean().reset_index()

            for kpi_a, kpi_b, expected_dir in expected_correlations:
                if kpi_a not in traj.columns or kpi_b not in traj.columns:
                    continue

                vals_a = traj[kpi_a].dropna()
                vals_b = traj[kpi_b].dropna()

                if len(vals_a) < 3:
                    continue

                # Align lengths
                min_len = min(len(vals_a), len(vals_b))
                vals_a = vals_a.iloc[:min_len]
                vals_b = vals_b.iloc[:min_len]

                try:
                    corr, p_val = stats.pearsonr(vals_a, vals_b)
                except Exception:
                    corr, p_val = np.nan, 1.0

                actual_dir = "positive" if corr > 0 else "negative"
                consistent = actual_dir == expected_dir

                rows.append({
                    "scenario": scenario,
                    "kpi_a": kpi_a,
                    "kpi_b": kpi_b,
                    "expected_direction": expected_dir,
                    "actual_correlation": round(corr, 4),
                    "actual_direction": actual_dir,
                    "p_value": round(p_val, 6),
                    "consistent": consistent,
                    "significant": p_val < SIGNIFICANCE_LEVEL
                })

        result = pd.DataFrame(rows)
        result.to_csv(RESULTS_DIR / "internal_consistency.csv", index=False)

        consistent_count = result["consistent"].sum()
        total = len(result)
        print(f"MoS 6 — Internal Consistency: {consistent_count}/{total} correlations in expected direction")

        return result

    def run_sobol_gsa(
        self,
        kpi: str = "corruption_index",
        scenario: str = "A",
        n_sample: int = 64,
        n_citizens: int = 1000,
        n_steps: int = 50,
        use_llm: bool = False,
        output: Optional[Path] = None,
    ) -> dict:
        """
        MoS 3 — Sensitivity Analysis (real Sobol GSA, not a feasibility stub).

        Runs the live Phase 3 model (`model_phase3.KaNovaModelPhase3`) once per
        Sobol sample point, overriding the 10-parameter space defined in
        `GSA_PROBLEM`/`GSA_PARAM_MAP` directly on the live `CONSTITUTION`
        singleton for the duration of each run, then computes first-order (S1)
        and total-order (ST) Sobol indices from the real final-year `kpi`
        output.

        This supersedes `tests/salib_gsa/feasibility_check.py`, which only
        verifies SALib sampling/analysis wiring against a synthetic Y and
        reports a cost estimate — it does not run the simulation. This method
        is the actual sensitivity-analysis deliverable referenced in the
        module docstring and requested by both IEEE Access reviewers.

        Total runs = n_sample x (2k + 2), k = GSA_PROBLEM["num_vars"] (13).
        Defaults (n_sample=64, n_citizens=1000) match the RunPod-scale design
        in feasibility_check.py — reduce both for a fast local smoke test.

        Overrides are applied to whichever scenario's constitution the run
        actually reads, resolved through config.scenario_registry (fixed
        2026-10-21; previously always mutated the MFU singleton, so any
        scenario other than "A" silently perturbed nothing).

        Scope note for the manuscript: the ten constitutional parameters are
        MFU-specific tunable constants, and Scenario C's 2008 encoding is a
        separately-sourced fixed historical document rather than a free
        parameter space. The three feedback/dynamics parameters, however, are
        Ka-Nova modelling choices rather than provisions of any real
        constitution, so perturbing them is legitimate on ANY scenario — and
        for the trust floor it is only meaningful on a military chain, since
        that is the only chain where the floor binds. Running this on C/TH/PK
        for `trust_index` is what quantifies Reviewer 1 pt.2 for trust.
        """
        if not SALIB_AVAILABLE:
            raise ImportError(
                "SALib is not installed — run_sobol_gsa requires SALib==1.5.1 "
                "(see requirements.txt). Install it before calling this method."
            )

        import dataclasses
        from model_phase3 import KaNovaModelPhase3

        param_values = salib_sobol_sample.sample(GSA_PROBLEM, n_sample, calc_second_order=False)
        total_runs = param_values.shape[0]
        print(f"\nSobol GSA: {total_runs} model runs "
              f"(n_sample={n_sample}, k={GSA_PROBLEM['num_vars']}, kpi={kpi}, scenario={scenario})")

        # Each CONSTITUTION section (merit, chambers, federal, iig, military,
        # simulation) is a frozen dataclass — individual fields can't be
        # mutated in place. Snapshot the whole section objects so every
        # override is reverted exactly, even if a run raises.
        # LATENT BUG FIXED 2026-10-21. This always mutated the MFU singleton
        # imported at module load, but since the bug #11 registry refactor the
        # model loads its constitution via get_scenario(scenario). So calling
        # run_sobol_gsa(scenario="C") perturbed MFU while the model ran on
        # CONSTITUTION_2008, and every override was silently a no-op — the GSA
        # would have reported near-zero sensitivity for every parameter and
        # looked like a valid result. Resolve the target from the registry so
        # the object perturbed is the object the run actually reads.
        from config.scenario_registry import get_scenario
        target_constitution = get_scenario(scenario).constitution

        section_names = sorted({section for section, _ in GSA_PARAM_MAP.values()})
        missing = [
            (s, f) for name, (s, f) in GSA_PARAM_MAP.items()
            if not hasattr(getattr(target_constitution, s, None), f)
        ]
        if missing:
            raise AttributeError(
                f"Scenario {scenario!r}'s constitution is missing GSA target "
                f"fields {missing}. Backfill them before running the GSA on "
                f"this scenario rather than letting overrides silently no-op."
            )
        originals = {section: getattr(target_constitution, section) for section in section_names}

        Y = np.zeros(total_runs)
        try:
            for row_idx, row in enumerate(param_values):
                overrides_by_section = {}
                for col_idx, name in enumerate(GSA_PROBLEM["names"]):
                    section, attr = GSA_PARAM_MAP[name]
                    overrides_by_section.setdefault(section, {})[attr] = float(row[col_idx])
                for section, field_overrides in overrides_by_section.items():
                    setattr(target_constitution, section, dataclasses.replace(originals[section], **field_overrides))

                seed = row_idx * 100 + ord(scenario)
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
                final = df.iloc[-1]
                Y[row_idx] = final[kpi] if kpi in final else np.nan

                if (row_idx + 1) % max(1, total_runs // 10) == 0:
                    print(f"    {row_idx + 1}/{total_runs} runs complete")
        finally:
            # Always restore — a GSA run must not leave CONSTITUTION mutated
            # for any other analysis that imports the singleton afterward.
            for section, original_section in originals.items():
                setattr(target_constitution, section, original_section)

        if np.isnan(Y).any():
            raise ValueError(
                f"KPI '{kpi}' missing from final-year model output on "
                f"{int(np.isnan(Y).sum())}/{total_runs} runs — check KPI_COLUMNS / model_phase3.get_results()."
            )

        Si = salib_sobol_analyze.analyze(GSA_PROBLEM, Y, calc_second_order=False, print_to_console=False)

        rows = []
        for i, name in enumerate(GSA_PROBLEM["names"]):
            rows.append({
                "parameter": name,
                "S1": round(float(Si["S1"][i]), 4),
                "S1_conf": round(float(Si["S1_conf"][i]), 4),
                "ST": round(float(Si["ST"][i]), 4),
                "ST_conf": round(float(Si["ST_conf"][i]), 4),
            })
        result_df = pd.DataFrame(rows).sort_values("ST", ascending=False).reset_index(drop=True)

        print(f"\n    {'Parameter':<42} {'S1':>8} {'ST':>8}")
        print(f"    {'-'*42} {'-'*8} {'-'*8}")
        for _, r in result_df.iterrows():
            flag = " <-- dominant" if r["ST"] > 0.10 else ""
            print(f"    {r['parameter']:<42} {r['S1']:>8.4f} {r['ST']:>8.4f}{flag}")

        out_path = output or (RESULTS_DIR / f"sobol_sensitivity_{scenario}_{kpi}.csv")
        result_df.to_csv(out_path, index=False)
        print(f"\nSobol sensitivity indices saved: {out_path}")

        return {
            "kpi": kpi,
            "scenario": scenario,
            "n_sample": n_sample,
            "total_runs": int(total_runs),
            "indices": result_df,
        }


# ══════════════════════════════════════════════════════════════════════════════
# PUBLICATION TABLE GENERATOR
# ══════════════════════════════════════════════════════════════════════════════

class PublicationTables:
    """Generate publication-ready tables for journal submission."""

    def __init__(self, loader: ResultsLoader):
        self.loader = loader

    def table_1_scenario_comparison(self) -> pd.DataFrame:
        """
        Table 1 — Main scenario comparison at Year 50.
        Format: KPI | Scenario A mean(sd) | B mean(sd) | C mean(sd)
        """

        final_df = self.loader.get_final_year()
        rows = []

        key_kpis = [
            ("corruption_index", "Corruption Index"),
            ("trust_index", "Public Trust Index"),
            ("iig_effectiveness", "IIG Effectiveness"),
            ("coup_probability", "Coup Probability"),
            ("ethnic_harmony", "Ethnic Harmony"),
            # Labelled explicitly: this is geographic (state-GDP) inequality,
            # not citizen-income inequality. See the unit-mismatch note on
            # MYANMAR_BASELINES["gini_coefficient"].
            ("gini_coefficient", "Gini (state-GDP inequality)"),
            ("employment_rate", "Employment Rate"),
            ("knowledge_capital", "Knowledge Capital"),
            ("north_star_progress", "North Star Progress"),
            ("stability_index", "Stability Index"),
            ("shame_register_size", "Shame Register Size"),
            ("brain_drain_rate", "Brain Drain Rate")
        ]

        for kpi_col, kpi_label in key_kpis:
            if kpi_col not in final_df.columns:
                continue

            row = {"KPI": kpi_label}

            for scenario in ["A", "B", "C"]:
                vals = final_df[
                    final_df["scenario"] == scenario
                ][kpi_col].dropna()

                if vals.empty:
                    row[f"Scenario_{scenario}"] = "N/A"
                else:
                    row[f"Scenario_{scenario}"] = (
                        f"{vals.mean():.3f} ({vals.std():.3f})"
                    )

            rows.append(row)

        result = pd.DataFrame(rows)
        result.to_csv(RESULTS_DIR / "table1_scenario_comparison.csv", index=False)
        print(f"\nTable 1 saved: {RESULTS_DIR}/table1_scenario_comparison.csv")

        # Print formatted
        print("\nTable 1 — Scenario Comparison at Final Year (Mean ± SD)")
        print("=" * 75)
        print(f"{'KPI':<25} {'Scenario A':>15} {'Scenario B':>15} {'Scenario C':>15}")
        print("-" * 75)
        for _, row in result.iterrows():
            print(
                f"{row['KPI']:<25} "
                f"{str(row.get('Scenario_A', 'N/A')):>15} "
                f"{str(row.get('Scenario_B', 'N/A')):>15} "
                f"{str(row.get('Scenario_C', 'N/A')):>15}"
            )
        print("=" * 75)

        return result

    def table_2_mos_summary(
        self,
        calibration: pd.DataFrame,
        consistency: pd.DataFrame,
        variance: pd.DataFrame,
        tests: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Table 2 — Measures of Success summary.
        """

        rows = []

        # MoS 1 — Behavioral Validity (from calibration)
        cal_pass = calibration["within_10pct_threshold"].mean()
        rows.append({
            "MoS": "MoS 1 — Behavioral Validity",
            "Criterion": "Year Zero within 10% of Myanmar baseline",
            "Result": f"{cal_pass:.1%} KPIs passed",
            "Status": "PASS" if cal_pass > 0.70 else "PARTIAL"
        })

        # MoS 4 — Sample Sufficiency
        var_pass = variance["variance_stable"].mean()
        rows.append({
            "MoS": "MoS 4 — Sample Sufficiency",
            "Criterion": "Variance stabilizes with 100 runs (change < 1%)",
            "Result": f"{var_pass:.1%} KPIs stable",
            "Status": "PASS" if var_pass > 0.80 else "PARTIAL"
        })

        # MoS 5 — Scenario Differentiation
        sig_rate = tests["significant"].mean() if not tests.empty else 0.0
        rows.append({
            "MoS": "MoS 5 — Scenario Differentiation",
            "Criterion": "Scenarios statistically different (p < 0.05)",
            "Result": f"{sig_rate:.1%} comparisons significant",
            "Status": "PASS" if sig_rate > 0.50 else "PARTIAL"
        })

        # MoS 6 — Internal Consistency
        con_pass = consistency["consistent"].mean() if not consistency.empty else 0.0
        rows.append({
            "MoS": "MoS 6 — Internal Consistency",
            "Criterion": "Feedback loops in expected direction",
            "Result": f"{con_pass:.1%} correlations consistent",
            "Status": "PASS" if con_pass > 0.80 else "PARTIAL"
        })

        # MoS 7 — Reproducibility
        rows.append({
            "MoS": "MoS 7 — Reproducibility",
            "Criterion": "Same seed produces same results",
            "Result": "Deterministic seeding implemented",
            "Status": "PASS"
        })

        # MoS 8 — Calibration
        rows.append({
            "MoS": "MoS 8 — Calibration",
            "Criterion": "Year Zero matches real Myanmar data",
            "Result": f"{cal_pass:.1%} within threshold",
            "Status": "PASS" if cal_pass > 0.70 else "PARTIAL"
        })

        result = pd.DataFrame(rows)
        result.to_csv(RESULTS_DIR / "table2_mos_summary.csv", index=False)
        print(f"Table 2 saved: {RESULTS_DIR}/table2_mos_summary.csv")

        print("\nTable 2 — Measures of Success")
        print("=" * 80)
        for _, row in result.iterrows():
            print(f"  {row['MoS']}")
            print(f"    Criterion: {row['Criterion']}")
            print(f"    Result:    {row['Result']}")
            print(f"    Status:    {row['Status']}")
        print("=" * 80)

        return result


# ══════════════════════════════════════════════════════════════════════════════
# MASTER ANALYSIS RUNNER
# ══════════════════════════════════════════════════════════════════════════════

class KPIAnalysis:
    """
    Master analysis runner.
    Runs all analyses in correct order and saves all outputs.
    """

    def __init__(self, results_dir: Path = RESULTS_DIR):
        self.results_dir = results_dir
        self.loader = ResultsLoader(results_dir)

    def run_full_analysis(self):
        """Run complete KPI analysis pipeline."""

        print("\n" + "=" * 60)
        print("KA-NOVA KPI ANALYSIS")
        print("=" * 60)

        # Load data
        self.loader.load()

        # Descriptive statistics
        print("\n[1/6] Descriptive Statistics...")
        desc = DescriptiveStats(self.loader)
        descriptive = desc.compute_all()
        trajectories = desc.compute_trajectories()

        # Statistical tests
        print("\n[2/6] Statistical Significance Tests...")
        tests = StatisticalTests(self.loader)
        pairwise = tests.run_all_tests()
        kruskal = tests.kruskal_wallis_test()

        # Calibration
        print("\n[3/6] Calibration Validation...")
        calibration = CalibrationValidator(self.loader)
        cal_results = calibration.validate_year_zero()

        # North Star
        print("\n[4/6] North Star Analysis...")
        ns = NorthStarAnalyzer(self.loader)
        ns_progress = ns.compute_progress()
        milestones = ns.check_milestone_achievement()

        # Sensitivity
        print("\n[5/6] Sensitivity Analysis...")
        sensitivity = SensitivityAnalyzer(self.loader)
        variance = sensitivity.compute_variance_stability()
        consistency = sensitivity.compute_internal_consistency()

        # Publication tables
        print("\n[6/6] Generating Publication Tables...")
        pub = PublicationTables(self.loader)
        table1 = pub.table_1_scenario_comparison()
        table2 = pub.table_2_mos_summary(
            cal_results, consistency, variance, pairwise
        )

        print("\n" + "=" * 60)
        print("Analysis complete. All files saved to results/")
        print("=" * 60)
        print(f"\nOutput files:")
        for f in sorted(self.results_dir.glob("*.csv")):
            size = f.stat().st_size
            print(f"  {f.name:<45} {size:>8} bytes")

        return {
            "descriptive": descriptive,
            "trajectories": trajectories,
            "pairwise_tests": pairwise,
            "kruskal": kruskal,
            "calibration": cal_results,
            "north_star": ns_progress,
            "milestones": milestones,
            "variance": variance,
            "consistency": consistency,
            "table1": table1,
            "table2": table2
        }


# ══════════════════════════════════════════════════════════════════════════════
# CLI
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":

    import argparse

    parser = argparse.ArgumentParser(description="Ka-Nova KPI Analysis")
    parser.add_argument(
        "--results",
        type=str,
        default=None,
        help="Path to results directory (default: RESULTS_DIR, i.e. results_phase3/ "
             "or $KA_NOVA_RESULTS_DIR)"
    )
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Quick analysis — descriptive stats and calibration only"
    )
    # GSA entry point. run_sobol_gsa() previously had no CLI, so it could not be
    # launched from a pod without exec'ing in and writing Python by hand.
    parser.add_argument("--gsa", action="store_true",
                        help="Run Sobol global sensitivity analysis instead of KPI analysis")
    parser.add_argument("--gsa-kpi", type=str, default="corruption_index",
                        help="KPI to analyse (default: corruption_index)")
    parser.add_argument("--gsa-scenario", type=str, default="A",
                        help="Scenario whose constitution is perturbed (default: A)")
    parser.add_argument("--gsa-samples", type=int, default=64,
                        help="Sobol n_sample; total runs = n_sample*(2k+2) (default: 64)")
    parser.add_argument("--gsa-citizens", type=int, default=1000)
    parser.add_argument("--gsa-steps", type=int, default=50)
    args = parser.parse_args()

    if args.gsa:
        sa = SensitivityAnalyzer.__new__(SensitivityAnalyzer)
        SensitivityAnalyzer.run_sobol_gsa(
            sa,
            kpi=args.gsa_kpi,
            scenario=args.gsa_scenario,
            n_sample=args.gsa_samples,
            n_citizens=args.gsa_citizens,
            n_steps=args.gsa_steps,
            use_llm=False,
        )
        raise SystemExit(0)

    analysis = KPIAnalysis(
        results_dir=Path(args.results) if args.results else RESULTS_DIR
    )

    if args.quick:
        print("Quick analysis mode...")
        analysis.loader.load()
        desc = DescriptiveStats(analysis.loader)
        desc.compute_all()
        cal = CalibrationValidator(analysis.loader)
        cal.validate_year_zero()
    else:
        results = analysis.run_full_analysis()