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
