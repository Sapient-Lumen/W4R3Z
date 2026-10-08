from __future__ import annotations

"""Side-effect-free, bounded replace planning for editor commands.

The planner answers "what would change?" before a buffer mutates. Literal work
is local and coordinate-preserving. Every caller-authored regex match scan runs
in the shared killable worker, returning concrete spans and expanded replacement
text as plain data; timeout, zero-width matches, malformed templates, and result
budgets therefore fail before mutation.
"""

from bisect import bisect_right
from array import array
from collections.abc import Iterable, Iterator, Sequence
from dataclasses import dataclass, field
import math
import multiprocessing
import operator
import re

from micromax.regex_runtime import (
    DEFAULT_REGEX_WORKER_RESULT_MAX_BYTES,
    RegexWorkerError,
    RegexWorkerOperationError,
    RegexWorkerTimeoutError,
    bounded_regex_replacement_rows,
    bounded_regex_replacement_rows_from_chunks,
)
from micromax.regex_tools import (
    convert_replacement_template,
)

from .textpos import OFFSET_TYPECODE, line_start_offsets_for_lines


DEFAULT_EDITOR_REPLACE_MAX_MATCHES = 100_000
DEFAULT_EDITOR_REPLACE_REGEX_TIMEOUT_SECONDS = 0.25
DEFAULT_EDITOR_REPLACE_PATTERN_MAX_BYTES = 10_000
DEFAULT_EDITOR_LITERAL_SCAN_CHARS = 256 * 1024


@dataclass(frozen=True)
class ReplaceMatch:
    """One planned replacement witness."""

    start: int
    end: int
    line: int
    col: int
    end_line: int
    end_col: int
    old: str
    new: str

    def row(self) -> list[object]:
        return [
            int(self.line),
            int(self.col),
            int(self.end_line),
            int(self.end_col),
            self.old,
            self.new,
        ]


@dataclass(frozen=True, slots=True)
class ReplacementEdit:
    """One projected source span plus already-expanded replacement text."""

    start: int
    end: int
    new: str


def _pack_replacement_rows(
    rows: Iterable[tuple[int, int, str]],
) -> tuple[array, str | None, tuple[str, ...] | None]:
    """Return packed spans plus the narrowest immutable replacement owner."""

    spans = array(OFFSET_TYPECODE)
    first_new = ""
    news: list[str] | None = None
    count = 0
    for raw_start, raw_end, raw_new in rows:
        spans.append(int(raw_start))
        spans.append(int(raw_end))
        new = str(raw_new)
        if count == 0:
            first_new = new
        elif news is None and new != first_new:
            news = [first_new] * count
        if news is not None:
            news.append(new)
        count += 1
    if news is None:
        return spans, first_new, None
    return spans, None, tuple(news)


