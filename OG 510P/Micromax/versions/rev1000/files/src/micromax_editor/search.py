from __future__ import annotations

import math
import multiprocessing
import re
import weakref
from array import array
from bisect import bisect_left, bisect_right
from collections.abc import Iterable, Iterator, Sequence
from dataclasses import dataclass
from typing import Literal

from micromax.regex_runtime import (
    RegexWorkerError,
    RegexWorkerTimeoutError,
    bounded_regex_spans,
)

from .buffer import Buffer, Cursor
from .textpos import PackedOffsets, line_start_offsets_for_lines


SearchSpan = tuple[int, int]

DEFAULT_EDITOR_REGEX_TIMEOUT_SECONDS = 0.25
DEFAULT_EDITOR_SEARCH_MAX_MATCHES = 100_000
DEFAULT_EDITOR_REGEX_PATTERN_MAX_BYTES = 10_000


class SearchPatternError(ValueError):
    """Raised when foreground-safe search preparation cannot be completed."""


class SearchMatchLimitError(RuntimeError):
    """Raised before a search materializes more than its public span budget."""


class SearchExecutionError(RuntimeError):
    """Raised when a bounded search snapshot carries an execution failure."""


class PackedSearchSpans(Sequence[SearchSpan]):
    """Read-only parallel start/end arrays with lazy pair materialization."""

    __slots__ = ("starts", "ends")

    def __init__(self, spans: Iterable[SearchSpan] = ()) -> None:
        starts = array("Q")
        ends = array("Q")
        for raw_start, raw_end in spans:
            start = max(0, int(raw_start))
            end = max(start, int(raw_end))
            starts.append(start)
            ends.append(end)
        self.starts = PackedOffsets._from_owned_array(starts)
        self.ends = PackedOffsets._from_owned_array(ends)

    @classmethod
    def _from_owned_arrays(
        cls,
        starts: array,
        ends: array,
    ) -> "PackedSearchSpans":
        if len(starts) != len(ends):
            raise ValueError("search span arrays must have equal length")
        result = cls.__new__(cls)
        result.starts = PackedOffsets._from_owned_array(starts)
        result.ends = PackedOffsets._from_owned_array(ends)
        return result

    @property
    def storage_bytes(self) -> int:
        return int(self.starts.storage_bytes + self.ends.storage_bytes)

    def __len__(self) -> int:
        return len(self.starts)

    def __getitem__(self, index: int | slice) -> SearchSpan | tuple[SearchSpan, ...]:
        if isinstance(index, slice):
            indices = range(*index.indices(len(self)))
            return tuple((self.starts[i], self.ends[i]) for i in indices)
        return (self.starts[index], self.ends[index])

    def __iter__(self) -> Iterator[SearchSpan]:
        return (
            (int(start), int(end))
            for start, end in zip(self.starts, self.ends, strict=True)
        )

    def __eq__(self, other: object) -> bool:
        if isinstance(other, PackedSearchSpans):
            return self.starts == other.starts and self.ends == other.ends
        if isinstance(other, Sequence):
            return len(self) == len(other) and all(
                left == (int(right[0]), int(right[1]))
                for left, right in zip(self, other, strict=True)
            )
        return NotImplemented

    def __repr__(self) -> str:
        count = len(self)
        if count <= 6:
            return f"PackedSearchSpans({tuple(self)!r})"
        head = tuple(self[index] for index in range(3))
        tail = tuple(self[index] for index in range(count - 3, count))
        return f"PackedSearchSpans({head!r} ... {tail!r}, count={count})"


@dataclass
class SearchState:
    query: str = ""
    literal: bool = True
    case_sensitive: bool = False
    last_match: Cursor | None = None


