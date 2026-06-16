from _collections import deque
from _ast import Num


def parser():
    while 1:
        data = list(input().split(' '))
        for number in data:
            if len(number) > 0:
                yield (number)


input_parser = parser()


def gw():
    global input_parser
    return next(input_parser)


def gi():
    data = gw()
    return int(data)


MOD = int(1e9 + 7)

import numpy
from collections import deque
from math import sqrt
from math import floor
import heapq
#https://atcoder.jp/contests/abc148/tasks/abc148_f
#F - Playing Tag on Tree
"""
"""
N = gi()
U = gi()
V = gi()
t = [[] for i in range(N + 1)]
d = [[-1 for i in range(2)] for j in range(N + 1)]

for _ in range(1, N):
    a = gi()
    b = gi()
    t[a].append(b)
    t[b].append(a)


def bfs(s, di):
    d[s][di] = 0
    q = deque()
    q.append(s)
    while len(q):
        v = q.pop()
        for u in t[v]:
            if d[u][di] >= 0:
                continue
            d[u][di] = d[v][di] + 1
            q.append(u)


bfs(U, 0)
bfs(V, 1)

ans = 0
for l in range(1, N + 1):
    if len(t[l]) > 1:
        continue
    du = d[l][0]
    dv = d[l][1]
    #print(l, du, dv)
    if dv >= du:
        ans = max(ans, dv - 1)

print(ans)
