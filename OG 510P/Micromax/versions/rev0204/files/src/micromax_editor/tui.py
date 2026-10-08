from __future__ import annotations

"""micromax_editor.tui

A tiny curses-based TUI for the headless editor core.

Goal: provide the minimal tactile loop early:
  input -> ed.dispatch_key -> render

This intentionally avoids advanced rendering (syntax highlighting, spans, mouse,
etc.). It's meant to be a tiny proving ground for the core semantics.
"""

import curses
from bisect import bisect_right
import sys
from dataclasses import dataclass
import time
from typing import Any
import re

from .editor import Editor, md_balanced_span, md_backslash_escaped, md_docs_continuation_line, md_fenced_code_line_flags, md_html_block_line_flags, md_html_comment_line_spans, md_indented_code_line_flags, md_inline_code_delimiter_spans, md_inline_code_spans, md_inline_html_tag_spans, md_inline_link_target, md_inline_link_target_multiline, md_link_matches, md_norm_ref_id
from .micromax_bridge import install_editor_hostcalls
from .plugins import PluginManager


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


def search_match_spans(
    text: str,
    query: str,
    *,
    literal: bool = True,
    case_sensitive: bool = False,
) -> list[tuple[int, int]]:
    """Return best-effort visible search-match spans for one rendered row.

    This is intentionally renderer-oriented and line-fragment-local: it mirrors
    the current TUI's visible text rather than trying to reconstruct hidden
    off-screen context. That keeps the first ``hlsearch`` pass tiny, predictable,
    and safe for softwrap/scrolling while still making repeated visible matches
    easy to scan.
    """

    s = str(text or "")
    q = str(query or "")
    if not s or not q:
        return []

    if literal:
        hay = s if case_sensitive else s.casefold()
        needle = q if case_sensitive else q.casefold()
        if not needle:
            return []
        spans: list[tuple[int, int]] = []
        start = 0
        while True:
            i = hay.find(needle, start)
            if i < 0:
                break
            spans.append((int(i), int(i + len(needle))))
            start = int(i + max(1, len(needle)))
        return spans

    flags = 0 if case_sensitive else re.IGNORECASE
    try:
        pattern = re.compile(q, flags)
    except re.error:
        return []

    spans: list[tuple[int, int]] = []
    for m in pattern.finditer(s):
        a, b = int(m.start()), int(m.end())
        if b > a:
            spans.append((a, b))
    return _merge_spans(spans)


def trailing_whitespace_spans(
    line: str,
    *,
    frag_start: int = 0,
    frag_text: str | None = None,
) -> list[tuple[int, int]]:
    """Return visible trailing-whitespace spans for one rendered row fragment.

    Policy (tiny, renderer-oriented):
      - trailing whitespace is any final run of spaces/tabs in the *logical* line
      - only the intersection with the current visible fragment is returned
      - this keeps softwrap and horizontal scroll honest without promoting the cue
        into the headless editor model
    """

    full = str(line or "")
    frag = str(full if frag_text is None else frag_text)
    if not full or not frag:
        return []

    start = max(0, int(frag_start))
    end = start + len(frag)

    m = re.search(r"[ 	]+$", full)
    if not m:
        return []
    ta, tb = int(m.start()), int(m.end())
    aa = max(start, ta)
    bb = min(end, tb)
    if bb <= aa:
        return []
    return [(int(aa - start), int(bb - start))]


def tab_error_spans(
    line: str,
    *,
    tabstospaces: bool,
    frag_start: int = 0,
    frag_text: str | None = None,
) -> list[tuple[int, int]]:
    """Return visible tab/indentation-mismatch spans for one rendered fragment.

    Policy (tiny, micro-esque, renderer-oriented):
      - when ``tabstospaces`` is true, **all literal tab characters** are cues
      - when ``tabstospaces`` is false, **space characters in the initial indent
        run** are cues while tabs stay ordinary
      - only the intersection with the current visible fragment is returned so
        softwrap and horizontal scrolling stay honest

    This deliberately mirrors micro's documented ``hltaberrors`` rule closely
    enough to be useful without adding a richer indentation diagnostics model.
    """

    full = str(line or "")
    frag = str(full if frag_text is None else frag_text)
    if not full or not frag:
        return []

    start = max(0, int(frag_start))
    end = start + len(frag)
    spans: list[tuple[int, int]] = []

    if bool(tabstospaces):
        for idx, ch in enumerate(full):
            if ch != "	":
                continue
            aa = max(start, int(idx))
            bb = min(end, int(idx) + 1)
            if bb > aa:
                spans.append((int(aa - start), int(bb - start)))
        return spans

    indent_end = 0
    while indent_end < len(full) and full[indent_end] in " 	":
        indent_end += 1
    i = 0
    while i < indent_end:
        if full[i] != " ":
            i += 1
            continue
        j = i + 1
        while j < indent_end and full[j] == " ":
            j += 1
        aa = max(start, int(i))
        bb = min(end, int(j))
        if bb > aa:
            spans.append((int(aa - start), int(bb - start)))
        i = j
    return spans


