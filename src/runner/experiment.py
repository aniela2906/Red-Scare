"""Running a solver over many instances, with a timeout and a progress bar.

Example::

    from runner import load_instances, run_experiment

    def solve(instance):
        ...                      # your algorithm
        return 3                 # an int, True/False, or "?" if you cannot tell

    results = run_experiment(solve, load_instances(max_n=1000), problem="none")
    results.summary()            # table of answers and running times
    results.save()               # -> results/none.tsv
"""

from __future__ import annotations

import contextlib
import csv
import difflib
import inspect
import math
import multiprocessing as mp
import numbers
import os
import pickle
import sys
import time
import traceback
import warnings
from collections.abc import Callable, Iterable, Iterator
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Literal

from tqdm.auto import tqdm

from ._paths import results_dir as _results_dir
from ._timefmt import format_duration, parse_duration
from .instances import Instance, load_instance, load_instances

__all__ = ["PROBLEMS", "Results", "RunResult", "run_experiment"]

Status = Literal["ok", "timeout", "error", "crashed", "skipped"]

#: The five Red Scare problems and the kind of answer each one expects.
PROBLEMS: dict[str, str] = {
    "alternate": "bool",
    "few": "int",
    "many": "int",
    "none": "int",
    "some": "bool",
}

#: Answers that mean "I could not solve this instance" ("?!" = "and it is a hard problem").
NO_ANSWER = ("?", "?!")

DEFAULT_TIMEOUT = "20m"

_SYMBOL = {"ok": "✓", "timeout": "⏱", "error": "✗", "crashed": "✗", "skipped": "·"}
_TSV_FIELDS = ["instance", "n", "m", "status", "answer", "seconds", "error"]


# --------------------------------------------------------------------------- results


@dataclass(frozen=True)
class RunResult:
    """What happened when the solver ran on one instance.

    Attributes:
        instance: instance name, e.g. ``"G-ex"``.
        n, m:     number of vertices and edges.
        status:   ``"ok"``, ``"timeout"``, ``"error"``, ``"crashed"`` or ``"skipped"``.
        answer:   the solver's answer (``True``/``False`` become ``"true"``/``"false"``),
                  or ``None`` if there is none.
        seconds:  time spent inside the solver (for a timeout: the time limit).
        error:    one-line error message, if something went wrong.
        traceback: the full Python traceback, if the solver raised an exception.
        warning:  a note about a suspicious answer (e.g. a number for a yes/no problem).
    """

    instance: str
    n: int
    m: int
    status: Status
    answer: int | str | None = None
    seconds: float | None = None
    error: str | None = None
    traceback: str | None = None
    warning: str | None = None

    @property
    def ok(self) -> bool:
        """True if the solver finished and returned an answer."""
        return self.status == "ok"


