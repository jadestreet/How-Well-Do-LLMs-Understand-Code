import os
import sys
import json
import argparse
from typing import List, Tuple, Dict
import openai
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
from script.util import parse_llm_response, construct_input_large, convert_tensors

# =========================
# Pricing & usage helpers
# =========================

# Rates are dollars per 1,000 tokens. 
PRICING_PER_1K = {
    "gpt-5": {
        "prompt": 0.00125,
        "prompt_cached": 0.000125,   
        "completion": 0.01000,
    },
    "gpt-5-mini": {
        "prompt": 0.00025,
        "prompt_cached": 0.000025,   
        "completion": 0.00200,
    },
    "gpt-5-nano": {
        "prompt": 0.00005,
        "prompt_cached": 0.00005,
        "completion": 0.00040,
    },
    "gpt-5-codex": {
        "prompt": 0.00125,
        "prompt_cached": 0.000125, 
        "completion": 0.01000,
    },
    "gpt-5-pro": {
        "prompt": 0.01500,
        "prompt_cached": 0.01500, 
        "completion": 0.12000,
    },
}

def _usage_as_dict(u):
    if u is None:
        return {}
    if isinstance(u, dict):
        return u
    # try pydantic v2 then dict()
    for attr in ("model_dump", "dict"):
        fn = getattr(u, attr, None)
        if callable(fn):
            try:
                return fn()
            except Exception:
                pass
    # shallow scrape fallback
    out = {}
    for k in ("input_tokens", "output_tokens", "prompt_tokens", "completion_tokens", "total_tokens"):
        if hasattr(u, k):
            out[k] = getattr(u, k)
    for k in ("input_tokens_details", "output_tokens_details", "completion_tokens_details"):
        if hasattr(u, k):
            out[k] = _usage_as_dict(getattr(u, k))
    return out

def _extract_usage(resp):
    """
    Normalize usage from Responses API or Chat Completions API.
    Returns: {"input": int, "cached_input": int, "output": int, "reasoning": int}
    """
    u = _usage_as_dict(getattr(resp, "usage", None))
    input_tok  = int(u.get("input_tokens")  or u.get("prompt_tokens") or 0)
    output_tok = int(u.get("output_tokens") or u.get("completion_tokens") or 0)

    in_det  = _usage_as_dict(u.get("input_tokens_details"))
    cached  = int(in_det.get("cached_tokens", 0) or 0)

    out_det = _usage_as_dict(u.get("output_tokens_details") or u.get("completion_tokens_details"))
    reason  = int(out_det.get("reasoning_tokens", 0) or 0)

    return {"input": input_tok, "cached_input": cached, "output": output_tok, "reasoning": reason}

def cost_from_usage(u, model_name):
    """
    USD cost using per-1K pricing with cached-input tier.
    u: {"input", "cached_input", "output", ...}
    """
    rates = PRICING_PER_1K.get(model_name) or PRICING_PER_1K["gpt-5"]
    fresh_in   = max(0, int(u.get("input", 0)) - int(u.get("cached_input", 0)))
    cached_in  = int(u.get("cached_input", 0))
    out_tok    = int(u.get("output", 0))
    return (fresh_in * rates["prompt"] + cached_in * rates["prompt_cached"] + out_tok * rates["completion"]) / 1000.0


def collect_code_files_from_csv(csv_path: str) -> Tuple[List[str], int]:
    """
    Reads a combined_summary/top_k CSV (like top_100_lowest_accuracy.csv)
    and returns:
        - a list of filenames with '.c' appended
        - the count of files

    Expected columns:
        program,gpt-3.5-turbo__overall_accuracy,...,worst_model
    """
    df = pd.read_csv(csv_path)
    if "program" not in df.columns:
        raise ValueError(f"{csv_path} must contain a 'program' column")

    filenames = [f"{p}.c" for p in df["program"].astype(str).tolist()]
    count = len(filenames)
    return filenames, count

# =========================
# Args & paths
# =========================