def parse_showchars_option(raw: str) -> dict[str, str]:
    """Parse a tiny micro-esque ``showchars`` option string.

    Supported keys are the small subset we can render honestly in the current
    one-cell-per-character curses TUI: ``space``, ``tab``, ``ispace``, and
    ``itab``. Unknown keys are ignored. Values may be empty; an empty value just
    disables that specific replacement.

    Example: ``tab=>,space=.,itab=|>,ispace=|``.
    """

    out: dict[str, str] = {}
    s = str(raw or '').strip()
    if not s:
        return out
    for part in s.split(','):
        item = str(part).strip()
        if not item or '=' not in item:
            continue
        key, value = item.split('=', 1)
        key = str(key).strip().lower()
        if key not in {'space', 'tab', 'ispace', 'itab'}:
            continue
        out[key] = str(value)
    return out



def render_showchars_fragment(
    line: str,
    *,
    frag_start: int = 0,
    frag_text: str | None = None,
    spec: dict[str, str] | None = None,
) -> tuple[str, list[tuple[int, int]]]:
    """Return a visible-fragment string with tiny invisible-character cues.

    Policy (tiny, renderer-local):
      - replacements only affect the *displayed* fragment, never the buffer text
      - only file-backed spaces/tabs are replaced; softwrap continuation-indent
        prefix spaces stay as plain spaces because they are renderer-introduced
      - ``ispace`` / ``itab`` override ``space`` / ``tab`` in the leading indent
        run before the first visible character on the logical line
      - all replacements stay one-cell wide for now, so even ``tab`` / ``itab``
        use only the first configured character in the current curses TUI
    """

    full = str(line or '')
    frag = str(full if frag_text is None else frag_text)
    cfg = dict(spec or {})
    if not frag or not cfg:
        return (frag, [])

    start = max(0, int(frag_start))
    # Softwrap continuation rows may begin with renderer-added prefix spaces.
    tail_len = len(full[start : start + len(frag)])
    prefix_len = max(0, len(frag) - int(tail_len))

    indent_end = 0
    while indent_end < len(full) and full[indent_end] in ' \t':
        indent_end += 1

    chars = list(frag)
    spans: list[tuple[int, int]] = []
    for i, ch in enumerate(frag):
        if i < prefix_len:
            continue
        abs_i = start + (i - prefix_len)
        indent = abs_i < indent_end
        key = ''
        if ch == ' ':
            key = 'ispace' if indent and ('ispace' in cfg) else 'space'
        elif ch == '\t':
            key = 'itab' if indent and ('itab' in cfg) else 'tab'
        else:
            continue
        glyph = str(cfg.get(key, '') or '')
        if not glyph:
            continue
        chars[i] = glyph[:1]
        spans.append((int(i), int(i) + 1))
    return (''.join(chars), spans)



def matching_brace_positions(
    lines: list[str],
    *,
    line: int,
    col: int,
    match_left: bool = True,
) -> list[tuple[int, int]]:
    """Return visible-model brace pair positions for the primary cursor point.

    Policy (tiny, renderer-local, syntax-agnostic):
      - only the classic pairs ``()`` / ``[]`` / ``{}`` are considered
      - prefer the character directly under the cursor; when ``match_left`` is
        true and that is not a brace, also consider the character immediately to
        the left (micro-esque I-beam behavior)
      - matching is purely textual and nest-aware across the whole buffer
      - return ``[]`` when there is no brace under/left of the cursor or when no
        matching partner exists

    Returned positions are ``[(line, col), (line, col)]`` for the active brace
    and its partner. The helper deliberately stays local to the renderer rather
    than promising a richer syntax/tree-aware brace model in editor-core state.
    """

    if not lines:
        return []
    li = max(0, min(int(line), len(lines) - 1))
    cur = str(lines[li] or '')
    cc = max(0, int(col))

    pairs = {'(': ')', '[': ']', '{': '}', ')': '(', ']': '[', '}': '{'}
    opens = '([{'
    closes = ')]}'

    active_col: int | None = None
    active_ch = ''
    if 0 <= cc < len(cur) and cur[cc] in pairs:
        active_col = cc
        active_ch = cur[cc]
    elif bool(match_left) and cc > 0 and 0 <= cc - 1 < len(cur) and cur[cc - 1] in pairs:
        active_col = cc - 1
        active_ch = cur[cc - 1]
    if active_col is None:
        return []

    starts: list[int] = []
    doc_parts: list[str] = []
    off = 0
    for idx, raw in enumerate(lines):
        s = str(raw or '')
        starts.append(off)
        doc_parts.append(s)
        off += len(s)
        if idx + 1 < len(lines):
            doc_parts.append('\n')
            off += 1
    doc = ''.join(doc_parts)
    if not doc:
        return []

    active_off = starts[li] + int(active_col)
    if active_off < 0 or active_off >= len(doc):
        return []

    mate = pairs[active_ch]
    found_off: int | None = None
    depth = 1
    if active_ch in opens:
        for idx in range(active_off + 1, len(doc)):
            ch = doc[idx]
            if ch == active_ch:
                depth += 1
            elif ch == mate:
                depth -= 1
                if depth == 0:
                    found_off = idx
                    break
    else:
        for idx in range(active_off - 1, -1, -1):
            ch = doc[idx]
            if ch == active_ch:
                depth += 1
            elif ch == mate:
                depth -= 1
                if depth == 0:
                    found_off = idx
                    break
    if found_off is None:
        return []

    def _offset_to_pos(offset: int) -> tuple[int, int]:
        line_idx = bisect_right(starts, int(offset)) - 1
        line_idx = max(0, min(line_idx, len(starts) - 1))
        return (int(line_idx), int(offset - starts[line_idx]))

    active_pos = (int(li), int(active_col))
    mate_pos = _offset_to_pos(int(found_off))
    return [active_pos, mate_pos]


