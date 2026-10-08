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


def test_binding_info_and_whichkey_use_derived_descriptions() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.vm.eval('"Ctrl-z" "command:help" "ed.bind" hostcall', filename='<global-bind>')
    ed.vm.eval('"nav" "Ctrl-x" "command:quit" "ed.bind-mode" hostcall', filename='<nav-bind>')
    _hostcall(ed, 'ed.keymode-push', 'nav')

    rows = _hostcall(ed, 'ed.available-binding-info')[-1]
    assert [r[:5] for r in rows] == [
        ['nav', 'Ctrl-x', 'command:quit', 'request editor quit', 0],
        ['global', 'Ctrl-z', 'command:help', 'show help for commands/actions', 0],
    ]
    assert rows[0][5][0] == '<nav-bind>'
    assert rows[1][5][0] == '<global-bind>'

    resolved = _hostcall(ed, 'ed.resolve-key-info', 'Ctrl-x')[-1]
    assert resolved[:5] == ['nav', 'Ctrl-x', 'command:quit', 'request editor quit', 0]

    ed.messages.clear()
    assert ed.exec_command_line('whichkey')
    assert ed.messages[-1] == (
        'whichkey: 2 binding(s), '
        'Ctrl-x@nav->request editor quit, '
        'Ctrl-z@global->show help for commands/actions'
    )


def test_binddoc_and_bindmodedoc_override_default_descriptions() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.vm.eval('"Ctrl-h" "command:help" "ed.bind" hostcall', filename='<global-bind>')
    ed.vm.eval('"nav" "Ctrl-g" "command:showkeymodes" "ed.bind-mode" hostcall', filename='<mode-bind>')

    ed.messages.clear()
    assert ed.exec_command_line('binddoc Ctrl-h help topics')
    assert ed.messages[-1] == 'binddoc: Ctrl-h -> help topics'

    ed.messages.clear()
    assert ed.exec_command_line('bindmodedoc nav Ctrl-g enter goto map')
    assert ed.messages[-1] == 'bindmodedoc: Ctrl-g@nav -> enter goto map'

    info_global = _hostcall(ed, 'ed.binding-info-for', 0)[-1]
    info_nav = _hostcall(ed, 'ed.binding-info-for', 'nav')[-1]
    g = next(r for r in info_global if r[0] == 'Ctrl-h')
    n = next(r for r in info_nav if r[0] == 'Ctrl-g')
    assert g[:4] == ['Ctrl-h', 'command:help', 'help topics', 0]
    assert n[:4] == ['Ctrl-g', 'command:showkeymodes', 'enter goto map', 0]

    ed.messages.clear()
    assert ed.exec_command_line('showkey Ctrl-h')
    assert '[desc help topics]' in ed.messages[-1]

    _hostcall(ed, 'ed.keymode-push', 'nav')
    ed.messages.clear()
    assert ed.exec_command_line('whichkey')
    assert ed.messages[-1] == (
        'whichkey: 2 binding(s), '
        'Ctrl-g@nav->enter goto map, '
        'Ctrl-h@global->help topics'
    )


def test_binding_doc_commands_fail_plainly_on_missing_bindings() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.messages.clear()
    assert not ed.exec_command_line('binddoc Ctrl-h help topics')
    assert ed.messages[-1] == 'binddoc: no such binding: Ctrl-h'

    ed.messages.clear()
    assert not ed.exec_command_line('bindmodedoc nav Ctrl-g enter goto map')
    assert ed.messages[-1] == 'bindmodedoc: no such binding: Ctrl-g@nav'


def test_unbind_commands_fail_plainly_on_missing_bindings() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.messages.clear()
    assert not ed.exec_command_line('unbind Ctrl-h')
    assert ed.messages[-1] == 'unbind: no such binding: Ctrl-h'

    ed.messages.clear()
    assert not ed.exec_command_line('unbindmode nav Ctrl-g')
    assert ed.messages[-1] == 'unbindmode: no such binding: Ctrl-g@nav'




def test_bind_commands_report_typed_success_feedback() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.messages.clear()
    assert ed.exec_command_line('bind Ctrl-h command:help')
    assert ed.messages[-1] == 'bind: Ctrl-h -> command:help'

    ed.messages.clear()
    assert ed.exec_command_line('bindmode nav Ctrl-g command:showkeymodes')
    assert ed.messages[-1] == 'bindmode: Ctrl-g@nav -> command:showkeymodes'

def test_unbind_commands_report_typed_success_feedback() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    assert ed.exec_command_line('bind Ctrl-h command:help')
    ed.messages.clear()
    assert ed.exec_command_line('unbind Ctrl-h')
    assert ed.messages[-1] == 'unbind: Ctrl-h'

    ed.exec_command_line('bindmode nav Ctrl-g command:showkeymodes')
    ed.messages.clear()
    assert ed.exec_command_line('unbindmode nav Ctrl-g')
    assert ed.messages[-1] == 'unbindmode: Ctrl-g@nav'