def parse_args():
    parser = argparse.ArgumentParser(
        description="Test LLM Code Semantic Understanding via OpenAI API"
    )
    parser.add_argument("--type_kernels", type=str, default="loop3_1000",
                        help="Type kernel directory name.")
    parser.add_argument("--model_name", type=str, default="gpt-5",
                        help="OpenAI model name (e.g., gpt-5, gpt-5-mini, gpt-5-codex)")
    parser.add_argument("--api_key", type=str, default="",
                        help="API key for accessing OpenAI API. If empty, uses OPENAI_API_KEY env var.")
    parser.add_argument("--use_background", action="store_true", default=True,
                        help="Include background information in the prompt.")
    parser.add_argument("--temperature", type=float, default=0.0,
                        help="Sampling temperature for chat models (ignored by GPT-5).")
    parser.add_argument("--num_samples", type=int, default=1,
                        help="Number of samples for self-consistency.")
    parser.add_argument("--batch_size", type=int, default=12,
                        help="Batch size for processing queries.")
    parser.add_argument("--max_workers", type=int, default=8,
                        help="Number of parallel worker threads.")
    parser.add_argument("--max_tokens", type=int, default=64,
                        help="Maximum tokens to generate per response (Responses API: max_output_tokens).")
    parser.add_argument("--seed", type=int, default=42,
                        help="Random seed for file selection.")
    parser.add_argument("--report_usage", action="store_true", default=False,
                        help="Collect and print per-program usage (input/fresh+cached/output/reasoning) and cost.")
    return parser.parse_args()

CONFIG = parse_args()
openai.api_key = CONFIG.api_key or os.getenv("OPENAI_API_KEY", "")

BASE_DIR         = os.path.join(os.getcwd(), "data")
TYPE_KERNELS     = CONFIG.type_kernels
CODE_DIR         = os.path.join(BASE_DIR, TYPE_KERNELS, "code")
QUERY_DIR        = os.path.join(BASE_DIR, TYPE_KERNELS, "queries")
GROUND_TRUTH_DIR = os.path.join(BASE_DIR, TYPE_KERNELS, "ground_truth")
RESULTS_DIR      = os.path.join(BASE_DIR, TYPE_KERNELS, "llm_results", CONFIG.model_name.replace("/", "_"))
os.makedirs(RESULTS_DIR, exist_ok=True)

print(f"Using model: {CONFIG.model_name}")
print(f"Code directory: {CODE_DIR}")
print(f"Query directory: {QUERY_DIR}")
print(f"Ground truth directory: {GROUND_TRUTH_DIR}")

# Select experiment set

selected_code_files = [
    os.path.join(CODE_DIR, f)
    for f in os.listdir(CODE_DIR)
    if os.path.isfile(os.path.join(CODE_DIR, f))
]
print(f"Loaded all {len(selected_code_files)} programs from {CODE_DIR}")



# =========================
# Model callers
# =========================

def get_model_response_GPT(prompt_text: str,
                            model: str = "gpt-4o-mini",
                            num_return_sequences: int = 1,
                            temperature: float = 0.0,
                            max_output_tokens: int = 512) -> Dict:
    out_texts: List[str] = []
    out_usages: List[Dict[str, int]] = []
    system_fingerprint = None

    def _extract_usage(resp):
        usage = getattr(resp, "usage", None)
        if usage:
            return {
                "input": getattr(usage, "input_tokens", 0)
                         or getattr(usage, "prompt_tokens", 0),
                "output": getattr(usage, "output_tokens", 0)
                         or getattr(usage, "completion_tokens", 0),
            }
        return {"input": 0, "output": 0}

    for _ in range(num_return_sequences):
        if model.lower() == "gpt-4o-mini":
            # --- Responses API ---
            r = openai.responses.create(
                model=model,
                input=prompt_text,
                temperature=temperature,
                max_output_tokens=max_output_tokens,
            )
            system_fingerprint = getattr(r, "system_fingerprint", None)
            out_usages.append(_extract_usage(r))
            text = getattr(r, "output_text", None)
            if not text:
                # fallback parse for structured output
                for item in (getattr(r, "output", []) or []):
                    if getattr(item, "type", "") == "message":
                        for c in (getattr(item, "content", []) or []):
                            if getattr(c, "type", "") == "output_text":
                                text = (c.text or "").strip()
                                break
                        if text:
                            break
            out_texts.append((text or "").strip())

        elif model.lower() == "gpt-3.5-turbo":
            # --- Chat Completions API ---
            r = openai.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt_text}],
                temperature=temperature,
                max_tokens=max_output_tokens,
                n=1,
            )
            system_fingerprint = getattr(r, "system_fingerprint", None)
            out_usages.append(_extract_usage(r))
            text = (r.choices[0].message.content or "").strip()
            out_texts.append(text)

        else:
            raise ValueError(f"Unsupported model: {model}")

    return {
        "generated_texts": out_texts,
        "usage_list": out_usages,
        "system_fingerprint": system_fingerprint,
    }