def brace_match_spans(
    *,
    line_index: int,
    frag_start: int,
    frag_text: str,
    brace_positions: list[tuple[int, int]],
) -> list[tuple[int, int]]:
    """Return visible one-cell spans for matched braces in one rendered fragment."""

    if not brace_positions or not frag_text:
        return []
    start = max(0, int(frag_start))
    end = start + len(str(frag_text))
    out: list[tuple[int, int]] = []
    for li, col in brace_positions:
        if int(li) != int(line_index):
            continue
        aa = max(start, int(col))
        bb = min(end, int(col) + 1)
        if bb > aa:
            out.append((int(aa - start), int(bb - start)))
    return out


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
    """Return the visible screen-cell index for a tiny ``colorcolumn`` cue.

    Policy (tiny, renderer-local):
      - ``colorcolumn <= 0`` disables the cue
      - in non-softwrap views, the configured document column is compared against
        the fragment's starting character column so horizontal scrolling stays
        honest
      - in softwrap views, the cue is interpreted as a *screen* column and thus
        repeats on each wrapped visual row, matching common editor behavior
    """

    col = int(colorcolumn)
    width = max(0, int(view_width))
    if col <= 0 or width <= 0:
        return None
    if bool(softwrap):
        x = col - 1
    else:
        x = (col - 1) - max(0, int(frag_start))
    if x < 0 or x >= width:
        return None
    return int(x)


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
    """Return the tiny TUI gutter width for line numbers, or ``0`` when off.

    The gutter is intentionally a UI-level concern for now: future renderers can
    choose their own visuals while still reusing the same editor options.
    Width is ``digits(total logical lines) + 1`` so there is always one spacer
    column between the gutter and the buffer text.
    """

    eb = ed.cur()
    if not bool(ed.options.get("ruler", local=eb.local_options)):
        return 0
    digits = max(1, len(str(max(1, len(eb.buf.lines)))))
    return digits + 1


def line_number_gutter_text(
    ed: Editor,
    *,
    line_index: int,
    wrap_start_col: int,
    gutter_width: int,
) -> str:
    """Return the display text for one rendered buffer row's line-number cell.

    Policy (tiny, deterministic, micro-esque):
      - if the ruler is off, return ``""``
      - wrapped continuation rows show a blank gutter
      - `relativeruler` shows relative numbers off the current line while the
        current line still shows its absolute 1-based line number
      - the final column is reserved as a spacer before buffer text
    """

    if int(gutter_width) <= 0:
        return ""
    if int(wrap_start_col) > 0:
        return " " * int(gutter_width)

    eb = ed.cur()
    cur_line = int(eb.cursors[eb.primary].line) if eb.cursors else 0
    is_relative = bool(ed.options.get("relativeruler", local=eb.local_options))
    li = max(0, int(line_index))
    n = (li + 1) if (not is_relative or li == cur_line) else abs(li - cur_line)
    cell_w = max(1, int(gutter_width) - 1)
    return f"{n:>{cell_w}} "


def scrollbar_gutter_width(ed: Editor) -> int:
    """Return the tiny right-edge scrollbar gutter width, or ``0`` when off.

    The first pass intentionally reserves only one extra screen column in the
    TUI. That keeps the cue renderer-local and easy to remove/replace later.
    """

    eb = ed.cur()
    return 1 if bool(ed.options.get("scrollbar", local=eb.local_options)) else 0


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
    """Return the tiny scrollbar thumb glyph.

    Policy (tiny, renderer-local):
      - prefer the existing micro-esque option name ``scrollbarchar``
      - if the option is empty, fall back to ``|``
      - if multiple characters are configured, use only the first visible one so
        the one-column scrollbar contract stays intact
    """

    try:
        eb = ed.cur()
        raw = str(ed.options.get("scrollbarchar", local=eb.local_options) or "")
    except Exception:
        raw = ""
    return raw[:1] or "|"


