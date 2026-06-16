class UnionFind():
    # 作りたい要素数nで初期化
    # 使用するインスタンス変数の初期化
    def __init__(self, n):
        self.n = n
        # root[x]<0ならそのノードが根かつその値が木の要素数
        # rootノードでその木の要素数を記録する
        self.root = [-1]*(n+1)
        # 木をくっつける時にアンバランスにならないように調整する
        self.rnk = [0]*(n+1)

    # ノードxのrootノードを見つける
    def Find_Root(self, x):
        if(self.root[x] < 0):
            return x
        else:
            # ここで代入しておくことで、後の繰り返しを避ける
            self.root[x] = self.Find_Root(self.root[x])
            return self.root[x]
    # 木の併合、入力は併合したい各ノード
    def Unite(self, x, y):
        # 入力ノードのrootノードを見つける
        x = self.Find_Root(x)
        y = self.Find_Root(y)
        # すでに同じ木に属していた場合
        if(x == y):
            return 
        # 違う木に属していた場合rnkを見てくっつける方を決める
        elif(self.rnk[x] > self.rnk[y]):
            self.root[x] += self.root[y]
            self.root[y] = x

        else:
            self.root[y] += self.root[x]
            self.root[x] = y
            # rnkが同じ（深さに差がない場合）は1増やす
            if(self.rnk[x] == self.rnk[y]):
                self.rnk[y] += 1
    # xとyが同じグループに属するか判断
    def isSameGroup(self, x, y):
        return self.Find_Root(x) == self.Find_Root(y)

    # ノードxが属する木のサイズを返す
    def Count(self, x):
        return -self.root[self.Find_Root(x)]



H,W=map(int,input().split())
tree=UnionFind(H*W)
s=[input() for i in range(H)]

for i in range(H):
    for j in range(W):
        x=i*W+j+1
        if i>0 and s[i][j]!=s[i-1][j]: tree.Unite(x,x-W)
        if i<H-1 and s[i][j]!=s[i+1][j]: tree.Unite(x,x+W)
        if j>0 and s[i][j]!=s[i][j-1]: tree.Unite(x,x-1)
        if j<W-1 and s[i][j]!=s[i][j+1]: tree.Unite(x,x+1)

dicw={}


for i in range(H):
    for j in range(W):
        p=tree.Find_Root(i*W+j+1)
        if not p in dicw:
            dicw[p]=0
        if s[i][j]==".":
            dicw[p]+=1

ans=0
for i in dicw:
    n=tree.Count(i)

    ans+=dicw[i]*(n-dicw[i])
print(ans)