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

from collections import defaultdict, deque, Counter
from sys import exit
import heapq
import math
import copy
from operator import mul
from functools import reduce
from bisect import bisect_left, bisect_right

import sys
sys.setrecursionlimit(1000000000)

N, K = getNM()
S = input()

flag = S[0]
sta = 1
lista = []
# 14 2
# 11101010110011なら
# ２回まで0の箇所を消すことができる

# 00010を['0', 1, 3], ['1', 4, 4], ['0', 5, 5]という風に整頓する
for i in range(1, N):
    if flag != S[i]:
        # flag(0か1か), sta(どこから続いているか), i(最終的にどこまで続いたか)
        lista.append([flag, sta, i])
        flag = S[i]
        sta = i + 1
lista.append([flag, sta, N])
ans = 0
np = len(lista)
for i in range(np):
    if lista[i][0] == '0':
        index = min(i + 2 * K - 1, np - 1)
        opt = lista[index][2] - lista[i][1] + 1
        ans = max(ans, opt)
    else:
        index = min(i + 2 * K, np - 1)
        opt = lista[index][2] - lista[i][1] + 1
        ans = max(ans, opt)
print(ans)