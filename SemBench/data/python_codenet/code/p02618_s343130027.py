from collections import Counter,defaultdict,deque
from heapq import heappop,heappush,heapify
import sys,bisect,math,itertools,fractions,pprint,time,random
sys.setrecursionlimit(10**8)
mod = 10**9+7
INF = float('inf')
def inp(): return int(sys.stdin.readline())
def inpl(): return list(map(int, sys.stdin.readline().split()))

def cal(T):
    res = 0
    last = [0] * 26
    for day in range(D):
        t = T[day]; t -= 1
        last[t] = 0
        res += s[day][t]
        for i in range(26):
            if i == t: continue
            last[i] += 1
            res -= c[i] * last[i]
    return res
start_time = time.time()
n = 26
D = inp()
c = inpl()
s = [inpl() for _ in range(D)]
last = [0] * n
res = [-1] * D
for d in range(D):
    ans = -1
    mx = -INF
    for i in range(n):
        now = s[d][i]
        for j in range(n):
            if i == j: continue
            now -= s[d][j] * (last[j]+1)
        if now > mx:
            mx = now
            ans = i
    res[d] = ans+1
    for j in range(n):
        last[j] += 1
        if j == ans: last[j] = 0
score = cal(res)
# print(now_score)
while time.time() - start_time < 1.83:
    td,tq = random.randrange(0,D), random.randrange(1,n+1)
    old_q = res[td]
    res[td] = tq
    now = cal(res)
    if now > score:
        score = now
    else:
        res[td] = old_q

for x in res:
    print(x)