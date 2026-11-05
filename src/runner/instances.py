"""Loading Red Scare instances into NetworkX graphs.

Every instance file looks like this (see ``red-scare/data/README.md``)::

    n m r
    s t
    <n vertex lines: "name" or "name *" for red vertices>
    <m edge lines: "u -- v" (undirected) or "u -> v" (directed)>

Example::

    from runner import load_instance, load_instances

    g = load_instance("G-ex")                 # one instance
    small = load_instances(max_n=1000)        # every instance with at most 1000 vertices
    walls = load_instances("wall-*")          # every wall instance
"""

from __future__ import annotations

import difflib
import fnmatch
import os
import re
from collections.abc import Iterable
from dataclasses import dataclass, field
from pathlib import Path

import networkx as nx
from tqdm.auto import tqdm

from ._paths import data_dir as _data_dir

__all__ = [
    "Instance",
    "InstanceFormatError",
    "InstanceNotFoundError",
    "list_families",
    "list_instances",
    "load_instance",
    "load_instances",
]

PathLike = str | os.PathLike[str]

# Show a progress bar when loading at least this many files.
_PROGRESS_THRESHOLD = 10


class InstanceFormatError(ValueError):
    """An instance file does not follow the Red Scare file format."""

    def __init__(self, path: Path, line: int | None, message: str):
        self.path = path
        self.line = line
        where = f"{path.name}, line {line}" if line is not None else path.name
        super().__init__(f"{where}: {message}")


class InstanceNotFoundError(LookupError):
    """No instance file with the requested name exists."""

    def __str__(self) -> str:  # LookupError would otherwise wrap the message in quotes
        return str(self.args[0]) if self.args else ""


@dataclass(frozen=True, eq=False)
class Instance:
    """One Red Scare instance: a graph, a start ``s``, an end ``t`` and red vertices.

    Attributes:
        name:   file name without ``.txt``, e.g. ``"G-ex"`` or ``"wall-p-10"``.
        family: the kind of graph, e.g. ``"wall-p"``, ``"grid"``, ``"common"``.
        graph:  a ``networkx.Graph`` (undirected) or ``networkx.DiGraph`` (directed).
                Every vertex has the attribute ``red`` (True/False), so
                ``graph.nodes[v]["red"]`` works as well as ``instance.is_red(v)``.
        s, t:   the start and end vertex. Vertex names are always strings.
        red:    the set of red vertices.
        path:   where the file was loaded from.
        self_loops_removed: how many ``v -- v`` edges the file had. They can never be part
                of a path, so they are left out of ``graph`` (some ``smallworld`` files have them).

    Your solver may change ``graph`` freely: the runner gives every run its own copy.
    """

    name: str
    family: str
    graph: nx.Graph = field(repr=False)
    s: str
    t: str
    red: frozenset[str] = field(repr=False)
    path: Path = field(repr=False)
    self_loops_removed: int = field(default=0, repr=False)

    @property
    def n(self) -> int:
        """Number of vertices."""
        return self.graph.number_of_nodes()

    @property
    def m(self) -> int:
        """Number of edges."""
        return self.graph.number_of_edges()

    @property
    def r(self) -> int:
        """Number of red vertices."""
        return len(self.red)

    @property
    def directed(self) -> bool:
        """True if the edges are directed (``u -> v``)."""
        return self.graph.is_directed()

    def is_red(self, vertex: str) -> bool:
        """True if ``vertex`` is red."""
        return vertex in self.red

    def copy(self) -> Instance:
        """A copy with its own graph, safe to modify."""
        return Instance(
            self.name,
            self.family,
            self.graph.copy(),
            self.s,
            self.t,
            self.red,
            self.path,
            self.self_loops_removed,
        )

    def __repr__(self) -> str:
        kind = "directed" if self.directed else "undirected"
        return f"Instance({self.name!r}, n={self.n}, m={self.m}, r={self.r}, {kind})"


# --------------------------------------------------------------------------- parsing


def family_of(name: str) -> str:
    """The graph family of an instance name: drop trailing parts that contain digits.

    >>> family_of("wall-p-10"), family_of("increase-n8-1"), family_of("P3"), family_of("G-ex")
    ('wall-p', 'increase', 'P3', 'G-ex')
    """
    parts = name.split("-")
    while len(parts) > 1 and any(ch.isdigit() for ch in parts[-1]):
        parts.pop()
    return "-".join(parts)


