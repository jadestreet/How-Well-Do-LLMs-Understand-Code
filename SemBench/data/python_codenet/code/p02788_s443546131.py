import bisect
import sys
input=sys.stdin.readline
n,d,a=map(int,input().split())
l=[list(map(int,input().split())) for i in range(n)]
l.sort()

data0=[0]*(n+1)
data1=[0]*(n+1)

def _add(data,k,x):
  while k<=n:
    data[k]+=x
    k+=k&-k

def add(l,r,x):
  _add(data0,l,-x*(l-1))
  _add(data0,r,x*(r-1))
  _add(data1,l,x)
  _add(data1,r,-x)

def _get(data,k):
  s=0
  while k:
    s+=data[k]
    k-=k&-k
  return s

def query(l,r):
  return _get(data1,r-1)*(r-1)+_get(data0,r-1)-_get(data1,l-1)*(l-1)-_get(data0,l-1)

x=[]
for i in range(n):
  x.append(l[i][0])
  add(i+1,i+2,l[i][1])

Right=[]
for i in range(n):
  Right.append(bisect.bisect_right(x,x[i]+2*d))

p=0
ans=0
while p<n:
  Q=query(p+1,p+2)
  add(p+1,Right[p]+1,-((Q+a-1)//a)*a)
  ans+=(Q+a-1)//a
  p=min(p+1,n-1)
  while query(p+1,p+2)<=0:
    p+=1
    if p==n:
      break
print(ans)