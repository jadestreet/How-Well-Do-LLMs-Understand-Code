import math
#import sys
#input = sys.stdin.readline

def make_divisors(n):
    divisors = []
    for i in range(1, int(n**0.5)+1):
        if n % i == 0:
            divisors.append(i)
            if i != n // i:
                divisors.append(n//i)

    # divisors.sort()
    return divisors

def ValueToBits(x,digit):
    res = [0 for i in range(digit)]
    now = x
    for i in range(digit):
        res[i]=now%2
        now = now >> 1
    return res

def BitsToValue(arr):
    n = len(arr)
    ans = 0
    for i in range(n):
        ans+= arr[i] * 2**i
    return ans

def ZipArray(a):
    aa = [[a[i],i]for i in range(n)]

    aa.sort(key = lambda x : x[0])
    for i in range(n):
        aa[i][0]=i+1
    aa.sort(key = lambda x : x[1])
    b=[aa[i][0] for i in range(len(a))]
    return b

def ValueToArray10(x, digit):
    ans = [0 for i in range(digit)]
    now = x
    for i in range(digit):
        ans[digit-i-1] = now%10
        now = now //10
    return ans

def Zeros(a,b):
    if(b<=-1):
        return [0 for i in range(a)]
    else:
        return [[0 for i in range(b)] for i in range(a)]

def AddV2(v,w):
    return [v[0]+w[0],v[1]+w[1]]

dir4 = [[1,0],[0,1],[-1,0],[0,-1]]


def clamp(x,y,z):
    return max(y,min(z,x))

class Bit:
    def __init__(self, n):
        self.size = n
        self.tree = [0] * (n + 1)
 
    def sum(self, i):
        s = 0
        while i > 0:
            s += self.tree[i]
            i -= i & -i
        return s
 
    def add(self, i, x):
        while i <= self.size:
            self.tree[i] += x
            i += i & -i
            
#
def Zaatsu(a):
    a.sort()
    now = a[0][0]
    od = 0
    for i in range(n):
        if(now==a[i][0]):
            a[i][0]=od
        else:
            now = a[i][0]
            od+=1
            a[i][0] = od
    
    a.sort(key = lambda x : x[1])
    return a

class UnionFind:
    def __init__(self, n):
        self.par = [i for i in range(n+1)]
        self.rank = [0] * (n+1)

    # 検索
    def find(self, x):
        if self.par[x] == x:
            return x
        else:
            self.par[x] = self.find(self.par[x])
            return self.par[x]

    # 併合
    def union(self, x, y):
        x = self.find(x)
        y = self.find(y)
        if self.rank[x] < self.rank[y]:
            self.par[x] = y
        else:
            self.par[y] = x
            if self.rank[x] == self.rank[y]:
                self.rank[x] += 1

    # 同じ集合に属するか判定
    def same_check(self, x, y):
        return self.find(x) == self.find(y)


'''
def cmb(n, r, p):
    if (r < 0) or (n < r):
        return 0
    r = min(r, n - r)
    return fact[n] * factinv[r] * factinv[n-r] % p

p = 2
N = 10 ** 6 + 2
fact = [1, 1]  # fact[n] = (n! mod p)
factinv = [1, 1]  # factinv[n] = ((n!)^(-1) mod p)
inv = [0, 1]  # factinv 計算用

for i in range(2, N + 1):
    fact.append((fact[-1] * i) % p)
    inv.append((-inv[p % i] * (p // i)) % p)
    factinv.append((factinv[-1] * inv[-1]) % p)

'''

def rl(x):
    return range(len(x))

# a = list(map(int, input().split()))

#################################################
#################################################
#################################################
#################################################

#31-

s = input()
x,y = list(map(int, input().split()))

now = 0
right = 0
while(True):
    if(len(s)==now):
        break
    if(s[now]=='T'):
        break
    right+=1
    now+=1
#
x -= right
chain = 0
xy = 0
seg = [[],[]]
while(True):
    if(len(s)==now):
        break
    if(s[now]=='T'):
        
        if(chain>0):
            seg[xy].append(chain)
            chain=0
        xy = 1-xy
    else:
        chain+=1
    now+=1

if(chain>0):
    seg[xy].append(chain)

#print(seg,x,y)


n = len(seg[0])
m = sum(seg[0])

if(abs(x)>m):
    print("No")
    exit()

dp=[[0 for i in range(m+1)] for i in range(n+1)]
dp[0][0]=1

for i in range(n):
    nowlen = seg[0][i]
    for j in range(m+1):
        if(dp[i][j]==1):
            if(j+nowlen<=m):
                dp[i+1][j+nowlen]=1
            if(j-nowlen>=0):
                dp[i+1][j-nowlen]=1
                
#print(dp)
if(dp[-1][abs(x)]==0):
    print("No")
    exit()

n = len(seg[1])
m = sum(seg[1])

if(abs(y)>m):
    print("No")
    exit()

dp=[[0 for i in range(m+1)] for i in range(n+1)]
dp[0][0]=1

for i in range(n):
    nowlen = seg[1][i]
    for j in range(m+1):
        if(dp[i][j]==1):
            if(j+nowlen<=m):
                dp[i+1][j+nowlen]=1
            if(j-nowlen>=0):
                dp[i+1][j-nowlen]=1
                
#print(dp)
if(dp[-1][abs(y)]==0):
    print("No")
    exit()

print("Yes")





