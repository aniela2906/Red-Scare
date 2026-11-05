"""Run the None solver on every instance.

uv run python src/none/run.py
"""

from none.solver import solve
from runner import draw_many, load_instances, run_experiment

if __name__ == "__main__":
    results = run_experiment(solve, load_instances(), problem="none")
    results.save()  # -> results/none.tsv
    if results.failed:
        draw_many(results.failed)  # pictures of the instances that went wrong
