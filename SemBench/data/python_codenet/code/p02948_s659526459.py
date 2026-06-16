import sys
from collections import Counter
from collections import deque
import heapq
import math
import fractions
import bisect
def input(): return sys.stdin.readline().strip()
def mp(): return map(int,input().split())
def lmp(): return list(map(int,input().split()))

n,m=mp()
l=[lmp() for i in range(n)]
l.append([10**6,10**6])
val=[]
heapq.heapify(val)
ans=0
c=0
l=sorted(l,key=lambda x: x[0],reverse=True)
for i in range(1,m+1):
    while l[-1][0]==i:
        q=l.pop()
        heapq.heappush(val,(-1)*q[1])
        c+=1
    if c>0:
        ans-=heapq.heappop(val)
        c-=1
print(ans)