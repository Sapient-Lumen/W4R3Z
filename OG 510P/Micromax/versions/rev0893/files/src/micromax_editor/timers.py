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
    script_context: bool = False
    plugin_load_root: str | None = None
    plugin_generation: int | None = None
    script_origin_id: str | None = None


class TimerQueue:
    def __init__(self) -> None:
        self._next_id: int = 1
        self._heap: list[tuple[float, int]] = []
        self._tasks: dict[int, TimerTask] = {}

    def schedule(
        self,
        *,
        now: float,
        delay_ms: int,
        xt: Any,
        group: Optional[str] = None,
        script_context: bool = False,
        plugin_load_root: str | None = None,
        plugin_generation: int | None = None,
        script_origin_id: str | None = None,
    ) -> int:
        if delay_ms < 0:
            delay_ms = 0
        due = float(now) + (float(delay_ms) / 1000.0)
        tid = int(self._next_id)
        self._next_id += 1
        task = TimerTask(
            task_id=tid,
            due=due,
            xt=xt,
            group=group,
            script_context=bool(script_context),
            plugin_load_root=(str(plugin_load_root) if plugin_load_root else None),
            plugin_generation=(int(plugin_generation) if plugin_generation not in (None, "") else None),
            script_origin_id=(str(script_origin_id) if script_origin_id else None),
        )
        self._tasks[tid] = task
        heapq.heappush(self._heap, (task.due, tid))
        return tid

    def get(self, tid: int) -> TimerTask | None:
        """Return a pending timer task by id, if it still exists."""

        return self._tasks.get(int(tid))

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

    def retag_group(self, old: str, new: str) -> int:
        """Rename the group tag on pending timers."""

        old_group = str(old)
        new_group = str(new)
        changed = 0
        for t in list(self._tasks.values()):
            if t.group == old_group and not t.canceled:
                t.group = new_group
                changed += 1
        return changed

    def pop_due(
        self,
        *,
        now: float,
        limit: int = 1000,
        allow: Callable[[TimerTask], bool] | None = None,
    ) -> list[TimerTask]:
        """Pop up to limit due tasks, skipping canceled/unknown heap entries.

        When ``allow`` is supplied, due-but-denied tasks remain pending instead
        of being consumed.  This lets lower-authority script callers pump their
        own timers without erasing or firing trusted due timers.
        """

        out: list[TimerTask] = []
        deferred: list[tuple[float, int]] = []
        n = 0
        while self._heap and n < limit:
            due, tid = self._heap[0]
            if float(due) > float(now):
                break
            heapq.heappop(self._heap)
            t = self._tasks.get(int(tid))
            if t is None:
                continue
            if t.canceled:
                self._tasks.pop(int(tid), None)
                continue
            if allow is not None and not bool(allow(t)):
                deferred.append((float(due), int(tid)))
                continue
            self._tasks.pop(int(tid), None)
            out.append(t)
            n += 1
        for item in deferred:
            heapq.heappush(self._heap, item)
        return out

    def groups(self) -> list[str]:
        """Return active timer groups for diagnostics/tests."""

        return sorted({str(t.group) for t in self._tasks.values() if t.group and not t.canceled})

    def pending_count(self) -> int:
        return sum(1 for t in self._tasks.values() if not t.canceled)
