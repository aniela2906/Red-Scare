"""Draw the figures for the Some section of the report.

uv run python report/figures/make_some_figures.py

Writes one SVG (used by some.typ) and one PNG (for previews) per figure next to this script. The graphs are small hand-made examples,
so every position is fixed by hand to keep the pictures readable.
"""

from __future__ import annotations

import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyArrowPatch, FancyBboxPatch

OUT = Path(__file__).resolve().parent

RED = "#c8281e"
NODE = "#e6e9ef"
EDGE = "#8a93a3"
INK = "#18202c"
S_COLOR = "#1f6fd1"  # route / unit from s
T_COLOR = "#d98200"  # route / unit from t
BAD = "#b3261e"
GOOD = "#1d7a45"
RADIUS = 0.3
PAIR_OFFSET = 0.13

plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 11, "svg.fonttype": "path"})


# ----------------------------------------------------------------------------- helpers


def _unit(p, q):
    dx, dy = q[0] - p[0], q[1] - p[1]
    length = math.hypot(dx, dy) or 1.0
    return dx / length, dy / length


def _segment(pos, a, b, offset=0.0, cut_a=RADIUS, cut_b=RADIUS):
    p, q = pos[a], pos[b]
    ux, uy = _unit(p, q)
    nx_, ny_ = -uy, ux
    start = (p[0] + ux * cut_a + nx_ * offset, p[1] + uy * cut_a + ny_ * offset)
    end = (q[0] - ux * cut_b + nx_ * offset, q[1] - uy * cut_b + ny_ * offset)
    return start, end


def _cut(node, aux):
    return RADIUS + 0.06 if node in aux else RADIUS


