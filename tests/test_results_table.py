from runner import Results, RunResult, list_instances, write_results_txt


def test_results_txt(tmp_path, capsys):
    Results(
        [
            RunResult("G-ex", 8, 9, "ok", answer=3),
            RunResult("P3", 3, 2, "timeout"),
        ],
        problem="none",
    ).save(tmp_path / "none.tsv")
    Results([RunResult("G-ex", 8, 9, "ok", answer="true")], problem="some").save(
        tmp_path / "some.tsv"
    )
    out = write_results_txt(tmp_path, tmp_path / "results.txt")
    lines = out.read_text().splitlines()
    assert lines[0] == "instance\tn\tA\tF\tM\tN\tS"
    assert len(lines) == 1 + len(list_instances())
    rows = {line.split("\t")[0]: line.split("\t") for line in lines[1:]}
    assert rows["G-ex"] == ["G-ex", "8", "?", "?", "?", "3", "true"]
    assert rows["P3"] == ["P3", "3", "?", "?", "?", "?", "?"]
    assert "No results yet for: alternate, few, many" in capsys.readouterr().out
