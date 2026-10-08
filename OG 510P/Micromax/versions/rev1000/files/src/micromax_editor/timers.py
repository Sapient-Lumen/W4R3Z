"""micromax_editor.timers

A tiny deterministic timer queue for the editor embedding (rev66).

This exists to support plugin ergonomics like:
- debounce / coalesce repeated events
- autosave / periodic tasks

Constraints:
- no threads
- deterministic in tests (injectable clock)
- best-effort: timer handlers are isolated and exceptions are reported

This module owns pending timer lifetimes.  Execution is handled by the Editor,
because it owns the embedded VM, but cancellation/cleanup must release delayed
callback objects immediately instead of retaining them until their due time.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
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
    """Deterministic timer queue with explicit delayed-resource ownership."""

    _COMPACT_HEAP_MIN_ENTRIES = 64

    def __init__(self) -> None:
        self._next_id: int = 1
        self._heap: list[tuple[float, int]] = []
        self._tasks: dict[int, TimerTask] = {}

    def _clone_tasks(self, tasks: dict[int, TimerTask]) -> dict[int, TimerTask]:
        return {int(tid): replace(task) for tid, task in tasks.items() if not bool(task.canceled)}

    def _rebuild_heap(self) -> None:
        """Rebuild the due-time heap from live tasks only."""

        self._heap = [
            (float(getattr(task, "due", 0.0)), int(tid))
            for tid, task in self._tasks.items()
            if not bool(getattr(task, "canceled", False))
        ]
        heapq.heapify(self._heap)

    def _maybe_compact_heap(self) -> None:
        """Bound stale heap entries left by O(1) cancellation.

        Python's heapq recipe for mutable priority queues marks/deletes entries in
        a dictionary and lets stale heap rows be skipped later.  That is fine only
        if the stale side is bounded.  Timers are script-visible delayed work, so
        repeated schedule/cancel cycles should not grow a second unbounded queue.
        """

        live = len(self._tasks)
        if len(self._heap) > max(self._COMPACT_HEAP_MIN_ENTRIES, live * 2 + 16):
            self._rebuild_heap()

    def retained_task_count(self) -> int:
        """Return live task rows retained by the queue.

        This is a diagnostic/test hook for the lifecycle contract: canceled
        timers should not keep callback quotations, plugin roots, or generations
        alive inside ``_tasks``.
        """

        return len(self._tasks)

    def heap_entry_count(self) -> int:
        """Return raw heap entries, including bounded stale id rows."""

        return len(self._heap)

    def snapshot_state(self) -> tuple[dict[int, TimerTask], list[tuple[float, int]], int]:
        """Return a restorable snapshot of all live timer-owner state."""

        self._maybe_compact_heap()
        return (self._clone_tasks(self._tasks), list(self._heap), int(self._next_id))

    def restore_state(
        self,
        *,
        tasks: dict[int, TimerTask],
        heap: list[tuple[float, int]] | None = None,
        next_id: int | None = None,
    ) -> None:
        """Restore all timer-owner state from a snapshot."""

        self._tasks = self._clone_tasks({int(tid): task for tid, task in dict(tasks).items()})
        if heap is not None:
            live_ids = set(self._tasks)
            self._heap = [
                (float(due), int(tid))
                for due, tid in list(heap)
                if int(tid) in live_ids
            ]
            heapq.heapify(self._heap)
        else:
            self._rebuild_heap()
        if next_id is not None:
            self._next_id = int(next_id)

    def snapshot_group_tasks(self, groups: tuple[str, ...]) -> dict[int, TimerTask]:
        """Return cloned live timer tasks owned by any runtime group."""

        group_set = {str(group) for group in groups}
        return {
            int(tid): replace(task)
            for tid, task in self._tasks.items()
            if not bool(task.canceled) and str(getattr(task, "group", "") or "") in group_set
        }

    def restore_group_tasks(self, groups: tuple[str, ...], tasks: dict[int, TimerTask]) -> None:
        """Restore touched group timer rows without rewinding unrelated groups."""

        group_set = {str(group) for group in groups}
        touched_ids = {int(tid) for tid in tasks}
        for tid, task in list(self._tasks.items()):
            if int(tid) in touched_ids or str(getattr(task, "group", "") or "") in group_set:
                self._tasks.pop(int(tid), None)
        self._tasks.update(self._clone_tasks({int(tid): task for tid, task in dict(tasks).items()}))
        self._rebuild_heap()

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

        task = self._tasks.get(int(tid))
        if task is None or bool(task.canceled):
            return None
        return task

    def cancel(self, tid: int) -> bool:
        task = self._tasks.pop(int(tid), None)
        if task is None:
            return False
        task.canceled = True
        self._maybe_compact_heap()
        return True

    def cancel_group(self, group: str) -> int:
        g = str(group)
        removed = 0
        for tid, task in list(self._tasks.items()):
            if task.group == g and not task.canceled:
                task.canceled = True
                self._tasks.pop(int(tid), None)
                removed += 1
        if removed:
            self._rebuild_heap()
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
        if not self._tasks and self._heap:
            self._heap = []
        else:
            self._maybe_compact_heap()
        return out

    def groups(self) -> list[str]:
        """Return active timer groups for diagnostics/tests."""

        return sorted({str(t.group) for t in self._tasks.values() if t.group and not t.canceled})

    def pending_count(self) -> int:
        return sum(1 for t in self._tasks.values() if not t.canceled)
