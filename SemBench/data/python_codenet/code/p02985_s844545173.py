#ABC133-E Virus Tree 2
"""
問題：
n頂点の木(辺の情報が与えられる)に対して、k色で頂点を塗り分ける時、距離が2以下の頂点に対して同じ色
を塗ってはいけないという制約下で、何通りの塗り分け方が存在するか。

解法：
ある頂点xに対して、その親が既に塗られている場合、xの子の数をcとして、xの子の塗り方の総数は
(k-2)Pc
なお、木の頂点の塗り方をk通りとした場合、それ以降は子の塗り方さえ考えれば良いので、x自体の塗り方の総数は
既に考慮されている。

また、根については、根と同時にその子について一気に決定する必要があり、
根の子の個数をcとして、kP(c+1)としなけらばならない。
"""
import sys
readline = sys.stdin.buffer.readline
def even(n): return 1 if n%2==0 else 0
mod = 10**9+7

#順列modあり
def factrial_memo(n=10**5+1,mod=10**9+7): # [1,n)までの階乗と逆元の階乗
    fact = [1, 1]  # fact[n] = (n! mod mod)
    factinv = [1, 1]  # factinv[n] = ((n!)^(-1) mod mod)
    inv = [0, 1]  # factinv 計算用
    for i in range(2, n + 1):
        fact.append((fact[-1] * i) % mod)
        inv.append((-inv[mod % i] * (mod // i)) % mod)
        factinv.append((factinv[-1] * inv[-1]) % mod)
    return fact,factinv # warning:1-indexed list

#そのまま使う
fact,factinv = factrial_memo()

def permutation(n,m,mod=10**9+7): #nPm
    return fact[n]*factinv[n-m]%mod

n,k = map(int,readline().split())

g = [[] for _ in range(n)] #隣接リスト
for i in range(n-1):
    a,b = map(int,readline().split())
    a,b = a-1,b-1
    g[a].append(b)
    g[b].append(a)

#親のノードに子を入れてくdfs
root = 0 #根
stack = [0]
parent = [0]*n
order = []
while stack:
    x = stack.pop()
    order.append(x)
    for i in g[x]:
        if i == parent[x]:
            continue
        parent[i] = x
        stack.append(i)

ans = 1

for x in order: #親
    if len(g[x]) == 1 and x != root:
        continue
    if len(g[x]) >= k: #条件を満たす彩色ができない
        print(0)
        exit()
    if x == root:
        ans *= permutation(k,len(g[x])+1)
        ans %= mod
    else:
        ans *= permutation(k-2,len(g[x])-1)
        ans %= mod

print(ans)