@dataclass(frozen=True)
class CompiledSearch:
    """One coordinate-preserving search plan shared by all search surfaces.

    Literal ignore-case searches use ``re.escape`` plus ``re.IGNORECASE``
    instead of transforming the haystack and query. Unicode case transforms can
    change string length, so offsets from a case-folded copy are not safe editor
    coordinates for the original buffer.

    Caller-authored regexes deliberately retain only their source string here.
    Compiling them in the foreground would reopen the containment boundary:
    CPython's parser itself can raise ``RecursionError`` on a deeply nested but
    byte-bounded pattern before matching begins.  The isolated worker therefore
    owns both compilation and matching for every non-literal query.
    """

    query: str
    literal: bool
    case_sensitive: bool
    source: str
    regex: re.Pattern[str] | None


@dataclass(frozen=True)
class SearchSnapshot:
    """One immutable whole-buffer match set and its source-coordinate map."""

    buffer_ref: weakref.ReferenceType[Buffer]
    buffer_version: int
    query: str
    literal: bool
    case_sensitive: bool
    text_length: int
    line_starts: PackedOffsets
    spans: PackedSearchSpans
    error: str = ""
    worker_routed: bool = False
    timed_out: bool = False

    @property
    def span_starts(self) -> PackedOffsets:
        return self.spans.starts

    @property
    def span_ends(self) -> PackedOffsets:
        return self.spans.ends

    @property
    def storage_bytes(self) -> int:
        """Return retained compact coordinate payload for this snapshot."""

        return int(self.line_starts.storage_bytes + self.spans.storage_bytes)

    def matches_state(self, buf: Buffer, state: SearchState) -> bool:
        return (
            self.buffer_ref() is buf
            and int(self.buffer_version) == int(buf.version)
            and str(self.query) == str(state.query or "")
            and bool(self.literal) == bool(state.literal)
            and bool(self.case_sensitive) == bool(state.case_sensitive)
        )

    def cursor_index(self, buf: Buffer, cursor: Cursor) -> int:
        cur = buf.clamp(cursor)
        line = max(0, min(int(cur.line), max(0, len(self.line_starts) - 1)))
        line_start = int(self.line_starts[line]) if self.line_starts else 0
        return min(int(self.text_length), int(line_start + int(cur.col)))

    def cursor_for_index(self, buf: Buffer, index: int) -> Cursor:
        if not self.line_starts:
            return Cursor(0, 0)
        bounded = max(0, min(int(index), int(self.text_length)))
        line = max(0, bisect_right(self.line_starts, bounded) - 1)
        line = min(line, max(0, len(buf.lines) - 1))
        col = max(0, bounded - int(self.line_starts[line]))
        return buf.clamp(Cursor(int(line), int(col)))


@dataclass(frozen=True)
class SearchNavigation:
    """One resolved move within an exact whole-buffer match set."""

    cursor: Cursor
    start: int
    end: int
    match_index: int
    match_count: int
    wrapped: bool = False

    @property
    def summary(self) -> str:
        return f"{int(self.match_index)}/{int(self.match_count)}"


def compile_search_strict(
    query: str,
    *,
    literal: bool = True,
    case_sensitive: bool = False,
) -> CompiledSearch | None:
    """Prepare one search pattern without compiling caller regex locally.

    The historical function name remains for compatibility.  Only escaped
    literal patterns are compiled here; non-literal syntax is validated by the
    same killable child that performs the scan.
    """

    q = str(query or "")
    if not q:
        return None
    source = re.escape(q) if bool(literal) else q
    flags = 0 if bool(case_sensitive) else re.IGNORECASE
    regex: re.Pattern[str] | None = None
    if bool(literal):
        try:
            regex = re.compile(source, flags)
        except re.error as exc:
            raise SearchPatternError(f"invalid regex: {exc}") from exc
    return CompiledSearch(
        query=q,
        literal=bool(literal),
        case_sensitive=bool(case_sensitive),
        source=source,
        regex=regex,
    )


