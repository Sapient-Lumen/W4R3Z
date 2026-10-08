#!/usr/bin/env python3
"""mxtimely: bounded repo evidence lane for constrained cloudtainers.

The full Micromax test suite is intentionally resumable rather than short.  This
wrapper keeps everyday handoff checks usable inside short tooltimer windows:
children receive outer timeouts, noisy child output is captured by default, and
optional mxtest slices count as success only when they leave a clean partial
checkpoint with no failed/timed-out test evidence.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

from mxtoolrun import format_duration, isolated_python_env, run_captured, tail_text  # noqa: E402

DEFAULT_MANIFEST = ".artifacts/mxtimely-mxtest.json"
DEFAULT_SUMMARY = ".artifacts/mxtimely-summary.json"
DEFAULT_CHUNKS = 32
DEFAULT_MAX_RUNTIME_SECONDS = 14.0
DEFAULT_MAX_NEW_TESTS = 12
DEFAULT_MAX_NEW_FILES = 1
DEFAULT_TEST_BATCH_SIZE = 6
DEFAULT_FILE_TIMEOUT_SECONDS = 20

_ALLOWED_PARTIAL_REASONS = {
    "max-runtime-seconds-reached",
    "max-new-tests-reached",
    "max-new-files-reached",
    "max-new-chunks-reached",
    "max-new-budget-reached",
    "previous-passed-files-cover-chunk",
}


@dataclass(frozen=True)
class TimelyStep:
    """One bounded child command in the timely lane."""

    name: str
    argv: list[str]
    timeout_seconds: int
    partial_manifest: str = ""


@dataclass(frozen=True)
class TimelyResult:
    """Result row emitted by the timely lane."""

    name: str
    returncode: int
    elapsed_seconds: float
    ok: bool
    timed_out: bool = False
    note: str = ""

    def as_json(self) -> dict[str, object]:
        return {
            "name": self.name,
            "returncode": self.returncode,
            "elapsed_seconds": round(float(self.elapsed_seconds), 3),
            "ok": bool(self.ok),
            "timed_out": bool(self.timed_out),
            "note": self.note,
        }


def bounded_env() -> dict[str, str]:
    """Return the deterministic environment shared by handoff tool children."""

    return isolated_python_env(ROOT)


def scaled_timeout(seconds: int | float, *, scale: float) -> int:
    """Return a positive integer timeout after applying a user scale."""

    return max(1, int(round(float(seconds) * max(0.1, float(scale)))))


def build_mxtest_command(
    *,
    manifest: str,
    chunks: int = DEFAULT_CHUNKS,
    max_runtime_seconds: float = DEFAULT_MAX_RUNTIME_SECONDS,
    max_new_tests: int = DEFAULT_MAX_NEW_TESTS,
    max_new_files: int = DEFAULT_MAX_NEW_FILES,
    test_batch_size: int = DEFAULT_TEST_BATCH_SIZE,
    file_timeout: int = DEFAULT_FILE_TIMEOUT_SECONDS,
) -> list[str]:
    """Return the bounded resumable mxtest command used by mxtimely."""

    return [
        sys.executable,
        "tools/mxtest.py",
        "--run-chunks",
        str(max(1, int(chunks))),
        "--strategy",
        "segment",
        "--isolate-files",
        "--resume",
        "--checkpoint-tests",
        "--max-new-tests",
        str(max(0, int(max_new_tests))),
        "--max-new-files",
        str(max(0, int(max_new_files))),
        "--test-batch-size",
        str(max(0, int(test_batch_size))),
        "--file-timeout",
        str(max(0, int(file_timeout))),
        "--max-runtime-seconds",
        str(max(0.0, float(max_runtime_seconds))),
        "--json",
        str(manifest),
        "--durations",
        "0",
    ]


def build_steps(
    *,
    manifest: str = DEFAULT_MANIFEST,
    timeout_scale: float = 1.0,
    include_tests: bool = False,
    include_doctor: bool = True,
    chunks: int = DEFAULT_CHUNKS,
    max_runtime_seconds: float = DEFAULT_MAX_RUNTIME_SECONDS,
    max_new_tests: int = DEFAULT_MAX_NEW_TESTS,
    max_new_files: int = DEFAULT_MAX_NEW_FILES,
    test_batch_size: int = DEFAULT_TEST_BATCH_SIZE,
    file_timeout: int = DEFAULT_FILE_TIMEOUT_SECONDS,
) -> list[TimelyStep]:
    """Return the default short-window tool sequence."""

    scale = max(0.1, float(timeout_scale))
    steps = [
        TimelyStep("context", [sys.executable, "tools/mxcontext.py", "--check"], scaled_timeout(15, scale=scale)),
        TimelyStep("audit", [sys.executable, "tools/mxaudit.py", "--check"], scaled_timeout(18, scale=scale)),
        TimelyStep("lint", [sys.executable, "tools/mxlint.py"], scaled_timeout(15, scale=scale)),
        TimelyStep("portable", [sys.executable, "tools/mxportable.py", "--quiet"], scaled_timeout(15, scale=scale)),
    ]
    if include_doctor:
        steps.append(TimelyStep("doctor", [sys.executable, "tools/mxdoctor.py"], scaled_timeout(22, scale=scale)))
    if include_tests:
        outer = 8 + int(max(0.0, float(max_runtime_seconds))) + int(max(0, int(max_new_files))) * max(1, int(file_timeout))
        steps.append(
            TimelyStep(
                "mxtest-slice",
                build_mxtest_command(
                    manifest=manifest,
                    chunks=chunks,
                    max_runtime_seconds=max_runtime_seconds,
                    max_new_tests=max_new_tests,
                    max_new_files=max_new_files,
                    test_batch_size=test_batch_size,
                    file_timeout=file_timeout,
                ),
                scaled_timeout(min(30, outer), scale=scale),
                partial_manifest=manifest,
            )
        )
    return steps


def _count_status(payload: dict[str, Any], *names: str) -> int:
    total = 0
    for field in ("chunk_status_counts", "test_status_counts"):
        counts = payload.get(field)
        if not isinstance(counts, dict):
            continue
        for name in names:
            try:
                total += int(counts.get(name, 0) or 0)
            except (TypeError, ValueError):
                continue
    return total


def _chunk_skip_reasons(payload: dict[str, Any]) -> list[str]:
    rows = payload.get("chunk_results")
    if not isinstance(rows, list):
        return []
    reasons: list[str] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        reason = row.get("skip_reason")
        if isinstance(reason, str) and reason and not bool(row.get("resumed")):
            reasons.extend(part for part in reason.split("+") if part)
    return reasons


def mxtest_budgeted_partial_ok(manifest: str | Path) -> tuple[bool, str]:
    """Return whether a nonzero mxtest result is an acceptable clean checkpoint."""

    path = Path(manifest)
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return False, f"missing or unreadable mxtest manifest: {exc}"
    if not isinstance(payload, dict):
        return False, "mxtest manifest is not a JSON object"
    if payload.get("status") != "partial" or payload.get("complete") is True:
        return False, f"mxtest status is {payload.get('status')!r}, not a clean partial checkpoint"
    bad = _count_status(payload, "failed", "timed_out", "running")
    if bad:
        return False, f"mxtest manifest includes {bad} failed/timed-out/running row(s)"
    test_partial = 0
    counts = payload.get("test_status_counts")
    if isinstance(counts, dict):
        try:
            test_partial = int(counts.get("partial", 0) or 0)
        except (TypeError, ValueError):
            test_partial = 0
    if test_partial:
        return False, f"mxtest manifest includes {test_partial} partial test row(s)"
    progress = _count_status(payload, "passed")
    if progress <= 0:
        return False, "mxtest partial checkpoint contains no passed progress"
    unexpected = [reason for reason in _chunk_skip_reasons(payload) if reason not in _ALLOWED_PARTIAL_REASONS]
    if unexpected:
        return False, "mxtest partial checkpoint has unexpected skip reason(s): " + ", ".join(sorted(set(unexpected)))
    return True, "clean budget-limited mxtest checkpoint"


def _compact_success_note(step: TimelyStep, output: str, *, fallback: str = "") -> str:
    lines = [line.strip() for line in output.splitlines() if line.strip()]
    if step.name == "portable":
        for line in reversed(lines):
            if "portability cases passed" in line:
                return line
    if step.name == "context":
        for line in lines:
            if line.startswith("Rev:"):
                return line
    if step.name == "audit":
        for line in lines:
            if "timely runway present=" in line:
                return line
    if step.name == "lint" and lines:
        return lines[-1]
    if step.name == "doctor":
        for line in reversed(lines):
            if line.startswith("mxdoctor:"):
                return line
        return "doctor preflight passed"
    return fallback or (lines[-1] if lines else "ok")


def _tail(text: str, *, max_lines: int = 80) -> str:
    return tail_text(text, max_lines=max_lines)


def result_for_returncode(
    step: TimelyStep,
    returncode: int,
    elapsed: float,
    *,
    timed_out: bool = False,
    output: str = "",
) -> TimelyResult:
    """Translate a child exit status into timely success/failure semantics."""

    if timed_out:
        return TimelyResult(step.name, int(returncode), elapsed, False, timed_out=True, note="outer timeout")
    if int(returncode) == 0:
        return TimelyResult(step.name, int(returncode), elapsed, True, note=_compact_success_note(step, output))
    if step.partial_manifest:
        ok, note = mxtest_budgeted_partial_ok(step.partial_manifest)
        return TimelyResult(step.name, int(returncode), elapsed, ok, note=note)
    return TimelyResult(step.name, int(returncode), elapsed, False)


def run_step(step: TimelyStep, *, verbose_children: bool = False) -> TimelyResult:
    """Run one timely step with an outer timeout and low-frequency heartbeat."""

    print(f"mxtimely: {step.name} (timeout {step.timeout_seconds}s)")
    if verbose_children:
        print("$ " + " ".join(step.argv))
    sys.stdout.flush()
    command = run_captured(
        step.argv,
        cwd=ROOT,
        env=bounded_env(),
        timeout_seconds=float(step.timeout_seconds),
        label=step.name,
        heartbeat_seconds=min(10.0, max(0.0, float(step.timeout_seconds) / 2.0)),
        heartbeat_prefix="mxtimely",
    )
    result = result_for_returncode(
        step,
        command.returncode,
        command.elapsed_seconds,
        timed_out=command.timed_out,
        output=command.output,
    )

    if verbose_children and command.output:
        print(command.output.rstrip())
    elif result.ok:
        note = f" — {result.note}" if result.note else ""
        print(f"  ok in {format_duration(result.elapsed_seconds)}{note}")
    else:
        print(f"  FAIL rc={result.returncode} in {format_duration(result.elapsed_seconds)}")
        if command.output:
            print(_tail(command.output))
    sys.stdout.flush()
    return result


def _planned_step_names(steps: list[TimelyStep] | list[str] | None, results: list[TimelyResult]) -> list[str]:
    """Return the planned step names for summary honesty."""

    if steps is None:
        return [result.name for result in results]
    names: list[str] = []
    for step in steps:
        if isinstance(step, TimelyStep):
            names.append(step.name)
        else:
            names.append(str(step))
    return names


def _summary_status(*, complete: bool, results: list[TimelyResult]) -> str:
    """Return a truthful compact status for complete, failed, and partial runs."""

    if any(not result.ok for result in results):
        return "failed"
    if not complete:
        return "partial"
    return "passed"


def write_summary(
    path: str | Path,
    results: list[TimelyResult],
    *,
    planned_steps: list[TimelyStep] | list[str] | None = None,
) -> None:
    """Write a compact JSON summary for the timely lane.

    Incremental writes are intentionally marked partial until every planned step
    has produced a result.  An outer cloudtainer/tooltimer stop must leave fresh
    evidence without making a completed-lane success claim.
    """

    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    total_elapsed = sum(float(result.elapsed_seconds) for result in results)
    slowest = max(results, key=lambda result: float(result.elapsed_seconds), default=None)
    planned_names = _planned_step_names(planned_steps, results)
    result_names = [result.name for result in results]
    complete = bool(len(result_names) == len(planned_names) and result_names == planned_names)
    status = _summary_status(complete=complete, results=results)
    payload = {
        "schema": "micromax.mxtimely.summary.v3",
        "ok": bool(status == "passed"),
        "status": status,
        "complete": bool(complete),
        "completed_steps": len(results),
        "planned_step_count": len(planned_names),
        "planned_steps": planned_names,
        "pending_steps": planned_names[len(results) :] if not complete else [],
        "total_elapsed_seconds": round(total_elapsed, 3),
        "slowest_step": slowest.name if slowest is not None else "",
        "slowest_elapsed_seconds": round(float(slowest.elapsed_seconds), 3) if slowest is not None else 0.0,
        "results": [result.as_json() for result in results],
    }
    target.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def print_summary(results: list[TimelyResult], *, summary_path: str | None = None) -> None:
    """Emit a compact human summary after all bounded children finish."""

    print()
    print("mxtimely summary")
    total_elapsed = sum(float(result.elapsed_seconds) for result in results)
    for result in results:
        status = "ok" if result.ok else "FAIL"
        note = f" ({result.note})" if result.note else ""
        print(f"  {status:4s} {result.name:13s} rc={result.returncode} elapsed={format_duration(result.elapsed_seconds)}{note}")
    print(f"  total elapsed: {format_duration(total_elapsed)}")
    if summary_path:
        print(f"  summary: {summary_path}")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="run bounded Micromax handoff tools")
    parser.add_argument("--manifest", default=DEFAULT_MANIFEST, help="mxtest slice manifest path")
    parser.add_argument("--summary-json", default=DEFAULT_SUMMARY, help="write mxtimely summary JSON here; empty disables")
    parser.add_argument("--timeout-scale", type=float, default=1.0, help="scale outer child timeouts (default: 1.0)")
    parser.add_argument("--with-tests", action="store_true", help="append a tiny bounded mxtest slice after the handoff tools")
    parser.add_argument("--skip-tests", action="store_true", help="do not run the optional mxtest slice")
    parser.add_argument("--skip-doctor", action="store_true", help="skip the fast doctor preflight")
    parser.add_argument("--verbose-children", action="store_true", help="stream captured child output after each step")
    parser.add_argument("--chunks", type=int, default=DEFAULT_CHUNKS, help="mxtest chunk count")
    parser.add_argument("--max-runtime-seconds", type=float, default=DEFAULT_MAX_RUNTIME_SECONDS, help="mxtest graceful runtime budget")
    parser.add_argument("--max-new-tests", type=int, default=DEFAULT_MAX_NEW_TESTS, help="mxtest new-test budget")
    parser.add_argument("--max-new-files", type=int, default=DEFAULT_MAX_NEW_FILES, help="mxtest new-file budget")
    parser.add_argument("--test-batch-size", type=int, default=DEFAULT_TEST_BATCH_SIZE, help="mxtest per-file node batch size")
    parser.add_argument("--file-timeout", type=int, default=DEFAULT_FILE_TIMEOUT_SECONDS, help="mxtest per-file timeout")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    steps = build_steps(
        manifest=str(args.manifest),
        timeout_scale=float(args.timeout_scale),
        include_tests=bool(args.with_tests) and not bool(args.skip_tests),
        include_doctor=not bool(args.skip_doctor),
        chunks=int(args.chunks),
        max_runtime_seconds=float(args.max_runtime_seconds),
        max_new_tests=int(args.max_new_tests),
        max_new_files=int(args.max_new_files),
        test_batch_size=int(args.test_batch_size),
        file_timeout=int(args.file_timeout),
    )
    results: list[TimelyResult] = []
    summary_path = str(args.summary_json or "")
    for step in steps:
        result = run_step(step, verbose_children=bool(args.verbose_children))
        results.append(result)
        if summary_path:
            # Persist after each bounded child so an outer cloudtainer stop does
            # not leave the previous revision's summary masquerading as fresh
            # evidence for the current revision.
            write_summary(summary_path, results, planned_steps=steps)
        if not result.ok:
            break
    if summary_path:
        write_summary(summary_path, results, planned_steps=steps)
    print_summary(results, summary_path=summary_path or None)
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
