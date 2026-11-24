// Red Scare! Report: Typst version of report_all.docx in IEEE conference style.
// Text, numbers, tables and figures are taken unchanged from the Word report.
//
// Build (from the repo root):
//   typst compile --font-path report/fonts report/report.typ
// report/fonts holds TeX Gyre Termes/Cursor (free Times/Courier clones)
// that the IEEE template expects.

#import "@preview/charged-ieee:0.1.4": ieee

#show: ieee.with(
  title: [Red Scare! Report #v(4pt) #text(size: 11pt)[By:]],
  authors: (
    (name: "Aniela Marta Ciecierska", email: "anci@itu.dk"),
    (name: "Cristina Tuá Silvestre", email: "s25444@itu.dk"),
    (name: "Jakub Piotr Gasior", email: "jaga@itu.dk"),
    (name: "Javier Valldecabres Casas", email: "s25429@itu.dk"),
    (name: "Joao Pedro Monteiro Maia", email: "s25441@itu.dk"),
    (name: "Maja Rzeszotarska", email: "mrze@itu.dk"),
    (name: "Zofia Brodewicz", email: "zobr@itu.dk"),
  ),
  paper-size: "a4",
)

// Keep the text 1:1 with the Word report: no equation numbers, and
// third-level headings without the template's added "a)" and ":".
#set math.equation(numbering: none)
#show heading.where(level: 3): it => block(above: 8pt, below: 6pt, sticky: true,
  text(size: 10pt, style: "italic", it.body))

// Tables keep the Word report's own captions ("Table 1." ... ), so they are
// placed as plain tables with a caption line above, IEEE style.
#let tcaption(body) = block(above: 10pt, below: 4pt, width: 100%,
  align(center, text(size: 8pt, body)))
#let fcaption(body) = block(above: 4pt, below: 10pt, width: 100%,
  align(left, text(size: 8pt, body)))
#let rule-table(..args) = align(center, text(size: 8pt, table(
  stroke: none,
  inset: (x: 4pt, y: 2.2pt),
  ..args,
)))

#place(top + center, float: true, scope: "parent", clearance: 18pt,
  text(size: 9pt, link("https://github.com/aniela2906/Red-Scare.git")))

= Results:

We evaluated five problems - Alternate, Few, Many, None, and Some - on 154 graph instances. _Table 1_ summarizes the number of instances solved, total execution time, and theoretical running time of our algorithms.

#tcaption[*Table 1.* Summary of results across all 154 graph instances.]
#rule-table(
  columns: 5,
  align: (left, right, right, right, left),
  table.hline(stroke: 0.8pt),
  table.header[Problem][Solved][Unsolved][Total time (s)][General complexity],
  table.hline(stroke: 0.4pt),
  [Alternate], [154], [0], [0.17], [$(O(n+m))$],
  [Few], [154], [0], [1.27], [$(O((n+m) log n))$],
  [Many], [74], [80], [14.16], [Class-dependent],
  [None], [154], [0], [0.46], [$(O(n+m))$],
  [Some], [154], [0], [19.87], [Class-dependent],
  table.hline(stroke: 0.8pt),
)
#v(6pt)

The following table gives our results for all graph instances with at least 500 vertices. The columns represent Alternate (A), Few (F), Many (M), None (N), and Some (S). An entry of ? indicates that no solution was found within a reasonable time; ?! indicates computational hardness for the relevant graph class. The complete results for all instances are provided in the tab-separated file results.txt.