def get_model_response_GPT5(prompt_text: str, num_return_sequences: int = 1):
    out_texts: List[str] = []
    out_usages: List[Dict[str, int]] = []

    # --- STRICT: freeze the knobs you can control (keep them constant across runs) ---
    _request_kwargs = {
        "model": CONFIG.model_name,
        "input": prompt_text,
        "reasoning": {"effort": "low"},        # keep this fixed for all runs
    }

    system_fingerprint = None

    for _ in range(num_return_sequences):
        r = openai.responses.create(**_request_kwargs)

        # record system_fingerprint for reproducibility diagnostics
        system_fingerprint = getattr(r, "system_fingerprint", None)

        # usage
        try:
            out_usages.append(_extract_usage(r))
        except Exception:
            out_usages.append({"input": 0, "cached_input": 0, "output": 0, "reasoning": 0})

        # fast path
        text = getattr(r, "output_text", None)
        if text:
            out_texts.append(text.strip())
            continue

        # structured walk
        text = ""
        for item in getattr(r, "output", []) or []:
            if getattr(item, "type", "") == "message":
                for c in getattr(item, "content", []) or []:
                    if getattr(c, "type", "") == "output_text":
                        text = (c.text or "").strip()
                        break
            if text:
                break

        # rare fallback
        if not text and hasattr(r, "choices"):
            try:
                text = (r.choices[0].message["content"] or "").strip()
            except Exception:
                pass

        if not text:
            # Preserve full object for debugging
            raise RuntimeError(f"No text in response. Full object:\n{r.model_dump_json(indent=2)}")

        out_texts.append(text)

    return {
        "generated_texts": out_texts,
        "usage_list": out_usages,
        "system_fingerprint": system_fingerprint,  # <— added
    }


# =========================
# Pipeline
# =========================

def process_query(program_name, category, prompt_text, ground_truth):
    result = {
        "program": program_name,
        "category": category,
        "prompt": prompt_text,
        "ground_truth": ground_truth,
        "conversation": [],
        "first_response_correct": None,
        "_usage_list": [],  # capture real usage here
    }

    code_file = os.path.join(CODE_DIR, program_name + ".c")
    input_text = construct_input_large(code_file, prompt_text, category)
    if CONFIG.model_name.startswith("gpt-5"):
        initial_output = get_model_response_GPT5(
            input_text,
            num_return_sequences=1
        )
    else:
        print("using gpt-4o-mini or gpt-3.5-turbo")
        initial_output = get_model_response_GPT(
            input_text,
            model=CONFIG.model_name,
            num_return_sequences=1,
            temperature=CONFIG.temperature,
            max_output_tokens=CONFIG.max_tokens
        )

    # usage
    result["_usage_list"].extend(initial_output.get("usage_list", []))

    # parse
    decisions = [parse_llm_response(text) for text in initial_output["generated_texts"]][0]
    result["conversation"].append({
        "role": "initial_response",
        "response": {"generated_texts": initial_output["generated_texts"]},
        "parsed_decisions": decisions
    })
    result["first_response_correct"] = (decisions == ground_truth) if decisions is not None else None

    final_decision = decisions
    result.update({
        "final_answer": "yes" if final_decision else "no",
        "correct": (final_decision == ground_truth)
    })
    return result