class ReplacementEdits(Sequence[ReplacementEdit]):
    """Immutable replacement rows with packed source coordinates.

    Dense delayed query-replace plans need random access, ordered iteration, and
    stable source coordinates, but they do not need one long-lived Python object
    (plus two Python integers) per match.  This owner stores interleaved
    ``start,end`` values in private unsigned 64-bit cells.  Literal plans retain
    one shared replacement string; regex plans retain a replacement tuple only
    when capture expansion actually varies by match.

    Indexing projects one short-lived :class:`ReplacementEdit`, preserving the
    existing sequence contract without retaining the object graph.  The owner is
    immutable after publication and therefore shares safely across plugin/runtime
    snapshots instead of being recursively rebuilt by ``copy.deepcopy``.
    """

    __slots__ = ("_spans", "_uniform_new", "_news")

    def __init__(self, edits: Iterable[ReplacementEdit] = ()) -> None:
        spans, uniform_new, news = _pack_replacement_rows(
            (edit.start, edit.end, edit.new) for edit in edits
        )
        self._spans = spans
        self._uniform_new = uniform_new
        self._news = news

    @classmethod
    def _from_owned_uniform_spans(
        cls,
        spans: array,
        replacement: str,
    ) -> "ReplacementEdits":
        """Publish an unpublished interleaved span array without copying it."""

        if spans.typecode != OFFSET_TYPECODE:
            raise ValueError(
                f"replacement span array must use {OFFSET_TYPECODE!r} cells"
            )
        if len(spans) % 2 != 0:
            raise ValueError("replacement span array must contain start/end pairs")
        result = cls.__new__(cls)
        result._spans = spans
        result._uniform_new = str(replacement)
        result._news = None
        return result

    @classmethod
    def from_rows(
        cls,
        rows: Iterable[tuple[int, int, str]],
    ) -> "ReplacementEdits":
        """Pack validated regex-worker rows without retaining row objects."""

        spans, uniform_new, news = _pack_replacement_rows(rows)
        result = cls.__new__(cls)
        result._spans = spans
        result._uniform_new = uniform_new
        result._news = news
        return result

    def __deepcopy__(self, memo: dict[int, object]) -> "ReplacementEdits":
        """Share this immutable plan across delayed-runtime snapshots."""

        memo[id(self)] = self
        return self

    @property
    def coordinate_bytes(self) -> int:
        """Return bytes occupied by packed start/end cells."""

        return int(self._spans.itemsize * len(self._spans))

    @property
    def uses_uniform_replacement(self) -> bool:
        return self._news is None

    @property
    def retained_replacement_values(self) -> int:
        if not self:
            return 0
        return 1 if self._news is None else len(self._news)

    def __len__(self) -> int:
        return len(self._spans) // 2

    def _replacement_at(self, index: int) -> str:
        news = self._news
        if news is None:
            return str(self._uniform_new or "")
        return str(news[index])

    def _item_at(self, index: int) -> ReplacementEdit:
        item = operator.index(index)
        if item < 0:
            item += len(self)
        if item < 0 or item >= len(self):
            raise IndexError("replacement edit index out of range")
        span_at = item * 2
        return ReplacementEdit(
            start=int(self._spans[span_at]),
            end=int(self._spans[span_at + 1]),
            new=self._replacement_at(item),
        )

    def __getitem__(
        self,
        index: int | slice,
    ) -> ReplacementEdit | tuple[ReplacementEdit, ...]:
        if isinstance(index, slice):
            indices = range(*index.indices(len(self)))
            return tuple(self._item_at(item) for item in indices)
        return self._item_at(index)

    def __iter__(self) -> Iterator[ReplacementEdit]:
        return (self._item_at(index) for index in range(len(self)))

    def __eq__(self, other: object) -> bool:
        if isinstance(other, ReplacementEdits):
            if self._spans != other._spans or len(self) != len(other):
                return False
            if self._news is None and other._news is None:
                return self._uniform_new == other._uniform_new
        if isinstance(other, Sequence):
            return len(self) == len(other) and all(
                left == right
                for left, right in zip(self, other, strict=True)
            )
        return NotImplemented

    def __repr__(self) -> str:
        count = len(self)
        if count <= 6:
            return f"ReplacementEdits({tuple(self)!r})"
        head = tuple(self[index] for index in range(3))
        tail = tuple(self[index] for index in range(count - 3, count))
        return f"ReplacementEdits({head!r} ... {tail!r}, count={count})"


@dataclass(frozen=True)
class ReplacementEditScan:
    """Concrete non-overlapping edits without eager display coordinates/old text."""

    ok: bool
    error: str = ""
    edits: ReplacementEdits = field(default_factory=ReplacementEdits)
    worker_routed: bool = False
    timed_out: bool = False


@dataclass(frozen=True, slots=True)
class _ReplacementScanRequest:
    search: str
    value: str
    start: int
    match_limit: int
    result_limit: int
    replacement_bytes: int


@dataclass(frozen=True)
class ReplacementScan:
    """Concrete non-overlapping replacements against one immutable source."""

    ok: bool
    error: str = ""
    matches: tuple[ReplaceMatch, ...] = ()
    worker_routed: bool = False
    timed_out: bool = False


