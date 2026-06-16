# -*- coding: utf-8 -*-
import numpy as np
import sys
from collections import deque
from collections import defaultdict
import heapq
import collections
import itertools
import bisect


def zz():
    return list(map(int, sys.stdin.readline().split()))


def z():
    return int(sys.stdin.readline())


def S():
    return sys.stdin.readline()


def C(line):
    return [sys.stdin.readline() for _ in range(line)]


l, r, d = zz()
ans = 0
for i in range(l, r+1):
    if(i % d == 0):
        ans += 1
print(ans)
