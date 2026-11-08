"""Problem Few."""

import heapq


def solve(instance):
    """Few: min number of red vertices on any s,t-path, or -1 if none.
    Dijkstra with vertex costs (1 if red, else 0). Walks are fine because
    removing a cycle from a walk never adds red vertices.
    Works on directed and undirected networkx graphs
    (G.neighbors gives successors for a DiGraph)."""
    G = instance.graph
    s, t = instance.s, instance.t
    red = set(instance.red)

    INF = float("inf")
    dist = {v: INF for v in G.nodes}
    dist[s] = 1 if s in red else 0
    pq = [(dist[s], 0, s)]
    counter = 0  # tie-breaker so heapq never compares vertex names

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