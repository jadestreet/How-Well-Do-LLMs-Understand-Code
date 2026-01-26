
import argparse
import pandas as pd
from pathlib import Path
from scipy.stats import spearmanr, kendalltau
import os
CATEGORIES = [
    "All_geo",
    "DataDep",
    "DeadCode",
    "Dominators",
    "FuncReach",
    "Liveness",
    "LoopReach",
]
def corr(x, y):
    """Return (spearman_rho, spearman_p)."""
    rho, p_rho = spearmanr(x, y)
    return rho, p_rho

def main(input_file, output_file):
    df = pd.read_csv(input_file)

    postfix =  "_p1"
    results = []
    post_fix_specific = "_p1"
    for cat in CATEGORIES:
        col = f"{cat}{postfix}"
        if col not in df.columns:
            raise ValueError(f"Missing column {col} in CSV")

        # drop rows with NaN in either benchmark
        for bench, bench_col in [("HumanEval", f"HumanEval{post_fix_specific}"), ("MBPP", f"MBPP{post_fix_specific}")]:
            sub = df[[col, bench_col]].dropna()
            if len(sub) < 3:
                print(f"[WARN] Too few models with both {col} and {bench_col} (n={len(sub)})")
                continue
            rho, p_rho= corr(sub[col], sub[bench_col])
            results.append(dict(
                Category=cat.replace("SemBench_", ""),
                Metric=postfix.strip("_"),
                Benchmark=bench,
                Spearman_rho=rho,
                Spearman_p=p_rho,
                N=len(sub),
            ))

    out_df = pd.DataFrame(results)
    out_df.sort_values(["Benchmark", "Category"], inplace=True)
    if output_file:
        out_df.to_csv(output_file, index=False)
        print(f"Saved results to {output_file}")
    print(out_df.to_string(index=False))

if __name__ == "__main__":
    # --- Use argparse with current dir defaults ---
    current_dir = os.getcwd()
    parser = argparse.ArgumentParser(description="Compute correlation for SemBench results.")
    parser.add_argument(
        "--input_file",
        type=str,
        default=os.path.join(current_dir, "finalresult.csv"),
        help="Input CSV file"
    )
    #
    parser.add_argument(
        "--output_file",
        type=str,
        default=os.path.join(current_dir, "corr_updated.csv"),
        help="Output CSV file (default: ./corr_updated.csv)"
    )

    args = parser.parse_args()
    main(args.input_file, args.output_file)
