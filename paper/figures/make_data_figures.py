#!/usr/bin/env python3
"""
Figures 5 and 6: data figures built from the local rule-based campaign.

Reviewer 1 concern 6 asked for figures "regenerated directly from the
underlying data/model as publication-quality vector or high-resolution
graphics" with consistent fonts, labels, symbols and line weights. These are
vector PDF, drawn from results_phase3/scenario_*_all.csv, and share one style
block with no per-figure overrides, the same discipline as the TikZ schematics
in this directory.

SOURCE: the 2026-11-25 local campaign. Six reported scenarios, rule-based
elite layer, N=100 runs, 11,000 citizens, 50 years. Scenario A is excluded
because it is dropped from the reported roster.

FORM CHOICE, stated because it encodes a finding rather than a preference:
six overplotted trajectories would put three near-coincident civilian lines on
top of each other and three military ones on top of each other, which is
visually unreadable and also precisely the result. Small multiples in two rows
by chain_type make the clustering legible instead of hiding it.

COLOUR: two categorical slots only, validated with the dataviz validator
(adjacent-pair delta-E 24.7 protan, 33.6 normal, all six checks pass). Line
style carries the same distinction independently, so the figures remain
readable in greyscale print and under colour-vision deficiency. No figure
relies on hue alone.

NOT INCLUDED: Figures 7 and 8 from the submitted manuscript need the
generative campaign (coup signals emitted by LLM elite agents, and the LLM
versus rule-based comparison). The rule-based arm emits zero coup signals, so
neither can be drawn from this data.
"""
from pathlib import Path
import matplotlib
matplotlib.use("PDF")
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

HERE    = Path(__file__).resolve().parent
RESULTS = Path("results_phase3")

# ── shared style, the single source of truth for these figures ─────────────
CORRUPT = "#2a78d6"   # categorical slot 1
TRUST   = "#eb6834"   # categorical slot 2
INK     = "#1a1a1a"
RULE    = "#787878"
BAND_A  = 0.18        # uncertainty band alpha

plt.rcParams.update({
    "font.family":       "sans-serif",
    "font.sans-serif":   ["Helvetica", "Arial", "DejaVu Sans"],
    "font.size":         8,
    "axes.labelsize":    8,
    "axes.titlesize":    8,
    "xtick.labelsize":   7,
    "ytick.labelsize":   7,
    "legend.fontsize":   7,
    "axes.edgecolor":    RULE,
    "axes.linewidth":    0.4,
    "xtick.color":       RULE,
    "ytick.color":       RULE,
    "text.color":        INK,
    "axes.labelcolor":   INK,
    "grid.color":        RULE,
    "grid.linewidth":    0.3,
    "grid.alpha":        0.35,
    "pdf.fonttype":      42,     # embed TrueType, required by IEEE
    "savefig.bbox":      "tight",
    "savefig.pad_inches": 0.02,
})

MM = 1 / 25.4
CIVILIAN = [("SK", "South Korea 1987"), ("CL", "Chile 1980"), ("DE", "Germany 1949")]
MILITARY = [("PK", "Pakistan 1973+8th"), ("TH", "Thailand 2017"), ("C", "Myanmar 2008")]


def load(code):
    return pd.read_csv(RESULTS / f"scenario_{code.lower()}_all.csv")


def band(ax, df, col, colour, style, label):
    """Mean with a plus/minus one SD band, across whatever runs survive each year."""
    g = df.groupby("year")[col]
    m, s, n = g.mean(), g.std().fillna(0.0), g.size()
    # Only plot years where at least 10 runs remain, so the tail is not a
    # survivor subsample masquerading as a trajectory. Same defect class as
    # the survivor-biased KPI summary fixed in run_phase3.py.
    keep = n >= 10
    m, s = m[keep], s[keep]
    ax.fill_between(m.index, m - s, m + s, color=colour, alpha=BAND_A, linewidth=0)
    ax.plot(m.index, m.values, color=colour, linewidth=1.1, linestyle=style, label=label)


