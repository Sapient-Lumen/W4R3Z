from __future__ import annotations

from collections import deque
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Callable, Iterable, Iterator


_TEXT_SIZE_CHUNK_CHARS = 64 * 1024


def logical_text_bytes(text: str) -> int:
    """Return bounded-allocation UTF-8 bytes for retained editor text.

    Undo budgets need a stable, portable unit without allocating one second
    full-document byte string merely to count it.  ASCII—the overwhelmingly
    common editor case—is exact from ``len``; other text is encoded in bounded
    chunks with the same surrogate policy used by the buffer's signatures.

    This is logical retained text, not Python object size, allocator overhead,
    RSS, or a hard process-memory bound.
    """

    value = str(text)
    if value.isascii():
        return len(value)
    total = 0
    for start in range(0, len(value), _TEXT_SIZE_CHUNK_CHARS):
        total += len(
            value[start : start + _TEXT_SIZE_CHUNK_CHARS].encode(
                "utf-8",
                errors="surrogatepass",
            )
        )
    return int(total)


@dataclass(frozen=True)
class RetainedTextCharge:
    """Logical text retained by one undo row for one editor-owned buffer."""

    owner: object = field(compare=False, repr=False)
    label: str
    byte_count: int

    def __post_init__(self) -> None:
        object.__setattr__(self, "label", str(self.label or "buffer"))
        object.__setattr__(self, "byte_count", max(0, int(self.byte_count)))


@dataclass(frozen=True)
class UndoBudgetOverage:
    """One soft budget still exceeded by the newest indivisible undo row."""

    label: str
    retained_text_bytes: int
    budget_bytes: int


@dataclass(frozen=True)
class UndoTrimReport:
    """Observable result of removing complete oldest linear-history rows."""

    dropped_edits: int = 0
    dropped_retained_text_bytes: int = 0
    over_budget: tuple[UndoBudgetOverage, ...] = ()


@dataclass
class Edit:
    undo: Callable[[], None]
    redo: Callable[[], None]
    description: str = ""
    target: Callable[[], str] | None = None
    # Optional host/editor provenance attached by higher layers.  The undo
    # manager remains intentionally dumb about policy; editor.py decides whether
    # a caller may replay a particular entry before invoking undo()/redo().
    authority: object | None = None
    # Explicit logical payload accounting.  Callbacks may retain other small
    # state, but document text is the dominant and user-controllable cost.
    retained_text: tuple[RetainedTextCharge, ...] = ()
    # Higher layers may attach an opaque grouping witness.  UndoManager does
    # not interpret it; editor.py uses it to replace one still-top row when a
    # later adjacent keystroke belongs to the same bounded user action.
    history_group: object | None = field(default=None, compare=False, repr=False)


@dataclass(frozen=True)
class UndoSnapshot:
    """Lightweight copy of the linear undo/redo stacks.

    The contained ``Edit`` objects intentionally remain shared: each edit holds
    tiny callbacks into editor buffers, so rollback should restore stack
    membership without cloning closures or trying to serialize editor state.
    """

    undo: tuple[Edit, ...]
    redo: tuple[Edit, ...]
    suppress: int