@dataclass(frozen=True)
class ReplacePlan:
    """Plain-data result for a replace request.

    ``error`` is message text without a command prefix. Callers decide whether
    the prefix is ``replace``, ``replaceall``, ``qreplace``, or a preview surface.
    """

    ok: bool
    error: str = ""
    search: str = ""
    value: str = ""
    replace_all: bool = False
    literal: bool = False
    case_sensitive: bool = True
    start_index: int = 0
    count: int = 0
    matches: tuple[ReplaceMatch, ...] = ()
    new_text: str | None = None

    @property
    def changed(self) -> bool:
        return self.ok and self.new_text is not None and self.count > 0

    def rows(self) -> list[list[object]]:
        """Return compact sample rows for scripting surfaces."""

        return [match.row() for match in self.matches]

    def summary_row(self) -> list[object]:
        """Return ``[ok count all literal case start error rows]``."""

        return [
            1 if self.ok else 0,
            int(self.count),
            1 if self.replace_all else 0,
            1 if self.literal else 0,
            1 if self.case_sensitive else 0,
            int(self.start_index),
            str(self.error),
            self.rows(),
        ]


def _materialize_matches(
    text: str,
    edits: Iterable[ReplacementEdit],
    *,
    limit: int | None = None,
) -> tuple[ReplaceMatch, ...]:
    """Project sorted source edits to display rows in one forward text walk.

    The old planner called ``str.count`` and ``str.rfind`` from the beginning of
    the document twice for every match.  Dense replace-all plans therefore did
    cumulative prefix rescans.  Match offsets are monotonic, so one newline
    cursor can produce all requested line/column pairs in linear time and
    constant auxiliary storage.
    """

    source = str(text)
    maximum = None if limit is None else max(0, int(limit))
    out: list[ReplaceMatch] = []
    line = 0
    line_start = 0
    scan_at = 0

    def coordinate(index: int) -> tuple[int, int]:
        nonlocal line, line_start, scan_at
        bounded = max(0, min(int(index), len(source)))
        while scan_at < bounded:
            newline = source.find("\n", scan_at, bounded)
            if newline < 0:
                scan_at = bounded
                break
            line += 1
            line_start = newline + 1
            scan_at = newline + 1
        return int(line), int(bounded - line_start)

    for edit in edits:
        if maximum is not None and len(out) >= maximum:
            break
        start = max(0, min(int(edit.start), len(source)))
        end = max(start, min(int(edit.end), len(source)))
        start_line, start_col = coordinate(start)
        end_line, end_col = coordinate(end)
        out.append(
            ReplaceMatch(
                start=start,
                end=end,
                line=start_line,
                col=start_col,
                end_line=end_line,
                end_col=end_col,
                old=source[start:end],
                new=str(edit.new),
            )
        )
    return tuple(out)


def _apply_edits(text: str, edits: Iterable[ReplacementEdit]) -> str:
    pieces: list[str] = []
    position = 0
    for edit in edits:
        pieces.append(text[position : edit.start])
        pieces.append(edit.new)
        position = edit.end
    pieces.append(text[position:])
    return "".join(pieces)


