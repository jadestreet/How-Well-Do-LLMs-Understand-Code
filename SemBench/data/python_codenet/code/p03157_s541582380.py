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
import re
import queue
from decimal import *


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
        return [Scanner.string() for i in range(n)]

    @staticmethod
    def int_list_list(n):
        return [Scanner.map_int() for i in range(n)]

    @staticmethod
    def int_cols_list(n):
        return [Scanner.int() for i in range(n)]


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
    def divisor(n):
        res = []
        i = 1
        for i in range(1, int(n ** 0.5) + 1):
            if n % i == 0:
                res.append(i)
                if i != n // i:
                    res.append(n // i)
        return res

    @staticmethod
    def round_up(a, b):
        return -(-a // b)

    @staticmethod
    def is_prime(n):
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


def pop_count(x):
    x = x - ((x >> 1) & 0x5555555555555555)
    x = (x & 0x3333333333333333) + ((x >> 2) & 0x3333333333333333)
    x = (x + (x >> 4)) & 0x0f0f0f0f0f0f0f0f
    x = x + (x >> 8)
    x = x + (x >> 16)
    x = x + (x >> 32)
    return x & 0x0000007f


MOD = int(1e09) + 7
INF = int(1e15)

visited = None
S = None
H, W = None, None


def bfs(x, y):
    global visited
    if visited[y][x]:
        return 0
    q = []
    q.append((x, y))
    black = 0
    white = 0
    while q != []:
        x, y = q.pop()
        DIR = [(-1, 0), (1, 0), (0, 1), (0, -1)]
        for d in DIR:
            nx, ny = x + d[0], y + d[1]
            if 0 <= nx < W and 0 <= ny < H and S[y][x] != S[ny][nx] and not visited[ny][nx]:
                visited[ny][nx] = True
                if S[ny][nx] == '.':
                    white += 1
                else:
                    black += 1
                q.append((nx, ny))
    return black * white


def solve():
    global H, W
    global S
    global visited
    H, W = Scanner.map_int()
    S = Scanner.string_list(H)
    visited = [[False for _ in range(W)] for _ in range(H)]
    ans = 0
    for x in range(W):
        for y in range(H):
            ans += bfs(x, y)
    print(ans)


def main():
    # sys.stdin = open("sample.txt")
    # print('YNEOS'[not solve()::2])
    solve()


if __name__ == "__main__":
    main()
