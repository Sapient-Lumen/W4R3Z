from __future__ import annotations

import re
from dataclasses import dataclass

from .buffer import Buffer, Cursor
from .textpos import cursor_to_index, index_to_cursor


@dataclass
class SearchState:
    query: str = ""
    literal: bool = True
    case_sensitive: bool = False
    last_match: Cursor | None = None


def match_start_indices(buf: Buffer, state: SearchState) -> list[int]:
    """Return start indices for non-empty matches of ``state`` in ``buf``.

    This is a tiny whole-buffer helper for status/TUI surfaces that want a
    shared search-position model (for example ``1/7``) without having to
    reimplement literal/regex + ignorecase semantics themselves.

    Policy:
      - empty queries return ``[]``
      - literal searches return every non-overlapping substring hit
      - regex searches return every **non-empty** match start; zero-width
        matches are ignored so lightweight UX surfaces do not pretend invisible
        cursor-stationary matches are meaningful navigation targets
    """

    q = state.query
    if not q:
        return []

    hay = buf.get_text()
    flags = 0
    if not state.case_sensitive:
        flags |= re.IGNORECASE

    if state.literal:
        needle = q
        hay2 = hay
        if flags & re.IGNORECASE:
            needle = needle.casefold()
            hay2 = hay2.casefold()
        if not needle:
            return []
        out: list[int] = []
        start = 0
        while True:
            pos = hay2.find(needle, start)
            if pos < 0:
                return out
            out.append(int(pos))
            start = int(pos + max(1, len(needle)))

    try:
        rx = re.compile(q, flags)
    except re.error:
        return []

    out: list[int] = []
    for m in rx.finditer(hay):
        a = int(m.start())
        b = int(m.end())
        if b > a:
            out.append(a)
    return out


def search_position(buf: Buffer, state: SearchState, *, cursor: Cursor) -> tuple[int, int]:
    """Return ``(current, total)`` search-position counts for ``cursor``.

    ``current`` is 1-based when the cursor is sitting exactly on a known match
    start for the active search, otherwise ``0``. ``total`` is the number of
    non-empty matches in the whole buffer.
    """

    starts = match_start_indices(buf, state)
    total = int(len(starts))
    if total <= 0:
        return (0, 0)
    cur_i = cursor_to_index(buf, cursor)
    try:
        idx = starts.index(int(cur_i)) + 1
    except ValueError:
        idx = 0
    return (int(idx), total)

def find_next(buf: Buffer, state: SearchState, *, start: Cursor) -> Cursor | None:
    """Find the next occurrence of state.query starting at `start`."""

    q = state.query
    if not q:
        return None

    hay = buf.get_text()
    start_i = cursor_to_index(buf, start)

    flags = 0
    if not state.case_sensitive:
        flags |= re.IGNORECASE

    if state.literal:
        if flags & re.IGNORECASE:
            hay_l = hay.lower()
            q_l = q.lower()
            pos = hay_l.find(q_l, start_i)
        else:
            pos = hay.find(q, start_i)
        if pos < 0:
            return None
        return index_to_cursor(buf, pos)

    # regex
    try:
        rx = re.compile(q, flags)
    except re.error:
        return None

    m = rx.search(hay, pos=start_i)
    if not m:
        return None
    return index_to_cursor(buf, m.start())


def find_prev(buf: Buffer, state: SearchState, *, start: Cursor) -> Cursor | None:
    """Find the previous occurrence before `start` (searching backward)."""

    q = state.query
    if not q:
        return None

    hay = buf.get_text()
    start_i = cursor_to_index(buf, start)

    flags = 0
    if not state.case_sensitive:
        flags |= re.IGNORECASE

    if state.literal:
        hay2 = hay
        q2 = q
        if flags & re.IGNORECASE:
            hay2 = hay.lower()
            q2 = q.lower()
        pos = hay2.rfind(q2, 0, start_i)
        if pos < 0:
            return None
        return index_to_cursor(buf, pos)

    try:
        rx = re.compile(q, flags)
    except re.error:
        return None

    last = None
    for m in rx.finditer(hay, 0, start_i):
        last = m
    if not last:
        return None
    return index_to_cursor(buf, last.start())
