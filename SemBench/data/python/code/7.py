# 7.py — Fibonacci numbers (top-down memoization) and series builder
from typing import Dict, List, Optional

def fib(n: int, memo: Optional[Dict[int, int]] = None) -> int:
    if n < 0:
        raise ValueError("n must be non-negative")
    if memo is None:
        memo = {}
    if n <= 1:
        return n
    if n in memo:
        return memo[n]
    memo[n] = fib(n - 1, memo) + fib(n - 2, memo)
    return memo[n]

def fib_series(k: int) -> List[int]:
    res: List[int] = []
    for i in range(k):
        res.append(fib(i))
    return res