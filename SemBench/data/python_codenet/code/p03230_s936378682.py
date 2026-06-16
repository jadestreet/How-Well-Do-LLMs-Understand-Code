# -*- coding: utf-8 -*-

"""
参考：https://img.atcoder.jp/tenka1-2018/editorial.pdf
　　　https://ferin-tech.hatenablog.com/entry/2018/10/29/135010
　　　https://babcs2035.hateblo.jp/entry/2018/11/03/143845
　　　https://naoyat.hatenablog.jp/entry/tenka1-2018-vc
　　　https://atcoder.jp/contests/tenka1-2018-beginner/submissions/3996670
"""

import sys, re
from collections import deque, defaultdict, Counter
from math import sqrt, hypot, factorial, pi, sin, cos, radians, log10
if sys.version_info.minor >= 5: from math import gcd
else: from fractions import gcd 
from heapq import heappop, heappush, heapify, heappushpop
from bisect import bisect_left, bisect_right
from itertools import permutations, combinations, product
from operator import itemgetter, mul
from copy import copy, deepcopy
from functools import reduce, partial
from fractions import Fraction
from string import ascii_lowercase, ascii_uppercase, digits

def input(): return sys.stdin.readline().strip()
def list2d(a, b, c): return [[c] * b for i in range(a)]
def list3d(a, b, c, d): return [[[d] * c for j in range(b)] for i in range(a)]
def ceil(x, y=1): return int(-(-x // y))
def round(x): return int((x*2+1) // 2)
def fermat(x, y, MOD): return x * pow(y, MOD-2, MOD) % MOD
def lcm(x, y): return (x * y) // gcd(x, y)
def lcm_list(nums): return reduce(lcm, nums, 1)
def gcd_list(nums): return reduce(gcd, nums, nums[0])
def INT(): return int(input())
def MAP(): return map(int, input().split())
def LIST(): return list(map(int, input().split()))
sys.setrecursionlimit(10 ** 9)
INF = float('inf')
MOD = 10 ** 9 + 7

N = INT()

cnt = 1
add = 2
while cnt < N:
    cnt += add
    add += 1
# 条件を満たすものを構成できる
if cnt == N:
    # 各部分集合の要素数:c 部分集合の数:add
    c = add - 1
    ans = list2d(add, c, 0)
    k = 1
    for i in range(add):
        for j in range(i, c):
            ans[i][j] = k
            ans[j+1][i] = k
            k += 1
    print('Yes')
    print(add)
    for i in range(add):
        print(c, *ans[i])
else:
    print('No')
