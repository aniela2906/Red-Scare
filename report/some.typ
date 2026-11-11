// Red Scare report: the Some problem.
// Build:   typst compile --root . report/some.typ     (from the repo root)
//          --root . lets the report read results/some.tsv for the results tables.
// Figures: uv run python report/figures/make_some_figures.py

#set document(title: "Red Scare: the Some problem", author: "João Maia")
#set page(paper: "a4", margin: 2.5cm, numbering: "1")
#set text(size: 11pt, lang: "en")
#set par(justify: true)
#set heading(numbering: "1.")
#show figure.caption: set text(size: 9.5pt)
#show figure: set block(spacing: 1.6em)

#let Some = smallcaps[Some]
#let TDP = smallcaps[Two disjoint paths]
#let fig(file, width: 100%, caption: none) = figure(
  image("figures/" + file + ".svg", width: width),
  placement: auto,
  caption: caption,
)

#align(center)[
  #text(size: 17pt, weight: "bold")[Red Scare: the #Some problem]
  #v(0.2em)
  João Maia
]

= The problem

Let's first understand the problem and its edge cases, and then how we came up with the algorithm that solves almost every instance.
We will also see that there is one kind of graph for which no polynomial-time algorithm is known: the problem is NP-hard there.

#Some asks: is there a path from $s$ to $t$ that goes through at least one red vertex?
The important word is _path_: no vertex may be used twice.
For the sake of simplicity we start with undirected graphs only.
@fig-yes-no shows one graph where the answer is yes and one where it is no.

#fig("some-yes-no", caption: [
  Left: the path $s, a, r, c, t$ passes through the red vertex $r$.
  Right: $t$ is easy to reach, but every red vertex hangs off the side.
  Going into $q$ or $r$ means coming back out through the vertex we came from, so no path visits red.
]) <fig-yes-no>

= A first idea: BFS from the red vertex

The first idea is to pick a red vertex $r$ and run two BFS from it: one to find $s$ and one to find $t$.
If both are found, it looks like there is a path $s ~> r ~> t$.
We do this for every red vertex until one works.

There are a few optimisations we could add.
For example, using disjoint sets (or one search from $s$) to skip red vertices that are not even in the same component as $s$ and $t$.
As we will see, the final algorithm only keeps the simplest of these.

Running two BFS costs $O(n+m)$, so in total this is $O(r dot (n+m))$, where $r$ is the number of red vertices.

Now comes the important question: does this work for all undirected graphs?
The answer is a straight no.
BFS is a kind of greedy solution: each search grabs the shortest route it can find, and the two searches know nothing about each other.
So the two routes can overlap, as in @fig-overlap, where both use the vertices $a$ and $b$.
Glued together they give $s, a, b, r, b, a, t$, which uses $a$ and $b$ twice.
That is a walk, not a path.

The BFS answer is wrong either way.
If we accept the overlap, we say yes on graphs where no path exists.
If we reject it, we say no in @fig-overlap, where a path _does_ exist: $s$ just has to take the long way round.
What we would need is a way to _recalculate_ a route once we see that it blocks the other one, and BFS cannot do that.

#fig("some-bfs-overlap", width: 92%, caption: [
  Left: the two shortest routes from $r$ share $a$ and $b$.
  Right: a real path through $r$ exists, but only if the route to $s$ gives up $a$ and $b$.
]) <fig-overlap>

= Turning it into a network flow problem

This issue, needing to recalculate routes when a better choice appears, is exactly what network flow algorithms are built for.
In max-flow / min-cut problems, Ford–Fulkerson keeps changing earlier routes until it finds the best flow, or finds the bottleneck that stops it.
The idea fits our problem closely: we want a flow (which in our case is really a path) that passes through the red vertex.

To turn the graph into a flow network we do the following (@fig-network):
- Add a _super source_ $X$ with an arc to $s$ and an arc to $t$, each of capacity 1.
  This makes sure both $s$ and $t$ are part of the answer.
- Make the red vertex $r$ the _sink_.
  As before, we do this for every red vertex, one at a time.
- Every other capacity is 1: one unit of flow is one route.

#fig("some-network", width: 92%, caption: [
  The example graph, and the same graph with the super source $X$ and the red vertex $r$ as the sink.
]) <fig-network>

