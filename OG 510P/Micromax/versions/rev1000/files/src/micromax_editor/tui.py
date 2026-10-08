from __future__ import annotations

"""micromax_editor.tui

A tiny curses-based TUI for the headless editor core.

Goal: provide the minimal tactile loop early:
  input -> ed.dispatch_key -> render

This remains a deliberately small proving ground for the core semantics.  It
does consume the shared bounded visual-cue model, so syntax, selections,
search, diagnostics, and docs emphasis cannot quietly diverge from headless
screen snapshots.
"""

import curses
from collections.abc import Sequence
import sys
from dataclasses import dataclass
import time
from typing import Any
import re

from .editor import (
    Editor,
    brace_match_spans as _brace_match_spans_shared,
    colorcolumn_screen_x as _colorcolumn_screen_x_shared,
    matching_brace_positions as _matching_brace_positions_shared,
    overflow_marker_cells as _overflow_marker_cells_shared,
    parse_showchars_option as _parse_showchars_option_shared,
    render_showchars_fragment as _render_showchars_fragment_shared,
    search_match_spans,
    tab_error_spans as _tab_error_spans_shared,
    trailing_whitespace_spans as _trailing_whitespace_spans_shared,
)
from .markdown_docs import (
    _ellipsize_left,
    _ellipsize_right,
    md_balanced_span,
    md_backslash_escaped,
    md_docs_continuation_line,
    md_fenced_code_line_flags,
    md_html_block_line_flags,
    md_html_comment_line_spans,
    md_indented_code_line_flags,
    md_inline_code_delimiter_spans,
    md_inline_code_spans,
    md_inline_html_tag_spans,
    md_inline_link_target,
    md_inline_link_target_multiline,
    md_link_matches,
    md_norm_ref_id,
)
from .startup import create_editor_runtime, open_initial_buffer


def _model_int(value: object, default: int = 0) -> int:
    """Return an integer model field without collapsing a valid zero coordinate."""

    try:
        return int(value)  # type: ignore[arg-type]
    except (TypeError, ValueError, OverflowError):
        return int(default)


HIGHLIGHT_PRECEDENCE = (
    "syntax",
    "docs-inline",
    "showchar",
    "color-column",
    "whitespace-diagnostic",
    "brace-match",
    "search",
    "selection-secondary",
    "selection-primary",
    "search-current",
)


def replace_curses_color(
    attr: int,
    color_attr: int,
    *,
    color_mask: int | None = None,
) -> int:
    """Replace, rather than bitwise-combine, one curses color pair."""

    mask = int(curses.A_COLOR if color_mask is None else color_mask)
    return int((int(attr) & ~mask) | int(color_attr))


def _span_covers(spans: Sequence[tuple[int, int]], start: int, end: int) -> bool:
    return any(int(a) <= int(start) and int(end) <= int(b) for a, b in spans)


def _tagged_span_at(
    spans: Sequence[tuple[int, int, str]],
    start: int,
    end: int,
) -> str:
    for a, b, tag in spans:
        if int(a) <= int(start) and int(end) <= int(b):
            return str(tag)
    return ""


def _model_spans(value: object) -> list[tuple[int, int]]:
    """Read valid half-open spans from one shared-model field."""

    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        return []
    out: list[tuple[int, int]] = []
    for raw in value:
        if not isinstance(raw, Sequence) or isinstance(raw, (str, bytes, bytearray)):
            continue
        if len(raw) < 2:
            continue
        try:
            a = int(raw[0])
            b = int(raw[1])
        except (TypeError, ValueError, OverflowError):
            continue
        if a >= 0 and b > a:
            out.append((a, b))
    return out


def _model_tagged_spans(value: object) -> list[tuple[int, int, str]]:
    """Read valid tagged half-open spans from one shared-model field."""

    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        return []
    out: list[tuple[int, int, str]] = []
    for raw in value:
        if not isinstance(raw, Sequence) or isinstance(raw, (str, bytes, bytearray)):
            continue
        if len(raw) < 3:
            continue
        try:
            a = int(raw[0])
            b = int(raw[1])
        except (TypeError, ValueError, OverflowError):
            continue
        tag = str(raw[2] or "")
        if a >= 0 and b > a and tag:
            out.append((a, b, tag))
    return out


def syntax_highlight_attr(
    base_attr: int,
    tag: str,
    *,
    colors: bool | None = None,
) -> int:
    """Map one tiny syntax tag onto restrained reference-TUI attributes."""

    attr = int(base_attr)
    kind = str(tag or "")
    if kind == "comment":
        attr |= curses.A_DIM
    elif kind == "kw":
        attr |= curses.A_BOLD
    elif kind == "def":
        attr |= curses.A_BOLD | curses.A_UNDERLINE

    use_colors = bool(colors) if colors is not None else False
    if colors is None:
        try:
            use_colors = bool(curses.has_colors())
        except Exception:
            use_colors = False
    if not use_colors:
        return int(attr)

    pair_by_tag = {
        "kw": 1,
        "str": 2,
        "num": 4,
        "def": 5,
    }
    pair = pair_by_tag.get(kind)
    if pair is None:
        return int(attr)
    try:
        return replace_curses_color(attr, curses.color_pair(int(pair)))
    except Exception:
        return int(attr)


def highlight_segment_points(
    start: int,
    end: int,
    *span_groups: Sequence[tuple[int, int]],
) -> list[int]:
    """Return sorted segment boundaries clipped to one visible range."""

    aa = int(start)
    bb = int(end)
    if bb <= aa:
        return [aa]
    points = {aa, bb}
    for spans in span_groups:
        for raw_start, raw_end in spans:
            span_start = max(aa, int(raw_start))
            span_end = min(bb, int(raw_end))
            if span_end <= span_start:
                continue
            points.add(span_start)
            points.add(span_end)
    return sorted(points)


def viewport_highlight_work_needed(
    *span_groups: Sequence[tuple[int, int]],
    colorcolumn_x: int | None = None,
) -> bool:
    """Return whether the segmented viewport path has visible work to do."""

    return colorcolumn_x is not None or any(bool(spans) for spans in span_groups)


def viewport_highlight_attr(
    base_attr: int,
    start: int,
    end: int,
    *,
    docs_dim: Sequence[tuple[int, int]] | None = None,
    docs_bold: Sequence[tuple[int, int]] | None = None,
    docs_italic: Sequence[tuple[int, int]] | None = None,
    showchars: Sequence[tuple[int, int]] | None = None,
    colorcolumn: Sequence[tuple[int, int]] | None = None,
    trailing: Sequence[tuple[int, int]] | None = None,
    tab_error: Sequence[tuple[int, int]] | None = None,
    braces: Sequence[tuple[int, int]] | None = None,
    search: Sequence[tuple[int, int]] | None = None,
    current_search: Sequence[tuple[int, int]] | None = None,
    secondary_selection: Sequence[tuple[int, int]] | None = None,
    primary_selection: Sequence[tuple[int, int]] | None = None,
    italic_attr: int = 0,
    brace_attr: int = 0,
) -> int:
    """Resolve the reference viewport highlight precedence for one segment.

    Ordinary search stays below direct selections.  The current search match is
    last and adds underline, so it remains distinguishable when query-replace
    or another interaction also selects the same text.  Every direct-manipulation
    layer clears inherited dim state rather than letting syntax comments or
    whitespace diagnostics make selected text unreadable.
    """

    attr = int(base_attr)
    a = int(start)
    b = int(end)
    dim_spans = docs_dim or ()
    bold_spans = docs_bold or ()
    italic_spans = docs_italic or ()
    showchar_spans = showchars or ()
    color_spans = colorcolumn or ()
    trailing_spans = trailing or ()
    tab_spans = tab_error or ()
    brace_spans = braces or ()
    search_spans = search or ()
    current_spans = current_search or ()
    secondary_spans = secondary_selection or ()
    primary_spans = primary_selection or ()

    if _span_covers(dim_spans, a, b):
        attr |= curses.A_DIM
    if _span_covers(bold_spans, a, b):
        attr |= curses.A_BOLD
    if _span_covers(italic_spans, a, b):
        attr |= int(italic_attr)
    if _span_covers(showchar_spans, a, b):
        attr |= curses.A_DIM
    if _span_covers(color_spans, a, b):
        attr |= curses.A_REVERSE | curses.A_DIM
    if _span_covers(trailing_spans, a, b) or _span_covers(tab_spans, a, b):
        attr |= curses.A_REVERSE | curses.A_DIM
    if _span_covers(brace_spans, a, b):
        attr |= int(brace_attr)
    if _span_covers(search_spans, a, b):
        attr = (attr & ~int(curses.A_DIM)) | curses.A_REVERSE
    selection_emphasis = int(curses.A_DIM | curses.A_BOLD | curses.A_UNDERLINE)
    if _span_covers(secondary_spans, a, b):
        attr = (attr & ~selection_emphasis) | curses.A_REVERSE | curses.A_UNDERLINE
    if _span_covers(primary_spans, a, b):
        attr = (attr & ~selection_emphasis) | curses.A_REVERSE | curses.A_BOLD
    if _span_covers(current_spans, a, b):
        attr = (
            (attr & ~int(curses.A_DIM))
            | curses.A_REVERSE
            | curses.A_BOLD
            | curses.A_UNDERLINE
        )
    return int(attr)


def _merge_spans(spans: list[tuple[int, int]]) -> list[tuple[int, int]]:
    """Merge overlapping/adjacent spans.

    Spans are [start,end) indices.
    """

    if not spans:
        return []
    spans2 = sorted((int(a), int(b)) for a, b in spans if int(b) > int(a))
    out: list[tuple[int, int]] = []
    cur_a, cur_b = spans2[0]
    for a, b in spans2[1:]:
        if a <= cur_b:
            cur_b = max(cur_b, b)
        else:
            out.append((cur_a, cur_b))
            cur_a, cur_b = a, b
    out.append((cur_a, cur_b))
    return out



@dataclass(frozen=True)
class MdInlineMarkupMatch:
    """Tiny docs/help inline-markup match used by docs-cues snapshots."""

    kind: str
    start: int
    end: int
    body_start: int
    body_end: int
    delimiter: str
    delimiter_length: int
    text: str


