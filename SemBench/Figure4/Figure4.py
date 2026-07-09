#figure 4
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from matplotlib.gridspec import GridSpec
from matplotlib import patheffects as pe
from matplotlib.ticker import AutoMinorLocator
from io import StringIO
import os
import re
from pathlib import Path

CUR_dir = Path(__file__).parent.resolve()
DEFAULT_INPUT = CUR_dir.parent / "finalresult.csv"
DEFAULT_OUT_PNG = CUR_dir / "Figure 4.png"
DEFAULT_OUT_PDF = CUR_dir / "Figure 4.pdf"
# -------------------------
# Global style
# -------------------------
plt.rcParams.update({
    "font.size": 12,
    "axes.titlesize": 13,
    "axes.labelsize": 12,
    "xtick.labelsize": 11,
    "ytick.labelsize": 11,
    "legend.fontsize": 9,
    "axes.linewidth": 1.1,
    "xtick.direction": "out",
    "ytick.direction": "out",
    "xtick.major.size": 4.5,
    "ytick.major.size": 4.5,
    "xtick.minor.size": 2.5,
    "ytick.minor.size": 2.5,
    "grid.linewidth": 0.6,
})

# -------------------------
# Data (inline CSV from user)
# -------------------------
df = pd.read_csv(DEFAULT_INPUT)
# -------------------------
# Unique markers per model (no abbreviations)
# -------------------------
# A stable list of distinct markers; repeat if more models than markers
marker_cycle = ["o", "s", "D", "^", "v", "<", ">", "P", "X", "*", "H", "+", "x", "1", "2", "3", "4"]
markers = {model: marker_cycle[i % len(marker_cycle)] for i, model in enumerate(df["model"].tolist())}
df["Marker"] = df["model"].map(markers)
# -------------------------
# Consistent color mapping for models
# -------------------------
color_cycle = plt.rcParams["axes.prop_cycle"].by_key()["color"]
color_map = {model: color_cycle[i % len(color_cycle)] for i, model in enumerate(df["model"])}



# -------------------------
# Helper: add linear fit + ρ text with white halo
# -------------------------
def add_fit_line(ax, x_series, y_series, line_kwargs=None, text_anchor=(0.03, 0.97)):
    if line_kwargs is None:
        line_kwargs = {"linewidth": 2, "alpha": 0.9}

    x = np.asarray(x_series, dtype=float)
    y = np.asarray(y_series, dtype=float)
    mask = ~np.isnan(x) & ~np.isnan(y)
    x = x[mask]; y = y[mask]
    if x.size < 2:
        return

    m, b = np.polyfit(x, y, deg=1)
    xs = np.linspace(0, 100, 200)
    ys = m * xs + b

    line = ax.plot(xs, ys, zorder=3, solid_capstyle="round", **line_kwargs)[0]
    line.set_path_effects([pe.Stroke(linewidth=line.get_linewidth() + 2.0, foreground="white"),
                           pe.Normal()])

    # --- Linear regression p-value (slope == 0) ---
    try:
        from scipy.stats import linregress
        lr = linregress(x, y)
        lr_p = lr.pvalue  # two-sided p-value for H0: slope = 0

        if lr_p <= 0.001:
            lr_stars = "***"
        elif lr_p <= 0.01:
            lr_stars = "**"
        elif lr_p <= 0.05:
            lr_stars = "*"
        else:
            lr_stars = ""

        lr_text = rf"$p_{{LR}}={lr_p:.3f}{lr_stars}$"
    except Exception:
        lr_text = None    
    try:
        from scipy.stats import spearmanr
        rho, pval = spearmanr(x, y)

        # significance stars
        if pval <= 0.001:
            stars = "***"
        elif pval <= 0.01:
            stars = "**"
        elif pval <= 0.05:
            stars = "*"
        else:
            stars = ""

        sp_text = (
            rf"$\rho = {rho:.2f}$(p-value={pval:.3f}{stars})")
        

    except Exception:
        xr = pd.Series(x).rank().to_numpy()
        yr = pd.Series(y).rank().to_numpy()
        rho = np.corrcoef(xr, yr)[0, 1]
        sp_text = rf"$\rho = {rho:.2f}$"
    # Annotate (equation + rho)
    sign = "+" if b >= 0 else "−"
    eq_text = rf"$y = {m:.2f}x\, {sign}\, {abs(b):.2f}$"
    eq_text += (f", {lr_text}" if lr_text is not None else "")


    txt = ax.text(
        text_anchor[0], text_anchor[1],
        eq_text + "\n" + sp_text,
        transform=ax.transAxes,
        va=("top" if text_anchor[1] > 0.5 else "bottom"),
        ha=("left" if text_anchor[0] < 0.5 else "right"),
        fontsize=9, #fontweight="semibold",
        bbox=dict(boxstyle="round,pad=0.25,rounding_size=0.15", fc="white", ec="#D0D0D0", alpha=0.9),
        zorder=4
    )
    txt.set_path_effects([pe.Stroke(linewidth=1.2, foreground="white"), pe.Normal()])