def draw(
    ax,
    pos,
    edges,
    *,
    red=(),
    directed=False,
    aux=(),
    aux_edges=(),
    routes=(),
    warn=(),
    tags=None,
    edge_labels=None,
    title=None,
    verdict=None,
):
    """Draw a small graph.

    routes: list of (sequence of nodes, color, style) with style "solid" or "undo".
    aux:    helper nodes (drawn as dashed squares), aux_edges: dashed arrows.
    warn:   nodes circled with a dashed red ring (a vertex used twice, a dead end, ...).
    """
    ax.set_aspect("equal")
    ax.axis("off")
    tags = tags or {}
    edge_labels = edge_labels or {}

    covered = {(seq[k], seq[k + 1]) for seq, *_ in routes for k in range(len(seq) - 1)}
    edge_set = set(edges)
    for u, v in edges:
        # A pair of opposite arcs (u -> v and v -> u) is drawn side by side.
        offset = PAIR_OFFSET if directed and (v, u) in edge_set else 0.0
        start, end = _segment(pos, u, v, offset, cut_a=_cut(u, aux), cut_b=_cut(v, aux))
        # Where a route runs along an arc, the route's own arrow shows the direction.
        arrow = directed and (u, v) not in covered
        ax.add_patch(
            FancyArrowPatch(
                start,
                end,
                arrowstyle="-|>,head_length=7,head_width=4" if arrow else "-",
                color=EDGE,
                lw=1.6,
                shrinkA=0,
                shrinkB=0,
                zorder=1,
            )
        )
    for u, v in aux_edges:
        start, end = _segment(pos, u, v, cut_a=_cut(u, aux), cut_b=_cut(v, aux))
        ax.add_patch(
            FancyArrowPatch(
                start,
                end,
                arrowstyle="-|>,head_length=7,head_width=4",
                color=EDGE,
                lw=1.6,
                linestyle=(0, (4, 3)),
                shrinkA=0,
                shrinkB=0,
                zorder=1,
            )
        )
    for (u, v), text in edge_labels.items():
        (x1, y1), (x2, y2) = pos[u], pos[v]
        ux, uy = _unit(pos[u], pos[v])
        ax.text(
            (x1 + x2) / 2 - uy * 0.22,
            (y1 + y2) / 2 + ux * 0.22,
            text,
            ha="center",
            va="center",
            fontsize=9,
            color=INK,
            bbox={"boxstyle": "round,pad=0.12", "fc": "white", "ec": "none"},
            zorder=4,
        )

    for seq, color, style in routes:
        for k in range(len(seq) - 1):
            a, b = seq[k], seq[k + 1]
            if directed and (b, a) in edge_set:
                offset = PAIR_OFFSET
            else:
                offset = {S_COLOR: -0.07, T_COLOR: 0.07}.get(color, 0.16)
            last = k == len(seq) - 2
            start, end = _segment(
                pos, a, b, offset, cut_a=_cut(a, aux) + 0.03, cut_b=_cut(b, aux) + 0.06
            )
            ax.add_patch(
                FancyArrowPatch(
                    start,
                    end,
                    arrowstyle="-|>,head_length=8,head_width=4.5"
                    if (last or directed or style == "undo")
                    else "-",
                    color=BAD if style == "undo" else color,
                    lw=2.4 if style == "undo" else 3.6,
                    linestyle=(0, (4, 2.5)) if style == "undo" else "-",
                    shrinkA=0,
                    shrinkB=0,
                    capstyle="round",
                    zorder=2,
                )
            )

    for name, (x, y) in pos.items():
        if name in aux:
            ax.add_patch(
                FancyBboxPatch(
                    (x - 0.3, y - 0.24),
                    0.6,
                    0.48,
                    boxstyle="round,pad=0.02,rounding_size=0.08",
                    fc="white",
                    ec=INK,
                    lw=1.3,
                    linestyle=(0, (3, 2)),
                    zorder=3,
                )
            )
            color = INK
        else:
            is_red = name in red
            ax.add_patch(
                Circle(
                    (x, y),
                    RADIUS,
                    fc=RED if is_red else NODE,
                    ec=RED if is_red else EDGE,
                    lw=1.4,
                    zorder=3,
                )
            )
            color = "white" if is_red else INK
        ax.text(x, y, _label(name), ha="center", va="center", color=color, zorder=5,
                fontsize=11, fontweight="bold")
        if name in warn:
            ax.add_patch(
                Circle((x, y), RADIUS + 0.13, fc="none", ec=BAD, lw=2, linestyle=(0, (3, 2)), zorder=4)
            )
        if name in tags:
            text, where = tags[name]
            dy = {"above": 0.55, "below": -0.55}[where]
            ax.text(x, y + dy, text, ha="center", va="center", fontsize=9.5, color="#5b6575",
                    style="italic", zorder=5)

    xs = [p[0] for p in pos.values()]
    ys = [p[1] for p in pos.values()]
    ax.set_xlim(min(xs) - 0.75, max(xs) + 0.75)
    ax.set_ylim(min(ys) - 0.75, max(ys) + 0.75)
    if title:
        ax.set_title(title, fontsize=11.5, color=INK, pad=6)
    if verdict:
        text, ok = verdict
        ax.text(0.5, -0.02, text, transform=ax.transAxes, ha="center", va="top", fontsize=10.5,
                color=GOOD if ok else BAD, fontweight="bold")


def _label(name):
    subs = {"1": "₁", "2": "₂"}
    if len(name) == 2 and name[0] in "st" and name[1] in subs:
        return name[0] + subs[name[1]]
    return name


def save(fig, name):
    fig.savefig(OUT / f"{name}.svg", bbox_inches="tight", pad_inches=0.05)
    fig.savefig(OUT / f"{name}.png", bbox_inches="tight", pad_inches=0.05, dpi=160)
    plt.close(fig)
    print(f"wrote {name}.svg / .png")


# --------------------------------------------------------------------------- examples

# The running example: the two quick searches overlap on a and b,
# but a real path exists: s, c, e, d, r, b, a, t.
EX_POS = {
    "s": (0, 0),
    "a": (2, 0),
    "t": (4, 0),
    "b": (2, 1.25),
    "r": (2, 2.5),
    "c": (0, 1.25),
    "e": (0, 2.5),
    "d": (1, 3.2),
}
EX_EDGES = [("s", "a"), ("a", "t"), ("a", "b"), ("b", "r"), ("s", "c"), ("c", "e"), ("e", "d"), ("d", "r")]
EX_TAGS = {"s": ("start", "below"), "t": ("end", "below")}


