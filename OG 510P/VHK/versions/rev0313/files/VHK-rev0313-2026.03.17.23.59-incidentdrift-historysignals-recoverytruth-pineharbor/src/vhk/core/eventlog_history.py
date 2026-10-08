from __future__ import annotations

"""Utilities for browsing/summarizing a directory of ``run_*.jsonl`` logs."""

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from vhk.core.eventlog_report import read_event_log, summarize_event_log


def list_run_logs(log_dir: Path) -> list[Path]:
    """Return ``run_*.jsonl`` files in ``log_dir``, newest first."""

    if not log_dir.exists():
        return []
    paths = list(log_dir.glob("run_*.jsonl"))
    paths.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return paths


@dataclass
class RunRow:
    path: str
    run_id: str | None
    project: str | None
    macro: str | None
    ok: bool | None
    started_ts: float | None
    ended_ts: float | None
    duration_s: float | None
    retries: int
    wait_attempts: int
    error: str | None

    def to_dict(self) -> dict[str, Any]:
        return {
            "path": self.path,
            "run_id": self.run_id,
            "project": self.project,
            "macro": self.macro,
            "ok": self.ok,
            "started_ts": self.started_ts,
            "ended_ts": self.ended_ts,
            "duration_s": self.duration_s,
            "retries": self.retries,
            "wait_attempts": self.wait_attempts,
            "error": self.error,
        }


def summarize_run_log(path: Path) -> RunRow:
    events = read_event_log(path)
    summary = summarize_event_log(events)

    run = summary.get("run") or {}
    steps = summary.get("steps") or []
    retries = 0
    for s in steps:
        try:
            retries += int(s.get("retry_count") or 0)
        except Exception:
            continue

    def _safe_float(v: Any) -> float | None:
        try:
            if v is None:
                return None
            return float(v)
        except Exception:
            return None

    return RunRow(
        path=str(path),
        run_id=run.get("run_id"),
        project=run.get("project"),
        macro=run.get("macro"),
        ok=run.get("ok"),
        started_ts=_safe_float(run.get("started_ts")),
        ended_ts=_safe_float(run.get("ended_ts")),
        duration_s=_safe_float(run.get("duration_s")),
        retries=retries,
        wait_attempts=int((summary.get("counts") or {}).get("wait_events") or 0),
        error=run.get("error"),
    )


def collect_history(
    log_dir: Path,
    *,
    limit: int = 20,
    status: str = "all",
    macro: str | None = None,
) -> list[RunRow]:
    """Collect a list of recent run summaries from ``log_dir``.

    Parameters
    ----------
    limit:
        Maximum number of rows returned *after filtering*.
    status:
        One of ``all``, ``ok``, ``fail``.
    macro:
        Optional macro name filter (exact match).
    """

    status = str(status or "all").lower()
    if status not in {"all", "ok", "fail"}:
        raise ValueError("status must be one of: all, ok, fail")

    out: list[RunRow] = []
    for p in list_run_logs(log_dir):
        row = summarize_run_log(p)
        if macro and row.macro != macro:
            continue
        if status == "ok" and row.ok is not True:
            continue
        if status == "fail" and row.ok is not False:
            continue
        out.append(row)
        if len(out) >= int(limit):
            break
    return out
