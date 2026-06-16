# 4.py — Quicksort with Lomuto partition
# Structure adapted from widely used real-world implementations (e.g., TheAlgorithms/Python, MIT license).
# Functions:
# - quicksort: user-facing wrapper that sorts and returns the array
# - _quicksort: recursive helper
# - partition: Lomuto partition scheme using a for-loop

from typing import List

def partition(arr: List[int], low: int, high: int) -> int:
    pivot = arr[high]
    i = low - 1
    for j in range(low, high):
        if arr[j] <= pivot:
            i += 1
            arr[i], arr[j] = arr[j], arr[i]
    arr[i + 1], arr[high] = arr[high], arr[i + 1]
    return i + 1

def _quicksort(arr: List[int], low: int, high: int) -> None:
    if low < high:
        pi = partition(arr, low, high)
        _quicksort(arr, low, pi - 1)
        _quicksort(arr, pi + 1, high)

def quicksort(arr: List[int]) -> List[int]:
    n = len(arr)
    if n <= 1:
        return arr
    _quicksort(arr, 0, n - 1)
    return arr
