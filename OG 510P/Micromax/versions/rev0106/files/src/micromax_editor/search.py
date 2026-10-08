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
