
"""Problem None."""

import networkx as nx
from runner import Instance


def solve(instance: Instance) -> int:
    """Length of a shortest s,t-path whose internal vertices are all non-red.

    s and t themselves may be red. If the edge st exists the answer is 1.
    Return -1 if there is no such path. Example: G-ex -> 3 (path 0, 1, 2, 3).

    Return "?" if you cannot solve this instance, or "?!" if the problem is hard for it.

    Useful things on ``instance``:
        instance.graph       the networkx Graph (undirected) or DiGraph (directed)
        instance.s, .t       start and end vertex (vertex names are strings)
        instance.red         set of red vertices; instance.is_red(v) also works
        instance.directed    True for directed graphs
    You may modify instance.graph: every run gets its own copy.
    """

    # get graph and vertices from the instance
    graph = instance.graph
    s = instance.s
    t = instance.t
    red = instance.red

    # remove all red vertices (since we dont want them on the path) except start and end
    red_to_remove = set(red) - {s, t}
    graph.remove_nodes_from(red_to_remove)

    # shortest path using BFS
    try:
        return nx.shortest_path_length(
            graph,
            source=s,
            target=t
        )

    # Return -1 if no valid path exists
    except nx.NetworkXNoPath:
        return -1
