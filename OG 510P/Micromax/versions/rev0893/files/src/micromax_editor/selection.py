from __future__ import annotations

from dataclasses import dataclass

from .buffer import Cursor


@dataclass(frozen=True)
class Selection:
    """A selection defined by two cursors.

    Selections are treated as half-open ranges: [start, end).
    """

    a: Cursor
    b: Cursor

    def normalized(self) -> tuple[Cursor, Cursor]:
        if (self.b.line, self.b.col) < (self.a.line, self.a.col):
            return self.b, self.a
        return self.a, self.b

    def is_empty(self) -> bool:
        s, e = self.normalized()
        return (s.line, s.col) == (e.line, e.col)
