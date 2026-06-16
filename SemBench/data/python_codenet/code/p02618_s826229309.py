from random import randint, getrandbits, random
from math import exp
import time
import sys
start = time.perf_counter()
input = sys.stdin.readline

def scoring():
    last = [0] * 26
    res = 0
    penalty = 0
    for i in range(D):
        t = out[i]
        res += S[i][t]
        penalty += sc - (i + 1 - last[t]) * C[t]
        res -= penalty
        last[t] = i + 1
    return res

def solve(score):
    T0 = 2.e3
    T1 = 6.e2
    TL = 1.8
    T = T0
    cnt = 0
    while True:
        if cnt % 50 == 0:
            now = time.perf_counter()
            elapsed =  now - start
            if elapsed > TL:
                break
            t = elapsed / TL
            T = pow(T0, 1 - t) * pow(T1, t)
        if getrandbits(1):
            d = randint(0, D - 1)
            q = randint(0, 25)
            old = out[d]
            out[d] = q
            tmp = scoring()
            p = exp((tmp - score) / T)
            r = random()
            if tmp > score or r < p:
                score = tmp
            else:
                out[d] = old
        else:
            d1 = randint(0, D - 2)
            d2 = randint(d1 + 1, min(d1 + 16, D - 1))
            out[d1], out[d2] = out[d2], out[d1]
            tmp = scoring()
            p = exp((tmp - score) / T)
            r = random()
            if tmp > score or r < p:
                score = tmp
            else:
                out[d1], out[d2] = out[d2], out[d1]
        cnt += 1

D = int(input())
C = list(map(int, input().split()))
S = [list(map(int, input().split())) for _ in range(D)]
out = [randint(0, 25) for _ in range(D)]
sc = sum(C)
score = scoring()
solve(score)
for i in out:
    print(i + 1)