from __future__ import annotations

from dataclasses import dataclass, field
from contextlib import contextmanager
from bisect import bisect_right
import codecs
import json
import time
import re
import shlex
import string
import os
import webbrowser
from pathlib import Path
from typing import Any
from urllib.parse import unquote

from micromax import VM
from micromax.regex_tools import convert_replacement_template

from .buffer import Buffer, Cursor
from .command_dispatcher import CommandDispatcher, install_default_commands
from .commandbar import Prompt
from .cmdline import parse_cmdline
from .commands import ActionRegistry
from .keymap import Keymap, parse_action_chain
from .options import Options
from .search import SearchState, find_next, find_prev, search_position
from .textpos import cursor_to_index, index_to_cursor
from .selection import Selection
from .undo import Edit, UndoManager
from .filetypes import detect_filetype
from .timers import TimerQueue
from .highlight import highlight_line, HIGHLIGHT_TAGS
from .statusformat import render_status_template
from .capabilities import refresh_vm_features
from .fs_sandbox import fs_root as fs_sandbox_root, resolve_path as fs_resolve_path, is_allowed as fs_path_allowed
from .persist_sandbox import persist_root as persist_sandbox_root, resolve_path as persist_resolve_path, is_allowed as persist_path_allowed, deny_reason as persist_deny_reason


# Actions that are expected to mutate the active buffer.
#
# This list powers the "protected/read-only" buffer guard used for internal
# help/docs buffers. Unlike OS-level readonly file permissions, protected
# buffers should reject edits (so users don't accidentally trash generated
# content).
MUTATING_ACTIONS: set[str] = {
    "InsertText",
    "InsertNewline",
    "Backspace",
    "Delete",
    "Undo",
    "Redo",
    "Cut",
    "Paste",
    "CutLine",
    "DuplicateLine",
    "MoveLinesUp",
    "MoveLinesDown",
    "IndentSelection",
    "UnindentSelection",
    "InsertTab",
    "QueryReplaceYes",
    "QueryReplaceAll",
    "QueryReplaceLast",
}


def _merge_spans(spans: list[tuple[int, int]]) -> list[tuple[int, int]]:
    """Merge overlapping/adjacent ``[start,end)`` spans."""

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


def search_match_spans(
    text: str,
    query: str,
    *,
    literal: bool = True,
    case_sensitive: bool = False,
) -> list[tuple[int, int]]:
    """Return best-effort visible search-match spans for one rendered row.

    This stays row-fragment-local on purpose: the shared editor-side search row
    model should expose the exact visible fragment matches that the reference UI
    is painting, not reconstruct hidden off-screen context.
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

    Policy (tiny, shared visible-row model):
      - trailing whitespace is any final run of spaces/tabs in the logical line
      - only the intersection with the current visible fragment is returned
      - this keeps softwrap and horizontal scrolling honest without promoting the
        cue into a larger whole-buffer style system
    """

    full = str(line or "")
    frag = str(full if frag_text is None else frag_text)
    if not full or not frag:
        return []

    start = max(0, int(frag_start))
    end = start + len(frag)

    m = re.search(r"[ \t]+$", full)
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

    Policy (tiny, shared visible-row model):
      - when ``tabstospaces`` is true, all literal tab characters are cues
      - when ``tabstospaces`` is false, space characters in the initial indent
        run are cues while tabs stay ordinary
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
            if ch != "\t":
                continue
            aa = max(start, int(idx))
            bb = min(end, int(idx) + 1)
            if bb > aa:
                spans.append((int(aa - start), int(bb - start)))
        return spans

    indent_end = 0
    while indent_end < len(full) and full[indent_end] in " \t":
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


def matching_brace_positions(
    lines: list[str],
    *,
    line: int,
    col: int,
    match_left: bool = True,
) -> list[tuple[int, int]]:
    """Return visible brace-pair positions for the primary cursor point.

    Policy (tiny, shared visible-row model, syntax-agnostic):
      - only the classic pairs ``()`` / ``[]`` / ``{}`` are considered
      - prefer the character directly under the cursor; when ``match_left`` is
        true and that is not a brace, also consider the character immediately to
        the left (micro-esque I-beam behavior)
      - matching is purely textual and nest-aware across the whole buffer
      - return ``[]`` when there is no brace under/left of the cursor or when no
        matching partner exists
    """

    if not lines:
        return []
    li = max(0, min(int(line), len(lines) - 1))
    cur = str(lines[li] or "")
    cc = max(0, int(col))

    pairs = {"(": ")", "[": "]", "{": "}", ")": "(", "]": "[", "}": "{"}
    opens = "([{"
    closes = ")] }".replace(" ", "")

    active_col: int | None = None
    active_ch = ""
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
        s = str(raw or "")
        starts.append(off)
        doc_parts.append(s)
        off += len(s)
        if idx + 1 < len(lines):
            doc_parts.append("\n")
            off += 1
    doc = "".join(doc_parts)
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
    elif active_ch in closes:
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


def colorcolumn_screen_x(
    *,
    colorcolumn: int,
    frag_start: int,
    view_width: int,
    softwrap: bool,
) -> int | None:
    """Return the visible screen-cell index for a tiny ``colorcolumn`` cue.

    Policy (tiny, shared visible-row model):
      - ``colorcolumn <= 0`` disables the cue
      - in non-softwrap views, the configured document column is compared against
        the fragment's starting character column so horizontal scrolling stays
        honest
      - in softwrap views, the cue is interpreted as a screen column and thus
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


def parse_showchars_option(raw: str) -> dict[str, str]:
    """Parse a tiny micro-esque ``showchars`` option string.

    Supported keys are the small subset Micromax can render honestly in the
    current one-cell-per-character reference TUI and shared visible-row model:
    ``space``, ``tab``, ``ispace``, and ``itab``. Unknown keys are ignored.
    Values may be empty; an empty value just disables that specific
    replacement.

    Example: ``tab=>,space=.,itab=|>,ispace=|``.
    """

    out: dict[str, str] = {}
    s = str(raw or "").strip()
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

    Policy (tiny, shared visible-row model):
      - replacements only affect the *displayed* fragment, never the buffer text
      - only file-backed spaces/tabs are replaced; softwrap continuation-indent
        prefix spaces stay as plain spaces because they are renderer-introduced
      - ``ispace`` / ``itab`` override ``space`` / ``tab`` in the leading indent
        run before the first visible character on the logical line
      - all replacements stay one-cell wide for now, so even ``tab`` / ``itab``
        use only the first configured character in the current reference TUI
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

def overflow_marker_cells(
    *,
    line_text: str,
    frag_start: int,
    view_width: int,
    softwrap: bool,
) -> list[tuple[int, str]]:
    """Return tiny left/right overflow-marker cells for one visible fragment.

    Policy (tiny, shared visible-row model):
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


def render_overflow_fragment(
    line: str,
    *,
    frag_start: int = 0,
    frag_text: str | None = None,
    view_width: int = 0,
    softwrap: bool = False,
) -> tuple[str, list[tuple[int, str]]]:
    """Return a visible fragment with tiny overflow markers already applied.

    The shared editor-side display-row model wants the same plain-text result
    the reference curses TUI paints, not just the marker cell positions. This
    helper therefore keeps the underlying policy tiny and text-first: overlay
    the marker characters onto the visible fragment without introducing a wider
    style/theme contract.
    """

    full = str(line or '')
    frag = str(full if frag_text is None else frag_text)
    width = max(0, int(view_width if view_width else len(frag)))
    if width <= 0:
        return ('', [])

    cells = overflow_marker_cells(
        line_text=full,
        frag_start=frag_start,
        view_width=width,
        softwrap=softwrap,
    )
    if not cells:
        return (frag[:width], [])

    chars = list(frag[:width])
    for pos, ch in cells:
        xx = max(0, int(pos))
        if xx >= len(chars):
            chars.extend(' ' * (xx - len(chars) + 1))
        chars[xx] = str(ch)[:1]
    return (''.join(chars), [(int(pos), str(ch)[:1]) for pos, ch in cells])


# --- Markdown helpers (docs/help browser) ---

def md_norm_ref_id(s: str) -> str:
    """Normalize a markdown reference-id (case-insensitive, collapse whitespace)."""

    try:
        return re.sub(r"\s+", " ", str(s or "").strip()).casefold()
    except Exception:
        return ""


def md_link_label_has_text(s: str) -> bool:
    """Return True when a tiny markdown link label has visible text.

    CommonMark requires link labels to contain at least one non-whitespace
    character. The docs browser keeps that rule deliberately small and shared so
    empty or space-only labels do not become live inline/reference/shortcut
    links just because a regex-shaped destination happened to follow.
    """

    text = str(s or "")
    return any(not ch.isspace() for ch in text)


def md_leading_spaces_upto3(line: str) -> int | None:
    """Return the count of leading markdown block-indent spaces (0..3).

    The tiny docs browser intentionally follows CommonMark's "up to three
    spaces" rule for block starters. Tabs do not count here, and four leading
    spaces should be left as code-block-ish prose rather than parsed as
    headings or reference definitions.
    """

    s = str(line or "")
    col = 0
    while col < len(s) and s[col] == " " and col < 4:
        col += 1
    if col < len(s) and s[col] == "\t":
        return None
    if col >= 4:
        return None
    return col


_MD_BACKSLASH_UNESCAPE_CHARS = set(string.punctuation) | {" ", "\t"}


def md_backslash_unescape(text: str) -> str:
    r"""Undo a tiny markdown-safe subset of backslash escapes.

    The docs browser only needs a small, inspectable policy here: punctuation
    escapes behave like markdown escapes, and we also treat ``\ `` / ``\t`` as
    useful local-doc conveniences for path-like destinations. Unknown escapes
    stay literal.
    """

    s = str(text or "")
    if not s:
        return ""

    out: list[str] = []
    i = 0
    while i < len(s):
        ch = s[i]
        if ch == "\\" and i + 1 < len(s):
            nxt = s[i + 1]
            if nxt in _MD_BACKSLASH_UNESCAPE_CHARS:
                out.append(nxt)
                i += 2
                continue
        out.append(ch)
        i += 1
    return ''.join(out)


def _md_rest_is_title(rest: str) -> bool:
    """Return True when *rest* is empty or a tiny markdown link title."""

    r = str(rest or "").strip()
    if not r:
        return True

    opener = r[:1]
    if opener in ('"', "'"):
        i = 1
        while i < len(r):
            ch = r[i]
            if ch == "\\":
                i += 2
                continue
            if ch == opener:
                return not r[i + 1 :].strip()
            i += 1
        return False

    if opener == '(':
        span = md_balanced_span(r, 0, opener='(', closer=')')
        if span is None:
            return False
        _, end = span
        return not r[end:].strip()

    return False


def _md_inline_rest_closes_on_line(rest: str) -> bool:
    """Return True when *rest* contains a tiny inline-link close on one line.

    ``rest`` is the content after a parsed destination. We accept either an
    immediate ``)`` (possibly after spaces/tabs) or a tiny markdown title
    followed by ``)``. Any trailing text after the closer is ignored so callers
    can keep scanning the rest of the source line normally.
    """

    r = str(rest or "")
    i = 0
    while i < len(r):
        ch = r[i]
        if ch == "\\":
            i += 2
            continue
        if ch == ')':
            return _md_rest_is_title(r[:i])
        i += 1
    return False


def md_inline_link_target_multiline(after_open: str, next_line: str = "", next_next_line: str = "") -> str:
    """Extract a tiny wrapped inline-link destination.

    CommonMark allows inline-link pieces to be separated by spaces/tabs and up
    to one line ending. Micromax keeps this intentionally small and shared:
    support destination-on-next-line and title/close-on-next-line shells around
    the existing destination parser without growing a full multiline inline
    parser.
    """

    first = str(after_open or "").lstrip(" \t")
    cont1 = str(next_line or "")
    cont2 = str(next_next_line or "")
    if first:
        dest_src = first
    else:
        dest_src = cont1.lstrip(" \t")
        cont1 = cont2
        cont2 = ""
        if not dest_src:
            return ""

    parsed = _md_link_target_prefix(dest_src)
    if parsed is None:
        return ""
    dest, rest, used_angle_brackets = parsed
    if not dest or not _md_link_rest_has_required_separator(rest, used_angle_brackets=used_angle_brackets):
        return ""

    if _md_inline_rest_closes_on_line(rest):
        return dest
    if rest.strip(" \t"):
        if _md_rest_is_title(rest):
            return dest if str(cont1 or "").lstrip(" \t").startswith(')') else ""
        return ""

    tail1 = str(cont1 or "").lstrip(" \t")
    if not tail1:
        return ""
    if _md_inline_rest_closes_on_line(tail1):
        return dest
    if _md_rest_is_title(tail1):
        return dest if str(cont2 or "").lstrip(" \t").startswith(')') else ""
    return ""


def md_docs_continuation_line(
    lines: list[object],
    idx: int,
    *,
    fence_flags: list[bool] | None = None,
    html_block_flags: list[bool] | None = None,
    comment_spans: list[list[tuple[int, int]]] | None = None,
) -> str:
    """Return one docs/help continuation line, or ``''`` when it is inert.

    This keeps small multiline markdown affordances aligned across editor
    actions, pickers, and the TUI: fenced/raw-HTML/comment-hidden lines and
    blank lines do not participate as wrapped link/reference continuations.
    """

    xs = list(lines or [])
    j = int(idx)
    if j < 0 or j >= len(xs):
        return ""
    if fence_flags and j < len(fence_flags) and fence_flags[j]:
        return ""
    if html_block_flags and j < len(html_block_flags) and html_block_flags[j]:
        return ""
    s2 = str(xs[j])
    stripped = s2.lstrip(" \t")
    if not stripped:
        return ""
    if comment_spans:
        spans2 = comment_spans[j] if j < len(comment_spans) else []
        col0 = len(s2) - len(stripped)
        if md_span_contains(spans2, int(col0), int(col0) + 1):
            return ""
    return s2


def _md_link_target_prefix(text: str) -> tuple[str, str, bool] | None:
    """Parse one tiny markdown link destination prefix.

    Returns ``(destination, rest, used_angle_brackets)`` when ``text`` starts
    with a destination, leaving any trailing title/whitespace in ``rest`` for
    the caller to decide about. This is shared by inline-link parsing and
    multi-line reference-link definitions so the docs browser does not grow
    separate destination regexes.
    """

    s = str(text or "")
    if not s:
        return None

    if s.startswith('<'):
        i = 1
        while i < len(s):
            ch = s[i]
            if ch == "\\":
                i += 2
                continue
            if ch == '>':
                dest = s[1:i].strip()
                if dest:
                    return (md_backslash_unescape(dest), s[i + 1 :], True)
                return None
            if ch in "\r\n<":
                return None
            i += 1
        return None

    i = 0
    depth = 0
    while i < len(s):
        ch = s[i]
        if ch == "\\":
            if i + 1 >= len(s):
                break
            i += 2
            continue
        if ch in "\r\n":
            break
        if ch.isspace():
            break
        if ord(ch) < 32:
            return None
        if ch == '(':
            depth += 1
        elif ch == ')':
            if depth == 0:
                break
            depth -= 1
        i += 1

    raw_dest = s[:i]
    if not raw_dest or depth != 0:
        return None
    return (md_backslash_unescape(raw_dest).strip(), s[i:], False)


def _md_link_rest_has_required_separator(rest: str, *, used_angle_brackets: bool) -> bool:
    """Return True when link-destination trailing text starts legally.

    Angle-bracket destinations need whitespace before an optional title;
    immediate ``)`` is still fine. Bare destinations do not need a separate
    check here because the tiny destination parser already stops before the
    whitespace that would separate a following title.
    """

    r = str(rest or "")
    if not r or not used_angle_brackets:
        return True
    return r[:1].isspace() or r.startswith(')')


def md_reference_def_target_info(after_colon: str, next_line: str = "", next_next_line: str = "") -> tuple[str, int]:
    """Extract a tiny markdown reference-definition destination plus line usage.

    Returns ``(target, continuation_lines_used)`` where the second value is the
    number of following physical lines consumed by the tiny shared parser:

    - ``0`` when the definition stays on the starter line
    - ``1`` when the destination or title comes from ``next_line``
    - ``2`` when both a wrapped destination and a wrapped title are used

    CommonMark allows up to one line ending after the colon and after the
    destination inside reference definitions. Micromax keeps that support
    intentionally small and shared: the destination parser is reused, while the
    surrounding multiline logic stays conservative and inspectable.
    """

    first = str(after_colon or "").lstrip(" \t")
    used_lines = 0
    if first:
        dest_src = first
        peek_title = str(next_line or "")
    else:
        dest_src = str(next_line or "").lstrip(" \t")
        if not dest_src:
            return ("", 0)
        used_lines = 1
        peek_title = str(next_next_line or "")

    parsed = _md_link_target_prefix(dest_src)
    if parsed is None:
        return ("", 0)
    dest, rest, used_angle_brackets = parsed
    if not dest or not _md_link_rest_has_required_separator(rest, used_angle_brackets=used_angle_brackets):
        return ("", 0)

    if rest.strip(" \t"):
        return ((dest, used_lines) if _md_rest_is_title(rest) else ("", 0))

    title_line = str(peek_title or "").lstrip(" \t")
    if title_line[:1] in ('"', "'", '('):
        return ((dest, used_lines + 1) if _md_rest_is_title(title_line) else ("", 0))

    return (dest, used_lines)


def md_reference_def_target(after_colon: str, next_line: str = "", next_next_line: str = "") -> str:
    """Extract a tiny markdown reference-definition destination."""

    return md_reference_def_target_info(after_colon, next_line, next_next_line)[0]


def md_inline_link_target(inner: str) -> str:
    """Extract and *validate* a tiny inline-link destination.

    Supports the docs-browser cases that are awkward with ``split()`` alone:
      - balanced parentheses in bare destinations
      - backslash escapes inside destinations/titles
      - optional quoted or parenthesized titles

    The policy stays intentionally conservative: malformed trailing content
    returns ``''`` so callers can fall back to other markdown forms.
    """

    s = str(inner or "").strip()
    if not s:
        return ""

    parsed = _md_link_target_prefix(s)
    if parsed is None:
        return ""
    dest, rest, used_angle_brackets = parsed
    if not dest or not _md_link_rest_has_required_separator(rest, used_angle_brackets=used_angle_brackets) or not _md_rest_is_title(rest):
        return ""
    return dest

_BACKTICK_RUN_RE = re.compile(r"(?<!`)(?P<ticks>`+)(?!`)")
_FENCE_OPEN_RE = re.compile(r"^[ ]{0,3}(?P<fence>`{3,}|~{3,})(?P<rest>.*)$")
_SETEXT_UNDERLINE_RE = re.compile(r"^[ ]{0,3}(?P<run>=+|-{2,})[ \\t]*$")


_MD_HTML_BLOCK_TAGS = {
    "address", "article", "aside", "base", "basefont", "blockquote", "body",
    "caption", "center", "col", "colgroup", "dd", "details", "dialog",
    "dir", "div", "dl", "dt", "fieldset", "figcaption", "figure",
    "footer", "form", "frame", "frameset", "h1", "h2", "h3", "h4",
    "h5", "h6", "head", "header", "hr", "html", "iframe", "legend",
    "li", "link", "main", "menu", "menuitem", "meta", "nav", "noframes",
    "ol", "optgroup", "option", "p", "param", "search", "section",
    "source", "summary", "table", "tbody", "td", "tfoot", "th", "thead",
    "title", "tr", "track", "ul",
}


_MD_HTML_BLOCK_TYPE1_RE = re.compile(
    r"^[ ]{0,3}<(?P<tag>script|pre|style|textarea)(?=[\t />]|$)",
    flags=re.IGNORECASE,
)
_MD_HTML_BLOCK_TYPE3_RE = re.compile(r"^[ ]{0,3}<\?")
_MD_HTML_BLOCK_TYPE4_RE = re.compile(r"^[ ]{0,3}<![A-Z]")
_MD_HTML_BLOCK_TYPE5_RE = re.compile(r"^[ ]{0,3}<!\[CDATA\[")
_MD_HTML_BLOCK_TYPE6_RE = re.compile(
    rf"^[ ]{{0,3}}</?(?:{'|'.join(sorted(re.escape(t) for t in _MD_HTML_BLOCK_TAGS))})(?=[\t />]|$)",
    flags=re.IGNORECASE,
)


_MD_HTML_TYPE7_EXCLUDED = {"pre", "script", "style", "textarea"}


def md_backslash_escaped(s: str, idx: int) -> bool:
    """Return True when the character at *idx* is escaped by odd backslashes.

    This tiny helper is shared by docs-browser scanners so literal markdown like
    ``\\[example]`` or ``\\<https://example.invalid>`` stays prose instead of
    turning into a live link/footnote/autolink.
    """

    text = str(s or "")
    i = int(idx)
    if i <= 0 or i > len(text):
        return False
    n = 0
    j = i - 1
    while j >= 0 and text[j] == "\\":
        n += 1
        j -= 1
    return (n % 2) == 1


def md_html_comment_spans(line: str, *, in_comment: bool = False) -> tuple[list[tuple[int, int]], bool]:
    """Return tiny raw-HTML comment spans for one source line.

    The policy is intentionally small and shared across docs/help surfaces:
      - recognizes HTML comment open/close markers ``<!--`` / ``-->``
      - supports multi-line comments via ``in_comment`` carry state
      - returns spans covering the raw-comment text on this line

    This is a precedence helper, not a full HTML tokenizer. It keeps literal
    markdown examples inside HTML comments from leaking back into the live docs
    browser as links, refs, or footnotes.
    """

    s = str(line or "")
    if not s:
        return ([], bool(in_comment))

    spans: list[tuple[int, int]] = []
    i = 0
    inside = bool(in_comment)
    n = len(s)
    while i < n:
        if inside:
            j = s.find('-->', i)
            if j < 0:
                spans.append((i, n))
                return (spans, True)
            spans.append((i, j + 3))
            i = j + 3
            inside = False
            continue
        j = s.find('<!--', i)
        if j < 0:
            break
        k = s.find('-->', j + 4)
        if k < 0:
            spans.append((j, n))
            return (spans, True)
        spans.append((j, k + 3))
        i = k + 3
    return (spans, inside)


def md_html_comment_line_spans(lines: list[object]) -> list[list[tuple[int, int]]]:
    """Return per-line raw-HTML comment spans for a docs/help buffer."""

    xs = [str(x) for x in (lines or [])]
    out: list[list[tuple[int, int]]] = []
    inside = False
    for s in xs:
        spans, inside = md_html_comment_spans(s, in_comment=inside)
        out.append(spans)
    return out


def _md_inline_code_parts(line: str) -> list[tuple[int, int, int, int, int, int]]:
    """Return tiny inline-code opener/body/closer spans for one line.

    Returned tuples are ``(open_a, open_b, body_a, body_b, close_a, close_b)``.
    The policy intentionally matches :func:`md_inline_code_spans`: equal-length
    backtick delimiters only, longer runs allowed, fenced-code openers ignored,
    and unmatched/escaped runs skipped.
    """

    s = str(line or "")
    if not s:
        return []
    if re.match(r"^\s*`{3,}", s):
        return []

    runs = list(_BACKTICK_RUN_RE.finditer(s))
    if not runs:
        return []

    out: list[tuple[int, int, int, int, int, int]] = []
    i = 0
    while i < len(runs):
        m = runs[i]
        open_a = int(m.start('ticks'))
        open_b = int(m.end('ticks'))
        n = len(str(m.group('ticks') or ''))
        if md_backslash_escaped(s, open_a):
            i += 1
            continue
        j = i + 1
        matched = False
        while j < len(runs):
            m2 = runs[j]
            if len(str(m2.group('ticks') or '')) != n:
                j += 1
                continue
            close_a = int(m2.start('ticks'))
            close_b = int(m2.end('ticks'))
            if close_a > open_b:
                out.append((open_a, open_b, open_b, close_a, close_a, close_b))
                i = j + 1
                matched = True
                break
            j += 1
        if not matched:
            i += 1
    return out


def md_inline_code_spans(line: str) -> list[tuple[int, int]]:
    """Return spans for tiny inline markdown code in a docs/help line.

    Policy is intentionally small but useful for docs-browser precedence:
      - recognizes inline code spans with equal-length backtick delimiters
      - supports longer delimiters so literal backticks can appear inside code
      - returns spans for the *inside* text (excluding the backticks)
      - ignores fenced code block markers (```...).

    Spans are ``(start, end)`` indices into ``line``.
    """

    return [(int(body_a), int(body_b)) for _oa, _ob, body_a, body_b, _ca, _cb in _md_inline_code_parts(line)]



def md_inline_code_delimiter_spans(line: str) -> list[tuple[int, int]]:
    """Return backtick-delimiter spans for tiny inline markdown code.

    This stays intentionally tiny and shared-substrate-first. It reuses the same
    equal-length backtick scan as :func:`md_inline_code_spans` so docs/help
    source view can give visible code-span delimiters a small cue without
    inventing another parser path.

    Returned spans cover only the opening/closing backtick delimiter runs, not
    the code body text itself.
    """

    out: list[tuple[int, int]] = []
    for open_a, open_b, _body_a, _body_b, close_a, close_b in _md_inline_code_parts(line):
        if int(open_b) > int(open_a):
            out.append((int(open_a), int(open_b)))
        if int(close_b) > int(close_a):
            out.append((int(close_a), int(close_b)))
    out.sort()
    return out


def md_inline_code_matches(line: str) -> list[MdCodeMatch]:
    """Return tiny docs/help inline-code matches for one source line.

    This keeps code-span inspection on the same tiny shared substrate as the
    existing precedence/style helpers: equal-length backtick delimiters only,
    no richer markdown AST, and just enough structured metadata for shared
    docs-cues snapshots and future UIs/LLMs.
    """

    s = str(line or "")
    if not s:
        return []
    out: list[MdCodeMatch] = []
    for open_a, open_b, body_a, body_b, close_a, close_b in _md_inline_code_parts(s):
        start = int(open_a)
        end = int(close_b)
        delimiter_length = max(0, int(open_b) - int(open_a))
        out.append(
            MdCodeMatch(
                kind='code',
                start=start,
                end=end,
                body_start=int(body_a),
                body_end=int(body_b),
                delimiter_length=int(delimiter_length),
                text=s[int(body_a):int(body_b)],
            )
        )
    return out


def md_raw_html_tag_matches(
    line: str,
    *,
    masked_spans: list[tuple[int, int]] | None = None,
) -> list[MdLiteralTokenMatch]:
    """Return tiny docs/help inline raw-HTML tag matches for one line.

    This reuses the same small shared raw-HTML helper the docs browser already
    trusts for precedence and dimming, but packages the visible tokens as
    structured matches so shared docs-cues snapshots and future UIs/LLMs do not
    need to rescan dim spans to learn what literal source is on screen.
    Supported autolinks stay out of this helper; they already flow through the
    ordinary shared link metadata path.
    """

    from micromax_editor.tui import md_raw_html_tag_token_spans

    s = str(line or "")
    if not s:
        return []
    out: list[MdLiteralTokenMatch] = []
    for a, b in md_raw_html_tag_token_spans(s, masked_spans=masked_spans):
        start = int(a)
        end = int(b)
        token = s[start:end]
        detail = ''
        m = re.match(r"</?\??([A-Za-z][A-Za-z0-9:-]*)", token)
        if m is not None:
            detail = str(m.group(1)).casefold()
        out.append(
            MdLiteralTokenMatch(
                kind='raw-html-tag',
                start=start,
                end=end,
                text=token,
                detail=detail,
            )
        )
    return out


def md_escaped_markdown_matches(
    line: str,
    *,
    masked_spans: list[tuple[int, int]] | None = None,
) -> list[MdLiteralTokenMatch]:
    r"""Return tiny docs/help escaped-markdown token matches for one line.

    This reuses the same tiny escape-pair helper the docs/help TUI already uses
    for dim source cues, but packages the visible escape pairs as structured
    matches so shared docs-cues snapshots can report which literal markdown
    punctuation was escaped on screen.
    """

    from micromax_editor.tui import md_escaped_markdown_token_spans

    s = str(line or "")
    if not s:
        return []
    out: list[MdLiteralTokenMatch] = []
    for a, b in md_escaped_markdown_token_spans(s, masked_spans=masked_spans):
        start = int(a)
        end = int(b)
        token = s[start:end]
        detail = token[1:] if len(token) >= 2 else ''
        out.append(
            MdLiteralTokenMatch(
                kind='escaped-markdown',
                start=start,
                end=end,
                text=token,
                detail=detail,
            )
        )
    return out


def md_inline_html_tag_spans(line: str, *, masked_spans: list[tuple[int, int]] | None = None) -> list[tuple[int, int]]:
    """Return tiny inline raw-HTML/autolink spans for one source line.

    The policy is intentionally small and precedence-oriented, not a full HTML
    tokenizer. It exists so docs/help link detection can avoid regex-shaped false
    positives in CommonMark-style cases where HTML tags or autolinks bind tighter
    than link grouping, e.g. ``[foo <bar attr="](baz)">``.

    Recognized forms:
      - autolinks: ``<https://...>`` / ``<mailto:...>``
      - permissive raw tags starting ``<tag ...>``, ``</tag>``, ``<?...>``

    Spans are ``(start, end)`` indices into ``line``. Callers may pass
    ``masked_spans`` (inline code, HTML comments, etc.) so already-inert regions
    stay inert here too.
    """

    s = str(line or "")
    if not s:
        return []

    masks = [(int(a), int(b)) for a, b in (masked_spans or [])]
    out: list[tuple[int, int]] = []
    i = 0
    n = len(s)
    while i < n:
        if s[i] != '<' or md_backslash_escaped(s, i) or md_span_contains(masks, i, i + 1):
            i += 1
            continue

        m = re.match(r"<(?P<url>(?:https?://|mailto:)[^ >]+)>", s[i:])
        if m is not None:
            end = i + int(m.end())
            if not md_span_contains(masks, i, end):
                out.append((i, end))
                i = end
                continue

        j = i + 1
        if j >= n:
            break

        ch = s[j]
        if ch == '/':
            j += 1
            if j >= n or not s[j].isalpha():
                i += 1
                continue
        elif ch == '?':
            pass
        elif not ch.isalpha():
            i += 1
            continue

        end = s.find('>', j + 1)
        if end < 0:
            i += 1
            continue
        end += 1
        if md_span_contains(masks, i, end):
            i += 1
            continue
        out.append((i, end))
        i = end

    return out


def md_html_type7_tag_line(line: str) -> bool:
    """Return True for a tiny complete-tag line suitable for type-7-ish blocks.

    This is intentionally conservative and inspectable. It recognizes lines that
    are *just* one complete open/close tag (optionally with attributes and up to
    three leading spaces), excluding the raw-block tags already handled by the
    tighter type-1 helper (``<pre>``, ``<script>``, ``<style>``,
    ``<textarea>``) and excluding comments/declarations/processing instructions.

    The goal is not full HTML validation; it is to catch the CommonMark/GFM-ish
    docs cases that matter to Micromax, such as ``<widget-box data-x="1">`` or
    ``</widget-box>`` lines that should keep subsequent literal markdown inert
    until a blank line.
    """

    s = str(line or "")
    if not s:
        return False
    if re.match(r"^[ ]{4,}", s):
        return False

    rest = re.sub(r"^[ ]{0,3}", "", s).rstrip()
    if len(rest) < 3 or rest[0] != '<' or rest[-1] != '>':
        return False
    if rest.startswith(('<!--', '<?', '<!')):
        return False

    i = 1
    closing = False
    if rest[1:2] == '/':
        closing = True
        i = 2

    if i >= len(rest) - 1 or not rest[i].isalpha():
        return False

    j = i + 1
    while j < len(rest):
        ch = rest[j]
        if ch.isalnum() or ch in {'-', ':'}:
            j += 1
            continue
        break

    name = rest[i:j].casefold()
    if not name or name in _MD_HTML_TYPE7_EXCLUDED:
        return False

    nxt = rest[j:j + 1]
    if nxt and (not nxt.isspace()) and nxt not in {'>', '/'}:
        return False

    if closing:
        return not rest[j:-1].strip()

    quote = ''
    k = j
    while k < len(rest):
        ch = rest[k]
        if quote:
            if ch == quote:
                quote = ''
            k += 1
            continue
        if ch in {'"', "'"}:
            quote = ch
            k += 1
            continue
        if ch == '<':
            return False
        if ch == '>':
            return k == len(rest) - 1
        k += 1
    return False


def md_html_block_line_flags(lines: list[object]) -> list[bool]:
    """Return zero-based per-line flags for tiny raw-HTML blocks.

    Policy is intentionally small and shared across docs/help surfaces. It aims
    at the CommonMark/GFM HTML block cases that matter for an editor-centric
    docs browser without becoming a full HTML parser:
      - type 1: ``<script|pre|style|textarea ...>`` through a matching end tag
      - type 3: processing instructions ``<? ... ?>``
      - type 4: declarations ``<!A...>`` through ``>``
      - type 5: CDATA ``<![CDATA[ ... ]]>``
      - type 6-ish: common block tags like ``<div>``/``<table>`` or closing
        forms like ``</div>`` through the next blank line
      - type 7-ish: complete generic tag-only lines like ``<widget-box>`` or
        ``</widget-box>`` through the next blank line, but only when they do
        not interrupt a paragraph

    HTML comments remain handled by :func:`md_html_comment_line_spans` so inline
    comment spans can coexist with visible prose on the same source line.
    """

    xs = [str(x) for x in (lines or [])]
    if not xs:
        return []

    flags: list[bool] = [False] * len(xs)
    mode = ""
    end_tag = ""

    for i, s in enumerate(xs):
        line = str(s)
        if mode == "blank":
            if not line.strip():
                mode = ""
                continue
            flags[i] = True
            continue

        if mode == "type1":
            flags[i] = True
            if re.search(rf"</{re.escape(end_tag)}(?=[\t />]|$)", line, flags=re.IGNORECASE):
                mode = ""
                end_tag = ""
            continue

        if mode == "type3":
            flags[i] = True
            if "?>" in line:
                mode = ""
            continue

        if mode == "type4":
            flags[i] = True
            if ">" in line:
                mode = ""
            continue

        if mode == "type5":
            flags[i] = True
            if "]]>" in line:
                mode = ""
            continue

        m1 = _MD_HTML_BLOCK_TYPE1_RE.match(line)
        if m1 is not None:
            flags[i] = True
            end_tag = str(m1.group('tag') or '').casefold()
            if end_tag and not re.search(rf"</{re.escape(end_tag)}(?=[\t />]|$)", line, flags=re.IGNORECASE):
                mode = "type1"
            else:
                end_tag = ""
            continue

        if _MD_HTML_BLOCK_TYPE3_RE.match(line):
            flags[i] = True
            if "?>" not in line:
                mode = "type3"
            continue

        if _MD_HTML_BLOCK_TYPE4_RE.match(line):
            flags[i] = True
            if ">" not in line:
                mode = "type4"
            continue

        if _MD_HTML_BLOCK_TYPE5_RE.match(line):
            flags[i] = True
            if "]]>" not in line:
                mode = "type5"
            continue

        if _MD_HTML_BLOCK_TYPE6_RE.match(line):
            flags[i] = True
            mode = "blank"
            continue

        prev_blank = i == 0 or not str(xs[i - 1]).strip()
        if prev_blank and md_html_type7_tag_line(line):
            flags[i] = True
            mode = "blank"
            continue

    return flags


def md_fenced_code_line_flags(lines: list[object]) -> list[bool]:
    """Return zero-based per-line flags for tiny fenced code blocks.

    Policy is intentionally small and shared across docs/help surfaces:
      - opening fence: up to 3 leading spaces, then ``` or ~~~ (3+ chars)
      - closing fence: same marker character, at least the opener length
      - lines inside the fence, including opener/closer, are flagged ``True``

    This is a precedence helper, not a full markdown block parser. It keeps
    fenced examples inert so markdown-looking text inside them stays prose for
    docs actions and TUI link underlining.
    """

    xs = [str(x) for x in (lines or [])]
    if not xs:
        return []

    flags: list[bool] = [False] * len(xs)
    in_fence = False
    fence_ch = ''
    fence_len = 0

    for i, s in enumerate(xs):
        if not in_fence:
            m = _FENCE_OPEN_RE.match(s)
            if m is None:
                continue
            fence = str(m.group('fence') or '')
            if not fence:
                continue
            in_fence = True
            fence_ch = fence[0]
            fence_len = len(fence)
            flags[i] = True
            continue

        flags[i] = True
        if re.match(rf"^[ ]{{0,3}}{re.escape(fence_ch)}{{{int(fence_len)},}}[ \t]*$", s):
            in_fence = False
            fence_ch = ''
            fence_len = 0

    return flags



def md_indented_code_line_flags(
    lines: list[object],
    *,
    fence_flags: list[bool] | None = None,
    html_block_flags: list[bool] | None = None,
) -> list[bool]:
    """Return zero-based flags for tiny blank-separated indented code-ish runs.

    This helper is intentionally smaller than full CommonMark. It only covers
    the blank-separated top-level shape that shows up in Micromax's docs/help
    source view:
      - a run begins at start-of-file or after a blank line
      - the first non-blank line begins with 4+ spaces or a tab
      - the run continues across blank lines and later 4+-space/tab lines
      - fenced/raw-HTML lines are never claimed here

    The goal is shared precedence for docs/help surfaces so obvious source-view
    code examples stay code-ish for helpfollow/helplinkpick/TUI rendering
    without committing the editor to a fuller markdown block parser.
    """

    xs = [str(x) for x in (lines or [])]
    if not xs:
        return []

    fence_flags = list(fence_flags or [])
    html_block_flags = list(html_block_flags or [])
    flags: list[bool] = [False] * len(xs)
    in_code = False

    def _is_inert_elsewhere(idx: int) -> bool:
        return bool((idx < len(fence_flags) and fence_flags[idx]) or (idx < len(html_block_flags) and html_block_flags[idx]))

    def _is_indented_codeish(s: str) -> bool:
        return s.startswith("\t") or bool(re.match(r"^ {4,}", s))

    for i, s in enumerate(xs):
        if _is_inert_elsewhere(i):
            in_code = False
            continue
        if in_code:
            if not s.strip():
                keep_blank = False
                j = int(i) + 1
                while j < len(xs):
                    if _is_inert_elsewhere(j):
                        break
                    sj = str(xs[j])
                    if not sj.strip():
                        j += 1
                        continue
                    if _is_indented_codeish(sj):
                        keep_blank = True
                    break
                if keep_blank:
                    flags[i] = True
                    continue
                in_code = False
            elif _is_indented_codeish(s):
                flags[i] = True
                continue
            else:
                in_code = False
        prev_blank = i == 0 or not str(xs[i - 1]).strip()
        if prev_blank and _is_indented_codeish(s):
            flags[i] = True
            in_code = True

    return flags



def _ellipsize_right(text: str, width: int) -> str:
    """Return *text* clipped to *width* with an end ellipsis when needed."""

    s = str(text or "")
    w = max(0, int(width))
    if w <= 0:
        return ""
    if len(s) <= w:
        return s
    if w == 1:
        return s[:1]
    return s[: max(0, w - 1)] + "…"


def _ellipsize_left(text: str, width: int) -> str:
    """Return *text* clipped to *width* with a leading ellipsis when needed."""

    s = str(text or "")
    w = max(0, int(width))
    if w <= 0:
        return ""
    if len(s) <= w:
        return s
    if w == 1:
        return s[-1:]
    return "…" + s[-max(0, w - 1):]


def _fit_left_right_text(left: str, right: str, width: int, *, sep: str = " ") -> str:
    """Fit left/right prompt text into *width* while preserving right detail.

    This is used by picker rows where the leading label is usually the primary
    thing to scan, but the trailing detail often carries the distinguishing path,
    location, or mode. When truncation is needed we keep as much of the right
    detail as possible, using an ellipsis on the left side rather than simply
    chopping the whole combined string at the end.
    """

    w = max(0, int(width))
    if w <= 0:
        return ""

    left_s = str(left or "")
    right_s = str(right or "")
    if not right_s:
        return _ellipsize_right(left_s, w)
    if not left_s:
        return _ellipsize_left(right_s, w)

    right_block = f"{sep}{right_s}"
    full = left_s + right_block
    if len(full) <= w:
        return full
    if len(right_block) >= w:
        return _ellipsize_left(right_block, w)

    avail_left = max(0, w - len(right_block))
    return (_ellipsize_right(left_s, avail_left) + right_block)[:w]


def md_span_contains(spans: list[tuple[int, int]], a: int, b: int) -> bool:
    """Return True when ``[a,b)`` is fully covered by one span in ``spans``."""

    aa = int(a)
    bb = int(b)
    return any(int(sa) <= aa and bb <= int(sb) for sa, sb in spans)


@dataclass(frozen=True)
class MdLinkMatch:
    """Tiny docs/help markdown link match used by editor actions and the TUI."""

    kind: str
    start: int
    end: int
    label_start: int
    label_end: int
    display: str
    target: str


@dataclass(frozen=True)
class MdImageMatch:
    """Tiny docs/help markdown image match used by docs-cues snapshots."""

    kind: str
    start: int
    end: int
    alt_start: int
    alt_end: int
    alt_text: str
    target: str


@dataclass(frozen=True)
class MdCodeMatch:
    """Tiny docs/help inline-code match used by docs-cues snapshots."""

    kind: str
    start: int
    end: int
    body_start: int
    body_end: int
    delimiter_length: int
    text: str


@dataclass(frozen=True)
class MdLiteralTokenMatch:
    """Tiny docs/help literal-source token used by docs-cues snapshots."""

    kind: str
    start: int
    end: int
    text: str
    detail: str


def md_help_link_target_info(target: str) -> dict[str, str]:
    """Return a tiny classification snapshot for one docs/help link target.

    The editor already follows a small set of target shapes in help buffers:
    same-page fragments, cross-doc fragments, docs topics / relative file paths,
    and external ``http(s)`` / ``mailto:`` URLs. Exposing the same tiny
    classification keeps future UIs/scripts/LLMs from rediscovering that logic
    by scraping raw targets.
    """

    t = str(target or "").strip().strip('"').strip("'")
    out = {
        "target": t,
        "target_kind": "",
        "doc": "",
        "fragment": "",
    }
    if not t:
        return out

    low = t.casefold()
    if low.startswith("http://") or low.startswith("https://"):
        out["target_kind"] = "external"
        return out
    if low.startswith("mailto:"):
        out["target_kind"] = "mailto"
        return out

    doc_part, hash_mark, frag_part = t.partition("#")
    frag = unquote(str(frag_part or "").strip()) if hash_mark else ""
    if hash_mark and not doc_part.strip():
        out["fragment"] = frag
        out["target_kind"] = "footnote" if frag.startswith("^") else "fragment"
        return out

    doc = unquote(str(doc_part or t).strip())
    out["doc"] = doc
    out["fragment"] = frag
    looks_like_path = doc.endswith('.md') or ('/' in doc) or ('\\' in doc)
    if hash_mark:
        out["target_kind"] = "file-fragment" if looks_like_path else "doc-fragment"
    else:
        out["target_kind"] = "file" if looks_like_path else "doc"
    return out


def md_help_link_source_kind(line: str, start: int, end: int, kind: str) -> str:
    """Return a tiny source-form classification for one visible docs/help link.

    ``docs_cues_model(...)`` already exposes what a visible link points to, but
    future UIs/scripts/LLMs sometimes also want to know *how* the source spelled
    that link: inline destination, autolink, footnote reference, or a
    reference-style link resolved through definitions elsewhere in the doc.

    The classifier intentionally stays tiny and source-view-oriented rather than
    promoting a fuller markdown AST.
    """

    k = str(kind or "")
    if k == "autolink":
        return "autolink"
    if k == "footnote":
        return "footnote"
    if k != "link":
        return ""

    s = str(line or "")
    a = max(0, int(start))
    b = max(a, int(end))
    frag = s[a:b]
    if not frag.startswith('['):
        return ""
    label_span = md_balanced_span(frag, 0, opener='[', closer=']')
    if label_span is None:
        return ""
    _, lb = label_span
    after = frag[lb:lb + 1]
    if after == '(':
        return "inline"
    if after == '[' or after == '':
        return "reference"
    return ""


def md_help_image_source_kind(line: str, start: int, end: int, kind: str) -> str:
    """Return a tiny source-form classification for one visible docs/help image.

    ``docs_cues_model(...)`` already exposes what a visible image points to, but
    future UIs/scripts/LLMs sometimes also want to know *how* the source spelled
    that image: inline destination or reference-style image syntax resolved
    through definitions elsewhere in the doc.

    The classifier intentionally stays tiny and source-view-oriented rather than
    promoting a fuller markdown AST.
    """

    if str(kind or "") != "image":
        return ""

    s = str(line or "")
    a = max(0, int(start))
    b = max(a, int(end))
    frag = s[a:b]
    if not frag.startswith('!['):
        return ""
    label_span = md_balanced_span(frag, 1, opener='[', closer=']')
    if label_span is None:
        return ""
    _, lb = label_span
    after = frag[lb:lb + 1]
    if after == '(':
        return "inline"
    if after == '[' or after == '':
        return "reference"
    return ""


def md_help_link_reference_form(line: str, start: int, end: int, kind: str) -> str:
    """Return ``full`` / ``collapsed`` / ``shortcut`` for reference-style links.

    ``docs_cues_model(...)`` already exposes link targets and coarse source
    kinds. Future UIs/scripts/LLMs sometimes also need the exact CommonMark-ish
    reference spelling the visible source used without reparsing the row:
    ``[label][id]`` (full), ``[label][]`` (collapsed), or ``[id]`` (shortcut).

    The classifier stays intentionally tiny and source-view-oriented rather than
    promoting a fuller markdown AST.
    """

    if md_help_link_source_kind(line, start, end, kind) != "reference":
        return ""

    s = str(line or "")
    a = max(0, int(start))
    b = max(a, int(end))
    frag = s[a:b]
    if not frag.startswith('['):
        return ""
    label_span = md_balanced_span(frag, 0, opener='[', closer=']')
    if label_span is None:
        return ""
    _, lb = label_span
    after = frag[lb:lb + 1]
    if after == '[':
        ref_span = md_balanced_span(frag, lb, opener='[', closer=']')
        if ref_span is None:
            return ""
        rs, re = ref_span
        return "collapsed" if frag[rs + 1:re - 1] == '' else "full"
    if after == '':
        return "shortcut"
    return ""


def md_help_image_reference_form(line: str, start: int, end: int, kind: str) -> str:
    """Return ``full`` / ``collapsed`` / ``shortcut`` for reference-style images.

    This mirrors :func:`md_help_link_reference_form` for visible docs/help image
    source. It keeps reference-style images inspectable as tiny source-view
    facts without promoting a fuller markdown AST.
    """

    if md_help_image_source_kind(line, start, end, kind) != "reference":
        return ""

    s = str(line or "")
    a = max(0, int(start))
    b = max(a, int(end))
    frag = s[a:b]
    if not frag.startswith('!['):
        return ""
    label_span = md_balanced_span(frag, 1, opener='[', closer=']')
    if label_span is None:
        return ""
    _, lb = label_span
    after = frag[lb:lb + 1]
    if after == '[':
        ref_span = md_balanced_span(frag, lb, opener='[', closer=']')
        if ref_span is None:
            return ""
        rs, re = ref_span
        return "collapsed" if frag[rs + 1:re - 1] == '' else "full"
    if after == '':
        return "shortcut"
    return ""


def md_inline_markup_delimiter_kind(delimiter: str) -> str:
    """Return a tiny source-delimiter family for inline markup tokens.

    ``docs_cues_model(...)`` already exposes inline-markup kinds like strong,
    emphasis, and strike. Future UIs/scripts/LLMs sometimes also want the
    literal delimiter family used by the visible source without re-filtering the
    raw ``delimiter`` field: asterisk-based emphasis, underscore-based
    emphasis, or tilde-based strikethrough.

    The classifier intentionally stays tiny and source-view-oriented rather than
    promoting a fuller markdown AST.
    """

    frag = str(delimiter or "")
    if not frag:
        return ""
    lead = frag[:1]
    if lead == '*':
        return 'asterisk'
    if lead == '_':
        return 'underscore'
    if lead == '~':
        return 'tilde'
    return ''


def md_fenced_code_marker_kind(marker: str) -> str:
    """Return a tiny marker family for fenced-code rows.

    CommonMark/GFM fenced blocks are source-spelled with either backticks or
    tildes. ``docs_cues_model(...)`` already exposes tiny fence details like the
    raw marker text and info string on opener rows; this helper promotes the
    common "which fence family is this block using?" question into a stable tiny
    classifier so future UIs/scripts/LLMs do not have to re-interpret the raw
    one-character ``marker`` field every time.
    """

    frag = str(marker or '')
    if frag == '`':
        return 'backtick'
    if frag == '~':
        return 'tilde'
    return ''


def md_balanced_span(s: str, open_idx: int, *, opener: str, closer: str) -> tuple[int, int] | None:
    """Return ``(start, end)`` for a tiny balanced-delimiter span, or ``None``.

    This helper is intentionally small but covers the docs-browser cases regexes
    handle poorly: nested bracket labels like ``[Vision [nested]]`` and inline
    destinations with nested parentheses like ``(topic(one).md)``.
    """

    text = str(s or '')
    i0 = int(open_idx)
    if i0 < 0 or i0 >= len(text) or text[i0] != opener:
        return None

    depth = 0
    i = i0
    while i < len(text):
        ch = text[i]
        if ch == "\\":
            i += 2
            continue
        if ch == opener:
            depth += 1
        elif ch == closer:
            depth -= 1
            if depth == 0:
                return (i0, i + 1)
        i += 1
    return None


def md_label_contains_nested_links(
    label_src: str,
    defs: dict[str, str],
    footdefs: dict[str, tuple[int, int]] | None = None,
) -> bool:
    """Return True when *label_src* contains a valid nested markdown link.

    CommonMark allows balanced brackets inside link text, but valid links may
    not contain other links at any level of nesting. The tiny docs browser keeps
    this rule intentionally small and shared by recursively scanning the label
    contents with the same link matcher and rejecting the outer link when an
    inner *link* match exists.

    Images remain allowed inside link labels because ``md_link_matches`` already
    ignores image syntax, mirroring CommonMark's ``[![moon](img)](/uri)`` case.
    """

    inner = str(label_src or '')
    if not inner or '[' not in inner:
        return False
    for match in md_link_matches(inner, defs, footdefs):
        if str(match.kind) == 'link':
            return True
    return False


def md_link_matches(
    line: str,
    defs: dict[str, str],
    footdefs: dict[str, tuple[int, int]] | None = None,
    masked_spans: list[tuple[int, int]] | None = None,
    next_line: str = "",
    next_next_line: str = "",
) -> list[MdLinkMatch]:
    """Return tiny docs/help markdown link matches for one source line.

    Policy intentionally mirrors the editor's help-browser actions and the tiny
    TUI underline model while staying much smaller than a full markdown parser.
    """

    s = str(line or '')
    if not s:
        return []

    footdefs = dict(footdefs or {})
    code_spans = md_inline_code_spans(s)
    mask_spans = list(code_spans)
    if masked_spans:
        mask_spans.extend((int(a), int(b)) for a, b in masked_spans)
    html_spans = md_inline_html_tag_spans(s, masked_spans=mask_spans)
    out: list[MdLinkMatch] = []
    i = 0
    while i < len(s):
        ch = s[i]

        if ch == '<':
            if md_backslash_escaped(s, i) or md_span_contains(mask_spans, i, i + 1):
                i += 1
                continue
            m = re.match(r"<(?P<url>(?:https?://|mailto:)[^ >]+)>", s[i:])
            if m is not None:
                url = str(m.group('url') or '').strip()
                if url:
                    a = i + int(m.start())
                    b = i + int(m.end())
                    ua = i + int(m.start('url'))
                    ub = i + int(m.end('url'))
                    out.append(MdLinkMatch('autolink', a, b, ua, ub, url, url))
                    i = b
                    continue

        if ch != '[':
            i += 1
            continue
        if md_backslash_escaped(s, i) or md_span_contains(mask_spans, i, i + 1):
            i += 1
            continue
        # Treat the second opener of [label][id] as part of the same construct,
        # not as a standalone shortcut ref, even if the first opener stayed prose.
        if i > 0 and s[i - 1] == ']':
            i += 1
            continue

        label_span = md_balanced_span(s, i, opener='[', closer=']')
        if label_span is None:
            i += 1
            continue
        a, b = label_span
        if md_span_contains(mask_spans, a, b):
            i = max(i + 1, b)
            continue
        if a > 0 and s[a - 1] == '!':
            i = b
            continue

        if any(int(sa) < b and a < int(sb) for sa, sb in html_spans):
            i = b
            continue

        label = s[a + 1:b - 1]
        if not md_link_label_has_text(label):
            i = b
            continue
        if md_label_contains_nested_links(label, defs, footdefs):
            i += 1
            continue
        after = s[b:b+1]

        if after == '(':
            inner_span = md_balanced_span(s, b, opener='(', closer=')')
            if inner_span is not None:
                _, d = inner_span
                if not md_span_contains(mask_spans, a, d):
                    target = md_inline_link_target(s[b + 1:d - 1])
                    if target:
                        out.append(MdLinkMatch('link', a, d, a + 1, b - 1, label, target))
                        i = d
                        continue
            target = md_inline_link_target_multiline(s[b + 1 :], next_line, next_next_line)
            if target:
                out.append(MdLinkMatch('link', a, len(s), a + 1, b - 1, label, target))
                i = len(s)
                continue

        if after == '[':
            id_span = md_balanced_span(s, b, opener='[', closer=']')
            if id_span is not None:
                _, d = id_span
                if not md_span_contains(mask_spans, a, d):
                    rid = s[b + 1:d - 1].strip() or label.strip()
                    target = defs.get(md_norm_ref_id(rid))
                    if target:
                        out.append(MdLinkMatch('link', a, d, a + 1, b - 1, label, target))
                        i = d
                        continue

        if label.startswith('^') and after != ':':
            rid = label[1:].strip()
            if rid and footdefs.get(md_norm_ref_id(rid)) is not None:
                out.append(MdLinkMatch('footnote', a, b, a + 1, b - 1, f"[^{rid}]", f"#^{rid}"))
                i = b
                continue

        if after != ':':
            rid = label.strip()
            target = defs.get(md_norm_ref_id(rid)) if rid else None
            if target:
                out.append(MdLinkMatch('link', a, b, a + 1, b - 1, rid, target))
                i = b
                continue

        i += 1

    return out


def md_image_matches(
    line: str,
    defs: dict[str, str],
    *,
    masked_spans: list[tuple[int, int]] | None = None,
    next_line: str = "",
    next_next_line: str = "",
) -> list[MdImageMatch]:
    """Return tiny docs/help markdown image matches for one source line.

    This intentionally stays smaller than a fuller markdown AST. It mirrors the
    supported inline/reference/shortcut image forms the docs/help TUI already
    dims, so shared docs-cues snapshots can report visible image targets
    without adding another parser path.
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

    out: list[MdImageMatch] = []
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

        alt_text = s[la + 1 : lb - 1]
        after = s[lb:lb + 1]

        if after == '(':
            inner_span = md_balanced_span(s, lb, opener='(', closer=')')
            if inner_span is not None:
                _, end = inner_span
                if not _covered(i, end):
                    target = md_inline_link_target(s[lb + 1 : end - 1])
                    if target:
                        out.append(MdImageMatch('image', i, end, la + 1, lb - 1, alt_text, target))
                        i = end
                        continue
            target = md_inline_link_target_multiline(s[lb + 1 :], next_line, next_next_line)
            if target:
                out.append(MdImageMatch('image', i, len(s), la + 1, lb - 1, alt_text, target))
                i = len(s)
                continue

        if after == '[':
            id_span = md_balanced_span(s, lb, opener='[', closer=']')
            if id_span is not None:
                _, end = id_span
                if not _covered(i, end):
                    rid = s[lb + 1 : end - 1].strip() or alt_text.strip()
                    target = defs.get(md_norm_ref_id(rid))
                    if target:
                        out.append(MdImageMatch('image', i, end, la + 1, lb - 1, alt_text, target))
                        i = end
                        continue

        if after != ':':
            rid = alt_text.strip()
            target = defs.get(md_norm_ref_id(rid)) if rid else None
            if target:
                out.append(MdImageMatch('image', i, lb, la + 1, lb - 1, alt_text, target))
                i = lb
                continue

        i += 1

    return out


def md_strip_inline_markup(s: str) -> str:
    """Best-effort markdown-inline text cleanup for heading anchors/titles.

    This is intentionally tiny rather than CommonMark-complete. It removes the
    most common formatting wrappers so heading slugs and picker labels behave
    more like rendered markdown, not raw source.
    """

    out = str(s or "")
    if not out:
        return ""

    # Images/links/reference links/autolinks -> visible label text.
    out = re.sub(r"!\[(?P<label>[^\]]*)\]\((?P<inner>[^)]*)\)", lambda m: str(m.group("label") or ""), out)
    out = re.sub(r"\[(?P<label>[^\]]+)\]\((?P<inner>[^)]*)\)", lambda m: str(m.group("label") or ""), out)
    out = re.sub(r"\[(?P<label>[^\]]+)\]\[(?P<id>[^\]]*)\]", lambda m: str(m.group("label") or ""), out)
    out = re.sub(r"<(?P<url>(?:https?://|mailto:)[^ >]+)>", lambda m: str(m.group("url") or ""), out)

    # Inline code/emphasis/strikethrough markers -> contents.
    out = re.sub(r"`([^`]*)`", lambda m: str(m.group(1) or ""), out)
    out = re.sub(r"\*\*([^*]+)\*\*", lambda m: str(m.group(1) or ""), out)
    out = re.sub(r"__([^_]+)__", lambda m: str(m.group(1) or ""), out)
    out = re.sub(r"\*([^*]+)\*", lambda m: str(m.group(1) or ""), out)
    out = re.sub(r"_([^_]+)_", lambda m: str(m.group(1) or ""), out)
    out = re.sub(r"~~([^~]+)~~", lambda m: str(m.group(1) or ""), out)

    # Drop residual markdown-y punctuation/HTML tags conservatively.
    out = re.sub(r"<[^>]+>", "", out)
    out = out.replace("[", "").replace("]", "")
    out = out.replace("(", "").replace(")", "")
    return re.sub(r"\s+", " ", out).strip()


def md_heading_auto_id(title: str, *, seen: dict[str, int] | None = None) -> str:
    """Best-effort GitHub-style heading slug for docs fragments.

    Rules kept intentionally small:
      - remove common markdown inline markup
      - lowercase
      - replace whitespace runs with ``-``
      - drop most punctuation
      - preserve unicode letters/digits
      - de-duplicate with ``-1``, ``-2``, ... when ``seen`` is provided
    """

    clean = md_strip_inline_markup(title).strip().lower()
    parts: list[str] = []
    prev_dash = False
    for ch in clean:
        if ch.isalnum():
            parts.append(ch)
            prev_dash = False
            continue
        if ch.isspace() or ch == "-":
            if parts and not prev_dash:
                parts.append("-")
                prev_dash = True
            continue
        # Drop other punctuation/markup characters.
    slug = "".join(parts).strip("-") or "section"
    if seen is None:
        return slug
    n = int(seen.get(slug, 0))
    seen[slug] = n + 1
    if n <= 0:
        return slug
    return f"{slug}-{n}"



@dataclass
class EditorBuffer:
    name: str
    buf: Buffer
    cursors: list[Cursor]
    sel_anchors: list[Cursor | None]
    cursor_ids: list[int]
    # Index into `cursors`/`sel_anchors` designating the *primary* cursor.
    # Cursor lists remain in document order.
    primary: int
    local_options: dict[str, Any]

    # Per-cursor "goal" x (visual column) used for softwrap-aware vertical motion.
    goal_x_by_cursor: dict[int, int] = field(default_factory=dict)

    # A small stack used to recover from accidental selection/cursor clears.
    # This is intentionally *not* part of undo history (it's closer to a register).
    sel_stack: list[tuple[list[Cursor], list[Cursor | None], list[int], int]] = field(default_factory=list)

    # A tiny "jumplist" for navigation (Vim/Helix-style).
    # - push current cursor/selection state
    # - jump back/forward through the list
    #
    # This is intentionally *not* undo: it captures *where you were*, not edits.
    jump_list: list[tuple[list[Cursor], list[Cursor | None], list[int], int]] = field(default_factory=list)
    jump_index: int = -1

    # Best-effort autosave scheduling state.
    # None means either the buffer is clean or autosave is not currently armed.
    autosave_dirty_since: float | None = None


@dataclass(frozen=True)
class MacroStep:
    kind: str  # 'action' | 'command'
    name: str
    payload: dict[str, Any]


@dataclass(frozen=True)
class ActiveKeyMode:
    name: str
    once: bool = False
    # If true, this mode *captures* all keys: unbound keys do not fall through
    # to lower-precedence modes/global bindings.
    #
    # This is useful for modal interactions like query-replace confirmation
    # prompts (y/n/a/q) where accidental global bindings would be surprising.
    capture: bool = False


@dataclass
class QueryReplaceSession:
    """State for an interactive, micro/Emacs-style "query replace" loop."""

    buffer_name: str
    search: str
    value: str
    literal: bool

    # Match semantics (mirrors search): case-insensitive when ignorecase is enabled.
    case_sensitive: bool = True

    # Best-effort count of remaining matches from the session start (for UX).
    total: int = 0

    # Precompiled regex and replacement template for regex mode.
    regex: re.Pattern[str] | None = None
    repl_py: str = ""

    # Search continuation point.
    next_start: Cursor = field(default_factory=lambda: Cursor(0, 0))

    # Current match span and the concrete replacement text for this match.
    match_start: Cursor | None = None
    match_end: Cursor | None = None
    match_repl: str = ""

    # Undo snapshot at session start (recorded as one undo entry on finish).
    before: tuple[str, list[Cursor], list[Cursor | None], list[int], int] | None = None

    replaced: int = 0
    examined: int = 0


class Editor:
    """Headless editor core.

    Design priorities:
      - **unit-testable** core (no terminal dependencies)
      - micro-esque UX primitives (command bar, action chains, incsearch, macros)
      - micromax embedded as the plugin/macro language

    This is intentionally not a full TUI yet. The goal is to keep core logic
    highly testable while we steadily steal the best "goodies" from micro.
    """

    def __init__(self) -> None:
        # Monotonic ids for cursors so we can implement "remove latest cursor"
        # semantics while still keeping the cursor list in document order.
        self._next_cursor_id: int = 1

        self.buffers: dict[str, EditorBuffer] = {}
        self.active: str | None = None

        # Buffer MRU: tracks recently-active buffers for prev-buffer behavior.
        self._buffer_mru: list[str] = []

        self.keymap = Keymap()
        self._install_builtin_keymode_bindings()
        self.actions = ActionRegistry()
        # Back-compat alias
        self.commands = self.actions

        self.undo = UndoManager()

        self.options = Options()
        self._install_default_options()

        self.command_dispatcher = CommandDispatcher()
        install_default_commands(self)

        self.search = SearchState(query="", literal=True, case_sensitive=False)

        # Interactive query-replace session (qreplace/queryreplace).
        self.qreplace: QueryReplaceSession | None = None
        self.prompt: Prompt | None = None

        self.messages: list[str] = []
        self.should_quit: bool = False

        # Script context depth (non-zero when called from micromax hostcalls).
        # Used to enforce capability gates on powerful editor commands.
        self._script_depth: int = 0

        # Double-tap quit guard: when dirty buffers exist, `quit` arms once
        # (prints a warning) and only quits on a second attempt or with -f/!.
        self._quit_armed: bool = False

        # Double-tap close-buffer guard: mirrors quit semantics, but scoped to the
        # `close` command so users don't accidentally discard a dirty buffer.
        self._close_armed: bool = False
        self._close_armed_name: str = ""


        # Double-tap bulk-close guards (closeall/only).
        self._closeall_armed: bool = False
        self._only_armed: bool = False

        # Clipboard is stored as a *list* of items.
        # - Most copy operations produce a single item.
        # - Multi-cursor copy/cut can produce one item per cursor.
        self.clipboard_items: list[str] = []
        self.clipboard_kind: str = "items"  # items|lines
        self._cutline_accum: bool = False

        # Clipboard change tracking (used by UI layers for external backends).
        # - serial increments on every clipboard mutation
        # - from_script is true when the change happened inside script_context()
        self.clipboard_serial: int = 0
        self.clipboard_from_script: bool = False

        # Prompt history (command + find).
        self.history: dict[str, list[str]] = {"command": [], "find": []}

        # Search-first command palette MRU, scoped to actual palette selections
        # rather than all editor actions. This keeps the palette helpful without
        # letting high-frequency movement actions dominate it.
        self._palette_recent: list[tuple[str, str]] = []
        self._palette_recent_limit: int = 12

        # Recent files MRU (fast file switching / command palette companion).
        # Entries are absolute-ish paths as strings (best-effort normalized).
        self.recent_files: list[str] = []
        self._recent_limit: int = 20

        # Saved primary-cursor positions keyed by normalized file path.
        # This is best-effort and only persisted when `savecursor` +
        # `cap.persist` are enabled.
        self._saved_cursors: dict[str, dict[str, int]] = {}

        # Help/docs navigation stack (for docs-backed help buffers).
        # Stores docs topics (slugs) so users can `helpback` after `helpfollow`.
        self._help_stack: list[str] = []
        self._help_stack_limit: int = 40

        # Help/docs heading caches (best-effort).
        # Used for docs-link section labeling when `help.linksections=heading`
        # and for grouped help-outline picker section labels.
        self._help_heading_cache_topic: str = ""
        self._help_heading_cache_nlines: int = 0
        self._help_heading_cache: list[tuple[int, str]] = []
        self._help_heading_fragment_cache_topic: str = ""
        self._help_heading_fragment_cache_nlines: int = 0
        self._help_heading_fragment_cache: dict[int, str] = {}
        self._help_outline_section_cache_topic: str = ""
        self._help_outline_section_cache_nlines: int = 0
        self._help_outline_section_cache: dict[int, str] = {}
        self._help_heading_title_cache_topic: str = ""
        self._help_heading_title_cache_nlines: int = 0
        self._help_heading_title_cache: dict[str, str] = {}
        self._docs_catalog_cache: dict[str, dict[str, str]] = {}
        self._docs_heading_title_cache: dict[str, dict[str, str]] = {}

        # External URL opener (capability-gated). Tests can override this.
        self._open_url_fn = webbrowser.open

        # Pending external URL open confirmation (docs browser safety).
        self._pending_open_url: str | None = None
        self._pending_open_url_source: str = ""

        # Embedded micromax VM.
        self.vm = VM()
        self._install_default_actions()

        # Editor -> micromax event hooks (non-authoritative; notifications only).
        # Plugins can `hook-add` handlers to these.
        try:
            self.vm.eval(
                "hook ed.pre-action hook ed.on-action "
                "hook ed.on-open hook ed.on-save hook ed.on-change",
                filename="<editor>",
            )
        except Exception:
            pass

        # Keep VM feature advertisement aligned with capability options.
        # Optional hostcalls may be installed later by the UI/bridge.
        try:
            self.refresh_capabilities()
        except Exception:
            pass

        # optional: set externally
        self.plugin_manager: Any = None

        # Deterministic timer queue (for plugins: debounce/autosave).
        # Tests can override _now_fn to avoid real time.
        self._now_fn = time.monotonic
        self.timers = TimerQueue()

        # scratch input for actions/commands
        self.input: dict[str, Any] = {}

        # Macro recording (micro-style "record/play last macro", extended with named macros)
        self.macro_recording: bool = False
        self._macro_buffer: list[MacroStep] = []
        self._macro_target: str = "last"
        self._macro_prev_last: list[MacroStep] | None = None
        self._macro_playing: bool = False

        # Stored macros (name -> steps). "last" is the default.
        self.macro: list[MacroStep] = []
        self.macros: dict[str, list[MacroStep]] = {"last": self.macro}

        # Multi-cursor selection search state (for Alt-n / Alt-x style workflows)
        self._mc_last_match_start: Cursor | None = None

        # Optional keymap mode stack.
        #
        # This is intentionally smaller than a full modal editor architecture:
        # the active stack only affects keybinding lookup order. Global bindings
        # always remain as the final fallback.
        #
        # Modes can be persistent or one-shot. One-shot (transient) modes are
        # inspired by Helix minor modes, Kakoune's next-key layers, and Emacs'
        # transient maps: they get first crack at the next key, then pop.
        self.key_mode_stack: list[ActiveKeyMode] = []

        # Named marks (portable, headless navigation points).
        # Stored as: name -> (buffer_name, Cursor).
        self.marks: dict[str, tuple[str, Cursor]] = {}

        # Viewport state (headless-friendly scrolling model).
        # A UI should keep this updated via `ed.viewport!`.
        self.viewport_top_line: int = 0
        # When softwrap is enabled, the viewport may begin partway through a long
        # logical line. This is the wrap-row index (0-based) within top_line.
        self.viewport_top_subline: int = 0
        self.viewport_left_col: int = 0
        self.viewport_height: int = 0
        self.viewport_width: int = 0

    # ----- messaging -----
    def message(self, s: str) -> None:
        self.messages.append(str(s))



    # ----- script context -----
    @contextmanager
    def script_context(self):
        """Context manager marking operations as originating from scripts/plugins.

        The headless editor is the "host world." Some commands (open/save, etc.)
        provide filesystem authority. We want interactive users to keep the usual
        editor UX while allowing hosts to run scripts with **no ambient authority**
        unless a capability is explicitly enabled.

        Hostcalls that can execute editor commands or submit prompts should wrap
        their work in this context so command implementations can enforce
        capability gates for *script-originated* requests.
        """

        self._script_depth += 1
        try:
            yield
        finally:
            self._script_depth = max(0, int(self._script_depth) - 1)

    def in_script_context(self) -> bool:
        """True when the current call stack originated from a script hostcall."""

        return bool(int(self._script_depth) > 0)

    # ----- prompt completion matching -----

    def _completion_fuzzy_positions(self, candidate: str, query: str) -> list[int] | None:
        """Return subsequence match positions for query in candidate, or None.

        This is intentionally tiny and deterministic: it is *not* trying to be a
        full fzf clone. We only need a predictable fallback when exact-prefix
        completion finds nothing.
        """
        q = str(query or "").casefold()
        c = str(candidate).casefold()
        if q == "":
            return []

        out: list[int] = []
        start = 0
        for ch in q:
            pos = c.find(ch, start)
            if pos < 0:
                return None
            out.append(pos)
            start = pos + 1
        return out

    def _completion_fuzzy_sort_key(self, candidate: str, query: str) -> tuple[int, int, int, int, int, int, str] | None:
        """Return a deterministic sort key for fuzzy completion candidates.

        Lower is better. We prefer:
        - contiguous substring hits over plain subsequence hits
        - earlier matches
        - tighter spans
        - more consecutive / boundary-aligned characters
        - shorter candidates
        """
        positions = self._completion_fuzzy_positions(candidate, query)
        if positions is None:
            return None

        folded_candidate = str(candidate).casefold()
        folded_query = str(query or "").casefold()
        substring_at = folded_candidate.find(folded_query) if folded_query else 0

        consecutive = 0
        boundary = 0
        for idx, pos in enumerate(positions):
            if idx > 0 and pos == (positions[idx - 1] + 1):
                consecutive += 1

            if pos == 0:
                boundary += 1
            else:
                prev = candidate[pos - 1]
                cur = candidate[pos]
                if prev in "-_/.: " or (prev.islower() and cur.isupper()):
                    boundary += 1

        start = positions[0] if positions else 0
        span = (positions[-1] - positions[0]) if positions else 0
        return (
            0 if substring_at >= 0 else 1,
            substring_at if substring_at >= 0 else start,
            start,
            span,
            -consecutive,
            -boundary,
            len(candidate),
            str(candidate),
        )

    def _completion_candidates_for_prefix(
        self,
        names: list[str],
        prefix: str,
        *,
        at_eol: bool,
    ) -> tuple[list[str], bool]:
        """Return built-in completion candidates and whether fuzzy fallback was used.

        Policy:
        - exact prefix matches win when present
        - otherwise, fall back to a tiny subsequence matcher for command-ish names
        - path completion stays on its own explicit prefix-based path
        """
        raw_names = sorted({str(n) for n in names})
        exact = [n for n in raw_names if n.startswith(prefix)]
        fuzzy = False

        if exact:
            chosen = exact
        elif prefix != "":
            scored: list[tuple[tuple[int, int, int, int, int, int, str], str]] = []
            for n in raw_names:
                key = self._completion_fuzzy_sort_key(n, prefix)
                if key is not None:
                    scored.append((key, n))
            scored.sort(key=lambda item: item[0])
            chosen = [n for _key, n in scored]
            fuzzy = bool(chosen)
        else:
            chosen = []

        if at_eol:
            chosen = [n + " " for n in chosen]
        return (chosen, fuzzy)

    def _prompt_known_keymodes(self) -> list[str]:
        names = set(self.keymap.modes())
        names.update(str(m) for m in self.active_key_modes())
        return sorted(str(n) for n in names if str(n))

    def _prompt_hook_names(self) -> list[str]:
        from micromax.vm import HookWord

        names: set[str] = set()
        for wl in self.vm.wordlists.values():
            for name, word in wl.items():
                if isinstance(word, HookWord):
                    names.add(str(name))
        return sorted(names)

    def _prompt_vm_word_names(self) -> list[str]:
        return sorted(str(n) for n in self.vm.all_words_view().keys())

    def _prompt_help_topic_names(self) -> list[str]:
        names = list(self.command_dispatcher.names()) + list(self.actions.names()) + self._prompt_vm_word_names()
        return sorted({str(n) for n in names})

    def _prompt_command_palette_names(self) -> list[str]:
        names = list(self.command_dispatcher.names()) + list(self.actions.names())
        return sorted({str(n) for n in names})

    def _prompt_vm_word_row(self, insert: str) -> list[str]:
        from micromax.vm import ColonWord, DeferredWord, HookWord, PrimitiveWord, word_doc_summary, word_effect

        raw = str(insert)
        name = raw[:-1] if raw.endswith(" ") else raw
        found = self.vm.find_word_with_wid(name)
        if found is None:
            return [str(insert), "word", "", ""]
        wid, w = found
        kind = "word"
        if isinstance(w, PrimitiveWord):
            kind = "primitive"
        elif isinstance(w, ColonWord):
            kind = "colon"
        elif isinstance(w, DeferredWord):
            kind = "deferred"
        elif isinstance(w, HookWord):
            kind = "hook"
        effect = str(word_effect(w) or "").strip()
        wl = str(self.vm.wordlist_names.get(int(wid), f"wl{wid}"))
        menu = f"{kind} wl={wl}"
        if effect:
            menu = f"{menu} {effect}"
        info = str(word_doc_summary(w) or "")
        return [str(insert), "word", menu, info]


    def _prompt_buffer_row(self, insert: str) -> list[str]:
        raw = str(insert)
        name = raw[:-1] if raw.endswith(" ") else raw
        eb = self.buffers.get(name)
        if eb is None:
            return [str(insert), "buffer", "", ""]
        menu = "active" if (self.active == name) else "buffer"
        path = getattr(eb.buf, "path", None) or ""
        nlines = len(getattr(eb.buf, "lines", []) or [])
        info_parts: list[str] = []
        if path:
            info_parts.append(str(path))
        if nlines:
            info_parts.append(f"{nlines} lines")
        info = " | ".join(info_parts)
        return [str(insert), "buffer", str(menu), str(info)]

    def _prompt_mark_row(self, insert: str) -> list[str]:
        raw = str(insert)
        name = raw[:-1] if raw.endswith(" ") else raw
        if name not in self.marks:
            return [str(insert), "mark", "", ""]
        buf_name, cur = self.marks[name]
        menu = f"{buf_name}:{int(cur.line)+1}:{int(cur.col)+1}"
        info = ""
        eb = self.buffers.get(buf_name)
        if eb is not None:
            line_i = int(cur.line)
            if 0 <= line_i < len(eb.buf.lines):
                s = eb.buf.lines[line_i].rstrip("\n")
                s = s.strip()
                if len(s) > 80:
                    s = s[:77] + "..."
                info = s
        return [str(insert), "mark", str(menu), str(info)]

    def plugin_inventory_entry(self, name: str) -> str:
        pm = getattr(self, "plugin_manager", None)
        if pm is None:
            return str(name)
        plugin_name = str(name)
        loaded = False
        version = ""
        reqs: list[str] = []
        try:
            loaded = bool(plugin_name in getattr(pm, "plugins", {}))
            cand = getattr(pm, "candidates", {}).get(plugin_name) if hasattr(pm, "candidates") else None
            if cand is not None:
                version = str(cand.meta.version or "")
                reqs = [str(x) for x in list(cand.meta.requires or []) if str(x).strip() != ""]
            elif loaded:
                plug = getattr(pm, "plugins", {}).get(plugin_name)
                meta = getattr(plug, "meta", {}) if plug is not None else {}
                if isinstance(meta, dict):
                    version = str(meta.get("version") or "")
                    reqs = [str(x) for x in list(meta.get("requires") or []) if str(x).strip() != ""]
        except Exception:
            pass
        errs: list[str] = []
        try:
            errs = [str(e) for (n, e) in getattr(pm, "load_errors", []) if str(n) == plugin_name]
        except Exception:
            errs = []
        flags: list[str] = []
        if errs:
            flags.append("error")
        else:
            flags.append("loaded" if loaded else "available")
        if version:
            flags.append(f"v{version}")
        if reqs:
            flags.append("deps:" + ",".join(reqs))
        return f"{plugin_name} [{', '.join(flags)}]" if flags else plugin_name

    def plugin_reload_with_feedback(self, name: str) -> bool:
        """Reload a plugin and report the resulting state in the current plugin dialect.

        The command-bar `plugin reload NAME` path became much more explicit over
        several tiny trust-first passes. The live scripting hostcall path should
        not drift back to older generic error messages, so this method centralizes
        the user-visible feedback shape for both command and hostcall reloads.
        """

        pm = getattr(self, "plugin_manager", None)
        if pm is None:
            self.message("plugin reload: no plugin manager")
            return False
        plugin_name = str(name)
        loaded_before = bool(plugin_name in getattr(pm, "plugins", {}))
        cand_before = getattr(pm, "candidates", {}).get(plugin_name) if hasattr(pm, "candidates") else None
        try:
            errs_before = [str(e) for (n, e) in getattr(pm, "load_errors", []) if str(n) == plugin_name]
        except Exception:
            errs_before = []
        if not loaded_before:
            if cand_before is None and not errs_before:
                self.message(f"plugin reload: no such plugin: {plugin_name}")
                return False
            self.message(f"plugin reload: {self.plugin_inventory_entry(plugin_name)}")
            if errs_before:
                self.message(f"  errors: {len(errs_before)}")
                for err in errs_before[-50:]:
                    self.message(f"    - {err}")
            else:
                self.message("  reload: plugin not loaded")
            return False
        try:
            pm.reload(plugin_name)
        except Exception as e:
            try:
                errs_after = [str(err) for (n, err) in getattr(pm, "load_errors", []) if str(n) == plugin_name]
            except Exception:
                errs_after = []
            cand_after = getattr(pm, "candidates", {}).get(plugin_name) if hasattr(pm, "candidates") else None
            loaded_after = bool(plugin_name in getattr(pm, "plugins", {}))
            if loaded_after or cand_after is not None or errs_after:
                self.message(f"plugin reload: {self.plugin_inventory_entry(plugin_name)}")
                if errs_after:
                    self.message(f"  errors: {len(errs_after)}")
                    for err in errs_after[-50:]:
                        self.message(f"    - {err}")
                else:
                    self.message(f"  reload error: {e}")
                return False
            self.message(f"plugin reload: no such plugin: {plugin_name}")
            return False
        self.message(f"plugin reload: {self.plugin_inventory_entry(plugin_name)}")
        return True

    def _prompt_plugin_row(self, insert: str) -> list[str]:
        raw = str(insert)
        name = raw[:-1] if raw.endswith(" ") else raw
        pm = getattr(self, "plugin_manager", None)
        if pm is None:
            return [str(insert), "plugin", "", ""]

        loaded = name in getattr(pm, "plugins", {})
        cand = getattr(pm, "candidates", {}).get(name) if hasattr(pm, "candidates") else None

        desc = ""
        try:
            if cand is not None:
                desc = str(cand.meta.description or "")
            elif loaded:
                meta = getattr(pm.plugins.get(name), "meta", {}) if pm else {}
                desc = str(meta.get("description") or "")
        except Exception:
            pass

        errs: list[str] = []
        try:
            errs = [str(e) for (n, e) in getattr(pm, "load_errors", []) if str(n) == name]
        except Exception:
            errs = []

        summary = self.plugin_inventory_entry(name)
        menu = summary[len(name):].strip() if summary.startswith(name) else summary

        info = desc
        if errs:
            info = errs[-1] if len(errs) == 1 else f"{len(errs)} errors; last: {errs[-1]}"
        return [str(insert), "plugin", str(menu), str(info)]


    def _prompt_option_value_candidates(
        self,
        name: str,
        prefix: str,
        *,
        at_eol: bool,
    ) -> tuple[list[str], bool]:
        spec = self.options.spec(str(name))
        if spec is None:
            return ([], False)
        if spec.kind == "bool":
            return self._completion_candidates_for_prefix(["true", "false"], prefix, at_eol=at_eol)
        if spec.kind == "enum" and spec.enum:
            return self._completion_candidates_for_prefix(list(spec.enum), prefix, at_eol=at_eol)
        return ([], False)


    def _prompt_display_value(self, value: object) -> str:
        if isinstance(value, bool):
            return "true" if value else "false"
        if value is None:
            return "0"
        return str(value)

    def _prompt_option_row(self, name: str, *, local: bool) -> list[str]:
        spec = self.options.spec(str(name))
        if spec is None:
            return [str(name), "option", "", ""]

        scope = "local" if local else "global"
        kind = str(spec.kind)
        if spec.kind == "enum" and spec.enum:
            kind = kind + "[" + "|".join(str(x) for x in spec.enum) + "]"

        cur_local = self.cur().local_options if local else None
        cur = self.options.get(spec.name, local=cur_local)
        menu = f"{kind} {scope} current={self._prompt_display_value(cur)} default={self._prompt_display_value(spec.default)}"
        return [spec.name + " ", "option", menu, str(spec.doc or "")]

    def _prompt_path_row(self, insert: str) -> list[str]:
        import os

        raw = str(insert)
        body = raw[:-1] if raw.endswith(" ") else raw
        if body.startswith(("'", '"')):
            body = body[1:]
        if body.endswith(("'", '"')):
            body = body[:-1]
        kind = "dir" if body.endswith(os.sep) else "file"
        menu = "directory" if kind == "dir" else "file"
        return [str(insert), kind, menu, body]

    def _help_topic_meta_text(self, row: list[object]) -> str:
        parts: list[str] = []
        if len(row) >= 3 and row[2] not in (None, 0, ""):
            parts.append(str(row[2]))
        if len(row) >= 4 and row[3] not in (None, 0, ""):
            parts.append(str(row[3]))
        return " ".join(parts).strip()

    def _search_terms(self, query: str) -> list[str]:
        return [str(part) for part in str(query or "").split() if str(part)]

    def _multi_term_field_key(
        self,
        fields: list[tuple[int, str]],
        query: str,
        *,
        fallback_rank: int,
        tie_name: str,
    ) -> tuple[int, int, int, int, int, int, int, int, int, str] | None:
        terms = self._search_terms(query)
        if len(terms) <= 1:
            return None

        matched: list[tuple[int, int, int, int, int, int, int, str]] = []
        for term in terms:
            best: tuple[int, int, int, int, int, int, int, str] | None = None
            for field_rank, raw_text in fields:
                text = str(raw_text or "")
                if text == "":
                    continue
                key = self._completion_fuzzy_sort_key(text, term)
                if key is None:
                    continue
                cand = (field_rank, *key)
                if best is None or cand < best:
                    best = cand
            if best is None:
                return None
            matched.append(best)

        return (
            fallback_rank,
            sum(item[0] for item in matched),
            sum(item[1] for item in matched),
            sum(item[2] for item in matched),
            sum(item[3] for item in matched),
            sum(item[4] for item in matched),
            sum(item[5] for item in matched),
            sum(item[6] for item in matched),
            sum(item[7] for item in matched),
            str(tie_name).casefold(),
        )

    def _apropos_row_sort_key(self, row: list[object], query: str) -> tuple[int, int, int, int, int, int, int, int, int, str] | None:
        q = str(query or "").strip()
        if q == "":
            return (0, 0, 0, 0, 0, 0, 0, 0, 0, "")

        name = str(row[0]) if row else ""
        name_key = self._completion_fuzzy_sort_key(name, q)
        if name_key is not None:
            return (0, *name_key, name.casefold())

        meta = self._help_topic_meta_text(row)
        if meta:
            folded_meta = meta.casefold()
            folded_q = q.casefold()
            if folded_q and folded_q in folded_meta:
                pos = folded_meta.find(folded_q)
                return (1, pos, pos, 0, 0, 0, 0, len(meta), len(name), name.casefold())

            meta_key = self._completion_fuzzy_sort_key(meta, q)
            if meta_key is not None:
                return (2, *meta_key, name.casefold())

        multi_key = self._multi_term_field_key([(0, name), (1, meta)], q, fallback_rank=3, tie_name=name)
        if multi_key is not None:
            return multi_key
        return None

    def _command_palette_row_key(self, row: list[object]) -> tuple[str, str]:
        name = str(row[0]) if row else ""
        kind = str(row[1]) if len(row) >= 2 else ""
        return (kind, name)

    def _record_palette_recent(self, kind: str, name: str) -> None:
        k = str(kind or "").strip()
        nm = str(name or "").strip()
        if k not in ("command", "action") or not nm:
            return
        entry = (k, nm)
        self._palette_recent = [it for it in self._palette_recent if it != entry]
        self._palette_recent.insert(0, entry)
        limit = max(1, int(self._palette_recent_limit))
        del self._palette_recent[limit:]

    def _command_palette_recent_rank(self, row: list[object]) -> int:
        entry = self._command_palette_row_key(row)
        try:
            return self._palette_recent.index(entry)
        except ValueError:
            return max(1000, len(self._palette_recent) + 100)

    def command_palette_recent_rows(self, *, limit: int | None = None) -> list[list[str]]:
        rows: list[list[str]] = []
        for kind, name in self._palette_recent:
            if kind == "command":
                c = self.command_dispatcher.get(name)
                if c is None:
                    continue
                info = f"group={c.group}" if c.group else ""
                rows.append([str(name), "command", str(c.doc or ""), info])
                continue
            if kind == "action":
                a = self.actions.get(name)
                if a is None:
                    continue
                rows.append([str(name), "action", str(a.doc or ""), ""])
        return rows[:limit] if limit is not None else rows

    def command_palette_recent_file_rows(self, *, limit: int | None = None) -> list[list[str]]:
        """Rows for recent files shown inside the command palette."""
        rows: list[list[str]] = []
        for raw in list(getattr(self, 'recent_files', [])):
            p = str(raw)
            try:
                pp = Path(p)
                menu = str(pp.name) if pp.name else 'file'
                info = str(pp.parent) if str(pp.parent) not in ('.', '') else ''
            except Exception:
                menu, info = 'file', ''
            rows.append([p, 'recentfile', menu, info])
        return rows[:limit] if limit is not None else rows

    def _command_palette_nonrecent_rows(self) -> list[list[str]]:
        recent = {self._command_palette_row_key(row) for row in self.command_palette_recent_rows()}
        out: list[list[str]] = []
        for row in self.command_palette_rows():
            if self._command_palette_row_key(row) in recent:
                continue
            out.append([str(x) for x in row[:4]])
        return out

    def _command_palette_section_label(self, row: list[object]) -> str:
        kind = str(row[1]) if len(row) >= 2 else ""
        if kind == 'openpath':
            menu = str(row[2]) if len(row) >= 3 else ""
            if menu == 'dir':
                return 'Directories'
            if menu == 'file' or menu == 'other':
                return 'Files'
            return 'Open'
        if kind == 'recentfile':
            return 'Recent Files'
        if self._command_palette_recent_rank(row) < max(1000, len(self._palette_recent) + 100):
            return 'Recent'
        if kind == 'action':
            return 'Actions'
        return 'Commands'

    def _looks_like_path_query(self, q: str) -> bool:
        """Heuristic: does a palette query look like a filesystem path?"""

        s = str(q or "").strip()
        if not s:
            return False
        if any(ch in s for ch in ("/", "\\")):
            return True
        if s.startswith(("./", "../", "~", "/")):
            return True
        if s.endswith((".md", ".mx", ".py", ".json", ".toml", ".yaml", ".yml")):
            return True
        return False

    def command_palette_rows(self) -> list[list[str]]:
        rows: list[list[str]] = []
        for name in self.command_dispatcher.names():
            c = self.command_dispatcher.get(name)
            if c is None:
                continue
            info = f"group={c.group}" if c.group else ""
            rows.append([str(name), "command", str(c.doc or ""), info])
        for name in self.actions.names():
            a = self.actions.get(name)
            if a is None:
                continue
            rows.append([str(name), "action", str(a.doc or ""), ""])

        def _kind_rank(kind: str) -> int:
            return {"recentfile": 0, "command": 1, "action": 2}.get(str(kind), 3)

        rows.sort(key=lambda row: (str(row[0]).casefold(), _kind_rank(str(row[1])), str(row[1]).casefold()))
        return rows

    def command_palette_apropos_rows(self, query: str, *, limit: int | None = None) -> list[list[str]]:
        q = str(query or "").strip()
        file_rows = self.command_palette_recent_file_rows()

        def _path_completion_rows(raw: str, *, limit: int = 60) -> list[list[str]]:
            """Best-effort filesystem path completion rows for the palette.

            This is capability-gated (cap.fs-list) because it exposes host filesystem
            information to scripts/UI surfaces.

            Rows are: [path kind menu info] with kind=openpath and menu=dir|file.
            Directory rows include a trailing '/' so pressing Enter can drill down.
            """

            if not bool(self.options.get("cap.fs-list")):
                return []
            s = str(raw or "").strip()
            if not s:
                return []

            expanded = fs_resolve_path(self, s)

            ends_sep = s.endswith(("/", "\\"))
            try:
                if not ends_sep and expanded.exists() and expanded.is_dir():
                    base = expanded
                    prefix = ""
                elif ends_sep:
                    base = expanded
                    prefix = ""
                else:
                    base = expanded.parent
                    prefix = expanded.name
            except Exception:
                base = expanded.parent
                prefix = expanded.name

            # Optional filesystem sandbox: when cap.fs-root is set, refuse
            # to list outside it (including via symlink escapes).
            if not fs_path_allowed(self, base):
                return []

            try:
                if not base.exists() or not base.is_dir():
                    return []
            except Exception:
                return []

            try:
                items = list(base.iterdir())
            except Exception:
                return []

            want = prefix.casefold()
            rows2: list[list[str]] = []

            # Preserve the user's typed directory prefix (./, ../, ~/, /abs/, etc.)
            # so completion candidates actually match the query string.
            typed_dir = ""
            if ends_sep:
                typed_dir = s
            else:
                try:
                    if expanded.exists() and expanded.is_dir() and not prefix:
                        typed_dir = s
                except Exception:
                    typed_dir = ""
            if typed_dir and not typed_dir.endswith(("/", "\\")):
                typed_dir = typed_dir + "/"
            if not typed_dir:
                slash = max(s.rfind("/"), s.rfind("\\"))
                typed_dir = s[: slash + 1] if slash >= 0 else ""
            typed_dir = typed_dir.replace("\\", "/")


            for child in items:
                name = child.name
                if want and not name.casefold().startswith(want):
                    continue
                is_dir = False
                is_file = False
                try:
                    is_dir = child.is_dir()
                    is_file = child.is_file()
                except Exception:
                    pass
                menu = "dir" if is_dir else "file" if is_file else "other"
                disp = typed_dir + name
                if is_dir and not disp.endswith("/"):
                    disp = disp + "/"
                rows2.append([disp, "openpath", menu, ""])

            def _rank(row: list[str]) -> tuple[int, str]:
                menu = str(row[2])
                return (0 if menu == "dir" else 1, str(row[0]).casefold())

            rows2.sort(key=_rank)
            return rows2[: max(0, int(limit))]

        open_rows: list[list[str]] = []
        if q and self._looks_like_path_query(q):
            open_rows = [[q, "openpath", "open", "path-like query"]]
            open_rows = _path_completion_rows(q, limit=max(0, min(80, int(limit or 60)))) + open_rows
        rows = self.command_palette_rows() + file_rows + open_rows
        if q == "":
            out = file_rows + self.command_palette_recent_rows() + self._command_palette_nonrecent_rows()
            return out[:limit] if limit is not None else out

        scored: list[tuple[tuple[int, int, int, int, int, int, int, int, int, str], int, int, int, list[str]]] = []

        def _kind_rank(kind: str) -> int:
            return {"openpath": 0, "recentfile": 1, "command": 2, "action": 3}.get(str(kind), 4)

        for idx, row in enumerate(rows):
            key = self._apropos_row_sort_key(row, q)
            if key is None:
                continue
            recent_rank = self._command_palette_recent_rank(row)
            scored.append((key, recent_rank, _kind_rank(str(row[1])), idx, [str(x) for x in row]))

        scored.sort(
            key=lambda item: (
                item[0][:-2],
                item[1],
                item[0][-2],
                item[0][-1],
                item[2],
                item[3],
            )
        )
        out = [row for _key, _recent, _rank, _idx, row in scored]
        return out[:limit] if limit is not None else out

    def command_palette_section_rows(self, query: str = "", *, limit: int | None = None) -> list[list[object]]:
        q = str(query or "").strip()
        section_order = ["Directories", "Files", "Open", "Recent Files", "Recent", "Commands", "Actions"]

        if q == "":
            buckets: dict[str, list[list[str]]] = {label: [] for label in section_order}
            for row in self.command_palette_recent_file_rows():
                vals = [str(x) for x in list(row[:4])]
                while len(vals) < 4:
                    vals.append("")
                buckets["Recent Files"].append(vals)
            for row in self.command_palette_recent_rows():
                vals = [str(x) for x in list(row[:4])]
                while len(vals) < 4:
                    vals.append("")
                buckets["Recent"].append(vals)
            for row in self._command_palette_nonrecent_rows():
                vals = [str(x) for x in list(row[:4])]
                while len(vals) < 4:
                    vals.append("")
                label = self._command_palette_section_label(vals)
                buckets.setdefault(label, [])
                buckets[label].append(vals)
            sections = [[label, buckets[label]] for label in section_order if buckets.get(label)]
            extras = [label for label in buckets.keys() if label not in section_order and buckets.get(label)]
            sections.extend([[label, buckets[label]] for label in extras])
            return self._limit_grouped_prompt_sections(sections, limit=limit, browse_budget=True)

        rows = self.command_palette_apropos_rows(q, limit=None)
        buckets: dict[str, list[list[str]]] = {label: [] for label in section_order}
        for row in rows:
            vals = [str(x) for x in list(row[:4])]
            while len(vals) < 4:
                vals.append("")
            label = self._command_palette_section_label(vals)
            buckets.setdefault(label, [])
            buckets[label].append(vals)
        sections: list[list[object]] = []
        for label in section_order:
            items = buckets.get(label, [])
            if items:
                sections.append([label, items])
        extras = [label for label in buckets.keys() if label not in section_order and buckets.get(label)]
        sections.extend([[label, buckets[label]] for label in extras])
        return self._limit_grouped_prompt_sections(sections, limit=limit, browse_budget=False)

    def help_topic_rows(self) -> list[list[str]]:
        rows = self.command_palette_rows()
        for name in self._prompt_vm_word_names():
            row = self._prompt_vm_word_row(name)
            rows.append([str(name), str(row[1]), str(row[2]), str(row[3])])
        return rows

    def _topic_section_names(self, kind: str) -> tuple[str, str]:
        k = str(kind or "").strip().casefold()
        if k == "command":
            return ("Command", "Commands")
        if k == "action":
            return ("Action", "Actions")
        if k == "buffer":
            return ("Buffer", "Buffers")
        if k == "mark":
            return ("Mark", "Marks")
        if k == "jump":
            return ("Jump", "Jumps")
        if k == "doc":
            return ("Doc", "Docs")
        if k == "link":
            return ("Link", "Links")
        if k in ("recent", "recentfile"):
            return ("Recent file", "Recent files")
        return ("Word", "Words")

    def _group_topic_rows(self, rows: list[list[str]]) -> list[list[object]]:
        section_order = ["Commands", "Actions", "Words"]
        buckets: dict[str, list[list[str]]] = {label: [] for label in section_order}
        extra_labels: list[str] = []
        for row in rows:
            vals = [str(x) for x in list(row[:4])]
            while len(vals) < 4:
                vals.append("")
            _single, plural = self._topic_section_names(vals[1])
            if plural not in buckets:
                buckets[plural] = []
                extra_labels.append(plural)
            buckets[plural].append(vals)
        out: list[list[object]] = []
        for label in section_order + extra_labels:
            items = buckets.get(label, [])
            if items:
                out.append([label, items])
        return out

    def help_topic_section_rows(self) -> list[list[object]]:
        return self._group_topic_rows(self.help_topic_rows())

    def apropos_rows(self, query: str, *, limit: int | None = None) -> list[list[str]]:
        q = str(query or "").strip()
        rows = self.help_topic_rows()
        if q == "":
            return rows[:limit] if limit is not None else rows

        scored: list[tuple[tuple[int, int, int, int, int, int, int, int, str], int, int, list[str]]] = []

        def _kind_rank(kind: str) -> int:
            return {"recentfile": 0, "command": 1, "action": 2}.get(str(kind), 3)

        for idx, row in enumerate(rows):
            key = self._apropos_row_sort_key(row, q)
            if key is None:
                continue
            scored.append((key, _kind_rank(str(row[1])), idx, [str(x) for x in row]))

        scored.sort(key=lambda item: (item[0], item[1], item[2]))
        out = [row for _key, _rank, _idx, row in scored]
        return out[:limit] if limit is not None else out

    def apropos_section_rows(self, query: str, *, limit: int | None = None) -> list[list[object]]:
        return self._group_topic_rows(self.apropos_rows(query, limit=limit))

    def _binding_row_mode(self, row: list[str]) -> str:
        """Best-effort binding mode name encoded in a binding prompt row."""
        try:
            menu = str(row[2] if len(row) > 2 else "")
            m = re.match(r"@([^\s]+)", menu)
            if m is not None:
                return str(m.group(1) or "global")
        except Exception:
            pass
        return "global"

    def _binding_section_label_for_mode(self, mode: str) -> str:
        raw = str(mode or "global")
        if raw == "global":
            return "Global"
        if raw == "prompt":
            return "Prompt"
        return raw

    def _binding_section_label(self, row: list[str]) -> str:
        """Best-effort visible section label for binding picker rows."""
        return self._binding_section_label_for_mode(self._binding_row_mode(row))

    def _binding_section_label_rank(self, label: str) -> tuple[int, str]:
        lbl = str(label or "")
        active_labels: list[str] = []
        try:
            active_labels = [
                self._binding_section_label_for_mode(str(m))
                for m in self.active_key_modes()
                if str(m) not in ("", "global", "prompt")
            ]
        except Exception:
            active_labels = []
        if lbl == "Prompt":
            return (0, lbl.casefold())
        if lbl in active_labels:
            return (1 + active_labels.index(lbl), lbl.casefold())
        if lbl == "Global":
            return (10, lbl.casefold())
        return (20, lbl.casefold())

    def _binding_section_sort_key(self, row: list[str]) -> tuple[int, str, str, str]:
        label = self._binding_section_label(row)
        rank, folded = self._binding_section_label_rank(label)
        key = str(row[0] if row else "")
        menu = str(row[2] if len(row) > 2 else "")
        return (int(rank), str(folded), key.casefold(), menu.casefold())

    def binding_prompt_rows(self) -> list[list[str]]:
        rows: list[list[str]] = []
        for mode, key, action, desc, _group, _span in self.available_binding_info_rows():
            mode_s = str(mode or "global")
            menu = f"@{mode_s} {action}"
            info = str(desc or "")
            rows.append([str(key), "binding", menu, info])
        rows.sort(key=self._binding_section_sort_key)
        return rows

    def binding_section_rows(self, query: str = "", *, limit: int | None = None) -> list[list[object]]:
        """Group current-binding rows by visible winning-mode label."""
        rows = self.binding_apropos_rows(query, limit=limit)
        return self._group_prompt_rows_by_section(
            rows,
            label_fn=self._binding_section_label,
            label_sort_key=self._binding_section_label_rank,
        )


    def _buffer_section_label(self, row: list[str]) -> str:
        """Best-effort section label for buffer picker rows.

        Used by the TUI to render section headers (and by the prompt row sorter so
        buffers appear grouped rather than interleaved).
        """
        try:
            name = str(row[0] if row else "")
            if name.startswith("help:"):
                return "Help"
            if name.startswith("*"):
                return "Scratch"
            info = str(row[3] if len(row) > 3 else "")
            path = info.split("|", 1)[0].strip() if info else ""
            if path:
                try:
                    root = self._project_root_for_path(path)
                except Exception:
                    root = None
                if root:
                    return str(root)
                return self._path_parent_section_label(path, fallback="Buffers")
        except Exception:
            pass
        return "Buffers"

    def _path_parent_section_label(self, path: str, *, fallback: str) -> str:
        """Return a visible parent-directory section label for one path.

        Picker/status surfaces should stay human and category-aware when a path
        has no useful parent directory (for example a relative ``notes.txt`` row
        whose filesystem parent would otherwise render as raw ``.``).
        """

        raw = str(path or "").strip()
        if raw == "":
            return str(fallback)
        try:
            parent = str(Path(raw).parent)
        except Exception:
            return str(fallback)
        if parent in ("", "."):
            return str(fallback)
        return parent

    def _buffer_section_label_rank(self, label: str) -> tuple[int, str]:
        lbl = str(label or "")
        rank = 2
        if lbl == "Help":
            rank = 0
        elif lbl in ("Scratch", "Buffers"):
            rank = 1
        return (int(rank), lbl.casefold())

    def _buffer_section_sort_key(self, row: list[str]) -> tuple[int, str, str]:
        label = self._buffer_section_label(row)
        rank, folded = self._buffer_section_label_rank(label)
        name = str(row[0] if row else "")
        return (int(rank), str(folded), name.casefold())


    def buffer_prompt_rows(self) -> list[list[str]]:
        rows: list[list[str]] = []
        for name in self.buffer_names():
            insert = str(name)
            row = self._prompt_buffer_row(insert)
            # _prompt_buffer_row expects an 'insert' string; ensure 4 cols
            vals = list(row[:4])
            while len(vals) < 4:
                vals.append("")
            rows.append([str(vals[0]), str(vals[1]), str(vals[2]), str(vals[3])])
        rows.sort(key=self._buffer_section_sort_key)
        return rows

    def _group_prompt_rows_by_section(
        self,
        rows: list[list[str]],
        *,
        label_fn,
        label_sort_key=None,
    ) -> list[list[object]]:
        """Return grouped prompt rows as ``[[label [[insert kind menu info] ...]] ...]``.

        This keeps the headless section-row hostcalls aligned with the same
        small section-label helpers the TUI and prompt preview/status surfaces
        already use.
        """

        buckets: dict[str, list[list[str]]] = {}
        order: list[str] = []
        for row in rows:
            vals = [str(x) for x in row[:4]]
            while len(vals) < 4:
                vals.append("")
            label = str(label_fn(vals))
            if label not in buckets:
                buckets[label] = []
                order.append(label)
            buckets[label].append(vals)
        labels = order
        if label_sort_key is not None:
            labels = sorted(buckets.keys(), key=label_sort_key)
        return [[label, buckets[label]] for label in labels]

    def _limit_grouped_prompt_sections(
        self,
        sections: list[list[object]],
        *,
        limit: int | None = None,
        browse_budget: bool = False,
    ) -> list[list[object]]:
        """Limit grouped prompt rows while keeping section boundaries intact.

        When ``browse_budget`` is true, empty-query picker browsing gets a tiny
        round-robin budget so each visible section contributes at least one row
        before larger sections consume the remainder of the window.
        """

        groups: list[tuple[str, list[list[str]]]] = []
        for sec in sections:
            label = str(sec[0] if sec else "")
            items = sec[1] if len(sec) > 1 else []
            rows: list[list[str]] = []
            for row in items:
                vals = [str(x) for x in list(row[:4])]
                while len(vals) < 4:
                    vals.append("")
                rows.append(vals)
            if rows:
                groups.append((label, rows))
        if limit is None:
            return [[label, rows] for label, rows in groups]

        cap = max(1, int(limit))
        if not groups:
            return []

        if browse_budget and cap >= len(groups):
            quotas = [1 for _ in groups]
            remaining = cap - len(groups)
            while remaining > 0:
                progressed = False
                for i, (_label, rows) in enumerate(groups):
                    if quotas[i] >= len(rows):
                        continue
                    quotas[i] += 1
                    remaining -= 1
                    progressed = True
                    if remaining <= 0:
                        break
                if not progressed:
                    break
            out: list[list[object]] = []
            for quota, (label, rows) in zip(quotas, groups):
                chunk = rows[:quota]
                if chunk:
                    out.append([label, chunk])
            return out

        out: list[list[object]] = []
        remaining = cap
        for label, rows in groups:
            if remaining <= 0:
                break
            chunk = rows[:remaining]
            if chunk:
                out.append([label, chunk])
                remaining -= len(chunk)
        return out

    def _flatten_grouped_prompt_sections(
        self,
        sections: list[list[object]],
        *,
        limit: int | None = None,
        browse_budget: bool = False,
    ) -> list[list[str]]:
        """Flatten grouped prompt rows using the same section-limit policy."""

        out: list[list[str]] = []
        for sec in self._limit_grouped_prompt_sections(
            sections,
            limit=limit,
            browse_budget=browse_budget,
        ):
            items = sec[1] if len(sec) > 1 else []
            for row in items:
                vals = [str(x) for x in list(row[:4])]
                while len(vals) < 4:
                    vals.append("")
                out.append(vals)
        return out

    def buffer_section_rows(self, query: str = "", *, limit: int | None = None) -> list[list[object]]:
        """Group buffer picker rows by their visible picker section label."""
        rows = self.buffer_apropos_rows(query, limit=limit)
        return self._group_prompt_rows_by_section(
            rows,
            label_fn=self._buffer_section_label,
            label_sort_key=self._buffer_section_label_rank,
        )

    def plugin_names(self) -> list[str]:
        pm = getattr(self, "plugin_manager", None)
        names: set[str] = set()
        if pm is not None:
            try:
                names.update(str(n) for n in getattr(pm, "plugins", {}).keys())
            except Exception:
                pass
            try:
                names.update(str(n) for n in getattr(pm, "candidates", {}).keys())
            except Exception:
                pass
            try:
                names.update(str(n) for (n, _e) in getattr(pm, "load_errors", []))
            except Exception:
                pass
        return sorted({str(n) for n in names if str(n).strip() != ""}, key=lambda s: s.casefold())


    def _plugin_section_label(self, row: list[str]) -> str:
        """Best-effort section label for plugin picker rows."""
        try:
            menu = str(row[2] if len(row) > 2 else "")
            low = menu.casefold()
            if "error" in low:
                return "Errors"
            if "loaded" in low:
                return "Loaded"
            if "available" in low:
                return "Available"
            return "Available"
        except Exception:
            return "Plugins"

    def _plugin_section_display_label(self, row: list[str], rows: list[list[object]] | None = None) -> str:
        """Return the visible plugin section label, with a tiny per-section count.

        The plugin loop has become increasingly count-aware in plain command
        output (`plugin list`, `plugin errors`). The searchable picker should
        not make section size implicit again, so section headers and previews
        reuse the same coarse idea: `Errors (1)`, `Loaded (2)`, `Available (3)`.
        """

        base = str(self._plugin_section_label(row) or "")
        if not base:
            return ""
        pool = rows
        if pool is None and self.prompt is not None and self.prompt.kind == "plugin":
            pool = list(getattr(self.prompt, "suggestion_rows", []) or [])
        if not pool:
            return base
        count = 0
        for item in pool:
            vals = [str(x) for x in list(item[:4])]
            while len(vals) < 4:
                vals.append("")
            if str(self._plugin_section_label(vals) or "") == base:
                count += 1
        return f"{base} ({count})" if count > 0 else base

    def _plugin_section_sort_key(self, row: list[str]) -> tuple[int, str, str]:
        label = self._plugin_section_label(row)
        rank = {"Errors": 0, "Loaded": 1, "Available": 2}.get(label, 3)
        name = str(row[0] if row else "")
        return (int(rank), str(label).casefold(), name.casefold())


    def plugin_prompt_rows(self) -> list[list[str]]:
        rows: list[list[str]] = []
        for name in self.plugin_names():
            insert = str(name)
            row = self._prompt_plugin_row(insert)
            vals = list(row[:4])
            while len(vals) < 4:
                vals.append("")
            rows.append([str(vals[0]), str(vals[1]), str(vals[2]), str(vals[3])])
        rows.sort(key=self._plugin_section_sort_key)
        return rows

    def _plugin_row_sort_key(self, row: list[object], query: str) -> tuple[int, int, int, int, int, int, int, int, int, str] | None:
        q = str(query or "").strip()
        if q == "":
            return (0, 0, 0, 0, 0, 0, 0, 0, 0, "")

        key = str(row[0]) if row else ""
        key_key = self._completion_fuzzy_sort_key(key, q)
        if key_key is not None:
            return (0, *key_key, key.casefold())

        meta = " ".join([str(row[2]) if len(row) >= 3 else "", str(row[3]) if len(row) >= 4 else ""]).strip()
        if meta:
            folded_meta = meta.casefold()
            folded_q = q.casefold()
            if folded_q and folded_q in folded_meta:
                pos = folded_meta.find(folded_q)
                return (1, pos, pos, 0, 0, 0, 0, len(meta), len(key), key.casefold())

            meta_key = self._completion_fuzzy_sort_key(meta, q)
            if meta_key is not None:
                return (2, *meta_key, key.casefold())
        return None

    def plugin_apropos_rows(self, query: str, *, limit: int | None = None) -> list[list[str]]:
        q = str(query or "").strip()
        rows = self.plugin_prompt_rows()
        if q == "":
            return rows[:limit] if limit is not None else rows

        scored: list[tuple[tuple[int, int, int, int, int, int, int, int, int, str], int, list[str]]] = []
        for idx, row in enumerate(rows):
            key = self._plugin_row_sort_key(row, q)
            if key is None:
                continue
            scored.append((key, idx, [str(x) for x in row]))

        scored.sort(key=lambda item: (item[0], item[1]))
        out = [row for _key, _idx, row in scored]
        return out[:limit] if limit is not None else out

    def plugin_section_rows(self, query: str = "", *, limit: int | None = None) -> list[list[object]]:
        """Group plugin picker rows by their visible picker section label."""
        rows = self.plugin_apropos_rows(query, limit=limit)
        grouped = self._group_prompt_rows_by_section(
            rows,
            label_fn=self._plugin_section_label,
            label_sort_key=lambda label: {"Errors": 0, "Loaded": 1, "Available": 2}.get(str(label), 3),
        )
        out: list[list[object]] = []
        for sec in grouped:
            label = str(sec[0] if sec else "")
            items = list(sec[1] if len(sec) > 1 else [])
            display = f"{label} ({len(items)})" if label and items else label
            out.append([display, items])
        return out


    def _buffer_row_sort_key(self, row: list[object], query: str) -> tuple[int, int, int, int, int, int, int, int, int, str] | None:
        q = str(query or "").strip()
        if q == "":
            return (0, 0, 0, 0, 0, 0, 0, 0, 0, "")

        key = str(row[0]) if row else ""
        key_key = self._completion_fuzzy_sort_key(key, q)
        if key_key is not None:
            return (0, *key_key, key.casefold())

        info = str(row[3]) if len(row) >= 4 else ""
        if info:
            folded_info = info.casefold()
            folded_q = q.casefold()
            if folded_q and folded_q in folded_info:
                pos = folded_info.find(folded_q)
                return (1, pos, pos, 0, 0, 0, 0, len(info), len(key), key.casefold())
            info_key = self._completion_fuzzy_sort_key(info, q)
            if info_key is not None:
                return (2, *info_key, key.casefold())

        menu = str(row[2]) if len(row) >= 3 else ""
        if menu:
            folded_menu = menu.casefold()
            folded_q = q.casefold()
            if folded_q and folded_q in folded_menu:
                pos = folded_menu.find(folded_q)
                return (3, pos, pos, 0, 0, 0, 0, len(menu), len(key), key.casefold())
            menu_key = self._completion_fuzzy_sort_key(menu, q)
            if menu_key is not None:
                return (4, *menu_key, key.casefold())

        multi_key = self._multi_term_field_key([(0, key), (1, info), (2, menu)], q, fallback_rank=5, tie_name=key)
        if multi_key is not None:
            return multi_key
        return None

    def buffer_apropos_rows(self, query: str, *, limit: int | None = None) -> list[list[str]]:
        q = str(query or "").strip()
        rows = self.buffer_prompt_rows()
        if q == "":
            return rows[:limit] if limit is not None else rows

        scored: list[tuple[tuple[int, int, int, int, int, int, int, int, int, str], int, list[str]]] = []
        for idx, row in enumerate(rows):
            key = self._buffer_row_sort_key(row, q)
            if key is None:
                continue
            scored.append((key, idx, [str(x) for x in row]))

        scored.sort(key=lambda item: (item[0], item[1]))
        out = [row for _key, _idx, row in scored]
        return out[:limit] if limit is not None else out

    def _mark_section_label(self, row: list[str]) -> str:
        """Best-effort section label for mark picker rows.

        Marks are global navigation points, but in practice users usually think
        of them by the owning buffer first. Keep the label exact/simple so future
        UIs/LLMs can reuse it directly instead of reverse-engineering `menu`.
        """
        try:
            name = str(row[0] if row else "")
            if name in self.marks:
                buf_name, _cur = self.marks[name]
                return str(buf_name)
            menu = str(row[2] if len(row) > 2 else "")
            m = re.match(r"(.+):(\d+):(\d+)\s*$", menu)
            if m is not None:
                return str(m.group(1))
        except Exception:
            pass
        return "Marks"

    def _mark_section_label_rank(self, label: str) -> tuple[int, str]:
        lbl = str(label or "")
        rank = 1
        if self.active is not None and lbl == str(self.active):
            rank = 0
        elif lbl == "Marks":
            rank = 2
        return (int(rank), lbl.casefold())

    def _mark_section_sort_key(self, row: list[str]) -> tuple[int, str, str]:
        label = self._mark_section_label(row)
        name = str(row[0] if row else "")
        rank, folded = self._mark_section_label_rank(label)
        return (int(rank), str(folded), name.casefold())

    def mark_prompt_rows(self) -> list[list[str]]:
        rows: list[list[str]] = []
        for name in sorted(self.marks.keys()):
            insert = str(name)
            row = self._prompt_mark_row(insert)
            vals = list(row[:4])
            while len(vals) < 4:
                vals.append("")
            rows.append([str(vals[0]), str(vals[1]), str(vals[2]), str(vals[3])])
        rows.sort(key=self._mark_section_sort_key)
        return rows

    def _mark_row_sort_key(self, row: list[object], query: str) -> tuple[int, int, int, int, int, int, int, int, int, str] | None:
        q = str(query or "").strip()
        if q == "":
            return (0, 0, 0, 0, 0, 0, 0, 0, 0, "")

        key = str(row[0]) if row else ""
        key_key = self._completion_fuzzy_sort_key(key, q)
        if key_key is not None:
            return (0, *key_key, key.casefold())

        info = str(row[3]) if len(row) >= 4 else ""
        if info:
            folded_info = info.casefold()
            folded_q = q.casefold()
            if folded_q and folded_q in folded_info:
                pos = folded_info.find(folded_q)
                return (1, pos, pos, 0, 0, 0, 0, len(info), len(key), key.casefold())
            info_key = self._completion_fuzzy_sort_key(info, q)
            if info_key is not None:
                return (2, *info_key, key.casefold())

        menu = str(row[2]) if len(row) >= 3 else ""
        if menu:
            folded_menu = menu.casefold()
            folded_q = q.casefold()
            if folded_q and folded_q in folded_menu:
                pos = folded_menu.find(folded_q)
                return (3, pos, pos, 0, 0, 0, 0, len(menu), len(key), key.casefold())
            menu_key = self._completion_fuzzy_sort_key(menu, q)
            if menu_key is not None:
                return (4, *menu_key, key.casefold())

        multi_key = self._multi_term_field_key([(0, key), (1, info), (2, menu)], q, fallback_rank=5, tie_name=key)
        if multi_key is not None:
            return multi_key
        return None

    def mark_apropos_rows(self, query: str, *, limit: int | None = None) -> list[list[str]]:
        q = str(query or "").strip()
        rows = self.mark_prompt_rows()
        if q == "":
            return rows[:limit] if limit is not None else rows

        scored: list[tuple[tuple[int, int, int, int, int, int, int, int, int, str], int, list[str]]] = []
        for idx, row in enumerate(rows):
            key = self._mark_row_sort_key(row, q)
            if key is None:
                continue
            scored.append((key, idx, [str(x) for x in row]))

        scored.sort(key=lambda item: (item[0], item[1]))
        out = [row for _key, _idx, row in scored]
        return out[:limit] if limit is not None else out

    def mark_section_rows(self, query: str = "", *, limit: int | None = None) -> list[list[object]]:
        """Group mark rows by owning buffer for future pickers/UIs."""
        rows = self.mark_apropos_rows(query, limit=limit)
        return self._group_prompt_rows_by_section(
            rows,
            label_fn=self._mark_section_label,
            label_sort_key=self._mark_section_label_rank,
        )

    def _jump_section_label(self, row: list[str]) -> str:
        """Best-effort section label for jumplist picker rows."""
        try:
            eb = self.cur()
            self._normalize_cursor_lists(eb)
            cur_i = int(eb.jump_index)
            m = re.match(r"\s*(\d+)", str(row[0] if row else ""))
            if m is None or cur_i < 0:
                return "Jumps"
            idx0 = int(m.group(1), 10) - 1
            if idx0 == cur_i:
                return "Current"
            if idx0 < cur_i:
                return "Back"
            return "Forward"
        except Exception:
            return "Jumps"

    def _jump_section_label_rank(self, label: str) -> tuple[int, str]:
        lbl = str(label or "")
        rank = {"Current": 0, "Back": 1, "Forward": 2, "Jumps": 3}.get(lbl, 4)
        return (int(rank), lbl.casefold())

    def _jump_section_sort_key(self, row: list[str]) -> tuple[int, int, int]:
        label = self._jump_section_label(row)
        rank, _folded = self._jump_section_label_rank(label)
        try:
            eb = self.cur()
            self._normalize_cursor_lists(eb)
            cur_i = int(eb.jump_index)
            m = re.match(r"\s*(\d+)", str(row[0] if row else ""))
            idx0 = int(m.group(1), 10) - 1 if m is not None else -1
            if label == "Back":
                return (int(rank), max(0, cur_i - idx0), 0)
            if label == "Forward":
                return (int(rank), max(0, idx0 - cur_i), 0)
            if idx0 >= 0:
                return (int(rank), 0, idx0)
        except Exception:
            pass
        return (int(rank), 0, 0)

    def jump_prompt_rows(self) -> list[list[str]]:
        """Return jumplist picker rows for the current buffer.

        Rows are [[insert kind menu info] ...]. `insert` is a 1-based jumplist
        index so users can type a number, while `menu`/`info` carry the useful
        context for fuzzy search.
        """
        eb = self.cur()
        self._normalize_cursor_lists(eb)
        rows: list[list[str]] = []
        n = int(len(eb.jump_list))
        # Newest-first feels best for navigation history.
        for idx0 in range(n - 1, -1, -1):
            snap = eb.jump_list[idx0]
            curs, _anchors, _cursor_ids, primary = snap
            if not curs:
                continue
            pi = int(primary) if 0 <= int(primary) < len(curs) else 0
            c = curs[pi]
            insert = str(idx0 + 1)
            marker = "*" if idx0 == int(eb.jump_index) else " "
            menu = f"{marker}{idx0 + 1}/{n} {int(c.line) + 1}:{int(c.col) + 1}"
            info = ""
            li = int(c.line)
            if 0 <= li < len(eb.buf.lines):
                s = eb.buf.lines[li].rstrip("\n").strip()
                if len(s) > 80:
                    s = s[:77] + "..."
                info = s
            rows.append([insert, "jump", str(menu), str(info)])
        if 0 <= int(eb.jump_index) < n:
            rows.sort(key=self._jump_section_sort_key)
        return rows

    def _jump_row_sort_key(self, row: list[object], query: str) -> tuple[int, int, int, int, int, int, int, int, int, str] | None:
        q = str(query or "").strip()
        if q == "":
            return (0, 0, 0, 0, 0, 0, 0, 0, 0, "")

        key = str(row[0]) if row else ""
        key_key = self._completion_fuzzy_sort_key(key, q)
        if key_key is not None:
            return (0, *key_key, key.casefold())

        info = str(row[3]) if len(row) >= 4 else ""
        if info:
            folded_info = info.casefold()
            folded_q = q.casefold()
            if folded_q and folded_q in folded_info:
                pos = folded_info.find(folded_q)
                return (1, pos, pos, 0, 0, 0, 0, len(info), len(key), key.casefold())
            info_key = self._completion_fuzzy_sort_key(info, q)
            if info_key is not None:
                return (2, *info_key, key.casefold())

        menu = str(row[2]) if len(row) >= 3 else ""
        if menu:
            folded_menu = menu.casefold()
            folded_q = q.casefold()
            if folded_q and folded_q in folded_menu:
                pos = folded_menu.find(folded_q)
                return (3, pos, pos, 0, 0, 0, 0, len(menu), len(key), key.casefold())
            menu_key = self._completion_fuzzy_sort_key(menu, q)
            if menu_key is not None:
                return (4, *menu_key, key.casefold())

        multi_key = self._multi_term_field_key([(0, key), (1, info), (2, menu)], q, fallback_rank=5, tie_name=key)
        if multi_key is not None:
            return multi_key
        return None

    def jump_apropos_rows(self, query: str, *, limit: int | None = None) -> list[list[str]]:
        q = str(query or "").strip()
        rows = self.jump_prompt_rows()
        if q == "":
            return rows[:limit] if limit is not None else rows

        scored: list[tuple[tuple[int, int, int, int, int, int, int, int, int, str], int, list[str]]] = []
        for idx0, row in enumerate(rows):
            key = self._jump_row_sort_key(row, q)
            if key is None:
                continue
            scored.append((key, idx0, [str(x) for x in row]))

        scored.sort(key=lambda item: (item[0], item[1]))
        out = [row for _key, _idx, row in scored]
        return out[:limit] if limit is not None else out

    def jump_section_rows(self, query: str = "", *, limit: int | None = None) -> list[list[object]]:
        """Group jumplist rows by relation to the current jump entry."""
        rows = self.jump_apropos_rows(query, limit=limit)
        return self._group_prompt_rows_by_section(
            rows,
            label_fn=self._jump_section_label,
            label_sort_key=self._jump_section_label_rank,
        )

    def _binding_row_sort_key(self, row: list[object], query: str) -> tuple[int, int, int, int, int, int, int, int, int, str] | None:
        q = str(query or "").strip()
        if q == "":
            return (0, 0, 0, 0, 0, 0, 0, 0, 0, "")

        key = str(row[0]) if row else ""
        key_key = self._completion_fuzzy_sort_key(key, q)
        if key_key is not None:
            return (0, *key_key, key.casefold())

        info = str(row[3]) if len(row) >= 4 else ""
        if info:
            folded_info = info.casefold()
            folded_q = q.casefold()
            if folded_q and folded_q in folded_info:
                pos = folded_info.find(folded_q)
                return (1, pos, pos, 0, 0, 0, 0, len(info), len(key), key.casefold())
            info_key = self._completion_fuzzy_sort_key(info, q)
            if info_key is not None:
                return (2, *info_key, key.casefold())

        menu = str(row[2]) if len(row) >= 3 else ""
        if menu:
            folded_menu = menu.casefold()
            folded_q = q.casefold()
            if folded_q and folded_q in folded_menu:
                pos = folded_menu.find(folded_q)
                return (3, pos, pos, 0, 0, 0, 0, len(menu), len(key), key.casefold())
            menu_key = self._completion_fuzzy_sort_key(menu, q)
            if menu_key is not None:
                return (4, *menu_key, key.casefold())

        multi_key = self._multi_term_field_key([(0, key), (1, info), (2, menu)], q, fallback_rank=5, tie_name=key)
        if multi_key is not None:
            return multi_key
        return None

    def binding_apropos_rows(self, query: str, *, limit: int | None = None) -> list[list[str]]:
        q = str(query or "").strip()
        rows = self.binding_prompt_rows()
        if q == "":
            return rows[:limit] if limit is not None else rows

        scored: list[tuple[tuple[int, int, int, int, int, int, int, int, str], int, list[str]]] = []
        for idx, row in enumerate(rows):
            key = self._binding_row_sort_key(row, q)
            if key is None:
                continue
            scored.append((key, idx, [str(x) for x in row]))

        scored.sort(key=lambda item: (item[0], item[1]))
        out = [row for _key, _idx, row in scored]
        return out[:limit] if limit is not None else out

    def _prompt_commandish_suggestion_rows(
        self,
        *,
        cmd: str,
        toks: list[str],
        tok_i: int,
        candidates: list[str],
    ) -> list[list[str]]:
        rows: list[list[str]] = []
        for cand in candidates:
            insert = str(cand)
            raw = insert[:-1] if insert.endswith(" ") else insert
            row = [insert, "", "", ""]

            if tok_i == 0:
                c = self.command_dispatcher.get(raw)
                if c is not None:
                    info = ""
                    if c.group:
                        info = f"group={c.group}"
                    row = [insert, "command", str(c.doc or ""), info]
                rows.append(row)
                continue

            if tok_i == 1 and cmd in ("set", "setlocal", "show", "toggle", "togglelocal"):
                rows.append(self._prompt_option_row(raw, local=(cmd in ("setlocal", "togglelocal"))))
                continue

            if tok_i == 2 and cmd in ("set", "setlocal") and len(toks) >= 2:
                name = str(toks[1])
                spec = self.options.spec(name)
                cur_local = self.cur().local_options if cmd == "setlocal" else None
                cur = None
                if spec is not None:
                    cur = self.options.get(name, local=cur_local)
                menu = f"value for {name}"
                if cur is not None and raw == self._prompt_display_value(cur):
                    menu = menu + " (current)"
                info = str(spec.doc or "") if spec is not None else ""
                row = [insert, "value", menu, info]
                rows.append(row)
                continue

            if tok_i == 1 and cmd in ("help", "apropos"):
                topic_kind = "help topic" if cmd == "help" else "search topic"
                c = self.command_dispatcher.get(raw)
                if c is not None:
                    rows.append([insert, "command", str(c.doc or ""), topic_kind])
                    continue
                a = self.actions.get(raw)
                if a is not None:
                    rows.append([insert, "action", str(a.doc or ""), topic_kind])
                    continue
                rows.append(self._prompt_vm_word_row(insert))
                continue

            if tok_i == 1 and cmd == "commandpick":
                c = self.command_dispatcher.get(raw)
                if c is not None:
                    rows.append([insert, "command", str(c.doc or ""), "command palette"])
                    continue
                a = self.actions.get(raw)
                if a is not None:
                    rows.append([insert, "action", str(a.doc or ""), "command palette"])
                    continue

            if tok_i == 1 and cmd == "showcmd":
                c = self.command_dispatcher.get(raw)
                if c is not None:
                    rows.append([insert, "command", str(c.doc or ""), "inspect command"])
                    continue

            if tok_i == 1 and cmd == "showhook":
                rows.append([insert, "hook", "hook", "inspect hook"])
                continue

            if tok_i == 1 and cmd == "showword":
                rows.append(self._prompt_vm_word_row(insert))
                continue

            if tok_i == 1 and cmd == "buffer":
                rows.append(self._prompt_buffer_row(insert))
                continue

            if tok_i == 1 and cmd in ("mark", "markjump"):
                rows.append(self._prompt_mark_row(insert))
                continue

            if tok_i == 1 and cmd == "plugin":
                rows.append([insert, "subcommand", "plugin action", ""])
                continue

            if tok_i == 2 and cmd == "plugin" and len(toks) >= 2 and str(toks[1]) in ("reload", "info", "errors"):
                rows.append(self._prompt_plugin_row(insert))
                continue

            if tok_i == 1 and cmd == "macro":
                rows.append([insert, "subcommand", "macro action", ""])
                continue

            if tok_i == 2 and cmd == "macro" and len(toks) >= 2 and toks[1] in ("play", "record", "rec", "start"):
                rows.append([insert, "macro", "macro slot", ""])
                continue

            if tok_i == 1 and cmd in ("keymode", "pushkeymode", "pushkeymode-once", "prefixmode"):
                menu = "active keymode" if raw in self.active_key_modes() else "keymode"
                rows.append([insert, "keymode", menu, ""])
                continue

            if tok_i == 1 and cmd == "showbindings":
                if raw == "active":
                    rows.append([insert, "special", "currently active keymodes", ""])
                else:
                    menu = "active keymode" if raw in self.active_key_modes() else "keymode"
                    rows.append([insert, "keymode", menu, "show bindings"])
                continue

            if tok_i == 1 and cmd in ("bindmode", "bindmodedoc", "unbindmode", "bindmodeprefix"):
                rows.append([insert, "keymode", "owner mode", ""])
                continue

            if tok_i == 3 and cmd == "bindmodeprefix":
                rows.append([insert, "keymode", "prefix mode", ""])
                continue

            rows.append(row)
        return rows

    def _prompt_bind_suggestion_rows(
        self,
        *,
        cmd: str,
        toks: list[str],
        tok_i: int,
        candidates: list[str],
    ) -> list[list[str]]:
        action_tok_i = 2 if cmd == "bind" else 3
        if tok_i < action_tok_i or len(toks) <= action_tok_i:
            return [[str(c), "", "", ""] for c in candidates]

        action_head = toks[action_tok_i]
        for lead in ("command-edit:", "command:"):
            if action_head.startswith(lead):
                first = action_head[len(lead):]
                nested_toks = [first] + toks[action_tok_i + 1 :]
                nested_tok_i = tok_i - action_tok_i
                if nested_tok_i == 0:
                    rows: list[list[str]] = []
                    for cand in candidates:
                        insert = str(cand)
                        raw = insert[:-1] if insert.endswith(" ") else insert
                        if raw.startswith(lead):
                            nested_raw = raw[len(lead):]
                        else:
                            nested_raw = raw
                        nested_rows = self._prompt_commandish_suggestion_rows(
                            cmd=nested_raw,
                            toks=[nested_raw],
                            tok_i=0,
                            candidates=[nested_raw + (" " if insert.endswith(" ") else "")],
                        )
                        nr = nested_rows[0] if nested_rows else [nested_raw, "command", "", ""]
                        rows.append([insert, "binding-command", nr[2], lead[:-1]])
                    return rows
                return self._prompt_commandish_suggestion_rows(
                    cmd=(nested_toks[0] if nested_toks else ""),
                    toks=nested_toks,
                    tok_i=nested_tok_i,
                    candidates=candidates,
                )

        if tok_i == action_tok_i:
            rows: list[list[str]] = []
            for cand in candidates:
                insert = str(cand)
                raw = insert[:-1] if insert.endswith(" ") else insert
                if raw in ("command:", "command-edit:"):
                    rows.append([insert, "binding-prefix", "binding command rhs", ""])
                    continue
                a = self.actions.get(raw)
                if a is not None:
                    rows.append([insert, "action", str(a.doc or ""), "binding rhs"])
                    continue
                rows.append([insert, "", "", ""])
            return rows

        return [[str(c), "", "", ""] for c in candidates]

    def _prompt_suggestion_rows(
        self,
        *,
        cmd: str,
        toks: list[str],
        tok_i: int,
        candidates: list[str],
        path_mode: bool = False,
    ) -> list[list[str]]:
        if path_mode:
            return [self._prompt_path_row(c) for c in candidates]
        if cmd in ("bind", "bindmode"):
            return self._prompt_bind_suggestion_rows(cmd=cmd, toks=toks, tok_i=tok_i, candidates=candidates)
        return self._prompt_commandish_suggestion_rows(cmd=cmd, toks=toks, tok_i=tok_i, candidates=candidates)

    def _prompt_action_spec_prefix_candidates(
        self,
        prefix: str,
        *,
        at_eol: bool,
    ) -> tuple[list[str], bool]:
        names = list(self.actions.names()) + ["command:", "command-edit:"]
        chosen, fuzzy = self._completion_candidates_for_prefix(names, prefix, at_eol=False)
        out: list[str] = []
        for c in chosen:
            if c.endswith(":"):
                out.append(c)
            elif at_eol:
                out.append(c + " ")
            else:
                out.append(c)
        return (out, fuzzy)

    def _prompt_bind_action_candidates(
        self,
        *,
        cmd: str,
        toks: list[str],
        tok_i: int,
        prefix: str,
        at_eol: bool,
    ) -> tuple[list[str], bool]:
        if cmd == "bind":
            action_tok_i = 2
        elif cmd == "bindmode":
            action_tok_i = 3
        else:
            return ([], False)

        if tok_i < action_tok_i or len(toks) <= action_tok_i:
            return ([], False)

        action_head = toks[action_tok_i]
        for lead in ("command-edit:", "command:"):
            if action_head.startswith(lead):
                first = action_head[len(lead) :]
                nested_toks = [first] + toks[action_tok_i + 1 :]
                nested_tok_i = tok_i - action_tok_i
                nested_cmd = nested_toks[0] if nested_toks else ""
                nested_prefix = first if nested_tok_i == 0 else prefix
                candidates, fuzzy = self._prompt_command_token_candidates(
                    cmd=nested_cmd,
                    toks=nested_toks,
                    tok_i=nested_tok_i,
                    prefix=nested_prefix,
                    at_eol=at_eol,
                )
                if nested_tok_i == 0:
                    candidates = [lead + c for c in candidates]
                return (candidates, fuzzy)

        if tok_i == action_tok_i:
            return self._prompt_action_spec_prefix_candidates(prefix, at_eol=at_eol)
        return ([], False)

    def _prompt_command_token_candidates(
        self,
        *,
        cmd: str,
        toks: list[str],
        tok_i: int,
        prefix: str,
        at_eol: bool,
    ) -> tuple[list[str], bool]:
        if tok_i == 0:
            return self._completion_candidates_for_prefix(
                self.command_dispatcher.names(),
                prefix,
                at_eol=at_eol,
            )
        if tok_i == 1 and cmd in ("set", "setlocal", "show", "toggle", "togglelocal"):
            return self._completion_candidates_for_prefix(
                [spec.name for spec in self.options.list_specs(include_aliases=True)],
                prefix,
                at_eol=at_eol,
            )
        if tok_i == 2 and cmd in ("set", "setlocal") and len(toks) >= 2:
            return self._prompt_option_value_candidates(toks[1], prefix, at_eol=at_eol)
        if tok_i == 1 and cmd in ("help", "apropos"):
            return self._completion_candidates_for_prefix(
                self._prompt_help_topic_names(),
                prefix,
                at_eol=at_eol,
            )
        if tok_i == 1 and cmd == "commandpick":
            return self._completion_candidates_for_prefix(
                self._prompt_command_palette_names(),
                prefix,
                at_eol=at_eol,
            )
        if tok_i == 1 and cmd == "showcmd":
            return self._completion_candidates_for_prefix(
                list(self.command_dispatcher.names()),
                prefix,
                at_eol=at_eol,
            )
        if tok_i == 1 and cmd == "showhook":
            return self._completion_candidates_for_prefix(
                self._prompt_hook_names(),
                prefix,
                at_eol=at_eol,
            )
        if tok_i == 1 and cmd == "showword":
            return self._completion_candidates_for_prefix(
                self._prompt_vm_word_names(),
                prefix,
                at_eol=at_eol,
            )

        if tok_i == 1 and cmd == "buffer":
            return self._completion_candidates_for_prefix(
                self.buffer_names(),
                prefix,
                at_eol=at_eol,
            )
        if tok_i == 1 and cmd in ("mark", "markjump"):
            return self._completion_candidates_for_prefix(
                sorted(list(self.marks.keys())),
                prefix,
                at_eol=at_eol,
            )
        if tok_i == 1 and cmd == "plugin":
            return self._completion_candidates_for_prefix(
                ["list", "reload", "info", "errors"],
                prefix,
                at_eol=at_eol,
            )
        if tok_i == 2 and cmd == "plugin" and len(toks) >= 2:
            sub = str(toks[1])
            if sub == "reload":
                if self.plugin_manager:
                    return self._completion_candidates_for_prefix(
                        list(self.plugin_manager.plugins.keys()),
                        prefix,
                        at_eol=at_eol,
                    )
                return ([], False)
            if sub in ("info", "errors"):
                return self._completion_candidates_for_prefix(
                    self.plugin_names(),
                    prefix,
                    at_eol=at_eol,
                )
        if tok_i == 1 and cmd == "macro":
            return self._completion_candidates_for_prefix(
                ["record", "stop", "cancel", "play", "list"],
                prefix,
                at_eol=at_eol,
            )
        if tok_i == 2 and cmd == "macro" and len(toks) >= 2 and toks[1] in ("play", "record", "rec", "start"):
            return self._completion_candidates_for_prefix(
                list(self.macros.keys()),
                prefix,
                at_eol=at_eol,
            )
        if tok_i == 1 and cmd in ("keymode", "pushkeymode", "pushkeymode-once", "prefixmode"):
            mode_names = [m for m in self._prompt_known_keymodes() if m != "global"]
            if cmd == "keymode":
                mode_names = ["global"] + mode_names
            return self._completion_candidates_for_prefix(
                mode_names,
                prefix,
                at_eol=at_eol,
            )
        if tok_i == 1 and cmd == "showbindings":
            return self._completion_candidates_for_prefix(
                ["active"] + self._prompt_known_keymodes(),
                prefix,
                at_eol=at_eol,
            )
        if tok_i == 1 and cmd in ("bindmode", "bindmodedoc", "unbindmode"):
            mode_names = [m for m in self._prompt_known_keymodes() if m != "global"]
            return self._completion_candidates_for_prefix(
                mode_names,
                prefix,
                at_eol=at_eol,
            )
        if tok_i == 1 and cmd == "bindmodeprefix":
            mode_names = [m for m in self._prompt_known_keymodes() if m != "global"]
            return self._completion_candidates_for_prefix(
                mode_names,
                prefix,
                at_eol=at_eol,
            )
        if tok_i == 3 and cmd == "bindmodeprefix":
            mode_names = [m for m in self._prompt_known_keymodes() if m != "global"]
            return self._completion_candidates_for_prefix(
                mode_names,
                prefix,
                at_eol=at_eol,
            )
        if cmd in ("bind", "bindmode"):
            return self._prompt_bind_action_candidates(
                cmd=cmd,
                toks=toks,
                tok_i=tok_i,
                prefix=prefix,
                at_eol=at_eol,
            )
        return ([], False)

    # ----- keymap modes -----
    def active_key_mode_rows(self) -> list[list[object]]:
        out: list[list[object]] = []
        seen: set[str] = set()
        for km in reversed(self.key_mode_stack):
            m = str(km.name)
            if not m or m == 'global' or m in seen:
                continue
            seen.add(m)
            out.append([m, 1 if km.once else 0])
        return out

    def active_key_modes(self) -> list[str]:
        return [str(row[0]) for row in self.active_key_mode_rows()]

    def current_key_mode(self) -> str | None:
        modes = self.active_key_modes()
        return modes[0] if modes else None

    def current_key_mode_once(self) -> bool:
        rows = self.active_key_mode_rows()
        return bool(rows and rows[0][1])

    def current_capture_key_mode(self) -> str | None:
        if not self.key_mode_stack:
            return None
        top = self.key_mode_stack[-1]
        if getattr(top, "capture", False):
            return str(top.name)
        return None

    def current_key_mode_capture(self) -> bool:
        return self.current_capture_key_mode() is not None

    def set_key_mode(self, mode: str | None, *, capture: bool = False) -> None:
        if mode is None or str(mode) == '' or str(mode) == 'global':
            self.key_mode_stack = []
            return
        self.key_mode_stack = [ActiveKeyMode(str(mode), once=False, capture=bool(capture))]

    def push_key_mode(self, mode: str, *, once: bool = False, capture: bool = False) -> None:
        m = str(mode)
        if not m or m == 'global':
            return
        self.key_mode_stack.append(ActiveKeyMode(m, once=bool(once), capture=bool(capture)))

    def pop_key_mode(self) -> str | None:
        if not self.key_mode_stack:
            return None
        return self.key_mode_stack.pop().name

    def _install_builtin_keymode_bindings(self) -> None:
        """Install tiny internal keymode bindings that must work without plugins.

        Plugins are expected to provide the full default keymap, but some
        modal/editor-internal loops (like query-replace) should remain usable
        even in a headless test harness or minimal embed.
        """

        # Query-replace confirmation loop (capture mode).
        self.keymap.bind("y", "QueryReplaceYes", mode="qreplace")
        self.keymap.bind("Y", "QueryReplaceYes", mode="qreplace")
        self.keymap.bind("Enter", "QueryReplaceYes", mode="qreplace")

        self.keymap.bind("n", "QueryReplaceNo", mode="qreplace")
        self.keymap.bind("N", "QueryReplaceNo", mode="qreplace")

        self.keymap.bind("a", "QueryReplaceAll", mode="qreplace")
        self.keymap.bind("A", "QueryReplaceAll", mode="qreplace")

        self.keymap.bind("l", "QueryReplaceLast", mode="qreplace")
        self.keymap.bind("L", "QueryReplaceLast", mode="qreplace")

        self.keymap.bind("q", "QueryReplaceQuit", mode="qreplace")
        self.keymap.bind("Q", "QueryReplaceQuit", mode="qreplace")
        self.keymap.bind("Esc", "QueryReplaceQuit", mode="qreplace")

        # External URL open confirmation loop (capture mode).
        # This keeps docs browsing safe-by-default even when cap.open-url is enabled.
        self.keymap.bind("y", "OpenUrlYes", mode="openurl")
        self.keymap.bind("Y", "OpenUrlYes", mode="openurl")
        self.keymap.bind("Enter", "OpenUrlYes", mode="openurl")

        self.keymap.bind("n", "OpenUrlNo", mode="openurl")
        self.keymap.bind("N", "OpenUrlNo", mode="openurl")
        self.keymap.bind("Esc", "OpenUrlNo", mode="openurl")

        self.keymap.bind("c", "OpenUrlCopy", mode="openurl")
        self.keymap.bind("C", "OpenUrlCopy", mode="openurl")

        # Prompt picker navigation (non-command prompts).
        # This makes built-in pickers usable even without plugins.
        self.keymap.bind("UpArrow", "PromptSuggestPrev|PromptHistoryPrev", mode="prompt")
        self.keymap.bind("DownArrow", "PromptSuggestNext|PromptHistoryNext", mode="prompt")
        # PageUp/PageDown jump by a small window in picker lists (without mutating the query).
        # For command/find prompts, these fall back to history navigation.
        self.keymap.bind("PageUp", "PromptSuggestPageUp|PromptHistoryPrev", mode="prompt")
        self.keymap.bind("PageDown", "PromptSuggestPageDown|PromptHistoryNext", mode="prompt")
        # Section jumps for grouped suggestion lists.
        self.keymap.bind("Alt-UpArrow", "PromptSuggestPrevSection", mode="prompt")
        self.keymap.bind("Alt-DownArrow", "PromptSuggestNextSection", mode="prompt")
        self.keymap.bind("Ctrl-y", "PromptCopySelected", mode="prompt")
        self.keymap.bind("Ctrl-Home", "PromptSuggestFirst|PromptHome", mode="prompt")
        self.keymap.bind("Ctrl-End", "PromptSuggestLast|PromptEnd", mode="prompt")

    # ----- prompt keymode -----
    def _push_prompt_keymode(self) -> None:
        # Reserve the keymap mode name "prompt" for the built-in prompt bar.
        self.key_mode_stack = [km for km in self.key_mode_stack if km.name != 'prompt']
        self.key_mode_stack.append(ActiveKeyMode('prompt', once=False))

    def _pop_prompt_keymode(self) -> None:
        self.key_mode_stack = [km for km in self.key_mode_stack if km.name != 'prompt']

    def resolve_key_binding(self, key: str):
        return self.keymap.get_binding(key, modes=self.active_key_modes())

    def binding_desc(self, binding: object) -> str:
        b = binding
        desc = str(getattr(b, 'desc', '') or '').strip()
        if desc:
            return desc

        spec = str(getattr(b, 'action_spec', '') or '').strip()
        if not spec:
            return ''
        steps = parse_action_chain(spec)
        if not steps:
            return ''

        def _short_doc(doc: str) -> str:
            d = str(doc).strip()
            if ' - ' in d:
                return d.split(' - ', 1)[1].strip()
            return d

        def _step_desc(action: str) -> str:
            act = str(action).strip()
            if not act:
                return ''
            if act.startswith('command:'):
                tail = act[len('command:') :].strip()
                if not tail:
                    return ''
                try:
                    cl = parse_cmdline(tail)
                except Exception:
                    cl = None
                name = cl.name if cl is not None else tail.split(None, 1)[0]
                cmd = self.command_dispatcher.get(name)
                if cmd is not None and cmd.doc:
                    return _short_doc(cmd.doc)
            a = self.actions.get(act)
            if a is not None and a.doc:
                return _short_doc(a.doc)
            return ''

        first = _step_desc(steps[0].action)
        if len(steps) <= 1:
            return first
        if first:
            return first + ' …'
        return ''

    def available_binding_rows(self) -> list[list[object]]:
        return self.keymap.resolved_binding_rows(self.active_key_modes())

    def available_binding_info_rows(self) -> list[list[object]]:
        rows = self.keymap.resolved_binding_info_rows(self.active_key_modes())
        out: list[list[object]] = []
        for mode, key, action, desc, group, span in rows:
            resolved_desc = str(desc) if desc not in (0, None, '') else self.binding_desc(
                self.keymap.get_binding(str(key), modes=[str(mode)])
            )
            out.append([mode, key, action, resolved_desc or 0, group, span])
        return out

    def resolve_key_info_row(self, key: str) -> list[object] | int:
        row = self.keymap.resolved_binding_info_row(key, modes=self.active_key_modes())
        if row == 0:
            return 0
        mode, key2, action, desc, group, span = row
        if desc in (0, None, ''):
            b = self.resolve_key_binding(str(key))
            desc = self.binding_desc(b) if b is not None else ''
        return [mode, key2, action, desc or 0, group, span]

    def binding_info_rows_for(self, mode: str | None = None) -> list[list[object]]:
        rows = self.keymap.binding_info_rows_for(mode)
        out: list[list[object]] = []
        for key, action, desc, group, span in rows:
            resolved_desc = str(desc) if desc not in (0, None, '') else self.binding_desc(
                self.keymap.get_binding(str(key), modes=[('global' if mode is None else str(mode))])
            )
            out.append([key, action, resolved_desc or 0, group, span])
        return out

    def dispatch_key(self, key: str) -> bool:
        """Resolve and execute a bound key.

        One-shot keymodes get first crack at the next key press. If the key is
        not bound in the topmost one-shot mode, that mode is popped and lookup
        falls through to the remaining active modes and global bindings.
        """

        while self.key_mode_stack and self.key_mode_stack[-1].once:
            top = self.key_mode_stack[-1]
            b = self.keymap.get_binding(key, modes=[top.name])
            if b is not None:
                try:
                    return self.run_action_chain(b.action_spec)
                finally:
                    if self.key_mode_stack and self.key_mode_stack[-1] == top:
                        self.key_mode_stack.pop()
            self.key_mode_stack.pop()

        # Capture modes intercept all keypresses: if a key is not bound in the
        # active capture mode, it does not fall through to global bindings.
        if self.key_mode_stack and getattr(self.key_mode_stack[-1], 'capture', False):
            top = self.key_mode_stack[-1]
            b = self.keymap.get_binding(key, modes=[top.name])
            if b is None:
                return False
            try:
                return self.run_action_chain(b.action_spec)
            finally:
                if top.once and self.key_mode_stack and self.key_mode_stack[-1] == top:
                    self.key_mode_stack.pop()

        # Docs/help buffers act like a tiny in-editor browser:
        # - Enter follows the markdown link under cursor (best-effort).
        # - Backspace goes back in the docs navigation stack.
        # - y copies the link target under cursor (like "copy link address").
        if self.prompt is None and self.current_help_doc_topic():
            if key == "Enter":
                return bool(self.help_follow())
            if key == "Backspace":
                return bool(self.help_back())
            if key in {"y", "Y"}:
                return bool(self.help_copy_link_target())


        b = self.resolve_key_binding(key)
        if b is None:
            # Fallback: treat unbound printable keys as text input.
            # - when a prompt is active, edit the prompt
            # - otherwise, insert into the buffer
            if len(key) == 1 and key.isprintable() and key not in ('\n', '\r', '\t'):
                self.input['text'] = key
                return self.run_action('PromptInsertText' if self.prompt is not None else 'InsertText')
            return False
        return self.run_action_chain(b.action_spec)

    def _emit_mx_hook(self, hook_word: str, *args: Any) -> None:
        """Fire a micromax hook word if present.

        Hooks are best-effort: exceptions are caught and recorded as messages.
        Hook handlers run in the editor's embedded VM but are treated as
        notifications: we discard any stack effects after the call.
        """

        try:
            if self.vm.find_word(hook_word) is None:
                return
            depth = len(self.vm.stack)
            self.vm.stack.extend(args)
            self.vm.eval(hook_word, filename="<editor-hook>")
            del self.vm.stack[depth:]
        except Exception as e:
            self.message(f"hook {hook_word}: error: {e}")

    # ----- undo snapshot helpers -----
    def _snapshot_buffer_state(self, eb: EditorBuffer) -> tuple[str, list[Cursor], list[Cursor | None], list[int], int]:
        self._normalize_cursor_lists(eb)
        return (
            eb.buf.get_text(),
            [Cursor(c.line, c.col) for c in eb.cursors],
            [Cursor(a.line, a.col) if a else None for a in eb.sel_anchors],
            [int(x) for x in eb.cursor_ids],
            int(eb.primary),
        )

    def _restore_buffer_state(self, eb: EditorBuffer, snap: tuple[str, list[Cursor], list[Cursor | None], list[int], int]) -> None:
        text, curs, anchors, cursor_ids, primary = snap
        eb.buf.set_text(text)
        eb.cursors[:] = [Cursor(c.line, c.col) for c in curs]
        eb.sel_anchors[:] = [Cursor(a.line, a.col) if a else None for a in anchors]
        eb.cursor_ids[:] = [int(x) for x in cursor_ids]
        eb.primary = int(primary)
        self._normalize_cursor_lists(eb)

    def _record_undo_snapshot(
        self,
        eb: EditorBuffer,
        before: tuple[str, list[Cursor], list[Cursor | None], list[int], int],
        after: tuple[str, list[Cursor], list[Cursor | None], list[int], int],
        desc: str,
    ) -> None:
        def _undo() -> None:
            self._restore_buffer_state(eb, before)

        def _redo() -> None:
            self._restore_buffer_state(eb, after)

        def _target() -> str:
            name = str(getattr(eb.buf, "path", "") or getattr(eb, "name", "") or "").strip()
            self._normalize_cursor_lists(eb)
            if eb.cursors:
                c = eb.cursors[eb.primary]
                if name:
                    return f"{name} @ {c.line + 1}:{c.col}"
                return f"{c.line + 1}:{c.col}"
            return name

        self.undo.record(Edit(undo=_undo, redo=_redo, description=desc, target=_target))

    def _sync_buffer_fastdirty_mode(self, eb: EditorBuffer) -> None:
        try:
            eb.buf.set_fastdirty(bool(self.options.get("fastdirty", local=eb.local_options)))
        except Exception:
            pass

    def _sync_all_buffer_fastdirty_modes(self) -> None:
        for eb in self.buffers.values():
            self._sync_buffer_fastdirty_mode(eb)

    # ----- buffers -----
    def new_buffer(
        self,
        name: str = "*scratch*",
        text: str = "",
        *,
        path: str | None = None,
        fileformat: str | None = None,
        encoding: str | None = None,
    ) -> None:
        cid = self._alloc_cursor_id()
        ft = detect_filetype(str(path or ""), str(text or ""))
        ff = str(fileformat or self.options.get("fileformat") or "unix").strip().lower()
        if ff not in ("unix", "dos"):
            ff = "unix"
        enc = str(encoding or self.options.get("encoding") or "utf-8").strip() or "utf-8"
        self.buffers[name] = EditorBuffer(
            name=name,
            buf=Buffer(text, path=path),
            cursors=[Cursor(0, 0)],
            sel_anchors=[None],
            cursor_ids=[cid],
            primary=0,
            local_options={"filetype": ft, "fileformat": ff, "encoding": enc},
        )
        self._sync_buffer_fastdirty_mode(self.buffers[name])
        self._activate_buffer(name)

    def filetype(self) -> str:
        """Return the active buffer's detected filetype."""
        eb = self.cur()
        ft = eb.local_options.get("filetype")
        if isinstance(ft, str) and ft:
            return ft
        # Best-effort fallback.
        ft2 = detect_filetype(str(eb.buf.path or ""), eb.buf.get_text())
        eb.local_options["filetype"] = ft2
        return ft2

    def _update_buffer_path(self, eb: EditorBuffer, path: str) -> None:
        eb.buf.path = str(path)
        eb.local_options["filetype"] = detect_filetype(str(path), eb.buf.get_text())

    def _autosave_seconds(self, eb: EditorBuffer) -> int:
        try:
            raw = self.options.get("autosave", local=eb.local_options)
            return max(0, int(raw or 0))
        except Exception:
            return 0

    def _note_buffer_changed(self, eb: EditorBuffer) -> None:
        if not bool(getattr(eb.buf, "dirty", False)):
            eb.autosave_dirty_since = None
            return
        if self._autosave_seconds(eb) <= 0:
            eb.autosave_dirty_since = None
            return
        if not str(getattr(eb.buf, "path", "") or ""):
            eb.autosave_dirty_since = None
            return
        if bool(self.options.get("readonly", local=eb.local_options)):
            eb.autosave_dirty_since = None
            return
        eb.autosave_dirty_since = self.now()

    def _arm_autosave_if_needed(self, eb: EditorBuffer, *, now: float | None = None) -> None:
        if not bool(getattr(eb.buf, "dirty", False)):
            eb.autosave_dirty_since = None
            return
        if self._autosave_seconds(eb) <= 0:
            eb.autosave_dirty_since = None
            return
        if not str(getattr(eb.buf, "path", "") or ""):
            eb.autosave_dirty_since = None
            return
        if bool(self.options.get("readonly", local=eb.local_options)):
            eb.autosave_dirty_since = None
            return
        if eb.autosave_dirty_since is None:
            eb.autosave_dirty_since = float(self.now() if now is None else now)

    def _autosave_buffer_due(self, eb: EditorBuffer, *, now: float | None = None) -> bool:
        when = float(self.now() if now is None else now)
        self._arm_autosave_if_needed(eb, now=when)
        since = eb.autosave_dirty_since
        if since is None:
            return False
        secs = self._autosave_seconds(eb)
        if secs <= 0:
            return False
        return (when - float(since)) >= float(secs)

    def _detect_fileformat_from_text(self, text: str) -> str:
        """Return a tiny line-ending format guess for opened text."""

        s = str(text or "")
        i = s.find("\n")
        if i > 0 and s[i - 1] == "\r":
            return "dos"
        return "unix"

    def _normalize_encoding_name(self, raw: object) -> str:
        """Return a usable codec name (best-effort)."""

        enc = str(raw or "").strip() or "utf-8"
        try:
            return str(codecs.lookup(enc).name or enc)
        except LookupError:
            return enc

    def _persist_enabled(self) -> bool:
        """Return True if editor-owned persistence is enabled (cap.persist)."""

        try:
            return bool(self.options.get("cap.persist"))
        except Exception:
            return False

    def _persist_store_path(self, raw: str, *, default: str) -> Path | None:
        """Resolve a persistence file path under cap.persist-root (best-effort)."""

        if not self._persist_enabled():
            return None

        s = str(raw or "").strip() or str(default or "").strip()
        if not s:
            return None

        p = persist_resolve_path(self, s)
        if not persist_path_allowed(self, p):
            self.message(persist_deny_reason(self, p))
            return None
        return p

    def _recent_store_path(self) -> Path | None:
        """Return the configured recent-files persistence path (or None)."""

        raw = os.environ.get("MICROMAX_RECENT_FILE") or str(self.options.get("recent.file") or "")
        return self._persist_store_path(raw, default="~/.config/micromax/recent.json")

    def load_recent_files(self) -> bool:
        """Load recent file MRU from disk (best-effort).

        This is gated by options:
        - `recent.persist` (opt-in)
        - `cap.persist` (unsafe; off by default)

        Returns True when a file existed and was loaded.
        """
        if not bool(self.options.get("recent.persist")):
            return False
        p = self._recent_store_path()
        if p is None:
            return False
        if not p.exists() or p.is_dir():
            return False
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            if isinstance(data, list):
                xs = [str(x) for x in data if isinstance(x, (str, int, float))]
                out: list[str] = []
                seen: set[str] = set()
                for raw in xs:
                    n = self._normalize_path(str(raw))
                    if not n or n in seen:
                        continue
                    seen.add(n)
                    out.append(str(raw))
                self.recent_files[:] = out[: int(self._recent_limit)]
        except Exception as e:
            self.message(f"recent load error: {e}")
            return False
        return True

    def save_recent_files(self) -> bool:
        """Persist recent file MRU to disk (best-effort)."""
        if not bool(self.options.get("recent.persist")):
            return False
        p = self._recent_store_path()
        if p is None:
            return False
        try:
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(json.dumps(list(self.recent_files), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        except Exception as e:
            self.message(f"recent save error: {e}")
            return False
        return True

    def _history_store_path(self) -> Path | None:
        """Return the configured prompt-history persistence path (or None)."""

        raw = os.environ.get("MICROMAX_HISTORY_FILE") or str(self.options.get("history.file") or "")
        return self._persist_store_path(raw, default="~/.config/micromax/history.json")

    def load_prompt_history(self) -> bool:
        """Load prompt history from disk (best-effort).

        This is gated by options:
        - `history.persist` (opt-in)
        - `cap.persist` (unsafe; off by default)

        Returns True when a file existed and was loaded.
        """

        if not bool(self.options.get("history.persist")):
            return False
        p = self._history_store_path()
        if p is None:
            return False
        if not p.exists() or p.is_dir():
            return False

        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except Exception as e:
            self.message(f"history load error: {e}")
            return False

        limit = 200
        try:
            limit = max(1, int(self.options.get("history.limit")))
        except Exception:
            limit = 200

        def _norm_list(v: object) -> list[str]:
            if not isinstance(v, list):
                return []
            out: list[str] = []
            for it in v:
                if isinstance(it, (str, int, float)):
                    s = str(it).strip("\n")
                    if s:
                        out.append(s)
            # Clamp to last N (most recent).
            return out[-limit:]

        if isinstance(data, dict):
            for k, v in data.items():
                kk = str(k)
                xs = _norm_list(v)
                if xs:
                    self.history[kk] = xs
        elif isinstance(data, list):
            # Legacy: treat a bare list as command history.
            xs = _norm_list(data)
            if xs:
                self.history["command"] = xs
        else:
            return False

        return True

    def save_prompt_history(self) -> bool:
        """Persist prompt history to disk (best-effort)."""

        if not bool(self.options.get("history.persist")):
            return False
        p = self._history_store_path()
        if p is None:
            return False

        limit = 200
        try:
            limit = max(1, int(self.options.get("history.limit")))
        except Exception:
            limit = 200

        # Clamp each kind and keep the JSON deterministic.
        data: dict[str, list[str]] = {}
        for k in sorted(self.history.keys(), key=lambda x: str(x)):
            xs = self.history.get(k, [])
            if not isinstance(xs, list):
                continue
            out: list[str] = []
            for it in xs:
                s = str(it).strip("\n")
                if s:
                    out.append(s)
            if out:
                data[str(k)] = out[-limit:]

        try:
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        except Exception as e:
            self.message(f"history save error: {e}")
            return False

        return True

    def _cursor_store_path(self) -> Path | None:
        """Return the configured savecursor persistence path (or None)."""

        raw = os.environ.get("MICROMAX_CURSOR_FILE") or str(self.options.get("savecursor.file") or "")
        return self._persist_store_path(raw, default="~/.config/micromax/cursor.json")

    def load_saved_cursors(self) -> bool:
        """Load saved primary-cursor positions from disk (best-effort).

        This is gated by options:
        - `savecursor` (opt-in)
        - `cap.persist` (unsafe; off by default)

        Returns True when a file existed and was loaded.
        """

        if not bool(self.options.get("savecursor")):
            return False
        p = self._cursor_store_path()
        if p is None:
            return False
        if not p.exists() or p.is_dir():
            return False

        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except Exception as e:
            self.message(f"savecursor load error: {e}")
            return False

        if not isinstance(data, dict):
            return False

        out: dict[str, dict[str, int]] = {}
        for raw_path, raw_pos in data.items():
            norm = self._normalize_path(str(raw_path))
            if not norm:
                continue
            line = 0
            col = 0
            try:
                if isinstance(raw_pos, dict):
                    line = max(0, int(raw_pos.get("line", 0) or 0))
                    col = max(0, int(raw_pos.get("col", 0) or 0))
                elif isinstance(raw_pos, (list, tuple)) and len(raw_pos) >= 2:
                    line = max(0, int(raw_pos[0] or 0))
                    col = max(0, int(raw_pos[1] or 0))
                else:
                    continue
            except Exception:
                continue
            out[norm] = {"line": int(line), "col": int(col)}

        self._saved_cursors = out
        return True

    def save_saved_cursors(self) -> bool:
        """Persist saved primary-cursor positions to disk (best-effort)."""

        if not bool(self.options.get("savecursor")):
            return False
        p = self._cursor_store_path()
        if p is None:
            return False

        data: dict[str, dict[str, int]] = {}
        for key in sorted(self._saved_cursors.keys()):
            item = self._saved_cursors.get(key)
            if not isinstance(item, dict):
                continue
            try:
                data[str(key)] = {
                    "line": max(0, int(item.get("line", 0) or 0)),
                    "col": max(0, int(item.get("col", 0) or 0)),
                }
            except Exception:
                continue

        try:
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        except Exception as e:
            self.message(f"savecursor save error: {e}")
            return False
        return True

    def _remember_cursor_for_buffer(self, eb: EditorBuffer | None) -> bool:
        """Remember one buffer's primary cursor position (best-effort)."""

        if eb is None or not bool(self.options.get("savecursor")):
            return False
        raw = str(getattr(eb.buf, "path", "") or "")
        norm = self._normalize_path(raw)
        if not norm:
            return False
        self._normalize_cursor_lists(eb)
        c = eb.cursors[eb.primary]
        self._saved_cursors[norm] = {"line": max(0, int(c.line)), "col": max(0, int(c.col))}
        try:
            self.save_saved_cursors()
        except Exception:
            pass
        return True

    def _restore_cursor_for_buffer(self, eb: EditorBuffer | None) -> bool:
        """Restore one buffer's primary cursor position when available."""

        if eb is None or not bool(self.options.get("savecursor")):
            return False
        raw = str(getattr(eb.buf, "path", "") or "")
        norm = self._normalize_path(raw)
        if not norm:
            return False
        item = self._saved_cursors.get(norm)
        if not isinstance(item, dict):
            return False

        self._normalize_cursor_lists(eb)
        c = eb.cursors[eb.primary]
        try:
            line = max(0, int(item.get("line", 0) or 0))
            col = max(0, int(item.get("col", 0) or 0))
        except Exception:
            return False
        max_line = max(0, len(eb.buf.lines) - 1)
        c.line = min(line, max_line)
        try:
            max_col = len(str(eb.buf.lines[c.line]))
        except Exception:
            max_col = 0
        c.col = min(col, max(0, max_col))
        eb.sel_anchors[eb.primary] = None
        self._normalize_cursor_lists(eb)
        return True

    def _project_root_for_path(self, path: str) -> str:
        """Best-effort project root: walk up looking for .git/.hg/.svn/pyproject/etc."""
        raw = str(path or "")
        if not raw:
            return ""
        try:
            p = Path(raw).expanduser().resolve(strict=False)
        except Exception:
            p = Path(raw).expanduser()
        cur = p.parent if p.is_file() else p
        for _ in range(8):
            if not cur:
                break
            try:
                if (cur / '.git').exists() or (cur / '.hg').exists() or (cur / '.svn').exists():
                    return str(cur)
                if (cur / 'pyproject.toml').exists() or (cur / 'package.json').exists() or (cur / 'Cargo.toml').exists():
                    return str(cur)
            except Exception:
                pass
            if cur.parent == cur:
                break
            cur = cur.parent
        return ""

    def _normalize_path(self, path: str) -> str:
        """Best-effort normalize a filesystem path for comparisons/MRUs.

        We keep buffer names stable (what the user typed) but use normalization
        for deduping and matching *the same file* across relative/tilde paths.
        """
        raw = str(path or "")
        if not raw:
            return ""
        p = Path(raw).expanduser()
        try:
            return str(p.resolve(strict=False))
        except Exception:
            return str(p)

    def _push_recent_file(self, path: str) -> None:
        """Insert path into the recent-files MRU (front).

        Recent lists are intentionally tiny and deterministic: we keep them
        headless-friendly and make no attempt to persist yet.
        """
        raw = str(path or "")
        if raw == "":
            return
        norm = self._normalize_path(raw)
        if norm == "":
            return
        # Dedup by normalized path, but keep the stored string stable-ish.
        for i, existing in enumerate(list(self.recent_files)):
            if self._normalize_path(existing) == norm:
                del self.recent_files[i]
                break
        self.recent_files.insert(0, raw)
        if len(self.recent_files) > int(self._recent_limit):
            self.recent_files[:] = self.recent_files[: int(self._recent_limit)]

        try:
            self.save_recent_files()
        except Exception:
            pass

    def clear_recent_files(self) -> None:
        self.recent_files.clear()
        try:
            self.save_recent_files()
        except Exception:
            pass

    def recent_prompt_rows(self) -> list[list[str]]:
        """Rows for the recent-file picker: [[path kind menu info] ...]."""
        out: list[list[str]] = []
        for raw in self.recent_files:
            p = str(raw)
            try:
                pp = Path(p)
                menu = str(pp.name) if pp.name else "file"
                info = str(pp.parent) if str(pp.parent) not in (".", "") else ""
            except Exception:
                menu, info = "file", ""
            out.append([p, "recent", menu, info])
        return out

    def _recent_section_label(self, row: list[str], *, by_project: bool = True) -> str:
        """Best-effort visible section label for recent-file rows.

        Recent-file pickers already expose grouped rows headlessly; this helper
        keeps the live prompt, TUI headers, section jumps, preview/status, and
        hostcalls aligned on the same small grouping policy.
        """

        path = str(row[0] if row else "")
        if by_project:
            try:
                root = self._project_root_for_path(path)
            except Exception:
                root = ""
            if root:
                return str(root)
        return self._path_parent_section_label(path, fallback="Recent Files")

    def _recent_section_row(self, row: list[str], *, by_project: bool = True) -> list[str]:
        """Return a recent picker row rewritten for its visible section.

        When a project root is known, make the row a little more scan-friendly by
        showing the project name + path relative to that root, similar to the
        grouped headless hostcall shape.
        """

        vals = [str(x) for x in list(row[:4])]
        while len(vals) < 4:
            vals.append("")
        if not by_project:
            return vals
        path = str(vals[0])
        root = self._project_root_for_path(path)
        if not root:
            return vals
        try:
            rel = str(Path(path).expanduser().resolve(strict=False).relative_to(Path(root)))
        except Exception:
            rel = str(Path(path).name)
        vals[2] = str(Path(root).name or "project")
        vals[3] = rel
        return vals

    def _recent_section_rows(self, query: str = "", *, limit: int | None = None, by_project: bool = True) -> list[list[object]]:
        """Group recent-file rows by visible section label.

        Groups preserve the first-seen section order from the MRU/apropos row
        stream so recent-file pickers stay recency-friendly instead of sorting
        buckets alphabetically.
        """

        rows = self.recent_apropos_rows(query, limit=limit)
        buckets: dict[str, list[list[str]]] = {}
        order: list[str] = []
        for row in rows:
            vals = [str(x) for x in row[:4]]
            while len(vals) < 4:
                vals.append("")
            label = self._recent_section_label(vals, by_project=by_project)
            if label not in buckets:
                buckets[label] = []
                order.append(label)
            buckets[label].append(self._recent_section_row(vals, by_project=by_project))
        return [[label, buckets[label]] for label in order]

    def recent_apropos_rows(self, query: str, *, limit: int | None = None) -> list[list[str]]:
        q = str(query or "").strip()
        rows = self.recent_prompt_rows()
        if q == "":
            return rows[:limit] if limit is not None else rows
        scored: list[tuple[tuple[int, int, int, int, int, int, int, int, int, str], int, list[str]]] = []
        for idx, row in enumerate(rows):
            key = self._buffer_row_sort_key(row, q)
            if key is None:
                continue
            scored.append((key, idx, [str(x) for x in row]))
        scored.sort(key=lambda item: (item[0], item[1]))
        out2 = [row for _k, _idx, row in scored]
        return out2[:limit] if limit is not None else out2

    def recent_section_rows_by_dir(self, query: str = "", *, limit: int | None = None) -> list[list[object]]:
        """Group recent file rows into directory sections."""
        return self._recent_section_rows(query, limit=limit, by_project=False)

    def recent_section_rows_by_project(self, query: str = "", *, limit: int | None = None) -> list[list[object]]:
        """Group recent file rows into project-root sections (Helix-style)."""
        return self._recent_section_rows(query, limit=limit, by_project=True)

    # ----- docs/help buffers -----
    def docs_root(self) -> Path:
        """Return the docs root directory (best-effort).

        By default we look for a `docs/` directory relative to the current
        working directory (repo layout). This can be overridden via the
        MICROMAX_DOCS environment variable.
        """

        raw = os.environ.get("MICROMAX_DOCS") or "docs"
        p = Path(str(raw)).expanduser()
        if not p.is_absolute():
            p = (Path.cwd() / p)
        return p

    def _scan_docs(self) -> list[dict[str, str]]:
        """Return a small docs index as a list of dicts.

        Each entry contains: topic, path, title, summary.
        """

        root = self.docs_root()
        if not root.exists() or root.is_dir() is False:
            return []
        out: list[dict[str, str]] = []
        try:
            files = sorted([p for p in root.glob("*.md") if p.is_file()], key=lambda p: p.name.casefold())
        except Exception:
            files = []

        for p in files:
            stem = p.stem
            slug = re.sub(r"^\d+\-", "", stem)
            topic = slug or stem
            title = ""
            summary = ""
            try:
                txt = p.read_text(encoding="utf-8")
                lines = txt.splitlines()
                heading_scan = self._md_heading_scan(lines)
                heading_entries = [(line0, level, title0, frag0, col0) for line0, _line1, level, title0, frag0, col0 in heading_scan]
                heading_line_idxs = {int(k) for line0, line1, _level, _title0, _frag0, _col0 in heading_scan for k in range(int(line0), int(line1))}
                if heading_entries:
                    _line0, _level, title0, _frag0, _col0 = heading_entries[0]
                    title = str(title0 or "")
                for i, line in enumerate(lines):
                    s = line.strip()
                    if not s:
                        continue
                    if i in heading_line_idxs or _SETEXT_UNDERLINE_RE.match(s) is not None:
                        continue
                    if not title and s.startswith("#"):
                        title = s.lstrip("#").strip()
                        continue
                    if not summary and not s.startswith("#"):
                        summary = s
                        break
            except Exception:
                pass
            out.append({"topic": str(topic), "path": str(p), "title": str(title), "summary": str(summary)})
        return out

    def _docs_catalog(self) -> dict[str, dict[str, str]]:
        """Return a tiny cached docs catalog keyed by common target spellings."""

        cache = getattr(self, "_docs_catalog_cache", None)
        if isinstance(cache, dict) and cache:
            return dict(cache)

        out: dict[str, dict[str, str]] = {}
        for ent in self._scan_docs():
            topic = str(ent.get("topic", "") or "").strip()
            path = str(ent.get("path", "") or "").strip()
            title = str(ent.get("title", "") or "").strip()
            if not path:
                continue
            stem = Path(path).stem
            slug = re.sub(r"^\d+\-", "", stem) or stem
            entry = {"path": path, "title": title, "topic": topic or slug}
            keys = {topic, path, Path(path).name, stem, slug}
            for key in keys:
                k = str(key or "").strip().casefold()
                if k:
                    out.setdefault(k, entry)

        self._docs_catalog_cache = dict(out)
        return dict(out)

    def _help_doc_title_for_target(self, doc: str) -> str:
        """Resolve a docs target like ``94-softwrap.md`` to a human title."""

        raw = unquote(str(doc or "").strip())
        if not raw:
            return ""

        entry = self._docs_catalog().get(raw.casefold())
        if entry is not None:
            return str(entry.get("title", "") or "")

        path = self.find_doc_path(raw)
        if path:
            entry2 = self._docs_catalog().get(str(path).casefold())
            if entry2 is not None:
                return str(entry2.get("title", "") or "")
        return ""

    def _help_heading_titles_by_fragment(self) -> dict[str, str]:
        """Return current help-buffer heading titles keyed by resolved fragment."""

        topic = self.current_help_doc_topic()
        if not topic:
            return {}
        eb = self.cur()
        nlines = len(eb.buf.lines)
        if (
            topic == self._help_heading_title_cache_topic
            and nlines == self._help_heading_title_cache_nlines
        ):
            return dict(self._help_heading_title_cache)

        out: dict[str, str] = {}
        for _line0, _level, title, frag, _col0 in self._md_heading_entries(list(eb.buf.lines)):
            f = str(frag or "").strip()
            if f:
                out.setdefault(f, str(title or ""))

        self._help_heading_title_cache_topic = str(topic)
        self._help_heading_title_cache_nlines = int(nlines)
        self._help_heading_title_cache = dict(out)
        return dict(out)

    def _help_doc_heading_titles_for_target(self, doc: str) -> dict[str, str]:
        """Resolve a docs target to ``{fragment: title}`` heading metadata."""

        raw = unquote(str(doc or "").strip())
        if not raw:
            return self._help_heading_titles_by_fragment()

        entry = self._docs_catalog().get(raw.casefold())
        path = str(entry.get("path", "") or "") if entry is not None else ""
        if not path:
            path = self.find_doc_path(raw) or ""
        if not path:
            return {}
        key = self._normalize_path(path) or str(path)
        cache = getattr(self, "_docs_heading_title_cache", {})
        if key in cache:
            return dict(cache[key])

        out: dict[str, str] = {}
        try:
            lines = Path(path).read_text(encoding="utf-8").splitlines()
            for _line0, _level, title, frag, _col0 in self._md_heading_entries(lines):
                f = str(frag or "").strip()
                if f:
                    out.setdefault(f, str(title or ""))
        except Exception:
            out = {}

        cache[key] = dict(out)
        self._docs_heading_title_cache = cache
        return dict(out)

    def _doc_section_info_for_path(self, path: str) -> tuple[int, str]:
        """Best-effort visible section label for a docs path.

        The docs tree is intentionally numbered into coarse topical families,
        so the docs picker can expose those families as stable section labels
        without inventing a separate metadata file.
        """

        stem = Path(str(path or "")).stem
        m = re.match(r"^(\d+)(?:-|$)", stem)
        if m is None:
            return (999, "Docs")
        n = int(m.group(1), 10)
        if n < 10:
            return (0, "00–09 Project")
        if n < 20:
            return (10, "10–19 Research")
        if n < 30:
            return (20, "20–29 Language + VM")
        if n < 40:
            return (30, "30–39 Host + integration")
        if n < 50:
            return (40, "40–49 Planning")
        if n < 60:
            return (50, "50–59 Editor core")
        if n < 70:
            return (60, "60–69 Editor + host")
        if n < 80:
            return (70, "70–79 Tutorials + discovery")
        if n < 90:
            return (80, "80–89 Config + plugins")
        if n < 100:
            return (90, "90–99 Advanced notes")
        return (100, "100+ Feature notes")

    def _doc_section_label(self, row: list[str]) -> str:
        topic = str(row[0] if row else "")
        cache = getattr(self, "_doc_section_labels", {})
        if topic and topic in cache:
            return str(cache[topic])
        path = self.find_doc_path(topic) if topic else None
        if path:
            return str(self._doc_section_info_for_path(path)[1])
        return "Docs"

    def _doc_section_label_rank(self, label: str) -> tuple[int, str]:
        ranks = getattr(self, "_doc_section_label_ranks", {})
        if label in ranks:
            return (int(ranks[label]), str(label).casefold())
        return (999, str(label).casefold())

    def doc_prompt_rows(self) -> list[list[str]]:
        """Rows for docs picker: [[topic kind menu info] ...]."""

        out: list[list[str]] = []
        section_labels: dict[str, str] = {}
        section_ranks: dict[str, int] = {}
        for ent in self._scan_docs():
            topic = str(ent.get("topic", ""))
            path = str(ent.get("path", ""))
            title = str(ent.get("title", ""))
            summary = str(ent.get("summary", ""))
            menu = title or Path(path).name
            info = summary
            rank, section = self._doc_section_info_for_path(path)
            section_labels[topic] = section
            section_ranks.setdefault(section, int(rank))
            out.append([topic, "doc", menu, info])
        self._doc_section_labels = section_labels
        self._doc_section_label_ranks = section_ranks
        out.sort(
            key=lambda row: (
                self._doc_section_label_rank(self._doc_section_label(row)),
                str(row[0]).casefold(),
                str(row[2]).casefold(),
            )
        )
        return out

    def doc_section_rows(self, query: str = "", *, limit: int | None = None) -> list[list[object]]:
        """Group docs picker rows by their numbered docs family."""
        rows = self.doc_apropos_rows(query, limit=limit)
        return self._group_prompt_rows_by_section(
            rows,
            label_fn=self._doc_section_label,
            label_sort_key=self._doc_section_label_rank,
        )

    def doc_apropos_rows(self, query: str, *, limit: int | None = None) -> list[list[str]]:
        q = str(query or "").strip()
        rows = self.doc_prompt_rows()
        if q == "":
            return rows[:limit] if limit is not None else rows

        scored: list[tuple[tuple[int, int, int, int, int, int, int, int, int, str], int, list[str]]] = []
        for idx, row in enumerate(rows):
            key = self._apropos_row_sort_key(row, q)
            if key is None:
                continue
            scored.append((key, idx, [str(x) for x in row]))
        scored.sort(key=lambda item: (item[0], item[1]))
        out2 = [row for _k, _idx, row in scored]
        return out2[:limit] if limit is not None else out2

    def find_doc_path(self, topic_or_path: str) -> str | None:
        """Resolve a docs topic (or path) to an on-disk markdown file."""

        raw = str(topic_or_path or "").strip()
        if not raw:
            return None

        # Explicit path (absolute or contains separators).
        if raw.endswith(".md") or ("/" in raw) or ("\\" in raw):
            p = Path(raw).expanduser()
            if not p.is_absolute():
                p = Path.cwd() / p
            if p.exists() and p.is_file():
                return str(p)

        want = raw.casefold()
        for ent in self._scan_docs():
            topic = str(ent.get("topic", ""))
            stem = Path(str(ent.get("path", ""))).stem
            if want in {topic.casefold(), stem.casefold()}:
                return str(ent.get("path"))
        return None

    def open_help_doc(self, topic: str, *, push_stack: bool = True) -> bool:
        """Open a docs markdown file into a protected read-only help buffer."""

        path = self.find_doc_path(topic)
        if not path:
            return False

        p = Path(path)
        stem = p.stem
        slug = re.sub(r"^\d+\-", "", stem)
        name = f"help:{slug or stem}"

        # Help navigation: if we are currently in a help buffer and are
        # switching to a different docs topic, push the current topic.
        if bool(push_stack):
            cur_help = self.current_help_doc_topic()
            new_help = str(slug or stem)
            if cur_help and cur_help != new_help:
                self._help_stack.append(cur_help)
                if len(self._help_stack) > int(self._help_stack_limit):
                    self._help_stack = self._help_stack[-int(self._help_stack_limit) :]

        # If already open (by normalized path), just switch to it.
        target_norm = self._normalize_path(str(p))
        if target_norm:
            for bname, eb in self.buffers.items():
                if eb.buf.path and self._normalize_path(str(eb.buf.path)) == target_norm:
                    self.switch_buffer(bname)
                    # Mark as protected in case it was opened via `open`.
                    try:
                        self.cur().local_options["readonly"] = True
                        self.cur().local_options["help_doc"] = str(slug or stem)
                    except Exception:
                        pass
                    return True

        try:
            text = p.read_text(encoding="utf-8")
        except Exception as e:
            self.message(f"help: {e}")
            return False

        self.new_buffer(name=name, text=text, path=str(p))
        try:
            eb2 = self.cur()
            eb2.local_options["readonly"] = True
            eb2.local_options["help_doc"] = str(slug or stem)
            eb2.buf.mark_clean()
        except Exception:
            pass
        return True

    def refresh_capabilities(self) -> None:
        """Refresh capability feature advertisement based on current options."""

        refresh_vm_features(self, self.vm)

    def open_url(self, url: str) -> bool:
        """Open an external URL (capability-gated; best-effort)."""

        if not bool(self.options.get("cap.open-url")):
            return False
        u = str(url or "").strip()
        if not u:
            return False
        try:
            return bool(self._open_url_fn(u, new=2))
        except TypeError:
            # Some openers don't accept keyword args.
            try:
                return bool(self._open_url_fn(u))
            except Exception:
                return False
        except Exception:
            return False

    def current_help_doc_topic(self) -> str | None:
        """Return the current help-doc topic slug (or None)."""

        try:
            eb = self.cur()
        except Exception:
            return None
        try:
            if not bool(eb.local_options.get("readonly")):
                return None
            t = eb.local_options.get("help_doc")
            s = str(t or "").strip()
            return s or None
        except Exception:
            return None

    def help_back(self) -> bool:
        """Go back to the previous docs help page (best-effort)."""

        if not self._help_stack:
            self.message("helpback: back stack empty")
            return False
        topic = str(self._help_stack.pop()).strip()
        if not topic:
            return False
        # Avoid re-pushing onto the stack.
        if self.open_help_doc(topic, push_stack=False):
            self.message(f"helpback: {self.format_help_target()}")
            return True
        self.message(f"help docs: no such doc: {topic}")
        return False



    def _md_norm_ref_id(self, s: str) -> str:
        """Normalize a markdown reference-id (case-insensitive, collapse whitespace)."""

        return md_norm_ref_id(s)

    def _md_reference_defs(self, lines: list[object]) -> dict[str, str]:
        """Parse markdown reference definitions: [id]: target "title".

        This is intentionally small and conservative: it supports the common forms
        used in docs/help pages without needing a full markdown parser.
        """

        defs: dict[str, str] = {}
        xs = list(lines)
        fence_flags = md_fenced_code_line_flags(xs)
        html_block_flags = md_html_block_line_flags(xs)
        comment_spans = md_html_comment_line_spans(xs)


        for i, ln in enumerate(xs):
            if i < len(fence_flags) and fence_flags[i]:
                continue
            if i < len(html_block_flags) and html_block_flags[i]:
                continue
            s = str(ln)
            j = md_leading_spaces_upto3(s)
            if j is None or j >= len(s) or s[j:j+1] != '[' or md_backslash_escaped(s, j):
                continue
            spans = comment_spans[i] if i < len(comment_spans) else []
            if md_span_contains(spans, j, j + 1):
                continue
            span = md_balanced_span(s, j, opener='[', closer=']')
            if span is None:
                continue
            a, b = span
            k = b
            while k < len(s) and s[k].isspace():
                k += 1
            if s[k:k+1] != ':':
                continue
            raw_id = s[a + 1:b - 1]
            if not md_link_label_has_text(raw_id):
                continue
            rid = self._md_norm_ref_id(raw_id)
            if not rid:
                continue

            target = md_reference_def_target(
                s[k + 1 :],
                md_docs_continuation_line(xs, i + 1, fence_flags=fence_flags, html_block_flags=html_block_flags, comment_spans=comment_spans),
                md_docs_continuation_line(xs, i + 2, fence_flags=fence_flags, html_block_flags=html_block_flags, comment_spans=comment_spans),
            )
            if target:
                defs[rid] = target
        return defs

    def _md_footnote_defs(self, lines: list[object]) -> dict[str, tuple[int, int]]:
        """Parse markdown footnote definitions: ``[^id]: body``.

        Returns ``footnote-id -> (line1, col1)`` using a tiny, best-effort parse.
        We only need the anchor location for docs-buffer navigation, so indented
        continuation lines are left alone.
        """

        defs: dict[str, tuple[int, int]] = {}
        xs = list(lines)
        fence_flags = md_fenced_code_line_flags(xs)
        html_block_flags = md_html_block_line_flags(xs)
        comment_spans = md_html_comment_line_spans(xs)
        for i, ln in enumerate(xs):
            if i < len(fence_flags) and fence_flags[i]:
                continue
            if i < len(html_block_flags) and html_block_flags[i]:
                continue
            s = str(ln)
            col0 = md_leading_spaces_upto3(s)
            if col0 is None:
                continue
            m = re.match(r"\[\^(?P<id>[^\]]+)\]\s*:\s*", s[col0:])
            if not m:
                continue
            spans = comment_spans[i] if i < len(comment_spans) else []
            if md_span_contains(spans, int(col0), int(col0) + 1):
                continue
            rid = self._md_norm_ref_id(m.group('id') or '')
            if not rid:
                continue
            defs[rid] = (i + 1, int(col0) + 1)
        return defs

    def _md_target_from_parens(self, inner: str) -> str:
        """Extract a link target from inside markdown (...) content.

        This uses :func:`md_inline_link_target` so invalid inline-link forms can
        fall back to reference-link parsing.
        """

        return md_inline_link_target(inner)

    def help_follow(self) -> bool:
        """Follow a markdown link under the cursor in a help/docs buffer."""

        eb = self.cur()
        if not self.current_help_doc_topic():
            self.message("helpfollow: not in a docs buffer")
            return False
        target = self._help_link_target_under_cursor(eb)
        if not target:
            self.message("helpfollow: no link under cursor")
            return False
        low = str(target or "").strip().casefold()
        is_external = low.startswith("http://") or low.startswith("https://") or low.startswith("mailto:")
        ok = bool(self._follow_help_link(target, base_path=str(eb.buf.path) if eb.buf.path else None))
        if ok and not is_external:
            self.message(f"helpjump: {self.format_help_target()}")
        return ok

    def help_copy_link_target(self) -> bool:
        """Copy the markdown link target under the cursor (docs/help buffers only)."""

        eb = self.cur()
        if not self.current_help_doc_topic():
            self.message("helplinkcopy: not in a docs buffer")
            return False
        target = self._help_link_target_under_cursor(eb)
        if not target:
            self.message("helplinkcopy: no link under cursor")
            return False
        self.set_clipboard_items([str(target)], kind="items")
        self.message(f"helplinkcopy: {target}")
        return True

    def _open_url_feedback_prefix(self, source: str = "") -> str:
        """Return the command surface prefix for opening an external URL."""

        return "helpfollow" if str(source or "").strip().lower() == "help" else "urlopen"

    def _copy_url_feedback_prefix(self, source: str = "") -> str:
        """Return the command surface prefix for copying a pending external URL."""

        return "helplinkcopy" if str(source or "").strip().lower() == "help" else "urlcopy"

    # ----- URL-under-cursor helpers -----

    _URL_TOKEN_RE = re.compile(r'(?:https?://|mailto:)[^\s<>()\[\]{}"\']+')

    def _trim_url_token(self, tok: str) -> str:
        s = str(tok or "").strip()
        if not s:
            return ""

        left_wrap = set("<([{") | {"'", chr(34)}
        right_wrap = set(">)]}") | {"'", chr(34), ".", ",", ";", "!"}

        while s and s[0] in left_wrap:
            s = s[1:]
        while s and s[-1] in right_wrap:
            s = s[:-1]
        return s.strip()

    def url_under_cursor(self) -> str | None:
        """Best-effort URL under the primary cursor (any buffer).

        This is intentionally conservative and only recognizes:
        - http://...
        - https://...
        - mailto:...

        The cursor must be within the detected URL span.
        """

        eb = self.cur()
        if not eb.buf.lines:
            return None
        self._normalize_cursor_lists(eb)
        c = eb.cursors[eb.primary]
        idx = max(0, min(int(c.line), len(eb.buf.lines) - 1))
        line = str(eb.buf.lines[idx])
        col = int(c.col)

        for m in self._URL_TOKEN_RE.finditer(line):
            a, b = int(m.start()), int(m.end())
            if a <= col <= b:
                u = self._trim_url_token(str(m.group(0) or ""))
                return u or None
        return None

    def open_url_under_cursor(self) -> bool:
        """Open an external URL under cursor (capability-gated; confirm by default)."""

        u = self.url_under_cursor()
        if not u:
            self.message("urlopen: no url under cursor")
            return False

        if not bool(self.options.get("cap.open-url")):
            self.message(f"urlopen: disabled (cap.open-url). Enable with: set cap.open-url true\n{u}")
            return False

        if bool(self.options.get("open-url.confirm")):
            return bool(self.begin_open_url_confirm(u, source="cursor"))

        ok = self.open_url(u)
        if ok:
            self.message(f"urlopen: {u}")
            return True
        self.message(f"urlopen: failed: {u}")
        return False

    def copy_url_under_cursor(self) -> bool:
        """Copy the URL under cursor into the clipboard (any buffer)."""

        u = self.url_under_cursor()
        if not u:
            self.message("urlcopy: no url under cursor")
            return False
        self.set_clipboard_items([u], kind="items")
        self.message(f"urlcopy: {u}")
        return True


    def _help_link_target_under_cursor(self, eb: "EditorBuffer") -> str | None:
        """Best-effort markdown link target under the primary cursor."""

        if not eb.buf.lines:
            return None
        self._normalize_cursor_lists(eb)
        c = eb.cursors[eb.primary]
        idx = max(0, min(int(c.line), len(eb.buf.lines) - 1))
        line = str(eb.buf.lines[idx])
        col = int(c.col)

        lines = list(eb.buf.lines)
        fence_flags = md_fenced_code_line_flags(lines)
        html_block_flags = md_html_block_line_flags(lines)
        indented_code_flags = md_indented_code_line_flags(lines, fence_flags=fence_flags, html_block_flags=html_block_flags)
        if idx < len(fence_flags) and fence_flags[idx]:
            return None
        if idx < len(html_block_flags) and html_block_flags[idx]:
            return None
        if idx < len(indented_code_flags) and indented_code_flags[idx]:
            return None

        # Markdown link scan (best-effort).
        # Supported forms:
        #   - inline links: [label](target "title")
        #   - reference links: [label][id] and [label][] (collapsed)
        #   - shortcut reference links: [id]
        #   - autolinks: <https://...> and <mailto:...>

        defs = self._md_reference_defs(lines)
        footdefs = self._md_footnote_defs(lines)
        comment_spans = md_html_comment_line_spans(lines)
        line_comment_spans = comment_spans[idx] if idx < len(comment_spans) else []

        next_line = md_docs_continuation_line(lines, idx + 1, fence_flags=fence_flags, html_block_flags=html_block_flags, comment_spans=comment_spans)
        next_next_line = md_docs_continuation_line(lines, idx + 2, fence_flags=fence_flags, html_block_flags=html_block_flags, comment_spans=comment_spans)
        for match in md_link_matches(line, defs, footdefs, masked_spans=line_comment_spans, next_line=next_line, next_next_line=next_next_line):
            if int(match.start) <= col <= int(match.end):
                return str(match.target or '') or None

        return None

    def _follow_help_link(self, target: str, *, base_path: str | None) -> bool:
        """Follow a docs-help link target (internal docs, relative file, or external URL)."""

        t = str(target or "").strip().strip('"').strip("'")
        if not t:
            return False

        low = t.casefold()
        if low.startswith("http://") or low.startswith("https://") or low.startswith("mailto:"):
            if bool(self.options.get("cap.open-url")):
                # Safe-by-default: confirm before opening external URLs.
                if bool(self.options.get("open-url.confirm")):
                    return bool(self.begin_open_url_confirm(t, source="help"))

                ok = self.open_url(t)
                if ok:
                    self.message(f"{self._open_url_feedback_prefix('help')}: {t}")
                    return True
                self.message(f"{self._open_url_feedback_prefix('help')}: failed: {t}")
                return False
            # Keep the UX explicit: this is intentionally capability-gated.
            # (Docs page `98-help-browser.md` includes the same hint.)
            self.message(
                f"{self._open_url_feedback_prefix('help')}: disabled (cap.open-url). Enable with: set cap.open-url true\n{t}"
            )
            return False

        # Same-page or cross-doc markdown fragments.
        doc_part, hash_mark, frag_part = t.partition("#")
        frag = unquote(str(frag_part or "").strip()) if hash_mark else ""
        if hash_mark and not doc_part.strip():
            return self._jump_help_fragment(frag)

        # Relative docs paths are percent-decoded before resolution so links like
        # ``topic%20name.md`` behave like ordinary local files.
        resolved_doc = unquote(str(doc_part or t).strip())
        if base_path and resolved_doc:
            try:
                base = Path(str(base_path)).parent
                cand = (base / resolved_doc).resolve()
                if cand.exists() and cand.is_file():
                    ok = bool(self.open_help_doc(str(cand), push_stack=True))
                    if not ok:
                        return False
                    if frag:
                        return self._jump_help_fragment(frag)
                    return True
            except Exception:
                pass

        # Otherwise treat as a docs topic (slug) or explicit path.
        if self.open_help_doc(resolved_doc, push_stack=True):
            if frag:
                return self._jump_help_fragment(frag)
            return True
        self.message(f"help docs: no such doc: {resolved_doc}")
        return False

    def begin_open_url_confirm(self, url: str, *, source: str = "") -> bool:
        """Begin a capture-mode confirmation loop for opening an external URL."""

        u = str(url or "").strip()
        if not u:
            return False
        if not bool(self.options.get("cap.open-url")):
            return False

        # Remove any prior openurl mode so we don't stack confirmations.
        self.key_mode_stack = [km for km in self.key_mode_stack if km.name != "openurl"]

        self._pending_open_url = u
        self._pending_open_url_source = str(source or "")
        self.push_key_mode("openurl", capture=True)
        source_tag = str(source or "").strip().lower()
        if source_tag == "help":
            head = "open external link from help?"
        elif source_tag == "cursor":
            head = "open external link under cursor?"
        elif source_tag == "command":
            head = "open external link from command?"
        else:
            head = "open external link?"
        self.message(f"{head} y/Enter=open n/Esc=cancel c=copy\n{u}")
        return True

    def _finish_open_url_confirm(self) -> None:
        self._pending_open_url = None
        self._pending_open_url_source = ""
        self.key_mode_stack = [km for km in self.key_mode_stack if km.name != "openurl"]

    def help_link_rows(self, query: str = "", *, limit: int | None = None) -> list[list[str]]:
        """Return markdown links in the current help/docs buffer as rows.

        Rows are: [label kind target info]
        """

        topic = self.current_help_doc_topic()
        if not topic:
            return []
        eb = self.cur()
        rows: list[list[str]] = []
        lines = list(eb.buf.lines)
        defs = self._md_reference_defs(lines)
        footdefs = self._md_footnote_defs(lines)
        fence_flags = md_fenced_code_line_flags(lines)
        html_block_flags = md_html_block_line_flags(lines)
        indented_code_flags = md_indented_code_line_flags(lines, fence_flags=fence_flags, html_block_flags=html_block_flags)
        comment_spans = md_html_comment_line_spans(lines)
        for i, ln in enumerate(lines):
            if i < len(fence_flags) and fence_flags[i]:
                continue
            if i < len(html_block_flags) and html_block_flags[i]:
                continue
            if i < len(indented_code_flags) and indented_code_flags[i]:
                continue
            s = str(ln)
            spans = comment_spans[i] if i < len(comment_spans) else []
            next_line = md_docs_continuation_line(lines, i + 1, fence_flags=fence_flags, html_block_flags=html_block_flags, comment_spans=comment_spans)
            next_next_line = md_docs_continuation_line(lines, i + 2, fence_flags=fence_flags, html_block_flags=html_block_flags, comment_spans=comment_spans)
            for match in md_link_matches(s, defs, footdefs, masked_spans=spans, next_line=next_line, next_next_line=next_next_line):
                info = f"{i+1}:{int(match.label_start)+1}"
                rows.append([str(match.display or match.target), 'link', str(match.target), info])

        q = str(query or '').strip()
        if q:
            scored: list[tuple[tuple[int, int, int, int, int, int, int, int, int, str], int, list[str]]] = []
            for idx, row in enumerate(rows):
                key = self._helplink_row_sort_key(row, q)
                if key is None:
                    continue
                scored.append((key, idx, row))
            scored.sort(key=lambda item: (item[0], item[1]))
            rows = [r for _k, _i, r in scored]

        if limit is not None:
            return rows[: max(1, int(limit))]
        return rows

    def _helplink_section_label(self, row: list[str]) -> str:
        """Backward-compat section label helper for docs-link rows.

        Rows are: [label kind target info]

        New code should prefer:
          - `_helplink_kind_label` (Docs/Files/External)
          - `_helplink_heading_label` (nearest heading breadcrumb)
        """

        return self._helplink_kind_label(row)

    def _helplink_kind_label(self, row: list[str]) -> str:
        """Classify docs links as Docs/Files/External (stable default)."""

        try:
            tgt = str(row[2] if len(row) > 2 else "")
            info = md_help_link_target_info(tgt)
            kind = str(info.get("target_kind", "") or "")
            if kind in {"external", "mailto"}:
                return "External"
            if kind in {"file", "file-fragment"}:
                return "Files"
        except Exception:
            pass
        return "Docs"

    def _help_heading_paths(self) -> list[tuple[int, str]]:
        """Return [(line1, path), ...] heading paths for the current docs buffer.

        The "path" is a breadcrumb-like label built from heading levels.
        We intentionally treat the page's H1 as a document title and omit it
        from the breadcrumb, so most pages yield readable section labels like
        "Links" or "External links" rather than "Help browser › Links".

        Paths are best-effort and cached by (topic, nlines).
        """

        topic = self.current_help_doc_topic()
        if not topic:
            return []
        eb = self.cur()
        nlines = len(eb.buf.lines)
        if topic == self._help_heading_cache_topic and nlines == self._help_heading_cache_nlines:
            return list(self._help_heading_cache)

        idx: list[tuple[int, str]] = []
        stack: list[str] = []

        for line0, level, title, _frag, _col0 in self._md_heading_entries(list(eb.buf.lines)):
            # Ignore H1 as a "document title".
            if level == 1:
                stack = []
                continue

            # Shift levels down so H2 becomes breadcrumb level 1.
            lvl = max(1, min(level - 1, 6))
            stack = stack[: max(0, int(lvl) - 1)]
            stack.append(title)
            path = " › ".join(stack).strip()
            idx.append((int(line0) + 1, path))

        self._help_heading_cache_topic = str(topic)
        self._help_heading_cache_nlines = int(nlines)
        self._help_heading_cache = list(idx)
        return list(idx)

    def _md_heading_title_parts(self, raw_title: str, *, col0: int) -> tuple[str, str, int] | None:
        """Normalize tiny markdown heading title text for pickers/fragments.

        Returns ``(display, explicit_id, col0)`` where ``display`` is human-facing
        text (common inline markup stripped) and ``explicit_id`` is any trailing
        attr-list id like ``{#frag}`` / ``{: #frag }``.
        """

        title0 = str(raw_title or "").strip()
        if not title0:
            return None

        explicit_id = ""
        title = title0

        attr_m = re.search(r"\s+(?P<attrs>\{(?::)?\s*[^{}]*\})\s*$", title0)
        if attr_m is not None:
            attrs = str(attr_m.group("attrs") or "")
            id_m = re.search(r"#(?P<id>[^\s}]+)", attrs)
            if id_m is not None:
                explicit_id = str(id_m.group("id") or "").strip()
                title = title0[: int(attr_m.start())].rstrip()

        display = md_strip_inline_markup(title)
        if not display:
            display = title.strip()
        if not display:
            return None
        return (display, explicit_id, int(col0))

    def _md_heading_parts(self, line: str) -> tuple[int, str, str, int] | None:
        """Parse one ATX heading line into (level, title, fragment_id, col0).

        ``title`` is cleaned for human display/picker use. ``fragment_id`` is the
        explicit custom id (``{#id}`` / ``{: #id }``) when present, otherwise the
        empty string so callers can derive an automatic slug.
        """

        s = str(line)
        col0 = md_leading_spaces_upto3(s)
        if col0 is None:
            return None
        m = re.match(r"(?P<hashes>#{1,6})\s+(?P<title>.+?)\s*(?:#+\s*)?$", s[col0:])
        if not m:
            return None
        raw_title = str(m.group("title") or "").strip()
        if not raw_title:
            return None
        level = len(str(m.group("hashes") or ""))
        level = max(1, min(int(level), 6))
        col0 = int(col0) + int(m.start("title"))

        title_parts = self._md_heading_title_parts(raw_title, col0=col0)
        if title_parts is None:
            return None
        display, explicit_id, col0 = title_parts
        return (level, display, explicit_id, col0)

    def _md_heading_scan(self, lines: list[object]) -> list[tuple[int, int, int, str, str, int]]:
        """Return tiny markdown heading metadata for one docs/help buffer.

        Entries are ``(line0, line1_exclusive, level, title, fragment_id, col0)``.
        Policy stays intentionally small/shared: ATX headings are supported fully,
        and setext headings recognize one or more preceding paragraph-like lines
        before a ``===`` or ``---`` underline outside fenced code blocks.
        """

        xs = [str(x) for x in (lines or [])]
        if not xs:
            return []

        fence_flags = md_fenced_code_line_flags(xs)
        html_block_flags = md_html_block_line_flags(xs)
        comment_spans = md_html_comment_line_spans(xs)
        out: list[tuple[int, int, int, str, str, int]] = []
        for i, s in enumerate(xs):
            if i < len(fence_flags) and fence_flags[i]:
                continue
            if i < len(html_block_flags) and html_block_flags[i]:
                continue
            spans = comment_spans[i] if i < len(comment_spans) else []

            atx = self._md_heading_parts(s)
            if atx is not None:
                level, title, explicit_id, col0 = atx
                if not md_span_contains(spans, int(col0), int(col0) + 1):
                    out.append((i, i + 1, level, title, explicit_id, col0))
                continue

            m = _SETEXT_UNDERLINE_RE.match(s)
            if m is None or i <= 0:
                continue

            parts_rev: list[str] = []
            start = i
            col0 = 0
            for j in range(i - 1, -1, -1):
                if j < len(fence_flags) and fence_flags[j]:
                    break
                if j < len(html_block_flags) and html_block_flags[j]:
                    break
                title_line = str(xs[j])
                stripped = title_line.strip()
                if not stripped:
                    break
                if self._md_heading_parts(title_line) is not None:
                    break
                if re.match(r"^[ ]{0,3}(?:>|[*+-]\s|\d+[.)]\s)", title_line):
                    break
                if re.match(r"^\s{4,}", title_line):
                    break
                if _FENCE_OPEN_RE.match(title_line):
                    break
                if _SETEXT_UNDERLINE_RE.match(title_line) is not None:
                    break

                title_spans = comment_spans[j] if j < len(comment_spans) else []
                line_col0 = len(title_line) - len(title_line.lstrip(' '))
                if md_span_contains(title_spans, int(line_col0), int(line_col0) + 1):
                    break

                start = j
                col0 = line_col0
                parts_rev.append(stripped)

            if not parts_rev:
                continue

            level = 1 if str(m.group('run') or '').startswith('=') else 2
            raw_title = " ".join(reversed(parts_rev)).strip()
            title_parts = self._md_heading_title_parts(raw_title, col0=col0)
            if title_parts is None:
                continue
            display, explicit_id, col0 = title_parts
            out.append((start, i + 1, level, display, explicit_id, col0))

        return out

    def _md_heading_entries(self, lines: list[object]) -> list[tuple[int, int, str, str, int]]:
        """Return tiny markdown heading entries for one docs/help buffer.

        Entries are ``(line0, level, title, fragment_id, col0)``. This is a thin
        compatibility view over ``_md_heading_scan`` so callers that only care
        about the heading target line keep a simple tuple shape.
        """

        return [(line0, level, title, frag, col0) for line0, _line1, level, title, frag, col0 in self._md_heading_scan(lines)]

    def _md_section_entry_by_line(self, lines: list[object]) -> dict[int, dict[str, Any]]:
        """Return nearest-heading section metadata keyed by source line index.

        Each value is a tiny breadcrumb-like snapshot describing the nearest
        preceding markdown heading that owns that line in docs/help source.
        This keeps visible row-local section context shareable with future
        UIs/scripts/LLMs without forcing them to rerun heading scans.
        """

        xs = [str(x) for x in (lines or [])]
        if not xs:
            return {}

        scan = self._md_heading_scan(xs)
        if not scan:
            return {}

        seen_heading_ids: dict[str, int] = {}
        heading_entries: list[tuple[int, dict[str, Any]]] = []
        stack: list[dict[str, Any]] = []
        for line0, line1, level, title, explicit_fragment, col0 in scan:
            stack = stack[: max(0, int(level) - 1)]
            resolved_fragment = str(explicit_fragment or md_heading_auto_id(title, seen=seen_heading_ids))
            source_kind = 'atx' if int(line1) <= int(line0) + 1 else 'setext'
            frag_source = 'explicit' if str(explicit_fragment) else 'auto'
            node = {
                'title': str(title),
                'fragment': str(resolved_fragment),
                'level': int(level),
            }
            stack.append(node)
            heading_entries.append(
                (
                    int(line0),
                    {
                        'kind': 'section',
                        'heading_line': int(line0),
                        'heading_end_line': max(int(line0), int(line1) - 1),
                        'heading_col': int(col0),
                        'level': int(level),
                        'title': str(title),
                        'fragment': str(resolved_fragment),
                        'explicit_fragment': str(explicit_fragment),
                        'fragment_source': str(frag_source),
                        'source_kind': str(source_kind),
                        'path': ' › '.join(str(part.get('title', '') or '') for part in stack if str(part.get('title', '') or '')),
                        'path_titles': [str(part.get('title', '') or '') for part in stack if str(part.get('title', '') or '')],
                    },
                )
            )

        out: dict[int, dict[str, Any]] = {}
        current: dict[str, Any] | None = None
        entry_idx = 0
        for line_idx in range(len(xs)):
            while entry_idx < len(heading_entries) and int(heading_entries[entry_idx][0]) <= int(line_idx):
                current = dict(heading_entries[entry_idx][1])
                entry_idx += 1
            if current is not None:
                out[int(line_idx)] = dict(current)
        return out

    def _md_heading_line_roles(self, lines: list[object]) -> dict[int, tuple[str, int]]:
        """Return tiny heading render roles keyed by source line index.

        Roles are ``(role, level)`` where ``role`` is one of:
        - ``"title"`` for ATX heading lines and the title lines of setext headings
        - ``"underline"`` for the ``===`` / ``---`` underline line of a setext heading

        This is a tiny shared compatibility helper for docs/help rendering so
        setext headings can reuse the same heading scan the docs browser already
        trusts for titles, outline rows, fragments, and heading breadcrumbs.
        """

        out: dict[int, tuple[str, int]] = {}
        for line0, line1, level, _title, _frag, _col0 in self._md_heading_scan(lines):
            if int(line1) <= int(line0) + 1:
                out[int(line0)] = ("title", int(level))
                continue
            for i in range(int(line0), max(int(line0), int(line1) - 1)):
                out[int(i)] = ("title", int(level))
            out[max(int(line0), int(line1) - 1)] = ("underline", int(level))
        return out

    def _md_fenced_code_line_roles(self, lines: list[object]) -> dict[int, str]:
        """Return tiny fenced-code render roles keyed by source line index.

        Roles are one of:
        - ``"fence"`` for the opening/closing fence lines
        - ``"body"`` for interior lines of the fenced block

        This intentionally reuses the same tiny fence policy already trusted by
        docs/help navigation and link-underlining precedence, so live docs/help
        rendering can make fenced examples visibly code-ish without growing a
        second fence parser in the TUI.
        """

        xs = [str(x) for x in (lines or [])]
        if not xs:
            return {}

        out: dict[int, str] = {}
        in_fence = False
        fence_ch = ''
        fence_len = 0

        for i, s in enumerate(xs):
            if not in_fence:
                m = _FENCE_OPEN_RE.match(s)
                if m is None:
                    continue
                fence = str(m.group('fence') or '')
                if not fence:
                    continue
                in_fence = True
                fence_ch = fence[0]
                fence_len = len(fence)
                out[int(i)] = 'fence'
                continue

            if re.match(rf"^[ ]{{0,3}}{re.escape(fence_ch)}{{{int(fence_len)},}}[     ]*$", s):
                out[int(i)] = 'fence'
                in_fence = False
                fence_ch = ''
                fence_len = 0
                continue

            out[int(i)] = 'body'

        return out

    def _md_block_entries_by_line(self, lines: list[object]) -> dict[int, list[dict[str, Any]]]:
        """Return tiny parsed block-ish docs/help metadata keyed by line index.

        This stays deliberately source-view-first: it reuses the same tiny fence,
        HTML-block, and indented-code scans Micromax already trusts for docs/help
        precedence and styling, but packages the visible rows as explicit entries
        so future UIs/scripts/LLMs do not have to infer fence info strings or
        block grouping from `line_role` alone.
        """

        xs = [str(x) for x in (lines or [])]
        if not xs:
            return {}

        html_block_flags = md_html_block_line_flags(xs)
        indented_code_flags = md_indented_code_line_flags(xs, html_block_flags=html_block_flags)
        out: dict[int, list[dict[str, Any]]] = {}

        in_fence = False
        fence_ch = ''
        fence_len = 0
        fence_info_string = ''
        fence_language = ''
        fence_block_index = 0
        for i, s in enumerate(xs):
            if not in_fence:
                m = _FENCE_OPEN_RE.match(s)
                if m is None:
                    continue
                fence = str(m.group('fence') or '')
                if not fence:
                    continue
                fence_block_index += 1
                in_fence = True
                fence_ch = fence[0]
                fence_len = len(fence)
                rest = str(m.group('rest') or '')
                info_string = rest.strip(' 	')
                language = str(info_string.split()[0]) if info_string else ''
                fence_info_string = str(info_string)
                fence_language = str(language)
                out.setdefault(int(i), []).append(
                    {
                        'kind': 'fenced-code',
                        'role': 'opener',
                        'block_index': int(fence_block_index),
                        'start': int(m.start('fence')),
                        'end': int(m.end('fence')),
                        'text': str(s),
                        'marker': str(fence_ch),
                        'marker_kind': str(md_fenced_code_marker_kind(fence_ch)),
                        'marker_count': int(fence_len),
                        'indent': int(m.start('fence')),
                        'info_string': str(fence_info_string),
                        'language': str(fence_language),
                        'has_language': 1 if fence_language else 0,
                    }
                )
                continue

            m_close = re.match(rf"^(?P<indent>[ ]{{0,3}})(?P<fence>{re.escape(fence_ch)}{{{int(fence_len)},}})(?P<trailing>[ 	]*)$", s)
            if m_close is not None:
                fence = str(m_close.group('fence') or '')
                out.setdefault(int(i), []).append(
                    {
                        'kind': 'fenced-code',
                        'role': 'closer',
                        'block_index': int(fence_block_index),
                        'start': int(m_close.start('fence')),
                        'end': int(m_close.end('fence')),
                        'text': str(s),
                        'marker': str(fence_ch),
                        'marker_kind': str(md_fenced_code_marker_kind(fence_ch)),
                        'marker_count': int(len(fence)),
                        'indent': int(m_close.start('fence')),
                        'info_string': str(fence_info_string),
                        'language': str(fence_language),
                        'has_language': 1 if fence_language else 0,
                    }
                )
                in_fence = False
                fence_ch = ''
                fence_len = 0
                fence_info_string = ''
                fence_language = ''
                continue

            out.setdefault(int(i), []).append(
                {
                    'kind': 'fenced-code',
                    'role': 'body',
                    'block_index': int(fence_block_index),
                    'start': 0,
                    'end': int(len(s)),
                    'text': str(s),
                    'marker': str(fence_ch),
                    'marker_kind': str(md_fenced_code_marker_kind(fence_ch)),
                    'marker_count': int(fence_len),
                    'info_string': str(fence_info_string),
                    'language': str(fence_language),
                    'has_language': 1 if fence_language else 0,
                }
            )

        html_block_index = 0
        in_html = False
        for i, flag in enumerate(html_block_flags):
            if not flag:
                in_html = False
                continue
            if not in_html:
                html_block_index += 1
                in_html = True
            s = xs[i]
            out.setdefault(int(i), []).append(
                {
                    'kind': 'html-block',
                    'role': 'line',
                    'block_index': int(html_block_index),
                    'start': 0,
                    'end': int(len(s)),
                    'text': str(s),
                }
            )

        indented_code_index = 0
        in_indented = False
        for i, flag in enumerate(indented_code_flags):
            if not flag:
                in_indented = False
                continue
            if not in_indented:
                indented_code_index += 1
                in_indented = True
            s = xs[i]
            leading = re.match(r'^[ 	]+', s)
            indent_text = str(leading.group(0) or '') if leading else ''
            out.setdefault(int(i), []).append(
                {
                    'kind': 'indented-code',
                    'role': 'line',
                    'block_index': int(indented_code_index),
                    'start': 0,
                    'end': int(len(s)),
                    'text': str(s),
                    'indent_text': str(indent_text),
                    'indent_width': int(len(indent_text)),
                }
            )

        return out

    def _md_definition_entries_by_line(self, lines: list[object]) -> dict[int, list[dict[str, Any]]]:
        """Return tiny parsed markdown definition metadata keyed by line index.

        This stays intentionally small and reuses the same tiny definition scans
        already trusted by docs/help navigation and live TUI styling. Starter
        rows carry the visible marker token plus normalized ids/targets;
        continuation rows carry the owning definition id so future UIs/scripts/
        LLMs can tell which wrapped reference or indented footnote body they are
        looking at without reparsing visible prose.
        """

        xs = list(lines)
        if not xs:
            return {}

        fence_flags = md_fenced_code_line_flags(xs)
        html_block_flags = md_html_block_line_flags(xs)
        comment_spans = md_html_comment_line_spans(xs)
        out: dict[int, list[dict[str, Any]]] = {}

        for i, ln in enumerate(xs):
            if i < len(fence_flags) and fence_flags[i]:
                continue
            if i < len(html_block_flags) and html_block_flags[i]:
                continue
            s = str(ln)
            col0 = md_leading_spaces_upto3(s)
            if col0 is None:
                continue
            spans = comment_spans[i] if i < len(comment_spans) else []
            if md_span_contains(spans, int(col0), int(col0) + 1):
                continue

            m_fn = re.match(r"\[\^(?P<id>[^\]]+)\]\s*:\s*", s[col0:])
            if m_fn:
                rid = self._md_norm_ref_id(m_fn.group('id') or '')
                if rid:
                    a = int(col0)
                    match_text = str(m_fn.group(0) or '')
                    render_b = int(col0) + int(m_fn.end())
                    colon_offset = int(match_text.find(':'))
                    b = int(col0) + (colon_offset + 1 if colon_offset >= 0 else int(m_fn.end()))
                    marker_text = str(s[a:b])
                    starter = {
                        'kind': 'footnote-definition',
                        'role': 'starter',
                        'id': str(rid),
                        'start': int(a),
                        'end': int(b),
                        'text': marker_text,
                        'render_end': int(render_b),
                        'target': f'#^{rid}',
                        'target_kind': 'footnote',
                        'target_doc': '',
                        'target_fragment': f'^{rid}',
                    }
                    out.setdefault(int(i), []).append(starter)

                    j = int(i) + 1
                    continuation_index = 0
                    while j < len(xs):
                        if j < len(fence_flags) and fence_flags[j]:
                            break
                        if j < len(html_block_flags) and html_block_flags[j]:
                            break
                        sj = str(xs[j])
                        if not sj.strip():
                            break
                        spans_j = comment_spans[j] if j < len(comment_spans) else []
                        stripped = sj.lstrip(' ')
                        if sj.startswith('	'):
                            stripped = sj[1:]
                        elif len(sj) - len(stripped) < 4:
                            break
                        first_col = len(sj) - len(stripped)
                        if md_span_contains(spans_j, int(first_col), int(first_col) + 1):
                            break
                        continuation_index += 1
                        out.setdefault(int(j), []).append(
                            {
                                'kind': 'footnote-definition-cont',
                                'role': 'continuation',
                                'parent_kind': 'footnote-definition',
                                'id': str(rid),
                                'continuation_index': int(continuation_index),
                                'start': 0,
                                'end': int(len(sj)),
                                'text': str(sj),
                                'target': f'#^{rid}',
                                'target_kind': 'footnote',
                                'target_doc': '',
                                'target_fragment': f'^{rid}',
                            }
                        )
                        j += 1
                    continue

            if col0 >= len(s) or s[col0:col0 + 1] != '[' or md_backslash_escaped(s, col0):
                continue
            span = md_balanced_span(s, col0, opener='[', closer=']')
            if span is None:
                continue
            a, b = span
            k = b
            while k < len(s) and s[k].isspace():
                k += 1
            if s[k:k + 1] != ':':
                continue
            raw_id = s[a + 1:b - 1]
            if not md_link_label_has_text(raw_id):
                continue
            rid = self._md_norm_ref_id(raw_id)
            if not rid:
                continue

            target, used_lines = md_reference_def_target_info(
                s[k + 1 :],
                md_docs_continuation_line(xs, i + 1, fence_flags=fence_flags, html_block_flags=html_block_flags, comment_spans=comment_spans),
                md_docs_continuation_line(xs, i + 2, fence_flags=fence_flags, html_block_flags=html_block_flags, comment_spans=comment_spans),
            )
            if not target:
                continue
            resolved = md_help_link_target_info(target)
            marker_text = str(s[int(a):int(k + 1)])
            starter = {
                'kind': 'reference-definition',
                'role': 'starter',
                'id': str(rid),
                'start': int(a),
                'end': int(k + 1),
                'text': marker_text,
                'target': str(target),
                'target_kind': str(resolved.get('target_kind', '') or ''),
                'target_doc': str(resolved.get('doc', '') or ''),
                'target_fragment': str(resolved.get('fragment', '') or ''),
            }
            out.setdefault(int(i), []).append(starter)
            for off in range(1, int(used_lines) + 1):
                cont_line = int(i) + int(off)
                if 0 <= cont_line < len(xs):
                    sj = str(xs[cont_line])
                    out.setdefault(cont_line, []).append(
                        {
                            'kind': 'reference-definition-cont',
                            'role': 'continuation',
                            'parent_kind': 'reference-definition',
                            'id': str(rid),
                            'continuation_index': int(off),
                            'start': 0,
                            'end': int(len(sj)),
                            'text': str(sj),
                            'target': str(target),
                            'target_kind': str(resolved.get('target_kind', '') or ''),
                            'target_doc': str(resolved.get('doc', '') or ''),
                            'target_fragment': str(resolved.get('fragment', '') or ''),
                        }
                    )

        return out

    def _md_definition_line_roles(self, lines: list[object]) -> dict[int, tuple[str, int, int]]:
        """Return tiny markdown definition render roles keyed by source line index.

        Roles are ``(role, col0, col1)`` where ``role`` is one of:
        - ``"reference"`` for reference-definition starter lines
        - ``"reference-cont"`` for tiny wrapped destination/title continuation lines
        - ``"footnote"`` for footnote-definition starter lines
        - ``"footnote-cont"`` for tiny indented footnote continuation lines

        ``col0:col1`` marks the starter token span to emphasize on definition
        opener lines (for example ``[visionref]:`` or ``[^note]:``). Continuation
        lines use ``0:0``.

        This intentionally reuses the same tiny shared definition logic already
        trusted by docs/help navigation instead of adding another render-only
        parser path in the TUI.
        """

        out: dict[int, tuple[str, int, int]] = {}
        for idx, entries in self._md_definition_entries_by_line(lines).items():
            if not entries:
                continue
            entry = dict(entries[0])
            kind = str(entry.get('kind', '') or '')
            if kind == 'reference-definition':
                out[int(idx)] = ('reference', int(entry.get('start', 0) or 0), int(entry.get('end', 0) or 0))
            elif kind == 'reference-definition-cont':
                out[int(idx)] = ('reference-cont', 0, 0)
            elif kind == 'footnote-definition':
                out[int(idx)] = ('footnote', int(entry.get('start', 0) or 0), int(entry.get('render_end', entry.get('end', 0)) or 0))
            elif kind == 'footnote-definition-cont':
                out[int(idx)] = ('footnote-cont', 0, 0)
        return out

    def _help_heading_targets(self, eb: "EditorBuffer") -> dict[str, tuple[int, int]]:
        """Return fragment-id -> (line1, col1) for headings in a docs buffer."""

        seen: dict[str, int] = {}
        out: dict[str, tuple[int, int]] = {}
        for line0, _level, title, explicit_id, col0 in self._md_heading_entries(list(eb.buf.lines)):
            frag = str(explicit_id or md_heading_auto_id(title, seen=seen)).strip()
            if not frag:
                continue
            out[frag.casefold()] = (int(line0) + 1, int(col0) + 1)
        return out

    def _jump_current_buffer_to(self, line1: int, col1: int = 1) -> bool:
        """Move the primary cursor to 1-based ``line1:col1`` (best-effort)."""

        eb = self.cur()
        self._normalize_cursor_lists(eb)
        new_c = eb.buf.clamp(Cursor(max(0, int(line1) - 1), max(0, int(col1) - 1)))
        cur = eb.cursors[eb.primary]
        if (new_c.line, new_c.col) != (cur.line, cur.col) and bool(self.options.get("jumplist.auto", local=eb.local_options)):
            self.push_jump()
            eb.cursors[eb.primary] = new_c
            self.push_jump()
            return True
        eb.cursors[eb.primary] = new_c
        return True

    def _jump_help_fragment(self, frag: str) -> bool:
        """Jump to ``#fragment`` in the current docs buffer (best-effort)."""

        topic = self.current_help_doc_topic()
        if not topic:
            self.message("helpfollow: not in a docs buffer")
            return False
        eb = self.cur()
        want = unquote(str(frag or "").strip()).strip()
        if want.startswith("#"):
            want = want[1:].strip()
        if not want:
            return False

        targets = self._help_heading_targets(eb)
        pos = targets.get(want.casefold())
        if pos is None:
            footdefs = self._md_footnote_defs(list(eb.buf.lines))
            foot_key = str(want)
            if foot_key.startswith('^'):
                foot_key = foot_key[1:]
            pos = footdefs.get(md_norm_ref_id(foot_key))
        if pos is None:
            self.message(f"helpjump: no section or footnote: #{want}")
            return False
        line1, col1 = pos
        return self._jump_current_buffer_to(line1, col1)

    def _help_heading_fragments_by_line(self) -> dict[int, str]:
        """Return heading-line -> resolved fragment ids for the current docs page."""

        topic = self.current_help_doc_topic()
        if not topic:
            return {}
        eb = self.cur()
        nlines = len(eb.buf.lines)
        if (
            topic == self._help_heading_fragment_cache_topic
            and nlines == self._help_heading_fragment_cache_nlines
        ):
            return dict(self._help_heading_fragment_cache)

        seen: dict[str, int] = {}
        out: dict[int, str] = {}
        for line0, _level, title, explicit_id, _col0 in self._md_heading_entries(list(eb.buf.lines)):
            frag = str(explicit_id or md_heading_auto_id(title, seen=seen)).strip()
            if frag:
                out[int(line0) + 1] = frag

        self._help_heading_fragment_cache_topic = str(topic)
        self._help_heading_fragment_cache_nlines = int(nlines)
        self._help_heading_fragment_cache = dict(out)
        return dict(out)

    def _help_heading_path_for_line(self, line1: int) -> str:
        """Return the nearest heading breadcrumb for 1-based line number."""

        line = max(1, int(line1))
        idx = self._help_heading_paths()
        if not idx:
            return "Top"
        lines = [n for n, _p in idx]
        j = int(bisect_right(lines, line)) - 1
        if j < 0:
            return "Top"
        try:
            return str(idx[j][1] or "Top")
        except Exception:
            return "Top"

    def _help_outline_sections_by_line(self) -> dict[int, str]:
        """Return heading-line -> parent breadcrumb labels for outline rows.

        Unlike docs-link heading labels, outline grouping keeps the document H1 in
        the parent breadcrumb so child H2 rows on large docs pages do not all
        collapse back into a generic ``Top`` bucket.
        """

        topic = self.current_help_doc_topic()
        if not topic:
            return {}
        eb = self.cur()
        nlines = len(eb.buf.lines)
        if (
            topic == self._help_outline_section_cache_topic
            and nlines == self._help_outline_section_cache_nlines
        ):
            return dict(self._help_outline_section_cache)

        out: dict[int, str] = {}
        stack: list[str] = []
        for line0, level, title, _frag, _col0 in self._md_heading_entries(list(eb.buf.lines)):
            lvl = max(1, min(int(level), 6))
            stack = stack[: max(0, lvl - 1)]
            parent = " › ".join(stack).strip() or "Top"
            out[int(line0) + 1] = parent
            stack.append(str(title))

        self._help_outline_section_cache_topic = str(topic)
        self._help_outline_section_cache_nlines = int(nlines)
        self._help_outline_section_cache = dict(out)
        return dict(out)

    def help_outline_section_label(self, row: list[str]) -> str:
        """Section label for a help-outline row based on parent headings."""

        try:
            info = str(row[3] if len(row) > 3 else "")
            if ":" in info:
                line_s, _col_s = info.split(":", 1)
                line = int(line_s)
                return str(self._help_outline_sections_by_line().get(line, "Top") or "Top")
        except Exception:
            pass
        return "Top"

    def _help_outline_query_meta(self, row: list[str]) -> str:
        """Hidden parent-breadcrumb metadata used to rank heading queries.

        The visible row shape stays small (`[title kind menu info]`), but outline,
        navigator, and `helpjump` queries should still be able to match parent
        breadcrumb terms such as ``Guide Links`` or ``Guide Deep dive``.

        This deliberately favors the *parent* breadcrumb over the full path so a
        query like ``Guide Links`` still ranks the actual ``Links`` heading above
        deeper descendants such as ``Deep dive`` that merely live under that path.
        """

        parts: list[str] = []
        section = str(self.help_outline_section_label(row) or "")
        if section and section != "Top":
            parts.append(section)
        menu = str(row[2] if len(row) > 2 else "")
        if menu:
            parts.append(menu)
        info = str(row[3] if len(row) > 3 else "")
        if info:
            parts.append(info)
            if ":" in info:
                try:
                    line_s, _col_s = info.split(":", 1)
                    frag = str(self._help_heading_fragments_by_line().get(int(line_s), "") or "")
                    if frag:
                        parts.append(frag)
                except Exception:
                    pass
        return " ".join(part for part in parts if part).strip()

    def _help_outline_row_sort_key(self, row: list[str], query: str) -> tuple[int, int, int, int, int, int, int, int, int, str] | None:
        q = str(query or "").strip()
        if q == "":
            return (0, 0, 0, 0, 0, 0, 0, 0, 0, "")

        name = str(row[0] if row else "")
        name_key = self._completion_fuzzy_sort_key(name, q)
        if name_key is not None:
            return (0, *name_key, name.casefold())

        meta = self._help_outline_query_meta(row)
        multi_key = self._multi_term_field_key(
            [(0, name), (1, meta)],
            q,
            fallback_rank=1,
            tie_name=name,
        )
        if multi_key is not None:
            return multi_key

        if meta:
            folded_meta = meta.casefold()
            folded_q = q.casefold()
            if folded_q and folded_q in folded_meta:
                pos = folded_meta.find(folded_q)
                return (2, pos, pos, 0, 0, 0, 0, len(meta), len(name), name.casefold())

            meta_key = self._completion_fuzzy_sort_key(meta, q)
            if meta_key is not None:
                return (3, *meta_key, name.casefold())
        return None

    def _helplink_query_meta(self, row: list[str]) -> str:
        """Hidden heading/kind metadata used to rank docs-link queries.

        Link labels stay visibly small (``[label kind target info]``), but link
        pickers should still be able to reuse the same section context users can
        already see in docs pages and grouped picker headers. That lets queries
        like ``External micro editor`` or ``Reference Vision ref`` combine the
        link label with its nearest-heading context instead of forcing a bare
        label-only search.
        """

        parts: list[str] = []
        heading = str(self._helplink_heading_label(row) or "")
        if heading and heading != "Top":
            parts.append(heading)
        kind = str(self._helplink_kind_label(row) or "")
        if kind:
            parts.append(kind)
        target = str(row[2] if len(row) > 2 else "")
        if target:
            parts.append(target)
            info_map = md_help_link_target_info(target)
            target_doc = str(info_map.get("doc", "") or "")
            target_fragment = str(info_map.get("fragment", "") or "")
            if target_doc:
                title = self._help_doc_title_for_target(target_doc)
                if title:
                    parts.append(title)
            if target_fragment:
                if target_doc:
                    frag_titles = self._help_doc_heading_titles_for_target(target_doc)
                else:
                    frag_titles = self._help_heading_titles_by_fragment()
                frag_title = str(frag_titles.get(target_fragment, "") or "")
                if frag_title:
                    parts.append(frag_title)
        info = str(row[3] if len(row) > 3 else "")
        if info and " — " in info:
            parts.append(info.split(" — ", 1)[1])
        return " ".join(part for part in parts if part).strip()

    def _helplink_row_sort_key(self, row: list[str], query: str) -> tuple[int, int, int, int, int, int, int, int, int, str] | None:
        q = str(query or "").strip()
        if q == "":
            return (0, 0, 0, 0, 0, 0, 0, 0, 0, "")

        name = str(row[0] if row else "")
        name_key = self._completion_fuzzy_sort_key(name, q)
        if name_key is not None:
            return (0, *name_key, name.casefold())

        meta = self._helplink_query_meta(row)
        multi_key = self._multi_term_field_key(
            [(0, name), (1, meta)],
            q,
            fallback_rank=1,
            tie_name=name,
        )
        if multi_key is not None:
            return multi_key

        if meta:
            folded_meta = meta.casefold()
            folded_q = q.casefold()
            if folded_q and folded_q in folded_meta:
                pos = folded_meta.find(folded_q)
                return (2, pos, pos, 0, 0, 0, 0, len(meta), len(name), name.casefold())

            meta_key = self._completion_fuzzy_sort_key(meta, q)
            if meta_key is not None:
                return (3, *meta_key, name.casefold())
        return None

    def _helplink_heading_label(self, row: list[str]) -> str:
        """Section label for a docs link row based on nearest markdown heading."""

        try:
            info = str(row[3] if len(row) > 3 else "")
            if ":" in info:
                line_s, _col_s = info.split(":", 1)
                line = int(line_s)
                return self._help_heading_path_for_line(line)
        except Exception:
            pass
        return "Top"

    def helplink_section_label(self, row: list[str]) -> str:
        """Section label for docs-link pickers.

        Controlled by option `help.linksections`:
          - "kind" (default): Docs/Files/External
          - "heading": nearest heading breadcrumb (Top/Links/External links/...)
        """

        mode = str(self.options.get("help.linksections") or "kind").strip().lower()
        if mode == "heading":
            return self._helplink_heading_label(row)
        return self._helplink_kind_label(row)

    def help_link_section_rows_kind(self, query: str = "", *, limit: int | None = None) -> list[list[object]]:
        """Grouped link rows by kind (Docs/Files/External)."""

        rows = self.help_link_rows(query, limit=limit)
        section_order = ["Docs", "Files", "External"]
        buckets: dict[str, list[list[str]]] = {label: [] for label in section_order}
        for row in rows:
            vals = [str(x) for x in list(row[:4])]
            while len(vals) < 4:
                vals.append("")
            label = self._helplink_kind_label(vals)
            buckets.setdefault(label, [])
            buckets[label].append(vals)
        out: list[list[object]] = []
        for label in section_order:
            items = buckets.get(label, [])
            if items:
                out.append([label, items])
        return out

    def help_link_section_rows_heading(self, query: str = "", *, limit: int | None = None) -> list[list[object]]:
        """Grouped link rows by nearest markdown heading."""

        rows = self.help_link_rows(query, limit=limit)
        buckets: dict[str, list[list[str]]] = {}
        for row in rows:
            vals = [str(x) for x in list(row[:4])]
            while len(vals) < 4:
                vals.append("")
            label = self._helplink_heading_label(vals)
            if label not in buckets:
                buckets[label] = []
            buckets[label].append(vals)
        return [[label, items] for (label, items) in buckets.items() if items]

    def help_link_section_rows(self, query: str = "", *, limit: int | None = None) -> list[list[object]]:
        """Grouped link rows for the current docs/help buffer.

        Shape: [[label, rows] ...], where rows are [[label kind target info] ...].
        """

        mode = str(self.options.get("help.linksections") or "kind").strip().lower()
        if mode == "heading":
            return self.help_link_section_rows_heading(query, limit=limit)
        return self.help_link_section_rows_kind(query, limit=limit)

    def help_outline_section_rows(self, query: str = "", *, limit: int | None = None) -> list[list[object]]:
        """Grouped outline rows by their parent-heading breadcrumb label."""

        rows = self.help_outline_rows(query, limit=limit)
        return self._group_prompt_rows_by_section(
            rows,
            label_fn=self.help_outline_section_label,
        )

    def help_outline_rows(self, query: str = "", *, limit: int | None = None) -> list[list[str]]:
        """Return markdown headings in the current help/docs buffer as rows.

        Rows are: [title kind menu info]
          - title: heading text (without leading hashes)
          - kind: "heading"
          - menu: heading level marker ("h1".."h6")
          - info: "line:col" position (1-based)
        """

        topic = self.current_help_doc_topic()
        if not topic:
            return []
        eb = self.cur()
        rows: list[list[str]] = []
        for line0, level, title, _frag, col0 in self._md_heading_entries(list(eb.buf.lines)):
            menu = f"h{level}"
            info = f"{int(line0)+1}:{int(col0)+1}"
            rows.append([title, "heading", menu, info])

        q = str(query or "").strip()
        if q:
            scored: list[tuple[tuple[int, int, int, int, int, int, int, int, int, str], int, list[str]]] = []
            for idx, row in enumerate(rows):
                key = self._help_outline_row_sort_key(row, q)
                if key is None:
                    continue
                scored.append((key, idx, row))
            scored.sort(key=lambda item: (item[0], item[1]))
            rows = [r for _k, _i, r in scored]

        if limit is not None:
            return rows[: max(1, int(limit))]
        return rows

    def help_nav_section_rows(self, query: str = "", *, limit: int | None = None) -> list[list[object]]:
        """Return combined headings + link rows for the current docs/help buffer.

        Shape: ``[[label, rows] ...]``, where rows are in the familiar
        ``[name kind menu info]`` shape.

        Sections are ordered as:
          - heading breadcrumb groups from ``helpoutlinepick``
          - Docs/Files/External (or heading-grouped links)

        This keeps the combined navigator aligned with the dedicated outline and
        link pickers instead of collapsing all headings into one generic bucket.
        """

        # Split the total limit to keep both headings and links represented.
        head_cap: int | None
        link_cap: int | None
        if limit is None:
            head_cap = None
            link_cap = None
        else:
            lim = max(1, int(limit))
            head_cap = max(1, lim // 2)
            link_cap = max(1, lim - head_cap)

        heading_sections = self.help_outline_section_rows(query, limit=head_cap)
        # Reuse the same link grouping policy as `helplinkpick` so the
        # combined navigator stays consistent with the dedicated link picker.
        link_sections = self.help_link_section_rows(query, limit=link_cap)

        # helpnav polish: include the nearest heading breadcrumb in link-row info
        # so links are easier to scan and search (without changing helplink rows).
        for sec in link_sections:
            try:
                if not isinstance(sec, list) or len(sec) < 2:
                    continue
                rows = sec[1]
                if not isinstance(rows, list):
                    continue
                for row in rows:
                    if not isinstance(row, list) or len(row) < 4:
                        continue
                    info = str(row[3] or '')
                    if ':' not in info:
                        continue
                    try:
                        line_s, _col_s = info.split(':', 1)
                        line = int(line_s)
                    except Exception:
                        continue
                    crumb = self._help_heading_path_for_line(line)
                    if crumb and crumb != 'Top' and crumb not in info:
                        row[3] = f"{info} — {crumb}"
            except Exception:
                continue

        out: list[list[object]] = []
        for sec in heading_sections:
            try:
                if isinstance(sec, list) and len(sec) >= 2 and sec[1]:
                    out.append([sec[0], sec[1]])
            except Exception:
                continue
        # Preserve link-section order from help_link_section_rows.
        for sec in link_sections:
            try:
                if isinstance(sec, list) and len(sec) >= 2 and sec[1]:
                    out.append([sec[0], sec[1]])
            except Exception:
                continue
        return out

    def help_nav_rows(self, query: str = "", *, limit: int | None = None) -> list[list[str]]:
        """Flattened combined docs navigator rows.

        This is used by the built-in help navigator picker (`helpnavpick`).
        """

        sections = self.help_nav_section_rows(query, limit=limit)
        flat: list[list[str]] = []
        for sec in sections:
            if not isinstance(sec, list) or len(sec) < 2:
                continue
            rows = sec[1]
            if not isinstance(rows, list):
                continue
            for row in rows:
                try:
                    vals = [str(x) for x in list(row[:4])]
                    while len(vals) < 4:
                        vals.append("")
                    flat.append(vals)
                except Exception:
                    continue

        if limit is not None:
            return flat[: max(1, int(limit))]
        return flat



    def close_buffer(self, name: str | None = None, *, force: bool = False) -> bool:
        """Close (delete) a buffer by name, or the active buffer when name is None.

        If the buffer is dirty, this uses a double-tap guard (unless force=True),
        mirroring the `quit` command's safety behavior.
        """
        target = str(name or (self.active or ""))
        if not target or target not in self.buffers:
            return False
        eb = self.buffers[target]
        if eb.buf.dirty and not bool(force):
            if self._close_armed and self._close_armed_name == target:
                # proceed
                pass
            else:
                self._close_armed = True
                self._close_armed_name = target
                self.message(f"unsaved changes in: {target}; run `close` again or `close -f` to force")
                return False

        self._close_armed = False
        self._close_armed_name = ""

        self._remember_cursor_for_buffer(eb)

        # Drop marks pointing at this buffer (keeps navigation helpers sane).
        for mk, (bufname, _cur) in list(self.marks.items()):
            if bufname == target:
                del self.marks[mk]

        # Delete the buffer.
        del self.buffers[target]

        # Choose a new active buffer.
        if self.active == target:
            self._buffer_mru = [x for x in self._buffer_mru if x != target and x in self.buffers]
            nxt = self.previous_buffer_name()
            if nxt:
                self._activate_buffer(nxt)
            elif self.buffers:
                names = list(self.buffers.keys())
                self._activate_buffer(names[-1])
            else:
                self.new_buffer("*scratch*", "")
        else:
            self._buffer_mru = [x for x in self._buffer_mru if x in self.buffers]
        return True

    def buffer_names(self) -> list[str]:
        """Return buffer names (stable sorted order)."""
        return sorted(self.buffers.keys())

    def _touch_buffer_mru(self, name: str) -> None:
        """Record that buffer `name` became active (best-effort)."""
        n = str(name or "").strip()
        if not n:
            return
        self._buffer_mru = [n] + [x for x in self._buffer_mru if x != n]
        if self.buffers:
            self._buffer_mru = [x for x in self._buffer_mru if x in self.buffers]

    def _activate_buffer(self, name: str) -> None:
        """Set active buffer and touch MRU (expects buffer exists)."""
        prev = self.buffers.get(str(self.active or "")) if self.active else None
        if prev is not None and str(self.active or "") != str(name):
            self._remember_cursor_for_buffer(prev)
        self.active = str(name)
        self._touch_buffer_mru(str(name))

    def previous_buffer_name(self) -> str:
        """Return the most-recently-used *other* buffer name, or ''."""
        cur = str(self.active or "")
        for n in list(self._buffer_mru):
            if n and n != cur and n in self.buffers:
                return n
        return ""

    def close_buffers(self, names: list[str], *, keep: str | None = None) -> None:
        """Close many buffers (forcefully; caller handles dirty confirmation)."""
        close_set = {str(n) for n in names if str(n) in self.buffers}
        if not close_set:
            return

        for mk, (bn, _cur) in list(self.marks.items()):
            if bn in close_set:
                del self.marks[mk]

        for n in close_set:
            self._remember_cursor_for_buffer(self.buffers.get(n))
            if n in self.buffers:
                del self.buffers[n]

        self._buffer_mru = [x for x in self._buffer_mru if x in self.buffers]

        k = str(keep or "")
        if k and k in self.buffers:
            self._activate_buffer(k)
            return

        for n in list(self._buffer_mru):
            if n in self.buffers:
                self._activate_buffer(n)
                return

        if self.buffers:
            names2 = list(self.buffers.keys())
            self._activate_buffer(names2[-1])
        else:
            self.new_buffer("*scratch*", "")

    def switch_buffer(self, name: str) -> bool:
        """Make `name` the active buffer if it exists."""
        n = str(name)
        if n not in self.buffers:
            return False
        self._activate_buffer(n)
        return True

    def rename_buffer(self, old: str, new: str) -> bool:
        """Rename a buffer key (and update mark targets).

        This keeps buffer identity stable enough for marks and scripts while
        still allowing commands like `save as` to retitle the buffer.
        """
        o = str(old)
        n = str(new)
        if o not in self.buffers:
            return False
        if n == o:
            return True
        if n in self.buffers:
            # refuse to clobber
            return False
        eb = self.buffers.pop(o)
        eb.name = n
        self.buffers[n] = eb
        if self.active == o:
            self._activate_buffer(n)
        # Update MRU entry (if any).
        self._buffer_mru = [n if x == o else x for x in self._buffer_mru]
        self._buffer_mru = [x for i,x in enumerate(self._buffer_mru) if x and x not in self._buffer_mru[:i]]
        # Update mark targets.
        for mk, (bn, cur) in list(self.marks.items()):
            if bn == o:
                self.marks[mk] = (n, Cursor(cur.line, cur.col))
        return True

    def mark_set(self, name: str) -> bool:
        """Set a named mark at the primary cursor in the active buffer."""
        mk = str(name or "").strip()
        if not mk:
            return False
        eb = self.cur()
        self._normalize_cursor_lists(eb)
        c = eb.cursors[eb.primary]
        self.marks[mk] = (eb.name, Cursor(int(c.line), int(c.col)))
        return True

    def mark_jump(self, name: str) -> bool:
        """Jump to a named mark, pushing the jumplist."""
        mk = str(name or "").strip()
        if not mk:
            return False
        if mk not in self.marks:
            return False
        buf_name, tgt = self.marks[mk]
        if buf_name not in self.buffers:
            return False
        # Save where we were.
        self.push_jump()
        self.switch_buffer(buf_name)
        eb = self.cur()
        self._normalize_cursor_lists(eb)
        eb.primary = max(0, min(int(eb.primary), len(eb.cursors) - 1))
        eb.cursors[eb.primary] = eb.buf.clamp(Cursor(int(tgt.line), int(tgt.col)))
        eb.sel_anchors[eb.primary] = None
        return True

    def mark_rows(self) -> list[list[object]]:
        """Return rows for marks as [[name buffer line col] ...]."""
        rows: list[list[object]] = []
        for name in sorted(self.marks.keys()):
            bn, cur = self.marks[name]
            rows.append([str(name), str(bn), int(cur.line), int(cur.col)])
        return rows

    def cur(self) -> EditorBuffer:
        if self.active is None or self.active not in self.buffers:
            raise RuntimeError("No active buffer")
        return self.buffers[self.active]

    def primary_index(self) -> int:
        eb = self.cur()
        self._normalize_cursor_lists(eb)
        return int(eb.primary)

    def set_primary_index(self, i: int) -> None:
        eb = self.cur()
        self._normalize_cursor_lists(eb)
        if not eb.cursors:
            eb.primary = 0
            return
        eb.primary = max(0, min(int(i), len(eb.cursors) - 1))
        self._normalize_cursor_lists(eb)

    def primary_cursor(self) -> Cursor:
        eb = self.cur()
        self._normalize_cursor_lists(eb)
        return eb.cursors[eb.primary]

    def format_cursor_target(self) -> str:
        """Return a tiny `name @ line:col` label for the current primary cursor."""
        eb = self.cur()
        name = str(getattr(eb.buf, "path", "") or getattr(eb, "name", "") or "").strip()
        c = self.primary_cursor()
        if name:
            return f"{name} @ {c.line + 1}:{c.col}"
        return f"{c.line + 1}:{c.col}"

    def format_help_target(self) -> str:
        """Return a tiny `topic @ line:col` label for the current help/doc cursor."""
        topic = str(self.current_help_doc_topic() or "").strip()
        c = self.primary_cursor()
        if topic:
            return f"{topic} @ {c.line + 1}:{c.col}"
        return self.format_cursor_target()

    def format_search_target(self, *, prefix: str = "find") -> str:
        """Return a tiny search-feedback label with target + optional `i/n` summary."""
        target = self.format_cursor_target()
        try:
            summary = str(self.search_position_model().get("summary", "") or "").strip()
        except Exception:
            summary = ""
        if summary:
            return f"{prefix}: {target} ({summary})"
        return f"{prefix}: {target}"

    @staticmethod
    def _count_label(n: int, singular: str, plural: str | None = None) -> str:
        n_i = int(n)
        if plural is None:
            plural = singular + "s"
        word = singular if n_i == 1 else plural
        return f"{n_i} {word}"

    def format_clipboard_feedback(
        self,
        *,
        verb: str,
        count: int,
        count_label: str,
        total_chars: int,
        include_target: bool = False,
    ) -> str:
        msg = f"{verb}: {self._count_label(count, count_label)}, {self._count_label(total_chars, 'char')}"
        if include_target:
            msg += f" -> {self.format_cursor_target()}"
        return msg

    def _alloc_cursor_id(self) -> int:
        cid = int(self._next_cursor_id)
        self._next_cursor_id += 1
        return cid

    def _normalize_cursor_lists(self, eb: EditorBuffer) -> None:
        """Normalize multi-cursor invariants.

        Invariants (rev14):
          - `cursors` + `sel_anchors` are the same length
          - list order is document order (line,col)
          - duplicate cursor positions are removed
          - `primary` points at the primary cursor
          - cursor and anchor positions are clamped to the buffer
        """

        # Keep sel_anchors aligned with cursors.
        if len(eb.sel_anchors) < len(eb.cursors):
            eb.sel_anchors.extend([None] * (len(eb.cursors) - len(eb.sel_anchors)))
        if len(eb.sel_anchors) > len(eb.cursors):
            eb.sel_anchors[:] = eb.sel_anchors[: len(eb.cursors)]

        # Keep cursor_ids aligned with cursors.
        if len(eb.cursor_ids) < len(eb.cursors):
            eb.cursor_ids.extend([self._alloc_cursor_id() for _ in range(len(eb.cursors) - len(eb.cursor_ids))])
        if len(eb.cursor_ids) > len(eb.cursors):
            eb.cursor_ids[:] = eb.cursor_ids[: len(eb.cursors)]

        if not eb.cursors:
            eb.cursors[:] = [Cursor(0, 0)]
            eb.sel_anchors[:] = [None]
            eb.cursor_ids[:] = [self._alloc_cursor_id()]
            eb.primary = 0

        # Clamp primary index.
        if eb.primary < 0:
            eb.primary = 0
        if eb.primary >= len(eb.cursors):
            eb.primary = max(0, len(eb.cursors) - 1)

        # Clamp cursor + anchor positions.
        items: list[tuple[Cursor, Cursor | None, int, bool, int]] = []
        for i, c in enumerate(eb.cursors):
            cc = eb.buf.clamp(Cursor(c.line, c.col))
            a = eb.sel_anchors[i]
            aa = eb.buf.clamp(Cursor(a.line, a.col)) if a is not None else None
            cid = int(eb.cursor_ids[i])
            items.append((cc, aa, cid, i == eb.primary, i))

        # Deduplicate by cursor position.
        chosen: dict[tuple[int, int], tuple[Cursor, Cursor | None, int, bool, int]] = {}
        for c, a, cid, is_primary, idx in items:
            key = (c.line, c.col)
            if key not in chosen:
                chosen[key] = (c, a, cid, is_primary, idx)
                continue
            c0, a0, cid0, p0, idx0 = chosen[key]

            # Prefer the primary cursor when merging duplicates, else earliest.
            take_new = False
            if is_primary and not p0:
                take_new = True
            elif is_primary == p0 and idx < idx0:
                take_new = True

            if take_new:
                # Preserve a non-empty anchor if possible.
                if a is None and a0 is not None:
                    a = a0
                chosen[key] = (c, a, cid, is_primary, idx)
            else:
                if a0 is None and a is not None:
                    chosen[key] = (c0, a, cid0, p0, idx0)

        deduped = list(chosen.values())
        deduped.sort(key=lambda t: (t[0].line, t[0].col, t[2]))

        # Rebuild lists + primary index.
        new_primary = 0
        for j, (_c, _a, _cid, p, _idx) in enumerate(deduped):
            if p:
                new_primary = j
                break

        eb.cursors[:] = [Cursor(c.line, c.col) for (c, _a, _cid, _p, _idx) in deduped]
        eb.sel_anchors[:] = [Cursor(a.line, a.col) if a is not None else None for (_c, a, _cid, _p, _idx) in deduped]
        eb.cursor_ids[:] = [int(cid) for (_c, _a, cid, _p, _idx) in deduped]
        eb.primary = new_primary

    # ----- selection (per cursor) -----
    def selection(self, i: int | None = None) -> Selection | None:
        eb = self.cur()
        self._normalize_cursor_lists(eb)
        if i is None:
            i = eb.primary
        if i < 0 or i >= len(eb.cursors):
            return None
        a = eb.sel_anchors[i]
        if a is None:
            return None
        return Selection(a, eb.cursors[i])

    def has_selection(self, i: int | None = None) -> bool:
        """Return True if there is a non-empty selection.

        - i is None: any cursor
        - i >= 0: that cursor index
        """

        eb = self.cur()
        self._normalize_cursor_lists(eb)
        if i is not None:
            sel = self.selection(i)
            return sel is not None and not sel.is_empty()
        for j in range(len(eb.cursors)):
            sel = self.selection(j)
            if sel is not None and not sel.is_empty():
                return True
        return False

    def has_primary_selection(self) -> bool:
        """Return True if the primary cursor has a non-empty selection."""
        eb = self.cur()
        self._normalize_cursor_lists(eb)
        sel = self.selection(None)
        return sel is not None and not sel.is_empty()

    def clear_selection(self, i: int | None = None) -> None:
        eb = self.cur()
        self._normalize_cursor_lists(eb)
        if i is None:
            # clear all
            eb.sel_anchors[:] = [None] * len(eb.cursors)
            return
        if i == -1:
            i = eb.primary
        if 0 <= i < len(eb.sel_anchors):
            eb.sel_anchors[i] = None


    # ----- selection/cursor recovery stack -----
    def push_selections(self) -> None:
        """Push the current cursor+selection state onto a small stack.

        This is inspired by selection-oriented editors where it's easy to
        accidentally clear/merge selections; having a tiny recovery stack is
        a cheap, testable escape hatch. This stack is *not* part of undo.
        """

        eb = self.cur()
        self._normalize_cursor_lists(eb)
        snap = (
            [Cursor(c.line, c.col) for c in eb.cursors],
            [Cursor(a.line, a.col) if a else None for a in eb.sel_anchors],
            [int(x) for x in eb.cursor_ids],
            int(eb.primary),
        )
        eb.sel_stack.append(snap)

    def pop_selections(self) -> bool:
        """Pop and restore the last saved cursor+selection state."""

        eb = self.cur()
        self._normalize_cursor_lists(eb)
        if not eb.sel_stack:
            return False
        curs, anchors, cursor_ids, primary = eb.sel_stack.pop()
        eb.cursors[:] = [Cursor(c.line, c.col) for c in curs]
        eb.sel_anchors[:] = [Cursor(a.line, a.col) if a else None for a in anchors]
        eb.cursor_ids[:] = [int(x) for x in cursor_ids]
        eb.primary = int(primary)
        self._normalize_cursor_lists(eb)
        return True

    def clear_saved_selections(self) -> None:
        eb = self.cur()
        eb.sel_stack.clear()

    # ----- jumplist (navigation) -----
    def _snapshot_cursor_only(self, eb: EditorBuffer) -> tuple[list[Cursor], list[Cursor | None], list[int], int]:
        self._normalize_cursor_lists(eb)
        return (
            [Cursor(c.line, c.col) for c in eb.cursors],
            [Cursor(a.line, a.col) if a else None for a in eb.sel_anchors],
            [int(x) for x in eb.cursor_ids],
            int(eb.primary),
        )

    def _restore_cursor_only(
        self,
        eb: EditorBuffer,
        snap: tuple[list[Cursor], list[Cursor | None], list[int], int],
    ) -> None:
        curs, anchors, cursor_ids, primary = snap
        eb.cursors[:] = [Cursor(c.line, c.col) for c in curs]
        eb.sel_anchors[:] = [Cursor(a.line, a.col) if a else None for a in anchors]
        eb.cursor_ids[:] = [int(x) for x in cursor_ids]
        eb.primary = int(primary)
        self._normalize_cursor_lists(eb)

    def push_jump(self) -> bool:
        """Push current cursor/selection state onto the jumplist.

        This is the navigation sibling of undo: it tracks *where you were*.
        Inspired by Vim/Helix jump lists.
        """

        eb = self.cur()
        snap = self._snapshot_cursor_only(eb)

        # Deduplicate consecutive identical entries.
        if eb.jump_list and eb.jump_index == len(eb.jump_list) - 1:
            if eb.jump_list[-1] == snap:
                return False

        # If we've jumped back, truncate the "forward" tail (browser/Vim semantics).
        if eb.jump_index >= 0 and eb.jump_index < len(eb.jump_list) - 1:
            eb.jump_list[:] = eb.jump_list[: eb.jump_index + 1]

        eb.jump_list.append(snap)
        eb.jump_index = len(eb.jump_list) - 1

        # Bounded size.
        MAX_JUMPS = 100
        if len(eb.jump_list) > MAX_JUMPS:
            drop = len(eb.jump_list) - MAX_JUMPS
            eb.jump_list[:] = eb.jump_list[drop:]
            eb.jump_index = max(-1, eb.jump_index - drop)

        return True

    def jump_back(self) -> bool:
        eb = self.cur()
        self._normalize_cursor_lists(eb)
        if eb.jump_index <= 0 or not eb.jump_list:
            return False
        eb.jump_index -= 1
        self._restore_cursor_only(eb, eb.jump_list[eb.jump_index])
        return True

    def jump_forward(self) -> bool:
        eb = self.cur()
        self._normalize_cursor_lists(eb)
        if not eb.jump_list:
            return False
        if eb.jump_index < 0:
            return False
        if eb.jump_index >= len(eb.jump_list) - 1:
            return False
        eb.jump_index += 1
        self._restore_cursor_only(eb, eb.jump_list[eb.jump_index])
        return True

    def jump_back_feedback(self) -> bool:
        """Jump backward and report the landed target or failure explicitly."""
        ok = self.jump_back()
        if ok:
            self.message(f"jumpback: {self.format_cursor_target()}")
        else:
            self.message("jumpback: no earlier jump")
        return ok

    def jump_forward_feedback(self) -> bool:
        """Jump forward and report the landed target or failure explicitly."""
        ok = self.jump_forward()
        if ok:
            self.message(f"jumpforward: {self.format_cursor_target()}")
        else:
            self.message("jumpforward: no later jump")
        return ok

    def _format_undo_redo_feedback(self, verb: str, edit: Edit) -> str:
        desc = str(getattr(edit, "description", "") or "").strip() or "change"
        target = ""
        try:
            target_fn = getattr(edit, "target", None)
            if callable(target_fn):
                target = str(target_fn() or "").strip()
        except Exception:
            target = ""
        msg = f"{verb}: {desc}"
        if target:
            msg += f" -> {target}"
        return msg

    def undo_feedback(self) -> bool:
        edit = self.undo.peek_undo()
        if edit is None:
            self.message("undo: nothing to undo")
            return False
        if not self.undo.undo():
            self.message("undo: nothing to undo")
            return False
        self.message(self._format_undo_redo_feedback("undo", edit))
        return True

    def redo_feedback(self) -> bool:
        edit = self.undo.peek_redo()
        if edit is None:
            self.message("redo: nothing to redo")
            return False
        if not self.undo.redo():
            self.message("redo: nothing to redo")
            return False
        self.message(self._format_undo_redo_feedback("redo", edit))
        return True

    def jump_to_index(self, idx: int) -> bool:
        """Jump to an explicit jumplist entry (0-based index)."""
        eb = self.cur()
        self._normalize_cursor_lists(eb)
        if not eb.jump_list:
            return False
        i = int(idx)
        if i < 0 or i >= len(eb.jump_list):
            return False
        eb.jump_index = i
        self._restore_cursor_only(eb, eb.jump_list[eb.jump_index])
        try:
            self.ensure_cursor_visible()
        except Exception:
            pass
        return True

    def jump_info(self) -> tuple[int, int]:
        eb = self.cur()
        return int(eb.jump_index), int(len(eb.jump_list))

    def clear_jumps(self) -> None:
        eb = self.cur()
        eb.jump_list.clear()
        eb.jump_index = -1
    def selection_range(self, i: int | None = None) -> tuple[Cursor, Cursor] | None:
        sel = self.selection(i)
        if sel is None:
            return None
        s, e = sel.normalized()
        if (s.line, s.col) == (e.line, e.col):
            return None
        return s, e

    def selection_text(self, i: int | None = None) -> str:
        rng = self.selection_range(i)
        if rng is None:
            return ""
        s, e = rng
        return self.cur().buf.get_range_text(s, e)

    def _all_selection_ranges(self) -> list[tuple[int, Cursor, Cursor]]:
        eb = self.cur()
        self._normalize_cursor_lists(eb)
        out: list[tuple[int, Cursor, Cursor]] = []
        for i in range(len(eb.cursors)):
            rng = self.selection_range(i)
            if rng is None:
                continue
            s, e = rng
            out.append((i, s, e))
        return out

    def _delete_selections(self) -> bool:
        """Delete all non-empty selections across cursors."""
        eb = self.cur()
        ranges = self._all_selection_ranges()
        if not ranges:
            return False
        # Delete from bottom to top so earlier coordinates remain valid.
        ranges.sort(key=lambda t: (t[1].line, t[1].col), reverse=True)
        for i, s, e in ranges:
            eb.cursors[i] = eb.buf.delete_range(s, e)
            eb.sel_anchors[i] = None
        return True

    # ----- files -----
    def _parse_open_target(self, raw_path: str) -> tuple[str, Cursor | None]:
        """Parse a tiny micro-esque ``file:line[:col]`` open target.

        The policy stays intentionally conservative and shared-core:
        - gated by the ``parsecursor`` option
        - if the literal path already exists, keep it literal (so existing
          colon-containing filenames remain openable)
        - line numbers are 1-based, columns are 0-based
        - malformed suffixes stay literal paths
        """

        raw = str(raw_path or "")
        if not bool(self.options.get("parsecursor")):
            return (raw, None)

        try:
            literal = Path(raw).expanduser()
            if literal.exists():
                return (raw, None)
        except OSError:
            return (raw, None)

        parts = raw.rsplit(':', 2)
        path_part = ""
        line_s = ""
        col_s: str | None = None
        if len(parts) == 2 and parts[0] and parts[1].isdigit():
            path_part, line_s = parts
            col_s = None
        elif len(parts) == 3 and parts[0] and parts[1].isdigit() and parts[2].isdigit():
            path_part, line_s, col_s = parts
        else:
            return (raw, None)

        line_no = max(1, int(line_s or "1")) - 1
        col_no = max(0, int(col_s or "0"))
        return (path_part, Cursor(line_no, col_no))

    def _set_buffer_primary_cursor(self, eb: EditorBuffer, cur: Cursor) -> None:
        """Clamp/set the primary cursor and clear its selection."""
        self._normalize_cursor_lists(eb)
        idx = int(eb.primary)
        eb.cursors[idx] = eb.buf.clamp(Cursor(int(cur.line), int(cur.col)))
        eb.sel_anchors[idx] = None

    def open_file(self, path: str, *, initial_cursor: Cursor | None = None) -> bool:
        parsed_path, parsed_cursor = self._parse_open_target(path)
        target_cursor = initial_cursor if initial_cursor is not None else parsed_cursor
        p = Path(str(parsed_path or "")).expanduser()
        fileformat = str(self.options.get("fileformat") or "unix")
        encoding_raw = str(self.options.get("encoding") or "utf-8").strip() or "utf-8"
        encoding = self._normalize_encoding_name(encoding_raw)

        # Refuse to open directories (deterministic UX + avoids exceptions).
        try:
            if p.exists() and p.is_dir():
                self.message(f"open: is a directory: {p}")
                return False
        except OSError:
            pass

        # If this file is already open (by normalized path), just switch to it.
        target_norm = self._normalize_path(str(p))
        if target_norm:
            for name, eb in self.buffers.items():
                if eb.buf.path and self._normalize_path(str(eb.buf.path)) == target_norm:
                    self.switch_buffer(name)
                    if target_cursor is not None:
                        self._set_buffer_primary_cursor(self.cur(), target_cursor)
                    self._push_recent_file(str(eb.buf.path))
                    return True

        text = ""
        if p.exists():
            raw = p.read_bytes().decode(encoding)
            text = raw.replace("\r\n", "\n").replace("\r", "\n")
            fileformat = self._detect_fileformat_from_text(raw)
        self.new_buffer(name=str(p), text=text, path=str(p), fileformat=fileformat, encoding=encoding_raw)
        if target_cursor is not None:
            self._set_buffer_primary_cursor(self.cur(), target_cursor)
        else:
            self._restore_cursor_for_buffer(self.cur())
        self._push_recent_file(str(p))

        # lifecycle hook
        try:
            self._emit_mx_hook("ed.on-open", str(self.cur().name), str(p), self.filetype())
        except Exception:
            pass
        return True

    def _save_buffer(self, eb: EditorBuffer) -> dict[str, object]:
        if bool(self.options.get("readonly", local=eb.local_options)):
            raise RuntimeError("Buffer is read-only")
        if not eb.buf.path:
            raise RuntimeError("Buffer has no path")
        p = Path(str(eb.buf.path))
        if p.exists() and p.is_dir():
            raise IsADirectoryError(str(p))

        before_text = eb.buf.get_text()
        normalized_text = before_text
        cleanup_parts: list[str] = []

        if bool(self.options.get("rmtrailingws", local=eb.local_options)):
            trimmed_lines = [str(line).rstrip(" \t") for line in eb.buf.lines]
            trimmed_text = "\n".join(trimmed_lines)
            if trimmed_text != normalized_text:
                normalized_text = trimmed_text
                cleanup_parts.append("trim trailing whitespace")

        if (
            bool(self.options.get("eofnewline", local=eb.local_options))
            and normalized_text != ""
            and not normalized_text.endswith("\n")
        ):
            normalized_text += "\n"
            cleanup_parts.append("add eof newline")

        if normalized_text != before_text:
            before = self._snapshot_buffer_state(eb)
            eb.buf.set_text(normalized_text)
            self._normalize_cursor_lists(eb)
            after = self._snapshot_buffer_state(eb)
            desc = cleanup_parts[0] if len(cleanup_parts) == 1 else "normalize save text"
            self._record_undo_snapshot(eb, before, after, desc)

        if bool(self.options.get("mkparents", local=eb.local_options)):
            p.parent.mkdir(parents=True, exist_ok=True)

        fileformat = str(self.options.get("fileformat", local=eb.local_options) or "unix").strip().lower()
        if fileformat == "dos":
            save_text = eb.buf.get_text().replace("\n", "\r\n")
        else:
            save_text = eb.buf.get_text()
        encoding_raw = str(self.options.get("encoding", local=eb.local_options) or "utf-8")
        encoding = self._normalize_encoding_name(encoding_raw)
        p.write_bytes(save_text.encode(encoding))
        eb.buf.mark_clean()
        eb.autosave_dirty_since = None
        self._push_recent_file(str(eb.buf.path))
        self._remember_cursor_for_buffer(eb)
        try:
            self._emit_mx_hook("ed.on-save", str(eb.name), str(eb.buf.path))
        except Exception:
            pass
        return {
            "path": str(eb.buf.path),
            "cleanup_parts": list(cleanup_parts),
            "fileformat": fileformat,
            "encoding": str(encoding_raw).strip() or "utf-8",
        }

    def save(self) -> dict[str, object]:
        return self._save_buffer(self.cur())

    def autosave_dirty_buffers(self, *, now: float | None = None, immediate: bool = False) -> list[str]:
        when = float(self.now() if now is None else now)
        saved: list[str] = []
        for eb in list(self.buffers.values()):
            if not bool(getattr(eb.buf, "dirty", False)):
                eb.autosave_dirty_since = None
                continue
            if self._autosave_seconds(eb) <= 0:
                eb.autosave_dirty_since = None
                continue
            if not str(getattr(eb.buf, "path", "") or ""):
                continue
            if bool(self.options.get("readonly", local=eb.local_options)):
                continue
            if not immediate and not self._autosave_buffer_due(eb, now=when):
                continue
            if immediate and eb.autosave_dirty_since is None:
                eb.autosave_dirty_since = when
            try:
                self._save_buffer(eb)
                saved.append(str(eb.name))
            except Exception as e:
                eb.autosave_dirty_since = when
                self.message(f"autosave error: {eb.name}: {e}")
        return saved

    def load_user_init(self, *, path: str | None = None) -> bool:
        """Load a user init/rc file (best-effort).

        Default path: ~/.config/micromax/init.mx
        Override via the MICROMAX_INIT environment variable or the explicit path arg.

        Returns True when a file existed and was evaluated successfully.
        """
        raw = path or os.environ.get("MICROMAX_INIT") or "~/.config/micromax/init.mx"
        p = Path(raw).expanduser()
        if not p.exists() or p.is_dir():
            return False
        try:
            self.vm.eval(p.read_text(encoding="utf-8"), filename=str(p))
        except Exception as e:
            self.message(f"init error: {e}")
            return False
        return True

    # ----- viewport (scrolling model) -----
    def viewport_model(self) -> dict[str, int]:
        """Return the current viewport model.

        This is UI-owned state, but stored in the headless core so actions can
        keep the cursor visible and future renderers can share semantics.
        """
        return {
            "top_line": int(self.viewport_top_line),
            "top_subline": int(self.viewport_top_subline),
            "left_col": int(self.viewport_left_col),
            "height": int(self.viewport_height),
            "width": int(self.viewport_width),
        }

    def set_viewport(
        self,
        *,
        top_line: int | None = None,
        top_subline: int | None = None,
        left_col: int | None = None,
        height: int | None = None,
        width: int | None = None,
        follow_cursor: bool = True,
    ) -> None:
        """Set viewport fields (best-effort clamped)."""
        if height is not None:
            self.viewport_height = max(1, int(height))
        if width is not None:
            self.viewport_width = max(1, int(width))

        eb = self.cur()
        softwrap = bool(self.options.get("softwrap", local=eb.local_options))
        # When softwrap is enabled, horizontal scrolling is disabled.
        if softwrap:
            self.viewport_left_col = 0
        max_top = max(0, len(eb.buf.lines) - 1)
        # Softwrap introduces a secondary vertical offset: which wrapped row within
        # `top_line` is at the top of the viewport.
        if not bool(self.options.get("softwrap", local=eb.local_options)):
            self.viewport_top_subline = 0
        if top_subline is not None:
            self.viewport_top_subline = max(0, int(top_subline))
        if top_line is not None:
            self.viewport_top_line = max(0, min(int(top_line), max_top))
            if top_subline is None:
                self.viewport_top_subline = 0
        if left_col is not None:
            # When softwrap is enabled, horizontal scrolling is disabled.
            if bool(self.options.get("softwrap", local=eb.local_options)):
                self.viewport_left_col = 0
            else:
                self.viewport_left_col = max(0, int(left_col))
        if follow_cursor:
            self.ensure_cursor_visible()

    # ----- softwrap visual-row mapping helpers -----
    def _softwrap_contindent_setting(self, eb: "EditorBuffer") -> int:
        try:
            return int(self.options.get("softwrap.contindent", local=eb.local_options))
        except Exception:
            return -1

    def _tabmovement_step(self, eb: "EditorBuffer", line: str, col: int, *, direction: int) -> int:
        """Return the horizontal cursor delta for micro-esque `tabmovement`.

        When `tabstospaces` and `tabmovement` are both enabled, leading runs of
        exactly `tabsize` spaces behave like one tab stop for left/right motion.
        This mirrors micro's conservative rule closely:

        - only the leading indentation run participates
        - only exact all-space chunks of width `tabsize` are collapsed
        - otherwise movement stays character-wise
        """
        try:
            enabled = bool(self.options.get("tabmovement", local=eb.local_options))
            spaces = bool(self.options.get("tabstospaces", local=eb.local_options))
            tabsize = int(self.options.get("tabsize", local=eb.local_options))
        except Exception:
            return -1 if int(direction) < 0 else 1

        if (not enabled) or (not spaces) or tabsize <= 1:
            return -1 if int(direction) < 0 else 1

        s = str(line or "")
        col = max(0, min(int(col), len(s)))

        def _indent_only(prefix: str) -> bool:
            return all(ch in (" ", "\t") for ch in str(prefix or ""))

        if int(direction) < 0:
            start = col - tabsize
            if start >= 0 and s[start:col] == (" " * tabsize) and _indent_only(s[:start]):
                return -tabsize
            return -1

        end = col + tabsize
        if end < len(s) and s[col:end] == (" " * tabsize) and _indent_only(s[:col]):
            return tabsize
        return 1

    @staticmethod
    def _leading_ws_cols(s: str) -> int:
        # Count leading spaces/tabs as visual columns (tabs count as 1 here; renderers may expand later).
        n = 0
        for ch in str(s or ""):
            if ch in (" ", "    "):
                n += 1
            else:
                break
        return int(n)

    def _contindent_for_line(self, eb: "EditorBuffer", s: str, *, w: int) -> int:
        """Continuation indent for wrapped fragments under softwrap.

        This mirrors the common UX of "use the original line's indent for wrapped
        fragments", while keeping the model tiny and deterministic.
        """
        w = int(w)
        if w <= 1:
            return 0
        setting = self._softwrap_contindent_setting(eb)
        if setting == 0:
            return 0
        if setting < 0:
            lead = self._leading_ws_cols(s)
            max_cont = min(8, w - 1)
            return max(0, min(int(lead), int(max_cont)))
        return max(0, min(int(setting), w - 1))

    @staticmethod
    def _wrap_seg(w: int, cont: int) -> int:
        w = int(w)
        cont = max(0, int(cont))
        if w <= 0:
            return 1
        if cont <= 0:
            return max(1, w)
        return max(1, w - cont)

    def _wordwrap_enabled(self, eb: "EditorBuffer") -> bool:
        try:
            return bool(self.options.get("wordwrap", local=eb.local_options))
        except Exception:
            return False

    @staticmethod
    def _find_wordwrap_break(s: str, start: int, end: int) -> int | None:
        """Return the next row start for [start:end] when breaking at spaces.

        The returned value is an absolute character index strictly greater than
        ``start``. The break prefers the final whitespace character that fits in
        the current row, which keeps every source character visible while still
        biasing the wrap boundary toward word edges.
        """
        start = max(0, int(start))
        end = max(start, int(end))
        if end - start <= 1:
            return None
        for idx in range(end - 1, start, -1):
            if str(s[idx]).isspace():
                return idx + 1
        return None

    def _wrap_row_starts_for_line_with_cont(
        self,
        eb: "EditorBuffer",
        s: str,
        w: int,
        cont: int,
    ) -> list[int]:
        w = int(w)
        if w <= 0 or s == "":
            return [0]
        cont = max(0, min(int(cont), w - 1))
        wordwrap = self._wordwrap_enabled(eb)
        starts = [0]
        start = 0
        row = 0
        s_len = len(s)
        while start < s_len:
            cap = max(1, w if row <= 0 else self._wrap_seg(w, cont))
            end = min(s_len, start + cap)
            if end >= s_len:
                break
            next_start = self._find_wordwrap_break(s, start, end) if wordwrap else None
            if next_start is None or next_start <= start:
                next_start = end
            starts.append(int(next_start))
            start = int(next_start)
            row += 1
        return starts

    def _wrap_row_starts_for_line(self, eb: "EditorBuffer", s: str, *, w: int) -> list[int]:
        cont = self._contindent_for_line(eb, s, w=w)
        return self._wrap_row_starts_for_line_with_cont(eb, s, int(w), int(cont))

    def _wrap_start_for_row_in_line(self, eb: "EditorBuffer", s: str, *, w: int, row: int) -> int:
        starts = self._wrap_row_starts_for_line(eb, s, w=w)
        row = max(0, min(int(row), max(0, len(starts) - 1)))
        return int(starts[row])

    def _wrap_end_for_row_in_line(self, eb: "EditorBuffer", s: str, *, w: int, row: int) -> int:
        starts = self._wrap_row_starts_for_line(eb, s, w=w)
        row = max(0, min(int(row), max(0, len(starts) - 1)))
        if row + 1 < len(starts):
            return int(starts[row + 1])
        return int(len(s))

    def _wrap_cap_for_row_in_line(self, eb: "EditorBuffer", s: str, *, w: int, row: int) -> int:
        start = self._wrap_start_for_row_in_line(eb, s, w=w, row=row)
        end = self._wrap_end_for_row_in_line(eb, s, w=w, row=row)
        return max(0, int(end - start))

    def _wraps_for_line_with_cont(self, eb: "EditorBuffer", s: str, w: int, cont: int) -> int:
        return len(self._wrap_row_starts_for_line_with_cont(eb, s, int(w), int(cont)))

    def _wrap_row_for_col_with_cont(self, eb: "EditorBuffer", s: str, col: int, w: int, cont: int) -> int:
        """Return wrap-row index for a character column in a softwrapped line."""
        w = int(w)
        if w <= 0:
            return 0
        starts = self._wrap_row_starts_for_line_with_cont(eb, s, w, cont)
        col = max(0, min(int(col), len(s)))
        row = 0
        for idx, start in enumerate(starts):
            if col < int(start):
                break
            row = idx
        return int(row)

    def _wraps_for_line(self, eb: "EditorBuffer", s: str, *, w: int) -> int:
        cont = self._contindent_for_line(eb, s, w=w)
        return self._wraps_for_line_with_cont(eb, s, int(w), int(cont))

    def _visual_row_index(self, eb: "EditorBuffer", line: int, wrap_row: int, *, w: int) -> int:
        """Return global visual-row index for (line, wrap_row)."""
        line = max(0, min(int(line), max(0, len(eb.buf.lines) - 1)))
        wrap_row = max(0, int(wrap_row))
        y = 0
        for li in range(0, line):
            y += self._wraps_for_line(eb, eb.buf.lines[li], w=int(w))
        return int(y + wrap_row)

    def _cursor_visual_yx(self, eb: "EditorBuffer", c: "Cursor", *, w: int) -> tuple[int, int]:
        """Return (global_y, x_in_wrap_row) for cursor c under width w."""
        w = int(w)
        if w <= 0:
            return (int(c.line), int(c.col))
        line = max(0, min(int(c.line), max(0, len(eb.buf.lines) - 1)))
        s = eb.buf.lines[line] if line < len(eb.buf.lines) else ""
        col = max(0, min(int(c.col), len(s)))
        cont = self._contindent_for_line(eb, s, w=w)
        wrap_row = self._wrap_row_for_col_with_cont(eb, s, col, w, cont)
        wrap_start = self._wrap_start_for_row_in_line(eb, s, w=w, row=wrap_row)
        x = (col - wrap_start) + (cont if wrap_row > 0 else 0)
        y = self._visual_row_index(eb, line, wrap_row, w=w)
        return (int(y), int(x))

    def _total_visual_rows(self, eb: "EditorBuffer", *, w: int) -> int:
        w = int(w)
        if w <= 0:
            return max(1, len(eb.buf.lines))
        return max(1, sum(self._wraps_for_line(eb, s, w=w) for s in eb.buf.lines))

    def _doc_pos_for_visual_row(self, eb: "EditorBuffer", target_y: int, goal_x: int, *, w: int) -> "Cursor":
        """Map a global visual-row index + desired x to a document Cursor."""
        w = int(w)
        if w <= 0:
            # Fallback: treat visual rows as logical lines.
            li = max(0, min(int(target_y), max(0, len(eb.buf.lines) - 1)))
            s = eb.buf.lines[li] if li < len(eb.buf.lines) else ""
            return Cursor(li, max(0, min(int(goal_x), len(s))))

        y = max(0, int(target_y))
        goal_x = max(0, int(goal_x))
        acc = 0
        if not eb.buf.lines:
            return Cursor(0, 0)
        for li, s in enumerate(eb.buf.lines):
            cont = self._contindent_for_line(eb, s, w=w)
            wraps = self._wraps_for_line_with_cont(eb, s, w, cont)
            if y < acc + wraps:
                sub = y - acc
                if s == "":
                    return Cursor(li, 0)
                wrap_start = self._wrap_start_for_row_in_line(eb, s, w=w, row=sub)
                row_end = self._wrap_end_for_row_in_line(eb, s, w=w, row=sub)
                if sub <= 0:
                    col = min(wrap_start + goal_x, row_end)
                    return Cursor(li, col)
                # continuation row: x includes indent
                if goal_x <= cont:
                    return Cursor(li, wrap_start)
                col = min(wrap_start + (goal_x - cont), row_end)
                return Cursor(li, col)
            acc += wraps
        # Clamp to end of last line.
        li = len(eb.buf.lines) - 1
        s = eb.buf.lines[li]
        return Cursor(li, len(s))

    def _viewport_visual_start(self, eb: "EditorBuffer", *, w: int) -> int:
        """Return global visual-row index for the viewport's top."""
        w = int(w)
        top = max(0, min(int(self.viewport_top_line), max(0, len(eb.buf.lines) - 1)))
        sub = max(0, int(self.viewport_top_subline))
        if w <= 0:
            return int(top)
        s = eb.buf.lines[top] if top < len(eb.buf.lines) else ""
        wraps = self._wraps_for_line(eb, s, w=w)
        sub = min(sub, max(0, wraps - 1))
        return self._visual_row_index(eb, top, sub, w=w)

    def _set_viewport_from_visual_start(self, eb: "EditorBuffer", start_y: int, *, w: int) -> None:
        """Set viewport_top_line/top_subline from a global visual-row index."""
        w = int(w)
        if not eb.buf.lines:
            self.viewport_top_line = 0
            self.viewport_top_subline = 0
            return
        if w <= 0:
            self.viewport_top_line = max(0, min(int(start_y), max(0, len(eb.buf.lines) - 1)))
            self.viewport_top_subline = 0
            return
        y = max(0, int(start_y))
        acc = 0
        for li, s in enumerate(eb.buf.lines):
            wraps = self._wraps_for_line(eb, s, w=w)
            if y < acc + wraps:
                self.viewport_top_line = li
                self.viewport_top_subline = y - acc
                return
            acc += wraps
        self.viewport_top_line = len(eb.buf.lines) - 1
        self.viewport_top_subline = 0


    def _move_cursors_visual(self, dy: int, *, extend_selection: bool = False) -> bool:
        """Move all cursors by dy visual rows when softwrap is enabled."""
        eb = self.cur()
        self._normalize_cursor_lists(eb)
        w = int(self.viewport_width)
        if w <= 0:
            # no viewport width yet; fall back to logical-line motion
            for i, c in enumerate(eb.cursors):
                eb.cursors[i] = eb.buf.clamp(Cursor(int(c.line) + int(dy), int(c.col)))
            if not extend_selection:
                self.clear_selection()
            return True

        total = self._total_visual_rows(eb, w=w)
        # Maintain per-cursor goal x (visual column) for vertical motions.
        if not hasattr(eb, "goal_x_by_cursor"):
            eb.goal_x_by_cursor = {}  # type: ignore[attr-defined]

        for i, c in enumerate(eb.cursors):
            cid = int(eb.cursor_ids[i]) if i < len(eb.cursor_ids) else i
            y, x = self._cursor_visual_yx(eb, c, w=w)
            goal_x = int(eb.goal_x_by_cursor.get(cid, x))  # type: ignore[attr-defined]
            target_y = max(0, min(int(y) + int(dy), max(0, total - 1)))
            eb.cursors[i] = eb.buf.clamp(self._doc_pos_for_visual_row(eb, target_y, goal_x, w=w))

        if not extend_selection:
            self.clear_selection()
        return True

    def ensure_cursor_visible(self) -> None:
        """Adjust viewport so the primary cursor is visible."""
        try:
            eb = self.cur()
            self._normalize_cursor_lists(eb)
            c = eb.cursors[eb.primary]
        except Exception:
            return
        h = int(self.viewport_height)
        w = int(self.viewport_width)
        if h <= 0 or w <= 0:
            return

        try:
            raw_scrollmargin = int(self.options.get("scrollmargin", local=eb.local_options))
        except Exception:
            raw_scrollmargin = 0
        scrollmargin = max(0, min(int(raw_scrollmargin), max(0, (h - 1) // 2)))

        softwrap = bool(self.options.get("softwrap", local=eb.local_options))

        # vertical
        if not softwrap:
            if int(c.line) < int(self.viewport_top_line) + scrollmargin:
                self.viewport_top_line = max(0, int(c.line) - scrollmargin)
            elif int(c.line) > int(self.viewport_top_line) + h - 1 - scrollmargin:
                self.viewport_top_line = max(0, int(c.line) - h + 1 + scrollmargin)
            self.viewport_top_subline = 0
        else:
            # Softwrap scrolling is in *visual rows* (wrapped fragments), not logical lines.
            start_y = self._viewport_visual_start(eb, w=w)
            cur_y, _cur_x = self._cursor_visual_yx(eb, c, w=w)
            total = self._total_visual_rows(eb, w=w)
            max_start = max(0, total - h)
            if cur_y < start_y + scrollmargin:
                start_y = cur_y - scrollmargin
            elif cur_y > start_y + h - 1 - scrollmargin:
                start_y = cur_y - h + 1 + scrollmargin
            start_y = max(0, min(int(start_y), int(max_start)))
            self._set_viewport_from_visual_start(eb, start_y, w=w)

        # horizontal
        if bool(self.options.get("softwrap", local=eb.local_options)):
            # softwrap disables horizontal scrolling
            self.viewport_left_col = 0
        else:
            if int(c.col) < int(self.viewport_left_col):
                self.viewport_left_col = int(c.col)
            elif int(c.col) >= int(self.viewport_left_col) + w:
                self.viewport_left_col = max(0, int(c.col) - w + 1)

        # Clamp top against buffer length.
        self.viewport_top_line = max(0, min(int(self.viewport_top_line), max(0, len(eb.buf.lines) - 1)))
        if softwrap and eb.buf.lines:
            wraps = self._wraps_for_line(eb, eb.buf.lines[int(self.viewport_top_line)], w=int(w))
            self.viewport_top_subline = max(0, min(int(self.viewport_top_subline), max(0, wraps - 1)))
        else:
            self.viewport_top_subline = 0
        self.viewport_left_col = max(0, int(self.viewport_left_col))


    def view_rows(self, *, height: int | None = None, width: int | None = None) -> list[tuple[int, int, str]]:
        """Return screen rows for the active buffer under the current viewport.

        Each row is a tuple: (line_index, start_col, fragment).

        - When softwrap is disabled, start_col is the viewport's left_col and
          fragment is a simple substring slice.
        - When softwrap is enabled, long logical lines are wrapped into multiple
          screen rows and start_col is the wrap's starting *character* column.

        Notes:
          - This is a **rendering model**, not a UI. It intentionally ignores
            styling/spans for now.
          - Tabs are treated as single characters here; a future renderer can
            expand tabs to visual columns.
        """

        eb = self.cur()
        h = int(height if height is not None else self.viewport_height)
        w = int(width if width is not None else self.viewport_width)
        if h <= 0 or w <= 0:
            return []

        top = int(self.viewport_top_line)
        left = int(self.viewport_left_col)
        softwrap = bool(self.options.get("softwrap", local=eb.local_options))

        rows: list[tuple[int, int, str]] = []
        if not softwrap:
            for row in range(h):
                li = top + row
                if li >= len(eb.buf.lines):
                    break
                ln = eb.buf.lines[li]
                frag = ln[left : left + w]
                rows.append((li, left, frag))
            return rows

        # softwrap: walk logical lines, emit wrapped fragments until the screen fills.
        li = top
        first_subline = max(0, int(self.viewport_top_subline))
        while li < len(eb.buf.lines) and len(rows) < h:
            ln = eb.buf.lines[li]
            if ln == "":
                rows.append((li, 0, ""))
                li += 1
                continue

            cont = self._contindent_for_line(eb, ln, w=w)
            wraps = self._wraps_for_line_with_cont(eb, ln, w, cont)
            sub = first_subline if li == top else 0
            sub = max(0, min(int(sub), max(0, wraps - 1)))

            while len(rows) < h and sub < wraps:
                start = self._wrap_start_for_row_in_line(eb, ln, w=w, row=sub)
                cap = self._wrap_cap_for_row_in_line(eb, ln, w=w, row=sub)
                prefix = (" " * cont) if sub > 0 and cont > 0 else ""
                frag = prefix + ln[start : start + cap]
                rows.append((li, start, frag))
                sub += 1
            li += 1
        return rows

    def cursor_view_pos(self, *, height: int | None = None, width: int | None = None) -> tuple[int, int]:
        """Return (y, x) of the primary cursor within the current viewport.

        For softwrap, this maps the cursor into wrapped screen rows.
        """
        try:
            eb = self.cur()
            self._normalize_cursor_lists(eb)
            c = eb.cursors[eb.primary]
        except Exception:
            return (0, 0)

        h = int(height if height is not None else self.viewport_height)
        w = int(width if width is not None else self.viewport_width)
        if h <= 0 or w <= 0:
            return (0, 0)

        top = int(self.viewport_top_line)
        left = int(self.viewport_left_col)
        softwrap = bool(self.options.get("softwrap", local=eb.local_options))

        if not softwrap:
            return (int(c.line) - top, int(c.col) - left)

        start_y = self._viewport_visual_start(eb, w=w)
        cy, cx = self._cursor_visual_yx(eb, c, w=w)
        y = int(cy) - int(start_y)
        x = int(cx)
        return (y, x)

    # ----- timers (host-driven, deterministic) -----
    def now(self) -> float:
        return float(self._now_fn())

    def pump_timers(self, *, limit: int = 1000) -> int:
        """Run due timer callbacks.

        Timer callbacks run in the embedded VM and are treated like hooks:
        best-effort notifications. We isolate stack effects and record
        exceptions as editor messages.
        """

        now = self.now()
        tasks = self.timers.pop_due(now=now, limit=int(limit))
        ran = 0
        for t in tasks:
            depth = len(self.vm.stack)
            try:
                self.vm.exec_xt(t.xt)
            except Exception as e:
                self.message(f"timer {t.task_id} error: {e}")
            finally:
                del self.vm.stack[depth:]
            ran += 1
        try:
            self.autosave_dirty_buffers(now=now)
        except Exception:
            pass
        return int(ran)

    # ----- syntax highlighting (span model) -----
    def highlight_tags(self) -> list[str]:
        return list(HIGHLIGHT_TAGS)

    def highlight_spans(self, start: int, count: int) -> list[list[list[object]]]:
        """Return per-line highlight spans for the active buffer.

        Result is a list aligned with the requested range: out[0] contains
        spans for line `start`. Each per-line span is [start_col, end_col, tag].

        This is intentionally tiny; renderers/themes decide how to map tags to
        color or attributes.
        """

        eb = self.cur()
        lines = eb.buf.lines
        if int(count) <= 0 or not lines:
            return []
        a = max(0, int(start))
        b = min(len(lines), a + int(count))
        ft = str(self.filetype())
        return [highlight_line(ft, str(lines[i])) for i in range(a, b)]

    def page_height(self, *, eb: EditorBuffer | None = None) -> int:
        """Return the current page movement size.

        If a UI has set a viewport height, page movement uses it. Otherwise we
        fall back to the `page.height` option.
        """
        if int(self.viewport_height) > 0:
            return int(self.viewport_height)
        eb2 = eb or self.cur()
        return int(self.options.get("page.height", local=eb2.local_options))

    def page_step(self, *, eb: EditorBuffer | None = None) -> int:
        """Return the effective PageUp/PageDown jump.

        The jump is the page height minus the configured overlap, clamped so a
        page move always advances by at least one logical/visual row.
        """
        eb2 = eb or self.cur()
        page = max(1, int(self.page_height(eb=eb2)))
        try:
            raw_overlap = int(self.options.get("pageoverlap", local=eb2.local_options))
        except Exception:
            raw_overlap = 0
        overlap = max(0, min(int(raw_overlap), max(0, page - 1)))
        return max(1, int(page) - int(overlap))

    def is_protected_buffer(self, eb: EditorBuffer | None = None) -> bool:
        """Return True if this buffer is marked as protected/read-only."""

        eb2 = eb or self.cur()
        try:
            return bool(self.options.get("readonly", local=eb2.local_options))
        except Exception:
            return False

    # ----- status / infobar model -----
    def editor_mode(self) -> str:
        """Return a tiny, headless editor mode label.

        This is intentionally conservative: until we have richer modal editing,
        the statusline model only distinguishes normal editing from active prompt
        modes. Macro recording/playback are reported as orthogonal flags in the
        status model instead of becoming separate editor modes.
        """

        if self.prompt is not None:
            kind = str(self.prompt.kind or "").strip().lower()
            return kind or "prompt"
        capture_mode = self.current_capture_key_mode()
        if capture_mode is not None:
            return str(capture_mode)
        return "normal"

    def capture_status_model(self) -> dict[str, Any]:
        """Return a small, portable model for active capture keymodes.

        Capture keymodes already exist as shared editor behavior (`qreplace`,
        `openurl`), but future UIs/statuslines/scripts should not have to parse
        transient TUI message text to understand them.
        """

        mode = str(self.current_capture_key_mode() or "")
        out: dict[str, Any] = {
            "capture_kind": "",
            "capture_summary": "",
            "capture_detail": "",
            "capture_progress": "",
            "capture_source": "",
            "capture_search": "",
            "capture_replace": "",
            "capture_url": "",
            "capture_examined": 0,
            "capture_count": 0,
            "capture_replaced": 0,
        }
        if not mode:
            return out

        out["capture_kind"] = mode
        if mode == "qreplace" and self.qreplace is not None:
            sess = self.qreplace
            examined = max(0, int(sess.examined or 0))
            total = max(0, int(sess.total or 0))
            shown = min(examined, total) if total > 0 else 0
            replaced = max(0, int(sess.replaced or 0))
            progress = f"{shown}/{total}" if total > 0 else ""
            head = "?replace"
            bits: list[str] = []
            if progress:
                bits.append(progress)
            if replaced > 0:
                bits.append(f"{replaced} repl")
            if bits:
                head += " [" + " • ".join(bits) + "]"
            out.update(
                {
                    "capture_summary": head,
                    "capture_detail": f"{sess.search} -> {sess.value}".strip(),
                    "capture_progress": progress,
                    "capture_search": str(sess.search),
                    "capture_replace": str(sess.value),
                    "capture_examined": examined,
                    "capture_count": total,
                    "capture_replaced": replaced,
                }
            )
            return out

        if mode == "openurl":
            source = str(getattr(self, "_pending_open_url_source", "") or "").strip().lower()
            if source == "help":
                head = "?open external link from help"
            elif source == "cursor":
                head = "?open external link under cursor"
            elif source == "command":
                head = "?open external link from command"
            else:
                head = "?open external link"
            detail = str(getattr(self, "_pending_open_url", "") or "").strip()
            out.update(
                {
                    "capture_summary": head,
                    "capture_detail": detail,
                    "capture_source": source,
                    "capture_url": detail,
                }
            )
            return out

        out["capture_summary"] = mode
        return out

    def interaction_status_model(self) -> dict[str, Any]:
        """Return a tiny shared model for the active bottom-row interaction.

        This intentionally sits one level above the raw prompt/capture state: it
        describes the *current visible prompt-style interaction surface* that the
        minimal TUI would show on the bottom row, while still staying plain and
        inspectable for future UIs, statuslines, scripts, and tests.
        """

        out: dict[str, Any] = {
            "interaction_active": 0,
            "interaction_kind": "",
            "interaction_prefix": "",
            "interaction_summary": "",
            "interaction_detail": "",
            "interaction_position": "",
            "interaction_line": "",
        }

        capture = self.capture_status_model()
        capture_kind = str(capture.get("capture_kind", "") or "")
        if capture_kind:
            summary = str(capture.get("capture_summary", "") or "")
            detail = str(capture.get("capture_detail", "") or "")
            position = str(capture.get("capture_progress", "") or "")
            line = summary
            if detail:
                line += "  | " + detail
            out.update(
                {
                    "interaction_active": 1,
                    "interaction_kind": capture_kind,
                    "interaction_prefix": "?",
                    "interaction_summary": summary,
                    "interaction_detail": detail,
                    "interaction_position": position,
                    "interaction_line": line,
                }
            )
            return out

        if self.prompt is None:
            return out

        kind = str(self.prompt.kind or "")
        if kind in ("command", "palette"):
            prefix = ":"
        elif kind == "find":
            prefix = "/"
        else:
            prefix = "?"
        summary = prefix + str(self.prompt.text or "")
        position = ""
        detail = ""
        if kind == "find":
            position = str(self.search_position_model().get("summary", "") or "")
        elif kind not in ("command", "find"):
            position = str(self.prompt_current_position().get("summary", "") or "")
            detail = str(self.prompt_current_preview() or "")

        line = summary
        if position:
            line += "  [" + position + "]"
        if detail:
            line += "  | " + detail

        out.update(
            {
                "interaction_active": 1,
                "interaction_kind": kind,
                "interaction_prefix": prefix,
                "interaction_summary": summary,
                "interaction_detail": detail,
                "interaction_position": position,
                "interaction_line": line,
            }
        )
        return out

    def interaction_model(self, width: int) -> dict[str, Any]:
        """Return a tiny shared layout model for the visible prompt/capture row.

        This is the width-aware sibling of ``interaction_status_model()``: it
        preserves the same prompt/capture metadata while also exposing the final
        visible row text that the minimal curses TUI would paint for a given
        width.
        """

        w = max(0, int(width))
        out: dict[str, Any] = {
            "active": 0,
            "width": w,
            "kind": "",
            "prefix": "",
            "summary": "",
            "detail": "",
            "position": "",
            "raw_line": "",
            "text": "",
            "truncated": 0,
        }
        if w <= 0:
            return out

        interaction = self.interaction_status_model()
        raw_line = str(interaction.get("interaction_line", "") or "")
        if not raw_line:
            return out

        text = _ellipsize_right(raw_line, w)
        out.update(
            {
                "active": 1,
                "kind": str(interaction.get("interaction_kind", "") or ""),
                "prefix": str(interaction.get("interaction_prefix", "") or ""),
                "summary": str(interaction.get("interaction_summary", "") or ""),
                "detail": str(interaction.get("interaction_detail", "") or ""),
                "position": str(interaction.get("interaction_position", "") or ""),
                "raw_line": raw_line,
                "text": text,
                "truncated": 1 if text != raw_line else 0,
            }
        )
        return out

    def keymenu_model(self, width: int) -> dict[str, Any]:
        """Return a tiny shared model for the visible keymenu row.

        The model stays deliberately small and text-first: it exposes the
        current context plus the visible shortcut entries so future UIs,
        scripts, tests, and LLMs do not need to reverse-engineer the row from a
        dimmed curses string.
        """

        w = max(0, int(width))
        out: dict[str, Any] = {
            "active": 0,
            "width": w,
            "context": "",
            "entries": [],
            "text": "",
            "truncated": 0,
        }
        if w <= 0:
            return out
        try:
            local = self.cur().local_options
            visible = bool(self.options.get("keymenu", local=local))
        except Exception:
            local = None
            visible = True

        prompt = self.prompt
        capture_mode = self.current_capture_key_mode()
        context = "normal"
        entries: list[dict[str, str]] = []

        def add_entry(key: str, label: str) -> None:
            entries.append({"key": str(key), "label": str(label), "text": f"{key} {label}".strip()})

        if prompt is not None:
            kind = str(prompt.kind or "")
            context = kind or "prompt"
            if kind not in ("command", "find") and prompt.suggestion_rows:
                add_entry("Enter", "Choose")
                add_entry("Esc", "Cancel")
                add_entry("Up/Down", "Move")
                add_entry("PgUp/PgDn", "Page")
                add_entry("Alt-Up/Down", "Section")
            elif kind == "find":
                add_entry("Enter", "Next")
                add_entry("Esc", "Cancel")
                add_entry("Up/Down", "Hist")
                add_entry("Home/End", "Move")
            else:
                add_entry("Enter", "Run")
                add_entry("Esc", "Cancel")
                add_entry("Up/Down", "Hist")
                add_entry("Home/End", "Move")
        elif capture_mode == "qreplace":
            context = "qreplace"
            add_entry("Y/Enter", "Replace")
            add_entry("N", "Skip")
            add_entry("A", "All")
            add_entry("L", "Last")
            add_entry("Q/Esc", "Quit")
        elif capture_mode == "openurl":
            context = "openurl"
            add_entry("Y/Enter", "Open")
            add_entry("N/Esc", "Cancel")
            add_entry("C", "Copy")
        else:
            add_entry("^Q", "Quit")
            add_entry("^S", "Save")
            add_entry("^F", "Find")
            add_entry("^E", "Cmd")
            add_entry("^O", "Open")
            add_entry("^G", "Help")

        raw_text = "  ".join(str(row.get("text", "") or "") for row in entries if str(row.get("text", "") or ""))
        text = raw_text[:w]
        out.update(
            {
                "active": 1 if visible else 0,
                "context": context,
                "entries": entries,
                "text": text,
                "truncated": 1 if text != raw_text else 0,
            }
        )
        return out

    def keymenu_text(self, width: int) -> str:
        """Return a tiny nano-style key-menu summary for the current context."""

        return str(self.keymenu_model(width).get("text", "") or "")

    def constantshow_text(self) -> str:
        """Return a tiny cursor summary for the idle infobar."""

        st = self.status_model()
        line = max(1, int(st.get("display_line", 1) or 1))
        total = max(1, int(st.get("line_count", 1) or 1))
        col = max(1, int(st.get("display_col", 1) or 1))
        pct = max(0, min(100, int(st.get("percentage", 0) or 0)))
        return f"Ln {line}/{total}, Col {col} ({pct}%)"

    def infobar_model(self, width: int) -> dict[str, Any]:
        """Return a tiny shared layout model for the visible idle infobar row.

        This mirrors the current tiny policy used by the curses TUI: the left
        side carries the last message, `constantshow` optionally claims the
        right edge for a compact cursor summary, and the right side wins when
        space is tight.
        """

        w = max(0, int(width))
        out: dict[str, Any] = {
            "active": 0,
            "width": w,
            "message_raw": "",
            "summary_raw": "",
            "message": "",
            "summary": "",
            "padding": "",
            "padding_width": 0,
            "constantshow": 0,
            "truncated_message": 0,
            "truncated_summary": 0,
            "text": "",
        }
        if w <= 0:
            return out

        try:
            eb = self.cur()
            local = eb.local_options
        except Exception:
            eb = None
            local = None
        if not bool(self.options.get("infobar", local=local)):
            return out
        st = self.status_model()
        if bool(st.get("interaction_active", 0) or 0):
            return out

        message_raw = str(st.get("last_message", "") or "")
        constantshow = 1 if bool(self.options.get("constantshow", local=local)) else 0
        summary_raw = self.constantshow_text().strip() if constantshow else ""
        message = message_raw
        summary = summary_raw
        padding = ""
        truncated_message = 0
        truncated_summary = 0

        if not constantshow or not summary_raw:
            message = _ellipsize_right(message_raw, w)
            truncated_message = 1 if message != message_raw else 0
            out.update(
                {
                    "active": 1,
                    "message_raw": message_raw,
                    "summary_raw": summary_raw,
                    "message": message,
                    "summary": "",
                    "constantshow": constantshow,
                    "truncated_message": truncated_message,
                    "text": message,
                }
            )
            return out

        if len(summary_raw) >= w:
            summary = _ellipsize_left(summary_raw, w)
            truncated_summary = 1 if summary != summary_raw else 0
            out.update(
                {
                    "active": 1,
                    "message_raw": message_raw,
                    "summary_raw": summary_raw,
                    "message": "",
                    "summary": summary,
                    "constantshow": constantshow,
                    "truncated_message": 1 if message_raw else 0,
                    "truncated_summary": truncated_summary,
                    "text": summary,
                }
            )
            return out

        if not message_raw:
            padding = " " * max(0, w - len(summary_raw))
            out.update(
                {
                    "active": 1,
                    "message_raw": message_raw,
                    "summary_raw": summary_raw,
                    "message": "",
                    "summary": summary_raw,
                    "padding": padding,
                    "padding_width": len(padding),
                    "constantshow": constantshow,
                    "text": (padding + summary_raw)[:w],
                }
            )
            return out

        sep = "  "
        avail_message = w - len(summary_raw) - len(sep)
        if avail_message <= 0:
            summary = _ellipsize_left(summary_raw, w)
            truncated_summary = 1 if summary != summary_raw else 0
            out.update(
                {
                    "active": 1,
                    "message_raw": message_raw,
                    "summary_raw": summary_raw,
                    "message": "",
                    "summary": summary,
                    "constantshow": constantshow,
                    "truncated_message": 1 if message_raw else 0,
                    "truncated_summary": truncated_summary,
                    "text": summary,
                }
            )
            return out

        message = _ellipsize_right(message_raw, avail_message)
        truncated_message = 1 if message != message_raw else 0
        padding = " " * max(0, w - len(message) - len(summary_raw))
        out.update(
            {
                "active": 1,
                "message_raw": message_raw,
                "summary_raw": summary_raw,
                "message": message,
                "summary": summary_raw,
                "padding": padding,
                "padding_width": len(padding),
                "constantshow": constantshow,
                "truncated_message": truncated_message,
                "truncated_summary": truncated_summary,
                "text": (message + padding + summary_raw)[:w],
            }
        )
        return out

    def infobar_text(self, width: int) -> str:
        """Return the idle infobar line for the current editor state."""

        return str(self.infobar_model(width).get("text", "") or "")

    def line_number_gutter_width(self) -> int:
        """Return the tiny reference gutter width for line numbers.

        The minimal curses TUI currently reserves ``digits(total_lines) + 1``
        cells when `ruler` is on. Exposing that tiny policy here keeps future
        UIs/scripts/LLMs from re-deriving it from renderer code.
        """

        eb = self.cur()
        if not bool(self.options.get("ruler", local=eb.local_options)):
            return 0
        digits = max(1, len(str(max(1, len(eb.buf.lines)))))
        return digits + 1

    def line_number_gutter_text(self, *, line_index: int, wrap_start_col: int, gutter_width: int) -> str:
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

        eb = self.cur()
        cur_line = int(eb.cursors[eb.primary].line) if eb.cursors else 0
        is_relative = bool(self.options.get("relativeruler", local=eb.local_options))
        li = max(0, int(line_index))
        n = (li + 1) if (not is_relative or li == cur_line) else abs(li - cur_line)
        cell_w = max(1, int(gutter_width) - 1)
        return f"{n:>{cell_w}} "

    def scrollbar_gutter_width(self) -> int:
        """Return the tiny reference right-edge scrollbar gutter width."""

        eb = self.cur()
        return 1 if bool(self.options.get("scrollbar", local=eb.local_options)) else 0

    def scrollbar_thumb_span(self, *, total_rows: int, start_row: int, window_rows: int) -> tuple[int, int] | None:
        """Return the tiny scrollbar thumb span as ``(top, size)`` within the window.

        The model intentionally works on abstract rows so callers can use
        logical lines in ordinary views and visual rows under softwrap.
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

    def scrollbar_thumb_char(self) -> str:
        """Return the tiny one-cell scrollbar thumb glyph."""

        try:
            eb = self.cur()
            raw = str(self.options.get("scrollbarchar", local=eb.local_options) or "")
        except Exception:
            raw = ""
        return raw[:1] or "|"

    def gutter_model(self, lines: int, cols: int) -> dict[str, Any]:
        """Return the shared visible gutter model for one screen size.

        This lifts the remaining small reference-TUI gutter truth into one
        inspectable editor-side snapshot: the left line-number cells and the
        right-edge scrollbar thumb rows are exposed with stable screen
        positions, so future UIs, tests, scripts, and LLMs do not need to
        rebuild those visible gutters from scattered layout helpers.
        """

        h = max(0, int(lines))
        w = max(0, int(cols))
        layout = dict(self.screen_layout_model(lines=h, cols=w))
        window = dict(self.edit_window_model(lines=h, cols=w))
        left_w = int(layout.get("gutter_left", 0) or 0)
        right_w = int(layout.get("gutter_right", 0) or 0)
        viewport_h = int(layout.get("viewport_height", 0) or 0)
        scrollbar_x = int(layout.get("scrollbar_x", max(0, w - right_w)) or max(0, w - right_w))
        out: dict[str, Any] = {
            "active": 0,
            "lines": h,
            "cols": w,
            "left_width": left_w,
            "right_width": right_w,
            "line_numbers_active": 0,
            "scrollbar_active": 0,
            "scrollbar_x": int(scrollbar_x),
            "line_numbers": [],
            "scrollbar_rows": [],
        }

        rows = list(window.get("rows") or [])
        number_rows: list[dict[str, Any]] = []
        if left_w > 0:
            cur_line = int(self.primary_cursor().line)
            for row in rows:
                li = int(row.get("line", 0) or 0)
                start_col = int(row.get("start_col", 0) or 0)
                text = self.line_number_gutter_text(
                    line_index=li,
                    wrap_start_col=start_col,
                    gutter_width=left_w,
                )
                number_rows.append(
                    {
                        "screen_y": int(row.get("screen_y", 0) or 0),
                        "screen_x": 0,
                        "width": left_w,
                        "line": li,
                        "start_col": start_col,
                        "current": 1 if start_col == 0 and li == cur_line else 0,
                        "text": text,
                    }
                )

        scrollbar_rows: list[dict[str, Any]] = []
        if right_w > 0 and viewport_h > 0:
            eb = self.cur()
            softwrap_enabled = bool(self.options.get("softwrap", local=eb.local_options))
            if softwrap_enabled:
                total_rows = self._total_visual_rows(eb, w=max(1, int(layout.get("viewport_width", 1) or 1)))
                start_row = self._viewport_visual_start(eb, w=max(1, int(layout.get("viewport_width", 1) or 1)))
            else:
                total_rows = max(1, len(eb.buf.lines))
                vp = dict(window.get("viewport") or {})
                start_row = max(0, int(vp.get("top_line", vp.get("top", 0)) or 0))
            thumb = self.scrollbar_thumb_span(total_rows=total_rows, start_row=start_row, window_rows=viewport_h)
            if thumb is not None:
                thumb_top, thumb_size = thumb
                thumb_char = self.scrollbar_thumb_char()
                for yy in range(int(thumb_top), min(int(viewport_h), int(thumb_top) + int(thumb_size))):
                    scrollbar_rows.append(
                        {
                            "screen_y": int(yy),
                            "screen_x": int(scrollbar_x),
                            "width": right_w,
                            "kind": "thumb",
                            "text": thumb_char,
                        }
                    )

        out.update(
            {
                "active": 1 if number_rows or scrollbar_rows else 0,
                "line_numbers_active": 1 if number_rows else 0,
                "scrollbar_active": 1 if scrollbar_rows else 0,
                "line_numbers": number_rows,
                "scrollbar_rows": scrollbar_rows,
            }
        )
        return out

    def screen_layout_model(self, lines: int, cols: int) -> dict[str, Any]:
        """Return the tiny reference screen-layout model for the curses UI.

        This keeps the reference editor's row/column reservation policy
        inspectable: future UIs, tests, scripts, and LLMs can see how much of a
        screen is consumed by gutters, picker suggestions, and bottom chrome
        without scraping curses output or repeating the layout math by hand.
        Combine it with `bottom_rows_model(width)` when the visible bottom-row
        *text* matters.
        """

        h = max(0, int(lines))
        w = max(0, int(cols))
        out: dict[str, Any] = {
            "lines": h,
            "cols": w,
            "viewport_x": 0,
            "viewport_y": 0,
            "viewport_width": 0,
            "viewport_height": 0,
            "suggestions_y": 0,
            "suggestions_height": 0,
            "suggestions_width": 0,
            "gutter_left": 0,
            "gutter_right": 0,
            "scrollbar_x": 0,
            "bottom_rows": [],
            "bottom_rows_count": 0,
            "chrome_top_y": -1,
            "prompt_y": -1,
            "status_y": -1,
            "keymenu_y": -1,
        }
        if h <= 0 or w <= 0:
            return out

        gutter_left = int(self.line_number_gutter_width())
        gutter_right = int(self.scrollbar_gutter_width())

        bottom_rows_text = self.bottom_rows_model(w)
        bottom_rows: list[dict[str, Any]] = []
        if bottom_rows_text:
            start_y = max(0, h - len(bottom_rows_text))
            for idx, row in enumerate(bottom_rows_text):
                kind = str(row.get("kind", "") or "")
                slot = str(row.get("slot", "") or "")
                y = int(start_y + idx)
                entry = {"kind": kind, "slot": slot, "y": y}
                bottom_rows.append(entry)
                if slot == "prompt" and int(out.get("prompt_y", -1)) < 0:
                    out["prompt_y"] = y
                if kind == "statusline" and int(out.get("status_y", -1)) < 0:
                    out["status_y"] = y
                if kind == "keymenu" and int(out.get("keymenu_y", -1)) < 0:
                    out["keymenu_y"] = y
            out["chrome_top_y"] = int(start_y)

        sug_h = 0
        if self.prompt is not None and self.prompt.kind not in ("command", "find") and self.prompt.suggestion_rows:
            sug_h = min(8, max(1, h // 4))

        viewport_h = max(1, h - len(bottom_rows) - sug_h)
        viewport_w = max(1, w - gutter_left - gutter_right)
        scrollbar_x = int(gutter_left + viewport_w)

        out.update(
            {
                "viewport_x": int(gutter_left),
                "viewport_y": 0,
                "viewport_width": int(viewport_w),
                "viewport_height": int(viewport_h),
                "suggestions_y": int(viewport_h),
                "suggestions_height": int(sug_h),
                "suggestions_width": int(viewport_w),
                "gutter_left": int(gutter_left),
                "gutter_right": int(gutter_right),
                "scrollbar_x": int(scrollbar_x),
                "bottom_rows": bottom_rows,
                "bottom_rows_count": int(len(bottom_rows)),
            }
        )
        return out

    def _viewport_rows_model_from_parts(
        self,
        *,
        lines: int,
        cols: int,
        layout: dict[str, Any],
        window: dict[str, Any],
        gutter: dict[str, Any],
    ) -> dict[str, Any]:
        """Return the shared visible edit-surface rows from existing model parts.

        This keeps the composed viewport rows deterministic and inspectable
        without forcing callers to zip together edit-window rows and gutter
        rows by hand. Styling still belongs to the renderer; the shared editor
        core owns the boring visible text/position contract.
        """

        h = max(0, int(lines))
        w = max(0, int(cols))
        viewport_y = int(layout.get("viewport_y", 0) or 0)
        viewport_x = int(layout.get("viewport_x", 0) or 0)
        viewport_h = int(layout.get("viewport_height", 0) or 0)
        viewport_w = int(layout.get("viewport_width", 0) or 0)
        left_w = int(layout.get("gutter_left", 0) or 0)
        right_w = int(layout.get("gutter_right", 0) or 0)
        right_x = int(layout.get("scrollbar_x", viewport_x + viewport_w) or (viewport_x + viewport_w))

        out: dict[str, Any] = {
            "active": 0,
            "lines": h,
            "cols": w,
            "y": int(viewport_y),
            "x": int(viewport_x),
            "width": int(viewport_w),
            "height": int(viewport_h),
            "left_width": int(left_w),
            "right_width": int(right_w),
            "rows": [],
            "row_count": 0,
        }
        if viewport_h <= 0 or viewport_w <= 0:
            return out

        rows_by_screen_y = {
            int(row.get("screen_y", -1)): dict(row)
            for row in list(window.get("rows") or [])
            if isinstance(row, dict)
        }
        line_numbers_by_y = {
            int(row.get("screen_y", -1)): dict(row)
            for row in list(gutter.get("line_numbers") or [])
            if isinstance(row, dict)
        }
        scrollbar_by_y = {
            int(row.get("screen_y", -1)): dict(row)
            for row in list(gutter.get("scrollbar_rows") or [])
            if isinstance(row, dict)
        }
        cursor = dict(window.get("cursor") or {})
        cursor_visible = bool(int(cursor.get("visible", 0) or 0))
        cursor_y = int(cursor.get("screen_y", -1) or -1)
        cursor_x = int(cursor.get("screen_x", -1) or -1)

        out_rows: list[dict[str, Any]] = []
        for view_y in range(int(viewport_h)):
            screen_y = int(viewport_y + view_y)
            row_model = dict(rows_by_screen_y.get(screen_y, {}))
            left_model = dict(line_numbers_by_y.get(screen_y, {}))
            right_model = dict(scrollbar_by_y.get(screen_y, {}))
            frag = str(row_model.get("text", "") or "")
            if viewport_w > 0:
                frag = frag[: int(viewport_w)]
            left_text = str(left_model.get("text", "") or "") if left_w > 0 else ""
            if left_w > 0 and not left_text:
                left_text = " " * int(left_w)
            right_text = str(right_model.get("text", "") or "") if right_w > 0 else ""
            right_fill = right_text if right_text else ((" " * int(right_w)) if right_w > 0 else "")
            combined = (left_text + frag.ljust(max(0, int(viewport_w))) + right_fill).rstrip()
            cursor_here = 1 if cursor_visible and int(screen_y) == int(cursor_y) else 0
            out_rows.append(
                {
                    "view_y": int(view_y),
                    "screen_y": int(screen_y),
                    "line": int(row_model["line"]) if "line" in row_model else -1,
                    "has_line": 1 if row_model else 0,
                    "start_col": int(row_model.get("start_col", 0) or 0),
                    "text": frag,
                    "text_x": int(viewport_x),
                    "text_width": int(viewport_w),
                    "continuation": int(row_model.get("continuation", 0) or 0),
                    "left_x": 0,
                    "left_text": left_text,
                    "left_width": int(left_w),
                    "current": int(left_model.get("current", 0) or 0),
                    "right_x": int(right_x),
                    "right_text": right_text,
                    "right_width": int(right_w),
                    "combined_text": combined,
                    "cursor_here": int(cursor_here),
                    "cursor_x": int(cursor_x) if cursor_here else -1,
                    "empty": 0 if row_model else 1,
                }
            )

        out.update(
            {
                "active": 1 if out_rows else 0,
                "rows": out_rows,
                "row_count": int(len(out_rows)),
            }
        )
        return out

    def viewport_rows_model(self, lines: int, cols: int) -> dict[str, Any]:
        """Return the shared visible viewport-row model for one screen size.

        This zips together the edit-window rows and visible gutters into one
        inspectable row-ordered snapshot, so future UIs, tests, scripts, and
        LLM handoffs can answer the practical question "what visible edit rows
        exist right now?" without rejoining line numbers, text fragments, and
        scrollbar rows by screen position.
        """

        h = max(0, int(lines))
        w = max(0, int(cols))
        layout = dict(self.screen_layout_model(lines=h, cols=w))
        window = dict(self.edit_window_model(lines=h, cols=w))
        gutter = dict(self.gutter_model(lines=h, cols=w))
        return self._viewport_rows_model_from_parts(
            lines=h,
            cols=w,
            layout=layout,
            window=window,
            gutter=gutter,
        )

    def _search_rows_model_from_window(
        self,
        *,
        lines: int,
        cols: int,
        layout: dict[str, Any],
        window: dict[str, Any],
    ) -> dict[str, Any]:
        """Return visible search-match spans aligned with one live edit window.

        The contract deliberately stays viewport-local and text-first: expose
        the exact visible row fragments, their best-effort search-match spans,
        and which visible match currently owns the primary cursor without
        promoting search highlighting into a larger whole-buffer style system.
        """

        h = max(0, int(lines))
        w = max(0, int(cols))
        viewport_h = int(layout.get("viewport_height", 0) or 0)
        viewport_w = int(layout.get("viewport_width", 0) or 0)
        eb = self.cur()
        enabled = bool(self.options.get("hlsearch", local=eb.local_options))
        query = str(self.search.query or "")
        literal = bool(self.search.literal)
        case_sensitive = bool(self.search.case_sensitive)
        out: dict[str, Any] = {
            "active": 1 if query else 0,
            "enabled": 1 if enabled else 0,
            "lines": h,
            "cols": w,
            "y": int(layout.get("viewport_y", 0) or 0),
            "x": int(layout.get("viewport_x", 0) or 0),
            "width": int(max(0, viewport_w)),
            "height": int(max(0, viewport_h)),
            "query": str(query),
            "literal": 1 if literal else 0,
            "case_sensitive": 1 if case_sensitive else 0,
            "rows": [],
            "row_count": 0,
            "match_rows": 0,
        }
        if viewport_h <= 0 or viewport_w <= 0:
            return out

        cursor = dict(window.get("cursor") or {})
        cursor_visible = bool(int(cursor.get("visible", 0) or 0))
        cursor_view_y = int(cursor["view_y"]) if "view_y" in cursor else -1
        cursor_view_x = int(cursor["view_x"]) if "view_x" in cursor else -1
        rows_by_view_y = {
            int(row.get("view_y", -1)): dict(row)
            for row in list(window.get("rows") or [])
            if isinstance(row, dict)
        }

        out_rows: list[dict[str, Any]] = []
        match_rows = 0
        for view_y in range(int(viewport_h)):
            row = dict(rows_by_view_y.get(int(view_y), {}))
            text = str(row.get("text", "") or "")
            spans = search_match_spans(
                text,
                query,
                literal=literal,
                case_sensitive=case_sensitive,
            ) if enabled and query else []
            current_spans = [
                (int(a), int(b))
                for a, b in spans
                if cursor_visible and int(view_y) == int(cursor_view_y) and int(a) <= int(cursor_view_x) < int(b)
            ]
            if spans:
                match_rows += 1
            out_rows.append(
                {
                    "view_y": int(view_y),
                    "screen_y": int(row["screen_y"]) if "screen_y" in row else int(layout.get("viewport_y", 0) or 0) + int(view_y),
                    "line": int(row["line"]) if "line" in row else -1,
                    "start_col": int(row["start_col"]) if "start_col" in row else 0,
                    "text": text,
                    "spans": [[int(a), int(b)] for a, b in spans],
                    "current_spans": [[int(a), int(b)] for a, b in current_spans],
                    "match_count": int(len(spans)),
                    "current_match_count": int(len(current_spans)),
                }
            )

        out.update(
            {
                "rows": out_rows,
                "row_count": int(len(out_rows)),
                "match_rows": int(match_rows),
            }
        )
        return out

    def search_rows_model(self, lines: int, cols: int) -> dict[str, Any]:
        """Return the shared visible search-cue model for one screen size.

        This reports viewport-local search-match spans for the active whole-
        buffer search, aligned with the same live edit-window rows the minimal
        curses TUI paints. It stays smaller than a general style API: just the
        visible row fragments, their spans, and the cursor-owned current match.
        """

        h = max(0, int(lines))
        w = max(0, int(cols))
        layout = dict(self.screen_layout_model(lines=h, cols=w))
        window = dict(self.edit_window_model(lines=h, cols=w))
        layout = dict(window)
        layout.setdefault("lines", h)
        layout.setdefault("cols", w)
        return self._search_rows_model_from_window(
            lines=h,
            cols=w,
            layout=layout,
            window=window,
        )

    def _showchars_rows_model_from_window(
        self,
        *,
        lines: int,
        cols: int,
        layout: dict[str, Any],
        window: dict[str, Any],
    ) -> dict[str, Any]:
        """Return visible ``showchars`` replacements aligned with one edit window.

        The contract stays viewport-local and text-first: expose the exact raw
        row fragments, their visible replacement text, and the replacement spans
        produced by the current tiny ``showchars`` policy without promoting that
        cue into a larger whole-buffer style system.
        """

        h = max(0, int(lines))
        w = max(0, int(cols))
        viewport_h = int(layout.get("viewport_height", 0) or 0)
        viewport_w = int(layout.get("viewport_width", 0) or 0)
        eb = self.cur()
        raw_spec = str(self.options.get("showchars", local=eb.local_options) or "")
        spec = parse_showchars_option(raw_spec)
        out: dict[str, Any] = {
            "active": 1 if spec else 0,
            "enabled": 1 if spec else 0,
            "lines": h,
            "cols": w,
            "y": int(layout.get("viewport_y", 0) or 0),
            "x": int(layout.get("viewport_x", 0) or 0),
            "width": int(max(0, viewport_w)),
            "height": int(max(0, viewport_h)),
            "spec": str(raw_spec),
            "rows": [],
            "row_count": 0,
            "changed_rows": 0,
        }
        if viewport_h <= 0 or viewport_w <= 0:
            return out

        rows_by_view_y = {
            int(row.get("view_y", -1)): dict(row)
            for row in list(window.get("rows") or [])
            if isinstance(row, dict)
        }

        out_rows: list[dict[str, Any]] = []
        changed_rows = 0
        for view_y in range(int(viewport_h)):
            row = dict(rows_by_view_y.get(int(view_y), {}))
            text = str(row.get("text", "") or "")
            line_index = int(row["line"]) if "line" in row else -1
            start_col = int(row["start_col"]) if "start_col" in row else 0
            line_text = str(eb.buf.lines[line_index]) if 0 <= int(line_index) < len(eb.buf.lines) else text
            display_text, spans = render_showchars_fragment(
                line_text,
                frag_start=int(start_col),
                frag_text=text,
                spec=spec,
            )
            if spans:
                changed_rows += 1
            out_rows.append(
                {
                    "view_y": int(view_y),
                    "screen_y": int(row["screen_y"]) if "screen_y" in row else int(layout.get("viewport_y", 0) or 0) + int(view_y),
                    "line": int(line_index),
                    "start_col": int(start_col),
                    "text": text,
                    "display_text": str(display_text),
                    "spans": [[int(a), int(b)] for a, b in spans],
                    "replacement_count": int(len(spans)),
                }
            )

        out.update(
            {
                "rows": out_rows,
                "row_count": int(len(out_rows)),
                "changed_rows": int(changed_rows),
            }
        )
        return out

    def showchars_rows_model(self, lines: int, cols: int) -> dict[str, Any]:
        """Return the shared visible ``showchars`` row model for one screen size.

        Future UIs, tests, scripts, and LLM handoffs can inspect the exact
        visible replacements and their spans without re-parsing the option or
        recomputing fragment-local indentation rules in renderer code.
        """

        h = max(0, int(lines))
        w = max(0, int(cols))
        layout = dict(self.screen_layout_model(lines=h, cols=w))
        window = dict(self.edit_window_model(lines=h, cols=w))
        layout = dict(window)
        layout.setdefault("lines", h)
        layout.setdefault("cols", w)
        return self._showchars_rows_model_from_window(
            lines=h,
            cols=w,
            layout=layout,
            window=window,
        )

    def _viewport_cues_model_from_parts(
        self,
        *,
        lines: int,
        cols: int,
        layout: dict[str, Any],
        window: dict[str, Any],
        search_rows: dict[str, Any],
        showchars_rows: dict[str, Any],
    ) -> dict[str, Any]:
        """Return shared visible cue spans aligned with one live edit window.

        This keeps the contract deliberately viewport-local and span-first:
        expose the tiny non-text cues that the reference TUI overlays on edit
        rows (current row, search/current match, showchars replacements,
        trailing whitespace, tab errors, colorcolumn, and brace pairs) without
        promoting them into a broader theme or attribute system.
        """

        h = max(0, int(lines))
        w = max(0, int(cols))
        viewport_h = int(layout.get("viewport_height", 0) or 0)
        viewport_w = int(layout.get("viewport_width", 0) or 0)
        eb = self.cur()
        raw_showchars = str(self.options.get("showchars", local=eb.local_options) or "")
        showchars_enabled = bool(parse_showchars_option(raw_showchars))
        cursorline_enabled = bool(self.options.get("cursorline", local=eb.local_options))
        hlsearch_enabled = bool(self.options.get("hlsearch", local=eb.local_options))
        hltrailingws_enabled = bool(self.options.get("hltrailingws", local=eb.local_options))
        hltaberrors_enabled = bool(self.options.get("hltaberrors", local=eb.local_options))
        colorcolumn = int(self.options.get("colorcolumn", local=eb.local_options) or 0)
        tabstospaces = bool(self.options.get("tabstospaces", local=eb.local_options))
        softwrap_enabled = bool(self.options.get("softwrap", local=eb.local_options))
        matchbrace_enabled = bool(self.options.get("matchbrace", local=eb.local_options))
        matchbraceleft_enabled = bool(self.options.get("matchbraceleft", local=eb.local_options))

        out: dict[str, Any] = {
            "active": 1 if viewport_h > 0 and viewport_w > 0 else 0,
            "enabled": 1 if any(
                [
                    cursorline_enabled,
                    hlsearch_enabled,
                    showchars_enabled,
                    hltrailingws_enabled,
                    hltaberrors_enabled,
                    int(colorcolumn) > 0,
                    matchbrace_enabled,
                ]
            ) else 0,
            "lines": h,
            "cols": w,
            "y": int(layout.get("viewport_y", 0) or 0),
            "x": int(layout.get("viewport_x", 0) or 0),
            "width": int(max(0, viewport_w)),
            "height": int(max(0, viewport_h)),
            "cursorline_enabled": 1 if cursorline_enabled else 0,
            "hlsearch_enabled": 1 if hlsearch_enabled else 0,
            "showchars_enabled": 1 if showchars_enabled else 0,
            "hltrailingws_enabled": 1 if hltrailingws_enabled else 0,
            "hltaberrors_enabled": 1 if hltaberrors_enabled else 0,
            "tabstospaces": 1 if tabstospaces else 0,
            "colorcolumn": int(colorcolumn),
            "matchbrace_enabled": 1 if matchbrace_enabled else 0,
            "matchbraceleft_enabled": 1 if matchbraceleft_enabled else 0,
            "rows": [],
            "row_count": 0,
            "cue_rows": 0,
        }
        if viewport_h <= 0 or viewport_w <= 0:
            return out

        cursor = dict(window.get("cursor") or {})
        cursor_visible = bool(int(cursor.get("visible", 0) or 0))
        cursor_view_y = int(cursor["view_y"]) if "view_y" in cursor else -1
        rows_by_view_y = {
            int(row.get("view_y", -1)): dict(row)
            for row in list(window.get("rows") or [])
            if isinstance(row, dict)
        }
        search_by_y = {
            int(row.get("screen_y", -1)): dict(row)
            for row in list(search_rows.get("rows") or [])
            if isinstance(row, dict)
        }
        showchars_by_y = {
            int(row.get("screen_y", -1)): dict(row)
            for row in list(showchars_rows.get("rows") or [])
            if isinstance(row, dict)
        }
        brace_positions = matching_brace_positions(
            list(eb.buf.lines),
            line=int(eb.cursors[eb.primary].line),
            col=int(eb.cursors[eb.primary].col),
            match_left=matchbraceleft_enabled,
        ) if matchbrace_enabled else []

        out_rows: list[dict[str, Any]] = []
        cue_rows = 0
        for view_y in range(int(viewport_h)):
            row = dict(rows_by_view_y.get(int(view_y), {}))
            screen_y = int(row["screen_y"]) if "screen_y" in row else int(layout.get("viewport_y", 0) or 0) + int(view_y)
            text = str(row.get("text", "") or "")
            line_index = int(row["line"]) if "line" in row else -1
            start_col = int(row.get("start_col", 0) or 0)
            line_text = str(eb.buf.lines[line_index]) if 0 <= int(line_index) < len(eb.buf.lines) else text

            search_row = dict(search_by_y.get(int(screen_y), {}))
            search_spans = [
                [int(a), int(b)] for a, b in [tuple(int(x) for x in span[:2]) for span in list(search_row.get("spans") or [])]
            ]
            current_search_spans = [
                [int(a), int(b)] for a, b in [tuple(int(x) for x in span[:2]) for span in list(search_row.get("current_spans") or [])]
            ]
            showchars_row = dict(showchars_by_y.get(int(screen_y), {}))
            showchar_spans = [
                [int(a), int(b)] for a, b in [tuple(int(x) for x in span[:2]) for span in list(showchars_row.get("spans") or [])]
            ]
            trailing_spans_ = trailing_whitespace_spans(
                line_text,
                frag_start=int(start_col),
                frag_text=text,
            ) if hltrailingws_enabled else []
            tab_error_spans_ = tab_error_spans(
                line_text,
                tabstospaces=tabstospaces,
                frag_start=int(start_col),
                frag_text=text,
            ) if hltaberrors_enabled else []
            color_x = colorcolumn_screen_x(
                colorcolumn=int(colorcolumn),
                frag_start=int(start_col),
                view_width=int(viewport_w),
                softwrap=softwrap_enabled,
            )
            colorcolumn_spans = [] if color_x is None or int(color_x) >= len(text) else [(int(color_x), int(color_x) + 1)]
            brace_spans_ = brace_match_spans(
                line_index=int(line_index),
                frag_start=int(start_col),
                frag_text=text,
                brace_positions=brace_positions,
            ) if matchbrace_enabled else []
            cursorline = 1 if cursor_visible and cursorline_enabled and int(view_y) == int(cursor_view_y) else 0
            row_has_any = bool(cursorline or search_spans or current_search_spans or showchar_spans or trailing_spans_ or tab_error_spans_ or colorcolumn_spans or brace_spans_)
            if row_has_any:
                cue_rows += 1
            out_rows.append(
                {
                    "view_y": int(view_y),
                    "screen_y": int(screen_y),
                    "line": int(line_index),
                    "start_col": int(start_col),
                    "text": text,
                    "cursorline": int(cursorline),
                    "search_spans": search_spans,
                    "current_search_spans": current_search_spans,
                    "showchar_spans": showchar_spans,
                    "trailing_spans": [[int(a), int(b)] for a, b in trailing_spans_],
                    "tab_error_spans": [[int(a), int(b)] for a, b in tab_error_spans_],
                    "colorcolumn_x": int(color_x) if color_x is not None else -1,
                    "colorcolumn_blank": 1 if color_x is not None and int(color_x) >= len(text) else 0,
                    "colorcolumn_spans": [[int(a), int(b)] for a, b in colorcolumn_spans],
                    "brace_spans": [[int(a), int(b)] for a, b in brace_spans_],
                    "cue_count": int(
                        int(cursorline)
                        + len(search_spans)
                        + len(current_search_spans)
                        + len(showchar_spans)
                        + len(trailing_spans_)
                        + len(tab_error_spans_)
                        + len(colorcolumn_spans)
                        + len(brace_spans_)
                    ),
                }
            )

        out.update(
            {
                "rows": out_rows,
                "row_count": int(len(out_rows)),
                "cue_rows": int(cue_rows),
            }
        )
        return out

    def viewport_cues_model(self, lines: int, cols: int) -> dict[str, Any]:
        """Return the shared visible cue-span model for one screen snapshot.

        Future UIs, tests, scripts, and LLM handoffs can inspect the tiny
        visible non-text edit-window cues the reference TUI paints — current
        row, search/current match, showchars replacements, trailing whitespace,
        tab errors, colorcolumn, and brace pairs — without scraping curses
        attributes or recomputing those spans from raw buffer state.
        """

        h = max(0, int(lines))
        w = max(0, int(cols))
        layout = dict(self.screen_layout_model(lines=h, cols=w))
        window = dict(self.edit_window_model(lines=h, cols=w))
        layout = dict(window)
        layout.setdefault("lines", h)
        layout.setdefault("cols", w)
        search_rows = dict(
            self._search_rows_model_from_window(
                lines=h,
                cols=w,
                layout=layout,
                window=window,
            )
        )
        showchars_rows = dict(
            self._showchars_rows_model_from_window(
                lines=h,
                cols=w,
                layout=layout,
                window=window,
            )
        )
        return self._viewport_cues_model_from_parts(
            lines=h,
            cols=w,
            layout=layout,
            window=window,
            search_rows=search_rows,
            showchars_rows=showchars_rows,
        )

    def _docs_cues_model_from_parts(
        self,
        *,
        lines: int,
        cols: int,
        layout: dict[str, Any],
        window: dict[str, Any],
    ) -> dict[str, Any]:
        """Return shared visible docs/help scanability spans for one edit window.

        This keeps the contract deliberately viewport-local and span-first: it
        exposes the tiny markdown-ish emphasis/link/list/blockquote/table cues
        the reference TUI paints for docs/help buffers without promoting them
        into a broader theme system or a full markdown AST.
        """

        from .tui import (
            md_autolink_token_spans,
            md_blockquote_alert_marker,
            md_blockquote_body_span,
            md_blockquote_prefix,
            md_emphasis_spans,
            md_escaped_markdown_token_spans,
            md_footnote_ref_token_spans,
            md_image_token_spans,
            md_inline_markup_delimiter_spans,
            md_inline_markup_matches,
            md_link_label_spans,
            md_link_source_token_spans,
            md_list_marker,
            md_raw_html_tag_token_spans,
            md_strikethrough_spans,
            md_strong_spans,
            md_table_cell_entries,
            md_table_delimiter_entries,
            md_table_pipe_spans,
            md_table_row_kinds,
            md_task_body_span,
            md_task_checkbox,
            md_thematic_break_char_spans,
            md_thematic_break_span,
        )

        h = max(0, int(lines))
        w = max(0, int(cols))
        viewport_h = int(layout.get("viewport_height", 0) or 0)
        viewport_w = int(layout.get("viewport_width", 0) or 0)
        help_topic = self.current_help_doc_topic()
        enabled = bool(help_topic)
        out: dict[str, Any] = {
            "active": 1 if enabled and viewport_h > 0 and viewport_w > 0 else 0,
            "enabled": 1 if enabled else 0,
            "help_doc": str(help_topic or ""),
            "lines": h,
            "cols": w,
            "y": int(layout.get("viewport_y", 0) or 0),
            "x": int(layout.get("viewport_x", 0) or 0),
            "width": int(max(0, viewport_w)),
            "height": int(max(0, viewport_h)),
            "rows": [],
            "row_count": 0,
            "cue_rows": 0,
            "link_rows": 0,
            "link_entry_count": 0,
            "local_doc_link_rows": 0,
            "fragment_link_rows": 0,
            "external_link_rows": 0,
            "footnote_link_rows": 0,
            "inline_link_rows": 0,
            "reference_link_rows": 0,
            "full_reference_link_rows": 0,
            "collapsed_reference_link_rows": 0,
            "shortcut_reference_link_rows": 0,
            "autolink_rows": 0,
            "footnote_ref_rows": 0,
            "local_doc_link_count": 0,
            "fragment_link_count": 0,
            "external_link_count": 0,
            "footnote_link_count": 0,
            "inline_link_count": 0,
            "reference_link_count": 0,
            "full_reference_link_count": 0,
            "collapsed_reference_link_count": 0,
            "shortcut_reference_link_count": 0,
            "autolink_count": 0,
            "footnote_ref_count": 0,
            "image_rows": 0,
            "image_entry_count": 0,
            "inline_image_rows": 0,
            "reference_image_rows": 0,
            "full_reference_image_rows": 0,
            "collapsed_reference_image_rows": 0,
            "shortcut_reference_image_rows": 0,
            "local_doc_image_rows": 0,
            "fragment_image_rows": 0,
            "external_image_rows": 0,
            "footnote_image_rows": 0,
            "inline_image_count": 0,
            "reference_image_count": 0,
            "full_reference_image_count": 0,
            "collapsed_reference_image_count": 0,
            "shortcut_reference_image_count": 0,
            "local_doc_image_count": 0,
            "fragment_image_count": 0,
            "external_image_count": 0,
            "footnote_image_count": 0,
            "code_rows": 0,
            "code_entry_count": 0,
            "single_backtick_code_rows": 0,
            "multi_backtick_code_rows": 0,
            "single_backtick_code_count": 0,
            "multi_backtick_code_count": 0,
            "markup_rows": 0,
            "markup_entry_count": 0,
            "strong_markup_rows": 0,
            "emphasis_markup_rows": 0,
            "strike_markup_rows": 0,
            "asterisk_markup_rows": 0,
            "underscore_markup_rows": 0,
            "tilde_markup_rows": 0,
            "strong_entry_count": 0,
            "emphasis_entry_count": 0,
            "strike_entry_count": 0,
            "asterisk_markup_count": 0,
            "underscore_markup_count": 0,
            "tilde_markup_count": 0,
            "table_rows": 0,
            "table_entry_count": 0,
            "table_header_rows": 0,
            "table_body_rows": 0,
            "table_delimiter_rows": 0,
            "default_aligned_table_rows": 0,
            "left_aligned_table_rows": 0,
            "center_aligned_table_rows": 0,
            "right_aligned_table_rows": 0,
            "table_header_cell_count": 0,
            "table_body_cell_count": 0,
            "table_delimiter_cell_count": 0,
            "default_aligned_table_entry_count": 0,
            "left_aligned_table_entry_count": 0,
            "center_aligned_table_entry_count": 0,
            "right_aligned_table_entry_count": 0,
            "structure_rows": 0,
            "structure_entry_count": 0,
            "list_rows": 0,
            "list_entry_count": 0,
            "bullet_list_rows": 0,
            "ordered_list_rows": 0,
            "bullet_list_entry_count": 0,
            "ordered_list_entry_count": 0,
            "task_rows": 0,
            "task_entry_count": 0,
            "checked_task_rows": 0,
            "unchecked_task_rows": 0,
            "checked_task_entry_count": 0,
            "unchecked_task_entry_count": 0,
            "bullet_task_rows": 0,
            "ordered_task_rows": 0,
            "bullet_task_entry_count": 0,
            "ordered_task_entry_count": 0,
            "blockquote_rows": 0,
            "blockquote_entry_count": 0,
            "blockquote_alert_rows": 0,
            "blockquote_alert_entry_count": 0,
            "note_blockquote_alert_rows": 0,
            "tip_blockquote_alert_rows": 0,
            "important_blockquote_alert_rows": 0,
            "warning_blockquote_alert_rows": 0,
            "caution_blockquote_alert_rows": 0,
            "note_blockquote_alert_entry_count": 0,
            "tip_blockquote_alert_entry_count": 0,
            "important_blockquote_alert_entry_count": 0,
            "warning_blockquote_alert_entry_count": 0,
            "caution_blockquote_alert_entry_count": 0,
            "thematic_break_rows": 0,
            "thematic_break_entry_count": 0,
            "heading_rows": 0,
            "heading_entry_count": 0,
            "heading_title_rows": 0,
            "heading_underline_rows": 0,
            "atx_heading_rows": 0,
            "setext_heading_rows": 0,
            "heading_title_entry_count": 0,
            "heading_underline_entry_count": 0,
            "atx_heading_entry_count": 0,
            "setext_heading_entry_count": 0,
            "section_rows": 0,
            "section_distinct_count": 0,
            "definition_rows": 0,
            "definition_entry_count": 0,
            "reference_definition_rows": 0,
            "reference_definition_cont_rows": 0,
            "footnote_definition_rows": 0,
            "footnote_definition_cont_rows": 0,
            "reference_definition_entry_count": 0,
            "reference_definition_cont_entry_count": 0,
            "footnote_definition_entry_count": 0,
            "footnote_definition_cont_entry_count": 0,
            "block_rows": 0,
            "block_entry_count": 0,
            "backtick_fenced_code_rows": 0,
            "tilde_fenced_code_rows": 0,
            "language_fenced_code_rows": 0,
            "bare_fenced_code_rows": 0,
            "backtick_fenced_code_count": 0,
            "tilde_fenced_code_count": 0,
            "language_fenced_code_count": 0,
            "bare_fenced_code_count": 0,
            "fenced_code_entry_count": 0,
            "fenced_code_opener_entry_count": 0,
            "fenced_code_body_entry_count": 0,
            "fenced_code_closer_entry_count": 0,
            "html_block_entry_count": 0,
            "indented_code_entry_count": 0,
        }
        if viewport_h <= 0 or viewport_w <= 0:
            return out

        rows_by_view_y = {
            int(row.get("view_y", -1)): dict(row)
            for row in list(window.get("rows") or [])
            if isinstance(row, dict)
        }
        line_comment_spans: list[list[tuple[int, int]]] = []
        defs: dict[str, str] = {}
        footdefs: dict[str, tuple[int, int]] = {}
        fence_flags: list[bool] = []
        html_block_flags: list[bool] = []
        indented_code_flags: list[bool] = []
        heading_roles: dict[int, tuple[str, int]] = {}
        fenced_roles: dict[int, str] = {}
        definition_roles: dict[int, tuple[str, int, int]] = {}
        table_kinds: dict[int, str] = {}
        table_alignments_by_line: dict[int, dict[int, str]] = {}
        heading_entries_by_line: dict[int, list[dict[str, Any]]] = {}
        section_entry_by_line: dict[int, dict[str, Any]] = {}
        definition_entries_by_line: dict[int, list[dict[str, Any]]] = {}
        block_entries_by_line: dict[int, list[dict[str, Any]]] = {}
        eb = self.cur()
        if enabled:
            buf_lines = list(eb.buf.lines)
            defs = self._md_reference_defs(buf_lines)
            footdefs = self._md_footnote_defs(buf_lines)
            fence_flags = md_fenced_code_line_flags(buf_lines)
            html_block_flags = md_html_block_line_flags(buf_lines)
            line_comment_spans = md_html_comment_line_spans(buf_lines)
            indented_code_flags = md_indented_code_line_flags(
                buf_lines,
                fence_flags=fence_flags,
                html_block_flags=html_block_flags,
            )
            heading_roles = self._md_heading_line_roles(buf_lines)
            section_entry_by_line = self._md_section_entry_by_line(buf_lines)
            fenced_roles = self._md_fenced_code_line_roles(buf_lines)
            definition_roles = self._md_definition_line_roles(buf_lines)
            definition_entries_by_line = self._md_definition_entries_by_line(buf_lines)
            block_entries_by_line = self._md_block_entries_by_line(buf_lines)
            table_kinds = md_table_row_kinds([str(ln) for ln in buf_lines])
            for line_idx, kind in sorted(table_kinds.items()):
                if str(kind) != "delimiter":
                    continue
                alignments = {
                    int(entry.get("column", 0) or 0): str(entry.get("align", "default") or "default")
                    for entry in md_table_delimiter_entries(str(buf_lines[int(line_idx)]))
                }
                if not alignments:
                    continue
                table_alignments_by_line[int(line_idx)] = dict(alignments)
                header_idx = int(line_idx) - 1
                if table_kinds.get(header_idx) == "header":
                    table_alignments_by_line[header_idx] = dict(alignments)
                body_idx = int(line_idx) + 1
                while table_kinds.get(body_idx) == "body":
                    table_alignments_by_line[body_idx] = dict(alignments)
                    body_idx += 1
            seen_heading_ids: dict[str, int] = {}
            for line0, line1, level, title, explicit_fragment, _col0 in self._md_heading_scan(buf_lines):
                resolved_fragment = str(explicit_fragment or md_heading_auto_id(title, seen=seen_heading_ids))
                source_kind = 'atx' if int(line1) <= int(line0) + 1 else 'setext'
                for idx in range(int(line0), int(line1)):
                    role = 'underline' if source_kind == 'setext' and idx == int(line1) - 1 else 'title'
                    entry: dict[str, Any] = {
                        'kind': 'heading',
                        'role': str(role),
                        'source_kind': str(source_kind),
                        'level': int(level),
                        'title': str(title),
                        'fragment': str(resolved_fragment),
                        'explicit_fragment': str(explicit_fragment),
                        'fragment_source': 'explicit' if str(explicit_fragment) else 'auto',
                    }
                    if role == 'underline':
                        stripped = str(buf_lines[idx]).strip()
                        marker = '=' if stripped.startswith('=') else '-'
                        entry['marker'] = str(marker)
                        entry['marker_count'] = int(sum(1 for ch in stripped if ch == marker))
                    heading_entries_by_line.setdefault(int(idx), []).append(entry)

        rows: list[dict[str, Any]] = []
        cue_rows = 0
        link_rows = 0
        link_entry_count = 0
        local_doc_link_rows = 0
        fragment_link_rows = 0
        external_link_rows = 0
        footnote_link_rows = 0
        inline_link_rows = 0
        reference_link_rows = 0
        full_reference_link_rows = 0
        collapsed_reference_link_rows = 0
        shortcut_reference_link_rows = 0
        autolink_rows = 0
        footnote_ref_rows = 0
        local_doc_link_count = 0
        fragment_link_count = 0
        external_link_count = 0
        footnote_link_count = 0
        inline_link_count = 0
        reference_link_count = 0
        full_reference_link_count = 0
        collapsed_reference_link_count = 0
        shortcut_reference_link_count = 0
        autolink_count = 0
        footnote_ref_count = 0
        image_rows = 0
        image_entry_count = 0
        inline_image_rows = 0
        reference_image_rows = 0
        full_reference_image_rows = 0
        collapsed_reference_image_rows = 0
        shortcut_reference_image_rows = 0
        local_doc_image_rows = 0
        fragment_image_rows = 0
        external_image_rows = 0
        footnote_image_rows = 0
        inline_image_count = 0
        reference_image_count = 0
        full_reference_image_count = 0
        collapsed_reference_image_count = 0
        shortcut_reference_image_count = 0
        local_doc_image_count = 0
        fragment_image_count = 0
        external_image_count = 0
        footnote_image_count = 0
        code_rows = 0
        code_entry_count = 0
        single_backtick_code_rows = 0
        multi_backtick_code_rows = 0
        single_backtick_code_count = 0
        multi_backtick_code_count = 0
        markup_rows = 0
        markup_entry_count = 0
        strong_markup_rows = 0
        emphasis_markup_rows = 0
        strike_markup_rows = 0
        asterisk_markup_rows = 0
        underscore_markup_rows = 0
        tilde_markup_rows = 0
        strong_entry_count = 0
        emphasis_entry_count = 0
        strike_entry_count = 0
        asterisk_markup_count = 0
        underscore_markup_count = 0
        tilde_markup_count = 0
        table_rows = 0
        table_entry_count = 0
        table_header_rows = 0
        table_body_rows = 0
        table_delimiter_rows = 0
        default_aligned_table_rows = 0
        left_aligned_table_rows = 0
        center_aligned_table_rows = 0
        right_aligned_table_rows = 0
        table_header_cell_count = 0
        table_body_cell_count = 0
        table_delimiter_cell_count = 0
        default_aligned_table_entry_count = 0
        left_aligned_table_entry_count = 0
        center_aligned_table_entry_count = 0
        right_aligned_table_entry_count = 0
        structure_rows = 0
        structure_entry_count = 0
        list_rows = 0
        list_entry_count = 0
        bullet_list_rows = 0
        ordered_list_rows = 0
        bullet_list_entry_count = 0
        ordered_list_entry_count = 0
        task_rows = 0
        task_entry_count = 0
        checked_task_rows = 0
        unchecked_task_rows = 0
        checked_task_entry_count = 0
        unchecked_task_entry_count = 0
        bullet_task_rows = 0
        ordered_task_rows = 0
        bullet_task_entry_count = 0
        ordered_task_entry_count = 0
        blockquote_rows = 0
        blockquote_entry_count = 0
        blockquote_alert_rows = 0
        blockquote_alert_entry_count = 0
        note_blockquote_alert_rows = 0
        tip_blockquote_alert_rows = 0
        important_blockquote_alert_rows = 0
        warning_blockquote_alert_rows = 0
        caution_blockquote_alert_rows = 0
        note_blockquote_alert_entry_count = 0
        tip_blockquote_alert_entry_count = 0
        important_blockquote_alert_entry_count = 0
        warning_blockquote_alert_entry_count = 0
        caution_blockquote_alert_entry_count = 0
        thematic_break_rows = 0
        thematic_break_entry_count = 0
        heading_rows = 0
        heading_entry_count = 0
        heading_title_rows = 0
        heading_underline_rows = 0
        atx_heading_rows = 0
        setext_heading_rows = 0
        h1_heading_rows = 0
        h2_heading_rows = 0
        h3_heading_rows = 0
        h4_heading_rows = 0
        h5_heading_rows = 0
        h6_heading_rows = 0
        explicit_fragment_heading_rows = 0
        auto_fragment_heading_rows = 0
        heading_title_entry_count = 0
        heading_underline_entry_count = 0
        atx_heading_entry_count = 0
        setext_heading_entry_count = 0
        h1_heading_entry_count = 0
        h2_heading_entry_count = 0
        h3_heading_entry_count = 0
        h4_heading_entry_count = 0
        h5_heading_entry_count = 0
        h6_heading_entry_count = 0
        explicit_fragment_heading_entry_count = 0
        auto_fragment_heading_entry_count = 0
        section_rows = 0
        visible_section_paths: set[str] = set()
        definition_rows = 0
        definition_entry_count = 0
        reference_definition_rows = 0
        reference_definition_cont_rows = 0
        footnote_definition_rows = 0
        footnote_definition_cont_rows = 0
        reference_definition_entry_count = 0
        reference_definition_cont_entry_count = 0
        footnote_definition_entry_count = 0
        footnote_definition_cont_entry_count = 0
        block_rows = 0
        block_entry_count = 0
        backtick_fenced_code_rows = 0
        tilde_fenced_code_rows = 0
        language_fenced_code_rows = 0
        bare_fenced_code_rows = 0
        backtick_fenced_code_count = 0
        tilde_fenced_code_count = 0
        language_fenced_code_count = 0
        bare_fenced_code_count = 0
        fenced_code_rows = 0
        fenced_code_opener_rows = 0
        fenced_code_body_rows = 0
        fenced_code_closer_rows = 0
        html_block_rows = 0
        indented_code_rows = 0
        fenced_code_entry_count = 0
        fenced_code_opener_entry_count = 0
        fenced_code_body_entry_count = 0
        fenced_code_closer_entry_count = 0
        html_block_entry_count = 0
        indented_code_entry_count = 0
        literal_rows = 0
        literal_entry_count = 0
        raw_html_rows = 0
        escaped_markdown_rows = 0
        raw_html_entry_count = 0
        escaped_markdown_entry_count = 0
        for view_y in range(int(viewport_h)):
            row = dict(rows_by_view_y.get(int(view_y), {}))
            text = str(row.get("text", "") or "")
            line_index = int(row["line"]) if "line" in row else -1
            start_col = int(row.get("start_col", 0) or 0)
            link_spans: list[tuple[int, int]] = []
            link_entries: list[dict[str, Any]] = []
            local_doc_link_entries: list[dict[str, Any]] = []
            fragment_link_entries: list[dict[str, Any]] = []
            external_link_entries: list[dict[str, Any]] = []
            footnote_link_entries: list[dict[str, Any]] = []
            inline_link_entries: list[dict[str, Any]] = []
            reference_link_entries: list[dict[str, Any]] = []
            full_reference_link_entries: list[dict[str, Any]] = []
            collapsed_reference_link_entries: list[dict[str, Any]] = []
            shortcut_reference_link_entries: list[dict[str, Any]] = []
            autolink_entries: list[dict[str, Any]] = []
            footnote_ref_entries: list[dict[str, Any]] = []
            image_entries: list[dict[str, Any]] = []
            inline_image_entries: list[dict[str, Any]] = []
            reference_image_entries: list[dict[str, Any]] = []
            full_reference_image_entries: list[dict[str, Any]] = []
            collapsed_reference_image_entries: list[dict[str, Any]] = []
            shortcut_reference_image_entries: list[dict[str, Any]] = []
            local_doc_image_entries: list[dict[str, Any]] = []
            fragment_image_entries: list[dict[str, Any]] = []
            external_image_entries: list[dict[str, Any]] = []
            footnote_image_entries: list[dict[str, Any]] = []
            code_entries: list[dict[str, Any]] = []
            single_backtick_code_entries: list[dict[str, Any]] = []
            multi_backtick_code_entries: list[dict[str, Any]] = []
            markup_entries: list[dict[str, Any]] = []
            strong_markup_entries: list[dict[str, Any]] = []
            emphasis_markup_entries: list[dict[str, Any]] = []
            strike_markup_entries: list[dict[str, Any]] = []
            asterisk_markup_entries: list[dict[str, Any]] = []
            underscore_markup_entries: list[dict[str, Any]] = []
            tilde_markup_entries: list[dict[str, Any]] = []
            literal_entries: list[dict[str, Any]] = []
            raw_html_literal_entries: list[dict[str, Any]] = []
            escaped_markdown_entries: list[dict[str, Any]] = []
            table_entries: list[dict[str, Any]] = []
            table_header_entries: list[dict[str, Any]] = []
            table_body_entries: list[dict[str, Any]] = []
            table_delimiter_entries: list[dict[str, Any]] = []
            default_aligned_table_entries: list[dict[str, Any]] = []
            left_aligned_table_entries: list[dict[str, Any]] = []
            center_aligned_table_entries: list[dict[str, Any]] = []
            right_aligned_table_entries: list[dict[str, Any]] = []
            structure_entries: list[dict[str, Any]] = []
            list_entries: list[dict[str, Any]] = []
            task_entries: list[dict[str, Any]] = []
            checked_task_entries: list[dict[str, Any]] = []
            unchecked_task_entries: list[dict[str, Any]] = []
            bullet_task_entries: list[dict[str, Any]] = []
            ordered_task_entries: list[dict[str, Any]] = []
            blockquote_entries: list[dict[str, Any]] = []
            blockquote_alert_entries: list[dict[str, Any]] = []
            note_blockquote_alert_entries: list[dict[str, Any]] = []
            tip_blockquote_alert_entries: list[dict[str, Any]] = []
            important_blockquote_alert_entries: list[dict[str, Any]] = []
            warning_blockquote_alert_entries: list[dict[str, Any]] = []
            caution_blockquote_alert_entries: list[dict[str, Any]] = []
            thematic_break_entries: list[dict[str, Any]] = []
            heading_entries: list[dict[str, Any]] = []
            heading_title_entries: list[dict[str, Any]] = []
            heading_underline_entries: list[dict[str, Any]] = []
            atx_heading_entries: list[dict[str, Any]] = []
            setext_heading_entries: list[dict[str, Any]] = []
            h1_heading_entries: list[dict[str, Any]] = []
            h2_heading_entries: list[dict[str, Any]] = []
            h3_heading_entries: list[dict[str, Any]] = []
            h4_heading_entries: list[dict[str, Any]] = []
            h5_heading_entries: list[dict[str, Any]] = []
            h6_heading_entries: list[dict[str, Any]] = []
            explicit_fragment_heading_entries: list[dict[str, Any]] = []
            auto_fragment_heading_entries: list[dict[str, Any]] = []
            section_entry: dict[str, Any] = {}
            definition_entries: list[dict[str, Any]] = []
            reference_definition_entries: list[dict[str, Any]] = []
            reference_definition_cont_entries: list[dict[str, Any]] = []
            footnote_definition_entries: list[dict[str, Any]] = []
            footnote_definition_cont_entries: list[dict[str, Any]] = []
            block_entries: list[dict[str, Any]] = []
            fenced_code_entries: list[dict[str, Any]] = []
            backtick_fenced_code_entries: list[dict[str, Any]] = []
            tilde_fenced_code_entries: list[dict[str, Any]] = []
            language_fenced_code_entries: list[dict[str, Any]] = []
            bare_fenced_code_entries: list[dict[str, Any]] = []
            fenced_code_opener_entries: list[dict[str, Any]] = []
            fenced_code_body_entries: list[dict[str, Any]] = []
            fenced_code_closer_entries: list[dict[str, Any]] = []
            html_block_entries: list[dict[str, Any]] = []
            indented_code_entries: list[dict[str, Any]] = []
            dim_spans: list[tuple[int, int]] = []
            bold_spans: list[tuple[int, int]] = []
            italic_spans: list[tuple[int, int]] = []
            line_role = ""
            heading_level = 0
            table_kind = ""
            definition_role = ""
            inert = False
            if enabled and 0 <= int(line_index) < len(eb.buf.lines):
                line_is_fenced = bool(int(line_index) < len(fence_flags) and fence_flags[int(line_index)])
                fenced_role = str(fenced_roles.get(int(line_index), '') or '') if line_is_fenced else ''
                is_fenced_fence = fenced_role == 'fence'
                is_fenced_body = fenced_role == 'body'
                line_is_html_block = bool(int(line_index) < len(html_block_flags) and html_block_flags[int(line_index)])
                line_is_indented_code = bool(int(line_index) < len(indented_code_flags) and indented_code_flags[int(line_index)])
                inert = bool(line_is_fenced or line_is_html_block or line_is_indented_code)
                heading_role, heading_level = (heading_roles.get(int(line_index)) or ('', 0)) if not inert else ('', 0)
                definition_role, def_col0, def_col1 = (definition_roles.get(int(line_index)) or ('', 0, 0)) if not inert else ('', 0, 0)
                line_is_definition = bool(definition_role)
                table_kind = '' if inert else str(table_kinds.get(int(line_index), '') or '')
                is_table_header = table_kind == 'header'
                is_table_delim = table_kind == 'delimiter'
                is_thematic_break = (not inert) and (md_thematic_break_span(text) is not None)
                if heading_role == 'title':
                    line_role = 'heading-title'
                elif heading_role == 'underline':
                    line_role = 'heading-underline'
                elif is_table_header:
                    line_role = 'table-header'
                elif is_table_delim:
                    line_role = 'table-delimiter'
                elif is_thematic_break:
                    line_role = 'thematic-break'
                elif is_fenced_fence:
                    line_role = 'fenced-fence'
                elif is_fenced_body:
                    line_role = 'fenced-body'
                elif line_is_html_block:
                    line_role = 'html-block'
                elif line_is_indented_code:
                    line_role = 'indented-code'
                elif line_is_definition:
                    line_role = 'definition'

                next_line = md_docs_continuation_line(
                    list(eb.buf.lines),
                    int(line_index) + 1,
                    fence_flags=fence_flags,
                    html_block_flags=html_block_flags,
                    comment_spans=line_comment_spans,
                )
                next_next_line = md_docs_continuation_line(
                    list(eb.buf.lines),
                    int(line_index) + 2,
                    fence_flags=fence_flags,
                    html_block_flags=html_block_flags,
                    comment_spans=line_comment_spans,
                )
                masked_spans = line_comment_spans[int(line_index)] if int(line_index) < len(line_comment_spans) else []
                heading_entries = [
                    {
                        **dict(entry),
                        'start': 0,
                        'end': int(len(text)),
                        'text': str(text),
                    }
                    for entry in heading_entries_by_line.get(int(line_index), [])
                ] if not inert else []
                heading_title_entries = [
                    dict(entry)
                    for entry in heading_entries
                    if str(entry.get("role", "") or "") == "title"
                ]
                heading_underline_entries = [
                    dict(entry)
                    for entry in heading_entries
                    if str(entry.get("role", "") or "") == "underline"
                ]
                atx_heading_entries = [
                    dict(entry)
                    for entry in heading_entries
                    if str(entry.get("source_kind", "") or "") == "atx"
                ]
                setext_heading_entries = [
                    dict(entry)
                    for entry in heading_entries
                    if str(entry.get("source_kind", "") or "") == "setext"
                ]
                h1_heading_entries = [
                    dict(entry)
                    for entry in heading_entries
                    if int(entry.get("level", 0) or 0) == 1
                ]
                h2_heading_entries = [
                    dict(entry)
                    for entry in heading_entries
                    if int(entry.get("level", 0) or 0) == 2
                ]
                h3_heading_entries = [
                    dict(entry)
                    for entry in heading_entries
                    if int(entry.get("level", 0) or 0) == 3
                ]
                h4_heading_entries = [
                    dict(entry)
                    for entry in heading_entries
                    if int(entry.get("level", 0) or 0) == 4
                ]
                h5_heading_entries = [
                    dict(entry)
                    for entry in heading_entries
                    if int(entry.get("level", 0) or 0) == 5
                ]
                h6_heading_entries = [
                    dict(entry)
                    for entry in heading_entries
                    if int(entry.get("level", 0) or 0) == 6
                ]
                explicit_fragment_heading_entries = [
                    dict(entry)
                    for entry in heading_entries
                    if str(entry.get("fragment_source", "") or "") == "explicit"
                ]
                auto_fragment_heading_entries = [
                    dict(entry)
                    for entry in heading_entries
                    if str(entry.get("fragment_source", "") or "") == "auto"
                ]
                section_entry = dict(section_entry_by_line.get(int(line_index), {}))
                definition_entries = [
                    {
                        key: value
                        for key, value in dict(entry).items()
                        if key != 'render_end'
                    }
                    for entry in definition_entries_by_line.get(int(line_index), [])
                ] if not inert else []
                reference_definition_entries = [
                    dict(entry)
                    for entry in definition_entries
                    if str(entry.get("kind", "") or "") == "reference-definition"
                ]
                reference_definition_cont_entries = [
                    dict(entry)
                    for entry in definition_entries
                    if str(entry.get("kind", "") or "") == "reference-definition-cont"
                ]
                footnote_definition_entries = [
                    dict(entry)
                    for entry in definition_entries
                    if str(entry.get("kind", "") or "") == "footnote-definition"
                ]
                footnote_definition_cont_entries = [
                    dict(entry)
                    for entry in definition_entries
                    if str(entry.get("kind", "") or "") == "footnote-definition-cont"
                ]
                block_entries = [dict(entry) for entry in block_entries_by_line.get(int(line_index), [])]
                fenced_code_entries = [
                    dict(entry)
                    for entry in block_entries
                    if str(entry.get("kind", "") or "") == "fenced-code"
                ]
                backtick_fenced_code_entries = [
                    dict(entry)
                    for entry in fenced_code_entries
                    if str(entry.get("marker_kind", "") or "") == "backtick"
                ]
                tilde_fenced_code_entries = [
                    dict(entry)
                    for entry in fenced_code_entries
                    if str(entry.get("marker_kind", "") or "") == "tilde"
                ]
                language_fenced_code_entries = [
                    dict(entry)
                    for entry in fenced_code_entries
                    if int(entry.get("has_language", 0) or 0) == 1
                ]
                bare_fenced_code_entries = [
                    dict(entry)
                    for entry in fenced_code_entries
                    if int(entry.get("has_language", 0) or 0) == 0
                ]
                fenced_code_opener_entries = [
                    dict(entry)
                    for entry in fenced_code_entries
                    if str(entry.get("role", "") or "") == "opener"
                ]
                fenced_code_body_entries = [
                    dict(entry)
                    for entry in fenced_code_entries
                    if str(entry.get("role", "") or "") == "body"
                ]
                fenced_code_closer_entries = [
                    dict(entry)
                    for entry in fenced_code_entries
                    if str(entry.get("role", "") or "") == "closer"
                ]
                html_block_entries = [
                    dict(entry)
                    for entry in block_entries
                    if str(entry.get("kind", "") or "") == "html-block"
                ]
                indented_code_entries = [
                    dict(entry)
                    for entry in block_entries
                    if str(entry.get("kind", "") or "") == "indented-code"
                ]
                if not inert:
                    link_matches = md_link_matches(
                        text,
                        defs,
                        footdefs,
                        masked_spans=masked_spans,
                        next_line=next_line,
                        next_next_line=next_next_line,
                    )
                    link_spans = [
                        (int(m.label_start), int(m.label_end))
                        for m in link_matches
                    ]
                    link_entries = []
                    for match in link_matches:
                        meta = md_help_link_target_info(str(match.target or ""))
                        source_kind = str(md_help_link_source_kind(text, int(match.start), int(match.end), str(match.kind)))
                        reference_form = str(md_help_link_reference_form(text, int(match.start), int(match.end), str(match.kind)))
                        link_entries.append(
                            {
                                "kind": str(match.kind),
                                "source_kind": str(source_kind),
                                "reference_form": str(reference_form),
                                "start": int(match.start),
                                "end": int(match.end),
                                "label_start": int(match.label_start),
                                "label_end": int(match.label_end),
                                "display": str(match.display),
                                "target": str(match.target),
                                "target_kind": str(meta.get("target_kind", "") or ""),
                                "target_doc": str(meta.get("doc", "") or ""),
                                "target_fragment": str(meta.get("fragment", "") or ""),
                            }
                        )
                    local_doc_link_entries = [
                        dict(entry)
                        for entry in link_entries
                        if str(entry.get("target_kind", "") or "") in {"doc", "doc-fragment", "file", "file-fragment"}
                    ]
                    fragment_link_entries = [
                        dict(entry)
                        for entry in link_entries
                        if str(entry.get("target_kind", "") or "") in {"fragment", "footnote", "doc-fragment", "file-fragment"}
                    ]
                    external_link_entries = [
                        dict(entry)
                        for entry in link_entries
                        if str(entry.get("target_kind", "") or "") in {"external", "mailto"}
                    ]
                    footnote_link_entries = [
                        dict(entry)
                        for entry in link_entries
                        if str(entry.get("target_kind", "") or "") == "footnote"
                    ]
                    inline_link_entries = [
                        dict(entry)
                        for entry in link_entries
                        if str(entry.get("source_kind", "") or "") == "inline"
                    ]
                    reference_link_entries = [
                        dict(entry)
                        for entry in link_entries
                        if str(entry.get("source_kind", "") or "") == "reference"
                    ]
                    full_reference_link_entries = [
                        dict(entry)
                        for entry in link_entries
                        if str(entry.get("reference_form", "") or "") == "full"
                    ]
                    collapsed_reference_link_entries = [
                        dict(entry)
                        for entry in link_entries
                        if str(entry.get("reference_form", "") or "") == "collapsed"
                    ]
                    shortcut_reference_link_entries = [
                        dict(entry)
                        for entry in link_entries
                        if str(entry.get("reference_form", "") or "") == "shortcut"
                    ]
                    autolink_entries = [
                        dict(entry)
                        for entry in link_entries
                        if str(entry.get("source_kind", "") or "") == "autolink"
                    ]
                    footnote_ref_entries = [
                        dict(entry)
                        for entry in link_entries
                        if str(entry.get("source_kind", "") or "") == "footnote"
                    ]
                    image_matches = md_image_matches(
                        text,
                        defs,
                        masked_spans=masked_spans,
                        next_line=next_line,
                        next_next_line=next_next_line,
                    )
                    image_entries = []
                    for match in image_matches:
                        meta = md_help_link_target_info(str(match.target or ""))
                        source_kind = str(md_help_image_source_kind(text, int(match.start), int(match.end), str(match.kind)))
                        reference_form = str(md_help_image_reference_form(text, int(match.start), int(match.end), str(match.kind)))
                        image_entries.append(
                            {
                                "kind": str(match.kind),
                                "source_kind": str(source_kind),
                                "reference_form": str(reference_form),
                                "start": int(match.start),
                                "end": int(match.end),
                                "alt_start": int(match.alt_start),
                                "alt_end": int(match.alt_end),
                                "alt_text": str(match.alt_text),
                                "target": str(match.target),
                                "target_kind": str(meta.get("target_kind", "") or ""),
                                "target_doc": str(meta.get("doc", "") or ""),
                                "target_fragment": str(meta.get("fragment", "") or ""),
                            }
                        )
                    inline_image_entries = [
                        dict(entry)
                        for entry in image_entries
                        if str(entry.get("source_kind", "") or "") == "inline"
                    ]
                    reference_image_entries = [
                        dict(entry)
                        for entry in image_entries
                        if str(entry.get("source_kind", "") or "") == "reference"
                    ]
                    full_reference_image_entries = [
                        dict(entry)
                        for entry in image_entries
                        if str(entry.get("reference_form", "") or "") == "full"
                    ]
                    collapsed_reference_image_entries = [
                        dict(entry)
                        for entry in image_entries
                        if str(entry.get("reference_form", "") or "") == "collapsed"
                    ]
                    shortcut_reference_image_entries = [
                        dict(entry)
                        for entry in image_entries
                        if str(entry.get("reference_form", "") or "") == "shortcut"
                    ]
                    local_doc_image_entries = [
                        dict(entry)
                        for entry in image_entries
                        if str(entry.get("target_kind", "") or "") in {"doc", "doc-fragment", "file", "file-fragment"}
                    ]
                    fragment_image_entries = [
                        dict(entry)
                        for entry in image_entries
                        if str(entry.get("target_kind", "") or "") in {"fragment", "footnote", "doc-fragment", "file-fragment"}
                    ]
                    external_image_entries = [
                        dict(entry)
                        for entry in image_entries
                        if str(entry.get("target_kind", "") or "") in {"external", "mailto"}
                    ]
                    footnote_image_entries = [
                        dict(entry)
                        for entry in image_entries
                        if str(entry.get("target_kind", "") or "") == "footnote"
                    ]
                    code_matches = md_inline_code_matches(text)
                    code_entries = [
                        {
                            "kind": str(match.kind),
                            "start": int(match.start),
                            "end": int(match.end),
                            "body_start": int(match.body_start),
                            "body_end": int(match.body_end),
                            "delimiter_length": int(match.delimiter_length),
                            "delimiter_kind": ("single-backtick" if int(match.delimiter_length) == 1 else "multi-backtick"),
                            "text": str(match.text),
                        }
                        for match in code_matches
                    ]
                    single_backtick_code_entries = [
                        dict(entry)
                        for entry in code_entries
                        if int(entry.get("delimiter_length", 0) or 0) == 1
                    ]
                    multi_backtick_code_entries = [
                        dict(entry)
                        for entry in code_entries
                        if int(entry.get("delimiter_length", 0) or 0) > 1
                    ]
                    markup_matches = md_inline_markup_matches(text)
                    markup_entries = [
                        {
                            "kind": str(match.kind),
                            "start": int(match.start),
                            "end": int(match.end),
                            "body_start": int(match.body_start),
                            "body_end": int(match.body_end),
                            "delimiter": str(match.delimiter),
                            "delimiter_length": int(match.delimiter_length),
                            "delimiter_kind": str(md_inline_markup_delimiter_kind(str(match.delimiter))),
                            "text": str(match.text),
                        }
                        for match in markup_matches
                    ]
                    strong_markup_entries = [
                        dict(entry)
                        for entry in markup_entries
                        if str(entry.get("kind", "") or "") == "strong"
                    ]
                    emphasis_markup_entries = [
                        dict(entry)
                        for entry in markup_entries
                        if str(entry.get("kind", "") or "") == "emphasis"
                    ]
                    strike_markup_entries = [
                        dict(entry)
                        for entry in markup_entries
                        if str(entry.get("kind", "") or "") == "strike"
                    ]
                    asterisk_markup_entries = [
                        dict(entry)
                        for entry in markup_entries
                        if str(entry.get("delimiter_kind", "") or "") == "asterisk"
                    ]
                    underscore_markup_entries = [
                        dict(entry)
                        for entry in markup_entries
                        if str(entry.get("delimiter_kind", "") or "") == "underscore"
                    ]
                    tilde_markup_entries = [
                        dict(entry)
                        for entry in markup_entries
                        if str(entry.get("delimiter_kind", "") or "") == "tilde"
                    ]
                    literal_entries = [
                        {
                            "kind": str(match.kind),
                            "start": int(match.start),
                            "end": int(match.end),
                            "text": str(match.text),
                            "detail": str(match.detail),
                        }
                        for match in (
                            md_raw_html_tag_matches(text, masked_spans=masked_spans)
                            + md_escaped_markdown_matches(text, masked_spans=masked_spans)
                        )
                    ]
                    literal_entries.sort(key=lambda entry: (int(entry["start"]), int(entry["end"])))
                    raw_html_literal_entries = [
                        dict(entry)
                        for entry in literal_entries
                        if str(entry.get("kind", "") or "") == "raw-html-tag"
                    ]
                    escaped_markdown_entries = [
                        dict(entry)
                        for entry in literal_entries
                        if str(entry.get("kind", "") or "") == "escaped-markdown"
                    ]
                    code_spans = md_inline_code_spans(text)
                    code_delim_spans = md_inline_code_delimiter_spans(text)
                    strong_spans = md_strong_spans(text)
                    emphasis_spans = md_emphasis_spans(text)
                    strike_spans = md_strikethrough_spans(text)
                    inline_markup_delim_spans = md_inline_markup_delimiter_spans(text)
                    pipe_spans = md_table_pipe_spans(text) if table_kind else []
                    if table_kind == "delimiter":
                        table_entries = [dict(entry) for entry in md_table_delimiter_entries(text)]
                    elif table_kind in {"header", "body"}:
                        table_entries = [
                            {
                                **dict(entry),
                                "kind": f"{table_kind}-cell",
                            }
                            for entry in md_table_cell_entries(text)
                        ]
                    if table_entries:
                        alignments = table_alignments_by_line.get(int(line_index), {})
                        table_entries = [
                            {
                                **dict(entry),
                                "align": str(
                                    alignments.get(
                                        int(entry.get("column", 0) or 0),
                                        entry.get("align", "default") or "default",
                                    )
                                ),
                            }
                            for entry in table_entries
                        ]
                    table_header_entries = [
                        dict(entry)
                        for entry in table_entries
                        if str(entry.get("kind", "") or "") == "header-cell"
                    ]
                    table_body_entries = [
                        dict(entry)
                        for entry in table_entries
                        if str(entry.get("kind", "") or "") == "body-cell"
                    ]
                    table_delimiter_entries = [
                        dict(entry)
                        for entry in table_entries
                        if str(entry.get("kind", "") or "") == "delimiter-cell"
                    ]
                    default_aligned_table_entries = [
                        dict(entry)
                        for entry in table_entries
                        if str(entry.get("align", "default") or "default") == "default"
                    ]
                    left_aligned_table_entries = [
                        dict(entry)
                        for entry in table_entries
                        if str(entry.get("align", "default") or "default") == "left"
                    ]
                    center_aligned_table_entries = [
                        dict(entry)
                        for entry in table_entries
                        if str(entry.get("align", "default") or "default") == "center"
                    ]
                    right_aligned_table_entries = [
                        dict(entry)
                        for entry in table_entries
                        if str(entry.get("align", "default") or "default") == "right"
                    ]
                    list_info = md_list_marker(text, max_leading_spaces=None)
                    list_marker_spans = [tuple(int(x) for x in list_info[:2])] if list_info else []
                    task_info = md_task_checkbox(text, max_leading_spaces=None)
                    task_box_spans = [tuple(int(x) for x in task_info[:2])] if task_info else []
                    checked_task_body = []
                    task_body = md_task_body_span(text, max_leading_spaces=None)
                    if task_info and bool(task_info[2]) and task_body is not None:
                        checked_task_body = [tuple(int(x) for x in task_body)]
                    blockquote_info = md_blockquote_prefix(text)
                    blockquote_prefix_spans = [tuple(int(x) for x in blockquote_info[:2])] if blockquote_info else []
                    blockquote_body = []
                    body_span = md_blockquote_body_span(text)
                    if blockquote_info and body_span is not None:
                        blockquote_body = [tuple(int(x) for x in body_span)]
                    blockquote_alert_info = md_blockquote_alert_marker(text)
                    blockquote_alert_spans = [tuple(int(x) for x in blockquote_alert_info[:2])] if blockquote_alert_info else []
                    footnote_ref_spans = md_footnote_ref_token_spans(
                        text,
                        footdefs,
                        masked_spans=masked_spans,
                        next_line=next_line,
                        next_next_line=next_next_line,
                    )
                    autolink_token_spans = md_autolink_token_spans(
                        text,
                        masked_spans=masked_spans,
                        next_line=next_line,
                        next_next_line=next_next_line,
                    )
                    image_token_spans = md_image_token_spans(
                        text,
                        defs,
                        masked_spans=masked_spans,
                        next_line=next_line,
                        next_next_line=next_next_line,
                    )
                    link_source_token_spans = md_link_source_token_spans(
                        text,
                        defs,
                        footdefs,
                        masked_spans=masked_spans,
                        next_line=next_line,
                        next_next_line=next_next_line,
                    )
                    raw_html_tag_spans = md_raw_html_tag_token_spans(
                        text,
                        masked_spans=masked_spans,
                    )
                    escaped_markdown_spans = md_escaped_markdown_token_spans(
                        text,
                        masked_spans=masked_spans,
                    )
                    thematic_break_chars = md_thematic_break_char_spans(text) if is_thematic_break else []
                    structure_entries = []
                    if list_info:
                        a, b, list_kind = list_info
                        list_entry = {
                            "kind": "list-marker",
                            "start": int(a),
                            "end": int(b),
                            "text": str(text[int(a):int(b)]),
                            "list_kind": str(list_kind),
                            "marker": str(text[int(a):int(b)]),
                        }
                        structure_entries.append(list_entry)
                        list_entries.append(dict(list_entry))
                    if task_info:
                        a, b, checked = task_info
                        task_entry: dict[str, Any] = {
                            "kind": "task-checkbox",
                            "start": int(a),
                            "end": int(b),
                            "text": str(text[int(a):int(b)]),
                            "checked": 1 if checked else 0,
                        }
                        if list_info:
                            la, lb, list_kind = list_info
                            task_entry["list_kind"] = str(list_kind)
                            task_entry["list_marker"] = str(text[int(la):int(lb)])
                        if task_body is not None:
                            task_entry["body_start"] = int(task_body[0])
                            task_entry["body_end"] = int(task_body[1])
                        structure_entries.append(task_entry)
                        task_entries.append(dict(task_entry))
                    checked_task_entries = [
                        dict(entry)
                        for entry in task_entries
                        if int(entry.get("checked", 0) or 0) == 1
                    ]
                    unchecked_task_entries = [
                        dict(entry)
                        for entry in task_entries
                        if int(entry.get("checked", 0) or 0) == 0
                    ]
                    bullet_task_entries = [
                        dict(entry)
                        for entry in task_entries
                        if str(entry.get("list_kind", "") or "") == "bullet"
                    ]
                    ordered_task_entries = [
                        dict(entry)
                        for entry in task_entries
                        if str(entry.get("list_kind", "") or "") == "ordered"
                    ]
                    if blockquote_info:
                        a, b, depth = blockquote_info
                        quote_entry: dict[str, Any] = {
                            "kind": "blockquote-prefix",
                            "start": int(a),
                            "end": int(b),
                            "text": str(text[int(a):int(b)]),
                            "depth": int(depth),
                        }
                        if body_span is not None:
                            quote_entry["body_start"] = int(body_span[0])
                            quote_entry["body_end"] = int(body_span[1])
                        structure_entries.append(quote_entry)
                        blockquote_entries.append(dict(quote_entry))
                    if blockquote_alert_info:
                        a, b, alert_kind = blockquote_alert_info
                        alert_entry = {
                            "kind": "blockquote-alert",
                            "start": int(a),
                            "end": int(b),
                            "text": str(text[int(a):int(b)]),
                            "alert_kind": str(alert_kind),
                        }
                        structure_entries.append(alert_entry)
                        blockquote_alert_entries.append(dict(alert_entry))
                    note_blockquote_alert_entries = [
                        dict(entry)
                        for entry in blockquote_alert_entries
                        if str(entry.get("alert_kind", "") or "") == "note"
                    ]
                    tip_blockquote_alert_entries = [
                        dict(entry)
                        for entry in blockquote_alert_entries
                        if str(entry.get("alert_kind", "") or "") == "tip"
                    ]
                    important_blockquote_alert_entries = [
                        dict(entry)
                        for entry in blockquote_alert_entries
                        if str(entry.get("alert_kind", "") or "") == "important"
                    ]
                    warning_blockquote_alert_entries = [
                        dict(entry)
                        for entry in blockquote_alert_entries
                        if str(entry.get("alert_kind", "") or "") == "warning"
                    ]
                    caution_blockquote_alert_entries = [
                        dict(entry)
                        for entry in blockquote_alert_entries
                        if str(entry.get("alert_kind", "") or "") == "caution"
                    ]
                    if is_thematic_break:
                        thematic_span = md_thematic_break_span(text)
                        if thematic_span is not None:
                            a, b = thematic_span
                            marker = ""
                            for ch in text[int(a):int(b)]:
                                if ch in '-_*':
                                    marker = ch
                                    break
                            thematic_entry = {
                                "kind": "thematic-break",
                                "start": int(a),
                                "end": int(b),
                                "text": str(text[int(a):int(b)]),
                                "marker": str(marker),
                                "marker_count": int(len(thematic_break_chars)),
                            }
                            structure_entries.append(thematic_entry)
                            thematic_break_entries.append(dict(thematic_entry))
                    structure_entries.sort(key=lambda entry: (int(entry.get("start", 0)), int(entry.get("end", 0)), str(entry.get("kind", ""))))
                    definition_marker_spans = [(int(def_col0), int(def_col1))] if int(def_col1) > int(def_col0) else []
                    dim_spans = _merge_spans(
                        code_spans
                        + code_delim_spans
                        + strike_spans
                        + inline_markup_delim_spans
                        + pipe_spans
                        + checked_task_body
                        + blockquote_body
                        + masked_spans
                        + image_token_spans
                        + link_source_token_spans
                        + raw_html_tag_spans
                        + escaped_markdown_spans
                    )
                    bold_spans = _merge_spans(
                        strong_spans
                        + code_delim_spans
                        + list_marker_spans
                        + task_box_spans
                        + blockquote_prefix_spans
                        + blockquote_alert_spans
                        + footnote_ref_spans
                        + autolink_token_spans
                        + thematic_break_chars
                        + definition_marker_spans
                    )
                    italic_spans = _merge_spans(emphasis_spans)

            row_entry = {
                "view_y": int(view_y),
                "screen_y": int(row["screen_y"]) if "screen_y" in row else int(layout.get("viewport_y", 0) or 0) + int(view_y),
                "line": int(line_index),
                "start_col": int(start_col),
                "text": text,
                "inert": 1 if inert else 0,
                "line_role": str(line_role),
                "heading_level": int(heading_level),
                "table_kind": str(table_kind),
                "definition_role": str(definition_role),
                "link_spans": [[int(a), int(b)] for a, b in link_spans],
                "link_entries": link_entries,
                "local_doc_link_entries": local_doc_link_entries,
                "fragment_link_entries": fragment_link_entries,
                "external_link_entries": external_link_entries,
                "footnote_link_entries": footnote_link_entries,
                "inline_link_entries": inline_link_entries,
                "reference_link_entries": reference_link_entries,
                "full_reference_link_entries": full_reference_link_entries,
                "collapsed_reference_link_entries": collapsed_reference_link_entries,
                "shortcut_reference_link_entries": shortcut_reference_link_entries,
                "autolink_entries": autolink_entries,
                "footnote_ref_entries": footnote_ref_entries,
                "image_entries": image_entries,
                "inline_image_entries": inline_image_entries,
                "reference_image_entries": reference_image_entries,
                "full_reference_image_entries": full_reference_image_entries,
                "collapsed_reference_image_entries": collapsed_reference_image_entries,
                "shortcut_reference_image_entries": shortcut_reference_image_entries,
                "local_doc_image_entries": local_doc_image_entries,
                "fragment_image_entries": fragment_image_entries,
                "external_image_entries": external_image_entries,
                "footnote_image_entries": footnote_image_entries,
                "code_entries": code_entries,
                "single_backtick_code_entries": single_backtick_code_entries,
                "multi_backtick_code_entries": multi_backtick_code_entries,
                "markup_entries": markup_entries,
                "strong_markup_entries": strong_markup_entries,
                "emphasis_markup_entries": emphasis_markup_entries,
                "strike_markup_entries": strike_markup_entries,
                "asterisk_markup_entries": asterisk_markup_entries,
                "underscore_markup_entries": underscore_markup_entries,
                "tilde_markup_entries": tilde_markup_entries,
                "literal_entries": literal_entries,
                "raw_html_literal_entries": raw_html_literal_entries,
                "escaped_markdown_entries": escaped_markdown_entries,
                "table_entries": table_entries,
                "table_header_entries": table_header_entries,
                "table_body_entries": table_body_entries,
                "table_delimiter_entries": table_delimiter_entries,
                "default_aligned_table_entries": default_aligned_table_entries,
                "left_aligned_table_entries": left_aligned_table_entries,
                "center_aligned_table_entries": center_aligned_table_entries,
                "right_aligned_table_entries": right_aligned_table_entries,
                "structure_entries": structure_entries,
                "list_entries": list_entries,
                "task_entries": task_entries,
                "checked_task_entries": checked_task_entries,
                "unchecked_task_entries": unchecked_task_entries,
                "bullet_task_entries": bullet_task_entries,
                "ordered_task_entries": ordered_task_entries,
                "blockquote_entries": blockquote_entries,
                "blockquote_alert_entries": blockquote_alert_entries,
                "note_blockquote_alert_entries": note_blockquote_alert_entries,
                "tip_blockquote_alert_entries": tip_blockquote_alert_entries,
                "important_blockquote_alert_entries": important_blockquote_alert_entries,
                "warning_blockquote_alert_entries": warning_blockquote_alert_entries,
                "caution_blockquote_alert_entries": caution_blockquote_alert_entries,
                "thematic_break_entries": thematic_break_entries,
                "heading_entries": heading_entries,
                "heading_title_entries": heading_title_entries,
                "heading_underline_entries": heading_underline_entries,
                "atx_heading_entries": atx_heading_entries,
                "setext_heading_entries": setext_heading_entries,
                "h1_heading_entries": h1_heading_entries,
                "h2_heading_entries": h2_heading_entries,
                "h3_heading_entries": h3_heading_entries,
                "h4_heading_entries": h4_heading_entries,
                "h5_heading_entries": h5_heading_entries,
                "h6_heading_entries": h6_heading_entries,
                "explicit_fragment_heading_entries": explicit_fragment_heading_entries,
                "auto_fragment_heading_entries": auto_fragment_heading_entries,
                "section_entry": section_entry,
                "definition_entries": definition_entries,
                "reference_definition_entries": reference_definition_entries,
                "reference_definition_cont_entries": reference_definition_cont_entries,
                "footnote_definition_entries": footnote_definition_entries,
                "footnote_definition_cont_entries": footnote_definition_cont_entries,
                "block_entries": block_entries,
                "fenced_code_entries": fenced_code_entries,
                "backtick_fenced_code_entries": backtick_fenced_code_entries,
                "tilde_fenced_code_entries": tilde_fenced_code_entries,
                "language_fenced_code_entries": language_fenced_code_entries,
                "bare_fenced_code_entries": bare_fenced_code_entries,
                "fenced_code_opener_entries": fenced_code_opener_entries,
                "fenced_code_body_entries": fenced_code_body_entries,
                "fenced_code_closer_entries": fenced_code_closer_entries,
                "html_block_entries": html_block_entries,
                "indented_code_entries": indented_code_entries,
                "dim_spans": [[int(a), int(b)] for a, b in dim_spans],
                "bold_spans": [[int(a), int(b)] for a, b in bold_spans],
                "italic_spans": [[int(a), int(b)] for a, b in italic_spans],
                "link_count": int(len(link_spans)),
                "local_doc_link_count": int(len(local_doc_link_entries)),
                "fragment_link_count": int(len(fragment_link_entries)),
                "external_link_count": int(len(external_link_entries)),
                "footnote_link_count": int(len(footnote_link_entries)),
                "inline_link_count": int(len(inline_link_entries)),
                "reference_link_count": int(len(reference_link_entries)),
                "full_reference_link_count": int(len(full_reference_link_entries)),
                "collapsed_reference_link_count": int(len(collapsed_reference_link_entries)),
                "shortcut_reference_link_count": int(len(shortcut_reference_link_entries)),
                "autolink_count": int(len(autolink_entries)),
                "footnote_ref_count": int(len(footnote_ref_entries)),
                "image_count": int(len(image_entries)),
                "inline_image_count": int(len(inline_image_entries)),
                "reference_image_count": int(len(reference_image_entries)),
                "full_reference_image_count": int(len(full_reference_image_entries)),
                "collapsed_reference_image_count": int(len(collapsed_reference_image_entries)),
                "shortcut_reference_image_count": int(len(shortcut_reference_image_entries)),
                "local_doc_image_count": int(len(local_doc_image_entries)),
                "fragment_image_count": int(len(fragment_image_entries)),
                "external_image_count": int(len(external_image_entries)),
                "footnote_image_count": int(len(footnote_image_entries)),
                "code_count": int(len(code_entries)),
                "single_backtick_code_count": int(len(single_backtick_code_entries)),
                "multi_backtick_code_count": int(len(multi_backtick_code_entries)),
                "markup_count": int(len(markup_entries)),
                "strong_markup_count": int(len(strong_markup_entries)),
                "emphasis_markup_count": int(len(emphasis_markup_entries)),
                "strike_markup_count": int(len(strike_markup_entries)),
                "asterisk_markup_count": int(len(asterisk_markup_entries)),
                "underscore_markup_count": int(len(underscore_markup_entries)),
                "tilde_markup_count": int(len(tilde_markup_entries)),
                "literal_count": int(len(literal_entries)),
                "raw_html_literal_count": int(len(raw_html_literal_entries)),
                "escaped_markdown_count": int(len(escaped_markdown_entries)),
                "table_count": int(len(table_entries)),
                "table_header_count": int(len(table_header_entries)),
                "table_body_count": int(len(table_body_entries)),
                "table_delimiter_count": int(len(table_delimiter_entries)),
                "default_aligned_table_count": int(len(default_aligned_table_entries)),
                "left_aligned_table_count": int(len(left_aligned_table_entries)),
                "center_aligned_table_count": int(len(center_aligned_table_entries)),
                "right_aligned_table_count": int(len(right_aligned_table_entries)),
                "structure_count": int(len(structure_entries)),
                "list_count": int(len(list_entries)),
                "bullet_list_count": int(sum(1 for entry in list_entries if str(entry.get("list_kind", "") or "") == "bullet")),
                "ordered_list_count": int(sum(1 for entry in list_entries if str(entry.get("list_kind", "") or "") == "ordered")),
                "task_count": int(len(task_entries)),
                "checked_task_count": int(len(checked_task_entries)),
                "unchecked_task_count": int(len(unchecked_task_entries)),
                "bullet_task_count": int(len(bullet_task_entries)),
                "ordered_task_count": int(len(ordered_task_entries)),
                "blockquote_count": int(len(blockquote_entries)),
                "blockquote_alert_count": int(len(blockquote_alert_entries)),
                "note_blockquote_alert_count": int(len(note_blockquote_alert_entries)),
                "tip_blockquote_alert_count": int(len(tip_blockquote_alert_entries)),
                "important_blockquote_alert_count": int(len(important_blockquote_alert_entries)),
                "warning_blockquote_alert_count": int(len(warning_blockquote_alert_entries)),
                "caution_blockquote_alert_count": int(len(caution_blockquote_alert_entries)),
                "thematic_break_count": int(len(thematic_break_entries)),
                "heading_count": int(len(heading_entries)),
                "heading_title_count": int(len(heading_title_entries)),
                "heading_underline_count": int(len(heading_underline_entries)),
                "atx_heading_count": int(len(atx_heading_entries)),
                "setext_heading_count": int(len(setext_heading_entries)),
                "h1_heading_count": int(len(h1_heading_entries)),
                "h2_heading_count": int(len(h2_heading_entries)),
                "h3_heading_count": int(len(h3_heading_entries)),
                "h4_heading_count": int(len(h4_heading_entries)),
                "h5_heading_count": int(len(h5_heading_entries)),
                "h6_heading_count": int(len(h6_heading_entries)),
                "explicit_fragment_heading_count": int(len(explicit_fragment_heading_entries)),
                "auto_fragment_heading_count": int(len(auto_fragment_heading_entries)),
                "section_count": 1 if section_entry else 0,
                "definition_count": int(len(definition_entries)),
                "reference_definition_count": int(len(reference_definition_entries)),
                "reference_definition_cont_count": int(len(reference_definition_cont_entries)),
                "footnote_definition_count": int(len(footnote_definition_entries)),
                "footnote_definition_cont_count": int(len(footnote_definition_cont_entries)),
                "block_count": int(len(block_entries)),
                "fenced_code_count": int(len(fenced_code_entries)),
                "backtick_fenced_code_count": int(len(backtick_fenced_code_entries)),
                "tilde_fenced_code_count": int(len(tilde_fenced_code_entries)),
                "language_fenced_code_count": int(len(language_fenced_code_entries)),
                "bare_fenced_code_count": int(len(bare_fenced_code_entries)),
                "fenced_code_opener_count": int(len(fenced_code_opener_entries)),
                "fenced_code_body_count": int(len(fenced_code_body_entries)),
                "fenced_code_closer_count": int(len(fenced_code_closer_entries)),
                "html_block_count": int(len(html_block_entries)),
                "indented_code_count": int(len(indented_code_entries)),
                "span_count": int(len(link_spans) + len(dim_spans) + len(bold_spans) + len(italic_spans)),
            }
            if line_role or link_spans or dim_spans or bold_spans or italic_spans:
                cue_rows += 1
            if link_entries:
                link_rows += 1
                link_entry_count += int(len(link_entries))
                if local_doc_link_entries:
                    local_doc_link_rows += 1
                if fragment_link_entries:
                    fragment_link_rows += 1
                if external_link_entries:
                    external_link_rows += 1
                if footnote_link_entries:
                    footnote_link_rows += 1
                if inline_link_entries:
                    inline_link_rows += 1
                if reference_link_entries:
                    reference_link_rows += 1
                if full_reference_link_entries:
                    full_reference_link_rows += 1
                if collapsed_reference_link_entries:
                    collapsed_reference_link_rows += 1
                if shortcut_reference_link_entries:
                    shortcut_reference_link_rows += 1
                if autolink_entries:
                    autolink_rows += 1
                if footnote_ref_entries:
                    footnote_ref_rows += 1
                for entry in link_entries:
                    target_kind = str(entry.get("target_kind", "") or "")
                    source_kind = str(entry.get("source_kind", "") or "")
                    reference_form = str(entry.get("reference_form", "") or "")
                    if target_kind in {"external", "mailto"}:
                        external_link_count += 1
                    if target_kind in {"doc", "doc-fragment", "file", "file-fragment"}:
                        local_doc_link_count += 1
                    if target_kind in {"fragment", "footnote", "doc-fragment", "file-fragment"}:
                        fragment_link_count += 1
                    if target_kind == "footnote":
                        footnote_link_count += 1
                    if source_kind == "inline":
                        inline_link_count += 1
                    elif source_kind == "reference":
                        reference_link_count += 1
                        if reference_form == "full":
                            full_reference_link_count += 1
                        elif reference_form == "collapsed":
                            collapsed_reference_link_count += 1
                        elif reference_form == "shortcut":
                            shortcut_reference_link_count += 1
                    elif source_kind == "autolink":
                        autolink_count += 1
                    elif source_kind == "footnote":
                        footnote_ref_count += 1
            if image_entries:
                image_rows += 1
                image_entry_count += int(len(image_entries))
                if inline_image_entries:
                    inline_image_rows += 1
                if reference_image_entries:
                    reference_image_rows += 1
                if full_reference_image_entries:
                    full_reference_image_rows += 1
                if collapsed_reference_image_entries:
                    collapsed_reference_image_rows += 1
                if shortcut_reference_image_entries:
                    shortcut_reference_image_rows += 1
                if local_doc_image_entries:
                    local_doc_image_rows += 1
                if fragment_image_entries:
                    fragment_image_rows += 1
                if external_image_entries:
                    external_image_rows += 1
                if footnote_image_entries:
                    footnote_image_rows += 1
                for entry in image_entries:
                    source_kind = str(entry.get("source_kind", "") or "")
                    reference_form = str(entry.get("reference_form", "") or "")
                    target_kind = str(entry.get("target_kind", "") or "")
                    if source_kind == "inline":
                        inline_image_count += 1
                    elif source_kind == "reference":
                        reference_image_count += 1
                        if reference_form == "full":
                            full_reference_image_count += 1
                        elif reference_form == "collapsed":
                            collapsed_reference_image_count += 1
                        elif reference_form == "shortcut":
                            shortcut_reference_image_count += 1
                    if target_kind in {"external", "mailto"}:
                        external_image_count += 1
                    if target_kind in {"doc", "doc-fragment", "file", "file-fragment"}:
                        local_doc_image_count += 1
                    if target_kind in {"fragment", "footnote", "doc-fragment", "file-fragment"}:
                        fragment_image_count += 1
                    if target_kind == "footnote":
                        footnote_image_count += 1
            if code_entries:
                code_rows += 1
                code_entry_count += int(len(code_entries))
                if single_backtick_code_entries:
                    single_backtick_code_rows += 1
                if multi_backtick_code_entries:
                    multi_backtick_code_rows += 1
                for entry in code_entries:
                    if int(entry.get("delimiter_length", 0) or 0) == 1:
                        single_backtick_code_count += 1
                    elif int(entry.get("delimiter_length", 0) or 0) > 1:
                        multi_backtick_code_count += 1
            if markup_entries:
                markup_rows += 1
                markup_entry_count += int(len(markup_entries))
                if strong_markup_entries:
                    strong_markup_rows += 1
                if emphasis_markup_entries:
                    emphasis_markup_rows += 1
                if strike_markup_entries:
                    strike_markup_rows += 1
                if asterisk_markup_entries:
                    asterisk_markup_rows += 1
                if underscore_markup_entries:
                    underscore_markup_rows += 1
                if tilde_markup_entries:
                    tilde_markup_rows += 1
                for entry in markup_entries:
                    kind = str(entry.get("kind", "") or "")
                    delimiter_kind = str(entry.get("delimiter_kind", "") or "")
                    if kind == "strong":
                        strong_entry_count += 1
                    elif kind == "emphasis":
                        emphasis_entry_count += 1
                    elif kind == "strike":
                        strike_entry_count += 1
                    if delimiter_kind == "asterisk":
                        asterisk_markup_count += 1
                    elif delimiter_kind == "underscore":
                        underscore_markup_count += 1
                    elif delimiter_kind == "tilde":
                        tilde_markup_count += 1
            if literal_entries:
                literal_rows += 1
                literal_entry_count += int(len(literal_entries))
                if raw_html_literal_entries:
                    raw_html_rows += 1
                if escaped_markdown_entries:
                    escaped_markdown_rows += 1
                for entry in literal_entries:
                    kind = str(entry.get("kind", "") or "")
                    if kind == "raw-html-tag":
                        raw_html_entry_count += 1
                    elif kind == "escaped-markdown":
                        escaped_markdown_entry_count += 1
            if table_entries:
                table_rows += 1
                table_entry_count += int(len(table_entries))
                if table_header_entries:
                    table_header_rows += 1
                if table_body_entries:
                    table_body_rows += 1
                if table_delimiter_entries:
                    table_delimiter_rows += 1
                if default_aligned_table_entries:
                    default_aligned_table_rows += 1
                if left_aligned_table_entries:
                    left_aligned_table_rows += 1
                if center_aligned_table_entries:
                    center_aligned_table_rows += 1
                if right_aligned_table_entries:
                    right_aligned_table_rows += 1
                for entry in table_entries:
                    kind = str(entry.get("kind", "") or "")
                    align = str(entry.get("align", "default") or "default")
                    if kind == "header-cell":
                        table_header_cell_count += 1
                    elif kind == "body-cell":
                        table_body_cell_count += 1
                    elif kind == "delimiter-cell":
                        table_delimiter_cell_count += 1
                    if align == "default":
                        default_aligned_table_entry_count += 1
                    elif align == "left":
                        left_aligned_table_entry_count += 1
                    elif align == "center":
                        center_aligned_table_entry_count += 1
                    elif align == "right":
                        right_aligned_table_entry_count += 1
            if structure_entries:
                structure_rows += 1
                structure_entry_count += int(len(structure_entries))
                for entry in structure_entries:
                    kind = str(entry.get("kind", "") or "")
                    if kind == "list-marker":
                        list_entry_count += 1
                    elif kind == "task-checkbox":
                        task_entry_count += 1
                    elif kind == "blockquote-prefix":
                        blockquote_entry_count += 1
                    elif kind == "blockquote-alert":
                        blockquote_alert_entry_count += 1
                        alert_kind = str(entry.get("alert_kind", "") or "")
                        if alert_kind == "note":
                            note_blockquote_alert_entry_count += 1
                        elif alert_kind == "tip":
                            tip_blockquote_alert_entry_count += 1
                        elif alert_kind == "important":
                            important_blockquote_alert_entry_count += 1
                        elif alert_kind == "warning":
                            warning_blockquote_alert_entry_count += 1
                        elif alert_kind == "caution":
                            caution_blockquote_alert_entry_count += 1
                    elif kind == "thematic-break":
                        thematic_break_entry_count += 1
            if list_entries:
                list_rows += 1
                kinds = {str(entry.get("list_kind", "") or "") for entry in list_entries}
                if "bullet" in kinds:
                    bullet_list_rows += 1
                if "ordered" in kinds:
                    ordered_list_rows += 1
                for entry in list_entries:
                    list_kind = str(entry.get("list_kind", "") or "")
                    if list_kind == "bullet":
                        bullet_list_entry_count += 1
                    elif list_kind == "ordered":
                        ordered_list_entry_count += 1
            if task_entries:
                task_rows += 1
                if checked_task_entries:
                    checked_task_rows += 1
                if unchecked_task_entries:
                    unchecked_task_rows += 1
                task_kinds = {str(entry.get("list_kind", "") or "") for entry in task_entries}
                if "bullet" in task_kinds:
                    bullet_task_rows += 1
                if "ordered" in task_kinds:
                    ordered_task_rows += 1
                for entry in task_entries:
                    if int(entry.get("checked", 0) or 0) == 1:
                        checked_task_entry_count += 1
                    else:
                        unchecked_task_entry_count += 1
                    list_kind = str(entry.get("list_kind", "") or "")
                    if list_kind == "bullet":
                        bullet_task_entry_count += 1
                    elif list_kind == "ordered":
                        ordered_task_entry_count += 1
            if blockquote_entries:
                blockquote_rows += 1
            if blockquote_alert_entries:
                blockquote_alert_rows += 1
                if note_blockquote_alert_entries:
                    note_blockquote_alert_rows += 1
                if tip_blockquote_alert_entries:
                    tip_blockquote_alert_rows += 1
                if important_blockquote_alert_entries:
                    important_blockquote_alert_rows += 1
                if warning_blockquote_alert_entries:
                    warning_blockquote_alert_rows += 1
                if caution_blockquote_alert_entries:
                    caution_blockquote_alert_rows += 1
            if thematic_break_entries:
                thematic_break_rows += 1
            if heading_entries:
                heading_rows += 1
                heading_entry_count += int(len(heading_entries))
                if heading_title_entries:
                    heading_title_rows += 1
                if heading_underline_entries:
                    heading_underline_rows += 1
                if atx_heading_entries:
                    atx_heading_rows += 1
                if setext_heading_entries:
                    setext_heading_rows += 1
                if h1_heading_entries:
                    h1_heading_rows += 1
                if h2_heading_entries:
                    h2_heading_rows += 1
                if h3_heading_entries:
                    h3_heading_rows += 1
                if h4_heading_entries:
                    h4_heading_rows += 1
                if h5_heading_entries:
                    h5_heading_rows += 1
                if h6_heading_entries:
                    h6_heading_rows += 1
                if explicit_fragment_heading_entries:
                    explicit_fragment_heading_rows += 1
                if auto_fragment_heading_entries:
                    auto_fragment_heading_rows += 1
                for entry in heading_entries:
                    role = str(entry.get("role", "") or "")
                    source_kind = str(entry.get("source_kind", "") or "")
                    level = int(entry.get("level", 0) or 0)
                    if role == "title":
                        heading_title_entry_count += 1
                    elif role == "underline":
                        heading_underline_entry_count += 1
                    if source_kind == "atx":
                        atx_heading_entry_count += 1
                    elif source_kind == "setext":
                        setext_heading_entry_count += 1
                    if level == 1:
                        h1_heading_entry_count += 1
                    elif level == 2:
                        h2_heading_entry_count += 1
                    elif level == 3:
                        h3_heading_entry_count += 1
                    elif level == 4:
                        h4_heading_entry_count += 1
                    elif level == 5:
                        h5_heading_entry_count += 1
                    elif level == 6:
                        h6_heading_entry_count += 1
                    frag_source = str(entry.get("fragment_source", "") or "")
                    if frag_source == "explicit":
                        explicit_fragment_heading_entry_count += 1
                    elif frag_source == "auto":
                        auto_fragment_heading_entry_count += 1
            if section_entry:
                section_rows += 1
                path = str(section_entry.get("path", "") or "")
                if path:
                    visible_section_paths.add(path)
            if definition_entries:
                definition_rows += 1
                definition_entry_count += int(len(definition_entries))
                if reference_definition_entries:
                    reference_definition_rows += 1
                if reference_definition_cont_entries:
                    reference_definition_cont_rows += 1
                if footnote_definition_entries:
                    footnote_definition_rows += 1
                if footnote_definition_cont_entries:
                    footnote_definition_cont_rows += 1
                for entry in definition_entries:
                    kind = str(entry.get("kind", "") or "")
                    if kind == "reference-definition":
                        reference_definition_entry_count += 1
                    elif kind == "reference-definition-cont":
                        reference_definition_cont_entry_count += 1
                    elif kind == "footnote-definition":
                        footnote_definition_entry_count += 1
                    elif kind == "footnote-definition-cont":
                        footnote_definition_cont_entry_count += 1
            if block_entries:
                block_rows += 1
                block_entry_count += int(len(block_entries))
                if fenced_code_entries:
                    fenced_code_rows += 1
                if backtick_fenced_code_entries:
                    backtick_fenced_code_rows += 1
                if tilde_fenced_code_entries:
                    tilde_fenced_code_rows += 1
                if language_fenced_code_entries:
                    language_fenced_code_rows += 1
                if bare_fenced_code_entries:
                    bare_fenced_code_rows += 1
                if fenced_code_opener_entries:
                    fenced_code_opener_rows += 1
                if fenced_code_body_entries:
                    fenced_code_body_rows += 1
                if fenced_code_closer_entries:
                    fenced_code_closer_rows += 1
                if html_block_entries:
                    html_block_rows += 1
                if indented_code_entries:
                    indented_code_rows += 1
                for entry in block_entries:
                    kind = str(entry.get("kind", "") or "")
                    role = str(entry.get("role", "") or "")
                    if kind == "fenced-code":
                        fenced_code_entry_count += 1
                        marker_kind = str(entry.get("marker_kind", "") or "")
                        if marker_kind == "backtick":
                            backtick_fenced_code_count += 1
                        elif marker_kind == "tilde":
                            tilde_fenced_code_count += 1
                        if int(entry.get("has_language", 0) or 0) == 1:
                            language_fenced_code_count += 1
                        else:
                            bare_fenced_code_count += 1
                        if role == "opener":
                            fenced_code_opener_entry_count += 1
                        elif role == "body":
                            fenced_code_body_entry_count += 1
                        elif role == "closer":
                            fenced_code_closer_entry_count += 1
                    elif kind == "html-block":
                        html_block_entry_count += 1
                    elif kind == "indented-code":
                        indented_code_entry_count += 1
            rows.append(row_entry)

        out.update(
            {
                "rows": rows,
                "row_count": int(len(rows)),
                "cue_rows": int(cue_rows),
                "link_rows": int(link_rows),
                "link_entry_count": int(link_entry_count),
                "local_doc_link_rows": int(local_doc_link_rows),
                "fragment_link_rows": int(fragment_link_rows),
                "external_link_rows": int(external_link_rows),
                "footnote_link_rows": int(footnote_link_rows),
                "inline_link_rows": int(inline_link_rows),
                "reference_link_rows": int(reference_link_rows),
                "full_reference_link_rows": int(full_reference_link_rows),
                "collapsed_reference_link_rows": int(collapsed_reference_link_rows),
                "shortcut_reference_link_rows": int(shortcut_reference_link_rows),
                "autolink_rows": int(autolink_rows),
                "footnote_ref_rows": int(footnote_ref_rows),
                "local_doc_link_count": int(local_doc_link_count),
                "fragment_link_count": int(fragment_link_count),
                "external_link_count": int(external_link_count),
                "footnote_link_count": int(footnote_link_count),
                "inline_link_count": int(inline_link_count),
                "reference_link_count": int(reference_link_count),
                "full_reference_link_count": int(full_reference_link_count),
                "collapsed_reference_link_count": int(collapsed_reference_link_count),
                "shortcut_reference_link_count": int(shortcut_reference_link_count),
                "autolink_count": int(autolink_count),
                "footnote_ref_count": int(footnote_ref_count),
                "image_rows": int(image_rows),
                "image_entry_count": int(image_entry_count),
                "inline_image_rows": int(inline_image_rows),
                "reference_image_rows": int(reference_image_rows),
                "full_reference_image_rows": int(full_reference_image_rows),
                "collapsed_reference_image_rows": int(collapsed_reference_image_rows),
                "shortcut_reference_image_rows": int(shortcut_reference_image_rows),
                "local_doc_image_rows": int(local_doc_image_rows),
                "fragment_image_rows": int(fragment_image_rows),
                "external_image_rows": int(external_image_rows),
                "footnote_image_rows": int(footnote_image_rows),
                "inline_image_count": int(inline_image_count),
                "reference_image_count": int(reference_image_count),
                "full_reference_image_count": int(full_reference_image_count),
                "collapsed_reference_image_count": int(collapsed_reference_image_count),
                "shortcut_reference_image_count": int(shortcut_reference_image_count),
                "local_doc_image_count": int(local_doc_image_count),
                "fragment_image_count": int(fragment_image_count),
                "external_image_count": int(external_image_count),
                "footnote_image_count": int(footnote_image_count),
                "code_rows": int(code_rows),
                "code_entry_count": int(code_entry_count),
                "single_backtick_code_rows": int(single_backtick_code_rows),
                "multi_backtick_code_rows": int(multi_backtick_code_rows),
                "single_backtick_code_count": int(single_backtick_code_count),
                "multi_backtick_code_count": int(multi_backtick_code_count),
                "markup_rows": int(markup_rows),
                "markup_entry_count": int(markup_entry_count),
                "strong_markup_rows": int(strong_markup_rows),
                "emphasis_markup_rows": int(emphasis_markup_rows),
                "strike_markup_rows": int(strike_markup_rows),
                "asterisk_markup_rows": int(asterisk_markup_rows),
                "underscore_markup_rows": int(underscore_markup_rows),
                "tilde_markup_rows": int(tilde_markup_rows),
                "strong_entry_count": int(strong_entry_count),
                "emphasis_entry_count": int(emphasis_entry_count),
                "strike_entry_count": int(strike_entry_count),
                "asterisk_markup_count": int(asterisk_markup_count),
                "underscore_markup_count": int(underscore_markup_count),
                "tilde_markup_count": int(tilde_markup_count),
                "table_rows": int(table_rows),
                "table_entry_count": int(table_entry_count),
                "table_header_rows": int(table_header_rows),
                "table_body_rows": int(table_body_rows),
                "table_delimiter_rows": int(table_delimiter_rows),
                "default_aligned_table_rows": int(default_aligned_table_rows),
                "left_aligned_table_rows": int(left_aligned_table_rows),
                "center_aligned_table_rows": int(center_aligned_table_rows),
                "right_aligned_table_rows": int(right_aligned_table_rows),
                "table_header_cell_count": int(table_header_cell_count),
                "table_body_cell_count": int(table_body_cell_count),
                "table_delimiter_cell_count": int(table_delimiter_cell_count),
                "default_aligned_table_entry_count": int(default_aligned_table_entry_count),
                "left_aligned_table_entry_count": int(left_aligned_table_entry_count),
                "center_aligned_table_entry_count": int(center_aligned_table_entry_count),
                "right_aligned_table_entry_count": int(right_aligned_table_entry_count),
                "structure_rows": int(structure_rows),
                "structure_entry_count": int(structure_entry_count),
                "list_rows": int(list_rows),
                "list_entry_count": int(list_entry_count),
                "bullet_list_rows": int(bullet_list_rows),
                "ordered_list_rows": int(ordered_list_rows),
                "bullet_list_entry_count": int(bullet_list_entry_count),
                "ordered_list_entry_count": int(ordered_list_entry_count),
                "task_rows": int(task_rows),
                "task_entry_count": int(task_entry_count),
                "checked_task_rows": int(checked_task_rows),
                "unchecked_task_rows": int(unchecked_task_rows),
                "checked_task_entry_count": int(checked_task_entry_count),
                "unchecked_task_entry_count": int(unchecked_task_entry_count),
                "bullet_task_rows": int(bullet_task_rows),
                "ordered_task_rows": int(ordered_task_rows),
                "bullet_task_entry_count": int(bullet_task_entry_count),
                "ordered_task_entry_count": int(ordered_task_entry_count),
                "blockquote_rows": int(blockquote_rows),
                "blockquote_entry_count": int(blockquote_entry_count),
                "blockquote_alert_rows": int(blockquote_alert_rows),
                "blockquote_alert_entry_count": int(blockquote_alert_entry_count),
                "note_blockquote_alert_rows": int(note_blockquote_alert_rows),
                "tip_blockquote_alert_rows": int(tip_blockquote_alert_rows),
                "important_blockquote_alert_rows": int(important_blockquote_alert_rows),
                "warning_blockquote_alert_rows": int(warning_blockquote_alert_rows),
                "caution_blockquote_alert_rows": int(caution_blockquote_alert_rows),
                "note_blockquote_alert_entry_count": int(note_blockquote_alert_entry_count),
                "tip_blockquote_alert_entry_count": int(tip_blockquote_alert_entry_count),
                "important_blockquote_alert_entry_count": int(important_blockquote_alert_entry_count),
                "warning_blockquote_alert_entry_count": int(warning_blockquote_alert_entry_count),
                "caution_blockquote_alert_entry_count": int(caution_blockquote_alert_entry_count),
                "thematic_break_rows": int(thematic_break_rows),
                "thematic_break_entry_count": int(thematic_break_entry_count),
                "heading_rows": int(heading_rows),
                "heading_entry_count": int(heading_entry_count),
                "heading_title_rows": int(heading_title_rows),
                "heading_underline_rows": int(heading_underline_rows),
                "atx_heading_rows": int(atx_heading_rows),
                "setext_heading_rows": int(setext_heading_rows),
                "h1_heading_rows": int(h1_heading_rows),
                "h2_heading_rows": int(h2_heading_rows),
                "h3_heading_rows": int(h3_heading_rows),
                "h4_heading_rows": int(h4_heading_rows),
                "h5_heading_rows": int(h5_heading_rows),
                "h6_heading_rows": int(h6_heading_rows),
                "explicit_fragment_heading_rows": int(explicit_fragment_heading_rows),
                "auto_fragment_heading_rows": int(auto_fragment_heading_rows),
                "heading_title_entry_count": int(heading_title_entry_count),
                "heading_underline_entry_count": int(heading_underline_entry_count),
                "atx_heading_entry_count": int(atx_heading_entry_count),
                "setext_heading_entry_count": int(setext_heading_entry_count),
                "h1_heading_entry_count": int(h1_heading_entry_count),
                "h2_heading_entry_count": int(h2_heading_entry_count),
                "h3_heading_entry_count": int(h3_heading_entry_count),
                "h4_heading_entry_count": int(h4_heading_entry_count),
                "h5_heading_entry_count": int(h5_heading_entry_count),
                "h6_heading_entry_count": int(h6_heading_entry_count),
                "explicit_fragment_heading_entry_count": int(explicit_fragment_heading_entry_count),
                "auto_fragment_heading_entry_count": int(auto_fragment_heading_entry_count),
                "section_rows": int(section_rows),
                "section_distinct_count": int(len(visible_section_paths)),
                "definition_rows": int(definition_rows),
                "definition_entry_count": int(definition_entry_count),
                "reference_definition_rows": int(reference_definition_rows),
                "reference_definition_cont_rows": int(reference_definition_cont_rows),
                "footnote_definition_rows": int(footnote_definition_rows),
                "footnote_definition_cont_rows": int(footnote_definition_cont_rows),
                "reference_definition_entry_count": int(reference_definition_entry_count),
                "reference_definition_cont_entry_count": int(reference_definition_cont_entry_count),
                "footnote_definition_entry_count": int(footnote_definition_entry_count),
                "footnote_definition_cont_entry_count": int(footnote_definition_cont_entry_count),
                "block_rows": int(block_rows),
                "block_entry_count": int(block_entry_count),
                "backtick_fenced_code_rows": int(backtick_fenced_code_rows),
                "tilde_fenced_code_rows": int(tilde_fenced_code_rows),
                "language_fenced_code_rows": int(language_fenced_code_rows),
                "bare_fenced_code_rows": int(bare_fenced_code_rows),
                "backtick_fenced_code_count": int(backtick_fenced_code_count),
                "tilde_fenced_code_count": int(tilde_fenced_code_count),
                "language_fenced_code_count": int(language_fenced_code_count),
                "bare_fenced_code_count": int(bare_fenced_code_count),
                "fenced_code_rows": int(fenced_code_rows),
                "fenced_code_opener_rows": int(fenced_code_opener_rows),
                "fenced_code_body_rows": int(fenced_code_body_rows),
                "fenced_code_closer_rows": int(fenced_code_closer_rows),
                "html_block_rows": int(html_block_rows),
                "indented_code_rows": int(indented_code_rows),
                "fenced_code_entry_count": int(fenced_code_entry_count),
                "fenced_code_opener_entry_count": int(fenced_code_opener_entry_count),
                "fenced_code_body_entry_count": int(fenced_code_body_entry_count),
                "fenced_code_closer_entry_count": int(fenced_code_closer_entry_count),
                "html_block_entry_count": int(html_block_entry_count),
                "indented_code_entry_count": int(indented_code_entry_count),
                "literal_rows": int(literal_rows),
                "literal_entry_count": int(literal_entry_count),
                "raw_html_rows": int(raw_html_rows),
                "escaped_markdown_rows": int(escaped_markdown_rows),
                "raw_html_entry_count": int(raw_html_entry_count),
                "escaped_markdown_entry_count": int(escaped_markdown_entry_count),
            }
        )
        return out

    def docs_cues_model(self, lines: int, cols: int) -> dict[str, Any]:
        """Return shared visible docs/help scanability spans for one screen.

        Future UIs, tests, scripts, and LLM handoffs can inspect the same tiny
        markdown-ish heading/link/list/blockquote/table cues the reference TUI
        paints for docs/help buffers without scraping curses attributes or
        re-parsing those visible row fragments themselves.
        """

        h = max(0, int(lines))
        w = max(0, int(cols))
        layout = dict(self.screen_layout_model(lines=h, cols=w))
        window = dict(self.edit_window_model(lines=h, cols=w))
        layout = dict(window)
        layout.setdefault("lines", h)
        layout.setdefault("cols", w)
        return self._docs_cues_model_from_parts(
            lines=h,
            cols=w,
            layout=layout,
            window=window,
        )

    def prompt_panel_model(self, lines: int, cols: int) -> dict[str, Any]:
        """Return the shared visible picker-panel model for one screen size.

        This lifts the remaining reference-TUI prompt-panel truth into one
        inspectable editor-side snapshot: if a picker-style prompt currently has
        visible suggestion rows, the model reports the reserved panel geometry
        plus the rendered visible entries with stable screen positions.

        Future UIs, scripts, tests, and LLMs can inspect the same picker panel
        the curses TUI paints without recomputing suggestion height, sticky
        headers, more markers, or row placement from several smaller helpers.
        """

        h = max(0, int(lines))
        w = max(0, int(cols))
        layout = dict(self.screen_layout_model(lines=h, cols=w))
        sug_h = int(layout.get("suggestions_height", 0) or 0)
        sug_y = int(layout.get("suggestions_y", 0) or 0)
        sug_w = int(layout.get("suggestions_width", 0) or 0)
        prompt = self.prompt
        kind = "" if prompt is None else str(prompt.kind or "")
        out: dict[str, Any] = {
            "active": 0,
            "kind": kind,
            "lines": h,
            "cols": w,
            "y": int(sug_y),
            "x": 0,
            "width": int(max(0, sug_w)),
            "screen_width": int(w),
            "height": int(max(0, sug_h)),
            "entries": [],
            "row_count": 0,
        }
        if prompt is None or kind in ("command", "find") or sug_h <= 0 or sug_w <= 0:
            return out
        if not prompt.suggestion_rows:
            return out

        entries: list[dict[str, Any]] = []
        for idx, row in enumerate(self.prompt_display_model(max_lines=sug_h, width=sug_w)):
            if not isinstance(row, dict):
                continue
            ent = dict(row)
            ent.setdefault("text", "")
            ent["screen_y"] = int(sug_y + idx)
            ent["screen_x"] = 0
            entries.append(ent)

        out.update(
            {
                "active": 1 if entries else 0,
                "entries": entries,
                "row_count": int(len(entries)),
            }
        )
        return out

    def edit_window_model(self, lines: int, cols: int) -> dict[str, Any]:
        """Return the shared reference edit-window model for a given screen.

        This lifts the remaining tiny curses-specific viewing truth into one
        inspectable editor-side snapshot: given a screen size, it applies the
        same reference layout reservation policy as the minimal TUI, syncs the
        viewport size/follow-cursor behavior, and reports the visible edit
        window rows plus the primary cursor's position within that window.

        Unlike `screen_layout_model(...)`, this is intentionally a *live view*
        snapshot: it may update the stored viewport size/origin the same way a
        real renderer would before painting.
        """

        layout = dict(self.screen_layout_model(lines=lines, cols=cols))
        view_h = int(layout.get("viewport_height", 0) or 0)
        view_w = int(layout.get("viewport_width", 0) or 0)
        out: dict[str, Any] = dict(layout)
        out.update(
            {
                "rows": [],
                "row_count": 0,
                "viewport": self.viewport_model(),
                "cursor": {
                    "view_y": 0,
                    "view_x": 0,
                    "screen_y": int(layout.get("viewport_y", 0) or 0),
                    "screen_x": int(layout.get("viewport_x", 0) or 0),
                    "visible": 0,
                },
                "softwrap": 0,
            }
        )
        if view_h <= 0 or view_w <= 0:
            return out

        self.set_viewport(height=view_h, width=view_w, follow_cursor=True)
        vp = self.viewport_model()
        eb = self.cur()
        softwrap = bool(self.options.get("softwrap", local=eb.local_options))
        rows = self.view_rows(height=view_h, width=view_w)
        row_models: list[dict[str, Any]] = []
        base_y = int(layout.get("viewport_y", 0) or 0)
        base_x = int(layout.get("viewport_x", 0) or 0)
        for view_y, (li, start_col, frag) in enumerate(rows):
            row_models.append(
                {
                    "view_y": int(view_y),
                    "screen_y": int(base_y + view_y),
                    "screen_x": int(base_x),
                    "line": int(li),
                    "start_col": int(start_col),
                    "text": str(frag),
                    "continuation": 1 if softwrap and int(start_col) > 0 else 0,
                }
            )

        cy, cx = self.cursor_view_pos(height=view_h, width=view_w)
        cursor_visible = 1 if 0 <= int(cy) < len(row_models) and 0 <= int(cx) < view_w else 0
        out.update(
            {
                "rows": row_models,
                "row_count": int(len(row_models)),
                "viewport": vp,
                "cursor": {
                    "view_y": int(cy),
                    "view_x": int(cx),
                    "screen_y": int(base_y + cy),
                    "screen_x": int(base_x + cx),
                    "visible": int(cursor_visible),
                },
                "softwrap": 1 if softwrap else 0,
            }
        )
        return out


    def _display_rows_model_from_parts(
        self,
        *,
        lines: int,
        cols: int,
        layout: dict[str, Any],
        window: dict[str, Any],
        prompt_panel: dict[str, Any],
        showchars_rows: dict[str, Any],
        viewport_rows: dict[str, Any],
    ) -> dict[str, Any]:
        """Return shared display-text screen rows from already-synced model parts."""

        h = max(0, int(lines))
        w = max(0, int(cols))
        out: dict[str, Any] = {
            "active": 0,
            "lines": h,
            "cols": w,
            "rows": [],
            "row_count": 0,
        }
        if h <= 0 or w <= 0:
            return out

        eb = self.cur()
        layout_rows = list(layout.get("bottom_rows", []) or [])
        bottom_rows_text = list(self.bottom_rows_model(w)) if w > 0 else []
        bottom_rows: list[dict[str, Any]] = []
        for idx, row in enumerate(bottom_rows_text):
            entry = dict(row)
            if idx < len(layout_rows):
                entry["y"] = int(layout_rows[idx].get("y", -1) or -1)
            else:
                entry["y"] = -1
            bottom_rows.append(entry)

        cursor = dict(window.get("cursor") or {})
        cursor.setdefault("visible", 0)
        cursor["mode"] = "edit"
        prompt_y = int(layout.get("prompt_y", -1) or -1)
        if prompt_y >= 0 and self.prompt is not None:
            prompt_cursor = max(0, int(self.status_model().get("prompt_cursor", 0) or 0))
            cursor = {
                "mode": "prompt",
                "screen_y": int(prompt_y),
                "screen_x": max(0, min(max(0, w - 1), 1 + prompt_cursor)),
                "visible": 1 if w > 0 and h > 0 else 0,
            }
        cursor_visible = bool(int(cursor.get("visible", 0) or 0))
        cursor_y = int(cursor.get("screen_y", -1) or -1)
        cursor_x = int(cursor.get("screen_x", -1) or -1)

        softwrap_enabled = bool(self.options.get("softwrap", local=eb.local_options))
        overflow_enabled = bool(self.options.get("overflowmarkers", local=eb.local_options))
        showchars_by_y = {
            int(row.get("screen_y", -1)): dict(row)
            for row in list(showchars_rows.get("rows") or [])
            if isinstance(row, dict)
        }
        viewport_by_y = {
            int(row.get("screen_y", -1)): dict(row)
            for row in list(viewport_rows.get("rows") or [])
            if isinstance(row, dict)
        }
        panel_by_y = {
            int(row.get("screen_y", -1)): dict(row)
            for row in list(prompt_panel.get("entries") or [])
            if isinstance(row, dict)
        }
        bottom_by_y = {
            int(row.get("y", -1)): dict(row)
            for row in list(bottom_rows or [])
            if isinstance(row, dict)
        }

        rows: list[dict[str, Any]] = []
        for y in range(int(h)):
            text = ""
            entry: dict[str, Any] = {
                "screen_y": int(y),
                "screen_x": 0,
                "width": int(w),
                "kind": "blank",
                "text": text,
                "raw_text": text,
                "display_changed": 0,
                "empty": 1,
                "cursor_here": 1 if cursor_visible and int(y) == int(cursor_y) else 0,
                "cursor_x": int(cursor_x) if cursor_visible and int(y) == int(cursor_y) else -1,
            }
            vp = viewport_by_y.get(int(y))
            if vp is not None:
                frag = str(vp.get("text", "") or "")
                line_index = int(vp["line"]) if "line" in vp else -1
                start_col = int(vp.get("start_col", 0) or 0)
                view_w = int(vp.get("text_width", layout.get("viewport_width", 0) or 0) or 0)
                left_text = str(vp.get("left_text", "") or "")
                right_text = str(vp.get("right_text", "") or "")
                right_w = int(vp.get("right_width", 0) or 0)
                right_fill = right_text if right_text else ((" " * int(right_w)) if right_w > 0 else "")
                raw_text = str(vp.get("combined_text", "") or "")[: int(w)]
                showchars_model = dict(showchars_by_y.get(int(y), {}))
                display_frag0 = str(showchars_model.get("display_text", frag) or frag)
                line_text = str(eb.buf.lines[line_index]) if 0 <= int(line_index) < len(eb.buf.lines) else str(frag)
                display_frag, overflow_cells = render_overflow_fragment(
                    line_text,
                    frag_start=int(start_col),
                    frag_text=display_frag0,
                    view_width=int(view_w),
                    softwrap=softwrap_enabled or not overflow_enabled,
                )
                display_area = str(display_frag).ljust(max(0, int(view_w)))
                text = (left_text + display_area + right_fill).rstrip()[: int(w)]
                entry.update(
                    {
                        "kind": "viewport",
                        "text": text,
                        "raw_text": raw_text,
                        "display_changed": 1 if text != raw_text else 0,
                        "empty": 0 if vp and text else 1,
                        "view_y": int(vp.get("view_y", 0) or 0),
                        "line": int(line_index),
                        "has_line": int(vp.get("has_line", 0) or 0),
                        "start_col": int(start_col),
                        "continuation": int(vp.get("continuation", 0) or 0),
                        "viewport_text": frag,
                        "viewport_display_text": str(display_frag),
                        "overflow_cells": [[int(pos), str(ch)] for pos, ch in overflow_cells],
                        "overflow_count": int(len(overflow_cells)),
                        "overflow_left": 1 if any(int(pos) == 0 and str(ch) == '<' for pos, ch in overflow_cells) else 0,
                        "overflow_right": 1 if any(str(ch) == '>' for _, ch in overflow_cells) else 0,
                    }
                )
            panel = panel_by_y.get(int(y))
            if panel is not None:
                text = str(panel.get("text", "") or "")[: int(w)]
                entry.update(
                    {
                        "kind": "prompt-panel",
                        "text": text,
                        "raw_text": text,
                        "display_changed": 0,
                        "empty": 0 if text else 1,
                        "type": str(panel.get("type", "") or ""),
                        "row_kind": str(panel.get("row_kind", "") or ""),
                        "selected": int(panel.get("selected", 0) or 0),
                    }
                )
            bottom = bottom_by_y.get(int(y))
            if bottom is not None:
                text = str(bottom.get("text", "") or "")[: int(w)]
                entry.update(
                    {
                        "kind": str(bottom.get("kind", "bottom") or "bottom"),
                        "slot": str(bottom.get("slot", "") or ""),
                        "text": text,
                        "raw_text": text,
                        "display_changed": 0,
                        "empty": 0 if text else 1,
                    }
                )
            rows.append(entry)

        out.update(
            {
                "active": 1 if rows else 0,
                "rows": rows,
                "row_count": int(len(rows)),
            }
        )
        return out

    def display_rows_model(self, lines: int, cols: int) -> dict[str, Any]:
        """Return the shared display-text screen rows for one visible snapshot.

        This is the painted-text sibling of ``screen_rows_model(...)``: future
        UIs, tests, scripts, and LLM handoffs can inspect the same plain row
        text the reference curses TUI draws after tiny ``showchars`` and
        overflow-marker policy are applied, without scraping curses output or
        redoing row-overlay logic by hand.
        """

        h = max(0, int(lines))
        w = max(0, int(cols))
        if h <= 0 or w <= 0:
            return {"active": 0, "lines": h, "cols": w, "rows": [], "row_count": 0}

        layout = dict(self.screen_layout_model(lines=h, cols=w))
        window = dict(self.edit_window_model(lines=h, cols=w))
        layout = dict(window)
        layout.setdefault("lines", h)
        layout.setdefault("cols", w)
        prompt_panel = dict(self.prompt_panel_model(lines=h, cols=w))
        gutter = dict(self.gutter_model(lines=h, cols=w))
        showchars_rows = dict(
            self._showchars_rows_model_from_window(
                lines=h,
                cols=w,
                layout=layout,
                window=window,
            )
        )
        viewport_rows = dict(
            self._viewport_rows_model_from_parts(
                lines=h,
                cols=w,
                layout=layout,
                window=window,
                gutter=gutter,
            )
        )
        return self._display_rows_model_from_parts(
            lines=h,
            cols=w,
            layout=layout,
            window=window,
            prompt_panel=prompt_panel,
            showchars_rows=showchars_rows,
            viewport_rows=viewport_rows,
        )

    def screen_rows_model(self, lines: int, cols: int) -> dict[str, Any]:
        """Return the shared plain-text screen rows for one visible snapshot.

        This flattens the composed visible screen into ordered row maps so
        future UIs, tests, scripts, and LLM handoffs can ask the boring but
        practical question "what plain text is on screen right now?" without
        scraping curses output or manually overlaying viewport rows, picker
        rows, and bottom chrome by hand.
        """

        h = max(0, int(lines))
        w = max(0, int(cols))
        out: dict[str, Any] = {
            "active": 0,
            "lines": h,
            "cols": w,
            "rows": [],
            "row_count": 0,
        }
        if h <= 0 or w <= 0:
            return out

        layout = dict(self.screen_layout_model(lines=h, cols=w))
        window = dict(self.edit_window_model(lines=h, cols=w))
        layout = dict(window)
        layout.setdefault("lines", h)
        layout.setdefault("cols", w)
        prompt_panel = dict(self.prompt_panel_model(lines=h, cols=w))
        gutter = dict(self.gutter_model(lines=h, cols=w))
        viewport_rows = dict(
            self._viewport_rows_model_from_parts(
                lines=h,
                cols=w,
                layout=layout,
                window=window,
                gutter=gutter,
            )
        )
        layout_rows = list(layout.get("bottom_rows", []) or [])
        bottom_rows_text = list(self.bottom_rows_model(w)) if w > 0 else []
        bottom_rows: list[dict[str, Any]] = []
        for idx, row in enumerate(bottom_rows_text):
            entry = dict(row)
            if idx < len(layout_rows):
                entry["y"] = int(layout_rows[idx].get("y", -1) or -1)
            else:
                entry["y"] = -1
            bottom_rows.append(entry)

        cursor = dict(window.get("cursor") or {})
        cursor.setdefault("visible", 0)
        cursor["mode"] = "edit"
        prompt_y = int(layout.get("prompt_y", -1) or -1)
        if prompt_y >= 0 and self.prompt is not None:
            prompt_cursor = max(0, int(self.status_model().get("prompt_cursor", 0) or 0))
            cursor = {
                "mode": "prompt",
                "screen_y": int(prompt_y),
                "screen_x": max(0, min(max(0, w - 1), 1 + prompt_cursor)),
                "visible": 1 if w > 0 and h > 0 else 0,
            }
        cursor_visible = bool(int(cursor.get("visible", 0) or 0))
        cursor_y = int(cursor.get("screen_y", -1) or -1)
        cursor_x = int(cursor.get("screen_x", -1) or -1)

        viewport_by_y = {
            int(row.get("screen_y", -1)): dict(row)
            for row in list(viewport_rows.get("rows") or [])
            if isinstance(row, dict)
        }
        panel_by_y = {
            int(row.get("screen_y", -1)): dict(row)
            for row in list(prompt_panel.get("entries") or [])
            if isinstance(row, dict)
        }
        bottom_by_y = {
            int(row.get("y", -1)): dict(row)
            for row in list(bottom_rows or [])
            if isinstance(row, dict)
        }

        rows: list[dict[str, Any]] = []
        for y in range(int(h)):
            text = ""
            kind = "blank"
            entry: dict[str, Any] = {
                "screen_y": int(y),
                "screen_x": 0,
                "width": int(w),
                "kind": kind,
                "text": text,
                "empty": 1,
                "cursor_here": 1 if cursor_visible and int(y) == int(cursor_y) else 0,
                "cursor_x": int(cursor_x) if cursor_visible and int(y) == int(cursor_y) else -1,
            }
            vp = viewport_by_y.get(int(y))
            if vp is not None:
                text = str(vp.get("combined_text", "") or "")[: int(w)]
                entry.update(
                    {
                        "kind": "viewport",
                        "text": text,
                        "empty": 0 if vp and text else 1,
                        "view_y": int(vp.get("view_y", 0) or 0),
                        "line": int(vp["line"]) if "line" in vp else -1,
                        "has_line": int(vp.get("has_line", 0) or 0),
                        "start_col": int(vp.get("start_col", 0) or 0),
                        "continuation": int(vp.get("continuation", 0) or 0),
                    }
                )
            panel = panel_by_y.get(int(y))
            if panel is not None:
                text = str(panel.get("text", "") or "")[: int(w)]
                entry.update(
                    {
                        "kind": "prompt-panel",
                        "text": text,
                        "empty": 0 if text else 1,
                        "type": str(panel.get("type", "") or ""),
                        "row_kind": str(panel.get("row_kind", "") or ""),
                        "selected": int(panel.get("selected", 0) or 0),
                    }
                )
            bottom = bottom_by_y.get(int(y))
            if bottom is not None:
                text = str(bottom.get("text", "") or "")[: int(w)]
                entry.update(
                    {
                        "kind": str(bottom.get("kind", "bottom") or "bottom"),
                        "slot": str(bottom.get("slot", "") or ""),
                        "text": text,
                        "empty": 0 if text else 1,
                    }
                )
            rows.append(entry)

        out.update(
            {
                "active": 1 if rows else 0,
                "rows": rows,
                "row_count": int(len(rows)),
            }
        )
        return out

    def screen_model(self, lines: int, cols: int) -> dict[str, Any]:
        """Return one shared visible-screen snapshot for the reference TUI.

        This is a tiny composition helper layered on top of the existing shared
        layout/edit-window/prompt-panel/bottom-row models. It gives future UIs,
        tests, scripts, and LLMs one inspectable map for "what is on screen
        now?" without forcing them to stitch together geometry, visible edit
        rows, prompt suggestions, bottom-row text, and active cursor placement
        by hand.
        """

        h = max(0, int(lines))
        w = max(0, int(cols))
        layout = dict(self.screen_layout_model(lines=h, cols=w))
        window = dict(self.edit_window_model(lines=h, cols=w))
        layout = dict(window)
        layout.setdefault("lines", h)
        layout.setdefault("cols", w)

        prompt_panel = dict(self.prompt_panel_model(lines=h, cols=w))
        gutter = dict(self.gutter_model(lines=h, cols=w))
        search_rows = dict(
            self._search_rows_model_from_window(
                lines=h,
                cols=w,
                layout=layout,
                window=window,
            )
        )
        showchars_rows = dict(
            self._showchars_rows_model_from_window(
                lines=h,
                cols=w,
                layout=layout,
                window=window,
            )
        )
        viewport_rows = dict(
            self._viewport_rows_model_from_parts(
                lines=h,
                cols=w,
                layout=layout,
                window=window,
                gutter=gutter,
            )
        )
        viewport_cues = dict(
            self._viewport_cues_model_from_parts(
                lines=h,
                cols=w,
                layout=layout,
                window=window,
                search_rows=search_rows,
                showchars_rows=showchars_rows,
            )
        )
        docs_cues = dict(
            self._docs_cues_model_from_parts(
                lines=h,
                cols=w,
                layout=layout,
                window=window,
            )
        )
        display_rows = dict(
            self._display_rows_model_from_parts(
                lines=h,
                cols=w,
                layout=layout,
                window=window,
                prompt_panel=prompt_panel,
                showchars_rows=showchars_rows,
                viewport_rows=viewport_rows,
            )
        )
        layout_rows = list(layout.get("bottom_rows", []) or [])
        bottom_rows_text = list(self.bottom_rows_model(w)) if w > 0 else []
        bottom_rows: list[dict[str, Any]] = []
        for idx, row in enumerate(bottom_rows_text):
            entry = dict(row)
            if idx < len(layout_rows):
                entry["y"] = int(layout_rows[idx].get("y", -1) or -1)
            else:
                entry["y"] = -1
            bottom_rows.append(entry)

        cursor = dict(window.get("cursor") or {})
        cursor.setdefault("visible", 0)
        cursor["mode"] = "edit"
        prompt_y = int(layout.get("prompt_y", -1) or -1)
        if prompt_y >= 0 and self.prompt is not None:
            prompt_cursor = max(0, int(self.status_model().get("prompt_cursor", 0) or 0))
            cursor = {
                "mode": "prompt",
                "screen_y": int(prompt_y),
                "screen_x": max(0, min(max(0, w - 1), 1 + prompt_cursor)),
                "visible": 1 if w > 0 and h > 0 else 0,
            }

        out = {
            "lines": h,
            "cols": w,
            "layout": layout,
            "gutter": gutter,
            "search_rows": search_rows,
            "showchars_rows": showchars_rows,
            "viewport_rows": viewport_rows,
            "viewport_cues": viewport_cues,
            "docs_cues": docs_cues,
            "display_rows": display_rows,
            "edit_window": window,
            "prompt_panel": prompt_panel,
            "bottom_rows": bottom_rows,
            "bottom_rows_count": int(len(bottom_rows)),
            "cursor": cursor,
        }
        out["screen_rows"] = self.screen_rows_model(lines=h, cols=w)
        return out

    def bottom_rows_model(self, width: int) -> list[dict[str, Any]]:
        """Return the currently visible bottom-row chrome as ordered row maps.

        The list is ordered top-to-bottom exactly as the minimal curses TUI will
        paint the visible bottom rows. This keeps the editor-side contract tiny
        but useful for future renderers, scripts, tests, and LLM handoffs: they
        can inspect the active keymenu/interaction/infobar/statusline stack
        directly instead of rebuilding it from scattered options and renderer
        helpers.
        """

        w = max(0, int(width))
        if w <= 0:
            return []

        eb = self.cur()
        rows: list[dict[str, Any]] = []
        keymenu = self.keymenu_model(w)
        if int(keymenu.get("active", 0) or 0):
            rows.append(
                {
                    "kind": "keymenu",
                    "slot": "help",
                    "text": str(keymenu.get("text", "") or ""),
                }
            )

        interaction = self.interaction_model(w)
        if int(interaction.get("active", 0) or 0):
            rows.append(
                {
                    "kind": "interaction",
                    "slot": "prompt",
                    "text": str(interaction.get("text", "") or ""),
                }
            )
        else:
            infobar = self.infobar_model(w)
            if int(infobar.get("active", 0) or 0):
                rows.append(
                    {
                        "kind": "infobar",
                        "slot": "prompt",
                        "text": str(infobar.get("text", "") or ""),
                    }
                )

        if bool(self.options.get("statusline", local=eb.local_options)):
            rows.append(
                {
                    "kind": "statusline",
                    "slot": "status",
                    "text": self.statusline_text(w),
                }
            )
        return rows

    def display_file_name(self, eb: EditorBuffer | None = None) -> str:
        """Return the effective filename/status label for the active buffer.

        When `basename` is off, path-backed buffers prefer the full path so
        statusline/infobar-style views can mirror micro-esque behavior. Buffers
        without a path keep their ordinary buffer name.
        """

        eb = self.cur() if eb is None else eb
        path = str(eb.buf.path or "")
        if not path:
            return str(eb.name)
        if bool(self.options.get("basename", local=eb.local_options)):
            return str(Path(path).name or eb.name)
        return path

    def status_model(self) -> dict[str, Any]:
        """Return a small, portable statusline/infobar model.

        The goal is to let future UI layers render shared editor state without
        inventing semantics. Values are chosen to be easy for micromax scripts,
        tests, and future tooling to inspect directly.
        """

        eb = self.cur()
        self._normalize_cursor_lists(eb)
        c = eb.cursors[eb.primary]

        path = str(eb.buf.path or "")
        raw_file_name = Path(path).name if path else str(eb.name)
        display_name = self.display_file_name(eb)
        filetype = self.filetype()

        protected = bool(self.options.get("readonly", local=eb.local_options))

        # OS-level read-only status (file permissions). This is distinct from
        # "protected" buffers: you can still edit an unwritable file and then
        # `saveas` elsewhere, but protected buffers should reject edits.
        try:
            readonly_file = bool(path) and Path(path).exists() and (not Path(path).is_dir()) and (not os.access(Path(path), os.W_OK))
        except OSError:
            readonly_file = False
        readonly = bool(protected) or bool(readonly_file)

        selection_count = 0
        for i in range(len(eb.cursors)):
            sel = self.selection(i)
            if sel is not None and not sel.is_empty():
                selection_count += 1

        primary_sel = self.selection(None)
        primary_sel_chars = 0
        if primary_sel is not None and not primary_sel.is_empty():
            primary_sel_chars = len(self.selection_text(None))

        prompt_kind = self.prompt.kind if self.prompt is not None else ""
        prompt_text = self.prompt.text if self.prompt is not None else ""
        capture = self.capture_status_model()
        interaction = self.interaction_status_model()
        prompt_current_row = self.prompt_current_row()
        prompt_current_insert = prompt_current_row[0] if prompt_current_row else ""
        prompt_current_kind = prompt_current_row[1] if prompt_current_row else ""
        prompt_current_menu = prompt_current_row[2] if prompt_current_row else ""
        prompt_current_info = prompt_current_row[3] if prompt_current_row else ""
        prompt_pos = self.prompt_current_position()
        search_pos = self.search_position_model()
        buffer_names = self.buffer_names()
        try:
            buffer_index = int(buffer_names.index(str(self.active or ""))) + 1 if buffer_names else 0
        except ValueError:
            buffer_index = 0
        buffer_count = int(len(buffer_names))
        buffer_summary = f"{buffer_index}/{buffer_count}" if buffer_count > 0 else ""

        out: dict[str, Any] = {
            "mode": self.editor_mode(),
            "keymode": self.current_key_mode() or "",
            "keymode_once": 1 if self.current_key_mode_once() else 0,
            "keymode_capture": 1 if self.current_key_mode_capture() else 0,
            "buffer_name": str(eb.name),
            "file_name": str(raw_file_name),
            "display_name": str(display_name),
            "buffer_index": int(buffer_index),
            "buffer_count": int(buffer_count),
            "buffer_summary": str(buffer_summary),
            "filetype": str(filetype),
            "encoding": str(self.options.get("encoding", local=eb.local_options) or "utf-8"),
            "fileformat": str(self.options.get("fileformat", local=eb.local_options) or "unix"),
            "path": path,
            "cwd": str(Path.cwd()),
            "dirty": 1 if eb.buf.dirty else 0,
            "readonly": 1 if readonly else 0,
            "protected": 1 if protected else 0,
            "line": int(c.line),
            "col": int(c.col),
            "display_line": int(c.line) + 1,
            "display_col": int(c.col) + 1,
            "position": f"{int(c.line) + 1}:{int(c.col) + 1}",
            "line_count": int(len(eb.buf.lines)),
            "percentage": int((int(c.line) / max(1, int(len(eb.buf.lines)) - 1)) * 100),
            "cursor_count": int(len(eb.cursors)),
            "primary_cursor_index": int(eb.primary),
            "cursor_summary": f"{int(eb.primary) + 1}/{int(len(eb.cursors))}",
            "selection_count": int(selection_count),
            "selection_summary": str(int(selection_count)),
            "primary_selection_chars": int(primary_sel_chars),
            "prompt_kind": str(prompt_kind),
            "prompt_text": str(prompt_text),
            "prompt_cursor": int(self.prompt.cursor) if self.prompt is not None else 0,

            "viewport_top_line": int(self.viewport_top_line),
            "viewport_left_col": int(self.viewport_left_col),
            "viewport_height": int(self.viewport_height),
            "viewport_width": int(self.viewport_width),
            "display_viewport_top_line": int(self.viewport_top_line) + 1,
            "display_viewport_left_col": int(self.viewport_left_col) + 1,
            "prompt_current_insert": str(prompt_current_insert),
            "prompt_current_kind": str(prompt_current_kind),
            "prompt_current_menu": str(prompt_current_menu),
            "prompt_current_info": str(prompt_current_info),
            "prompt_current_section": self.prompt_current_section(),
            "prompt_current_preview": self.prompt_current_preview(),
            "prompt_index": int(prompt_pos.get("index", 0) or 0),
            "prompt_count": int(prompt_pos.get("count", 0) or 0),
            "prompt_section_index": int(prompt_pos.get("section_index", 0) or 0),
            "prompt_section_count": int(prompt_pos.get("section_count", 0) or 0),
            "prompt_position_summary": str(prompt_pos.get("summary", "") or ""),
            "search_query": str(search_pos.get("query", "") or ""),
            "search_literal": int(search_pos.get("literal", 0) or 0),
            "search_case_sensitive": int(search_pos.get("case_sensitive", 0) or 0),
            "search_match_index": int(search_pos.get("index", 0) or 0),
            "search_match_count": int(search_pos.get("count", 0) or 0),
            "search_summary": str(search_pos.get("summary", "") or ""),
            "last_message": str(self.messages[-1]) if self.messages else "",
            "macro_recording": 1 if self.macro_recording else 0,
            "macro_playing": 1 if self._macro_playing else 0,
            "macro_name": str(self._macro_target) if self.macro_recording else "",
        }
        out.update(capture)
        out.update(interaction)
        return out

    def status_summary(self) -> str:
        """Return a compact, deterministic status summary string.

        This is mainly for the headless REPL and `showstatus` command. UI layers
        should prefer `status_model()`.
        """

        st = self.status_model()
        parts = [
            f"mode={st['mode']}",
            f"buffer={str(st.get('display_name', st['file_name']))!r}",
            f"dirty={st['dirty']}",
            f"readonly={st['readonly']}",
            f"pos={st['position']}",
            f"cursors={int(st['primary_cursor_index']) + 1}/{st['cursor_count']}",
            f"sels={st['selection_count']}",
            f"selchars={st['primary_selection_chars']}",
        ]
        if st['keymode']:
            suffix = '!' if st.get('keymode_once') else ''
            parts.append(f"keymode={st['keymode']!r}{suffix}")
        if st['prompt_kind']:
            parts.append(f"prompt={st['prompt_kind']!r}")
        if int(st.get('buffer_count', 0) or 0) > 1 and st.get('buffer_summary'):
            parts.append(f"buf_pos={st['buffer_summary']!r}")
        if st.get('search_query') and st.get('search_summary'):
            parts.append(f"search_pos={st['search_summary']!r}")
        if st['prompt_kind'] not in ('', 'command', 'find') and st.get('prompt_position_summary'):
            parts.append(f"prompt_pos={st['prompt_position_summary']!r}")
        if st['prompt_kind'] not in ('', 'command', 'find') and st.get('prompt_current_preview'):
            parts.append(f"prompt_item={st['prompt_current_preview']!r}")
        if st.get('interaction_kind') and not st.get('capture_kind'):
            parts.append(f"interaction={st['interaction_kind']!r}")
            if st.get('interaction_position'):
                parts.append(f"interaction_pos={st['interaction_position']!r}")
            if st.get('interaction_detail'):
                parts.append(f"interaction_item={st['interaction_detail']!r}")
        if st.get('capture_kind'):
            parts.append(f"capture={st['capture_kind']!r}")
        if st.get('capture_progress'):
            parts.append(f"capture_pos={st['capture_progress']!r}")
        if st.get('capture_detail'):
            parts.append(f"capture_item={st['capture_detail']!r}")
        if st['macro_recording']:
            parts.append(f"macro=rec:{st['macro_name']!r}")
        if st['macro_playing']:
            parts.append("macro=play")
        return " ".join(parts)

    def statusline_model(self, width: int) -> dict[str, Any]:
        """Return a tiny shared layout model for the visible statusline row.

        The model intentionally stays text-first and inspectable: future
        UIs/scripts/LLMs can see the rendered left/right segments, truncation
        policy, and final padding without having to reverse-engineer the final
        one-line status string.
        """

        w = max(0, int(width))
        out: dict[str, Any] = {
            "active": 0,
            "width": w,
            "left_raw": "",
            "right_raw": "",
            "left": "",
            "right": "",
            "padding": "",
            "padding_width": 0,
            "truncated_left": 0,
            "truncated_right": 0,
            "text": "",
        }
        if w <= 0:
            return out

        if not bool(self.options.get("statusline", local=self.cur().local_options)):
            return out

        st = self.status_model()
        fmt_l = str(self.options.get("statusformatl", local=self.cur().local_options) or "")
        fmt_r = str(self.options.get("statusformatr", local=self.cur().local_options) or "")
        left_raw = render_status_template(fmt_l, ed=self, status=st)
        right_raw = render_status_template(fmt_r, ed=self, status=st).strip()
        left = left_raw
        right = right_raw
        truncated_left = 0
        truncated_right = 0

        # If the right side alone is too long, show the end (keeps mode/key hints).
        if len(right) >= w:
            right = right[-w:]
            truncated_right = 1 if right != right_raw else 0
            out.update(
                {
                    "active": 1,
                    "left_raw": left_raw,
                    "right_raw": right_raw,
                    "right": right,
                    "truncated_left": 1 if left_raw else 0,
                    "truncated_right": truncated_right,
                    "text": right,
                }
            )
            return out

        # Fit left + right into width, truncating left if needed.
        avail_left = w - len(right)
        if len(left) > avail_left:
            truncated_left = 1
            # Reserve at least one char if possible; add an ellipsis when truncating.
            if avail_left <= 0:
                left = ""
            elif avail_left == 1:
                left = left[:1]
            else:
                left = left[: max(0, avail_left - 1)] + "…"

        padding = " " * max(0, w - len(left) - len(right))
        text = (left + padding + right)[:w]
        out.update(
            {
                "active": 1,
                "left_raw": left_raw,
                "right_raw": right_raw,
                "left": left,
                "right": right,
                "padding": padding,
                "padding_width": len(padding),
                "truncated_left": truncated_left,
                "truncated_right": truncated_right,
                "text": text,
            }
        )
        return out

    def statusline_text(self, width: int) -> str:
        """Return a micro-esque single-line statusline string for the current viewport width.

        UI layers should generally prefer `status_model()` / `statusline_model()` for richer
        structure, but having a deterministic reference formatter is useful for the minimal TUI,
        REPL output, and tests.
        """
        return str(self.statusline_model(width).get("text", "") or "")

    # ----- prompt (command bar / find bar) -----
    def enter_prompt(self, kind: str, *, prefill: str = "") -> None:
        self.prompt = Prompt(kind=kind)
        self.prompt.prefill(prefill)
        self._push_prompt_keymode()

    def _palette_prompt_rows(self, query: str, *, limit: int = 40) -> list[list[str]]:
        q = str(query or "").strip()
        cap = max(1, int(limit))
        sections = self.command_palette_section_rows(q, limit=None)
        return self._flatten_grouped_prompt_sections(
            sections,
            limit=cap,
            browse_budget=(q == ""),
        )

    def _topic_prompt_rows(self, query: str, *, limit: int = 40) -> list[list[str]]:
        q = str(query or "").strip()
        cap = max(1, int(limit))
        sections = self.apropos_section_rows(q, limit=None) if q else self.help_topic_section_rows()
        return self._flatten_grouped_prompt_sections(
            sections,
            limit=cap,
            browse_budget=(q == ""),
        )

    def _binding_prompt_rows(self, query: str, *, limit: int = 40) -> list[list[str]]:
        q = str(query or "").strip()
        cap = max(1, int(limit))
        sections = self.binding_section_rows(q, limit=None)
        return self._flatten_grouped_prompt_sections(
            sections,
            limit=cap,
            browse_budget=(q == ""),
        )


    def _buffer_prompt_rows(self, query: str, *, limit: int = 40) -> list[list[str]]:
        q = str(query or "").strip()
        cap = max(1, int(limit))
        sections = self.buffer_section_rows(q, limit=None)
        return self._flatten_grouped_prompt_sections(
            sections,
            limit=cap,
            browse_budget=(q == ""),
        )

    def _mark_prompt_rows(self, query: str, *, limit: int = 40) -> list[list[str]]:
        q = str(query or "").strip()
        cap = max(1, int(limit))
        sections = self.mark_section_rows(q, limit=None)
        return self._flatten_grouped_prompt_sections(
            sections,
            limit=cap,
            browse_budget=(q == ""),
        )

    def _jump_prompt_rows(self, query: str, *, limit: int = 40) -> list[list[str]]:
        q = str(query or "").strip()
        cap = max(1, int(limit))
        sections = self.jump_section_rows(q, limit=None)
        return self._flatten_grouped_prompt_sections(
            sections,
            limit=cap,
            browse_budget=(q == ""),
        )

    def _plugin_prompt_rows(self, query: str, *, limit: int = 40) -> list[list[str]]:
        q = str(query or "").strip()
        cap = max(1, int(limit))
        sections = self.plugin_section_rows(q, limit=None)
        return self._flatten_grouped_prompt_sections(
            sections,
            limit=cap,
            browse_budget=(q == ""),
        )

    def _recent_prompt_rows(self, query: str, *, limit: int = 40) -> list[list[str]]:
        q = str(query or "").strip()
        cap = max(1, int(limit))
        sections = self._recent_section_rows(q, limit=None, by_project=True)
        return self._flatten_grouped_prompt_sections(
            sections,
            limit=cap,
            browse_budget=(q == ""),
        )

    def _recent_dir_prompt_rows(self, query: str, *, limit: int = 40) -> list[list[str]]:
        q = str(query or "").strip()
        cap = max(1, int(limit))
        sections = self._recent_section_rows(q, limit=None, by_project=False)
        return self._flatten_grouped_prompt_sections(
            sections,
            limit=cap,
            browse_budget=(q == ""),
        )

    def _refresh_buffer_prompt_suggestions(self, *, limit: int = 40) -> bool:
        if self.prompt is None or self.prompt.kind != "buffer":
            return False
        rows = self._buffer_prompt_rows(self.prompt.text, limit=limit)
        if not rows:
            return False
        cands = [str(row[0]) for row in rows]
        self.prompt.begin_suggestions(cands, start=0, end=len(self.prompt.text), rows=rows)
        return True

    def _refresh_mark_prompt_suggestions(self, *, limit: int = 40) -> bool:
        if self.prompt is None or self.prompt.kind != "mark":
            return False
        rows = self._mark_prompt_rows(self.prompt.text, limit=limit)
        if not rows:
            return False
        cands = [str(row[0]) for row in rows]
        self.prompt.begin_suggestions(cands, start=0, end=len(self.prompt.text), rows=rows)
        return True

    def _refresh_jump_prompt_suggestions(self, *, limit: int = 40) -> bool:
        if self.prompt is None or self.prompt.kind != "jump":
            return False
        rows = self._jump_prompt_rows(self.prompt.text, limit=limit)
        if not rows:
            return False
        cands = [str(row[0]) for row in rows]
        self.prompt.begin_suggestions(cands, start=0, end=len(self.prompt.text), rows=rows)
        return True

    def _refresh_plugin_prompt_suggestions(self, *, limit: int = 40) -> bool:
        if self.prompt is None or self.prompt.kind != "plugin":
            return False
        rows = self._plugin_prompt_rows(self.prompt.text, limit=limit)
        if not rows:
            return False
        cands = [str(row[0]) for row in rows]
        self.prompt.begin_suggestions(cands, start=0, end=len(self.prompt.text), rows=rows)
        return True

    def _refresh_recent_prompt_suggestions(self, *, limit: int = 40) -> bool:
        if self.prompt is None or self.prompt.kind != "recent":
            return False
        rows = self._recent_prompt_rows(self.prompt.text, limit=limit)
        if not rows:
            return False
        cands = [str(row[0]) for row in rows]
        self.prompt.begin_suggestions(cands, start=0, end=len(self.prompt.text), rows=rows)
        return True

    def _refresh_recent_dir_prompt_suggestions(self, *, limit: int = 40) -> bool:
        if self.prompt is None or self.prompt.kind != "recentdir":
            return False
        rows = self._recent_dir_prompt_rows(self.prompt.text, limit=limit)
        if not rows:
            return False
        cands = [str(row[0]) for row in rows]
        self.prompt.begin_suggestions(cands, start=0, end=len(self.prompt.text), rows=rows)
        return True

    def _doc_prompt_rows(self, query: str, *, limit: int = 40) -> list[list[str]]:
        q = str(query or "").strip()
        cap = max(1, int(limit))
        sections = self.doc_section_rows(q, limit=None)
        return self._flatten_grouped_prompt_sections(
            sections,
            limit=cap,
            browse_budget=(q == ""),
        )

    def _refresh_doc_prompt_suggestions(self, *, limit: int = 40) -> bool:
        if self.prompt is None or self.prompt.kind != "doc":
            return False
        rows = self._doc_prompt_rows(self.prompt.text, limit=limit)
        if not rows:
            return False
        cands = [str(row[0]) for row in rows]
        self.prompt.begin_suggestions(cands, start=0, end=len(self.prompt.text), rows=rows)
        return True

    def _helplink_prompt_rows(self, query: str, *, limit: int = 80) -> list[list[str]]:
        q = str(query or "").strip()
        cap = max(1, int(limit))
        if q:
            return self.help_link_rows(q, limit=cap)
        sections = self.help_link_section_rows(q, limit=None)
        return self._flatten_grouped_prompt_sections(
            sections,
            limit=cap,
            browse_budget=True,
        )

    def _refresh_helplink_prompt_suggestions(self, *, limit: int = 80) -> bool:
        if self.prompt is None or self.prompt.kind != "helplink":
            return False
        rows = self._helplink_prompt_rows(self.prompt.text, limit=limit)
        if not rows:
            return False
        cands = [str(row[0]) for row in rows]
        self.prompt.begin_suggestions(cands, start=0, end=len(self.prompt.text), rows=rows)
        return True

    def _helpoutline_prompt_rows(self, query: str, *, limit: int = 120) -> list[list[str]]:
        q = str(query or "").strip()
        cap = max(1, int(limit))
        if q:
            return self.help_outline_rows(q, limit=cap)
        sections = self.help_outline_section_rows(q, limit=None)
        return self._flatten_grouped_prompt_sections(
            sections,
            limit=cap,
            browse_budget=True,
        )

    def _refresh_helpoutline_prompt_suggestions(self, *, limit: int = 120) -> bool:
        if self.prompt is None or self.prompt.kind != "helpoutline":
            return False
        rows = self._helpoutline_prompt_rows(self.prompt.text, limit=limit)
        if not rows:
            return False
        cands = [str(row[0]) for row in rows]
        self.prompt.begin_suggestions(cands, start=0, end=len(self.prompt.text), rows=rows)
        return True

    def _helpnav_prompt_rows(self, query: str, *, limit: int = 160) -> list[list[str]]:
        q = str(query or "").strip()
        cap = max(1, int(limit))
        if q:
            return self.help_nav_rows(q, limit=cap)
        sections = self.help_nav_section_rows(q, limit=None)
        return self._flatten_grouped_prompt_sections(
            sections,
            limit=cap,
            browse_budget=True,
        )

    def _refresh_helpnav_prompt_suggestions(self, *, limit: int = 160) -> bool:
        if self.prompt is None or self.prompt.kind != "helpnav":
            return False
        rows = self._helpnav_prompt_rows(self.prompt.text, limit=limit)
        if not rows:
            return False
        cands = [str(row[0]) for row in rows]
        self.prompt.begin_suggestions(cands, start=0, end=len(self.prompt.text), rows=rows)
        return True


    def _refresh_palette_prompt_suggestions(self, *, limit: int = 40) -> bool:
        if self.prompt is None or self.prompt.kind != "palette":
            return False
        rows = self._palette_prompt_rows(self.prompt.text, limit=limit)
        if not rows:
            return False
        cands = [str(row[0]) for row in rows]
        self.prompt.begin_suggestions(cands, start=0, end=len(self.prompt.text), rows=rows)
        return True

    def _refresh_topic_prompt_suggestions(self, *, limit: int = 40) -> bool:
        if self.prompt is None or self.prompt.kind != "topic":
            return False
        rows = self._topic_prompt_rows(self.prompt.text, limit=limit)
        if not rows:
            return False
        cands = [str(row[0]) for row in rows]
        self.prompt.begin_suggestions(cands, start=0, end=len(self.prompt.text), rows=rows)
        return True

    def _refresh_binding_prompt_suggestions(self, *, limit: int = 40) -> bool:
        if self.prompt is None or self.prompt.kind != "binding":
            return False
        rows = self._binding_prompt_rows(self.prompt.text, limit=limit)
        if not rows:
            return False
        cands = [str(row[0]) for row in rows]
        self.prompt.begin_suggestions(cands, start=0, end=len(self.prompt.text), rows=rows)
        return True

    def enter_command_palette(self, query: str = "") -> None:
        self.enter_prompt("palette", prefill=str(query or ""))
        self._refresh_palette_prompt_suggestions()

    def enter_topic_prompt(self, query: str = "") -> None:
        self.enter_prompt("topic", prefill=str(query or ""))
        self._refresh_topic_prompt_suggestions()

    def enter_binding_prompt(self, query: str = "") -> None:
        self.enter_prompt("binding", prefill=str(query or ""))
        self._refresh_binding_prompt_suggestions()


    def enter_buffer_prompt(self, query: str = "") -> None:
        self.enter_prompt("buffer", prefill=str(query or ""))
        self._refresh_buffer_prompt_suggestions()

    def enter_mark_prompt(self, query: str = "") -> None:
        self.enter_prompt("mark", prefill=str(query or ""))
        self._refresh_mark_prompt_suggestions()


    def enter_jump_prompt(self, query: str = "") -> None:
        self.enter_prompt("jump", prefill=str(query or ""))
        self._refresh_jump_prompt_suggestions()

    def enter_plugin_prompt(self, query: str = "") -> None:
        self.enter_prompt("plugin", prefill=str(query or ""))
        self._refresh_plugin_prompt_suggestions()

    def enter_recent_prompt(self, query: str = "") -> None:
        self.enter_prompt("recent", prefill=str(query or ""))
        self._refresh_recent_prompt_suggestions()

    def enter_recent_dir_prompt(self, query: str = "") -> None:
        self.enter_prompt("recentdir", prefill=str(query or ""))
        self._refresh_recent_dir_prompt_suggestions()

    def enter_doc_prompt(self, query: str = "") -> None:
        self.enter_prompt("doc", prefill=str(query or ""))
        self._refresh_doc_prompt_suggestions()

    def enter_helplink_prompt(self, query: str = "") -> None:
        """Open a picker over links in the current docs/help buffer."""

        self.enter_prompt("helplink", prefill=str(query or ""))
        self._refresh_helplink_prompt_suggestions()

    def enter_helpoutline_prompt(self, query: str = "") -> None:
        """Open a picker over headings in the current docs/help buffer."""

        self.enter_prompt("helpoutline", prefill=str(query or ""))
        self._refresh_helpoutline_prompt_suggestions()

    def enter_helpnav_prompt(self, query: str = "") -> None:
        """Open a combined picker over headings + links in the current docs/help buffer."""

        self.enter_prompt("helpnav", prefill=str(query or ""))
        self._refresh_helpnav_prompt_suggestions()


    def _sync_prompt_after_text_change(self) -> None:
        if self.prompt is None:
            return
        if self.prompt.kind == "palette":
            self._refresh_palette_prompt_suggestions()
        elif self.prompt.kind == "topic":
            self._refresh_topic_prompt_suggestions()
        elif self.prompt.kind == "binding":
            self._refresh_binding_prompt_suggestions()
        elif self.prompt.kind == "buffer":
            self._refresh_buffer_prompt_suggestions()
        elif self.prompt.kind == "mark":
            self._refresh_mark_prompt_suggestions()
        elif self.prompt.kind == "jump":
            self._refresh_jump_prompt_suggestions()
        elif self.prompt.kind == "plugin":
            self._refresh_plugin_prompt_suggestions()
        elif self.prompt.kind == "recent":
            self._refresh_recent_prompt_suggestions()
        elif self.prompt.kind == "recentdir":
            self._refresh_recent_dir_prompt_suggestions()
        elif self.prompt.kind == "doc":
            self._refresh_doc_prompt_suggestions()
        elif self.prompt.kind == "helplink":
            self._refresh_helplink_prompt_suggestions()
        elif self.prompt.kind == "helpoutline":
            self._refresh_helpoutline_prompt_suggestions()
        elif self.prompt.kind == "helpnav":
            self._refresh_helpnav_prompt_suggestions()
        elif self.prompt.kind == "find" and bool(self.options.get("incsearch", local=self.cur().local_options)):
            self.find(self.prompt.text, literal=self.search.literal)

    def set_prompt_text(self, s: str) -> bool:
        if self.prompt is None:
            return False
        self.prompt.set_text(s)
        self._sync_prompt_after_text_change()
        return True

    def set_prompt_text_cursor(self, s: str, cursor: int) -> bool:
        """Set prompt text and cursor (0-based), then refresh prompt state."""
        if self.prompt is None:
            return False
        self.prompt.set_text(s)
        self.prompt.set_cursor(int(cursor))
        self._sync_prompt_after_text_change()
        return True

    def prompt_current_row(self) -> list[str]:
        if self.prompt is None or not self.prompt.suggestion_rows:
            return []
        idx = int(self.prompt.suggest_index)
        if idx < 0 or idx >= len(self.prompt.suggestion_rows):
            idx = 0
        row = list(self.prompt.suggestion_rows[idx][:4])
        while len(row) < 4:
            row.append("")
        return [str(row[0]), str(row[1]), str(row[2]), str(row[3])]

    def prompt_current_position(self) -> dict[str, Any]:
        """Return a compact position model for the active prompt selection.

        This keeps headless APIs, status surfaces, and the minimal TUI aligned on
        one small notion of “where am I in this picker?”, including the current
        row's coarse section when one exists.
        """

        out: dict[str, Any] = {
            "index": 0,
            "count": 0,
            "section": "",
            "section_index": 0,
            "section_count": 0,
            "summary": "",
        }
        if self.prompt is None or not self.prompt.suggestion_rows:
            return out

        rows = [list(r[:4]) for r in self.prompt.suggestion_rows]
        idx = int(self.prompt.suggest_index)
        if idx < 0 or idx >= len(rows):
            idx = 0
        count = int(len(rows))
        kind = str(self.prompt.kind or "")
        cur = [str(x) for x in list(rows[idx][:4])]
        while len(cur) < 4:
            cur.append("")
        label = str(self.prompt_row_section_label(cur, prompt_kind=kind) or "")
        section_count = 0
        section_index = 0
        if label:
            seen = 0
            for pos, row in enumerate(rows):
                vals = [str(x) for x in list(row[:4])]
                while len(vals) < 4:
                    vals.append("")
                if str(self.prompt_row_section_label(vals, prompt_kind=kind) or "") != label:
                    continue
                seen += 1
                if pos == idx:
                    section_index = int(seen)
            section_count = int(seen)

        summary = f"{idx + 1}/{count}"
        if label and section_count > 0:
            sec_pos = section_index if section_index > 0 else 1
            summary = f"{summary} • {label} {sec_pos}/{section_count}"

        out.update({
            "index": int(idx + 1),
            "count": int(count),
            "section": str(label),
            "section_index": int(section_index),
            "section_count": int(section_count),
            "summary": str(summary),
        })
        return out

    def search_position_model(self) -> dict[str, Any]:
        """Return a compact position model for the active whole-buffer search.

        This keeps status surfaces, the minimal TUI, and future UIs/LLMs aligned
        on one tiny notion of “where am I in the current search?”, reusing the
        editor's existing literal/regex + ignorecase semantics.
        """

        out: dict[str, Any] = {
            "query": "",
            "literal": 1 if bool(self.search.literal) else 0,
            "case_sensitive": 1 if bool(self.search.case_sensitive) else 0,
            "index": 0,
            "count": 0,
            "summary": "",
        }
        query = str(self.search.query or "")
        if not query:
            return out

        eb = self.cur()
        self._normalize_cursor_lists(eb)
        cur = eb.cursors[eb.primary]
        idx, total = search_position(eb.buf, self.search, cursor=cur)
        out.update({
            "query": str(query),
            "literal": 1 if bool(self.search.literal) else 0,
            "case_sensitive": 1 if bool(self.search.case_sensitive) else 0,
            "index": int(idx),
            "count": int(total),
            "summary": f"{idx}/{total}",
        })
        return out

    def prompt_window_model(self, *, max_lines: int) -> dict[str, Any]:
        """Return the shared picker-window model used by the TUI.

        This exposes the same scroll-window, sticky-header, and more-marker
        structure the minimal TUI uses so future UIs/scripts/LLMs do not need to
        reconstruct it from raw suggestion rows.
        """

        out: dict[str, Any] = {
            "kind": "",
            "max_lines": max(0, int(max_lines)),
            "flat_count": 0,
            "selected_index": 0,
            "selected_flat_index": 0,
            "start": 0,
            "end": 0,
            "show_top": 0,
            "show_bottom": 0,
            "sticky_section": "",
            "hidden_above": 0,
            "hidden_below": 0,
            "entries": [],
        }
        if self.prompt is None or not self.prompt.suggestion_rows or int(max_lines) <= 0:
            return out
        kind = str(self.prompt.kind or "")
        if kind in ("command", "find"):
            out["kind"] = kind
            return out

        rows = [list(r[:4]) for r in self.prompt.suggestion_rows]

        def _label_for(row: list[str]) -> str:
            return str(self.prompt_row_section_label([str(x) for x in row], prompt_kind=kind) or "")

        labels: list[str] = []
        counts: dict[str, int] = {}
        for row in rows:
            lbl = _label_for([str(x) for x in row])
            labels.append(lbl)
            if lbl:
                counts[lbl] = int(counts.get(lbl, 0) or 0) + 1

        flat: list[dict[str, Any]] = []
        last_label = ""
        for idx2, row in enumerate(rows):
            vals = [str(x) for x in list(row[:4])]
            while len(vals) < 4:
                vals.append("")
            label = labels[idx2] if idx2 < len(labels) else _label_for(vals)
            if label and label != last_label:
                flat.append({"type": "header", "label": str(label), "count": int(counts.get(label, 0) or 0)})
                last_label = label
            flat.append({
                "type": "row",
                "label": str(label),
                "count": int(counts.get(label, 0) or 0),
                "suggestion_index": int(idx2),
                "row": vals,
                "row_kind": str(vals[1] if len(vals) > 1 else ""),
                "selected": 0,
            })

        sel = int(self.prompt.suggest_index) if self.prompt.suggestion_rows else 0
        if sel < 0 or sel >= len(rows):
            sel = 0
        sel_pos = 0
        for i, item in enumerate(flat):
            if int(item.get("suggestion_index", -1)) == sel:
                sel_pos = i
                break

        content_n = max(1, int(max_lines))
        start = end = 0
        show_top = show_bottom = False
        for _ in range(3):
            content_n = max(1, int(content_n))
            start = max(0, sel_pos - content_n // 2)
            end = min(len(flat), start + content_n)
            if end - start < content_n:
                start = max(0, end - content_n)

            show_top = start > 0
            show_bottom = end < len(flat)
            need = (1 if show_top else 0) + (1 if show_bottom else 0)
            new_content_n = max(1, int(max_lines) - need)
            if new_content_n == content_n:
                break
            content_n = new_content_n

        sticky_label = ""
        if start > 0 and start < len(flat):
            item0 = flat[start]
            if str(item0.get("type", "")) != "header" and str(item0.get("label", "")):
                sticky_label = str(item0.get("label", ""))

        above_n = sum(1 for item in flat[:start] if str(item.get("type", "")) == "row")
        below_n = sum(1 for item in flat[end:] if str(item.get("type", "")) == "row")

        entries: list[dict[str, Any]] = []
        if show_top:
            entries.append({"type": "more", "direction": "up", "hidden": int(above_n)})
        if sticky_label:
            entries.append({"type": "sticky", "label": sticky_label, "count": int(counts.get(sticky_label, 0) or 0)})

        for item in flat[start:end]:
            typ = str(item.get("type", ""))
            if typ == "header":
                entries.append({"type": "header", "label": str(item.get("label", "")), "count": int(item.get("count", 0) or 0)})
                continue
            row = [str(x) for x in list(item.get("row", [])[:4])]
            while len(row) < 4:
                row.append("")
            entries.append({
                "type": "row",
                "label": str(item.get("label", "")),
                "count": int(item.get("count", 0) or 0),
                "suggestion_index": int(item.get("suggestion_index", 0) or 0),
                "row": row,
                "row_kind": str(item.get("row_kind", "")),
                "selected": 1 if int(item.get("suggestion_index", -1)) == sel else 0,
            })
        if show_bottom:
            entries.append({"type": "more", "direction": "down", "hidden": int(below_n)})

        if len(entries) > int(max_lines):
            while len(entries) > int(max_lines):
                if show_bottom and entries and str(entries[-1].get("type", "")) == "more" and len(entries) >= 2:
                    entries.pop(-2)
                else:
                    entries.pop()

        out.update({
            "kind": kind,
            "flat_count": int(len(flat)),
            "selected_index": int(sel),
            "selected_flat_index": int(sel_pos),
            "start": int(start),
            "end": int(end),
            "show_top": 1 if show_top else 0,
            "show_bottom": 1 if show_bottom else 0,
            "sticky_section": str(sticky_label),
            "hidden_above": int(above_n),
            "hidden_below": int(below_n),
            "entries": entries,
        })
        return out

    def prompt_display_model(self, *, max_lines: int, width: int) -> list[dict[str, Any]]:
        """Return a shared rendered prompt-row model for the active picker.

        This mirrors the visible prompt rows the minimal TUI shows, but keeps the
        result renderer-agnostic and headlessly inspectable for future
        UIs/scripts/LLMs.
        """

        p = self.prompt
        if p is None or not p.suggestion_rows or int(max_lines) <= 0 or int(width) <= 0:
            return []
        kind = str(p.kind or "")
        if kind in ("command", "find"):
            return []

        model = self.prompt_window_model(max_lines=max_lines)
        entries = model.get("entries", []) if isinstance(model, dict) else []

        def _label_disp(lbl: str, count: int) -> str:
            n = int(count or 0)
            return f"{lbl} ({n})" if n > 0 else str(lbl)

        out: list[dict[str, Any]] = []
        for ent in entries if isinstance(entries, list) else []:
            if not isinstance(ent, dict):
                continue
            typ = str(ent.get("type", ""))
            if typ == "more":
                hidden = int(ent.get("hidden", 0) or 0)
                direction = str(ent.get("direction", "down"))
                arrow = "↑" if direction == "up" else "↓"
                suffix = f" (+{hidden})" if hidden > 0 else ""
                out.append({
                    "type": "more",
                    "text": _ellipsize_right(f"{arrow} more…{suffix}", max(0, int(width))),
                    "row_kind": "more",
                    "section_label": "",
                    "selected": 0,
                    "hidden": int(hidden),
                    "direction": str(direction),
                })
                continue
            if typ in ("header", "sticky"):
                lbl = str(ent.get("label", ""))
                count = int(ent.get("count", 0) or 0)
                header_text = f"-- {_label_disp(lbl, count)} --"
                if count > 0 and len(header_text) > int(width):
                    header_text = f"-- {lbl} --"
                out.append({
                    "type": str(typ),
                    "text": _ellipsize_right(header_text, max(0, int(width))),
                    "row_kind": "header",
                    "section_label": str(lbl),
                    "selected": 0,
                    "count": int(count),
                })
                continue
            if typ != "row":
                continue

            row = [str(x) for x in list(ent.get("row", [])[:4])]
            while len(row) < 4:
                row.append("")
            name = str(row[0] if len(row) > 0 else "")
            row_kind = str(ent.get("row_kind", row[1] if len(row) > 1 else ""))
            menu = str(row[2] if len(row) > 2 else "")
            info = str(row[3] if len(row) > 3 else "")

            if kind in ("helpoutline", "helpnav") and row_kind == "heading":
                mm = re.match(r"^h([1-6])$", str(menu or "").strip().casefold())
                if mm:
                    try:
                        lvl = int(mm.group(1))
                    except Exception:
                        lvl = 1
                    if lvl > 1:
                        name = ("  " * (lvl - 1)) + name

            detail = f"{menu} | {info}" if menu and info else (menu or info)
            selected = 1 if bool(int(ent.get("selected", 0) or 0)) else 0
            prefix = "> " if selected else "  "
            body = _fit_left_right_text(name, detail, max(0, int(width) - len(prefix)), sep=" — ")
            out.append({
                "type": "row",
                "text": (prefix + body)[: max(0, int(width))],
                "row_kind": str(row_kind),
                "section_label": str(ent.get("label", "") or ""),
                "selected": int(selected),
                "row": row,
                "menu": str(menu),
                "info": str(info),
                "suggestion_index": int(ent.get("suggestion_index", 0) or 0),
            })
        return out

    def prompt_current_section(self) -> str:
        row = self.prompt_current_row()
        if not row:
            return ""
        # Prompt-specific section naming overrides.
        if self.prompt is not None and self.prompt.kind == "helplink":
            # Reuse the same visible section labels the docs-link pickers and TUI
            # headers already show (Docs / Files / External or heading buckets).
            return str(self.helplink_section_label([str(x) for x in row]))

        if self.prompt is not None and self.prompt.kind == "helpoutline":
            return str(self.help_outline_section_label([str(x) for x in row]))

        if self.prompt is not None and self.prompt.kind == "helpnav":
            # Rows are either headings ([title "heading" hN line:col])
            # or links ([label "link" target line:col]).
            kind2 = str(row[1] or "").strip().lower()
            if kind2 == "heading":
                return str(self.help_outline_section_label([str(x) for x in row]))
            if kind2 == "link":
                return str(self.helplink_section_label([str(x) for x in row]))
            return "Items"
        if self.prompt is not None and self.prompt.kind == "topic":
            _single, plural = self._topic_section_names(str(row[1] or ""))
            return str(plural)
        if self.prompt is not None and self.prompt.kind == "binding":
            return str(self._binding_section_label(row))
        if self.prompt is not None and self.prompt.kind == "recent":
            return self.prompt_row_section_label(row, prompt_kind="recent")
        if self.prompt is not None and self.prompt.kind == "recentdir":
            return self.prompt_row_section_label(row, prompt_kind="recentdir")
        if self.prompt is not None and self.prompt.kind == "buffer":
            return str(self._buffer_section_label(row))
        if self.prompt is not None and self.prompt.kind == "mark":
            return str(self._mark_section_label(row))
        if self.prompt is not None and self.prompt.kind == "jump":
            return str(self._jump_section_label(row))
        if self.prompt is not None and self.prompt.kind == "plugin":
            return str(self._plugin_section_display_label(row))
        if self.prompt is not None and self.prompt.kind == "doc":
            return str(self._doc_section_label(row))
        if self.prompt is not None and self.prompt.kind == "palette":
            return str(self._command_palette_section_label(row))
        kind = str(row[1] or "")
        if kind == "binding":
            return "Binding"
        single, _plural = self._topic_section_names(kind)
        return single

    def prompt_current_preview(self) -> str:
        row = self.prompt_current_row()
        if not row:
            return ""
        name, _kind, menu, info = row
        section = self.prompt_current_section()
        if self.prompt is not None and self.prompt.kind == "doc":
            head_name = str(menu or name)
            head = f"{section}: {head_name}" if section else head_name
            detail = str(info or "")
            if detail:
                return f"{head} — {detail}"
            return head
        if self.prompt is not None and self.prompt.kind == "plugin":
            head_name = str(name)
            menu_s = str(menu or "").strip()
            if menu_s:
                head_name = f"{head_name} {menu_s}".strip()
            head = f"{section}: {head_name}" if section else head_name
            detail = str(info or "")
            return head if not detail else f"{head} — {detail}"
        head = f"{section}: {name}" if section else str(name)
        detail = ""
        if menu and info:
            detail = f"{menu} | {info}"
        elif menu:
            detail = menu
        elif info:
            detail = info
        return head if not detail else f"{head} — {detail}"

    def cancel_prompt(self) -> bool:
        if self.prompt is None:
            return False
        self.prompt = None
        self._pop_prompt_keymode()
        return True

    def _push_history(self, kind: str, text: str) -> None:
        text = text.strip("\n")
        if not text:
            return
        h = self.history.setdefault(kind, [])
        if h and h[-1] == text:
            return
        h.append(text)

        # Keep histories bounded.
        limit = 200
        try:
            limit = max(1, int(self.options.get("history.limit")))
        except Exception:
            limit = 200
        if len(h) > limit:
            del h[:-limit]

        # Best-effort persistence (gated by history.persist + cap.persist).
        try:
            self.save_prompt_history()
        except Exception:
            pass

    def _counted_prompt_zero_summary(self, label: str, noun: str, query: str = "") -> str:
        """Return one tiny zero-match dialect for searchable picker submit paths.

        Search-first prompts should stay explicit about *what* query produced no
        result instead of collapsing back to a vague ``(none)`` message exactly
        when the visible match count drops to zero.
        """

        q = str(query or "").strip()
        head = str(label)
        if q:
            head = f"{head} {q}"
        return f"{head}: 0 {str(noun)}(s)"

    def submit_prompt(self) -> bool:
        if self.prompt is None:
            return False
        prompt = self.prompt
        kind = prompt.kind
        text = prompt.text
        self.prompt = None
        self._pop_prompt_keymode()
        if kind == "command":
            # exec_command_line records command history.
            return self.exec_command_line(text)
        if kind == "find":
            self._push_history("find", text)
            return self.find(text, announce=True)
        if kind == "palette":
            self._push_history("palette", text)
            q = str(text or "").strip()
            target = ""
            target_kind = ""
            if prompt.suggestions:
                idx = int(prompt.suggest_index) % len(prompt.suggestions)
                target = str(prompt.suggestions[idx]).strip()
                row = list(prompt.suggestion_rows[idx][:4]) if idx < len(prompt.suggestion_rows) else []
                target_kind = str(row[1]) if len(row) >= 2 else ""
                if prompt.text != prompt.suggest_base and q:
                    target = q
                    target_kind = ""
            if target and not target_kind:
                if self.command_dispatcher.get(target) is not None:
                    target_kind = "command"
                elif self.actions.get(target) is not None:
                    target_kind = "action"
                elif self._looks_like_path_query(str(target)):
                    target_kind = "openpath"
            if not target:
                if q and self.command_dispatcher.get(q) is not None:
                    target, target_kind = q, "command"
                elif q and self.actions.get(q) is not None:
                    target, target_kind = q, "action"
                elif q:
                    rows = self.command_palette_apropos_rows(q, limit=1)
                    if rows:
                        target = str(rows[0][0]).strip()
                        target_kind = str(rows[0][1]).strip()
            if not target or target_kind not in ("command", "action", "recentfile", "openpath"):
                self.message(self._counted_prompt_zero_summary("commandpick", "match", q))
                return False
            if target_kind in ("recentfile", "openpath"):
                # When filesystem listing is enabled, treat directory targets as
                # a drill-down: keep the palette open and navigate into that dir
                # instead of trying to open it as a file.
                if target_kind == "openpath" and bool(self.options.get("cap.fs-list")):
                    try:
                        p = fs_resolve_path(self, str(target))
                        if fs_sandbox_root(self) is not None and not fs_path_allowed(self, p):
                            raise RuntimeError(f"outside cap.fs-root: {p}")
                        if p.exists() and p.is_dir():
                            raw = str(target).strip()
                            if raw and not raw.endswith(("/", "\\")):
                                raw = raw + "/"
                            self.enter_command_palette(raw)
                            return True
                    except Exception:
                        pass

                # Script safety: selecting an openpath/recentfile row must not grant
                # ambient filesystem authority. Require cap.fs-open in script context.
                if self.in_script_context() and not bool(self.options.get("cap.fs-open")):
                    self.message("open: disabled (cap.fs-open). Enable with: set cap.fs-open true")
                    return False

                try:
                    raw_target, initial_cursor = self._parse_open_target(str(target))
                    # Optional filesystem sandbox root.
                    if fs_sandbox_root(self) is not None:
                        p2 = fs_resolve_path(self, raw_target)
                        if not fs_path_allowed(self, p2):
                            self.message(f"open: outside cap.fs-root: {p2}")
                            return False
                        ok2 = self.open_file(str(p2), initial_cursor=initial_cursor)
                    else:
                        ok2 = self.open_file(str(target), initial_cursor=initial_cursor)
                except Exception as e:
                    self.message(f"open: {e}")
                    return False
                if ok2:
                    self.message(f"opened: {self.format_cursor_target()}")
                return bool(ok2)
            if target_kind == "action":
                ok = self.run_action(target)
                if ok:
                    self._record_palette_recent("action", target)
                return ok
            self._record_palette_recent("command", target)
            self.enter_prompt("command", prefill=target + " " )
            return True
        if kind == "topic":
            self._push_history("topic", text)
            target = ""
            if prompt.suggestions:
                idx = int(prompt.suggest_index) % len(prompt.suggestions)
                target = str(prompt.suggestions[idx]).strip()
                if prompt.text != prompt.suggest_base and str(prompt.text).strip():
                    target = str(prompt.text).strip()
            if not target:
                q = str(text or "").strip()
                if q:
                    rows = self.apropos_rows(q, limit=1)
                    if rows:
                        target = str(rows[0][0]).strip()
            if not target:
                self.message(self._counted_prompt_zero_summary("topicpick", "topic", text))
                return False
            return self.exec_command_line("help " + shlex.quote(target))
        if kind == "binding":
            self._push_history("binding", text)
            target = ""
            if prompt.suggestions:
                idx = int(prompt.suggest_index) % len(prompt.suggestions)
                target = str(prompt.suggestions[idx]).strip()
                if prompt.text != prompt.suggest_base and str(prompt.text).strip():
                    target = str(prompt.text).strip()
            if not target:
                q = str(text or "").strip()
                if q:
                    rows = self.binding_apropos_rows(q, limit=1)
                    if rows:
                        target = str(rows[0][0]).strip()
            if not target:
                self.message(self._counted_prompt_zero_summary("bindingpick", "binding", text))
                return False
            return self.exec_command_line("showkey " + shlex.quote(target))
        if kind == "buffer":
            self._push_history("buffer", text)
            target = ""
            if prompt.suggestions:
                idx = int(prompt.suggest_index) % len(prompt.suggestions)
                target = str(prompt.suggestions[idx]).strip()
                if prompt.text != prompt.suggest_base and str(prompt.text).strip():
                    target = str(prompt.text).strip()
            if not target:
                q = str(text or "").strip()
                if q and q in self.buffers:
                    target = q
                elif q:
                    rows = self.buffer_apropos_rows(q, limit=1)
                    if rows:
                        target = str(rows[0][0]).strip()
            if not target:
                self.message(self._counted_prompt_zero_summary("bufferpick", "buffer", text))
                return False
            if not self.switch_buffer(target):
                self.message(f"bufferpick: no such buffer: {target}")
                return False
            try:
                eb = self.cur()
                path = str(getattr(eb.buf, "path", "") or getattr(eb, "name", "") or "").strip()
                c = self.primary_cursor()
                if path:
                    self.message(f"buffer: {path} @ {c.line + 1}:{c.col}")
                else:
                    self.message(f"buffer @ {c.line + 1}:{c.col}")
            except Exception:
                self.message(f"buffer: {target}")
            return True
        if kind == "plugin":
            self._push_history("plugin", text)
            target = ""
            if prompt.suggestions:
                idx = int(prompt.suggest_index) % len(prompt.suggestions)
                target = str(prompt.suggestions[idx]).strip()
                if prompt.text != prompt.suggest_base and str(prompt.text).strip():
                    target = str(prompt.text).strip()
            if not target:
                q = str(text or "").strip()
                if q:
                    rows = self.plugin_apropos_rows(q, limit=1)
                    if rows:
                        target = str(rows[0][0]).strip()
            if not target:
                self.message(self._counted_prompt_zero_summary("pluginpick", "plugin", text))
                return False

            pm = getattr(self, "plugin_manager", None)
            loaded = bool(pm and target in getattr(pm, "plugins", {}))
            has_errors = False
            try:
                has_errors = bool(pm and any(str(n) == str(target) for (n, _e) in getattr(pm, "load_errors", [])))
            except Exception:
                has_errors = False
            if loaded:
                cmd = "plugin reload " + shlex.quote(target)
            elif has_errors:
                cmd = "plugin errors " + shlex.quote(target)
            else:
                cmd = "plugin info " + shlex.quote(target)
            return self.exec_command_line(cmd)
        if kind == "recent":
            self._push_history("recent", text)
            target = ""
            if prompt.suggestions:
                idx = int(prompt.suggest_index) % len(prompt.suggestions)
                target = str(prompt.suggestions[idx]).strip()
                if prompt.text != prompt.suggest_base and str(prompt.text).strip():
                    target = str(prompt.text).strip()
            if not target:
                q = str(text or "").strip()
                if q:
                    rows = self.recent_apropos_rows(q, limit=1)
                    if rows:
                        target = str(rows[0][0]).strip()
            if not target:
                self.message(self._counted_prompt_zero_summary("recentpick", "recent file", text))
                return False
            return self.exec_command_line("open " + shlex.quote(target))

        if kind == "recentdir":
            self._push_history("recentdir", text)
            target = ""
            if prompt.suggestions:
                idx = int(prompt.suggest_index) % len(prompt.suggestions)
                target = str(prompt.suggestions[idx]).strip()
                if prompt.text != prompt.suggest_base and str(prompt.text).strip():
                    target = str(prompt.text).strip()
            if not target:
                q = str(text or "").strip()
                if q:
                    rows = self.recent_apropos_rows(q, limit=1)
                    if rows:
                        target = str(rows[0][0]).strip()
            if not target:
                self.message(self._counted_prompt_zero_summary("recentdirpick", "recent file", text))
                return False
            return self.exec_command_line("open " + shlex.quote(target))

        if kind == "doc":
            self._push_history("doc", text)
            target = ""
            if prompt.suggestions:
                idx = int(prompt.suggest_index) % len(prompt.suggestions)
                target = str(prompt.suggestions[idx]).strip()
                if prompt.text != prompt.suggest_base and str(prompt.text).strip():
                    target = str(prompt.text).strip()
            if not target:
                q = str(text or "").strip()
                if q:
                    rows = self.doc_apropos_rows(q, limit=1)
                    if rows:
                        target = str(rows[0][0]).strip()
            if not target:
                self.message(self._counted_prompt_zero_summary("docpick", "doc", text))
                return False
            if not self.open_help_doc(target):
                self.message(f"docpick: no such doc: {target}")
                return False
            self.message(f"help: {self.format_help_target()}")
            return True

        if kind == "helpnav":
            self._push_history("helpnav", text)

            chosen: list[str] | None = None
            if prompt.suggestion_rows and prompt.suggestions:
                idx = int(prompt.suggest_index) % len(prompt.suggestions)
                row = list(prompt.suggestion_rows[idx][:4]) if idx < len(prompt.suggestion_rows) else []
                chosen = [str(x) for x in row]

                # If the user typed extra text, treat it as a query and re-resolve.
                if prompt.text != prompt.suggest_base and str(prompt.text).strip():
                    q2 = str(prompt.text).strip()
                    rows2 = self.help_nav_rows(q2, limit=1)
                    chosen = [str(x) for x in rows2[0][:4]] if rows2 else None

            if chosen is None:
                q = str(text or "").strip()
                if q:
                    rows = self.help_nav_rows(q, limit=1)
                    chosen = [str(x) for x in rows[0][:4]] if rows else None

            if not chosen or len(chosen) < 2:
                self.message(self._counted_prompt_zero_summary("helpnavpick", "help target", text))
                return False

            row_kind = str(chosen[1] or "").strip().lower()
            if row_kind == "link":
                target = str(chosen[2] if len(chosen) > 2 else "").strip()
                if not target:
                    self.message("helpnavpick: invalid link")
                    return False
                eb = self.cur()
                low = target.casefold()
                is_external = low.startswith("http://") or low.startswith("https://") or low.startswith("mailto:")
                ok = bool(self._follow_help_link(target, base_path=str(eb.buf.path) if eb.buf.path else None))
                if ok and not is_external:
                    self.message(f"helpjump: {self.format_cursor_target()}")
                return ok

            if row_kind == "heading":
                linecol = str(chosen[3] if len(chosen) > 3 else "").strip()
                if not linecol:
                    self.message("helpnavpick: bad heading location")
                    return False
                try:
                    if ":" in linecol:
                        a, b = linecol.split(":", 1)
                        line_i = int(a, 10)
                        col_i = int(b, 10)
                    else:
                        line_i = int(linecol, 10)
                        col_i = 1
                except Exception:
                    self.message("helpnavpick: bad heading location")
                    return False

                line0 = max(0, int(line_i) - 1)
                col0 = max(0, int(col_i) - 1)
                eb = self.cur()
                self._normalize_cursor_lists(eb)
                eb.cursors[eb.primary] = eb.buf.clamp(Cursor(line0, col0))
                self.ensure_cursor_visible()
                self.message(f"helpjump: {self.format_cursor_target()}")
                return True

            self.message("helpnavpick: invalid selection")
            return False

        if kind == "helplink":
            self._push_history("helplink", text)
            target = ""
            if prompt.suggestion_rows and prompt.suggestions:
                idx = int(prompt.suggest_index) % len(prompt.suggestions)
                row = list(prompt.suggestion_rows[idx][:4]) if idx < len(prompt.suggestion_rows) else []
                # row: [label kind target info]
                target = str(row[2] if len(row) > 2 else "").strip()
                if prompt.text != prompt.suggest_base and str(prompt.text).strip():
                    target = str(prompt.text).strip()
            if not target:
                q = str(text or "").strip()
                if q:
                    rows = self.help_link_rows(q, limit=1)
                    if rows:
                        target = str(rows[0][2] if len(rows[0]) > 2 else rows[0][0]).strip()
            if not target:
                self.message(self._counted_prompt_zero_summary("helplinkpick", "link", text))
                return False
            eb = self.cur()
            low = target.casefold()
            is_external = low.startswith("http://") or low.startswith("https://") or low.startswith("mailto:")
            ok = bool(self._follow_help_link(target, base_path=str(eb.buf.path) if eb.buf.path else None))
            if ok and not is_external:
                self.message(f"helpjump: {self.format_cursor_target()}")
            return ok
        if kind == "helpoutline":
            self._push_history("helpoutline", text)
            linecol = ""
            if prompt.suggestion_rows and prompt.suggestions:
                idx = int(prompt.suggest_index) % len(prompt.suggestions)
                row = list(prompt.suggestion_rows[idx][:4]) if idx < len(prompt.suggestion_rows) else []
                # row: [title kind menu info], where info is "line:col"
                linecol = str(row[3] if len(row) > 3 else "").strip()
                if prompt.text != prompt.suggest_base and str(prompt.text).strip():
                    # If the user typed extra text, treat it as a query and re-resolve.
                    q2 = str(prompt.text).strip()
                    rows2 = self.help_outline_rows(q2, limit=1)
                    if rows2:
                        linecol = str(rows2[0][3] if len(rows2[0]) > 3 else "").strip()
            if not linecol:
                q = str(text or "").strip()
                if q:
                    rows = self.help_outline_rows(q, limit=1)
                    if rows:
                        linecol = str(rows[0][3] if len(rows[0]) > 3 else "").strip()
            if not linecol:
                self.message(self._counted_prompt_zero_summary("helpoutlinepick", "heading", text))
                return False
            # Parse 1-based "line:col"
            try:
                if ":" in linecol:
                    a, b = linecol.split(":", 1)
                    line_i = int(a, 10)
                    col_i = int(b, 10)
                else:
                    line_i = int(linecol, 10)
                    col_i = 1
            except Exception:
                self.message("helpoutlinepick: bad heading location")
                return False

            line0 = max(0, int(line_i) - 1)
            col0 = max(0, int(col_i) - 1)
            eb = self.cur()
            self._normalize_cursor_lists(eb)
            eb.cursors[eb.primary] = eb.buf.clamp(Cursor(line0, col0))
            self.ensure_cursor_visible()
            self.message(f"helpjump: {self.format_cursor_target()}")
            return True



        if kind == "mark":
            self._push_history("mark", text)
            target = ""
            if prompt.suggestions:
                idx = int(prompt.suggest_index) % len(prompt.suggestions)
                target = str(prompt.suggestions[idx]).strip()
                if prompt.text != prompt.suggest_base and str(prompt.text).strip():
                    target = str(prompt.text).strip()
            if not target:
                q = str(text or "").strip()
                if q and q in self.marks:
                    target = q
                elif q:
                    rows = self.mark_apropos_rows(q, limit=1)
                    if rows:
                        target = str(rows[0][0]).strip()
            if not target:
                self.message(self._counted_prompt_zero_summary("markpick", "mark", text))
                return False
            if not self.mark_jump(target):
                self.message(f"markpick: no such mark: {target}")
                return False
            eb = self.cur()
            self._normalize_cursor_lists(eb)
            c = eb.cursors[eb.primary]
            name = str(getattr(eb.buf, "path", "") or getattr(eb, "name", "") or "").strip()
            if name:
                self.message(f"markjump: {target} -> {name} @ {int(c.line) + 1}:{int(c.col)}")
            else:
                self.message(f"markjump: {target} -> {int(c.line) + 1}:{int(c.col)}")
            return True
        if kind == "jump":
            self._push_history("jump", text)
            target = ""
            if prompt.suggestions:
                idx = int(prompt.suggest_index) % len(prompt.suggestions)
                target = str(prompt.suggestions[idx]).strip()
                if prompt.text != prompt.suggest_base and str(prompt.text).strip():
                    target = str(prompt.text).strip()
            if not target:
                q = str(text or "").strip()
                if q:
                    rows = self.jump_apropos_rows(q, limit=1)
                    if rows:
                        target = str(rows[0][0]).strip()
            if not target:
                self.message(self._counted_prompt_zero_summary("jumppick", "jump", text))
                return False
            m = re.match(r"\s*(\d+)", str(target))
            if not m:
                self.message("jumppick: invalid selection")
                return False
            n = int(m.group(1), 10)
            if not self.jump_to_index(n - 1):
                self.message(f"jumppick: out of range: {n}")
                return False
            self.message(f"jump: {self.format_cursor_target()}")
            return True
        return False

    def prompt_history_prev(self) -> bool:
        if self.prompt is None:
            return False
        h = self.history.get(self.prompt.kind, [])
        if not h:
            return False
        if self.prompt.hist_index is None:
            self.prompt.hist_saved = self.prompt.text
            self.prompt.hist_index = len(h)
        if self.prompt.hist_index <= 0:
            return False
        self.prompt.hist_index -= 1
        self.set_prompt_text(h[self.prompt.hist_index])
        return True

    def prompt_history_next(self) -> bool:
        if self.prompt is None:
            return False
        h = self.history.get(self.prompt.kind, [])
        if self.prompt.hist_index is None:
            return False
        if self.prompt.hist_index >= len(h) - 1:
            # restore saved
            saved = self.prompt.hist_saved
            self.prompt.hist_index = None
            self.prompt.hist_saved = ""
            self.set_prompt_text(saved)
            return True
        self.prompt.hist_index += 1
        self.set_prompt_text(h[self.prompt.hist_index])
        return True


    # ----- prompt completion (command bar) -----
    def prompt_suggestions(self) -> list[str]:
        """Return current prompt suggestions as a new list."""
        if self.prompt is None:
            return []
        return list(self.prompt.suggestions)

    def prompt_suggestion_rows(self) -> list[list[str]]:
        """Return current prompt suggestion rows as [[insert kind menu info] ...]."""
        if self.prompt is None:
            return []
        out: list[list[str]] = []
        for row in self.prompt.suggestion_rows:
            vals = list(row[:4])
            while len(vals) < 4:
                vals.append("")
            out.append([str(vals[0]), str(vals[1]), str(vals[2]), str(vals[3])])
        return out

    def clear_prompt_suggestions(self) -> bool:
        """Clear the active prompt suggestion session."""
        if self.prompt is None or not self.prompt.suggestions:
            return False
        self.prompt.clear_suggestions()
        return True

    def prompt_suggest_move(self, delta: int) -> bool:
        """Move picker selection within the active prompt's suggestion list.

        This is intended for *picker-style* prompts (buffer/doc/help pickers,
        palette, etc.) where Up/Down should move the highlighted selection
        without mutating the user's typed query.

        Command/find prompts keep their traditional Up/Down semantics (history
        navigation), so this returns False for those prompt kinds.

        Wrap policy:
        - when option `prompt.wrap` is true (default), selection wraps at ends
        - when false, selection clamps to [0, n-1]
        """

        if self.prompt is None:
            return False
        if self.prompt.kind in ("command", "find"):
            return False
        if not self.prompt.suggestion_rows:
            return False
        n = len(self.prompt.suggestion_rows)
        if n <= 0:
            return False
        i = int(self.prompt.suggest_index)
        wrap = True
        try:
            wrap = bool(self.options.get("prompt.wrap"))
        except Exception:
            wrap = True
        if wrap:
            self.prompt.suggest_index = (i + int(delta)) % n
        else:
            self.prompt.suggest_index = max(0, min(n - 1, i + int(delta)))
        return True

    def prompt_suggest_page(self, pages: int) -> bool:
        """Move picker selection by a fixed page step.

        This is bound to PageUp/PageDown in prompt mode for picker-style
        prompts. The step size is controlled by option `prompt.page` (default
        8), matching the typical number of suggestion rows visible in the
        minimal TUI.

        Returns False for command/find prompts so those keys can fall back to
        history navigation.
        """

        if self.prompt is None:
            return False
        if self.prompt.kind in ("command", "find"):
            return False
        step = 8
        try:
            raw = int(self.options.get("prompt.page"))
            if raw > 0:
                step = raw
        except Exception:
            step = 8
        return bool(self.prompt_suggest_move(int(pages) * int(step)))

    def prompt_suggest_first(self) -> bool:
        """Jump picker selection to the first suggestion row (index 0).

        Returns False for command/find prompts.
        """

        if self.prompt is None:
            return False
        if self.prompt.kind in ("command", "find"):
            return False
        if not self.prompt.suggestion_rows:
            return False
        self.prompt.suggest_index = 0
        return True


    def prompt_suggest_last(self) -> bool:
        """Jump picker selection to the last suggestion row (index n-1).

        Returns False for command/find prompts.
        """

        if self.prompt is None:
            return False
        if self.prompt.kind in ("command", "find"):
            return False
        if not self.prompt.suggestion_rows:
            return False
        self.prompt.suggest_index = max(0, len(self.prompt.suggestion_rows) - 1)
        return True

    def prompt_row_section_label(self, row: list[str], *, prompt_kind: str | None = None) -> str:
        """Best-effort section label for a prompt suggestion row.

        This is used for:
        - rendering section headers in the minimal TUI suggestion list
        - section-jump navigation in picker-style prompts

        Row shape is generally: [insert kind menu info].
        """

        kind = str(prompt_kind or (self.prompt.kind if self.prompt is not None else "") or "")
        vals = [str(x) for x in list(row[:4])]
        while len(vals) < 4:
            vals.append("")

        try:
            if kind == "palette":
                return str(self._command_palette_section_label(vals))
            if kind == "topic":
                _single, plural = self._topic_section_names(str(vals[1] if len(vals) > 1 else ""))
                return str(plural)
            if kind == "recent":
                return str(self._recent_section_label(vals, by_project=True))
            if kind == "recentdir":
                return str(self._recent_section_label(vals, by_project=False))
            if kind == "binding":
                return str(self._binding_section_label(vals))
            if kind == "buffer":
                return str(self._buffer_section_label(vals))
            if kind == "mark":
                return str(self._mark_section_label(vals))
            if kind == "jump":
                return str(self._jump_section_label(vals))
            if kind == "plugin":
                return str(self._plugin_section_display_label(vals))
            if kind == "doc":
                return str(self._doc_section_label(vals))
            if kind == "helplink":
                return str(self.helplink_section_label(vals))
            if kind == "helpoutline":
                return str(self.help_outline_section_label(vals))
            if kind == "helpnav":
                k2 = str(vals[1] if len(vals) > 1 else "")
                if k2 == "heading":
                    return str(self.help_outline_section_label(vals))
                if k2 == "link":
                    return str(self.helplink_section_label(vals))
                return "Items"
        except Exception:
            pass

        return kind.title() if kind else "Items"

    def _prompt_section_starts(self) -> list[int]:
        """Return indices of the first row of each section in the suggestion list."""

        if self.prompt is None or not self.prompt.suggestion_rows:
            return []
        out: list[int] = []
        last = None
        for i, row in enumerate(self.prompt.suggestion_rows):
            lbl = self.prompt_row_section_label([str(x) for x in list(row[:4])])
            if lbl != last:
                out.append(i)
                last = lbl
        return out

    def prompt_suggest_next_section(self) -> bool:
        """Jump picker selection to the next section in the suggestion list."""

        if self.prompt is None:
            return False
        if self.prompt.kind in ("command", "find"):
            return False
        if not self.prompt.suggestion_rows:
            return False
        starts = self._prompt_section_starts()
        if not starts:
            return False
        i = int(self.prompt.suggest_index)
        # Find current section start index.
        cur_s = 0
        for si, st in enumerate(starts):
            if st <= i:
                cur_s = si
            else:
                break
        wrap = True
        try:
            wrap = bool(self.options.get("prompt.wrap"))
        except Exception:
            wrap = True
        if cur_s + 1 < len(starts):
            self.prompt.suggest_index = int(starts[cur_s + 1])
            return True
        if wrap:
            self.prompt.suggest_index = int(starts[0])
            return True
        self.prompt.suggest_index = int(starts[-1])
        return True

    def prompt_suggest_prev_section(self) -> bool:
        """Jump picker selection to the start of the current/previous section."""

        if self.prompt is None:
            return False
        if self.prompt.kind in ("command", "find"):
            return False
        if not self.prompt.suggestion_rows:
            return False
        starts = self._prompt_section_starts()
        if not starts:
            return False
        i = int(self.prompt.suggest_index)
        cur_s = 0
        for si, st in enumerate(starts):
            if st <= i:
                cur_s = si
            else:
                break
        cur_start = int(starts[cur_s])
        # If we're inside the section, jump to its start first.
        if i > cur_start:
            self.prompt.suggest_index = cur_start
            return True
        wrap = True
        try:
            wrap = bool(self.options.get("prompt.wrap"))
        except Exception:
            wrap = True
        if cur_s > 0:
            self.prompt.suggest_index = int(starts[cur_s - 1])
            return True
        if wrap:
            self.prompt.suggest_index = int(starts[-1])
            return True
        self.prompt.suggest_index = int(starts[0])
        return True

    def prompt_copy_selected(self) -> bool:
        """Copy the currently selected prompt row to the clipboard.

        Heuristic:
        - for link rows (kind == 'link'), copy the link target (col 2)
        - otherwise copy the displayed name/insert text (col 0)

        This is useful in docs pickers (copy link target without moving the
        buffer cursor) and is generic enough to be handy in other pickers.
        """

        row = self.prompt_current_row()
        if not row:
            return False
        name, kind, target, _info = [str(x or "") for x in row[:4]]
        out = ""
        if str(kind).strip().lower() == "link" and str(target).strip():
            out = str(target).strip()
        else:
            out = str(name).strip()
        if not out:
            return False
        self.set_clipboard_items([out], kind="items")
        self.message(f"copied\n{out}")
        return True

    def _path_completion_candidates(
        self,
        unquoted_prefix: str,
        *,
        at_eol: bool,
        quote: str | None = None,
        close_dirs: bool = False,
    ) -> list[str]:
        """Return filesystem path completion candidates for the command prompt.

        This is intentionally simple and portable:

        - String-based suggestions (no UI coupling).
        - Hidden files are only suggested when the user starts the name with '.'.
        - Directories get a trailing path separator so you can keep completing inside.
        - Files at end-of-line get a trailing space (dirs do not).

        Quoting policy (shell-ish, but tiny):

        - If the user already started a quote token (" or '), we complete inside
          that quote style.
        - If the user did *not* start a quote token, but the completion contains
          whitespace or a double quote, we auto-wrap the path in double quotes and
          escape internal backslashes and `"`.
        - For directory completions where quoting is active, we keep the closing
          quote *open* (unless `close_dirs=True`) so users can keep tabbing into
          the path.

        Note: This consults the current process working directory via pathlib/os.
        If a host embedding needs tighter sandboxing, it should gate filesystem
        access before exposing editor commands that rely on it.
        """
        import os
        from pathlib import Path

        typed = str(unquoted_prefix or "")
        # Split into (dirpart, namepart) preserving a trailing separator for dirs.
        dirpart, namepart = os.path.split(typed)
        if dirpart != "" and not dirpart.endswith(os.sep):
            dirpart = dirpart + os.sep

        # Special-case a bare '~' so users can type `open ~` then Tab.
        if typed == "~":
            dirpart, namepart = "~" + os.sep, ""

        # Resolve search directory for listing (expand ~, keep user-typed text for display).
        search_dir = Path(dirpart or ".").expanduser()
        try:
            if not search_dir.exists() or not search_dir.is_dir():
                return []
            entries = list(search_dir.iterdir())
        except OSError:
            return []

        show_hidden = namepart.startswith(".")
        max_items = 60 if typed == "" else 200

        def _escape_double(s: str) -> str:
            return s.replace("\\", "\\\\").replace('"', '\\"')

        def _render(path: str, *, is_dir: bool) -> str:
            # Decide whether we should quote even if the user didn't.
            needs_quote = any(ch.isspace() for ch in path) or ('"' in path)
            q = quote
            if q is None and needs_quote:
                q = '"'

            trail = " " if (at_eol and (not is_dir)) else ""

            if q is None:
                return path + trail

            body = path
            # Only escape for double quotes (posix-ish).
            if q == '"':
                body = _escape_double(body)

            # Keep quotes open for dirs so users can keep completing.
            if is_dir:
                return (q + body + q) if close_dirs else (q + body)
            return q + body + q + trail

        cands: list[tuple[int, str]] = []  # (kind, candidate) where kind=0 dir, 1 file
        for child in entries:
            nm = child.name
            if not show_hidden and nm.startswith("."):
                continue
            if not nm.startswith(namepart):
                continue
            try:
                is_dir = child.is_dir()
            except OSError:
                is_dir = False
            suffix = os.sep if is_dir else ""
            cand_path = f"{dirpart}{nm}{suffix}"
            cands.append((0 if is_dir else 1, _render(cand_path, is_dir=is_dir)))
            if len(cands) >= max_items:
                break

        # Sort dirs first, then lexicographically (case-sensitive, like many shells).
        cands.sort(key=lambda t: (t[0], t[1]))
        return [c for _k, c in cands]


    def _mx_prompt_completion_candidates(
        self,
        *,
        cmd: str,
        tok_i: int,
        prefix: str,
        toks: list[str],
    ) -> tuple[list[str], list[list[str]], int]:
        """Ask embedded micromax for extra prompt completion candidates.

        Lookup order:
          1) `ed.complete.<cmd>`
          2) `ed.complete`

        Supported completion-word contracts (best-effort):

            ( cmd tok_i prefix toks -- cands mode )
            ( cmd tok_i prefix toks -- cands rows mode )

        - cands: list of strings to insert into the prompt
        - rows: optional list of `[insert kind menu info]` annotations
        - mode: 0 = no candidates, 1 = add, 2 = replace

        This stays intentionally small, but the optional row contract lets
        plugins participate in the same metadata surface as built-in
        completions without forcing a UI choice.

        Errors are caught and surfaced as editor messages. The VM stack is
        restored after the call.
        """

        def _normalize_mode(value: object) -> int:
            if isinstance(value, bool):
                return 1 if value else 0
            if isinstance(value, int):
                return int(value)
            return 1 if value else 0

        def _normalize_rows(value: object, cands: list[str]) -> list[list[str]]:
            out: list[list[str]] = []
            if not isinstance(value, list):
                return out
            for i, item in enumerate(value):
                if i >= len(cands):
                    break
                if isinstance(item, list):
                    row = [str(x) for x in item[:4]]
                else:
                    row = [str(item)]
                while len(row) < 4:
                    row.append("")
                row[0] = cands[i]
                out.append(row[:4])
            return out

        vm = self.vm
        cmd = str(cmd)
        name_candidates = [f"ed.complete.{cmd}", "ed.complete"]

        for wname in name_candidates:
            if vm.find_word(wname) is None:
                continue

            depth = len(vm.stack)
            try:
                vm.stack.extend([cmd, int(tok_i), str(prefix), list(toks)])
                vm.eval(wname, filename="<editor-complete>")

                produced = vm.stack[depth:]
                if len(produced) < 2:
                    return ([], [], 0)

                cands = produced[-2]
                rows_obj: object = []
                mode = produced[-1]
                if len(produced) >= 3 and isinstance(produced[-2], list) and isinstance(produced[-3], list):
                    cands = produced[-3]
                    rows_obj = produced[-2]
                    mode = produced[-1]

                out: list[str] = []
                if isinstance(cands, list):
                    for x in cands:
                        out.append(str(x))

                # Sanity caps (avoid pathological suggestion lists).
                if len(out) > 400:
                    out = out[:400]

                rows = _normalize_rows(rows_obj, out)
                return (out, rows, _normalize_mode(mode))
            except Exception as e:
                try:
                    from micromax.vm import MicromaxError

                    if isinstance(e, MicromaxError):
                        self.message(vm.format_error(e))
                    else:
                        self.message(f"mx completion error: {e}")
                except Exception:
                    self.message(f"mx completion error: {e}")
                return ([], [], 0)
            finally:
                del vm.stack[depth:]

        return ([], [], 0)


    def _overlay_suggestion_rows(
        self,
        base_rows: list[list[str]],
        candidates: list[str],
        extra_candidates: list[str],
        extra_rows: list[list[str]],
    ) -> list[list[str]]:
        """Overlay plugin-provided suggestion rows onto inferred row metadata."""

        if not base_rows or not extra_candidates or not extra_rows:
            return base_rows

        out = [list(r[:4]) + [""] * max(0, 4 - len(r[:4])) for r in base_rows]
        index_by_insert: dict[str, int] = {}
        for i, cand in enumerate(candidates):
            index_by_insert.setdefault(str(cand), i)

        for i, cand in enumerate(extra_candidates):
            if i >= len(extra_rows):
                continue
            dst_i = index_by_insert.get(str(cand))
            if dst_i is None or dst_i >= len(out):
                continue
            row = [str(x) for x in list(extra_rows[i])[:4]]
            while len(row) < 4:
                row.append("")
            row[0] = str(candidates[dst_i])
            for j in range(1, 4):
                if row[j] != "":
                    out[dst_i][j] = row[j]
        return [r[:4] for r in out]


    def prompt_complete(self, *, direction: int = 1) -> bool:
        """Autocomplete / cycle suggestions in the active prompt.

        Intended to be bound to Tab (forward) and Shift-Tab (backward).
        Command prompts use token-aware completion; topic prompts use ranked
        command/action/word topic rows; binding prompts use ranked current
        binding rows.
        """
        if self.prompt is None or self.prompt.kind not in (
            "command",
            "palette",
            "topic",
            "binding",
            "buffer",
            "mark",
            "jump",
            "plugin",
            "recent",
            "recentdir",
            "doc",
            "helplink",
            "helpoutline",
            "helpnav",
        ):
            return False

        # If a suggestion session is active, cycle through candidates.
        if self.prompt.suggestions:
            step = 1 if int(direction) >= 0 else -1
            if self.prompt.text == self.prompt.suggest_base:
                idx = 0 if step > 0 else (len(self.prompt.suggestions) - 1)
            else:
                idx = self.prompt.suggest_index + step
            self.prompt.apply_suggestion(idx)
            return True

        if self.prompt.kind == "topic":
            ok = self._refresh_topic_prompt_suggestions()
            if ok:
                preview = ", ".join(str(c) for c in self.prompt.suggestions[:6])
                suffix = " ..." if len(self.prompt.suggestions) > 6 else ""
                self.message("topics: " + preview + suffix)
            return ok
        if self.prompt.kind == "binding":
            ok = self._refresh_binding_prompt_suggestions()
            if ok:
                preview = ", ".join(str(c) for c in self.prompt.suggestions[:6])
                suffix = " ..." if len(self.prompt.suggestions) > 6 else ""
                self.message("bindings: " + preview + suffix)
            return ok

        # Picker-style prompts: ensure a suggestion session exists, then cycle.
        if self.prompt.kind == "palette":
            return bool(self._refresh_palette_prompt_suggestions())
        if self.prompt.kind == "buffer":
            return bool(self._refresh_buffer_prompt_suggestions())
        if self.prompt.kind == "mark":
            return bool(self._refresh_mark_prompt_suggestions())
        if self.prompt.kind == "jump":
            return bool(self._refresh_jump_prompt_suggestions())
        if self.prompt.kind == "plugin":
            return bool(self._refresh_plugin_prompt_suggestions())
        if self.prompt.kind == "recent":
            return bool(self._refresh_recent_prompt_suggestions())
        if self.prompt.kind == "recentdir":
            return bool(self._refresh_recent_dir_prompt_suggestions())
        if self.prompt.kind == "doc":
            return bool(self._refresh_doc_prompt_suggestions())

        text = self.prompt.text
        cur = self.prompt.cursor

        def scan_tokens(s: str) -> list[tuple[str, int, int]]:
            """Return [(token, start, end), ...] using forgiving shell-ish rules.

            This is for completion only (not command execution). It is quote-aware
            (whitespace inside quotes stays inside the token) and handles a minimal
            subset of escapes so completions like `"a\\\"b"` stay one token.

            We don't attempt to fully emulate `/bin/sh` here; execution uses
            `shlex.split` in `parse_cmdline()`.
            """
            out: list[tuple[str, int, int]] = []
            start: int | None = None
            in_single = False
            in_double = False

            i = 0
            while i < len(s):
                ch = s[i]

                # Minimal escaping: outside single quotes, backslash escapes the
                # next character so it cannot terminate a quote.
                if ch == "\\" and not in_single:
                    if start is None:
                        start = i
                    i = i + 2 if (i + 1) < len(s) else i + 1
                    continue

                if ch == "'" and not in_double:
                    in_single = not in_single
                    if start is None:
                        start = i
                    i += 1
                    continue
                if ch == '"' and not in_single:
                    in_double = not in_double
                    if start is None:
                        start = i
                    i += 1
                    continue

                if (not in_single) and (not in_double) and ch.isspace():
                    if start is not None:
                        out.append((s[start:i], start, i))
                        start = None
                    i += 1
                    continue

                if start is None and not ch.isspace():
                    start = i

                i += 1

            if start is not None:
                out.append((s[start:len(s)], start, len(s)))
            return out

        spans = scan_tokens(text)
        toks = [t for t, _s, _e in spans]

        # Find the token under the cursor, or treat cursor as a new token.
        tok_i: int | None = None
        tok_start = tok_end = cur
        tok = ""
        for i, (t, s, e) in enumerate(spans):
            if s <= cur <= e:
                tok_i = i
                tok_start, tok_end = s, e
                tok = t
                break

        if tok_i is None:
            # cursor in whitespace
            tok_i = 0
            for _t, _s, e in spans:
                if e < cur:
                    tok_i += 1
            tok_start = tok_end = cur
            tok = ""

        # Quote-aware completion: if the current token begins with a quote, we
        # complete *within* it. For convenience we normalize away a trailing
        # matching quote when determining the prefix.
        quote: str | None = None
        quote_closed = False
        tok_inner = tok
        tok_norm = tok
        if tok.startswith(("'", '"')):
            quote = tok[0]
            rest = tok[1:]
            if rest.endswith(quote):
                quote_closed = True
                rest = rest[:-1]
            tok_inner = rest
            tok_norm = quote + rest

        cmd = toks[0] if toks else ""
        prefix = tok_norm

        # Avoid dumping huge suggestion lists on empty prefix.
        if prefix == "" and tok_i == 0:
            return False

        candidates, fuzzy_candidates = self._prompt_command_token_candidates(
            cmd=cmd,
            toks=toks,
            tok_i=tok_i,
            prefix=prefix,
            at_eol=(tok_end >= len(text)),
        )
        path_mode = False

        if (not candidates) and tok_i == 1 and cmd in ("open", "save", "cd"):
            # Filesystem completion for micro-style commands remains explicit
            # prefix completion; fuzzy path search is a separate future feature.
            candidates = self._path_completion_candidates(
                tok_inner,
                at_eol=(tok_end >= len(text)),
                quote=quote,
                close_dirs=quote_closed,
            )
            path_mode = bool(candidates)

        # Allow micromax plugins to extend/override completion.
        mx_cands, mx_rows, mx_mode = self._mx_prompt_completion_candidates(cmd=cmd, tok_i=tok_i, prefix=prefix, toks=toks)
        if mx_mode == 2:
            candidates = list(mx_cands)
            fuzzy_candidates = False
            path_mode = False
        elif mx_mode == 1 and mx_cands:
            if not candidates:
                candidates = list(mx_cands)
            else:
                for c in mx_cands:
                    if c not in candidates:
                        candidates.append(c)

        if not candidates:
            return False

        rows = self._prompt_suggestion_rows(
            cmd=cmd,
            toks=toks,
            tok_i=tok_i,
            candidates=candidates,
            path_mode=path_mode,
        )
        rows = self._overlay_suggestion_rows(rows, candidates, mx_cands, mx_rows)

        # Strip the added space for common-prefix calculation and headless
        # message/debug output.
        raw = [c[:-1] if c.endswith(" ") else c for c in candidates]

        import os as _os

        common = _os.path.commonprefix(raw) if (raw and (not fuzzy_candidates)) else ""

        if len(candidates) == 1:
            c = candidates[0]
            new = text[:tok_start] + c + text[tok_end:]
            self.set_prompt_text(new)
            self.prompt.set_cursor(tok_start + len(c))
            if fuzzy_candidates:
                self.message("fuzzy: " + raw[0])
            return True

        if common and len(common) > len(prefix):
            def _prefer_exact_common_candidate() -> bool:
                """Heuristic: prefer the exact candidate over starting a session.

                We only do this when the other matches are clearly "picker"
                variants.

                Rationale:
                - `he` should complete to `help ` even if `helppick` exists.
                - `tog` should *not* complete to `toggle ` when `togglelocal`
                  exists; the first Tab should expand to the common prefix
                  (`toggle`) and start a session.
                - `bind ... command:sh` completion should start a session rather
                  than snapping to the exact `command:show ` candidate.
                """

                if common not in raw:
                    return False
                others = [r for r in raw if r != common]
                if not others:
                    return False

                # Special-case `help` (and derived forms like
                # `command-edit:help`): it's almost always what the user meant
                # when typing `he`, even if helper commands like `helppick`,
                # `helpback`, and `helpfollow` exist.
                if common.endswith("help"):
                    return True

                def _is_pick_variant(r: str) -> bool:
                    if not r.startswith(common):
                        return False
                    suf = r[len(common) :]
                    return suf.startswith("pick") or suf.startswith("-pick") or suf.startswith("_pick")

                return all(_is_pick_variant(r) for r in others)

            if _prefer_exact_common_candidate():
                # If the common prefix itself is a full candidate, prefer it.
                #
                # Example: completing `he` with candidates `help` and
                # `helppick`. In that case we want the first Tab to land on
                # `help ` (a full command), not just insert `help` and require
                # another keypress.
                for cand in candidates:
                    rc = cand[:-1] if cand.endswith(" ") else cand
                    if rc == common:
                        c = cand
                        new = text[:tok_start] + c + text[tok_end:]
                        self.set_prompt_text(new)
                        self.prompt.set_cursor(tok_start + len(c))
                        if fuzzy_candidates:
                            self.message("fuzzy: " + common)
                        return True
            new = text[:tok_start] + common + text[tok_end:]
            self.set_prompt_text(new)
            self.prompt.set_cursor(tok_start + len(common))
            self.prompt.begin_suggestions(candidates, start=tok_start, end=(tok_start + len(common)), rows=rows)
            self.message("matches: " + ", ".join(raw))
            return True

        self.prompt.begin_suggestions(candidates, start=tok_start, end=tok_end, rows=rows)
        self.message(("fuzzy matches: " if fuzzy_candidates else "matches: ") + ", ".join(raw))
        return True

    # ----- command bar -----
    def exec_command_line(self, cmdline: str) -> bool:
        """Execute a command-bar line.

        If macro recording is enabled, successful command lines are recorded as
        macro steps *except* for macro-management commands themselves.
        """

        self._push_history("command", cmdline)
        cl = parse_cmdline(cmdline)
        if cl is None:
            return False

        if cl.name not in {"quit", "quit!"}:
            self._quit_armed = False


        if cl.name not in {"close", "close!"}:
            self._close_armed = False
            self._close_armed_name = ""

        if self.macro_recording and not self._macro_playing and cl.name != "macro":
            self._macro_buffer.append(MacroStep(kind="command", name="command", payload={"cmdline": cmdline}))

        return self.command_dispatcher.exec(self, cl)

    # ----- search -----
    def _sync_search_options(self) -> None:
        eb = self.cur()
        ignorecase = bool(self.options.get("ignorecase", local=eb.local_options))
        self.search.case_sensitive = not ignorecase

    def find(self, query: str, *, literal: bool | None = None, announce: bool = False) -> bool:
        self._sync_search_options()
        self.search.query = query
        if literal is not None:
            self.search.literal = bool(literal)

        eb = self.cur()
        self._normalize_cursor_lists(eb)
        start = eb.cursors[eb.primary]
        m = find_next(eb.buf, self.search, start=start)
        if m is None:
            self.message("find: not found" if announce else "not found")
            return False
        eb.cursors[eb.primary] = m
        self.search.last_match = m
        if announce:
            self.message(self.format_search_target(prefix="find"))
        return True

    def find_next(self) -> bool:
        if not self.search.query:
            self.message("findnext: no active search")
            return False
        self._sync_search_options()
        eb = self.cur()
        self._normalize_cursor_lists(eb)
        start = eb.cursors[eb.primary]
        start2 = Cursor(start.line, start.col + 1)
        m = find_next(eb.buf, self.search, start=start2)
        if m is None:
            self.message("findnext: not found")
            return False
        eb.cursors[eb.primary] = m
        self.search.last_match = m
        self.message(self.format_search_target(prefix="findnext"))
        return True

    def find_prev(self) -> bool:
        if not self.search.query:
            self.message("findprev: no active search")
            return False
        self._sync_search_options()
        eb = self.cur()
        self._normalize_cursor_lists(eb)
        start = eb.cursors[eb.primary]
        m = find_prev(eb.buf, self.search, start=start)
        if m is None:
            self.message("findprev: not found")
            return False
        eb.cursors[eb.primary] = m
        self.search.last_match = m
        self.message(self.format_search_target(prefix="findprev"))
        return True

    # ----- query replace (interactive) -----
    def begin_query_replace(self, search: str, value: str, *, literal: bool = False) -> bool:
        """Start an interactive query-replace session.

        This is deliberately small and headless:
        - current match is selected
        - y/Enter replaces, n skips, a replaces all remaining, l replaces and quits, q/Esc quits
        """

        # Protected buffers (help/docs) should reject edits.
        try:
            if hasattr(self, "is_protected_buffer") and self.is_protected_buffer():
                self.message("qreplace: read-only buffer")
                return False
        except Exception:
            pass

        eb = self.cur()
        self._normalize_cursor_lists(eb)
        p = eb.primary

        sess = QueryReplaceSession(
            buffer_name=str(eb.name),
            search=str(search),
            value=str(value),
            literal=bool(literal),
            next_start=Cursor(eb.cursors[p].line, eb.cursors[p].col),
        )

        # Match semantics follow the editor's ignorecase option (like find/FindNext).
        ignorecase = bool(self.options.get("ignorecase", local=eb.local_options))
        sess.case_sensitive = not ignorecase

        if not sess.literal:
            try:
                flags_re = re.IGNORECASE if not sess.case_sensitive else 0
                sess.regex = re.compile(sess.search, flags_re)
            except re.error as e:
                self.message(f"qreplace: invalid regex: {e}")
                return False
            sess.repl_py = convert_replacement_template(sess.value)
        sess.before = self._snapshot_buffer_state(eb)

        # Best-effort count of matches remaining from the starting cursor.
        try:
            text0 = str(sess.before[0]) if sess.before is not None else eb.buf.get_text()
            start_i0 = cursor_to_index(eb.buf, sess.next_start)
            if sess.literal:
                if sess.search:
                    hay = text0 if sess.case_sensitive else text0.lower()
                    needle = sess.search if sess.case_sensitive else sess.search.lower()
                    pos = start_i0
                    total = 0
                    while True:
                        i = hay.find(needle, pos)
                        if i < 0:
                            break
                        total += 1
                        pos = i + max(1, len(needle))
                    sess.total = total
            else:
                if sess.regex is not None:
                    sess.total = sum(1 for _m in sess.regex.finditer(text0, pos=start_i0))
        except Exception:
            sess.total = 0

        self.qreplace = sess

        # Enter a capture keymode so global bindings can't fire accidentally.
        self.push_key_mode("qreplace", capture=True)
        return self._qreplace_select_next()

    def _qreplace_clear_primary_selection(self) -> None:
        eb = self.cur()
        self._normalize_cursor_lists(eb)
        eb.sel_anchors[eb.primary] = None

    def _qreplace_select_next(self) -> bool:
        sess = self.qreplace
        if sess is None:
            return False

        eb = self.cur()
        if str(eb.name) != str(sess.buffer_name):
            # If the user switched buffers mid-session, bail safely.
            return self._qreplace_finish(canceled=True)

        self._normalize_cursor_lists(eb)
        p = eb.primary

        text = eb.buf.get_text()
        start_i = cursor_to_index(eb.buf, sess.next_start)

        # Find next match.
        if sess.literal:
            if sess.case_sensitive:
                i = text.find(sess.search, start_i)
            else:
                i = text.lower().find(sess.search.lower(), start_i)
            if i < 0:
                if sess.examined == 0 and sess.replaced == 0:
                    # Nothing matched at all; treat as a normal "not found".
                    self.key_mode_stack = [km for km in self.key_mode_stack if km.name != "qreplace"]
                    self.qreplace = None
                    self.message("qreplace: not found")
                    return False
                return self._qreplace_finish(canceled=False)
            j = i + len(sess.search)
            sess.match_start = index_to_cursor(eb.buf, i)
            sess.match_end = index_to_cursor(eb.buf, j)
            sess.match_repl = sess.value
        else:
            assert sess.regex is not None
            m = sess.regex.search(text, pos=start_i)
            if m is None:
                if sess.examined == 0 and sess.replaced == 0:
                    self.key_mode_stack = [km for km in self.key_mode_stack if km.name != "qreplace"]
                    self.qreplace = None
                    self.message("qreplace: not found")
                    return False
                return self._qreplace_finish(canceled=False)
            i, j = m.span()
            sess.match_start = index_to_cursor(eb.buf, i)
            sess.match_end = index_to_cursor(eb.buf, j)
            try:
                sess.match_repl = m.expand(sess.repl_py)
            except Exception:
                sess.match_repl = sess.value

        sess.examined += 1

        # Select the match so it is visible in the TUI.
        eb.sel_anchors[p] = Cursor(sess.match_start.line, sess.match_start.col)  # type: ignore[union-attr]
        eb.cursors[p] = Cursor(sess.match_end.line, sess.match_end.col)  # type: ignore[union-attr]

        extra = f"match {sess.examined}"
        if sess.total:
            extra += f"/{sess.total}"

        self.message(
            f"qreplace: y/Enter replace, n skip, a all, l last, q/Esc quit  ({sess.replaced} replaced; {extra})"
        )
        return True

    def _qreplace_apply_current(self) -> bool:
        sess = self.qreplace
        if sess is None or sess.match_start is None or sess.match_end is None:
            return False
        eb = self.cur()
        if str(eb.name) != str(sess.buffer_name):
            return self._qreplace_finish(canceled=True)

        self._normalize_cursor_lists(eb)
        p = eb.primary

        cur = eb.buf.replace_range(sess.match_start, sess.match_end, sess.match_repl)
        eb.cursors[p] = cur
        eb.sel_anchors[p] = None
        sess.replaced += 1
        sess.next_start = Cursor(cur.line, cur.col)
        return True

    def qreplace_yes(self) -> bool:
        if not self._qreplace_apply_current():
            return False
        return self._qreplace_select_next()

    def qreplace_no(self) -> bool:
        sess = self.qreplace
        if sess is None or sess.match_end is None:
            return False
        # Skip: continue search after the end of the current match.
        sess.next_start = Cursor(sess.match_end.line, sess.match_end.col)
        self._qreplace_clear_primary_selection()
        return self._qreplace_select_next()

    def qreplace_last(self) -> bool:
        if not self._qreplace_apply_current():
            return False
        return self._qreplace_finish(canceled=False)

    def qreplace_all(self) -> bool:
        if self.qreplace is None:
            return False
        # Replace current + all remaining matches without pausing.
        while self.qreplace is not None:
            sess = self.qreplace
            if sess is None or sess.match_start is None or sess.match_end is None:
                break
            self._qreplace_apply_current()
            if self.qreplace is None:
                break
            self._qreplace_select_next()
        return True

    def qreplace_quit(self) -> bool:
        return self._qreplace_finish(canceled=True)

    def _qreplace_finish(self, *, canceled: bool) -> bool:
        sess = self.qreplace
        if sess is None:
            return False

        eb = self.cur()
        if str(eb.name) == str(sess.buffer_name):
            self._normalize_cursor_lists(eb)
            eb.sel_anchors[eb.primary] = None

            after = self._snapshot_buffer_state(eb)
            if sess.before is not None and sess.before != after and sess.replaced > 0:
                self._record_undo_snapshot(eb, sess.before, after, "qreplace")

        # Drop the capture mode.
        self.key_mode_stack = [km for km in self.key_mode_stack if km.name != "qreplace"]
        self.qreplace = None

        if canceled:
            self.message(f"qreplace: canceled ({sess.replaced} replaced)")
        else:
            self.message(f"qreplace: done ({sess.replaced} replaced)")
        return True

    # ----- runtime reload (plugins, bindings, etc.) -----
    def reload_runtime(self) -> bool:
        self.keymap = Keymap()
        self._install_builtin_keymode_bindings()
        if not self.plugin_manager:
            self.message("reloaded (no plugins)")
            return True
        names = list(self.plugin_manager.plugins.keys())
        for n in names:
            self.plugin_manager.reload(n)
        self.message("reloaded")
        return True

    # ----- macros -----
    def start_macro(self, name: str = "last") -> bool:
        """Start recording a macro into `name`.

        By default, this records into "last" (micro-style). Recording captures the
        actions/commands the editor runs, plus the action input snapshot needed
        to replay those actions deterministically.
        """
        if self._macro_playing or self.macro_recording:
            return False
        nm = str(name or "last")
        self._macro_target = nm
        self._macro_prev_last = list(self.macro)
        self._macro_buffer.clear()
        self.macro_recording = True
        self.message(f"macro: recording ({nm})")
        return True

    def stop_macro(self) -> bool:
        """Stop recording, saving the macro to its target name and to 'last'."""
        if self._macro_playing or not self.macro_recording:
            return False
        self.macro_recording = False
        steps = list(self._macro_buffer)
        self._macro_buffer.clear()

        # Save into 'last' (mutate list to keep stable reference).
        self.macro[:] = steps
        # Also save into the target name.
        self.macros[self._macro_target] = list(steps)
        self.macros["last"] = self.macro

        self.message(f"macro: saved {len(steps)} steps ({self._macro_target})")
        return True

    def cancel_macro(self) -> bool:
        """Stop recording and discard recorded steps (restore previous last macro)."""
        if self._macro_playing or not self.macro_recording:
            return False
        self.macro_recording = False
        self._macro_buffer.clear()
        if self._macro_prev_last is not None:
            self.macro[:] = list(self._macro_prev_last)
            self.macros["last"] = self.macro
        self.message("macro: canceled")
        return True

    def toggle_macro(self) -> bool:
        """Toggle recording of the 'last' macro (micro-style)."""
        return self.stop_macro() if self.macro_recording else self.start_macro("last")

    def play_macro(self, name: str = "last", *, count: int = 1) -> bool:
        """Play a recorded macro by name (default: 'last')."""
        nm = str(name or "last")
        try:
            want_count = int(count)
        except Exception:
            want_count = 0
        if self._macro_playing:
            return False
        if want_count <= 0:
            self.message("macro play: count must be > 0")
            return False
        steps = self.macros.get(nm, None)
        if steps is None and nm == "last":
            steps = self.macro
        if not steps:
            self.message(f"macro play: no such macro: {nm}")
            return False

        steps = list(steps)
        self._macro_playing = True
        try:
            for _ in range(want_count):
                for step in steps:
                    if step.kind == "action":
                        # restore input snapshot
                        self.input = dict(step.payload.get("input", {}))
                        self.run_action(step.name)
                    elif step.kind == "command":
                        self.exec_command_line(str(step.payload.get("cmdline", "")))
        finally:
            self._macro_playing = False
        step_word = "step" if len(steps) == 1 else "steps"
        self.message(f"macro: played {nm} x{want_count} ({len(steps)} {step_word})")
        return True

    def macro_names(self) -> list[str]:
        return sorted(self.macros.keys())

    def macro_list_entries(self) -> list[str]:
        """Return tiny human-facing macro inventory rows.

        Policy:
        - omit the default empty ``last`` slot so ``macro list`` does not pretend
          an unsaved macro already exists
        - keep names sorted and show recorded step counts for quick inspection
        """

        out: list[str] = []
        for name in self.macro_names():
            steps = list(self.macros.get(str(name), self.macro))
            if str(name) == "last" and not steps:
                continue
            count = len(steps)
            step_word = "step" if count == 1 else "steps"
            out.append(f"{name} ({count} {step_word})")
        return out

    def macro_list_message(self) -> str:
        """Return the tiny user-facing ``macro list`` summary string.

        Keep the visible inventory count-aware in both the empty and non-empty
        cases so tiny automation inspection does not switch dialects exactly
        when the entry count drops to zero.
        """

        entries = self.macro_list_entries()
        head = f"macros: {len(entries)} macro(s)"
        if not entries:
            return head
        return head + ", " + ", ".join(entries)

    def get_macro(self, name: str = "last") -> list[MacroStep]:
        return list(self.macros.get(str(name), self.macro))

    def set_macro(self, name: str, steps: list[MacroStep]) -> None:
        nm = str(name or "last")
        if nm == "last":
            self.macro[:] = list(steps)
            self.macros["last"] = self.macro
        else:
            self.macros[nm] = list(steps)


# ----- action execution -----
    def run_action(self, name: str) -> bool:
        act = self.actions.get(name)
        if act is None:
            raise KeyError(f"Unknown action: {name}")
        try:
            eb0 = self.cur()
            before_ver = int(getattr(eb0.buf, "version", 0))
        except Exception:
            eb0 = None  # type: ignore[assignment]
            before_ver = 0
        self._emit_mx_hook("ed.pre-action", name)

        if self.macro_recording and not self._macro_playing and name not in {"ToggleMacro", "PlayMacro", "CancelMacro"}:
            # Snapshot only the parts of input needed by common actions.
            self._macro_buffer.append(MacroStep(kind="action", name=name, payload={"input": dict(self.input)}))

        protected = False
        try:
            if eb0 is None:
                eb0 = self.cur()
            protected = bool(self.options.get("readonly", local=getattr(eb0, "local_options", {})))
        except Exception:
            protected = False

        if protected and str(name) in MUTATING_ACTIONS:
            self.message(f"{name}: read-only buffer")
            ok = False
        else:
            ok = bool(act.fn(self))

        # Lifecycle-ish notification: did this action mutate the active buffer?
        try:
            eb1 = self.cur()
            after_ver = int(getattr(eb1.buf, "version", 0))
            if ok and after_ver != before_ver:
                self._note_buffer_changed(eb1)
                self._emit_mx_hook("ed.on-change", str(eb1.name), str(name))
        except Exception:
            pass

        # Keep multi-cursor invariants stable after every action.
        try:
            eb = self.cur()
            self._normalize_cursor_lists(eb)
        except Exception:
            eb = None  # type: ignore[assignment]

        # Softwrap vertical motion wants a stable per-cursor "goal" x (visual column).
        # We update it after most actions, but avoid overwriting it after vertical
        # visual moves (Up/Down/PageUp/PageDown + selection variants), where we want
        # to preserve the goal even when clamped by short wrap rows.
        try:
            if eb is not None and bool(self.options.get("softwrap", local=eb.local_options)):
                if name not in {"CursorUp", "CursorDown", "PageUp", "PageDown", "SelectUp", "SelectDown"}:
                    w = int(self.viewport_width) if int(self.viewport_width) > 0 else 1
                    for i, c in enumerate(eb.cursors):
                        cid = int(eb.cursor_ids[i]) if i < len(eb.cursor_ids) else i
                        _y, x = self._cursor_visual_yx(eb, c, w=w)
                        eb.goal_x_by_cursor[cid] = int(x)
        except Exception:
            pass

        # Keep viewport aligned with the primary cursor for UI layers.
        try:
            self.ensure_cursor_visible()
        except Exception:
            pass

        self._emit_mx_hook("ed.on-action", name, 1 if ok else 0)
        return ok

    def _run_action_spec(self, spec: str) -> bool:
        s = spec.lstrip()

        if s.startswith("command:"):
            return self.exec_command_line(s[len("command:") :])
        if s.startswith("command-edit:"):
            self.enter_prompt("command", prefill=s[len("command-edit:") :])
            return True
        if s.startswith("mx:"):
            code = s[len("mx:") :]
            try:
                self.vm.eval(code, filename="<keybinding>")
                return True
            except Exception as e:
                self.message(str(e))
                return False

        return self.run_action(s.strip())

    def run_action_chain(self, spec: str) -> bool:
        """Execute a micro-style action chain string."""
        steps = parse_action_chain(spec)
        last_ok = False
        for step in steps:
            last_ok = self._run_action_spec(step.action)
            if step.sep == ",":
                continue
            if step.sep == "|" and last_ok:
                break
            if step.sep == "&" and not last_ok:
                break
        return last_ok

    # ----- clipboard helpers -----
    def clipboard_text(self) -> str:
        if self.clipboard_kind == "lines":
            if not self.clipboard_items:
                return ""
            return "\n".join(self.clipboard_items) + "\n"
        return "\n".join(self.clipboard_items)

    def _smartpaste_indent_prefix(self, line: str, col: int) -> str:
        """Return the indentation prefix smartpaste may reuse for multi-line paste.

        We intentionally keep this tiny and conservative:
          - only whitespace before the insertion point counts
          - pastes in the middle of text do not gain extra indent
          - tabs/spaces are preserved exactly as they appear on the line
        """

        col2 = max(0, min(int(col), len(line)))
        prefix = line[:col2]
        if prefix and any(ch not in (" ", "\t") for ch in prefix):
            return ""
        return prefix

    def _smartpaste_text(self, text: str, *, line: str, col: int) -> str:
        """Return a best-effort smart-indented paste payload.

        Inspired by micro's `smartpaste` option, but deliberately conservative:
        only multi-line pastes of blocks whose minimum non-empty indentation is
        zero are shifted, and only by the whitespace prefix that already exists
        before the insertion point.
        """

        if not bool(self.options.get("smartpaste")):
            return text
        if "\n" not in text:
            return text

        prefix = self._smartpaste_indent_prefix(line, col)
        if not prefix:
            return text

        parts = text.split("\n")
        nonempty = [part for part in parts if part != ""]
        if len(nonempty) <= 1:
            return text

        min_indent: int | None = None
        for part in nonempty:
            lead = 0
            while lead < len(part) and part[lead] in (" ", "\t"):
                lead += 1
            if min_indent is None or lead < min_indent:
                min_indent = lead
        if (min_indent or 0) > 0:
            return text

        out = [parts[0]]
        for part in parts[1:]:
            if part:
                out.append(prefix + part)
            else:
                out.append(part)
        return "\n".join(out)
    def set_clipboard_items(self, items: list[str], *, kind: str = "items") -> None:
        self.clipboard_items = list(items)
        self.clipboard_kind = kind
        # Track source so UI layers can avoid exporting script-driven clipboard
        # updates to privileged backends unless explicitly enabled.
        try:
            self.clipboard_from_script = bool(self.in_script_context())
        except Exception:
            self.clipboard_from_script = False
        self.clipboard_serial = int(getattr(self, 'clipboard_serial', 0)) + 1
    def _paste_reset(self) -> None:
        self._cutline_accum = False

    def clipboard_terminal_export_sequence(self) -> tuple[str | None, str]:
        """Return an OSC 52 sequence for exporting the clipboard (best-effort).

        This is primarily used by the curses TUI when:
          - clipboard=terminal
          - clipboard.osc52=true

        Safety: if the clipboard change was triggered in script context, we
        only allow export when cap.clipboard-write is enabled.

        Returns (seq, err). When seq is None, err may contain a human hint.
        """

        try:
            if str(self.options.get('clipboard') or '') != 'terminal':
                return (None, '')
            if not bool(self.options.get('clipboard.osc52')):
                return (None, '')
        except Exception:
            return (None, '')

        # Script-driven clipboard exports are gated.
        if bool(getattr(self, 'clipboard_from_script', False)) and not bool(self.options.get('cap.clipboard-write')):
            return (None, 'clipboard export disabled for scripts (set cap.clipboard-write true)')

        try:
            max_bytes = int(self.options.get('clipboard.osc52.max') or 0)
        except Exception:
            max_bytes = 0

        try:
            from .osc52 import osc52_sequence
        except Exception as e:
            return (None, f'osc52 unavailable: {e}')

        return osc52_sequence(self.clipboard_text(), max_bytes=max_bytes)


    def clipboard_external_export(self) -> tuple[bool, str]:
        """Best-effort export of the clipboard via external tools.

        Used primarily by UI layers when clipboard=external.

        Safety: script-originated clipboard updates are gated by
        cap.clipboard-write.

        Returns (ok, err). When ok is False, err may contain a human hint.
        """

        try:
            if str(self.options.get('clipboard') or '') != 'external':
                return (False, '')
        except Exception:
            return (False, '')

        # Script-driven clipboard exports are gated.
        if bool(getattr(self, 'clipboard_from_script', False)) and not bool(self.options.get('cap.clipboard-write')):
            return (False, 'clipboard export disabled for scripts (set cap.clipboard-write true)')

        try:
            cmd = str(self.options.get('clipboard.external.cmd') or '')
            args = str(self.options.get('clipboard.external.args') or '')
        except Exception:
            cmd = ''
            args = ''

        try:
            from .clipboard_external import detect_external_clipboard_cmd, parse_override
        except Exception as e:
            return (False, f'external clipboard unavailable: {e}')

        cc = parse_override(cmd, args) or detect_external_clipboard_cmd()
        if cc is None:
            # Avoid spamming the user; UI layers may show this once.
            if not bool(getattr(self, '_clipboard_external_warned', False)):
                setattr(self, '_clipboard_external_warned', True)
            return (False, 'no external clipboard tool found (try wl-copy/xclip/xsel/pbcopy/clip)')

        import subprocess

        try:
            timeout = float(self.options.get('clipboard.external.timeout') or 1.0)
        except Exception:
            timeout = 1.0

        try:
            p = subprocess.run(
                list(cc.argv),
                input=self.clipboard_text(),
                text=True,
                encoding='utf-8',
                errors='replace',
                timeout=timeout if timeout and timeout > 0 else None,
                capture_output=True,
                check=False,
            )
        except Exception as e:
            return (False, f'clipboard tool failed: {e}')

        if int(getattr(p, 'returncode', 1) or 0) != 0:
            err = ''
            try:
                err = (p.stderr or '').strip()
            except Exception:
                err = ''
            if not err:
                err = f'clipboard tool exited {p.returncode}'
            return (False, err)

        return (True, '')



    def clipboard_external_import_text(self) -> tuple[str | None, str]:
        """Best-effort import of clipboard text via external tools.

        Used primarily by editor actions (Paste) and hostcalls when
        clipboard=external.

        Safety: in script context, imports are gated by cap.clipboard-read.
        Interactive imports remain allowed.

        Returns (text, err). When text is None, err may contain a human hint.
        """

        try:
            if str(self.options.get('clipboard') or '') != 'external':
                return (None, 'clipboard backend is not external (set clipboard external)')
        except Exception:
            return (None, 'clipboard backend is not external (set clipboard external)')

        # Script-driven clipboard imports are gated.
        try:
            if bool(self.in_script_context()) and not bool(self.options.get('cap.clipboard-read')):
                return (None, 'clipboard import disabled for scripts (set cap.clipboard-read true)')
        except Exception:
            pass

        try:
            cmd = str(self.options.get('clipboard.external.readcmd') or '')
            args = str(self.options.get('clipboard.external.readargs') or '')
        except Exception:
            cmd = ''
            args = ''

        try:
            from .clipboard_external import detect_external_clipboard_read_cmd, parse_override
        except Exception as e:
            return (None, f'external clipboard unavailable: {e}')

        cc = parse_override(cmd, args) or detect_external_clipboard_read_cmd()
        if cc is None:
            return (None, 'no external clipboard read tool found (try wl-paste/xclip/xsel/pbpaste/powershell)')

        import subprocess

        try:
            timeout = float(self.options.get('clipboard.external.readtimeout') or 1.0)
        except Exception:
            timeout = 1.0

        try:
            pr = subprocess.run(
                list(cc.argv),
                input=None,
                capture_output=True,
                check=False,
                timeout=timeout if timeout and timeout > 0 else None,
            )
        except Exception as e:
            return (None, f'clipboard read tool failed: {e}')

        if int(getattr(pr, 'returncode', 1) or 0) != 0:
            err = ''
            try:
                err = (pr.stderr or b'').decode('utf-8', errors='replace').strip()
            except Exception:
                err = ''
            if not err:
                err = f'clipboard read tool exited {pr.returncode}'
            return (None, err)

        try:
            out = (pr.stdout or b'').decode('utf-8', errors='replace')
        except Exception:
            out = ''
        return (out, '')
    # ----- defaults -----
    def _install_default_options(self) -> None:
        self.options.register("ignorecase", True, kind="bool", doc="case-insensitive searching")
        self.options.register("incsearch", True, kind="bool", doc="incremental search as you type")
        self.options.register("hlsearch", False, kind="bool", doc="highlight matches (UI layer)")
        self.options.register("hltrailingws", False, kind="bool", doc="highlight visible trailing whitespace (UI layer)")
        self.options.register("cursorline", True, kind="bool", doc="highlight the current visible row (UI layer)")
        self.options.register(
            "matchbrace",
            True,
            kind="bool",
            doc="highlight matching braces under or just left of the cursor (UI layer)",
        )
        self.options.register(
            "matchbraceleft",
            True,
            kind="bool",
            doc="match braces immediately left of the cursor too (UI layer)",
        )
        self.options.register(
            "matchbracestyle",
            "underline",
            kind="enum",
            enum=["underline", "highlight"],
            doc="matchbrace: render visible matches with underline or highlight (UI layer)",
        )


        # Paste aggregation: when enabled, UI layers may aggregate bursts of
        # character key events into a single insert so terminal pastes don't
        # trigger auto-indent/auto-pairs on a per-key basis. (micro-esque)
        self.options.register(
            "paste",
            False,
            kind="bool",
            doc="aggregate paste bursts (UI layer; enable temporarily if your terminal lacks bracketed paste)",
        )

        self.options.register(
            "clipboard",
            "internal",
            kind="enum",
            enum=["internal", "external", "terminal"],
            doc="clipboard backend (internal/external/terminal)",
        )


        # Terminal clipboard export (OSC 52). UI layers can optionally export
        # the editor's clipboard to the system clipboard via terminal escape
        # sequences. This is best-effort (terminal support varies).
        self.options.register(
            "clipboard.osc52",
            True,
            kind="bool",
            doc="clipboard=terminal: export copies via OSC 52 (TUI, best-effort)",
        )
        self.options.register(
            "clipboard.osc52.max",
            100000,
            kind="int",
            doc="clipboard=terminal: max UTF-8 bytes to export via OSC 52 (0=unlimited)",
        )

        # External clipboard export (best-effort). UI layers may use these
        # settings to pipe copied text to a system clipboard tool.
        self.options.register(
            "clipboard.external.cmd",
            "",
            kind="str",
            doc="clipboard=external: override clipboard tool command (empty=auto-detect)",
        )
        self.options.register(
            "clipboard.external.args",
            "",
            kind="str",
            doc="clipboard=external: override clipboard tool args (shell-like string)",
        )
        self.options.register(
            "clipboard.external.timeout",
            1.0,
            kind="float",
            doc="clipboard=external: timeout (seconds) for clipboard tool",
        )

        # External clipboard import (best-effort). Paste may use these settings
        # to read the system clipboard via a platform clipboard tool.
        self.options.register(
            "clipboard.external.readcmd",
            "",
            kind="str",
            doc="clipboard=external: override clipboard read command (empty=auto-detect)",
        )
        self.options.register(
            "clipboard.external.readargs",
            "",
            kind="str",
            doc="clipboard=external: override clipboard read args (shell-like string)",
        )
        self.options.register(
            "clipboard.external.readtimeout",
            1.0,
            kind="float",
            doc="clipboard=external: timeout (seconds) for clipboard read tool",
        )
        self.options.register(
            "clipboard.external.import",
            True,
            kind="bool",
            doc="clipboard=external: on Paste, import from system clipboard (best-effort)",
        )

        # Capability gate: allow script-driven clipboard exports when a privileged
        # clipboard backend is in use (terminal/external). Interactive copy/cut
        # remains allowed; this only affects exports triggered in script context.
        self.options.register(
            "cap.clipboard-write",
            False,
            kind="bool",
            doc="allow scripts to export clipboard to system clipboard (terminal/external)",
        )

        # Capability gate: allow scripts to read/import the system clipboard via
        # external tools. Interactive paste remains allowed.
        self.options.register(
            "cap.clipboard-read",
            False,
            kind="bool",
            doc="allow scripts to import system clipboard via external tools",
        )

        self.options.register("jumplist.auto", True, kind="bool", doc="auto-push jumplist for jump commands (goto/jump)")

        self.options.register("indent", "    ", kind="str", doc="indent prefix")
        self.options.register(
            "fileformat",
            "unix",
            kind="enum",
            enum=["unix", "dos"],
            doc="line ending format used when saving this buffer (unix=LF, dos=CRLF)",
        )
        self.options.register(
            "encoding",
            "utf-8",
            kind="str",
            doc="text encoding used when opening and saving this buffer",
        )
        self.options.register(
            "fastdirty",
            False,
            kind="bool",
            doc="use a cheap modified flag instead of comparing buffer content against the last clean baseline",
        )
        self.options.register(
            "autoindent",
            True,
            kind="bool",
            doc="preserve the current line's leading whitespace when inserting a newline",
        )
        self.options.register(
            "autosave",
            0,
            kind="int",
            doc="automatically save dirty path-backed buffers every N seconds (0=off)",
        )
        self.options.register(
            "readonly",
            False,
            kind="bool",
            doc="disallow edits and saves in the current buffer unless locally overridden",
        )
        self.options.register(
            "keepautoindent",
            False,
            kind="bool",
            doc="keep whitespace-only autoindent lines when pressing Enter again",
        )

        # Tabs: we follow micro-esque naming so config muscle-memory ports.
        # - tabsize controls *display* width (and how many spaces we insert when
        #   tabstospaces=true).
        # - tabstospaces controls whether the Tab key inserts '\t' or spaces.
        # Note: the core buffer is character-based; UI layers render tabs using
        # tabsize and can choose their own visual policies.
        self.options.register("tabsize", 4, kind="int", doc="tab width in spaces (display + tab insertion)")
        self.options.register("tabstospaces", True, kind="bool", doc="convert typed tabs to spaces")
        self.options.register(
            "tabmovement",
            False,
            kind="bool",
            doc="treat leading runs of tabsize spaces like one tab stop for left/right motion",
        )
        self.options.register(
            "rmtrailingws",
            False,
            kind="bool",
            doc="trim trailing spaces/tabs from lines when saving the buffer",
        )
        self.options.register(
            "eofnewline",
            False,
            kind="bool",
            doc="ensure non-empty saves end with a final newline",
        )
        self.options.register(
            "mkparents",
            False,
            kind="bool",
            doc="create missing parent directories automatically when saving",
        )

        self.options.register("page.height", 30, kind="int", doc="page movement size for PageUp/PageDown")
        self.options.register(
            "pageoverlap",
            0,
            kind="int",
            doc="rows to keep visible between PageUp/PageDown moves",
        )
        self.options.register(
            "prompt.page",
            8,
            kind="int",
            doc="picker prompts: PageUp/PageDown selection jump size (rows)",
        )
        self.options.register(
            "prompt.wrap",
            True,
            kind="bool",
            doc="picker prompts: wrap selection at ends (true) or clamp (false)",
        )

        # Docs browser: controls how `helplinkpick` sections are labeled.
        # - kind: legacy Docs/Files/External grouping
        # - heading: group links by nearest markdown heading (Top/Links/...)
        self.options.register(
            "help.linksections",
            "kind",
            kind="enum",
            enum=["kind", "heading"],
            doc="docs browser: helplinkpick section labels (kind|heading)",
        )
        # Viewport defaults for UI layers. A future TUI should call `ed.viewport!`
        # on startup and on resize to keep these current.
        self.options.register("viewport.height", 30, kind="int", doc="viewport height (lines) for UI scrolling")
        self.options.register("viewport.width", 80, kind="int", doc="viewport width (cols) for UI horizontal scrolling")
        self.options.register(
            "scrollmargin",
            0,
            kind="int",
            doc="minimum vertical context rows to keep around the cursor while scrolling",
        )
        self.options.register(
            "colorcolumn",
            0,
            kind="int",
            doc="highlight a single visible guide column in the TUI/editor view (0=off)",
        )
        self.options.register(
            "scrollbar",
            False,
            kind="bool",
            doc="show a tiny right-edge scrollbar cue in the TUI/editor view",
        )
        self.options.register(
            "scrollbarchar",
            "|",
            kind="str",
            doc="character used for the tiny right-edge scrollbar cue (TUI/editor view)",
        )
        self.options.register(
            "showchars",
            "",
            kind="str",
            doc="show tiny visible replacements for spaces/tabs in the TUI/editor view (micro-esque key=value list)",
        )
        self.options.register(
            "overflowmarkers",
            False,
            kind="bool",
            doc="show tiny left/right markers for horizontally clipped lines in the TUI/editor view",
        )
        self.options.register("softwrap", False, kind="bool", doc="soft-wrap long lines instead of horizontal scrolling")
        self.options.register("wordwrap", False, kind="bool", doc="wrap softwrapped lines at spaces when possible")
        self.options.register("softwrap.contindent", -1, kind="int", doc="softwrap continuation indent columns (-1=auto, 0=off)")
        self.options.register("ruler", False, kind="bool", doc="show line numbers in the TUI/editor view")
        self.options.register("relativeruler", False, kind="bool", doc="show relative line numbers when ruler is enabled")
        self.options.register(
            "keymenu",
            False,
            kind="bool",
            doc="show a tiny nano-style key menu in the curses TUI",
        )
        self.options.register(
            "hltaberrors",
            False,
            kind="bool",
            doc="highlight tabs when spaces are expected and leading spaces when tabs are expected",
        )

        # Recent files MRU + prompt history (optional persistence).
        #
        # Persistence touches the host filesystem, so it is gated by `cap.persist`
        # (disabled by default). When enabled, `cap.persist-root` can constrain
        # where persistence files live.
        self.options.register("recent.persist", False, kind="bool", doc="persist recent file MRU to disk (requires cap.persist)")
        self.options.register("recent.file", "~/.config/micromax/recent.json", kind="str", doc="path for recent file MRU persistence")

        self.options.register("history.persist", False, kind="bool", doc="persist prompt history to disk (requires cap.persist)")
        self.options.register_alias(
            "savehistory",
            "history.persist",
            doc="remember prompt/command history between sessions (requires cap.persist)",
        )
        self.options.register("history.file", "~/.config/micromax/history.json", kind="str", doc="path for prompt history persistence")
        self.options.register("history.limit", 200, kind="int", doc="max stored history entries per prompt kind")

        self.options.register("savecursor", False, kind="bool", doc="persist per-file primary cursor positions (requires cap.persist)")
        self.options.register("savecursor.file", "~/.config/micromax/cursor.json", kind="str", doc="path for savecursor persistence")
        self.options.register("parsecursor", False, kind="bool", doc="parse open targets like file:line[:col] into an initial cursor position")
        self.options.register("smartpaste", False, kind="bool", doc="best-effort indent multi-line pastes to the current line prefix")

        # Capability gates (host-owned world). These control whether *unsafe*
        # host surfaces are advertised/enabled.
        self.options.register("cap.persist", False, kind="bool", doc="allow editor-owned persistence files (recent/history/savecursor) to be read/written (unsafe)")
        self.options.register("cap.persist-root", "~/.config/micromax", kind="str", doc="sandbox root for persistence files (empty=unrestricted)")
        self.options.register("cap.open-url", False, kind="bool", doc="allow opening external URLs from docs (unsafe)")
        self.options.register(
            "open-url.confirm",
            True,
            kind="bool",
            doc="confirm before opening external URLs from docs (even when cap.open-url is enabled)",
        )
        self.options.register("cap.shell", False, kind="bool", doc="allow running shell commands from scripts (unsafe)")
        self.options.register("cap.fs-open", False, kind="bool", doc="allow scripts to open files from disk (unsafe)")
        self.options.register("cap.fs-save", False, kind="bool", doc="allow scripts to save buffers to disk (unsafe)")
        self.options.register("cap.fs-read", False, kind="bool", doc="allow scripts to read arbitrary files from disk (unsafe)")
        self.options.register("cap.fs-list", False, kind="bool", doc="allow scripts to list directory entries from disk (unsafe)")
        self.options.register("cap.fs-stat", False, kind="bool", doc="allow scripts to stat paths on disk (unsafe)")
        self.options.register("cap.fs-root", "", kind="str", doc="filesystem sandbox root for cap.fs-* helpers (empty=unrestricted)")

        # Statusline / infobar: micro-esque split format strings.
        # Directives are embedded as $() expressions, e.g. $(filename), $(line),
        # $(opt:filetype), $(bind:SomeAction).
        self.options.register("statusline", True, kind="bool", doc="show status line (UI layer)")
        self.options.register("infobar", True, kind="bool", doc="show the idle message/prompt line in the curses TUI")
        self.options.register(
            "constantshow",
            False,
            kind="bool",
            doc="show a tiny right-aligned cursor summary in the idle infobar (nano-esque)",
        )
        self.options.register("basename", False, kind="bool", doc="show only the basename in filename/statusline displays instead of the full path")
        # TUI debug helpers.
        self.options.register(
            "tui.bracketedpaste",
            True,
            kind="bool",
            doc="TUI: enable bracketed paste mode (CSI ? 2004 h/l)",
        )
        self.options.register("tui.rawkeys", False, kind="bool", doc="TUI: show raw key events instead of dispatching")
        self.options.register(
            "statusformatl",
            "$(filename)$(modified)$(readonly)",
            kind="str",
            doc="status line left format string (micro-esque $() directives)",
        )
        self.options.register(
            "statusformatr",
            "ft:$(opt:filetype) enc:$(opt:encoding) $(opt:fileformat)$(searchpos)$(bufpos) $(position)$(cur)$(sel) $(percentage)% $(mode)$(keymode)$(macro)",
            kind="str",
            doc="status line right format string (micro-esque $() directives)",
        )

    def _install_default_actions(self) -> None:
        # ---- editing ----
        def a_insert_text(ed: Editor) -> bool:
            text = str(ed.input.get("text", ""))
            eb = ed.cur()
            ed._normalize_cursor_lists(eb)
            before = ed._snapshot_buffer_state(eb)

            # Replace selections per cursor.
            ranges = ed._all_selection_ranges()
            if ranges:
                ranges.sort(key=lambda t: (t[1].line, t[1].col), reverse=True)
                for i, s, e in ranges:
                    eb.cursors[i] = eb.buf.replace_range(s, e, text)
                    eb.sel_anchors[i] = None
            # Insert at all cursors.
            for i in reversed(range(len(eb.cursors))):
                if ed.selection_range(i) is not None:
                    # already handled above
                    continue
                eb.cursors[i] = eb.buf.insert(eb.cursors[i], text)

            after = ed._snapshot_buffer_state(eb)
            ed._record_undo_snapshot(eb, before, after, f"insert {len(text)}")
            return True

        def a_insert_newline(ed: Editor) -> bool:
            eb = ed.cur()
            ed._normalize_cursor_lists(eb)
            before = ed._snapshot_buffer_state(eb)

            def _leading_ws(s: str) -> str:
                i = 0
                while i < len(s) and s[i] in (" ", "\t"):
                    i += 1
                return s[:i]

            def _newline_indent(line: str, col: int, *, enabled: bool) -> str:
                # Preserve the current line's indentation without duplicating it
                # when splitting *inside* the indent prefix.
                if not enabled:
                    return ""
                lead = _leading_ws(line)
                if col <= len(lead):
                    return lead[:col]
                return lead

            def _clear_whitespace_only_line(li: int) -> None:
                if li < 0 or li >= len(eb.buf.lines):
                    return
                s = eb.buf.lines[li]
                if not s or any(ch not in (" ", "\t") for ch in s):
                    return
                eb.buf.delete_range(Cursor(li, 0), Cursor(li, len(s)))
                for j, cur in enumerate(eb.cursors):
                    if int(cur.line) == li and int(cur.col) > 0:
                        eb.cursors[j] = Cursor(li, 0)
                for j, anc in enumerate(eb.sel_anchors):
                    if anc is not None and int(anc.line) == li and int(anc.col) > 0:
                        eb.sel_anchors[j] = Cursor(li, 0)

            autoindent_enabled = bool(ed.options.get("autoindent", local=eb.local_options))
            keep_autoindent = bool(ed.options.get("keepautoindent", local=eb.local_options))

            # Replace selections per cursor first.
            ranges = ed._all_selection_ranges()
            if ranges:
                ranges.sort(key=lambda t: (t[1].line, t[1].col), reverse=True)
                for i, s, e in ranges:
                    line = eb.buf.lines[s.line]
                    indent = _newline_indent(line, int(s.col), enabled=autoindent_enabled)
                    clear_prev = autoindent_enabled and (not keep_autoindent) and bool(line) and all(ch in (" ", "\t") for ch in line)
                    eb.cursors[i] = eb.buf.replace_range(s, e, "\n" + indent)
                    eb.sel_anchors[i] = None
                    if clear_prev:
                        _clear_whitespace_only_line(int(eb.cursors[i].line) - 1)

            # Insert newline at all remaining cursors.
            for i in reversed(range(len(eb.cursors))):
                if ed.selection_range(i) is not None:
                    continue
                c = eb.cursors[i]
                line = eb.buf.lines[c.line]
                indent = _newline_indent(line, int(c.col), enabled=autoindent_enabled)
                clear_prev = autoindent_enabled and (not keep_autoindent) and bool(line) and all(ch in (" ", "\t") for ch in line)
                eb.cursors[i] = eb.buf.insert(c, "\n" + indent)
                if clear_prev:
                    _clear_whitespace_only_line(int(eb.cursors[i].line) - 1)

            after = ed._snapshot_buffer_state(eb)
            if before == after:
                return False
            ed._record_undo_snapshot(eb, before, after, "newline")
            return True

        def a_backspace(ed: Editor) -> bool:
            eb = ed.cur()
            ed._normalize_cursor_lists(eb)
            before = ed._snapshot_buffer_state(eb)

            if ed._delete_selections():
                after = ed._snapshot_buffer_state(eb)
                ed._record_undo_snapshot(eb, before, after, "delete selection")
                return True

            for i in reversed(range(len(eb.cursors))):
                eb.cursors[i] = eb.buf.delete_char(eb.cursors[i], backward=True)

            after = ed._snapshot_buffer_state(eb)
            if before == after:
                return False
            ed._record_undo_snapshot(eb, before, after, "backspace")
            return True

        def a_delete_forward(ed: Editor) -> bool:
            """Delete char to the right (forward delete / Delete key)."""

            eb = ed.cur()
            ed._normalize_cursor_lists(eb)
            before = ed._snapshot_buffer_state(eb)

            if ed._delete_selections():
                after = ed._snapshot_buffer_state(eb)
                ed._record_undo_snapshot(eb, before, after, "delete selection")
                return True

            for i in reversed(range(len(eb.cursors))):
                eb.cursors[i] = eb.buf.delete_char(eb.cursors[i], backward=False)

            after = ed._snapshot_buffer_state(eb)
            if before == after:
                return False
            ed._record_undo_snapshot(eb, before, after, "delete")
            return True

        def a_undo(ed: Editor) -> bool:
            return ed.undo_feedback()

        def a_redo(ed: Editor) -> bool:
            return ed.redo_feedback()

        # ---- movement ----
        def _move_all(ed: Editor, dline: int, dcol: int) -> bool:
            eb = ed.cur()
            ed._normalize_cursor_lists(eb)
            for i, c in enumerate(eb.cursors):
                eb.cursors[i] = eb.buf.clamp(Cursor(c.line + dline, c.col + dcol))
            ed.clear_selection()
            return True

        def _move_horiz_all(ed: Editor, direction: int, *, extend_selection: bool = False) -> bool:
            eb = ed.cur()
            ed._normalize_cursor_lists(eb)
            step_dir = -1 if int(direction) < 0 else 1
            for i, c in enumerate(eb.cursors):
                line = eb.buf.lines[int(c.line)] if 0 <= int(c.line) < len(eb.buf.lines) else ""
                dcol = ed._tabmovement_step(eb, line, int(c.col), direction=step_dir)
                eb.cursors[i] = eb.buf.clamp(Cursor(c.line, c.col + dcol))
            if not extend_selection:
                ed.clear_selection()
            return True

        def a_left(ed: Editor) -> bool:
            return _move_horiz_all(ed, -1, extend_selection=False)

        def a_right(ed: Editor) -> bool:
            return _move_horiz_all(ed, +1, extend_selection=False)

        def a_up(ed: Editor) -> bool:
            eb = ed.cur()
            if bool(ed.options.get("softwrap", local=eb.local_options)):
                return ed._move_cursors_visual(-1, extend_selection=False)
            return _move_all(ed, -1, 0)

        def a_down(ed: Editor) -> bool:
            eb = ed.cur()
            if bool(ed.options.get("softwrap", local=eb.local_options)):
                return ed._move_cursors_visual(+1, extend_selection=False)
            return _move_all(ed, +1, 0)

        def a_start_line(ed: Editor) -> bool:
            eb = ed.cur()
            ed._normalize_cursor_lists(eb)
            softwrap = bool(ed.options.get("softwrap", local=eb.local_options))
            w = int(ed.viewport_width) if int(ed.viewport_width) > 0 else int(ed.options.get("viewport.width", local=eb.local_options))
            for i, c in enumerate(eb.cursors):
                if not softwrap or w <= 0:
                    eb.cursors[i] = Cursor(c.line, 0)
                    continue
                s = eb.buf.lines[int(c.line)] if 0 <= int(c.line) < len(eb.buf.lines) else ""
                cont = ed._contindent_for_line(eb, s, w=w)
                row = ed._wrap_row_for_col_with_cont(eb, s, int(c.col), w, cont)
                start = ed._wrap_start_for_row_in_line(eb, s, w=w, row=row)
                eb.cursors[i] = Cursor(c.line, start)
            ed.clear_selection()
            return True

        def a_end_line(ed: Editor) -> bool:
            eb = ed.cur()
            ed._normalize_cursor_lists(eb)
            softwrap = bool(ed.options.get("softwrap", local=eb.local_options))
            w = int(ed.viewport_width) if int(ed.viewport_width) > 0 else int(ed.options.get("viewport.width", local=eb.local_options))
            for i, c in enumerate(eb.cursors):
                s = eb.buf.lines[int(c.line)] if 0 <= int(c.line) < len(eb.buf.lines) else ""
                if not softwrap or w <= 0:
                    eb.cursors[i] = Cursor(c.line, len(s))
                    continue
                cont = ed._contindent_for_line(eb, s, w=w)
                row = ed._wrap_row_for_col_with_cont(eb, s, int(c.col), w, cont)
                end_col = ed._wrap_end_for_row_in_line(eb, s, w=w, row=row)
                eb.cursors[i] = Cursor(c.line, end_col)
            ed.clear_selection()
            return True

        def a_doc_top(ed: Editor) -> bool:
            """Move cursor(s) to top of document (Ctrl-Home)."""
            eb = ed.cur()
            ed._normalize_cursor_lists(eb)
            for i, c in enumerate(eb.cursors):
                eb.cursors[i] = eb.buf.clamp(Cursor(0, int(c.col)))
            ed.clear_selection()
            return True

        def a_doc_bottom(ed: Editor) -> bool:
            """Move cursor(s) to bottom of document (Ctrl-End)."""
            eb = ed.cur()
            ed._normalize_cursor_lists(eb)
            last = max(0, len(eb.buf.lines) - 1)
            for i, c in enumerate(eb.cursors):
                eb.cursors[i] = eb.buf.clamp(Cursor(last, int(c.col)))
            ed.clear_selection()
            return True

        def a_page_up(ed: Editor) -> bool:
            """Move cursor(s) up by a page (PageUp).

            Page height is controlled by `page.height` (default: 30). The tiny
            `pageoverlap` option can keep a few rows from the previous view in
            sight. Under softwrap, both values are measured in *visual rows*.
            """
            eb = ed.cur()
            ed._normalize_cursor_lists(eb)
            step = int(ed.page_step(eb=eb))
            page = max(1, int(ed.page_height(eb=eb)))
            if bool(ed.options.get("softwrap", local=eb.local_options)):
                ok = ed._move_cursors_visual(-step, extend_selection=False)
                w = int(ed.viewport_width)
                h = max(1, int(page))
                if w > 0 and h > 0:
                    total = ed._total_visual_rows(eb, w=w)
                    max_start = max(0, total - h)
                    start_y = ed._viewport_visual_start(eb, w=w)
                    ed._set_viewport_from_visual_start(eb, max(0, min(start_y - step, max_start)), w=w)
                return ok
            for i, c in enumerate(eb.cursors):
                eb.cursors[i] = eb.buf.clamp(Cursor(int(c.line) - step, int(c.col)))
            h = max(1, int(page))
            max_top = max(0, len(eb.buf.lines) - h)
            ed.viewport_top_line = max(0, min(int(ed.viewport_top_line) - step, max_top))
            ed.viewport_top_subline = 0
            ed.clear_selection()
            return True

        def a_page_down(ed: Editor) -> bool:
            """Move cursor(s) down by a page (PageDown)."""
            eb = ed.cur()
            ed._normalize_cursor_lists(eb)
            step = int(ed.page_step(eb=eb))
            page = max(1, int(ed.page_height(eb=eb)))
            if bool(ed.options.get("softwrap", local=eb.local_options)):
                ok = ed._move_cursors_visual(+step, extend_selection=False)
                w = int(ed.viewport_width)
                h = max(1, int(page))
                if w > 0 and h > 0:
                    total = ed._total_visual_rows(eb, w=w)
                    max_start = max(0, total - h)
                    start_y = ed._viewport_visual_start(eb, w=w)
                    ed._set_viewport_from_visual_start(eb, max(0, min(start_y + step, max_start)), w=w)
                return ok
            for i, c in enumerate(eb.cursors):
                eb.cursors[i] = eb.buf.clamp(Cursor(int(c.line) + step, int(c.col)))
            h = max(1, int(page))
            max_top = max(0, len(eb.buf.lines) - h)
            ed.viewport_top_line = max(0, min(int(ed.viewport_top_line) + step, max_top))
            ed.viewport_top_subline = 0
            ed.clear_selection()
            return True

        def a_word_left(ed: Editor) -> bool:
            """Move cursor(s) left by one word boundary (Ctrl-Left)."""
            eb = ed.cur()
            ed._normalize_cursor_lists(eb)
            for i, c in enumerate(eb.cursors):
                eb.cursors[i] = eb.buf.word_boundary_left(c)
            ed.clear_selection()
            return True

        def a_word_right(ed: Editor) -> bool:
            """Move cursor(s) right to the next word boundary (Ctrl-Right)."""
            eb = ed.cur()
            ed._normalize_cursor_lists(eb)
            for i, c in enumerate(eb.cursors):
                eb.cursors[i] = eb.buf.word_boundary_right(c)
            ed.clear_selection()
            return True

        # ---- navigation history (jumplist) ----
        def a_push_jump(ed: Editor) -> bool:
            return ed.push_jump()

        def a_jump_back(ed: Editor) -> bool:
            return ed.jump_back_feedback()

        def a_jump_forward(ed: Editor) -> bool:
            return ed.jump_forward_feedback()

        # ---- selection ----
        def _ensure_anchor_all(ed: Editor) -> None:
            eb = ed.cur()
            ed._normalize_cursor_lists(eb)
            for i, a in enumerate(eb.sel_anchors):
                if a is None:
                    c = eb.cursors[i]
                    eb.sel_anchors[i] = Cursor(c.line, c.col)

        def _select_move(ed: Editor, dline: int, dcol: int) -> bool:
            _ensure_anchor_all(ed)
            eb = ed.cur()
            for i, c in enumerate(eb.cursors):
                eb.cursors[i] = eb.buf.clamp(Cursor(c.line + dline, c.col + dcol))
            return True

        def a_select_left(ed: Editor) -> bool:
            _ensure_anchor_all(ed)
            return _move_horiz_all(ed, -1, extend_selection=True)

        def a_select_right(ed: Editor) -> bool:
            _ensure_anchor_all(ed)
            return _move_horiz_all(ed, +1, extend_selection=True)

        def a_select_word_left(ed: Editor) -> bool:
            """Extend selection left to previous word boundary (Shift-Ctrl-Left)."""
            _ensure_anchor_all(ed)
            eb = ed.cur()
            ed._normalize_cursor_lists(eb)
            for i, c in enumerate(eb.cursors):
                eb.cursors[i] = eb.buf.word_boundary_left(c)
            return True

        def a_select_word_right(ed: Editor) -> bool:
            """Extend selection right to next word boundary (Shift-Ctrl-Right)."""
            _ensure_anchor_all(ed)
            eb = ed.cur()
            ed._normalize_cursor_lists(eb)
            for i, c in enumerate(eb.cursors):
                eb.cursors[i] = eb.buf.word_boundary_right(c)
            return True

        def a_select_up(ed: Editor) -> bool:
            _ensure_anchor_all(ed)
            eb = ed.cur()
            if bool(ed.options.get("softwrap", local=eb.local_options)):
                return ed._move_cursors_visual(-1, extend_selection=True)
            return _select_move(ed, -1, 0)

        def a_select_down(ed: Editor) -> bool:
            _ensure_anchor_all(ed)
            eb = ed.cur()
            if bool(ed.options.get("softwrap", local=eb.local_options)):
                return ed._move_cursors_visual(+1, extend_selection=True)
            return _select_move(ed, +1, 0)

        def a_select_all(ed: Editor) -> bool:
            eb = ed.cur()
            # SelectAll collapses to a single cursor (simple, predictable).
            eb.cursors[:] = [Cursor(0, 0)]
            eb.sel_anchors[:] = [Cursor(0, 0)]
            eb.cursor_ids[:] = [ed._alloc_cursor_id()]
            eb.primary = 0
            last_line = len(eb.buf.lines) - 1
            eb.cursors[0] = Cursor(last_line, len(eb.buf.lines[last_line]))
            return True

        def a_clear_selection(ed: Editor) -> bool:
            if not ed.has_selection() and all(a is None for a in ed.cur().sel_anchors):
                return False
            ed.clear_selection()
            return True

        def a_flip_selections(ed: Editor) -> bool:
            """Swap selection anchor/cursor endpoints (Helix/Kakoune-inspired)."""

            eb = ed.cur()
            ed._normalize_cursor_lists(eb)
            changed = False
            for i, a in enumerate(eb.sel_anchors):
                if a is None:
                    continue
                c = eb.cursors[i]
                eb.cursors[i] = Cursor(a.line, a.col)
                eb.sel_anchors[i] = Cursor(c.line, c.col)
                changed = True
            if changed:
                ed._normalize_cursor_lists(eb)
            return changed

        def a_ensure_selections_forward(ed: Editor) -> bool:
            """Ensure selection direction is forward (anchor <= cursor)."""

            eb = ed.cur()
            ed._normalize_cursor_lists(eb)
            changed = False
            for i, a in enumerate(eb.sel_anchors):
                if a is None:
                    continue
                c = eb.cursors[i]
                if (c.line, c.col) < (a.line, a.col):
                    eb.cursors[i] = Cursor(a.line, a.col)
                    eb.sel_anchors[i] = Cursor(c.line, c.col)
                    changed = True
            if changed:
                ed._normalize_cursor_lists(eb)
            return changed

        # ---- clipboard ----
        def a_copy(ed: Editor) -> bool:
            eb = ed.cur()
            ed._normalize_cursor_lists(eb)
            parts: list[str] = []
            for i in range(len(eb.cursors)):
                if ed.has_selection(i):
                    parts.append(ed.selection_text(i))
            if not parts:
                ed.message("no selection")
                return False
            ed.set_clipboard_items(parts, kind="items")
            ed._cutline_accum = False
            ed.message(
                ed.format_clipboard_feedback(
                    verb="copied",
                    count=len(parts),
                    count_label="selection",
                    total_chars=sum(len(part) for part in parts),
                )
            )
            return True

        def a_cut(ed: Editor) -> bool:
            eb = ed.cur()
            ed._normalize_cursor_lists(eb)
            parts: list[str] = []
            for i in range(len(eb.cursors)):
                if ed.has_selection(i):
                    parts.append(ed.selection_text(i))
            if not parts:
                ed.message("no selection")
                return False

            before = ed._snapshot_buffer_state(eb)
            # Delete selections across cursors
            ok = ed._delete_selections()
            after = ed._snapshot_buffer_state(eb)
            if ok:
                ed._record_undo_snapshot(eb, before, after, "cut")
            ed.set_clipboard_items(parts, kind="items")
            ed._cutline_accum = False
            if ok:
                ed.message(
                    ed.format_clipboard_feedback(
                        verb="cut",
                        count=len(parts),
                        count_label="selection",
                        total_chars=sum(len(part) for part in parts),
                        include_target=True,
                    )
                )
            return ok
        def a_paste(ed: Editor) -> bool:
            system_text: str | None = None
            err_hint = ""

            # When clipboard=external, micro-esque Ctrl-v should paste from the
            # system clipboard (best-effort). We keep the editor's internal clipboard
            # as a fallback when tools are unavailable.
            try:
                backend = str(ed.options.get('clipboard') or '')
            except Exception:
                backend = ''
            if backend == 'external':
                try:
                    do_import = bool(ed.options.get('clipboard.external.import'))
                except Exception:
                    do_import = True
                if do_import:
                    system_text, err_hint = ed.clipboard_external_import_text()

            if system_text is None and not ed.clipboard_items:
                # No internal clipboard; show a gentle one-time hint for external
                # clipboard missing (interactive only).
                if err_hint and not ed.in_script_context():
                    if err_hint.startswith('no external clipboard read tool'):
                        if not bool(getattr(ed, '_clipboard_external_read_warned', False)):
                            setattr(ed, '_clipboard_external_read_warned', True)
                            ed.message(str(err_hint))
                    elif err_hint.startswith('clipboard import disabled for scripts'):
                        pass
                    elif err_hint.startswith('clipboard backend is not external'):
                        pass
                    else:
                        ed.message(str(err_hint))
                elif not err_hint:
                    ed.message('paste: clipboard empty')
                return False

            eb = ed.cur()
            ed._normalize_cursor_lists(eb)
            before = ed._snapshot_buffer_state(eb)

            if system_text is not None:
                per_cursor = [system_text] * len(eb.cursors)
            else:
                items = ed.clipboard_items
                if ed.clipboard_kind == 'items' and len(items) == len(eb.cursors):
                    per_cursor = list(items)
                else:
                    per_cursor = [ed.clipboard_text()] * len(eb.cursors)

            smart_per_cursor: list[str] = []
            for i in range(len(eb.cursors)):
                rng = ed.selection_range(i)
                anchor = rng[0] if rng is not None else eb.cursors[i]
                line = eb.buf.lines[anchor.line]
                smart_per_cursor.append(ed._smartpaste_text(str(per_cursor[i]), line=line, col=int(anchor.col)))
            per_cursor = smart_per_cursor

            ops: list[tuple[int, Cursor, Cursor | None]] = []
            for i in range(len(eb.cursors)):
                rng = ed.selection_range(i)
                if rng is None:
                    ops.append((i, eb.cursors[i], None))
                else:
                    s, e = rng
                    ops.append((i, s, e))

            # Apply from bottom to top.
            def _key(t: tuple[int, Cursor, Cursor | None]) -> tuple[int, int]:
                return (t[1].line, t[1].col)

            ops.sort(key=_key, reverse=True)
            for i, s, e in ops:
                text = per_cursor[i]
                if e is None:
                    eb.cursors[i] = eb.buf.insert(eb.cursors[i], text)
                else:
                    eb.cursors[i] = eb.buf.replace_range(s, e, text)
                eb.sel_anchors[i] = None

            after = ed._snapshot_buffer_state(eb)
            ed._record_undo_snapshot(eb, before, after, 'paste')
            ed._paste_reset()
            ed.message(
                ed.format_clipboard_feedback(
                    verb='paste',
                    count=len(per_cursor),
                    count_label='cursor',
                    total_chars=sum(len(part) for part in per_cursor),
                    include_target=True,
                )
            )
            return True

        # ---- line ops ----
        def a_cut_line(ed: Editor) -> bool:
            eb = ed.cur()
            ed._normalize_cursor_lists(eb)
            before = ed._snapshot_buffer_state(eb)

            # Delete unique lines touched by cursors.
            lines = sorted({c.line for c in eb.cursors}, reverse=True)
            cut_parts: list[str] = []
            for li in lines:
                cut_parts.append(eb.buf.lines[li])
                eb.buf.delete_line(li)
                # adjust cursors + anchors above deleted line
                for i, c in enumerate(eb.cursors):
                    if c.line > li:
                        eb.cursors[i] = Cursor(c.line - 1, c.col)
                    elif c.line == li:
                        eb.cursors[i] = eb.buf.clamp(Cursor(li, 0))
                    a = eb.sel_anchors[i]
                    if a is not None:
                        if a.line > li:
                            eb.sel_anchors[i] = Cursor(a.line - 1, a.col)
                        elif a.line == li:
                            eb.sel_anchors[i] = Cursor(li, 0)

            ed.clear_selection()

            if ed._cutline_accum and ed.clipboard_items:
                ed.clipboard_items.extend(reversed(cut_parts))
                ed.clipboard_kind = "lines"
            else:
                ed.set_clipboard_items(list(reversed(cut_parts)), kind="lines")
            ed._cutline_accum = True

            after = ed._snapshot_buffer_state(eb)
            ed._record_undo_snapshot(eb, before, after, "cut line")
            return True

        def a_duplicate_line(ed: Editor) -> bool:
            eb = ed.cur()
            ed._normalize_cursor_lists(eb)
            before = ed._snapshot_buffer_state(eb)
            line = eb.cursors[eb.primary].line
            eb.cursors[eb.primary] = eb.buf.duplicate_line(line)
            after = ed._snapshot_buffer_state(eb)
            ed._record_undo_snapshot(eb, before, after, "duplicate line")
            return True

        def a_move_lines_up(ed: Editor) -> bool:
            eb = ed.cur()
            ed._normalize_cursor_lists(eb)
            before = ed._snapshot_buffer_state(eb)

            span = _selected_line_span(ed)
            if span is None:
                span = (eb.cursors[eb.primary].line, eb.cursors[eb.primary].line)
            start, end = span
            if start <= 0:
                return False
            # move block up by one
            block = eb.buf.lines[start : end + 1]
            eb.buf.lines[start - 1 : end + 1] = block + [eb.buf.lines[start - 1]]
            eb.buf.touch_external()

            # adjust cursors/anchors in block
            for i, c in enumerate(eb.cursors):
                if start <= c.line <= end:
                    eb.cursors[i] = Cursor(c.line - 1, c.col)
                elif c.line == start - 1:
                    eb.cursors[i] = Cursor(end, c.col)
            for i, a in enumerate(eb.sel_anchors):
                if a is None:
                    continue
                if start <= a.line <= end:
                    eb.sel_anchors[i] = Cursor(a.line - 1, a.col)
                elif a.line == start - 1:
                    eb.sel_anchors[i] = Cursor(end, a.col)

            after = ed._snapshot_buffer_state(eb)
            ed._record_undo_snapshot(eb, before, after, "move lines up")
            return True

        def a_move_lines_down(ed: Editor) -> bool:
            eb = ed.cur()
            ed._normalize_cursor_lists(eb)
            before = ed._snapshot_buffer_state(eb)

            span = _selected_line_span(ed)
            if span is None:
                span = (eb.cursors[eb.primary].line, eb.cursors[eb.primary].line)
            start, end = span
            if end >= len(eb.buf.lines) - 1:
                return False
            block = eb.buf.lines[start : end + 1]
            eb.buf.lines[start : end + 2] = [eb.buf.lines[end + 1]] + block
            eb.buf.touch_external()

            for i, c in enumerate(eb.cursors):
                if start <= c.line <= end:
                    eb.cursors[i] = Cursor(c.line + 1, c.col)
                elif c.line == end + 1:
                    eb.cursors[i] = Cursor(start, c.col)
            for i, a in enumerate(eb.sel_anchors):
                if a is None:
                    continue
                if start <= a.line <= end:
                    eb.sel_anchors[i] = Cursor(a.line + 1, a.col)
                elif a.line == end + 1:
                    eb.sel_anchors[i] = Cursor(start, a.col)

            after = ed._snapshot_buffer_state(eb)
            ed._record_undo_snapshot(eb, before, after, "move lines down")
            return True

        # ---- indent ----
        def _selected_line_span(ed: Editor) -> tuple[int, int] | None:
            # Union of all cursor selections; returns bounding span.
            ranges = ed._all_selection_ranges()
            if not ranges:
                return None
            starts: list[int] = []
            ends: list[int] = []
            for _, s, e in ranges:
                start = s.line
                end = e.line
                if e.col == 0 and end > start:
                    end -= 1
                starts.append(start)
                ends.append(end)
            return (min(starts), max(ends))

        def a_indent_selection(ed: Editor) -> bool:
            span = _selected_line_span(ed)
            if span is None:
                return False
            eb = ed.cur()
            before = ed._snapshot_buffer_state(eb)
            pref = str(ed.options.get("indent", local=eb.local_options))
            for li in range(span[0], span[1] + 1):
                eb.buf.lines[li] = pref + eb.buf.lines[li]

            # adjust cursors/anchors if on affected lines
            for i, a in enumerate(eb.sel_anchors):
                if a and span[0] <= a.line <= span[1]:
                    eb.sel_anchors[i] = Cursor(a.line, a.col + len(pref))
            for i, c in enumerate(eb.cursors):
                if span[0] <= c.line <= span[1]:
                    eb.cursors[i] = Cursor(c.line, c.col + len(pref))
            eb.buf.touch_external()

            after = ed._snapshot_buffer_state(eb)
            ed._record_undo_snapshot(eb, before, after, "indent")
            return True

        def a_unindent_selection(ed: Editor) -> bool:
            span = _selected_line_span(ed)
            if span is None:
                return False
            eb = ed.cur()
            before = ed._snapshot_buffer_state(eb)
            pref = str(ed.options.get("indent", local=eb.local_options))
            removed = 0
            for li in range(span[0], span[1] + 1):
                ln = eb.buf.lines[li]
                if ln.startswith(pref):
                    eb.buf.lines[li] = ln[len(pref) :]
                    removed = len(pref)
                else:
                    n = 0
                    while n < len(pref) and n < len(ln) and ln[n] == " ":
                        n += 1
                    if n:
                        eb.buf.lines[li] = ln[n:]
                        removed = max(removed, n)

            if removed:
                for i, a in enumerate(eb.sel_anchors):
                    if a and span[0] <= a.line <= span[1]:
                        eb.sel_anchors[i] = Cursor(a.line, max(0, a.col - removed))
                for i, c in enumerate(eb.cursors):
                    if span[0] <= c.line <= span[1]:
                        eb.cursors[i] = Cursor(c.line, max(0, c.col - removed))

            eb.buf.touch_external()
            after = ed._snapshot_buffer_state(eb)
            if before == after:
                return False
            ed._record_undo_snapshot(eb, before, after, "unindent")
            return True

        # ---- prompt / completion ----
        def a_autocomplete(ed: Editor) -> bool:
            # Prompt completion (command bar) lives on Editor so it can consult
            # command names, options, macros, plugin names, etc.
            return ed.prompt_complete(direction=1)

        def a_prompt_complete_prev(ed: Editor) -> bool:
            return ed.prompt_complete(direction=-1)

        def a_insert_tab(ed: Editor) -> bool:
            if ed.prompt is not None:
                # In the command prompt, Tab is reserved for completion; don't insert a
                # literal tab when completion fails.
                if ed.prompt.kind == "find":
                    ed.set_prompt_text(ed.prompt.text + "\t")
                    return True
                return False

            eb = ed.cur()
            ed._normalize_cursor_lists(eb)
            before = ed._snapshot_buffer_state(eb)

            tabstospaces = bool(ed.options.get("tabstospaces", local=eb.local_options))
            tabsize_raw = int(ed.options.get("tabsize", local=eb.local_options))
            tabsize = max(1, tabsize_raw)

            def _visual_col(line: str, col: int) -> int:
                # Best-effort visual column accounting for existing tabs.
                v = 0
                for ch in line[: max(0, min(col, len(line)))]:
                    if ch == "\t":
                        v += tabsize - (v % tabsize)
                    else:
                        v += 1
                return v

            def _tab_text_at(line: str, col: int) -> str:
                if not tabstospaces:
                    return "\t"
                v = _visual_col(line, col)
                n = tabsize - (v % tabsize)
                if n <= 0:
                    n = tabsize
                return " " * n

            # Replace selections per cursor first (should usually be handled by
            # IndentSelection, but we keep this action robust).
            ranges = ed._all_selection_ranges()
            if ranges:
                ranges.sort(key=lambda t: (t[1].line, t[1].col), reverse=True)
                for i, s, e in ranges:
                    line = eb.buf.lines[s.line]
                    eb.cursors[i] = eb.buf.replace_range(s, e, _tab_text_at(line, int(s.col)))
                    eb.sel_anchors[i] = None

            # Insert at all remaining cursors.
            for i in reversed(range(len(eb.cursors))):
                if ed.selection_range(i) is not None:
                    continue
                c = eb.cursors[i]
                line = eb.buf.lines[c.line]
                eb.cursors[i] = eb.buf.insert(c, _tab_text_at(line, int(c.col)))

            after = ed._snapshot_buffer_state(eb)
            if before == after:
                return False
            ed._record_undo_snapshot(eb, before, after, "tab")
            return True


        def _is_text_key(k: str) -> bool:
            return len(k) == 1 and k.isprintable() and k not in ('\n', '\r', '\t')

        def a_prompt_insert_text(ed: Editor) -> bool:
            if ed.prompt is None:
                return False
            text = str(ed.input.get('text', ''))
            if text == '':
                return False
            p = ed.prompt
            s = p.text
            i = int(p.cursor)
            new = s[:i] + text + s[i:]
            return ed.set_prompt_text_cursor(new, i + len(text))

        def a_prompt_backspace(ed: Editor) -> bool:
            if ed.prompt is None:
                return False
            p = ed.prompt
            i = int(p.cursor)
            if i <= 0:
                return False
            s = p.text
            new = s[: i - 1] + s[i:]
            return ed.set_prompt_text_cursor(new, i - 1)

        def a_prompt_delete(ed: Editor) -> bool:
            if ed.prompt is None:
                return False
            p = ed.prompt
            i = int(p.cursor)
            s = p.text
            if i >= len(s):
                return False
            new = s[:i] + s[i + 1 :]
            return ed.set_prompt_text_cursor(new, i)

        def a_prompt_left(ed: Editor) -> bool:
            if ed.prompt is None:
                return False
            ed.prompt.set_cursor(int(ed.prompt.cursor) - 1)
            return True

        def a_prompt_right(ed: Editor) -> bool:
            if ed.prompt is None:
                return False
            ed.prompt.set_cursor(int(ed.prompt.cursor) + 1)
            return True

        def a_prompt_home(ed: Editor) -> bool:
            if ed.prompt is None:
                return False
            ed.prompt.set_cursor(0)
            return True

        def a_prompt_end(ed: Editor) -> bool:
            if ed.prompt is None:
                return False
            ed.prompt.set_cursor(len(ed.prompt.text))
            return True

        # ---- prompt modes ----
        def a_command_mode(ed: Editor) -> bool:
            ed.enter_prompt("command")
            return True

        def a_command_palette(ed: Editor) -> bool:
            ed.enter_command_palette()
            return True

        def a_topic_prompt(ed: Editor) -> bool:
            ed.enter_topic_prompt()
            return True

        def a_binding_prompt(ed: Editor) -> bool:
            ed.enter_binding_prompt()
            return True

        def a_find(ed: Editor) -> bool:
            ed.search.literal = True
            ed.enter_prompt("find")
            return True

        def a_find_literal(ed: Editor) -> bool:
            ed.search.literal = True
            ed.enter_prompt("find")
            return True

        def a_find_regex(ed: Editor) -> bool:
            ed.search.literal = False
            ed.enter_prompt("find")
            return True

        def a_find_next(ed: Editor) -> bool:
            return ed.find_next()

        def a_find_prev(ed: Editor) -> bool:
            return ed.find_prev()

        def a_escape(ed: Editor) -> bool:
            return ed.cancel_prompt()

        def a_submit(ed: Editor) -> bool:
            return ed.submit_prompt()

        # ---- query replace confirmation loop ----
        def a_qreplace_yes(ed: Editor) -> bool:
            return ed.qreplace_yes()

        def a_qreplace_no(ed: Editor) -> bool:
            return ed.qreplace_no()

        def a_qreplace_all(ed: Editor) -> bool:
            return ed.qreplace_all()

        def a_qreplace_last(ed: Editor) -> bool:
            return ed.qreplace_last()

        def a_qreplace_quit(ed: Editor) -> bool:
            return ed.qreplace_quit()

        def a_prompt_prev(ed: Editor) -> bool:
            return ed.prompt_history_prev()

        def a_prompt_next(ed: Editor) -> bool:
            return ed.prompt_history_next()

        def a_prompt_suggest_prev(ed: Editor) -> bool:
            return ed.prompt_suggest_move(-1)

        def a_prompt_suggest_next(ed: Editor) -> bool:
            return ed.prompt_suggest_move(+1)

        def a_prompt_suggest_prev_section(ed: Editor) -> bool:
            return ed.prompt_suggest_prev_section()

        def a_prompt_suggest_next_section(ed: Editor) -> bool:
            return ed.prompt_suggest_next_section()

        def a_prompt_suggest_page_up(ed: Editor) -> bool:
            return ed.prompt_suggest_page(-1)

        def a_prompt_suggest_page_down(ed: Editor) -> bool:
            return ed.prompt_suggest_page(+1)

        def a_prompt_copy_selected(ed: Editor) -> bool:
            return ed.prompt_copy_selected()

        def a_prompt_suggest_first(ed: Editor) -> bool:
            return ed.prompt_suggest_first()

        def a_prompt_suggest_last(ed: Editor) -> bool:
            return ed.prompt_suggest_last()

        # ---- macros ----
        def a_toggle_macro(ed: Editor) -> bool:
            return ed.toggle_macro()

        def a_play_macro(ed: Editor) -> bool:
            return ed.play_macro()

        def a_cancel_macro(ed: Editor) -> bool:
            return ed.cancel_macro()

        # ---- multiple cursors ----
        def a_spawn_mc_up(ed: Editor) -> bool:
            eb = ed.cur()
            ed._normalize_cursor_lists(eb)
            c = eb.cursors[eb.primary]
            if c.line <= 0:
                return False
            eb.cursors.append(eb.buf.clamp(Cursor(c.line - 1, c.col)))
            eb.sel_anchors.append(None)
            eb.cursor_ids.append(ed._alloc_cursor_id())
            return True

        def a_spawn_mc_down(ed: Editor) -> bool:
            eb = ed.cur()
            ed._normalize_cursor_lists(eb)
            c = eb.cursors[eb.primary]
            if c.line >= len(eb.buf.lines) - 1:
                return False
            eb.cursors.append(eb.buf.clamp(Cursor(c.line + 1, c.col)))
            eb.sel_anchors.append(None)
            eb.cursor_ids.append(ed._alloc_cursor_id())
            return True

        def a_remove_mc(ed: Editor) -> bool:
            eb = ed.cur()
            if len(eb.cursors) <= 1:
                return False
            ed._normalize_cursor_lists(eb)
            # Remove the most recently created *non-primary* cursor.
            candidates = [(cid, i) for i, cid in enumerate(eb.cursor_ids) if i != eb.primary]
            if not candidates:
                return False
            _cid, idx = max(candidates, key=lambda t: t[0])
            eb.cursors.pop(idx)
            eb.sel_anchors.pop(idx)
            eb.cursor_ids.pop(idx)
            if eb.primary > idx:
                eb.primary -= 1
            return True

        def a_remove_all_mc(ed: Editor) -> bool:
            eb = ed.cur()
            if len(eb.cursors) <= 1:
                return False
            ed._normalize_cursor_lists(eb)
            p = eb.primary
            eb.cursors[:] = [eb.cursors[p]]
            eb.sel_anchors[:] = [eb.sel_anchors[p]]
            eb.cursor_ids[:] = [eb.cursor_ids[p]]
            eb.primary = 0
            return True

        def a_cycle_primary_next(ed: Editor) -> bool:
            """Cycle the primary cursor forward (Kakoune/Helix-inspired)."""
            eb = ed.cur()
            ed._normalize_cursor_lists(eb)
            if len(eb.cursors) <= 1:
                return False
            eb.primary = (eb.primary + 1) % len(eb.cursors)
            return True

        def a_cycle_primary_prev(ed: Editor) -> bool:
            """Cycle the primary cursor backward (Kakoune/Helix-inspired)."""
            eb = ed.cur()
            ed._normalize_cursor_lists(eb)
            if len(eb.cursors) <= 1:
                return False
            eb.primary = (eb.primary - 1) % len(eb.cursors)
            return True

        def a_collapse_to_primary(ed: Editor) -> bool:
            """Drop all cursors except the primary one."""
            eb = ed.cur()
            ed._normalize_cursor_lists(eb)
            if len(eb.cursors) <= 1:
                return False
            p = eb.primary
            eb.cursors[:] = [eb.cursors[p]]
            eb.sel_anchors[:] = [eb.sel_anchors[p]]
            eb.cursor_ids[:] = [eb.cursor_ids[p]]
            eb.primary = 0
            return True

        def _mc_needle(ed: Editor, eb: EditorBuffer) -> tuple[str, int] | None:
            # Ensure selection exists on primary cursor; if not, select current word.
            p = eb.primary
            if not ed.has_primary_selection():
                r = eb.buf.word_range_at(eb.cursors[p])
                if r is None:
                    return None
                s, e = r
                eb.sel_anchors[p] = s
                eb.cursors[p] = e
            text = ed.selection_text(None)
            if text == "":
                return None
            return text, len(text)

        def _find_next_literal(ed: Editor, eb: EditorBuffer, needle: str, start: Cursor) -> Cursor | None:
            ignorecase = bool(ed.options.get("ignorecase", local=eb.local_options))
            if not ignorecase:
                return eb.buf.find(needle, start=start)
            # naive case-insensitive forward search
            nlow = needle.lower()
            cur = eb.buf.clamp(start)
            # first line
            idx = eb.buf.lines[cur.line].lower().find(nlow, cur.col)
            if idx >= 0:
                return Cursor(cur.line, idx)
            for li in range(cur.line + 1, len(eb.buf.lines)):
                idx = eb.buf.lines[li].lower().find(nlow)
                if idx >= 0:
                    return Cursor(li, idx)
            return None

        def a_spawn_mc_select(ed: Editor) -> bool:
            eb = ed.cur()
            ed._normalize_cursor_lists(eb)
            info = _mc_needle(ed, eb)
            if info is None:
                return False
            needle, nlen = info

            # Start after the end of the current selection.
            rng = ed.selection_range(None)
            assert rng is not None
            _s, e = rng
            start = Cursor(e.line, e.col)
            m = _find_next_literal(ed, eb, needle, start)
            if m is None:
                return False

            eb.cursors.append(Cursor(m.line, m.col + nlen))
            eb.sel_anchors.append(Cursor(m.line, m.col))
            eb.cursor_ids.append(ed._alloc_cursor_id())
            ed._mc_last_match_start = Cursor(m.line, m.col)
            return True

        def a_skip_mc(ed: Editor) -> bool:
            eb = ed.cur()
            ed._normalize_cursor_lists(eb)
            info = _mc_needle(ed, eb)
            if info is None:
                return False
            needle, nlen = info

            # Continue from last match start if present; else from current selection end.
            start = ed._mc_last_match_start
            if start is None:
                rng = ed.selection_range(None)
                assert rng is not None
                _s, e = rng
                start = e
            m = _find_next_literal(ed, eb, needle, Cursor(start.line, start.col + 1))
            if m is None:
                return False

            # move primary selection to this match (visual feedback)
            p = eb.primary
            eb.sel_anchors[p] = Cursor(m.line, m.col)
            eb.cursors[p] = Cursor(m.line, m.col + nlen)
            ed._mc_last_match_start = Cursor(m.line, m.col)
            return True

        def a_spawn_mc_lines(ed: Editor) -> bool:
            eb = ed.cur()
            ed._normalize_cursor_lists(eb)
            if not ed.has_primary_selection():
                return False
            rng = ed.selection_range(None)
            assert rng is not None
            s, e = rng
            start_line = s.line
            end_line = e.line
            if e.col == 0 and end_line > start_line:
                end_line -= 1
            # replace cursor set with one cursor per line at col 0
            eb.cursors[:] = [Cursor(li, 0) for li in range(start_line, end_line + 1)]
            eb.sel_anchors[:] = [None] * len(eb.cursors)
            eb.cursor_ids[:] = [ed._alloc_cursor_id() for _ in eb.cursors]
            eb.primary = 0
            return True

        def a_noop(ed: Editor) -> bool:
            return False

        # ---- docs/help browser helpers ----
        def a_help_copy_link_target(ed: Editor) -> bool:
            return bool(ed.help_copy_link_target())

        def a_open_url_under_cursor(ed: Editor) -> bool:
            return bool(ed.open_url_under_cursor())

        def a_copy_url_under_cursor(ed: Editor) -> bool:
            return bool(ed.copy_url_under_cursor())

        # ---- external URL confirmation (capture mode) ----
        def a_openurl_yes(ed: Editor) -> bool:
            u = str(ed._pending_open_url or "").strip()
            source = str(getattr(ed, "_pending_open_url_source", "") or "")
            if not u:
                ed._finish_open_url_confirm()
                return False
            ed._finish_open_url_confirm()
            ok = ed.open_url(u)
            if ok:
                ed.message(f"{ed._open_url_feedback_prefix(source)}: {u}")
                return True
            ed.message(f"{ed._open_url_feedback_prefix(source)}: failed: {u}")
            return False

        def a_openurl_no(ed: Editor) -> bool:
            u = str(ed._pending_open_url or "").strip()
            ed._finish_open_url_confirm()
            if u:
                ed.message("canceled")
            return True

        def a_openurl_copy(ed: Editor) -> bool:
            u = str(ed._pending_open_url or "").strip()
            source = str(getattr(ed, "_pending_open_url_source", "") or "")
            if not u:
                ed._finish_open_url_confirm()
                return False
            ed.set_clipboard_items([u], kind="items")
            ed._finish_open_url_confirm()
            ed.message(f"{ed._copy_url_feedback_prefix(source)}: {u}")
            return True

        # ---- register actions ----
        self.actions.register("InsertText", a_insert_text, doc="Insert editor.input['text'] at cursor(s)")
        self.actions.register("InsertNewline", a_insert_newline, doc="Insert newline at cursor(s)")
        self.actions.register("Backspace", a_backspace, doc="Delete char to the left")
        self.actions.register("Delete", a_delete_forward, doc="Delete char to the right")
        self.actions.register("Undo", a_undo)
        self.actions.register("Redo", a_redo)

        self.actions.register("CursorLeft", a_left)
        self.actions.register("CursorRight", a_right)
        self.actions.register("CursorUp", a_up)
        self.actions.register("CursorDown", a_down)
        self.actions.register("StartOfLine", a_start_line)
        self.actions.register("EndOfLine", a_end_line)

        self.actions.register("WordLeft", a_word_left, doc="Move left by word boundary")
        self.actions.register("WordRight", a_word_right, doc="Move right by word boundary")
        self.actions.register("PageUp", a_page_up)
        self.actions.register("PageDown", a_page_down)
        self.actions.register("DocTop", a_doc_top)
        self.actions.register("DocBottom", a_doc_bottom)

        self.actions.register("PushJump", a_push_jump, doc="Save cursor/selection state to jumplist")
        self.actions.register("JumpBack", a_jump_back, doc="Jump backward in the jumplist")
        self.actions.register("JumpForward", a_jump_forward, doc="Jump forward in the jumplist")

        self.actions.register("SelectLeft", a_select_left, doc="Extend selection left")
        self.actions.register("SelectRight", a_select_right, doc="Extend selection right")
        self.actions.register("SelectWordLeft", a_select_word_left, doc="Extend selection left by word")
        self.actions.register("SelectWordRight", a_select_word_right, doc="Extend selection right by word")
        self.actions.register("SelectUp", a_select_up, doc="Extend selection up")
        self.actions.register("SelectDown", a_select_down, doc="Extend selection down")
        self.actions.register("SelectAll", a_select_all)
        self.actions.register("ClearSelection", a_clear_selection)
        self.actions.register("FlipSelections", a_flip_selections, doc="Swap selection anchor/cursor endpoints")
        self.actions.register("EnsureSelectionsForward", a_ensure_selections_forward, doc="Ensure selection direction is forward")

        self.actions.register("Copy", a_copy)
        self.actions.register("Cut", a_cut)
        self.actions.register("Paste", a_paste)
        self.actions.register("CutLine", a_cut_line)
        self.actions.register("DuplicateLine", a_duplicate_line)
        self.actions.register("MoveLinesUp", a_move_lines_up)
        self.actions.register("MoveLinesDown", a_move_lines_down)
        self.actions.register("IndentSelection", a_indent_selection)
        self.actions.register("UnindentSelection", a_unindent_selection)

        self.actions.register("Autocomplete", a_autocomplete, doc="Autocomplete/cycle in the active prompt")
        self.actions.register("PromptCompletePrev", a_prompt_complete_prev, doc="Cycle prompt completions backward")
        self.actions.register("InsertTab", a_insert_tab)

        self.actions.register("PromptInsertText", a_prompt_insert_text, doc="Insert editor.input['text'] into the active prompt")
        self.actions.register("PromptBackspace", a_prompt_backspace, doc="Delete char left in prompt")
        self.actions.register("PromptDelete", a_prompt_delete, doc="Delete char right in prompt")
        self.actions.register("PromptLeft", a_prompt_left, doc="Move prompt cursor left")
        self.actions.register("PromptRight", a_prompt_right, doc="Move prompt cursor right")
        self.actions.register("PromptHome", a_prompt_home, doc="Move prompt cursor to start")
        self.actions.register("PromptEnd", a_prompt_end, doc="Move prompt cursor to end")

        self.actions.register("CommandMode", a_command_mode, doc="Open the command bar")
        self.actions.register("CommandPalette", a_command_palette, doc="Open the searchable command/action palette")
        self.actions.register("TopicPrompt", a_topic_prompt, doc="Open the searchable topic/help prompt")
        self.actions.register("BindingPrompt", a_binding_prompt, doc="Open the searchable binding/help prompt")
        self.actions.register("Find", a_find, doc="Open find prompt (literal)")
        self.actions.register("FindLiteral", a_find_literal, doc="Open find prompt (literal)")
        self.actions.register("FindRegex", a_find_regex, doc="Open find prompt (regex)")
        self.actions.register("FindNext", a_find_next)
        self.actions.register("FindPrevious", a_find_prev)
        self.actions.register("Escape", a_escape, doc="Close the active prompt")
        self.actions.register("SubmitPrompt", a_submit, doc="Submit active prompt")

        self.actions.register("HelpCopyLinkTarget", a_help_copy_link_target, doc="Docs browser: copy link target under cursor")
        self.actions.register("OpenUrlUnderCursor", a_open_url_under_cursor, doc="Open URL under cursor (cap.open-url; confirm)")
        self.actions.register("CopyUrlUnderCursor", a_copy_url_under_cursor, doc="Copy URL under cursor to clipboard")


        self.actions.register("QueryReplaceYes", a_qreplace_yes, doc="Query-replace: replace this match")
        self.actions.register("QueryReplaceNo", a_qreplace_no, doc="Query-replace: skip this match")
        self.actions.register("QueryReplaceAll", a_qreplace_all, doc="Query-replace: replace all remaining matches")
        self.actions.register("QueryReplaceLast", a_qreplace_last, doc="Query-replace: replace this match and quit")
        self.actions.register("QueryReplaceQuit", a_qreplace_quit, doc="Query-replace: quit")

        self.actions.register("OpenUrlYes", a_openurl_yes, doc="Open external URL (confirm mode): yes")
        self.actions.register("OpenUrlNo", a_openurl_no, doc="Open external URL (confirm mode): cancel")
        self.actions.register("OpenUrlCopy", a_openurl_copy, doc="Open external URL (confirm mode): copy")

        self.actions.register("PromptHistoryPrev", a_prompt_prev)
        self.actions.register("PromptHistoryNext", a_prompt_next)

        self.actions.register("PromptSuggestPrev", a_prompt_suggest_prev, doc="Picker prompts: move selection up")
        self.actions.register("PromptSuggestNext", a_prompt_suggest_next, doc="Picker prompts: move selection down")
        self.actions.register(
            "PromptSuggestPrevSection",
            a_prompt_suggest_prev_section,
            doc="Picker prompts: jump to start of current/previous section",
        )
        self.actions.register(
            "PromptSuggestNextSection",
            a_prompt_suggest_next_section,
            doc="Picker prompts: jump to start of next section",
        )
        self.actions.register(
            "PromptSuggestPageUp",
            a_prompt_suggest_page_up,
            doc="Picker prompts: jump selection up by a page (prompt.page)",
        )
        self.actions.register(
            "PromptSuggestPageDown",
            a_prompt_suggest_page_down,
            doc="Picker prompts: jump selection down by a page (prompt.page)",
        )
        self.actions.register("PromptCopySelected", a_prompt_copy_selected, doc="Picker prompts: copy selected row")
        self.actions.register("PromptSuggestFirst", a_prompt_suggest_first, doc="Picker prompts: jump selection to first row")
        self.actions.register("PromptSuggestLast", a_prompt_suggest_last, doc="Picker prompts: jump selection to last row")

        self.actions.register("ToggleMacro", a_toggle_macro)
        self.actions.register("PlayMacro", a_play_macro)
        self.actions.register("CancelMacro", a_cancel_macro, doc="Cancel macro recording without saving")

        self.actions.register("SpawnMultiCursorUp", a_spawn_mc_up)
        self.actions.register("SpawnMultiCursorDown", a_spawn_mc_down)
        self.actions.register("SpawnMultiCursorSelect", a_spawn_mc_select)
        self.actions.register("SpawnMultiCursor", a_spawn_mc_lines, doc="Spawn cursors at each line in selection")
        self.actions.register("RemoveMultiCursor", a_remove_mc)
        self.actions.register("RemoveAllMultiCursors", a_remove_all_mc)
        self.actions.register("SkipMultiCursor", a_skip_mc)

        self.actions.register("CyclePrimaryNext", a_cycle_primary_next)
        self.actions.register("CyclePrimaryPrev", a_cycle_primary_prev)
        self.actions.register("CollapseToPrimary", a_collapse_to_primary)

        self.actions.register("Noop", a_noop)