def _prepare_replacement_scan(
    *,
    source_length: int,
    search: str,
    value: str,
    start_index: int,
    literal: bool,
    max_matches: int,
    max_pattern_bytes: int,
    max_result_bytes: int,
) -> _ReplacementScanRequest:
    """Validate shared literal/regex budgets and normalize scalar inputs."""

    query = str(search)
    replacement = str(value)
    try:
        raw_start = int(start_index)
    except (TypeError, ValueError, OverflowError):
        raw_start = 0
    start = max(0, min(raw_start, max(0, int(source_length))))
    try:
        match_limit = max(0, int(max_matches))
    except (TypeError, ValueError, OverflowError):
        match_limit = int(DEFAULT_EDITOR_REPLACE_MAX_MATCHES)
    try:
        pattern_limit = int(max_pattern_bytes)
    except (TypeError, ValueError, OverflowError):
        pattern_limit = int(DEFAULT_EDITOR_REPLACE_PATTERN_MAX_BYTES)
    if pattern_limit <= 0:
        pattern_limit = int(DEFAULT_EDITOR_REPLACE_PATTERN_MAX_BYTES)
    try:
        result_limit = int(max_result_bytes)
    except (TypeError, ValueError, OverflowError):
        result_limit = int(DEFAULT_REGEX_WORKER_RESULT_MAX_BYTES)
    if result_limit <= 0:
        result_limit = int(DEFAULT_REGEX_WORKER_RESULT_MAX_BYTES)

    if query == "":
        raise ValueError("empty search")

    replacement_bytes = len(replacement.encode("utf-8", errors="replace"))
    if replacement_bytes > result_limit:
        raise ValueError(
            "replacement too large: "
            f"{replacement_bytes} bytes > {result_limit}"
        )

    pattern_bytes = len(query.encode("utf-8", errors="replace"))
    if pattern_bytes > pattern_limit:
        label = "literal" if literal else "regex"
        raise ValueError(
            f"{label} pattern too large: {pattern_bytes} bytes > {pattern_limit}"
        )

    return _ReplacementScanRequest(
        search=query,
        value=replacement,
        start=start,
        match_limit=match_limit,
        result_limit=result_limit,
        replacement_bytes=replacement_bytes,
    )


def _line_cursor_for_offset(
    lines: Sequence[str],
    line_starts: Sequence[int],
    source_length: int,
    offset: int,
) -> tuple[int, int]:
    """Project one clamped canonical offset without flattening the source."""

    pos = max(0, min(int(offset), int(source_length)))
    line = max(0, bisect_right(line_starts, pos) - 1)
    line = min(line, len(lines) - 1)
    col = max(0, min(pos - int(line_starts[line]), len(lines[line])))
    return int(line), int(col)


def _canonical_line_range_text(
    lines: Sequence[str],
    line_starts: Sequence[int],
    source_length: int,
    start: int,
    end: int,
) -> str:
    """Materialize one bounded range of exact ``"\n".join(lines)`` text."""

    left = max(0, min(int(start), int(source_length)))
    right = max(left, min(int(end), int(source_length)))
    left_line, left_col = _line_cursor_for_offset(
        lines,
        line_starts,
        source_length,
        left,
    )
    right_line, right_col = _line_cursor_for_offset(
        lines,
        line_starts,
        source_length,
        right,
    )
    if left_line == right_line:
        return lines[left_line][left_col:right_col]
    parts = [lines[left_line][left_col:]]
    parts.extend(lines[left_line + 1 : right_line])
    parts.append(lines[right_line][:right_col])
    return "\n".join(parts)


def _canonical_line_chunks(
    lines: Sequence[str],
    line_starts: Sequence[int],
    source_length: int,
    *,
    chunk_chars: int,
) -> Iterable[str]:
    """Yield fixed offset windows of exact canonical line-vector text.

    The compact line-start witness maps each window boundary in O(log lines),
    while tuple slicing and ``str.join`` assemble the bounded body in C. This
    avoids both a complete document string and one Python-level operation per
    logical line. Huge individual lines remain bounded by ``chunk_chars``.
    """

    try:
        limit = max(1, int(chunk_chars))
    except (TypeError, ValueError, OverflowError):
        limit = int(DEFAULT_EDITOR_LITERAL_SCAN_CHARS)

    length = max(0, int(source_length))
    if length <= 0:
        yield ""
        return
    for left in range(0, length, limit):
        yield _canonical_line_range_text(
            lines,
            line_starts,
            length,
            left,
            min(length, left + limit),
        )


