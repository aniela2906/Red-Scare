"""Run the Many solver on every instance.

uv run python src/many/run.py
"""

from many.solver import solve
from runner import draw_many, load_instances, run_experiment

if __name__ == "__main__":
    results = run_experiment(solve, load_instances(), problem="many")
    results.save()  # -> results/many.tsv
    if results.failed:
        draw_many(results.failed)  # pictures of the instances that went wrong
