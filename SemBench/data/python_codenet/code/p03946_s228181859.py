# 高橋くんと見えざる手
n, t = map(int, input().split())
a = list(map(int, input().split()))

max_value = [[0, n] for i in range(n + 1)]

# max_value[i]=後ろからi番目までの値で最も大きい値
for i in range(1, n + 1):
    num = a[-i]
    if max_value[i - 1][0] < num:
        max_value[i][0] = num
        max_value[i][1] = n + 1 - i
    else:
        max_value[i] = max_value[i - 1]


min_value = [10**10 for i in range(n + 1)]
# min_value[i]=初めからi番目までの値で最も小さい値
for _ in range(n):
    x = a[_]
    min_value[_ + 1] = min(min_value[_], x)

max_dif = 0
for i in range(1, n + 1):
    if max_value[i][0] > min_value[n - i]:
        max_dif = max(max_dif, max_value[i][0] - min_value[n - i])


disk = []
for i in range(1, n + 1):
    base = a[i - 1]
    if base + max_dif == max_value[n - i][0]:
        disk.append((i, max_value[n - i][1]))

######


class UnionFind:
    def __init__(self, n):
        self.par = [i for i in range(n + 1)]
        self.rank = [0] * (n + 1)

    # 検索
    def find(self, x):
        if self.par[x] == x:
            return x
        else:
            self.par[x] = self.find(self.par[x])
            return self.par[x]

    # 併合
    def union(self, x, y):
        x = self.find(x)
        y = self.find(y)
        if self.rank[x] < self.rank[y]:
            self.par[x] = y
        else:
            self.par[y] = x
            if self.rank[x] == self.rank[y]:
                self.rank[x] += 1

    # 同じ集合に属するか判定
    def same_check(self, x, y):
        return self.find(x) == self.find(y)


uni = UnionFind(n)
for some in disk:
    a, b = some[0], some[1]
    uni.union(a, b)
for i in range(n + 1):
    uni.find(i)

# UnionFind

group = {i: [] for i in range(n + 1)}

for i in range(n + 1):
    group[uni.par[i]].append(i)
ans = 0
for i in range(n + 1):
    L = len(group[i])
    ans += L * (L - 1) // 2
print(ans)
