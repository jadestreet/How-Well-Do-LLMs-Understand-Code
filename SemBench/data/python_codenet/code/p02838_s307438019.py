import sys
def input(): return sys.stdin.readline().strip()
def mapint(): return map(int, input().split())
sys.setrecursionlimit(10**9)

N = int(input())
As = list(mapint())
mod = 10**9+7

bits = [0]*70
for a in As:
    for l in range(a.bit_length()):
        if (a>>l)&1:
            bits[l] += 1

ans = 0
for i in range(70):
    one = bits[i]
    zero = N-one
    mul = pow(2, i, mod)
    ans += one*zero*mul
    ans %= mod

print(ans)