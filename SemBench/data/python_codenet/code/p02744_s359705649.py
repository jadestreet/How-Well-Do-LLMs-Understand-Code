import sys
input = sys.stdin.readline
sys.setrecursionlimit(10**7)
from collections import Counter, deque
from collections import defaultdict
from itertools import combinations, permutations, accumulate, groupby, product
from bisect import bisect_left,bisect_right
from heapq import heapify, heappop, heappush
from math import floor, ceil
from operator import itemgetter
def I(): return int(input())
def MI(): return map(int, input().split())
def LI(): return list(map(int, input().split()))
def LI2(): return [int(input()) for i in range(n)]
def MXI(): return [[LI()]for i in range(n)]
def printns(x): print('\n'.join(x))
def printni(x): print('\n'.join(list(map(str,x))))
inf = 10**17
mod = 10**9 + 7
#s=input().rstrip()

n=I()
lis=[[]for i in range(n)]
lis[0].append([1])
for i in range(n-1):
    for j in lis[i]:
        for m in range(max(j)+1):
            lis[i+1].append(j+[m+1])
        #print(max(j))
#print(lis[n-1])
alpha=["a","b","c","d","e","f","g","h","i","j"]
for u in lis[n-1]:
    ans=""
    for j in u:
        ans+=alpha[j-1]
    print(ans)