#tcaption[*Table 2.* Results for graph instances with at least 500 vertices.]
#rule-table(
  columns: 7,
  align: (left, right, center, right, right, right, center),
  table.hline(stroke: 0.8pt),
  table.header[Instance name][n][A][F][M][N][S],
  table.hline(stroke: 0.4pt),
  [bht], [5757], [false], [0], [?!], [6], [true],
  [common-1-1000], [1000], [false], [-1], [-1], [-1], [false],
  [common-1-1500], [1500], [false], [-1], [-1], [-1], [false],
  [common-1-2000], [2000], [false], [-1], [-1], [-1], [false],
  [common-1-2500], [2500], [false], [1], [?!], [6], [true],
  [common-1-3000], [3000], [false], [1], [?!], [6], [true],
  [common-1-3500], [3500], [false], [1], [?!], [6], [true],
  [common-1-4000], [4000], [false], [1], [?!], [6], [true],
  [common-1-4500], [4500], [true], [1], [?!], [6], [true],
  [common-1-500], [500], [false], [-1], [-1], [-1], [false],
  [common-1-5000], [5000], [true], [1], [?!], [6], [true],
  [common-1-5757], [5757], [true], [1], [?!], [6], [true],
  [common-2-1000], [1000], [true], [1], [?!], [4], [true],
  [common-2-1500], [1500], [true], [1], [?!], [4], [true],
  [common-2-2000], [2000], [true], [1], [?!], [4], [true],
  [common-2-2500], [2500], [true], [1], [?!], [4], [true],
  [common-2-3000], [3000], [true], [1], [?!], [4], [true],
  [common-2-3500], [3500], [true], [1], [?!], [4], [true],
  [common-2-4000], [4000], [true], [1], [?!], [4], [true],
  [common-2-4500], [4500], [true], [1], [?!], [4], [true],
  [common-2-500], [500], [true], [1], [?!], [4], [true],
  [common-2-5000], [5000], [true], [1], [?!], [4], [true],
  [common-2-5757], [5757], [true], [1], [?!], [4], [true],
  [gnm-1000-1500-0], [1000], [false], [1], [?!], [-1], [true],
  [gnm-1000-1500-1], [1000], [false], [2], [?!], [-1], [true],
  [gnm-1000-2000-0], [1000], [false], [0], [?!], [7], [true],
  [gnm-1000-2000-1], [1000], [false], [2], [?!], [-1], [true],
  [gnm-2000-3000-0], [2000], [false], [0], [?!], [8], [true],
  [gnm-2000-3000-1], [2000], [true], [2], [?!], [-1], [true],
  [gnm-2000-4000-0], [2000], [false], [0], [?!], [6], [true],
  [gnm-2000-4000-1], [2000], [false], [0], [?!], [5], [true],
  [gnm-3000-4500-0], [3000], [false], [0], [?!], [10], [true],
  [gnm-3000-4500-1], [3000], [false], [2], [?!], [-1], [true],
  [gnm-3000-6000-0], [3000], [false], [0], [?!], [6], [true],
  [gnm-3000-6000-1], [3000], [false], [2], [?!], [6], [true],
  [gnm-4000-6000-0], [4000], [false], [0], [?!], [7], [true],
  [gnm-4000-6000-1], [4000], [false], [1], [?!], [15], [true],
  [gnm-4000-8000-0], [4000], [false], [0], [?!], [5], [true],
  [gnm-4000-8000-1], [4000], [true], [2], [?!], [6], [true],
  [gnm-5000-10000-0], [5000], [false], [2], [?!], [5], [true],
  [gnm-5000-10000-1], [5000], [true], [1], [?!], [5], [true],
  [gnm-5000-7500-0], [5000], [false], [-1], [-1], [-1], [false],
  [gnm-5000-7500-1], [5000], [false], [-1], [-1], [-1], [false],
  [grid-25-0], [625], [true], [0], [?!], [324], [true],
  [grid-25-1], [625], [true], [0], [?!], [123], [true],
  [grid-25-2], [625], [true], [5], [?!], [-1], [true],
  [grid-50-0], [2500], [false], [0], [?!], [1249], [true],
  [grid-50-1], [2500], [false], [0], [?!], [521], [true],
  [grid-50-2], [2500], [false], [11], [?!], [-1], [true],
  [increase-n500-1], [500], [true], [2], [16], [1], [true],
  [increase-n500-2], [500], [true], [1], [17], [1], [true],
  [increase-n500-3], [500], [true], [1], [16], [1], [true],
  [rusty-1-2000], [2000], [false], [-1], [-1], [-1], [false],
  [rusty-1-2500], [2500], [false], [-1], [-1], [-1], [false],
  [rusty-1-3000], [3000], [false], [0], [?!], [14], [true],
  [rusty-1-3500], [3500], [false], [0], [?!], [14], [true],
  [rusty-1-4000], [4000], [false], [0], [?!], [13], [true],
  [rusty-1-4500], [4500], [false], [0], [?!], [7], [true],
  [rusty-1-5000], [5000], [false], [0], [?!], [7], [true],
  [rusty-1-5757], [5757], [false], [0], [?!], [7], [true],
  [rusty-2-2000], [2000], [false], [0], [?!], [5], [true],
  [rusty-2-2500], [2500], [false], [0], [?!], [4], [true],
  [rusty-2-3000], [3000], [false], [0], [?!], [4], [true],
  [rusty-2-3500], [3500], [false], [0], [?!], [4], [true],
  [rusty-2-4000], [4000], [false], [0], [?!], [4], [true],
  [rusty-2-4500], [4500], [false], [0], [?!], [4], [true],
  [rusty-2-5000], [5000], [false], [0], [?!], [4], [true],
  [rusty-2-5757], [5757], [false], [0], [?!], [4], [true],
  [smallworld-30-0], [900], [false], [0], [?!], [9], [true],
  [smallworld-30-1], [900], [true], [1], [?!], [11], [true],
  [smallworld-40-0], [1600], [false], [0], [?!], [8], [true],
  [smallworld-40-1], [1600], [true], [1], [?!], [13], [true],
  [smallworld-50-0], [2500], [false], [0], [?!], [3], [true],
  [smallworld-50-1], [2500], [true], [2], [?!], [-1], [true],
  [wall-n-100], [800], [false], [0], [0], [1], [false],
  [wall-n-1000], [8000], [false], [0], [0], [1], [false],
  [wall-n-10000], [80000], [false], [0], [0], [1], [false],
  [wall-p-100], [602], [false], [0], [?!], [1], [true],
  [wall-p-1000], [6002], [false], [0], [?!], [1], [true],
  [wall-p-10000], [60002], [false], [0], [?!], [1], [true],
  [wall-z-100], [701], [false], [0], [0], [1], [false],
  [wall-z-1000], [7001], [false], [0], [0], [1], [false],
  [wall-z-10000], [70001], [false], [0], [0], [1], [false],
  table.hline(stroke: 0.8pt),
)
#v(6pt)

