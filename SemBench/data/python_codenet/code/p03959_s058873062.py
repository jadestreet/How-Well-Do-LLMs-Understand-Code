import sys, re
from collections import deque, defaultdict, Counter
from math import ceil, sqrt, hypot, factorial, pi, sin, cos, tan, asin, acos, atan, radians, degrees#, log2
from itertools import accumulate, permutations, combinations, combinations_with_replacement, product, groupby
from operator import itemgetter, mul
from copy import deepcopy
from string import ascii_lowercase, ascii_uppercase, digits
from bisect import bisect, bisect_left, insort, insort_left
from fractions import gcd
from heapq import heappush, heappop
from functools import reduce
def input(): return sys.stdin.readline().strip()
def INT(): return int(input())
def MAP(): return map(int, input().split())
def LIST(): return list(map(int, input().split()))
def ZIP(n): return zip(*(MAP() for _ in range(n)))
sys.setrecursionlimit(10 ** 9)
INF = float('inf')
mod = 10**9 + 7
#from decimal import *

N = INT()
T = LIST()
A = LIST()

h = [0]*N
ma = -1
for i, t in enumerate(T):
	if ma < t:
		h[i] = t
		ma = t


ma = -1
for i, a in enumerate(A[::-1]):
	if ma < a:
		if h[-i-1] and a != h[-i-1]:
			print(0)
			exit()
		h[-i-1] = a
		ma = a

acc_t = list(accumulate(h, max))
acc_a = list(accumulate(h[::-1], max))[::-1]

if acc_t != T or acc_a != A:
	print(0)
	exit()

mi = [min(t, a) for t, a in zip(T, A)]

ans = 1
for i in range(N):
	if h[i] == 0:
		ans *= mi[i]
		ans %= mod

print(ans)