from collections import defaultdict, deque, Counter
from heapq import heappush, heappop, heapify
from bisect import bisect_right, bisect_left
import random
from itertools import permutations, accumulate, combinations, product
import sys
import string
from bisect import bisect_left, bisect_right
from math import factorial, ceil, floor, gamma, log
from operator import mul
from functools import reduce
from copy import deepcopy

sys.setrecursionlimit(2147483647)
INF = 10 ** 20
def LI(): return list(map(int, sys.stdin.buffer.readline().split()))
def I(): return int(sys.stdin.buffer.readline())
def LS(): return sys.stdin.buffer.readline().rstrip().decode('utf-8').split()
def S(): return sys.stdin.buffer.readline().rstrip().decode('utf-8')
def IR(n): return [I() for i in range(n)]
def LIR(n): return [LI() for i in range(n)]
def SR(n): return [S() for i in range(n)]
def LSR(n): return [LS() for i in range(n)]
def SRL(n): return [list(S()) for i in range(n)]
def MSRL(n): return [[int(j) for j in list(S())] for i in range(n)]
mod = 10 ** 9 + 7


h, w = LI()
grid = SRL(h)
visited = [[0] * w for _ in range(h)]

def solve(sy, sx):
    dq = deque([(sy, sx)])
    visited[sy][sx] = 1
    bi = [0, 1]
    while dq:
        cy, cx = dq.popleft()
        for i, j in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            ny = cy + i
            nx = cx + j
            if 0 <= ny < h and 0 <= nx < w and not visited[ny][nx]:
                if grid[ny][nx] != grid[cy][cx]:
                    bi[int(grid[sy][sx] == grid[ny][nx])] += 1
                    dq += [(ny, nx)]
                    visited[ny][nx] = 1
    return bi[0] * bi[1]

ans = 0
for y in range(h):
    for x in range(w):
        if visited[y][x]:
            continue
        else:
            ans += solve(y, x)


print(ans)