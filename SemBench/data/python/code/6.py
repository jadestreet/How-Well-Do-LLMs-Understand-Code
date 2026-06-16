# 6.py — Breadth-First Search (BFS) over adjacency lists
from collections import deque
from typing import Dict, List, Hashable

def _enqueue_unvisited(graph: Dict[Hashable, List[Hashable]], node: Hashable, visited: set, dq: deque) -> None:
    for nbr in graph.get(node, []):
        if nbr not in visited:
            visited.add(nbr)
            dq.append(nbr)

def bfs(graph: Dict[Hashable, List[Hashable]], start: Hashable):
    if start is None:
        return []
    visited = set([start])
    order: List[Hashable] = []
    dq = deque([start])
    while dq:
        node = dq.popleft()
        order.append(node)
        _enqueue_unvisited(graph, node, visited, dq)
    return order
