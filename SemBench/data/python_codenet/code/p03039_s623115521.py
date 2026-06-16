# coding: utf-8
import re
import math
import fractions
import random
import time
#import numpy as np
mod=int(10**9+7)
inf=int(10**20)
fac=[1]*250000
for a in range(2,250000):
    fac[a]=fac[a-1]*a%mod
class union_find():
    def __init__(self,n):
        self.n=n
        self.P=[a for a in range(N)]
        self.rank=[0]*n

    def find(self,x):
        if(x!=self.P[x]):self.P[x]=self.find(self.P[x])
        return self.P[x]

    def same(self,x,y):
        return self.find(x)==self.find(y)

    def link(self,x,y):
        if self.rank[x]<self.rank[y]:
            self.P[x]=y
        elif self.rank[y]<self.rank[x]:
            self.P[y]=x
        else:
            self.P[x]=y
            self.rank[y]+=1

    def unite(self,x,y):
        self.link(self.find(x),self.find(y))

    def size(self):
        S=set()
        for a in range(self.n):
            S.add(self.find(a))
        return len(S)
def bin_(num,size):
    A=[0]*size
    for a in range(size):
        if (num>>(size-a-1))&1==1:
            A[a]=1
        else:
            A[a]=0
    return A
def comb(n,r):return math.factorial(n)//math.factorial(n-r)//math.factorial(r)
def next_comb(num,size):
    x=num&(-num)
    y=num+x
    z=num&(~y)
    z//=x
    z=z>>1
    num=(y|z)
    if(num>=(1<<size)):return False
    else:
        return num



def comb_(n,r):return fac[n]*pow(fac[n-r],mod-2,mod)*pow(fac[r],mod-2,mod)
#main
def solve():
    return

#入力
N,M,K=map(int,input().split())
sum_=0
for a in range(1,N):
    sum_+=M*M*abs(N-a)*a*comb_(N*M-2,K-2)
    sum_%=mod
for a in range(1,M):
    sum_+=N*N*abs(M-a)*a*comb_(N*M-2,K-2)
    sum_%=mod

print(sum_)
