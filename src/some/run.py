"""Run the Some solver on every instance.

uv run python src/some/run.py
"""

from runner import draw_many, load_instances, run_experiment
from some.solver import solve

if __name__ == "__main__":
    results = run_experiment(solve, load_instances(), problem="some")
    results.save()  # -> results/some.tsv
    if results.failed:
        draw_many(results.failed)  # pictures of the instances that went wrong
