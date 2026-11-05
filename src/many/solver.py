"""Problem Many."""

from runner import Instance


def solve(instance: Instance) -> int:
    """The maximum number of red vertices on any s,t-path.

    Return -1 if there is no s,t-path. Example: G-ex -> 2 (path 0, 5, 6, 7, 3).

    Return "?" if you cannot solve this instance, or "?!" if the problem is hard for it.

    Useful things on ``instance``:
        instance.graph       the networkx Graph (undirected) or DiGraph (directed)
        instance.s, .t       start and end vertex (vertex names are strings)
        instance.red         set of red vertices; instance.is_red(v) also works
        instance.directed    True for directed graphs
    You may modify instance.graph: every run gets its own copy.
    """
    raise NotImplementedError("Write your algorithm for Many in src/many/solver.py.")
