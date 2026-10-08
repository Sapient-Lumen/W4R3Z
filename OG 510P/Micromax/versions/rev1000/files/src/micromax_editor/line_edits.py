from __future__ import annotations

from bisect import bisect_left
from dataclasses import dataclass
from typing import Iterable

from .buffer import Cursor


def _source_lines(lines: Iterable[str]) -> tuple[str, ...]:
    source = tuple(str(line) for line in lines)
    return source if source else ("",)


@dataclass(frozen=True)
class MoveLineBlockPlan:
    """One immutable line-block permutation and its coordinate projection.

    ``start`` and ``end`` are inclusive source-line indexes. ``direction`` is
    exactly ``-1`` or ``1``. Ordinary coordinates follow the source line whose
    text they addressed. A half-open whole-line selection needs one exception:
    its trailing ``(end + 1, 0)`` endpoint denotes the boundary after the moved
    block, not the first character of the displaced neighboring line. Callers
    mark that endpoint with ``trailing_boundary=True``.
    """

    lines: tuple[str, ...]
    start: int
    end: int
    direction: int
    old_to_new: tuple[int, ...]

    @classmethod
    def build(
        cls,
        lines: Iterable[str],
        *,
        start: int,
        end: int,
        direction: int,
    ) -> MoveLineBlockPlan:
        source = _source_lines(lines)
        start_i = int(start)
        end_i = int(end)
        direction_i = int(direction)
        if direction_i not in (-1, 1):
            raise ValueError("line-block direction must be -1 or 1")
        if not (0 <= start_i <= end_i < len(source)):
            raise ValueError("line-block span is outside the source")
        if direction_i < 0 and start_i == 0:
            raise ValueError("top line block cannot move up")
        if direction_i > 0 and end_i == len(source) - 1:
            raise ValueError("bottom line block cannot move down")

        line_map = list(range(len(source)))
        if direction_i < 0:
            output = (
                source[: start_i - 1]
                + source[start_i : end_i + 1]
                + (source[start_i - 1],)
                + source[end_i + 1 :]
            )
            line_map[start_i - 1] = end_i
            for line in range(start_i, end_i + 1):
                line_map[line] = line - 1
        else:
            output = (
                source[:start_i]
                + (source[end_i + 1],)
                + source[start_i : end_i + 1]
                + source[end_i + 2 :]
            )
            line_map[end_i + 1] = start_i
            for line in range(start_i, end_i + 1):
                line_map[line] = line + 1

        return cls(
            lines=output,
            start=start_i,
            end=end_i,
            direction=direction_i,
            old_to_new=tuple(line_map),
        )

    @property
    def source_trailing_boundary(self) -> Cursor:
        return Cursor(self.end + 1, 0)

    @property
    def target_trailing_boundary(self) -> Cursor:
        return Cursor(self.end + self.direction + 1, 0)

    def project(self, cursor: Cursor, *, trailing_boundary: bool = False) -> Cursor:
        point = Cursor(int(cursor.line), int(cursor.col))
        if trailing_boundary and point == self.source_trailing_boundary:
            return self.target_trailing_boundary
        return Cursor(self.old_to_new[point.line], point.col)


@dataclass(frozen=True)
class DuplicateLineBlockPlan:
    """Duplicate one contiguous source block with explicit coordinate policy."""

    lines: tuple[str, ...]
    start: int
    end: int

    @classmethod
    def build(
        cls,
        lines: Iterable[str],
        *,
        start: int,
        end: int,
    ) -> DuplicateLineBlockPlan:
        source = _source_lines(lines)
        start_i = int(start)
        end_i = int(end)
        if not (0 <= start_i <= end_i < len(source)):
            raise ValueError("duplicate-line span is outside the source")
        insert_at = end_i + 1
        output = source[:insert_at] + source[start_i : end_i + 1] + source[insert_at:]
        return cls(lines=output, start=start_i, end=end_i)

    @property
    def count(self) -> int:
        return self.end - self.start + 1

    @property
    def insertion_boundary(self) -> Cursor:
        return Cursor(self.end + 1, 0)

    def project_original(self, cursor: Cursor, *, keep_boundary: bool = False) -> Cursor:
        """Keep a point attached to its original source text.

        Positions in later source lines shift by the inserted block length. A
        whole-line selection endpoint at the insertion boundary can instead stay
        with the original block when ``keep_boundary`` is true.
        """

        point = Cursor(int(cursor.line), int(cursor.col))
        if keep_boundary and point == self.insertion_boundary:
            return point
        if point.line >= self.end + 1:
            return Cursor(point.line + self.count, point.col)
        return point

    def project_duplicate(self, cursor: Cursor) -> Cursor:
        """Move a source-block point to the corresponding duplicated line."""

        point = Cursor(int(cursor.line), int(cursor.col))
        if not (self.start <= point.line <= self.end):
            raise ValueError("point is outside the duplicated source block")
        return Cursor(point.line + self.count, point.col)


@dataclass(frozen=True)
class DeleteLinesPlan:
    """Delete unique source lines in one mutation and project surviving cursors."""

    lines: tuple[str, ...]
    deleted: tuple[int, ...]
    source_line_count: int

    @classmethod
    def build(cls, lines: Iterable[str], *, deleted: Iterable[int]) -> DeleteLinesPlan:
        source = _source_lines(lines)
        rows = tuple(sorted({int(line) for line in deleted}))
        if not rows:
            raise ValueError("delete-lines plan requires at least one source line")
        if rows[0] < 0 or rows[-1] >= len(source):
            raise ValueError("deleted line is outside the source")
        deleted_set = set(rows)
        output = tuple(line for index, line in enumerate(source) if index not in deleted_set)
        if not output:
            output = ("",)
        return cls(lines=output, deleted=rows, source_line_count=len(source))

    @property
    def cut_lines(self) -> tuple[int, ...]:
        return self.deleted

    def project(self, cursor: Cursor) -> Cursor:
        point = Cursor(int(cursor.line), int(cursor.col))
        line = point.line
        deleted_before = bisect_left(self.deleted, line)
        index = bisect_left(self.deleted, line)
        is_deleted = index < len(self.deleted) and self.deleted[index] == line
        if not is_deleted:
            return Cursor(line - deleted_before, point.col)

        # A deleted cursor lands at column zero on the next surviving source
        # line, or the final surviving line when no later line exists.
        target = min(line - deleted_before, len(self.lines) - 1)
        return Cursor(max(0, target), 0)
