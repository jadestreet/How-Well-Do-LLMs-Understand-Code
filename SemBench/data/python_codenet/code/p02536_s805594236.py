n,m=map(int,input().split())
xy = [map(int, input().split()) for _ in range(m)]
x, y = [list(i) for i in zip(*xy)]
ans=0

l=[-1]*n

def rootfind(a):
    changelist=[]
    while 1:
        if l[a-1]>0:
            changelist.append(a)
            a=l[a-1]
        else:
            break
    for e in changelist:
        l[e-1]=a
    return a


def rootunion(c,d):
    cr=rootfind(c)
    dr=rootfind(d)
    if cr==dr:
        pass
    else:
        l[cr-1]=dr


for j in range(m):
    p=x[j]
    q=y[j]
    rootunion(p,q)

for o in l:
    if o<0:
        ans+=1

print(ans-1)