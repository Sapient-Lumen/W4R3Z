from __future__ import annotations

from micromax_editor.buffer import Cursor
from micromax_editor.editor import Editor
from micromax_editor.micromax_bridge import install_editor_hostcalls


def _set_cursor_on_substring(ed: Editor, needle: str) -> None:
    eb = ed.cur()
    for i, line in enumerate(eb.buf.lines):
        s = str(line)
        if needle in s:
            eb.cursors[0] = Cursor(i, s.index(needle))
            eb.primary = 0
            return
    raise AssertionError(f"needle not found: {needle}")


def _hostcall(ed: Editor, name: str, *args: object) -> list[object]:
    vm = ed.vm
    for a in args:
        vm.stack.append(a)
    vm.stack.append(name)
    vm.eval('hostcall')
    return list(vm.stack)


def test_helphistory_command_and_rows_show_current_and_back_targets() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    assert ed.open_help_doc('help-browser') is True

    _set_cursor_on_substring(ed, 'Softwrap')
    c0 = ed.cur().cursors[ed.cur().primary]
    assert ed.exec_command_line('helpfollow') is True

    assert ed.exec_command_line('helphistory') is True
    assert ed.messages[-1] == (
        f"helphistory: 2 help target(s), [here] softwrap @ 1:0; "
        f"[back 1] help-browser @ {c0.line + 1}:{c0.col}"
    )

    rows = ed.help_history_rows()
    assert rows[0][0] == 'current'
    assert rows[0][1] == 0
    assert rows[0][2] == 'softwrap'
    assert rows[0][4] == '1:0'
    assert rows[1] == ['back', 1, 'help-browser', 'Help browser', f'{c0.line + 1}:{c0.col}', 'ready']

    ed.vm.stack.clear()
    _hostcall(ed, 'ed.helphistory-rows')
    assert ed.vm.pop() == rows


def test_helphistory_can_show_session_history_even_outside_docs_buffer() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    assert ed.open_help_doc('help-browser') is True

    _set_cursor_on_substring(ed, 'Softwrap')
    assert ed.exec_command_line('helpfollow') is True
    assert ed.exec_command_line('helpback') is True

    ed.new_buffer('*scratch*', 'hi\n')
    assert ed.current_help_doc_topic() is None

    assert ed.exec_command_line('helphistory') is True
    rows = ed.help_history_rows()
    assert ed.messages[-1] == (
        f"helphistory: 2 help target(s), [dormant] help-browser @ {rows[0][4]}; "
        "[forward 1] softwrap @ 1:0"
    )
    assert rows[0][0] == 'dormant'
    assert rows[0][1] == 0
    assert rows[0][2] == 'help-browser'
    assert rows[0][4] != ''
    assert rows[1] == ['forward', 1, 'softwrap', rows[1][3], '1:0', 'ready']
    assert 'Softwrap' in str(rows[1][3])


def test_helpresume_reopens_dormant_help_target_without_consuming_forward_history() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    assert ed.open_help_doc('help-browser') is True

    _set_cursor_on_substring(ed, 'Softwrap')
    assert ed.exec_command_line('helpfollow') is True
    assert ed.exec_command_line('helpback') is True

    ed.new_buffer('*scratch*', 'hi\n')
    assert ed.current_help_doc_topic() is None

    assert ed.exec_command_line('helpresume') is True
    st = ed.status_model()
    assert ed.messages[-1] == f"helpresume: help-browser @ {st['help_position']}"
    assert st['help_navigation_active'] == 1
    assert st['help_navigation_dormant'] == 0
    assert st['help_forward_available'] == 1
    assert st['help_forward_target'] == 'softwrap'

    ed.vm.stack.clear()
    _hostcall(ed, 'ed.help-forward')
    assert ed.vm.pop() == 1
    assert ed.status_model()['last_message'] == 'helpforward: softwrap @ 1:0'


