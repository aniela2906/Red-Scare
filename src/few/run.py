"""Run the Few solver on every instance.

uv run python src/few/run.py
"""

from few.solver import solve
from runner import draw_many, load_instances, run_experiment

if __name__ == "__main__":
    results = run_experiment(solve, load_instances(), problem="few")
    results.save()  # -> results/few.tsv
    if results.failed:
        draw_many(results.failed)  # pictures of the instances that went wrong