def overflow_marker_cells(
    *,
    line_text: str,
    frag_start: int,
    view_width: int,
    softwrap: bool,
) -> list[tuple[int, str]]:
    """Return tiny left/right overflow-marker cells for one rendered fragment.

    Policy (tiny, renderer-local):
      - markers only appear in non-softwrap views, where horizontal clipping is
        otherwise invisible
      - ``<`` marks hidden content to the left of the viewport
      - ``>`` marks hidden content to the right of the viewport
      - when only one screen cell is available, the right marker wins so the
        cue still hints that the line continues forward
    """

    width = max(0, int(view_width))
    start = max(0, int(frag_start))
    if width <= 0 or bool(softwrap):
        return []

    text = str(line_text or "")
    hidden_left = start > 0
    hidden_right = len(text) > (start + width)
    if not hidden_left and not hidden_right:
        return []
    if width == 1:
        return [(0, '>')] if hidden_right else [(0, '<')]

    out: list[tuple[int, str]] = []
    if hidden_left:
        out.append((0, '<'))
    if hidden_right:
        out.append((width - 1, '>'))
    return out


def _render(stdscr: "curses._CursesWindow", ed: Editor) -> None:
    stdscr.erase()
    h, w = stdscr.getmaxyx()
    screen_w = max(1, w)

    # Reserve 2 lines: prompt + status.
    # When a picker-style prompt is active, also reserve a small suggestions area.
    sug_h = 0
    if ed.prompt is not None and ed.prompt.kind not in ("command", "find") and ed.prompt.suggestion_rows:
        sug_h = min(8, max(1, h // 4))
    view_h = max(1, h - 2 - sug_h)
    gutter_w = line_number_gutter_width(ed)
    scrollbar_w = scrollbar_gutter_width(ed)
    text_x = int(gutter_w)
    view_w = max(1, w - text_x - scrollbar_w)
    scrollbar_x = text_x + view_w
    ed.set_viewport(height=view_h, width=view_w, follow_cursor=True)
    vp = ed.viewport_model()

    eb = ed.cur()
    top = int(vp["top_line"])
    left = int(vp["left_col"])
    softwrap_enabled = bool(ed.options.get("softwrap", local=eb.local_options))
    showchars_spec = parse_showchars_option(str(ed.options.get("showchars", local=eb.local_options) or ""))

    # Buffer lines
    rows = ed.view_rows(height=view_h, width=view_w)
    is_help = bool(ed.current_help_doc_topic())
    defs = ed._md_reference_defs(list(eb.buf.lines)) if is_help else {}
    footdefs = ed._md_footnote_defs(list(eb.buf.lines)) if is_help else {}
    fence_flags = md_fenced_code_line_flags(list(eb.buf.lines)) if is_help else []
    html_block_flags = md_html_block_line_flags(list(eb.buf.lines)) if is_help else []
    indented_code_flags = md_indented_code_line_flags(list(eb.buf.lines), fence_flags=fence_flags, html_block_flags=html_block_flags) if is_help else []
    comment_spans = md_html_comment_line_spans(list(eb.buf.lines)) if is_help else []
    heading_roles = ed._md_heading_line_roles(list(eb.buf.lines)) if is_help else {}
    fenced_roles = ed._md_fenced_code_line_roles(list(eb.buf.lines)) if is_help else {}
    definition_roles = ed._md_definition_line_roles(list(eb.buf.lines)) if is_help else {}
    table_kinds = md_table_row_kinds([str(ln) for ln in eb.buf.lines]) if is_help else {}
    cy, cx = ed.cursor_view_pos(height=view_h, width=view_w)
    matchbrace_enabled = bool(ed.options.get("matchbrace", local=eb.local_options))
    matchbraceleft_enabled = bool(ed.options.get("matchbraceleft", local=eb.local_options))
    brace_positions = matching_brace_positions(
        [str(ln) for ln in eb.buf.lines],
        line=int(eb.cursors[eb.primary].line),
        col=int(eb.cursors[eb.primary].col),
        match_left=matchbraceleft_enabled,
    ) if matchbrace_enabled else []

    def _draw_overflow_markers(row: int, cells: list[tuple[int, str]], base_attr: int) -> None:
        if not cells:
            return
        marker_attr = int(base_attr) | curses.A_BOLD | curses.A_DIM
        for xx, ch in cells:
            try:
                stdscr.addnstr(int(row), text_x + int(xx), str(ch), 1, marker_attr)
            except curses.error:
                pass

    for row, (_li, _start, frag) in enumerate(rows):
        row_cursor_attr = cursorline_row_attr(ed, row=row, current_row=cy, local_options=eb.local_options)
        try:
            if text_x > 0:
                num = line_number_gutter_text(ed, line_index=int(_li), wrap_start_col=int(_start), gutter_width=text_x)
                num_attr = curses.A_DIM if num.strip() else 0
                if int(_start) == 0 and int(_li) == int(eb.cursors[eb.primary].line):
                    num_attr = curses.A_BOLD
                num_attr |= row_cursor_attr
                stdscr.addnstr(row, 0, num, text_x, num_attr)
            line_text = str(eb.buf.lines[int(_li)]) if 0 <= int(_li) < len(eb.buf.lines) else str(frag)
            overflowmarkers_enabled = bool(ed.options.get("overflowmarkers", local=eb.local_options))
            overflow_cells = overflow_marker_cells(
                line_text=line_text,
                frag_start=int(_start),
                view_width=view_w,
                softwrap=softwrap_enabled or not overflowmarkers_enabled,
            )
            display_frag, showchar_spans = render_showchars_fragment(
                line_text,
                frag_start=int(_start),
                frag_text=str(frag),
                spec=showchars_spec,
            )
            hlsearch_enabled = bool(ed.options.get("hlsearch", local=eb.local_options))
            search_spans = search_match_spans(
                str(frag),
                str(ed.search.query or ""),
                literal=bool(ed.search.literal),
                case_sensitive=bool(ed.search.case_sensitive),
            ) if hlsearch_enabled else []
            current_search_spans = [
                (int(a), int(b))
                for a, b in search_spans
                if int(row) == int(cy) and int(a) <= int(cx) < int(b)
            ]
            hltrailingws_enabled = bool(ed.options.get("hltrailingws", local=eb.local_options))
            trailing_spans = trailing_whitespace_spans(
                line_text,
                frag_start=int(_start),
                frag_text=str(frag),
            ) if hltrailingws_enabled else []
            hltaberrors_enabled = bool(ed.options.get("hltaberrors", local=eb.local_options))
            tab_error_spans_ = tab_error_spans(
                line_text,
                tabstospaces=bool(ed.options.get("tabstospaces", local=eb.local_options)),
                frag_start=int(_start),
                frag_text=str(frag),
            ) if hltaberrors_enabled else []
            color_x = colorcolumn_screen_x(
                colorcolumn=int(ed.options.get("colorcolumn", local=eb.local_options)),
                frag_start=int(_start),
                view_width=view_w,
                softwrap=softwrap_enabled,
            )
            colorcolumn_spans = [] if color_x is None or int(color_x) >= len(frag) else [(int(color_x), int(color_x) + 1)]
            brace_spans = brace_match_spans(
                line_index=int(_li),
                frag_start=int(_start),
                frag_text=str(frag),
                brace_positions=brace_positions,
            )
            if not is_help:
                if not search_spans and not trailing_spans and not tab_error_spans_ and color_x is None and not brace_spans and not showchar_spans:
                    stdscr.addnstr(row, text_x, display_frag, view_w, row_cursor_attr)
                    _draw_overflow_markers(row, overflow_cells, row_cursor_attr)
                    continue

                bounds = {0, len(frag)}
                for sa, sb in search_spans + current_search_spans + trailing_spans + tab_error_spans_ + colorcolumn_spans + brace_spans + showchar_spans:
                    if int(sb) <= int(sa):
                        continue
                    bounds.add(max(0, int(sa)))
                    bounds.add(min(len(frag), int(sb)))
                pts = sorted(bounds)
                for i in range(len(pts) - 1):
                    aa = int(pts[i])
                    bb = int(pts[i + 1])
                    if bb <= aa:
                        continue
                    attr = row_cursor_attr
                    if any(sa <= aa and bb <= sb for sa, sb in trailing_spans):
                        attr |= curses.A_REVERSE | curses.A_DIM
                    if any(sa <= aa and bb <= sb for sa, sb in tab_error_spans_):
                        attr |= curses.A_REVERSE | curses.A_DIM
                    if any(sa <= aa and bb <= sb for sa, sb in search_spans):
                        attr |= curses.A_REVERSE
                    if any(sa <= aa and bb <= sb for sa, sb in current_search_spans):
                        attr |= curses.A_BOLD
                    if any(sa <= aa and bb <= sb for sa, sb in colorcolumn_spans):
                        attr |= curses.A_REVERSE | curses.A_DIM
                    if any(sa <= aa and bb <= sb for sa, sb in brace_spans):
                        attr |= brace_match_attr(ed, local_options=eb.local_options)
                    if any(sa <= aa and bb <= sb for sa, sb in showchar_spans):
                        attr |= curses.A_DIM
                    stdscr.addnstr(row, text_x + aa, display_frag[aa:bb], max(0, view_w - aa), attr)
                if color_x is not None and int(color_x) >= len(frag):
                    stdscr.addnstr(row, text_x + int(color_x), " ", 1, row_cursor_attr | curses.A_REVERSE | curses.A_DIM)
                _draw_overflow_markers(row, overflow_cells, row_cursor_attr)
                continue
            line_is_fenced = bool(int(_li) < len(fence_flags) and fence_flags[int(_li)])
            fenced_role = str(fenced_roles.get(int(_li), '') or '') if line_is_fenced else ''
            is_fenced_fence = fenced_role == 'fence'
            is_fenced_body = fenced_role == 'body'
            line_is_html_block = bool(int(_li) < len(html_block_flags) and html_block_flags[int(_li)])
            line_is_indented_code = bool(int(_li) < len(indented_code_flags) and indented_code_flags[int(_li)])
            line_is_inert = line_is_fenced or line_is_html_block or line_is_indented_code
            heading_role = "" if line_is_inert else str((heading_roles.get(int(_li)) or ("", 0))[0])
            is_heading_title = heading_role == "title"
            is_heading_underline = heading_role == "underline"
            definition_role, def_col0, def_col1 = (definition_roles.get(int(_li)) or ('', 0, 0)) if not line_is_inert else ('', 0, 0)
            line_is_definition = bool(definition_role)
            table_kind = "" if line_is_inert else str(table_kinds.get(int(_li), "") or "")
            is_table_header = table_kind == "header"
            is_table_delim = table_kind == "delimiter"
            thematic_break_span = None if line_is_inert else md_thematic_break_span(str(frag))
            is_thematic_break = thematic_break_span is not None

            base_attr = row_cursor_attr
            if is_heading_title or is_table_header:
                base_attr |= curses.A_BOLD
            if is_heading_underline or is_table_delim or is_thematic_break or is_fenced_body or line_is_indented_code or line_is_html_block or line_is_definition:
                base_attr |= curses.A_DIM
            if is_fenced_fence:
                base_attr |= curses.A_BOLD | curses.A_DIM
            if (is_heading_title or is_heading_underline or is_table_header) and curses.has_colors():
                base_attr |= curses.color_pair(1)
            elif is_thematic_break and curses.has_colors():
                base_attr |= curses.color_pair(2)

            next_line = md_docs_continuation_line(list(eb.buf.lines), int(_li) + 1, fence_flags=fence_flags, html_block_flags=html_block_flags, comment_spans=comment_spans) if is_help else ""
            next_next_line = md_docs_continuation_line(list(eb.buf.lines), int(_li) + 2, fence_flags=fence_flags, html_block_flags=html_block_flags, comment_spans=comment_spans) if is_help else ""
            link_spans = [] if line_is_inert else md_link_label_spans(str(frag), defs, footdefs, masked_spans=(comment_spans[int(_li)] if int(_li) < len(comment_spans) else []), next_line=next_line, next_next_line=next_next_line)
            code_spans = [] if line_is_inert else md_inline_code_spans(str(frag))
            code_delim_spans = [] if line_is_inert else md_inline_code_delimiter_spans(str(frag))
            strong_spans = [] if line_is_inert else md_strong_spans(str(frag))
            emphasis_spans = [] if line_is_inert else md_emphasis_spans(str(frag))
            strike_spans = [] if line_is_inert else md_strikethrough_spans(str(frag))
            inline_markup_delim_spans = [] if line_is_inert else md_inline_markup_delimiter_spans(str(frag))
            pipe_spans = md_table_pipe_spans(str(frag)) if table_kind else []
            list_info = None if line_is_inert else md_list_marker(str(frag), max_leading_spaces=None)
            list_marker_spans = [list_info[:2]] if list_info else []
            task_info = None if line_is_inert else md_task_checkbox(str(frag), max_leading_spaces=None)
            task_box_spans = [task_info[:2]] if task_info else []
            checked_task_body = [md_task_body_span(str(frag), max_leading_spaces=None)] if task_info and task_info[2] and md_task_body_span(str(frag), max_leading_spaces=None) else []
            blockquote_info = None if line_is_inert else md_blockquote_prefix(str(frag))
            blockquote_prefix_spans = [blockquote_info[:2]] if blockquote_info else []
            blockquote_body = [md_blockquote_body_span(str(frag))] if blockquote_info and md_blockquote_body_span(str(frag)) else []
            blockquote_alert_info = None if line_is_inert else md_blockquote_alert_marker(str(frag))
            blockquote_alert_spans = [blockquote_alert_info[:2]] if blockquote_alert_info else []
            footnote_ref_spans = [] if line_is_inert else md_footnote_ref_token_spans(
                str(frag),
                footdefs,
                masked_spans=(comment_spans[int(_li)] if int(_li) < len(comment_spans) else []),
                next_line=next_line,
                next_next_line=next_next_line,
            )
            autolink_token_spans = [] if line_is_inert else md_autolink_token_spans(
                str(frag),
                masked_spans=(comment_spans[int(_li)] if int(_li) < len(comment_spans) else []),
                next_line=next_line,
                next_next_line=next_next_line,
            )
            image_token_spans = [] if line_is_inert else md_image_token_spans(
                str(frag),
                defs,
                masked_spans=(comment_spans[int(_li)] if int(_li) < len(comment_spans) else []),
                next_line=next_line,
                next_next_line=next_next_line,
            )
            link_source_token_spans = [] if line_is_inert else md_link_source_token_spans(
                str(frag),
                defs,
                footdefs,
                masked_spans=(comment_spans[int(_li)] if int(_li) < len(comment_spans) else []),
                next_line=next_line,
                next_next_line=next_next_line,
            )
            raw_html_tag_spans = [] if line_is_inert else md_raw_html_tag_token_spans(
                str(frag),
                masked_spans=(comment_spans[int(_li)] if int(_li) < len(comment_spans) else []),
            )
            escaped_markdown_spans = [] if line_is_inert else md_escaped_markdown_token_spans(
                str(frag),
                masked_spans=(comment_spans[int(_li)] if int(_li) < len(comment_spans) else []),
            )
            thematic_break_chars = md_thematic_break_char_spans(str(frag)) if is_thematic_break else []
            definition_marker_spans = [(int(def_col0), int(def_col1))] if int(def_col1) > int(def_col0) else []
            line_comment_spans = comment_spans[int(_li)] if int(_li) < len(comment_spans) else []
            dim_spans = _merge_spans(code_spans + code_delim_spans + strike_spans + inline_markup_delim_spans + pipe_spans + checked_task_body + blockquote_body + line_comment_spans + image_token_spans + link_source_token_spans + raw_html_tag_spans + escaped_markdown_spans)
            bold_spans = _merge_spans(strong_spans + code_delim_spans + [(int(a), int(b)) for a, b in list_marker_spans + task_box_spans + blockquote_prefix_spans + blockquote_alert_spans + footnote_ref_spans + autolink_token_spans + thematic_break_chars + definition_marker_spans])
            italic_spans = _merge_spans(emphasis_spans)

            def _write_range(a: int, b: int, attr0: int) -> None:
                """Write frag[a:b] applying tiny docs-help style overlays."""

                if b <= a:
                    return
                bounds = {int(a), int(b)}
                for sa, sb in dim_spans + bold_spans + italic_spans + search_spans + current_search_spans + trailing_spans + tab_error_spans_ + colorcolumn_spans + brace_spans + showchar_spans:
                    sa = int(sa)
                    sb = int(sb)
                    if sb <= a or sa >= b:
                        continue
                    bounds.add(max(int(a), sa))
                    bounds.add(min(int(b), sb))
                pts = sorted(bounds)
                if len(pts) <= 1:
                    stdscr.addnstr(row, text_x + a, display_frag[a:b], max(0, view_w - a), attr0)
                    return
                italic_attr = int(getattr(curses, 'A_ITALIC', 0) or curses.A_UNDERLINE)
                for i in range(len(pts) - 1):
                    aa = int(pts[i])
                    bb = int(pts[i + 1])
                    if bb <= aa:
                        continue
                    attr = int(attr0)
                    if any(sa <= aa and bb <= sb for sa, sb in dim_spans):
                        attr |= curses.A_DIM
                    if any(sa <= aa and bb <= sb for sa, sb in bold_spans):
                        attr |= curses.A_BOLD
                    if any(sa <= aa and bb <= sb for sa, sb in italic_spans):
                        attr |= italic_attr
                    if any(sa <= aa and bb <= sb for sa, sb in trailing_spans):
                        attr |= curses.A_REVERSE | curses.A_DIM
                    if any(sa <= aa and bb <= sb for sa, sb in tab_error_spans_):
                        attr |= curses.A_REVERSE | curses.A_DIM
                    if any(sa <= aa and bb <= sb for sa, sb in search_spans):
                        attr |= curses.A_REVERSE
                    if any(sa <= aa and bb <= sb for sa, sb in current_search_spans):
                        attr |= curses.A_BOLD
                    if any(sa <= aa and bb <= sb for sa, sb in colorcolumn_spans):
                        attr |= curses.A_REVERSE | curses.A_DIM
                    if any(sa <= aa and bb <= sb for sa, sb in brace_spans):
                        attr |= brace_match_attr(ed, local_options=eb.local_options)
                    if any(sa <= aa and bb <= sb for sa, sb in showchar_spans):
                        attr |= curses.A_DIM
                    stdscr.addnstr(row, text_x + aa, display_frag[aa:bb], max(0, view_w - aa), attr)
                if color_x is not None and int(color_x) >= len(frag):
                    stdscr.addnstr(row, text_x + int(color_x), " ", 1, attr0 | curses.A_REVERSE | curses.A_DIM)

            if not link_spans:
                _write_range(0, len(frag), base_attr)
                _draw_overflow_markers(row, overflow_cells, row_cursor_attr)
                continue

            x = 0
            for a, b in link_spans:
                if a > x:
                    _write_range(x, a, base_attr)
                attr = base_attr | curses.A_UNDERLINE
                if curses.has_colors():
                    attr |= curses.color_pair(3)
                if int(cy) == int(row) and int(a) <= int(cx) < int(b):
                    attr |= curses.A_BOLD
                _write_range(a, b, attr)
                x = b
            if x < len(frag):
                _write_range(x, len(frag), base_attr)
            _draw_overflow_markers(row, overflow_cells, row_cursor_attr)
        except curses.error:
            pass

    st = ed.status_model()

    # Suggestion list (pickers)
    if sug_h > 0:
        items = _prompt_display_items(ed, max_lines=sug_h, width=view_w)
        for i, it in enumerate(items[:sug_h]):
            line = it.text
            y = view_h + i
            try:
                attr = 0
                if it.is_selected:
                    attr = curses.A_REVERSE
                elif it.is_header:
                    attr = curses.A_BOLD
                    if curses.has_colors():
                        attr |= curses.color_pair(1)
                elif it.is_more:
                    attr = curses.A_DIM
                    if curses.has_colors():
                        attr |= curses.color_pair(2)

                # Row-kind styling (UI-only, scan-friendly):
                # - palette actions get a hint color/bold
                # - palette openpath/recentfile rows get a file-ish hint
                # - helplink/helpnav link rows get a link-ish hint
                # - helpnav heading rows are bold
                rk = str(it.row_kind or "")
                if not it.is_header and not it.is_more:
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

    # Tiny right-edge scrollbar cue.
    if int(scrollbar_w) > 0:
        if softwrap_enabled:
            total_rows = ed._total_visual_rows(eb, w=view_w)
            start_row = ed._viewport_visual_start(eb, w=view_w)
        else:
            total_rows = max(1, len(eb.buf.lines))
            start_row = max(0, int(top))
        thumb = scrollbar_thumb_span(total_rows=total_rows, start_row=start_row, window_rows=view_h)
        if thumb is not None:
            thumb_top, thumb_size = thumb
            thumb_char = scrollbar_thumb_char(ed)
            for yy in range(int(thumb_top), min(int(view_h), int(thumb_top) + int(thumb_size))):
                try:
                    stdscr.addnstr(yy, int(scrollbar_x), thumb_char, 1, curses.A_REVERSE | curses.A_DIM)
                except curses.error:
                    pass

    # Prompt line
    prompt_y = h - 2
    if ed.prompt is not None:
        kind = str(ed.prompt.kind)
        prefix = ":" if kind in ("command", "palette") else ("/" if kind == "find" else "?")
        text = str(ed.prompt.text)
        line = prefix + text

        # Minimal picker usability: show compact picker position + current preview.
        pos = str(st.get("prompt_position_summary", "") or "")
        preview = str(st.get("prompt_current_preview", "") or "")
        search_pos = str(st.get("search_summary", "") or "")
        if kind == "find":
            if search_pos:
                line = line + "  [" + search_pos + "]"
        elif kind not in ("command", "find"):
            if pos:
                line = line + "  [" + pos + "]"
            if preview:
                # Keep it single-line and truncatable.
                line = line + "  | " + preview

        try:
            stdscr.addnstr(prompt_y, 0, line, screen_w)
        except curses.error:
            pass
    else:
        # show last message when no prompt is active
        msg = str(st.get("last_message", ""))
        try:
            stdscr.addnstr(prompt_y, 0, msg, screen_w)
        except curses.error:
            pass

    # Status line
    status_y = h - 1
    status = ed.statusline_text(screen_w)
    try:
        stdscr.addnstr(status_y, 0, status, screen_w)
    except curses.error:
        pass

    # Place the terminal cursor.
    try:
        if ed.prompt is not None:
            px = 1 + int(st.get("prompt_cursor", 0)) - left  # prompt isn't horizontally scrolled yet
            stdscr.move(prompt_y, max(0, min(screen_w - 1, px)))
        else:
            cy, cx = ed.cursor_view_pos(height=view_h, width=view_w)
            stdscr.move(max(0, min(view_h - 1, int(cy))), max(0, min(w - 1, text_x + int(cx))))
    except curses.error:
        pass

    stdscr.refresh()


def run_tui(
    path: str | None = None,
    *,
    plugins_root: str = "plugins",
) -> int:
    ed = Editor()
    install_editor_hostcalls(ed)

    pm = PluginManager(ed.vm)
    ed.plugin_manager = pm
    pm.load_tree(plugins_root)

    for name, err in getattr(pm, "load_errors", []):
        ed.message(f"plugin load failed: {name}: {err}")

    # User rc/init (best-effort). Loaded after plugins so it can override.
    ed.load_user_init()
    # Refresh capability advertisement now that init may have changed options.
    try:
        ed.refresh_capabilities()
    except Exception:
        pass
    # Optional recent-file persistence (best-effort; gated by recent.persist + cap.persist options).
    try:
        ed.load_recent_files()
    except Exception:
        pass
    # Optional prompt-history persistence (best-effort; gated by history.persist + cap.persist).
    try:
        ed.load_prompt_history()
    except Exception:
        pass
    # Optional savecursor persistence (best-effort; gated by savecursor + cap.persist).
    try:
        ed.load_saved_cursors()
    except Exception:
        pass


    if path:
        ed.open_file(path)
    else:
        ed.new_buffer("*scratch*", "")

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
    ap.add_argument("--plugins", default="plugins", help="plugin root directory")
    args = ap.parse_args(argv)
    return int(run_tui(args.path, plugins_root=args.plugins))


if __name__ == "__main__":
    raise SystemExit(main())
