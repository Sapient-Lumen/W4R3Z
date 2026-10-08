from __future__ import annotations

"""Query-replace identity, source-generation, and coordinate witnesses.

Query-replace spans multiple keypresses. A mutable display name is therefore
not enough authority to identify the buffer that may be edited or whose undo
snapshot must be finalized: buffers can be renamed, closed, and later replaced
under the same name while the interaction is live. Match coordinates are also
valid only for the exact text generation that produced them.

The delayed interaction additionally needs a trustworthy view of its original
text. Retaining ``"\n".join(lines)`` duplicates a complete many-line document.
``QueryReplaceSourceSnapshot`` instead owns a shallow tuple of immutable line
objects plus compact packed line starts. Untouched strings remain shared with
the live buffer, while the tuple and private coordinate owner are detached from
future list mutation.
"""

from bisect import bisect_right
from dataclasses import dataclass, field
from typing import Sequence
import weakref

from .buffer import Cursor
from .textpos import PackedOffsets, line_start_offsets_for_lines


def advance_cursor_through_text_span(
    cursor: Cursor,
    text: str,
    start: int,
    end: int,
) -> Cursor:
    """Advance through one bounded canonical-text span without slicing it.

    This flat-string helper remains the executable geometry oracle used by
    focused tests and small callers. Product query-replace navigation uses the
    line-coordinate sibling below so it does not require a retained document
    string.
    """

    origin = Cursor(int(cursor.line), int(cursor.col))
    value = str(text)
    left = max(0, min(int(start), len(value)))
    right = max(left, min(int(end), len(value)))
    newline_count = value.count("\n", left, right)
    if newline_count <= 0:
        return Cursor(int(origin.line), int(origin.col) + right - left)
    last_newline = value.rfind("\n", left, right)
    return Cursor(
        int(origin.line) + int(newline_count),
        int(right - last_newline - 1),
    )


def advance_cursor_through_source_span(
    cursor: Cursor,
    source_start: Cursor,
    source_end: Cursor,
) -> Cursor:
    """Advance ``cursor`` by one source span expressed as line coordinates.

    Query-replace consumes planned source spans monotonically. When the span
    stays on one line, only its column width matters. Once it crosses a newline,
    the resulting column is exactly the source end column, independent of the
    current mapped column. This is the line-vector equivalent of counting and
    locating newlines in a flat string.
    """

    origin = Cursor(int(cursor.line), int(cursor.col))
    left = Cursor(int(source_start.line), int(source_start.col))
    right = Cursor(int(source_end.line), int(source_end.col))
    line_delta = int(right.line) - int(left.line)
    if line_delta <= 0:
        return Cursor(
            int(origin.line),
            int(origin.col) + max(0, int(right.col) - int(left.col)),
        )
    return Cursor(int(origin.line) + line_delta, int(right.col))


def advance_cursor_by_text(cursor: Cursor, text: str) -> Cursor:
    """Return the cursor reached after traversing canonical buffer ``text``."""

    value = str(text)
    return advance_cursor_through_text_span(cursor, value, 0, len(value))