def test_helpback_from_dormant_target_preserves_exact_forward_history() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    assert ed.open_help_doc('help-browser') is True

    _set_cursor_on_substring(ed, 'Softwrap')
    c0 = ed.cur().cursors[ed.cur().primary]
    assert ed.exec_command_line('helpfollow') is True

    ed.new_buffer('*scratch*', 'hi\n')
    assert ed.current_help_doc_topic() is None

    assert ed.exec_command_line('helpback') is True
    st = ed.status_model()
    assert ed.current_help_doc_topic() == 'help-browser'
    assert ed.messages[-1] == f"helpback: help-browser @ {c0.line + 1}:{c0.col}"
    assert st['help_forward_available'] == 1
    assert st['help_forward_target'] == 'softwrap'
    assert st['help_forward_position'] == '1:0'
    assert st['help_navigation_summary'] == 'help-browser -> softwrap @ 1:0 (+1)'

    assert ed.exec_command_line('helpforward') is True
    assert ed.current_help_doc_topic() == 'softwrap'
    st2 = ed.status_model()
    assert st2['help_back_available'] == 1
    assert st2['help_back_target'] == 'help-browser'
    assert st2['help_back_position'] == f'{c0.line + 1}:{c0.col}'



def test_helpforward_from_dormant_target_preserves_exact_back_history() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    assert ed.open_help_doc('help-browser') is True

    _set_cursor_on_substring(ed, 'Softwrap')
    c0 = ed.cur().cursors[ed.cur().primary]
    assert ed.exec_command_line('helpfollow') is True
    assert ed.exec_command_line('helpback') is True

    ed.new_buffer('*scratch*', 'hi\n')
    assert ed.current_help_doc_topic() is None

    assert ed.exec_command_line('helpforward') is True
    st = ed.status_model()
    assert ed.current_help_doc_topic() == 'softwrap'
    assert ed.messages[-1] == 'helpforward: softwrap @ 1:0'
    assert st['help_back_available'] == 1
    assert st['help_back_target'] == 'help-browser'
    assert st['help_back_position'] == f'{c0.line + 1}:{c0.col}'
    assert st['help_navigation_summary'] == f"softwrap <- help-browser @ {c0.line + 1}:{c0.col} (+1)"


def test_help_docs_open_reuses_dormant_immediate_back_target() -> None:
    ed = Editor()
    assert ed.open_help_doc('help-browser') is True

    _set_cursor_on_substring(ed, 'Softwrap')
    c0 = ed.cur().cursors[ed.cur().primary]
    assert ed.exec_command_line('helpfollow') is True

    ed.new_buffer('*scratch*', 'hi\n')
    assert ed.current_help_doc_topic() is None

    assert ed.exec_command_line('help docs help-browser') is True
    st = ed.status_model()
    assert ed.current_help_doc_topic() == 'help-browser'
    assert ed.messages[-1] == f"help docs: help-browser @ {c0.line + 1}:{c0.col}"
    assert st['help_back_count'] == 0
    assert st['help_forward_available'] == 1
    assert st['help_forward_count'] == 1
    assert st['help_forward_target'] == 'softwrap'
    assert st['help_forward_position'] == '1:0'
    assert st['help_navigation_summary'] == f"help-browser -> softwrap @ 1:0 (+1)"


def test_opening_new_help_doc_from_dormant_target_pushes_exact_back_history() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    assert ed.open_help_doc('help-browser') is True

    _set_cursor_on_substring(ed, 'Softwrap')
    c0 = ed.cur().cursors[ed.cur().primary]
    ed.new_buffer('*scratch*', 'hi\n')

    assert ed.open_help_doc('vision') is True
    st = ed.status_model()
    assert st['help_topic'] == 'vision'
    assert st['help_back_available'] == 1
    assert st['help_back_target'] == 'help-browser'
    assert st['help_back_position'] == f'{c0.line + 1}:{c0.col}'
    assert st['help_navigation_summary'] == f"vision <- help-browser @ {c0.line + 1}:{c0.col} (+1)"

    assert ed.exec_command_line('helpback') is True
    assert ed.current_help_doc_topic() == 'help-browser'
    assert ed.status_model()['help_position'] == f'{c0.line + 1}:{c0.col}'


