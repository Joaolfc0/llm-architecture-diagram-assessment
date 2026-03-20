"""
Publication-quality figure generation for the paper.
Run from this directory:  python generate_figures.py
Outputs: figure1_criteria.pdf  figure2_conditions.pdf  figure3_errors.pdf
"""

import os
import warnings
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

warnings.filterwarnings("ignore", message=".*tight_layout.*")

# ─── Output directory (same folder as this script) ──────────────────────────
OUT_DIR = os.path.dirname(os.path.abspath(__file__))

# ─── Shared style ────────────────────────────────────────────────────────────
RC = {
    "font.family":       "sans-serif",
    "font.size":         10,
    "axes.spines.top":   False,
    "axes.spines.right": False,
    "axes.spines.left":  True,
    "axes.spines.bottom":True,
    "axes.grid":         True,
    "axes.grid.axis":    "x",
    "grid.color":        "#dddddd",
    "grid.linestyle":    "-",
    "grid.linewidth":    0.7,
    "xtick.labelsize":   9,
    "ytick.labelsize":   10,
    "axes.titlesize":    11,
    "axes.titleweight":  "bold",
    "axes.titlepad":     8,
    "figure.dpi":        150,
}

DOT_COLOR  = "#111111"
BAR_COLOR  = "#111111"
CI_COLOR   = "#555555"


def _save(fig, name):
    path = os.path.join(OUT_DIR, name)
    fig.savefig(path, format="pdf", bbox_inches="tight")
    print(f"  Saved -> {path}")
    plt.close(fig)


# ═══════════════════════════════════════════════════════════════════════════════
#  FIGURE 1 — Core outcomes by criterion
# ═══════════════════════════════════════════════════════════════════════════════
def figure1_criteria():
    # Ordered weakest → strongest (top → bottom on inverted y-axis)
    criteria = ["Clarity", "Accuracy", "Consistency", "Completeness", "Level of detail"]
    y = np.arange(len(criteria))

    # --- Panel A: Agreement rate ---
    agree_vals = [75.6, 84.2, 83.1, 82.1, 87.9]
    agree_lo   = [66.7, 71.1, 74.6, 73.1, 78.8]
    agree_hi   = [84.6, 94.7, 91.5, 91.0, 95.5]
    agree_mean = 82.2   # overall reference line

    # --- Panel B: Factual correctness ---
    fc_vals = [43.6, 55.3, 57.7, 64.2, 66.7]
    fc_lo   = [32.1, 39.5, 46.5, 52.2, 54.5]
    fc_hi   = [55.1, 71.1, 69.0, 76.1, 77.3]
    fc_mean  = 57.5   # overall reference line (approx midpoint for visual)

    with plt.rc_context(RC):
        fig, (ax_a, ax_b) = plt.subplots(
            1, 2, figsize=(10, 3.6), sharey=True,
            gridspec_kw={"wspace": 0.08}
        )

        def _dot_panel(ax, vals, lo, hi, mean_val, title, xlim=(55, 100)):
            xerr_lo = [v - l for v, l in zip(vals, lo)]
            xerr_hi = [h - v for v, h in zip(vals, hi)]
            ax.errorbar(
                vals, y,
                xerr=[xerr_lo, xerr_hi],
                fmt="o",
                color=DOT_COLOR,
                ecolor=CI_COLOR,
                elinewidth=1.4,
                capsize=4,
                capthick=1.4,
                markersize=6,
                linewidth=0,
                zorder=3,
            )
            ax.axvline(mean_val, color="#888888", linewidth=1,
                       linestyle="--", zorder=1, label=f"Overall ({mean_val:.1f}%)")
            ax.set_xlim(xlim)
            ax.set_xlabel("Rate (%)")
            ax.set_title(title)
            ax.set_yticks(y)
            ax.set_yticklabels(criteria)
            ax.invert_yaxis()
            ax.legend(fontsize=8, frameon=False, loc="lower right")

        _dot_panel(ax_a, agree_vals, agree_lo, agree_hi, agree_mean,
                   "A — Agreement rate", xlim=(55, 100))
        _dot_panel(ax_b, fc_vals, fc_lo, fc_hi, fc_mean,
                   "B — Factual correctness rate", xlim=(25, 85))

        # Remove left y-axis tick labels on panel B (shared)
        ax_b.tick_params(labelleft=False)

        fig.tight_layout()
        _save(fig, "figure1_criteria.pdf")


