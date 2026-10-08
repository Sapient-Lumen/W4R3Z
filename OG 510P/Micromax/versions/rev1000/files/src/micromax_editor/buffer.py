from __future__ import annotations

import hashlib
from collections.abc import Callable, Iterable, Iterator, MutableSequence
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Any

# Exact dirty tracking hashes the whole logical document after each mutation.
# Keep each temporary UTF-8 allocation bounded even when a file consists of one
# enormous line.  The editor may still choose sticky ``fastdirty`` mode for a
# large buffer, but clean-baseline creation and explicit exact mode should not
# require a second full-document byte string.
_SIGNATURE_CHUNK_CHARS = 64 * 1024

# A direct join+encode is materially faster for ordinary buffers. Bound that
# fast path by characters so its worst-case UTF-8 allocation remains finite
# (at most about 4 MiB), then stream genuinely large documents.
_SIGNATURE_FAST_PATH_CHARS = 1024 * 1024

# Micromax keeps exact return-to-clean semantics for ordinary documents, then
# installs a visible buffer-local ``fastdirty=true`` override when a newly
# opened buffer reaches this measured threshold.  On the reference cloudtainer,
# the old exact path crossed roughly 2 ms/edit at 1 MiB and 9 ms/edit at 4 MiB
# before rendering or syntax work.  One MiB preserves exact semantics much
# longer than upstream micro's current 50 KiB heuristic while preventing the
# large-file per-keystroke cliff in this Python host.
FASTDIRTY_AUTO_BYTES = 1024 * 1024


def _join_line_fragments(*parts: str) -> str:
    """Join line fragments once, without chained immutable concatenations.

    One logical-line edit already has to allocate the resulting Python string.
    Chained ``prefix + replacement + suffix`` expresses that edit as two
    concatenations and can recopy a large prefix.  Presenting all fragments to
    ``str.join`` in one operation trims that copy work on the measured
    very-long-line path while remaining simple for ordinary rows.  Prefix/suffix
    slices still dominate peak Python allocation; this is not a rope.
    """

    return "".join(parts)


def _splice_line_text(
    line: str,
    start: int,
    end: int,
    replacement: str,
) -> str:
    """Return ``line[:start] + replacement + line[end:]`` in one join.

    Coordinates are expected to be clamped by the caller.  Keeping this tiny
    constructor shared prevents insert, delete, and replace from quietly
    regressing to different allocation shapes.
    """

    value = str(line)
    a = max(0, min(int(start), len(value)))
    b = max(a, min(int(end), len(value)))
    middle = str(replacement)
    if not middle:
        if a == b:
            return value
        if a == 0:
            return value[b:]
        if b >= len(value):
            return value[:a]
        return _join_line_fragments(value[:a], value[b:])
    if a == 0:
        if b >= len(value):
            return middle
        return _join_line_fragments(middle, value[b:])
    if b >= len(value):
        return _join_line_fragments(value[:a], middle)
    return _join_line_fragments(value[:a], middle, value[b:])


def _encoded_text_chunks(text: str) -> Iterator[bytes]:
    """Yield bounded UTF-8 chunks with the buffer's surrogate policy."""

    value = str(text)
    if len(value) <= _SIGNATURE_FAST_PATH_CHARS:
        if value:
            yield value.encode("utf-8", errors="surrogatepass")
        return
    for start in range(0, len(value), _SIGNATURE_CHUNK_CHARS):
        yield value[start : start + _SIGNATURE_CHUNK_CHARS].encode(
            "utf-8",
            errors="surrogatepass",
        )


def normalize_buffer_text(text: str) -> str:
    """Return the editor's canonical LF-only in-memory text form.

    Python's ``str.splitlines`` recognizes several Unicode separators beyond
    CR/LF.  Treating those code points as structural line breaks in some
    mutation paths but ordinary characters in others made cursor geometry
    depend on which helper happened to receive the text.  The editor's
    documented contract is narrower and portable: CRLF and CR normalize to LF;
    every other character remains data.
    """

    return str(text).replace("\r\n", "\n").replace("\r", "\n")


