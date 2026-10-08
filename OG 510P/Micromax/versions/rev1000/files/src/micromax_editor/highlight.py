"""micromax_editor.highlight

Syntax highlighting model.

The editor core stays UI-agnostic. Instead of embedding terminal colors or
rendering logic, we expose a tiny *span model*:

- highlight data is a list of spans per line
- each span is [start_col, end_col, tag]
- tags are small, stable-ish strings ("comment", "str", "kw", ...)

The curses TUI and the compact headless screen contract consume the same
projected spans.  Plugins retain the full-line hostcall surface.

This module is intentionally small and deterministic. It's a tokenizer-light
approach: line-local scanning plus a small keyword set.

Future extensions (deferred): incremental state across lines (multi-line
strings/comments), filetype-specific highlighters, and theme mapping.
"""

from __future__ import annotations

from dataclasses import dataclass


# Public tag vocabulary.
# Keep this set tiny; renderers/themes can choose colors later.
HIGHLIGHT_TAGS: list[str] = [
    "comment",
    "str",
    "kw",
    "num",
    "def",
]


# Visible rendering may scan from the start of a logical line to preserve the
# tiny line-local lexer state.  Keep that prefix finite so a single enormous
# line cannot make a bounded screen request perform unbounded syntax work.
VISIBLE_HIGHLIGHT_SCAN_MAX_CHARS = 4096


@dataclass(frozen=True)
class Span:
    start: int
    end: int
    tag: str

    def to_row(self) -> list[object]:
        return [int(self.start), int(self.end), str(self.tag)]


def highlight_line(filetype: str, line: str) -> list[list[object]]:
    """Return highlight spans for one line.

    Output is JSON-ish: [[start, end, tag], ...].

    For now we only provide a useful default for "micromax" and otherwise
    return an empty list.
    """

    ft = str(filetype or "").lower()
    if ft == "micromax":
        return [s.to_row() for s in _highlight_micromax_line(str(line or ""))]
    return []


def project_highlight_spans(
    spans: list[list[object]],
    *,
    fragment_start: int,
    fragment_length: int,
    display_offset: int = 0,
) -> list[list[object]]:
    """Clip full-line highlight spans into display-local coordinates.

    Malformed rows are ignored.  The output keeps the same compact
    ``[start, end, tag]`` shape as ``highlight_line`` and is suitable for
    viewport models and independent renderers. ``display_offset`` accounts for
    renderer-owned cells before the source fragment, such as softwrap
    continuation indentation.
    """

    start = max(0, int(fragment_start))
    length = max(0, int(fragment_length))
    offset = max(0, int(display_offset))
    end = start + length
    if length <= 0:
        return []

    out: list[list[object]] = []
    for raw in spans:
        if not isinstance(raw, (list, tuple)) or len(raw) < 3:
            continue
        try:
            a = int(raw[0])
            b = int(raw[1])
        except (TypeError, ValueError, OverflowError):
            continue
        tag = str(raw[2] or "")
        if tag not in HIGHLIGHT_TAGS:
            continue
        aa = max(start, a)
        bb = min(end, b)
        if bb > aa:
            out.append(
                [
                    int(offset + aa - start),
                    int(offset + bb - start),
                    tag,
                ]
            )
    return out


# ----- micromax highlighter (tiny, line-local) -----

_MICROMAX_KEYWORDS: set[str] = {
    # control-ish words in the shipped stdlib; this is intentionally partial
    "if",
    "else",
    "then",
    "begin",
    "until",
    "while",
    "repeat",
    "case",
    "of",
    "endof",
    "endcase",
    # defining words
    "variable",
    "constant",
    "hook",
}


def _highlight_micromax_line(line: str) -> list[Span]:
    spans: list[Span] = []
    n = len(line)
    i = 0

    def is_delim(ch: str) -> bool:
        return ch.isspace() or ch in [":", ";", "[", "]", "\"", "(", ")", "\\"]

    # Track whether the next word should be highlighted as a definition name.
    want_def = False

    while i < n:
        c = line[i]

        # whitespace
        if c.isspace():
            i += 1
            continue

        # line comment: \\ ... EOL
        if c == "\\":
            spans.append(Span(i, n, "comment"))
            break

        # paren comment: ( ... ) (line-local)
        if c == "(":
            j = line.find(")", i + 1)
            if j == -1:
                j = n
            else:
                j += 1
            spans.append(Span(i, j, "comment"))
            i = j
            want_def = False
            continue

        # string: "..." with minimal escapes
        if c == '"':
            j = i + 1
            while j < n:
                if line[j] == "\\" and j + 1 < n:
                    j += 2
                    continue
                if line[j] == '"':
                    j += 1
                    break
                j += 1
            spans.append(Span(i, j, "str"))
            i = j
            want_def = False
            continue

        # single-char symbols
        if c in [":", ";", "[", "]"]:
            spans.append(Span(i, i + 1, "kw"))
            want_def = (c == ":")
            i += 1
            continue

        # word/number
        j = i
        while j < n and not is_delim(line[j]):
            j += 1
        tok = line[i:j]

        if want_def and tok:
            spans.append(Span(i, j, "def"))
            want_def = False
        else:
            # number?
            t = tok
            if t.startswith("-"):
                t = t[1:]
            if t.isdigit() and tok != "":
                spans.append(Span(i, j, "num"))
            elif tok in _MICROMAX_KEYWORDS:
                spans.append(Span(i, j, "kw"))

        i = j

    # Coalesce adjacent spans with same tag (small hygiene for renderers).
    spans2: list[Span] = []
    for s in spans:
        if not spans2:
            spans2.append(s)
            continue
        prev = spans2[-1]
        if prev.tag == s.tag and prev.end == s.start:
            spans2[-1] = Span(prev.start, s.end, prev.tag)
        else:
            spans2.append(s)

    # Sanity: clamp, drop empties.
    out: list[Span] = []
    for s in spans2:
        a = max(0, min(n, int(s.start)))
        b = max(0, min(n, int(s.end)))
        if b > a and s.tag in HIGHLIGHT_TAGS:
            out.append(Span(a, b, s.tag))

    return out
