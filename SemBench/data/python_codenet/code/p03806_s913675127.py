# -*- coding: utf-8 -*-
import sys
import math
import os
import itertools
import string
import heapq
import _collections
from collections import Counter
from collections import defaultdict
from functools import lru_cache
import bisect


class Scanner():
    @staticmethod
    def int():
        return int(sys.stdin.readline().rstrip())

    @staticmethod
    def string():
        return sys.stdin.readline().rstrip()

    @staticmethod
    def map_int():
        return [int(x) for x in Scanner.string().split()]

    @staticmethod
    def string_list(n):
        return [input() for i in range(n)]

    @staticmethod
    def int_list_list(n):
        return [Scanner.map_int() for i in range(n)]

    @staticmethod
    def int_cols_list(n):
        return [int(input()) for i in range(n)]


class Math():
    @staticmethod
    def gcd(a, b):
        if b == 0:
            return a
        return Math.gcd(b, a % b)

    @staticmethod
    def lcm(a, b):
        return (a * b) // Math.gcd(a, b)

    @staticmethod
    def roundUp(a, b):
        return -(-a // b)

    @staticmethod
    def toUpperMultiple(a, x):
        return Math.roundUp(a, x) * x

    @staticmethod
    def toLowerMultiple(a, x):
        return (a // x) * x

    @staticmethod
    def nearPow2(n):
        if n <= 0:
            return 0
        if n & (n - 1) == 0:
            return n
        ret = 1
        while(n > 0):
            ret <<= 1
            n >>= 1
        return ret

    @staticmethod
    def sign(n):
        if n == 0:
            return 0
        if n < 0:
            return -1
        return 1

    @staticmethod
    def isPrime(n):
        if n < 2:
            return False
        if n == 2:
            return True
        if n % 2 == 0:
            return False
        d = int(n ** 0.5) + 1
        for i in range(3, d + 1, 2):
            if n % i == 0:
                return False
        return True


MOD = int(1e09) + 7
INF = int(1e09)


def main():
    # sys.stdin = open("sample.txt")
    N, Ma, Mb = Scanner.map_int()
    A = [0] * N
    B = [0] * N
    C = [0] * N

    for i in range(N):
        a, b, c = Scanner.map_int()
        A[i], B[i], C[i] = a, b, c
    dp = [[[INF for _ in range(401)] for _ in range(401)] for _ in range(41)]
    dp[0][0][0] = 0
    for i in range(N):
        for j in range(401):
            for k in range(401):
                if dp[i][j][k] == INF:
                    continue
                dp[i+1][j][k] = min(dp[i+1][j][k], dp[i][j][k])
                dp[i+1][j + A[i]][k + B[i]] = min(
                    dp[i+1][j + A[i]][k + B[i]], dp[i][j][k] + C[i])

    ans = INF
    for i in range(1, 401):
        for j in range(1, 401):
            if dp[N][i][j] == INF:
                continue
            if Ma * j == Mb * i:
                ans = min(ans, dp[N][i][j])
    if ans == INF:
        ans = -1
    print(ans)


if __name__ == "__main__":
    main()
