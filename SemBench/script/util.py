import json
import os
import re
from typing import Optional, List

INSTRUCTION_TEMPLATE = "Given the {language} code and background information, your response should start with an option between \"[Final answer: yes]\" or \"[Final answer: no]\" then you should explain your solution step by step briefly."
DOM_DATA_INSTRUCTION = "the line numbers do NOT imply execution order or control flow."
INSTRUCTION_DETAILS_TEMPLATE = """
Given the {language} code with line numbers, background information, and test question, answer the question.
Output must follow this format exactly:
Line 1: <answer>[Final answer: yes]</answer> or <answer>[Final answer: no]</answer>
Line 2-5: Exactly 2-4 bullet points ("- ...") that justify Line 1.

Rules:
- Do NOT output anything before Line 1.
- Do NOT repeat the question.
- Do NOT add any other tags besides <answer> on Line 1.
- Use only "yes" or "no" (lowercase) inside [Final answer: ...].
"""

INSTRUCTION = INSTRUCTION_TEMPLATE.format(language="C")

_BOILERPLATE_RE = re.compile(
    r'(?i)\b(?:yes\s*/\s*no|yes\s+or\s+no)\b[\?\:\.\s]*'
)


_clean_re   = re.compile(r'[^A-Za-z0-9\[\]:\s]')
_prefix_re  = re.compile(r'(?:final\s*)?answer\s*:', flags=re.IGNORECASE)
_bracket_re = re.compile(r'\[final\s*answer:\s*(?:yes|no)\]', flags=re.IGNORECASE)
_verdict_re = re.compile(r'(?:final\s*)?answer\s*:\s*(yes|no)', flags=re.IGNORECASE)
_word_no  = re.compile(r'\bno\b')
_word_yes = re.compile(r'\byes\b')

def parse_llm_response(response: str) -> Optional[bool]:
    cleaned = _clean_re.sub('', response)
    for line in reversed(cleaned.splitlines()):
        low = line.lower()
        if 'answer' not in low:
            continue
        if len(_bracket_re.findall(line)) > 1:
            continue
        if not _prefix_re.search(line):
            continue
        has_yes = bool(_word_yes.search(line))
        has_no  = bool(_word_no.search(line))
        if has_yes and has_no:
            continue
        hits = _verdict_re.findall(line)
        if not hits:
            continue
        unique = {h.lower() for h in hits}
        if unique == {'yes'}:
            return True
        if unique == {'no'}:
            return False
    return None

def _resolve_language(code_file, language=None):
    if language:
        normalized = language.lower()
        if normalized == "c":
            return "C"
        if normalized in {"py", "python"}:
            return "Python"
        return language

    _, ext = os.path.splitext(str(code_file).lower())
    if ext == ".py":
        return "Python"
    return "C"


def _get_background_info():
    try:
        from script.prompts.BACKGROUND_new import background_info
    except ImportError:
        background_info = {}
    return background_info


def _read_code(code_file):
    try:
        with open(code_file, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        print(f"Error reading code file {code_file}: {e}")
        return ""


def _format_line_numbered_code(code_file):
    code = _read_code(code_file)
    if str(code_file).lower().endswith(".json"):
        try:
            code_dict = json.loads(code)
            return "\n".join(
                f"{ln}: {text}" for ln, text in sorted(
                    code_dict.items(),
                    key=lambda item: (
                        0,
                        int(item[0])
                    ) if str(item[0]).isdigit() else (1, str(item[0]))
                )
            )
        except Exception as e:
            print(f"Error parsing line-numbered code file {code_file}: {e}")
            return ""
    return "\n".join(f"{ln}: {text}" for ln, text in enumerate(code.splitlines(), start=1))


def construct_input_large(code_file, prompt, category, language=None):
    """
    Builds the full prompt for the LLM, including the code, background info,
    few-shot examples, and the test question.
    """
    language_name = _resolve_language(code_file, language)
    input_text = INSTRUCTION_TEMPLATE.format(language=language_name) + "\n\n"
    background_info = _get_background_info()
    code = _read_code(code_file)

    if background_info.get(category, ""):
        input_text += background_info.get(category, "") + "\n\n"

    input_text += "See the " + language_name + " Code and answer the question:\n" + code + "\n\n" + "Test Question: " + prompt
    
    return input_text


def construct_input_large_domdata(code_file, prompt, category, language=None):
    """
    Builds a line-numbered prompt for dominator and data-dependency questions.
    """
    language_name = _resolve_language(code_file, language)
    input_text = INSTRUCTION_DETAILS_TEMPLATE.format(language=language_name).strip() + "\n\n"
    background_info = _get_background_info()
    formatted_code = _format_line_numbered_code(code_file)

    if background_info.get(category, ""):
        input_text += background_info.get(category, "") + "\n\n"

    input_text += (
        "See the " + language_name + " Code and answer the question, the "
        + language_name + " code is indexed with line numbers, "
        + DOM_DATA_INSTRUCTION + "\n"
        + formatted_code
        + "\n\n"
        + "The statements in the questions are wrapped with <statement></statement>. "
        + "Test Question: " + prompt
    )
    return input_text

def convert_tensors(obj):
    """
    Recursively converts any torch.Tensor objects in an object to Python scalars/lists.
    (Retained for legacy support; API responses are JSON serializable.)
    """
    try:
        import torch
        if isinstance(obj, torch.Tensor):
            return obj.item() if obj.numel() == 1 else obj.tolist()
    except ImportError:
        pass
    if isinstance(obj, dict):
        return {k: convert_tensors(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_tensors(v) for v in obj]
    else:
        return obj
