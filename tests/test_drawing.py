import matplotlib.pyplot as plt
import pytest

from runner import draw, draw_many, load_instance, run_experiment


@pytest.fixture(autouse=True)
def close_figures():
    yield
    plt.close("all")


def test_draw_with_path(tmp_path):
    out = tmp_path / "g.png"
    ax = draw("G-ex", path=["0", "5", "6", "7", "3"], save=out, show=False)
    assert out.is_file() and "G-ex" in ax.get_title()


def test_draw_directed_and_grid():
    draw(load_instance("increase-n8-1"), show=False)
    draw("grid-5-0", show=False)
    draw("common-1-20", show=False)  # no edges at all


def test_draw_too_big_explains_what_to_do():
    with pytest.raises(ValueError, match="around="):
        draw("rusty-1-2000", show=False)


def test_draw_around():
    ax = draw("rusty-1-2000", around="rusty", radius=1, show=False)
    assert "around 'rusty'" in ax.get_title()


def test_draw_bad_input():
    with pytest.raises(ValueError, match="not in"):
        draw("G-ex", path=["0", "99"], show=False)
    with pytest.raises(ValueError, match="Unknown layout"):
        draw("G-ex", layout="pretty", show=False)
    with pytest.raises(ValueError, match="names like"):
        draw("G-ex", layout="grid", show=False)


def test_path_with_a_non_edge_is_still_drawn():
    draw("G-ex", path=["0", "6", "3"], show=False)


def test_draw_many_from_results(tmp_path):
    results = run_experiment(lambda i: 1 / 0, ["G-ex", "P3", "rusty-1-2000"])
    fig = draw_many(results.failed, save=tmp_path / "f.png", show=False)
    assert len(fig.axes) == 3 and (tmp_path / "f.png").is_file()


def test_draw_many_nothing(capsys):
    assert draw_many([], show=False) is None
    assert "Nothing to draw" in capsys.readouterr().out


def test_headless_show_saves_a_file(monkeypatch, tmp_path):
    monkeypatch.setattr("runner.drawing.repo_root", lambda: tmp_path)
    draw("P3")
    assert (tmp_path / "figures" / "P3.png").is_file()
