"""
================================================================================
PROJECT KA-NOVA
charts/visualize.py

Visualization — All Dissertation Charts
Ka-Nova Simulation Engine v1.0

Generates publication-ready charts from simulation results.
All charts saved as PNG (300 DPI) for dissertation submission.

Chart categories:
    1. KPI Trajectories — 50-year time series per scenario
    2. Scenario Comparison — A vs B vs C box plots
    3. Feedback Loop Analysis — correlation heatmaps
    4. North Star Progress — composite trajectory
    5. Distribution Charts — final year distributions
    6. Calibration Chart — Year Zero vs real data
    7. Summary Dashboard — single overview figure

Usage:
    python3 charts/visualize.py                   all charts
    python3 charts/visualize.py --chart kpi       KPI trajectories only
    python3 charts/visualize.py --chart compare   Comparison charts only

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

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
from matplotlib.gridspec import GridSpec

# ── PATHS ─────────────────────────────────────────────────────────────────────
RESULTS_DIR = Path("results")
CHARTS_DIR  = Path("charts")
KPI_DIR     = CHARTS_DIR / "kpi"
FEEDBACK_DIR= CHARTS_DIR / "feedback"
COMPARE_DIR = CHARTS_DIR / "comparison"


# ══════════════════════════════════════════════════════════════════════════════
# STYLE
# ══════════════════════════════════════════════════════════════════════════════

SCENARIO_COLORS = {
    "A": "#1D9E75",   # teal  — full MFU
    "B": "#C9A84C",   # gold  — no safeguards
    "C": "#8B1A1A"    # red   — military baseline
}

SCENARIO_LABELS = {
    "A": "Scenario A — Full MFU",
    "B": "Scenario B — No Safeguards",
    "C": "Scenario C — Military Baseline"
}

SCENARIO_LINESTYLES = {
    "A": "-",
    "B": "--",
    "C": ":"
}

DPI = 300
FIGSIZE_WIDE  = (14, 6)
FIGSIZE_SQUARE= (10, 8)
FIGSIZE_TALL  = (10, 12)
FIGSIZE_DASH  = (18, 12)

def set_style():
    """Apply consistent Ka-Nova chart style."""
    plt.style.use("seaborn-v0_8-whitegrid")
    plt.rcParams.update({
        "font.family":        "serif",
        "font.size":          11,
        "axes.titlesize":     13,
        "axes.labelsize":     11,
        "axes.titleweight":   "bold",
        "axes.spines.top":    False,
        "axes.spines.right":  False,
        "figure.dpi":         100,
        "savefig.dpi":        DPI,
        "savefig.bbox":       "tight",
        "legend.framealpha":  0.9,
        "legend.fontsize":    10,
        "lines.linewidth":    2.0,
        "grid.alpha":         0.40
    })

def add_watermark(fig):
    """Add Ka-Nova watermark to figure."""
    fig.text(
        0.99, 0.01, "Project Ka-Nova | MSc Data Science | UH",
        ha="right", va="bottom", fontsize=7,
        color="gray", alpha=0.5, style="italic"
    )


# ══════════════════════════════════════════════════════════════════════════════
# DATA LOADER
# ══════════════════════════════════════════════════════════════════════════════

def load_results() -> pd.DataFrame:
    """Load simulation results."""
    path = RESULTS_DIR / "all_results.csv"
    if not path.exists():
        raise FileNotFoundError(
            f"Results not found at {path}. Run simulation first: python3 run.py"
        )
    df = pd.read_csv(path)
    print(f"Loaded {len(df):,} rows from {path}")
    return df

def get_trajectories(df: pd.DataFrame) -> pd.DataFrame:
    """Compute mean trajectories per scenario per year."""
    kpi_cols = [c for c in df.columns
                if c not in ["year","scenario","run_id","seed",
                              "final_year","simulation_failed","failure_reason"]]
    return df.groupby(["scenario","year"])[kpi_cols].agg(["mean","std"]).reset_index()


# ══════════════════════════════════════════════════════════════════════════════
# 1. KPI TRAJECTORIES
# ══════════════════════════════════════════════════════════════════════════════

class KPITrajectoryCharts:
    """
    50-year KPI time series — one chart per KPI.
    Shows mean trajectory with ±1 SD confidence band per scenario.
    """

    KPI_META = {
        "corruption_index":   ("Corruption Index",          "Index (0=clean, 1=corrupt)",  True),
        "trust_index":        ("Public Trust Index",         "Index (0=low, 1=high)",        False),
        "iig_effectiveness":  ("IIG Effectiveness",          "Rate (0=ineffective, 1=high)", False),
        "coup_probability":   ("Coup Probability",           "Probability",                  True),
        "ethnic_harmony":     ("Ethnic Harmony Index",       "Index (0=low, 1=high)",        False),
        "gini_coefficient":   ("Gini Coefficient",           "Gini (0=equal, 1=unequal)",    True),
        "employment_rate":    ("Employment Rate",            "Rate",                         False),
        "knowledge_capital":  ("Knowledge Capital",          "Cumulative index",             False),
        "brain_drain_rate":   ("Brain Drain Rate",           "Emigration rate",              True),
        "north_star_progress":("North Star Progress",        "Composite (0=none, 1=full)",   False),
        "stability_index":    ("Stability Index",            "Index (0=unstable, 1=stable)", False),
        "shame_register_size":("Shame Register — Entries",   "Count",                        False),
        "total_ruin_events":  ("Total Ruin Protocol Events", "Count",                        False),
        "inflation_rate":     ("Inflation Rate",             "Rate",                         True),
        "tax_compliance":     ("Tax Compliance Rate",        "Rate",                         False),
    }

    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.scenarios = sorted(df["scenario"].unique())
        KPI_DIR.mkdir(parents=True, exist_ok=True)

    def plot_all(self):
        """Generate trajectory chart for every KPI."""
        generated = 0
        for kpi, (title, ylabel, lower_better) in self.KPI_META.items():
            if kpi not in self.df.columns:
                continue
            self.plot_single(kpi, title, ylabel, lower_better)
            generated += 1
        print(f"  KPI trajectories: {generated} charts saved to {KPI_DIR}/")

    def plot_single(self, kpi, title, ylabel, lower_better=False):
        """Plot one KPI trajectory."""
        set_style()
        fig, ax = plt.subplots(figsize=FIGSIZE_WIDE)

        for scenario in self.scenarios:
            s_df = self.df[self.df["scenario"] == scenario]
            traj = s_df.groupby("year")[kpi].agg(["mean","std"]).reset_index()
            if traj.empty:
                continue

            years = traj["year"].values
            means = traj["mean"].values
            stds  = traj["std"].fillna(0).values

            color = SCENARIO_COLORS.get(scenario, "gray")
            ls    = SCENARIO_LINESTYLES.get(scenario, "-")
            label = SCENARIO_LABELS.get(scenario, scenario)

            ax.plot(years, means, color=color, linestyle=ls,
                    linewidth=2.5, label=label, zorder=3)
            ax.fill_between(
                years,
                np.clip(means - stds, 0, None),
                np.clip(means + stds, 0, 2),
                alpha=0.15, color=color, zorder=2
            )

        # Reference lines
        from analysis.kpi import MYANMAR_BASELINES, NORTH_STAR_TARGETS
        if kpi in MYANMAR_BASELINES:
            ax.axhline(
                MYANMAR_BASELINES[kpi], color="gray",
                linestyle="--", linewidth=1.0, alpha=0.6,
                label=f"Myanmar baseline ({MYANMAR_BASELINES[kpi]:.2f})"
            )
        if kpi in NORTH_STAR_TARGETS:
            ax.axhline(
                NORTH_STAR_TARGETS[kpi], color="navy",
                linestyle=":", linewidth=1.0, alpha=0.6,
                label=f"North Star target ({NORTH_STAR_TARGETS[kpi]:.2f})"
            )

        ax.set_title(f"{title}\n50-Year Trajectory by Scenario")
        ax.set_xlabel("Year")
        ax.set_ylabel(ylabel)
        ax.legend(loc="best")

        # Direction annotation
        direction = "Lower is better" if lower_better else "Higher is better"
        ax.text(0.02, 0.97, direction, transform=ax.transAxes,
                fontsize=8, color="gray", va="top", style="italic")

        add_watermark(fig)
        plt.tight_layout()
        path = KPI_DIR / f"{kpi}.png"
        plt.savefig(path)
        plt.close()


# ══════════════════════════════════════════════════════════════════════════════
# 2. SCENARIO COMPARISON
# ══════════════════════════════════════════════════════════════════════════════

class ScenarioComparisonCharts:
    """
    Box plots comparing final-year distributions across scenarios.
    Shows the full distribution — not just means.
    """

    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.final_year = df["year"].max()
        self.final_df = df[df["year"] == self.final_year]
        self.scenarios = sorted(df["scenario"].unique())
        COMPARE_DIR.mkdir(parents=True, exist_ok=True)

    def plot_all(self):
        """Generate all comparison charts."""
        self.plot_key_kpis_grid()
        self.plot_violin_comparison()
        self.plot_scenario_radar()
        print(f"  Comparison charts saved to {COMPARE_DIR}/")

    def plot_key_kpis_grid(self):
        """Grid of box plots for key KPIs."""
        set_style()

        key_kpis = [
            "corruption_index", "trust_index", "iig_effectiveness",
            "coup_probability", "ethnic_harmony", "gini_coefficient",
            "employment_rate", "north_star_progress", "stability_index"
        ]
        available = [k for k in key_kpis if k in self.final_df.columns]
        if not available:
            return

        n_cols = 3
        n_rows = (len(available) + n_cols - 1) // n_cols
        fig, axes = plt.subplots(n_rows, n_cols, figsize=(16, n_rows * 4))
        axes = axes.flatten() if n_rows > 1 else [axes] if n_cols == 1 else axes.flatten()

        for i, kpi in enumerate(available):
            ax = axes[i]
            data = [
                self.final_df[self.final_df["scenario"] == s][kpi].dropna().values
                for s in self.scenarios
            ]
            colors = [SCENARIO_COLORS.get(s, "gray") for s in self.scenarios]

            bp = ax.boxplot(
                data, patch_artist=True, notch=False,
                medianprops={"color": "black", "linewidth": 2},
                whiskerprops={"linewidth": 1.5},
                capprops={"linewidth": 1.5}
            )
            for patch, color in zip(bp["boxes"], colors):
                patch.set_facecolor(color)
                patch.set_alpha(0.7)

            ax.set_xticklabels(self.scenarios)
            ax.set_title(kpi.replace("_", " ").title(), fontsize=11)
            ax.set_xlabel("Scenario")

        # Hide unused subplots
        for i in range(len(available), len(axes)):
            axes[i].set_visible(False)

        # Legend
        patches = [
            mpatches.Patch(color=SCENARIO_COLORS.get(s, "gray"),
                           label=SCENARIO_LABELS.get(s, s), alpha=0.7)
            for s in self.scenarios
        ]
        fig.legend(handles=patches, loc="lower center",
                   ncol=len(self.scenarios), bbox_to_anchor=(0.5, 0),
                   fontsize=10, framealpha=0.9)

        fig.suptitle(
            f"Ka-Nova — KPI Distributions at Year {self.final_year}\nScenario Comparison",
            fontsize=14, fontweight="bold", y=1.01
        )
        add_watermark(fig)
        plt.tight_layout()
        plt.savefig(COMPARE_DIR / "kpi_grid_comparison.png")
        plt.close()

    def plot_violin_comparison(self):
        """Violin plots for top 6 KPIs."""
        set_style()

        kpis = ["corruption_index", "trust_index", "coup_probability",
                "ethnic_harmony", "north_star_progress", "stability_index"]
        available = [k for k in kpis if k in self.final_df.columns]
        if not available:
            return

        fig, axes = plt.subplots(2, 3, figsize=(15, 10))
        axes = axes.flatten()

        for i, kpi in enumerate(available):
            ax = axes[i]
            plot_data = []
            plot_labels = []

            for s in self.scenarios:
                vals = self.final_df[
                    self.final_df["scenario"] == s
                ][kpi].dropna().values
                if len(vals) > 0:
                    plot_data.append(vals)
                    plot_labels.append(s)

            if not plot_data:
                continue

            parts = ax.violinplot(
                plot_data, positions=range(len(plot_data)),
                showmeans=True, showmedians=True
            )

            for j, (pc, label) in enumerate(zip(parts["bodies"], plot_labels)):
                pc.set_facecolor(SCENARIO_COLORS.get(label, "gray"))
                pc.set_alpha(0.70)

            parts["cmeans"].set_color("white")
            parts["cmedians"].set_color("black")

            ax.set_xticks(range(len(plot_labels)))
            ax.set_xticklabels(plot_labels)
            ax.set_title(kpi.replace("_", " ").title())

        for i in range(len(available), len(axes)):
            axes[i].set_visible(False)

        fig.suptitle(
            "Ka-Nova — KPI Violin Plots at Final Year",
            fontsize=14, fontweight="bold"
        )
        add_watermark(fig)
        plt.tight_layout()
        plt.savefig(COMPARE_DIR / "violin_comparison.png")
        plt.close()

    def plot_scenario_radar(self):
        """Radar chart comparing scenarios on 6 key dimensions."""
        set_style()

        dimensions = [
            ("corruption_index",    "Corruption\n(inverted)", True),
            ("trust_index",         "Trust",                  False),
            ("ethnic_harmony",      "Ethnic\nHarmony",        False),
            ("stability_index",     "Stability",              False),
            ("north_star_progress", "North Star\nProgress",   False),
            ("employment_rate",     "Employment",             False)
        ]

        available = [(k, l, inv) for k, l, inv in dimensions
                     if k in self.final_df.columns]
        if len(available) < 3:
            return

        n = len(available)
        angles = np.linspace(0, 2 * np.pi, n, endpoint=False).tolist()
        angles += angles[:1]

        fig, ax = plt.subplots(figsize=(9, 9),
                               subplot_kw={"projection": "polar"})

        for scenario in self.scenarios:
            s_df = self.final_df[self.final_df["scenario"] == scenario]
            values = []
            for kpi, label, invert in available:
                val = s_df[kpi].mean()
                val = max(0.0, min(1.0, val if not np.isnan(val) else 0.5))
                if invert:
                    val = 1.0 - val
                values.append(val)
            values += values[:1]

            color = SCENARIO_COLORS.get(scenario, "gray")
            label = SCENARIO_LABELS.get(scenario, scenario)

            ax.plot(angles, values, color=color, linewidth=2,
                    linestyle=SCENARIO_LINESTYLES.get(scenario, "-"),
                    label=label)
            ax.fill(angles, values, color=color, alpha=0.10)

        ax.set_xticks(angles[:-1])
        ax.set_xticklabels([l for _, l, _ in available], size=10)
        ax.set_ylim(0, 1)
        ax.set_yticks([0.25, 0.50, 0.75, 1.00])
        ax.set_yticklabels(["0.25", "0.50", "0.75", "1.00"], size=8)
        ax.grid(True, alpha=0.3)

        ax.set_title(
            f"Ka-Nova — Scenario Comparison Radar\nFinal Year",
            size=13, fontweight="bold", pad=20
        )
        ax.legend(loc="upper right", bbox_to_anchor=(1.35, 1.15), fontsize=9)

        add_watermark(fig)
        plt.tight_layout()
        plt.savefig(COMPARE_DIR / "radar_comparison.png")
        plt.close()


# ══════════════════════════════════════════════════════════════════════════════
# 3. FEEDBACK LOOP ANALYSIS
# ══════════════════════════════════════════════════════════════════════════════

class FeedbackLoopCharts:
    """
    Correlation heatmaps and loop interaction charts.
    """

    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.scenarios = sorted(df["scenario"].unique())
        FEEDBACK_DIR.mkdir(parents=True, exist_ok=True)

    def plot_all(self):
        """Generate all feedback loop charts."""
        self.plot_correlation_heatmaps()
        self.plot_loop_interactions()
        print(f"  Feedback charts saved to {FEEDBACK_DIR}/")

    def plot_correlation_heatmaps(self):
        """Correlation heatmap per scenario."""
        set_style()

        kpis = [k for k in [
            "corruption_index", "trust_index", "iig_effectiveness",
            "coup_probability", "ethnic_harmony", "gini_coefficient",
            "employment_rate", "knowledge_capital", "stability_index",
            "north_star_progress", "brain_drain_rate"
        ] if k in self.df.columns]

        if len(kpis) < 3:
            return

        n_scenarios = len(self.scenarios)
        fig, axes = plt.subplots(1, n_scenarios,
                                 figsize=(7 * n_scenarios, 7))
        if n_scenarios == 1:
            axes = [axes]

        for ax, scenario in zip(axes, self.scenarios):
            s_df = self.df[self.df["scenario"] == scenario]
            traj = s_df.groupby("year")[kpis].mean()
            corr = traj.corr()

            short_names = [k.replace("_index","").replace("_rate","")
                           .replace("_probability","").replace("_capital","")
                           for k in kpis]

            sns.heatmap(
                corr,
                ax=ax,
                annot=True, fmt=".2f",
                cmap="RdYlGn",
                vmin=-1, vmax=1,
                center=0,
                xticklabels=short_names,
                yticklabels=short_names,
                linewidths=0.5,
                cbar_kws={"shrink": 0.8},
                annot_kws={"size": 7}
            )
            ax.set_title(
                f"Scenario {scenario}\nKPI Correlation Matrix",
                fontsize=12, fontweight="bold"
            )
            ax.tick_params(axis="x", rotation=45, labelsize=8)
            ax.tick_params(axis="y", rotation=0, labelsize=8)

        fig.suptitle(
            "Ka-Nova — KPI Correlation Heatmaps by Scenario",
            fontsize=14, fontweight="bold", y=1.02
        )
        add_watermark(fig)
        plt.tight_layout()
        plt.savefig(FEEDBACK_DIR / "correlation_heatmaps.png")
        plt.close()

    def plot_loop_interactions(self):
        """
        Plot key feedback loop relationships as scatter plots.
        Shows the directional relationships between loop inputs and outputs.
        """
        set_style()

        loop_pairs = [
            ("iig_effectiveness",  "corruption_index",    "P2: IIG → Corruption"),
            ("trust_index",        "stability_index",     "P1: Trust → Stability"),
            ("shame_register_size","corruption_index",    "S4: Shame → Corruption"),
            ("ethnic_harmony",     "stability_index",     "S1: Harmony → Stability"),
            ("knowledge_capital",  "north_star_progress", "E4: Knowledge → North Star"),
            ("gini_coefficient",   "employment_rate",     "E3: Inequality → Employment"),
        ]

        available = [
            (a, b, title) for a, b, title in loop_pairs
            if a in self.df.columns and b in self.df.columns
        ]
        if not available:
            return

        n_cols = 3
        n_rows = (len(available) + n_cols - 1) // n_cols
        fig, axes = plt.subplots(n_rows, n_cols, figsize=(14, n_rows * 4.5))
        axes = axes.flatten() if hasattr(axes, "flatten") else [axes]

        for i, (kpi_x, kpi_y, title) in enumerate(available):
            ax = axes[i]
            for scenario in self.scenarios:
                s_df = self.df[self.df["scenario"] == scenario]
                traj = s_df.groupby("year")[[kpi_x, kpi_y]].mean()
                ax.scatter(
                    traj[kpi_x], traj[kpi_y],
                    color=SCENARIO_COLORS.get(scenario, "gray"),
                    alpha=0.6, s=20,
                    label=SCENARIO_LABELS.get(scenario, scenario)
                )
                # Trend line
                if len(traj) > 3:
                    z = np.polyfit(traj[kpi_x].values, traj[kpi_y].values, 1)
                    p = np.poly1d(z)
                    x_line = np.linspace(traj[kpi_x].min(), traj[kpi_x].max(), 50)
                    ax.plot(x_line, p(x_line),
                            color=SCENARIO_COLORS.get(scenario, "gray"),
                            linestyle="--", linewidth=1.0, alpha=0.8)

            ax.set_xlabel(kpi_x.replace("_", " ").title(), fontsize=9)
            ax.set_ylabel(kpi_y.replace("_", " ").title(), fontsize=9)
            ax.set_title(title, fontsize=10, fontweight="bold")

        for i in range(len(available), len(axes)):
            axes[i].set_visible(False)

        handles = [
            mpatches.Patch(color=SCENARIO_COLORS.get(s, "gray"),
                           label=SCENARIO_LABELS.get(s, s), alpha=0.7)
            for s in self.scenarios
        ]
        fig.legend(handles=handles, loc="lower center",
                   ncol=len(self.scenarios), bbox_to_anchor=(0.5, 0),
                   fontsize=9, framealpha=0.9)

        fig.suptitle(
            "Ka-Nova — Feedback Loop Relationships",
            fontsize=14, fontweight="bold", y=1.01
        )
        add_watermark(fig)
        plt.tight_layout()
        plt.savefig(FEEDBACK_DIR / "loop_interactions.png")
        plt.close()


# ══════════════════════════════════════════════════════════════════════════════
# 4. NORTH STAR PROGRESS
# ══════════════════════════════════════════════════════════════════════════════

class NorthStarChart:
    """North Star composite trajectory and milestone visualization."""

    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.scenarios = sorted(df["scenario"].unique())
        COMPARE_DIR.mkdir(parents=True, exist_ok=True)

    def plot_all(self):
        """Generate North Star charts."""
        self.plot_composite_trajectory()
        self.plot_decade_milestones()
        print(f"  North Star charts saved to {COMPARE_DIR}/")

    def plot_composite_trajectory(self):
        """Plot composite north star progress over 50 years."""
        set_style()
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

        # Left — north star progress
        for scenario in self.scenarios:
            s_df = self.df[self.df["scenario"] == scenario]
            if "north_star_progress" not in s_df.columns:
                continue
            traj = s_df.groupby("year")["north_star_progress"].agg(
                ["mean", "std"]
            ).reset_index()

            years = traj["year"].values
            means = traj["mean"].values
            stds  = traj["std"].fillna(0).values
            color = SCENARIO_COLORS.get(scenario, "gray")
            label = SCENARIO_LABELS.get(scenario, scenario)

            ax1.plot(years, means, color=color, linewidth=2.5, label=label)
            ax1.fill_between(
                years,
                np.clip(means - stds, 0, 1),
                np.clip(means + stds, 0, 1),
                alpha=0.15, color=color
            )

        # Decade milestone lines
        for decade_year, label in [(10,"Decade 1"),(20,"Decade 2"),
                                    (35,"Decade 3"),(50,"Decade 4")]:
            ax1.axvline(decade_year, color="navy", linestyle=":",
                        linewidth=0.8, alpha=0.5)
            ax1.text(decade_year + 0.3, 0.02, label,
                     fontsize=7, color="navy", alpha=0.6)

        ax1.axhline(0.80, color="gold", linestyle="--",
                    linewidth=1.0, alpha=0.7, label="Target (0.80)")
        ax1.set_ylim(0, 1.05)
        ax1.set_xlabel("Year")
        ax1.set_ylabel("North Star Progress (0–1)")
        ax1.set_title("North Star Composite Progress\n50-Year Trajectory")
        ax1.legend(loc="upper left", fontsize=9)

        # Right — corruption trajectory (primary drag on north star)
        for scenario in self.scenarios:
            s_df = self.df[self.df["scenario"] == scenario]
            if "corruption_index" not in s_df.columns:
                continue
            traj = s_df.groupby("year")["corruption_index"].mean()
            color = SCENARIO_COLORS.get(scenario, "gray")
            label = SCENARIO_LABELS.get(scenario, scenario)
            ax2.plot(traj.index, traj.values, color=color,
                     linestyle=SCENARIO_LINESTYLES.get(scenario, "-"),
                     linewidth=2.5, label=label)

        ax2.axhline(0.20, color="green", linestyle="--",
                    linewidth=1.0, alpha=0.7, label="Target (<0.20)")
        ax2.axhline(0.72, color="red", linestyle=":",
                    linewidth=1.0, alpha=0.5, label="Myanmar baseline (0.72)")
        ax2.set_xlabel("Year")
        ax2.set_ylabel("Corruption Index")
        ax2.set_title("Corruption Index Trajectory\n(Primary North Star Drag)")
        ax2.legend(loc="upper right", fontsize=9)

        fig.suptitle(
            "Ka-Nova — North Star Progress toward SEA Leadership",
            fontsize=14, fontweight="bold"
        )
        add_watermark(fig)
        plt.tight_layout()
        plt.savefig(COMPARE_DIR / "north_star_progress.png")
        plt.close()

    def plot_decade_milestones(self):
        """Bar chart of milestone achievement rates per scenario."""
        set_style()

        milestone_file = RESULTS_DIR / "milestone_achievement.csv"
        if not milestone_file.exists():
            return

        milestones_df = pd.read_csv(milestone_file)
        if milestones_df.empty:
            return

        milestone_names = milestones_df["milestone"].unique()
        x = np.arange(len(milestone_names))
        width = 0.25

        fig, ax = plt.subplots(figsize=(12, 6))

        for i, scenario in enumerate(self.scenarios):
            s_df = milestones_df[milestones_df["scenario"] == scenario]
            rates = []
            for milestone in milestone_names:
                m_df = s_df[s_df["milestone"] == milestone]
                rate = m_df["achievement_rate"].values[0] if not m_df.empty else 0.0
                rates.append(rate)

            offset = (i - 1) * width
            bars = ax.bar(
                x + offset, rates, width,
                label=SCENARIO_LABELS.get(scenario, scenario),
                color=SCENARIO_COLORS.get(scenario, "gray"),
                alpha=0.80, edgecolor="white"
            )

        ax.set_xticks(x)
        ax.set_xticklabels(
            [m.replace("_", " ").title() for m in milestone_names],
            rotation=15, ha="right"
        )
        ax.set_ylim(0, 1.1)
        ax.axhline(0.70, color="navy", linestyle="--",
                   linewidth=1.0, alpha=0.6, label="70% threshold")
        ax.set_ylabel("Achievement Rate")
        ax.set_title(
            "Ka-Nova — Decade Milestone Achievement by Scenario",
            fontsize=13, fontweight="bold"
        )
        ax.legend(loc="upper right", fontsize=9)
        add_watermark(fig)
        plt.tight_layout()
        plt.savefig(COMPARE_DIR / "decade_milestones.png")
        plt.close()


# ══════════════════════════════════════════════════════════════════════════════
# 5. CALIBRATION CHART
# ══════════════════════════════════════════════════════════════════════════════

class CalibrationChart:
    """Visualize Year Zero calibration against real Myanmar data."""

    def __init__(self, df: pd.DataFrame):
        self.df = df
        COMPARE_DIR.mkdir(parents=True, exist_ok=True)

    def plot(self):
        """Bar chart — simulation Year 0 vs Myanmar real data."""
        set_style()

        from analysis.kpi import MYANMAR_BASELINES

        year_zero = self.df[self.df["year"] == 0]
        if year_zero.empty:
            return

        kpis = [k for k in MYANMAR_BASELINES.keys() if k in year_zero.columns]
        if not kpis:
            return

        real_vals = [MYANMAR_BASELINES[k] for k in kpis]
        sim_vals  = [year_zero[k].mean() for k in kpis]
        labels    = [k.replace("_", "\n") for k in kpis]

        x = np.arange(len(kpis))
        width = 0.35

        fig, ax = plt.subplots(figsize=(13, 6))

        ax.bar(x - width/2, real_vals, width,
               label="Real Myanmar Data", color="#2C3E50", alpha=0.80)
        ax.bar(x + width/2, sim_vals, width,
               label="Ka-Nova Year 0 Simulation", color=SCENARIO_COLORS["A"],
               alpha=0.80)

        # Error annotations
        for i, (real, sim) in enumerate(zip(real_vals, sim_vals)):
            error_pct = abs(sim - real) / max(0.001, real) * 100
            color = "green" if error_pct < 10 else "orange" if error_pct < 20 else "red"
            ax.text(i, max(real, sim) + 0.02, f"{error_pct:.1f}%",
                    ha="center", va="bottom", fontsize=8, color=color,
                    fontweight="bold")

        ax.set_xticks(x)
        ax.set_xticklabels(labels, fontsize=8)
        ax.set_ylabel("Value")
        ax.set_title(
            "Ka-Nova — Year Zero Calibration vs Real Myanmar Data\n"
            "(Green % = within 10% threshold, Orange = 10–20%, Red = >20%)",
            fontsize=12, fontweight="bold"
        )
        ax.legend(fontsize=10)
        ax.set_ylim(0, 1.1)
        add_watermark(fig)
        plt.tight_layout()
        plt.savefig(COMPARE_DIR / "calibration_year_zero.png")
        plt.close()
        print(f"  Calibration chart saved to {COMPARE_DIR}/calibration_year_zero.png")


# ══════════════════════════════════════════════════════════════════════════════
# 6. SUMMARY DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════

class SummaryDashboard:
    """
    Single-figure summary dashboard — the dissertation key figure.
    Shows the most important findings at a glance.
    """

    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.scenarios = sorted(df["scenario"].unique())
        self.final_year = df["year"].max()
        COMPARE_DIR.mkdir(parents=True, exist_ok=True)

    def plot(self):
        """Generate the main dashboard figure."""
        set_style()
        fig = plt.figure(figsize=FIGSIZE_DASH)
        gs = GridSpec(3, 4, figure=fig, hspace=0.45, wspace=0.35)

        # Title
        fig.suptitle(
            "Project Ka-Nova — Simulation Dashboard\n"
            "Stress-Testing MFU Governance Framework over 50 Years",
            fontsize=15, fontweight="bold", y=0.98
        )

        # Panel 1 — North Star Progress (top left wide)
        ax1 = fig.add_subplot(gs[0, :2])
        self._plot_mini_trajectory(ax1, "north_star_progress",
                                   "North Star Progress", target=0.80)

        # Panel 2 — Corruption (top right wide)
        ax2 = fig.add_subplot(gs[0, 2:])
        self._plot_mini_trajectory(ax2, "corruption_index",
                                   "Corruption Index", target=0.20,
                                   lower_better=True)

        # Panel 3-5 — Key KPIs middle row
        kpis_mid = [
            ("trust_index",       "Trust Index",      False),
            ("coup_probability",  "Coup Probability", True),
            ("ethnic_harmony",    "Ethnic Harmony",   False),
            ("stability_index",   "Stability Index",  False)
        ]
        for i, (kpi, label, lower) in enumerate(kpis_mid):
            ax = fig.add_subplot(gs[1, i])
            self._plot_mini_trajectory(ax, kpi, label, lower_better=lower)

        # Panel 6 — Final year comparison bar (bottom left)
        ax6 = fig.add_subplot(gs[2, :2])
        self._plot_final_comparison_bar(ax6)

        # Panel 7 — Shame register growth (bottom right)
        ax7 = fig.add_subplot(gs[2, 2:])
        self._plot_mini_trajectory(ax7, "shame_register_size",
                                   "Shame Register Growth")

        # Legend
        patches = [
            mpatches.Patch(
                color=SCENARIO_COLORS.get(s, "gray"),
                label=SCENARIO_LABELS.get(s, s), alpha=0.8
            )
            for s in self.scenarios
        ]
        fig.legend(handles=patches, loc="lower center",
                   ncol=len(self.scenarios), bbox_to_anchor=(0.5, 0),
                   fontsize=10, framealpha=0.9)

        add_watermark(fig)
        path = COMPARE_DIR / "summary_dashboard.png"
        plt.savefig(path)
        plt.close()
        print(f"  Summary dashboard saved to {path}")

    def _plot_mini_trajectory(
        self, ax, kpi, title,
        target=None, lower_better=False
    ):
        """Plot a mini trajectory for dashboard panel."""
        if kpi not in self.df.columns:
            ax.set_title(title + "\n(no data)")
            return

        for scenario in self.scenarios:
            s_df = self.df[self.df["scenario"] == scenario]
            traj = s_df.groupby("year")[kpi].mean()
            color = SCENARIO_COLORS.get(scenario, "gray")
            ls    = SCENARIO_LINESTYLES.get(scenario, "-")
            ax.plot(traj.index, traj.values, color=color,
                    linestyle=ls, linewidth=2.0)

        if target is not None:
            ax.axhline(target, color="navy", linestyle="--",
                       linewidth=0.8, alpha=0.6)

        ax.set_title(title, fontsize=10, fontweight="bold")
        ax.set_xlabel("Year", fontsize=8)
        ax.tick_params(labelsize=8)

        direction = "↓ better" if lower_better else "↑ better"
        ax.text(0.98, 0.02, direction, transform=ax.transAxes,
                fontsize=7, ha="right", va="bottom",
                color="gray", style="italic")

    def _plot_final_comparison_bar(self, ax):
        """Horizontal bar chart comparing final-year KPIs."""
        kpis = [
            "corruption_index", "trust_index",
            "ethnic_harmony", "stability_index",
            "employment_rate", "north_star_progress"
        ]
        available = [k for k in kpis if k in self.df.columns]
        if not available:
            return

        final_df = self.df[self.df["year"] == self.final_year]
        y = np.arange(len(available))
        height = 0.25

        for i, scenario in enumerate(self.scenarios):
            s_df = final_df[final_df["scenario"] == scenario]
            vals = [s_df[k].mean() if k in s_df.columns else 0.0
                    for k in available]
            offset = (i - 1) * height
            ax.barh(y + offset, vals, height,
                    label=SCENARIO_LABELS.get(scenario, scenario),
                    color=SCENARIO_COLORS.get(scenario, "gray"),
                    alpha=0.80)

        ax.set_yticks(y)
        ax.set_yticklabels(
            [k.replace("_", " ").title() for k in available],
            fontsize=8
        )
        ax.set_xlim(0, 1.0)
        ax.set_xlabel("Value", fontsize=8)
        ax.set_title("Final Year KPI Comparison", fontsize=10,
                     fontweight="bold")
        ax.tick_params(labelsize=8)


# ══════════════════════════════════════════════════════════════════════════════
# MASTER CHART RUNNER
# ══════════════════════════════════════════════════════════════════════════════

class ChartRunner:
    """Runs all chart generators."""

    def __init__(self, results_dir: Path = RESULTS_DIR):
        self.results_dir = results_dir

    def run_all(self):
        """Generate all charts."""
        print("\n" + "=" * 55)
        print("KA-NOVA CHART GENERATOR")
        print("=" * 55)

        df = load_results()

        print("\n[1/6] KPI Trajectory Charts...")
        KPITrajectoryCharts(df).plot_all()

        print("[2/6] Scenario Comparison Charts...")
        ScenarioComparisonCharts(df).plot_all()

        print("[3/6] Feedback Loop Charts...")
        FeedbackLoopCharts(df).plot_all()

        print("[4/6] North Star Charts...")
        NorthStarChart(df).plot_all()

        print("[5/6] Calibration Chart...")
        CalibrationChart(df).plot()

        print("[6/6] Summary Dashboard...")
        SummaryDashboard(df).plot()

        # Count all generated files
        all_charts = list(CHARTS_DIR.rglob("*.png"))
        print(f"\nTotal charts generated: {len(all_charts)}")
        print(f"Saved to: {CHARTS_DIR}/")
        for chart in sorted(all_charts):
            size_kb = chart.stat().st_size // 1024
            print(f"  {str(chart.relative_to(CHARTS_DIR)):<50} {size_kb:>5} KB")

    def run_single(self, chart_type: str):
        """Run a single chart type."""
        df = load_results()

        chart_map = {
            "kpi":       lambda: KPITrajectoryCharts(df).plot_all(),
            "compare":   lambda: ScenarioComparisonCharts(df).plot_all(),
            "feedback":  lambda: FeedbackLoopCharts(df).plot_all(),
            "northstar": lambda: NorthStarChart(df).plot_all(),
            "calibration": lambda: CalibrationChart(df).plot(),
            "dashboard": lambda: SummaryDashboard(df).plot()
        }

        if chart_type not in chart_map:
            print(f"Unknown chart type: {chart_type}")
            print(f"Available: {list(chart_map.keys())}")
            return

        print(f"Generating {chart_type} charts...")
        chart_map[chart_type]()


# ══════════════════════════════════════════════════════════════════════════════
# CLI
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Ka-Nova Chart Generator")
    parser.add_argument(
        "--chart",
        choices=["kpi","compare","feedback","northstar","calibration","dashboard","all"],
        default="all",
        help="Which charts to generate (default: all)"
    )
    parser.add_argument(
        "--results",
        type=str,
        default="results",
        help="Path to results directory"
    )
    args = parser.parse_args()

    runner = ChartRunner(results_dir=Path(args.results))

    if args.chart == "all":
        runner.run_all()
    else:
        runner.run_single(args.chart)