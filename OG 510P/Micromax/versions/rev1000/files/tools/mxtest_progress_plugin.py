"""Tiny pytest plugin used by tools/mxtest.py for interrupt-resume evidence.

The plugin writes one JSON line after a selected test reaches a resume-safe
terminal state.  It is intentionally small and has no project imports so pytest
children can load it with ``-p tools.mxtest_progress_plugin`` from the source
root.
"""
from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any

_PROGRESS_PATH: Path | None = None


def pytest_addoption(parser: Any) -> None:
    group = parser.getgroup("mxtest")
    group.addoption(
        "--mxtest-progress-jsonl",
        action="store",
        default="",
        help="internal: write JSONL records for mxtest per-test checkpoints",
    )


def pytest_configure(config: Any) -> None:
    global _PROGRESS_PATH
    raw = str(config.getoption("--mxtest-progress-jsonl") or "")
    _PROGRESS_PATH = Path(raw) if raw else None


def _append_record(path: Path, record: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, sort_keys=True) + "\n")
        handle.flush()
        os.fsync(handle.fileno())


def pytest_runtest_logreport(report: Any) -> None:
    path = _PROGRESS_PATH
    if path is None:
        return

    # A normal passing test is only resume-safe after teardown has completed;
    # recording at call-time would miss teardown failures.  Setup/call skips are
    # already terminal for ordinary skip/xfail outcomes, so they are also safe.
    terminal_ok = (report.when == "teardown" and report.passed) or (
        report.when in {"setup", "call"} and report.skipped
    )
    if not terminal_ok:
        return
    _append_record(
        path,
        {
            "nodeid": str(report.nodeid),
            "outcome": str(report.outcome),
            "when": str(report.when),
            "duration": float(getattr(report, "duration", 0.0) or 0.0),
            "time": round(time.time(), 6),
        },
    )
