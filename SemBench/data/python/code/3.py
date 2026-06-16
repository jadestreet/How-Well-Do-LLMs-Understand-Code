"""
3.py — Dijkstra's shortest path (structure based on widely used real-world implementations, e.g., TheAlgorithms/Python, MIT license).
Two functions:
- dijkstra: computes single-source shortest paths on adjacency-matrix graphs
- min_distance: helper to choose the next vertex
"""

def min_distance(dist, visited):
    min_val = float('inf')
    min_idx = -1
    for i in range(len(dist)):
        if not visited[i] and dist[i] < min_val:
            min_val = dist[i]
            min_idx = i
    return min_idx

def dijkstra(graph, src):
    n = len(graph)
    dist = [float('inf')] * n
    visited = [False] * n
    dist[src] = 0
    for _ in range(n):
        u = min_distance(dist, visited)
        if u == -1:
            break
        visited[u] = True
        for v in range(n):
            if graph[u][v] and not visited[v] and dist[u] + graph[u][v] < dist[v]:
                dist[v] = dist[u] + graph[u][v]
    return dist
