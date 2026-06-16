# 9.py — Matrix multiplication with basic shape checks
from typing import List, Tuple

def dims(M: List[List[int]]) -> Tuple[int, int]:
    rows = len(M)
    cols = len(M[0]) if rows > 0 else 0
    return rows, cols

def matmul(A: List[List[int]], B: List[List[int]]) -> List[List[int]]:
    if not A or not B:
        raise ValueError("empty matrix not allowed")
    ra, ca = dims(A)
    rb, cb = dims(B)
    if ca != rb:
        raise ValueError("incompatible shapes")
    m, k, n = ra, ca, cb
    C = [[0] * n for _ in range(m)]
    for i in range(m):
        for j in range(n):
            s = 0
            for t in range(k):
                s += A[i][t] * B[t][j]
            C[i][j] = s
    return C
