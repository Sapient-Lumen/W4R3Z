from micromax_editor.editor import Editor
from micromax_editor.micromax_bridge import install_editor_hostcalls


def _hostcall(ed: Editor, name: str, *args: object) -> list[object]:
    vm = ed.vm
    for a in args:
        vm.stack.append(a)
    vm.stack.append(name)
    vm.eval('hostcall')
    return list(vm.stack)


def test_mx_bind_showkey_bindings_and_unbind() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.vm.eval('"Ctrl-h" "command:help" "ed.bind" hostcall', filename='<bind-test>')

    assert ed.exec_command_line('showkey Ctrl-h')
    assert ed.messages
    msg = ed.messages[-1]
    assert 'Ctrl-h -> command:help' in msg
    assert '<bind-test>:' in msg

    ed.vm.stack.clear()
    _hostcall(ed, 'ed.bindings')
    rows = ed.vm.pop_list()
    row = next(r for r in rows if r[0] == 'Ctrl-h')
    assert row[1] == 'command:help'
    assert row[2][0] == '<bind-test>'

    ed.vm.stack.clear()
    _hostcall(ed, 'ed.unbind', 'Ctrl-h')
    assert ed.vm.pop_int() == 1

    ed.messages.clear()
    assert not ed.exec_command_line('showkey Ctrl-h')
    assert ed.messages and ed.messages[-1] == 'showkey: no such binding: Ctrl-h'


def test_command_unbind_removes_interactive_binding() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    assert ed.exec_command_line('bind Ctrl-x command:help')
    assert ed.exec_command_line('showkey Ctrl-x')
    assert 'Ctrl-x -> command:help' in ed.messages[-1]
    assert '[desc show help for commands/actions]' in ed.messages[-1]

    assert ed.exec_command_line('unbind Ctrl-x')
    assert ed.messages[-1] == 'unbind: Ctrl-x'
    assert not ed.exec_command_line('showkey Ctrl-x')
    assert ed.messages[-1] == 'showkey: no such binding: Ctrl-x'
