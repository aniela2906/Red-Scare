"""Problem Few."""

from runner import Instance


def solve(instance: Instance) -> int:
    """The minimum number of red vertices on any s,t-path.

    Return -1 if there is no s,t-path. Example: G-ex -> 0 (path 0, 1, 2, 3).

    Return "?" if you cannot solve this instance, or "?!" if the problem is hard for it.

    Useful things on ``instance``:
        instance.graph       the networkx Graph (undirected) or DiGraph (directed)
        instance.s, .t       start and end vertex (vertex names are strings)
        instance.red         set of red vertices; instance.is_red(v) also works
        instance.directed    True for directed graphs
    You may modify instance.graph: every run gets its own copy.
    """
    raise NotImplementedError("Write your algorithm for Few in src/few/solver.py.")
