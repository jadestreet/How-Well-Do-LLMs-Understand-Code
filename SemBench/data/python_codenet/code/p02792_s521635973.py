import sys
from collections import Counter
from collections import deque
import math
import bisect
def input(): return sys.stdin.readline().strip()
def mp(): return map(int,input().split())
def lmp(): return list(map(int,input().split()))

n=int(input())
grid=[[0]*10 for i in range(10)]
for i in range(1,n+1):
    a=int(str(i)[0])
    b=int(str(i)[-1])
    grid[a][b]+=1
ans=0
for i in range(10):
    for k in range(10):
        ans+=grid[i][k]*grid[k][i]
print(ans)