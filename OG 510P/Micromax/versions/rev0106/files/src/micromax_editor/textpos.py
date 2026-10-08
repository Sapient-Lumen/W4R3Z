from __future__ import annotations

"""Small helpers for converting between Cursor coordinates and flat text offsets.

These are deliberately boring and deterministic.

Why a tiny module?

- Search and replace are both much easier to implement over flat indices.
- The editor core is line-based and exposes Cursor(line,col).
- Keeping a *single* implementation avoids drift between features.
"""

from .buffer import Buffer, Cursor


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
