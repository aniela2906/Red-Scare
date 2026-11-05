"""Drawing instances with matplotlib, e.g. to understand why a solver failed.

Examples::

    from runner import draw, draw_many, load_instance

    draw("G-ex")                                  # by name
    draw(load_instance("G-ex"), path=["0", "1", "2", "3"])   # highlight a path
    draw("rusty-1-2000", around="rusty", radius=2)           # part of a big graph
    draw_many(results.failed)                     # every failed instance of an experiment
"""

from __future__ import annotations

import itertools
import math
import os
import re
from collections.abc import Collection, Iterable, Sequence
from pathlib import Path
from typing import Any

import networkx as nx

from ._paths import repo_root
from .instances import Instance, load_instance

__all__ = ["draw", "draw_many"]

RED = "#d62728"
GREY = "#c9ccd1"
EDGE = "#8a8f98"
START = "#2ca02c"
END = "#1f77b4"
PATH = "#ff7f0e"

_COORD_NAME = re.compile(r"^(\d+)_(\d+)$")
LAYOUTS = ("auto", "grid", "spring", "circular", "spectral", "shell", "kamada_kawai")


def _as_instance(item: Any) -> Instance:
    if isinstance(item, Instance):
        return item
    if isinstance(item, (str, os.PathLike)):
        return load_instance(item)
    name = getattr(item, "instance", None)  # a RunResult
    if isinstance(name, str):
        return load_instance(name)
    raise TypeError(f"Can only draw an Instance, an instance name or a run result, not {item!r}.")


def _layout(graph: nx.Graph, layout: str, seed: int) -> dict[Any, tuple[float, float]]:
    if layout not in LAYOUTS:
        raise ValueError(f"Unknown layout {layout!r}. Choose one of: {', '.join(LAYOUTS)}.")
    graph = graph.to_undirected(as_view=True)  # directed distances give lopsided layouts
    coords = {v: _COORD_NAME.match(str(v)) for v in graph}
    has_coords = len(graph) > 0 and all(coords.values())
    if layout == "grid" or (layout == "auto" and has_coords):
        if not has_coords:
            raise ValueError("layout='grid' needs vertex names like '3_4' (x_y coordinates).")
        return {v: (int(m.group(1)), -int(m.group(2))) for v, m in coords.items()}  # type: ignore[union-attr]
    if layout == "auto" and len(graph) <= 60 and len(graph) > 1 and nx.is_connected(graph):
        return nx.kamada_kawai_layout(graph)  # tidier than spring layout for small graphs
    if layout in ("auto", "spring"):
        k = 1.5 / math.sqrt(max(len(graph), 1))
        return nx.spring_layout(graph, seed=seed, k=k, iterations=100 if len(graph) <= 200 else 50)
    if layout == "kamada_kawai":
        return nx.kamada_kawai_layout(graph)
    return getattr(nx, f"{layout}_layout")(graph)


def _path_edges(instance: Instance, path: Sequence[str]) -> tuple[list, list]:
    """Split the steps of ``path`` into real edges and steps that are not edges of the graph."""
    unknown = [v for v in path if v not in instance.graph]
    if unknown:
        raise ValueError(f"The path uses vertices that are not in {instance.name}: {unknown[:5]}.")
    good, bad = [], []
    for u, v in itertools.pairwise(path):
        (good if instance.graph.has_edge(u, v) else bad).append((u, v))
    return good, bad


def _node_size(n: int) -> float:
    if n <= 30:
        return 380
    if n <= 100:
        return 160
    if n <= 300:
        return 60
    return 25


