# SemBench: How Well Do LLMs Understand Code
This repository includes the data and script of this project. After downloading the repository and setting up the environment, enter this directory by ```cd How_Well_Do_LLMs_Understand_Code```.
## SemBench
This folder contains files for question generation, the evaluation stage, and figure plotting scripts.
To view and execute the script, enter this directory by ```cd SemBench```.
### main script 1: parser.py
The script performs **static semantic analysis** on a directory of C source files and emits a **JSON report per file**. It uses **Clang/LLVM** when available (for reliable AST, loop analysis, dominator tree, dead code).

**Quick Start**

```bash
python parse_semantic_features.py \
  --clang-bin clang \
  --opt-bin opt \
  --libclang-so $CONDA_PREFIX/lib/libclang.so.17 \
  --code-dir ./data/loop3_1000/code \
  --output-dir ./data/loop3_1000/parsed_code
```

After it finishes, JSON files appear in `--output-dir` (default: `./data/loop3_1000/parsed_code`).

**Arguments**

| Flag | Description | Default |
|------|-------------|---------|
| `--clang-bin` | Path or command for Clang. Used for preprocessing and static analyzer. | `clang` |
| `--opt-bin` | Path or command for LLVM `opt`. Used to query SCEV and Dominator Tree. | `opt` |
| `--libclang-so` | Full path to `libclang.so`. | `$CONDA_PREFIX/lib/libclang.so.17` |
| `--code-dir` | Directory with input `.c` files. | `./data/loop3_1000/code` |
| `--output-dir` | Destination directory for per-file JSON outputs. | `./data/loop3_1000/parsed_code` |

### main script 2: query.py
**Purpose**
Automatically generates **SemBench question–answer pairs** from parsed C code (`parsed_code/*.json`), producing two aligned JSONs per program:
```
queries/<program>.json
ground_truth/<program>.json
```

**Command**
```bash
python query.py
```

### main script 3: evaluate_api.py
**Purpose**
Evaluates SemBench code understanding tasks using **OpenAI GPT models** (e.g., GPT‑5, GPT‑5‑Mini, GPT‑4o‑Mini).  
It automates querying, response parsing, accuracy computation, and cost reporting.
**Command Example**
```bash
python evaluate_api.py \
--model_name gpt-5 \  
--type_kernels loop3_1000 \  
--api_key sk-XXXX \  
--report_usage
```
**Arguments**
| Flag | Description | Default |
|------|-------------|----------|
| `--type_kernels` | Dataset subdirectory (e.g., `loop3_1000`). | `loop3_1000` |
| `--model_name` | OpenAI model name. | `gpt-5` |
| `--api_key` | OpenAI API key (or env var `OPENAI_API_KEY`). | `""` |
| `--use_background` | Include background info in prompts. | `True` |
| `--temperature` | Sampling temperature. | `0.0` |
| `--num_samples` | Number of samples for self-consistency. | `1` |
| `--batch_size` | Batch size for query processing. | `12` |
| `--max_workers` | Thread workers for parallel runs. | `8` |
| `--max_tokens` | Max tokens to generate per response. | `64` |
| `--seed` | Random seed for reproducibility. | `42` |
| `--report_usage` | Show per-program token and cost usage. | `False` |

### main script 4: evaluate_opensource.py
**Purpose**
Runs **local or Hugging Face models** (e.g., Mistral, Qwen, CodeLlama, DeepSeek) using `transformers`.  
Implements **distributed inference (NCCL)** for large models.
**Command Example**
```bash
torchrun --nproc_per_node=4 evaluate_opensource.py   --model_name mistralai/Mistral-7B-Instruct-v0.3   --type_kernels loop3_1000
```
For the Python CodeNet subset, run from `SemBench`:
```bash
python evaluate_opensource.py \
  --model_name mistralai/Mistral-7B-Instruct-v0.3 \
  --type_kernels python_codenet \
  --language python
```
We use ```sbatch job.sh``` to evaluate all models. 

**Arguments**
| Flag | Description | Default |
|------|-------------|----------|
| `--model_name` | Hugging Face model name. | `mistralai/Mistral-7B-Instruct-v0.3` |
| `--batch_size` | Batch size for prompt processing. | `24` |
| `--max_tokens` | Max new tokens to generate. | `64` |
| `--temperature` | Sampling temperature. | `0.0` |
| `--num_samples` | Number of self-consistency samples. | `1` |
| `--use_self_consistency` | Enable self-consistency evaluation. | `False` |
| `--do_dynamic_temperature` | Enable dynamic temperature. | `True` |
| `--base_dir` | Base dataset directory. | `/SemBench/data` |
| `--type_kernels` | Dataset subset type. | From `config.json` |
| `--language` | Source language to evaluate: `auto`, `c`, or `python`. | `auto` |

## Python SemBench workflow
The Python workflow lives in `Python_workflow/` and uses repo-relative defaults. The included `SemBench/data/python_codenet` subset contains the selected Python files, parsed records, generated questions, and ground truth labels.

From the repository root:
```bash
python Python_workflow/python_parser.py \
  --code-dir SemBench/data/python_codenet/code \
  --output-dir SemBench/data/python_codenet/parsed_code

python Python_workflow/python_query.py \
  --parsed-dir SemBench/data/python_codenet/parsed_code \
  --code-dir SemBench/data/python_codenet/code \
  --query-dir SemBench/data/python_codenet/queries \
  --ground-truth-dir SemBench/data/python_codenet/ground_truth

python Python_workflow/run_self_check.py
```

