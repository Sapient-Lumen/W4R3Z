from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
from typing import Callable, Iterator


@dataclass
class Edit:
    undo: Callable[[], None]
    redo: Callable[[], None]
    description: str = ""
    target: Callable[[], str] | None = None


class UndoManager:
    """Tiny undo/redo stack.

    For now we only support linear history.

    Notes for embedding:
      - `suppress_recording()` is used by higher-level helpers (e.g. editor hostcalls)
        that want to group multiple operations into a single undo step.
      - Suppression is *transaction friendly*: suppressed edits do not touch undo/redo
        stacks, so callers can roll back safely on errors.
    """

    def __init__(self) -> None:
        self._undo: list[Edit] = []
        self._redo: list[Edit] = []
        self._suppress: int = 0

    def depth(self) -> int:
        return len(self._undo)

    def redo_depth(self) -> int:
        return len(self._redo)

    def is_suppressed(self) -> bool:
        return self._suppress > 0

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
        self._redo.clear()

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
        e.undo()
        self._redo.append(e)
        return True

    def redo(self) -> bool:
        if not self._redo:
            return False
        e = self._redo.pop()
        e.redo()
        self._undo.append(e)
        return True
