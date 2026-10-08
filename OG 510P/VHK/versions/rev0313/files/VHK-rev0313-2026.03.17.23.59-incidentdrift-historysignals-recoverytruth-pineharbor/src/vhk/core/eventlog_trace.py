from __future__ import annotations

"""Export VHK JSONL event logs to trace viewer formats.

Today we target the de-facto "Chrome Trace Event" JSON format (Catapult).
This can be opened in Chrome's tracing UI and in Perfetto's legacy JSON
viewer.

Why JSON trace?
  - It is a widely supported, simple format.
  - It provides a usable timeline view (steps, waits, retries) without
    needing a custom Studio UI.

The VHK event log is JSONL with timestamps in seconds since epoch.
Trace viewers typically expect microsecond timestamps relative to the start
of the trace; we normalize accordingly.
"""

from dataclasses import dataclass
from typing import Any, Iterable


def _to_us(ts_s: float, base_s: float) -> int:
    # Trace Event Format expects timestamps in microseconds.
    return int(round((ts_s - base_s) * 1_000_000))


def _safe_float(v: Any) -> float | None:
    try:
        if v is None:
            return None
        return float(v)
    except Exception:
        return None


@dataclass
class _ActiveStep:
    macro: str
    step_id: str
    attempt: int
    step_type: str


