# 8.py — Palindrome check ignoring non-alphanumeric characters
from typing import List, Optional

def clean(s: str) -> List[str]:
    letters = [c.lower() for c in s if c.isalnum()]
    return letters

def is_palindrome(s: Optional[str]) -> bool:
    if s is None:
        return False
    letters = clean(s)
    i, j = 0, len(letters) - 1
    while i < j:
        if letters[i] != letters[j]:
            return False
        i += 1
        j -= 1
    return True
