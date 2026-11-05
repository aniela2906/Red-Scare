"""Problem None."""

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
    raise NotImplementedError("Write your algorithm for None in src/none/solver.py.")
