from __future__ import annotations

"""Plan non-overlapping text edits against one immutable document snapshot.

Multi-cursor commands are easiest to reason about when every range refers to the
same pre-edit document. This module keeps that rule pure and UI-independent:
coordinates become flat offsets once, conflicting ranges fail before mutation,
and compact geometry remaps sidecars. The product planner builds directly over
one canonical line vector; the flat-string planner remains an executable oracle.
"""

from bisect import bisect_right
from collections.abc import Callable, Iterable, Sequence
from dataclasses import dataclass

from .buffer import BufferEditConflict, Cursor, normalize_buffer_text
from .textpos import (
    line_start_offsets as compact_line_start_offsets,
    line_start_offsets_for_lines as compact_line_start_offsets_for_lines,
)


class SimultaneousEditError(ValueError):
    """Raised when one transaction contains ambiguous/conflicting edits."""


@dataclass(frozen=True)
class SimultaneousTextEdit:
    """One replacement expressed in coordinates of the original document.

    ``owner`` identifies the cursor that should land at the end of the inserted
    text.  It may be ``None`` for edits that only need ordinary position
    remapping.
    """

    start: Cursor
    end: Cursor
    text: str
    owner: int | None = None


@dataclass(frozen=True)
class _IndexedEdit:
    start: int
    end: int
    text: str
    owners: tuple[int, ...]
    new_start: int
    new_end: int
    delta_after: int


@dataclass(frozen=True)
class SimultaneousTextSplice:
    """One compact invertible replacement from a simultaneous edit plan.

    Old coordinates address the pre-edit document.  New coordinates address
    the resulting document.  Keeping both coordinate spaces lets undo validate
    every replacement against one immutable current-text snapshot before the
    buffer changes, including adjacent deletions whose inverse insertions share
    one resulting offset.
    """

    old_start: int
    old_end: int
    new_start: int
    new_end: int
    old_text: str
    new_text: str


@dataclass(frozen=True)
class SimultaneousEditWitness:
    """Sparse exact inverse data for one atomic group of text replacements."""

    splices: tuple[SimultaneousTextSplice, ...] = ()

    @property
    def text_changed(self) -> bool:
        return bool(self.splices)

    def retained_texts(self) -> tuple[str, ...]:
        """Return only strings read by replay callbacks.

        Equal replacement slices are omitted when the witness is built, so a
        sidecar-only edit does not pin callback-dead document text.
        """

        return tuple(
            text
            for splice in self.splices
            for text in (splice.old_text, splice.new_text)
        )


@dataclass(frozen=True)
class AppliedSimultaneousEdit:
    """Outcome returned by the editor-side application seam."""

    changed: bool
    text_changed: bool
    edit_count: int
    history_witness: SimultaneousEditWitness | None = None


@dataclass(frozen=True)
class SimultaneousEditPlan:
    """A validated one-snapshot edit plan and its position mapping."""

    original_text: str
    new_text: str
    edits: tuple[_IndexedEdit, ...]
    edit_starts: tuple[int, ...]
    owner_offsets: tuple[tuple[int, int], ...]

    @property
    def text_changed(self) -> bool:
        return self.new_text != self.original_text

    @property
    def edit_count(self) -> int:
        return len(self.edits)

    def owner_offset(self, owner: int) -> int | None:
        return _owner_offset(self.owner_offsets, owner)

    def compact_history_witness(self) -> SimultaneousEditWitness:
        """Project the full planning strings into sparse exact inverse slices.

        Planning still needs the immutable source and result documents for
        cursor mapping.  Linear undo does not: it needs only changed slices and
        their positions in the before/after coordinate spaces.
        """

        # Individually changing rows can cancel into the exact source document.
        # That is a sidecar-only action: retaining its component slices would
        # make Undo/Redo publish false text mutations that application skipped.
        if not self.text_changed:
            return SimultaneousEditWitness()

        return _compact_history_witness(
            self.edits,
            read_slice=lambda start, end: self.original_text[start:end],
        )

    def map_offset(self, offset: int, *, affinity: str = "right") -> int:
        """Map an original-document offset into ``new_text``.

        Right affinity is the editor default: a position at an insertion point
        moves after inserted text, and a position inside a replaced range
        collapses to the replacement end.  Left affinity is provided for small
        callers that need the opposite boundary behavior.
        """

        return _map_offset_through_indexed_edits(
            source_length=len(self.original_text),
            edits=self.edits,
            edit_starts=self.edit_starts,
            offset=offset,
            affinity=affinity,
        )