class Results:
    """The results of :func:`run_experiment`. Behaves like a list of :class:`RunResult`.

    Handy things to do with it::

        results.summary()              # print a table
        results["G-ex"].answer         # look up one instance by name (or results[0])
        results.failed                 # only timeouts, errors and crashes
        results.show_error("G-ex")     # full traceback of one failed run
        results.save()                 # write results/<problem>.tsv
        draw_many(results.failed)      # look at the graphs that went wrong
    """

    def __init__(
        self,
        runs: Iterable[RunResult],
        *,
        problem: str | None = None,
        solver: str | None = None,
        timeout: float | None = None,
        instances: dict[str, Instance] | None = None,
    ):
        self.runs: list[RunResult] = list(runs)
        self.problem = problem
        self.solver = solver
        self.timeout = timeout
        self._instances = instances or {}

    # ---- list-like behaviour
    def __len__(self) -> int:
        return len(self.runs)

    def __iter__(self) -> Iterator[RunResult]:
        return iter(self.runs)

    def __bool__(self) -> bool:
        return bool(self.runs)

    def __getitem__(self, key: int | str | slice) -> Any:
        if isinstance(key, slice):
            return self._subset(self.runs[key])
        if isinstance(key, str):
            for run in self.runs:
                if run.instance == key:
                    return run
            names = [r.instance for r in self.runs]
            close = difflib.get_close_matches(key, names, n=3)
            hint = f" Did you mean {' or '.join(map(repr, close))}?" if close else ""
            raise KeyError(f"No result for instance {key!r}.{hint}")
        return self.runs[key]

    def __contains__(self, name: object) -> bool:
        return any(r.instance == name for r in self.runs)

    def _subset(self, runs: Iterable[RunResult]) -> Results:
        return Results(
            runs,
            problem=self.problem,
            solver=self.solver,
            timeout=self.timeout,
            instances=self._instances,
        )

    # ---- filters
    @property
    def ok(self) -> Results:
        """Runs that finished with an answer."""
        return self._subset(r for r in self.runs if r.status == "ok")

    @property
    def failed(self) -> Results:
        """Runs that went wrong: timeouts, errors and crashes (not the skipped ones)."""
        return self._subset(r for r in self.runs if r.status in ("timeout", "error", "crashed"))

    @property
    def skipped(self) -> Results:
        """Runs that never started (stopped with Ctrl+C, or the solver is not implemented)."""
        return self._subset(r for r in self.runs if r.status == "skipped")

    @property
    def timed_out(self) -> Results:
        """Runs that hit the time limit."""
        return self._subset(r for r in self.runs if r.status == "timeout")

    @property
    def errors(self) -> Results:
        """Runs where the solver raised an exception or crashed."""
        return self._subset(r for r in self.runs if r.status in ("error", "crashed"))

    @property
    def unsolved(self) -> Results:
        """Runs where the solver answered ``"?"`` or ``"?!"``."""
        return self._subset(r for r in self.runs if r.status == "ok" and r.answer in NO_ANSWER)

    def answers(self) -> dict[str, int | str | None]:
        """``{instance name: answer}`` for every run (``None`` when there is no answer)."""
        return {r.instance: r.answer for r in self.runs}

    def instances(self) -> list[Instance]:
        """The :class:`Instance` objects of these runs, e.g. to draw them."""
        out = []
        for run in self.runs:
            inst = self._instances.get(run.instance)
            if inst is None:
                inst = self._instances[run.instance] = load_instance(run.instance)
            out.append(inst)
        return out

    # ---- display
    def counts(self) -> dict[str, int]:
        """How many runs ended with each status, e.g. ``{"ok": 150, "timeout": 4}``."""
        counts: dict[str, int] = {}
        for run in self.runs:
            counts[run.status] = counts.get(run.status, 0) + 1
        return counts

    def _totals_line(self) -> str:
        counts = self.counts()
        parts = [f"{counts[s]} {s}" for s in _SYMBOL if counts.get(s)]
        unsolved = len(self.unsolved)
        if unsolved:
            parts.append(f'{unsolved} answered "?"')
        total = sum(r.seconds or 0 for r in self.runs if r.status in ("ok", "error"))
        line = f"{len(self.runs)} instances: {', '.join(parts) or 'nothing ran'}"
        line += f" · solver time {format_duration(total)}"
        timed = [r for r in self.runs if r.status == "ok" and r.seconds is not None]
        if timed:
            slowest = max(timed, key=lambda r: r.seconds or 0)
            line += f" · slowest {slowest.instance} ({format_duration(slowest.seconds)})"
        return line

    def __repr__(self) -> str:
        what = f"{self.problem!r}, " if self.problem else ""
        counts = ", ".join(f"{k}={v}" for k, v in self.counts().items())
        return f"<Results {what}{len(self)} runs: {counts or 'empty'}>"

    def summary(self, *, only_failed: bool = False, file: Any = None) -> None:
        """Print a table with one row per instance and a line of totals.

        Args:
            only_failed: show only timeouts, errors and crashes.
            file: where to print (default: the screen).
        """
        rows = list(self.failed if only_failed else self.runs)
        out = file or sys.stdout
        if rows:
            name_w = max(8, *(len(r.instance) for r in rows))
            ans_w = max(6, *(len(_fmt_answer(r.answer)) for r in rows))
            print(
                f"  {'instance':<{name_w}}  {'n':>7}  {'m':>7}  {'status':<8}  "
                f"{'answer':<{ans_w}}  {'time':>9}  note",
                file=out,
            )
            for r in rows:
                note = r.error or r.warning or ""
                if len(note) > 70:
                    note = note[:67] + "..."
                print(
                    f"{_SYMBOL[r.status]} {r.instance:<{name_w}}  {r.n:>7}  {r.m:>7}  "
                    f"{r.status:<8}  {_fmt_answer(r.answer):<{ans_w}}  "
                    f"{format_duration(r.seconds) if r.seconds is not None else '-':>9}  {note}",
                    file=out,
                )
        elif only_failed:
            print("Nothing failed. 🎉", file=out)
        print(self._totals_line(), file=out)

    def show_error(self, name: str | None = None) -> None:
        """Print the full error (with traceback) of one failed run.

        With no name, shows the first failed run.
        """
        if name is None:
            failed = [r for r in self.runs if r.error]
            if not failed:
                print("No run failed with an error.")
                return
            run = failed[0]
        else:
            run = self[name]
        if run.traceback:
            print(f"--- {run.instance} ({run.status}) ---\n{run.traceback.rstrip()}")
        elif run.error:
            print(f"--- {run.instance} ({run.status}) ---\n{run.error}")
        else:
            print(f"{run.instance} has no error (status {run.status!r}, answer {run.answer!r}).")

    # ---- files
    def save(self, path: str | os.PathLike[str] | None = None, *, merge: bool = True) -> Path:
        """Write the results to a tab-separated file and return its path.

        Args:
            path: where to write. Default: ``results/<problem>.tsv`` in the repository.
            merge: if the file already exists, keep its rows for instances that are not
                in these results (so re-running a few instances does not erase the rest).
                Pass ``merge=False`` to overwrite the file completely.

        Skipped runs (never started) are not written, so they never replace real results.
        """
        if path is None:
            if not self.problem:
                raise ValueError(
                    "Don't know where to save: pass a path, e.g. results.save('my_results.tsv'), "
                    "or run the experiment with problem='none' / 'some' / 'many' / 'few' / 'alternate'."
                )
            path = _results_dir() / f"{self.problem}.tsv"
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)

        rows = {r.instance: r for r in self.runs if r.status != "skipped"}
        kept = 0
        if merge and path.exists():
            for old in Results.load(path).runs:
                if old.instance not in rows:
                    rows[old.instance] = old
                    kept += 1

        with path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f, delimiter="\t", lineterminator="\n")
            writer.writerow(_TSV_FIELDS)
            for r in rows.values():
                writer.writerow(
                    [
                        r.instance,
                        r.n,
                        r.m,
                        r.status,
                        "" if r.answer is None else r.answer,
                        "" if r.seconds is None else f"{r.seconds:.6f}",
                        (r.error or "").replace("\t", " ").replace("\n", " "),
                    ]
                )
        note = f" (kept {kept} earlier results for other instances)" if kept else ""
        written = len(rows) - kept
        print(f"Saved {written} result{'s' * (written != 1)} to {_pretty_path(path)}{note}")
        return path

    @classmethod
    def load(cls, path: str | os.PathLike[str]) -> Results:
        """Read results written by :meth:`save`."""
        path = Path(path)
        if not path.is_file():
            raise FileNotFoundError(f"No results file at {path}.")
        runs = []
        with path.open(encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f, delimiter="\t")
            missing = set(_TSV_FIELDS) - set(reader.fieldnames or [])
            if missing:
                raise ValueError(
                    f"{path.name} is not a results file (missing columns: {', '.join(sorted(missing))})."
                )
            for row in reader:
                answer: int | str | None = row["answer"] or None
                if isinstance(answer, str) and answer.lstrip("-").isdigit():
                    answer = int(answer)
                status = row["status"]
                if status not in _SYMBOL:
                    raise ValueError(
                        f"{path.name}: unknown status {status!r} for {row['instance']}."
                    )
                runs.append(
                    RunResult(
                        instance=row["instance"],
                        n=int(row["n"]),
                        m=int(row["m"]),
                        status=status,  # type: ignore[arg-type]
                        answer=answer,
                        seconds=float(row["seconds"]) if row["seconds"] else None,
                        error=row["error"] or None,
                    )
                )
        problem = path.stem if path.stem in PROBLEMS else None
        return cls(runs, problem=problem)


