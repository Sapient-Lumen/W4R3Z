from __future__ import annotations

from typing import TYPE_CHECKING, Any

from .buffer import Cursor

if TYPE_CHECKING:
    from .editor import Editor, EditorBuffer


def install_default_actions(self: Any) -> None:
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

        # A denied clipboard write must not delete text first.
        ed.require_clipboard_write()

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

        internal_items: list[str] = []
        internal_kind = 'items'
        if system_text is None:
            internal_items, internal_kind = ed.clipboard_items_snapshot()

        if system_text is None and not internal_items:
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
            items = internal_items
            if internal_kind == 'items' and len(items) == len(eb.cursors):
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
        # A denied clipboard write must not delete lines first.
        ed.require_clipboard_write()
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
            ed.append_clipboard_items(list(reversed(cut_parts)), kind="lines")
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
        if not ed.set_search_literal(True):
            return False
        ed.enter_prompt("find")
        return True

    def a_find_literal(ed: Editor) -> bool:
        if not ed.set_search_literal(True):
            return False
        ed.enter_prompt("find")
        return True

    def a_find_regex(ed: Editor) -> bool:
        if not ed.set_search_literal(False):
            return False
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
        return bool(ed.open_url_confirm_yes())

    def a_openurl_no(ed: Editor) -> bool:
        return bool(ed.open_url_confirm_no())

    def a_openurl_copy(ed: Editor) -> bool:
        return bool(ed.open_url_confirm_copy())

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
