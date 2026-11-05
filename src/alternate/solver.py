"""Problem Alternate."""

from runner import Instance


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
    raise NotImplementedError("Write your algorithm for Alternate in src/alternate/solver.py.")