class TraceBuilder:
    """Build a Chrome Trace Event JSON payload from VHK events."""

    def __init__(self, events: Iterable[dict[str, Any]], *, pid: int = 1) -> None:
        self.events = list(events)
        self.pid = int(pid)
        self._trace_events: list[dict[str, Any]] = []

        # Macro track numbering is stable across runs (but deterministic within a run).
        self._macro_order: dict[str, int] = {}

        # Active step context for events that don't include macro/step_id.
        self._step_stack: list[_ActiveStep] = []

        # Correlate step_start -> step_end.
        self._step_starts: dict[tuple[str, str, int], dict[str, Any]] = {}

        # Correlate wait_start -> wait_end (scoped to the current step).
        self._wait_starts: dict[tuple[str, str, int, str, int], dict[str, Any]] = {}
        self._wait_seq = 0

        # Correlate call_macro_start -> call_macro_end.
        self._call_stack: list[dict[str, Any]] = []

    # --------------------------- track helpers ---------------------------

    def _macro_idx(self, macro: str) -> int:
        if macro not in self._macro_order:
            self._macro_order[macro] = len(self._macro_order)
        return self._macro_order[macro]

    def _tid(self, macro: str, track: str) -> int:
        # Keep tracks visually grouped: steps, waits, attempts.
        base = self._macro_idx(macro)
        if track == "steps":
            return base
        if track == "waits":
            return 100 + base
        if track == "attempts":
            return 200 + base
        if track == "meta":
            return 500 + base
        return 900 + (base % 50)

    def _emit_thread_names(self) -> None:
        # Process name
        self._trace_events.append(
            {
                "name": "process_name",
                "ph": "M",
                "pid": self.pid,
                "tid": 0,
                "args": {"name": "vhk"},
            }
        )

        # Thread names for each macro's tracks.
        for macro, idx in self._macro_order.items():
            for track in ("steps", "waits", "attempts"):
                tid = self._tid(macro, track)
                self._trace_events.append(
                    {
                        "name": "thread_name",
                        "ph": "M",
                        "pid": self.pid,
                        "tid": tid,
                        "args": {"name": f"{macro}:{track}"},
                    }
                )

    # ------------------------------ emitters ----------------------------

    def _complete(self, *, name: str, ts_us: int, dur_us: int, macro: str, track: str, cat: str, args: dict[str, Any]) -> None:
        # 'X' is a complete event.
        self._trace_events.append(
            {
                "name": name,
                "cat": cat,
                "ph": "X",
                "ts": int(ts_us),
                "dur": int(max(0, dur_us)),
                "pid": self.pid,
                "tid": self._tid(macro, track),
                "args": args or {},
            }
        )

    def _instant(self, *, name: str, ts_us: int, macro: str, track: str, cat: str, args: dict[str, Any]) -> None:
        # 'i' is an instant event. 's' defines the scope; 't' == thread.
        self._trace_events.append(
            {
                "name": name,
                "cat": cat,
                "ph": "i",
                "s": "t",
                "ts": int(ts_us),
                "pid": self.pid,
                "tid": self._tid(macro, track),
                "args": args or {},
            }
        )

    # ------------------------------ build -------------------------------

    def build(self) -> dict[str, Any]:
        if not self.events:
            return {"traceEvents": [], "displayTimeUnit": "ms"}

        ts_values = [_safe_float(e.get("ts")) for e in self.events]
        ts_values = [t for t in ts_values if t is not None]
        base_s = min(ts_values) if ts_values else 0.0

        # First pass: discover macros for stable thread naming.
        for e in self.events:
            macro = e.get("macro")
            if isinstance(macro, str) and macro:
                self._macro_idx(macro)
            # call_macro also implies macro names.
            for k in ("parent_macro", "child_macro"):
                v = e.get(k)
                if isinstance(v, str) and v:
                    self._macro_idx(v)

        # Second pass: convert.
        run_start_ts: float | None = None
        run_end_ts: float | None = None
        run_id: str | None = None
        run_macro: str | None = None
        project: str | None = None

        for e in self.events:
            et = str(e.get("type") or "")
            ts_s = _safe_float(e.get("ts"))
            if ts_s is None:
                continue
            ts_us = _to_us(ts_s, base_s)

            # Try to infer macro context for events that omit it.
            macro = e.get("macro")
            if not isinstance(macro, str) or not macro:
                if self._step_stack:
                    macro = self._step_stack[-1].macro
                else:
                    macro = run_macro or "(unknown)"
            macro = str(macro)

            if et == "run_start":
                run_start_ts = ts_s
                run_id = str(e.get("run_id") or "") or run_id
                project = str(e.get("project") or "") or project
                run_macro = str(e.get("macro") or "") or run_macro
                self._instant(name="run_start", ts_us=ts_us, macro=run_macro or macro, track="meta", cat="vhk.run", args={"run_id": run_id, "project": project, "macro": run_macro})
                continue
            if et == "run_end":
                run_end_ts = ts_s
                ok = e.get("ok")
                self._instant(name="run_end", ts_us=ts_us, macro=run_macro or macro, track="meta", cat="vhk.run", args={"ok": ok, "error": e.get("error")})
                continue

            if et == "step_start":
                step_id = str(e.get("step_id") or "")
                attempt = int(e.get("attempt") or 1)
                step_type = str(e.get("step_type") or "step")
                self._step_starts[(macro, step_id, attempt)] = e
                self._step_stack.append(_ActiveStep(macro=macro, step_id=step_id, attempt=attempt, step_type=step_type))
                continue

            if et == "step_end":
                step_id = str(e.get("step_id") or "")
                attempt = int(e.get("attempt") or 1)
                step_type = str(e.get("step_type") or "step")
                ok = bool(e.get("ok"))
                duration_ms = int(e.get("duration_ms") or 0)
                dur_us = max(0, duration_ms) * 1000

                start = self._step_starts.pop((macro, step_id, attempt), None)
                if start is not None:
                    start_s = _safe_float(start.get("ts")) or ts_s
                    start_us = _to_us(start_s, base_s)
                else:
                    # Some synthetic/test logs only record step_end; infer.
                    start_us = ts_us - dur_us

                args: dict[str, Any] = {
                    "macro": macro,
                    "step_id": step_id,
                    "attempt": attempt,
                    "ok": ok,
                }
                if e.get("comment"):
                    args["comment"] = e.get("comment")
                if not ok:
                    if e.get("error"):
                        args["error"] = e.get("error")
                    if e.get("error_type"):
                        args["error_type"] = e.get("error_type")
                    if e.get("screenshot"):
                        args["screenshot"] = e.get("screenshot")
                    if e.get("error_context"):
                        args["error_context"] = e.get("error_context")

                self._complete(
                    name=step_type,
                    ts_us=start_us,
                    dur_us=dur_us,
                    macro=macro,
                    track="steps",
                    cat="vhk.step",
                    args=args,
                )

                # Pop stack if it matches the end event.
                if self._step_stack and self._step_stack[-1].macro == macro and self._step_stack[-1].step_id == step_id and self._step_stack[-1].attempt == attempt:
                    self._step_stack.pop()
                continue

            if et == "step_retry":
                self._instant(
                    name="retry",
                    ts_us=ts_us,
                    macro=macro,
                    track="steps",
                    cat="vhk.retry",
                    args={
                        "macro": macro,
                        "step_id": e.get("step_id"),
                        "step_type": e.get("step_type"),
                        "attempt": e.get("attempt"),
                        "retries_left": e.get("retries_left"),
                        "retry_delay_ms": e.get("retry_delay_ms"),
                        "error": e.get("error"),
                        "error_type": e.get("error_type"),
                    },
                )
                continue

            if et == "wait_start":
                kind = str(e.get("kind") or "wait")
                self._wait_seq += 1
                cur = self._step_stack[-1] if self._step_stack else None
                step_id = cur.step_id if cur else ""
                attempt = cur.attempt if cur else 1
                key = (macro, step_id, attempt, kind, self._wait_seq)
                self._wait_starts[key] = {"ts": ts_s, **e, "_key": key}
                # Also store the latest key for this (macro, step) to match wait_end.
                self._wait_starts[(macro, step_id, attempt, kind, 0)] = {"_last": key}
                continue

            if et == "wait_end":
                kind = str(e.get("kind") or "wait")
                cur = self._step_stack[-1] if self._step_stack else None
                step_id = cur.step_id if cur else ""
                attempt = cur.attempt if cur else 1
                last_key_rec = self._wait_starts.pop((macro, step_id, attempt, kind, 0), None)
                last_key = last_key_rec.get("_last") if isinstance(last_key_rec, dict) else None
                start = self._wait_starts.pop(last_key, None) if last_key else None

                start_s = _safe_float(start.get("ts")) if isinstance(start, dict) else None
                if start_s is None:
                    start_s = ts_s
                start_us = _to_us(start_s, base_s)
                dur_us = max(0, ts_us - start_us)

                args = {
                    "macro": macro,
                    "step_id": step_id,
                    "step_attempt": attempt,
                    "ok": e.get("ok"),
                    "attempts": e.get("attempts"),
                }
                # Copy a few interesting fields.
                for k in ("score", "dist", "x", "y", "text", "threshold", "tolerance", "timeout_ms"):
                    if k in e:
                        args[k] = e.get(k)
                self._complete(
                    name=f"wait:{kind}",
                    ts_us=start_us,
                    dur_us=dur_us,
                    macro=macro,
                    track="waits",
                    cat="vhk.wait",
                    args=args,
                )
                continue

            if et == "wait_attempt":
                kind = str(e.get("kind") or "wait")
                args = {"kind": kind}
                for k, v in e.items():
                    if k in {"ts", "type"}:
                        continue
                    args[k] = v
                self._instant(
                    name=f"attempt:{kind}",
                    ts_us=ts_us,
                    macro=macro,
                    track="attempts",
                    cat="vhk.wait_attempt",
                    args=args,
                )
                continue

            if et == "call_macro_start":
                self._call_stack.append({"ts": ts_s, **e})
                continue
            if et == "call_macro_end":
                # Pair with last start.
                start = self._call_stack.pop() if self._call_stack else None
                start_s = _safe_float(start.get("ts")) if isinstance(start, dict) else None
                start_us = _to_us(start_s or ts_s, base_s)
                dur_us = max(0, ts_us - start_us)
                parent = str(e.get("parent_macro") or (start or {}).get("parent_macro") or macro)
                child = str(e.get("child_macro") or (start or {}).get("child_macro") or "")
                self._complete(
                    name="CallMacro",
                    ts_us=start_us,
                    dur_us=dur_us,
                    macro=parent,
                    track="steps",
                    cat="vhk.call",
                    args={"parent_macro": parent, "child_macro": child},
                )
                continue

            # Default: keep some events as instants for context.
            if et in {"shell", "cursor", "image_search", "ocr", "pixel_search", "notify"}:
                args = {k: v for k, v in e.items() if k not in {"ts", "type"}}
                self._instant(name=et, ts_us=ts_us, macro=macro, track="meta", cat=f"vhk.{et}", args=args)
                continue

        # Add a run duration slice if we have both.
        if run_start_ts is not None and run_end_ts is not None:
            start_us = _to_us(run_start_ts, base_s)
            dur_us = _to_us(run_end_ts, base_s) - start_us
            self._complete(
                name="run",
                ts_us=start_us,
                dur_us=dur_us,
                macro=run_macro or "(unknown)",
                track="meta",
                cat="vhk.run",
                args={"run_id": run_id, "project": project, "macro": run_macro},
            )

        # Emit metadata thread names at the end (needs macro discovery).
        self._emit_thread_names()

        # Some trace viewers do better with sorted events.
        self._trace_events.sort(key=lambda r: (r.get("ts", -1), r.get("tid", 0), r.get("ph", "")))

        return {
            "traceEvents": self._trace_events,
            "displayTimeUnit": "ms",
        }


def eventlog_to_chrome_trace(events: Iterable[dict[str, Any]], *, pid: int = 1) -> dict[str, Any]:
    """Convert VHK JSONL events to a Chrome Trace Event JSON dict."""

    return TraceBuilder(events, pid=pid).build()
