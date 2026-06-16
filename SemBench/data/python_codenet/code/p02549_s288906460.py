import sys
sys.setrecursionlimit(10**7)

readline = sys.stdin.buffer.readline
def readstr():return readline().rstrip().decode()
def readstrs():return list(readline().decode().split())
def readint():return int(readline())
def readints():return list(map(int,readline().split()))
def printrows(x):print('\n'.join(map(str,x)))
def printline(x):print(' '.join(map(str,x)))


mod = 998244353
n,k = readints()
s = [readints() for i in range(k)]

a = [0] * (n+1)
a[1] = 1

b = [0] * k

for i in range(2,n+1):
    for j in range(k):
        l,r = s[j]
        if i-l>0:
            b[j] += a[i-l]
        if i-r-1>0:
            b[j] -= a[i-r-1]
        a[i] += b[j]
        a[i] %= mod

print(a[-1])







