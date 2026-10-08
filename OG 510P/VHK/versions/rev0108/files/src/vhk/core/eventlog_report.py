from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable


@dataclass
class StepAggregate:
    """Aggregated per-step performance/health stats from an event log."""

    step_id: str
    step_type: str
    count: int = 0
    ok_count: int = 0
    fail_count: int = 0
    retry_count: int = 0
    total_duration_ms: int = 0
    max_duration_ms: int = 0
    min_duration_ms: int | None = None

    def add_attempt(self, *, ok: bool, duration_ms: int) -> None:
        self.count += 1
        if ok:
            self.ok_count += 1
        else:
            self.fail_count += 1
        self.total_duration_ms += int(duration_ms)
        self.max_duration_ms = max(self.max_duration_ms, int(duration_ms))
        if self.min_duration_ms is None:
            self.min_duration_ms = int(duration_ms)
        else:
            self.min_duration_ms = min(self.min_duration_ms, int(duration_ms))

    @property
    def avg_duration_ms(self) -> float:
        if self.count <= 0:
            return 0.0
        return self.total_duration_ms / float(self.count)

    def to_dict(self) -> dict[str, Any]:
        out = asdict(self)
        out["avg_duration_ms"] = round(self.avg_duration_ms, 3)
        return out


@dataclass
class WaitAggregate:
    """Aggregated per-wait-kind stats from an event log."""

    kind: str
    count: int = 0
    ok_count: int = 0
    fail_count: int = 0
    total_duration_ms: int = 0
    max_duration_ms: int = 0
    min_duration_ms: int | None = None

    def add(self, *, ok: bool | None, duration_ms: int) -> None:
        self.count += 1
        if ok is True:
            self.ok_count += 1
        elif ok is False:
            self.fail_count += 1
        self.total_duration_ms += int(duration_ms)
        self.max_duration_ms = max(self.max_duration_ms, int(duration_ms))
        if self.min_duration_ms is None:
            self.min_duration_ms = int(duration_ms)
        else:
            self.min_duration_ms = min(self.min_duration_ms, int(duration_ms))

    @property
    def avg_duration_ms(self) -> float:
        if self.count <= 0:
            return 0.0
        return self.total_duration_ms / float(self.count)

    def to_dict(self) -> dict[str, Any]:
        out = asdict(self)
        out["avg_duration_ms"] = round(self.avg_duration_ms, 3)
        return out


def read_event_log(path: Path) -> list[dict[str, Any]]:
    """Read a JSONL event log written by :class:`vhk.core.events.EventLogger`."""

    events: list[dict[str, Any]] = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line:
            continue
        events.append(json.loads(line))
    return events


def find_latest_event_log(log_dir: Path) -> Path | None:
    """Return the most recently modified ``run_*.jsonl`` log in ``log_dir``."""

    if not log_dir.exists():
        return None
    candidates = list(log_dir.glob("run_*.jsonl"))
    if not candidates:
        return None
    candidates.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return candidates[0]


def _first(events: Iterable[dict[str, Any]], event_type: str) -> dict[str, Any] | None:
    for ev in events:
        if ev.get("type") == event_type:
            return ev
    return None


def _last(events: Iterable[dict[str, Any]], event_type: str) -> dict[str, Any] | None:
    found = None
    for ev in events:
        if ev.get("type") == event_type:
            found = ev
    return found