def _pretty_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(Path.cwd().resolve()))
    except ValueError:
        return str(path)


def _fmt_answer(answer: object) -> str:
    return "-" if answer is None else str(answer)


# --------------------------------------------------------------------------- answers


def _normalize_answer(answer: Any) -> tuple[Any, str | None]:
    """Make answers uniform: True -> "true", 3.0 -> 3, numpy ints -> int.

    Returns ``(answer, error)``; ``error`` is set when the answer is unusable.
    """
    if answer is None:
        return None, (
            "solve() returned None. Did you forget a `return` statement? "
            "Return '?' if you cannot solve this instance."
        )
    if type(answer).__module__ == "numpy" and hasattr(answer, "item"):
        answer = answer.item()  # numpy.int64 / numpy.bool_ -> int / bool
    if isinstance(answer, bool):
        return ("true" if answer else "false"), None
    if isinstance(answer, numbers.Integral):
        return int(answer), None
    if isinstance(answer, float) and math.isfinite(answer) and answer.is_integer():
        return int(answer), None
    if isinstance(answer, str):
        text = answer.strip()
        return (text.lower() if text.lower() in ("true", "false") else text), None
    if isinstance(answer, (float, numbers.Number)):
        return answer, None
    return repr(answer), None


def _check_answer(answer: Any, problem: str | None) -> str | None:
    """A warning if the answer does not look right for the problem, else None."""
    if problem is None or answer in NO_ANSWER:
        return None
    if PROBLEMS[problem] == "bool":
        if answer not in ("true", "false"):
            return f"'{problem}' expects True or False, got {answer!r}"
    elif not isinstance(answer, int) or answer < -1:
        return f"'{problem}' expects a whole number >= -1, got {answer!r}"
    return None


