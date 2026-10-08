from micromax_editor.editor import Editor
from micromax_editor.micromax_bridge import install_editor_hostcalls
from micromax_editor.buffer import Cursor


def _set_primary_cursor(ed: Editor, *, line: int, col: int) -> None:
    eb = ed.cur()
    ed._normalize_cursor_lists(eb)
    eb.cursors[eb.primary] = eb.buf.clamp(Cursor(int(line), int(col)))


def _primary_cursor(ed: Editor) -> tuple[int, int]:
    eb = ed.cur()
    ed._normalize_cursor_lists(eb)
    c = eb.cursors[eb.primary]
    return (int(c.line), int(c.col))


def test_jumppick_restores_explicit_history_entry() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.new_buffer('a', 'one\ntwo\nthree\nfour\nfive\n')

    _set_primary_cursor(ed, line=0, col=0)
    assert ed.push_jump() is True

    _set_primary_cursor(ed, line=1, col=1)  # 'two'
    assert ed.push_jump() is True

    _set_primary_cursor(ed, line=4, col=0)  # 'five'
    assert ed.push_jump() is True

    ed.exec_command_line('jumppick')
    assert ed.prompt is not None
    assert ed.prompt.kind == 'jump'
    assert ed.prompt.suggestions

    # Select the middle entry (index 2 in 1-based terms).
    assert '2' in ed.prompt.suggestions
    ed.prompt.suggest_index = ed.prompt.suggestions.index('2')
    assert ed.submit_prompt() is True

    assert _primary_cursor(ed) == (1, 1)
    eb = ed.cur()
    assert int(eb.jump_index) == 1
    target = str(eb.buf.path or eb.name)
    assert ed.status_model()["last_message"] == f"jump: {target} @ 2:1"



def test_jumppick_groups_rows_by_current_back_and_forward() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.new_buffer('a', 'one\ntwo\nthree\nfour\nfive\n')

    _set_primary_cursor(ed, line=0, col=0)
    assert ed.push_jump() is True
    _set_primary_cursor(ed, line=1, col=1)
    assert ed.push_jump() is True
    _set_primary_cursor(ed, line=4, col=0)
    assert ed.push_jump() is True

    assert ed.jump_to_index(1) is True

    assert [row[0] for row in ed.jump_prompt_rows()] == ['2', '1', '3']
    assert [sec[0] for sec in ed.jump_section_rows('')] == ['Current', 'Back', 'Forward']

    ed.exec_command_line('jumppick')
    assert ed.prompt is not None
    assert ed.prompt.kind == 'jump'
    assert [row[0] for row in ed.prompt.suggestion_rows] == ['2', '1', '3']

    labels = [
        ed.prompt_row_section_label([str(x) for x in row[:4]], prompt_kind='jump')
        for row in ed.prompt.suggestion_rows
    ]
    assert labels == ['Current', 'Back', 'Forward']
    assert ed.prompt_current_section() == 'Current'
    assert ed.prompt_current_preview().startswith('Current: 2')



def test_jumps_command_reports_zero_inventory_count() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.new_buffer('a', 'one\n')

    assert ed.exec_command_line('jumps') is True
    assert ed.messages[-1] == 'jumps: 0 jump(s)'



def test_jumps_command_reports_current_back_and_forward_register() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.new_buffer('a', 'one\ntwo\nthree\n')

    _set_primary_cursor(ed, line=0, col=0)
    assert ed.push_jump() is True
    _set_primary_cursor(ed, line=1, col=1)
    assert ed.push_jump() is True
    _set_primary_cursor(ed, line=2, col=2)
    assert ed.push_jump() is True
    assert ed.jump_to_index(1) is True

    assert ed.exec_command_line('jumps') is True
    assert ed.messages[-1] == (
        'jumps: 3 jump(s), '
        '[current] #2 a @ 2:1: two; '
        '[back 1] #1 a @ 1:0: one; '
        '[forward 1] #3 a @ 3:2: three'
    )


def test_jump_detail_row_hostcall_and_showjump_surface() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.new_buffer('a', 'one\ntwo\nthree\n')

    _set_primary_cursor(ed, line=0, col=0)
    assert ed.push_jump() is True
    _set_primary_cursor(ed, line=1, col=1)
    assert ed.push_jump() is True
    _set_primary_cursor(ed, line=2, col=2)
    assert ed.push_jump() is True
    assert ed.jump_to_index(1) is True

    ed.vm.stack.clear()
    ed.vm.eval('"1" "ed.jump-detail-row" hostcall')
    row = ed.vm.stack.pop()
    assert row == ['1', 1, 'back', 1, 'a', '1:0', 'one']

    assert ed.exec_command_line('showjump 1') is True
    assert ed.messages[-1] == 'showjump 1 [back 1] a @ 1:0 — one'

    assert ed.exec_command_line('showjump 2') is True
    assert ed.messages[-1] == 'showjump 2 [current] a @ 2:1 — two'

    assert ed.exec_command_line('showjump nope') is False
    assert ed.messages[-1] == 'showjump: no such jump: nope'
