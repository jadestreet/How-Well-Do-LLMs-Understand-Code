H, W = map(int, input().split())
S = [list(input()) for _ in range(H)]
edge = []

# 横の比較
for i in range(H):
    for j in range(W-1):
        if S[i][j] != S[i][j+1]:
            edge.append((i*W+j,i*W+j+1))
# 縦の比較
for i in range(H-1):
    for j in range(W):
        if S[i][j] != S[i+1][j]:
            edge.append((i*W+j, (i+1)*W+j))

class UnionFind():
    '''
    UnionFindでグラフの状態を管理する
    '''
    def __init__(self, n):
        self.n = n
        self.root = [-1]*(n+1)
        self.rnk = [0]*(n+1)

    def is_root(self, x):
        return self.root[x] < 0

    def find_root(self, x):
        '''
        ルートのノードを見つける
        '''
        if(self.root[x] < 0):
            return x
        else:
            self.root[x] = self.find_root(self.root[x])
            return self.root[x]

    def unite(self, x, y):
        '''
        ノード同士を連結する
        '''
        x = self.find_root(x)
        y = self.find_root(y)
        if(x == y):
            return 
        elif(self.rnk[x] > self.rnk[y]):
            self.root[x] += self.root[y]
            self.root[y] = x
        else:
            self.root[y] += self.root[x]
            self.root[x] = y
            if(self.rnk[x] == self.rnk[y]):
                self.rnk[y] += 1

    def is_same_group(self, x, y):
        '''
        同一のルーツを持つかどうか調査する
        '''
        return self.find_root(x) == self.find_root(y)

    def count(self, x):
        return -self.root[self.find_root(x)]

union = UnionFind(H*W)
for l, r in edge:
    union.unite(l, r)
cnt = [0] * (H*W)
for i in range(H*W):
    c = union.find_root(i)
    if S[i//W][i%W] == "#":
        cnt[c] += 1

ans = 0
for i in range(H*W):
    if union.is_root(i):
        r = union.find_root(i)
        c = union.count(i)
        ans += cnt[r] * (c-cnt[r])
print(ans)