@dataclass(frozen=True)
class LineVectorSimultaneousEditPlan:
    """A simultaneous edit plan that never owns a complete document string.

    ``new_lines`` is either the immutable source tuple (for a sidecar-only plan)
    or a detached canonical result list. Complete untouched lines retain their
    exact string objects; only touched output lines are joined. Flat offsets
    remain the compact mapping currency for cursor sidecars and sparse history,
    but source/result document strings are never materialized.
    """

    new_lines: Sequence[str]
    result_starts: Sequence[int]
    source_length: int
    result_length: int
    edits: tuple[_IndexedEdit, ...]
    edit_starts: tuple[int, ...]
    owner_offsets: tuple[tuple[int, int], ...]
    text_changed: bool
    history_witness: SimultaneousEditWitness | None

    @property
    def edit_count(self) -> int:
        return len(self.edits)

    def owner_offset(self, owner: int) -> int | None:
        return _owner_offset(self.owner_offsets, owner)

    def compact_history_witness(self) -> SimultaneousEditWitness:
        witness = self.history_witness
        if witness is None:
            raise RuntimeError("simultaneous line-vector plan did not capture history")
        return witness

    def map_offset(self, offset: int, *, affinity: str = "right") -> int:
        return _map_offset_through_indexed_edits(
            source_length=self.source_length,
            edits=self.edits,
            edit_starts=self.edit_starts,
            offset=offset,
            affinity=affinity,
        )


def _owner_offset(
    owner_offsets: Sequence[tuple[int, int]],
    owner: int,
) -> int | None:
    target = int(owner)
    for key, value in owner_offsets:
        if int(key) == target:
            return int(value)
    return None


def _map_offset_through_indexed_edits(
    *,
    source_length: int,
    edits: Sequence[_IndexedEdit],
    edit_starts: Sequence[int],
    offset: int,
    affinity: str,
) -> int:
    """Map one source offset using only compact edit geometry."""

    pos = max(0, min(int(offset), int(source_length)))
    if not edits:
        return pos

    if str(affinity) == "left":
        # At an edit start, stay before that edit. Otherwise use the most recent
        # edit to determine whether the point is inside or after it.
        index = bisect_right(edit_starts, pos - 1) - 1
    else:
        index = bisect_right(edit_starts, pos) - 1
    if index < 0:
        return pos

    edit = edits[index]
    if edit.start == edit.end and pos == edit.start:
        return edit.new_start if str(affinity) == "left" else edit.new_end
    if edit.start <= pos < edit.end:
        return edit.new_start if str(affinity) == "left" else edit.new_end
    return pos + int(edit.delta_after)


def _compact_history_witness(
    edits: Sequence[_IndexedEdit],
    *,
    read_slice: Callable[[int, int], str],
) -> SimultaneousEditWitness:
    """Project indexed geometry into sparse exact before/after slices."""

    splices: list[SimultaneousTextSplice] = []
    for edit in edits:
        old_text = str(read_slice(int(edit.start), int(edit.end)))
        new_text = str(edit.text)
        if old_text == new_text:
            continue
        splices.append(
            SimultaneousTextSplice(
                old_start=int(edit.start),
                old_end=int(edit.end),
                new_start=int(edit.new_start),
                new_end=int(edit.new_end),
                old_text=old_text,
                new_text=new_text,
            )
        )
    return SimultaneousEditWitness(splices=tuple(splices))


@dataclass(frozen=True)
class _ReplayRow:
    """One direction-resolved sparse replay row."""

    start: int
    end: int
    expected: str
    replacement: str