def fig_yes_no():
    fig, (left, right) = plt.subplots(1, 2, figsize=(9, 2.9))
    pos = {"s": (0, 0), "a": (1.4, 1), "r": (2.8, 1), "c": (4.2, 0), "b": (2.1, -0.6), "t": (5.6, 0)}
    draw(
        left,
        pos,
        [("s", "a"), ("a", "r"), ("r", "c"), ("c", "t"), ("s", "b"), ("b", "c")],
        red={"r"},
        routes=[(["s", "a", "r", "c", "t"], S_COLOR, "solid")],
        title="A path through red exists",
        verdict=("answer: true", True),
    )
    pos = {"s": (0, 0), "a": (1.4, 0), "b": (2.8, 0), "t": (4.2, 0), "r": (2.8, 1.3), "q": (1.4, 1.3)}
    draw(
        right,
        pos,
        [("s", "a"), ("a", "b"), ("b", "t"), ("b", "r"), ("a", "q")],
        red={"r", "q"},
        warn={"r", "q"},
        title="Every red vertex is a dead end",
        verdict=("answer: false", False),
    )
    save(fig, "some-yes-no")


def fig_bfs_overlap():
    fig, (left, right) = plt.subplots(1, 2, figsize=(8.5, 3.9))
    draw(
        left,
        EX_POS,
        EX_EDGES,
        red={"r"},
        tags=EX_TAGS,
        routes=[(["r", "b", "a", "s"], S_COLOR, "solid"), (["r", "b", "a", "t"], T_COLOR, "solid")],
        warn={"a", "b"},
        title="Two BFS from r: both use a and b",
        verdict=("overlap: not a path", False),
    )
    draw(
        right,
        EX_POS,
        EX_EDGES,
        red={"r"},
        tags=EX_TAGS,
        routes=[(["s", "c", "e", "d", "r", "b", "a", "t"], S_COLOR, "solid")],
        title="But a path through r exists",
        verdict=("s, c, e, d, r, b, a, t", True),
    )
    save(fig, "some-bfs-overlap")


def fig_network():
    fig, (left, right) = plt.subplots(1, 2, figsize=(8.5, 4.3))
    draw(left, EX_POS, EX_EDGES, red={"r"}, tags=EX_TAGS, title="The graph")
    pos = dict(EX_POS, X=(2, -1.4))
    draw(
        right,
        pos,
        EX_EDGES,
        red={"r"},
        aux={"X"},
        aux_edges=[("X", "s"), ("X", "t")],
        edge_labels={("X", "s"): "1", ("X", "t"): "1"},
        tags={"r": ("sink", "above"), "X": ("source", "below")},
        title="Add super source X, red r is the sink",
    )
    save(fig, "some-network")


def fig_split():
    fig, ax = plt.subplots(figsize=(7.5, 2.3))
    pos = {"u_in": (0, 0), "u_out": (1.6, 0), "v_in": (3.6, 0), "v_out": (5.2, 0)}
    ax.set_aspect("equal")
    ax.axis("off")
    for name, (x, y) in pos.items():
        ax.add_patch(
            FancyBboxPatch((x - 0.45, y - 0.26), 0.9, 0.52, boxstyle="round,pad=0.02,rounding_size=0.25",
                           fc=NODE, ec=EDGE, lw=1.4, zorder=3)
        )
        ax.text(x, y, name.replace("_", "$_{") + "}$", ha="center", va="center", fontsize=11, zorder=4)

    def arc(a, b, rad, label, color=EDGE, lw=1.6, ly=0.0):
        (x1, y1), (x2, y2) = pos[a], pos[b]
        ax.add_patch(
            FancyArrowPatch((x1 + (0.45 if x2 > x1 else -0.45), y1), (x2 - (0.45 if x2 > x1 else -0.45), y2),
                            connectionstyle=f"arc3,rad={rad}", arrowstyle="-|>,head_length=7,head_width=4",
                            color=color, lw=lw, zorder=2)
        )
        ax.text((x1 + x2) / 2, ly, label, ha="center", va="center", fontsize=9, color=INK,
                bbox={"boxstyle": "round,pad=0.12", "fc": "white", "ec": "none"}, zorder=5)

    arc("u_in", "u_out", 0, "1", color=S_COLOR, lw=2.6, ly=0.33)
    arc("v_in", "v_out", 0, "1", color=S_COLOR, lw=2.6, ly=0.33)
    arc("u_out", "v_in", -0.35, "1", ly=0.42)
    arc("v_out", "u_in", -0.28, "1", ly=-0.62)
    ax.text(0.8, 0.8, "vertex u", ha="center", fontsize=9.5, color="#5b6575", style="italic")
    ax.text(4.4, 0.8, "vertex v", ha="center", fontsize=9.5, color="#5b6575", style="italic")
    ax.set_xlim(-0.7, 5.9)
    ax.set_ylim(-0.95, 1.1)
    ax.set_title("Undirected edge u–v after splitting: every vertex lets 1 unit through", fontsize=11, pad=4)
    save(fig, "some-split")


