#####################################################################################################
##### 最大二部マッチング問題
#####################################################################################################

"""

参考（コード）
https://kopricky.github.io/code/For_Python/bipartite_matching.html
参考（最大フロー問題）
http://nw.tsuda.ac.jp/class/algoC/c9.html
https://ikatakos.com/pot/programming_algorithm/graph_theory/maximum_flow
http://vartkw.hatenablog.com/entry/2016/12/02/002703
参考（計算量）
https://ta1sa.hatenablog.com/entry/2020/04/13/123802
https://cp-algorithms.com/graph/dinic.html

ベンチマーク
http://judge.u-aizu.ac.jp/onlinejudge/description.jsp?id=GRL_7_A&lang=ja
https://atcoder.jp/contests/abc091/submissions/14937663

"""

import sys
input = sys.stdin.readline
from collections import deque


class MaxFlow:
    class Edge:
        def __init__(self, to, cap, rev):
            """
            :param to:  終点ノード
            :param cap: 残された容量
            :param rev: 遂になる逆向きのエッジ（ノード to の rev 番目のエッジ）
            """
            self.to, self.cap, self.rev = to, cap, rev

    def __init__(self, node_size, inf):
        self._node = node_size
        self._inf = inf
        self._level = [-1] * self._node
        self._iter = [0] * self._node
        self._graph = [[] for _ in range(self._node)]

    def add_edge(self, from_, to, cap):
        self._graph[from_].append(self.Edge(to, cap, len(self._graph[to])))
        self._graph[to].append(self.Edge(from_, 0, len(self._graph[from_]) - 1))

    def bfs(self, start):
        """
        概要: 流れる方向を大雑把に決める（※ ループ２回目以降は逆流辺の cap が正になるので逆流も可能になり、流れる方向に選択肢が出てくる。）
        入力: cap
        出力: level[v]            (※ start から v への（cap > 0 の辺のみを使った場合の）最短距離。経路が無い場合は -1)
        備考1: 最初は適当に見つかった最短経路から始めるが、ループが進むにつれて徐々に条件のきつい cap が入力として与えられるようになり、
              最終的に遠回りの経路も全て考慮した結果が得られる。
        備考2: level[sink]（最短経路長）が単調増加であるため、ステップ数 O(V) で探索が終了する。
        """
        self._level = [-1] * self._node
        next_set = deque()
        self._level[start] = 0
        next_set.append(start)
        while next_set:
            current = next_set.popleft()
            for edge in self._graph[current]:
                """ current vertex から進める候補が _graph[current] に格納されている。ここでは逆流辺（edge.rev）は考慮しない。"""
                if self._level[edge.to] < 0 < edge.cap:
                    self._level[edge.to] = self._level[current] + 1
                    next_set.append(edge.to)

    def dfs(self, start, end, flow):
        """
        概要: bfsで大雑把に決めた方向に実際に水を流してみて本当に流れるかを調べる。
        入力: level           （※ bfs で決めた方向）
        出力: cap, flowed
        内部変数: iter          (※ 探索済みかどうかをメモ)
        備考1: bfs で先に方向を決めたおかげで、ここのステップが効率化される。 O(EV)
        """
        if start == end:
            return flow
        while self._iter[start] < len(self._graph[start]):
            edge = self._graph[start][self._iter[start]]
            if edge.cap > 0 and self._level[start] < self._level[edge.to]:
                """ 二つ目の条件が bfs からの入力である水流の方向に対応 """
                flowed = self.dfs(edge.to, end, min(flow, edge.cap))
                if flowed > 0:
                    """ 水流を流すと、正方向のcapは減って、逆方向のcapは増える """
                    edge.cap -= flowed
                    self._graph[edge.to][edge.rev].cap += flowed
                    return flowed
            self._iter[start] += 1
        return 0

    def solve(self, source, sink):
        flow = 0
        while True:
            self.bfs(source)
            if self._level[sink] < 0:
                """ sinkへの最短距離が -1 ⇒ sink にたどり着けない ⇒ 増加路が存在しないため探索終了"""
                return flow
            self._iter = [0] * self._node
            while True:
                f = self.dfs(source, sink, self._inf)
                if f == 0:
                    break
                flow += f


class Dinic:
    def __init__(self, len_X, len_Y):
        """
        soursの位置 = 0
        sinkの位置  = len_X + len_Y + 1
        capacity   = 1
        の最大フロー問題
        """
        self.len_X, self.len_Y = len_X, len_Y
        self.mf = MaxFlow(self.len_X + self.len_Y + 2, min(self.len_X, self.len_Y))
        for i in range(self.len_X):
            """ sours から部分集合Xへの各点に capacity=1 の流れを作る """
            self.mf.add_edge(0, i + 1, 1)
        for i in range(self.len_Y):
            """ 部分集合Yへの各点からsinkへの capacity=1 の流れを作る """
            self.mf.add_edge(self.len_X + i + 1, self.len_X + self.len_Y + 1, 1)

    def add_edge(self, from_, to):
        """
        :param from_: 部分集合Xの頂点　（1,...,len_X）
        :param to:    部分集合Yの頂点　（len_X + 1,...,len_X + len_Y）
        """
        self.mf.add_edge(from_ + 1, to + self.len_X + 1, 1)

    def solve(self):
        return self.mf.solve(0, self.len_X + self.len_Y + 1)

#####################################################################################

N = int(input())

X = []
Y = []
for i in range(N):
    X.append([int(i) for i in input().split()])

for i in range(N):
    Y.append([int(i) for i in input().split()])

dinic = Dinic(len(X), len(Y))

for i in range(len(X)):
    for j in range(N):
        if X[i][0] < Y[j][0] and X[i][1] < Y[j][1]:
            dinic.add_edge(i,j)


print(dinic.solve())