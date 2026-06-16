# coding: utf-8
import sys

# from operator import itemgetter
sysread = sys.stdin.buffer.readline
read = sys.stdin.buffer.read
printout = sys.stdout.write
sprint = sys.stdout.flush
#from heapq import heappop, heappush
#from collections import defaultdict
sys.setrecursionlimit(10 ** 7)
#import math
# from itertools import product, accumulate, combinations, product
#import bisect
# import numpy as np
# from copy import deepcopy
from collections import deque
# from decimal import Decimal
# from numba import jit

INF = 1 << 50
EPS = 1e-8
mod = 998244353


def intread():
    return int(sysread())
def mapline(t=int):
    return map(t, sysread().split())
def mapread(t=int):
    return map(t, read().split())

def bfs(MAP, queue):

    while queue:
        turn, ci, cj = queue.popleft()
        for ii, jj in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            ni = ci + ii
            nj = cj + jj
            if MAP[ni][nj] == 0:
                MAP[ni][nj] = 1
                queue.append((turn + 1, ni, nj))
    return turn


def run():
    H, W = map(int, input().split())
    queue = deque([])
    MAP = [[1] * (W+2)]
    d = {'#' : 1, '.' : 0}
    for i in range(1, H+1):
        X = input()
        S = [1]
        for j, s in enumerate(X, 1):
            S.append(d[s])
            if s == '#':
                queue.append((0, i, j))
        S.append(1)
        MAP.append(S)

    #print(queue)
    MAP.append([1] * (W+2))

    print(bfs(MAP, queue))


if __name__ == "__main__":
    #print(math.gcd(0, 10))
    run()