def test_opening_new_help_doc_from_dormant_target_clears_forward_branch() -> None:
    ed = Editor()
    assert ed.open_help_doc('help-browser') is True

    _set_cursor_on_substring(ed, 'Softwrap')
    c0 = ed.cur().cursors[ed.cur().primary]
    assert ed.exec_command_line('helpfollow') is True
    assert ed.exec_command_line('helpback') is True

    ed.new_buffer('*scratch*', 'hi\n')
    st0 = ed.status_model()
    assert st0['help_navigation_summary'] == 'help-browser (dormant) -> softwrap @ 1:0 (+1)'
    assert st0['help_forward_available'] == 1

    assert ed.open_help_doc('vision') is True
    st1 = ed.status_model()
    assert st1['help_topic'] == 'vision'
    assert st1['help_back_available'] == 1
    assert st1['help_back_target'] == 'help-browser'
    assert st1['help_back_position'] == f'{c0.line + 1}:{c0.col}'
    assert st1['help_forward_available'] == 0
    assert st1['help_forward_count'] == 0
    assert st1['help_navigation_summary'] == f"vision <- help-browser @ {c0.line + 1}:{c0.col} (+1)"




def test_help_docs_open_reuses_immediate_forward_target_without_clearing_deeper_history() -> None:
    ed = Editor()
    assert ed.open_help_doc('help-browser') is True

    _set_cursor_on_substring(ed, 'Open the setext demo doc')
    help_browser_position = f"{ed.cur().cursors[ed.cur().primary].line + 1}:{ed.cur().cursors[ed.cur().primary].col}"
    assert ed.exec_command_line('helpfollow') is True
    assert ed.current_help_doc_topic() == 'setext-headings'

    _set_cursor_on_substring(ed, 'Vision from setext section')
    setext_position = f"{ed.cur().cursors[ed.cur().primary].line + 1}:{ed.cur().cursors[ed.cur().primary].col}"
    assert ed.exec_command_line('helpfollow') is True
    assert ed.current_help_doc_topic() == 'vision'
    vision_position = ed.status_model()['help_position']

    assert ed.exec_command_line('helpback') is True
    assert ed.current_help_doc_topic() == 'setext-headings'
    assert ed.exec_command_line('helpback') is True
    st0 = ed.status_model()
    assert ed.current_help_doc_topic() == 'help-browser'
    assert st0['help_forward_count'] == 2
    assert st0['help_forward_target'] == 'setext-headings'
    assert st0['help_forward_position'] == setext_position

    assert ed.exec_command_line('help docs setext-headings') is True
    st1 = ed.status_model()
    assert ed.current_help_doc_topic() == 'setext-headings'
    assert ed.messages[-1] == f'help docs: setext-headings @ {setext_position}'
    assert st1['help_back_available'] == 1
    assert st1['help_back_target'] == 'help-browser'
    assert st1['help_back_position'] == help_browser_position
    assert st1['help_forward_count'] == 1
    assert st1['help_forward_target'] == 'vision'
    assert st1['help_forward_position'] == vision_position


def test_opening_same_help_doc_from_closed_dormant_target_restores_exact_position() -> None:
    ed = Editor()
    assert ed.open_help_doc('help-browser') is True

    _set_cursor_on_substring(ed, 'Softwrap')
    c0 = ed.cur().cursors[ed.cur().primary]
    assert ed.exec_command_line('helpfollow') is True
    assert ed.exec_command_line('helpback') is True

    ed.new_buffer('*scratch*', 'hi\n')
    assert ed.close_buffer('help:help-browser', force=True) is True
    assert 'help:help-browser' not in ed.buffers

    assert ed.open_help_doc('help-browser') is True
    st = ed.status_model()
    c1 = ed.cur().cursors[ed.cur().primary]
    assert ed.current_help_doc_topic() == 'help-browser'
    assert c1.line == c0.line
    assert c1.col == c0.col
    assert st['help_position'] == f'{c0.line + 1}:{c0.col}'
    assert st['help_forward_available'] == 1
    assert st['help_forward_target'] == 'softwrap'
    assert st['help_navigation_summary'] == f"help-browser -> softwrap @ 1:0 (+1)"