def compile_search(
    query: str,
    *,
    literal: bool = True,
    case_sensitive: bool = False,
) -> CompiledSearch | None:
    """Prepare one search plan, returning ``None`` for empty input.

    Caller-authored regex syntax is intentionally not validated in the
    foreground; the killable worker owns that compilation step.
    """

    try:
        return compile_search_strict(
            query,
            literal=literal,
            case_sensitive=case_sensitive,
        )
    except SearchPatternError:
        return None


def search_needs_containment(
    state: SearchState,
    *,
    compiled: CompiledSearch | None = None,
) -> bool:
    """Return whether the active query uses the bounded regex lane.

    ``compiled`` is accepted for compatibility with older callers.  Direct
    editor regexes no longer rely on a risk heuristic: every non-empty,
    non-literal query is contained by default.
    """

    del compiled
    return bool(not state.literal and str(state.query or ""))


def match_spans(
    text: str,
    *,
    query: str,
    literal: bool = True,
    case_sensitive: bool = False,
    compiled: CompiledSearch | None = None,
    max_matches: int | None = None,
    timeout_seconds: float = DEFAULT_EDITOR_REGEX_TIMEOUT_SECONDS,
    worker_context: multiprocessing.context.BaseContext | None = None,
) -> list[SearchSpan]:
    """Return non-empty, non-overlapping matches in original-text offsets.

    Navigation, ``i/n`` status, and visible highlighting all consume this same
    match policy. Zero-width regex matches are omitted because the current
    editor has no visible, advancing target for them; treating them as a
    successful repeated-search destination would permit a no-movement loop.
    """

    source_text = str(text or "")
    if not source_text:
        return []
    pattern = compiled or compile_search(
        str(query or ""),
        literal=bool(literal),
        case_sensitive=bool(case_sensitive),
    )
    if pattern is None:
        return []

    try:
        limit = (
            int(DEFAULT_EDITOR_SEARCH_MAX_MATCHES)
            if max_matches is None
            else max(0, int(max_matches))
        )
    except (TypeError, ValueError, OverflowError):
        limit = int(DEFAULT_EDITOR_SEARCH_MAX_MATCHES)

    if not bool(pattern.literal):
        try:
            timeout = float(timeout_seconds)
        except (TypeError, ValueError, OverflowError):
            timeout = float(DEFAULT_EDITOR_REGEX_TIMEOUT_SECONDS)
        if not math.isfinite(timeout) or timeout <= 0:
            timeout = float(DEFAULT_EDITOR_REGEX_TIMEOUT_SECONDS)
        flags = "" if bool(pattern.case_sensitive) else "i"
        return list(
            bounded_regex_spans(
                source_text,
                pattern.source,
                flags=flags,
                timeout_seconds=timeout,
                max_matches=limit,
                worker_context=worker_context,
            )
        )

    literal_regex = pattern.regex
    if literal_regex is None:  # defensive guard for hand-built compatibility rows
        raise SearchPatternError("literal search plan has no compiled pattern")

    spans: list[SearchSpan] = []
    for match in literal_regex.finditer(source_text):
        start = int(match.start())
        end = int(match.end())
        if end <= start:
            continue
        if len(spans) >= limit:
            raise SearchMatchLimitError(
                f"search match limit exceeded: more than {limit} matches"
            )
        spans.append((start, end))
    return spans


def _packed_literal_spans(
    text: str,
    *,
    pattern: re.Pattern[str],
    max_matches: int,
) -> PackedSearchSpans:
    """Stream literal matches directly into compact snapshot storage."""

    starts = array("Q")
    ends = array("Q")
    limit = max(0, int(max_matches))
    for match in pattern.finditer(text):
        start = int(match.start())
        end = int(match.end())
        if end <= start:
            continue
        if len(starts) >= limit:
            raise SearchMatchLimitError(
                f"search match limit exceeded: more than {limit} matches"
            )
        starts.append(start)
        ends.append(end)
    return PackedSearchSpans._from_owned_arrays(starts, ends)