= Methods

== None

=== Algorithm

The _None_ problem asks whether there is a path from _s_ to _t_ that does not go through any least red vertex.

To solve this problem, we remove all red vertices (_R_) from the graph ($G = (V, E)$), except the source (_s_) and target (_t_), since these may be red. We then apply _Breadth-First Search (BFS)_ using _NetworkX_'s _shortest\_path\_length()_ \[1\] to find the shortest valid (_s_)-(_t_) path. Removing the forbidden vertices preserves exactly the valid paths, and _BFS_ guarantees the shortest path in an unweighted graph. If no path exists, we return (_-1_).

=== Correctness and running time

Removing the forbidden internal vertices preserved exactly the admissible s-t paths. BFS finds the shortest path in an unweighted graph. Both vertex filtering and BFS take $O(n + m)$ (where $n = |V|$ and $m = |E|$), for both directed and undirected graphs.

=== Results

Our implementation successfully processed all 154 instances, with a total solver time of 0.46 seconds. The slowest instance was common-2-5757, taking 0.08 seconds.

== Some

=== Algorithm

The _Some_ problem asks whether there is a path from _s_ to _t_ that goes through at least one red vertex. The important word is _path_: no vertex can be visited twice. Without that rule two BFS runs would be enough, and this rule is what makes the problem interesting.

=== A first idea: BFS

Our first idea was to pick a red vertex _r_, run a BFS from _r_ to _s_ and another from _r_ to _t_, and glue the two routes together. This breaks when both routes need the same vertex (_Figure 1_): the result visits _a_ twice, so it is not a path, even though a valid path exists if we go the long way around. We tested this on our data: the two-BFS idea gets 18 instances wrong (all _wall-p_ and most _rusty-1_ graphs), and the even simpler check “_s_ reaches a red vertex that reaches _t_” gets 14 wrong (the _wall-n_ and _wall-z_ graphs). What we really need are two routes from _r_, one to _s_ and one to _t_, that share no vertex.

#block(above: 10pt, below: 0pt, image("figures/some-bfs-overlap.svg", width: 100%))
#fcaption[*Figure 1.* Two shortest routes from r overlap in a and b, but a path through r exists.]

=== Turning it into a network flow problem

