from __future__ import annotations

from dataclasses import dataclass
import hashlib


@dataclass
class Cursor:
    """A cursor position (line, col) in *character* coordinates."""

    line: int = 0
    col: int = 0


class Buffer:
    """A simple line-based buffer.

    This is intentionally boring and very test-friendly.
    Once we need performance, we can swap internals (gap buffer, rope, piece
    table) behind the same API.
    """

    def __init__(self, text: str = "", *, path: str | None = None) -> None:
        self.path = path
        self._lines: list[str] = text.splitlines(keepends=False)
        if text.endswith("\n"):
            # keep a trailing empty line if the file ended with a newline
            self._lines.append("")
        if not self._lines:
            self._lines = [""]
        self.dirty: bool = False
        self.fastdirty: bool = False
        # A monotonically-increasing counter bumped on any text mutation.
        # This is a cheap, headless-friendly way to detect changes without
        # diffing the full buffer text.
        self.version: int = 0
        self._saved_sig: tuple[int, str] = self._text_signature(self.get_text())

    def _text_signature(self, text: str) -> tuple[int, str]:
        data = str(text).encode("utf-8", errors="surrogatepass")
        h = hashlib.blake2b(data, digest_size=16).hexdigest()
        return (len(data), h)

    def _current_signature(self) -> tuple[int, str]:
        return self._text_signature(self.get_text())

    def _refresh_dirty(self) -> None:
        self.dirty = self._current_signature() != self._saved_sig

    def set_fastdirty(self, enabled: bool) -> None:
        self.fastdirty = bool(enabled)
        if not self.fastdirty:
            self._refresh_dirty()

    def mark_clean(self) -> None:
        self._saved_sig = self._current_signature()
        self.dirty = False

    def _touch(self) -> None:
        self.version += 1
        if self.fastdirty:
            self.dirty = True
        else:
            self._refresh_dirty()

    def touch_external(self) -> None:
        """Mark an in-place structural edit done outside the helper methods."""

        self._touch()

    # ---- basic access ----
    @property
    def lines(self) -> list[str]:
        return self._lines

    def get_text(self) -> str:
        return "\n".join(self._lines)

    def set_text(self, text: str) -> None:
        self._lines = text.splitlines(keepends=False)
        if text.endswith("\n"):
            self._lines.append("")
        if not self._lines:
            self._lines = [""]
        self._touch()

    # ---- coordinate helpers ----
    def clamp(self, cur: Cursor) -> Cursor:
        line = max(0, min(cur.line, len(self._lines) - 1))
        col = max(0, min(cur.col, len(self._lines[line])))
        return Cursor(line, col)

    def insert(self, cur: Cursor, s: str) -> Cursor:
        """Insert text at cursor, returning the updated cursor."""
        cur = self.clamp(cur)

        if "\n" not in s:
            line = self._lines[cur.line]
            self._lines[cur.line] = line[: cur.col] + s + line[cur.col :]
            self._touch()
            return Cursor(cur.line, cur.col + len(s))

        parts = s.split("\n")
        line = self._lines[cur.line]
        before, after = line[: cur.col], line[cur.col :]
        new_lines = [before + parts[0]]
        new_lines.extend(parts[1:-1])
        new_lines.append(parts[-1] + after)

        self._lines[cur.line : cur.line + 1] = new_lines
        self._touch()
        return Cursor(cur.line + len(new_lines) - 1, len(parts[-1]))

    def delete_range(self, start: Cursor, end: Cursor) -> Cursor:
        """Delete text in [start,end), returning the resulting cursor."""
        start = self.clamp(start)
        end = self.clamp(end)
        if (end.line, end.col) < (start.line, start.col):
            start, end = end, start

        if start.line == end.line:
            line = self._lines[start.line]
            self._lines[start.line] = line[: start.col] + line[end.col :]
            self._touch()
            return Cursor(start.line, start.col)

        first = self._lines[start.line]
        last = self._lines[end.line]
        merged = first[: start.col] + last[end.col :]
        self._lines[start.line : end.line + 1] = [merged]
        self._touch()
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

    def replace_range(self, start: Cursor, end: Cursor, s: str) -> Cursor:
        """Replace [start,end) with s, returning the updated cursor."""
        cur = self.delete_range(start, end)
        return self.insert(cur, s)

    # ---- line helpers ----
    def delete_line(self, line: int) -> Cursor:
        """Delete an entire line, keeping the buffer non-empty."""
        if not self._lines:
            self._lines = [""]
        line = max(0, min(line, len(self._lines) - 1))

        if len(self._lines) == 1:
            self._lines[0] = ""
            self._touch()
            return Cursor(0, 0)

        del self._lines[line]
        self._touch()
        line = min(line, len(self._lines) - 1)
        return Cursor(line, 0)

    def duplicate_line(self, line: int) -> Cursor:
        """Duplicate the given line below itself."""
        if not self._lines:
            self._lines = [""]
        line = max(0, min(line, len(self._lines) - 1))
        self._lines.insert(line + 1, self._lines[line])
        self._touch()
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