def search_match_spans(
    text: str,
    query: str,
    *,
    literal: bool = True,
    case_sensitive: bool = False,
) -> list[SearchSpan]:
    """Return best-effort spans for the historical rendering helper.

    Literal work remains local. Regex work uses the same killable default child
    as editor navigation, so importing this helper cannot revive synchronous
    backtracking. Its pre-existing UI contract is deliberately non-throwing:
    invalid syntax, timeout, protocol failure, or a match-budget refusal renders
    as no highlights. Command/navigation surfaces use :func:`scan_buffer` and
    keep the exact failure visible to the user instead of passing through here.
    """

    try:
        return match_spans(
            text,
            query=query,
            literal=literal,
            case_sensitive=case_sensitive,
        )
    except (RegexWorkerError, SearchMatchLimitError, SearchPatternError):
        return []


def _line_starts(buf: Buffer) -> PackedOffsets:
    starts = line_start_offsets_for_lines(buf.lines)
    return PackedOffsets._from_owned_array(starts)


def _search_snapshot(
    buf: Buffer,
    state: SearchState,
    *,
    text_length: int,
    line_starts: Sequence[int],
    spans: Sequence[SearchSpan] = (),
    error: str = "",
    worker_routed: bool = False,
    timed_out: bool = False,
) -> SearchSnapshot:
    packed_lines = (
        line_starts
        if isinstance(line_starts, PackedOffsets)
        else PackedOffsets(line_starts)
    )
    packed_spans = (
        spans
        if isinstance(spans, PackedSearchSpans)
        else PackedSearchSpans(spans)
    )
    return SearchSnapshot(
        buffer_ref=weakref.ref(buf),
        buffer_version=int(buf.version),
        query=str(state.query or ""),
        literal=bool(state.literal),
        case_sensitive=bool(state.case_sensitive),
        text_length=int(text_length),
        line_starts=packed_lines,
        spans=packed_spans,
        error=str(error or ""),
        worker_routed=bool(worker_routed),
        timed_out=bool(timed_out),
    )


