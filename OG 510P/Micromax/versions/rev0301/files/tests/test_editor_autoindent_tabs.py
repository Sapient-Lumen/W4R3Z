from __future__ import annotations

from micromax_editor.buffer import Cursor
from micromax_editor.editor import Editor


def test_insert_newline_preserves_current_line_indentation() -> None:
    ed = Editor()
    ed.new_buffer('*t*', '    foo')

    # Enter at end-of-line copies leading indentation onto the new line.
    ed.cur().cursors[0] = Cursor(0, len('    foo'))
    assert ed.run_action('InsertNewline') is True
    assert ed.cur().buf.get_text() == '    foo\n    '
    assert ed.primary_cursor() == Cursor(1, 4)


def test_insert_newline_does_not_double_indent_when_splitting_before_indent() -> None:
    ed = Editor()
    ed.new_buffer('*t*', '    foo')

    # Enter at col 0 should create a blank line above without duplicating indent.
    ed.cur().cursors[0] = Cursor(0, 0)
    assert ed.run_action('InsertNewline') is True
    assert ed.cur().buf.lines == ['', '    foo']
    assert ed.primary_cursor() == Cursor(1, 0)


def test_insert_newline_inside_indent_splits_indent_prefix_safely() -> None:
    ed = Editor()
    ed.new_buffer('*t*', '    foo')

    # Splitting inside the indent prefix should not duplicate spaces.
    ed.cur().cursors[0] = Cursor(0, 2)
    assert ed.run_action('InsertNewline') is True
    assert ed.cur().buf.lines == ['  ', '    foo']
    assert ed.primary_cursor() == Cursor(1, 2)


def test_insert_tab_respects_tabstospaces_and_tabsize() -> None:
    ed = Editor()

    # Default: tabstospaces=true, tabsize=4.
    ed.new_buffer('*t*', '')
    ed.cur().cursors[0] = Cursor(0, 0)
    assert ed.run_action('InsertTab') is True
    assert ed.cur().buf.get_text() == '    '
    assert ed.primary_cursor() == Cursor(0, 4)

    # Align to the next tab stop.
    ed.new_buffer('*u*', 'x')
    ed.cur().cursors[0] = Cursor(0, 1)
    assert ed.run_action('InsertTab') is True
    assert ed.cur().buf.get_text() == 'x   '
    assert ed.primary_cursor() == Cursor(0, 4)

    # Visual-column alignment should account for existing tabs.
    ed.new_buffer('*v*', '\t')
    ed.cur().cursors[0] = Cursor(0, 1)
    assert ed.run_action('InsertTab') is True
    assert ed.cur().buf.get_text() == '\t    '
    assert ed.primary_cursor() == Cursor(0, 5)

    # If tabstospaces is disabled, InsertTab inserts a literal tab.
    ed.options.set('tabstospaces', 'false')
    ed.new_buffer('*w*', '')
    ed.cur().cursors[0] = Cursor(0, 0)
    assert ed.run_action('InsertTab') is True
    assert ed.cur().buf.get_text() == '\t'
    assert ed.primary_cursor() == Cursor(0, 1)


def test_insert_newline_clears_whitespace_only_autoindent_line_by_default() -> None:
    ed = Editor()
    ed.new_buffer('*t*', '    ')

    ed.cur().cursors[0] = Cursor(0, 4)
    assert ed.run_action('InsertNewline') is True
    assert ed.cur().buf.lines == ['', '    ']
    assert ed.primary_cursor() == Cursor(1, 4)


def test_insert_newline_keeps_whitespace_only_autoindent_line_when_enabled() -> None:
    ed = Editor()
    ed.exec_command_line('set keepautoindent true')
    ed.new_buffer('*t*', '    ')

    ed.cur().cursors[0] = Cursor(0, 4)
    assert ed.run_action('InsertNewline') is True
    assert ed.cur().buf.lines == ['    ', '    ']
    assert ed.primary_cursor() == Cursor(1, 4)


def test_tabmovement_jumps_leading_space_runs_by_tabsize() -> None:
    ed = Editor()
    ed.new_buffer('*t*', '    alpha')
    ed.exec_command_line('set tabmovement true')

    eb = ed.cur()
    eb.cursors[0] = Cursor(0, 0)
    assert ed.run_action('CursorRight') is True
    assert ed.primary_cursor() == Cursor(0, 4)

    assert ed.run_action('CursorLeft') is True
    assert ed.primary_cursor() == Cursor(0, 0)


def test_tabmovement_stays_characterwise_outside_leading_indent_or_without_tabstospaces() -> None:
    ed = Editor()
    ed.new_buffer('*t*', 'xx    alpha')
    ed.exec_command_line('set tabmovement true')

    eb = ed.cur()
    eb.cursors[0] = Cursor(0, 2)
    assert ed.run_action('CursorRight') is True
    assert ed.primary_cursor() == Cursor(0, 3)

    ed2 = Editor()
    ed2.new_buffer('*u*', '    alpha')
    ed2.exec_command_line('set tabmovement true')
    ed2.exec_command_line('set tabstospaces false')

    eb2 = ed2.cur()
    eb2.cursors[0] = Cursor(0, 0)
    assert ed2.run_action('CursorRight') is True
    assert ed2.primary_cursor() == Cursor(0, 1)


def test_tabmovement_selection_motion_reuses_same_step_rule() -> None:
    ed = Editor()
    ed.new_buffer('*t*', '    alpha')
    ed.exec_command_line('set tabmovement true')

    eb = ed.cur()
    eb.cursors[0] = Cursor(0, 0)
    assert ed.run_action('SelectRight') is True
    assert ed.primary_cursor() == Cursor(0, 4)
    sel = ed.selection_text(None)
    assert sel == '    '

    assert ed.run_action('SelectLeft') is True
    assert ed.primary_cursor() == Cursor(0, 0)
    sel2 = ed.selection_text(None)
    assert sel2 == ''


def test_insert_newline_can_disable_autoindent() -> None:
    ed = Editor()
    ed.exec_command_line('set autoindent false')
    ed.new_buffer('*t*', '    foo')

    ed.cur().cursors[0] = Cursor(0, len('    foo'))
    assert ed.run_action('InsertNewline') is True
    assert ed.cur().buf.lines == ['    foo', '']
    assert ed.primary_cursor() == Cursor(1, 0)


def test_insert_newline_without_autoindent_does_not_clear_whitespace_only_line() -> None:
    ed = Editor()
    ed.exec_command_line('set autoindent false')
    ed.new_buffer('*t*', '    ')

    ed.cur().cursors[0] = Cursor(0, 4)
    assert ed.run_action('InsertNewline') is True
    assert ed.cur().buf.lines == ['    ', '']
    assert ed.primary_cursor() == Cursor(1, 0)


def test_keepautoindent_only_applies_when_autoindent_is_enabled() -> None:
    ed = Editor()
    ed.exec_command_line('set autoindent false')
    ed.exec_command_line('set keepautoindent true')
    ed.new_buffer('*t*', '    ')

    ed.cur().cursors[0] = Cursor(0, 4)
    assert ed.run_action('InsertNewline') is True
    assert ed.cur().buf.lines == ['    ', '']
    assert ed.primary_cursor() == Cursor(1, 0)
