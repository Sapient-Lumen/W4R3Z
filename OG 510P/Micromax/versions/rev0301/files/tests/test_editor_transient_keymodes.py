from micromax_editor.editor import Editor
from micromax_editor.micromax_bridge import install_editor_hostcalls


def _hostcall(ed: Editor, name: str, *args: object) -> list[object]:
    vm = ed.vm
    vm.stack.clear()
    for a in args:
        vm.stack.append(a)
    vm.stack.append(name)
    vm.eval('hostcall')
    return list(vm.stack)


def test_transient_keymode_consumes_next_bound_key_and_pops() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer('*scratch*', '')

    assert ed.exec_command_line('bind Ctrl-g command:showstatus')
    ed.vm.eval('"goto" "Ctrl-g" "command:showkeymodes" "ed.bind-mode" hostcall', filename='<goto-bind>')

    _hostcall(ed, 'ed.keymode-push-once', 'goto')
    st = _hostcall(ed, 'ed.status')[-1]
    assert st['keymode'] == 'goto'
    assert st['keymode_once'] == 1

    assert _hostcall(ed, 'ed.press-key', 'Ctrl-g')[-1] == 1
    assert ed.current_key_mode() is None

    # Mode-specific binding won, so showkeymodes output appears.
    assert any(m.startswith('active keymodes:') for m in ed.messages)


def test_transient_keymode_falls_through_to_global_on_miss() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer('*scratch*', '')

    assert ed.exec_command_line('bind Ctrl-g command:showstatus')
    ed.vm.eval('"goto" "Ctrl-h" "command:help" "ed.bind-mode" hostcall', filename='<goto-bind>')

    _hostcall(ed, 'ed.keymode-push-once', 'goto')
    assert ed.current_key_mode() == 'goto'
    assert ed.current_key_mode_once() is True

    assert ed.dispatch_key('Ctrl-g') is True
    assert ed.current_key_mode() is None
    assert ed.messages[-1].startswith('mode=normal ')


def test_keymode_rows_report_once_flags_and_command_surface() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer('*scratch*', '')

    assert ed.exec_command_line('pushkeymode nav')
    assert ed.exec_command_line('pushkeymode-once goto')

    rows = _hostcall(ed, 'ed.keymode-rows')
    known = rows.pop()
    active = rows.pop()
    assert active == [['goto', 1], ['nav', 0]]
    assert 'global' in known

    ed.messages.clear()
    assert ed.exec_command_line('showkeymodes')
    assert ed.messages[0] == 'active keymodes: goto!, nav'
