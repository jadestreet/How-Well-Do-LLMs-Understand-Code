# 18.py — Quickselect (k-th smallest) using Lomuto partition
from typing import List

def _partition(arr: List[int], low: int, high: int) -> int:
    pivot = arr[high]
    i = low
    for j in range(low, high):
        if arr[j] < pivot:
            arr[i], arr[j] = arr[j], arr[i]
            i += 1
    arr[i], arr[high] = arr[high], arr[i]
    return i

def _quickselect(arr: List[int], low: int, high: int, k: int) -> int:
    while low <= high:
        pi = _partition(arr, low, high)
        if pi == k:
            return arr[pi]
        elif pi < k:
            low = pi + 1
        else:
            high = pi - 1
    raise IndexError("k out of bounds")

def kth_smallest(arr: List[int], k: int) -> int:
    if k < 0 or k >= len(arr):
        raise IndexError("k out of bounds")
    return _quickselect(arr, 0, len(arr) - 1, k)
