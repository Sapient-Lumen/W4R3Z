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
    assert '#2' in ed.prompt.suggestions
    ed.prompt.suggest_index = ed.prompt.suggestions.index('#2')
    assert ed.submit_prompt() is True

    assert _primary_cursor(ed) == (1, 1)
    eb = ed.cur()
    assert int(eb.jump_index) == 1
    target = str(eb.buf.path or eb.name)
    assert ed.status_model()["last_message"] == f"jumppick #2 [back 1] -> {target} @ 2:1"



def test_jumppick_exact_slot_miss_is_typed() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.new_buffer('a', 'one\ntwo\nthree\n')

    _set_primary_cursor(ed, line=0, col=0)
    assert ed.push_jump() is True
    _set_primary_cursor(ed, line=1, col=1)
    assert ed.push_jump() is True

    assert ed.exec_command_line('jumppick #9') is True
    assert ed.prompt is not None
    assert ed.prompt.kind == 'jump'
    assert ed.submit_prompt() is False
    assert ed.messages[-1] == 'jumppick: no such jump: #9'

    assert ed.exec_command_line('jumppick 0') is True
    assert ed.prompt is not None
    assert ed.prompt.kind == 'jump'
    assert ed.submit_prompt() is False
    assert ed.messages[-1] == 'jumppick: no such jump: 0'


def test_jumppick_accepts_visible_hash_slot_query() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.new_buffer('a', 'one\ntwo\nthree\nfour\n')

    _set_primary_cursor(ed, line=0, col=0)
    assert ed.push_jump() is True
    _set_primary_cursor(ed, line=1, col=1)
    assert ed.push_jump() is True
    _set_primary_cursor(ed, line=2, col=2)
    assert ed.push_jump() is True

    assert ed.exec_command_line('jumppick #1') is True
    assert ed.prompt is not None
    assert ed.prompt.kind == 'jump'
    assert ed.prompt.text == '#1'
    assert ed.prompt.suggestions == ['#1']

    assert ed.submit_prompt() is True
    assert _primary_cursor(ed) == (0, 0)
    eb = ed.cur()
    assert int(eb.jump_index) == 0
    target = str(eb.buf.path or eb.name)
    assert ed.status_model()["last_message"] == f"jumppick #1 [back 2] -> {target} @ 1:0"


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

    assert [row[0] for row in ed.jump_prompt_rows()] == ['#2', '#1', '#3']
    assert [sec[0] for sec in ed.jump_section_rows('')] == ['Current', 'Back', 'Forward']

    ed.exec_command_line('jumppick')
    assert ed.prompt is not None
    assert ed.prompt.kind == 'jump'
    assert [row[0] for row in ed.prompt.suggestion_rows] == ['#2', '#1', '#3']

    labels = [
        ed.prompt_row_section_label([str(x) for x in row[:4]], prompt_kind='jump')
        for row in ed.prompt.suggestion_rows
    ]
    assert labels == ['Current', 'Back', 'Forward']
    assert ed.prompt_current_section() == 'Current'
    assert ed.prompt_current_preview().startswith('Current: #2')



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


def test_showjump_root_reports_runtime_summary_then_usage() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.new_buffer('a', 'one\ntwo\nthree\nfour\nfive\n')
    ed._normalize_cursor_lists(ed.cur())
    ed.cur().cursors[ed.cur().primary].line = 0
    ed.cur().cursors[ed.cur().primary].col = 0
    assert ed.push_jump() is True
    ed.cur().cursors[ed.cur().primary].line = 1
    ed.cur().cursors[ed.cur().primary].col = 1
    assert ed.push_jump() is True
    ed.cur().cursors[ed.cur().primary].line = 4
    ed.cur().cursors[ed.cur().primary].col = 0
    assert ed.push_jump() is True
    assert ed.jump_to_index(1) is True

    assert ed.exec_command_line('showjump') is False
    assert ed.messages == [
        'showjump: 3 jumps · #2 [current] a @ 2:1 — two',
        'usage: showjump INDEX|#N',
    ]


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

    ed.vm.stack.clear()
    ed.vm.eval('"#1" "ed.jump-detail-row" hostcall')
    hash_row = ed.vm.stack.pop()
    assert hash_row == ['#1', 1, 'back', 1, 'a', '1:0', 'one']

    assert ed.exec_command_line('showjump 1') is True
    assert ed.messages[-1] == 'showjump 1 [back 1] a @ 1:0 — one'

    assert ed.exec_command_line('showjump #1') is True
    assert ed.messages[-1] == 'showjump #1 [back 1] a @ 1:0 — one'

    assert ed.exec_command_line('showjump 2') is True
    assert ed.messages[-1] == 'showjump 2 [current] a @ 2:1 — two'

    assert ed.exec_command_line('showjump nope') is False
    assert ed.messages[-1] == 'showjump: no such jump: nope'


def test_jump_section_summary_rows_hostcall_and_showjumpgroups_surface() -> None:
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

    rows = ed.jump_section_summary_rows('two')
    assert rows == [['Current', 1, '#2', 'a @ 2:1 — two']]

    ed.vm.stack.clear()
    ed.vm.eval('"" "ed.jump-section-summary-rows" hostcall')
    host_rows = ed.vm.stack.pop()
    assert host_rows == [
        ['Current', 1, '#2', 'a @ 2:1 — two'],
        ['Back', 1, '#1', 'a @ 1:0 — one'],
        ['Forward', 1, '#3', 'a @ 3:2 — three'],
    ]

    ed.messages.clear()
    assert ed.exec_command_line('showjumpgroups two') is True
    assert ed.messages == [
        'showjumpgroups two: 1 section(s), 1 jump(s)',
        'Current: 1 (e.g. #2 — a @ 2:1 — two)',
    ]

    ed.messages.clear()
    assert ed.exec_command_line('showjumpgroups zzz-no-such-jump') is True
    assert ed.messages == ['showjumpgroups zzz-no-such-jump: 0 section(s), 0 jump(s)']
