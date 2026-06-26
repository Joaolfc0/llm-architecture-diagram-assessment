"""Shared helpers for the RQ analyses (RQ1, RQ2, RQ3).

Provides:
- Classification metrics (accuracy, precision, recall, F1, macro-F1) with a fixed
  positive class (label 1).
- Bootstrap confidence intervals for any metric, and for the image-minus-text
  difference of a metric.
- Wilson score interval for a proportion.
- Chi-square goodness-of-fit and independence wrappers.
- matplotlib plotting helpers (grouped bars with error bars, heatmaps) with no
  seaborn dependency.

Conventions:
- Binary labels: 0 = negative, 1 = positive. Positive class for precision/recall/F1 is 1.
- Representation: image = PNG; text = SVG | XML.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Sequence

import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
from sklearn.metrics import accuracy_score, cohen_kappa_score


POSITIVE_LABEL = 1
NEGATIVE_LABEL = 0


# --------------------------------------------------------------------------- #
# Representation mapping
# --------------------------------------------------------------------------- #
def format_to_representation(fmt: str) -> str:
    """Map an input format to its representation group.

    image = png; text = svg | xml.
    """
    f = str(fmt).strip().lower()
    if f == "png":
        return "image"
    if f in ("svg", "xml"):
        return "text"
    raise ValueError(f"Unknown format {fmt!r}; expected png/svg/xml")


# --------------------------------------------------------------------------- #
# Classification metrics
# --------------------------------------------------------------------------- #
@dataclass
class Confusion:
    tp: int
    fp: int
    fn: int
    tn: int

    @property
    def n(self) -> int:
        return self.tp + self.fp + self.fn + self.tn


def confusion(y_true: Sequence[int], y_pred: Sequence[int]) -> Confusion:
    """Confusion counts with positive class = 1."""
    yt = np.asarray(y_true).astype(int)
    yp = np.asarray(y_pred).astype(int)
    tp = int(np.sum((yt == POSITIVE_LABEL) & (yp == POSITIVE_LABEL)))
    fp = int(np.sum((yt == NEGATIVE_LABEL) & (yp == POSITIVE_LABEL)))
    fn = int(np.sum((yt == POSITIVE_LABEL) & (yp == NEGATIVE_LABEL)))
    tn = int(np.sum((yt == NEGATIVE_LABEL) & (yp == NEGATIVE_LABEL)))
    return Confusion(tp=tp, fp=fp, fn=fn, tn=tn)


def _safe_div(num: float, den: float, zero_division: float = 0.0) -> float:
    return num / den if den else zero_division


def accuracy(y_true: Sequence[int], y_pred: Sequence[int]) -> float:
    c = confusion(y_true, y_pred)
    return _safe_div(c.tp + c.tn, c.n)


def precision(y_true: Sequence[int], y_pred: Sequence[int], zero_division: float = 0.0) -> float:
    c = confusion(y_true, y_pred)
    return _safe_div(c.tp, c.tp + c.fp, zero_division)


def recall(y_true: Sequence[int], y_pred: Sequence[int], zero_division: float = 0.0) -> float:
    c = confusion(y_true, y_pred)
    return _safe_div(c.tp, c.tp + c.fn, zero_division)


def f1(y_true: Sequence[int], y_pred: Sequence[int], zero_division: float = 0.0) -> float:
    p = precision(y_true, y_pred, zero_division)
    r = recall(y_true, y_pred, zero_division)
    return _safe_div(2 * p * r, p + r, zero_division)


def _f1_for_label(y_true: np.ndarray, y_pred: np.ndarray, label: int) -> float:
    tp = int(np.sum((y_true == label) & (y_pred == label)))
    fp = int(np.sum((y_true != label) & (y_pred == label)))
    fn = int(np.sum((y_true == label) & (y_pred != label)))
    p = _safe_div(tp, tp + fp)
    r = _safe_div(tp, tp + fn)
    return _safe_div(2 * p * r, p + r)


def macro_f1(y_true: Sequence[int], y_pred: Sequence[int]) -> float:
    yt = np.asarray(y_true).astype(int)
    yp = np.asarray(y_pred).astype(int)
    return float(np.mean([_f1_for_label(yt, yp, lab) for lab in (NEGATIVE_LABEL, POSITIVE_LABEL)]))


def agreement(y_true: Sequence[int], y_pred: Sequence[int]) -> float:
    """Simple (raw) agreement = fraction of items where the two labels coincide.

    Thin wrapper over sklearn.metrics.accuracy_score, framed as
    rater-vs-ground-truth agreement.
    """
    if len(y_true) == 0:
        return float("nan")
    return float(accuracy_score(y_true, y_pred))


def cohen_kappa(y_true: Sequence[int], y_pred: Sequence[int]) -> float:
    """Cohen's kappa: chance-corrected agreement between two label sets.

    Thin wrapper over sklearn.metrics.cohen_kappa_score. Returns 1.0 for perfect
    agreement and 0.0 for agreement at chance level. When both label sets are
    constant and identical, sklearn returns NaN, so we map that to 1.0.
    """
    yt = np.asarray(y_true).astype(int)
    yp = np.asarray(y_pred).astype(int)
    if len(yt) == 0:
        return float("nan")
    with np.errstate(invalid="ignore"):
        k = cohen_kappa_score(yt, yp, labels=[NEGATIVE_LABEL, POSITIVE_LABEL])
    if np.isnan(k) and np.array_equal(yt, yp):
        return 1.0
    return float(k)


def ordinal_scale(lo: float = 1.0, hi: float = 4.0, step: float = 0.5) -> np.ndarray:
    """Full ordinal category grid (e.g. [1.0, 1.5, ..., 4.0]).

    Used as the `labels` set for weighted kappa so that the ordinal distances
    between half-step categories are encoded correctly (adjacent half-steps are
    one index apart, full points are two indices apart).
    """
    n = int(round((hi - lo) / step)) + 1
    return np.round(lo + step * np.arange(n), 6)


def weighted_cohen_kappa(
    y_true: Sequence[float],
    y_pred: Sequence[float],
    weights: str = "quadratic",
    labels: Sequence[float] | None = None,
) -> float:
    """Weighted Cohen's kappa for ORDINAL agreement.

    Thin wrapper over sklearn.metrics.cohen_kappa_score with `weights` set to
    'quadratic' (default) or 'linear'. Penalizes disagreements by how far apart
    the categories are on the ordinal scale.

    `labels` should be the full ordered category grid (see `ordinal_scale`) so the
    ordinal distances are correct even if some categories are absent from a sample.
    Returns 1.0 when both inputs are identical and constant (sklearn returns NaN).
    """
    yt = np.asarray(y_true, dtype=float)
    yp = np.asarray(y_pred, dtype=float)
    if len(yt) == 0:
        return float("nan")
    if labels is None:
        labels = np.unique(np.concatenate([yt, yp]))
    labels = np.round(np.asarray(labels, dtype=float), 6)

    # sklearn rejects fractional (continuous) labels, so encode each ordinal value
    # as its integer index in the grid. Index distance == ordinal distance, which
    # is exactly what quadratic/linear weights need.
    index_of = {v: i for i, v in enumerate(labels)}
    try:
        yt_idx = np.array([index_of[round(float(v), 6)] for v in yt], dtype=int)
        yp_idx = np.array([index_of[round(float(v), 6)] for v in yp], dtype=int)
    except KeyError as exc:
        raise ValueError(
            f"Value {exc} not present in the ordinal grid {list(labels)}; "
            "pass a `labels` grid that covers all observed scores."
        ) from None

    with np.errstate(invalid="ignore"):
        k = cohen_kappa_score(
            yt_idx, yp_idx, labels=list(range(len(labels))), weights=weights
        )
    if np.isnan(k) and np.array_equal(yt_idx, yp_idx):
        return 1.0
    return float(k)


def spearman_corr(x: Sequence[float], y: Sequence[float]) -> tuple[float, float]:
    """Spearman rank correlation (rho, p-value) via scipy.

    Complementary ordinal-association measure that handles the fractional GT mean
    naturally. Returns (nan, nan) if fewer than 2 paired points or no variance.
    """
    xa = np.asarray(x, dtype=float)
    ya = np.asarray(y, dtype=float)
    if len(xa) < 2:
        return float("nan"), float("nan")
    res = stats.spearmanr(xa, ya)
    return float(res.statistic), float(res.pvalue)


def metrics(y_true: Sequence[int], y_pred: Sequence[int]) -> dict[str, float]:
    """All metrics at once."""
    return {
        "accuracy": accuracy(y_true, y_pred),
        "precision": precision(y_true, y_pred),
        "recall": recall(y_true, y_pred),
        "f1": f1(y_true, y_pred),
        "macro_f1": macro_f1(y_true, y_pred),
        "n": int(len(y_true)),
    }


# --------------------------------------------------------------------------- #
# Bootstrap confidence intervals
# --------------------------------------------------------------------------- #
def bootstrap_ci(
    y_true: Sequence[int],
    y_pred: Sequence[int],
    metric_fn: Callable[[Sequence[int], Sequence[int]], float],
    n_boot: int = 10000,
    conf: float = 0.95,
    seed: int = 42,
) -> tuple[float, float, float]:
    """Percentile bootstrap CI for a paired (y_true, y_pred) metric.

    Returns (point_estimate, lo, hi).
    """
    yt = np.asarray(y_true).astype(int)
    yp = np.asarray(y_pred).astype(int)
    n = len(yt)
    point = float(metric_fn(yt, yp))
    if n == 0:
        return point, float("nan"), float("nan")
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, n, size=(n_boot, n))
    stats_arr = np.empty(n_boot, dtype=float)
    for b in range(n_boot):
        sample = idx[b]
        stats_arr[b] = metric_fn(yt[sample], yp[sample])
    alpha = (1.0 - conf) / 2.0
    lo = float(np.percentile(stats_arr, 100 * alpha))
    hi = float(np.percentile(stats_arr, 100 * (1 - alpha)))
    return point, lo, hi


def bootstrap_diff_ci(
    y_true_a: Sequence[int],
    y_pred_a: Sequence[int],
    y_true_b: Sequence[int],
    y_pred_b: Sequence[int],
    metric_fn: Callable[[Sequence[int], Sequence[int]], float],
    n_boot: int = 10000,
    conf: float = 0.95,
    seed: int = 42,
) -> dict[str, float]:
    """Bootstrap CI for metric(A) - metric(B), resampling each group independently.

    Group A is intended to be 'image', group B 'text'. Returns point diff, lo, hi,
    and whether the CI excludes 0.
    """
    yta, ypa = np.asarray(y_true_a).astype(int), np.asarray(y_pred_a).astype(int)
    ytb, ypb = np.asarray(y_true_b).astype(int), np.asarray(y_pred_b).astype(int)
    na, nb = len(yta), len(ytb)
    point = float(metric_fn(yta, ypa) - metric_fn(ytb, ypb))
    rng = np.random.default_rng(seed)
    idx_a = rng.integers(0, na, size=(n_boot, na))
    idx_b = rng.integers(0, nb, size=(n_boot, nb))
    diffs = np.empty(n_boot, dtype=float)
    for b in range(n_boot):
        sa, sb = idx_a[b], idx_b[b]
        diffs[b] = metric_fn(yta[sa], ypa[sa]) - metric_fn(ytb[sb], ypb[sb])
    alpha = (1.0 - conf) / 2.0
    lo = float(np.percentile(diffs, 100 * alpha))
    hi = float(np.percentile(diffs, 100 * (1 - alpha)))
    return {
        "diff": point,
        "lo": lo,
        "hi": hi,
        "excludes_zero": bool(lo > 0 or hi < 0),
    }


# --------------------------------------------------------------------------- #
# Proportion CI (Wilson)
# --------------------------------------------------------------------------- #
def wilson_ci(successes: int, n: int, conf: float = 0.95) -> tuple[float, float, float]:
    """Wilson score interval for a binomial proportion.

    Returns (proportion, lo, hi).
    """
    if n == 0:
        return float("nan"), float("nan"), float("nan")
    p = successes / n
    z = stats.norm.ppf(1 - (1 - conf) / 2.0)
    denom = 1 + z**2 / n
    center = (p + z**2 / (2 * n)) / denom
    margin = (z * np.sqrt(p * (1 - p) / n + z**2 / (4 * n**2))) / denom
    return float(p), float(center - margin), float(center + margin)


# --------------------------------------------------------------------------- #
# Chi-square wrappers
# --------------------------------------------------------------------------- #
@dataclass
class Chi2Result:
    chi2: float
    p_value: float
    dof: int
    expected: np.ndarray
    observed: np.ndarray
    min_expected: float
    low_expected_warning: bool

    def summary(self) -> str:
        warn = (
            "\n  WARNING: some expected counts < 5; chi-square approximation may be unreliable."
            if self.low_expected_warning
            else ""
        )
        return (
            f"chi2 = {self.chi2:.4f}, dof = {self.dof}, p = {self.p_value:.4g}, "
            f"min expected = {self.min_expected:.2f}{warn}"
        )


def chi2_gof(counts: Sequence[int], expected_probs: Sequence[float] | None = None) -> Chi2Result:
    """Chi-square goodness-of-fit test.

    counts: observed counts per category.
    expected_probs: expected probabilities (defaults to uniform). Must sum to 1.
    """
    obs = np.asarray(counts, dtype=float)
    total = obs.sum()
    k = len(obs)
    if expected_probs is None:
        expected_probs = np.full(k, 1.0 / k)
    expected_probs = np.asarray(expected_probs, dtype=float)
    expected = expected_probs * total
    chi2, p = stats.chisquare(f_obs=obs, f_exp=expected)
    min_exp = float(expected.min())
    return Chi2Result(
        chi2=float(chi2),
        p_value=float(p),
        dof=k - 1,
        expected=expected,
        observed=obs,
        min_expected=min_exp,
        low_expected_warning=min_exp < 5,
    )


def chi2_independence(table: np.ndarray) -> Chi2Result:
    """Chi-square test of independence on a contingency table (rows x cols)."""
    obs = np.asarray(table, dtype=float)
    chi2, p, dof, expected = stats.chi2_contingency(obs)
    min_exp = float(expected.min())
    return Chi2Result(
        chi2=float(chi2),
        p_value=float(p),
        dof=int(dof),
        expected=expected,
        observed=obs,
        min_expected=min_exp,
        low_expected_warning=min_exp < 5,
    )


# --------------------------------------------------------------------------- #
# Plotting helpers (matplotlib only)
# --------------------------------------------------------------------------- #
FIGSIZE = (7.5, 5.0)
FIGSIZE_WIDE = (9.5, 5.5)  # many x-axis groups (criteria, breakdowns)
FIGSIZE_ROW_4 = (11.0, 2.75)  # thin 4-panel row (RQ1)
FIGSIZE_ROW_3 = (10.5, 2.75)  # thin 3-panel row (RQ2 pooled)
LATEX_FIGSIZE = FIGSIZE  # backward-compatible alias
LATEX_FIGSIZE_WIDE = FIGSIZE_WIDE
REP_COLORS = {"image": "#4C72B0", "text": "#DD8452"}


def save_figure(fig: plt.Figure, path, dpi: int = 150) -> None:
    """Save with padding so titles and axis labels are not clipped."""
    fig.tight_layout(pad=1.4)
    fig.savefig(path, dpi=dpi, bbox_inches="tight", pad_inches=0.25)


def values_by_diagram(
    df,
    metric_fn: Callable,
    y_true_col: str = "gt_label",
    y_pred_col: str = "llm_label",
) -> list[float]:
    """Compute a metric once per diagram (empirical unit for boxplots)."""
    vals: list[float] = []
    for _, g in df.groupby("Diagram_ID", sort=True):
        yt = g[y_true_col].to_numpy()
        yp = g[y_pred_col].to_numpy()
        if len(yt) == 0:
            continue
        vals.append(float(metric_fn(yt, yp)))
    return vals


def kappa_values_by_diagram(
    df,
    y_true_col: str = "gt_score_mean",
    y_pred_col: str = "score",
    labels=None,
    weights: str = "quadratic",
) -> list[float]:
    """Weighted kappa per diagram for ordinal boxplots."""
    if labels is None:
        labels = ordinal_scale()
    vals: list[float] = []
    for _, g in df.groupby("Diagram_ID", sort=True):
        yt = g[y_true_col].to_numpy()
        yp = g[y_pred_col].to_numpy()
        if len(yt) == 0:
            continue
        vals.append(float(weighted_cohen_kappa(yt, yp, weights=weights, labels=labels)))
    return vals


def slim_boxplot(
    ax: plt.Axes,
    box_data: Sequence[Sequence[float]],
    labels: Sequence[str],
    colors: Sequence[str] | None = None,
    title: str = "",
    ylabel: str = "",
    ylim: tuple[float, float] | None = (0, 1),
    widths: float = 0.55,
    *,
    panel: bool = False,
    show_ylabel: bool = True,
    label_rotation: float = 25,
) -> plt.Axes:
    """Empirical boxplot — one box per label, no CI/error bars."""
    if panel:
        widths = 0.42
    positions = np.arange(1, len(labels) + 1)
    bp = ax.boxplot(
        [list(d) for d in box_data],
        positions=positions,
        widths=widths,
        patch_artist=True,
        showfliers=True,
        medianprops={"color": "black", "linewidth": 1.0 if panel else 1.2},
        whiskerprops={"linewidth": 0.7},
        capprops={"linewidth": 0.7},
    )
    if colors:
        for patch, color in zip(bp["boxes"], colors):
            patch.set_facecolor(color)
            patch.set_alpha(0.75)
            patch.set_edgecolor("black")
            patch.set_linewidth(0.5)
    ax.set_xticks(positions)
    fs_tick = 8 if panel else 10
    ax.set_xticklabels(labels, rotation=label_rotation, ha="right", fontsize=fs_tick)
    if ylim:
        lo, hi = ylim
        span = hi - lo if hi > lo else 1.0
        pad = 0.04 if panel else 0.06
        ax.set_ylim(lo, hi + span * pad)
    if show_ylabel and ylabel:
        ax.set_ylabel(ylabel, fontsize=9 if panel else 11)
    elif not show_ylabel:
        ax.set_ylabel("")
    fs_title = 9 if panel else 12
    pad_title = 6 if panel else 10
    ax.set_title(title, fontsize=fs_title, pad=pad_title)
    ax.tick_params(axis="y", labelsize=8 if panel else 10)
    ax.grid(axis="y", linestyle=":", alpha=0.5)
    return ax


def add_rep_legend(fig: plt.Figure, ncol: int = 2) -> None:
    """Shared image/text legend for multi-panel figures."""
    handles = [
        plt.Rectangle((0, 0), 1, 1, fc=REP_COLORS["image"], alpha=0.75, ec="black"),
        plt.Rectangle((0, 0), 1, 1, fc=REP_COLORS["text"], alpha=0.75, ec="black"),
    ]
    fig.legend(
        handles, ["image", "text"], loc="upper center",
        ncol=ncol, fontsize=8, frameon=False,
        bbox_to_anchor=(0.5, 1.02),
    )


def slim_grouped_boxplot(
    ax: plt.Axes,
    box_data: dict[str, list[list[float]]],
    group_labels: Sequence[str],
    series_names: Sequence[str],
    title: str = "",
    ylabel: str = "",
    ylim: tuple[float, float] | None = (0, 1),
) -> plt.Axes:
    """Grouped empirical boxplots (e.g. image vs text at each criterion)."""
    n_groups = len(group_labels)
    n_series = len(series_names)
    width = 0.7 / max(n_series, 1)
    positions: list[float] = []
    data: list[list[float]] = []
    colors: list[str] = []

    for gi, gname in enumerate(group_labels):
        for si, sname in enumerate(series_names):
            positions.append(gi + 1 + (si - (n_series - 1) / 2) * width)
            data.append(list(box_data[sname][gi]))
            colors.append(REP_COLORS.get(sname, "#888888"))

    bp = ax.boxplot(
        data,
        positions=positions,
        widths=width * 0.85,
        patch_artist=True,
        showfliers=True,
        medianprops={"color": "black", "linewidth": 1.0},
    )
    for patch, color in zip(bp["boxes"], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.75)
        patch.set_edgecolor("black")
        patch.set_linewidth(0.5)

    ax.set_xticks(np.arange(1, n_groups + 1))
    ax.set_xticklabels(group_labels, rotation=25, ha="right", fontsize=10)
    if ylim:
        lo, hi = ylim
        span = hi - lo if hi > lo else 1.0
        ax.set_ylim(lo, hi + span * 0.06)
    ax.set_ylabel(ylabel, fontsize=11)
    ax.set_title(title, fontsize=12, pad=10)
    ax.tick_params(axis="y", labelsize=10)
    handles = [
        plt.Rectangle((0, 0), 1, 1, fc=REP_COLORS.get(s, "#888888"), alpha=0.75, ec="black")
        for s in series_names
    ]
    ax.legend(handles, series_names, fontsize=10, loc="upper right")
    ax.grid(axis="y", linestyle=":", alpha=0.5)
    return ax


def slim_bar(
    ax: plt.Axes,
    labels: Sequence[str],
    values: Sequence[float],
    colors: Sequence[str],
    title: str = "",
    ylabel: str = "",
    ylim: tuple[float, float] | None = None,
    show_counts: Sequence[int] | None = None,
) -> plt.Axes:
    """Thin bar chart for categorical counts (no CI)."""
    x = np.arange(len(labels))
    ax.bar(x, values, color=colors, edgecolor="black", linewidth=0.5, width=0.55)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=11)
    if ylim:
        lo, hi = ylim
        top = hi + (hi - lo) * 0.12 if show_counts is not None else hi + (hi - lo) * 0.06
        ax.set_ylim(lo, top)
    ax.set_ylabel(ylabel, fontsize=11)
    ax.set_title(title, fontsize=12, pad=10)
    ax.tick_params(axis="y", labelsize=10)
    ax.grid(axis="y", linestyle=":", alpha=0.5)
    if show_counts is not None:
        for i, (v, c) in enumerate(zip(values, show_counts)):
            ax.text(i, v + 0.015, str(c), ha="center", va="bottom", fontsize=10)
    return ax


def grouped_bar_with_ci(
    ax: plt.Axes,
    group_labels: Sequence[str],
    series: dict[str, dict[str, tuple[float, float, float]]],
    title: str = "",
    ylabel: str = "",
    ylim: tuple[float, float] | None = (0, 1),
) -> plt.Axes:
    """Grouped bar chart with asymmetric error bars (point, lo, hi).

    group_labels: x-axis groups (e.g. metric names or criteria).
    series: {series_name: {group_label: (point, lo, hi)}}.
    """
    n_groups = len(group_labels)
    series_names = list(series.keys())
    n_series = len(series_names)
    x = np.arange(n_groups)
    width = 0.8 / max(n_series, 1)

    for i, sname in enumerate(series_names):
        points, los, his = [], [], []
        for g in group_labels:
            pt, lo, hi = series[sname].get(g, (np.nan, np.nan, np.nan))
            points.append(pt)
            los.append(pt - lo if not np.isnan(lo) else 0)
            his.append(hi - pt if not np.isnan(hi) else 0)
        offset = (i - (n_series - 1) / 2) * width
        ax.bar(
            x + offset,
            points,
            width=width,
            label=sname,
            color=REP_COLORS.get(sname, None),
            yerr=[los, his],
            capsize=4,
            edgecolor="black",
            linewidth=0.5,
        )

    ax.set_xticks(x)
    ax.set_xticklabels(group_labels, rotation=20, ha="right")
    if ylim:
        ax.set_ylim(*ylim)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.legend()
    ax.grid(axis="y", linestyle=":", alpha=0.5)
    return ax


def confusion_heatmap(ax: plt.Axes, c: Confusion, title: str = "") -> plt.Axes:
    """Render a 2x2 confusion matrix as a heatmap.

    Layout (rows = actual, cols = predicted), order [negative(0), positive(1)].
    """
    mat = np.array([[c.tn, c.fp], [c.fn, c.tp]], dtype=int)
    im = ax.imshow(mat, cmap="Blues")
    ax.set_xticks([0, 1])
    ax.set_yticks([0, 1])
    ax.set_xticklabels(["pred 0", "pred 1"])
    ax.set_yticklabels(["actual 0", "actual 1"])
    thresh = mat.max() / 2 if mat.max() else 0.5
    for r in range(2):
        for col in range(2):
            ax.text(
                col,
                r,
                str(mat[r, col]),
                ha="center",
                va="center",
                color="white" if mat[r, col] > thresh else "black",
                fontsize=12,
            )
    ax.set_title(title)
    return im


def value_heatmap(
    ax: plt.Axes,
    matrix: np.ndarray,
    row_labels: Sequence[str],
    col_labels: Sequence[str],
    title: str = "",
    fmt: str = "{:.2f}",
    cmap: str = "viridis",
    vmin: float = 0.0,
    vmax: float = 1.0,
) -> plt.Axes:
    """Annotated heatmap for a value matrix (e.g. F1 by criterion x representation)."""
    im = ax.imshow(matrix, cmap=cmap, vmin=vmin, vmax=vmax, aspect="auto")
    ax.set_xticks(np.arange(len(col_labels)))
    ax.set_yticks(np.arange(len(row_labels)))
    ax.set_xticklabels(col_labels)
    ax.set_yticklabels(row_labels)
    for r in range(matrix.shape[0]):
        for col in range(matrix.shape[1]):
            val = matrix[r, col]
            if not np.isnan(val):
                ax.text(
                    col,
                    r,
                    fmt.format(val),
                    ha="center",
                    va="center",
                    color="white" if val < (vmin + vmax) / 2 else "black",
                    fontsize=10,
                )
    ax.set_title(title)
    return im
