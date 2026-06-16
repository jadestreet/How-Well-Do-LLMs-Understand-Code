import sys, math, re
from functools import lru_cache
from collections import deque
sys.setrecursionlimit(10**9)
MOD = 10**9+7

def input():
    return sys.stdin.readline()[:-1]

def mi():
    return map(int, input().split())

def ii():
    return int(input())

def i2(n):
    tmp = [list(mi()) for i in range(n)]
    return [list(i) for i in zip(*tmp)]

s = input()
s = s.replace('BC', 'D')
matches = re.findall(r'[AD]+', s)
ans = 0
for w in matches:
    n = len(w)
    p = n-1
    for i in range(n-1, -1, -1):
        if w[i] == 'A':
            ans += p-i
            p -= 1

print(ans)