def _scan_literal_replacement_chunks(
    chunks: Iterable[str],
    request: _ReplacementScanRequest,
    *,
    replace_all: bool,
    case_sensitive: bool,
) -> ReplacementEditScan:
    """Scan fixed-width escaped literal matches over overlapping chunks."""

    flags = 0 if case_sensitive else re.IGNORECASE
    pattern = re.compile(re.escape(request.search), flags)
    overlap = max(0, len(request.search) - 1)
    carry = ""
    consumed = 0
    next_allowed = int(request.start)
    retained_bytes = 0
    spans = array(OFFSET_TYPECODE)
    edit_count = 0

    for raw_chunk in chunks:
        chunk = str(raw_chunk)
        window_start = consumed - len(carry)
        window = carry + chunk
        consumed += len(chunk)
        local_start = max(0, next_allowed - window_start)

        for found in pattern.finditer(window, pos=local_start):
            found_start = window_start + int(found.start())
            found_end = window_start + int(found.end())
            if found_start < next_allowed:
                continue
            if edit_count >= request.match_limit:
                return ReplacementEditScan(
                    ok=False,
                    error=(
                        "replace match limit exceeded: "
                        f"more than {request.match_limit} matches"
                    ),
                )
            retained_bytes += request.replacement_bytes + 48
            if retained_bytes > request.result_limit:
                return ReplacementEditScan(
                    ok=False,
                    error=(
                        "replace result budget exceeded: "
                        f"more than {request.result_limit} bytes"
                    ),
                )
            spans.append(found_start)
            spans.append(found_end)
            edit_count += 1
            next_allowed = found_end
            if not replace_all:
                return ReplacementEditScan(
                    ok=True,
                    edits=ReplacementEdits._from_owned_uniform_spans(
                        spans,
                        request.value,
                    ),
                )

        carry = window[-overlap:] if overlap > 0 else ""

    if edit_count <= 0:
        return ReplacementEditScan(ok=False, error="not found")
    return ReplacementEditScan(
        ok=True,
        edits=ReplacementEdits._from_owned_uniform_spans(
            spans,
            request.value,
        ),
    )


def scan_literal_replacement_edits_lines(
    lines: Sequence[str],
    search: str,
    value: str,
    *,
    start_index: int = 0,
    replace_all: bool = True,
    case_sensitive: bool = True,
    max_matches: int = DEFAULT_EDITOR_REPLACE_MAX_MATCHES,
    max_pattern_bytes: int = DEFAULT_EDITOR_REPLACE_PATTERN_MAX_BYTES,
    max_result_bytes: int = DEFAULT_REGEX_WORKER_RESULT_MAX_BYTES,
    chunk_chars: int = DEFAULT_EDITOR_LITERAL_SCAN_CHARS,
    line_starts: Sequence[int] | None = None,
) -> ReplacementEditScan:
    """Plan literal replacements without assembling a complete source string.

    ``re.escape`` plus Python's ordinary ``IGNORECASE`` engine remains the
    semantics oracle, including its Unicode case behavior. Because an escaped
    non-empty literal has fixed character width, retaining ``len(search)-1``
    characters between bounded chunks is sufficient to discover every
    cross-boundary match exactly once. The emitted offsets are coordinates in
    canonical ``"\\n".join(lines)`` text.
    """

    source_lines = (
        lines
        if isinstance(lines, tuple) and all(isinstance(line, str) for line in lines)
        else tuple(str(line) for line in lines)
    ) or ("",)
    starts = (
        line_starts
        if line_starts is not None and len(line_starts) == len(source_lines)
        else line_start_offsets_for_lines(source_lines)
    )
    length = int(starts[len(source_lines) - 1]) + len(source_lines[-1])
    try:
        request = _prepare_replacement_scan(
            source_length=length,
            search=search,
            value=value,
            start_index=start_index,
            literal=True,
            max_matches=max_matches,
            max_pattern_bytes=max_pattern_bytes,
            max_result_bytes=max_result_bytes,
        )
    except ValueError as exc:
        return ReplacementEditScan(ok=False, error=str(exc))
    return _scan_literal_replacement_chunks(
        _canonical_line_chunks(
            source_lines,
            starts,
            length,
            chunk_chars=chunk_chars,
        ),
        request,
        replace_all=bool(replace_all),
        case_sensitive=bool(case_sensitive),
    )



