# Red-Scare
### Algorithm Design (Autumn 2026)

```
Red-Scare/
├── red-scare/        # the assignment files (don't edit)
│   ├── data/         #   the 154 graphs
│   └── doc/          #   assignment text and report template
├── src/
│   ├── runner/       # shared code everyone uses
│   ├── none/         # one folder per problem
│   ├── some/
│   ├── many/
│   ├── few/
│   └── alternate/
├── report.docx       (PDF when we are done)
├── tests/
├── results/          # saved answers, one file per problem
└── results.txt       # the final table we hand in
```

## 1. Setup (once)

Install [uv](https://docs.astral.sh/uv/getting-started/installation/). Then, in this folder:

```bash
uv sync
```

## 2. Write your code

Open `src/<your problem>/solver.py` and fill in the `solve` function:

```python
def solve(instance):
    graph = instance.graph     # the graph (a networkx graph)
    s = instance.s             # start vertex
    t = instance.t             # end vertex
    red = instance.red         # the red vertices
    ...
    return 3                   # your answer
```

Return a number for None, Many and Few. Return `True` or `False` for Some and Alternate. If you can't work out the answer for a graph, return `"?"`.

## 3. Run it on all graphs

```bash
uv run python src/<your problem>/run.py
```

You'll see a progress bar and one line per graph. Each graph gets at most 20 minutes. At the end, your answers are saved in `results/<your problem>.tsv`, and pictures are drawn of the graphs that went wrong.

## Trying things out

You can also do it step by step in a script or notebook:

```python
from runner import load_instance, load_instances, run_experiment, draw
from some.solver import solve

g = load_instance("G-ex")            # load one graph
solve(g)                             # try your code on it
draw(g)                              # look at it

graphs = load_instances(max_n=1000)  # all graphs with at most 1000 vertices
results = run_experiment(solve, graphs, problem="some", timeout="5m")

results.summary()                    # table of answers and times
results.show_error("G-ex")           # what went wrong on one graph
results.save()                       # save to results/some.tsv
```

Other ways to pick graphs: `load_instances("wall-*")` for all names that start with `wall-`, or `load_instances(["G-ex", "P3"])` for just those two.

For a big graph, draw only the part near one vertex: `draw("rusty-1-2000", around="rusty")`.

## Making `results.txt`

When everyone has saved their answers:

```python
from runner import write_results_txt
write_results_txt()
```

Any answer that is missing shows up as `?`.

## Common questions

**It's taking forever.** Press Ctrl+C. You keep the answers you already have. To use a shorter time limit, pass `timeout="1m"`.

**Breakpoints don't stop.** Add `isolate=False` to `run_experiment`. The time limit is turned off in that mode.

**My `print` output doesn't show up in the notebook.** Same fix: `isolate=False`.

**Error on Windows or Mac about "worker process".** Put `solve` in a `.py` file, not a notebook. Run it the way `run.py` does, under `if __name__ == "__main__":`.

**Can I change the graph inside `solve`?** Yes. Each run gets its own copy.

**Some graphs have edges from a vertex to itself.** A few `smallworld` files do. These edges can never be part of a path, so they are removed when the graph is loaded.