def _natural_key(text: str) -> list[object]:
    """Sort key so that ``wall-p-2`` comes before ``wall-p-10``."""
    return [int(tok) if tok.isdigit() else tok.casefold() for tok in re.split(r"(\d+)", text)]


def _parse_header(path: Path, line: str) -> tuple[int, int, int]:
    parts = line.split()
    if len(parts) != 3 or not all(p.isdigit() for p in parts):
        raise InstanceFormatError(
            path, 1, f"expected three non-negative whole numbers 'n m r', found {line.strip()!r}."
        )
    n, m, r = (int(p) for p in parts)
    return n, m, r


def _read_header(path: Path) -> tuple[int, int, int]:
    """Read only the first line, so filtering by size never parses whole files."""
    with path.open(encoding="utf-8") as f:
        first = f.readline()
    if not first.strip():
        raise InstanceFormatError(
            path, 1, "the file is empty (expected 'n m r' on the first line)."
        )
    return _parse_header(path, first)


def parse_instance(path: PathLike) -> Instance:
    """Parse one instance file. Most people want :func:`load_instance` instead."""
    path = Path(path)
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise InstanceFormatError(path, None, "the file is not a UTF-8 text file.") from exc

    # (line number, stripped content) for every non-blank line; tolerates CRLF and stray spaces.
    lines = [(i, ln.strip()) for i, ln in enumerate(text.splitlines(), start=1) if ln.strip()]
    if not lines:
        raise InstanceFormatError(
            path, 1, "the file is empty (expected 'n m r' on the first line)."
        )
    if len(lines) < 2:
        raise InstanceFormatError(path, None, "the file ends before the 's t' line.")

    header_no, header = lines[0]
    n, m, r = _parse_header(path, header)
    if r > n:
        raise InstanceFormatError(path, header_no, f"r={r} red vertices but only n={n} vertices.")

    st_no, st_line = lines[1]
    st = st_line.split()
    if len(st) != 2:
        raise InstanceFormatError(
            path, st_no, f"expected the start and end vertex 's t', found {st_line!r}."
        )
    s, t = st

    vertex_lines = lines[2 : 2 + n]
    edge_lines = lines[2 + n :]
    if len(vertex_lines) < n:
        raise InstanceFormatError(
            path, None, f"the header says n={n} vertices but the file only has {len(vertex_lines)}."
        )

    vertices: list[str] = []
    red: set[str] = set()
    seen: set[str] = set()
    for line_no, line in vertex_lines:
        parts = line.split()
        if len(parts) == 2 and parts[1] == "*":
            red.add(parts[0])
        elif len(parts) != 1:
            hint = (
                " (is the vertex count n in the header too large?)"
                if "--" in line or "->" in line
                else ""
            )
            raise InstanceFormatError(
                path,
                line_no,
                f"expected a vertex name, optionally followed by ' *', found {line!r}{hint}.",
            )
        name = parts[0]
        if name in seen:
            raise InstanceFormatError(path, line_no, f"vertex {name!r} is listed twice.")
        seen.add(name)
        vertices.append(name)

    if len(red) != r:
        raise InstanceFormatError(
            path,
            header_no,
            f"the header says r={r} red vertices but {len(red)} are marked with '*'.",
        )
    for label, v in (("start vertex s", s), ("end vertex t", t)):
        if v not in seen:
            raise InstanceFormatError(path, st_no, f"the {label} {v!r} is not in the vertex list.")

    edges: list[tuple[str, str]] = []
    self_loops = 0
    arrow: str | None = None
    for line_no, line in edge_lines:
        parts = line.split()
        if len(parts) != 3 or parts[1] not in ("--", "->"):
            raise InstanceFormatError(
                path, line_no, f"expected an edge 'u -- v' or 'u -> v', found {line!r}."
            )
        u, op, v = parts
        if arrow is None:
            arrow = op
        elif op != arrow:
            raise InstanceFormatError(
                path, line_no, "the file mixes undirected ('--') and directed ('->') edges."
            )
        for endpoint in (u, v):
            if endpoint not in seen:
                raise InstanceFormatError(
                    path,
                    line_no,
                    f"edge {line!r} uses vertex {endpoint!r}, which is not in the vertex list.",
                )
        if u == v:
            self_loops += 1  # harmless for simple paths, but confuses e.g. nx.is_bipartite
            continue
        edges.append((u, v))

    if len(edges) + self_loops != m:
        raise InstanceFormatError(
            path,
            None,
            f"the header says m={m} edges but the file has {len(edges) + self_loops} edge lines.",
        )

    graph: nx.Graph = nx.DiGraph() if arrow == "->" else nx.Graph()
    graph.add_nodes_from((v, {"red": v in red}) for v in vertices)
    graph.add_edges_from(edges)
    if graph.number_of_edges() != len(edges):
        raise InstanceFormatError(
            path,
            None,
            f"the file lists the same edge more than once ({len(edges)} edge lines, "
            f"{graph.number_of_edges()} distinct edges); Red Scare graphs are simple.",
        )

    name = path.name.removesuffix(".txt")
    graph.graph.update(name=name, s=s, t=t)
    return Instance(name, family_of(name), graph, s, t, frozenset(red), path.resolve(), self_loops)


