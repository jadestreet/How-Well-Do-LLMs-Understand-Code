h, w = map(int, input().split())
A = [list(str(input())) for i in range(h)]

n = h*w

def Find(x, par):
    if par[x] < 0:
        return x
    else:
        par[x] = Find(par[x], par)
        return par[x]

def Unite(x, y, par, rank):
    x = Find(x, par)
    y = Find(y, par)

    if x != y:
        if rank[x] < rank[y]:
            par[y] += par[x]
            par[x] = y
        else:
            par[x] += par[y]
            par[y] = x
            if rank[x] == rank[y]:
                rank[x] += 1

def Same(x, y, par):
    return Find(x, par) == Find(y, par)

def Size(x, par):
    return -par[Find(x, par)]

par = [-1]*n
rank = [0]*n

for i in range(h):
    for j in range(w):
        idx1 = i*w+j
        idx2 = i*w+(w-1-j)
        idx3 = (h-1-i)*w+j
        Unite(idx1, idx2, par, rank)
        Unite(idx1, idx3, par, rank)
X = [0]*26
for i in range(h):
    for j in range(w):
        k = ord(A[i][j])-ord('a')
        X[k] += 1
temp = []
for i in range(26):
    if X[i] > 0:
        temp.append(X[i])
S = []
for i in range(h*w):
    if par[i] < 0:
        S.append(-par[i])

#print(temp)
#print(S)
S.sort(reverse=True)
import heapq
temp = [-1*t for t in temp]
heapq.heapify(temp)
for s in S:
    if temp:
        t = heapq.heappop(temp)*(-1)
        if t >= s:
            heapq.heappush(temp, (-1)*(t-s))
        else:
            print('No')
            exit()
    else:
        print('No')
        exit()
else:
    print('Yes')
