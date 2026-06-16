# 19.py — Parse integer from string (simplified atoi)
from typing import Tuple

def _consume_sign(s: str, i: int) -> Tuple[int, int]:
    sign = 1
    if i < len(s) and s[i] in '+-':
        if s[i] == '-':
            sign = -1
        i += 1
    return sign, i

def parse_int(s: str) -> int:
    i = 0
    while i < len(s) and s[i].isspace():
        i += 1
    sign, i = _consume_sign(s, i)
    val = 0
    any_digit = False
    while i < len(s) and s[i].isdigit():
        any_digit = True
        val = val * 10 + (ord(s[i]) - ord('0'))
        i += 1
    if not any_digit:
        raise ValueError("no digits")
    return sign * val
