"""Problem Alternate."""

from runner import Instance
from collections import deque


def solve(instance: Instance) -> bool:
    """True if there is an s,t-path that alternates between red and non-red vertices.

    Every edge on the path must join a red and a non-red vertex.
    Example: G-ex -> True (path 0, 5, 6, 7, 3).

    Return "?" if you cannot solve this instance, or "?!" if the problem is hard for it.

    Useful things on ``instance``:
        instance.graph       the networkx Graph (undirected) or DiGraph (directed)
        instance.s, .t       start and end vertex (vertex names are strings)
        instance.red         set of red vertices; instance.is_red(v) also works
        instance.directed    True for directed graphs
    You may modify instance.graph: every run gets its own copy.
    """

    graph = instance.graph
    s = instance.s
    t = instance.t
    red = instance.red

    if s == t:
        return True

    seen = {s}              # vertices already discovered (prevents loops)
    queue = deque([s])      # BFS queue: first discovered, first processed

    while queue:
        u = queue.popleft()                 # take the next vertex to explore
        for v in graph.adj[u]:            # look at every neighbour of u
            # Only cross the edge u -> v if exactly one endpoint is red.
            if (u in red) != (v in red):
                if v == t:                  # reached the target: success
                    return True
                if v not in seen:           # first time we see v
                    seen.add(v)
                    queue.append(v)

    # The queue is empty and t was never reached: no alternating path exists.
    return False