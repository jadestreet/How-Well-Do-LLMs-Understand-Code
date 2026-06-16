import sys
from collections import deque


def input():
    return sys.stdin.readline().strip()


sys.setrecursionlimit(20000000)

MOD = 10 ** 9 + 7
INF = float("inf")


def dfs(maze, H, W, sh, sw, gh, gw):
    visited = [[False] * W for _ in range(H)]
    visited[sh][sw] = True
    q = deque([(sh, sw)])
    while q:
        h, w = q.pop()
        if h == gh and w == gw:
            return True
        for dh, dw in [(1, 0), (-1, 0), (0, -1), (0, 1)]:
            nh = h + dh
            nw = w + dw
            if 0 <= nh < H and 0 <= nw < W:
                if not visited[nh][nw]:
                    if maze[nh][nw] == ".":
                        visited[nh][nw] = True
                        q.append((nh, nw))
    return False


def main():
    H, W = map(int, input().split())
    S = [list(input()) for _ in range(H)]
    dx = [1, 0, -1, 0]
    dy = [0, 1, 0, -1]
    seen = [[False] * W for _ in range(H)]

    def dfs(x, y, black, white):
        q = deque([(x, y)])
        while q:
            X, Y = q.pop()
            if seen[X][Y]:
                continue
            seen[X][Y] = True
            if S[X][Y] == "#":
                black += 1
            else:
                white += 1
            for i in range(4):
                nx = X + dx[i]
                ny = Y + dy[i]
                if not (0 <= nx < H and 0 <= ny < W):
                    continue
                if S[X][Y] == S[nx][ny]:
                    continue
                if seen[nx][ny]:
                    continue
                q.append((nx, ny))
        return black, white

    answer = 0
    for h in range(H):
        for w in range(W):
            if S[h][w] == ".":
                continue
            if seen[h][w]:
                continue
            black = 0
            white = 0
            black, white = dfs(h, w, black, white)
            answer += black * white

    print(answer)


if __name__ == "__main__":
    main()
