import networkx as nx
import pytest

from runner import (
    InstanceFormatError,
    InstanceNotFoundError,
    list_families,
    list_instances,
    load_instance,
    load_instances,
)
from runner.instances import _read_header, _resolve, family_of, parse_instance


def test_g_ex_matches_the_assignment():
    g = load_instance("G-ex")
    assert (g.n, g.m, g.r) == (8, 9, 3)
    assert (g.s, g.t) == ("0", "3")
    assert g.red == {"4", "5", "7"}
    assert not g.directed and isinstance(g.graph, nx.Graph)
    assert g.graph.nodes["4"]["red"] is True and g.is_red("5") and not g.is_red("0")
    assert repr(g) == "Instance('G-ex', n=8, m=9, r=3, undirected)"


@pytest.mark.parametrize("name", ["G-ex", "G-ex.txt"])
def test_name_with_or_without_extension(name):
    assert load_instance(name).name == "G-ex"


def test_load_by_path():
    path = load_instance("P3").path
    assert load_instance(str(path)).name == "P3"


def test_every_data_file_parses_and_matches_its_header():
    names = list_instances()
    assert len(names) == 154
    files = {}
    for name in names:
        inst = load_instance(name)
        n, m, r = _read_header(inst.path)
        assert (inst.n, inst.m + inst.self_loops_removed, inst.r) == (n, m, r), name
        assert inst.s in inst.graph and inst.t in inst.graph
        assert nx.number_of_selfloops(inst.graph) == 0
        files[name] = inst.directed
    assert sum(files.values()) == 31


def test_self_loops_are_dropped():
    inst = load_instance("smallworld-10-0")
    assert inst.self_loops_removed == 5


def test_edgeless_graph():
    inst = load_instance("common-1-20")
    assert inst.m == 0 and inst.n == 20


def test_directed_graph():
    inst = load_instance("increase-n8-1")
    assert inst.directed and isinstance(inst.graph, nx.DiGraph)


def test_unknown_name_suggests_close_match():
    with pytest.raises(InstanceNotFoundError, match="Did you mean 'G-ex'"):
        load_instance("G-x")


def test_families():
    fams = list_families()
    assert fams["wall-p"] == 8 and fams["G-ex"] == 1 and fams["increase"] == 18
    assert sum(fams.values()) == 154
    assert family_of("increase-n8-1") == "increase"
    assert family_of("ski-level10-2") == "ski"
    assert family_of("P3") == "P3"


def test_glob_and_natural_order():
    names = [i.name for i in load_instances("wall-p-*")]
    assert names == [f"wall-p-{k}" for k in (1, 2, 3, 4, 10, 100, 1000, 10000)]


def test_filters():
    small = load_instances(max_n=10)
    assert small and all(i.n <= 10 for i in small)
    assert all(i.directed for i in load_instances(max_n=50, directed=True))
    assert [i.name for i in load_instances(families="grid", max_n=25)] == [
        "grid-5-0",
        "grid-5-1",
        "grid-5-2",
    ]
    assert len(load_instances(limit=3)) == 3
    assert [i.name for i in load_instances(["P3", "G-ex"])] == ["G-ex", "P3"]


@pytest.mark.parametrize(
    ("kwargs", "error", "match"),
    [
        ({"names": "zz*"}, InstanceNotFoundError, "matches no instance"),
        ({"families": "wal"}, InstanceNotFoundError, "Did you mean"),
        ({"max_n": 2}, InstanceNotFoundError, "No instance matches max_n=2"),
        ({"max_n": -1}, ValueError, "max_n"),
        ({"limit": 0}, ValueError, "limit"),
        ({"directed": "yes"}, TypeError, "directed"),
    ],
)
def test_bad_filters(kwargs, error, match):
    with pytest.raises(error, match=match):
        load_instances(**kwargs)


GOOD = "3 2 1\na c\na\nb *\nc\na -- b\nb -- c\n"


def test_tolerates_crlf_trailing_spaces_and_blank_lines(write_instance):
    text = GOOD.replace("\n", "  \r\n") + "\r\n\r\n"
    inst = parse_instance(write_instance(text))
    assert (inst.n, inst.m, inst.red) == (3, 2, frozenset({"b"}))


def test_s_equals_t(write_instance):
    inst = parse_instance(write_instance("2 1 0\na a\na\nb\na -- b\n"))
    assert inst.s == inst.t == "a"


@pytest.mark.parametrize(
    ("text", "line", "match"),
    [
        ("", 1, "empty"),
        ("3 2\na c\n", 1, "three non-negative whole numbers"),
        ("3 2 1\na\n", 2, "'s t'"),
        ("3 2 1\na z\na\nb *\nc\na -- b\nb -- c\n", 2, "'z' is not in the vertex list"),
        ("3 2 1\na c\na\nb *\nc\na -- b\nb -- x\n", 7, "'x', which is not in the vertex list"),
        ("3 2 1\na c\na\nb *\nc\na -- b\nb - c\n", 7, "expected an edge"),
        ("3 2 1\na c\na\nb *\nc\na -- b\nb -> c\n", 7, "mixes"),
        ("3 2 1\na c\na\na *\nc\na -- c\nc -- a\n", 4, "listed twice"),
        ("3 2 2\na c\na\nb *\nc\na -- b\nb -- c\n", 1, "r=2"),
        ("3 3 1\na c\na\nb *\nc\na -- b\nb -- c\n", None, "m=3"),
        ("3 2 1\na c\na\nb *\nc\na -- b\nb -- a\n", None, "more than once"),
        ("4 2 1\na c\na\nb *\nc\na -- b\nb -- c\n", 6, "vertex count n"),
    ],
)
def test_format_errors_point_to_the_line(write_instance, text, line, match):
    with pytest.raises(InstanceFormatError, match=match) as info:
        parse_instance(write_instance(text))
    assert info.value.line == line
    assert "tiny.txt" in str(info.value)


def test_copy_is_independent():
    g = load_instance("G-ex")
    c = g.copy()
    c.graph.remove_node("4")
    assert "4" in g.graph and "4" not in c.graph


def test_resolve_rejects_missing_path(tmp_path):
    with pytest.raises(InstanceNotFoundError):
        _resolve(str(tmp_path / "nope.txt"), {})


def test_data_dir_env_var(monkeypatch, tmp_path, write_instance):
    write_instance(GOOD, "mine.txt")
    monkeypatch.setenv("RED_SCARE_DATA", str(tmp_path))
    assert list_instances() == ["mine"]
    monkeypatch.setenv("RED_SCARE_DATA", str(tmp_path / "missing"))
    with pytest.raises(FileNotFoundError, match="RED_SCARE_DATA"):
        list_instances()