def process_program(program_name):
    """
    Process all queries for a single program, returning a list of result dicts.
    """
    results = []
    query_file = os.path.join(QUERY_DIR, program_name + ".json")
    gt_file    = os.path.join(GROUND_TRUTH_DIR, program_name + ".json")
    try:
        with open(query_file) as qf:
            queries = json.load(qf)
        with open(gt_file) as gf:
            truths = json.load(gf)
    except Exception as e:
        print(f"Error loading queries for {program_name}: {e}", file=sys.stderr)
        return results
    for category, prompts in queries.items():
        if category != "dead_code":
            gts = truths.get(category, [])
            for i in range(0, len(prompts), CONFIG.batch_size):
                batch = prompts[i:i+CONFIG.batch_size]
                batch_truths = gts[i:i+CONFIG.batch_size]
                for pt, gt in zip(batch, batch_truths):
                    try:
                        res = process_query(program_name, category, pt, gt)
                        results.append(res)
                    except Exception as e:
                        print(f"Error in {program_name}/{category}: {e}", file=sys.stderr)
    return results


def main():
    programs = [os.path.splitext(os.path.basename(f))[0] for f in selected_code_files]
    if CONFIG.file:
        print(f"Running {len(programs)} programs from specified file {CONFIG.file}.")
    else:
        print(f"Running {len(programs)} selected programs.")

    all_results = []
    per_prog_usage: Dict[str, Dict[str, int]] = {}

    def _accumulate_usage(prog, usage_list):
        if not CONFIG.report_usage:
            return
        agg = per_prog_usage.setdefault(prog, {"input": 0, "cached_input": 0, "output": 0, "reasoning": 0})
        for u in usage_list:
            agg["input"]        += int(u.get("input", 0))
            agg["cached_input"] += int(u.get("cached_input", 0))
            agg["output"]       += int(u.get("output", 0))
            agg["reasoning"]    += int(u.get("reasoning", 0))

    with ThreadPoolExecutor(max_workers=CONFIG.max_workers) as executor:
        futures = {executor.submit(process_program, p): p for p in programs}
        for fut in as_completed(futures):
            prog = futures[fut]
            try:
                prog_res = fut.result()
                all_results.extend(prog_res)
                if CONFIG.report_usage:
                    blobs = []
                    for r in prog_res:
                        blobs.extend(r.get("_usage_list", []))
                    _accumulate_usage(prog, blobs)
            except Exception as e:
                print(f"Error processing program {prog}: {e}", file=sys.stderr)

    # Usage & cost report
    if CONFIG.report_usage and per_prog_usage:
        print("\n===== Per-Program Usage & Cost =====")
        grand_in = grand_cached = grand_out = grand_reason = 0
        grand_cost = 0.0
        for prog, u in sorted(per_prog_usage.items()):
            fresh_in = max(0, u["input"] - u["cached_input"])
            cost = cost_from_usage(u, CONFIG.model_name)
            grand_in     += u["input"]
            grand_cached += u["cached_input"]
            grand_out    += u["output"]
            grand_reason += u["reasoning"]
            grand_cost   += cost
            print(f"{prog:30s}  in={u['input']:6d} (fresh={fresh_in:6d}, cached={u['cached_input']:6d})"
                  f"  out={u['output']:6d}  reason={u['reasoning']:6d}  cost=${cost:.6f}")
        print("====================================")
        fresh_total = max(0, grand_in - grand_cached)
        print(f"TOTAL{'':26s}  in={grand_in:6d} (fresh={fresh_total:6d}, cached={grand_cached:6d})"
              f"  out={grand_out:6d}  reason={grand_reason:6d}  cost=${grand_cost:.6f}")

    # Persist results
    file_name = f"{CONFIG.model_name.replace('/', '_')}.jsonl"
    results_path = os.path.join(RESULTS_DIR, file_name)
    out = convert_tensors(all_results)
    with open(results_path, 'w', encoding='utf-8') as wf:
        for record in out:
            json_line = json.dumps(record, ensure_ascii=False)
            wf.write(json_line + '\n')
    print(f"Results saved to {results_path}")


if __name__ == "__main__":
    if not openai.api_key:
        print("ERROR: OpenAI API key not provided. Set --api_key or OPENAI_API_KEY env var.", file=sys.stderr)
        sys.exit(1)
    main()