def summarize_event_log(events: list[dict[str, Any]]) -> dict[str, Any]:
    """Summarize a VHK event log into aggregated step + wait stats."""

    run_start = _first(events, "run_start")
    run_end = _last(events, "run_end")
    first_ts = events[0].get("ts") if events else None
    last_ts = events[-1].get("ts") if events else None

    started_ts = (run_start or {}).get("ts", first_ts)
    ended_ts = (run_end or {}).get("ts", last_ts)
    duration_s = None
    try:
        if started_ts is not None and ended_ts is not None:
            duration_s = float(ended_ts) - float(started_ts)
    except Exception:
        duration_s = None

    step_aggs: dict[tuple[str, str], StepAggregate] = {}
    errors: list[dict[str, Any]] = []
    wait_counts: dict[str, int] = {}

    # Pair wait_start/wait_end by kind (best-effort). These events are emitted
    # within a single step attempt; treating them as LIFO stacks is good enough
    # and keeps us robust to occasional missing start/end records.
    wait_stacks: dict[str, list[float]] = {}
    wait_aggs: dict[str, WaitAggregate] = {}

    for ev in events:
        et = ev.get("type")
        if et == "step_end":
            step_id = str(ev.get("step_id", "?"))
            step_type = str(ev.get("step_type", "?"))
            key = (step_id, step_type)
            agg = step_aggs.get(key)
            if agg is None:
                agg = StepAggregate(step_id=step_id, step_type=step_type)
                step_aggs[key] = agg
            ok = bool(ev.get("ok", False))
            duration_ms = int(ev.get("duration_ms") or 0)
            agg.add_attempt(ok=ok, duration_ms=duration_ms)
            if not ok:
                errors.append(
                    {
                        "step_id": step_id,
                        "step_type": step_type,
                        "error": ev.get("error"),
                        "error_type": ev.get("error_type"),
                        "screenshot": ev.get("screenshot"),
                        "error_context": ev.get("error_context"),
                        "continued": bool(ev.get("continued", False)),
                    }
                )
        elif et == "step_retry":
            step_id = str(ev.get("step_id", "?"))
            step_type = str(ev.get("step_type", "?"))
            key = (step_id, step_type)
            agg = step_aggs.get(key)
            if agg is None:
                agg = StepAggregate(step_id=step_id, step_type=step_type)
                step_aggs[key] = agg
            agg.retry_count += 1
        elif et == "wait_attempt":
            kind = str(ev.get("kind", "unknown"))
            wait_counts[kind] = wait_counts.get(kind, 0) + 1
        elif et == "wait_start":
            kind = str(ev.get("kind", "unknown"))
            ts = ev.get("ts")
            try:
                ts_f = float(ts)
            except Exception:
                ts_f = None
            if ts_f is not None:
                wait_stacks.setdefault(kind, []).append(ts_f)
        elif et == "wait_end":
            kind = str(ev.get("kind", "unknown"))
            ts = ev.get("ts")
            try:
                end_f = float(ts)
            except Exception:
                end_f = None
            start_f = None
            stack = wait_stacks.get(kind) or []
            if stack:
                start_f = stack.pop()
            if start_f is None or end_f is None:
                continue
            dur_ms = int(max(0.0, (end_f - start_f) * 1000.0))
            ok = ev.get("ok")
            agg = wait_aggs.get(kind)
            if agg is None:
                agg = WaitAggregate(kind=kind)
                wait_aggs[kind] = agg
            agg.add(ok=ok if isinstance(ok, bool) else None, duration_ms=dur_ms)

    steps_sorted = sorted(step_aggs.values(), key=lambda a: a.total_duration_ms, reverse=True)
    wait_sorted = sorted(wait_counts.items(), key=lambda kv: kv[1], reverse=True)
    wait_dur_sorted = sorted(wait_aggs.values(), key=lambda a: a.total_duration_ms, reverse=True)
    total_wait_ms = sum(a.total_duration_ms for a in wait_aggs.values())

    return {
        "run": {
            "run_id": (run_start or {}).get("run_id"),
            "project": (run_start or {}).get("project"),
            "macro": (run_start or {}).get("macro"),
            "ok": (run_end or {}).get("ok"),
            "error": (run_end or {}).get("error"),
            "started_ts": started_ts,
            "ended_ts": ended_ts,
            "duration_s": round(duration_s, 3) if duration_s is not None else None,
        },
        "counts": {
            "events": len(events),
            "unique_steps": len(step_aggs),
            "wait_events": sum(wait_counts.values()),
            "error_steps": len(errors),
            "wait_total_s": round(total_wait_ms / 1000.0, 3),
        },
        "steps": [s.to_dict() for s in steps_sorted],
        "waits": [{"kind": k, "count": c} for k, c in wait_sorted],
        "wait_durations": [w.to_dict() for w in wait_dur_sorted],
        "errors": errors,
    }