@dataclass(frozen=True, slots=True)
class QueryReplaceSourceSnapshot:
    """Shallow immutable source generation for one delayed query-replace.

    ``lines`` shares immutable string objects with :class:`Buffer`; only its
    pointer tuple is new. ``_line_starts`` privately owns packed ``array('Q')``
    cells containing one flat start offset per logical line and exposes only a
    read-only sequence. It gives O(log n) projection without one Python integer
    object per line, a complete LF-joined string, or an array-to-bytes copy.
    """

    lines: tuple[str, ...]
    length: int
    _line_starts: PackedOffsets = field(repr=False)

    @classmethod
    def capture(cls, lines: Sequence[str] | None) -> "QueryReplaceSourceSnapshot":
        if isinstance(lines, tuple) and all(isinstance(line, str) for line in lines):
            source_lines = lines or ("",)
        else:
            source_lines = tuple(str(line) for line in (lines or ())) or ("",)
        starts = line_start_offsets_for_lines(source_lines)
        source_length = int(starts[len(source_lines) - 1]) + len(source_lines[-1])
        return cls(
            lines=source_lines,
            length=source_length,
            _line_starts=PackedOffsets._from_owned_array(starts),
        )

    def __deepcopy__(self, memo: dict[int, object]) -> "QueryReplaceSourceSnapshot":
        """Keep the immutable generation shared across runtime snapshots."""

        memo[id(self)] = self
        return self

    @property
    def line_count(self) -> int:
        return len(self.lines)

    @property
    def coordinate_bytes(self) -> int:
        return int(self._line_starts.storage_bytes)

    @property
    def line_starts(self) -> PackedOffsets:
        """Return the read-only compact canonical line-start sequence."""

        return self._line_starts

    def contains_offsets(self, start: int, end: int) -> bool:
        left = int(start)
        right = int(end)
        return 0 <= left <= right <= int(self.length)

    def cursor_at(self, offset: int) -> Cursor:
        """Project one clamped flat source offset to line/column coordinates."""

        pos = max(0, min(int(offset), int(self.length)))
        starts = self._line_starts
        line = max(0, bisect_right(starts, pos) - 1)
        line = min(line, len(self.lines) - 1)
        col = max(0, min(pos - int(starts[line]), len(self.lines[line])))
        return Cursor(int(line), int(col))

    def offset_at(self, cursor: Cursor) -> int:
        """Clamp one source cursor and return its canonical flat offset."""

        starts = self._line_starts
        line = max(0, min(int(cursor.line), len(self.lines) - 1))
        col = max(0, min(int(cursor.col), len(self.lines[line])))
        return int(starts[line]) + col

    def range_text(self, start: Cursor, end: Cursor) -> str:
        """Materialize exactly one source range, never the complete document."""

        left = self.cursor_at(self.offset_at(start))
        right = self.cursor_at(self.offset_at(end))
        if (int(right.line), int(right.col)) < (int(left.line), int(left.col)):
            left, right = right, left
        if int(left.line) == int(right.line):
            return self.lines[int(left.line)][int(left.col) : int(right.col)]
        parts = [self.lines[int(left.line)][int(left.col) :]]
        parts.extend(self.lines[int(left.line) + 1 : int(right.line)])
        parts.append(self.lines[int(right.line)][: int(right.col)])
        return "\n".join(parts)

    def range_text_offsets(self, start: int, end: int) -> str:
        left = max(0, min(int(start), int(self.length)))
        right = max(left, min(int(end), int(self.length)))
        return self.range_text(self.cursor_at(left), self.cursor_at(right))

    def materialize_text(self) -> str:
        """Return the complete canonical text for compatibility and test oracles."""

        return "\n".join(self.lines)


@dataclass(frozen=True)
class QueryReplaceBufferWitness:
    """Weak identity and text generation for one query-replace session."""

    name: str
    version: int | None
    _ref: weakref.ReferenceType[object] = field(compare=False, repr=False)

    @classmethod
    def capture(cls, name: object, editor_buffer: object) -> "QueryReplaceBufferWitness":
        return cls(
            name=str(name),
            version=cls._buffer_version(editor_buffer),
            _ref=weakref.ref(editor_buffer),
        )

    @staticmethod
    def _buffer_version(editor_buffer: object) -> int | None:
        """Return the editor buffer's text version when the host exposes one."""

        try:
            raw = getattr(getattr(editor_buffer, "buf"), "version")
            return int(raw)
        except (AttributeError, TypeError, ValueError):
            return None

    def resolve(self) -> object | None:
        """Return the captured object while it is still alive."""

        return self._ref()

    def is_current(self, editor_buffer: object | None = None) -> bool:
        """Return whether identity and the captured text generation still match.

        ``None`` versions preserve compatibility with alternate/legacy buffer
        hosts that do not expose a revision counter; production editor buffers
        always provide one.
        """

        target = self.resolve()
        if target is None:
            return False
        if editor_buffer is not None and target is not editor_buffer:
            return False
        current = self._buffer_version(target)
        if self.version is None:
            return True
        if current is None:
            return False
        return int(current) == int(self.version)

    def refresh(self, name: object, editor_buffer: object) -> "QueryReplaceBufferWitness":
        """Capture the new generation of the same live editor buffer."""

        if self.resolve() is not editor_buffer:
            raise ValueError("query-replace witness identity changed")
        return type(self).capture(name, editor_buffer)