Two routes that share no vertex is exactly what a flow of value 2 gives us (Menger's theorem \[2, Ch. 7\]). We build the network like this:

- *Vertex splitting:* every vertex _v_ becomes an arc _v_#sub[in] → _v_#sub[out] with capacity 1, so at most one unit of flow can pass through _v_. This is what stops the two routes from sharing a vertex.
- Every undirected edge _uv_ becomes two arcs, _u_#sub[out] → _v_#sub[in] and _v_#sub[out] → _u_#sub[in].
- *Super source* _X_ with arcs _X_ → _s_#sub[in] and _X_ → _t_#sub[in], capacity 1 each. The sink is _r_#sub[in]. So the flow is at most 2: one unit has to start at _s_, the other at _t_, and both must end at _r_.

=== Running Ford–Fulkerson

We run Ford–Fulkerson with BFS \[2, Ch. 7\]. Each round finds one route from _X_ to _r_ in the residual graph and pushes one unit along it. The residual graph also has backward arcs, which let a later round undo a choice made by an earlier round. Figure 2 shows why we need this. In round 1 the BFS takes _s_ → _a_ → _b_ → _r_ and uses up _a_. In round 2, _t_ can only get in through _a_, so the BFS follows the backward arc _a_ → _s_, which undoes that step and sends _s_ around through _c_, _e_, _d_ instead.

#place(top, float: true, scope: "parent", clearance: 14pt, {
  image("figures/some-rounds.svg", width: 100%)
  fcaption[*Figure 2.* The two rounds of Ford–Fulkerson. In round 2 the backward arc undoes s → a.]
})

We stop after at most two rounds. If the flow is 2, we read the path from the arcs that carry flow: the route from _s_ to _r_, then the route from _t_ reversed. If the flow stays at 1, there is a single bottleneck vertex that both routes need (max-flow min-cut), so no path goes through this _r_ and we try the next red vertex in the component of _s_. Two shortcuts come first: if _s_ and _t_ are not connected the answer is false, and if _s_ or _t_ is red, any _s,t_-path works. The pseudocode below shows the whole algorithm.

#place(bottom, float: true, scope: "parent", clearance: 14pt, block(
  width: 100%, inset: (x: 14pt, y: 8pt), stroke: (y: 0.6pt),
  text(size: 8pt, ```
SOME(G, s, t, R):
  if G is directed then
    if G has a cycle then return ?!        # NP-hard in general
    A = vertices reachable from s          # BFS
    B = vertices that can reach t          # BFS on reversed edges
    return (A ∩ B ∩ R is not empty)
  if t is not reachable from s then return false
  if s in R or t in R then return true
  build network N:
    each vertex v      ->  arc v_in -> v_out, capacity 1
    each edge {u, v}   ->  arcs u_out -> v_in and v_out -> u_in
    super source X     ->  arcs X -> s_in and X -> t_in, capacity 1
  for each red r in the component of s:
    flow = 0
    repeat 2 times:
      P = BFS from X to r_in in the residual graph
      if no P then break
      push 1 unit along P          # backward arcs undo old flow
      flow = flow + 1
    if flow = 2 then return true   # path = s-route + reversed t-route
    reset N
  return false
```),
))

=== Directed graphs

The same idea does not work for directed graphs. Directed _Some_ is NP-hard: given a directed graph and two pairs (_s_#sub[1], _t_#sub[1]) and (_s_#sub[2], _t_#sub[2]), add a red vertex _r_ with arcs _t_#sub[1] → _r_ → _s_#sub[2]. A path from _s_#sub[1] to _t_#sub[2] through _r_ exists exactly when the two pairs can be joined by two disjoint paths, which is the NP-complete _Two disjoint paths_ problem \[6\]. So for directed graphs with cycles our code answers ?!.

Directed graphs _without_ cycles are easy, though. We find the vertices reachable from _s_ and the vertices that can reach _t_ with two BFS runs, and the answer is true if some red vertex is in both. The two routes can never meet at a vertex _v_, because then _v_ → … → _r_ → … → _v_ would be a cycle. All 31 directed graphs in our data have no cycles, so we never had to answer ?!.

=== Correctness and running time

Every BFS takes $O(n+m)$. Undirected graphs need at most two BFS runs per red vertex, so the total is $O(r(n+m))$, where _r_ is the number of red vertices. Directed graphs without cycles take $O(n+m)$.

=== Results

We solved all 154 instances: 115 true, 39 false, and no ?!, with a total solver time of 19.9 seconds. The slowest instance was _wall-n-10000_ (2.9 s), where every red vertex has to be tried and fails. We also checked the solver against brute force (trying every simple path) on 6000 small random graphs, and every answer matched.

#tcaption[*Table 3.* Results for Some by graph type.]
#rule-table(
  columns: 6,
  align: (left, right, right, right, right, right),
  table.hline(stroke: 0.8pt),
  table.header[*Graphs*][*Instances*][*true*][*false*][*?!*][*Time (s)*],
  table.hline(stroke: 0.4pt),
  [Undirected], [123], [93], [30], [0], [19.45],
  [Directed, no cycles], [31], [22], [9], [0], [0.42],
  [Directed with cycles], [0], [–], [–], [–], [–],
  table.hline(stroke: 0.4pt),
  [*Total*], [*154*], [*115*], [*39*], [*0*], [*19.87*],
  table.hline(stroke: 0.8pt),
)
#v(6pt)

