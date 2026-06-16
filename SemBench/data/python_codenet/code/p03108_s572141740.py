mod = 10 ** 9 + 7
mod2 = 2 ** 61 + 1
from collections import deque
import heapq
import time
from bisect import bisect_left, insort_left, bisect_right
import sys

input = sys.stdin.readline
_NUMINT_ALL = list(range(10))


def main():
    ans = solve()

    if ans is True or ans is False:
        YesNo(ans)
    elif ans is not None:
        print(ans)


def solve():
    N, M = iip(False)

    AB = iipt(M)
    AB.reverse()
    uf = UfTree(N)

    benlist = [0]

    cur = 0
    for a, b in AB:
        a -= 1
        b -= 1
        c1 = uf.size(a)
        c2 = uf.size(b)
        uf.unite(a, b)
        if c2 != uf.size(a):
            cur += c1*c2
        benlist.append(cur)

    t = benlist.pop()
    benlist.reverse()
    #print(benlist)

    ans = [t - i for i in benlist]

    split_print_enter(ans)


#####################################################ライブラリ集ここから

def kiriage_warizan(a, b):
    return -(-a//b)


def iip(listed=True):  # 数字のinputをlistで受け取る
    d = input().rstrip("\n").split()
    try:
        ret = [int(i) for i in d]
    except:
        ret = [int(i) if i in _NUMINT_ALL else i for i in d]
        if len(ret) == 1:
            return ret[0]

    if len(ret) == 1 and not listed:
        return ret[0]
    return ret

def iipt(l, listed=False, num_only=True):  # 縦向きに並んでいるデータをリストに落とし込む(iip利用)
    ret = []
    for i in range(l):
        ret.append(iip(listed=listed))
    return ret


def saidai_kouyakusuu(A):  # 最大公約数
    l = len(A)
    while True:
        m = min(A)
        mx = max(A)
        if m == mx:
            return m

        for i in range(l):
            if A[i] % m == 0:
                A[i] = m
            else:
                A[i] %= m


def make_graph_edge_flat(N):  # グラフ作成のための辺をリストで返す
    ret = []
    for i in range(N-1):
        a, b, c = iip()
        a -= 1
        b -= 1
        ret[a].append((b, c))
        ret[b].append((a, c))
    return ret


def sort_tuples(l, index):  # タプルのリストを特定のインデックスでソートする
    if isinstance(l, list):
        l.sort(key=lambda x: x[index])
        return l
    else:
        l = list(l)
        return sorted(l, key=lambda x: x[index])


def count_elements(l):  # リストの中身の個数を種類分けして辞書で返す
    d = {}
    for i in l:
        if i in d:
            d[i] += 1
        else:
            d[i] = 1
    return d


def safeget(l, index, default="exception"):  # listの中身を取り出す時、listからはみ出たり
    if index >= len(l):                      # マイナスインデックスになったりするのを防ぐ
        if default == "exception":
            raise Exception("".join(["safegetに不正な値 ", index, "が渡されました。配列の長さは", len(l), "です"]))
        else:
            return default
    elif index < 0:
        if default == "exception":
            raise Exception("".join(["safegetに不正な値 ", index, "が渡されました。負の値は許可されていません"]))
        else:
            return default
    else:
        return l[index]


def sortstr(s):  # 文字列をソートする
    return "".join(sorted(s))


def iip_ord(startcode="a"):  # 文字列を数字の列に変換する(数字と文字は1:1対応)
    if isinstance(startcode, str):
        startcode = ord(startcode)
    return [ord(i) - startcode for i in input()]


def YesNo(s):  # TrueFalseや1, 0をYesNoに変換する
    if s:
        print("Yes")
    else:
        print("No")


def fprint(s):  # リストを平たくしてprintする(二次元リストを見やすくしたりとか)
    for i in s:
        print(i)


def bitall(N):  # ビット全探索用のインデックスを出力
    ret = []
    for i in range(2 ** N):
        a = []
        for j in range(N):
            a.append(i % 2)
            i //= 2
        ret.append(a)
    return ret

def split_print_space(s):  # リストの中身をスペース区切りで出力する
    print(" ".join([str(i) for i in s]))


def split_print_enter(s):  # リストの中身を改行区切りで出力する
    print("\n".join([str(i) for i in s]))


def soinsuu_bunkai(n):  # 素因数分解
    ret = []
    for i in range(2, int(n ** 0.5) + 1):
        while n % i == 0:
            n //= i
            ret.append(i)
        if i > n:
            break
    if n != 1:
        ret.append(n)
    return ret


def conbination(n, r, mod, test=False):  # nCrをmodを使って計算する
    if n <= 0:
        return 0
    if r == 0:
        return 1
    if r < 0:
        return 0
    if r == 1:
        return n
    ret = 1
    for i in range(n - r + 1, n + 1):
        ret *= i
        ret = ret % mod

    bunbo = 1
    for i in range(1, r + 1):
        bunbo *= i
        bunbo = bunbo % mod

    ret = (ret * inv(bunbo, mod)) % mod
    if test:
        # print(f"{n}C{r} = {ret}")
        pass
    return ret


def inv(n, mod):  #  modnにおける逆元を計算
    return power(n, mod - 2)


def power(n, p, mod_=mod):  # 繰り返し二乗法でn**p % modを計算
    if p == 0:
        return 1
    if p % 2 == 0:
        return (power(n, p // 2, mod_) ** 2) % mod_
    if p % 2 == 1:
        return (n * power(n, p - 1, mod_)) % mod_


def nibutan_func(func, target, left, right, side="left"): # 関数を二分探索
    l = left
    r = right
    x = (l + r) // 2
    while r-l > 1:
        x = (l+r)//2
        if func(x) == target:
            return x
        elif func(x) > target:
            r = x
        else:
            l = x

    if side == "left" or func(x) == target:
        return l
    else:
        return r


def nibutan_list(list_, target, side="left"):  # リストを二分探索
    if not isinstance(list_, list):
        list_ = list(list_)

    l = 0
    r = len(list_)
    x = (l + r) // 2
    while r-l > 1:
        x = (l+r)//2
        if list_[x] == target:
            return x
        elif list_[x] > target:
            r = x
        else:
            l = x

    if side == "left" or list_[x] == target:
        return l
    else:
        return r


class UfTree():
    def __init__(self, maxnum):
        self.parent = list(range(maxnum))
        self._size = [1] * maxnum
        self.rank = [0] * maxnum

    def size(self, a):
        return self._size[self.root(a)]

    def root(self, a):
        rank = 0
        cur = a
        while True:
            if self.parent[cur] == cur:
                #for i in path: # 経路圧縮
                #    self.parent[i] = cur
                return cur
            else:
                self.parent[cur] = self.parent[self.parent[cur]]
                cur = self.parent[cur]
                rank += 1

    def unite(self, a, b):
        ra = self.root(a)
        rb = self.root(b)
        if ra == rb:
            return self

        self._size[ra] += self._size[rb]
        self.parent[rb] = ra
        return self

if __name__ == "__main__":
    main()
