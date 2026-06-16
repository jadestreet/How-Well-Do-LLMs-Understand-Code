# 10.py — Topological sort (Kahn's algorithm)
from collections import deque, defaultdict
from typing import Iterable, Tuple, Dict, List, Hashable, Set

def build_graph(edges: Iterable[Tuple[Hashable, Hashable]]):
    adj: Dict[Hashable, List[Hashable]] = defaultdict(list)
    indegree: Dict[Hashable, int] = defaultdict(int)
    nodes: Set[Hashable] = set()
    for u, v in edges:
        adj[u].append(v)
        indegree[v] += 1
        nodes.add(u); nodes.add(v)
    for node in nodes:
        indegree.setdefault(node, 0)
        adj.setdefault(node, [])
    return adj, indegree, nodes

def topo_sort(edges: Iterable[Tuple[Hashable, Hashable]]):
    if edges is None:
        return []
    adj, indegree, nodes = build_graph(edges)
    dq = deque([x for x in nodes if indegree[x] == 0])
    order: List[Hashable] = []
    while dq:
        u = dq.popleft()
        order.append(u)
        for v in adj[u]:
            indegree[v] -= 1
            if indegree[v] == 0:
                dq.append(v)
    return order
