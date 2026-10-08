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


def test_bind_prefix_hostcall_creates_inspectable_prefix_binding() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.vm.eval('"goto" "Ctrl-g" "command:showkeymodes" "ed.bind-mode" hostcall', filename='<goto-bind>')
    out = _hostcall(ed, 'ed.bind-prefix', 'g', 'goto', 'goto menu')
    assert out[-1] == 1

    resolved = _hostcall(ed, 'ed.resolve-key-info', 'g')[-1]
    assert resolved[:4] == ['global', 'g', 'command:prefixmode goto', 'goto menu']

    ed.messages.clear()
    assert ed.dispatch_key('g')
    assert ed.current_key_mode() == 'goto'
    assert ed.current_key_mode_once()
    assert ed.messages[-1].startswith('whichkey: 2 binding(s), Ctrl-g@goto!->show active and known key modes')
    assert 'g@global->goto menu' in ed.messages[-1]

    ed.messages.clear()
    assert ed.dispatch_key('Ctrl-g')
    assert ed.current_key_mode() is None
    assert ed.messages[0] == 'active keymodes: goto!'
    assert ed.messages[1] == 'known keymodes: global, goto'


def test_prefixmode_and_bindprefix_commands() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.vm.eval('"nav" "x" "command:quit" "ed.bind-mode" hostcall', filename='<nav-bind>')

    ed.messages.clear()
    assert ed.exec_command_line('prefixmode nav')
    assert ed.current_key_mode() == 'nav'
    assert ed.current_key_mode_once()
    assert ed.messages[-1] == 'whichkey: 1 binding(s), x@nav!->request editor quit'

    ed.set_key_mode(None)
    ed.messages.clear()
    assert ed.exec_command_line('bindprefix z nav nav menu')
    assert ed.messages[-1] == 'bindprefix: z -> nav'

    ed.messages.clear()
    assert ed.exec_command_line('showkey z')
    assert ed.messages[-1] == 'z -> command:prefixmode nav [desc nav menu]'



def test_bind_mode_prefix_hostcall_creates_mode_local_prefix_binding() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.vm.eval('"goto" "g" "command:showkeymodes" "ed.bind-mode" hostcall', filename='<goto-bind>')
    out = _hostcall(ed, 'ed.bind-mode-prefix', 'nav', 'z', 'goto', 'goto menu')
    assert out[-1] == 1

    resolved_global = _hostcall(ed, 'ed.resolve-key-info', 'z')[-1]
    assert resolved_global == 0

    _hostcall(ed, 'ed.keymode-push', 'nav')
    resolved = _hostcall(ed, 'ed.resolve-key-info', 'z')[-1]
    assert resolved[:4] == ['nav', 'z', 'command:prefixmode goto', 'goto menu']

    ed.messages.clear()
    assert ed.dispatch_key('z')
    assert ed.current_key_mode() == 'goto'
    assert ed.current_key_mode_once()
    assert ed.messages[-1] == 'whichkey: 2 binding(s), g@goto!->show active and known key modes, z@nav->goto menu'

    ed.messages.clear()
    assert ed.dispatch_key('g')
    assert ed.current_key_mode() == 'nav'
    assert not ed.current_key_mode_once()


def test_bindmodeprefix_command_binds_mode_local_prefix_key() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.vm.eval('"tools" "x" "command:showkeymodes" "ed.bind-mode" hostcall', filename='<tools-bind>')

    ed.messages.clear()
    assert ed.exec_command_line('bindmodeprefix nav z tools tools menu')
    assert ed.messages[-1] == 'bindmodeprefix: z@nav -> tools'

    _hostcall(ed, 'ed.keymode-push', 'nav')
    ed.messages.clear()
    assert ed.exec_command_line('showkey z')
    assert ed.messages[-1] == 'z -> command:prefixmode tools [desc tools menu] [mode nav]'

    ed.messages.clear()
    assert ed.dispatch_key('z')
    assert ed.current_key_mode() == 'tools'
    assert ed.current_key_mode_once()
    assert ed.messages[-1] == 'whichkey: 2 binding(s), x@tools!->show active and known key modes, z@nav->tools menu'
