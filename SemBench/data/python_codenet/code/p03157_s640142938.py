import sys
sys.setrecursionlimit(10**7)
black = 0
white = 0
#x,y渡すと、（ｈ、ｗ）に入ってるかどうか判定
def check(s,t):
    if (0 <=  s <= h - 1) and (0 <= t <= w - 1):
        return True
    else:
        return False
def bfs(que):
    finished = set()
    while que:
        x , y, color = que.popleft()
        if x+y*w not in finished:
            finished.add(x+y*w)
            for i in range(-1,2,1):
                for j in range(-1,2,1):
                    if abs(i) + abs(j) < 2 and check(y+j,x+i):
                        if (x+i)+(y+j)*w not in finished:
                            que.append([x+i,y+j,grid[y+j][x+i]])
                        if color != grid[y+j][x+i]:
                            adjacent_list[x+w*y].append((x + i)+w*(y + j))
def dfs(node):
    global white
    global black
    finished.add(node)
    y,x = divmod(node,w)
    if grid[y][x] == '#':
        black += 1
    else:
        white += 1
    for i in adjacent_list[node]:
        if i not in finished:
            dfs(i)
from collections import deque
h,w = map(int, input().split())
grid = []
for i in range(h):
    grid.append(list(input()))
ans = 0
adjacent_list = [[] for i in range(h*w)]
"""
que = deque()
que.append([0,0,grid[0][0]])
bfs(que)
"""
for y in range(h):
    for x in range(w):
        for i in range(-1,2,1):
            for j in range(-1,2,1):
                if abs(i) + abs(j) < 2 and check(y+j,x+i):
                    if grid[y][x] != grid[y+j][x+i]:
                        adjacent_list[x+w*y].append((x + i)+w*(y + j))
#再び初期化
finished = set()
for i in range(h*w):
    #頂点iからdfsをする。黒と白をカウントしておいて最後にかける
    black = 0
    white = 0
    if i not in finished:
        dfs(i)
        ans += black * white
print(ans)