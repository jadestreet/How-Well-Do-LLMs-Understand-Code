import os
os.environ["PYTORCH_HIP_ALLOC_CONF"] = "expandable_segments:True"
os.environ["TRANSFORMERS_NO_CUDA_CACHE_WARMUP"] = "1"
os.environ["TRANSFORMERS_TRUST_REMOTE_CODE"] = "true"

import transformers.dynamic_module_utils as _dmu
_dmu.check_imports = lambda *a, **k: []
from transformers.generation.utils import DynamicCache
if not hasattr(DynamicCache, "get_max_length"):
    DynamicCache.get_max_length = DynamicCache.get_max_cache_shape

    
import json
import argparse
import torch
import torch.distributed as dist
import transformers.modeling_utils as mu
mu.caching_allocator_warmup = lambda *args, **kwargs: None
from transformers import AutoTokenizer, AutoModelForCausalLM, StoppingCriteriaList, StoppingCriteria
from script.util import parse_llm_response, construct_input_large

# ---------------- Distributed Setup ----------------
def setup_distributed():
    dist.init_process_group(backend="nccl")
    local_rank = int(os.environ.get("LOCAL_RANK", 0))
    world_size = dist.get_world_size()
    torch.cuda.set_device(local_rank)
    return local_rank, world_size

# ------------------ Stopping Criteria ------------------
class StopOnToken(StoppingCriteria):
    def __init__(self, stop_id: int):
        super().__init__()
        self.stop_id = stop_id

    def __call__(self, input_ids, scores, **kwargs):
        return input_ids[0, -1].item() == self.stop_id

# ------------------ Inference Wrapper ------------------
def get_llm_agent_response(prompts, llm_agent, stops, max_tokens, temperature, num_return_sequences):
    outputs = llm_agent(
        prompts,
        max_new_tokens=max_tokens,
        do_sample=False,
        temperature=temperature,
        num_return_sequences=num_return_sequences,
        stopping_criteria=stops
    )
    if isinstance(outputs, list):
        return {"generated_texts": [out["generated_text"] for out in outputs]}
    else:
        return {"generated_texts": outputs["generated_texts"]}

# ------------------ Core Query Processing ------------------
def process_query(program_name, category, prompt_text, ground_truth, llm_agent, stops, CONFIG):
    # Inform start of processing
    print(f"Sending initial prompt for program '{program_name}', category '{category}'")

    result = {
        "program": program_name,
        "category": category,
        "prompt": prompt_text,
        "ground_truth": ground_truth,
        "conversation": [],
        "first_response_correct": None,
        "correct_after_followup": None
    }
    code_file = os.path.join(CONFIG.base_dir, CONFIG.type_kernels, "code", program_name + ".c")
    input_text = construct_input_large(code_file, prompt_text, category)

    num_samples = CONFIG.num_samples if CONFIG.use_self_consistency else 1
    initial = get_llm_agent_response(
        input_text,
        llm_agent,
        stops,
        CONFIG.max_tokens,
        CONFIG.temperature if CONFIG.do_dynamic_temperature else 1.0,
        num_samples
    )
    decisions = [parse_llm_response(text) for text in initial["generated_texts"]][0]
    result["conversation"].append({
        "role": "initial_response",
        "response": initial,
        "parsed_decisions": decisions,
    })
    current = decisions
    result["first_response_correct"] = (decisions == ground_truth) if decisions is not None else None

    final_decision = current
    result.update({
        "final_answer": "yes" if final_decision else "no",
        "correct": final_decision == ground_truth
    })
    return result