def prompt_match_spans(text: str, query: str) -> list[tuple[int, int]]:
    """Return best-effort highlight spans for a picker suggestion line.

    Policy (tiny, deterministic, UI-only):
      - Split *query* on whitespace into tokens.
      - For each token, prefer case-insensitive **substring** matches.
      - If a token has no substring hit, fall back to a tiny **subsequence**
        matcher (fzf-style) and highlight the matched characters.

    Returned spans are [start,end) indices into *text*.
    """

    s = str(text or "")
    q = str(query or "").strip()
    if not s or not q:
        return []

    toks = [t for t in re.split(r"\s+", q) if t]
    if not toks:
        return []

    low = s.casefold()

    def _subseq_positions(hay: str, needle: str) -> list[int] | None:
        """Return subsequence match positions, or None."""
        h = str(hay or "")
        n = str(needle or "")
        if not n:
            return []
        out: list[int] = []
        start = 0
        for ch in n:
            pos = h.find(ch, start)
            if pos < 0:
                return None
            out.append(pos)
            start = pos + 1
        return out

    spans: list[tuple[int, int]] = []
    for t in toks:
        tlow = str(t).casefold()
        if not tlow:
            continue

        # Prefer substring hits (can have multiple occurrences).
        found_any = False
        start = 0
        while True:
            i = low.find(tlow, start)
            if i < 0:
                break
            spans.append((i, i + len(tlow)))
            found_any = True
            start = i + max(1, len(tlow))

        if found_any:
            continue

        # Fallback: subsequence highlight (single-character spans).
        pos = _subseq_positions(low, tlow)
        if pos:
            for i in pos:
                spans.append((i, i + 1))

    return _merge_spans(spans)


def trailing_whitespace_spans(
    line: str,
    *,
    frag_start: int = 0,
    frag_text: str | None = None,
) -> list[tuple[int, int]]:
    """Return the shared trailing-whitespace projection."""

    return _trailing_whitespace_spans_shared(
        line,
        frag_start=frag_start,
        frag_text=frag_text,
    )


def tab_error_spans(
    line: str,
    *,
    tabstospaces: bool,
    frag_start: int = 0,
    frag_text: str | None = None,
) -> list[tuple[int, int]]:
    """Return the shared indentation-diagnostic projection."""

    return _tab_error_spans_shared(
        line,
        tabstospaces=tabstospaces,
        frag_start=frag_start,
        frag_text=frag_text,
    )


def parse_showchars_option(raw: str) -> dict[str, str]:
    """Parse the shared tiny ``showchars`` option string."""

    return _parse_showchars_option_shared(raw)


def render_showchars_fragment(
    line: str,
    *,
    frag_start: int = 0,
    frag_text: str | None = None,
    spec: dict[str, str] | None = None,
    source_text_x: int | None = None,
) -> tuple[str, list[tuple[int, int]]]:
    """Return the shared visible-fragment ``showchars`` rendering result."""

    return _render_showchars_fragment_shared(
        line,
        frag_start=frag_start,
        frag_text=frag_text,
        spec=spec,
        source_text_x=source_text_x,
    )


def matching_brace_positions(
    lines: list[str],
    *,
    line: int,
    col: int,
    match_left: bool = True,
) -> list[tuple[int, int]]:
    """Return the shared textual brace-pair positions."""

    return _matching_brace_positions_shared(
        lines,
        line=line,
        col=col,
        match_left=match_left,
    )


def brace_match_spans(
    *,
    line_index: int,
    frag_start: int,
    frag_text: str,
    brace_positions: list[tuple[int, int]],
) -> list[tuple[int, int]]:
    """Return the shared visible brace spans."""

    return _brace_match_spans_shared(
        line_index=line_index,
        frag_start=frag_start,
        frag_text=frag_text,
        brace_positions=brace_positions,
    )


def brace_match_attr(ed: Editor, *, local_options: dict[str, Any] | None = None) -> int:
    """Return the tiny renderer-local style for visible brace matches."""

    style = str(ed.options.get("matchbracestyle", local=local_options) or "underline").strip().lower()
    if style == "highlight":
        return int(curses.A_BOLD | curses.A_REVERSE)
    return int(curses.A_BOLD | curses.A_UNDERLINE)


def cursorline_row_attr(ed: Editor, *, row: int, current_row: int, local_options: dict[str, Any] | None = None) -> int:
    """Return a tiny current-row highlight attribute for the rendered buffer view.

    This keeps the first ``cursorline`` pass deliberately small and renderer-local:
    when enabled, only the *currently visible* row under the primary cursor gets
    an extra cue. Under softwrap that means the active visual row, not every
    wrapped fragment of the logical line.
    """

    if int(row) != int(current_row):
        return 0
    try:
        enabled = bool(ed.options.get("cursorline", local=local_options))
    except Exception:
        enabled = False
    if not enabled:
        return 0
    return int(curses.A_UNDERLINE)


def colorcolumn_screen_x(
    *,
    colorcolumn: int,
    frag_start: int,
    view_width: int,
    softwrap: bool,
) -> int | None:
    """Return the shared visible ``colorcolumn`` cell."""

    return _colorcolumn_screen_x_shared(
        colorcolumn=colorcolumn,
        frag_start=frag_start,
        view_width=view_width,
        softwrap=softwrap,
    )


def _key_to_name(ch: Any) -> str | None:
    """Translate a *single* curses input event into an editor key name.

    Notes:
      - This function does **not** interpret multi-event sequences such as
        Alt/Meta key chords (often encoded as an ESC prefix).
      - For those, see :func:`decode_key_event`.
    """

    # Wide-character mode returns either an int (KEY_*) or a 1-char string.
    if isinstance(ch, int):
        m = {
            curses.KEY_LEFT: "LeftArrow",
            curses.KEY_RIGHT: "RightArrow",
            curses.KEY_UP: "UpArrow",
            curses.KEY_DOWN: "DownArrow",
            curses.KEY_HOME: "Home",
            curses.KEY_END: "End",
            curses.KEY_PPAGE: "PageUp",
            curses.KEY_NPAGE: "PageDown",
            curses.KEY_DC: "Delete",
            curses.KEY_BACKSPACE: "Backspace",
            curses.KEY_ENTER: "Enter",
        }
        # Shifted arrows (not supported on all terminals).
        m.update(
            {
                getattr(curses, "KEY_SLEFT", -1): "Shift-LeftArrow",
                getattr(curses, "KEY_SRIGHT", -1): "Shift-RightArrow",
                getattr(curses, "KEY_SUP", -1): "Shift-UpArrow",
                getattr(curses, "KEY_SDOWN", -1): "Shift-DownArrow",
            }
        )
        if ch in m and m[ch] is not None:
            return m[ch]
        return None

    if not isinstance(ch, str) or ch == "":
        return None

    # common control keys
    if ch == "\n" or ch == "\r":
        return "Enter"
    if ch == "\t":
        return "Tab"
    if ch == "\x1b":
        return "Esc"
    # Ctrl-Space (NUL) is a popular command palette binding.
    if ch == "\x00":
        return "Ctrl-Space"
    if ch in ("\x7f", "\b"):
        return "Backspace"

    # Ctrl-A..Ctrl-Z -> 1..26
    o = ord(ch)
    if 1 <= o <= 26:
        return f"Ctrl-{chr(o + 96)}"

    return ch


def _alt_combo_name(ch: Any) -> str | None:
    """Translate the *second* event of an ESC-prefixed Alt chord.

    Many terminals encode Alt/Meta chords as: ESC + <key>. In curses, the
    initial ESC often arrives as a distinct event, so the simplest MVP is a
    one-event lookahead.

    This intentionally only covers the low-hanging fruit: Alt+letters,
    Alt+punctuation, and Alt+special keys that curses decodes into KEY_* ints.
    """

    base = _key_to_name(ch)
    if base is None:
        return None
    # Letters: encode "Alt-Shift-x" for uppercase so bindings can be explicit.
    if isinstance(base, str) and len(base) == 1 and base.isalpha():
        if base.isupper():
            return f"Alt-Shift-{base.lower()}"
        return f"Alt-{base}"
    return f"Alt-{base}"


def decode_key_event(first: Any, second: Any | None = None) -> str | None:
    """Decode curses input into editor key names.

    - If *first* is ESC and *second* is provided, treat it as an Alt/Meta chord.
    - Otherwise decode just *first*.

    This is a small, testable helper so key-decoding doesn't hide in the TUI
    event loop.
    """

    if first == "\x1b" and second is not None:
        return _alt_combo_name(second)
    return _key_to_name(first)



# ----- paste helpers (UI-only) -----

_BRACKETED_PASTE_START = ["\x1b", "[", "2", "0", "0", "~"]
_BRACKETED_PASTE_END = ["\x1b", "[", "2", "0", "1", "~"]


def is_paste_char(ev: Any) -> bool:
    """Return True if *ev* is a character that can appear in a paste burst."""

    if not isinstance(ev, str) or len(ev) != 1:
        return False
    # Allow tabs and newlines even though they aren't "printable".
    if ev in ("\n", "\r", "\t"):
        return True
    return ev.isprintable() and ev != "\x1b"


def normalize_paste_text(s: str) -> str:
    """Normalize pasted text for the editor core (CRLF/CR -> LF)."""

    t = str(s or "")
    t = t.replace("\r\n", "\n")
    t = t.replace("\r", "\n")
    return t


def parse_bracketed_paste_stream(events: list[str]) -> tuple[str | None, list[str]]:
    """Parse a bracketed paste stream from raw characters.

    If *events* starts with ESC[200~ and contains a matching ESC[201~,
    return (payload, rest). Otherwise return (None, events).

    This is a pure helper used by tests; the live TUI loop reads from curses.
    """

    xs = [str(x) for x in (events or [])]
    if len(xs) < len(_BRACKETED_PASTE_START) or xs[: len(_BRACKETED_PASTE_START)] != _BRACKETED_PASTE_START:
        return (None, xs)

    for i in range(len(_BRACKETED_PASTE_START), len(xs) - len(_BRACKETED_PASTE_END) + 1):
        if xs[i : i + len(_BRACKETED_PASTE_END)] == _BRACKETED_PASTE_END:
            payload = ''.join(xs[len(_BRACKETED_PASTE_START) : i])
            rest = xs[i + len(_BRACKETED_PASTE_END) :]
            return (normalize_paste_text(payload), rest)

    return (None, xs)

def md_link_label_spans(
    line: str,
    defs: dict[str, str],
    footdefs: dict[str, tuple[int, int]] | None = None,
    masked_spans: list[tuple[int, int]] | None = None,
    next_line: str = "",
    next_next_line: str = "",
) -> list[tuple[int, int]]:
    """Return underline spans for markdown links in a docs/help line.

    This is intentionally tiny and mirrors the editor's docs link parsing:
      - inline links: [label](dest "title")
      - reference links: [label][id] and [label][]
      - footnotes: [^id] (only when a matching definition exists)
      - shortcut reference links: [id] (only when a matching definition exists)
      - autolinks: <https://...> / <mailto:...>

    Backtick code spans are masked first so code-ish text does not get link
    underlines or nested markdown treatment in the docs TUI.

    Spans are (start,end) indices for the *label text* (or URL) inside the
    visible delimiters so the TUI can underline them.
    """

    s = str(line or '')
    spans = [
        (int(match.label_start), int(match.label_end))
        for match in md_link_matches(s, defs, footdefs, masked_spans=masked_spans, next_line=next_line, next_next_line=next_next_line)
        if int(match.label_start) != int(match.label_end)
    ]
    spans.sort()
    return spans