Why 2 units?
$X$ can push at most 2 units, since it has two arcs of capacity 1.
Getting both units out means using both arcs, so one unit has to start at $s$ and the other at $t$.
If both units reach $r$, we have a route $s ~> r$ and a route $t ~> r$.
Flip the second one and glue the two: that is the path $s ~> r ~> t$.
So the question becomes: is the maximum flow from $X$ to $r$ equal to 2?

*Each vertex only once.*
Capacities in a flow network sit on edges, but our rule ("no repeated vertex") is about vertices.
Two routes could use different edges and still meet in the middle at the same vertex.
The standard fix is to split every vertex $v$ into $v_"in" -> v_"out"$ with capacity 1 (@fig-split).
Every edge into $v$ arrives at $v_"in"$, and every edge out of $v$ leaves from $v_"out"$, so at most one unit can pass through $v$.
An undirected edge ${u, v}$ becomes two arcs, $u_"out" -> v_"in"$ and $v_"out" -> u_"in"$, and the flow picks which one to use.
The sink is $r_"in"$.
Because the flow stops there, before the arc $r_"in" -> r_"out"$, the red vertex can receive both units: one from each side.

#fig("some-split", width: 75%, caption: [
  Splitting vertices. Only one unit can cross from $v_"in"$ to $v_"out"$, so at most one route uses $v$.
]) <fig-split>

= Running Ford–Fulkerson

Now that we have the network, we run a BFS from the super source $X$ to the sink $r_"in"$.

+ *Round 1.*
  $X$ only has arcs to $s$ and $t$, so this one BFS searches from $s$ and $t$ at the same time.
  It finds the shortest route to $r$, which starts at either $s$ or $t$, and we push 1 unit along it.
  If there is no route at all, we stop early: this red vertex does not work.
+ *Round 2.*
  We run BFS again, but now in the _residual graph_.
  This is the network as it looks given the flow so far: arcs that are full can't be used, and every arc that carries flow can be followed _backwards_, which undoes that flow.
  The arc used by round 1 out of $X$ is now full, so this route must start at the other one of $s$ and $t$.
+ If round 2 also finds a route, the flow is 2 and the answer is yes.
  If not, the flow has reached its maximum. That maximum is below 2, so no path from $s$ to $t$ passes through this red vertex.

The backwards step is what BFS alone was missing (@fig-rounds).
In round 1, the route from $s$ takes the shortcut through $a$ and $b$.
In round 2, the route from $t$ reaches $a$ and finds it full.
Instead of giving up, it follows the arc $s -> a$ backwards, back to $s$, and continues from there along $c, e, d$ to $r$.
After pushing, the unit from $s$ has moved to the long way round, and the unit from $t$ uses $a$ and $b$.
That is exactly the recalculation we wanted.

#fig("some-rounds", caption: [
  The two rounds on the example. The dashed red arrow is an arc followed backwards in the residual graph: it cancels the flow on $s -> a$.
]) <fig-rounds>

*Reading the path.*
We don't glue the two BFS routes together, because round 2's route contains a backwards step.
Instead, we look at which arcs carry flow at the end.
Every vertex passes on exactly what it receives, and carries at most 1 unit.
So starting at $s$ and following the arcs that carry flow leads to $r$, with no choices along the way and no repeated vertex.
The same holds from $t$.
Flip the second route and glue: in the example, $s, c, e, d, r$ and $t, a, b, r$ give $s, c, e, d, r, b, a, t$.

*Edge cases.*
If $s$ and $t$ are in different components, the answer is false.
If $s$ or $t$ is red, any $s$–$t$ path works, so one BFS is enough.
We only try red vertices in the same component as $s$ (one search finds them all), which is the only part of the disjoint-set optimisation that we kept.

*Running time.*
Building the network costs $O(n+m)$ and is done once.
Each red vertex costs at most two BFS, so $O(n+m)$, and resetting the flow afterwards only touches the arcs on the two routes.
In total this is $O(r dot (n+m))$, and less in practice, since we stop at the first red vertex that works.

= Directed graphs

This allows us to solve every undirected graph.
There is, however, a category of graphs that we can't solve in polynomial time: _directed graphs with cycles_.
This might seem counter-intuitive at first, since we are using network flow techniques, and flow works fine on directed graphs.
The trick that made undirected graphs work was flipping the route $s ~> r$ so that both units flow _into_ $r$.
On a directed graph we are not allowed to flip it.

