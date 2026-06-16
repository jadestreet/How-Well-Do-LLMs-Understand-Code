# 25.py — Tarjan's algorithm for strongly connected components
from typing import Dict, List, Hashable

def tarjan_scc(graph: Dict[Hashable, List[Hashable]]) -> List[List[Hashable]]:
    index = 0
    stack: List[Hashable] = []
    onstack = set()
    idx = {}
    low = {}
    sccs: List[List[Hashable]] = []

    def strongconnect(v):
        nonlocal index
        idx[v] = index
        low[v] = index
        index += 1
        stack.append(v); onstack.add(v)
        for w in graph.get(v, []):
            if w not in idx:
                strongconnect(w)
                low[v] = min(low[v], low[w])
            elif w in onstack:
                low[v] = min(low[v], idx[w])
        if low[v] == idx[v]:
            comp = []
            while True:
                w = stack.pop()
                onstack.remove(w)
                comp.append(w)
                if w == v:
                    break
            sccs.append(comp)

    for v in graph:
        if v not in idx:
            strongconnect(v)
    return sccs