def _replay_rows(
    witness: SimultaneousEditWitness,
    *,
    undo: bool,
) -> tuple[_ReplayRow, ...]:
    rows: list[_ReplayRow] = []
    for splice in witness.splices:
        if undo:
            rows.append(
                _ReplayRow(
                    start=int(splice.new_start),
                    end=int(splice.new_end),
                    expected=str(splice.new_text),
                    replacement=str(splice.old_text),
                )
            )
        else:
            rows.append(
                _ReplayRow(
                    start=int(splice.old_start),
                    end=int(splice.old_end),
                    expected=str(splice.old_text),
                    replacement=str(splice.new_text),
                )
            )
    return tuple(rows)


def _validate_replay_rows(
    rows: Sequence[_ReplayRow],
    *,
    source_length: int,
    read_slice: Callable[[int, int], str],
) -> None:
    """Validate every replay target before a caller can publish a mutation."""

    source_at = 0
    for index, row in enumerate(rows, start=1):
        start = int(row.start)
        end = int(row.end)
        expected = str(row.expected)
        if start < source_at or end < start or end > int(source_length):
            raise BufferEditConflict(
                "buffer simultaneous edit conflict at "
                f"splice {index}; invalid offsets {start}..{end} "
                f"for {int(source_length)} chars"
            )
        if end - start != len(expected):
            raise BufferEditConflict(
                "buffer simultaneous edit conflict at "
                f"splice {index}; witness geometry {end - start} "
                f"does not match expected {len(expected)} chars"
            )
        found = str(read_slice(start, end))
        if found != expected:
            raise BufferEditConflict(
                "buffer simultaneous edit conflict at "
                f"splice {index} offsets {start}..{end}; "
                f"expected {len(expected)} chars, found {len(found)}"
            )
        source_at = end


def replay_simultaneous_edit_witness(
    source_text: str,
    witness: SimultaneousEditWitness,
    *,
    undo: bool,
) -> str:
    """Return one atomically validated string replay of ``witness``.

    This remains the pure flat-text oracle and the exceptional query-replace
    generation checker.  Product buffer Undo/Redo uses the line-vector sibling
    below so sparse history does not recreate complete current and result
    document strings merely to commit a few changed slices.
    """

    source = str(source_text)
    rows = _replay_rows(witness, undo=bool(undo))
    _validate_replay_rows(
        rows,
        source_length=len(source),
        read_slice=lambda start, end: source[start:end],
    )

    if not rows:
        return source

    parts: list[str] = []
    source_at = 0
    for row in rows:
        parts.append(source[source_at : int(row.start)])
        parts.append(str(row.replacement))
        source_at = int(row.end)
    parts.append(source[source_at:])
    return "".join(parts)


def _line_vector_source_length(lines: Sequence[str], starts: Sequence[int]) -> int:
    if not lines:
        return 0
    return int(starts[len(lines) - 1]) + len(str(lines[-1]))


def line_start_offsets_for_lines(lines: Sequence[str] | None) -> Sequence[int]:
    """Return compact flat offsets for one canonical line vector."""

    return compact_line_start_offsets_for_lines(lines)


def cursor_to_offset_lines(
    lines: Sequence[str],
    starts: Sequence[int],
    cursor: Cursor,
) -> int:
    """Clamp a line/column cursor and return its flat line-vector offset."""

    if not lines:
        return 0
    line = max(0, min(int(cursor.line), len(lines) - 1))
    col = max(0, min(int(cursor.col), len(str(lines[line]))))
    return int(starts[line]) + col


def offset_to_cursor_lines(
    lines: Sequence[str],
    starts: Sequence[int],
    offset: int,
    *,
    source_length: int | None = None,
) -> Cursor:
    """Convert one clamped flat offset into line-vector coordinates."""

    if not lines:
        return Cursor(0, 0)
    length = (
        _line_vector_source_length(lines, starts)
        if source_length is None
        else int(source_length)
    )
    pos = max(0, min(int(offset), length))
    line = max(0, bisect_right(starts, pos) - 1)
    line = min(line, len(lines) - 1)
    col = max(0, min(pos - int(starts[line]), len(str(lines[line]))))
    return Cursor(int(line), int(col))


