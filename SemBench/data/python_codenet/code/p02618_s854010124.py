import time

START = time.time()

import random
import sys
input = sys.stdin.readline
Days = int(input())
C = list(map(int, input().split())) # 満足度低下
Ss = [list(map(int, input().split())) for _ in range(Days)]
# Ss[d][i]: d日目にiを開催したときの満足度

INF = 10**18
TIMELIMIT = 1.9


def outputToScore(T):
    last = [0]*26

    satisfied = 0
    for d, t in enumerate(T):
        t -= 1; d += 1
        satisfied += Ss[d-1][t]
        last[t] = d
        for i, c in enumerate(C):
            satisfied -= c*(d-last[i])
        # print(satisfied)
    return satisfied

def outputToScore2(T):
    last = [0]*26
    used = [[] for _ in range(26)]
    satisfied = 0
    for d, t in enumerate(T):
        t -= 1; d += 1
        satisfied += Ss[d-1][t]
        used[t].append(d)
        last[t] = d
        for i, c in enumerate(C):
            satisfied -= c*(d-last[i])
        # print(satisfied)
    return satisfied, used

def greedy():
    last = [0]*26
    T = []
    for d in range(Days):
        satisfied_max = -INF
        selected = -1
        for t in range(26):
            score_t = Ss[d][t]
            for j, c in enumerate(C):
                if t != j:
                    score_t -= c*(d+1-last[j])
            if score_t > satisfied_max:
                satisfied_max = score_t
                selected = t
        T.append(selected+1)
        last[selected] = d+1
    return T


def modifiedScore(d, aft, Used, T):
    bef = T[d-1]-1
    deltaSatis = Ss[d-1][aft] - Ss[d-1][bef]
    # d日目のコンテストをbefからaftに変える

    # bi-1 -> bi -> bi+1 を bi-1 -> bi+1
    befind = Used[bef].index(d)
    befday0 = 0 if befind == 0 else Used[bef][befind-1]
    befday2 = Days+1 if befind == len(Used[bef])-1 else Used[bef][befind+1]
    
    befd01 = d - befday0
    befd12 = befday2 - d
    befd02 = befday2-befday0
    deltaSatis -= C[bef]*(befd02*(befd02-1)//2) - C[bef]*(befd01*(befd01-1)//2 + befd12*(befd12-1)//2)

    # ai -> ai+1 を ai -> (insert) -> ai+1
    if len(Used[aft]) > 0:
        aftday0 = 0
        aftday2 = Days+1
        for a in Used[aft]:
            if a < d:
                aftday0 = a
            elif aftday2 == Days+1:
                aftday2 = a
        aftd01 = d - aftday0
        aftd12 = aftday2 - d
        aftd02 = aftd01 + aftd12
        deltaSatis += C[aft]*(aftd02*(aftd02-1)//2) - C[aft]*(aftd01*(aftd01-1)//2 + aftd12*(aftd12-1)//2)
    else:
        d01 = d
        d12 = Days+1 - d
        deltaSatis += C[aft] * Days*(Days+1)//2 - C[aft]*(d01*(d01-1)//2 + d12*(d12-1)//2)

    return deltaSatis


def update(Used, T, bef, aft, d):
    Used[bef].remove(d)
    inserted = False
    new = []
    for a in Used[aft]:
        if a > d and not inserted:
            inserted = True
            new.append(d)
        new.append(a)
    if not inserted:
        new.append(d)
    Used[aft] = new
    T[d-1] = aft+1
    return T, Used


def goingup(T, Used):
    d = random.randint(1, Days)
    bef = T[d-1]-1
    aft = random.randint(0, 25)

    if bef == aft:
        return T, Used

    if modifiedScore(d, aft, Used, T) > 0:
        T, Used = update(Used, T, bef, aft, d)
    return T, Used


def main():
    T = greedy()
    Satisfied, Used = outputToScore2(T)

    while time.time() - START < TIMELIMIT:
        T, Used = goingup(T, Used)
        
    print(*T, sep="\n")


def test():
    T = [int(input()) for _ in range(Days)] # 開催するコンテスト
    Q = int(input())
    Query = [list(map(int, input().split())) for _ in range(Q)]
    Satisfied, Used = outputToScore2(T)
    for d, aft in Query:
        aft -= 1
        bef = T[d-1]-1
        Satisfied += modifiedScore(d, aft, Used, T)
        T, Used = update(Used, T, T[d-1]-1, aft, d)
        print(Satisfied)


if __name__ == "__main__":
    main()
    # test()