== Many

=== Algorithm

_Many_ problem asks for the maximum number of red vertices on a simple s-t path, meaning a path that never repeats a vertex. If s = t, the answer is 1 if s is red and 0 otherwise. The problem is NP-hard, so no polynomial algorithm for all graphs is expected. We therefore solve exactly two well-defined graph classes in polynomial time:

+ directed graphs whose part relevant to s,t-paths contains no cycle.
+ undirected graphs in which every block (defined below) on the s,t-path is a single edge, a simple cycle, or has at most 16 vertices.

If there is no s,t-path at all, the answer is -1. We used NetworkX \[1\] for the implementation.

=== Directed graphs

Step 1: we find the vertices reachable from s and the vertices that can reach t, using breadth-first search \[2\]. Only those vertices are kept as the rest of the vertices do not influence the answer.

Step 2: on the remaining subgraph we test whether it is acyclic, i.e., a directed acyclic graph (DAG), and compute a topological order \[2\], which lists the vertices so that every edge points from an earlier to a later vertex. In a DAG every walk is automatically a simple path because following edges can never lead back to a vertex already visited.

Step 3: for every vertex v we store best(v), the largest number of red vertices on any path from s to v found so far. Initially best(s) is 1 if s is red and 0 otherwise, and all other vertices are marked “unreachable”. We then go through the vertices in topological order. When we are at u, best(u) is already final, because every path into u comes from an earlier vertex. For each edge from u to v we ask whether going through u is an improvement. Reaching v via u gives best(u) plus 1 if v is red (and plus 0 otherwise), and we keep this value if it beats what v had before. The answer is best(t). This is the standard dynamic-programming idea for DAGs \[2\].

If the subgraph had a cycle containing red vertices, an algorithm would have to remember which vertices were already used, and the number of possible sets of used vertices grows exponentially. For this hard case we return ?!.

=== Undirected graphs

Step 1: we compute the connected component of s. If t is not in it, no s,t-path exists and we return -1. Otherwise we continue with the component of s only, since the rest of the graph cannot lie on an s,t-path.

Step 2: we split the component into blocks. A block is a maximal part of the graph that stays connected when any single vertex is removed. Every edge lies in exactly one block, and two blocks share at most one vertex, which is always a cut vertex (a vertex whose removal disconnects the components). An edge whose removal disconnects the graph forms a block by itself. We find all blocks and cut vertices with one depth-first search, using the algorithm of Tarjan \[3\] and Hopcroft and Tarjan \[4\].

Step 3: we represent every block and every cut vertex as one node. We then join a cut vertex to each block that contains it. The result is a tree, because a cycle in it would mean that several blocks could be merged into one larger block. The tree represents how the blocks are connected to one another.

Step 4: in a tree there is exactly one path between two nodes, which we find with a breadth-first search from the node containing s to the node containing t. This tells us which blocks any simple s,t-path must use. To get from one block to the next, the path must go through the cut vertex between them. A simple path cannot enter a side branch of the tree and return, since returning would pass the same cut vertex a second time. Blocks that are not on the route are therefore never used.

Step 5: the path enters each block at the cut vertex towards the previous block (or at s for the first block) and leaves it at the cut vertex towards the next block (or at t for the last block). Because these vertices are fixed, each block becomes an independent subproblem of finding the simple path from the entry vertex to the exit vertex inside the block with the most red vertices. The method depends on what the block looks like:

- Single edge. There is only one route, entry to exit, so the value is the number of red vertices among the two endpoints.
- Cycle. Between two vertices on a cycle there are exactly two simple paths, one in each direction. We count the red vertices on each (including entry and exit) and take the larger. Going all the way around is not allowed, since it would revisit the entry vertex.
- Small block (at most 16 vertices). We use a subset dynamic program in the style of Held and Karp \[5\]. It builds paths from the entry vertex one step at a time. For every set S of vertices already used, and every vertex v where the path currently ends, it stores dp\[S\]\[v\], the largest number of red vertices on any simple path that starts at the entry vertex, uses exactly the vertices of S, and ends at v. A path is extended from v to a neighbour w only if w is not in S, so no vertex is ever repeated. The value of the block is the largest dp\[S\]\[b\] over all S, where b is the exit vertex. This tries all possibilities in a compact form, and it is only affordable because the block is small.
- Larger block that is not a cycle. We would need to choose among exponentially many paths, which is the hard part of the problem. Therefore we return ?!.

Step 6: we add up the block values. Since a red cut vertex between two consecutive blocks is counted in both, we subtract 1 for each such vertex. If s or t is itself a cut vertex, it is an endpoint of the route and nothing is subtracted for it. The sum is the answer.

=== Correctness and running time

*Directed graphs*: reachability, the acyclicity test with the topological order, and the dynamic program (which looks at each edge once) each take $O(n + m)$ time, so the total is $O(n + m)$.

*Undirected graphs*: the connected component of s, the blocks and cut vertices (one depth-first search), and the block-tree with the path from s to t are all computed in $O(n + m)$ time. Edge blocks and cycle blocks are solved in time linear in their size. For a small block with k vertices, the subset DP has at most $2^k dot k$ states (a set of used vertices and an end vertex), and each state is extended to at most k neighbours, so the cost is $O(2^k dot k^2)$. Since $k <= 16$, this is a constant (at most $16^2 dot 2^16 approx 1.7 dot 10^7$ steps) that does not depend on the size of the graph. The DP over all blocks costs $O(n)$ with a large constant factor, and the total for undirected graphs is $O(n + m)$.

The limit of 16 is a practical choice with no theoretical significance: a table of $2^16 dot 16 approx 10^6$ entries is small and fast to fill, while each extra vertex doubles the cost. The algorithm is polynomial for a fixed limit, but it would be exponential if the limit were allowed to grow with the input.

=== Many is NP-hard

Many is an optimisation problem, so we show that its decision version is NP-hard: _given (G, R, s, t, k), is there a simple s,t-path containing at least k red vertices?_ A polynomial-time algorithm for Many would answer this question by comparing the optimum with k, so Many is at least as hard. We reduce from _Hamiltonian Path_, which is known to be NP-complete \[7, Sec. 8.5\].

Let $G = (V, E)$ be an instance of _Hamiltonian Path_, with $n = |V|$ and $m = |E|$.

Construct an instance of Many as follows. Add two new vertices s and t, each connected to every vertex in _V_; s and t are not connected to each other. Keep all original edges and colour every vertex red, so $R = V union {s, t}$. Set $k = n + 2$. The resulting graph $G'$ has $n + 2$ vertices and $m + 2n$ edges, and can be constructed in $O(n + m)$ time.

Suppose the _Many_ instance has a simple _s,t_-path containing $n + 2$ red vertices. Since $G'$ has only $n + 2$ vertices and all of them are red, this path visits every vertex of $G'$ exactly once. The vertices _s_ and _t_ appear only as its endpoints, so removing them leaves a path $v_1, v_2, ..., v_n$ that visits each of the _n_ original vertices exactly once. Every edge between two consecutive vertices $v_i, v_(i+1)$ joins two original vertices. The only new edges are those at _s_ and _t_, so all of these edges belong to _E_. Therefore, $v_1, ..., v_n$ is a _Hamiltonian Path_ in _G_.

Conversely, suppose _G_ has a _Hamiltonian Path_ $v_1, v_2, ..., v_n$. Since s and t are connected to every original vertex, we can construct the path

$ s -> v_1 -> v_2 -> dots.h.c -> v_n -> t. $

This is a simple path through all $n + 2$ vertices, and all of them are red. No path in $G'$ can contain more than $n + 2$ vertices, so the optimal _Many_ value is exactly $n + 2$.