def figure5():
    fig, axes = plt.subplots(2, 3, figsize=(180 * MM, 86 * MM), sharex=True, sharey=True)
    for row, (group, rowname) in enumerate([(CIVILIAN, "civilian chain"),
                                            (MILITARY, "military chain")]):
        for col, (code, title) in enumerate(group):
            ax = axes[row, col]
            df = load(code)
            band(ax, df, "corruption_index", CORRUPT, "-",  "corruption")
            band(ax, df, "trust_index",      TRUST,   "--", "public trust")
            ax.set_title(title, pad=3)
            ax.set_ylim(-0.03, 1.03)
            ax.set_xlim(0, 49)
            ax.grid(True, linewidth=0.3)
            for sp in ("top", "right"):
                ax.spines[sp].set_visible(False)
            fail = df.groupby("run_id")["simulation_failed"].max().mean()
            if fail > 0:
                last = df.groupby("run_id")["year"].max()
                ax.axvline(last.mean(), color=RULE, linewidth=0.5, linestyle=":")
                ax.text(last.mean() - 1, 0.5, f"mean collapse\nyear {last.mean():.1f}",
                        fontsize=5.5, color=RULE, ha="right", va="center")
        axes[row, 0].set_ylabel(f"{rowname}\nindex", linespacing=1.5)
    for ax in axes[1]:
        ax.set_xlabel("simulated year")
    h, l = axes[0, 0].get_legend_handles_labels()
    fig.legend(h, l, loc="lower center", ncol=2, frameon=False,
               bbox_to_anchor=(0.5, -0.04))
    fig.savefig(HERE / "fig5_trajectories.pdf")
    plt.close(fig)


def figure6():
    fig, (axl, axr) = plt.subplots(
        1, 2, figsize=(180 * MM, 68 * MM), gridspec_kw={"width_ratios": [1.35, 1]})

    # left: coup-probability trajectories, grouped by chain_type
    for code, name in CIVILIAN:
        df = load(code)
        g = df.groupby("year")["coup_probability"].mean()
        axl.plot(g.index, g.values, color=CORRUPT, linewidth=1.1, linestyle="-", alpha=0.85)
    for code, name in MILITARY:
        df = load(code)
        g = df.groupby("year")["coup_probability"]
        n = df.groupby("year")["coup_probability"].size()
        m = g.mean()[n >= 10]
        axl.plot(m.index, m.values, color=TRUST, linewidth=1.1, linestyle="--", alpha=0.85)
        axl.text(m.index[-1] + 0.4, m.values[-1], code, fontsize=6, color=TRUST, va="center")
    axl.plot([], [], color=CORRUPT, linewidth=1.1, linestyle="-",
             label="civilian chain (SK, CL, DE)")
    axl.plot([], [], color=TRUST, linewidth=1.1, linestyle="--",
             label="military chain (PK, TH, C)")
    axl.set_xlabel("simulated year")
    axl.set_ylabel("coup probability")
    axl.set_xlim(0, 30)
    axl.set_ylim(-0.03, 1.0)
    axl.grid(True, linewidth=0.3)
    axl.legend(frameon=False, loc="upper left")
    for sp in ("top", "right"):
        axl.spines[sp].set_visible(False)
    axl.set_title("Coup probability, all three civilian encodings pinned at zero", pad=4)

    # right: terminal year. One measure across categories, so a single hue.
    labels, data = [], []
    for code, title in MILITARY:
        labels.append(f"{code}\n{title.split()[0]}")
        data.append(load(code).groupby("run_id")["year"].max().values)
    parts = axr.boxplot(data, vert=False, widths=0.5, patch_artist=True,
                        medianprops=dict(color=INK, linewidth=1.0),
                        boxprops=dict(facecolor=TRUST, alpha=0.30, edgecolor=INK, linewidth=0.6),
                        whiskerprops=dict(color=INK, linewidth=0.6),
                        capprops=dict(color=INK, linewidth=0.6),
                        flierprops=dict(marker="o", markersize=2.5, markerfacecolor=TRUST,
                                        markeredgecolor="none", alpha=0.5))
    for i, d in enumerate(data, start=1):
        axr.text(d.mean() + 1.2, i + 0.30, f"{d.mean():.2f} ± {d.std():.2f}",
                 fontsize=6, color=INK, va="center")
    axr.set_yticks(range(1, len(labels) + 1))
    axr.set_yticklabels(labels)
    axr.axvline(49, color=CORRUPT, linewidth=1.0, linestyle="-")
    axr.text(48.3, 0.55, "all civilian runs\nsurvive to year 49",
             fontsize=6, color=CORRUPT, ha="right", va="bottom")
    axr.set_xlabel("terminal year")
    axr.set_xlim(10, 52)
    axr.grid(True, axis="x", linewidth=0.3)
    for sp in ("top", "right", "left"):
        axr.spines[sp].set_visible(False)
    axr.set_title("Terminal year, 100 runs per scenario", pad=4)

    fig.tight_layout()
    fig.savefig(HERE / "fig6_coup_and_collapse.pdf")
    plt.close(fig)


if __name__ == "__main__":
    figure5()
    figure6()
    print("wrote fig5_trajectories.pdf and fig6_coup_and_collapse.pdf")
