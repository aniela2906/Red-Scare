"""Problem Some."""

from runner import Instance


def solve(instance: Instance) -> bool:
    """True if some s,t-path (a path: no repeated vertices) contains a red vertex.

    Example: G-ex -> True (path 0, 4, 3).

    Return "?" if you cannot solve this instance, or "?!" if the problem is hard for it.

    Useful things on ``instance``:
        instance.graph       the networkx Graph (undirected) or DiGraph (directed)
        instance.s, .t       start and end vertex (vertex names are strings)
        instance.red         set of red vertices; instance.is_red(v) also works
        instance.directed    True for directed graphs
    You may modify instance.graph: every run gets its own copy.
    """
    raise NotImplementedError("Write your algorithm for Some in src/some/solver.py.")