def draw(
    instance: Instance | str,
    *,
    path: Sequence[str] | None = None,
    highlight: Collection[str] | None = None,
    around: str | None = None,
    radius: int = 2,
    layout: str = "auto",
    labels: bool | str = "auto",
    max_nodes: int | None = 500,
    title: str | None = None,
    ax: Any = None,
    save: str | os.PathLike[str] | None = None,
    show: bool = True,
    seed: int = 1,
) -> Any:
    """Draw an instance: red vertices in red, ``s`` and ``t`` circled, arrows if directed.

    Args:
        instance: an :class:`Instance` or an instance name such as ``"G-ex"``.
        path: a list of vertices to highlight as a path, e.g. the path your solver found.
        highlight: extra vertices to circle in orange.
        around, radius: draw only the vertices at most ``radius`` steps from ``around``.
            Use this for big graphs, e.g. ``draw("rusty-1-2000", around="rusty")``.
        layout: ``"auto"`` (grid coordinates when the vertex names are ``x_y``, otherwise
            a spring layout), or ``"grid"``, ``"spring"``, ``"circular"``, ``"spectral"``,
            ``"shell"``, ``"kamada_kawai"``.
        labels: show vertex names. ``"auto"`` shows them on small drawings only.
        max_nodes: refuse to draw more vertices than this (drawing is slow and unreadable).
            ``None`` removes the limit.
        title: the title (default: name and size of the instance).
        ax: a matplotlib ``Axes`` to draw into (for your own subplots).
        save: also save the picture to this file, e.g. ``"g-ex.png"`` or ``"g-ex.pdf"``.
        show: open the picture. Without a screen it is saved to ``figures/<name>.png`` instead.
        seed: random seed of the spring layout, so the same graph always looks the same.

    Returns:
        The matplotlib ``Axes`` the graph was drawn on.
    """
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D

    inst = _as_instance(instance)
    graph = inst.graph
    subtitle = ""
    if around is not None:
        if around not in graph:
            raise ValueError(f"Vertex {around!r} is not in {inst.name}.")
        if not isinstance(radius, int) or radius < 0:
            raise ValueError(f"radius must be a whole number >= 0, got {radius!r}.")
        graph = nx.ego_graph(graph, around, radius=radius, undirected=True)
        subtitle = f"\naround {around!r}, radius {radius}: {len(graph)} of {inst.n} vertices"

    if max_nodes is not None and len(graph) > max_nodes:
        raise ValueError(
            f"{inst.name} has {len(graph)} vertices, too many to draw readably "
            f"(max_nodes={max_nodes}).\n"
            f"  - draw a part of it:  draw({inst.name!r}, around={inst.s!r}, radius=2)\n"
            f"  - or draw it anyway:  draw({inst.name!r}, max_nodes=None)   (can be slow)"
        )

    path = list(path) if path is not None else []
    good_steps, bad_steps = _path_edges(inst, path) if path else ([], [])
    highlight = set(highlight or ()) | set(path)

    created = ax is None
    if created:
        size = 6 if len(graph) <= 60 else 9
        _, ax = plt.subplots(figsize=(size + 1, size))
    n = len(graph)
    pos = _layout(graph, layout, seed)
    node_size = _node_size(n)
    nodes = list(graph)

    def ring(v: str) -> tuple[str, float]:
        if v == inst.s:
            return START, 3.0
        if v == inst.t:
            return END, 3.0
        if v in highlight:
            return PATH, 2.5
        return "white", 0.8

    rings = [ring(v) for v in nodes]

    def arrows(size: int) -> dict[str, Any]:
        # Arrow options only apply to directed graphs (networkx warns otherwise).
        if not graph.is_directed():
            return {"arrows": False}
        return {"arrows": True, "arrowstyle": "-|>", "arrowsize": size, "node_size": node_size}

    nx.draw_networkx_edges(
        graph,
        pos,
        ax=ax,
        edge_color=EDGE,
        width=1.0 if n <= 300 else 0.5,
        **arrows(12 if n <= 100 else 6),
    )
    if good_steps:
        nx.draw_networkx_edges(
            graph, pos, edgelist=good_steps, ax=ax, edge_color=PATH, width=3.0, **arrows(14)
        )
    visible_bad = [(u, v) for u, v in bad_steps if u in pos and v in pos]
    if visible_bad:
        nx.draw_networkx_edges(
            graph,
            pos,
            edgelist=visible_bad,
            ax=ax,
            edge_color=RED,
            width=2.0,
            style="dashed",
            arrows=False,
        )
    nx.draw_networkx_nodes(
        graph,
        pos,
        nodelist=nodes,
        ax=ax,
        node_size=node_size,
        node_color=[RED if v in inst.red else GREY for v in nodes],
        edgecolors=[c for c, _ in rings],
        linewidths=[w for _, w in rings],
    )
    show_labels = n <= 60 if labels == "auto" else bool(labels)
    if show_labels:
        nx.draw_networkx_labels(graph, pos, ax=ax, font_size=8 if n <= 30 else 6)

    kind = "directed" if inst.directed else "undirected"
    ax.set_title(title or f"{inst.name}  (n={inst.n}, m={inst.m}, r={inst.r}, {kind}){subtitle}")
    legend = [
        Line2D(
            [],
            [],
            marker="o",
            ls="",
            markerfacecolor=RED,
            markeredgecolor="white",
            markersize=9,
            label="red",
        ),
        Line2D(
            [],
            [],
            marker="o",
            ls="",
            markerfacecolor=GREY,
            markeredgecolor="white",
            markersize=9,
            label="not red",
        ),
        Line2D(
            [],
            [],
            marker="o",
            ls="",
            markerfacecolor="none",
            markeredgecolor=START,
            markeredgewidth=2.5,
            markersize=9,
            label=f"s = {inst.s}",
        ),
        Line2D(
            [],
            [],
            marker="o",
            ls="",
            markerfacecolor="none",
            markeredgecolor=END,
            markeredgewidth=2.5,
            markersize=9,
            label=f"t = {inst.t}",
        ),
    ]
    if path:
        legend.append(Line2D([], [], color=PATH, lw=3, label="path"))
    if bad_steps:
        legend.append(
            Line2D([], [], color=RED, lw=2, ls="--", label=f"not an edge ({len(bad_steps)})")
        )
    ax.legend(
        handles=legend,
        loc="upper center",
        bbox_to_anchor=(0.5, 0.0),
        ncol=min(len(legend), 3),
        fontsize=8,
        frameon=False,
    )
    ax.set_axis_off()

    if created:
        _finish(ax.figure, inst.name, save=save, show=show)
    elif save is not None:
        _save(ax.figure, save)
    return ax


