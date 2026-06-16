#!usr/bin/env python3
from collections import defaultdict
from collections import deque
from heapq import heappush, heappop
import sys
import math
import bisect
import random
def LI(): return list(map(int, sys.stdin.readline().split()))
def I(): return int(sys.stdin.readline())
def LS():return list(map(list, sys.stdin.readline().split()))
def S(): return list(sys.stdin.readline())[:-1]
def IR(n):
    l = [None for i in range(n)]
    for i in range(n):l[i] = I()
    return l
def LIR(n):
    l = [None for i in range(n)]
    for i in range(n):l[i] = LI()
    return l
def SR(n):
    l = [None for i in range(n)]
    for i in range(n):l[i] = S()
    return l
def LSR(n):
    l = [None for i in range(n)]
    for i in range(n):l[i] = SR()
    return l
mod = 1000000007

#A
def A():
    return

#B
def B():
    return

#C
def C():
    def dfs(i,k):
        if i == d:
            l.append(k)
        else:
            for j in range(2):
                dfs(i+1,k+[j])
    d,g = LI()
    p = LIR(d)
    ans = float("inf")
    l = []
    dfs(0,[])
    for k in l:
        m = 0
        o = 0
        q = [[p[i][0],p[i][1]] for i in range(d)]
        for i in range(d):
            if k[i]:
                o += q[i][0]
                m += q[i][0]*(i+1)*100+q[i][1]
                q[i][0] = 0
        while m < g:
            for i in range(d)[::-1]:
                for j in range(q[i][0]):
                    m += (i+1)*100
                    o += 1
                    if m >= g:break
                if m >= g:break
        ans = min(ans,o)
    print(ans)
#D
def D():
    s = S()
    n = len(s)
    dp = [[0,0,0,0] for i in range(n+1)]
    dp[0][0] = 1
    for i in range(n):
        if s[i] == "?":
            dp[i+1] = [3*dp[i][0]%mod,3*dp[i][1]%mod,3*dp[i][2]%mod,3*dp[i][3]%mod]
        else:
            dp[i+1] = [dp[i][0],dp[i][1],dp[i][2],dp[i][3]]
        if s[i] == "A":
            dp[i+1][1] += dp[i][0]
            dp[i+1][1] %= mod
        elif s[i] == "B":
            dp[i+1][2] += dp[i][1]
            dp[i+1][2] %= mod
        elif s[i] == "C":
            dp[i+1][3] += dp[i][2]
            dp[i+1][3] %= mod
        else:
            dp[i+1][1] += dp[i][0]
            dp[i+1][2] += dp[i][1]
            dp[i+1][3] += dp[i][2]
            dp[i+1][1] %= mod
            dp[i+1][2] %= mod
            dp[i+1][3] %= mod
    print(dp[n][3])
#E
def E():
    return

#F
def F():
    return

#G
def G():
    return

#H
def H():
    return

#Solve
if __name__ == "__main__":
    D()