def _line_vector_range_text(
    lines: Sequence[str],
    start: Cursor,
    end: Cursor,
) -> str:
    if int(start.line) == int(end.line):
        return str(lines[int(start.line)])[int(start.col) : int(end.col)]

    parts = [str(lines[int(start.line)])[int(start.col) :]]
    parts.extend(
        str(lines[line])
        for line in range(int(start.line) + 1, int(end.line))
    )
    parts.append(str(lines[int(end.line)])[: int(end.col)])
    return "\n".join(parts)


def _line_vector_range_equals(
    lines: Sequence[str],
    start: Cursor,
    end: Cursor,
    expected: str,
) -> bool:
    """Compare one canonical source range without joining that source range.

    Suppressed aggregate owners do not retain per-action history.  They still
    need to distinguish sidecar-only equal replacements from actual text edits,
    but materializing a large selected source slice solely for that boolean is
    discarded work.  Compare replacement pieces against source-line windows
    instead; allocations are bounded by the caller-authored replacement text.
    """

    value = str(expected)
    start_line = int(start.line)
    end_line = int(end.line)
    start_col = int(start.col)
    end_col = int(end.col)

    if start_line == end_line:
        if "\n" in value or len(value) != end_col - start_col:
            return False
        return str(lines[start_line]).startswith(value, start_col, end_col)

    pieces = value.split("\n")
    if len(pieces) != end_line - start_line + 1:
        return False

    first = str(lines[start_line])
    if len(pieces[0]) != len(first) - start_col:
        return False
    if not first.startswith(pieces[0], start_col):
        return False

    for line_index, piece in enumerate(pieces[1:-1], start=start_line + 1):
        if str(lines[line_index]) != piece:
            return False

    last = str(lines[end_line])
    return len(pieces[-1]) == end_col and last.startswith(pieces[-1], 0, end_col)


class _LineVectorReplayBuilder:
    """Build one canonical result vector while reusing untouched full lines."""

    def __init__(self, lines: Sequence[str]) -> None:
        self._source = lines
        self._source_line = 0
        self._source_col = 0
        self._result: list[str] = []
        self._pending: list[str] = []

    def _append_fragment(self, text: str) -> None:
        value = str(text)
        if value:
            self._pending.append(value)

    def _finish_line(self) -> None:
        if not self._pending:
            self._result.append("")
        elif len(self._pending) == 1:
            self._result.append(self._pending[0])
        else:
            self._result.append("".join(self._pending))
        self._pending.clear()

    def emit_source_to(self, target: Cursor) -> None:
        target_line = int(target.line)
        target_col = int(target.col)
        while self._source_line < target_line:
            source_line = str(self._source[self._source_line])
            if self._source_col == 0 and not self._pending:
                # A complete unchanged line can keep its exact string object.
                self._result.append(source_line)
            else:
                self._append_fragment(source_line[self._source_col :])
                self._finish_line()
            self._source_line += 1
            self._source_col = 0

        source_line = str(self._source[self._source_line])
        if target_col > self._source_col:
            self._append_fragment(source_line[self._source_col : target_col])
        self._source_col = target_col

    def skip_source_to(self, target: Cursor) -> None:
        self._source_line = int(target.line)
        self._source_col = int(target.col)

    def emit_replacement(self, text: str) -> None:
        value = str(text)
        start = 0
        while True:
            newline = value.find("\n", start)
            if newline < 0:
                self._append_fragment(value[start:])
                return
            self._append_fragment(value[start:newline])
            self._finish_line()
            start = newline + 1

    def finish(self) -> list[str]:
        self._finish_line()
        return self._result or [""]


def _build_line_vector_replacements(
    lines: Sequence[str],
    replacements: Sequence[tuple[Cursor, Cursor, str]],
) -> list[str]:
    """Build one detached vector from prevalidated, ordered replacements."""

    if not replacements:
        return list(lines)

    builder = _LineVectorReplayBuilder(lines)
    for start_cursor, end_cursor, replacement in replacements:
        builder.emit_source_to(start_cursor)
        builder.emit_replacement(replacement)
        builder.skip_source_to(end_cursor)

    final_cursor = Cursor(len(lines) - 1, len(str(lines[-1])))
    builder.emit_source_to(final_cursor)
    return builder.finish()


