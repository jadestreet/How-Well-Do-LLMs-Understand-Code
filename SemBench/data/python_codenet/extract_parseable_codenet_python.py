import ast
import argparse
import shutil
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Copy parseable Python CodeNet files into SemBench.")
    parser.add_argument(
        "--src-root",
        type=Path,
        default=REPO_ROOT / "SemBench" / "data" / "python" / "codenet_python" / "Project_CodeNet_Python800",
        help="Root directory containing raw CodeNet Python files.",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=REPO_ROOT / "SemBench" / "data" / "python_codenet" / "code",
        help="Destination directory for copied parseable files.",
    )
    parser.add_argument("--limit", type=int, default=10000, help="Maximum number of files to copy.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    count = 0
    for p in sorted(args.src_root.rglob("*")):
        if not p.is_file():
            continue
        try:
            text = p.read_text(encoding="utf-8", errors="replace")
            ast.parse(text)
        except Exception:
            continue

        # Avoid copying metadata/readme-like files.
        if len(text.strip().splitlines()) < 10:
            continue

        name_parts = p.parts[-2:] if len(p.parts) >= 3 else p.parts
        out_name = "_".join(name_parts).replace("/", "_")
        if not out_name.endswith(".py"):
            out_name += ".py"

        shutil.copyfile(p, args.out_dir / out_name)
        count += 1
        if count >= args.limit:
            break

    print(f"Copied {count} parseable Python files to {args.out_dir}")


if __name__ == "__main__":
    main()