def _scan_regex_replacement_request(
    request: _ReplacementScanRequest,
    *,
    source: str | None,
    source_chunks: Iterable[str] | None,
    expected_source_length: int | None,
    replace_all: bool,
    case_sensitive: bool,
    timeout_seconds: float,
    worker_context: multiprocessing.context.BaseContext | None,
) -> ReplacementEditScan:
    """Run one prepared regex scan through either exact source transport.

    Both the ordinary flat-string API and line-vector query-replace now share
    timeout normalization, replacement-template conversion, worker budgets,
    failure wording, row validation, and packed-plan publication.  Exactly one
    source owner must be supplied; the chunk path stages it outside the JSON
    request and verifies the canonical character count in the child transport.
    """

    if (source is None) == (source_chunks is None):
        raise ValueError("regex replacement scan requires exactly one source")

    replacement = convert_replacement_template(request.value)
    try:
        timeout = float(timeout_seconds)
    except (TypeError, ValueError, OverflowError):
        timeout = float(DEFAULT_EDITOR_REPLACE_REGEX_TIMEOUT_SECONDS)
    if not math.isfinite(timeout) or timeout <= 0:
        timeout = float(DEFAULT_EDITOR_REPLACE_REGEX_TIMEOUT_SECONDS)

    replace_every = bool(replace_all)
    flags = "" if case_sensitive else "i"
    worker_limit = (
        request.match_limit
        if replace_every
        else min(1, request.match_limit)
    )
    try:
        if source is not None:
            rows = bounded_regex_replacement_rows(
                source,
                request.search,
                replacement,
                start=request.start,
                replace_all=replace_every,
                flags=flags,
                timeout_seconds=timeout,
                max_matches=worker_limit,
                max_result_bytes=request.result_limit,
                worker_context=worker_context,
            )
        else:
            assert source_chunks is not None
            rows = bounded_regex_replacement_rows_from_chunks(
                source_chunks,
                request.search,
                replacement,
                expected_haystack_chars=expected_source_length,
                start=request.start,
                replace_all=replace_every,
                flags=flags,
                timeout_seconds=timeout,
                max_matches=worker_limit,
                max_result_bytes=request.result_limit,
                worker_context=worker_context,
            )
    except RegexWorkerTimeoutError as exc:
        return ReplacementEditScan(
            ok=False,
            error=str(exc),
            worker_routed=True,
            timed_out=True,
        )
    except RegexWorkerOperationError as exc:
        message = str(exc)
        if exc.kind == "match-limit" and message.startswith("regex match limit"):
            message = message.replace("regex match limit", "replace match limit", 1)
        elif exc.kind == "result-limit" and message.startswith(
            "regex result budget"
        ):
            message = message.replace(
                "regex result budget",
                "replace result budget",
                1,
            )
        return ReplacementEditScan(ok=False, error=message, worker_routed=True)
    except RegexWorkerError as exc:
        return ReplacementEditScan(ok=False, error=str(exc), worker_routed=True)

    edits = ReplacementEdits.from_rows(rows)
    if not edits:
        return ReplacementEditScan(ok=False, error="not found", worker_routed=True)
    return ReplacementEditScan(ok=True, edits=edits, worker_routed=True)