def md_footnote_ref_token_spans(
    line: str,
    footdefs: dict[str, tuple[int, int]] | None = None,
    *,
    masked_spans: list[tuple[int, int]] | None = None,
    next_line: str = "",
    next_next_line: str = "",
) -> list[tuple[int, int]]:
    """Return whole-token spans for visible markdown footnote references.

    This is intentionally tiny and UI-only. It reuses :func:`md_link_matches`
    so the live docs/help TUI can give ``[^id]`` source tokens a small visual
    cue without growing another footnote parser path.

    Returned spans cover the full visible token (including brackets) for valid
    footnote references on *line*.
    """

    s = str(line or '')
    spans = [
        (int(match.start), int(match.end))
        for match in md_link_matches(
            s,
            {},
            footdefs,
            masked_spans=masked_spans,
            next_line=next_line,
            next_next_line=next_next_line,
        )
        if str(match.kind) == 'footnote' and int(match.end) > int(match.start)
    ]
    spans.sort()
    return spans


def md_autolink_token_spans(
    line: str,
    *,
    masked_spans: list[tuple[int, int]] | None = None,
    next_line: str = "",
    next_next_line: str = "",
) -> list[tuple[int, int]]:
    """Return whole-token spans for visible supported autolinks.

    This stays intentionally tiny and UI-only. It reuses :func:`md_link_matches`
    so the live docs/help TUI can give visible ``<https://...>`` /
    ``<mailto:...>`` source tokens a small cue without inventing another
    autolink parser path.

    Returned spans cover the full visible autolink token (including angle
    brackets) for supported autolinks on *line*.
    """

    s = str(line or '')
    spans = [
        (int(match.start), int(match.end))
        for match in md_link_matches(
            s,
            {},
            {},
            masked_spans=masked_spans,
            next_line=next_line,
            next_next_line=next_next_line,
        )
        if str(match.kind) == 'autolink' and int(match.end) > int(match.start)
    ]
    spans.sort()
    return spans


def md_raw_html_tag_token_spans(
    line: str,
    *,
    masked_spans: list[tuple[int, int]] | None = None,
) -> list[tuple[int, int]]:
    """Return whole-token spans for visible inline raw HTML tags.

    This stays intentionally tiny and UI-only. It reuses the editor's shared
    inline raw-HTML span helper so the live docs/help TUI can make visible
    ``<kbd>`` / ``</kbd>`` / ``<a name=...>`` style source read a little more
    honestly without growing another parser path. Supported autolinks like
    ``<https://...>`` stay out of this helper because they already get their
    own source-view cue.

    Returned spans cover the full visible raw-HTML tag token on *line*.
    """

    s = str(line or '')
    if not s:
        return []

    masks = [(int(a), int(b)) for a, b in md_inline_code_spans(s)]
    if masked_spans:
        masks.extend((int(a), int(b)) for a, b in masked_spans)

    autolinks = {
        (int(a), int(b))
        for a, b in md_autolink_token_spans(s, masked_spans=masked_spans)
    }
    spans = [
        (int(a), int(b))
        for a, b in md_inline_html_tag_spans(s, masked_spans=masks)
        if int(b) > int(a) and (int(a), int(b)) not in autolinks
    ]
    spans.sort()
    return spans


def md_image_token_spans(
    line: str,
    defs: dict[str, str],
    *,
    masked_spans: list[tuple[int, int]] | None = None,
    next_line: str = "",
    next_next_line: str = "",
) -> list[tuple[int, int]]:
    """Return whole-token spans for visible supported markdown image syntax.

    This stays intentionally tiny and UI-only. It reuses the editor's shared
    markdown helpers (balanced spans, escape handling, and destination parsing)
    so the live docs/help TUI can make inert ``![alt](dest)`` / ``![alt][id]``
    source read a little more honestly without growing another parser path.

    Returned spans cover the full visible token (including ``!`` and brackets)
    for supported inline/reference/shortcut image forms on *line*.
    """

    s = str(line or '')
    if not s:
        return []

    mask_spans = [(int(a), int(b)) for a, b in md_inline_code_spans(s)]
    if masked_spans:
        mask_spans.extend((int(a), int(b)) for a, b in masked_spans)

    def _covered(a: int, b: int) -> bool:
        aa = int(a)
        bb = int(b)
        return any(int(sa) <= aa and bb <= int(sb) for sa, sb in mask_spans)

    out: list[tuple[int, int]] = []
    i = 0
    while i < len(s) - 1:
        if s[i] != '!' or s[i + 1] != '[':
            i += 1
            continue
        if md_backslash_escaped(s, i) or _covered(i, i + 1):
            i += 1
            continue

        label_span = md_balanced_span(s, i + 1, opener='[', closer=']')
        if label_span is None:
            i += 1
            continue
        la, lb = label_span
        if _covered(i, lb):
            i = max(i + 1, lb)
            continue

        label = s[la + 1 : lb - 1]
        after = s[lb:lb + 1]

        if after == '(':
            inner_span = md_balanced_span(s, lb, opener='(', closer=')')
            if inner_span is not None:
                _, end = inner_span
                if not _covered(i, end):
                    target = md_inline_link_target(s[lb + 1 : end - 1])
                    if target:
                        out.append((i, end))
                        i = end
                        continue
            target = md_inline_link_target_multiline(s[lb + 1 :], next_line, next_next_line)
            if target:
                out.append((i, len(s)))
                i = len(s)
                continue

        if after == '[':
            id_span = md_balanced_span(s, lb, opener='[', closer=']')
            if id_span is not None:
                _, end = id_span
                if not _covered(i, end):
                    rid = s[lb + 1 : end - 1].strip() or label.strip()
                    if defs.get(md_norm_ref_id(rid)):
                        out.append((i, end))
                        i = end
                        continue

        if after != ':':
            rid = label.strip()
            if defs.get(md_norm_ref_id(rid)):
                out.append((i, lb))
                i = lb
                continue

        i += 1

    out.sort()
    return out


def md_link_source_token_spans(
    line: str,
    defs: dict[str, str],
    footdefs: dict[str, tuple[int, int]] | None = None,
    *,
    masked_spans: list[tuple[int, int]] | None = None,
    next_line: str = "",
    next_next_line: str = "",
) -> list[tuple[int, int]]:
    """Return non-label source spans for visible supported markdown links.

    This stays intentionally tiny and UI-only. It reuses :func:`md_link_matches`
    so the live docs/help TUI can make visible markdown link scaffolding — the
    brackets plus destination/reference tail around the underlined label — read
    a little more like deliberate source without adding another parser path.

    Returned spans cover only the visible *non-label* pieces of supported
    ordinary links on *line*:

      - inline links: ``[label](dest)`` -> ``[`` + ``](`` + ``dest)``
      - reference links: ``[label][id]`` -> ``[`` + ``][id]``
      - shortcut refs: ``[label]`` -> ``[`` + ``]``

    Footnote references, autolinks, and images stay on their dedicated helpers.
    """

    s = str(line or '')
    if not s:
        return []

    out: list[tuple[int, int]] = []
    for match in md_link_matches(
        s,
        defs,
        footdefs,
        masked_spans=masked_spans,
        next_line=next_line,
        next_next_line=next_next_line,
    ):
        if str(match.kind) != 'link':
            continue
        a = int(match.start)
        b = int(match.end)
        la = int(match.label_start)
        lb = int(match.label_end)
        if la > a:
            out.append((a, la))
        if b > lb:
            out.append((lb, b))

    out.sort()
    return out


_MD_ESCAPED_MARKDOWN_CUE_CHARS = set('[]()!<>*_~`')


def md_escaped_markdown_token_spans(
    line: str,
    *,
    masked_spans: list[tuple[int, int]] | None = None,
) -> list[tuple[int, int]]:
    r"""Return tiny source-view cue spans for escaped markdown punctuation.

    This stays intentionally tiny and UI-only. It recognizes visible
    backslash-escaped markdown-significant punctuation like ``\[``, ``\!``,
    ``\<``, ``\*``, ``\_``, ``\~``, and ``\``` so the live docs/help TUI
    can hint that those characters are deliberate source escapes rather than
    stray prose punctuation.

    Policy is intentionally small:
      - only two-character escape pairs are cued
      - only a focused markdown-significant punctuation subset participates
      - escaped pairs inside inline code (or caller-supplied masked spans) are
        ignored
      - escaped backslashes do not recursively cue later characters

    Returned spans cover the visible two-character escape pair.
    """

    s = str(line or '')
    if not s:
        return []

    masks = [(int(a), int(b)) for a, b in md_inline_code_spans(s)]
    if masked_spans:
        masks.extend((int(a), int(b)) for a, b in masked_spans)

    def _covered(a: int, b: int) -> bool:
        aa = int(a)
        bb = int(b)
        return any(int(sa) <= aa and bb <= int(sb) for sa, sb in masks)

    out: list[tuple[int, int]] = []
    for i in range(len(s) - 1):
        if s[i] != '\\':
            continue
        if md_backslash_escaped(s, i):
            continue
        if s[i + 1] not in _MD_ESCAPED_MARKDOWN_CUE_CHARS:
            continue
        if _covered(i, i + 2):
            continue
        out.append((i, i + 2))
    out.sort()
    return out


# ----- tiny markdown inline emphasis helpers (docs/help scanability) -----


def _mask_inline_spans(line: str, spans: list[tuple[int, int]]) -> str:
    """Return *line* with *spans* blanked out for later regex scans."""

    s = str(line or "")
    if not s or not spans:
        return s
    xs = list(s)
    for a, b in spans:
        aa = max(0, int(a))
        bb = min(len(xs), int(b))
        for i in range(aa, bb):
            xs[i] = ' '
    return ''.join(xs)


_STRONG_STAR_RE = re.compile(r"(?<!\\)\*\*(?=\S)(?P<body>.+?)(?<=\S)\*\*")
_STRONG_UNDER_RE = re.compile(r"(?<![\\\w])__(?=\S)(?P<body>.+?)(?<=\S)__(?!\w)")
_STRIKE_RE = re.compile(r"(?<!\\)~~(?=\S)(?P<body>.+?)(?<=\S)~~")
_EM_STAR_RE = re.compile(r"(?<!\\)(?<!\*)\*(?!\*)(?=\S)(?P<body>.+?)(?<=\S)(?<!\*)\*(?!\*)")
_EM_UNDER_RE = re.compile(r"(?<![\\\w])_(?=\S)(?P<body>.+?)(?<=\S)_(?!\w)")


def _md_inline_markup_body_spans(masked: str, pattern: re.Pattern[str]) -> list[tuple[int, int]]:
    """Return body spans for a tiny markdown inline markup regex."""

    out: list[tuple[int, int]] = []
    for m in pattern.finditer(masked):
        a = int(m.start('body'))
        b = int(m.end('body'))
        if b > a:
            out.append((a, b))
    return out


