
import argparse
from pathlib import Path
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.collections import LineCollection
from matplotlib import colormaps as cmaps   # Matplotlib >=3.7
import matplotlib.colors as mcolors

# ------------------------- setting -------------------------
CUR_dir = Path(__file__).parent.resolve()
DEFAULT_INPUT = CUR_dir.parent / "finalresult.csv"
DEFAULT_OUT_PNG = CUR_dir / "Figure 1.png"
DEFAULT_OUT_PDF = CUR_dir / "Figure 1.pdf"


TARGET_MODELS = [
    "DeepSeek-Coder V2-Lite-Instr",
    "DeepSeek-Coder 7B-Instr v1.5",
    "CodeLlama-7B-Instr",
    "CodeLlama-13B-Instr",
    "Llama-3 8B-Instr",
    "Mamba Codestral 7B (v0.1)",
    "StarCoder 2 7B",
    "Qwen2.5-Coder 14B-Instr",
    "GPT-3.5 Turbo",
    "GPT-4o Mini",
    "GPT-5",
]


SIZE_MAP = {
    "DeepSeek-Coder V2-Lite-Instr": 16,
    "DeepSeek-Coder 7B-Instr v1.5": 7.15,
    "CodeLlama-7B-Instr": 6.95,
    "CodeLlama-13B-Instr": 13,
    "Llama-3 8B-Instr": 8,
    "Mamba Codestral 7B (v0.1)": 7.05,
    "StarCoder 2 7B": 6.85,
    "Qwen2.5-Coder 14B-Instr": 14,
    "GPT-3.5 Turbo": 19.6,
    "GPT-4o Mini": 19.8,
    "GPT-5": 20,
}


TICK_POSITIONS = [7, 8, 13, 14, 16, 20]
TICK_LABELS = ["7B", "8B", "13B", "14B", "16B", "closed source"]


def read_and_prepare(path_csv: Path) -> pd.DataFrame:
    if not path_csv.exists():
        print(f"[ERROR] CSV not found: {path_csv.resolve()}", file=sys.stderr)
        sys.exit(1)

    df = pd.read_csv(path_csv)


    need_cols = {"model", "family", "All_geo_p1", "HumanEval_p1"}
    missing = need_cols - set(df.columns)
    if missing:
        print(f"[ERROR] Missing columns in CSV: {sorted(missing)}", file=sys.stderr)
        sys.exit(1)


    filtered = df[df["model"].isin(TARGET_MODELS)].dropna(subset=["All_geo_p1", "HumanEval_p1"])


    filtered = filtered[["family", "model", "All_geo_p1", "HumanEval_p1"]].rename(
        columns={
            "family": "Family",
            "model": "Model",
            "All_geo_p1": "SemBench",
            "HumanEval_p1": "HumanEval",
        }
    )


    filtered["SizeB"] = filtered["Model"].map(SIZE_MAP)


    for c in ["SemBench", "HumanEval", "SizeB"]:
        filtered[c] = pd.to_numeric(filtered[c], errors="coerce")
    filtered = filtered.dropna(subset=["SemBench", "HumanEval", "SizeB"]).reset_index(drop=True)


    found = set(filtered["Model"])
    missing_models = [m for m in TARGET_MODELS if m not in found]
    if missing_models:
        print(f"[WARN] Missing in filtered data (not found or NaN): {missing_models}")

    return filtered


# ------------------------- helper -------------------------
def logsize_fit(x_sizeB, y_vals):

    x = np.asarray(x_sizeB, dtype=float)
    y = np.asarray(y_vals, dtype=float)
    m = np.isfinite(x) & np.isfinite(y) & (x > 0)
    x, y = x[m], y[m]
    if len(x) < 3:
        return None
    b1, b0 = np.polyfit(np.log(x), y, 1)  # slope, intercept
    return b1, b0


def gradient_line_by_y(ax, xs, ys, cmap, norm_y, lw=2.8, alpha=0.95, zorder=3):

    xs = np.asarray(xs, float)
    ys = np.asarray(ys, float)
    pts = np.array([xs, ys]).T.reshape(-1, 1, 2)
    segs = np.concatenate([pts[:-1], pts[1:]], axis=1)
    y_mid = 0.5 * (ys[:-1] + ys[1:])
    lc = LineCollection(segs, colors=cmap(norm_y(y_mid)),
                        linewidths=lw, alpha=alpha, zorder=zorder)
    ax.add_collection(lc)


def draw_gradient_spine_y(ax, side="left", cmap=None, norm_y=None, lw=3.0):

    xmin, xmax = ax.get_xlim()
    ymin, ymax = ax.get_ylim()
    x_const = xmin if side == "left" else xmax
    ys = np.linspace(ymin, ymax, 600)
    xs = np.full_like(ys, x_const, dtype=float)
    gradient_line_by_y(ax, xs, ys, cmap=cmap, norm_y=norm_y, lw=lw, alpha=1.0, zorder=10)
    ax.spines[side].set_visible(False)  


