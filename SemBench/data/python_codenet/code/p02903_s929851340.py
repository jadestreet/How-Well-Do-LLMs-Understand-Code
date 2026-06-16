import sys, math
from functools import lru_cache
from collections import defaultdict
from decimal import Decimal
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

def main():
    H, W, A, B = mi()
    ans = [[None]*W for i in range(H)]
    for i in range(B):
        for j in range(A):
            ans[i][j] = '0'
        for j in range(A, W):
            ans[i][j] = '1'
    for i in range(B, H):
        for j in range(A):
            ans[i][j] = '1'
        for j in range(A, W):
            ans[i][j] = '0'

    print(*[''.join(ans[i]) for i in range(H)], sep='\n')

if __name__ == '__main__':
    main()
