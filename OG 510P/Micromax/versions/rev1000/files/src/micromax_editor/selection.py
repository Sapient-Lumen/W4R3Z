from __future__ import annotations

from dataclasses import dataclass

from .buffer import Cursor


# Rendering a screen must remain bounded even when a script constructs a very
# large multicursor set.  The primary selection is always considered; this is
# the maximum total number of cursor ranges considered for one visible
# snapshot.
VISIBLE_SELECTION_MAX_RANGES = 4096


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


@dataclass(frozen=True)
class VisibleSelectionFragment:
    """Visible part of one logical selection on one rendered row fragment.

    ``start`` and ``end`` are fragment-local character coordinates. ``eol_x``
    names the blank cell immediately after the logical line when the selection
    includes that line break; renderers may omit it when no visible cell exists.
    """

    start: int
    end: int
    eol_x: int | None = None

    def has_text(self) -> bool:
        return int(self.end) > int(self.start)


def visible_selection_fragment(
    selection: Selection,
    *,
    line_index: int,
    line_length: int,
    fragment_start: int,
    fragment_length: int,
    display_offset: int = 0,
) -> VisibleSelectionFragment | None:
    """Project a half-open logical selection onto one visible line fragment.

    The helper does not allocate or inspect source text.  It therefore remains
    constant work per selection and works for horizontal scrolling and
    softwrapped rows. ``display_offset`` accounts for renderer-owned cells
    before the source fragment, such as continuation indentation. A logical
    newline is represented separately as ``eol_x`` so empty-line and
    newline-only selections do not become visually invisible.
    """

    s, e = selection.normalized()
    li = int(line_index)
    if li < int(s.line) or li > int(e.line):
        return None

    line_n = max(0, int(line_length))
    frag_start = max(0, int(fragment_start))
    frag_len = max(0, int(fragment_length))
    offset = max(0, int(display_offset))
    frag_end = frag_start + frag_len

    selected_start = int(s.col) if li == int(s.line) else 0
    selected_end = int(e.col) if li == int(e.line) else line_n
    selected_start = max(0, min(line_n, selected_start))
    selected_end = max(0, min(line_n, selected_end))

    clipped_start = max(selected_start, frag_start)
    clipped_end = min(selected_end, frag_end)
    source_local_start = max(0, clipped_start - frag_start)
    source_local_end = max(source_local_start, clipped_end - frag_start)
    local_start = offset + source_local_start
    local_end = offset + source_local_end

    # A selection contains this line's newline exactly when it continues onto a
    # later logical line.  Expose the blank after EOL only from the final visible
    # fragment of this line; the renderer still checks that the cell fits.
    eol_x: int | None = None
    if (
        li < int(e.line)
        and int(s.line) <= li
        and frag_start <= line_n <= frag_end
    ):
        eol_x = offset + max(0, line_n - frag_start)

    if local_end <= local_start and eol_x is None:
        return None
    return VisibleSelectionFragment(
        start=int(local_start),
        end=int(local_end),
        eol_x=eol_x,
    )
