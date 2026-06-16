import math
def P(n, r):
    return math.factorial(n)//math.factorial(n-r)
def C(n, r):
    return P(n, r)//math.factorial(r)

N = int(input())
moji =[]
for i in range(N):
    a = sorted(input())
    moji.append(''.join(a))


dic = {}
for i in moji:
    if i in dic:
        dic[i] += 1
    else:
        dic[i] = 1

ans = 0
for value in dic.values():
    if value >=2:
        ans+=C(value, 2)

print(ans)