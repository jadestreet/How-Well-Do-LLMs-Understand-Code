from collections import defaultdict

mod=1000000007
def mpow2(n):
    ret=1
    while n>0:
        ret*=2
        ret%=mod
        n-=1
    return ret

def gcd(a,b):
    if a<0:
        a*=-1
    if b<0:
        b*=-1
    if a<b:
        a,b=b,a
    if a%b:
        return gcd(b,a%b)
    return b

shift=2**64
d=defaultdict(int)
n=int(input())
l=[]
cnt0=0
for i in range(n):
    a,b=map(int,input().split())
    if a==b==0:
        cnt0+=1
        continue
    elif a==0:
        b=1
    elif b==0:
        a=1
    else:
        g=gcd(a,b)
        a//=g
        b//=g
    l.append((a,b))
    d[a*shift+b]+=1
res=1
for p in l:
    a=p[0]
    b=p[1]
    c=d[a*shift+b]+d[-a*shift-b]
    if c==0:
        continue
    d[a*shift+b]=0
    d[-a*shift-b]=0
    a=-p[1]
    b=p[0]
    cc=d[a*shift+b]+d[-a*shift-b]
    d[a*shift+b]=0
    d[-a*shift-b]=0
    if cc==0:
        res*=mpow2(c)
        res%=mod
    else:
        res*=mpow2(c)+mpow2(cc)-1
        res%=mod
print((res+cnt0+mod-1)%mod)