def _check_problem(problem: str | None) -> str | None:
    if problem is None:
        return None
    if not isinstance(problem, str):
        raise TypeError(f"problem must be a string such as 'some', not {problem!r}.")
    key = problem.strip().lower()
    if key not in PROBLEMS:
        close = difflib.get_close_matches(key, PROBLEMS, n=1)
        hint = f" Did you mean {close[0]!r}?" if close else ""
        raise ValueError(
            f"Unknown problem {problem!r}.{hint} Choose one of: {', '.join(sorted(PROBLEMS))}."
        )
    return key


# --------------------------------------------------------------------------- running one instance

# Messages from the child process: (kind, answer, seconds, error, traceback)
_Message = tuple[str, Any, float, str | None, str | None]


def _call_solver(solver: Callable[[Instance], Any], instance: Instance) -> _Message:
    start = time.perf_counter()
    try:
        raw = solver(instance)
    except NotImplementedError as exc:
        seconds = time.perf_counter() - start
        message = str(exc) or "solve() is not implemented yet."
        return ("not_implemented", None, seconds, message, traceback.format_exc())
    except SystemExit as exc:
        seconds = time.perf_counter() - start
        message = f"solve() called exit({exc.code if exc.code is not None else ''}); return an answer instead."
        return ("error", None, seconds, message, traceback.format_exc())
    except Exception as exc:
        seconds = time.perf_counter() - start
        return ("error", None, seconds, _one_line(exc), traceback.format_exc())
    seconds = time.perf_counter() - start
    answer, error = _normalize_answer(raw)
    if error:
        return ("error", None, seconds, error, None)
    return ("ok", answer, seconds, None, None)


