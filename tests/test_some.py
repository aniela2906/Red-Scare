"""Check the Some solver against brute force (try every simple path) on small random graphs."""

import itertools
import random

import networkx as nx
import pytest

from runner import Instance, load_instance
from some.solver import find_path, solve


def make(graph, s, t, red):
    for v in graph:
        graph.nodes[v]["red"] = v in red
    return Instance(
        name="test", family="test", graph=graph, s=s, t=t, red=frozenset(red), path=None
    )


def brute_force(inst):
    return any(
        any(v in inst.red for v in p) for p in nx.all_simple_paths(inst.graph, inst.s, inst.t)
    ) or (inst.s == inst.t and inst.s in inst.red)


def check_path(inst, path):
    assert path[0] == inst.s and path[-1] == inst.t
    assert len(set(path)) == len(path), "vertex repeated"
    assert any(v in inst.red for v in path), "no red vertex"
    for u, v in itertools.pairwise(path):
        assert inst.graph.has_edge(u, v), f"{u}-{v} is not an edge"


def random_instance(rng, directed):
    n = rng.randint(2, 9)
    p = rng.uniform(0.15, 0.6)
    if directed:  # random DAG: only edges from lower to higher number
        graph = nx.DiGraph()
        graph.add_nodes_from(map(str, range(n)))
        graph.add_edges_from(
            (str(i), str(j)) for i in range(n) for j in range(i + 1, n) if rng.random() < p
        )
    else:
        graph = nx.relabel_nodes(nx.gnp_random_graph(n, p, seed=rng.randrange(10**9)), str)
    s, t = rng.sample(sorted(graph.nodes), 2)
    red = {v for v in graph if rng.random() < 0.25}
    return make(graph, s, t, red)


@pytest.mark.parametrize("directed", [False, True])
def test_matches_brute_force(directed):
    rng = random.Random(7)
    for _ in range(3000):
        inst = random_instance(rng, directed)
        expected = brute_force(inst)
        path = find_path(inst)
        assert (path is not None) == expected, (inst.graph.edges, inst.s, inst.t, inst.red)
        if path is not None:
            check_path(inst, path)


def test_needs_undo_step():
    # The example from the explainer: t's only way to r goes through a.
    g = nx.Graph(
        [("s", "a"), ("a", "r"), ("s", "b"), ("b", "c"), ("c", "r"), ("t", "d"), ("d", "a")]
    )
    inst = make(g, "s", "t", {"r"})
    assert find_path(inst) == ["s", "b", "c", "r", "a", "d", "t"]


def test_walk_trap_is_false():
    g = nx.Graph(
        [
            ("s", "a"),
            ("s", "b"),
            ("a", "c"),
            ("b", "c"),
            ("c", "r"),
            ("r", "d"),
            ("d", "c"),
            ("c", "t"),
        ]
    )
    assert solve(make(g, "s", "t", {"r"})) is False


def test_directed_cycle_gives_hard():
    g = nx.DiGraph([("s", "a"), ("a", "s"), ("a", "t")])
    assert solve(make(g, "s", "t", {"a"})) == "?!"


def test_g_ex():
    inst = load_instance("G-ex")
    assert solve(inst) is True
    check_path(inst, find_path(inst))
