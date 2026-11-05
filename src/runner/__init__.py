"""Shared toolkit for the Red Scare! exercise: load instances, run solvers, draw graphs.

Quick start::

    from runner import load_instances, run_experiment, draw_many

    def solve(instance):
        # instance.graph  -> a networkx Graph or DiGraph
        # instance.s, instance.t, instance.red, instance.is_red(v)
        return 42

    results = run_experiment(solve, load_instances(max_n=500), problem="none")
    results.summary()
    results.save()                 # -> results/none.tsv
    draw_many(results.failed)      # look at what went wrong

Every function has a docstring with examples: try ``help(run_experiment)``.
"""

from ._timefmt import format_duration, parse_duration
from .drawing import draw, draw_many
from .experiment import PROBLEMS, Results, RunResult, run_experiment
from .instances import (
    Instance,
    InstanceFormatError,
    InstanceNotFoundError,
    list_families,
    list_instances,
    load_instance,
    load_instances,
)
from .results_table import write_results_txt

__all__ = [
    "PROBLEMS",
    "Instance",
    "InstanceFormatError",
    "InstanceNotFoundError",
    "Results",
    "RunResult",
    "draw",
    "draw_many",
    "format_duration",
    "list_families",
    "list_instances",
    "load_instance",
    "load_instances",
    "parse_duration",
    "run_experiment",
    "write_results_txt",
]
