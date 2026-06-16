# 19
from collections import Counter
import sys


def input(): return sys.stdin.readline().strip()
def I(): return int(input())
def LI(): return list(map(int, input().split()))
def IR(n): return [I() for i in range(n)]
def LIR(n): return [LI() for i in range(n)]
def SR(n): return [S() for i in range(n)]
def S(): return input()
def LS(): return input().split()


INF = float('inf')

n = I()
s = SR(n)
set_c = set(list(s[0]))
for elem in s:
    set_c = set_c & set(list(elem))
# print(set_c)
s = sorted(s, key=lambda x: len(x))[::-1]
d = {k: 51 for k in set_c}
for elem in s:
    c = Counter(list(elem))
    for k in d.keys():
        if k in c.keys():
            d[k] = min(d[k], c[k])
# print(d)
d = sorted(d.items(), key=lambda x: x[0])
# print(d)
ans = ''
for k, v in d:
    ans += k * v
print(ans)
