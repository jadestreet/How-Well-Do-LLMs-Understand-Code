def sep():
    return map(int,input().strip().split(" "))
def lis():
    return list(sep())

class MergeFind:
    def __init__(self, n):
        self.parent = list(range(n))
        self.size = [1] * n
        self.num_sets = n
        # self.lista = [[_] for _ in range(n)]

    def find(self, a):
        to_update = []
        while a != self.parent[a]:
            to_update.append(a)
            a = self.parent[a]
        for b in to_update:
            self.parent[b] = a
        return self.parent[a]

    def merge(self, a, b):
        a = self.find(a)
        b = self.find(b)
        if a == b:
            return
        if self.size[a] < self.size[b]:
            a, b = b, a
        self.num_sets -= 1
        self.parent[b] = a
        self.size[a] += self.size[b]
        # self.lista[a] += self.lista[b]
        # self.lista[b] = []

    def set_size(self, a):
        return self.size[self.find(a)]

    def __len__(self):
        return self.num_sets

n,m,k=sep()
d=MergeFind(n)
temp=[]
for _ in range(m):
    a,b=sep()
    a -= 1
    b -= 1
    temp.append((a,b))
    d.merge(a,b)
ans=[0]*n
for i in range(n):
    ans[i]=d.set_size(i)-1
for _ in range(k):
    a, b = sep()
    a -= 1
    b -= 1
    temp.append((a, b))
for i in temp:
    a,b=i
    if d.find(a)==d.find(b):
        ans[a]-=1
        ans[b]-=1
print(*ans)



