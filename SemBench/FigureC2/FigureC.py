"""
Draw grouped bar charts (raw accuracy) for:
(a) Qwen3 (top)
(b) StarCoder2 (bottom)
"""

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

cats = [
    "dead_code",
    "data_dependency",
    "function_reachability",
    "dominators",
    "loop_reachability",
    "liveness",
]
cats_pretty = ["Dead Code-S", "Data-Dep", "Func-Reach", "Dominators", "Dead Code-L", "Liveness", "Overall"]

qwen = {
    1.7: {"all": 42.07, "data_dependency": 51.77, "dead_code": 46.50, 
          "dominators": 31.48, "function_reachability": 30.92, 
          "liveness": 52.21, "loop_reachability": 45.34},
    8.0: {"all": 42.64, "data_dependency": 39.46, "dead_code": 56.60, 
          "dominators": 12.96, "function_reachability": 74.83, 
          "liveness": 47.38, "loop_reachability": 58.60},
    14.0: {"all": 48.48, "data_dependency": 54.56, "dead_code": 61.00, 
           "dominators": 51.90, "function_reachability": 58.40, 
           "liveness": 51.70, "loop_reachability": 24.89},
}


sc2 = {
    3.0: {"all": 5.23, "data_dependency": 6.56, "dead_code": 24.70, "dominators": 9.97,
          "function_reachability": 35.26, "liveness": 23.97, "loop_reachability": 14.50},
    7.0: {"all": 42.83, "data_dependency": 47.08, "dead_code": 61.85, "dominators": 41.78,
          "function_reachability": 36.08, "liveness": 43.26, "loop_reachability": 32.49},
    15.0: {"all": 49.19, "data_dependency": 27.61, "dead_code": 50.30, "dominators": 48.50,
           "function_reachability": 50.00, "liveness": 41.98, "loop_reachability": 51.25},
}



def size_label(family: str, sz: float) -> str:
    if float(sz).is_integer():
        return f"{family}-{int(sz)}B"
    return f"{family}-{sz}B"

def plot_grouped_subplot(ax, family_data, sizes_order, family_name, ylim=100):
    groups = cats + ["all"]
    n_groups = len(groups)
    n_sizes = len(sizes_order)

    x = np.arange(n_groups)
    width = 0.75 / n_sizes

    for i, sz in enumerate(sizes_order):
        vals = [family_data[sz][g] for g in groups]
        ax.bar(
            x + i * width - (n_sizes - 1) * width / 2,
            vals,
            width,
            label=size_label(family_name, sz),
        )

    ax.set_xticks(x)
    ax.set_xticklabels(cats_pretty, fontsize=13)
    ax.set_ylabel("Accuracy (%)", fontsize=15)
    ax.set_ylim(0, ylim)
    ax.grid(True, linewidth=0.5, alpha=0.6)
    ax.tick_params(axis="y", labelsize=13)

# ----------------------------
# Main: combined figure
# ----------------------------
def main():
    DEFAULT_OUT_PNG = Path(__file__).parent / "FigureC_scale.png"
    DEFAULT_OUT_PDF = Path(__file__).parent / "FigureC_scale.pdf"
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 9), sharex=True)

    # (a) Qwen3
    plot_grouped_subplot(ax1, qwen, [1.7, 8.0, 14.0], "Qwen3", ylim=100)
    ax1.text(0.01, 0.95, "(a) Qwen3", transform=ax1.transAxes,
             ha="left", va="top", fontsize=15, fontweight="bold")
    ax1.legend(ncol=4, fontsize=13, loc="lower center", bbox_to_anchor=(0.5, 1.02))

    # (b) StarCoder2
    plot_grouped_subplot(ax2, sc2, [3.0, 7.0, 15.0], "StarCoder2", ylim=100)
    ax2.text(0.01, 0.95, "(b) StarCoder2", transform=ax2.transAxes,
             ha="left", va="top", fontsize=15, fontweight="bold")
    ax2.set_xlabel("Semantic Categories", fontsize=15)
    ax2.legend(ncol=3, fontsize=13, loc="lower center", bbox_to_anchor=(0.5, -0.25))

    plt.tight_layout()
    plt.savefig(DEFAULT_OUT_PNG, dpi=300, bbox_inches="tight")
    plt.savefig(DEFAULT_OUT_PDF, dpi=300, bbox_inches="tight")

if __name__ == "__main__":
    main()
