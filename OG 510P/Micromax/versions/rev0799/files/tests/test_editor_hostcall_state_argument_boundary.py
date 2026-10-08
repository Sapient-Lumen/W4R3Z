from __future__ import annotations

import pytest

from micromax.vm import MicromaxError
from micromax_editor.buffer import Cursor
from micromax_editor.editor import Editor
from micromax_editor.micromax_bridge import install_editor_hostcalls


def _hostcall_error(ed: Editor, name: str, args: list[object], match: str) -> None:
    ed.vm.stack.clear()
    ed.vm.stack.extend(args)
    ed.vm.stack.append(name)
    with pytest.raises(MicromaxError, match=match):
        ed.vm.eval("hostcall")
    assert ed.vm.stack == args


def test_cursor_and_line_hostcall_type_errors_preserve_arguments() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer("arg-boundary", "abcdef")

    cases = [
        ("ed.line", ["bad"], "ed.line: expected int"),
        ("ed.lines", [0, "bad"], "ed.lines: expected int"),
        ("ed.range-text", [0, 0, "bad", 3], "ed.range-text: expected int"),
        ("ed.set-cursor", [0, "bad"], "ed.set-cursor: expected int"),
        ("ed.set-primary", ["bad"], "ed.set-primary: expected int"),
        ("ed.set-selection-range", [0, 0, "bad", 3], "ed.set-selection-range: expected int"),
    ]
    for hostcall, args, match in cases:
        _hostcall_error(ed, hostcall, list(args), match)
    assert ed.cur().buf.get_text() == "abcdef"


def test_set_selections_validates_before_mutating_existing_selection_state() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer("selection-boundary", "abcdef")
    eb = ed.cur()
    eb.cursors[:] = [Cursor(0, 1), Cursor(0, 4)]
    eb.sel_anchors[:] = [Cursor(0, 0), Cursor(0, 3)]
    eb.cursor_ids[:] = [1, 2]
    eb.primary = 0
    before = (
        [(c.line, c.col) for c in eb.cursors],
        [(a.line, a.col) if a is not None else None for a in eb.sel_anchors],
        list(eb.cursor_ids),
        eb.primary,
    )

    bad_state = [[0, 0, 0, 2], ["broken"]]
    _hostcall_error(ed, "ed.set-selections", [bad_state], r"expected \[\] or \[aL aC cL cC\]")

    after = (
        [(c.line, c.col) for c in eb.cursors],
        [(a.line, a.col) if a is not None else None for a in eb.sel_anchors],
        list(eb.cursor_ids),
        eb.primary,
    )
    assert after == before


def test_replace_selections_shape_error_preserves_arguments_and_buffer() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer("replace-selections-boundary", "foo foo")
    assert ed.run_action("SpawnMultiCursorSelect") is True
    assert len(ed.cur().cursors) == 2

    bad_replacements = ["a", "b", "c"]
    _hostcall_error(
        ed,
        "ed.replace-selections",
        [bad_replacements],
        "replacements must be 1 or match cursor count",
    )
    assert ed.cur().buf.get_text() == "foo foo"


def test_set_cursorstate_validation_failure_preserves_stack_and_id_allocator() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer("cursorstate-boundary", "abcdef")
    before_next = ed._next_cursor_id
    bad_state = [0, [[1, 0, 0, -1, -1], [1, "bad", 0, -1, -1]]]

    _hostcall_error(ed, "ed.set-cursorstate", [bad_state], "expected integer entries")

    assert ed._next_cursor_id == before_next
    eb = ed.cur()
    assert [(c.line, c.col) for c in eb.cursors] == [(0, 0)]
    assert eb.cursor_ids == [1]
