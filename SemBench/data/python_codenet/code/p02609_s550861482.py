from sys import stdin

def mpow(n, p, mod):
    if mod == 0:
        return 0
    r = 1
    while p > 0:
        if p & 1 == 1:
            r = r * n % mod
        n = n * n % mod
        p >>= 1
    return r
def popcount(u):
    if u == 0:
        return 0
    a = u % bin(u).count('1')
    return 1 + popcount(a)
def main():
    input = stdin.readline
    n = int(input())
    x = '0b' + input()
    xs = int(x, 0)
    xc = x.count('1')
    xsp = mpow(xs, 1, xc + 1)
    xsm = mpow(xs, 1, xc - 1)
    for i in range(2, n + 2):
        if x[i] == '0':
            y = xsp + mpow(2, n - i + 1, xc + 1)
            y = mpow(y, 1, xc + 1)
        elif xc == 1:
            print(0)
            continue
        else:
            y = xsm - mpow(2, n - i + 1, xc - 1)
            y = mpow(y, 1, xc - 1)
        print(popcount(y) + 1)
main()