import sys
import math
from collections import defaultdict

sys.setrecursionlimit(10**7)
def input():
    return sys.stdin.readline()[:-1]

mod = 10**9 + 7

def I(): return int(input())
def II(): return map(int, input().split())
def III(): return list(map(int, input().split()))
def Line(N):
    read_all = [tuple(map(int, input().split())) for _ in range(N)]
    return map(list,zip(*read_all))

#################

from collections import deque

N,K = II()
t,d = Line(N)

x = []
for i in range(N):
    x.append([t[i],d[i]])

x.sort(key=lambda x: -x[1])

used = []
for i in range(K):
    used.append(x[i])

a = defaultdict(list)
for u in used:
    a[u[0]].append(u[1])

num = len(a.keys())

rem = []
for k in a.keys():
    if len(a[k])>=2:
        a[k].sort(reverse=True)
        for i in range(1,len(a[k])):
            rem.append(a[k][i])
rem.sort()
rem = deque(rem)

b = defaultdict(list)
for i in range(N):
    if a[t[i]]==[]:
        b[t[i]].append(d[i])

app = []
for k in b.keys():
    app.append(max(b[k]))
app.sort(reverse=True)
app = deque(app)

val = sum([used[i][1] for i in range(len(used))]) + num**2
temp = val
while (rem and app):
    re,ap = rem.popleft(), app.popleft()
    temp = temp-re+ap-num**2+(num+1)**2
    if val < temp:
        val = temp
    num += 1

print(val)