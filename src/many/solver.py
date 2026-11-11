"""Problem Many.

Maximum number of red vertices on a simple s,t-path.

NP-hard in general (all vertices red => longest / Hamiltonian s,t-path).
Solved exactly in polynomial time for:
  (a) directed graphs whose s-t-relevant part is acyclic (DAG dynamic program)
  (b) undirected graphs where every biconnected component on the s-t route
      of the block-cut tree is a single edge or a simple cycle.
Everything else returns "?!".
"""

import networkx as nx

from runner import Instance


def solve(instance: Instance):
    G = instance.graph
    s, t = instance.s, instance.t
    red = set(instance.red)

    if s == t:
        return 1 if s in red else 0

    if G.is_directed():
        return _solve_directed(G, s, t, red)
    return _solve_undirected(G, s, t, red)


# ---------------------------------------------------------------- directed
def _solve_directed(G, s, t, red):
    reach = nx.descendants(G, s)
    if t not in reach:
        return -1

    relevant = (reach | {s}) & (nx.ancestors(G, t) | {t})
    H = G.subgraph(relevant)
    if not nx.is_directed_acyclic_graph(H):
        return "?!"

    NEG = float("-inf")
    best = {v: NEG for v in H}
    best[s] = 1 if s in red else 0
    for v in nx.topological_sort(H):
        if best[v] == NEG:
            continue
        for w in H.successors(v):
            cand = best[v] + (1 if w in red else 0)
            if cand > best[w]:
                best[w] = cand
    return int(best[t])


# -------------------------------------------------------------- undirected
def _solve_undirected(G, s, t, red):
    if not nx.has_path(G, s, t):
        return -1

    comp = nx.node_connected_component(G, s)
    C = G.subgraph(comp)

    blocks = [set(b) for b in nx.biconnected_components(C)]
    cuts = set(nx.articulation_points(C))

    T = nx.Graph()
    vertex_block = {}
    for i, b in enumerate(blocks):
        T.add_node(("b", i))
        for v in b:
            if v in cuts:
                T.add_edge(("b", i), ("v", v))
            else:
                vertex_block[v] = i

    def tnode(v):
        return ("v", v) if v in cuts else ("b", vertex_block[v])

    path = nx.shortest_path(T, tnode(s), tnode(t))

    total = 0
    for idx, node in enumerate(path):
        if node[0] == "v":
            if 0 < idx < len(path) - 1 and node[1] in red:
                total -= 1
            continue
        entry = s if idx == 0 else path[idx - 1][1]
        exit_ = t if idx == len(path) - 1 else path[idx + 1][1]
        val = _best_in_block(C.subgraph(blocks[node[1]]), entry, exit_, red)
        if val is None:
            return "?!"
        total += val
    return total


MAX_BLOCK = 16

def _best_by_dp(H, a, b, red):
    nodes = list(H.nodes())
    idx = {v: i for i, v in enumerate(nodes)}
    k = len(nodes)
    adj = [[idx[w] for w in H.neighbors(v)] for v in nodes]
    rd = [1 if v in red else 0 for v in nodes]
    A, B = idx[a], idx[b]

    dp = [[-1] * k for _ in range(1 << k)]
    dp[1 << A][A] = rd[A]
    best = -1
    for mask in range(1 << k):
        if not (mask >> A) & 1:
            continue
        row = dp[mask]
        for v in range(k):
            cur = row[v]
            if cur < 0:
                continue
            if v == B:
                best = max(best, cur)
                continue
            for w in adj[v]:
                if (mask >> w) & 1:
                    continue
                nm = mask | (1 << w)
                val = cur + rd[w]
                if val > dp[nm][w]:
                    dp[nm][w] = val
    return best if best >= 0 else None


def _best_in_block(H, a, b, red):
    k, e = H.number_of_nodes(), H.number_of_edges()

    def r(v):
        return 1 if v in red else 0

    if k == 2:
        return r(a) + r(b)

    if e == k:
        cyc = [a]
        prev, cur = None, a
        while True:
            nxt = [w for w in H.neighbors(cur) if w != prev][0]
            if nxt == a:
                break
            cyc.append(nxt)
            prev, cur = cur, nxt
        ib = cyc.index(b)
        arc1 = cyc[: ib + 1]
        arc2 = [a] + cyc[ib:][::-1]
        return max(sum(map(r, arc1)), sum(map(r, arc2)))

    if k <= MAX_BLOCK:
        return _best_by_dp(H, a, b, red)

    return None
    