def _one_line(exc: BaseException) -> str:
    text = str(exc).strip().splitlines()
    return f"{type(exc).__name__}: {text[0]}" if text else type(exc).__name__


def _child_main(conn: Any, solver: Callable[[Instance], Any], instance: Instance) -> None:
    """Entry point of the worker process: run the solver once and send the result back."""
    try:
        message = _call_solver(solver, instance)
    except KeyboardInterrupt:  # Ctrl+C: the parent handles it, stay quiet here
        return
    try:
        conn.send(message)
    except Exception as exc:  # e.g. an answer that cannot be pickled
        conn.send(
            ("error", None, message[2], f"Could not send the answer back: {_one_line(exc)}", None)
        )
    finally:
        conn.close()


def _mp_context() -> mp.context.BaseContext:
    # "fork" is fast and lets lambdas / notebook functions work. It is only safe on Linux.
    if sys.platform.startswith("linux") and "fork" in mp.get_all_start_methods():
        return mp.get_context("fork")
    return mp.get_context("spawn")


_SPAWN_HELP = (
    "On Windows and macOS each instance runs in a fresh Python process, which must be able to "
    "import your solver. Please:\n"
    "  1. define your solver with `def solve(instance): ...` at the top level of a .py file\n"
    "     (not inside another function, not a lambda, not in a notebook cell), and\n"
    '  2. start the experiment under `if __name__ == "__main__":`.\n'
    "Or pass isolate=False to run without a separate process (then the timeout is not enforced)."
)


def _run_isolated(
    ctx: mp.context.BaseContext,
    solver: Callable[[Instance], Any],
    instance: Instance,
    timeout: float | None,
    on_tick: Callable[[float], None],
) -> tuple[_Message | None, int | None]:
    """Run in a child process. Returns (message, exit code); message is None on timeout/crash."""
    receiver, sender = ctx.Pipe(duplex=False)
    proc = ctx.Process(
        target=_child_main, args=(sender, solver, instance), name=f"solve-{instance.name}"
    )
    try:
        with warnings.catch_warnings():
            # Python 3.12+ warns about fork() in a process with threads (tqdm has one); harmless here.
            warnings.filterwarnings("ignore", category=DeprecationWarning, message=".*fork.*")
            proc.start()
    except RuntimeError as exc:
        if "bootstrapping phase" in str(exc):
            raise RuntimeError(_SPAWN_HELP) from None
        raise
    sender.close()  # the parent only reads; this also makes recv() raise EOFError if the child dies
    try:
        start = time.perf_counter()
        while True:
            elapsed = time.perf_counter() - start
            if timeout is not None and elapsed >= timeout:
                return None, None  # timeout
            wait = 1.0 if timeout is None else min(1.0, timeout - elapsed)
            if receiver.poll(wait):
                try:
                    return receiver.recv(), None
                except (EOFError, OSError):
                    proc.join(5)
                    return None, proc.exitcode if proc.exitcode is not None else -1
            on_tick(time.perf_counter() - start)
    finally:
        receiver.close()
        if proc.is_alive():
            proc.terminate()
            proc.join(2)
            if proc.is_alive():
                proc.kill()
                proc.join()
        else:
            proc.join()
        with contextlib.suppress(Exception):
            proc.close()


# --------------------------------------------------------------------------- the experiment