def _md_inline_markup_match_spans(masked: str, pattern: re.Pattern[str]) -> list[tuple[int, int]]:
    """Return full-match spans for a tiny markdown inline markup regex."""

    out: list[tuple[int, int]] = []
    for m in pattern.finditer(masked):
        a = int(m.start())
        b = int(m.end())
        if b > a:
            out.append((a, b))
    return out


def _md_inline_markup_delimiter_spans(masked: str, pattern: re.Pattern[str]) -> list[tuple[int, int]]:
    """Return delimiter-token spans for a tiny markdown inline markup regex."""

    out: list[tuple[int, int]] = []
    for m in pattern.finditer(masked):
        a = int(m.start())
        ba = int(m.start('body'))
        bb = int(m.end('body'))
        b = int(m.end())
        if ba > a:
            out.append((a, ba))
        if b > bb:
            out.append((bb, b))
    return out



def _md_inline_markup_matches(masked: str, pattern: re.Pattern[str], *, kind: str) -> list[MdInlineMarkupMatch]:
    """Return tiny structured inline-markup matches for one regex pattern."""

    out: list[MdInlineMarkupMatch] = []
    for m in pattern.finditer(masked):
        start = int(m.start())
        end = int(m.end())
        body_start = int(m.start('body'))
        body_end = int(m.end('body'))
        if end <= start or body_end <= body_start:
            continue
        delimiter = masked[start:body_start]
        delimiter_length = max(0, len(delimiter))
        out.append(
            MdInlineMarkupMatch(
                kind=str(kind),
                start=start,
                end=end,
                body_start=body_start,
                body_end=body_end,
                delimiter=str(delimiter),
                delimiter_length=delimiter_length,
                text=masked[body_start:body_end],
            )
        )
    return out



def md_inline_markup_matches(line: str) -> list[MdInlineMarkupMatch]:
    """Return tiny structured docs/help inline-markup matches.

    Accepted forms intentionally mirror the existing tiny visible-style helpers:
    strong (`**...**` / `__...__`), emphasis (`*...*` / `_..._`), and strike
    (`~~...~~`). Code spans still take precedence, and emphasis stays out of
    strong/strike bodies.
    """

    s = str(line or "")
    protected = md_inline_code_spans(s)
    strong_masked = _mask_inline_spans(s, protected)

    out = _md_inline_markup_matches(strong_masked, _STRONG_STAR_RE, kind='strong')
    out.extend(_md_inline_markup_matches(strong_masked, _STRONG_UNDER_RE, kind='strong'))

    protected += _md_inline_markup_match_spans(strong_masked, _STRONG_STAR_RE)
    protected += _md_inline_markup_match_spans(strong_masked, _STRONG_UNDER_RE)

    strike_masked = _mask_inline_spans(s, protected)
    out.extend(_md_inline_markup_matches(strike_masked, _STRIKE_RE, kind='strike'))
    protected += _md_inline_markup_match_spans(strike_masked, _STRIKE_RE)

    masked = _mask_inline_spans(s, protected)
    out.extend(_md_inline_markup_matches(masked, _EM_STAR_RE, kind='emphasis'))
    out.extend(_md_inline_markup_matches(masked, _EM_UNDER_RE, kind='emphasis'))
    out.sort(key=lambda m: (int(m.start), int(m.end), str(m.kind)))
    return out


def md_strong_spans(line: str) -> list[tuple[int, int]]:
    """Return body spans for tiny markdown strong emphasis.

    Accepted forms (best-effort, UI-only):
      - ``**strong**``
      - ``__strong__``

    Policy is intentionally small:
      - excludes escaped openers
      - requires non-whitespace just inside the delimiters
      - ignores text already claimed by inline-code spans
      - keeps underscore-delimited forms from matching inside words
    """

    s = str(line or "")
    masked = _mask_inline_spans(s, md_inline_code_spans(s))
    out = _md_inline_markup_body_spans(masked, _STRONG_STAR_RE)
    out.extend(_md_inline_markup_body_spans(masked, _STRONG_UNDER_RE))
    out.sort()
    return out


def md_strikethrough_spans(line: str) -> list[tuple[int, int]]:
    """Return body spans for tiny markdown strikethrough.

    Accepted form (best-effort, UI-only): ``~~strike~~``.
    """

    s = str(line or "")
    masked = _mask_inline_spans(s, md_inline_code_spans(s))
    return _md_inline_markup_body_spans(masked, _STRIKE_RE)


def md_emphasis_spans(line: str) -> list[tuple[int, int]]:
    """Return body spans for tiny markdown emphasis.

    Accepted forms (best-effort, UI-only):
      - ``*emphasis*``
      - ``_emphasis_``

    Policy is intentionally small:
      - excludes escaped openers
      - requires non-whitespace just inside delimiters
      - ignores text already claimed by inline code, strong, or strike spans
      - keeps underscore-delimited forms from matching inside words
    """

    s = str(line or "")
    protected = md_inline_code_spans(s)
    strong_masked = _mask_inline_spans(s, protected)
    protected += _md_inline_markup_match_spans(strong_masked, _STRONG_STAR_RE)
    protected += _md_inline_markup_match_spans(strong_masked, _STRONG_UNDER_RE)
    strike_masked = _mask_inline_spans(s, protected)
    protected += _md_inline_markup_match_spans(strike_masked, _STRIKE_RE)
    masked = _mask_inline_spans(s, protected)
    out = _md_inline_markup_body_spans(masked, _EM_STAR_RE)
    out.extend(_md_inline_markup_body_spans(masked, _EM_UNDER_RE))
    out.sort()
    return out


def md_inline_markup_delimiter_spans(line: str) -> list[tuple[int, int]]:
    """Return delimiter-token spans for tiny markdown inline markup.

    Accepted forms (best-effort, UI-only):
      - emphasis: ``*emphasis*`` / ``_emphasis_``
      - strong: ``**strong**`` / ``__strong__``
      - strike: ``~~strike~~``

    Policy intentionally mirrors the existing tiny body-span helpers:
      - ignores escaped delimiters
      - ignores text already claimed by inline code
      - keeps emphasis from reparsing inside strong or strike runs
      - stays deliberately far smaller than full CommonMark delimiter-run rules

    Returned spans cover only the visible delimiter tokens, not the styled body
    text. This lets the live docs/help TUI make source-view punctuation look a
    little more like deliberate markdown without growing another parser path.
    """

    s = str(line or "")
    protected = md_inline_code_spans(s)
    strong_masked = _mask_inline_spans(s, protected)

    out = _md_inline_markup_delimiter_spans(strong_masked, _STRONG_STAR_RE)
    out.extend(_md_inline_markup_delimiter_spans(strong_masked, _STRONG_UNDER_RE))

    protected += _md_inline_markup_match_spans(strong_masked, _STRONG_STAR_RE)
    protected += _md_inline_markup_match_spans(strong_masked, _STRONG_UNDER_RE)

    strike_masked = _mask_inline_spans(s, protected)
    out.extend(_md_inline_markup_delimiter_spans(strike_masked, _STRIKE_RE))
    protected += _md_inline_markup_match_spans(strike_masked, _STRIKE_RE)

    masked = _mask_inline_spans(s, protected)
    out.extend(_md_inline_markup_delimiter_spans(masked, _EM_STAR_RE))
    out.extend(_md_inline_markup_delimiter_spans(masked, _EM_UNDER_RE))
    out.sort()
    return out


# ----- tiny markdown list/task-list helpers (docs/help scanability) -----


def md_list_marker(line: str, *, max_leading_spaces: int | None = 3) -> tuple[int, int, str] | None:
    """Return the marker span/kind for a tiny markdown list item.

    Accepted forms (best-effort, UI-only):
      - ``- item`` / ``+ item`` / ``* item``
      - ``1. item`` / ``1) item``

    Default policy mirrors a small CommonMark-friendly subset:
      - up to three leading spaces
      - bullet markers ``-`` / ``+`` / ``*``
      - ordered markers with 1-9 digits plus ``.`` or ``)``
      - marker followed by whitespace or end-of-line

    ``max_leading_spaces=None`` opts into a looser source-view mode that allows
    deeper indentation for nested list items. Callers should only use that when
    they already know the line is *not* part of an indented code block.

    Returns ``(start, end, kind)`` where ``kind`` is ``"bullet"`` or
    ``"ordered"``. The span covers the literal marker token only (not the
    following whitespace).
    """

    s = str(line or "")
    indent_pat = r" *" if max_leading_spaces is None else f" {{0,{int(max_leading_spaces)}}}"
    m = re.match(rf"^(?P<indent>{indent_pat})(?P<marker>(?:[-+*]|\d{{1,9}}[.)]))(?:[ \t]+|$)", s)
    if not m:
        return None
    a = int(m.start('marker'))
    b = int(m.end('marker'))
    marker = str(m.group('marker') or '')
    kind = 'ordered' if marker and marker[0].isdigit() else 'bullet'
    return (a, b, kind)


def md_task_checkbox(line: str, *, max_leading_spaces: int | None = 3) -> tuple[int, int, bool] | None:
    """Return the checkbox span/state for a tiny markdown task-list item.

    Accepted forms (best-effort, UI-only):
      - ``- [ ] item``
      - ``* [x] item``
      - ``1. [X] item``

    ``max_leading_spaces`` matches :func:`md_list_marker`: the default stays
    conservative, while ``None`` allows nested list/task items in source-view
    contexts that already ruled out real indented code blocks.

    Returns ``(start, end, checked)`` for the literal ``[ ]`` / ``[x]`` token,
    or ``None`` when the line does not look like a task-list item.
    """

    s = str(line or "")
    info = md_list_marker(s, max_leading_spaces=max_leading_spaces)
    if not info:
        return None
    _ma, mb, _kind = info
    m = re.match(r"(?P<gap>[ \t]+)(?P<box>\[(?P<mark>[ xX])\])(?:[ \t]+|$)", s[mb:])
    if not m:
        return None
    a = mb + int(m.start('box'))
    b = mb + int(m.end('box'))
    checked = str(m.group('mark') or '').lower() == 'x'
    return (a, b, checked)


def md_task_body_span(line: str, *, max_leading_spaces: int | None = 3) -> tuple[int, int] | None:
    """Return the body span for a tiny markdown task-list item, if any."""

    info = md_task_checkbox(line, max_leading_spaces=max_leading_spaces)
    if not info:
        return None
    _a, b, _checked = info
    s = str(line or "")
    while b < len(s) and s[b].isspace():
        b += 1
    if b >= len(s):
        return None
    return (b, len(s))


# ----- tiny markdown blockquote helpers (docs/help scanability) -----


