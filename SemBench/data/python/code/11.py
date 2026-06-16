# 11.py — Greatest Common Divisor (iterative Euclidean algorithm)
from typing import Tuple

def _gcd_iter(a: int, b: int) -> int:
    while b != 0:
        a, b = b, a % b
    return abs(a)

def gcd(a: int, b: int) -> int:
    # Normalize signs, then delegate to the iterative routine.
    return _gcd_iter(abs(a), abs(b))
