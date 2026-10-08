from __future__ import annotations

from array import array
from bisect import bisect_right
from collections import OrderedDict
from collections.abc import Iterator, Sequence
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


class WordWrapLayout:
    """Checkpointed true-wordwrap geometry for one exact logical line.

    True wordwrap is sequential: each whitespace break determines the next row's
    starting point. Retaining every start as a Python integer is unnecessary,
    though. One construction scan records sparse native unsigned checkpoints;
    row/column lookup resumes from the nearest checkpoint and inspects at most
    ``checkpoint_stride`` wrap decisions.

    The stride grows conservatively for exceptionally large lines so the
    checkpoint payload remains bounded even when width is one character.
    """

    _MIN_CHECKPOINT_STRIDE = 64
    _MAX_CHECKPOINT_BYTES = 256 * 1024

    __slots__ = (
        "text",
        "width",
        "contindent",
        "checkpoint_stride",
        "_checkpoints",
        "_row_count",
    )

    def __init__(self, text: str, *, width: int, contindent: int = 0) -> None:
        self.text = str(text or "")
        self.width = int(width)
        if self.width <= 0:
            self.contindent = 0
        else:
            self.contindent = max(0, min(int(contindent), self.width - 1))

        cell_budget = max(1, self._MAX_CHECKPOINT_BYTES // array("Q").itemsize)
        upper_rows = max(1, len(self.text))
        bounded_stride = (upper_rows + cell_budget - 1) // cell_budget
        self.checkpoint_stride = max(
            self._MIN_CHECKPOINT_STRIDE,
            int(bounded_stride),
        )
        self._checkpoints = array("Q", [0])
        self._row_count = self._build()

    @property
    def row_count(self) -> int:
        return int(self._row_count)

    @property
    def storage_bytes(self) -> int:
        return int(self._checkpoints.itemsize * len(self._checkpoints))

    def matches(self, text: str, *, width: int, contindent: int) -> bool:
        return (
            self.text is text
            and self.width == int(width)
            and self.contindent
            == (0 if int(width) <= 0 else max(0, min(int(contindent), int(width) - 1)))
        )

    def _next_start(self, start: int, row: int) -> int:
        text_len = len(self.text)
        start_i = max(0, min(int(start), text_len))
        if start_i >= text_len or self.width <= 0:
            return text_len
        capacity = max(
            1,
            self.width
            if int(row) <= 0
            else wrap_seg(self.width, self.contindent),
        )
        end = min(text_len, start_i + capacity)
        if end >= text_len:
            return text_len
        next_start = find_wordwrap_break(self.text, start_i, end)
        if next_start is None or next_start <= start_i:
            next_start = end
        return int(next_start)

    def _build(self) -> int:
        if self.width <= 0 or self.text == "":
            return 1
        start = 0
        row = 0
        text_len = len(self.text)
        while start < text_len:
            next_start = self._next_start(start, row)
            if next_start >= text_len:
                break
            row += 1
            start = int(next_start)
            if row % self.checkpoint_stride == 0:
                self._checkpoints.append(start)
        return int(row + 1)

    def start_for_row(self, row: int) -> int:
        row_i = max(0, min(int(row), self.row_count - 1))
        checkpoint_index = min(
            len(self._checkpoints) - 1,
            row_i // self.checkpoint_stride,
        )
        current_row = checkpoint_index * self.checkpoint_stride
        start = int(self._checkpoints[checkpoint_index])
        while current_row < row_i:
            start = self._next_start(start, current_row)
            current_row += 1
        return int(start)

    def bounds_for_row(self, row: int) -> tuple[int, int]:
        row_i = max(0, min(int(row), self.row_count - 1))
        start = self.start_for_row(row_i)
        if row_i + 1 >= self.row_count:
            return (start, len(self.text))
        return (start, self._next_start(start, row_i))

    def row_for_col(self, col: int) -> int:
        if self.row_count <= 1:
            return 0
        col_i = max(0, min(int(col), len(self.text)))
        checkpoint_index = max(0, bisect_right(self._checkpoints, col_i) - 1)
        row = checkpoint_index * self.checkpoint_stride
        start = int(self._checkpoints[checkpoint_index])
        while row + 1 < self.row_count:
            next_start = self._next_start(start, row)
            if next_start > col_i:
                break
            start = next_start
            row += 1
        return int(row)

    def iter_bounds(self, start_row: int, limit: int) -> Iterator[tuple[int, int]]:
        remaining = max(0, int(limit))
        if remaining <= 0:
            return
        row = max(0, min(int(start_row), self.row_count - 1))
        start = self.start_for_row(row)
        while remaining > 0 and row < self.row_count:
            end = (
                len(self.text)
                if row + 1 >= self.row_count
                else self._next_start(start, row)
            )
            yield (int(start), int(end))
            row += 1
            remaining -= 1
            start = int(end)


class VisualRowIndex:
    """Compact, versioned prefix index for softwrapped line geometry.

    The pure helpers below remain the reference behavior.  This index is the
    editor's hot-path acceleration layer: it stores one unsigned row count and
    one Fenwick-tree cell per logical line, so prefix queries and visual-row
    lookup are logarithmic without allocating a Python ``int`` object per cell.

    A single line-preserving buffer splice can be refreshed incrementally when
    the caller owns the immediately preceding buffer version.  Width or wrapping
    changes, missed versions, line-count changes, and externally-authored edits
    rebuild from the authoritative line vector instead of attempting repair.
    """

    _MAX_INCREMENTAL_LINES = 256
    _WORDWRAP_CACHE_SLOTS = 4
    _WORDWRAP_EAGER_CHARS = 64 * 1024

    def __init__(
        self,
        lines: Sequence[str] | None,
        *,
        version: int,
        width: int,
        contindent_setting: int,
        wordwrap: bool = False,
    ) -> None:
        self.version = int(version)
        self.width = int(width)
        self.contindent_setting = int(contindent_setting)
        self.wordwrap = bool(wordwrap)
        self._counts = array("Q")
        self._tree = array("Q")
        self._wordwrap_indexes: OrderedDict[int, WordWrapLayout] = OrderedDict()
        self._rebuild(_line_rows(lines))

    @property
    def line_count(self) -> int:
        return len(self._counts)

    @property
    def storage_bytes(self) -> int:
        """Return compact array payload size, excluding tiny object headers."""

        return int(
            self._counts.itemsize * len(self._counts)
            + self._tree.itemsize * len(self._tree)
        )

    @property
    def wordwrap_cache_bytes(self) -> int:
        """Return retained sparse boundary payload for cached logical lines."""

        return sum(index.storage_bytes for index in self._wordwrap_indexes.values())

    @property
    def wordwrap_cache_size(self) -> int:
        return len(self._wordwrap_indexes)

    @property
    def total_rows(self) -> int:
        return max(1, self.prefix_rows(len(self._counts)))

    def row_count(self, line: int) -> int:
        if not self._counts:
            return 1
        line_i = max(0, min(int(line), len(self._counts) - 1))
        return int(self._counts[line_i])

    def _config_matches(
        self,
        *,
        width: int,
        contindent_setting: int,
        wordwrap: bool,
    ) -> bool:
        return (
            self.width == int(width)
            and self.contindent_setting == int(contindent_setting)
            and self.wordwrap == bool(wordwrap)
        )

    def _cache_wordwrap_index(
        self,
        line: int,
        index: WordWrapLayout,
    ) -> WordWrapLayout:
        line_i = int(line)
        self._wordwrap_indexes[line_i] = index
        self._wordwrap_indexes.move_to_end(line_i)
        while len(self._wordwrap_indexes) > self._WORDWRAP_CACHE_SLOTS:
            self._wordwrap_indexes.popitem(last=False)
        return index

    def wordwrap_line_index(self, line: int, text: str) -> WordWrapLayout:
        """Return one exact cached sparse layout for the authoritative line."""

        if not self.wordwrap:
            raise ValueError(
                "word-wrap line geometry requested while wordwrap is disabled"
            )
        line_i = max(0, int(line))
        source = str(text or "")
        cont = contindent_for_line(
            source,
            width=self.width,
            setting=self.contindent_setting,
        )
        cached = self._wordwrap_indexes.get(line_i)
        if cached is not None and cached.matches(
            source,
            width=self.width,
            contindent=cont,
        ):
            self._wordwrap_indexes.move_to_end(line_i)
            return cached

        return self._cache_wordwrap_index(
            line_i,
            WordWrapLayout(
                source,
                width=self.width,
                contindent=cont,
            ),
        )

    def _row_count(self, text: str, *, line: int | None = None) -> int:
        if self.width <= 0:
            return 1
        cont = contindent_for_line(
            text,
            width=self.width,
            setting=self.contindent_setting,
        )
        if (
            self.wordwrap
            and line is not None
            and len(text) >= self._WORDWRAP_EAGER_CHARS
        ):
            return self._cache_wordwrap_index(
                int(line),
                WordWrapLayout(
                    text,
                    width=self.width,
                    contindent=cont,
                ),
            ).row_count
        return max(
            1,
            wraps_for_line(
                text,
                width=self.width,
                contindent=cont,
                wordwrap=self.wordwrap,
            ),
        )

    def _rebuild(self, lines: Sequence[str]) -> None:
        self._wordwrap_indexes.clear()
        self._counts = array("Q")
        for line, text in enumerate(lines):
            self._counts.append(self._row_count(str(text), line=line))
        self._tree = array("Q", self._counts)
        size = len(self._tree)
        for index in range(1, size + 1):
            parent = index + (index & -index)
            if parent <= size:
                self._tree[parent - 1] += self._tree[index - 1]

    def _set_count(self, line: int, count: int) -> None:
        line_i = int(line)
        next_count = max(1, int(count))
        previous = int(self._counts[line_i])
        if previous == next_count:
            return
        self._counts[line_i] = next_count
        delta = next_count - previous
        index = line_i + 1
        size = len(self._tree)
        while index <= size:
            self._tree[index - 1] = int(self._tree[index - 1]) + delta
            index += index & -index

    def sync(
        self,
        lines: Sequence[str] | None,
        *,
        version: int,
        change: object | None,
        width: int,
        contindent_setting: int,
        wordwrap: bool = False,
    ) -> None:
        """Synchronize to one authoritative buffer/configuration witness."""

        rows = _line_rows(lines)
        next_version = int(version)
        if (
            next_version == self.version
            and len(rows) == len(self._counts)
            and self._config_matches(
                width=width,
                contindent_setting=contindent_setting,
                wordwrap=wordwrap,
            )
        ):
            return

        config_matches = self._config_matches(
            width=width,
            contindent_setting=contindent_setting,
            wordwrap=wordwrap,
        )
        start = getattr(change, "start_line", None)
        old_count = getattr(change, "old_line_count", None)
        new_count = getattr(change, "new_line_count", None)
        change_version = getattr(change, "version", None)
        try:
            start_i = int(start)
            old_count_i = int(old_count)
            new_count_i = int(new_count)
            change_version_i = int(change_version)
        except (TypeError, ValueError, OverflowError):
            start_i = old_count_i = new_count_i = change_version_i = -1

        can_update = (
            config_matches
            and next_version == self.version + 1
            and change_version_i == next_version
            and old_count_i == new_count_i
            and 0 < new_count_i <= self._MAX_INCREMENTAL_LINES
            and len(rows) == len(self._counts)
            and 0 <= start_i <= len(rows) - new_count_i
        )
        if can_update:
            for line_i in range(start_i, start_i + new_count_i):
                self._wordwrap_indexes.pop(line_i, None)
                self._set_count(
                    line_i,
                    self._row_count(str(rows[line_i]), line=line_i),
                )
            self.version = next_version
            return

        self.version = next_version
        self.width = int(width)
        self.contindent_setting = int(contindent_setting)
        self.wordwrap = bool(wordwrap)
        self._rebuild(rows)

    def prefix_rows(self, line_exclusive: int) -> int:
        """Return visual rows strictly before ``line_exclusive``."""

        index = max(0, min(int(line_exclusive), len(self._tree)))
        total = 0
        while index > 0:
            total += int(self._tree[index - 1])
            index -= index & -index
        return int(total)

    def visual_row(self, line: int, subline: int) -> int:
        if not self._counts:
            return max(0, int(subline))
        line_i = max(0, min(int(line), len(self._counts) - 1))
        return int(self.prefix_rows(line_i) + max(0, int(subline)))

    def line_subline_for_visual(self, target_y: int) -> ViewportTop:
        """Map an in-range visual row in O(log n), preserving old overflow behavior."""

        if not self._counts:
            return ViewportTop(0, 0)
        y = max(0, int(target_y))
        total = self.prefix_rows(len(self._counts))
        if y >= total:
            return ViewportTop(len(self._counts) - 1, 0)

        index = 0
        prefix = 0
        bit = 1 << (len(self._tree).bit_length() - 1)
        while bit:
            candidate = index + bit
            if candidate <= len(self._tree):
                candidate_prefix = prefix + int(self._tree[candidate - 1])
                if candidate_prefix <= y:
                    index = candidate
                    prefix = candidate_prefix
            bit >>= 1
        return ViewportTop(int(index), int(y - prefix))


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


def _next_wordwrap_row_start(
    text: str,
    *,
    start: int,
    row: int,
    width: int,
    contindent: int,
) -> int | None:
    """Return the next exact row start, or ``None`` for the final row."""

    source = str(text or "")
    w = int(width)
    start_i = max(0, min(int(start), len(source)))
    if w <= 0 or start_i >= len(source):
        return None
    cont = max(0, min(int(contindent), w - 1))
    cap = max(1, w if int(row) <= 0 else wrap_seg(w, cont))
    end = min(len(source), start_i + cap)
    if end >= len(source):
        return None
    next_start = find_wordwrap_break(source, start_i, end)
    if next_start is None or next_start <= start_i:
        next_start = end
    return int(next_start)


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
    while start < len(text):
        if bool(wordwrap):
            next_start = _next_wordwrap_row_start(
                text,
                start=start,
                row=row,
                width=w,
                contindent=cont,
            )
            if next_start is None:
                break
        else:
            cap = max(1, w if row <= 0 else wrap_seg(w, cont))
            end = min(len(text), start + cap)
            if end >= len(text):
                break
            next_start = end
        starts.append(int(next_start))
        start = int(next_start)
        row += 1
    return starts


def _fixed_wrap_count(text_length: int, *, width: int, contindent: int) -> int:
    """Count fixed-width rows without materializing one start per row."""

    length = max(0, int(text_length))
    w = int(width)
    if w <= 0 or length <= w:
        return 1
    cont = max(0, min(int(contindent), w - 1))
    continuation = wrap_seg(w, cont)
    remaining = length - w
    return int(1 + ((remaining + continuation - 1) // continuation))


def _fixed_wrap_start(
    text_length: int,
    *,
    width: int,
    contindent: int,
    row: int,
) -> int:
    """Return one clamped fixed-width row start using constant memory."""

    length = max(0, int(text_length))
    w = int(width)
    if w <= 0 or length <= 0:
        return 0
    count = _fixed_wrap_count(length, width=w, contindent=contindent)
    row_i = max(0, min(int(row), count - 1))
    if row_i <= 0:
        return 0
    cont = max(0, min(int(contindent), w - 1))
    return min(length, int(w + (row_i - 1) * wrap_seg(w, cont)))


def wrap_start_for_row_in_line(
    s: str,
    *,
    width: int,
    row: int,
    contindent: int = 0,
    wordwrap: bool = False,
) -> int:
    text = str(s or "")
    if not bool(wordwrap):
        return _fixed_wrap_start(
            len(text),
            width=int(width),
            contindent=int(contindent),
            row=int(row),
        )
    index = WordWrapLayout(
        text,
        width=width,
        contindent=contindent,
    )
    return index.start_for_row(row)


def wrap_end_for_row_in_line(
    s: str,
    *,
    width: int,
    row: int,
    contindent: int = 0,
    wordwrap: bool = False,
) -> int:
    text = str(s or "")
    if not bool(wordwrap):
        count = _fixed_wrap_count(
            len(text),
            width=int(width),
            contindent=int(contindent),
        )
        row_i = max(0, min(int(row), count - 1))
        if row_i + 1 >= count:
            return len(text)
        return _fixed_wrap_start(
            len(text),
            width=int(width),
            contindent=int(contindent),
            row=row_i + 1,
        )
    index = WordWrapLayout(
        text,
        width=width,
        contindent=contindent,
    )
    return index.bounds_for_row(row)[1]


def wrap_cap_for_row_in_line(
    s: str,
    *,
    width: int,
    row: int,
    contindent: int = 0,
    wordwrap: bool = False,
) -> int:
    text = str(s or "")
    if not bool(wordwrap):
        start = _fixed_wrap_start(
            len(text),
            width=int(width),
            contindent=int(contindent),
            row=int(row),
        )
        end = wrap_end_for_row_in_line(
            text,
            width=width,
            row=row,
            contindent=contindent,
            wordwrap=False,
        )
        return max(0, int(end - start))
    index = WordWrapLayout(
        text,
        width=width,
        contindent=contindent,
    )
    start, end = index.bounds_for_row(row)
    return max(0, int(end - start))


def wraps_for_line(
    s: str,
    *,
    width: int,
    contindent: int = 0,
    wordwrap: bool = False,
) -> int:
    text = str(s or "")
    w = int(width)
    if not bool(wordwrap):
        return _fixed_wrap_count(len(text), width=w, contindent=int(contindent))
    if w <= 0 or text == "":
        return 1

    cont = max(0, min(int(contindent), w - 1))
    start = 0
    row = 0
    count = 1
    while True:
        next_start = _next_wordwrap_row_start(
            text,
            start=start,
            row=row,
            width=w,
            contindent=cont,
        )
        if next_start is None:
            break
        count += 1
        start = int(next_start)
        row += 1
    return int(count)


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
    col_i = max(0, min(int(col), len(text)))
    if not bool(wordwrap):
        count = _fixed_wrap_count(len(text), width=w, contindent=int(contindent))
        if count <= 1 or col_i < w:
            return 0
        cont = max(0, min(int(contindent), w - 1))
        row = 1 + ((col_i - w) // wrap_seg(w, cont))
        return int(min(count - 1, row))

    index = WordWrapLayout(
        text,
        width=w,
        contindent=contindent,
    )
    return index.row_for_col(col_i)


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