def md_blockquote_prefix(line: str) -> tuple[int, int, int] | None:
    """Return the prefix span/depth for a tiny markdown blockquote line.

    Accepted forms (best-effort, UI-only):
      - ``> quote``
      - ``  > > nested``
      - ``>>dense`` is treated as nested quote markers only when the final
        marker is followed by whitespace or end-of-line.

    Returns ``(start, end, depth)`` for the marker prefix. The prefix does not
    include leading indentation, but does include the whitespace between nested
    markers so the TUI can style the left quote rail as one compact span.
    """

    s = str(line or "")
    i = 0
    while i < len(s) and i < 3 and s[i] == ' ':
        i += 1
    if i >= len(s) or s[i] != '>':
        return None
    start = i
    j = i
    depth = 0
    while j < len(s) and s[j] == '>':
        depth += 1
        j += 1
        if j >= len(s):
            return (start, j, depth)
        if s[j] == '>':
            continue
        if s[j] in ' \\t':
            while j < len(s) and s[j] in ' \\t':
                j += 1
            if j < len(s) and s[j] == '>':
                continue
            return (start, j, depth)
        return None
    return None


def md_blockquote_body_span(line: str) -> tuple[int, int] | None:
    """Return the body span for a tiny markdown blockquote line, if any."""

    info = md_blockquote_prefix(line)
    if not info:
        return None
    _a, b, _depth = info
    s = str(line or "")
    if b >= len(s):
        return None
    return (b, len(s))


def md_blockquote_alert_marker(line: str) -> tuple[int, int, str] | None:
    """Return the alert-marker span/kind for a tiny GitHub-style alert line.

    Accepted forms (best-effort, UI-only):
      - ``> [!NOTE]``
      - ``> [!TIP] body``
      - ``  > > [!WARNING]``

    The marker must appear immediately after the blockquote prefix that
    :func:`md_blockquote_prefix` already recognizes. This stays intentionally
    tiny and source-view-oriented: enough to make common alert opener lines
    scan better in docs/help buffers without committing Micromax to a fuller
    alert/admonition block model.

    Returns ``(start, end, kind)`` where ``kind`` is one of ``note``, ``tip``,
    ``important``, ``warning``, or ``caution``.
    """

    info = md_blockquote_prefix(line)
    if not info:
        return None
    _a, b, _depth = info
    s = str(line or "")
    m = re.match(r"(?P<marker>\[!(?P<kind>NOTE|TIP|IMPORTANT|WARNING|CAUTION)\])(?:[ \t]+|$)", s[b:])
    if not m:
        return None
    a = int(b) + int(m.start('marker'))
    c = int(b) + int(m.end('marker'))
    kind = str(m.group('kind') or '').lower()
    return (a, c, kind)


# ----- tiny markdown thematic-break helpers (docs/help scanability) -----


def md_thematic_break_span(line: str) -> tuple[int, int] | None:
    """Return the body span for a tiny markdown thematic-break line.

    Accepted forms (best-effort, UI-only):
      - ``---``
      - ``***``
      - ``___``
      - ``  - - -``

    Policy mirrors a small CommonMark/GFM-friendly subset:
      - up to three leading spaces
      - three or more matching ``-``, ``*``, or ``_`` characters
      - optional spaces or tabs between markers
      - no trailing non-whitespace text
    """

    s = str(line or "")
    m = re.match(r"^(?P<indent> {0,3})(?P<body>(?P<ch>[-_*])(?:[ \\t]*(?P=ch)){2,})[ \\t]*$", s)
    if not m:
        return None
    a = int(m.start('body'))
    b = int(m.end('body'))
    if b <= a:
        return None
    return (a, b)


def md_thematic_break_char_spans(line: str) -> list[tuple[int, int]]:
    """Return spans for the visible marker characters in a thematic break."""

    span = md_thematic_break_span(line)
    if not span:
        return []
    a, b = span
    s = str(line or "")
    return [(i, i + 1) for i in range(a, b) if s[i] in '-_*']


# ----- tiny markdown table helpers (docs/help scanability) -----


def md_table_delimiter_row(line: str) -> bool:
    """Return True if *line* looks like a GFM pipe-table delimiter row.

    This is intentionally small and UI-oriented, not a full block parser.
    Examples accepted:
      - | --- | --- |
      - | :--- | ---: |
      - --- | ---
    """

    s = str(line or "").strip()
    if not s or "|" not in s:
        return False
    raw = s
    if raw.startswith("|"):
        raw = raw[1:]
    if raw.endswith("|"):
        raw = raw[:-1]
    cells = [c.strip() for c in raw.split("|")]
    if len(cells) < 2:
        return False
    for cell in cells:
        if not cell or re.fullmatch(r":?-{3,}:?", cell) is None:
            return False
    return True


def md_table_pipe_row(line: str) -> bool:
    """Return True if *line* looks like a simple pipe-table content row."""

    s = str(line or "").strip()
    if not s or "|" not in s:
        return False
    return not md_table_delimiter_row(s)


def md_table_row_kinds(lines: list[str]) -> dict[int, str]:
    """Return line-index -> kind for small GFM-style pipe tables.

    Kinds are: ``header``, ``delimiter``, and ``body``.
    Only contiguous pipe rows following a header+delimiter pair are marked as
    body rows. This keeps the policy small, local, and predictable for the TUI.
    """

    xs = [str(x) for x in (lines or [])]
    out: dict[int, str] = {}
    i = 0
    n = len(xs)
    while i < n - 1:
        if md_table_pipe_row(xs[i]) and md_table_delimiter_row(xs[i + 1]):
            out[i] = "header"
            out[i + 1] = "delimiter"
            j = i + 2
            while j < n and md_table_pipe_row(xs[j]):
                out[j] = "body"
                j += 1
            i = j
            continue
        i += 1
    return out


def md_table_pipe_spans(line: str) -> list[tuple[int, int]]:
    """Return spans for literal ``|`` separators in a table row."""

    s = str(line or "")
    return [(i, i + 1) for i, ch in enumerate(s) if ch == "|"]


def md_table_cell_entries(line: str) -> list[dict[str, object]]:
    """Return tiny parsed visible cells for a simple pipe-table row.

    This intentionally stays tiny and UI-oriented rather than trying to fully
    parse Markdown tables. It trims outer cell padding, ignores empty edge
    segments introduced by leading/trailing pipes, and reports only visible
    cell text spans plus a stable zero-based ``column`` index.
    """

    s = str(line or "")
    pipe_cols = [i for i, ch in enumerate(s) if ch == "|"]
    if not pipe_cols:
        return []
    bounds = [-1, *pipe_cols, len(s)]
    entries: list[dict[str, object]] = []
    last = len(bounds) - 2
    for idx in range(len(bounds) - 1):
        raw_a = int(bounds[idx]) + 1
        raw_b = int(bounds[idx + 1])
        a = raw_a
        b = raw_b
        while a < b and s[a].isspace():
            a += 1
        while b > a and s[b - 1].isspace():
            b -= 1
        is_edge = idx == 0 or idx == last
        if is_edge and a == b:
            continue
        entries.append(
            {
                "kind": "cell",
                "column": int(len(entries)),
                "start": int(a),
                "end": int(b),
                "text": str(s[a:b]),
            }
        )
    return entries


def md_table_delimiter_entries(line: str) -> list[dict[str, object]]:
    """Return tiny parsed visible cells for a table delimiter row.

    Each entry records a trimmed cell token span plus a simple alignment label:
    ``default``, ``left``, ``right``, or ``center``.
    """

    out: list[dict[str, object]] = []
    for entry in md_table_cell_entries(line):
        token = str(entry.get("text", "") or "")
        if re.fullmatch(r":?-{3,}:?", token) is None:
            return []
        align = "default"
        if token.startswith(":") and token.endswith(":"):
            align = "center"
        elif token.startswith(":"):
            align = "left"
        elif token.endswith(":"):
            align = "right"
        out.append(
            {
                "kind": "delimiter-cell",
                "column": int(entry.get("column", 0) or 0),
                "start": int(entry.get("start", 0) or 0),
                "end": int(entry.get("end", 0) or 0),
                "text": token,
                "align": align,
                "marker_count": int(token.count("-")),
            }
        )
    return out


@dataclass(frozen=True)
class PromptDisplayItem:
    """A rendered prompt suggestion line with minimal metadata.

    This exists so the curses TUI can apply small style differences without
    re-parsing the rendered text. It intentionally keeps the *text* stable so
    existing tests over `_prompt_display_lines` remain valid.
    """

    text: str
    is_header: bool = False
    is_more: bool = False
    is_selected: bool = False
    row_kind: str = ""
    section_label: str = ""


def _prompt_display_items(ed: Editor, *, max_lines: int, width: int) -> list[PromptDisplayItem]:
    """Render the active prompt suggestions into display items (best-effort).

    This remains a thin TUI wrapper over the shared editor-side rendered prompt
    model so tests/headless tools and the minimal curses UI stay aligned.
    """

    out: list[PromptDisplayItem] = []
    for ent in ed.prompt_display_model(max_lines=max_lines, width=width):
        if not isinstance(ent, dict):
            continue
        typ = str(ent.get("type", ""))
        out.append(
            PromptDisplayItem(
                str(ent.get("text", "")),
                is_header=(typ in ("header", "sticky")),
                is_more=(typ == "more"),
                is_selected=bool(int(ent.get("selected", 0) or 0)),
                row_kind=str(ent.get("row_kind", "") or ""),
                section_label=str(ent.get("section_label", "") or ""),
            )
        )
    return out


def _prompt_display_lines(ed: Editor, *, max_lines: int, width: int) -> list[str]:
    """Render the active prompt suggestions into display lines (best-effort).

    This remains a simple list-of-strings helper used by unit tests.
    The curses TUI uses `_prompt_display_items` for style hints.
    """

    return [it.text for it in _prompt_display_items(ed, max_lines=max_lines, width=width)]


def line_number_gutter_width(ed: Editor) -> int:
    """Return the tiny shared/reference gutter width for line numbers."""

    return int(ed.line_number_gutter_width())


def line_number_gutter_text(
    ed: Editor,
    *,
    line_index: int,
    wrap_start_col: int,
    gutter_width: int,
) -> str:
    """Return the display text for one rendered buffer row's line-number cell."""

    return str(
        ed.line_number_gutter_text(
            line_index=line_index,
            wrap_start_col=wrap_start_col,
            gutter_width=gutter_width,
        )
    )


def scrollbar_gutter_width(ed: Editor) -> int:
    """Return the tiny shared/reference right-edge scrollbar gutter width."""

    return int(ed.scrollbar_gutter_width())


