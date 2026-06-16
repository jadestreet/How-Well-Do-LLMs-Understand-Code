#template
def inputlist(): return [int(k) for k in input().split()]
#template

def factorization(n):
    arr = []
    temp = n
    for i in range(2, int(-(-n**0.5//1))+1):
        if temp%i==0:
            cnt=0
            while temp%i==0:
                cnt+=1
                temp //= i
            arr.append([i, cnt])

    if temp!=1:
        arr.append([temp, 1])

    if arr==[]:
        arr.append([n, 1])

    return arr


N = int(input())
if N == 1:
    print(0)
    exit()
dp = [[0]*101 for _ in range(N+1)]
for i in range(2,N+1):
    li = factorization(i)
    n = len(li)
    li0 = [0]*n
    li1 = {}
    for k in range(n):
        li0[k] = li[k][0]
        li1[li[k][0]] = li[k][1]
    for j in range(2,101):
        if j in li0:
            dp[i][j] = dp[i-1][j] + li1[j]
            continue
        dp[i][j] = dp[i-1][j]

li = dp[N]
li.sort()
from bisect import bisect_right
indexa = bisect_right(li,0)
lia = li[indexa:]

na = len(lia)
c2 = 0
c4 = 0
c14 = 0
c24 = 0
c74 = 0
for i in range(na):
    if lia[i] >= 2:
        c2+=1
    if lia[i] >= 4:
        c4+=1
    if lia[i] >= 14:
        c14 +=1
    if lia[i] >= 24:
        c24+=1
    if lia[i] >= 74:
        c74+=1
d4_2 = c2-c4
d14_4 = c4 - c14
d24_2 = c2 - c24

def comb2(i):
    return i*(i-1)//2
def comb3(i):
    return i*(i-1)*(i-2)//6

ans = d4_2*comb2(c4) + 3*comb3(c4) + d14_4*c14 + 2*comb2(c14) + d24_2*c24 + 2*comb2(c24) +c74
print(ans)