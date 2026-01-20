import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import pandas as pd
from pathlib import Path

CUR_dir = Path(__file__).parent.resolve()
DEFAULT_INPUT = CUR_dir.parent / "finalresult.csv"
DEFAULT_OUT_PNG = CUR_dir / "Figure 3.png"
DEFAULT_OUT_PDF = CUR_dir / "Figure 3.pdf"
# --- Canonical order you want on the plots ---
categories = ["Data-Dep", "Dead-Code-S", "Dominators", "Func-Reach", "Liveness", "Dead-Code-L"]

# --- EXACT mapping: canonical name -> name in your CSV ---
NAME_MAP = {
    "GPT-4o Mini": "GPT-4o Mini",
    "GPT-3.5 Turbo": "GPT-3.5 Turbo",
    "GPT-5-Codex": "GPT-5-Codex",
    "GPT-5": "GPT-5",
    "DS-Coder V2-Lite": "DeepSeek-Coder V2-Lite-Instr",
    "DS-Coder 7B v1.5": "DeepSeek-Coder 7B-Instr v1.5",
    "DS-R1-Distill": "DeepSeek-R1-Distill-Qwen-7B",
    "CodeLlama-13B-Instr": "CodeLlama-13B-Instr",
    "CodeLlama-7B-Instr": "CodeLlama-7B-Instr",
    "Llama-3 8B-Instr": "Llama-3 8B-Instr",
    "Mistral 7B-Instr": "Mistral 7B-Instr (v0.3)",
    "Codestral 7B v0.1": "Mamba Codestral 7B (v0.1)",
    "Qwen2.5 14B Instr": "Qwen2.5-Coder 14B-Instr",
    "Qwen3 14B": "Qwen3 14B",
    "StarCoder 2 7B": "StarCoder 2 7B",
    "Phi-4 Reasoning": "Phi-4 Reasoning (14B)",
}
models = list(NAME_MAP.keys())

model_families = [
    ["GPT-4o Mini", "GPT-3.5 Turbo", "GPT-5-Codex", "GPT-5"],
    ["DS-Coder V2-Lite", "DS-Coder 7B v1.5", "DS-R1-Distill"],
    ["CodeLlama-13B-Instr", "CodeLlama-7B-Instr", "Llama-3 8B-Instr"],
    ["Mistral 7B-Instr", "Codestral 7B v0.1"],
    ["Qwen2.5 14B Instr", "Qwen3 14B"],
    ["StarCoder 2 7B"],
    ["Phi-4 Reasoning"]
]

# --- columns in your CSV ---
CSV_CATEGORY_COLS = ["DataDep_p1", "DeadCode_p1", "Dominators_p1", "FuncReach_p1", "Liveness_p1", "LoopReach_p1"]
CSV_OVERALL_COL = "All_geo_p1"

plt.rcParams.update({
    "font.size": 14,          # base font size
    "axes.titlesize": 18,     # subplot titles
    "axes.labelsize": 18,     # x/y labels
    "xtick.labelsize": 14,
    "ytick.labelsize": 14,
    "legend.fontsize": 20,
})

# ===== Read CSV =====
df = pd.read_csv(DEFAULT_INPUT)

# Validate required columns
required_cols = ["model", CSV_OVERALL_COL] + CSV_CATEGORY_COLS
missing_cols = [c for c in required_cols if c not in df.columns]
if missing_cols:
    raise AssertionError(f"Missing columns in CSV: {missing_cols}\nFound: {list(df.columns)}")

# Map canonical -> csv names for indexing, keep canonical for labels
mapped_models = [NAME_MAP[m] for m in models]

# Validate all mapped names exist in CSV
missing_rows = [mm for mm in mapped_models if mm not in set(df["model"])]
if missing_rows:
    raise AssertionError(f"Missing rows in CSV for mapped names: {missing_rows}")

# Build arrays in canonical order, using mapped CSV names
df_idx = df.set_index("model").reindex(mapped_models)

overall_acc = df_idx[CSV_OVERALL_COL].astype(float).to_numpy()
sub_acc = df_idx[CSV_CATEGORY_COLS].astype(float).to_numpy()

# Convert to percent if needed
if np.nanmax(overall_acc) <= 1.0:
    overall_acc *= 100.0
if np.nanmax(sub_acc) <= 1.0:
    sub_acc *= 100.0

# ===== Plot (same as your existing) =====
sort_idx = np.argsort(overall_acc)
models_sorted = [models[i] for i in sort_idx]
overall_acc_sorted = overall_acc[sort_idx]

colorscale = ["#d73027", "#fc8d59", "#fee08b", "#91cf60", "#1de4b3", "#4575b4", "#762a83", "#000000"]
cmap = LinearSegmentedColormap.from_list("warm_to_cold", colorscale)


