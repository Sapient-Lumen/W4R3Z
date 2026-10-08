from micromax_editor.buffer import Cursor
from micromax_editor.editor import Editor
from micromax_editor.micromax_bridge import install_editor_hostcalls


def _hostcall(ed: Editor, name: str, *args: object) -> list[object]:
    vm = ed.vm
    for a in args:
        vm.stack.append(a)
    vm.stack.append(name)
    vm.eval('hostcall')
    return list(vm.stack)


def test_status_model_hostcall_reports_portable_editor_state() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer('notes.txt', 'alpha\nbeta', path='/tmp/notes.txt')

    eb = ed.cur()
    eb.buf.dirty = True
    eb.cursors[0] = Cursor(1, 2)
    eb.sel_anchors[0] = Cursor(1, 0)
    ed.message('saved ok')
    ed.enter_prompt('command', prefill='open a')
    ed.macro_recording = True
    ed._macro_target = 'demo'

    ed.vm.stack.clear()
    _hostcall(ed, 'ed.status')
    st = ed.vm.pop_map()

    assert st['mode'] == 'command'
    assert st['buffer_name'] == 'notes.txt'
    assert st['file_name'] == 'notes.txt'
    assert st['path'] == '/tmp/notes.txt'
    assert st['dirty'] == 1
    assert st['readonly'] == 0
    assert st['line'] == 1
    assert st['col'] == 2
    assert st['display_line'] == 2
    assert st['display_col'] == 3
    assert st['position'] == '2:3'
    assert st['line_count'] == 2
    assert st['cursor_count'] == 1
    assert st['primary_cursor_index'] == 0
    assert st['selection_count'] == 1
    assert st['primary_selection_chars'] == 2
    assert st['prompt_kind'] == 'command'
    assert st['prompt_text'] == 'open a'
    assert st['last_message'] == 'saved ok'
    assert st['macro_recording'] == 1
    assert st['macro_name'] == 'demo'



def test_showstatus_and_status_summary_hostcall_are_deterministic() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer('*scratch*', 'abc')

    eb = ed.cur()
    eb.buf.dirty = True
    eb.cursors.append(Cursor(0, 1))
    eb.sel_anchors.append(None)
    eb.cursor_ids.append(ed._alloc_cursor_id())
    ed._normalize_cursor_lists(eb)
    ed.message('hello world')

    assert ed.exec_command_line('showstatus')
    msg = ed.messages[-1]
    assert "mode=normal" in msg
    assert "buffer='*scratch*'" in msg
    assert 'dirty=1' in msg
    assert 'pos=1:1' in msg
    assert 'cursors=1/2' in msg
    assert 'sels=0' in msg

    ed.vm.stack.clear()
    _hostcall(ed, 'ed.status-summary')
    assert ed.vm.pop_str() == msg


def test_command_palette_status_model_exposes_current_preview() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer('*scratch*', 'alpha')

    ed.enter_command_palette('status')

    ed.vm.stack.clear()
    _hostcall(ed, 'ed.status')
    st = ed.vm.pop_map()

    assert st['mode'] == 'palette'
    assert st['prompt_kind'] == 'palette'
    assert st['prompt_text'] == 'status'
    assert st['prompt_current_insert'] == 'showstatus'
    assert st['prompt_current_kind'] == 'command'
    assert st['prompt_current_section'] == 'Command'
    assert 'portable statusline summary' in st['prompt_current_preview']

    ed.vm.stack.clear()
    _hostcall(ed, 'ed.status-summary')
    summary = ed.vm.pop_str()
    assert "prompt='palette'" in summary
    assert 'prompt_item=' in summary


def test_command_palette_status_model_uses_recent_section_for_recent_item() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer('*scratch*', 'alpha')

    assert ed.exec_command_line('commandpick status')
    assert ed.submit_prompt() is True
    assert ed.prompt is not None
    assert ed.prompt.kind == 'command'
    ed.cancel_prompt()

    ed.enter_command_palette('')

    ed.vm.stack.clear()
    _hostcall(ed, 'ed.status')
    st = ed.vm.pop_map()

    assert st['mode'] == 'palette'
    assert st['prompt_current_insert'] == 'showstatus'
    assert st['prompt_current_section'] == 'Recent'
    assert 'Recent: showstatus' in st['prompt_current_preview']


def test_topic_prompt_status_model_exposes_current_preview() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer('*scratch*', 'alpha')

    ed.enter_topic_prompt('visible micromax')

    ed.vm.stack.clear()
    _hostcall(ed, 'ed.status')
    st = ed.vm.pop_map()

    assert st['mode'] == 'topic'
    assert st['prompt_kind'] == 'topic'
    assert st['prompt_text'] == 'visible micromax'
    assert st['prompt_current_insert'] == 'showword'
    assert st['prompt_current_kind'] == 'command'
    assert st['prompt_current_section'] == 'Command'
    assert 'show visible micromax word' in st['prompt_current_preview']

    ed.vm.stack.clear()
    _hostcall(ed, 'ed.status-summary')
    summary = ed.vm.pop_str()
    assert "prompt='topic'" in summary
    assert 'prompt_item=' in summary


def test_binding_prompt_status_model_exposes_current_preview() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer('*scratch*', 'alpha')

    ed.vm.eval('"Ctrl-z" "command:help" "ed.bind" hostcall', filename='<global-bind>')
    ed.vm.eval('"nav" "Ctrl-x" "command:quit" "ed.bind-mode" hostcall', filename='<nav-bind>')
    _hostcall(ed, 'ed.keymode-push', 'nav')
    ed.enter_binding_prompt('quit')

    ed.vm.stack.clear()
    _hostcall(ed, 'ed.status')
    st = ed.vm.pop_map()

    assert st['mode'] == 'binding'
    assert st['prompt_kind'] == 'binding'
    assert st['prompt_text'] == 'quit'
    assert st['prompt_current_insert'] == 'Ctrl-x'
    assert st['prompt_current_kind'] == 'binding'
    assert st['prompt_current_section'] == 'Binding'
    assert '@nav command:quit' in st['prompt_current_menu']
    assert 'request editor quit' in st['prompt_current_preview']

    ed.vm.stack.clear()
    _hostcall(ed, 'ed.status-summary')
    summary = ed.vm.pop_str()
    assert "prompt='binding'" in summary
    assert 'prompt_item=' in summary
