# 20.py — Prefix sums and range sum query
from typing import List

def build_prefix(arr: List[int]) -> List[int]:
    prefix = [0] * (len(arr) + 1)
    for i, x in enumerate(arr, start=1):
        prefix[i] = prefix[i - 1] + x
    return prefix

def range_sum(prefix: List[int], l: int, r: int) -> int:
    # sum over arr[l:r] using 1-based prefix where prefix[0] = 0
    if l < 0 or r < l or r > len(prefix) - 1:
        raise IndexError("invalid range")
    return prefix[r] - prefix[l]
