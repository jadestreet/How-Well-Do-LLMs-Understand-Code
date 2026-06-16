abc=list("abcdefghijklmnopqrstuvwxyz")

class SegmentTree:
    def __init__(self, init_value: list, segfunc, ide_ele):
        n = len(init_value)
        self.N0 = 1 << (n - 1).bit_length()
        self.ide_ele = ide_ele
        self.data = [ide_ele] * (2 * self.N0)
        self.segfunc = segfunc
        
        for i, x in enumerate(init_value):
            self.data[i + self.N0 - 1] = x
        for i in range(self.N0 - 2, -1, -1):
            self.data[i] = self.segfunc(self.data[2 * i + 1], self.data[2 * i + 2])
    
    def update(self, k: int, x):
        k += self.N0 - 1
        ############################
        self.data[k] = x
        ###########################
        while k:
            k = (k - 1) // 2
            self.data[k] = self.segfunc(self.data[k * 2 + 1], self.data[k * 2 + 2])
    
    def query(self, left: int, right: int):
        L = left + self.N0
        R = right + self.N0
        res = self.ide_ele
        ##########################
        a, b = [], []
        while L < R:
            if L & 1:
                a.append(L - 1)
                L += 1
            if R & 1:
                R -= 1
                b.append(R - 1)
            L >>= 1
            R >>= 1
        for i in a + b[::-1]:
            res = self.segfunc(res, self.data[i])
        ##########################
        return res



idx={}
for i in range(len(abc)):
    idx[abc[i]]=i
#print(idx)
N=int(input())
S=list(input())
Q=int(input())
L=[[0]*(N+1) for _ in range(26)]

def add(a,b):
    return a+b


for i in range(N):
    s=S[i]
    L[idx[s]][i+1]=1
    

segdict={}
for i in range(26):
    segdict[i]=SegmentTree(L[i],add,0)

for i in range(Q):
    query=input().split()
    num=int(query[0])

    if num==1:
        i=int(query[1])
        c=query[2]
        nows=S[i-1]
        segdict[idx[nows]].update(i,0)
        segdict[idx[c]].update(i,1)
        S[i-1]=c
    else:
        l=int(query[1])
        r=int(query[2])
        sub=0
        for j in range(26):
            x=segdict[j].query(l,r+1)
            if x>0:
                sub+=1
        print(sub)