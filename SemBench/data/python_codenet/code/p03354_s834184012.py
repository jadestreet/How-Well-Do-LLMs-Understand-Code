import sys


#https://note.nkmk.me/python-union-find/
class AlgUnionFind():
    def __init__(self, n):
        self.n = n
        self.parents = [-1] * n

    def find(self, x):
        if self.parents[x] < 0:
            return x
        else:
            self.parents[x] = self.find(self.parents[x])
            return self.parents[x]

    def union(self, x, y):
        x = self.find(x)
        y = self.find(y)

        if x == y:
            return

        if self.parents[x] > self.parents[y]:
            x, y = y, x

        self.parents[x] += self.parents[y]
        self.parents[y] = x

    def size(self, x):
        return -self.parents[self.find(x)]

    def same(self, x, y):
        return self.find(x) == self.find(y)

    def members(self, x):
        root = self.find(x)
        return [i for i in range(self.n) if self.find(i) == root]

    def roots(self):
        return [i for i, x in enumerate(self.parents) if x < 0]

    def group_count(self):
        return len(self.roots())

    def all_group_members(self):
        return {r: self.members(r) for r in self.roots()}

    def __str__(self):
        return '\n'.join('{}: {}'.format(r, self.members(r)) for r in self.roots())


def solve():
    input = sys.stdin.readline
    mod = 10 ** 9 + 7
    n, m = list(map(int, input().rstrip('\n').split()))
    p = list(map(int, input().rstrip('\n').split()))
    uf = AlgUnionFind(n)
    for i in range(m):
        x, y = list(map(int, input().rstrip('\n').split()))
        uf.union(x-1, y-1)
    for i in range(n):
        p[i] = [p[i]-1, p[i]-1 == i]
    while True:
        c_sw = False
        for i in range(len(p)):
            tn = p[i][0]
            if not p[i][1] and not p[tn][1]:
                if uf.same(tn, p[tn][0]):
                    p[tn][0], p[i][0] = p[i][0], p[tn][0]
                    p[i][1] = p[i][0] == i
                    p[tn][1] = p[tn][0] == tn
                    c_sw = True
        if not c_sw:
            break
    cnt = 0
    for i in range(n):
        cnt += p[i][1]
    print(cnt)


if __name__ == '__main__':
    solve()