def scan_buffer(
    buf: Buffer,
    state: SearchState,
    *,
    timeout_seconds: float = DEFAULT_EDITOR_REGEX_TIMEOUT_SECONDS,
    max_matches: int = DEFAULT_EDITOR_SEARCH_MAX_MATCHES,
    max_pattern_bytes: int = DEFAULT_EDITOR_REGEX_PATTERN_MAX_BYTES,
    worker_context: multiprocessing.context.BaseContext | None = None,
) -> SearchSnapshot:
    """Materialize one bounded reusable search truth row for a buffer version.

    Literal searches remain local. Every non-literal regex match operation runs
    in the shared killable worker, so safety does not depend on recognizing one
    particular catastrophic-backtracking shape. The returned snapshot carries
    an exact error instead of converting timeout, worker failure, invalid syntax,
    or match-budget exhaustion into ``not found``.
    """

    text = buf.get_text()
    starts = _line_starts(buf)
    query = str(state.query or "")
    query_bytes = len(query.encode("utf-8", errors="replace"))
    try:
        pattern_limit = max(0, int(max_pattern_bytes))
    except (TypeError, ValueError, OverflowError):
        pattern_limit = int(DEFAULT_EDITOR_REGEX_PATTERN_MAX_BYTES)
    if pattern_limit > 0 and query_bytes > pattern_limit:
        return _search_snapshot(
            buf,
            state,
            text_length=len(text),
            line_starts=starts,
            error=(
                "search pattern too large: "
                f"{query_bytes} bytes > {pattern_limit}"
            ),
        )
    try:
        compiled = compile_search_strict(
            state.query,
            literal=state.literal,
            case_sensitive=state.case_sensitive,
        )
    except SearchPatternError as exc:
        return _search_snapshot(
            buf,
            state,
            text_length=len(text),
            line_starts=starts,
            error=str(exc),
        )
    if compiled is None or not text:
        return _search_snapshot(
            buf,
            state,
            text_length=len(text),
            line_starts=starts,
        )

    try:
        timeout = float(timeout_seconds)
    except (TypeError, ValueError, OverflowError):
        timeout = float(DEFAULT_EDITOR_REGEX_TIMEOUT_SECONDS)
    if not math.isfinite(timeout) or timeout <= 0:
        timeout = float(DEFAULT_EDITOR_REGEX_TIMEOUT_SECONDS)
    try:
        match_limit = max(0, int(max_matches))
    except (TypeError, ValueError, OverflowError):
        match_limit = int(DEFAULT_EDITOR_SEARCH_MAX_MATCHES)

    worker_routed = bool(not state.literal)
    try:
        if worker_routed:
            flags = "" if bool(state.case_sensitive) else "i"
            spans: Sequence[SearchSpan] = bounded_regex_spans(
                text,
                compiled.source,
                flags=flags,
                timeout_seconds=timeout,
                max_matches=match_limit,
                worker_context=worker_context,
            )
        else:
            literal_pattern = compiled.regex
            if literal_pattern is None:
                raise SearchPatternError("literal search plan has no compiled pattern")
            spans = _packed_literal_spans(
                text,
                pattern=literal_pattern,
                max_matches=match_limit,
            )
    except RegexWorkerTimeoutError as exc:
        return _search_snapshot(
            buf,
            state,
            text_length=len(text),
            line_starts=starts,
            error=str(exc),
            worker_routed=True,
            timed_out=True,
        )
    except RegexWorkerError as exc:
        message = str(exc)
        marker = "search match limit exceeded:"
        if marker in message:
            message = marker + message.split(marker, 1)[1]
        return _search_snapshot(
            buf,
            state,
            text_length=len(text),
            line_starts=starts,
            error=message,
            worker_routed=True,
        )
    except SearchMatchLimitError as exc:
        return _search_snapshot(
            buf,
            state,
            text_length=len(text),
            line_starts=starts,
            error=str(exc),
        )

    return _search_snapshot(
        buf,
        state,
        text_length=len(text),
        line_starts=starts,
        spans=spans,
        worker_routed=worker_routed,
    )


def _usable_snapshot(
    buf: Buffer,
    state: SearchState,
    snapshot: SearchSnapshot | None,
) -> SearchSnapshot:
    if snapshot is not None and snapshot.matches_state(buf, state):
        return snapshot
    return scan_buffer(buf, state)


def match_start_indices(
    buf: Buffer,
    state: SearchState,
    *,
    snapshot: SearchSnapshot | None = None,
) -> list[int]:
    """Return source-buffer starts for every visible/advancing match."""

    snap = _usable_snapshot(buf, state, snapshot)
    return [int(start) for start in snap.span_starts]


def search_position(
    buf: Buffer,
    state: SearchState,
    *,
    cursor: Cursor,
    snapshot: SearchSnapshot | None = None,
) -> tuple[int, int]:
    """Return ``(current, total)`` from the exact shared match set.

    ``current`` is 1-based when the cursor is exactly on a match start and zero
    otherwise. ``total`` excludes zero-width regex matches for the same reason
    navigation and visible highlighting do.
    """

    snap = _usable_snapshot(buf, state, snapshot)
    total = int(len(snap.spans))
    if total <= 0:
        return (0, 0)
    cursor_index = int(snap.cursor_index(buf, cursor))
    index = int(bisect_left(snap.span_starts, cursor_index))
    if index < total and snap.span_starts[index] == cursor_index:
        return (int(index + 1), total)
    return (0, total)