colorscale = ["#d73027", "#fc8d59", "#fee08b", "#91cf60", "#1de4b3", "#4575b4", "#762a83", "#000000"]
colorscale_reversed = list(reversed(colorscale))
cmap = LinearSegmentedColormap.from_list("cold_to_warm", colorscale_reversed)

n_models = len(models)
norm = plt.Normalize(vmin=0, vmax=n_models - 1)
line_colors = [cmap(norm(i)) for i in range(n_models)]

fig, axes = plt.subplots(1, 3, figsize=(21, 7), gridspec_kw={"wspace": 0.25}, constrained_layout=False)
ax1, ax2, ax3 = axes


# (a) Overall by model
x_bar = np.arange(len(models_sorted))
bar_colors = [line_colors[rank] for rank, _ in enumerate(sort_idx)]
ax1.bar(x_bar, overall_acc_sorted, color=bar_colors, edgecolor="none")
ax1.set_ylabel("Accuracy (%)")
ax1.set_title("Accuracy of each model on SemBench")
ax1.set_ylim(0, 105)
ax1.set_yticks(np.arange(0, 101, 20))
ax1.grid(axis="y", alpha=0.25, linewidth=0.7)
ax1.set_xticks(x_bar)
ax1.set_xticklabels(models_sorted, rotation=45, ha="right")
ax1.text(-0.12, 1.05, "(a)", transform=ax1.transAxes, fontweight="bold", va="bottom")


# (b) Average by category
x_cat = np.arange(len(categories))
means = sub_acc.mean(axis=0)
sds = sub_acc.std(axis=0, ddof=0)
# Order categories by highest -> lowest overall accuracy
cat_order = np.argsort(-means)
categories_sorted = [categories[i] for i in cat_order]
means = means[cat_order]
sds = sds[cat_order]
sub_acc = sub_acc[:, cat_order]

#ax2.bar(x_cat, means, color="#DEA22C", edgecolor="none")
ax2.bar(
    x_cat,
    means,
    yerr=sds,
    color="#DEA22C",
    edgecolor="none",
    capsize=3,         # add little caps to error bars
    ecolor="gray",    # color for error bars
    linewidth= 0.8,
    alpha=0.9
)
ax2.set_ylabel("Accuracy (%)")
ax2.set_title("Average accuracy by category")
ax2.set_ylim(0, 105)
ax2.set_yticks(np.arange(0, 101, 20))
ax2.set_xticks(x_cat)
ax2.set_xticklabels(categories_sorted, rotation=45, ha="right")
ax2.grid(axis="y", alpha=0.25, linewidth=0.7)
for i, v in enumerate(means):
    ax2.text(i, v + 1.5, f"{v:.1f}", ha="center", va="bottom")
ax2.text(-0.12, 1.05, "(b)", transform=ax2.transAxes, fontweight="bold", va="bottom")


# (c) Per-category lines by model
# Find the best model from each model family

name_to_rank = {m: i for i, m in enumerate(models_sorted)}
family_best_rank = []
for fam in model_families:
    fam_rank = [name_to_rank[m] for m in fam]
    family_best_rank.append(max(fam_rank)) 
gpt_all_ranks = [
    name_to_rank[m]
    for fam in model_families
    if any(x.startswith("GPT") for x in fam)
    for m in fam if m.startswith("GPT")
]

family_best_rank = sorted(set(family_best_rank).union(gpt_all_ranks))
print(family_best_rank)
sub_acc_sorted = sub_acc[sort_idx]

for rank in sorted(family_best_rank):
    ax3.plot(
        x_cat, sub_acc_sorted[rank],
        marker="o",
        linewidth=1.8,
        markersize=4.5,
        color=line_colors[rank],
        label=models_sorted[rank],  # canonical labels on legend
        zorder=1
    )

means = sub_acc_sorted[family_best_rank].mean(axis=0)
sds = sub_acc_sorted[family_best_rank].std(axis=0, ddof=0)

ax3.set_xlim(x_cat[0] - 0.1, x_cat[-1] + 0.1)
ax3.set_xticks(x_cat)
ax3.set_xticklabels(categories_sorted, rotation=45, ha="right")
ax3.set_ylabel("Accuracy (%)")
ax3.set_title("Accuracy of the best model in each \n family across semantic categories")
ax3.set_ylim(0, 105)
ax3.set_yticks(np.arange(0, 101, 20))
ax3.grid(alpha=0.25, linewidth=0.7)

handles, labels = ax3.get_legend_handles_labels()
ax3.legend(handles[::-1], labels[::-1],
           loc="upper left", bbox_to_anchor=(1.02, 1.0),
           borderaxespad=0.0, ncol=1, frameon=False)
ax3.text(-0.12, 1.05, "(c)", transform=ax3.transAxes, fontweight="bold", va="bottom")

fig.tight_layout()
fig.savefig(DEFAULT_OUT_PDF, dpi=300, bbox_inches="tight")
fig.savefig(DEFAULT_OUT_PNG, dpi=300, bbox_inches="tight")