from __future__ import annotations

"""Small helpers for converting between Cursor coordinates and flat text offsets.

These are deliberately boring and deterministic.

Why a tiny module?

- Search and replace are both much easier to implement over flat indices.
- The editor core is line-based and exposes Cursor(line,col).
- Keeping a *single* implementation avoids drift between features.
"""

from array import array
from collections.abc import Iterable, Iterator, Sequence

from .buffer import Buffer, Cursor


# Flat editor coordinates cannot exceed Python's own string/list address space,
# so an unsigned 64-bit cell is ample while avoiding one Python ``int`` object
# per logical line.  ``array('Q')`` is already used by the softwrap prefix index
# for the same reason.
OFFSET_TYPECODE = "Q"


class PackedOffsets(Sequence[int]):
    """Read-only unsigned offsets backed by one compact native array.

    Coordinate snapshots live across editor interactions and history checks. A
    tuple of Python ``int`` objects is needlessly expensive, so the owner keeps
    offsets in private ``array('Q')`` cells while exposing only a read-only
    sequence surface. ``_from_owned_array`` transfers an unpublished array
    without the temporary full-size copy a bytes image would require.
    """

    __slots__ = ("_values",)

    def __init__(self, values: Iterable[int] = ()) -> None:
        self._values = array(
            OFFSET_TYPECODE,
            (max(0, int(value)) for value in values),
        )

    @classmethod
    def _from_owned_array(cls, values: array) -> "PackedOffsets":
        if values.typecode != OFFSET_TYPECODE:
            raise ValueError(
                f"packed offset array must use {OFFSET_TYPECODE!r} cells"
            )
        result = cls.__new__(cls)
        result._values = values
        return result

    @property
    def storage_bytes(self) -> int:
        return int(self._values.itemsize * len(self._values))

    def __len__(self) -> int:
        return len(self._values)

    def __getitem__(self, index: int | slice) -> int | tuple[int, ...]:
        if isinstance(index, slice):
            indices = range(*index.indices(len(self)))
            return tuple(int(self._values[item]) for item in indices)
        return int(self._values[index])

    def __iter__(self) -> Iterator[int]:
        return (int(value) for value in self._values)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, PackedOffsets):
            return self._values == other._values
        if isinstance(other, Sequence):
            return len(self) == len(other) and all(
                int(left) == int(right)
                for left, right in zip(self, other, strict=True)
            )
        return NotImplemented

    def __repr__(self) -> str:
        count = len(self)
        if count <= 8:
            return f"PackedOffsets({tuple(self)!r})"
        head = tuple(self[index] for index in range(4))
        tail = tuple(self[index] for index in range(count - 4, count))
        return f"PackedOffsets({head!r} ... {tail!r}, count={count})"


def line_start_offsets(text: str) -> array:
    """Return compact flat offsets for every LF-delimited logical line.

    The returned mutable array is owned by the caller.  Treat it as immutable
    once published as a coordinate witness; ``bisect`` and ordinary sequence
    indexing operate directly on it without reboxing the complete vector.
    """

    source = str(text)
    starts = array(OFFSET_TYPECODE, [0])
    search_from = 0
    while True:
        newline = source.find("\n", search_from)
        if newline < 0:
            break
        search_from = newline + 1
        starts.append(search_from)
    return starts


def line_start_offsets_for_lines(lines: Sequence[str] | None) -> array:
    """Return compact flat offsets for an authoritative line vector."""

    starts = array(OFFSET_TYPECODE)
    offset = 0
    if lines is not None:
        for line in lines:
            starts.append(offset)
            offset += len(str(line)) + 1
    if not starts:
        starts.append(0)
    return starts


def cursor_to_index(buf: Buffer, cur: Cursor) -> int:
    """Convert a Cursor to a 0-based character offset into buf.get_text()."""
    cur = buf.clamp(cur)
    idx = 0
    for li in range(int(cur.line)):
        idx += len(buf.lines[li]) + 1  # + '\n'
    idx += int(cur.col)
    return idx


def index_to_cursor(buf: Buffer, idx: int) -> Cursor:
    """Convert a 0-based character offset into buf.get_text() into a Cursor."""
    if idx <= 0:
        return Cursor(0, 0)

    s = buf.get_text()
    idx2 = min(int(idx), len(s))
    line = s.count("\n", 0, idx2)
    last_nl = s.rfind("\n", 0, idx2)
    col = idx2 if last_nl < 0 else idx2 - last_nl - 1
    return buf.clamp(Cursor(int(line), int(col)))