# ═══════════════════════════════════════════════════════════════════════════════
#  FIGURE 2 — Model × representation
# ═══════════════════════════════════════════════════════════════════════════════
def figure2_conditions():
    # y-axis order: ChatGPT–PNG, ChatGPT–SVG, Gemini–PNG, Gemini–SVG
    conditions = ["ChatGPT–PNG", "ChatGPT–SVG", "Gemini–PNG", "Gemini–SVG"]
    y = np.arange(len(conditions))

    # marker: circle for ChatGPT, square for Gemini
    # fill:   filled for PNG, open/hollow for SVG
    styles = [
        # (marker, mfc=markerfacecolor)
        ("o", DOT_COLOR),   # ChatGPT–PNG  filled circle
        ("o", "white"),     # ChatGPT–SVG  open circle
        ("s", DOT_COLOR),   # Gemini–PNG   filled square
        ("s", "white"),     # Gemini–SVG   open square
    ]

    # --- Panel A: Agreement ---
    agree_vals = [83.0, 82.2, 87.3, 75.9]
    agree_lo   = [75.0, 74.8, 78.2, 65.5]
    agree_hi   = [90.0, 88.8, 94.5, 86.2]

    # --- Panel B: Factual correctness ---
    fc_vals = [56.0, 55.1, 70.9, 50.0]
    fc_lo   = [46.0, 45.8, 58.2, 36.2]
    fc_hi   = [66.0, 64.5, 83.6, 62.1]

    with plt.rc_context(RC):
        fig, (ax_a, ax_b) = plt.subplots(
            1, 2, figsize=(10, 3.2), sharey=True,
            gridspec_kw={"wspace": 0.08},
            constrained_layout=True,
        )

        def _dot_panel(ax, vals, lo, hi, title, xlim=(30, 100)):
            for i, (val, l, h, (mk, mfc)) in enumerate(
                zip(vals, lo, hi, styles)
            ):
                ax.errorbar(
                    val, i,
                    xerr=[[val - l], [h - val]],
                    fmt=mk,
                    color=DOT_COLOR,
                    mfc=mfc,
                    mec=DOT_COLOR,
                    mew=1.5,
                    ecolor=CI_COLOR,
                    elinewidth=1.4,
                    capsize=4,
                    capthick=1.4,
                    markersize=7,
                    linewidth=0,
                    zorder=3,
                )
            ax.set_xlim(xlim)
            ax.set_xlabel("Rate (%)")
            ax.set_title(title)
            ax.set_yticks(y)
            ax.set_yticklabels(conditions)
            ax.invert_yaxis()
            # separator between ChatGPT and Gemini rows
            ax.axhline(1.5, color="#cccccc", linewidth=0.8, linestyle="-", zorder=0)

        _dot_panel(ax_a, agree_vals, agree_lo, agree_hi,
                   "A — Agreement rate", xlim=(55, 100))
        _dot_panel(ax_b, fc_vals, fc_lo, fc_hi,
                   "B — Factual correctness rate", xlim=(28, 92))

        ax_b.tick_params(labelleft=False)

        # Legend — placed to the right of panel B, well clear of x-axis labels
        legend_handles = [
            plt.Line2D([0], [0], marker="o", color="w", mfc=DOT_COLOR,
                       mec=DOT_COLOR, mew=1.5, ms=7, label="ChatGPT"),
            plt.Line2D([0], [0], marker="s", color="w", mfc=DOT_COLOR,
                       mec=DOT_COLOR, mew=1.5, ms=7, label="Gemini"),
            plt.Line2D([0], [0], marker="o", color="w", mfc=DOT_COLOR,
                       mec=DOT_COLOR, mew=1.5, ms=7, label="PNG (filled)"),
            plt.Line2D([0], [0], marker="o", color="w", mfc="white",
                       mec=DOT_COLOR, mew=1.5, ms=7, label="SVG (open)"),
        ]
        ax_b.legend(
            legend_handles,
            [h.get_label() for h in legend_handles],
            loc="lower right",
            fontsize=8,
            frameon=True,
            framealpha=0.9,
            edgecolor="#cccccc",
            ncol=1,
        )

        _save(fig, "figure2_conditions.pdf")


# ═══════════════════════════════════════════════════════════════════════════════
#  FIGURE 3 — Error profile
# ═══════════════════════════════════════════════════════════════════════════════
def figure3_errors():
    # Ordered most → least frequent (top → bottom)
    labels  = ["Hallucination", "Omission", "Vagueness", "Other",
               "Logic error", "Contradiction"]
    pcts    = [22.6, 17.5, 16.1, 16.1, 13.1, 2.9]
    counts  = [31,   24,   22,   22,   18,   4]   # n per error type

    y = np.arange(len(labels))

    with plt.rc_context(RC):
        fig, ax = plt.subplots(figsize=(6, 3.6))

        bars = ax.barh(y, pcts, color=BAR_COLOR, height=0.55, zorder=3)

        # Annotate with count at end of bar
        for bar, pct, n in zip(bars, pcts, counts):
            ax.text(
                pct + 0.4, bar.get_y() + bar.get_height() / 2,
                f"n = {n}",
                va="center", ha="left",
                fontsize=8.5, color="#333333",
            )

        ax.set_yticks(y)
        ax.set_yticklabels(labels)
        ax.invert_yaxis()
        ax.set_xlabel("% of incorrect justifications")
        ax.set_xlim(0, 30)
        ax.set_title("Error type distribution among incorrect justifications",
                     fontsize=11, fontweight="bold", pad=8)

        fig.tight_layout()
        _save(fig, "figure3_errors.pdf")


# ═══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("Generating figures…")
    figure1_criteria()
    figure2_conditions()
    figure3_errors()
    print("Done.")
