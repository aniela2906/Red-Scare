"""Combine the per-problem result files into the ``results.txt`` deliverable.

Each team saves its own results with ``results.save()`` (to ``results/<problem>.tsv``).
Then anyone can build the final table::

    from runner import write_results_txt
    write_results_txt()           # -> results.txt
"""

from __future__ import annotations

import os
from pathlib import Path

from ._paths import repo_root
from ._paths import results_dir as _results_dir
from .experiment import Results
from .instances import _all_files, _natural_key, _read_header

__all__ = ["write_results_txt"]

# Column order used in the report skeleton (doc/report.tex): A F M N S.
COLUMNS = [("A", "alternate"), ("F", "few"), ("M", "many"), ("N", "none"), ("S", "some")]


def write_results_txt(
    results_dir: str | os.PathLike[str] | None = None,
    out: str | os.PathLike[str] | None = None,
    *,
    data_dir: str | os.PathLike[str] | None = None,
) -> Path:
    """Write ``results.txt``: one row per instance, one column per problem, tab-separated.

    Args:
        results_dir: folder with ``alternate.tsv``, ``few.tsv``, ``many.tsv``, ``none.tsv``
            and ``some.tsv`` (default: ``results/`` in the repository). Missing files are fine.
        out: where to write (default: ``results.txt`` in the repository).
        data_dir: where the instances are. Normally found automatically.

    Every instance in the data folder gets a row. A cell is ``?`` when that problem has not
    been run on the instance, or when the run did not finish (timeout, error, ...).

    Returns:
        The path of the written file.
    """
    folder = Path(results_dir) if results_dir is not None else _results_dir()
    target = Path(out) if out is not None else repo_root() / "results.txt"

    answers: dict[str, dict[str, str]] = {}
    missing: list[str] = []
    for letter, problem in COLUMNS:
        path = folder / f"{problem}.tsv"
        if not path.is_file():
            missing.append(problem)
            continue
        answers[letter] = {
            r.instance: str(r.answer) for r in Results.load(path) if r.ok and r.answer is not None
        }

    files = _all_files(data_dir)
    names = sorted(files, key=_natural_key)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", encoding="utf-8", newline="") as f:
        f.write("\t".join(["instance", "n", *(letter for letter, _ in COLUMNS)]) + "\n")
        for name in names:
            n = _read_header(files[name])[0]
            cells = [answers.get(letter, {}).get(name, "?") for letter, _ in COLUMNS]
            f.write("\t".join([name, str(n), *cells]) + "\n")

    print(f"Wrote {len(names)} instances to {target}")
    if missing:
        print(f"No results yet for: {', '.join(missing)} (their columns are all '?').")
    unknown = sorted({i for col in answers.values() for i in col} - set(files))
    if unknown:
        print(
            f"Ignored results for instances that are not in the data folder: {', '.join(unknown)}"
        )
    return target