class UndoManager:
    """Small linear undo/redo owner with explicit retained-text accounting.

    Notes for embedding:
      - `suppress_recording()` is used by higher-level helpers (e.g. editor hostcalls)
        that want to group multiple operations into a single undo step.
      - Suppression is *transaction friendly*: suppressed edits do not touch undo/redo
        stacks, so callers can roll back safely on errors.
      - Text budgets trim complete oldest undo rows only.  They never split a
        transaction, and the newest row is retained even when it alone exceeds
        a configured budget so the just-completed change remains recoverable.
    """

    def __init__(self) -> None:
        # Deques keep oldest-row retirement O(1).  A list.pop(0) would turn a
        # steady-state byte budget into an O(history) cost on every new edit.
        self._undo: deque[Edit] = deque()
        self._redo: deque[Edit] = deque()
        self._suppress: int = 0
        self._undo_retained_text_total: int = 0
        self._redo_retained_text_total: int = 0
        self._undo_retained_text_by_owner: dict[int, tuple[object, int]] = {}
        self._redo_retained_text_by_owner: dict[int, tuple[object, int]] = {}

    def depth(self) -> int:
        return len(self._undo)

    def redo_depth(self) -> int:
        return len(self._redo)

    def is_suppressed(self) -> bool:
        return self._suppress > 0

    def snapshot(self) -> UndoSnapshot:
        """Return a tiny restorable snapshot of undo/redo membership."""

        return UndoSnapshot(tuple(self._undo), tuple(self._redo), int(self._suppress))

    def restore(self, snapshot: UndoSnapshot) -> None:
        """Restore undo/redo membership from ``snapshot``.

        This is deliberately stack-level only: callers that roll back editor
        state must also keep buffer object identities stable so the restored
        edit callbacks still point at live editor buffers.
        """

        self._undo.clear()
        self._undo.extend(snapshot.undo)
        self._redo.clear()
        self._redo.extend(snapshot.redo)
        self._suppress = max(0, int(snapshot.suppress))
        self._rebuild_retained_text_accounting()

    @contextmanager
    def suppress_recording(self) -> Iterator[None]:
        self._suppress += 1
        try:
            yield
        finally:
            self._suppress = max(0, self._suppress - 1)

    def record(self, edit: Edit) -> None:
        if self._suppress > 0:
            return
        self._undo.append(edit)
        self._undo_retained_text_total += self._add_edit_retained_text(
            self._undo_retained_text_by_owner,
            edit,
        )
        self._clear_redo()

    def replace_last(self, expected: Edit, edit: Edit) -> bool:
        """Replace the exact newest undo row and refresh cached accounting.

        This is deliberately an identity-guarded primitive rather than a
        general history rewrite.  A caller may compact a row only while the row
        it inspected is still newest; stale or suppressed requests are no-ops.
        Like recording a fresh branch, replacement releases every redo row.
        """

        if self._suppress > 0 or not self._undo or self._undo[-1] is not expected:
            return False

        removed = self._remove_edit_retained_text(
            self._undo_retained_text_by_owner,
            expected,
        )
        self._undo[-1] = edit
        added = self._add_edit_retained_text(
            self._undo_retained_text_by_owner,
            edit,
        )
        self._undo_retained_text_total = max(
            0,
            int(self._undo_retained_text_total) - removed + added,
        )
        self._clear_redo()
        return True

    def _clear_redo(self) -> None:
        """Release the abandoned redo branch and its cached text charges."""

        self._redo.clear()
        self._redo_retained_text_total = 0
        self._redo_retained_text_by_owner.clear()

    @staticmethod
    def _add_edit_retained_text(
        by_owner: dict[int, tuple[object, int]],
        edit: Edit,
    ) -> int:
        added = 0
        for charge in edit.retained_text:
            byte_count = max(0, int(charge.byte_count))
            if byte_count <= 0:
                continue
            owner = charge.owner
            ident = id(owner)
            row = by_owner.get(ident)
            prior = row[1] if row is not None and row[0] is owner else 0
            by_owner[ident] = (owner, int(prior) + byte_count)
            added += byte_count
        return int(added)

    @staticmethod
    def _remove_edit_retained_text(
        by_owner: dict[int, tuple[object, int]],
        edit: Edit,
    ) -> int:
        removed = 0
        for charge in edit.retained_text:
            byte_count = max(0, int(charge.byte_count))
            if byte_count <= 0:
                continue
            owner = charge.owner
            ident = id(owner)
            row = by_owner.get(ident)
            if row is None or row[0] is not owner:
                continue
            remaining = max(0, int(row[1]) - byte_count)
            if remaining:
                by_owner[ident] = (owner, remaining)
            else:
                by_owner.pop(ident, None)
            removed += byte_count
        return int(removed)

    def _rebuild_retained_text_accounting(self) -> None:
        """Rebuild cached totals after restoring arbitrary stack membership."""

        self._undo_retained_text_by_owner.clear()
        self._redo_retained_text_by_owner.clear()
        self._undo_retained_text_total = sum(
            self._add_edit_retained_text(self._undo_retained_text_by_owner, edit)
            for edit in self._undo
        )
        self._redo_retained_text_total = sum(
            self._add_edit_retained_text(self._redo_retained_text_by_owner, edit)
            for edit in self._redo
        )

    @staticmethod
    def _owner_retained_text_bytes(
        by_owner: dict[int, tuple[object, int]],
        owner: object,
    ) -> int:
        row = by_owner.get(id(owner))
        if row is None or row[0] is not owner:
            return 0
        return max(0, int(row[1]))

    def retained_text_bytes(
        self,
        owner: object | None = None,
        *,
        include_redo: bool = True,
    ) -> int:
        """Return logical text bytes retained by history.

        ``owner`` is matched by identity rather than equality because editor
        buffers are mutable dataclasses.  Undo/redo movement does not change the
        total while ``include_redo`` is true; recording a new edit releases the
        abandoned redo branch before budget enforcement.
        """

        if owner is None:
            total = int(self._undo_retained_text_total)
            if include_redo:
                total += int(self._redo_retained_text_total)
            return total

        total = self._owner_retained_text_bytes(
            self._undo_retained_text_by_owner,
            owner,
        )
        if include_redo:
            total += self._owner_retained_text_bytes(
                self._redo_retained_text_by_owner,
                owner,
            )
        return int(total)

    def trim_undo_to_budgets(
        self,
        budgets: Iterable[tuple[object, str, int]],
    ) -> UndoTrimReport:
        """Trim the oldest complete undo rows to satisfy touched-buffer limits.

        ``budgets`` should describe owners charged by the row just recorded.
        Limits at or below zero mean unlimited.  The redo stack is expected to
        be empty because ``record`` clears it.  Linear chronology means an old
        row for another buffer may also be retired when it precedes an
        over-budget row; removing arbitrary middle entries would make later
        inverses replay against the wrong state.

        The newest row is indivisible and always retained.  Any resulting soft
        overage is returned explicitly for user-visible feedback.
        """

        normalized: dict[int, tuple[object, str, int]] = {}
        order: list[int] = []
        for owner, label, raw_limit in budgets:
            limit = max(0, int(raw_limit))
            if limit <= 0:
                continue
            ident = id(owner)
            if ident not in normalized:
                order.append(ident)
            normalized[ident] = (owner, str(label or "buffer"), limit)

        if not normalized or not self._undo:
            return UndoTrimReport()

        def _owner_total(ident: int) -> int:
            owner = normalized[ident][0]
            return self._owner_retained_text_bytes(
                self._undo_retained_text_by_owner,
                owner,
            )

        def _over_budget() -> bool:
            return any(_owner_total(ident) > normalized[ident][2] for ident in order)

        dropped_edits = 0
        dropped_bytes = 0
        # Preserve the just-recorded row even when its one complete transaction
        # exceeds the limit.  This keeps the most recent user action recoverable
        # and makes the residual overage honest rather than silently lossy.
        while len(self._undo) > 1 and _over_budget():
            removed = self._undo.popleft()
            dropped_edits += 1
            removed_bytes = self._remove_edit_retained_text(
                self._undo_retained_text_by_owner,
                removed,
            )
            self._undo_retained_text_total = max(
                0,
                int(self._undo_retained_text_total) - removed_bytes,
            )
            dropped_bytes += removed_bytes

        overages = tuple(
            UndoBudgetOverage(
                label=normalized[ident][1],
                retained_text_bytes=_owner_total(ident),
                budget_bytes=int(normalized[ident][2]),
            )
            for ident in order
            if _owner_total(ident) > normalized[ident][2]
        )
        return UndoTrimReport(
            dropped_edits=int(dropped_edits),
            dropped_retained_text_bytes=int(dropped_bytes),
            over_budget=overages,
        )

    def can_undo(self) -> bool:
        return bool(self._undo)

    def can_redo(self) -> bool:
        return bool(self._redo)

    def peek_undo(self) -> Edit | None:
        if not self._undo:
            return None
        return self._undo[-1]

    def peek_redo(self) -> Edit | None:
        if not self._redo:
            return None
        return self._redo[-1]

    def undo(self) -> bool:
        if not self._undo:
            return False
        e = self._undo.pop()
        try:
            e.undo()
        except BaseException:
            # A guarded inverse may refuse stale text.  Keep history membership
            # unchanged so the user can inspect/recover instead of losing the
            # only description of the edit that failed to replay.
            self._undo.append(e)
            raise
        moved_bytes = self._remove_edit_retained_text(
            self._undo_retained_text_by_owner,
            e,
        )
        self._undo_retained_text_total = max(
            0,
            int(self._undo_retained_text_total) - moved_bytes,
        )
        self._redo.append(e)
        self._redo_retained_text_total += self._add_edit_retained_text(
            self._redo_retained_text_by_owner,
            e,
        )
        return True

    def redo(self) -> bool:
        if not self._redo:
            return False
        e = self._redo.pop()
        try:
            e.redo()
        except BaseException:
            self._redo.append(e)
            raise
        moved_bytes = self._remove_edit_retained_text(
            self._redo_retained_text_by_owner,
            e,
        )
        self._redo_retained_text_total = max(
            0,
            int(self._redo_retained_text_total) - moved_bytes,
        )
        self._undo.append(e)
        self._undo_retained_text_total += self._add_edit_retained_text(
            self._undo_retained_text_by_owner,
            e,
        )
        return True