def scan_regex_replacement_edits_lines(
    lines: Sequence[str],
    search: str,
    value: str,
    *,
    start_index: int = 0,
    replace_all: bool = True,
    case_sensitive: bool = True,
    timeout_seconds: float = DEFAULT_EDITOR_REPLACE_REGEX_TIMEOUT_SECONDS,
    max_matches: int = DEFAULT_EDITOR_REPLACE_MAX_MATCHES,
    max_pattern_bytes: int = DEFAULT_EDITOR_REPLACE_PATTERN_MAX_BYTES,
    max_result_bytes: int = DEFAULT_REGEX_WORKER_RESULT_MAX_BYTES,
    chunk_chars: int = DEFAULT_EDITOR_LITERAL_SCAN_CHARS,
    line_starts: Sequence[int] | None = None,
    worker_context: multiprocessing.context.BaseContext | None = None,
) -> ReplacementEditScan:
    """Plan regex replacements from canonical line chunks without parent flattening.

    Python's regex engine still requires one contiguous ``str`` in its killable
    child.  The parent, however, consumes bounded windows of exact
    ``"\n".join(lines)`` text into a private temporary file and sends only a
    small validated descriptor.  Session-start lines and packed line starts stay
    shared; no complete joined string, escaped JSON string, or UTF-8 request body
    is retained in the editor process.
    """

    source_lines = (
        lines
        if isinstance(lines, tuple) and all(isinstance(line, str) for line in lines)
        else tuple(str(line) for line in lines)
    ) or ("",)
    starts = (
        line_starts
        if line_starts is not None and len(line_starts) == len(source_lines)
        else line_start_offsets_for_lines(source_lines)
    )
    length = int(starts[len(source_lines) - 1]) + len(source_lines[-1])
    try:
        request = _prepare_replacement_scan(
            source_length=length,
            search=search,
            value=value,
            start_index=start_index,
            literal=False,
            max_matches=max_matches,
            max_pattern_bytes=max_pattern_bytes,
            max_result_bytes=max_result_bytes,
        )
    except ValueError as exc:
        return ReplacementEditScan(ok=False, error=str(exc))

    return _scan_regex_replacement_request(
        request,
        source=None,
        source_chunks=_canonical_line_chunks(
            source_lines,
            starts,
            length,
            chunk_chars=chunk_chars,
        ),
        expected_source_length=length,
        replace_all=bool(replace_all),
        case_sensitive=bool(case_sensitive),
        timeout_seconds=timeout_seconds,
        worker_context=worker_context,
    )


def scan_replacement_edits(
    text: str,
    search: str,
    value: str,
    *,
    start_index: int = 0,
    replace_all: bool = True,
    literal: bool = False,
    case_sensitive: bool = True,
    timeout_seconds: float = DEFAULT_EDITOR_REPLACE_REGEX_TIMEOUT_SECONDS,
    max_matches: int = DEFAULT_EDITOR_REPLACE_MAX_MATCHES,
    max_pattern_bytes: int = DEFAULT_EDITOR_REPLACE_PATTERN_MAX_BYTES,
    max_result_bytes: int = DEFAULT_REGEX_WORKER_RESULT_MAX_BYTES,
    worker_context: multiprocessing.context.BaseContext | None = None,
) -> ReplacementEditScan:
    """Collect compact concrete edits without constructing mutated text.

    Match coordinates and source slices are intentionally absent. Ordinary
    replace planning only exposes a bounded sample, and query-replace can
    recover each source slice from its immutable session-start snapshot. Packed
    start/end cells plus the narrowest replacement owner avoid retaining a
    Python edit object and two Python integers per match on dense plans.
    """

    source = str(text)
    try:
        request = _prepare_replacement_scan(
            source_length=len(source),
            search=search,
            value=value,
            start_index=start_index,
            literal=bool(literal),
            max_matches=max_matches,
            max_pattern_bytes=max_pattern_bytes,
            max_result_bytes=max_result_bytes,
        )
    except ValueError as exc:
        return ReplacementEditScan(ok=False, error=str(exc))

    if literal:
        return _scan_literal_replacement_chunks(
            (source,),
            request,
            replace_all=bool(replace_all),
            case_sensitive=bool(case_sensitive),
        )

    return _scan_regex_replacement_request(
        request,
        source=source,
        source_chunks=None,
        expected_source_length=None,
        replace_all=bool(replace_all),
        case_sensitive=bool(case_sensitive),
        timeout_seconds=timeout_seconds,
        worker_context=worker_context,
    )