*Where the flow breaks.*
Take the simplest directed graph where the answer is yes: $s -> r -> t$ (@fig-directed).
Build our network with arcs only in the given directions, and send flow from $X$ into $r_"in"$.
The unit from $s$ goes $X -> s -> r$.
The unit from $t$ is stuck, because $t$ has no arrows going out.
The flow is 1, so the algorithm says no, which is wrong.
The unit from $t$ would need to travel _against_ the arrow $r -> t$.

#fig("some-directed", width: 50%, caption: [
  Our network on the directed path $s -> r -> t$: only one unit reaches $r$.
]) <fig-directed>

The natural fix is to let the unit from $t$ follow arrows backwards.
The trouble is that flow units are all the same: the network can't tell the unit from $s$ apart from the unit from $t$.
An arc has one direction for everyone, so we would need

$ "arc" u -> v: quad "forwards if the unit from" s "uses it, backwards if the unit from" t "uses it." $

No flow network can express "the direction depends on which unit is using it".
If we reverse all arcs, the unit from $s$ breaks instead.
If we add both directions, the graph is no longer directed, and we would accept paths that go the wrong way down one-way arcs.

What we really need are two different kinds of flow, one going $s ~> r$ and one going $r ~> t$, kept apart.
This is called a two-commodity flow.
With whole units on a directed graph, it is exactly the _two disjoint paths_ problem.

*NP-hardness.*
"Our trick doesn't work" does not by itself prove that the problem is hard.
Maybe someone cleverer has a different trick.
A reduction is what rules that out:

+ #TDP: given a directed graph and vertices $s_1, t_1, s_2, t_2$, is there a path $s_1 ~> t_1$ and a path $s_2 ~> t_2$ that share no vertex?
  This is NP-complete [1].
+ Given such an instance, add one new red vertex $r$ with the arcs $t_1 -> r$ and $r -> s_2$, and ask #Some with $s = s_1$ and $t = t_2$ (@fig-reduction).
  The only way into $r$ is from $t_1$, and the only way out is to $s_2$.
  So every path through $r$ has the form $s_1 ~> t_1 -> r -> s_2 ~> t_2$ with no repeated vertex, which is exactly a pair of disjoint paths.
  In the other direction, any pair of disjoint paths glued through $r$ is a path through red.
+ So any polynomial algorithm for #Some on directed graphs, flow-based or not, would also solve #TDP in polynomial time.
  Unless P = NP, no such algorithm exists.
  For these instances our answer is `?!`.

#fig("some-reduction", width: 60%, caption: [
  The reduction. The added red vertex $r$ forces every path through red to consist of a route $s_1 ~> t_1$ and a disjoint route $s_2 ~> t_2$.
]) <fig-reduction>

To sum up: flow works on undirected graphs only because flipping lets both halves become the same kind of flow.
On directed graphs we can't flip, and we are left with two different kinds of flow, which is the hard problem.
For comparison, #TDP on _undirected_ graphs is solvable in polynomial time, which matches what we found.

*Directed graphs without cycles.*
It is also important to say that directed graphs _without_ cycles can be solved in polynomial time, and more easily than undirected ones.
In such a graph, the routes $s ~> r$ and $r ~> t$ can never share a vertex $v$.
If they did, we would have $v ~> r ~> v$, which is a cycle.
So two searches are enough: one forwards from $s$, and one backwards from $t$ following the arrows in reverse.
If some red vertex is found by both, the answer is yes.
This takes $O(n+m)$.
@fig-cycle shows why the same check is wrong once there is a cycle.
This is why our Python code starts by checking whether a directed graph has cycles.
If it does, we answer `?!`.

#fig("some-cycle", width: 50%, caption: [
  With the cycle $v -> r -> v$, $s$ reaches $r$ and $r$ reaches $t$, but both routes need $v$.
]) <fig-cycle>

= Results

#figure(
  table(
    columns: 3,
    align: left,
    stroke: none,
    table.hline(),
    table.header([*Graph*], [*Method*], [*Time*]),
    table.hline(stroke: 0.5pt),
    [$s$ or $t$ is red], [is there any $s$–$t$ path?], [$O(n+m)$],
    [Undirected], [flow with sink $r_"in"$, for each red $r$], [$O(r dot (n+m))$],
    [Directed, no cycles], [search from $s$ and back from $t$], [$O(n+m)$],
    [Directed with cycles], [NP-hard in general: `?!`], [–],
    table.hline(),
  ),
  caption: [Which method we use for which kind of graph.],
)