def fig_rounds():
    fig, axes = plt.subplots(1, 3, figsize=(12, 4.4))
    pos = dict(EX_POS, X=(2, -1.4))
    common = dict(red={"r"}, aux={"X"}, aux_edges=[("X", "s"), ("X", "t")])
    draw(
        axes[0],
        pos,
        EX_EDGES,
        **common,
        routes=[(["X", "s", "a", "b", "r"], S_COLOR, "solid")],
        title="Round 1: BFS from X",
        verdict=("flow = 1", True),
    )
    draw(
        axes[1],
        pos,
        EX_EDGES,
        **common,
        routes=[
            (["X", "s", "a", "b", "r"], S_COLOR, "solid"),
            (["X", "t", "a"], T_COLOR, "solid"),
            (["a", "s"], BAD, "undo"),
            (["s", "c", "e", "d", "r"], T_COLOR, "solid"),
        ],
        warn={"a"},
        title="Round 2: BFS in the residual graph",
        verdict=("a is full: undo s→a, flow = 2", True),
    )
    draw(
        axes[2],
        pos,
        EX_EDGES,
        **common,
        routes=[(["X", "s", "c", "e", "d", "r"], S_COLOR, "solid"), (["X", "t", "a", "b", "r"], T_COLOR, "solid")],
        title="Result: two routes meeting only at r",
        verdict=("path s, c, e, d, r, b, a, t", True),
    )
    save(fig, "some-rounds")


def fig_directed():
    fig, ax = plt.subplots(figsize=(5.5, 2.9))
    pos = {"s": (0, 0), "r": (2, 0), "t": (4, 0), "X": (2, -1.4)}
    draw(
        ax,
        pos,
        [("s", "r"), ("r", "t")],
        red={"r"},
        directed=True,
        aux={"X"},
        aux_edges=[("X", "s"), ("X", "t")],
        routes=[(["X", "s", "r"], S_COLOR, "solid")],
        warn={"t"},
        tags={"t": ("no arrow out", "above")},
        verdict=("flow = 1, but the path s, r, t exists", False),
    )
    save(fig, "some-directed")


def fig_cycle():
    fig, ax = plt.subplots(figsize=(5.5, 2.7))
    pos = {"s": (0, 0), "v": (2, 0), "t": (4, 0), "r": (2, 1.6)}
    draw(
        ax,
        pos,
        [("s", "v"), ("v", "t"), ("v", "r"), ("r", "v")],
        red={"r"},
        directed=True,
        routes=[(["s", "v", "r"], S_COLOR, "solid"), (["r", "v", "t"], T_COLOR, "solid")],
        warn={"v"},
        verdict=("s reaches r, r reaches t, but v is used twice", False),
    )
    save(fig, "some-cycle")


def fig_reduction():
    fig, ax = plt.subplots(figsize=(7, 3.7))
    pos = {"s1": (0, 1.5), "a": (1.8, 2.4), "m": (1.8, 0.6), "t1": (3.6, 1.5), "r": (5.4, 1.5),
           "s2": (5.4, -0.5), "t2": (0, -0.5)}
    draw(
        ax,
        pos,
        [("s1", "a"), ("a", "t1"), ("s1", "m"), ("m", "t1"), ("s2", "m"), ("m", "t2"), ("t1", "r"), ("r", "s2")],
        red={"r"},
        directed=True,
        routes=[(["s1", "a", "t1", "r"], S_COLOR, "solid"), (["r", "s2", "m", "t2"], T_COLOR, "solid")],
        tags={"s1": ("= s", "above"), "t2": ("= t", "below"), "r": ("new", "above")},
        verdict=("path through r  ⇔  disjoint s₁⇝t₁ and s₂⇝t₂", True),
    )
    save(fig, "some-reduction")


if __name__ == "__main__":
    fig_yes_no()
    fig_bfs_overlap()
    fig_network()
    fig_split()
    fig_rounds()
    fig_directed()
    fig_cycle()
    fig_reduction()