Therefore,
$ G "has a Hamiltonian Path" <==> "Many"(G', R, s, t) = n + 2. $

Since _Hamiltonian Path_ is NP-complete and the reduction takes polynomial time, _Many_ is _NP-hard_.

_Directed graphs._ The same reduction works for directed graphs. Replace every undirected edge ${u, v}$ of $G'$ by the two arcs $u -> v$ and $v -> u$. A simple path in the resulting directed graph uses each vertex at most once, so it corresponds to a simple path in $G'$ and the other way round. The argument above therefore goes through unchanged. Alternatively, one can reduce directly from _Directed Hamiltonian Path_, which is also NP-complete \[7, Sec. 8.5\]: add arcs $s -> v$ and $v -> t$ for every $v in V$.

_Relation to the ?! answers._ The graphs this reduction produces are exactly the cases where our solver answers ?!. $G'$ is undirected and forms a single block: it stays connected when any one vertex is removed, because s and t are joined to every other vertex. Whenever _G_ is not a path or a cycle and $n >= 15$, this block has more than 16 vertices and is not a cycle. The directed version contains cycles ($u -> v -> u$), and on a cyclic graph the topological-order DP cannot be used. So the hardness result covers precisely the graph classes for which we return ?!.

=== Results

We solved 74 of the 154 instances exactly and returned ?! for the other 80. The total solver time over all instances was 14.16 seconds. The slowest instance was wall-n-10000 (n = 80,000), which took 1.56 seconds.

In every one of the 80 hard cases the s-t path:

- for directed graph - contains a cycle in a relevant part
- for undirected graph - contains a block with more than 16 vertices that is not a cycle

== Few

=== Algorithm

The _Few_ problem asks for the minimum number of red vertices on an _s-t_ path, or _-1_ if no such path exists. Unlike _Some_ and _Many_, this problem is easy on every graph, directed or undirected: it is a shortest-path problem in disguise.

=== From red vertices to edge weights

We give every vertex a cost of 1 if it is red and 0 otherwise, so the cost of a route is the number of red vertices on it. To use a standard shortest-path algorithm we move this cost onto the edges: an edge (or arc) _u_ → _v_ gets weight 1 if _v_ is red and 0 otherwise, and the start _s_ adds 1 if it is red itself. The weight of a route from _s_ to _t_ is then exactly the number of red vertices on it. All weights are 0 or 1, so none is negative, and Dijkstra's algorithm \[2, Sec. 4.4\] finds the cheapest route from _s_ to _t_.

=== Why a walk is enough

Dijkstra's algorithm minimises over walks, which may repeat vertices, while the problem asks about paths. Here that does not matter. If a walk visits a vertex _v_ twice, we can cut out the part between the two visits. What is left is still an _s,t_-walk, and it uses no vertex that the original walk did not use, so the number of red vertices stays the same or drops. Repeating this until no vertex repeats turns any walk into a path that is at least as cheap. Since every path is also a walk, the cheapest walk and the cheapest path have the same cost.

=== Implementation

For every vertex _v_ we store dist(_v_), the fewest red vertices on any route from _s_ to _v_ found so far. Initially dist(_s_) is 1 if _s_ is red and 0 otherwise, and every other vertex has dist(_v_) = ∞. A priority queue (Python's _heapq_) holds entries (cost, counter, vertex). The counter breaks ties between equal costs, so the queue never has to compare vertex names.

In each step we take the cheapest entry _u_ from the queue. If its cost is larger than dist(_u_), the entry is outdated and we skip it. If _u_ = _t_, dist(_t_) is final and we stop. Otherwise, for every neighbour _v_ of _u_ we compute dist(_u_) + 1 if _v_ is red (+ 0 otherwise), and if this beats dist(_v_) we update it and push _v_. If _t_ is never reached, dist(_t_) stays ∞ and we return _-1_. If _s_ = _t_, the answer is simply 1 if _s_ is red and 0 otherwise.

The same code works for directed and undirected graphs, because _neighbors()_ returns the out-neighbours of a vertex in a directed graph and all its neighbours in an undirected graph.

=== Correctness and running time

Every vertex is taken out of the queue and processed at most once, and every edge is looked at a constant number of times, so there are at most $O(m)$ pushes. Each queue operation takes $O(log n)$, which gives a total of $O((n + m) log n)$. This is polynomial for all graphs, so _Few_ never needs the answer _?!_.

=== Results

We solved all 154 instances, with no _?!_, and a total solver time of 1.27 seconds. The slowest instance was _common-2-5757_ (_n_ = 5,757, _m_ = 163,671), which took 0.11 seconds.

In 24 instances no _s,t_-path exists, and in 69 instances there is a path that avoids all red vertices (answer 0). Larger answers are rare: the largest are 11 (_grid-50-2_), 9 (_ski-level20-2_) and 5 (_grid-25-2_). Table 2 shows the distribution of answers.

#tcaption[*Table 2.* Distribution of answers for Few.]
#rule-table(
  columns: 2,
  align: (left, right),
  table.hline(stroke: 0.8pt),
  table.header[*Answer*][*Instances*],
  table.hline(stroke: 0.4pt),
  [-1 (no path)], [24],
  [0], [69],
  [1], [42],
  [2], [14],
  [3 to 11], [5],
  table.hline(stroke: 0.4pt),
  [*Total*], [*154*],
  table.hline(stroke: 0.8pt),
)
#v(6pt)

== Alternate

=== Algorithm

For problem Alternate, we solved each instance $G$ by a breadth-first search from _s_ restricted to the _bichromatic_ edges of $G$, that is, the edges _uv_ for which exactly one of _u_ and _v_ is red. An $s,t$-path is alternating if and only if all of its edges are bichromatic, so an alternating path exists if and only if _t_ is reachable from _s_ in the subgraph _G′_ formed by these edges; a shortest $s,t$-walk in $G'$ visits no vertex twice and is therefore a simple path. We never construct $G'$ explicitly: the search runs on the adjacency lists of $G$ and skips every edge whose endpoints have the same colour, using a hash set of red vertices for constant-time colour tests, a hash set of discovered vertices, and a FIFO queue. The search stops as soon as _t_ is discovered, and the answer is trivially _true_ when $s = t$. The running time of this algorithm is $O(n + m)$, and our implementation spends 0.023 seconds on the instance common-2-5757 with _n_ = 5757 and _m_ = 163,671, which is the slowest of all instances. On the largest instance, wall-n-10000 with _n_ = 80,000, it spends less than 10⁻⁴ seconds, because no bichromatic edge leaves _s_ and the search ends immediately.

=== Correctness and running time

Since Alternate reduces to plain $s,t$-reachability in a subgraph of $G$, it is solvable in linear time in full generality. Consequently, there are no instances that we were unable to solve, and no hardness argument is needed for this problem.

=== Results

We solved problem Alternate for all graphs, directed and undirected, using this single algorithm; no structural property of the input (such as acyclicity, planarity, or bipartiteness) is required. In directed instances the search simply follows out-neighbours. All 154 instances were solved exactly (46 _true_, 108 _false_) in 0.17 seconds in total, far below the time limit of 20 minutes per instance.

#heading(numbering: none)[References]

#set text(size: 8pt)
#set par(first-line-indent: 0pt, justify: false)
#grid(
  columns: (auto, 1fr),
  column-gutter: 6pt,
  row-gutter: 6pt,
  [\[1\]], [NetworkX Developers. _NetworkX: Network Analysis in Python_. NetworkX Documentation. Available at: #link("https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.shortest_paths.generic.shortest_path_length.html") (accessed 5 November 2026).],
  [\[2\]], [J. Kleinberg and É. Tardos. Algorithm Design. Pearson/Addison-Wesley, 2006. Sec. 3.2–3.6 (graph traversal, reachability, topological ordering), Sec. 4.4 (Dijkstra's algorithm), Ch. 6 (dynamic programming), Ch. 8 (polynomial-time reductions and NP-completeness).],
  [\[3\]], [R. E. Tarjan. Depth-first search and linear graph algorithms. SIAM Journal on Computing, 1972.],
  [\[4\]], [J. Hopcroft and R. Tarjan. Algorithm 447: Efficient algorithms for graph manipulation. Communications of the ACM, 1973.],
  [\[5\]], [M. Held and R. M. Karp. A dynamic programming approach to sequencing problems. Journal of the Society for Industrial and Applied Mathematics, 1962.],
  [\[6\]], [S. Fortune, J. Hopcroft and J. Wyllie. The directed subgraph homeomorphism problem. Theoretical Computer Science 10(2):111–121, 1980.],
  [\[7\]], [Kleinberg, J., & Tardos, É. (2006). _Algorithm Design_. Pearson/Addison-Wesley. #link("https://www.cs.princeton.edu/~wayne/kleinberg-tardos/")],
)