# --------------------------------------------------------------------------- finding files


def _all_files(data_dir: PathLike | None) -> dict[str, Path]:
    folder = _data_dir(data_dir)
    files = {p.name.removesuffix(".txt"): p for p in folder.glob("*.txt") if p.is_file()}
    if not files:
        raise FileNotFoundError(f"The data folder {folder} contains no .txt instance files.")
    return files


def _suggest(word: str, options: Iterable[str]) -> str:
    matches = difflib.get_close_matches(word, list(options), n=3, cutoff=0.6)
    if not matches:
        return ""
    return " Did you mean " + " or ".join(repr(m) for m in matches) + "?"


def _resolve(name_or_path: PathLike, files: dict[str, Path]) -> Path:
    """Turn ``"G-ex"``, ``"G-ex.txt"`` or a path into the path of an existing file."""
    raw = os.fspath(name_or_path)
    key = Path(raw).name.removesuffix(".txt") if os.sep not in raw and "/" not in raw else None
    if key is not None and key in files:
        return files[key]
    path = Path(raw).expanduser()
    if path.is_file():
        return path
    if path.with_suffix(".txt").is_file() and path.suffix != ".txt":
        return path.with_suffix(".txt")
    hint = _suggest(key or path.name.removesuffix(".txt"), files)
    raise InstanceNotFoundError(
        f"No instance called {raw!r}.{hint}\nUse runner.list_instances() to see every name."
    )


def list_instances(data_dir: PathLike | None = None) -> list[str]:
    """Names of every instance in the data folder, in natural order (``wall-p-2`` before ``wall-p-10``)."""
    return sorted(_all_files(data_dir), key=_natural_key)


def list_families(data_dir: PathLike | None = None) -> dict[str, int]:
    """Every graph family and how many instances it has, e.g. ``{"wall-p": 8, ...}``."""
    counts: dict[str, int] = {}
    for name in list_instances(data_dir):
        fam = family_of(name)
        counts[fam] = counts.get(fam, 0) + 1
    return dict(sorted(counts.items(), key=lambda kv: _natural_key(kv[0])))


# --------------------------------------------------------------------------- public loaders


def load_instance(name_or_path: PathLike, *, data_dir: PathLike | None = None) -> Instance:
    """Load a single instance.

    Args:
        name_or_path: an instance name such as ``"G-ex"`` (``"G-ex.txt"`` also works)
            or the path to any file in the Red Scare format.
        data_dir: where the instances are. Normally found automatically.

    Example::

        g = load_instance("G-ex")
        print(g)              # Instance('G-ex', n=8, m=9, r=3, undirected)
        print(g.s, g.t)       # 0 3
    """
    if isinstance(name_or_path, Instance):
        return name_or_path
    if not isinstance(name_or_path, (str, os.PathLike)):
        raise TypeError(
            f"load_instance expects a name like 'G-ex' or a file path, not {type(name_or_path).__name__}."
        )
    return parse_instance(_resolve(name_or_path, _all_files(data_dir)))


def _as_list(value: str | Iterable[str] | None, what: str) -> list[str] | None:
    if value is None:
        return None
    if isinstance(value, (str, os.PathLike)):
        return [os.fspath(value)]
    try:
        items = [os.fspath(v) for v in value]
    except TypeError:
        raise TypeError(f"{what} must be a string or a list of strings, not {value!r}.") from None
    return items


