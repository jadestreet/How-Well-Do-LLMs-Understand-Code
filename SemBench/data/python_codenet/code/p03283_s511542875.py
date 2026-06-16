# Reference: https://ikatakos.com/pot/programming_algorithm/data_structure/binary_indexed_tree
# Fenwick Tree
class BinaryIndexedTree:
    # a = [0] * n
    # O(n)
    def __init__(self, n):
        self.size = n
        self.data = [0] * (n+1)

    # return sum(a[0:i])
    # O(log(n))
    def cumulative_sum(self, i):
        ans = 0
        while i > 0:
            ans += self.data[i]
            i -= i & -i
        return ans

    # a[i] += x
    # O(log(n))
    def add(self, i, x):
        i += 1
        while i <= self.size:
            self.data[i] += x
            i += i & -i

from sys import stdin
input = stdin.buffer.readline

def main():
    n, m, q = map(int, input().split())
    lr = [tuple(map(int, input().split())) for _ in range(m)]
    pq = [(0, 0, 0)] * q
    for ind in range(q):
        i, j = map(int, input().split())
        pq[ind] = (i, j, ind)

    lr.sort(key=lambda x: x[0])
    l = [i for i, j in lr]
    r = [j for i, j in lr]
    pq.sort(key=lambda x: x[0])

    BIT = BinaryIndexedTree(n+1)
    for i in r:
        BIT.add(i, 1)

    # search r[lr_ind:]
    lr_ind = 0
    ans = [0] * q
    for left, right, pq_ind in pq:
        while lr_ind < m and l[lr_ind] < left:
            BIT.add(r[lr_ind], -1)
            lr_ind += 1

        ans[pq_ind] = BIT.cumulative_sum(right+1)

    for i in ans:
        print(i)

main()