def scrollbar_thumb_span(*, total_rows: int, start_row: int, window_rows: int) -> tuple[int, int] | None:
    """Return a tiny scrollbar thumb span as ``(top, size)`` within the window.

    Policy (tiny, renderer-local):
      - if the document fits, return ``None``
      - otherwise size is a proportional thumb with a minimum height of 1 row
      - start/top are based on the current visible window start within the total
        row range

    The model intentionally works on abstract rows so callers can use logical
    lines in ordinary views and visual rows under softwrap.
    """

    win = max(0, int(window_rows))
    total = max(0, int(total_rows))
    start = max(0, int(start_row))
    if win <= 0 or total <= win or total <= 0:
        return None

    thumb = max(1, min(win, round((win * win) / total)))
    max_top = max(0, win - thumb)
    max_start = max(1, total - win)
    top = round(min(start, max_start) * max_top / max_start)
    top = max(0, min(int(top), max_top))
    return (int(top), int(thumb))


def scrollbar_thumb_char(ed: Editor) -> str:
    """Return the tiny scrollbar thumb glyph."""

    return str(ed.scrollbar_thumb_char())


def overflow_marker_cells(
    *,
    line_text: str,
    frag_start: int,
    view_width: int,
    softwrap: bool,
) -> list[tuple[int, str]]:
    """Return the shared tiny left/right overflow-marker cells."""

    return _overflow_marker_cells_shared(
        line_text=line_text,
        frag_start=frag_start,
        view_width=view_width,
        softwrap=softwrap,
    )


def keymenu_text(ed: Editor, *, width: int) -> str:
    """Return the shared tiny key-menu summary for the current context."""

    return ed.keymenu_text(int(width))


def capture_prompt_text(ed: Editor, *, width: int) -> str:
    """Return a tiny single-line prompt for active capture keymodes.

    The wording now reuses the shared editor-side interaction/capture status
    model so future UI layers/statuslines/scripts can inspect the same bottom-row
    surface without scraping renderer-only text.
    """

    w = max(0, int(width))
    if w <= 0:
        return ""

    st = ed.status_model()
    if not str(st.get("capture_kind", "") or ""):
        return ""
    model = ed.interaction_model(w)
    if not int(model.get("active", 0) or 0):
        return ""
    return str(model.get("text", "") or "")


def constantshow_text(ed: Editor) -> str:
    """Return the shared tiny cursor summary for the idle infobar."""

    return ed.constantshow_text()


def infobar_text(ed: Editor, *, width: int) -> str:
    """Return the shared idle infobar line for the current editor state."""

    return ed.infobar_text(int(width))


