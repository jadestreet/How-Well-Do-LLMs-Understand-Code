"""
2.py — Merge Sort (structure based on widely used real-world implementations, e.g., TheAlgorithms/Python, MIT license).
This single file contains two functions that are commonly found together in real codebases:
- merge_sort: recursively sorts the list
- merge: merges two sorted lists
"""

def merge_sort(arr):
    if len(arr) <= 1:
        return arr
    mid = len(arr) // 2
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])
    return merge(left, right)

def merge(left, right):
    i = 0
    j = 0
    result = []
    # loop header 1
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    # loop header 2
    while i < len(left):
        result.append(left[i])
        i += 1
    # loop header 3
    while j < len(right):
        result.append(right[j])
        j += 1
    return result