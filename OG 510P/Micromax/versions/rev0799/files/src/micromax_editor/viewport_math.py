from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass


@dataclass(frozen=True)
class VisualPoint:
    """A cursor position in softwrapped visual-row coordinates."""

    y: int
    x: int


@dataclass(frozen=True)
class ViewportTop:
    """Logical line/subline pair for the top of a softwrapped viewport."""

    line: int
    subline: int


def _line_rows(lines: Sequence[str] | None) -> Sequence[str]:
    if lines is None:
        return ()
    return lines


def leading_ws_cols(s: str) -> int:
    """Count leading indentation characters as display columns.

    The current editor's wrapping model treats a tab as one column in the
    headless model, matching the older in-editor comment.  Keeping this in a
    small helper gives the behavior a direct regression instead of burying it in
    the large editor class.
    """

    n = 0
    for ch in str(s or ""):
        if ch in (" ", "\t"):
            n += 1
            continue
        break
    return int(n)


def contindent_for_line(s: str, *, width: int, setting: int) -> int:
    """Return continuation indent for a wrapped line."""

    w = int(width)
    if w <= 1:
        return 0
    setting = int(setting)
    if setting == 0:
        return 0
    if setting < 0:
        max_cont = min(8, w - 1)
        return max(0, min(leading_ws_cols(s), int(max_cont)))
    return max(0, min(setting, w - 1))


def wrap_seg(width: int, contindent: int) -> int:
    """Return the text capacity of a continuation row."""

    w = int(width)
    cont = max(0, int(contindent))
    if w <= 0:
        return 1
    if cont <= 0:
        return max(1, w)
    return max(1, w - cont)


def find_wordwrap_break(s: str, start: int, end: int) -> int | None:
    """Return the next row start for ``s[start:end]`` when word wrapping."""

    text = str(s or "")
    start_i = max(0, int(start))
    end_i = max(start_i, min(int(end), len(text)))
    if end_i - start_i <= 1:
        return None
    for idx in range(end_i - 1, start_i, -1):
        if text[idx].isspace():
            return idx + 1
    return None


def wrap_row_starts_for_line(
    s: str,
    *,
    width: int,
    contindent: int = 0,
    wordwrap: bool = False,
) -> list[int]:
    """Return absolute character starts for every wrapped row in one line."""

    text = str(s or "")
    w = int(width)
    if w <= 0 or text == "":
        return [0]
    cont = max(0, min(int(contindent), w - 1))
    starts = [0]
    start = 0
    row = 0
    text_len = len(text)
    while start < text_len:
        cap = max(1, w if row <= 0 else wrap_seg(w, cont))
        end = min(text_len, start + cap)
        if end >= text_len:
            break
        next_start = find_wordwrap_break(text, start, end) if bool(wordwrap) else None
        if next_start is None or next_start <= start:
            next_start = end
        starts.append(int(next_start))
        start = int(next_start)
        row += 1
    return starts


def wrap_start_for_row_in_line(
    s: str,
    *,
    width: int,
    row: int,
    contindent: int = 0,
    wordwrap: bool = False,
) -> int:
    starts = wrap_row_starts_for_line(s, width=width, contindent=contindent, wordwrap=wordwrap)
    row_i = max(0, min(int(row), max(0, len(starts) - 1)))
    return int(starts[row_i])


def wrap_end_for_row_in_line(
    s: str,
    *,
    width: int,
    row: int,
    contindent: int = 0,
    wordwrap: bool = False,
) -> int:
    text = str(s or "")
    starts = wrap_row_starts_for_line(text, width=width, contindent=contindent, wordwrap=wordwrap)
    row_i = max(0, min(int(row), max(0, len(starts) - 1)))
    if row_i + 1 < len(starts):
        return int(starts[row_i + 1])
    return int(len(text))


def wrap_cap_for_row_in_line(
    s: str,
    *,
    width: int,
    row: int,
    contindent: int = 0,
    wordwrap: bool = False,
) -> int:
    start = wrap_start_for_row_in_line(s, width=width, row=row, contindent=contindent, wordwrap=wordwrap)
    end = wrap_end_for_row_in_line(s, width=width, row=row, contindent=contindent, wordwrap=wordwrap)
    return max(0, int(end - start))


def wraps_for_line(
    s: str,
    *,
    width: int,
    contindent: int = 0,
    wordwrap: bool = False,
) -> int:
    return len(wrap_row_starts_for_line(s, width=width, contindent=contindent, wordwrap=wordwrap))


def wrap_row_for_col(
    s: str,
    col: int,
    *,
    width: int,
    contindent: int = 0,
    wordwrap: bool = False,
) -> int:
    """Return the wrapped-row index containing ``col``."""

    text = str(s or "")
    w = int(width)
    if w <= 0:
        return 0
    starts = wrap_row_starts_for_line(text, width=w, contindent=contindent, wordwrap=wordwrap)
    col_i = max(0, min(int(col), len(text)))
    row = 0
    for idx, start in enumerate(starts):
        if col_i < int(start):
            break
        row = idx
    return int(row)


