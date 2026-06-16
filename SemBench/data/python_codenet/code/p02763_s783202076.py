import sys
input = sys.stdin.readline


class Bit:
    def __init__(self, n):
        self.n = n
        self.tree = [0]*(n+1)
        self.el = [0]*(n+1)
        self.depth = n.bit_length() - 1

    def sum(self, i):
        """ 区間[0,i) の総和を求める """
        s = 0
        i -= 1
        while i >= 0:
            s += self.tree[i]
            i = (i & (i + 1) )- 1
        return s

    def add(self, i, x):
        """ i 番目の要素に x を足す """
        self.el[i] += x
        while i < self.n:
            self.tree[i] += x
            i |= i + 1

    def get(self, i, j=None):
        """ 部分区間和 [i, j) """
        if j is None:
            return self.el[i]
        if i == 0:
            return self.sum(j)
        return self.sum(j) - self.sum(i)

    def lower_bound(self, x, equal=False):
        """ (a0+a1+...+ai < x となる最大の i, その時の a0+a1+...+ai )
             a0+a1+...+ai <= x としたい場合は equal = True
             二分探索であるため、ai>=0 を満たす必要がある"""
        sum_ = 0
        pos = -1    # 1-indexed の時は pos = 0
        if not equal:
            for i in range(self.depth, -1, -1):
                k = pos + (1 << i)
                if k < self.n and sum_ + self.tree[k] < x:  # 1-indexed の時は k <= self.n
                    sum_ += self.tree[k]
                    pos += 1 << i
        if equal:
            for i in range(self.depth, -1, -1):
                k = pos + (1 << i)
                if k < self.n and sum_ + self.tree[k] <= x: # 1-indexed の時は k <= self.n
                    sum_ += self.tree[k]
                    pos += 1 << i
        return pos, sum_

    def __getitem__(self, s):
        """ [a0, a1, a2, ...] """
        return self.el[s]

    def __iter__(self):
        """ [a0, a1, a2, ...] """
        for s in self.el[:self.n]:
            yield s

    def __str__(self):
        text1 = " ".join(["element:            "] + list(map(str, self)))
        text2 = " ".join(["cumsum(1-indexed):  "] + list(str(self.sum(i)) for i in range(1, self.n + 1)))
        return "\n".join((text1, text2))

####################################################################################################

import string

N = int(input())
S = input().strip()
Q = int(input())

B = [Bit(N) for _ in range(26)]

abc = string.ascii_lowercase                                            # [a-z] をロード
abc2 = dict()
for i, s in enumerate(abc):
    abc2[s] = i

for i, s in enumerate(S):
    B[abc2[s]].add(i,1)

for _ in range(Q):
    q = list(input().split())
    if q[0] == "1":
        a = int(q[1]) - 1
        b = q[2]
        for i in range(26):
            if B[i].el[a] == 1:
                B[i].add(a,-1)
        B[abc2[b]].add(a,1)
    if q[0] == "2":
        a = int(q[1]) - 1
        b = int(q[2]) - 1
        res = 0
        for i in range(26):
            res += (B[i].get(a, b+1) > 0)
        print(res)
