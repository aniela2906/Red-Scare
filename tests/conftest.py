import os

import matplotlib
import pytest

os.environ.setdefault("MPLBACKEND", "Agg")
matplotlib.use("Agg")


@pytest.fixture
def write_instance(tmp_path):
    """Write an instance file with the given text and return its path."""

    def write(text: str, name: str = "tiny.txt"):
        path = tmp_path / name
        path.write_text(text, encoding="utf-8", newline="")
        return path

    return write
