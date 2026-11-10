"""Problem Some: is there an s,t-path (no repeated vertices) through a red vertex?

Undirected graphs: network flow, one red vertex at a time.
    Split every vertex v into v_in -> v_out (capacity 1), so each vertex is used at most once.
    Every edge {u, v} becomes two arcs u_out -> v_in and v_out -> u_in (capacity 1).
    A super source X has arcs X -> s_in and X -> t_in (capacity 1).
    For a red vertex r, the sink is r_in. If 2 units arrive, there is a route s -> r and a
    route t -> r sharing only r; flipping the second one gives an s,t-path through r.
    Each red vertex costs at most 2 BFS rounds (Ford-Fulkerson), so O(r * (n + m)) in total.

Directed graphs without cycles: s reaches r and r reaches t is enough (a walk in a DAG can't
repeat a vertex). O(n + m).

Directed graphs with cycles: NP-hard in general, so we answer "?!".
"""

from __future__ import annotations

from collections import deque

import networkx as nx

from runner import Instance


def solve(instance: Instance) -> bool | str:
    """True if some s,t-path (a path: no repeated vertices) contains a red vertex.

    Example: G-ex -> True (path 0, 4, 3).
    """
    path = find_path(instance)
    if path == "?!":
        return "?!"
    return path is not None


def find_path(instance: Instance) -> list[str] | str | None:
    """An s,t-path through a red vertex, None if there is none, or "?!" if we can't tell.

    Handy for checking by eye: ``draw(instance, path=find_path(instance))``.
    """
    if instance.directed:
        return _directed_path(instance)
    return _undirected_path(instance)


# ----------------------------------------------------------------------------- directed


def _directed_path(instance: Instance) -> list[str] | str | None:
    graph, s, t, red = instance.graph, instance.s, instance.t, instance.red
    if not nx.is_directed_acyclic_graph(graph):
        return "?!"  # NP-hard in general (reduction from directed 2 disjoint paths)
    from_s = nx.descendants(graph, s) | {s}
    to_t = nx.ancestors(graph, t) | {t}
    for r in sorted(red & from_s & to_t):
        # No cycles, so gluing these two shortest paths can never repeat a vertex.
        return nx.shortest_path(graph, s, r) + nx.shortest_path(graph, r, t)[1:]
    return None


# --------------------------------------------------------------------------- undirected


def _undirected_path(instance: Instance) -> list[str] | None:
    graph, s, t, red = instance.graph, instance.s, instance.t, instance.red
    if s == t:
        return [s] if s in red else None
    component = nx.node_connected_component(graph, s)
    if t not in component:
        return None  # no s,t-path at all
    if s in red or t in red:
        return nx.shortest_path(graph, s, t)  # any s,t-path contains a red vertex
    candidates = sorted(r for r in red if r in component)
    if not candidates:
        return None

    network = _SplitNetwork(graph.subgraph(component), s, t)
    for r in candidates:
        path = network.path_through(r)
        if path is not None:
            return path
    return None


class _SplitNetwork:
    """The flow network H, built once, reused for every red target.

    Vertex number i becomes node 2*i (v_in) and 2*i + 1 (v_out); X is the last node.
    Arcs are stored in flat lists; arc e and arc e ^ 1 are each other's reverse.
    ``cap[e]`` is the capacity that is *left*, so pushing 1 unit along e means
    cap[e] -= 1 and cap[e ^ 1] += 1. Following a reverse arc undoes flow.
    """

    def __init__(self, graph: nx.Graph, s: str, t: str) -> None:
        self.names = list(graph.nodes)
        self.index = {v: i for i, v in enumerate(self.names)}
        size = 2 * len(self.names) + 1
        self.source = size - 1
        self.adj: list[list[int]] = [[] for _ in range(size)]
        self.head: list[int] = []
        self.cap: list[int] = []

        for i in range(len(self.names)):
            self._add_arc(2 * i, 2 * i + 1)  # v_in -> v_out
        for u, v in graph.edges:
            iu, iv = self.index[u], self.index[v]
            self._add_arc(2 * iu + 1, 2 * iv)  # u_out -> v_in
            self._add_arc(2 * iv + 1, 2 * iu)  # v_out -> u_in
        self._add_arc(self.source, 2 * self.index[s])  # X -> s_in
        self._add_arc(self.source, 2 * self.index[t])  # X -> t_in
        self.s, self.t = s, t

    def _add_arc(self, a: int, b: int) -> None:
        self.adj[a].append(len(self.head))
        self.head.append(b)
        self.cap.append(1)
        self.adj[b].append(len(self.head))
        self.head.append(a)
        self.cap.append(0)

    def path_through(self, r: str) -> list[str] | None:
        """Send up to 2 units from X to r_in. If both arrive, return the glued s,t-path."""
        sink = 2 * self.index[r]
        used: list[int] = []  # arcs we changed, so we can reset cheaply afterwards
        flow = 0
        for _ in range(2):
            route = self._bfs(sink)
            if route is None:
                break
            for e in route:
                self.cap[e] -= 1
                self.cap[e ^ 1] += 1
                used.append(e)
            flow += 1
        path = self._read_path(sink) if flow == 2 else None
        for e in used:  # set all flow back to 0
            self.cap[e] = 1 if e % 2 == 0 else 0
            self.cap[e ^ 1] = 1 if (e ^ 1) % 2 == 0 else 0
        return path

    def _bfs(self, sink: int) -> list[int] | None:
        """Shortest route X -> sink in the leftover network, as a list of arcs."""
        came_by = {self.source: -1}
        queue = deque([self.source])
        while queue:
            a = queue.popleft()
            for e in self.adj[a]:
                b = self.head[e]
                if self.cap[e] > 0 and b not in came_by:
                    came_by[b] = e
                    if b == sink:
                        route = []
                        while b != self.source:
                            e = came_by[b]
                            route.append(e)
                            b = self.head[e ^ 1]
                        return route[::-1]
                    queue.append(b)
        return None

    def _read_path(self, sink: int) -> list[str]:
        """Follow the arcs that carry flow from s and from t to r, then glue."""

        def follow(start: str) -> list[str]:
            node, walk = 2 * self.index[start], [start]
            while node != sink:
                # The forward arc (even index) leaving `node` that carries flow (cap 0 left).
                node = next(self.head[e] for e in self.adj[node] if e % 2 == 0 and self.cap[e] == 0)
                if node % 2 == 0:  # arrived at some v_in
                    walk.append(self.names[node // 2])
            return walk

        from_s, from_t = follow(self.s), follow(self.t)
        return from_s + from_t[::-1][1:]
