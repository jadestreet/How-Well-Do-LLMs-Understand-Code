class UnionFind():
    def __init__(self, n):
        self.n = n
        self.parents = [-1 for _ in range(n)]  # 各要素の親 自分が根の場合は -1 * (木の要素数)

    def root(self, x):  # xが属する木の根を返す
        if self.parents[x] < 0:  # 自分が根の場合
            return x
        else:
            self.parents[x] = self.root(self.parents[x])
            return self.parents[x]

    def merge(self, x, y):  # xが属する木とyが属する木を合体する
        x_root = self.root(x)  # xの根
        y_root = self.root(y)  # yの根

        if x_root == y_root:  # 同じ木に属する
            return

        if self.parents[x_root] > self.parents[y_root]:  # x_rootの要素数 > y_rootの要素数 にしたい
            x_root, y_root = y_root, x_root

        self.parents[x_root] += self.parents[y_root] # x_rootにy_rootを合体
        self.parents[y_root] = x_root


def main():
    h, w = map(int, input().split())
    grid = [list(input()) for _ in range(h)]
    black_list = []
    uf = UnionFind(h * w)

    for r in range(h):
        for c in range(w):
            if grid[r][c] == "#":
                black_list.append([r, c])
            for dr, dc in [[0, 1], [1, 0]]:
                nr = r + dr
                nc = c + dc
                if not (0 <= nr < h and 0 <= nc < w):
                    continue
                if grid[r][c] != grid[nr][nc]:
                    # 0 to h*w-1 に変換
                    uf.merge(r * w + c, nr * w + nc)

    ans = 0
    black_dict = dict()
    for r, c in black_list:  # それぞれの黒マスに対して
        z = uf.root(r * w + c)  # 根を求める
        if z in black_dict:  # それぞれの木に何個黒マスがあるか
            black_dict[z] += 1
        else:
            black_dict[z] = 1

    for index, size in enumerate(uf.parents):
        if size < 0:  # それぞれの木に対して
            if index not in black_dict:  # 黒マス0コは無視
                continue
            ans += black_dict[index] * (- size - black_dict[index])  # 黒マス x 白マス

    print(ans)


if __name__ == "__main__":
    main()
