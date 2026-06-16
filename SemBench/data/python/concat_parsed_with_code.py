#!/usr/bin/env python3
import argparse
import json
from pathlib import Path


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def read_code_for_program(program_name: str, code_dir: Path) -> str:
    """
    Prefer .py because this is the Python workflow.
    Fall back to .c only because the request mentioned .c once.
    """
    candidates = [
        code_dir / f"{program_name}.py",
        code_dir / f"{program_name}.c",
    ]

    for path in candidates:
        if path.exists():
            return path.read_text(encoding="utf-8", errors="replace")

    raise FileNotFoundError(
        f"No source file found for program '{program_name}' under {code_dir}. "
        f"Tried: {', '.join(str(p) for p in candidates)}"
    )


def main():
    parser = argparse.ArgumentParser(
        description="Concatenate parsed semantic JSON files with their source code into one JSONL file."
    )
    parser.add_argument(
        "--parsed-dir",
        default="SemBench/data/python/parsed_code",
        help="Directory containing parsed .json files.",
    )
    parser.add_argument(
        "--code-dir",
        default="SemBench/data/python/code",
        help="Directory containing source .py files.",
    )
    parser.add_argument(
        "--output",
        default="SemBench/data/python/python30_concatenated.jsonl",
        help="Output JSONL path.",
    )
    parser.add_argument(
        "--skip-missing-code",
        action="store_true",
        help="Skip parsed JSON files if the matching source file is missing.",
    )
    args = parser.parse_args()

    parsed_dir = Path(args.parsed_dir)
    code_dir = Path(args.code_dir)
    output_path = Path(args.output)

    if not parsed_dir.is_dir():
        raise SystemExit(f"ERROR: parsed-dir does not exist: {parsed_dir}")
    if not code_dir.is_dir():
        raise SystemExit(f"ERROR: code-dir does not exist: {code_dir}")

    output_path.parent.mkdir(parents=True, exist_ok=True)

    json_files = sorted(parsed_dir.glob("*.json"), key=lambda p: p.stem)

    written = 0
    skipped = 0

    with output_path.open("w", encoding="utf-8") as out_f:
        for json_path in json_files:
            program_name = json_path.stem

            try:
                parsed_info = load_json(json_path)
                code = read_code_for_program(program_name, code_dir)
            except FileNotFoundError as e:
                if args.skip_missing_code:
                    print(f"[SKIP] {program_name}: {e}")
                    skipped += 1
                    continue
                raise
            except json.JSONDecodeError as e:
                raise SystemExit(f"ERROR: failed to parse JSON file {json_path}: {e}")

            if not isinstance(parsed_info, dict):
                raise SystemExit(f"ERROR: expected JSON object in {json_path}, got {type(parsed_info)}")

            merged_info = dict(parsed_info)
            merged_info["code"] = code

            wrapped = {
                program_name: merged_info
            }

            out_f.write(json.dumps(wrapped, ensure_ascii=False) + "\n")
            written += 1

    print(f"Done. Wrote {written} records to {output_path}")
    if skipped:
        print(f"Skipped {skipped} records due to missing source code.")


if __name__ == "__main__":
    main()

'''
python SemBench/data/python/concat_parsed_with_code.py
'''