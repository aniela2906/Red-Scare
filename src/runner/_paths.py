"""Find the folder that holds the Red Scare instance files."""

from __future__ import annotations

import os
from pathlib import Path

ENV_VAR = "RED_SCARE_DATA"

# Where the data lives relative to the repository root.
_RELATIVE_DATA_DIR = Path("red-scare") / "data"


def _candidates() -> list[Path]:
    """Places we look for the data folder, most specific first."""
    found: list[Path] = []
    # 1. Relative to this file: <repo>/src/runner/_paths.py -> <repo>/red-scare/data
    here = Path(__file__).resolve()
    for parent in here.parents:
        found.append(parent / _RELATIVE_DATA_DIR)
    # 2. Relative to the current working directory and its parents.
    cwd = Path.cwd().resolve()
    for parent in (cwd, *cwd.parents):
        found.append(parent / _RELATIVE_DATA_DIR)
        found.append(parent / "data")
    return found


def data_dir(override: str | os.PathLike[str] | None = None) -> Path:
    """Return the folder with the ``*.txt`` instance files.

    Order of precedence:

    1. ``override`` (the ``data_dir=`` argument of the loading functions),
    2. the ``RED_SCARE_DATA`` environment variable,
    3. ``red-scare/data`` in the repository.
    """
    if override is not None:
        path = Path(override).expanduser()
        if not path.is_dir():
            raise FileNotFoundError(f"data_dir={str(override)!r} is not a folder.")
        return path.resolve()

    env = os.environ.get(ENV_VAR)
    if env:
        path = Path(env).expanduser()
        if not path.is_dir():
            raise FileNotFoundError(
                f"The environment variable {ENV_VAR}={env!r} does not point to a folder.\n"
                f"Fix it, or unset it to use the repository's red-scare/data folder."
            )
        return path.resolve()

    for candidate in _candidates():
        if candidate.is_dir() and any(candidate.glob("*.txt")):
            return candidate.resolve()

    raise FileNotFoundError(
        "Could not find the Red Scare data folder (red-scare/data).\n"
        "Run your code from inside the repository, or tell the runner where the data is:\n"
        f"  - set the environment variable {ENV_VAR}=/path/to/red-scare/data, or\n"
        "  - pass data_dir='/path/to/red-scare/data' to load_instance / load_instances."
    )


def repo_root() -> Path:
    """The repository root (the folder with ``pyproject.toml``), or the current folder."""
    for parent in Path(__file__).resolve().parents:
        if (parent / "pyproject.toml").is_file() and (parent / "src" / "runner").is_dir():
            return parent
    return Path.cwd().resolve()


def results_dir() -> Path:
    """Where ``Results.save()`` writes by default: ``<repo>/results``."""
    return repo_root() / "results"
