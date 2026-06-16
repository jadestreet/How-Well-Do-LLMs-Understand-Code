class BalancingTree:
    """平衡二分木のクラス
    Pivotを使った実装.
    0以上2^n - 2以下の整数を扱う
    """
    def __init__(self, n):
        """
        2の指数nで初期化
        """
        self.N = n
        self.root = self.node(1<<n, 1<<n)

    def debug(self):
        """デバッグ用の関数"""
        def debug_info(nd_):
            return (nd_.value - 1, nd_.pivot - 1, nd_.left.value - 1 if nd_.left else -1, nd_.right.value - 1 if nd_.right else -1)

        def debug_node(nd):
            re = []
            if nd.left:
                re += debug_node(nd.left)
            if nd.value: re.append(debug_info(nd))
            if nd.right:
                re += debug_node(nd.right)
            return re
        print("Debug - root =", self.root.value - 1, debug_node(self.root)[:50])

    def append(self, v):
        """
        v を追加（その時点で v はない前提）
        """
        v += 1
        nd = self.root
        while True:
            if v == nd.value:
                # v がすでに存在する場合に何か処理が必要ならここに書く
                return 0
            else:
                mi, ma = min(v, nd.value), max(v, nd.value)
                if mi < nd.pivot:
                    nd.value = ma
                    if nd.left:
                        nd = nd.left
                        v = mi
                    else:
                        p = nd.pivot
                        nd.left = self.node(mi, p - (p&-p)//2)
                        break
                else:
                    nd.value = mi
                    if nd.right:
                        nd = nd.right
                        v = ma
                    else:
                        p = nd.pivot
                        nd.right = self.node(ma, p + (p&-p)//2)
                        break

    def leftmost(self, nd):
        if nd.left: return self.leftmost(nd.left)
        return nd

    def rightmost(self, nd):
        if nd.right: return self.rightmost(nd.right)
        return nd

    def find_l(self, v):
        """
        vより真に小さいやつの中での最大値（なければ-1）
        """
        v += 1
        nd = self.root
        prev = 0
        if nd.value < v: prev = nd.value
        while True:
            if v <= nd.value:
                if nd.left:
                    nd = nd.left
                else:
                    return prev - 1
            else:
                prev = nd.value
                if nd.right:
                    nd = nd.right
                else:
                    return prev - 1

    def find_r(self, v):
        """
        vより真に大きいやつの中での最小値（なければRoot）
        """
        v += 1
        nd = self.root
        prev = 0
        if nd.value > v: prev = nd.value
        while True:
            if v < nd.value:
                prev = nd.value
                if nd.left:
                    nd = nd.left
                else:
                    return prev - 1
            else:
                if nd.right:
                    nd = nd.right
                else:
                    return prev - 1

    @property
    def max(self):
        """最大値の属性"""
        return self.find_l((1<<self.N)-1)

    @property
    def min(self):
        """最小値の属性"""
        return self.find_r(-1)

    def delete(self, v, nd = None, prev = None):
        """
        値がvのノードがあれば削除（なければ何もしない）
        """
        v += 1
        if not nd: nd = self.root
        if not prev: prev = nd
        while v != nd.value:
            prev = nd
            if v <= nd.value:
                if nd.left:
                    nd = nd.left
                else:
                    return
            else:
                if nd.right:
                    nd = nd.right
                else:
                    return
        if (not nd.left) and (not nd.right):
            if nd.value < prev.value:
                prev.left = None
            else:
                prev.right = None
        elif not nd.left:
            if nd.value < prev.value:
                prev.left = nd.right
            else:
                prev.right = nd.right
        elif not nd.right:
            if nd.value < prev.value:
                prev.left = nd.left
            else:
                prev.right = nd.left
        else:
            nd.value = self.leftmost(nd.right).value
            self.delete(nd.value - 1, nd.right, nd)

    def __contains__(self, v: int) -> bool:
        return self.find_r(v - 1) == v

    class node:
        """ノードをあらわすクラス
        v: 値
        p: ピボット値
        で初期化
        """
        def __init__(self, v, p):
            self.value = v
            self.pivot = p
            self.left = None
            self.right = None

Trees = [BalancingTree(50) for _ in range(26)]
N = int(input())
S = input()
Q = int(input())
alphabets = list("abcdefghijklmnopqrstuvwxyz")
c2n = {c: i for i, c in enumerate(alphabets)}
for i in range(N):
    Trees[c2n[S[i]]].append(i+1)
S = list(S)
for _ in range(Q):
    tmp = list(input().split())
    if tmp[0] == "1":
        _, i, c = tmp
        i = int(i)
        bef = S[i-1]
        if bef == c:
            continue
        Trees[c2n[bef]].delete(i)
        Trees[c2n[c]].append(i)
        S[i-1] = c
    else:
        _, l, r = tmp
        l = int(l)
        r = int(r)
        ans = 0
        for char in range(26):
            res = Trees[char].find_r(l-1)
            if l <= res <= r:
                ans += 1
        print(ans)