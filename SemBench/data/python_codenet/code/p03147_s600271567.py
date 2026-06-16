#!/usr/bin/env python3
import sys
import math
import decimal
import itertools
from itertools import product
from functools import reduce

def main():
    N = int(input())
    h = list(map(int, input().split()))

    ans = 0
    while h != [0] * N:
        if h[0] != 0:
            ans += 1
        for i in range(1, N):
            if h[i - 1] == 0 and h[i] != 0:
                ans += 1
        for i in range(N):
            if h[i] > 0:
                h[i] -= 1
    print(ans)


def input():
    return sys.stdin.readline()[:-1]
def gcd(*numbers):
    return reduce(math.gcd, numbers)
def lcm_base(x, y):
    return (x * y) // math.gcd(x, y)
def lcm(*numbers):
    return reduce(lcm_base, numbers, 1)
def sort_zip(a:list, b:list):
    z = zip(a, b)
    z = sorted(z)
    a, b = zip(*z)
    a = list(a)
    b = list(b)
    return a, b

if __name__ == '__main__':
    main()