# ------------------ Main ------------------
def main():
    local_rank, world_size = setup_distributed()

    with open("config.json", "r") as f:
        CONFIG_JSON = json.load(f)

    parser = argparse.ArgumentParser()
    parser.add_argument("--model_name", type=str, default="mistralai/Mistral-7B-Instruct-v0.3")
    parser.add_argument("--batch_size", type=int, default=24)
    parser.add_argument("--max_tokens", type=int, default=64)
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--num_samples", type=int, default=1)
    parser.add_argument("--use_self_consistency", action="store_true", default=False)
    parser.add_argument("--do_dynamic_temperature", action="store_true", default=True,
                    help="Enable dynamic temperature sampling.")   
    parser.add_argument("--base_dir", type=str, default= os.path.join(os.getcwd(), "data"))
    parser.add_argument("--type_kernels", type=str, default=CONFIG_JSON.get("type_kernels", "default_kernels"))
    CONFIG = parser.parse_args()

    def llm_agent(prompts, max_new_tokens, do_sample, temperature, num_return_sequences, stopping_criteria):
        # 1) batch‐tokenize and move to GPU
        inputs = tokenizer(
            prompts,
            return_tensors="pt",
            padding=True,
            truncation=True,
        ).to(device)
        prompt_len = inputs["input_ids"].shape[1]
        # 2) generate under no_grad
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                do_sample=do_sample,
                temperature=temperature,
                num_return_sequences=num_return_sequences,
                stopping_criteria=stopping_criteria,
                #return_full_text=False,
            )
            new_tokens = outputs[:, prompt_len:]
        
        try:
            torch.cuda.empty_cache()
        except RuntimeError:
            pass
        # 3) decode to text
        texts = tokenizer.batch_decode(new_tokens, skip_special_tokens=True)
        return [{"generated_text": t} for t in texts]  
    
    QUERY_DIR = os.path.join(CONFIG.base_dir, CONFIG.type_kernels, "queries")
    GROUND_TRUTH_DIR = os.path.join(CONFIG.base_dir, CONFIG.type_kernels, "ground_truth")
    tasks = []
    for fname in sorted(os.listdir(QUERY_DIR)):#[:FILE_COUNT]
        if not fname.endswith(".json"): continue
        program = fname[:-5]
        with open(os.path.join(QUERY_DIR, fname)) as fq, open(os.path.join(GROUND_TRUTH_DIR, fname)) as fg:
            queries = json.load(fq)
            truths = json.load(fg)
        for cat, prompts in queries.items():
            if cat == "dead_code":
                continue
            else:
                for pt, gt in zip(prompts, truths.get(cat, [])):
                    tasks.append((program, cat, pt, gt))
    tasks = tasks[local_rank::world_size]    
    
    tokenizer = AutoTokenizer.from_pretrained(CONFIG.model_name, use_fast=True, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(
        CONFIG.model_name,
        torch_dtype=torch.float16,
        low_cpu_mem_usage=True,
        device_map={"": local_rank},
        trust_remote_code=True,
        #attn_implementation="sdpa",
    )
    if CONFIG.model_name.startswith("Qwen/Qwen3") and hasattr(model.generation_config, "enable_thinking"):
        print("turn off thinking mode for Qwen/Qwen3")
        model.generation_config.enable_thinking = False
    if tokenizer.pad_token_id is None:
        tokenizer.add_special_tokens({"pad_token": "[PAD]"})
        model.resize_token_embeddings(len(tokenizer))
    model.generation_config.pad_token_id = tokenizer.pad_token_id
    model = torch.compile(model, mode="max-autotune")

    stop_id = tokenizer.convert_tokens_to_ids("<END>")
    stops = StoppingCriteriaList([StopOnToken(stop_id)])
    device = local_rank
    model.to(device)
    model.eval()
    
    RESULTS_DIR = os.path.join(CONFIG.base_dir, CONFIG.type_kernels, "llm_results", "ablation", CONFIG.model_name.replace("/", "_"))
    os.makedirs(RESULTS_DIR, exist_ok=True)
    out_path = os.path.join(RESULTS_DIR, f"rank{local_rank}_results.jsonl")

    with open(out_path, "w", encoding="utf-8") as fout:
        for program, category, prompt_text, ground_truth in tasks:
            try:
                res = process_query(
                    program, category, prompt_text, ground_truth,
                    llm_agent, stops, CONFIG
                )
            except Exception as e:
                error_record = {
                    "program": program,
                    "category": category,
                    "prompt": prompt_text,
                    "error": repr(e),
                }
                fout.write(json.dumps(error_record, ensure_ascii=False) + "\n")
                fout.flush()
                print(f"Error on {program}/{category}: {e!r}")
                continue

            fout.write(json.dumps(res, ensure_ascii=False) + "\n")
            fout.flush()

            try:
                torch.cuda.empty_cache()
            except RuntimeError:
                pass

    print(f"Done! Results streaming to {out_path}")
    
if __name__ == "__main__":
    main()