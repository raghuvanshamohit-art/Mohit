"""Matplotlib rendering for dynamic correlations (headless-safe)."""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")  # no display needed; render straight to files
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402


def plot_dynamic_correlation(
    roll: pd.DataFrame,
    title: str = "Dynamic correlation",
    path: str | None = None,
    ax=None,
):
    """Line chart of one or more pairwise correlation series over time."""
    created = ax is None
    if created:
        fig, ax = plt.subplots(figsize=(11, 6))
    else:
        fig = ax.figure

    for col in roll.columns:
        ax.plot(roll.index, roll[col], label=col.replace("~", "  vs  "), linewidth=1.4)

    ax.axhline(0.0, color="0.4", linewidth=0.8, linestyle="--")
    ax.set_ylim(-1.05, 1.05)
    ax.set_ylabel("Correlation")
    ax.set_title(title)
    ax.grid(True, alpha=0.25)
    ax.legend(loc="upper left", fontsize=8, ncol=max(1, len(roll.columns) // 6 + 1))
    fig.autofmt_xdate()
    fig.tight_layout()

    if path:
        fig.savefig(path, dpi=130)
        if created:
            plt.close(fig)
    return ax


def plot_heatmap(
    corr: pd.DataFrame,
    title: str = "Correlation matrix",
    path: str | None = None,
    ax=None,
):
    """Annotated correlation heatmap (diverging blue–white–red, centred at 0)."""
    created = ax is None
    if created:
        size = max(5.0, 0.85 * len(corr.columns) + 2.5)
        fig, ax = plt.subplots(figsize=(size, size * 0.85))
    else:
        fig = ax.figure

    data = corr.values
    im = ax.imshow(data, cmap="RdBu_r", vmin=-1, vmax=1, aspect="auto")

    ax.set_xticks(range(len(corr.columns)))
    ax.set_yticks(range(len(corr.index)))
    ax.set_xticklabels(corr.columns, rotation=45, ha="right", fontsize=8)
    ax.set_yticklabels(corr.index, fontsize=8)

    for i in range(data.shape[0]):
        for j in range(data.shape[1]):
            val = data[i, j]
            if np.isnan(val):
                continue
            ax.text(
                j, i, f"{val:.2f}", ha="center", va="center",
                color="white" if abs(val) > 0.55 else "black", fontsize=7.5,
            )

    ax.set_title(title)
    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04, label="Correlation")
    fig.tight_layout()

    if path:
        fig.savefig(path, dpi=130)
        if created:
            plt.close(fig)
    return ax
