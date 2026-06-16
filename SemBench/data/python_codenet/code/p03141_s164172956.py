import sys
import math
from collections import defaultdict
from bisect import bisect_left, bisect_right

sys.setrecursionlimit(10**7)
def input():
    return sys.stdin.readline()[:-1]

mod = 10**9 + 7

def I(): return int(input())
def LI(): return list(map(int, input().split()))
def LIR(row,col):
    if row <= 0:
        return [[] for _ in range(col)]
    elif col == 1:
        return [I() for _ in range(row)]
    else:
        read_all = [LI() for _ in range(row)]
        return map(list, zip(*read_all))

#################

N = I()
A,B = LIR(N,2)

from operator import itemgetter
def index_sort(A):
    A_sort = sorted(enumerate(A),key=itemgetter(1))
    index = [a[0] for a in A_sort]
    sorted_A = [a[1] for a in A_sort]
    return index, sorted_A

C = [A[i]+B[i] for i in range(N)]
index,_ = index_sort(C)
ans = 0
for i in range(N)[::-1]:
    if i%2 == (N-1)%2:
        ans += A[index[i]]
    else:
        ans -= B[index[i]]

print(ans)