def scan_replacement_matches(
    text: str,
    search: str,
    value: str,
    *,
    start_index: int = 0,
    replace_all: bool = True,
    literal: bool = False,
    case_sensitive: bool = True,
    timeout_seconds: float = DEFAULT_EDITOR_REPLACE_REGEX_TIMEOUT_SECONDS,
    max_matches: int = DEFAULT_EDITOR_REPLACE_MAX_MATCHES,
    max_pattern_bytes: int = DEFAULT_EDITOR_REPLACE_PATTERN_MAX_BYTES,
    max_result_bytes: int = DEFAULT_REGEX_WORKER_RESULT_MAX_BYTES,
    worker_context: multiprocessing.context.BaseContext | None = None,
) -> ReplacementScan:
    """Compatibility projection returning rich coordinates for every edit."""

    source = str(text)
    scan = scan_replacement_edits(
        source,
        search,
        value,
        start_index=start_index,
        replace_all=replace_all,
        literal=literal,
        case_sensitive=case_sensitive,
        timeout_seconds=timeout_seconds,
        max_matches=max_matches,
        max_pattern_bytes=max_pattern_bytes,
        max_result_bytes=max_result_bytes,
        worker_context=worker_context,
    )
    if not scan.ok:
        return ReplacementScan(
            ok=False,
            error=scan.error,
            worker_routed=scan.worker_routed,
            timed_out=scan.timed_out,
        )
    return ReplacementScan(
        ok=True,
        matches=_materialize_matches(source, scan.edits),
        worker_routed=scan.worker_routed,
        timed_out=scan.timed_out,
    )


def plan_replace(
    text: str,
    search: str,
    value: str,
    *,
    start_index: int = 0,
    replace_all: bool = False,
    literal: bool = False,
    case_sensitive: bool = True,
    sample_limit: int = 3,
    timeout_seconds: float = DEFAULT_EDITOR_REPLACE_REGEX_TIMEOUT_SECONDS,
    max_matches: int = DEFAULT_EDITOR_REPLACE_MAX_MATCHES,
    max_pattern_bytes: int = DEFAULT_EDITOR_REPLACE_PATTERN_MAX_BYTES,
    max_result_bytes: int = DEFAULT_REGEX_WORKER_RESULT_MAX_BYTES,
    worker_context: multiprocessing.context.BaseContext | None = None,
) -> ReplacePlan:
    """Return a side-effect-free replacement plan.

    Regex matching never runs in the editor process. The worker materializes
    concrete replacement rows once, so applying the plan cannot re-enter the
    backtracking engine or reinterpret captures against mutated text.
    """

    text = str(text)
    search = str(search)
    value = str(value)
    try:
        raw_start = int(start_index)
    except (TypeError, ValueError, OverflowError):
        raw_start = 0
    start = 0 if replace_all else max(0, min(raw_start, len(text)))
    try:
        samples = max(0, int(sample_limit))
    except (TypeError, ValueError, OverflowError):
        samples = 3

    def fail(message: str) -> ReplacePlan:
        return ReplacePlan(
            ok=False,
            error=str(message),
            search=search,
            value=value,
            replace_all=bool(replace_all),
            literal=bool(literal),
            case_sensitive=bool(case_sensitive),
            start_index=start,
        )

    scan = scan_replacement_edits(
        text,
        search,
        value,
        start_index=start,
        replace_all=replace_all,
        literal=literal,
        case_sensitive=case_sensitive,
        timeout_seconds=timeout_seconds,
        max_matches=max_matches,
        max_pattern_bytes=max_pattern_bytes,
        max_result_bytes=max_result_bytes,
        worker_context=worker_context,
    )
    if not scan.ok:
        return fail(scan.error)

    new_text = _apply_edits(text, scan.edits)
    matches = _materialize_matches(text, scan.edits, limit=samples)
    return ReplacePlan(
        ok=True,
        search=search,
        value=value,
        replace_all=bool(replace_all),
        literal=bool(literal),
        case_sensitive=bool(case_sensitive),
        start_index=start,
        count=len(scan.edits),
        matches=matches,
        new_text=new_text,
    )