### result analysis script 1: SemBench\Figure1\Figure1.py
Plots SemBench vs HumanEval correlation by model size.

**Arguments**
| Flag | Description | Default |
|------|-------------|----------|
| `-i`, `--input` | Path to input CSV. | `sembrech_updated3.csv` |
| `--png` | Output PNG file. | `Figure 1.png` |
| `--pdf` | Output PDF file. | `Figure 1.pdf` |

**Sample command**
```python Figure1/Figure1.py```

### result analysis script 2: SemBench\Figure3\Figure3.py
Generates accuracy comparisons per category and model family.

**Sample command**
```python Figure3/Figure3.py```


### result analysis script 3: SemBench\Figure4\Figure4.py
Generates scatter plots of SemBench categories vs HumanEval/MBPP.

**Sample command**
```python Figure4/Figure4.py```

### result analysis script 4: SemBench\correlation_analysis\compute_correlations.py
Computes Spearman correlation between SemBench and benchmark results.

**Arguments**
| Flag | Description | Default |
|------|-------------|----------|
| `--input_file` | Input SemBench CSV file. | `./finalresult.csv` |
| `--output_file` | Output correlation CSV file. | `./corr_updated.csv` |

**Sample command**
```python correlation_analysis/compute_correlations.py```

### Helper scripts
1. script\prompts\BACKGROUND_new.py
Background queries.
2. script\util.py
Utility functions for the four main scripts.
3. parser_helper.py & parser_helper_liveness.py
Decompose some complicated functions into separate files.

## file execution
This folder contains files from the data collection stage. To view and execute the script, enter this directory by ```cd file_execution```.
### Data
1. c_main_indep_with_code.csv
This file includes all files' information qualified for our first stage of file selection. Including file_name,program_id,code_length,lines_of_code,repo_name,path,standard_libs,custom_libs,code,unique_id. 
The files downloaded from CodeParrot exist in the form of a group of .arrow files. The unique_id is composed of the number of the .arrow file and the order of the file inside the .arrow file.
2. loop_5rs_loop_5rs_full.csv
This file records a selected pool of executable files from the last step. We execute each file for five rounds for stability and only select files that execute successfully into the next stage. 

3. ml_exe_loop_code.csv
This file includes the information on the finally qualified files. 
### Script
1. collect.py
This script reads the c_main_indep_with_code.csv, automatically decomposes it into individual C files, compiles, then executes and collects its attributes.
```bash
python collect.py \
  --version 1.0 \
  --rs colv1.0 \
  --rdtsc_lib ./librdtsc.so \
  --code_path ./c_main_indep_with_code.csv \
  --profile_result_path ./ml_profile_1.0.csv \
  --summary_txt ./run_summary_1.0.txt \
  --file_decomposition_output_directory ./decomposed \
  --thread_num 25 \
  --gcc_command "gcc -o {output_file} {input_file} {flags}" \
  --default_flags "-O2" \
  --compile_timeout 30 \
  --run_timeout 30
```

**Arguments**

| Flag | Description | Default |
|------|-------------|---------|
| `--version` | Run version tag used in suggested output filenames. | `1.0` |
| `--rs` | Run suffix. If omitted, auto-derived as `colv<version>`. | `colv<version>` |
| `--rdtsc_lib` | Path to `librdtsc.so` used for reading CPU cycle counters. | `./librdtsc.so` |
| `--code_path` | **Required.** Input CSV containing code rows. | `./c_main_indep_with_code.csv` |
| `--profile_result_path` | Output CSV summarizing profiling metrics. | `./ml_profile_<version>.csv` *(fallback: `./ml_profile.csv`)* |
| `--summary_txt` | Output TXT summary with descriptive statistics. | `./run_summary_<version>.txt` *(fallback: `./run_summary.txt`)* |
| `--file_decomposition_output_directory` | Directory where source files and compiled binaries are stored. | `./decomposed` |
| `--thread_num` | Maximum number of worker threads. | `25` |
| `--gcc_command` | GCC compilation template. Must include `{output_file}`, `{input_file}`, `{flags}`. | `"gcc -o {output_file} {input_file} {flags}"` |
| `--default_flags` | Compiler flags injected into the template. | `-O2` |
| `--compile_timeout` | Compilation timeout in seconds. | `30` |
| `--run_timeout` | Execution timeout in seconds. | `30` |

---

2. Helper files
- rdtsc.c: it is the helper script to generate librdtsc.so.
- librdtsc.so: the file uses the shared library librdtsc.so to access the CPU’s time-stamp counter (TSC) directly via the rdtsc instruction.
- col.sh: the sbatch script you may use to run the collect.py script if you are working on a SLURM system.

## Data sources

The C programs used to construct the main SemBench benchmark are sampled from the Hugging Face `codeparrot/github-code` dataset:
https://huggingface.co/datasets/codeparrot/github-code

The Python programs used in the supplementary cross-language analysis are sampled from IBM Project CodeNet:
https://github.com/IBM/Project_CodeNet

We use these datasets as raw source-code pools and apply the filtering, parsing, and semantic-question generation pipeline described in the paper.





