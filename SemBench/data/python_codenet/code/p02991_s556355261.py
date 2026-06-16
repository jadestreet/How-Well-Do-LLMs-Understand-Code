import sys
from io import StringIO
import unittest
import os
from collections import deque
import itertools

# 再帰処理上限(dfs作成時に設定するのが面倒なので限度近い値を組み込む)
sys.setrecursionlimit(999999999)


# 実装を行う関数
def resolve(test_def_name=""):
    n, m = map(int, input().split())
    u_s = [list(map(int, input().split())) for i in range(m)]
    s, t = map(int, input().split())

    point_s = [[] for i in range(n + 1)]
    [point_s[u[0]].append(u[1]) for u in u_s]

    # deq作成
    ans = [999999999 for i in range(n + 1)]
    bef = [999999999 for i in range(n + 1)]
    ans[s] = 0
    bef[s] = 0

    que = deque()
    que.appendleft(s)

    arrived1 = {}
    arrived2 = {}
    arrived3 = {}

    # BFS開始
    while len(que) is not 0:
        now = que.pop()

        # ケンケンパ
        work_s = point_s[now]
        ken = []
        for work in work_s:
            if arrived1.get(work, 0) == 0:
                ken.append(work)
                arrived1[work] = 1

        # list(itertools.chain.from_iterable(l_2d))
        work_s = [point_s[k] for k in ken]
        work_s = list(itertools.chain.from_iterable(work_s))
        kenken = []
        for work in work_s:
            if arrived2.get(work, 0) == 0:
                kenken.append(work)
                arrived2[work] = 1

        work_s = [point_s[k] for k in kenken]
        work_s = list(itertools.chain.from_iterable(work_s))
        kenkenpa = []
        for work in work_s:
            if arrived3.get(work, 0) == 0:
                kenkenpa.append(work)
                arrived3[work] = 1

        for ken in kenkenpa:
            if ans[ken] == 999999999:
                ans[ken] = ans[now] + 1
                bef[ken] = now
                # キューに追加(先頭に追加するのでappendleft())
                que.appendleft(ken)
            elif ans[ken] > ans[now] + 1:
                bef[ken] = now

    if ans[t] == 999999999:
        print(-1)
        return

    aa = bef[t]
    cnt = 1
    for i in range(9999999):
        if aa == s:
            break
        cnt += 1
        aa = bef[aa]

    print(cnt)


# テストクラス
class TestClass(unittest.TestCase):
    def assertIO(self, assert_input, output):
        stdout, sat_in = sys.stdout, sys.stdin
        sys.stdout, sys.stdin = StringIO(), StringIO(assert_input)
        resolve(sys._getframe().f_back.f_code.co_name)
        sys.stdout.seek(0)
        out = sys.stdout.read()[:-1]
        sys.stdout, sys.stdin = stdout, sat_in
        self.assertEqual(out, output)

    def test_input_1(self):
        test_input = """4 4
1 2
2 3
3 4
4 1
1 3"""
        output = """2"""
        self.assertIO(test_input, output)

    def test_input_2(self):
        test_input = """3 3
1 2
2 3
3 1
1 2"""
        output = """-1"""
        self.assertIO(test_input, output)

    def test_input_3(self):
        test_input = """2 0
1 2"""
        output = """-1"""
        self.assertIO(test_input, output)

    def test_input_4(self):
        test_input = """6 8
1 2
2 3
3 4
4 5
5 1
1 4
1 5
4 6
1 6"""
        output = """2"""
        self.assertIO(test_input, output)

    # 自作テストパターンのひな形(利用時は「tes_t」のアンダーバーを削除すること
    def tes_t_1original_1(self):
        test_input = """データ"""
        output = """データ"""
        self.assertIO(test_input, output)


# 実装orテストの呼び出し
if __name__ == "__main__":
    if os.environ.get("USERNAME") is None:
        # AtCoder提出時の場合
        resolve()

    else:
        # 自PCの場合
        unittest.main()
