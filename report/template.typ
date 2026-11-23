// Red Scare report template: Typst port of red-scare/doc/report.tex,
// laid out as an IEEE conference paper (black and white, two columns).
// Same text and structure as the LaTeX template; only the formatting is new.
//
// Build (from the repo root):
//   typst compile --font-path report/fonts report/template.typ
// report/fonts holds TeX Gyre Termes/Cursor (free Times/Courier clones)
// that the IEEE template expects.

#import "@preview/charged-ieee:0.1.4": ieee

#show: ieee.with(
  title: [Red Scare! Report],
  authors: ((name: "Alice Cooper"),),
  paper-size: "a4",
)

#show footnote.entry: set text(size: 8pt)

= Results

The following table gives my results for all graphs of at least 500 vertices.

#block(above: 10pt, below: 10pt, width: 100%)[#align(center, text(size: 8pt, table(
    columns: 7,
    align: (left, right, right, right, right, right, right),
    stroke: none,
    inset: (x: 5pt, y: 3pt),
    table.hline(stroke: 0.8pt),
    table.header[Instance name][$n$][A][F][M][N][S],
    table.hline(stroke: 0.4pt),
    [rusty-5762], [5,762], [true], [16], [--], [?], [5],
    [wall-p-10000], [10,000], [], [], [], [], [],
    [$dots.v$], [], [], [], [], [], [],
    table.hline(stroke: 0.8pt),
)))]

The columns are for the problems Alternate, Few, Many, None, and Some.
The table entries either give the answer, or contain '?' for those cases where I was unable to find a solution within reasonable time.
For those questions where there is a reason for my inability to find a good algorithm (because the problem is hard), I wrote '?!'.

For the complete table of all results, see the tab-separated text file `results.txt`.

= Methods

For problem A, I solved each instance $G$ by $dots.c$#footnote[Describe what you did.
  Use words like “building a inverse anti-tree without self-loops where each vertex in $G$ is presented by a Strogatz–Wasserman shtump.
  I then performed a standard longest hash sorting using the algorithm of Bronf (Algorithm 5 in [1]).”
  Be neat, brief, and precise.]
The running time of this algorithm is $dot.c$, and my implementation spends $dots.c$ seconds on the instance $dots.c$ with $n = dots.c$.

I solved problem $dots.c$ for all $dots.c$#footnote[For instance, “planar, bipartite”] graphs using $dots.c$.

I was unable to solve problem $dots.c$ except for the $dots.c$ instances.
This is because, in generality, this problem is $dots.c$.
To see this, consider the following reduction from $dots.c$.
Let $dots$

I was also unable to solve $dots.c$ for $dots.c$, but I don’t know why.#footnote[Remove or expand as necessary.]

#heading(numbering: none)[References]

#set text(size: 8pt)
#grid(
  columns: (auto, 1fr),
  column-gutter: 6pt,
  row-gutter: 6pt,
  [[1]], [_APLgraphlib---A library for Basic Graph Algorithms in APL_, version 2.11, 2016, Iverson Project, `github.com/iverson/APLgraphlib`.#footnote[If you use references to code, books, or papers, be professional about it. Use whatever style you want, but be consistent.]],
  [[2]], [A. Lovelace, _Algorithms and Data Structures in Pascal_, Addison–Wesley 1881.],
)
