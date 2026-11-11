"""Problem Few.
    The task is to find the minimum number of red vertices on any s,t-path, or -1 if no such
    path exists.

    We are using Dijkstra's algorithm with vertex costs - 1 if the vertex is red, 0
    otherwise. Dijkstra's algorithm finds the cheapest walk, which we can use, because
    even if the walk repeats a vertex (there is a cycle), we can just remove it. That action
    would never add any red vertices, possibly even remove some. That way the cheapest walk
    can always be shortened to a path of equal or even lower cost.

    The approach works on both directed (neighbors() returns only the vertices that the
    current vertex points to) and undirected graphs (neighbors() returns all neighbors).

    The running time is polynomial (O((n + m) log n)), because we process each vertex and
    each edge at most once, and every priority queue operation takes O(log n).

    We use the counter to distinguish entries with equal costs, so that heapq does not have
    to compare the vertex names."""

import heapq


def solve(instance):
    G = instance.graph
    s, t = instance.s, instance.t
    red = set(instance.red)

    INF = float("inf")
    dist = {v: INF for v in G.nodes}
    dist[s] = 1 if s in red else 0
    pq = [(dist[s], 0, s)]
    counter = 0

    while pq:
        d, _, u = heapq.heappop(pq)
        if d > dist[u]:
            continue
        if u == t:
            break
        for v in G.neighbors(u):
            nd = d + (1 if v in red else 0)
            if nd < dist[v]:
                dist[v] = nd
                counter += 1
                heapq.heappush(pq, (nd, counter, v))

    return -1 if dist[t] == INF else dist[t]