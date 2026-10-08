from __future__ import annotations

"""micromax_editor.tui

A tiny curses-based TUI for the headless editor core.

Goal: provide the minimal tactile loop early:
  input -> ed.dispatch_key -> render

This intentionally avoids advanced rendering (syntax highlighting, spans, mouse,
etc.). It's meant to be a tiny proving ground for the core semantics.
"""

import curses
import sys
from dataclasses import dataclass
import time
from typing import Any
import re

from .editor import Editor, md_norm_ref_id, md_inline_link_target
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

def md_link_label_spans(line: str, defs: dict[str, str]) -> list[tuple[int, int]]:
    """Return underline spans for markdown links in a docs/help line.

    This is intentionally tiny and mirrors the editor's docs link parsing:
      - inline links: [label](dest "title")
      - reference links: [label][id] and [label][]
      - shortcut reference links: [id] (only when a matching definition exists)
      - autolinks: <https://...> / <mailto:...>

    Spans are (start,end) indices for the *label text* (or URL) inside the
    visible delimiters so the TUI can underline them.
    """

    s = str(line or '')
    spans: list[tuple[int, int]] = []

    # Inline: [label](...)
    for m in re.finditer(r"\[(?P<label>[^\]]+)\]\((?P<inner>[^)]+)\)", s):
        inner = str(m.group('inner') or '')
        if not md_inline_link_target(inner):
            continue
        a = int(m.start('label'))
        b = int(m.end('label'))
        if a != b:
            spans.append((a, b))

    # Reference: [label][id] and [label][]
    for m in re.finditer(r"\[(?P<label>[^\]]+)\]\[(?P<id>[^\]]*)\]", s):
        label = str(m.group('label') or '').strip()
        rid = str(m.group('id') or '').strip() or label
        if not defs.get(md_norm_ref_id(rid)):
            continue
        a = int(m.start('label'))
        b = int(m.end('label'))
        if a != b:
            spans.append((a, b))

    # Shortcut reference: [id]
    for m in re.finditer(r"\[(?P<id>[^\]]+)\]", s):
        a0, b0 = int(m.start()), int(m.end())
        # Skip images: ![alt]
        if a0 > 0 and s[a0 - 1] == '!':
            continue
        after = s[b0:b0+1]
        if after in (':', '['):
            continue
        # Skip valid inline links: [id](...)
        if after == '(':
            mm = re.match(r"\[(?P<label>[^\]]+)\]\((?P<inner>[^)]+)\)", s[a0:])
            if mm is not None and md_inline_link_target(str(mm.group('inner') or '')):
                continue
        rid = str(m.group('id') or '').strip()
        if not rid:
            continue
        if not defs.get(md_norm_ref_id(rid)):
            continue
        a = int(m.start('id'))
        b = int(m.end('id'))
        if a != b:
            spans.append((a, b))

    # Autolinks: <https://...>
    for m in re.finditer(r"<(?P<url>(?:https?://|mailto:)[^ >]+)>", s):
        a = int(m.start('url'))
        b = int(m.end('url'))
        if a != b:
            spans.append((a, b))

    spans.sort()
    return spans



