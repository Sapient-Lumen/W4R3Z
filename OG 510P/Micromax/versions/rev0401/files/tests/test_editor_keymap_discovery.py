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


def test_binding_rows_for_mode_and_global() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.vm.eval('"Ctrl-x" "command:help" "ed.bind" hostcall', filename='<global-bind>')
    ed.vm.eval('"nav" "Ctrl-g" "command:goto 1" "ed.bind-mode" hostcall', filename='<nav-bind>')

    global_rows = _hostcall(ed, 'ed.binding-rows-for', 0)[-1]
    nav_rows = _hostcall(ed, 'ed.binding-rows-for', 'nav')[-1]

    grow = next(r for r in global_rows if r[0] == 'Ctrl-x')
    nrow = next(r for r in nav_rows if r[0] == 'Ctrl-g')
    assert grow[1] == 'command:help'
    assert grow[3][0] == '<global-bind>'
    assert grow[3][1] == 1
    assert nrow[1] == 'command:goto 1'
    assert nrow[3][0] == '<nav-bind>'
    assert nrow[3][1] == 1


def test_available_bindings_and_resolve_key_honor_active_modes() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.vm.eval('"Ctrl-x" "command:help" "ed.bind" hostcall', filename='<global-bind>')
    ed.vm.eval('"nav" "Ctrl-x" "command:quit" "ed.bind-mode" hostcall', filename='<nav-bind>')
    ed.vm.eval('"goto" "Ctrl-g" "command:showkeymodes" "ed.bind-mode" hostcall', filename='<goto-bind>')

    _hostcall(ed, 'ed.keymode-push', 'nav')
    _hostcall(ed, 'ed.keymode-push-once', 'goto')

    rows = _hostcall(ed, 'ed.available-bindings')[-1]
    assert [r[:4] for r in rows] == [
        ['goto', 'Ctrl-g', 'command:showkeymodes', 0],
        ['nav', 'Ctrl-x', 'command:quit', 0],
    ]
    assert rows[0][4][0] == '<goto-bind>'
    assert rows[1][4][0] == '<nav-bind>'

    resolved_x = _hostcall(ed, 'ed.resolve-key', 'Ctrl-x')[-1]
    resolved_g = _hostcall(ed, 'ed.resolve-key', 'Ctrl-g')[-1]
    resolved_h = _hostcall(ed, 'ed.resolve-key', 'Ctrl-h')[-1]

    assert resolved_x[:4] == ['nav', 'Ctrl-x', 'command:quit', 0]
    assert resolved_x[4][0] == '<nav-bind>'
    assert resolved_g[:4] == ['goto', 'Ctrl-g', 'command:showkeymodes', 0]
    assert resolved_g[4][0] == '<goto-bind>'
    assert resolved_h == 0


def test_showbindings_and_whichkey_surface() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.vm.eval('"Ctrl-z" "command:help" "ed.bind" hostcall', filename='<global-bind>')
    ed.vm.eval('"nav" "Ctrl-x" "command:quit" "ed.bind-mode" hostcall', filename='<nav-bind>')
    ed.vm.eval('"goto" "Ctrl-g" "command:showkeymodes" "ed.bind-mode" hostcall', filename='<goto-bind>')

    _hostcall(ed, 'ed.keymode-push', 'nav')
    _hostcall(ed, 'ed.keymode-push-once', 'goto')

    ed.messages.clear()
    assert ed.exec_command_line('showbindings')
    assert ed.messages[-1] == (
        'bindings active: 3 binding(s), '
        'Ctrl-g@goto!->command:showkeymodes, '
        'Ctrl-x@nav->command:quit, '
        'Ctrl-z@global->command:help'
    )

    ed.messages.clear()
    assert ed.exec_command_line('whichkey')
    assert ed.messages[-1] == (
        'whichkey: 3 binding(s), '
        'Ctrl-g@goto!->show active and known key modes, '
        'Ctrl-x@nav->request editor quit, '
        'Ctrl-z@global->show help for commands/actions'
    )

    ed.messages.clear()
    assert ed.exec_command_line('showbindings nav')
    assert ed.messages[-1] == 'bindings nav: 1 binding(s), Ctrl-x->command:quit'


def test_showbindings_and_whichkey_empty_are_count_aware() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.messages.clear()
    assert not ed.exec_command_line('showbindings')
    assert ed.messages[-1] == 'bindings active: 0 binding(s)'

    ed.messages.clear()
    assert not ed.exec_command_line('showbindings nav')
    assert ed.messages[-1] == 'bindings nav: 0 binding(s)'

    ed.messages.clear()
    assert not ed.exec_command_line('whichkey')
    assert ed.messages[-1] == 'whichkey: 0 binding(s)'
