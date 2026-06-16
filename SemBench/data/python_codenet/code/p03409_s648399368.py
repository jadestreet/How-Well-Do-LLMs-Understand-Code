from collections import defaultdict
import sys
sys.setrecursionlimit(10**7)
def dfs(v,t,f,used):
    if v==t:
        return f
    used[v]=True
    for nv,cap in G[v].items():
        if not used[nv] and cap>0:
            d=dfs(nv,t,min(f,cap),used)
            if d>0:
                G[v][nv]-=d
                G[nv][v]+=d
                return d
    return 0

def Max_Flow(s,t):
    flow=0
    while(True):
        used=[False]*(2*N+2)
        f=dfs(s,t,INF,used)
        if f==0:
            return flow
        flow+=f

INF=float('inf')

N=int(input())
G=[defaultdict(int) for i in range(2*N+2)]
arr=[]
for i in range(2*N):
    x,y=map(int,input().split())
    arr.append((x,y))

for i in range(N,2*N):
    for j in range(N):
        a,b=arr[i]
        c,d=arr[j]
        if a>c and b>d:
            G[i+1][j+1]=1
            G[j+1][i+1]=0

for i in range(N):
    G[0][N+i+1]=1
    G[N+i+1][0]=0
    G[i+1][2*N+1]=1
    G[2*N+1][i+1]=0
res=Max_Flow(0,2*N+1)
print(res)