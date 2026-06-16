# 12.py — Merge overlapping intervals
from typing import List

def _append_or_merge(merged: List[List[int]], cand: List[int]) -> None:
    if not merged or merged[-1][1] < cand[0]:
        merged.append(cand[:])
    else:
        merged[-1][1] = max(merged[-1][1], cand[1])

def merge_intervals(intervals: List[List[int]]) -> List[List[int]]:
    if not intervals:
        return []
    intervals.sort(key=lambda x: x[0])
    merged: List[List[int]] = []
    for seg in intervals:
        _append_or_merge(merged, seg)
    return merged
