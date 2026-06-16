def getN():
    return int(input())
def getNM():
    return map(int, input().split())
def getList():
    return list(map(int, input().split()))
def getArray(intn):
    return [int(input()) for i in range(intn)]
def input():
    return sys.stdin.readline().rstrip()
def rand_N(ran1, ran2):
    return random.randint(ran1, ran2)
def rand_List(ran1, ran2, rantime):
    return [random.randint(ran1, ran2) for i in range(rantime)]
def rand_ints_nodup(ran1, ran2, rantime):
  ns = []
  while len(ns) < rantime:
    n = random.randint(ran1, ran2)
    if not n in ns:
      ns.append(n)
  return sorted(ns)

def rand_query(ran1, ran2, rantime):
  r_query = []
  while len(r_query) < rantime:
    n_q = rand_ints_nodup(ran1, ran2, 2)
    if not n_q in r_query:
      r_query.append(n_q)
  return sorted(r_query)

from collections import defaultdict, deque, Counter
from sys import exit
from decimal import *
import heapq
import math
from fractions import gcd
import random
import string
import copy
from itertools import combinations, permutations, product
from operator import mul
from functools import reduce
from bisect import bisect_left, bisect_right

import sys
sys.setrecursionlimit(1000000000)
mod = 10 ** 9 + 7


#############
# Main Code #
#############

A, B = getNM()
A -= 1
B -= 1

maze = [['#'] * 100 for i in range(100)]

# 右半分を黒で塗る
for i in range(100):
    for j in range(50, 100):
        maze[i][j] = "."

for i in range((A + 25 - 1) // 25):
    for j in range(25):
        maze[2 * i][2 * j] = '.'
        if i == ((A + 25 - 1) // 25) - 1 and j == (A % 25) - 1:
            break

for i in range((B + 25 - 1) // 25):
    for j in range(25):
        maze[2 * i][2 * j + 51] = '#'
        if i == ((B + 25 - 1) // 25) - 1 and j == (B % 25) - 1:
            break

print(len(maze), len(maze[0]))
for i in maze:
    print(''.join(i))