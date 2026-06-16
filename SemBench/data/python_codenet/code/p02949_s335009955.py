#負の閉路検出
#n=頂点数 e=[[a,b,c],[]...](a~bの距離がc)
def find_negative_loop(n,e):
  d=n*[10**20];d[0]=0
  for h in range(n):
    for i,j,k in e:
      if d[j]>d[i]+k:
        d[j]=d[i]+k
        if h==n-1:return True
  return False

#DAG判定
#n=頂点数 e=隣接リスト
#flag=0...DAG判定　flag=1...トポロジカルソート
from collections import deque
def find_loop(n,e,flag):
  x=[0]*n
  d=deque()
  t=[]
  c=0
  for i in range(n):
    for j in e[i]:x[j]+=1
  for i in range(n):
    if x[i]==0:
      d.append(i)
      t.append(i)
      c+=1
  while d:
    i=d.popleft()
    for j in e[i]:
      x[j]-=1
      if x[j]==0:
        d.append(j)
        t.append(j)
        c+=1
  if flag==0:return c==n
  else:return t

#ベルマンフォード(d[i]=頂点sから頂点iの最短距離)
#単一始点最短経路(負の辺対応)
#s=始点 n=頂点数 e=[[a,b,c],[]...](a~bの距離がc)
def bellman_ford(s,n,e):
	inf=10**20;d=[inf]*n;d[s]=0
	while 1:
		f=True
		for i,j,k in e:
			if d[i]!=inf and d[j]>d[i]+k:d[j]=d[i]+k;f=False
		if f:break
	return d

#グラフ上でのBFS
#s=始点 n=頂点数 e=隣接リスト
def glaph_bfs(s,n,e):
  ans=[0]*n
  Q=[s]
  visited={s}
  while Q:
    P=[]
    for i in Q:
      ans[i]=1
      for j in e[i]:
        if j in visited:continue
        visited.add(j)
        P.append(j)
    Q=P
  return ans

n,m,p=map(int,input().split())
ef=[[]for _ in range(n)]
ee=[[]for _ in range(n)]
e=[]
for _ in range(m):
  a,b,c=map(int,input().split())
  a-=1
  b-=1
  c-=p
  ef[a].append(b)
  ee[b].append(a)
  e.append([a,b,c])
eff=glaph_bfs(0,n,ef)
eef=glaph_bfs(n-1,n,ee)
edge=[]
for a,b,c in e:
  if eff[a]==1 and eef[a]==1 and eff[b]==1 and eef[b]==1:
    edge.append([a,b,-c])
if find_negative_loop(n,edge):print(-1);exit()
print(max(-bellman_ford(0,n,edge)[n-1],0))