def _buffer_lines(text: str) -> list[str]:
    """Split canonical editor text while preserving a trailing empty line."""

    return normalize_buffer_text(text).split("\n")


class _ObservedLineView(MutableSequence[str]):
    """List-like live view used only while a transaction observes a buffer.

    ``Buffer.lines`` historically exposes its mutable line vector.  Ordinary
    editing still receives the exact backing ``list`` with no wrapper or
    per-mutation dispatch.  While an aggregate transaction is active, callers
    instead receive this live view so a direct slice/index mutation announces
    the first write *before* changing the backing list.  A Python embedder that
    retained the raw list before observation can still bypass this in-process
    seam; editor-owned mutation paths do not.
    """

    def __init__(self, owner: "Buffer") -> None:
        self._owner = owner

    def __len__(self) -> int:
        return len(self._owner._lines)

    def __iter__(self) -> Iterator[str]:
        return iter(self._owner._lines)

    def __getitem__(self, index: Any) -> Any:
        return self._owner._lines[index]

    def _prepare_mutation(self) -> None:
        self._owner._prepare_text_mutation()
        # The compatibility view does not publish a version/dirty boundary; its
        # caller still owns the historical ``touch_external()`` contract.  It
        # must nevertheless invalidate generation-local derived data before a
        # raw write, or a later save could adopt the pre-mutation signature.
        self._owner._current_sig = None

    def __setitem__(self, index: Any, value: Any) -> None:
        self._prepare_mutation()
        self._owner._lines[index] = value

    def __delitem__(self, index: Any) -> None:
        self._prepare_mutation()
        del self._owner._lines[index]

    def insert(self, index: int, value: str) -> None:
        self._prepare_mutation()
        self._owner._lines.insert(int(index), value)

    def append(self, value: str) -> None:
        self._prepare_mutation()
        self._owner._lines.append(value)

    def extend(self, values: Iterable[str]) -> None:
        self._prepare_mutation()
        self._owner._lines.extend(values)

    def clear(self) -> None:
        self._prepare_mutation()
        self._owner._lines.clear()

    def pop(self, index: int = -1) -> str:
        self._prepare_mutation()
        return self._owner._lines.pop(int(index))

    def remove(self, value: str) -> None:
        self._prepare_mutation()
        self._owner._lines.remove(value)

    def reverse(self) -> None:
        self._prepare_mutation()
        self._owner._lines.reverse()

    def sort(self, *args: Any, **kwargs: Any) -> None:
        self._prepare_mutation()
        self._owner._lines.sort(*args, **kwargs)

    def copy(self) -> list[str]:
        return self._owner._lines.copy()

    def count(self, value: str) -> int:
        return self._owner._lines.count(value)

    def index(self, value: str, *args: int) -> int:
        return self._owner._lines.index(value, *args)

    def __contains__(self, value: object) -> bool:
        return value in self._owner._lines

    def __repr__(self) -> str:
        return repr(self._owner._lines)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, _ObservedLineView):
            other = other._owner._lines
        return self._owner._lines == other

    def __iadd__(self, values: Iterable[str]) -> "_ObservedLineView":
        self.extend(values)
        return self

    def __imul__(self, count: int) -> "_ObservedLineView":
        self._prepare_mutation()
        self._owner._lines *= int(count)
        return self

    def __add__(self, other: object) -> list[str]:
        return self._owner._lines + other  # type: ignore[operator]

    def __radd__(self, other: object) -> list[str]:
        return other + self._owner._lines  # type: ignore[operator]

    def __mul__(self, count: int) -> list[str]:
        return self._owner._lines * int(count)

    __rmul__ = __mul__


@dataclass
class Cursor:
    """A cursor position (line, col) in *character* coordinates."""

    line: int = 0
    col: int = 0


@dataclass(frozen=True)
class BufferChange:
    """One exact line-vector splice attached to a buffer version.

    Consumers may update derived line geometry incrementally only when they
    already own ``version - 1`` and the splice preserves line count.  Unknown or
    externally-authored mutations deliberately publish no change row, forcing a
    safe rebuild instead of guessing which line objects changed.
    """

    version: int
    start_line: int
    old_line_count: int
    new_line_count: int


