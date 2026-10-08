"""micromax_editor.timers

A tiny deterministic timer queue for the editor embedding (rev66).

This exists to support plugin ergonomics like:
- debounce / coalesce repeated events
- autosave / periodic tasks

Constraints:
- no threads
- deterministic in tests (injectable clock)
- best-effort: timer handlers are isolated and exceptions are reported

This module only manages scheduling and due determination. Execution is handled
by the Editor, because it owns the embedded VM.
"""

from __future__ import annotations

from dataclasses import dataclass
import heapq
from typing import Any, Callable, Optional


@dataclass
class TimerTask:
    task_id: int
    due: float
    xt: Any
    group: Optional[str] = None
    canceled: bool = False


class TimerQueue:
    def __init__(self) -> None:
        self._next_id: int = 1
        self._heap: list[tuple[float, int]] = []
        self._tasks: dict[int, TimerTask] = {}

    def schedule(self, *, now: float, delay_ms: int, xt: Any, group: Optional[str] = None) -> int:
        if delay_ms < 0:
            delay_ms = 0
        due = float(now) + (float(delay_ms) / 1000.0)
        tid = int(self._next_id)
        self._next_id += 1
        task = TimerTask(task_id=tid, due=due, xt=xt, group=group)
        self._tasks[tid] = task
        heapq.heappush(self._heap, (task.due, tid))
        return tid

    def cancel(self, tid: int) -> bool:
        t = self._tasks.get(int(tid))
        if t is None:
            return False
        t.canceled = True
        return True

    def cancel_group(self, group: str) -> int:
        g = str(group)
        removed = 0
        for t in list(self._tasks.values()):
            if t.group == g and not t.canceled:
                t.canceled = True
                removed += 1
        return removed

    def pop_due(self, *, now: float, limit: int = 1000) -> list[TimerTask]:
        """Pop up to limit due tasks, skipping canceled/unknown heap entries."""

        out: list[TimerTask] = []
        n = 0
        while self._heap and n < limit:
            due, tid = self._heap[0]
            if float(due) > float(now):
                break
            heapq.heappop(self._heap)
            t = self._tasks.pop(int(tid), None)
            if t is None:
                continue
            if t.canceled:
                continue
            out.append(t)
            n += 1
        return out

    def pending_count(self) -> int:
        return sum(1 for t in self._tasks.values() if not t.canceled)