def _line_vectors_equal(left: Sequence[str], right: Sequence[str]) -> bool:
    """Compare canonical line vectors without flattening or reboxing either one."""

    if len(left) != len(right):
        return False
    return all(
        left_line is right_line or str(left_line) == str(right_line)
        for left_line, right_line in zip(left, right, strict=True)
    )


def _apply_replay_rows_to_line_vector(
    lines: Sequence[str],
    starts: Sequence[int],
    *,
    source_length: int,
    rows: Sequence[_ReplayRow],
) -> list[str]:
    """Validate and build one detached line-vector result for ``rows``."""

    cursor_ranges: dict[tuple[int, int], tuple[Cursor, Cursor]] = {}

    def _range_for(start: int, end: int) -> tuple[Cursor, Cursor]:
        key = (int(start), int(end))
        cached = cursor_ranges.get(key)
        if cached is not None:
            return cached
        pair = (
            offset_to_cursor_lines(
                lines,
                starts,
                int(start),
                source_length=source_length,
            ),
            offset_to_cursor_lines(
                lines,
                starts,
                int(end),
                source_length=source_length,
            ),
        )
        cursor_ranges[key] = pair
        return pair

    _validate_replay_rows(
        rows,
        source_length=source_length,
        read_slice=lambda start, end: _line_vector_range_text(
            lines,
            *_range_for(start, end),
        ),
    )

    return _build_line_vector_replacements(
        lines,
        tuple(
            (*_range_for(row.start, row.end), str(row.replacement))
            for row in rows
        ),
    )


def replay_simultaneous_edit_witness_lines(
    source_lines: Sequence[str],
    witness: SimultaneousEditWitness,
    *,
    undo: bool,
) -> list[str]:
    """Return one atomically validated sparse replay as a canonical line vector.

    The source line objects are snapshotted by reference.  Validation reads only
    witnessed slices.  Construction then walks the source once, reuses complete
    untouched line strings, joins only touched output lines, and returns one
    detached vector for a single :meth:`Buffer.replace_lines` commit.

    Empty expected slices retain the same zero-width authentication limit as the
    flat-text oracle.  The input must be Buffer's canonical LF-free line vector.
    """

    lines = (
        source_lines
        if isinstance(source_lines, tuple)
        else tuple(str(line) for line in source_lines)
    ) or ("",)
    starts = compact_line_start_offsets_for_lines(lines)
    source_length = _line_vector_source_length(lines, starts)
    rows = _replay_rows(witness, undo=bool(undo))
    return _apply_replay_rows_to_line_vector(
        lines,
        starts,
        source_length=source_length,
        rows=rows,
    )


def line_start_offsets(text: str) -> Sequence[int]:
    """Return compact flat offsets for every logical line start."""

    return compact_line_start_offsets(text)


def cursor_to_offset(text: str, starts: Sequence[int], cursor: Cursor) -> int:
    """Clamp one cursor to ``text`` and return its flat character offset."""

    s = str(text)
    if not starts:
        starts = (0,)
    line = max(0, min(int(cursor.line), len(starts) - 1))
    line_start = int(starts[line])
    if line + 1 < len(starts):
        line_end = int(starts[line + 1]) - 1  # exclude the separating newline
    else:
        line_end = len(s)
    col = max(0, min(int(cursor.col), max(0, line_end - line_start)))
    return line_start + col


def offset_to_cursor(text: str, starts: Sequence[int], offset: int) -> Cursor:
    """Convert a clamped flat offset into editor line/column coordinates."""

    s = str(text)
    if not starts:
        starts = (0,)
    pos = max(0, min(int(offset), len(s)))
    line = max(0, bisect_right(starts, pos) - 1)
    return Cursor(int(line), int(pos - int(starts[line])))


