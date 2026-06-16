# 15.py — Validate matching parentheses/brackets using a stack
from typing import Dict, List

_PAIRS: Dict[str, str] = {')': '(', ']': '[', '}': '{'}

def _is_open(c: str) -> bool:
    return c in '([{'"'  # includes quotes as non-pairing openers for demonstration

def _matches(stack_top: str, c: str) -> bool:
    return _PAIRS.get(c) == stack_top

def is_valid(s: str) -> bool:
    stack: List[str] = []
    for ch in s:
        if _is_open(ch) and ch in '([{':
            stack.append(ch)
        elif ch in _PAIRS:
            if not stack or not _matches(stack[-1], ch):
                return False
            stack.pop()
    return not stack