def visual_row_index(
    lines: list[str],
    line: int,
    wrap_row: int,
    *,
    width: int,
    contindent_setting: int,
    wordwrap: bool = False,
) -> int:
    """Return global visual-row index for ``(line, wrap_row)``."""

    rows = _line_rows(lines)
    if not rows:
        return max(0, int(wrap_row))
    line_i = max(0, min(int(line), max(0, len(rows) - 1)))
    y = 0
    for li in range(0, line_i):
        cont = contindent_for_line(rows[li], width=width, setting=contindent_setting)
        y += wraps_for_line(rows[li], width=width, contindent=cont, wordwrap=wordwrap)
    return int(y + max(0, int(wrap_row)))


def cursor_visual_yx(
    lines: list[str],
    *,
    line: int,
    col: int,
    width: int,
    contindent_setting: int,
    wordwrap: bool = False,
) -> VisualPoint:
    """Map a document cursor to global softwrapped visual coordinates."""

    rows = _line_rows(lines)
    w = int(width)
    if w <= 0:
        return VisualPoint(int(line), int(col))
    if not rows:
        return VisualPoint(0, 0)
    line_i = max(0, min(int(line), max(0, len(rows) - 1)))
    text = rows[line_i]
    col_i = max(0, min(int(col), len(text)))
    cont = contindent_for_line(text, width=w, setting=contindent_setting)
    wrap_row = wrap_row_for_col(text, col_i, width=w, contindent=cont, wordwrap=wordwrap)
    wrap_start = wrap_start_for_row_in_line(text, width=w, row=wrap_row, contindent=cont, wordwrap=wordwrap)
    x = (col_i - wrap_start) + (cont if wrap_row > 0 else 0)
    y = visual_row_index(rows, line_i, wrap_row, width=w, contindent_setting=contindent_setting, wordwrap=wordwrap)
    return VisualPoint(int(y), int(x))


def total_visual_rows(
    lines: list[str],
    *,
    width: int,
    contindent_setting: int,
    wordwrap: bool = False,
) -> int:
    rows = _line_rows(lines)
    w = int(width)
    if w <= 0:
        return max(1, len(rows))
    total = 0
    for text in rows:
        cont = contindent_for_line(text, width=w, setting=contindent_setting)
        total += wraps_for_line(text, width=w, contindent=cont, wordwrap=wordwrap)
    return max(1, int(total))


def doc_pos_for_visual_row(
    lines: list[str],
    *,
    target_y: int,
    goal_x: int,
    width: int,
    contindent_setting: int,
    wordwrap: bool = False,
) -> tuple[int, int]:
    """Map a global visual-row index plus target x to a document cursor."""

    rows = _line_rows(lines)
    w = int(width)
    if w <= 0:
        if not rows:
            return (0, 0)
        li = max(0, min(int(target_y), max(0, len(rows) - 1)))
        return (li, max(0, min(int(goal_x), len(rows[li]))))

    y = max(0, int(target_y))
    goal = max(0, int(goal_x))
    if not rows:
        return (0, 0)
    acc = 0
    for li, text in enumerate(rows):
        cont = contindent_for_line(text, width=w, setting=contindent_setting)
        wraps = wraps_for_line(text, width=w, contindent=cont, wordwrap=wordwrap)
        if y < acc + wraps:
            sub = y - acc
            if text == "":
                return (li, 0)
            wrap_start = wrap_start_for_row_in_line(text, width=w, row=sub, contindent=cont, wordwrap=wordwrap)
            row_end = wrap_end_for_row_in_line(text, width=w, row=sub, contindent=cont, wordwrap=wordwrap)
            if sub <= 0:
                return (li, min(wrap_start + goal, row_end))
            if goal <= cont:
                return (li, wrap_start)
            return (li, min(wrap_start + (goal - cont), row_end))
        acc += wraps
    li = len(rows) - 1
    return (li, len(rows[li]))


def viewport_visual_start(
    lines: list[str],
    *,
    top_line: int,
    top_subline: int,
    width: int,
    contindent_setting: int,
    wordwrap: bool = False,
) -> int:
    """Return global visual-row index for a viewport top pair."""

    rows = _line_rows(lines)
    if not rows:
        return 0
    w = int(width)
    top = max(0, min(int(top_line), max(0, len(rows) - 1)))
    sub = max(0, int(top_subline))
    if w <= 0:
        return int(top)
    cont = contindent_for_line(rows[top], width=w, setting=contindent_setting)
    wraps = wraps_for_line(rows[top], width=w, contindent=cont, wordwrap=wordwrap)
    sub = min(sub, max(0, wraps - 1))
    return visual_row_index(rows, top, sub, width=w, contindent_setting=contindent_setting, wordwrap=wordwrap)


def viewport_top_for_visual_start(
    lines: list[str],
    *,
    start_y: int,
    width: int,
    contindent_setting: int,
    wordwrap: bool = False,
) -> ViewportTop:
    """Return the logical top line/subline for a global visual-row index."""

    rows = _line_rows(lines)
    if not rows:
        return ViewportTop(0, 0)
    w = int(width)
    if w <= 0:
        return ViewportTop(max(0, min(int(start_y), max(0, len(rows) - 1))), 0)
    y = max(0, int(start_y))
    acc = 0
    for li, text in enumerate(rows):
        cont = contindent_for_line(text, width=w, setting=contindent_setting)
        wraps = wraps_for_line(text, width=w, contindent=cont, wordwrap=wordwrap)
        if y < acc + wraps:
            return ViewportTop(int(li), int(y - acc))
        acc += wraps
    return ViewportTop(len(rows) - 1, 0)