def navigate_search(
    buf: Buffer,
    state: SearchState,
    *,
    start: Cursor,
    direction: Literal["forward", "backward"] = "forward",
    include_start: bool = False,
    wrap: bool = False,
    snapshot: SearchSnapshot | None = None,
) -> SearchNavigation | None:
    """Resolve one target without mutating editor state."""

    snap = _usable_snapshot(buf, state, snapshot)
    if snap.error:
        raise SearchExecutionError(str(snap.error))
    if not snap.spans:
        return None

    start_index = int(snap.cursor_index(buf, start))
    wrapped = False

    if direction == "forward":
        target_index = int(
            bisect_left(snap.span_starts, start_index)
            if include_start
            else bisect_right(snap.span_starts, start_index)
        )
        if target_index >= len(snap.spans):
            if not wrap:
                return None
            target_index = 0
            wrapped = True
    elif direction == "backward":
        boundary = (
            bisect_right(snap.span_starts, start_index)
            if include_start
            else bisect_left(snap.span_starts, start_index)
        )
        target_index = int(boundary - 1)
        if target_index < 0:
            if not wrap:
                return None
            target_index = int(len(snap.spans) - 1)
            wrapped = True
    else:  # defensive guard for non-typed callers
        raise ValueError(f"unsupported search direction: {direction}")

    match_start, match_end = snap.spans[target_index]
    return SearchNavigation(
        cursor=snap.cursor_for_index(buf, int(match_start)),
        start=int(match_start),
        end=int(match_end),
        match_index=int(target_index + 1),
        match_count=int(len(snap.spans)),
        wrapped=bool(wrapped),
    )


def project_match_spans(
    spans: Sequence[SearchSpan],
    *,
    fragment_start: int,
    fragment_length: int,
    display_offset: int = 0,
    current_start: int | None = None,
    span_ends: Sequence[int] | None = None,
) -> tuple[list[SearchSpan], list[SearchSpan]]:
    """Project whole-buffer matches into one visible source fragment.

    ``fragment_start`` and ``fragment_length`` use flat source-buffer
    coordinates. ``display_offset`` accounts for renderer-owned prefix cells,
    such as soft-wrap continuation indentation. A cross-line or clipped match
    is projected into every visible fragment it intersects instead of being
    rediscovered by running the pattern independently against each row.
    """

    source_start = max(0, int(fragment_start))
    source_length = max(0, int(fragment_length))
    source_end = int(source_start + source_length)
    offset = max(0, int(display_offset))
    if source_length <= 0:
        return ([], [])

    visible: list[SearchSpan] = []
    current: list[SearchSpan] = []
    wanted_current = int(current_start) if current_start is not None else None
    first_index = (
        int(bisect_right(span_ends, source_start))
        if span_ends is not None
        else 0
    )
    for span_index in range(first_index, len(spans)):
        raw_start, raw_end = spans[span_index]
        match_start = int(raw_start)
        match_end = int(raw_end)
        if match_end <= source_start:
            continue
        if match_start >= source_end:
            break
        intersection_start = max(match_start, source_start)
        intersection_end = min(match_end, source_end)
        if intersection_end <= intersection_start:
            continue
        projected = (
            int(offset + intersection_start - source_start),
            int(offset + intersection_end - source_start),
        )
        visible.append(projected)
        if wanted_current is not None and match_start == wanted_current:
            current.append(projected)
    return (visible, current)


def find_next(buf: Buffer, state: SearchState, *, start: Cursor) -> Cursor | None:
    """Compatibility helper: find at/after ``start`` without wrapping."""

    result = navigate_search(
        buf,
        state,
        start=start,
        direction="forward",
        include_start=True,
        wrap=False,
    )
    return result.cursor if result is not None else None


def find_prev(buf: Buffer, state: SearchState, *, start: Cursor) -> Cursor | None:
    """Compatibility helper: find strictly before ``start`` without wrapping."""

    result = navigate_search(
        buf,
        state,
        start=start,
        direction="backward",
        include_start=False,
        wrap=False,
    )
    return result.cursor if result is not None else None