def map_cursor_through_replacement(
    cursor: Cursor,
    *,
    start: Cursor,
    old_end: Cursor,
    new_end: Cursor,
    affinity: str = "right",
) -> Cursor:
    """Map one line/column position through a single replacement.

    A one-range edit does not need a flattened source document merely to move
    cursor and selection sidecars.  Text before ``start`` is unchanged; text
    inside the replaced range collapses to the selected affinity; and text
    after ``old_end`` moves by the replacement's line/column geometry.

    ``right`` matches :meth:`SimultaneousEditPlan.map_offset`, the editor's
    ordinary behavior for insertions and replacements.  ``left`` is kept here
    as the exact local analogue for callers that need the opposite boundary.
    Inputs are expected to be clamped coordinates from one pre-edit buffer.
    """

    pos = Cursor(int(cursor.line), int(cursor.col))
    begin = Cursor(int(start.line), int(start.col))
    end = Cursor(int(old_end.line), int(old_end.col))
    result_end = Cursor(int(new_end.line), int(new_end.col))
    if (end.line, end.col) < (begin.line, begin.col):
        begin, end = end, begin

    point = (int(pos.line), int(pos.col))
    begin_key = (int(begin.line), int(begin.col))
    end_key = (int(end.line), int(end.col))
    right = str(affinity) != "left"

    if point < begin_key or (not right and point == begin_key):
        return pos

    if begin_key == end_key:
        if point == begin_key:
            return result_end if right else begin
    elif begin_key < point < end_key or (right and point == begin_key):
        return result_end if right else begin

    # The old end boundary is also the new end boundary after replacement.
    # This falls naturally out of the suffix mapping below and keeps left and
    # right affinity identical at the half-open range's far edge.
    if point >= end_key:
        if int(pos.line) == int(end.line):
            return Cursor(
                int(result_end.line),
                int(result_end.col) + int(pos.col) - int(end.col),
            )
        return Cursor(
            int(pos.line) + int(result_end.line) - int(end.line),
            int(pos.col),
        )

    return result_end if right else begin


def _indexed_inputs(
    original_text: str,
    edits: Iterable[SimultaneousTextEdit],
    *,
    source_starts: Sequence[int] | None = None,
) -> list[tuple[int, int, str, int | None]]:
    # ``source_starts`` is an immutable-generation witness supplied by the
    # editor.  Reboxing every cell into a tuple duplicated the complete line
    # index immediately before a multi-edit plan.  The planner only needs the
    # ordinary Sequence surface, so retain the caller's compact owner directly.
    starts: Sequence[int]
    if source_starts is None or len(source_starts) <= 0:
        starts = line_start_offsets(original_text)
    else:
        starts = source_starts
    out: list[tuple[int, int, str, int | None]] = []
    seen_owners: set[int] = set()
    for request in edits:
        start = cursor_to_offset(original_text, starts, request.start)
        end = cursor_to_offset(original_text, starts, request.end)
        if end < start:
            start, end = end, start
        owner = None if request.owner is None else int(request.owner)
        if owner is not None:
            if owner in seen_owners:
                raise SimultaneousEditError(f"cursor {owner} owns more than one edit")
            seen_owners.add(owner)
        out.append((start, end, normalize_buffer_text(request.text), owner))
    return out


def _indexed_line_inputs(
    source_lines: Sequence[str],
    edits: Iterable[SimultaneousTextEdit],
    *,
    source_starts: Sequence[int],
) -> list[tuple[int, int, str, int | None]]:
    """Index cursor requests directly against one canonical line vector."""

    out: list[tuple[int, int, str, int | None]] = []
    seen_owners: set[int] = set()
    for request in edits:
        start = cursor_to_offset_lines(source_lines, source_starts, request.start)
        end = cursor_to_offset_lines(source_lines, source_starts, request.end)
        if end < start:
            start, end = end, start
        owner = None if request.owner is None else int(request.owner)
        if owner is not None:
            if owner in seen_owners:
                raise SimultaneousEditError(f"cursor {owner} owns more than one edit")
            seen_owners.add(owner)
        out.append((start, end, normalize_buffer_text(request.text), owner))
    return out


