# 5.py — Binary search (iterative) with a wrapper
# Structure reflects common real-world implementations.
from typing import List

def _binary_search(arr: List[int], target: int, low: int, high: int) -> int:
    while low <= high:
        mid = (low + high) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            low = mid + 1
        else:
            high = mid - 1
    return -1

def binary_search(arr: List[int], target: int) -> int:
    if not arr:
        return -1
    return _binary_search(arr, target, 0, len(arr) - 1)
