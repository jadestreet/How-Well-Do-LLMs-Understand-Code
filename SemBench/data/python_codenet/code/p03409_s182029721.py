def getN():
    return int(input())
def getNM():
    return map(int, input().split())
def getList():
    return list(map(int, input().split()))
def getArray(intn):
    return [int(input()) for i in range(intn)]
def input():
    return sys.stdin.readline().rstrip()
def rand_N(ran1, ran2):
    return random.randint(ran1, ran2)
def rand_List(ran1, ran2, rantime):
    return [random.randint(ran1, ran2) for i in range(rantime)]
def rand_ints_nodup(ran1, ran2, rantime):
  ns = []
  while len(ns) < rantime:
    n = random.randint(ran1, ran2)
    if not n in ns:
      ns.append(n)
  return sorted(ns)

def rand_query(ran1, ran2, rantime):
  r_query = []
  while len(r_query) < rantime:
    n_q = rand_ints_nodup(ran1, ran2, 2)
    if not n_q in r_query:
      r_query.append(n_q)
  return sorted(r_query)

from collections import defaultdict, deque, Counter
from sys import exit
from decimal import *
import heapq
import math
from fractions import gcd
import random
import string
import copy
from itertools import combinations, permutations, product
from operator import mul
from functools import reduce
from bisect import bisect_left, bisect_right

import sys
sys.setrecursionlimit(1000000000)
mod = 10 ** 9 + 7


#############
# Main Code #
#############

N_s = getN()
A = [getList() for i in range(N_s)]
B = [getList() for i in range(N_s)]
query = []
# ノードの始点を2 * N_sに、終点を2 * N_s + 1に設定
for i in range(N_s):
    query.append([2 * N_s, i, 1])
    query.append([N_s + i, 2 * N_s + 1, 1])
for i in range(N_s):
    for j in range(N_s):
        if A[i][0] < B[j][0] and A[i][1] < B[j][1]:
            query.append([i, N_s + j, 1])

N = 2 * N_s + 2

ans = 0
lines = defaultdict(set)
cost = [[0] * N for i in range(N)]
for i in range(len(query)):
    a, b, c = query[i]
    lines[a].add(b)
    cost[a][b] += c

# 二部マッチング問題なので最大流
# staからスタート
def Ford_Fulkerson(sta, end):
    global ans
    queue = deque()
    queue.append([sta, float('inf')])

    ignore = [1] * N
    ignore[sta] = 0

    route = [0] * N
    route[sta] = -1

    while queue:
        s, flow = queue.pop()
        for t in lines[s]:  #s->t
            if ignore[t]: #未到達
                # flowは入ってくる量、出る量のうち小さい方
                flow = min(cost[s][t], flow)
                route[t] = s
                queue.append([t, flow])
                ignore[t] = 0
                if t == end: #ゴール到達
                    ans += flow
                    break
        else:
            continue #breakされなければWhile節の先頭に戻る
        # Falseはされない
        break
    else:
        return False

    t = end
    s = route[t]
    # goalまで流れた量はflow
    # 逆向きの辺を貼る
    while s != -1:
        #s->tのコスト減少，ゼロになるなら辺を削除
        cost[s][t] -= flow
        if cost[s][t] == 0:
            lines[s].remove(t)
            #t->s(逆順)のコスト増加，元がゼロなら辺を作成
        if cost[t][s] == 0:
            lines[t].add(s)

        cost[t][s] += flow

        # 一つ上の辺をたどる
        t = s
        s = route[t]

    return True

while True:
    # ちょびちょび流して行ってゴールまで流れなくなったら終了
    if Ford_Fulkerson(N - 2, N - 1):
        continue
    else:
        break

print(ans)