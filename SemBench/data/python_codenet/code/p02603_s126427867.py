import math,string,itertools,fractions,heapq,collections,re,array,bisect,sys,copy,functools
import time,random

sys.setrecursionlimit(10**7)
inf = 10**20
eps = 1.0 / 10**10
mod = 10**9+7
mod2 = 998244353
dd = [(-1,0),(0,1),(1,0),(0,-1)]
ddn = [(-1,0),(-1,1),(0,1),(1,1),(1,0),(1,-1),(0,-1),(-1,-1)]

def LI(): return list(map(int, sys.stdin.readline().split()))
def LLI(): return [list(map(int, l.split())) for l in sys.stdin.readlines()]
def LI_(): return [int(x)-1 for x in sys.stdin.readline().split()]
def LF(): return [float(x) for x in sys.stdin.readline().split()]
def LS(): return sys.stdin.readline().split()
def I(): return int(sys.stdin.readline())
def F(): return float(sys.stdin.readline())
def S(): return input()
def pf(s): return print(s, flush=True)
def pe(s): return print(str(s), file=sys.stderr)
def JA(a, sep): return sep.join(map(str, a))
def JAA(a, s, t): return s.join(t.join(map(str, b)) for b in a)


def main():
    n = I()
    a = LI()

    r = 1000
    t = []
    sf = True
    for i in range(n-1):
        if sf:
            if a[i] >= a[i+1]:
                continue
            t.append(a[i])
            sf = False
        else:
            if a[i] <= a[i+1]:
                continue
            t.append(a[i])
            sf = True

    if len(t) == 0:
        return r

    if t[-1] != a[-1]:
        t.append(a[-1])

    for i in range(len(t)//2):
        b = t[i*2]
        c = t[i*2 + 1]
        k = r // b
        r += (c-b) * k

    return r

print(main())