# ------------------------- Main Process -------------------------
def main():
    parser = argparse.ArgumentParser(description="SemBench vs HumanEval dual-axis plot with gradient axes/lines.")
    parser.add_argument("-i", "--input", default=DEFAULT_INPUT, help="Path to sembench CSV (default: sembench_updated3.csv)")
    parser.add_argument("--png", default=DEFAULT_OUT_PNG, help="Output PNG filename")
    parser.add_argument("--pdf", default=DEFAULT_OUT_PDF, help="Output PDF filename")
    args = parser.parse_args()

    dfp = read_and_prepare(Path(args.input))


    cmap_left = cmaps.get_cmap("autumn")   # red -> yellow
    cmap_right = cmaps.get_cmap("BuPu")    # blue -> purple
    norm_y = mcolors.Normalize(0, 100)     


    markers = ["o", "s", "^", "D", "P", "X", "*", "v", ">", "<"]
    model_list = dfp["Model"].tolist()
    model_to_marker = {m: markers[i % len(markers)] for i, m in enumerate(model_list)}

 
    fig, ax_left = plt.subplots(figsize=(9.6, 5.4), dpi=160)
    ax_right = ax_left.twinx()


    pair_gray = "0.55"
    for _, r in dfp.iterrows():
        ax_left.plot([r["SizeB"], r["SizeB"]],
                     [r["SemBench"], r["HumanEval"]],
                     color=pair_gray, alpha=0.35, linewidth=1.1, zorder=1)

    for _, r in dfp.iterrows():
        x = r["SizeB"]; mk = model_to_marker[r["Model"]]
        c_sem = cmap_left(norm_y(r["SemBench"]))
        c_he = cmap_right(norm_y(r["HumanEval"]))
        ax_left.scatter([x], [r["SemBench"]], s=84, marker=mk,
                        facecolors=c_sem, edgecolors=c_sem, linewidths=1.0, zorder=4)
        ax_right.scatter([x], [r["HumanEval"]], s=92, marker=mk,
                         facecolors=c_he, edgecolors=c_he, linewidths=1.6, zorder=4)


    def plot_grad_trend(ax, x_sizeB, y_vals, cmap):
        fit = logsize_fit(x_sizeB, y_vals)
        if fit is None:
            return
        b1, b0 = fit
        xs = np.linspace(np.nanmin(x_sizeB), np.nanmax(x_sizeB), 400)
        ys = b1 * np.log(xs) + b0
        gradient_line_by_y(ax, xs, ys, cmap=cmap, norm_y=norm_y, lw=2.8, alpha=0.95, zorder=3)

    plot_grad_trend(ax_left, dfp["SizeB"], dfp["SemBench"], cmap_left)
    plot_grad_trend(ax_right, dfp["SizeB"], dfp["HumanEval"], cmap_right)

    ax_left.set_xlim(min(TICK_POSITIONS) - 0.8, max(TICK_POSITIONS) + 0.8)
    ax_left.set_xticks(TICK_POSITIONS)
    ax_left.set_xticklabels(TICK_LABELS)

    ax_left.set_ylim(0, 100)
    ax_right.set_ylim(0, 100)

    ax_left.set_xlabel("Model size")
    ax_left.set_ylabel("SemBench Geomean (%)")
    ax_right.set_ylabel("HumanEval Pass@1 (%)")


    ax_left.grid(True, linewidth=0.35, alpha=0.35)


    draw_gradient_spine_y(ax_left, side="left", cmap=cmap_left, norm_y=norm_y, lw=3.0)
    draw_gradient_spine_y(ax_right, side="right", cmap=cmap_right, norm_y=norm_y, lw=3.0)

    '''
    legend_items = [
        Line2D([0], [0], color=pair_gray, linestyle="-", linewidth=1.1, label="Pair link"),
        Line2D([0], [0], color="black", linewidth=2.2, label="SemBench trend (log-size)"),
        Line2D([0], [0], color="black", linewidth=2.2, label="HumanEval trend (log-size)"),
        Line2D([0], [0], marker="o", linestyle="None", markersize=7,
               markerfacecolor="grey", markeredgecolor="grey",
               label="SemBench point (y-colored)"),
        Line2D([0], [0], marker="o", linestyle="None", markersize=7,
               markerfacecolor="white", markeredgecolor="grey",
               label="HumanEval point (y-colored edge)"),
    ]
    for m in model_list:
        legend_items.append(
            Line2D([0], [0], marker=model_to_marker[m], linestyle="None",
                   markersize=7, markerfacecolor="white", markeredgecolor="0.25", label=m)
        )
    ax_left.legend(handles=legend_items, frameon=False, fontsize=9, ncol=2, loc="lower right")
    '''
    # ---- Legend (colored) ----
    sem_mid = cmap_left(norm_y(50))
    he_mid  = cmap_right(norm_y(50))

    model_face_edge = {
        r["Model"]: (
            cmap_left(norm_y(r["SemBench"])),
            cmap_right(norm_y(r["HumanEval"]))
        )
        for _, r in dfp.iterrows()
    }

    legend_items = [
        Line2D([0], [0], color=pair_gray, linestyle="-", linewidth=1.1, label="Pair link"),
        Line2D([0], [0], color=sem_mid, linewidth=2.2, label="SemBench line and data point"),
        Line2D([0], [0], color=he_mid,  linewidth=2.2, label="HumanEval line and data point"),

    ]
    
    for m in model_list:
        mk = model_to_marker[m]
        fcol, ecol = model_face_edge[m]
        legend_items.append(
            Line2D([0], [0],
                marker=mk, linestyle="None", markersize=7, label=m) #markerfacecolor=fcol, markeredgecolor=ecol,
        )

    ax_left.legend(handles=legend_items, frameon=False, fontsize=9, ncol=2, loc="lower right")

    fig.tight_layout()
    fig.savefig(args.png, dpi=300, bbox_inches="tight")
    fig.savefig(args.pdf, bbox_inches="tight")
    print(f"[OK] Saved: {args.png}  and  {args.pdf}")


if __name__ == "__main__":
    main()