# 17.py — Insertion sort with element insertion helper
from typing import List

def _insert(arr: List[int], i: int) -> None:
    key = arr[i]
    j = i - 1
    while j >= 0 and arr[j] > key:
        arr[j + 1] = arr[j]
        j -= 1
    arr[j + 1] = key

def insertion_sort(arr: List[int]) -> List[int]:
    n = len(arr)
    for i in range(1, n):
        _insert(arr, i)
    return arr