def load_instances(
    names: str | Iterable[str] | None = None,
    *,
    families: str | Iterable[str] | None = None,
    min_n: int | None = None,
    max_n: int | None = None,
    directed: bool | None = None,
    limit: int | None = None,
    progress: bool = True,
    data_dir: PathLike | None = None,
) -> list[Instance]:
    """Load many instances at once. With no arguments, loads all of them.

    Args:
        names: which instances to load. One name or pattern, or a list of them.
            Patterns use ``*`` as a wildcard: ``"wall-*"``, ``"*-10"``, ``"grid-5-?"``.
        families: only these graph families, e.g. ``"grid"`` or ``["wall-p", "wall-z"]``
            (see :func:`list_families`).
        min_n, max_n: only instances with at least / at most this many vertices.
        directed: ``True`` for only directed graphs, ``False`` for only undirected ones.
        limit: load at most this many (after sorting, so you get the smallest ones).
        progress: show a progress bar while loading many files.
        data_dir: where the instances are. Normally found automatically.

    The result is sorted by family, then by size, so runs are always in the same order.

    Examples::

        everything = load_instances()
        quick_test = load_instances(max_n=100)
        walls      = load_instances("wall-*")
        two        = load_instances(["G-ex", "P3"])
        grids      = load_instances(families="grid", max_n=1000)
    """
    files = _all_files(data_dir)
    for arg_name, value, lowest in (("min_n", min_n, 0), ("max_n", max_n, 0), ("limit", limit, 1)):
        if value is not None and (
            isinstance(value, bool) or not isinstance(value, int) or value < lowest
        ):
            raise ValueError(f"{arg_name} must be a whole number >= {lowest}, got {value!r}.")
    if directed is not None and not isinstance(directed, bool):
        raise TypeError(f"directed must be True, False or None, got {directed!r}.")

    # 1. Pick files by name / pattern.
    patterns = _as_list(names, "names")
    if patterns is None:
        chosen = dict(files)
    else:
        chosen = {}
        for pattern in patterns:
            if any(ch in pattern for ch in "*?["):
                hits = {
                    k: p
                    for k, p in files.items()
                    if fnmatch.fnmatchcase(k, pattern.removesuffix(".txt"))
                }
                if not hits:
                    raise InstanceNotFoundError(
                        f"The pattern {pattern!r} matches no instance. "
                        f"Known families: {', '.join(list_families(data_dir))}."
                    )
                chosen.update(hits)
            else:
                path = _resolve(pattern, files)
                chosen[path.name.removesuffix(".txt")] = path

    # 2. Filter by family.
    wanted_families = _as_list(families, "families")
    if wanted_families is not None:
        known = {family_of(k) for k in files}
        for fam in wanted_families:
            if fam not in known:
                raise InstanceNotFoundError(
                    f"Unknown family {fam!r}.{_suggest(fam, known)}\n"
                    f"Known families: {', '.join(sorted(known, key=_natural_key))}."
                )
        chosen = {k: p for k, p in chosen.items() if family_of(k) in wanted_families}

    # 3. Filter by size using only the header line, then sort.
    headers = {k: _read_header(p) for k, p in chosen.items()}
    keep = [
        k
        for k in chosen
        if (min_n is None or headers[k][0] >= min_n) and (max_n is None or headers[k][0] <= max_n)
    ]
    keep.sort(key=lambda k: (_natural_key(family_of(k)), headers[k][0], _natural_key(k)))

    # 4. Parse. The direction filter needs the edges, so it is applied while parsing.
    result: list[Instance] = []
    show_bar = progress and len(keep) >= _PROGRESS_THRESHOLD
    for key in tqdm(keep, desc="Loading instances", unit="file", disable=not show_bar, leave=False):
        if limit is not None and len(result) >= limit:
            break
        inst = parse_instance(chosen[key])
        if directed is None or inst.directed == directed:
            result.append(inst)

    if not result:
        filters = {
            "names": names,
            "families": families,
            "min_n": min_n,
            "max_n": max_n,
            "directed": directed,
            "limit": limit,
        }
        used = ", ".join(f"{k}={v!r}" for k, v in filters.items() if v is not None)
        raise InstanceNotFoundError(f"No instance matches {used or 'your filters'}.")
    return result