def _build_indexed_edits(
    raw: list[tuple[int, int, str, int | None]],
    *,
    source_length: int,
) -> tuple[
    tuple[_IndexedEdit, ...],
    tuple[int, ...],
    tuple[tuple[int, int], ...],
    int,
]:
    """Share duplicate coalescing, conflict refusal, and offset geometry."""

    raw.sort(
        key=lambda item: (
            item[0],
            item[1],
            item[2],
            -1 if item[3] is None else item[3],
        )
    )

    merged: list[tuple[int, int, str, list[int]]] = []
    for start, end, text, owner in raw:
        if merged and (start, end, text) == merged[-1][:3]:
            if owner is not None:
                merged[-1][3].append(owner)
            continue
        owners = [] if owner is None else [owner]
        merged.append((start, end, text, owners))

    max_end = -1
    previous_start: int | None = None
    for start, end, _text, _owners in merged:
        if start < 0 or end < start or end > int(source_length):
            raise SimultaneousEditError(
                f"invalid edit offsets {start}..{end} for {int(source_length)} chars"
            )
        # Exact duplicates were already merged. Any other edits sharing a
        # start are order-dependent (including insertion + replacement).
        if previous_start is not None and start == previous_start:
            raise SimultaneousEditError(f"conflicting edits start at offset {start}")
        if start < max_end:
            raise SimultaneousEditError(
                f"overlapping edit ranges near offsets {start}..{max(end, max_end)}"
            )
        previous_start = start
        max_end = max(max_end, end)

    indexed: list[_IndexedEdit] = []
    owner_offsets: list[tuple[int, int]] = []
    cumulative_delta = 0
    for start, end, text, owners in merged:
        new_start = int(start) + int(cumulative_delta)
        new_end = int(new_start) + len(text)
        cumulative_delta += len(text) - (int(end) - int(start))

        for owner in owners:
            owner_offsets.append((int(owner), int(new_end)))
        indexed.append(
            _IndexedEdit(
                start=int(start),
                end=int(end),
                text=str(text),
                owners=tuple(int(owner) for owner in owners),
                new_start=int(new_start),
                new_end=int(new_end),
                delta_after=int(cumulative_delta),
            )
        )

    owner_offsets.sort(key=lambda row: row[0])
    indexed_rows = tuple(indexed)
    return (
        indexed_rows,
        tuple(edit.start for edit in indexed_rows),
        tuple(owner_offsets),
        int(source_length) + int(cumulative_delta),
    )


def plan_simultaneous_edits(
    original_text: str,
    edits: Iterable[SimultaneousTextEdit],
    *,
    source_starts: Sequence[int] | None = None,
) -> SimultaneousEditPlan:
    """Validate and merge edits that all refer to ``original_text``.

    Exact duplicate edits coalesce (including their cursor owners).  Any other
    same-start or overlapping ranges are ambiguous and fail closed.  Adjacent
    ranges remain valid.  Editor callers that already flattened cursor
    positions may pass ``source_starts`` to avoid rescanning the same immutable
    document solely to rebuild its line-start index.
    """

    raw_source_text = str(original_text)
    source_text = normalize_buffer_text(raw_source_text)
    # A caller-supplied line index is valid only for the exact text generation
    # it indexed.  CRLF/CR normalization changes flat offsets, so discard a
    # stale pre-normalization index rather than silently misaddressing edits.
    effective_starts = source_starts if raw_source_text == source_text else None
    raw = _indexed_inputs(source_text, edits, source_starts=effective_starts)
    indexed, edit_starts, owner_offsets, _result_length = _build_indexed_edits(
        raw,
        source_length=len(source_text),
    )

    parts: list[str] = []
    source_at = 0
    for edit in indexed:
        parts.append(source_text[source_at : int(edit.start)])
        parts.append(str(edit.text))
        source_at = int(edit.end)

    parts.append(source_text[source_at:])
    new_text = "".join(parts)
    return SimultaneousEditPlan(
        original_text=source_text,
        new_text=new_text,
        edits=indexed,
        edit_starts=edit_starts,
        owner_offsets=owner_offsets,
    )