def _collect_instances(instances: Any) -> list[Instance]:
    if isinstance(instances, Instance):
        return [instances]
    if instances is None or (isinstance(instances, str) and instances.strip().lower() == "all"):
        return load_instances()
    if isinstance(instances, (str, os.PathLike)):
        return load_instances(os.fspath(instances))
    if isinstance(instances, Results):
        return instances.instances()
    try:
        items = list(instances)
    except TypeError:
        raise TypeError(
            "instances must be a list of instances (from load_instances), an instance name, "
            f"a pattern like 'wall-*', or 'all' — not {type(instances).__name__}."
        ) from None
    out: list[Instance] = []
    for item in items:
        if isinstance(item, Instance):
            out.append(item)
        elif isinstance(item, (str, os.PathLike)):
            out.extend(load_instances(os.fspath(item), progress=False))
        else:
            raise TypeError(f"Expected an Instance or an instance name in the list, got {item!r}.")
    if not out:
        raise ValueError("The list of instances is empty, so there is nothing to run.")
    names = [i.name for i in out]
    duplicates = sorted({n for n in names if names.count(n) > 1})
    if duplicates:
        raise ValueError(f"These instances appear more than once: {', '.join(duplicates)}.")
    return out


def _check_solver(solver: Any) -> str:
    if not callable(solver):
        hint = ""
        if solver is None or isinstance(solver, (int, str, bool)):
            hint = " Did you write solve() with brackets? Pass the function itself: run_experiment(solve, ...)."
        raise TypeError(f"The first argument must be your solver function, got {solver!r}.{hint}")
    name = (
        getattr(solver, "__qualname__", None) or getattr(solver, "__name__", None) or repr(solver)
    )
    try:
        signature = inspect.signature(solver)
    except (TypeError, ValueError):
        return name
    try:
        signature.bind(object())
    except TypeError:
        raise TypeError(
            f"Your solver {name}{signature} must accept exactly one argument, the instance: "
            "def solve(instance): ..."
        ) from None
    return name