def draw_many(
    items: Iterable[Any],
    *,
    max_plots: int = 12,
    cols: int = 3,
    max_nodes: int | None = 300,
    save: str | os.PathLike[str] | None = None,
    show: bool = True,
    **draw_options: Any,
) -> Any:
    """Draw several instances side by side, e.g. ``draw_many(results.failed)``.

    Args:
        items: instances, instance names, or the results of :func:`run_experiment`.
        max_plots: draw at most this many (the rest are listed instead).
        cols: pictures per row.
        max_nodes: instances with more vertices get a short note instead of a drawing.
        save, show: as in :func:`draw`.
        **draw_options: passed on to :func:`draw` (e.g. ``layout="circular"``).

    Returns:
        The matplotlib ``Figure``, or ``None`` if there was nothing to draw.
    """
    import matplotlib.pyplot as plt

    from .experiment import Results, RunResult

    if isinstance(items, (Instance, RunResult, str, os.PathLike)):
        items = [items]
    if isinstance(items, Results):
        runs = {r.instance: r for r in items}
        items = items.instances()
    else:
        items = list(items)
        runs = {r.instance: r for r in items if isinstance(r, RunResult)}
    items = list(items)
    if not items:
        print("Nothing to draw.")
        return None
    if max_plots < 1:
        raise ValueError(f"max_plots must be at least 1, got {max_plots!r}.")
    if len(items) > max_plots:
        rest = [
            getattr(i, "name", None) or getattr(i, "instance", None) or str(i)
            for i in items[max_plots:]
        ]
        shown = ", ".join(rest[:10]) + (f" and {len(rest) - 10} more" if len(rest) > 10 else "")
        print(f"Drawing the first {max_plots} of {len(items)}; not drawn: {shown}")
        items = items[:max_plots]

    cols = max(1, min(cols, len(items)))
    rows = math.ceil(len(items) / cols)
    fig, axes = plt.subplots(rows, cols, figsize=(5 * cols, 4.6 * rows), squeeze=False)
    for ax, item in zip(axes.flat, items, strict=False):
        inst = _as_instance(item)
        run = runs.get(inst.name)
        label = inst.name
        if run is not None:
            label += (
                f"  [{run.status}" + (f": {run.answer}" if run.answer is not None else "") + "]"
            )
        if max_nodes is not None and inst.n > max_nodes:
            ax.text(
                0.5,
                0.5,
                f"{label}\nn={inst.n} is too big to draw here.\n"
                f"Try draw({inst.name!r}, around={inst.s!r})",
                ha="center",
                va="center",
                fontsize=10,
                transform=ax.transAxes,
            )
            ax.set_axis_off()
            continue
        draw(
            inst,
            ax=ax,
            title=f"{label}\nn={inst.n}, m={inst.m}, r={inst.r}",
            max_nodes=None,
            **draw_options,
        )
    for ax in list(axes.flat)[len(items) :]:
        ax.set_axis_off()
    fig.tight_layout()
    _finish(fig, "draw_many", save=save, show=show)
    return fig


# --------------------------------------------------------------------------- showing / saving


def _save(fig: Any, target: str | os.PathLike[str]) -> Path:
    path = Path(target)
    if not path.suffix:
        path = path.with_suffix(".png")
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=150, bbox_inches="tight")
    return path


def _has_screen() -> bool:
    import matplotlib

    backend = matplotlib.get_backend().lower()
    return backend not in ("agg", "pdf", "ps", "svg", "cairo", "pgf", "template")


def _finish(fig: Any, name: str, *, save: str | os.PathLike[str] | None, show: bool) -> None:
    import matplotlib.pyplot as plt

    if save is not None:
        print(f"Saved drawing to {_save(fig, save)}")
    if not show:
        return
    if _has_screen():
        plt.show()
    elif save is None:
        target = repo_root() / "figures" / f"{name}.png"
        print(f"No screen available, so the drawing was saved to {_save(fig, target)}")
        plt.close(fig)