def _render(stdscr: "curses._CursesWindow", ed: Editor) -> None:
    stdscr.erase()
    h, w = stdscr.getmaxyx()
    screen_w = max(1, w)

    eb = ed.cur()
    screen = ed.screen_model(lines=h, cols=w)
    layout = dict(screen.get("layout") or {})
    gutter = dict(screen.get("gutter") or {})
    viewport_cues = dict(screen.get("viewport_cues") or {})
    docs_cues = dict(screen.get("docs_cues") or {})
    display_rows = dict(screen.get("display_rows") or {})
    window = dict(screen.get("edit_window") or {})
    viewport_rows = dict(screen.get("viewport_rows") or {})
    view_h = int(layout.get("viewport_height", 0) or 0)
    text_x = int(layout.get("viewport_x", 0) or 0)
    view_w = int(layout.get("viewport_width", 0) or 0)
    scrollbar_x = _model_int(layout.get("scrollbar_x"), text_x + view_w)
    scrollbar_w = int(layout.get("gutter_right", 0) or 0)
    sug_h = int(layout.get("suggestions_height", 0) or 0)
    vp = dict(window.get("viewport") or ed.viewport_model())

    softwrap_enabled = bool(ed.options.get("softwrap", local=eb.local_options))

    # Buffer lines / visible viewport rows
    rows = list(viewport_rows.get("rows") or window.get("rows") or [])
    is_help = bool(ed.current_help_doc_topic())
    cue_by_y = {
        int(row.get("screen_y", -1)): dict(row)
        for row in list(viewport_cues.get("rows") or [])
        if isinstance(row, dict)
    }
    display_by_y = {
        int(row.get("screen_y", -1)): dict(row)
        for row in list(display_rows.get("rows") or [])
        if isinstance(row, dict) and str(row.get("kind", "") or "") == "viewport"
    }
    docs_by_y = {
        int(row.get("screen_y", -1)): dict(row)
        for row in list(docs_cues.get("rows") or [])
        if isinstance(row, dict)
    }
    cursor_model = dict(window.get("cursor") or {})
    cy = int(cursor_model.get("view_y", 0) or 0)
    cx = int(cursor_model.get("view_x", 0) or 0)

    def _draw_overflow_markers(row: int, cells: list[tuple[int, str]], base_attr: int) -> None:
        if not cells:
            return
        marker_attr = int(base_attr) | curses.A_BOLD | curses.A_DIM
        for xx, ch in cells:
            try:
                stdscr.addnstr(int(row), text_x + int(xx), str(ch), 1, marker_attr)
            except curses.error:
                pass

    for row_model in rows:
        row = int(row_model.get("view_y", 0) or 0)
        _li = int(row_model["line"]) if "line" in row_model else -1
        _start = int(row_model.get("start_col", 0) or 0)
        frag = str(row_model.get("text", "") or "")
        screen_y = _model_int(row_model.get("screen_y"), row)
        cue_row = dict(cue_by_y.get(int(screen_y), {}))
        row_cursor_attr = curses.A_UNDERLINE if bool(int(cue_row.get("cursorline", 0) or 0)) else 0
        try:
            if text_x > 0:
                num = str(row_model.get("left_text", "") or "")
                if not num and int(_li) >= 0:
                    num = line_number_gutter_text(ed, line_index=int(_li), wrap_start_col=int(_start), gutter_width=text_x)
                num_attr = curses.A_DIM if num.strip() else 0
                if bool(int(row_model.get("current", 0) or 0)) or (int(_start) == 0 and int(_li) == int(eb.cursors[eb.primary].line)):
                    num_attr = curses.A_BOLD
                num_attr |= row_cursor_attr
                stdscr.addnstr(screen_y, 0, num, text_x, num_attr)
            display_model = dict(display_by_y.get(int(screen_y), {}))
            overflow_cells = [
                (int(cell[0]), str(cell[1]))
                for cell in list(display_model.get("overflow_cells") or [])
                if isinstance(cell, (list, tuple)) and len(cell) >= 2
            ]
            display_frag = str(display_model.get("viewport_display_text", frag) or frag)
            syntax_spans = _model_tagged_spans(cue_row.get("syntax_spans"))
            syntax_boundaries = [(a, b) for a, b, _tag in syntax_spans]
            showchar_spans = _model_spans(cue_row.get("showchar_spans"))
            search_spans = _model_spans(cue_row.get("search_spans"))
            current_search_spans = _model_spans(cue_row.get("current_search_spans"))
            primary_selection_spans = _model_spans(
                cue_row.get("primary_selection_spans")
            )
            secondary_selection_spans = _model_spans(
                cue_row.get("secondary_selection_spans")
            )
            primary_selection_eol_x = _model_int(
                cue_row.get("primary_selection_eol_x"),
                -1,
            )
            secondary_selection_eol_x = _model_int(
                cue_row.get("secondary_selection_eol_x"),
                -1,
            )
            selection_eol_visible = any(
                0 <= int(x) < int(view_w)
                for x in (primary_selection_eol_x, secondary_selection_eol_x)
            )
            trailing_spans = _model_spans(cue_row.get("trailing_spans"))
            tab_error_spans_ = _model_spans(cue_row.get("tab_error_spans"))
            colorcolumn_spans = _model_spans(cue_row.get("colorcolumn_spans"))
            color_x = _model_int(cue_row.get("colorcolumn_x"), -1)
            color_x = None if color_x < 0 else color_x
            brace_spans = _model_spans(cue_row.get("brace_spans"))

            def _draw_selection_eol(base_attr: int) -> None:
                """Paint a selected logical newline as one visible blank cell."""

                eol_candidates = [
                    x
                    for x in (secondary_selection_eol_x, primary_selection_eol_x)
                    if 0 <= int(x) < int(view_w)
                ]
                if not eol_candidates:
                    return
                eol_x = int(min(eol_candidates))
                attr = viewport_highlight_attr(
                    int(base_attr),
                    eol_x,
                    eol_x + 1,
                    secondary_selection=(
                        [(eol_x, eol_x + 1)]
                        if int(secondary_selection_eol_x) == eol_x
                        else []
                    ),
                    primary_selection=(
                        [(eol_x, eol_x + 1)]
                        if int(primary_selection_eol_x) == eol_x
                        else []
                    ),
                )
                stdscr.addnstr(screen_y, text_x + eol_x, " ", 1, attr)

            if not is_help:
                if not selection_eol_visible and not viewport_highlight_work_needed(
                    syntax_boundaries,
                    search_spans,
                    current_search_spans,
                    secondary_selection_spans,
                    primary_selection_spans,
                    trailing_spans,
                    tab_error_spans_,
                    colorcolumn_spans,
                    brace_spans,
                    showchar_spans,
                    colorcolumn_x=color_x,
                ):
                    stdscr.addnstr(screen_y, text_x, display_frag, view_w, row_cursor_attr)
                    _draw_overflow_markers(screen_y, overflow_cells, row_cursor_attr)
                    continue

                pts = highlight_segment_points(
                    0,
                    len(frag),
                    syntax_boundaries,
                    search_spans,
                    current_search_spans,
                    secondary_selection_spans,
                    primary_selection_spans,
                    trailing_spans,
                    tab_error_spans_,
                    colorcolumn_spans,
                    brace_spans,
                    showchar_spans,
                )
                brace_attr = brace_match_attr(ed, local_options=eb.local_options)
                for i in range(len(pts) - 1):
                    aa = int(pts[i])
                    bb = int(pts[i + 1])
                    if bb <= aa:
                        continue
                    syntax_tag = _tagged_span_at(syntax_spans, aa, bb)
                    segment_base_attr = syntax_highlight_attr(
                        row_cursor_attr,
                        syntax_tag,
                    )
                    attr = viewport_highlight_attr(
                        segment_base_attr,
                        aa,
                        bb,
                        showchars=showchar_spans,
                        colorcolumn=colorcolumn_spans,
                        trailing=trailing_spans,
                        tab_error=tab_error_spans_,
                        braces=brace_spans,
                        search=search_spans,
                        current_search=current_search_spans,
                        secondary_selection=secondary_selection_spans,
                        primary_selection=primary_selection_spans,
                        brace_attr=brace_attr,
                    )
                    stdscr.addnstr(screen_y, text_x + aa, display_frag[aa:bb], max(0, view_w - aa), attr)
                if color_x is not None and int(color_x) >= len(frag):
                    stdscr.addnstr(screen_y, text_x + int(color_x), " ", 1, row_cursor_attr | curses.A_REVERSE | curses.A_DIM)
                _draw_selection_eol(row_cursor_attr)
                _draw_overflow_markers(screen_y, overflow_cells, row_cursor_attr)
                continue
            docs_row = dict(docs_by_y.get(int(screen_y), {}))
            line_role = str(docs_row.get("line_role", "") or "")
            link_spans = _model_spans(docs_row.get("link_spans"))
            dim_spans = _model_spans(docs_row.get("dim_spans"))
            bold_spans = _model_spans(docs_row.get("bold_spans"))
            italic_spans = _model_spans(docs_row.get("italic_spans"))

            base_attr = row_cursor_attr
            if line_role in ("heading-title", "table-header"):
                base_attr |= curses.A_BOLD
            if line_role in ("heading-underline", "table-delimiter", "thematic-break", "fenced-body", "html-block", "indented-code", "definition"):
                base_attr |= curses.A_DIM
            if line_role == "fenced-fence":
                base_attr |= curses.A_BOLD | curses.A_DIM
            if line_role in ("heading-title", "heading-underline", "table-header") and curses.has_colors():
                base_attr = replace_curses_color(base_attr, curses.color_pair(1))
            elif line_role == "thematic-break" and curses.has_colors():
                base_attr = replace_curses_color(base_attr, curses.color_pair(2))

            def _write_range(a: int, b: int, attr0: int) -> None:
                """Write frag[a:b] applying tiny docs-help style overlays."""

                if b <= a:
                    return
                pts = highlight_segment_points(
                    int(a),
                    int(b),
                    dim_spans,
                    bold_spans,
                    italic_spans,
                    search_spans,
                    current_search_spans,
                    secondary_selection_spans,
                    primary_selection_spans,
                    trailing_spans,
                    tab_error_spans_,
                    colorcolumn_spans,
                    brace_spans,
                    showchar_spans,
                )
                if len(pts) <= 1:
                    stdscr.addnstr(screen_y, text_x + a, display_frag[a:b], max(0, view_w - a), attr0)
                    return
                italic_attr = int(getattr(curses, 'A_ITALIC', 0) or curses.A_UNDERLINE)
                brace_attr = brace_match_attr(ed, local_options=eb.local_options)
                for i in range(len(pts) - 1):
                    aa = int(pts[i])
                    bb = int(pts[i + 1])
                    if bb <= aa:
                        continue
                    attr = viewport_highlight_attr(
                        attr0,
                        aa,
                        bb,
                        docs_dim=dim_spans,
                        docs_bold=bold_spans,
                        docs_italic=italic_spans,
                        showchars=showchar_spans,
                        colorcolumn=colorcolumn_spans,
                        trailing=trailing_spans,
                        tab_error=tab_error_spans_,
                        braces=brace_spans,
                        search=search_spans,
                        current_search=current_search_spans,
                        secondary_selection=secondary_selection_spans,
                        primary_selection=primary_selection_spans,
                        italic_attr=italic_attr,
                        brace_attr=brace_attr,
                    )
                    stdscr.addnstr(screen_y, text_x + aa, display_frag[aa:bb], max(0, view_w - aa), attr)
                if color_x is not None and int(color_x) >= len(frag):
                    stdscr.addnstr(screen_y, text_x + int(color_x), " ", 1, attr0 | curses.A_REVERSE | curses.A_DIM)

            if not link_spans:
                _write_range(0, len(frag), base_attr)
                _draw_selection_eol(base_attr)
                _draw_overflow_markers(screen_y, overflow_cells, row_cursor_attr)
                continue

            x = 0
            for a, b in link_spans:
                if a > x:
                    _write_range(x, a, base_attr)
                attr = base_attr | curses.A_UNDERLINE
                if curses.has_colors():
                    attr = replace_curses_color(attr, curses.color_pair(3))
                if int(cy) == int(row) and int(a) <= int(cx) < int(b):
                    attr |= curses.A_BOLD
                _write_range(a, b, attr)
                x = b
            if x < len(frag):
                _write_range(x, len(frag), base_attr)
            _draw_selection_eol(base_attr)
            _draw_overflow_markers(screen_y, overflow_cells, row_cursor_attr)
        except curses.error:
            pass

    # Suggestion list (pickers)
    prompt_panel = dict(screen.get("prompt_panel") or {})
    if int(prompt_panel.get("active", 0) or 0):
        entries = list(prompt_panel.get("entries") or [])
        panel_y = _model_int(prompt_panel.get("y"), view_h)
        for i, ent in enumerate(entries):
            line = str(ent.get("text", "") or "")
            y = _model_int(ent.get("screen_y"), panel_y + i)
            try:
                typ = str(ent.get("type", "") or "")
                rk = str(ent.get("row_kind", "") or "")
                is_selected = bool(int(ent.get("selected", 0) or 0))
                is_header = typ in ("header", "sticky")
                is_more = typ == "more"
                attr = 0
                if is_selected:
                    attr = curses.A_REVERSE
                elif is_header:
                    attr = curses.A_BOLD
                    if curses.has_colors():
                        attr |= curses.color_pair(1)
                elif is_more:
                    attr = curses.A_DIM
                    if curses.has_colors():
                        attr |= curses.color_pair(2)

                # Row-kind styling (UI-only, scan-friendly):
                # - palette actions get a hint color/bold
                # - palette openpath/recentfile rows get a file-ish hint
                # - helplink/helpnav link rows get a link-ish hint
                # - helpnav heading rows are bold
                if not is_header and not is_more:
                    if rk == "action":
                        attr |= curses.A_BOLD
                        if curses.has_colors():
                            attr = (attr & ~curses.A_COLOR) | curses.color_pair(5)
                    elif rk in ("openpath", "recentfile"):
                        if curses.has_colors():
                            attr = (attr & ~curses.A_COLOR) | curses.color_pair(2)
                    elif rk == "link":
                        if curses.has_colors():
                            attr = (attr & ~curses.A_COLOR) | curses.color_pair(3)
                    elif rk == "heading":
                        attr |= curses.A_BOLD
                        if curses.has_colors():
                            attr = (attr & ~curses.A_COLOR) | curses.color_pair(1)

                # Picker polish:
                # - highlight query token matches in suggestion rows
                # - dim the detail suffix after " — " (scan-friendly, fzf-ish)
                # (Headers and more-markers are left alone.)
                if (line.startswith(">") or line.startswith(" ")) and not line.startswith("--"):
                    q = str(ed.prompt.text if ed.prompt is not None else "")
                    # Skip the leading selector prefix ("> " or "  ") when matching.
                    off = 2 if len(line) >= 2 and line[1] == " " else 0

                    sep = " — "
                    j = line.find(sep, off)
                    detail_start = (j + len(sep)) if j >= 0 else None

                    body = line[off:]
                    spans = [(a + off, b + off) for a, b in prompt_match_spans(body, q)]

                    base_attr = attr
                    detail_attr = attr | curses.A_DIM

                    if spans:
                        # Match highlighting should override row-kind colors.
                        match_attr = (attr & ~curses.A_COLOR) | curses.A_BOLD
                        if curses.has_colors():
                            # 4: query matches in picker lists
                            match_attr = (match_attr & ~curses.A_COLOR) | curses.color_pair(4)
                        match_detail_attr = match_attr | curses.A_DIM

                        def _add(seg_a: int, seg_b: int, txt: str, a1: int, a2: int) -> None:
                            if seg_b <= seg_a:
                                return
                            if detail_start is None or seg_b <= detail_start:
                                stdscr.addnstr(y, seg_a, txt, max(0, screen_w - seg_a), a1)
                                return
                            if seg_a >= detail_start:
                                stdscr.addnstr(y, seg_a, txt, max(0, screen_w - seg_a), a2)
                                return
                            # Split at detail boundary.
                            k = max(0, int(detail_start) - int(seg_a))
                            if k > 0:
                                stdscr.addnstr(y, seg_a, txt[:k], max(0, screen_w - seg_a), a1)
                            stdscr.addnstr(y, seg_a + k, txt[k:], max(0, screen_w - (seg_a + k)), a2)

                        x = 0
                        for a, b in spans:
                            if a > x:
                                _add(x, a, line[x:a], base_attr, detail_attr)
                            _add(a, b, line[a:b], match_attr, match_detail_attr)
                            x = b
                        if x < len(line):
                            _add(x, len(line), line[x:], base_attr, detail_attr)
                    else:
                        # No match spans: still dim detail suffix if present.
                        if detail_start is not None and detail_start < len(line):
                            stdscr.addnstr(y, 0, line[:detail_start], screen_w, base_attr)
                            stdscr.addnstr(y, detail_start, line[detail_start:], max(0, screen_w - detail_start), detail_attr)
                        else:
                            stdscr.addnstr(y, 0, line, screen_w, base_attr)
                else:
                    stdscr.addnstr(y, 0, line, screen_w, attr)
            except curses.error:
                pass

    # Tiny right-edge scrollbar cue (shared viewport-row model, styled here).
    if int(scrollbar_w) > 0:
        drew_thumb = False
        for row_model in rows:
            right_text = str(row_model.get("right_text", "") or "")
            if not right_text:
                continue
            drew_thumb = True
            try:
                stdscr.addnstr(
                    int(row_model.get("screen_y", 0) or 0),
                    _model_int(row_model.get("right_x"), scrollbar_x),
                    right_text,
                    1,
                    curses.A_REVERSE | curses.A_DIM,
                )
            except curses.error:
                pass
        if not drew_thumb:
            if softwrap_enabled:
                total_rows = ed._total_visual_rows(eb, w=view_w)
                start_row = ed._viewport_visual_start(eb, w=view_w)
            else:
                total_rows = max(1, len(eb.buf.lines))
                start_row = max(0, int(vp.get("top_line", 0) or 0))
            thumb = scrollbar_thumb_span(total_rows=total_rows, start_row=start_row, window_rows=view_h)
            if thumb is not None:
                thumb_top, thumb_size = thumb
                thumb_char = scrollbar_thumb_char(ed)
                for yy in range(int(thumb_top), min(int(view_h), int(thumb_top) + int(thumb_size))):
                    try:
                        stdscr.addnstr(yy, int(scrollbar_x), thumb_char, 1, curses.A_REVERSE | curses.A_DIM)
                    except curses.error:
                        pass

    # Optional bottom-row chrome (shared row model, styled here).
    chrome_rows = list(screen.get("bottom_rows") or [])
    for idx, row_model in enumerate(chrome_rows):
        y = int(row_model.get("y", max(0, h - len(chrome_rows) + idx)) or max(0, h - len(chrome_rows) + idx))
        kind = str(row_model.get("kind", "") or "")
        slot = str(row_model.get("slot", "") or "")
        text = str(row_model.get("text", "") or "")
        attr = curses.A_DIM if kind == "keymenu" else 0
        try:
            stdscr.addnstr(y, 0, text, screen_w, attr)
        except curses.error:
            pass
    # Place the terminal cursor from the same composed screen snapshot used for
    # rows and chrome.  In particular, prompt coordinates must not inherit the
    # edit viewport's horizontal scroll offset or force a second status-model
    # traversal after screen composition.
    try:
        cursor_model = dict(screen.get("cursor") or window.get("cursor") or {})
        screen_y = _model_int(cursor_model.get("screen_y"), cy)
        screen_x = _model_int(cursor_model.get("screen_x"), text_x + cx)
        stdscr.move(
            max(0, min(h - 1, screen_y)),
            max(0, min(w - 1, screen_x)),
        )
    except curses.error:
        pass

    stdscr.refresh()