def run_experiment(
    solver: Callable[[Instance], Any],
    instances: Iterable[Instance] | Instance | str = "all",
    *,
    problem: str | None = None,
    timeout: float | str | None = DEFAULT_TIMEOUT,
    verbose: bool = True,
    isolate: bool = True,
) -> Results:
    """Run ``solver`` on every instance and collect the answers and running times.

    Args:
        solver: your function. It gets one :class:`Instance` and returns the answer:
            a whole number, ``True``/``False``, or ``"?"`` if it cannot solve the instance
            (``"?!"`` if the problem is hard for this instance).
        instances: what to run on. A list from :func:`load_instances`, a single instance,
            a name or pattern such as ``"wall-*"``, or ``"all"`` (the default).
        problem: ``"none"``, ``"some"``, ``"many"``, ``"few"`` or ``"alternate"``. Optional;
            it lets the runner check that answers have the right type, and names the
            file written by ``results.save()``.
        timeout: time limit per instance. Seconds (``60``) or text (``"90s"``, ``"20m"``,
            ``"1h"``); ``None`` for no limit. Default: 20 minutes.
        verbose: print one line per finished instance (the progress bar is always shown).
        isolate: run each instance in a separate process (default). This is what makes the
            timeout work and protects against crashes. Use ``isolate=False`` to debug with
            breakpoints or ``pdb``; the timeout is then *not* enforced.

    Returns:
        A :class:`Results` object. Press Ctrl+C to stop early: you still get the results
        of everything that finished.

    Example::

        results = run_experiment(solve, load_instances("wall-*"), problem="some", timeout="5m")
        results.summary()
    """
    solver_name = _check_solver(solver)
    problem = _check_problem(problem)
    timeout_s = parse_duration(timeout)
    todo = _collect_instances(instances)

    ctx = _mp_context() if isolate else None
    if ctx is not None and ctx.get_start_method() != "fork":
        try:
            pickle.dumps(solver)
        except Exception:
            raise TypeError(
                f"Your solver {solver_name!r} cannot be sent to a worker process.\n{_SPAWN_HELP}"
            ) from None

    limit_text = "not enforced (isolate=False)" if not isolate else format_duration(timeout_s)
    header = (
        f"Running {solver_name}"
        + (f" for problem '{problem}'" if problem else "")
        + f" on {len(todo)} instance{'s' * (len(todo) != 1)} · timeout {limit_text}"
        + f" · started {datetime.now():%H:%M:%S}"
    )
    print(header, flush=True)

    runs: list[RunResult] = []
    counts = {"ok": 0, "timeout": 0, "error": 0, "crashed": 0}
    stop_reason: str | None = None

    bar = tqdm(total=len(todo), unit="inst", dynamic_ncols=True, smoothing=0.1)

    def log(text: str) -> None:
        if verbose:
            bar.write(f"[{datetime.now():%H:%M:%S}] {text}")

    def show_running(inst: Instance, elapsed: float | None = None) -> None:
        running = f"{inst.name} (n={inst.n}, m={inst.m})"
        if elapsed is not None and elapsed >= 2:
            running += f" running {format_duration(elapsed)}"
        bar.set_description_str(running, refresh=False)
        bar.set_postfix_str(" ".join(f"{k}={v}" for k, v in counts.items() if v or k == "ok"))

    try:
        for index, inst in enumerate(todo):
            show_running(inst)
            exit_code = None
            if ctx is not None:
                message, exit_code = _run_isolated(
                    ctx, solver, inst, timeout_s, lambda t, inst=inst: show_running(inst, t)
                )
            else:
                message = _call_solver(solver, inst.copy())

            if message is None and exit_code is None:
                run = RunResult(
                    inst.name,
                    inst.n,
                    inst.m,
                    "timeout",
                    seconds=timeout_s,
                    error=f"timed out after {format_duration(timeout_s)}",
                )
                log(f"⏱ {inst.name}  timed out after {format_duration(timeout_s)}")
            elif message is None:
                run = RunResult(
                    inst.name,
                    inst.n,
                    inst.m,
                    "crashed",
                    error=f"the worker process died without an answer (exit code {exit_code}); "
                    "out of memory, or the solver called exit()?",
                )
                log(f"✗ {inst.name}  crashed (exit code {exit_code})")
            else:
                kind, answer, seconds, error, tb = message
                if kind == "ok":
                    warning = _check_answer(answer, problem)
                    run = RunResult(
                        inst.name, inst.n, inst.m, "ok", answer, seconds, warning=warning
                    )
                    log(
                        f"✓ {inst.name}  {format_duration(seconds)}  answer={answer}"
                        + (f"  ⚠ {warning}" if warning else "")
                    )
                else:
                    run = RunResult(inst.name, inst.n, inst.m, "error", None, seconds, error, tb)
                    log(f"✗ {inst.name}  {error}")
                    if kind == "not_implemented":
                        stop_reason = (
                            f"Stopped: {solver_name} is not implemented yet ({error})\n"
                            "Write your algorithm in solve() and run again."
                        )

            runs.append(run)
            counts[run.status] = counts.get(run.status, 0) + 1
            bar.update(1)
            if stop_reason:
                runs.extend(_skipped(todo[index + 1 :], "not run: the solver is not implemented"))
                break
    except KeyboardInterrupt:
        done = {r.instance for r in runs}
        runs.extend(
            _skipped([i for i in todo if i.name not in done], "not run: stopped with Ctrl+C")
        )
        stop_reason = f"Stopped with Ctrl+C after {len(done)} of {len(todo)} instances."
    finally:
        bar.set_description_str("done" if not stop_reason else "stopped", refresh=False)
        bar.set_postfix_str(" ".join(f"{k}={v}" for k, v in counts.items() if v or k == "ok"))
        bar.close()

    results = Results(
        runs,
        problem=problem,
        solver=solver_name,
        timeout=timeout_s,
        instances={i.name: i for i in todo},
    )
    if stop_reason:
        print(stop_reason)
    print(results._totals_line())
    if results.errors:
        print("Use results.show_error('<name>') to see the full error of a failed instance.")
    return results


def _skipped(instances: Iterable[Instance], reason: str) -> list[RunResult]:
    return [RunResult(i.name, i.n, i.m, "skipped", error=reason) for i in instances]
