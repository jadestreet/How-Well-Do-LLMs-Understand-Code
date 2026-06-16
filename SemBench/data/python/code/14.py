# 14.py — Depth-First Search to test path existence in a graph
from typing import Dict, List, Hashable, Set

def _dfs(u: Hashable, target: Hashable, graph: Dict[Hashable, List[Hashable]], visited: Set[Hashable]) -> bool:
    if u == target:
        return True
    visited.add(u)
    for v in graph.get(u, []):
        if v not in visited and _dfs(v, target, graph, visited):
            return True
    return False

def path_exists(graph: Dict[Hashable, List[Hashable]], start: Hashable, target: Hashable) -> bool:
    if start is None or target is None:
        return False
    visited: Set[Hashable] = set()
    return _dfs(start, target, graph, visited)