// ---- results, read from results/some.tsv (written by src/some/run.py) ----
#let rows = csv("../results/some.tsv", delimiter: "\t").slice(1).map(r => (
  name: r.at(0), n: int(r.at(1)), m: int(r.at(2)), status: r.at(3),
  answer: r.at(4), seconds: float(r.at(5)),
))
#let family(name) = {
  let parts = name.split("-")
  while parts.len() > 1 and parts.last().contains(regex("[0-9]")) { parts = parts.slice(0, -1) }
  parts.join("-")
}
#let thousands(x) = {
  let digits = str(x).clusters().rev()
  let out = ()
  for (i, d) in digits.enumerate() {
    if i > 0 and calc.rem(i, 3) == 0 { out.push(sym.space.thin) }
    out.push(d)
  }
  out.rev().join()
}
#let secs(x) = {
  if x < 0.001 { return "<0.001" }
  let ms = str(int(calc.round(x * 1000)))
  while ms.len() < 4 { ms = "0" + ms }
  ms.slice(0, -3) + "." + ms.slice(-3)
}
#let n-true = rows.filter(r => r.answer == "true").len()
#let n-false = rows.filter(r => r.answer == "false").len()
#let total = rows.map(r => r.seconds).sum()
#let slowest = rows.sorted(key: r => r.seconds).last()

All 31 directed graphs in the data set turned out to have no cycles, so we never needed `?!`.
We solved all #rows.len() instances: #n-true are true and #n-false are false.
Together they took #calc.round(total, digits: 1) seconds of solver time.
The slowest instance was #raw(slowest.name) ($n = #thousands(slowest.n)$), at #calc.round(slowest.seconds, digits: 1) seconds.
@tab-families sums up the results per family of graphs, and the appendix lists every instance.

#let families = rows.map(r => family(r.name)).dedup()
#figure(
  table(
    columns: 6,
    align: (left, right, right, right, right, right),
    stroke: none,
    table.hline(),
    table.header([*Family*], [*Instances*], [*true*], [*false*], [*Largest $n$*], [*Time (s)*]),
    table.hline(stroke: 0.5pt),
    ..families.map(f => {
      let rs = rows.filter(r => family(r.name) == f)
      (
        raw(f),
        str(rs.len()),
        str(rs.filter(r => r.answer == "true").len()),
        str(rs.filter(r => r.answer == "false").len()),
        thousands(calc.max(..rs.map(r => r.n))),
        secs(rs.map(r => r.seconds).sum()),
      )
    }).flatten(),
    table.hline(stroke: 0.5pt),
    [*Total*], [*#rows.len()*], [*#n-true*], [*#n-false*], [], [*#secs(total)*],
    table.hline(),
  ),
  caption: [Results per family of graphs. Time is the total solver time for the family.],
) <tab-families>

We tested the solver against brute force (trying every simple path) on 6000 small random graphs, both undirected and directed without cycles.
It always gave the same answer, and every path it returned was checked to be a real path through a red vertex.

= References

[1] S. Fortune, J. Hopcroft, J. Wyllie. The directed subgraph homeomorphism problem. _Theoretical Computer Science_ 10(2):111–121, 1980.

#pagebreak()
#set heading(numbering: none)
= Appendix: results for every instance <appendix>

All #rows.len() instances, in the same order as `results/some.tsv`.
Time is the solver time in seconds.

#{
  set text(size: 8pt)
  columns(2, gutter: 1.2em, table(
    columns: (1fr, auto, auto, auto, auto),
    align: (left, right, right, left, right),
    stroke: none,
    inset: (x: 4pt, y: 2.2pt),
    table.hline(),
    table.header([*Instance*], [*$n$*], [*$m$*], [*Answer*], [*Time*]),
    table.hline(stroke: 0.5pt),
    ..rows.map(r => (
      raw(r.name), thousands(r.n), thousands(r.m),
      if r.status == "ok" { r.answer } else { "?" },
      secs(r.seconds),
    )).flatten(),
    table.hline(),
  ))
}