def test_helpresume_reports_active_help_state_without_replaying() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    assert ed.open_help_doc('help-browser') is True

    st0 = ed.status_model()
    assert st0['help_resume_available'] == 0
    assert st0['help_resume_command'] == ''

    assert ed.exec_command_line('helpresume') is False
    assert ed.messages[-1] == 'helpresume: already active: help-browser @ 1:0'
    st1 = ed.status_model()
    assert st1['help_navigation_summary'] == 'help-browser'
    assert st1['help_position'] == '1:0'

    ed.vm.stack.clear()
    _hostcall(ed, 'ed.help-resume')
    assert ed.vm.pop() == 0
    assert ed.status_model()['last_message'] == 'helpresume: already active: help-browser @ 1:0'


def test_helpresume_reports_explicit_empty_state() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    assert ed.exec_command_line('helpresume') is False
    assert ed.messages[-1] == 'helpresume: no session help target'

    ed.vm.stack.clear()
    _hostcall(ed, 'ed.help-resume')
    assert ed.vm.pop() == 0


def test_helpresume_missing_dormant_target_keeps_action_name_visible() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed._help_session_entry = {'topic': 'zzz-no-such-session', 'line': 0, 'col': 0}

    assert ed.exec_command_line('helpresume') is False
    assert ed.messages[-1] == 'helpresume: missing doc: zzz-no-such-session'

    ed.vm.stack.clear()
    _hostcall(ed, 'ed.help-resume')
    assert ed.vm.pop() == 0
    assert ed.messages[-1] == 'helpresume: missing doc: zzz-no-such-session'


def test_helphistory_empty_inventory_is_explicit() -> None:
    ed = Editor()

    assert ed.exec_command_line('helphistory') is True
    assert ed.messages[-1] == 'helphistory: 0 help target(s)'


def test_helphistory_marks_missing_back_target_without_advertising_helpback() -> None:
    ed = Editor()
    assert ed.open_help_doc('help-browser') is True
    ed._help_stack = ['zzz-no-such-doc']

    assert ed.exec_command_line('helphistory') is True
    assert ed.messages[-1] == 'helphistory: 2 help target(s), [here] help-browser @ 1:0; [back 1 missing] zzz-no-such-doc'

    rows = ed.help_history_rows()
    assert rows[1] == ['back', 1, 'zzz-no-such-doc', '', '', 'missing']
    st = ed.status_model()
    assert st['help_back_count'] == 1
    assert st['help_back_available'] == 0
    assert st['help_back_command'] == ''
    assert st['help_back_warning'] == 'helpback: missing doc: zzz-no-such-doc'
    assert st['help_prune_available'] == 1
    assert st['help_prune_count'] == 1
    assert st['help_prune_command'] == 'helpprune'
    assert st['help_navigation_actions'] == ['helpprune']
    assert st['help_navigation_warning_summary'] == 'helpback: missing doc: zzz-no-such-doc'


def test_helpprune_removes_missing_heads_and_restores_actionable_helpback() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    assert ed.open_help_doc('help-browser') is True
    ed._help_stack = [
        {'topic': 'softwrap', 'line': 0, 'col': 0},
        {'topic': 'zzz-no-such-doc', 'line': 0, 'col': 0},
    ]

    st0 = ed.status_model()
    assert st0['help_back_available'] == 0
    assert st0['help_prune_available'] == 1
    assert st0['help_navigation_actions'] == ['helpprune']

    assert ed.exec_command_line('helpprune') is True
    assert ed.messages[-1] == 'helpprune: pruned 1 missing help target(s) (back 1)'

    st1 = ed.status_model()
    assert st1['help_back_available'] == 1
    assert st1['help_back_target'] == 'softwrap'
    assert st1['help_prune_available'] == 0
    assert st1['help_navigation_actions'] == ['helpback']

    ed.vm.stack.clear()
    _hostcall(ed, 'ed.help-back')
    assert ed.vm.pop() == 1
    assert ed.status_model()['last_message'] == 'helpback: softwrap @ 1:0'


def test_helpprune_reports_explicit_empty_state() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    assert ed.exec_command_line('helpprune') is False
    assert ed.messages[-1] == 'helpprune: nothing to prune'

    ed.vm.stack.clear()
    _hostcall(ed, 'ed.help-prune')
    assert ed.vm.pop() == 0
