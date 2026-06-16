def examA():
    A, B = LI()
    ans = A*B
    print(ans)
    return

def examB():
    N = I()
    A = LI()
    for a in A:
        if a==0:
            print(0)
            return
    ans = 1
    for a in A:
        ans *= a
        if ans>10**18:
            print(-1)
            return
    print(ans)
    return

def examC():
    A, B = LSI()
    ans =math.floor(int(A)*float(B))
    print(ans)
    return

def examD():
    def factorization(n):
        arr = defaultdict(int)
        temp = n
        for i in range(2, int(-(-n ** 0.5 // 1)) + 1):
            if temp % i == 0:
                cnt = 0
                while temp % i == 0:
                    cnt += 1
                    temp //= i
                arr[i] = cnt
        if temp != 1:
            arr[temp] = 1
        if arr == []:
            arr[n] = 1
        return arr
    C = [0,1,3,6,10,15,21,28,36,45]
    N = I()
    F = factorization(N)
    ans = 0
    #print(F)
    for f in F.values():
        for i in range(10):
            if C[i]>f:
                ans += i-1
                break
    print(ans)
    return

def examE():
    N = I()
    A = [0]*N
    B = [0]*N
    for i in range(N):
        A[i],B[i] = LI()
    A.sort()
    B.sort()
    if N%2==0:
        L = (A[N//2-1] + A[N//2])/2
        R = (B[N//2-1] + B[N//2])/2
        ans = int((R-L)*2) +1
    else:
        L = A[N//2]
        R = B[N//2]
        ans = (R-L)+1

    print(ans)
    return

def examF():
    inv = pow(2,mod2-2,mod2)
    N, S = LI()
    A = LI()
    dp = [[0]*(S+1)for _ in range(N+1)]
    dp[0][0] = pow(2,N,mod2)
    for i in range(N):
        a = A[i]
        for s in range(S+1):
            dp[i+1][s] += dp[i][s]
            dp[i+1][s] %= mod2
            if (s+a<=S):
                dp[i+1][s+a] += dp[i][s]*inv%mod2
                dp[i + 1][s+a] %= mod2
   # print(dp)
    ans = dp[-1][-1]%mod2
    print(ans)
    return

import sys,bisect,itertools,heapq,math,random
from copy import deepcopy
from heapq import heappop,heappush,heapify
from collections import Counter,defaultdict,deque
read = sys.stdin.buffer.read
readline = sys.stdin.buffer.readline
readlines = sys.stdin.buffer.readlines
def I(): return int(input())
def LI(): return list(map(int,sys.stdin.readline().split()))
def LSI(): return list(map(str,sys.stdin.readline().split()))
def LS(): return sys.stdin.readline().split()
def SI(): return sys.stdin.readline().strip()
global mod,mod2,inf,alphabet,_ep
mod = 10**9 + 7
mod2 = 998244353
inf = 1<<60
_ep = 10**(-12)
alphabet = [chr(ord('a') + i) for i in range(26)]

sys.setrecursionlimit(10**7)

if __name__ == '__main__':
    examF()

"""
142
12 9 1445 0 1
asd dfg hj o o
aidn
"""