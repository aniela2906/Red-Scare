import os
import time

import networkx as nx
import pytest

from runner import Results, load_instance, load_instances, parse_duration, run_experiment
from runner._timefmt import format_duration


def shortest_avoiding_red(inst):
    graph = inst.graph
    if graph.has_edge(inst.s, inst.t):
        return 1
    graph.remove_nodes_from([v for v in inst.red if v not in (inst.s, inst.t)])
    try:
        return nx.shortest_path_length(graph, inst.s, inst.t)
    except nx.NetworkXNoPath:
        return -1


def misbehaving(inst):
    if inst.name == "P3":
        raise KeyError("boom")
    if inst.name == "G-ex":
        time.sleep(30)
    if inst.name == "dodecahedron":
        os._exit(3)
    if inst.name == "wall-p-1":
        return True
    if inst.name == "wall-z-1":
        return None
    return "?"


SMALL = ["P3", "G-ex", "dodecahedron", "wall-p-1", "wall-z-1", "wall-n-1"]


@pytest.fixture(scope="module")
def mixed():
    start = time.perf_counter()
    results = run_experiment(misbehaving, SMALL, problem="none", timeout=1, verbose=False)
    return results, time.perf_counter() - start


def test_ok_answers():
    results = run_experiment(shortest_avoiding_red, ["G-ex", "P3"], problem="none")
    assert results["G-ex"].answer == 3
    assert results["P3"].answer == -1
    assert len(results.ok) == 2 and not results.failed


def test_each_status(mixed):
    results, _ = mixed
    status = {r.instance: r.status for r in results}
    assert status == {
        "G-ex": "timeout",
        "P3": "error",
        "dodecahedron": "crashed",
        "wall-p-1": "ok",
        "wall-z-1": "error",
        "wall-n-1": "ok",
    }
    assert "KeyError: 'boom'" in results["P3"].error
    assert "raise KeyError" in results["P3"].traceback
    assert "exit code 3" in results["dodecahedron"].error
    assert "forget a `return`" in results["wall-z-1"].error
    assert results["wall-p-1"].answer == "true"
    assert "expects a whole number" in results["wall-p-1"].warning
    assert results["wall-n-1"].answer == "?"
    assert [r.instance for r in results.unsolved] == ["wall-n-1"]


def test_timeout_is_enforced(mixed):
    _, elapsed = mixed
    assert elapsed < 10  # G-ex sleeps for 30 s but the limit is 1 s


def test_filters_and_lookup(mixed):
    results, _ = mixed
    assert {r.instance for r in results.failed} == {"G-ex", "P3", "dodecahedron", "wall-z-1"}
    assert [r.instance for r in results.timed_out] == ["G-ex"]
    assert {r.instance for r in results.errors} == {"P3", "dodecahedron", "wall-z-1"}
    assert results[0].instance == results.runs[0].instance
    assert "P3" in results
    with pytest.raises(KeyError, match="Did you mean 'G-ex'"):
        results["G-x"]
    assert {i.name for i in results.failed.instances()} <= set(SMALL)


def test_summary_and_show_error(mixed, capsys):
    results, _ = mixed
    results.summary()
    results.show_error("P3")
    out = capsys.readouterr().out
    assert "6 instances" in out and "KeyError" in out and "Traceback" in out


def test_not_implemented_stops_early(capsys):
    def solve(inst):
        raise NotImplementedError("write me")

    results = run_experiment(solve, ["G-ex", "P3", "wall-p-1"])
    assert [r.status for r in results] == ["error", "skipped", "skipped"]
    assert "not implemented yet" in capsys.readouterr().out
    assert not results.skipped.failed


def test_lambda_and_in_process():
    for isolate in (True, False):
        results = run_experiment(lambda inst: inst.n, "wall-p-1", isolate=isolate)
        assert results[0].answer == 8


def test_in_process_does_not_touch_the_loaded_graph():
    inst = load_instance("G-ex")
    run_experiment(shortest_avoiding_red, [inst], isolate=False)
    assert inst.n == 8


def test_answer_normalisation():
    answers = iter([False, 3.0, " TRUE ", "?!"])
    results = run_experiment(
        lambda i: next(answers), load_instances(max_n=8, limit=4), isolate=False
    )
    assert [r.answer for r in results] == ["false", 3, "true", "?!"]


@pytest.mark.parametrize(
    ("args", "kwargs", "error", "match"),
    [
        ((None,), {}, TypeError, "solver function"),
        ((lambda: 1,), {}, TypeError, "exactly one argument"),
        ((lambda i: 1,), {"problem": "sme"}, ValueError, "Did you mean 'some'"),
        ((lambda i: 1,), {"timeout": "5 parsecs"}, ValueError, "Unknown time unit"),
        ((lambda i: 1, []), {}, ValueError, "empty"),
        ((lambda i: 1, ["G-ex", "G-ex"]), {}, ValueError, "more than once"),
        ((lambda i: 1, 42), {}, TypeError, "instances must be"),
    ],
)
def test_bad_arguments(args, kwargs, error, match):
    with pytest.raises(error, match=match):
        run_experiment(*args, **kwargs)


def test_save_load_and_merge(tmp_path, mixed):
    results, _ = mixed
    path = results.save(tmp_path / "none.tsv")
    loaded = Results.load(path)
    assert loaded.problem == "none"
    assert [(r.instance, r.status, r.answer) for r in loaded] == [
        (r.instance, r.status, r.answer) for r in results
    ]
    rerun = run_experiment(lambda i: 7, ["P3"], problem="none")
    rerun.save(path)
    merged = Results.load(path)
    assert len(merged) == 6 and merged["P3"].answer == 7
    rerun.save(path, merge=False)
    assert len(Results.load(path)) == 1


def test_save_needs_a_path_without_problem():
    results = run_experiment(lambda i: 1, ["P3"])
    with pytest.raises(ValueError, match="pass a path"):
        results.save()


def test_load_rejects_other_files(tmp_path):
    bad = tmp_path / "x.tsv"
    bad.write_text("a\tb\n1\t2\n")
    with pytest.raises(ValueError, match="not a results file"):
        Results.load(bad)


@pytest.mark.parametrize(
    ("text", "seconds"),
    [(90, 90.0), ("90s", 90.0), ("20m", 1200.0), ("1h30m", 5400.0), ("1.5h", 5400.0), (None, None)],
)
def test_parse_duration(text, seconds):
    assert parse_duration(text) == seconds


@pytest.mark.parametrize("bad", [0, -5, "abc", "", "10x", True])
def test_parse_duration_rejects(bad):
    with pytest.raises((ValueError, TypeError)):
        parse_duration(bad)


def test_format_duration():
    assert format_duration(0.00001) == "<0.1ms"
    assert format_duration(1.234) == "1.23s"
    assert format_duration(1200) == "20m"
    assert format_duration(185) == "3m 05s"
    assert format_duration(None) == "no limit"


def count_vertices(inst):
    return inst.n


def test_spawn_mode_used_on_windows_and_macos(monkeypatch):
    import multiprocessing as mp

    monkeypatch.setattr("runner.experiment._mp_context", lambda: mp.get_context("spawn"))
    results = run_experiment(count_vertices, ["P3", "wall-p-1"], timeout="30s")
    assert [r.answer for r in results] == [3, 8]
    with pytest.raises(TypeError, match="top level of a .py file"):
        run_experiment(lambda inst: 1, "P3")