@dataclass(frozen=True)
class BufferSplice:
    """Exact inverse data for one normalized replacement.

    Ordinary editor undo should retain the replaced slice, not two complete
    immutable document strings.  The coordinates are copied at the mutation
    boundary so callers can replay the inverse without depending on mutable
    cursor objects owned elsewhere.
    """

    start: Cursor
    old_end: Cursor
    new_end: Cursor
    old_text: str
    new_text: str
    changed: bool


class BufferEditConflict(RuntimeError):
    """Raised when an inverse splice no longer matches its expected source."""


_EXPECTED_OLD_TEXT_UNSET = object()


class Buffer:
    """A simple line-based buffer.

    This is intentionally boring and very test-friendly.
    Once we need performance, we can swap internals (gap buffer, rope, piece
    table) behind the same API.
    """

    def __init__(self, text: str = "", *, path: str | None = None) -> None:
        self.path = path
        self._lines: list[str] = _buffer_lines(text)
        # Aggregate editor transactions install one-shot first-write observers.
        # Keep ordinary buffers on a raw list: the common typing loop pays only
        # a predictable empty-dict branch in owned mutation helpers, not a
        # permanent list-subclass dispatch.
        self._before_text_mutation_observers: dict[int, Callable[[Buffer], None]] = {}
        self._next_text_mutation_observer_id: int = 1
        self._observed_line_view: _ObservedLineView | None = None
        self.dirty: bool = False
        self.fastdirty: bool = False
        # A monotonically-increasing counter bumped on any text mutation.
        # This is a cheap, headless-friendly way to detect changes without
        # diffing the full buffer text.
        self.version: int = 0
        self.last_change: BufferChange | None = None
        self._saved_sig: tuple[int, str] = self._current_signature()
        # Exact mode already paid for this generation's signature.  Keep it so
        # save can adopt the current generation without immediately hashing the
        # same document again, and so auto-fastdirty can reason from exact bytes.
        self._current_sig: tuple[int, str] | None = self._saved_sig
        self._auto_fastdirty_enabled: bool = False
        self._auto_fastdirty_callback: Callable[[], None] | None = None

    def _text_signature(self, text: str) -> tuple[int, str]:
        """Hash one logical text value without one full encoded allocation."""

        digest = hashlib.blake2b(digest_size=16)
        byte_count = 0
        for chunk in _encoded_text_chunks(str(text)):
            digest.update(chunk)
            byte_count += len(chunk)
        return (byte_count, digest.hexdigest())

    def _current_signature(self) -> tuple[int, str]:
        """Hash the exact LF-joined document without one huge byte string.

        ``str.join`` performs the line-vector assembly in optimized native code.
        Large values are then encoded and hashed in bounded slices.  An earlier
        per-line Python walker reduced the temporary string as well, but made
        explicit exact mode more than an order of magnitude slower on files
        containing many short rows.
        """

        return self._text_signature(self.get_text())

    @staticmethod
    def line_vector_signature(lines: Iterable[str]) -> tuple[int, str]:
        """Hash trusted canonical lines as one LF-joined document, without join.

        Most ordinary edits use :meth:`_current_signature` because the native
        ``str.join`` path is materially faster for common buffers.  Recovery
        history is different: it already owns an immutable line generation and
        may replay it while ``fastdirty`` is enabled.  Retaining this generation
        signature lets replay compare against the *current* save baseline in
        O(1), without allocating a complete document merely to recover exact
        clean/dirty truth.
        """

        digest = hashlib.blake2b(digest_size=16)
        byte_count = 0
        first = True
        for line in lines:
            if first:
                first = False
            else:
                digest.update(b"\n")
                byte_count += 1
            for chunk in _encoded_text_chunks(str(line)):
                digest.update(chunk)
                byte_count += len(chunk)
        return (byte_count, digest.hexdigest())

    @property
    def baseline_byte_size(self) -> int:
        """Return the UTF-8 size of the last clean baseline."""

        return int(self._saved_sig[0])

    @property
    def current_byte_size(self) -> int | None:
        """Return the exact current UTF-8 size when this generation is known."""

        if self._current_sig is None:
            return None
        return int(self._current_sig[0])

    @property
    def current_signature(self) -> tuple[int, str] | None:
        """Return the cached exact signature for the live generation, if any."""

        if self._current_sig is None:
            return None
        return (int(self._current_sig[0]), str(self._current_sig[1]))

    def configure_auto_fastdirty(
        self,
        enabled: bool,
        callback: Callable[[], None] | None = None,
    ) -> None:
        """Configure sticky growth-triggered fast-dirty promotion.

        The editor enables this while the effective global value is not true and
        no buffer-local override is present. Promotion happens after the first
        exact generation at or above :data:`FASTDIRTY_AUTO_BYTES`; that crossing edit
        remains exactly classified, while later edits avoid whole-document
        hashing.  The callback mirrors the promotion into visible option state.
        """

        self._auto_fastdirty_enabled = bool(enabled)
        self._auto_fastdirty_callback = callback if enabled else None

    def _maybe_enable_auto_fastdirty(self, signature: tuple[int, str]) -> None:
        if (
            self.fastdirty
            or not self._auto_fastdirty_enabled
            or int(signature[0]) < FASTDIRTY_AUTO_BYTES
        ):
            return
        self.fastdirty = True
        callback = self._auto_fastdirty_callback
        if callback is not None:
            try:
                callback()
            except Exception:
                # The buffer's performance/safety policy must not make an
                # otherwise successful text mutation fail because a UI mirror
                # could not be refreshed.  Editor-owned callbacks are tiny and
                # deterministic; this is a defensive embedding boundary.
                pass

    def _refresh_dirty(self) -> None:
        signature = self._current_signature()
        self._current_sig = signature
        self.dirty = signature != self._saved_sig
        self._maybe_enable_auto_fastdirty(signature)

    def set_fastdirty(self, enabled: bool) -> None:
        target = bool(enabled)
        if self.fastdirty == target:
            return
        self.fastdirty = target
        if not self.fastdirty:
            self._refresh_dirty()

    @staticmethod
    def canonical_utf8_signature(payload: bytes) -> tuple[int, str]:
        """Hash an already materialized canonical UTF-8 document payload.

        Save already owns the exact bytes it is about to commit.  When those
        bytes are the strict UTF-8 encoding of the current LF-joined buffer,
        hashing them directly avoids rebuilding and re-encoding the complete
        document only to establish the clean baseline.
        """

        value = payload if isinstance(payload, bytes) else bytes(payload)
        digest = hashlib.blake2b(digest_size=16)
        digest.update(value)
        return (len(value), digest.hexdigest())

    def mark_clean(self, *, current_utf8: bytes | None = None) -> None:
        """Adopt the current generation as the exact clean baseline.

        ``current_utf8`` may be supplied only when it is the already-owned,
        strict UTF-8 encoding of this buffer's current canonical LF text.  The
        save path can prove that identity for an ordinary Unix/UTF-8 write and
        thereby avoid a second full text join and encode.
        """

        signature = self._current_sig
        if signature is None:
            signature = (
                self.canonical_utf8_signature(current_utf8)
                if current_utf8 is not None
                else self._current_signature()
            )
        self._current_sig = signature
        self._saved_sig = signature
        self.dirty = False

    def _touch(
        self,
        *,
        start_line: int | None = None,
        old_line_count: int | None = None,
        new_line_count: int | None = None,
    ) -> None:
        self.version += 1
        self._current_sig = None
        if (
            start_line is not None
            and old_line_count is not None
            and new_line_count is not None
        ):
            self.last_change = BufferChange(
                version=int(self.version),
                start_line=max(0, int(start_line)),
                old_line_count=max(0, int(old_line_count)),
                new_line_count=max(0, int(new_line_count)),
            )
        else:
            self.last_change = None
        if self.fastdirty:
            self.dirty = True
        else:
            self._refresh_dirty()

    def touch_external(self) -> None:
        """Mark an in-place structural edit done outside the helper methods."""

        self._touch()

    @contextmanager
    def observe_before_text_mutation(
        self,
        callback: Callable[[Buffer], None],
        *,
        once: bool = False,
    ) -> Iterator[None]:
        """Call ``callback`` immediately before owned text mutation.

        Observers may nest.  A one-shot observer removes itself only after its
        callback succeeds, so a failed journal capture prevents the mutation and
        remains armed for a retry.  This is an in-process editor seam, not a
        hostile-alias or thread-safety boundary.
        """

        ident = int(self._next_text_mutation_observer_id)
        self._next_text_mutation_observer_id += 1

        def _dispatch(buffer: Buffer) -> None:
            callback(buffer)
            if once:
                self._before_text_mutation_observers.pop(ident, None)

        self._before_text_mutation_observers[ident] = _dispatch
        try:
            yield
        finally:
            self._before_text_mutation_observers.pop(ident, None)

    def _prepare_text_mutation(self) -> None:
        """Publish one pre-mutation boundary to a stable observer snapshot."""

        observers = self._before_text_mutation_observers
        if not observers:
            return
        for callback in tuple(observers.values()):
            callback(self)

    # ---- basic access ----
    @property
    def lines(self) -> MutableSequence[str]:
        if not self._before_text_mutation_observers:
            return self._lines
        view = self._observed_line_view
        if view is None:
            view = _ObservedLineView(self)
            self._observed_line_view = view
        return view

    def get_text(self) -> str:
        return "\n".join(self._lines)

    def snapshot_lines(self) -> tuple[str, ...]:
        """Return one immutable shallow snapshot of the canonical line vector.

        Line strings are immutable, so aggregate rollback/history can retain a
        pointer vector without joining a second complete document string.  The
        tuple itself is detached from future list mutation while complete
        untouched line objects remain shared with the live buffer.
        """

        return tuple(self._lines)

    def _restore_lines_snapshot(self, lines: Iterable[str]) -> None:
        """Install a trusted canonical snapshot without deriving dirty state.

        Aggregate rollback/Undo restores ``version``, dirty policy, and saved
        signatures from the same editor-owned snapshot immediately afterward.
        Calling the ordinary mutation path here would hash/join a large document
        only to overwrite those derived fields, and would publish a misleading
        incremental ``last_change`` row for a non-monotonic history restore.
        """

        replacement = list(lines)
        if self._before_text_mutation_observers:
            # Undo/redo itself may run inside a wider aggregate transaction
            # (for example a macro containing ``Undo``).  Publish that restore
            # as the outer transaction's first write before replacing the live
            # vector; otherwise its rollback snapshot would begin *after* the
            # nested history operation and silently lose the true entry state.
            self._prepare_text_mutation()
        self._lines = replacement or [""]
        self._current_sig = None
        self.last_change = None

    def set_text(self, text: str) -> None:
        if self._before_text_mutation_observers:
            self._prepare_text_mutation()
        old_count = len(self._lines)
        self._lines = _buffer_lines(text)
        self._touch(
            start_line=0,
            old_line_count=old_count,
            new_line_count=len(self._lines),
        )

    # ---- coordinate helpers ----
    def clamp(self, cur: Cursor) -> Cursor:
        line = max(0, min(cur.line, len(self._lines) - 1))
        col = max(0, min(cur.col, len(self._lines[line])))
        return Cursor(line, col)

    def insert(self, cur: Cursor, s: str) -> Cursor:
        """Insert text at cursor, returning the updated cursor."""
        cur = self.clamp(cur)
        s = normalize_buffer_text(s)

        if "\n" not in s:
            line = self._lines[cur.line]
            if self._before_text_mutation_observers:
                self._prepare_text_mutation()
            self._lines[cur.line] = _splice_line_text(
                line,
                cur.col,
                cur.col,
                s,
            )
            self._touch(start_line=cur.line, old_line_count=1, new_line_count=1)
            return Cursor(cur.line, cur.col + len(s))

        parts = s.split("\n")
        line = self._lines[cur.line]
        before, after = line[: cur.col], line[cur.col :]
        new_lines = [_join_line_fragments(before, parts[0])]
        new_lines.extend(parts[1:-1])
        new_lines.append(_join_line_fragments(parts[-1], after))

        if self._before_text_mutation_observers:
            self._prepare_text_mutation()
        self._lines[cur.line : cur.line + 1] = new_lines
        self._touch(
            start_line=cur.line,
            old_line_count=1,
            new_line_count=len(new_lines),
        )
        return Cursor(cur.line + len(new_lines) - 1, len(parts[-1]))

    def delete_range(self, start: Cursor, end: Cursor) -> Cursor:
        """Delete text in [start,end), returning the resulting cursor."""
        start = self.clamp(start)
        end = self.clamp(end)
        if (end.line, end.col) < (start.line, start.col):
            start, end = end, start

        if start.line == end.line:
            line = self._lines[start.line]
            if self._before_text_mutation_observers:
                self._prepare_text_mutation()
            self._lines[start.line] = _splice_line_text(
                line,
                start.col,
                end.col,
                "",
            )
            self._touch(start_line=start.line, old_line_count=1, new_line_count=1)
            return Cursor(start.line, start.col)

        first = self._lines[start.line]
        last = self._lines[end.line]
        merged = _join_line_fragments(first[: start.col], last[end.col :])
        old_count = int(end.line - start.line + 1)
        if self._before_text_mutation_observers:
            self._prepare_text_mutation()
        self._lines[start.line : end.line + 1] = [merged]
        self._touch(
            start_line=start.line,
            old_line_count=old_count,
            new_line_count=1,
        )
        return Cursor(start.line, start.col)

    def get_range_text(self, start: Cursor, end: Cursor) -> str:
        """Return text in [start,end)."""
        start = self.clamp(start)
        end = self.clamp(end)
        if (end.line, end.col) < (start.line, start.col):
            start, end = end, start

        if start.line == end.line:
            return self._lines[start.line][start.col : end.col]

        out: list[str] = []
        out.append(self._lines[start.line][start.col :])
        for li in range(start.line + 1, end.line):
            out.append(self._lines[li])
        out.append(self._lines[end.line][: end.col])
        return "\n".join(out)

    def replace_range_with_witness(
        self,
        start: Cursor,
        end: Cursor,
        s: str,
        *,
        expected_old_text: object = _EXPECTED_OLD_TEXT_UNSET,
    ) -> BufferSplice:
        """Replace one range and return the compact exact inverse witness.

        The source slice is read exactly once.  Undo/redo callers may supply
        ``expected_old_text`` to fail closed rather than applying a stale
        position-based delta to text that no longer matches.
        """

        start = self.clamp(start)
        end = self.clamp(end)
        if (end.line, end.col) < (start.line, start.col):
            start, end = end, start
        start = Cursor(int(start.line), int(start.col))
        end = Cursor(int(end.line), int(end.col))

        replacement = normalize_buffer_text(s)
        old_text = self.get_range_text(start, end)
        if expected_old_text is not _EXPECTED_OLD_TEXT_UNSET:
            expected = normalize_buffer_text(str(expected_old_text))
            if old_text != expected:
                raise BufferEditConflict(
                    "buffer splice conflict at "
                    f"{start.line + 1}:{start.col}-"
                    f"{end.line + 1}:{end.col}; "
                    f"expected {len(expected)} chars, found {len(old_text)}"
                )

        if old_text == replacement:
            return BufferSplice(
                start=start,
                old_end=end,
                new_end=Cursor(int(end.line), int(end.col)),
                old_text=old_text,
                new_text=replacement,
                changed=False,
            )

        parts = replacement.split("\n")
        first = self._lines[start.line]
        last = self._lines[end.line]
        if len(parts) == 1:
            if start.line == end.line:
                new_lines = [
                    _splice_line_text(
                        first,
                        start.col,
                        end.col,
                        parts[0],
                    )
                ]
            else:
                # Replacing a multi-line range with one logical line must merge
                # the surviving outer fragments around the replacement.  Keep
                # this distinct from the true multi-line branch below; treating
                # one part as both the first and last part duplicates it and
                # incorrectly leaves two rows.
                new_lines = [
                    _join_line_fragments(
                        first[: start.col],
                        parts[0],
                        last[end.col :],
                    )
                ]
            cursor = Cursor(start.line, start.col + len(parts[0]))
        else:
            prefix = first[: start.col]
            suffix = last[end.col :]
            new_lines = [_join_line_fragments(prefix, parts[0])]
            new_lines.extend(parts[1:-1])
            new_lines.append(_join_line_fragments(parts[-1], suffix))
            cursor = Cursor(start.line + len(parts) - 1, len(parts[-1]))

        old_count = int(end.line - start.line + 1)
        if self._before_text_mutation_observers:
            self._prepare_text_mutation()
        self._lines[start.line : end.line + 1] = new_lines
        if not self._lines:
            self._lines = [""]
        self._touch(
            start_line=start.line,
            old_line_count=old_count,
            new_line_count=len(new_lines),
        )
        return BufferSplice(
            start=start,
            old_end=end,
            new_end=Cursor(int(cursor.line), int(cursor.col)),
            old_text=old_text,
            new_text=replacement,
            changed=True,
        )

    def replace_range(self, start: Cursor, end: Cursor, s: str) -> Cursor:
        """Replace ``[start,end)`` with ``s`` as one buffer mutation."""

        return self.replace_range_with_witness(start, end, s).new_end

    # ---- line helpers ----
    def replace_lines(self, lines: Iterable[str]) -> None:
        """Replace the complete canonical line vector as one owned mutation."""

        replacement = [str(line) for line in lines]
        if not replacement:
            replacement = [""]
        if self._before_text_mutation_observers:
            self._prepare_text_mutation()
        old_count = len(self._lines)
        self._lines = replacement
        self._touch(
            start_line=0,
            old_line_count=old_count,
            new_line_count=len(self._lines),
        )

    def delete_line(self, line: int) -> Cursor:
        """Delete an entire line, keeping the buffer non-empty."""
        if not self._lines:
            if self._before_text_mutation_observers:
                self._prepare_text_mutation()
            self._lines = [""]
        line = max(0, min(line, len(self._lines) - 1))

        if len(self._lines) == 1:
            if self._before_text_mutation_observers:
                self._prepare_text_mutation()
            self._lines[0] = ""
            self._touch(start_line=0, old_line_count=1, new_line_count=1)
            return Cursor(0, 0)

        if self._before_text_mutation_observers:
            self._prepare_text_mutation()
        del self._lines[line]
        self._touch(start_line=line, old_line_count=1, new_line_count=0)
        line = min(line, len(self._lines) - 1)
        return Cursor(line, 0)

    def duplicate_line(self, line: int) -> Cursor:
        """Duplicate the given line below itself."""
        if not self._lines:
            if self._before_text_mutation_observers:
                self._prepare_text_mutation()
            self._lines = [""]
        line = max(0, min(line, len(self._lines) - 1))
        if self._before_text_mutation_observers:
            self._prepare_text_mutation()
        self._lines.insert(line + 1, self._lines[line])
        self._touch(start_line=line + 1, old_line_count=0, new_line_count=1)
        return Cursor(line + 1, 0)

    def delete_char(self, cur: Cursor, *, backward: bool = False) -> Cursor:
        cur = self.clamp(cur)
        if backward:
            if cur.col > 0:
                return self.delete_range(Cursor(cur.line, cur.col - 1), cur)
            if cur.line > 0:
                prev_len = len(self._lines[cur.line - 1])
                return self.delete_range(Cursor(cur.line - 1, prev_len), Cursor(cur.line, 0))
            return cur

        # forward
        line = self._lines[cur.line]
        if cur.col < len(line):
            return self.delete_range(cur, Cursor(cur.line, cur.col + 1))
        if cur.line < len(self._lines) - 1:
            return self.delete_range(cur, Cursor(cur.line + 1, 0))
        return cur



    def word_boundary_right(self, cur: Cursor) -> Cursor:
        """Return the next word boundary to the right (micro-esque Ctrl-Right).

        A "word" is [A-Za-z0-9_]+ (unicode alnum + underscore), matching
        `word_range_at`. Movement skips the remainder of the current word (if
        inside one) and then skips separators to the next word start.

        This is intentionally conservative and UI-agnostic.
        """

        cur = self.clamp(cur)

        def is_word(ch: str) -> bool:
            return ch.isalnum() or ch == "_"

        line = int(cur.line)
        col = int(cur.col)
        while True:
            s = self._lines[line]
            n = len(s)

            # If we're at end-of-line, hop to the next line.
            if col >= n:
                if line >= len(self._lines) - 1:
                    return Cursor(line, n)
                line += 1
                col = 0
                continue

            # If we're inside a word, skip to the end of it.
            if col < n and is_word(s[col]):
                while col < n and is_word(s[col]):
                    col += 1

            # Skip separators to the next word start.
            while True:
                if col >= n:
                    break
                if is_word(s[col]):
                    return Cursor(line, col)
                col += 1

            # Reached end-of-line; continue onto the next line.
            if line >= len(self._lines) - 1:
                return Cursor(line, len(self._lines[line]))
            line += 1
            col = 0

    def word_boundary_left(self, cur: Cursor) -> Cursor:
        """Return the previous word boundary to the left (micro-esque Ctrl-Left).

        This lands at the *start* of the previous word.
        """

        cur = self.clamp(cur)

        def is_word(ch: str) -> bool:
            return ch.isalnum() or ch == "_"

        line = int(cur.line)
        col = int(cur.col)

        while True:
            if line == 0 and col == 0:
                return Cursor(0, 0)

            s = self._lines[line]
            # If we're at start-of-line, move to previous line end.
            if col == 0:
                line -= 1
                s = self._lines[line]
                col = len(s)
                continue

            i = col - 1

            # Skip separators backwards.
            while i >= 0 and not is_word(s[i]):
                i -= 1

            if i < 0:
                # Only separators before cursor on this line.
                col = 0
                continue

            # Now at a word char; skip the word backwards to its start.
            while i >= 0 and is_word(s[i]):
                i -= 1
            return Cursor(line, i + 1)
    def find(self, needle: str, *, start: Cursor | None = None) -> Cursor | None:
        """Find a substring forward from start."""
        if needle == "":
            return None
        cur = self.clamp(start or Cursor(0, 0))
        # first line from col
        idx = self._lines[cur.line].find(needle, cur.col)
        if idx >= 0:
            return Cursor(cur.line, idx)
        # subsequent lines
        for li in range(cur.line + 1, len(self._lines)):
            idx = self._lines[li].find(needle)
            if idx >= 0:
                return Cursor(li, idx)
        return None

    def word_range_at(self, cur: Cursor) -> tuple[Cursor, Cursor] | None:
        """Return (start,end) for the word under/near the cursor on the same line.

        A word is [A-Za-z0-9_]+ (unicode alnum + underscore).
        Used for micro-esque multi-cursor selection (Alt-n / ctrl-d style).
        """
        cur = self.clamp(cur)
        line = self._lines[cur.line]
        if not line:
            return None

        def is_word(ch: str) -> bool:
            return ch.isalnum() or ch == "_"

        # Choose an index to inspect.
        # If the cursor is at the end of a word, prefer the char to the left.
        idx = cur.col
        if idx > 0 and (idx == len(line) or (idx < len(line) and not is_word(line[idx]))) and is_word(line[idx - 1]):
            idx = idx - 1
        if idx >= len(line) or not is_word(line[idx]):
            return None

        start = idx
        while start > 0 and is_word(line[start - 1]):
            start -= 1
        end = idx + 1
        while end < len(line) and is_word(line[end]):
            end += 1
        return Cursor(cur.line, start), Cursor(cur.line, end)
