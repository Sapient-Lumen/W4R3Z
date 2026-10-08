from __future__ import annotations

from typing import TYPE_CHECKING, Any

from .buffer import Cursor
from .command_formatters import _format_active_buffer_feedback
from .line_edits import DeleteLinesPlan, DuplicateLineBlockPlan, MoveLineBlockPlan
from .simultaneous_edits import SimultaneousEditError, SimultaneousTextEdit

if TYPE_CHECKING:
    from .editor import Editor, EditorBuffer


def install_default_actions(self: Any) -> None:
    # ---- editing ----
    def _cursor_edit_range(ed: Editor, eb: EditorBuffer, index: int) -> tuple[Cursor, Cursor]:
        selection = ed._selection_from_normalized_buffer(eb, int(index))
        if selection is not None:
            start, end = selection.normalized()
            if (start.line, start.col) != (end.line, end.col):
                return start, end
        cursor = eb.cursors[int(index)]
        return cursor, cursor

    def _apply_cursor_edits(
        ed: Editor,
        eb: EditorBuffer,
        edits: list[SimultaneousTextEdit],
        *,
        clear_selection_indices: list[int],
        action_label: str,
        undo_label: str,
    ):
        try:
            return ed._apply_undoable_simultaneous_buffer_edits(
                eb,
                edits,
                clear_selection_indices=clear_selection_indices,
                description=undo_label,
            )
        except SimultaneousEditError as exc:
            ed.message(f"{action_label}: {exc}")
            return None

    def a_insert_text(ed: Editor) -> bool:
        text = str(ed.input.get("text", ""))
        eb = ed.cur()
        ed._normalize_cursor_lists(eb)
        edits: list[SimultaneousTextEdit] = []
        for index in range(len(eb.cursors)):
            start, end = _cursor_edit_range(ed, eb, index)
            edits.append(
                SimultaneousTextEdit(
                    start=start,
                    end=end,
                    text=text,
                    owner=index,
                )
            )
        result = _apply_cursor_edits(
            ed,
            eb,
            edits,
            clear_selection_indices=list(range(len(eb.cursors))),
            action_label="InsertText",
            undo_label=f"insert {len(text)}",
        )
        if result is None or not result.changed:
            return False
        return True

    def a_insert_newline(ed: Editor) -> bool:
        eb = ed.cur()
        ed._normalize_cursor_lists(eb)

        def _leading_ws(value: str) -> str:
            index = 0
            while index < len(value) and value[index] in (" ", "\t"):
                index += 1
            return value[:index]

        def _newline_indent(line: str, col: int, *, enabled: bool) -> str:
            if not enabled:
                return ""
            lead = _leading_ws(line)
            if col <= len(lead):
                return lead[:col]
            return lead

        autoindent_enabled = bool(ed.options.get("autoindent", local=eb.local_options))
        keep_autoindent = bool(ed.options.get("keepautoindent", local=eb.local_options))
        edits: list[SimultaneousTextEdit] = []
        for index in range(len(eb.cursors)):
            start, end = _cursor_edit_range(ed, eb, index)
            line = eb.buf.lines[int(start.line)]
            indent = _newline_indent(line, int(start.col), enabled=autoindent_enabled)
            clear_previous_indent = (
                autoindent_enabled
                and not keep_autoindent
                and bool(line)
                and all(ch in (" ", "\t") for ch in line)
            )
            edit_start = Cursor(int(start.line), 0) if clear_previous_indent else start
            edits.append(
                SimultaneousTextEdit(
                    start=edit_start,
                    end=end,
                    text="\n" + indent,
                    owner=index,
                )
            )

        result = _apply_cursor_edits(
            ed,
            eb,
            edits,
            clear_selection_indices=list(range(len(eb.cursors))),
            action_label="InsertNewline",
            undo_label="newline",
        )
        if result is None or not result.changed:
            return False
        return True

    def _delete_edit_for_cursor(
        ed: Editor,
        eb: EditorBuffer,
        index: int,
        *,
        backward: bool,
    ) -> SimultaneousTextEdit | None:
        start, end = _cursor_edit_range(ed, eb, index)
        if (start.line, start.col) != (end.line, end.col):
            return SimultaneousTextEdit(start=start, end=end, text="", owner=index)

        cursor = eb.cursors[index]
        line_index = int(cursor.line)
        col = int(cursor.col)
        if backward:
            if col > 0:
                start = Cursor(line_index, col - 1)
                end = cursor
            elif line_index > 0:
                start = Cursor(line_index - 1, len(eb.buf.lines[line_index - 1]))
                end = cursor
            else:
                return None
        else:
            line = eb.buf.lines[line_index]
            if col < len(line):
                start = cursor
                end = Cursor(line_index, col + 1)
            elif line_index < len(eb.buf.lines) - 1:
                start = cursor
                end = Cursor(line_index + 1, 0)
            else:
                return None
        return SimultaneousTextEdit(start=start, end=end, text="", owner=index)

    def _delete_per_cursor(ed: Editor, *, backward: bool, label: str, undo_label: str) -> bool:
        eb = ed.cur()
        ed._normalize_cursor_lists(eb)
        edits = [
            edit
            for index in range(len(eb.cursors))
            if (edit := _delete_edit_for_cursor(ed, eb, index, backward=backward)) is not None
        ]
        if not edits:
            return False
        result = _apply_cursor_edits(
            ed,
            eb,
            edits,
            clear_selection_indices=[int(edit.owner) for edit in edits if edit.owner is not None],
            action_label=label,
            undo_label=undo_label,
        )
        if result is None or not result.changed:
            return False
        return True

    def a_backspace(ed: Editor) -> bool:
        return _delete_per_cursor(
            ed,
            backward=True,
            label="Backspace",
            undo_label="backspace",
        )

    def a_delete_forward(ed: Editor) -> bool:
        """Delete one original-document range per cursor."""

        return _delete_per_cursor(
            ed,
            backward=False,
            label="Delete",
            undo_label="delete",
        )

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

        # Delete every range from one immutable snapshot; conflicting ranges
        # fail before the clipboard or buffer is changed.  The shared undoable
        # simultaneous-edit seam retains only the deleted slices and sidecars.
        ranges = ed._all_selection_ranges()
        try:
            result = ed._apply_undoable_simultaneous_buffer_edits(
                eb,
                [
                    SimultaneousTextEdit(
                        start=start,
                        end=end,
                        text="",
                        owner=index,
                    )
                    for index, start, end in ranges
                ],
                clear_selection_indices=[
                    index for index, _start, _end in ranges
                ],
                description="cut",
            )
        except SimultaneousEditError as exc:
            ed.message(f"Cut: {exc}")
            return False
        ok = bool(result.changed)
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

        if system_text is not None:
            per_cursor = [system_text] * len(eb.cursors)
        else:
            items = internal_items
            if internal_kind == 'items' and len(items) == len(eb.cursors):
                per_cursor = list(items)
            else:
                per_cursor = [ed.clipboard_text()] * len(eb.cursors)

        edits: list[SimultaneousTextEdit] = []
        for index in range(len(eb.cursors)):
            start, end = _cursor_edit_range(ed, eb, index)
            line = eb.buf.lines[int(start.line)]
            text = ed._smartpaste_text(
                str(per_cursor[index]),
                line=line,
                col=int(start.col),
            )
            per_cursor[index] = text
            edits.append(
                SimultaneousTextEdit(
                    start=start,
                    end=end,
                    text=text,
                    owner=index,
                )
            )

        result = _apply_cursor_edits(
            ed,
            eb,
            edits,
            clear_selection_indices=list(range(len(eb.cursors))),
            action_label="Paste",
            undo_label="paste",
        )
        if result is None or not result.changed:
            return False

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
    def _selection_trailing_boundary_roles(
        eb: EditorBuffer,
        boundary: Cursor,
    ) -> tuple[set[int], set[int]]:
        """Identify directed selection endpoints that mean "after the block".

        A coordinate at ``(line, 0)`` is otherwise indistinguishable from the
        first character of that line. Pairing it with its selection sidecar is
        what tells a line edit whether it is a half-open trailing boundary or a
        cursor attached to the neighboring line's text.
        """

        cursor_roles: set[int] = set()
        anchor_roles: set[int] = set()
        for index, cursor in enumerate(eb.cursors):
            anchor = eb.sel_anchors[index]
            if anchor is None or anchor == cursor:
                continue
            start, end = sorted(
                (anchor, cursor),
                key=lambda point: (int(point.line), int(point.col)),
            )
            if end != boundary or start == end:
                continue
            if cursor == boundary:
                cursor_roles.add(index)
            if anchor == boundary:
                anchor_roles.add(index)
        return cursor_roles, anchor_roles

    def _install_line_plan(
        eb: EditorBuffer,
        *,
        lines: tuple[str, ...],
        cursors: list[Cursor],
        anchors: list[Cursor | None],
    ) -> None:
        """Commit one source-snapshot line plan as one witnessed mutation."""

        eb.buf.replace_lines(lines)
        eb.cursors[:] = cursors
        eb.sel_anchors[:] = anchors

    def _cut_line_targets(ed: Editor, eb: EditorBuffer) -> set[int]:
        """Return every source row owned by one cursor or its selection.

        Cut-line is a per-cursor operation.  A selected cursor contributes all
        fully or partially selected rows; an unselected cursor contributes its
        own row.  The column-zero endpoint of a multi-line selection is the
        half-open boundary after the selected block, not another selected row.
        Building the union from one normalized source snapshot also avoids the
        old global-bounding-span bug, which could swallow unselected rows
        between disjoint selections or omit cursor-only rows beyond them.
        """

        deleted: set[int] = set()
        for index, cursor in enumerate(eb.cursors):
            selection = ed._selection_from_normalized_buffer(eb, index)
            if selection is None or selection.is_empty():
                deleted.add(int(cursor.line))
                continue
            start, end = selection.normalized()
            first = int(start.line)
            last = int(end.line)
            if int(end.col) == 0 and last > first:
                last -= 1
            deleted.update(range(first, last + 1))
        return deleted

    def a_cut_line(ed: Editor) -> bool:
        eb = ed.cur()
        ed._normalize_cursor_lists(eb)

        # A denied clipboard write must not delete lines first.
        ed.require_clipboard_write()
        before = ed._snapshot_undo_buffer_state(eb)
        plan = DeleteLinesPlan.build(
            eb.buf.lines,
            deleted=_cut_line_targets(ed, eb),
        )
        cut_parts = [eb.buf.lines[line] for line in plan.cut_lines]
        projected_cursors = [plan.project(cursor) for cursor in eb.cursors]
        _install_line_plan(
            eb,
            lines=plan.lines,
            cursors=projected_cursors,
            anchors=[None] * len(projected_cursors),
        )

        if ed._cutline_accum and ed.clipboard_items:
            ed.append_clipboard_items(cut_parts, kind="lines")
        else:
            ed.set_clipboard_items(cut_parts, kind="lines")
        ed._cutline_accum = True

        after = ed._snapshot_undo_buffer_state(eb)
        ed._record_undo_snapshot(eb, before, after, "cut line")
        return True

    def a_duplicate_line(ed: Editor) -> bool:
        eb = ed.cur()
        ed._normalize_cursor_lists(eb)

        before = ed._snapshot_undo_buffer_state(eb)
        selected_span = _selected_line_span(ed)
        has_selected_lines = selected_span is not None
        if selected_span is None:
            line = eb.cursors[eb.primary].line
            selected_span = (line, line)
        start, end = selected_span
        plan = DuplicateLineBlockPlan.build(eb.buf.lines, start=start, end=end)
        cursor_boundary_roles: set[int] = set()
        anchor_boundary_roles: set[int] = set()
        if has_selected_lines:
            cursor_boundary_roles, anchor_boundary_roles = (
                _selection_trailing_boundary_roles(eb, plan.insertion_boundary)
            )

        projected_cursors: list[Cursor] = []
        projected_anchors: list[Cursor | None] = []
        for index, cursor in enumerate(eb.cursors):
            if not has_selected_lines and index == eb.primary:
                projected_cursor = plan.project_duplicate(cursor)
            else:
                projected_cursor = plan.project_original(
                    cursor,
                    keep_boundary=index in cursor_boundary_roles,
                )
            projected_cursors.append(projected_cursor)

            anchor = eb.sel_anchors[index]
            if anchor is None:
                projected_anchors.append(None)
            elif (
                not has_selected_lines
                and index == eb.primary
                and anchor == cursor
            ):
                # A zero-width sidecar is not a real selection.  Moving the
                # primary cursor to its duplicate must not preserve a phantom
                # anchor that later code can mistake for selection state.
                projected_anchors.append(None)
            else:
                projected_anchors.append(
                    plan.project_original(
                        anchor,
                        keep_boundary=index in anchor_boundary_roles,
                    )
                )

        _install_line_plan(
            eb,
            lines=plan.lines,
            cursors=projected_cursors,
            anchors=projected_anchors,
        )
        after = ed._snapshot_undo_buffer_state(eb)
        ed._record_undo_snapshot(eb, before, after, "duplicate line")
        return True

    def _move_line_block(ed: Editor, *, direction: int, undo_label: str) -> bool:
        eb = ed.cur()
        ed._normalize_cursor_lists(eb)

        before = ed._snapshot_undo_buffer_state(eb)
        span = _selected_line_span(ed)
        if span is None:
            line = eb.cursors[eb.primary].line
            span = (line, line)
        start, end = span
        if direction < 0 and start <= 0:
            return False
        if direction > 0 and end >= len(eb.buf.lines) - 1:
            return False

        plan = MoveLineBlockPlan.build(
            eb.buf.lines,
            start=start,
            end=end,
            direction=direction,
        )
        cursor_boundary_roles, anchor_boundary_roles = (
            _selection_trailing_boundary_roles(eb, plan.source_trailing_boundary)
        )
        projected_cursors = [
            plan.project(
                cursor,
                trailing_boundary=index in cursor_boundary_roles,
            )
            for index, cursor in enumerate(eb.cursors)
        ]
        projected_anchors = [
            (
                plan.project(
                    anchor,
                    trailing_boundary=index in anchor_boundary_roles,
                )
                if anchor is not None
                else None
            )
            for index, anchor in enumerate(eb.sel_anchors)
        ]
        _install_line_plan(
            eb,
            lines=plan.lines,
            cursors=projected_cursors,
            anchors=projected_anchors,
        )

        after = ed._snapshot_undo_buffer_state(eb)
        ed._record_undo_snapshot(eb, before, after, undo_label)
        return True

    def a_move_lines_up(ed: Editor) -> bool:
        return _move_line_block(ed, direction=-1, undo_label="move lines up")

    def a_move_lines_down(ed: Editor) -> bool:
        return _move_line_block(ed, direction=1, undo_label="move lines down")

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
        ed._normalize_cursor_lists(eb)
        pref = str(ed.options.get("indent", local=eb.local_options))
        if pref == "":
            return False
        result = _apply_cursor_edits(
            ed,
            eb,
            [
                SimultaneousTextEdit(
                    start=Cursor(line, 0),
                    end=Cursor(line, 0),
                    text=pref,
                )
                for line in range(span[0], span[1] + 1)
            ],
            clear_selection_indices=[],
            action_label="IndentSelection",
            undo_label="indent",
        )
        if result is None or not result.changed:
            return False

        return True

    def a_unindent_selection(ed: Editor) -> bool:
        span = _selected_line_span(ed)
        if span is None:
            return False
        eb = ed.cur()
        ed._normalize_cursor_lists(eb)
        pref = str(ed.options.get("indent", local=eb.local_options))
        if pref == "":
            return False
        edits: list[SimultaneousTextEdit] = []
        for li in range(span[0], span[1] + 1):
            ln = eb.buf.lines[li]
            if ln.startswith(pref):
                removed = len(pref)
            else:
                removed = 0
                while removed < len(pref) and removed < len(ln) and ln[removed] == " ":
                    removed += 1
            if removed > 0:
                edits.append(
                    SimultaneousTextEdit(
                        start=Cursor(li, 0),
                        end=Cursor(li, removed),
                        text="",
                    )
                )
        if not edits:
            return False
        result = _apply_cursor_edits(
            ed,
            eb,
            edits,
            clear_selection_indices=[],
            action_label="UnindentSelection",
            undo_label="unindent",
        )
        if result is None or not result.changed:
            return False

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

        edits: list[SimultaneousTextEdit] = []
        for index in range(len(eb.cursors)):
            start, end = _cursor_edit_range(ed, eb, index)
            line = eb.buf.lines[int(start.line)]
            edits.append(
                SimultaneousTextEdit(
                    start=start,
                    end=end,
                    text=_tab_text_at(line, int(start.col)),
                    owner=index,
                )
            )

        result = _apply_cursor_edits(
            ed,
            eb,
            edits,
            clear_selection_indices=list(range(len(eb.cursors))),
            action_label="InsertTab",
            undo_label="tab",
        )
        if result is None or not result.changed:
            return False
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

    def a_file_picker(ed: Editor) -> bool:
        return bool(ed.enter_file_prompt())

    def a_new_buffer(ed: Editor) -> bool:
        try:
            ed.create_untitled_buffer()
        except Exception as e:
            ed.message(f"new: {e}")
            return False
        ed.message(_format_active_buffer_feedback(ed, prefix="new"))
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

    def _mc_needle(ed: Editor, eb: EditorBuffer) -> tuple[str, int, bool] | None:
        """Return the active occurrence needle and whether this call selected it."""

        primary = int(eb.primary)
        selection_created = False
        selection = ed._selection_from_normalized_buffer(eb, primary)
        if selection is None or selection.is_empty():
            word_range = eb.buf.word_range_at(eb.cursors[primary])
            if word_range is None:
                return None
            word_start, word_end = word_range
            eb.sel_anchors[primary] = word_start
            eb.cursors[primary] = word_end
            selection = ed._selection_from_normalized_buffer(eb, primary)
            selection_created = True

        assert selection is not None
        start, end = selection.normalized()
        needle = eb.buf.get_range_text(start, end)
        # The current literal-search substrate is line-local.  Refuse a
        # multiline selection rather than inventing a same-line endpoint.
        if needle == "" or "\n" in needle:
            return None
        return needle, len(needle), selection_created

    def _find_next_literal(ed: Editor, eb: EditorBuffer, needle: str, start: Cursor) -> Cursor | None:
        ignorecase = bool(ed.options.get("ignorecase", local=eb.local_options))
        if not ignorecase:
            return eb.buf.find(needle, start=start)
        # Small case-insensitive forward search with Buffer.find's line-local
        # semantics.  Lowercasing preserves the established editor behavior.
        nlow = needle.lower()
        cur = eb.buf.clamp(start)
        idx = eb.buf.lines[cur.line].lower().find(nlow, cur.col)
        if idx >= 0:
            return Cursor(cur.line, idx)
        for line_index in range(cur.line + 1, len(eb.buf.lines)):
            idx = eb.buf.lines[line_index].lower().find(nlow)
            if idx >= 0:
                return Cursor(line_index, idx)
        return None

    def _mc_selected_occurrences(
        ed: Editor,
        eb: EditorBuffer,
        needle: str,
    ) -> list[tuple[int, int, Cursor, Cursor]]:
        """Return selected matches as ``(cursor_id, index, start, end)`` rows."""

        ignorecase = bool(ed.options.get("ignorecase", local=eb.local_options))
        expected = needle.lower() if ignorecase else needle
        matches: list[tuple[int, int, Cursor, Cursor]] = []
        for index in range(len(eb.cursors)):
            selection = ed._selection_from_normalized_buffer(eb, index)
            if selection is None or selection.is_empty():
                continue
            start, end = selection.normalized()
            selected = eb.buf.get_range_text(start, end)
            comparable = selected.lower() if ignorecase else selected
            if comparable == expected:
                matches.append((int(eb.cursor_ids[index]), index, start, end))
        return matches

    def _mc_next_unoccupied(
        ed: Editor,
        eb: EditorBuffer,
        needle: str,
        start: Cursor,
        occupied: set[tuple[int, int, int, int]],
    ) -> Cursor | None:
        """Find the next literal occurrence not already selected."""

        needle_length = len(needle)
        search_from = Cursor(int(start.line), int(start.col))
        while True:
            match = _find_next_literal(ed, eb, needle, search_from)
            if match is None:
                return None
            key = (
                int(match.line),
                int(match.col),
                int(match.line),
                int(match.col) + needle_length,
            )
            if key not in occupied:
                return match
            search_from = Cursor(int(match.line), int(match.col) + max(1, needle_length))

    def a_spawn_mc_select(ed: Editor) -> bool:
        eb = ed.cur()
        ed._normalize_cursor_lists(eb)
        info = _mc_needle(ed, eb)
        if info is None:
            return False
        needle, needle_length, selection_created = info
        selected = _mc_selected_occurrences(ed, eb, needle)
        if not selected:
            return selection_created

        # Cursor IDs retain creation order while the public lists remain in
        # document order.  The newest selected occurrence is therefore the
        # truthful continuation point, independent of buffer switches or edits.
        _cursor_id, _index, _start, end = max(selected, key=lambda row: row[0])
        occupied = {
            (start.line, start.col, finish.line, finish.col)
            for _cid, _idx, start, finish in selected
        }
        match = _mc_next_unoccupied(ed, eb, needle, end, occupied)
        if match is None:
            return selection_created

        eb.cursors.append(Cursor(match.line, match.col + needle_length))
        eb.sel_anchors.append(Cursor(match.line, match.col))
        eb.cursor_ids.append(ed._alloc_cursor_id())
        ed._normalize_cursor_lists(eb)
        return True

    def a_skip_mc(ed: Editor) -> bool:
        eb = ed.cur()
        ed._normalize_cursor_lists(eb)
        info = _mc_needle(ed, eb)
        if info is None:
            return False
        needle, needle_length, selection_created = info
        selected = _mc_selected_occurrences(ed, eb, needle)
        if not selected:
            return selection_created

        _cursor_id, target_index, _start, end = max(selected, key=lambda row: row[0])
        occupied = {
            (start.line, start.col, finish.line, finish.col)
            for _cid, _idx, start, finish in selected
        }
        match = _mc_next_unoccupied(ed, eb, needle, end, occupied)
        if match is None:
            return selection_created

        # Skip only the newest selection.  Earlier choices and the primary
        # designation remain intact for the eventual simultaneous edit.
        eb.sel_anchors[target_index] = Cursor(match.line, match.col)
        eb.cursors[target_index] = Cursor(match.line, match.col + needle_length)
        ed._normalize_cursor_lists(eb)
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
    self.actions.register("FilePicker", a_file_picker, doc="Open the bounded project-file picker")
    self.actions.register("NewBuffer", a_new_buffer, doc="Create a collision-free untitled buffer")
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