def run_tui(
    path: str | None = None,
    *,
    help_doc: str | None = None,
    plugins_root: str | None = None,
    workspace_trust: str | None = None,
) -> int:
    runtime = create_editor_runtime(
        plugins_root=plugins_root,
        workspace_trust=workspace_trust,
    )
    ed = runtime.editor

    open_initial_buffer(ed, path=path, help_doc=help_doc, allow_help_outside_root=True)

    def _main(stdscr: "curses._CursesWindow") -> int:
        curses.curs_set(1)
        stdscr.keypad(True)
        stdscr.timeout(50)

        # Picker/doc UX polish: minimal color pairs.
        # (The headless core does not depend on curses color support.)
        try:
            if curses.has_colors():
                curses.start_color()
                try:
                    curses.use_default_colors()
                except Exception:
                    pass
                # 1: section headers / headings
                curses.init_pair(1, curses.COLOR_CYAN, -1)
                # 2: "more" markers
                curses.init_pair(2, curses.COLOR_YELLOW, -1)
                # 3: markdown links (help buffers)
                curses.init_pair(3, curses.COLOR_BLUE, -1)
                # 4: picker query match highlights
                curses.init_pair(4, curses.COLOR_MAGENTA, -1)
                # 5: palette actions (scan-friendly)
                curses.init_pair(5, curses.COLOR_GREEN, -1)
        except Exception:
            pass

        last_clip_serial = int(getattr(ed, 'clipboard_serial', 0))
        shown_external_clip_warn = False

        def _insert_paste_text(txt: str) -> None:
            s = normalize_paste_text(str(txt or ""))
            if not s:
                return
            try:
                ed.input['text'] = s
                ed.run_action('PromptInsertText' if ed.prompt is not None else 'InsertText')
            except Exception as e:
                ed.message(f"paste error: {e}")

        while not bool(getattr(ed, "should_quit", False)):
            # Allow plugins to schedule small debounced/autosave work without threads.
            try:
                ed.pump_timers()
            except Exception:
                pass
            _render(stdscr, ed)
            try:
                ch = stdscr.get_wch()
            except curses.error:
                # no input
                continue

            if ch == curses.KEY_RESIZE:
                continue

            # Raw-key debugging: print key events instead of dispatching.
            # Toggle via `:rawkeys` (micro-inspired).
            if bool(ed.options.get('tui.rawkeys')):
                # Allow Escape to exit raw mode quickly.
                if ch == "\x1b":
                    # If ESC is followed immediately by another key, treat it
                    # as an Alt/Meta chord instead of a raw-mode escape.
                    nxt: Any | None = None
                    try:
                        stdscr.timeout(0)
                        try:
                            nxt = stdscr.get_wch()
                        except curses.error:
                            nxt = None
                    finally:
                        # Restore the TUI's polling timeout.
                        try:
                            stdscr.timeout(50)
                        except Exception:
                            pass
                    if nxt is None:
                        ed.options.set('tui.rawkeys', 'false')
                        ed.message('rawkeys: off')
                        continue

                    mapped = decode_key_event(ch, nxt)
                    ed.message(f"rawkey: ESC+{nxt!r} mapped={mapped!r}")
                    continue

                mapped = decode_key_event(ch)
                if isinstance(ch, int):
                    try:
                        kname = curses.keyname(ch).decode('utf-8', 'replace')
                    except Exception:
                        kname = str(ch)
                    ed.message(f"rawkey: code={ch} curses={kname} mapped={mapped!r}")
                else:
                    try:
                        o = ord(ch) if isinstance(ch, str) and len(ch) == 1 else None
                    except Exception:
                        o = None
                    ed.message(f"rawkey: ch={ch!r} ord={o} mapped={mapped!r}")
                continue


            # Bracketed paste: terminals wrap pasted content in ESC[200~ ... ESC[201~
            # when bracketed paste mode is enabled.
            if ch == "" and bool(ed.options.get('tui.bracketedpaste')):
                look: list[Any] = []
                try:
                    stdscr.timeout(0)
                    for _ in range(5):
                        try:
                            look.append(stdscr.get_wch())
                        except curses.error:
                            break
                finally:
                    try:
                        stdscr.timeout(50)
                    except Exception:
                        pass

                seq = [""] + [x for x in look]
                seqs = [str(x) for x in seq]
                if len(seqs) >= 6 and seqs[:6] == _BRACKETED_PASTE_START:
                    buf: list[str] = []
                    deadline = time.monotonic() + 2.0
                    while True:
                        try:
                            ev = stdscr.get_wch()
                        except curses.error:
                            if time.monotonic() > deadline:
                                break
                            continue

                        if ev == "":
                            look2: list[Any] = []
                            ok_end = False
                            try:
                                stdscr.timeout(0)
                                for _ in range(5):
                                    try:
                                        look2.append(stdscr.get_wch())
                                    except curses.error:
                                        break
                            finally:
                                try:
                                    stdscr.timeout(50)
                                except Exception:
                                    pass

                            end_seq = [""] + [str(x) for x in look2]
                            if len(end_seq) >= 6 and end_seq[:6] == _BRACKETED_PASTE_END:
                                ok_end = True
                            if ok_end:
                                break
                            buf.append("")
                            for x in look2:
                                if isinstance(x, str):
                                    buf.append(x)
                            continue

                        if isinstance(ev, str):
                            buf.append(ev)
                            if sum(len(x) for x in buf) > 2_000_000:
                                break

                    _insert_paste_text(''.join(buf))
                    continue

                # Not a paste start: push back lookahead events.
                for ev in reversed(look):
                    try:
                        curses.unget_wch(ev)
                    except Exception:
                        pass

            # "paste" option: aggregate bursts of character events into a single
            # InsertText so terminals without bracketed paste don't trigger
            # autoindent/autopairs per key.
            if bool(ed.options.get('paste')) and is_paste_char(ch):
                buf = [str(ch)]
                look3: list[Any] = []
                try:
                    stdscr.timeout(0)
                    while True:
                        try:
                            ev = stdscr.get_wch()
                        except curses.error:
                            break
                        if is_paste_char(ev):
                            buf.append(str(ev))
                            if sum(len(x) for x in buf) > 2_000_000:
                                break
                            continue
                        look3.append(ev)
                        break
                finally:
                    try:
                        stdscr.timeout(50)
                    except Exception:
                        pass

                for ev in reversed(look3):
                    try:
                        curses.unget_wch(ev)
                    except Exception:
                        pass

                _insert_paste_text(''.join(buf))
                continue
# Alt/Meta chords are commonly encoded as ESC + <key>. We do a tiny
            # one-event lookahead so the headless editor's Alt-* bindings work
            # in a minimal curses UI.
            if ch == "\x1b":
                nxt2: Any | None = None
                try:
                    stdscr.timeout(0)
                    try:
                        nxt2 = stdscr.get_wch()
                    except curses.error:
                        nxt2 = None
                finally:
                    # Restore the TUI's polling timeout.
                    try:
                        stdscr.timeout(50)
                    except Exception:
                        pass
                if nxt2 is None:
                    key = decode_key_event(ch)
                else:
                    key = decode_key_event(ch, nxt2)
                    if key is None:
                        # If we can't interpret the chord, fall back to plain Esc.
                        key = "Esc"
            else:
                key = decode_key_event(ch)

            if key is None:
                continue

            try:
                ed.dispatch_key(key)
            except Exception as e:
                ed.message(f"tui error: {e}")            # Best-effort clipboard export when enabled.
            # - clipboard=terminal: OSC 52
            # - clipboard=external: pipe to wl-copy/xclip/etc
            try:
                cur_serial = int(getattr(ed, 'clipboard_serial', 0))
            except Exception:
                cur_serial = last_clip_serial
            if cur_serial != last_clip_serial:
                last_clip_serial = cur_serial
                try:
                    backend = str(ed.options.get('clipboard') or "")
                except Exception:
                    backend = ""

                try:
                    if backend == "terminal":
                        seq, err = ed.clipboard_terminal_export_sequence()
                        if seq:
                            try:
                                sys.__stdout__.write(str(seq))
                                sys.__stdout__.flush()
                            except Exception:
                                pass
                        elif err and not bool(getattr(ed, 'clipboard_from_script', False)):
                            ed.message(str(err))
                    elif backend == "external":
                        ok, err = ed.clipboard_external_export()
                        if (not ok) and err and not bool(getattr(ed, 'clipboard_from_script', False)):
                            if err.startswith("no external clipboard tool"):
                                if not shown_external_clip_warn:
                                    shown_external_clip_warn = True
                                    ed.message(str(err))
                            else:
                                ed.message(str(err))
                except Exception:
                    pass

        return 0

    # Enable bracketed paste mode (best-effort) so terminals wrap pastes in
    # \x1b[200~ ... \x1b[201~. Disable it on exit to avoid leaving the terminal
    # in a weird state.
    bp = False
    try:
        bp = bool(ed.options.get('tui.bracketedpaste'))
    except Exception:
        bp = False

    if bp:
        try:
            sys.__stdout__.write("\x1b[?2004h")
            sys.__stdout__.flush()
        except Exception:
            pass

    try:
        return curses.wrapper(_main)
    finally:
        try:
            ed._remember_cursor_for_buffer(ed.cur())
        except Exception:
            pass
        if bp:
            try:
                sys.__stdout__.write("\x1b[?2004l")
                sys.__stdout__.flush()
            except Exception:
                pass


def main(argv: list[str] | None = None) -> int:
    import argparse

    ap = argparse.ArgumentParser(prog="micromax-editor --tui", description="micromax-editor TUI (curses)")
    ap.add_argument("path", nargs="?", help="file to open")
    ap.add_argument("--help-doc", dest="help_doc", help="open a docs markdown file/topic in a protected help buffer")
    ap.add_argument(
        "--plugins",
        default=None,
        help="plugin root directory (default: ./plugins, then bundled installed plugins)",
    )
    args = ap.parse_args(argv)
    if args.path and args.help_doc:
        ap.error("pass either a path or --help-doc, not both")
    return int(run_tui(args.path, help_doc=args.help_doc, plugins_root=args.plugins))


if __name__ == "__main__":
    raise SystemExit(main())