def md_inline_code_spans(line: str) -> list[tuple[int, int]]:
    """Return dim spans for inline markdown code in a docs/help line.

    This is intentionally tiny:
      - recognizes `code` spans (single backticks)
      - returns spans for the *inside* text (excluding the backticks)
      - ignores fenced code block markers (```).

    Spans are (start,end) indices into *line*.
    """

    s = str(line or "")
    if not s:
        return []
    if s.strip().startswith("```"):
        return []

    out: list[tuple[int, int]] = []
    i = 0
    while True:
        a = s.find("`", i)
        if a < 0:
            break
        if a > 0 and s[a - 1] == "\\":
            i = a + 1
            continue
        b = s.find("`", a + 1)
        if b < 0:
            break
        if b > a + 1:
            out.append((a + 1, b))
        i = b + 1
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

    This mirrors `_prompt_display_lines` but preserves enough metadata for the
    TUI to style rows by kind (commands/actions/files/links/etc.) without
    changing the headless core.
    """

    p = ed.prompt
    if p is None or not p.suggestion_rows or max_lines <= 0:
        return []
    kind = str(p.kind or "")
    if kind in ("command", "find"):
        return []

    rows = [list(r[:4]) for r in p.suggestion_rows]

    def _label_for(row: list[str]) -> str:
        return str(ed.prompt_row_section_label([str(x) for x in row], prompt_kind=kind))

    # Precompute section labels + counts so headers can show useful totals.
    labels: list[str] = []
    counts: dict[str, int] = {}
    for row in rows:
        lbl = _label_for([str(x) for x in row])
        labels.append(lbl)
        if lbl:
            counts[lbl] = int(counts.get(lbl, 0)) + 1

    def _label_disp(lbl: str) -> str:
        n = int(counts.get(lbl, 0) or 0)
        return f"{lbl} ({n})" if n > 0 else str(lbl)

    # Build flattened list with section headers.
    # Each entry is (is_header, suggestion_index, section_label, row).
    flat: list[tuple[bool, int | None, str, list[str] | None]] = []
    last_label = ""
    for idx2, row in enumerate(rows):
        label = labels[idx2] if idx2 < len(labels) else _label_for([str(x) for x in row])
        if label and label != last_label:
            flat.append((True, None, label, None))
            last_label = label
        flat.append((False, idx2, label, [str(x) for x in row]))

    sel = int(p.suggest_index) if p.suggestion_rows else 0
    # Find the display position of the selected row (for centering).
    sel_pos = 0
    for i, (_is_hdr, sidx, _lbl, _row) in enumerate(flat):
        if sidx == sel:
            sel_pos = i
            break

    # Windowing: keep selection visible, but reserve space for "more" markers.
    content_n = int(max_lines)
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

    out: list[PromptDisplayItem] = []

    # Sticky section header (fzf-ish header-lines concept).
    sticky_label = ""
    if start > 0 and start < len(flat):
        is_hdr0, _sidx0, lbl0, _row0 = flat[start]
        if not is_hdr0 and lbl0:
            sticky_label = str(lbl0)

    above_n = sum(1 for is_hdr, _sidx, _lbl, _row in flat[:start] if not is_hdr)
    below_n = sum(1 for is_hdr, _sidx, _lbl, _row in flat[end:] if not is_hdr)

    if show_top:
        suffix = f" (+{above_n})" if above_n > 0 else ""
        out.append(PromptDisplayItem((f"↑ more…{suffix}")[: max(0, width)], is_more=True, row_kind="more"))
    if sticky_label:
        out.append(PromptDisplayItem((f"-- {_label_disp(sticky_label)} --")[: max(0, width)], is_header=True, row_kind="header", section_label=sticky_label))

    for is_hdr, sidx, lbl, row in flat[start:end]:
        if is_hdr:
            out.append(PromptDisplayItem((f"-- {_label_disp(lbl)} --")[: max(0, width)], is_header=True, row_kind="header", section_label=str(lbl)))
            continue

        assert row is not None
        name = str(row[0] if len(row) > 0 else "")
        row_kind = str(row[1] if len(row) > 1 else "")
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

        detail = ""
        if menu and info:
            detail = f"{menu} | {info}"
        else:
            detail = menu or info
        body = name if not detail else f"{name} — {detail}"
        prefix = ">" if sidx == sel else " "
        out.append(
            PromptDisplayItem(
                (prefix + " " + body)[: max(0, width)],
                is_selected=bool(sidx == sel),
                row_kind=row_kind,
                section_label=str(lbl or ""),
            )
        )

    if show_bottom:
        suffix = f" (+{below_n})" if below_n > 0 else ""
        out.append(PromptDisplayItem((f"↓ more…{suffix}")[: max(0, width)], is_more=True, row_kind="more"))

    # Keep within max_lines when sticky headers are added.
    if len(out) > max_lines:
        while len(out) > max_lines:
            if show_bottom and out and out[-1].text.startswith("↓") and len(out) >= 2:
                out.pop(-2)
            else:
                out.pop()

    return out


def _prompt_display_lines(ed: Editor, *, max_lines: int, width: int) -> list[str]:
    """Render the active prompt suggestions into display lines (best-effort).

    This remains a simple list-of-strings helper used by unit tests.
    The curses TUI uses `_prompt_display_items` for style hints.
    """

    return [it.text for it in _prompt_display_items(ed, max_lines=max_lines, width=width)]


def _render(stdscr: "curses._CursesWindow", ed: Editor) -> None:
    stdscr.erase()
    h, w = stdscr.getmaxyx()

    # Reserve 2 lines: prompt + status.
    # When a picker-style prompt is active, also reserve a small suggestions area.
    sug_h = 0
    if ed.prompt is not None and ed.prompt.kind not in ("command", "find") and ed.prompt.suggestion_rows:
        sug_h = min(8, max(1, h // 4))
    view_h = max(1, h - 2 - sug_h)
    view_w = max(1, w)
    ed.set_viewport(height=view_h, width=view_w, follow_cursor=True)
    vp = ed.viewport_model()

    eb = ed.cur()
    top = int(vp["top_line"])
    left = int(vp["left_col"])

    # Buffer lines
    rows = ed.view_rows(height=view_h, width=view_w)
    is_help = bool(ed.current_help_doc_topic())
    defs = ed._md_reference_defs(list(eb.buf.lines)) if is_help else {}
    cy, cx = ed.cursor_view_pos(height=view_h, width=view_w)

    for row, (_li, _start, frag) in enumerate(rows):
        try:
            if not is_help:
                stdscr.addnstr(row, 0, frag, view_w)
                continue
            is_heading = bool(re.match(r"^\s{0,3}#{1,6}\s+", str(frag)))
            base_attr = curses.A_BOLD if is_heading else 0
            if is_heading and curses.has_colors():
                base_attr |= curses.color_pair(1)

            link_spans = md_link_label_spans(str(frag), defs)
            code_spans = md_inline_code_spans(str(frag))

            def _write_range(a: int, b: int, attr0: int) -> None:
                """Write frag[a:b] applying inline-code dim spans (best-effort)."""

                if b <= a:
                    return
                if not code_spans:
                    stdscr.addnstr(row, a, frag[a:b], max(0, view_w - a), attr0)
                    return

                cur = int(a)
                for ca, cb in code_spans:
                    ca = int(ca)
                    cb = int(cb)
                    if cb <= cur or ca >= b:
                        continue
                    if ca > cur:
                        stdscr.addnstr(row, cur, frag[cur:ca], max(0, view_w - cur), attr0)
                    aa = max(cur, ca)
                    bb = min(int(b), cb)
                    if bb > aa:
                        stdscr.addnstr(row, aa, frag[aa:bb], max(0, view_w - aa), attr0 | curses.A_DIM)
                    cur = bb
                if cur < b:
                    stdscr.addnstr(row, cur, frag[cur:b], max(0, view_w - cur), attr0)

            if not link_spans:
                _write_range(0, len(frag), base_attr)
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
                                stdscr.addnstr(y, seg_a, txt, max(0, view_w - seg_a), a1)
                                return
                            if seg_a >= detail_start:
                                stdscr.addnstr(y, seg_a, txt, max(0, view_w - seg_a), a2)
                                return
                            # Split at detail boundary.
                            k = max(0, int(detail_start) - int(seg_a))
                            if k > 0:
                                stdscr.addnstr(y, seg_a, txt[:k], max(0, view_w - seg_a), a1)
                            stdscr.addnstr(y, seg_a + k, txt[k:], max(0, view_w - (seg_a + k)), a2)

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
                            stdscr.addnstr(y, 0, line[:detail_start], view_w, base_attr)
                            stdscr.addnstr(y, detail_start, line[detail_start:], max(0, view_w - detail_start), detail_attr)
                        else:
                            stdscr.addnstr(y, 0, line, view_w, base_attr)
                else:
                    stdscr.addnstr(y, 0, line, view_w, attr)
            except curses.error:
                pass

    # Prompt line
    prompt_y = h - 2
    if ed.prompt is not None:
        kind = str(ed.prompt.kind)
        prefix = ":" if kind in ("command", "palette") else ("/" if kind == "find" else "?")
        text = str(ed.prompt.text)
        line = prefix + text

        # Minimal picker usability: show the currently selected suggestion preview.
        preview = str(st.get("prompt_current_preview", "") or "")
        if preview and kind not in ("command", "find"):
            # Keep it single-line and truncatable.
            line = line + "  | " + preview

        try:
            stdscr.addnstr(prompt_y, 0, line, view_w)
        except curses.error:
            pass
    else:
        # show last message when no prompt is active
        msg = str(st.get("last_message", ""))
        try:
            stdscr.addnstr(prompt_y, 0, msg, view_w)
        except curses.error:
            pass

    # Status line
    status_y = h - 1
    status = ed.statusline_text(view_w)
    try:
        stdscr.addnstr(status_y, 0, status, view_w)
    except curses.error:
        pass

    # Place the terminal cursor.
    try:
        if ed.prompt is not None:
            px = 1 + int(st.get("prompt_cursor", 0)) - left  # prompt isn't horizontally scrolled yet
            stdscr.move(prompt_y, max(0, min(view_w - 1, px)))
        else:
            cy, cx = ed.cursor_view_pos(height=view_h, width=view_w)
            stdscr.move(max(0, min(view_h - 1, int(cy))), max(0, min(view_w - 1, int(cx))))
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