def plan_simultaneous_edits_lines(
    source_lines: Sequence[str],
    edits: Iterable[SimultaneousTextEdit],
    *,
    source_starts: Sequence[int] | None = None,
    capture_history_witness: bool = True,
) -> LineVectorSimultaneousEditPlan:
    """Plan and build one atomic multi-range edit without flat documents.

    All request coordinates address one immutable canonical line-vector
    snapshot. Exact duplicate edits coalesce, ambiguous overlap fails before
    result construction. When requested, the sparse witness authenticates only
    changed slices; suppressed aggregate owners may skip that discarded capture.
    The detached result vector reuses complete untouched line strings and joins
    only touched output lines.
    """

    lines = (
        source_lines
        if isinstance(source_lines, tuple)
        else tuple(str(line) for line in source_lines)
    ) or ("",)
    starts: Sequence[int]
    if source_starts is None or len(source_starts) != len(lines):
        starts = compact_line_start_offsets_for_lines(lines)
    else:
        starts = source_starts
    source_length = _line_vector_source_length(lines, starts)
    raw = _indexed_line_inputs(lines, edits, source_starts=starts)
    indexed, edit_starts, owner_offsets, result_length = _build_indexed_edits(
        raw,
        source_length=source_length,
    )

    changed_rows: list[tuple[_IndexedEdit, Cursor, Cursor, str]] = []
    for edit in indexed:
        start_cursor = offset_to_cursor_lines(
            lines,
            starts,
            int(edit.start),
            source_length=source_length,
        )
        end_cursor = offset_to_cursor_lines(
            lines,
            starts,
            int(edit.end),
            source_length=source_length,
        )
        replacement = str(edit.text)
        changed = (
            len(replacement) != int(edit.end) - int(edit.start)
            or not _line_vector_range_equals(
                lines,
                start_cursor,
                end_cursor,
                replacement,
            )
        )
        if not changed:
            continue

        changed_rows.append((edit, start_cursor, end_cursor, replacement))

    if changed_rows:
        candidate_lines: Sequence[str] = _build_line_vector_replacements(
            lines,
            [
                (start_cursor, end_cursor, replacement)
                for _edit, start_cursor, end_cursor, replacement in changed_rows
            ],
        )
        # Component replacements can cancel into the exact source generation.
        # Compare vectors without flattening: complete untouched strings
        # short-circuit by identity, so only rebuilt touched lines need content
        # comparison. A net-zero result must not dirty/version the buffer.
        text_changed = not _line_vectors_equal(candidate_lines, lines)
        if text_changed:
            new_lines = candidate_lines
            result_starts = compact_line_start_offsets_for_lines(new_lines)
        else:
            new_lines = lines
            result_starts = starts
    else:
        text_changed = False
        # A sidecar-only plan has the exact source generation as its result.
        # Reuse the caller-owned immutable coordinate witness rather than
        # allocating and rescanning an identical complete line-start vector.
        new_lines = lines
        result_starts = starts

    witness: SimultaneousEditWitness | None = None
    if capture_history_witness:
        splices: list[SimultaneousTextSplice] = []
        if text_changed:
            for edit, start_cursor, end_cursor, replacement in changed_rows:
                splices.append(
                    SimultaneousTextSplice(
                        old_start=int(edit.start),
                        old_end=int(edit.end),
                        new_start=int(edit.new_start),
                        new_end=int(edit.new_end),
                        old_text=_line_vector_range_text(
                            lines,
                            start_cursor,
                            end_cursor,
                        ),
                        new_text=replacement,
                    )
                )
        witness = SimultaneousEditWitness(splices=tuple(splices))

    actual_result_length = _line_vector_source_length(new_lines, result_starts)
    if actual_result_length != int(result_length):
        raise RuntimeError(
            "simultaneous line-vector result length mismatch: "
            f"expected {int(result_length)}, built {actual_result_length}"
        )

    return LineVectorSimultaneousEditPlan(
        new_lines=new_lines,
        result_starts=result_starts,
        source_length=int(source_length),
        result_length=int(result_length),
        edits=indexed,
        edit_starts=edit_starts,
        owner_offsets=owner_offsets,
        text_changed=text_changed,
        history_witness=witness,
    )