# -------------------------
# Figure layout: 2 rows x 6 columns
# -------------------------
# Columns correspond to the 6 semantic categories
cat_colshuman = [
    ("Dead Code - statement", "DeadCode_p1"),
    ("Data Dependency", "DataDep_p1"),
    ("Function Reachability", "FuncReach_p1"),
    ("Dominators", "Dominators_p1"),
    ("Dead Code - loop", "LoopReach_p1"),
    ("Liveness", "Liveness_p1"),
]
cat_colsmbpp = cat_colshuman

fig = plt.figure(figsize=(18, 6.8))
gs = GridSpec(2, 6, wspace=0.25, hspace=0.35)

axes = []
for r in range(2):
    row_axes = []
    for c in range(6):
        row_axes.append(fig.add_subplot(gs[r, c]))
    axes.append(row_axes)

# Styling helper
def style_ax(ax, title=None, xlabel=None, ylabel=None):
    # spines
    ax.spines["left"].set_color("#3A3A3A");   ax.spines["left"].set_linewidth(1.1)
    ax.spines["bottom"].set_color("#3A3A3A"); ax.spines["bottom"].set_linewidth(1.1)
    ax.spines["top"].set_color("#BDBDBD");    ax.spines["top"].set_linewidth(0.9)
    ax.spines["right"].set_color("#BDBDBD");  ax.spines["right"].set_linewidth(0.9)
    # grid
    ax.xaxis.set_minor_locator(AutoMinorLocator(2))
    ax.yaxis.set_minor_locator(AutoMinorLocator(2))
    ax.grid(which="major", linestyle="--", color="#B0B0B0", alpha=0.35)
    ax.grid(which="minor", linestyle=":",  color="#CFCFCF", alpha=0.25)
    ax.set_axisbelow(True)
    if title:  ax.set_title(title)
    if xlabel: ax.set_xlabel(xlabel)
    if ylabel: ax.set_ylabel(ylabel)
    # lock display ranges to 0-100 for apples-to-apples across panels
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)

# -------------------------
# Helper: panel labels (a, b, c, ...)
# -------------------------
def add_panel_label(ax, label, xy=(0.03, 0.06)):
    t = ax.text(
        xy[0], xy[1], f"({label})",
        transform=ax.transAxes,
        ha="left", va="bottom",
        fontsize=12, fontweight="bold",
        zorder=10
    )
    # optional: subtle white halo to keep readable on gridlines
    t.set_path_effects([pe.Stroke(linewidth=2.0, foreground="white"), pe.Normal()])


# -------------------------
# Plotting
# -------------------------
# Top row: HumanEval vs category
for j, (nice_name, col) in enumerate(cat_colshuman):
    ax = axes[0][j]
    style_ax(ax, title=nice_name, xlabel="HumanEval Pass@1 (%)", ylabel=("Accuracy (%)" if j == 0 else None))
    add_panel_label(ax, chr(ord("a") + j), xy=(0.03, 0.06))
    sub = df.dropna(subset=["HumanEval_p1", col])
    for _, row in sub.iterrows():
        ax.scatter(
            row["HumanEval_p1"], row[col],
            marker=row["Marker"], s=70,
            color=color_map[row["model"]],
            zorder=5
        )
    add_fit_line(ax, sub["HumanEval_p1"].values if len(sub) else np.array([]),
                    sub[col].values if len(sub) else np.array([]),
                 line_kwargs={"linewidth": 2, "alpha": 0.9}, text_anchor=(0.03, 0.97))

# Bottom row: MBPP vs category
for j, (nice_name, col) in enumerate(cat_colsmbpp):
    ax = axes[1][j]
    style_ax(
        ax,
        title=nice_name,
        xlabel=f"MBPP Pass@1 (%)", 
        ylabel=("Accuracy (%)" if j == 0 else None)
    )
    add_panel_label(ax, chr(ord("g") + j), xy=(0.03, 0.06))
    sub = df.dropna(subset=["MBPP_p1", col])
    for _, row in sub.iterrows():
        ax.scatter(
            row["MBPP_p1"], row[col],
            marker=row["Marker"], s=70,
            color=color_map[row["model"]],
            zorder=5
        )

    add_fit_line(ax, sub["MBPP_p1"].values if len(sub) else np.array([]),
                    sub[col].values if len(sub) else np.array([]),
                line_kwargs={"linewidth": 2, "alpha": 0.9, "linestyle": "--"},
                text_anchor=(0.03, 0.97))

# -------------------------
# Figure-level legend (colors consistent with figure)
# -------------------------
handles, labels = [], []
for _, row in df.iterrows():
    h = plt.Line2D(
        [], [], 
        marker=row["Marker"], linestyle="None",
        markersize=8,
        color=color_map[row["model"]],
        label=row["model"]
    )
    handles.append(h)
    labels.append(row["model"])

fig.legend(
    handles, labels,
    loc="upper center", ncol=5, frameon=False,
    bbox_to_anchor=(0.5, -0.02), fontsize=9
)
plt.tight_layout(rect=[0, 0.15, 1, 1])

# -------------------------
# Save
# -------------------------
plt.savefig(DEFAULT_OUT_PDF, format="pdf", bbox_inches="tight")
plt.savefig(DEFAULT_OUT_PNG, format="png", dpi=300, bbox_inches="tight")
plt.close()

print(f"Saved:\n  {DEFAULT_OUT_PDF}\n  {DEFAULT_OUT_PNG}")