# 30.py — A* pathfinding on a grid with obstacles
import heapq
from typing import List, Tuple, Dict, Optional

Grid = List[List[int]]  # 0 = free, 1 = wall

def neighbors(grid: Grid, r: int, c: int) -> List[Tuple[int,int]]:
    res = []
    for dr, dc in ((1,0),(-1,0),(0,1),(0,-1)):
        nr, nc = r + dr, c + dc
        if 0 <= nr < len(grid) and 0 <= nc < len(grid[0]) and grid[nr][nc] == 0:
            res.append((nr, nc))
    return res

def heuristic(a: Tuple[int,int], b: Tuple[int,int]) -> int:
    return abs(a[0]-b[0]) + abs(a[1]-b[1])

def reconstruct(came_from: Dict[Tuple[int,int], Tuple[int,int]], start: Tuple[int,int], goal: Tuple[int,int]) -> List[Tuple[int,int]]:
    cur = goal
    path = [cur]
    while cur != start:
        cur = came_from[cur]
        path.append(cur)
    path.reverse()
    return path

def astar(grid: Grid, start: Tuple[int,int], goal: Tuple[int,int]) -> Optional[List[Tuple[int,int]]]:
    if grid[start[0]][start[1]] == 1 or grid[goal[0]][goal[1]] == 1:
        return None
    open_heap = []
    heapq.heappush(open_heap, (0, start))
    g: Dict[Tuple[int,int], int] = {start: 0}
    came_from: Dict[Tuple[int,int], Tuple[int,int]] = {}
    closed = set()
    while open_heap:
        _, u = heapq.heappop(open_heap)
        if u in closed:
            continue
        if u == goal:
            return reconstruct(came_from, start, goal)
        closed.add(u)
        for v in neighbors(grid, *u):
            tentative = g[u] + 1
            if v in closed and tentative >= g.get(v, 10**9):
                continue
            if tentative < g.get(v, 10**9):
                came_from[v] = u
                g[v] = tentative
                f = tentative + heuristic(v, goal)
                heapq.heappush(open_heap, (f, v))
    return None
