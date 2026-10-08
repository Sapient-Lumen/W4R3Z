from pathlib import Path

from micromax_editor.editor import Editor
from micromax_editor.micromax_bridge import install_editor_hostcalls
from micromax_editor.plugins import PluginManager


def _hostcall(ed: Editor, name: str, *args: object) -> list[object]:
    vm = ed.vm
    for a in args:
        vm.stack.append(a)
    vm.stack.append(name)
    vm.eval('hostcall')
    return list(vm.stack)


def test_mode_bindings_resolve_with_global_fallback_and_status() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer('*scratch*', '')

    assert ed.exec_command_line('bind Ctrl-x command:help')
    ed.vm.eval('"nav" "Ctrl-x" "command:quit" "ed.bind-mode" hostcall', filename='<mode-bind>')

    ed.messages.clear()
    assert ed.exec_command_line('showkey Ctrl-x')
    assert 'Ctrl-x -> command:help' in ed.messages[-1]
    assert '[desc show help for commands/actions]' in ed.messages[-1]

    ed.vm.stack.clear()
    _hostcall(ed, 'ed.keymode!', 'nav')
    ed.vm.stack.clear()
    _hostcall(ed, 'ed.status')
    st = ed.vm.pop_map()
    assert st['keymode'] == 'nav'

    ed.messages.clear()
    assert ed.exec_command_line('showkey Ctrl-x')
    msg = ed.messages[-1]
    assert 'Ctrl-x -> command:quit' in msg
    assert '[mode nav]' in msg
    assert '<mode-bind>:' in msg

    ed.vm.stack.clear()
    _hostcall(ed, 'ed.binding-modes')
    rows = ed.vm.pop_list()
    nav_row = next(r for r in rows if r[0] == 'nav' and r[1] == 'Ctrl-x')
    assert nav_row[2] == 'command:quit'
    assert nav_row[4][0] == '<mode-bind>'


def test_keymode_stack_prefers_topmost_mode() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.vm.eval('"a" "Ctrl-g" "command:help" "ed.bind-mode" hostcall', filename='<mode-a>')
    ed.vm.eval('"b" "Ctrl-g" "command:quit" "ed.bind-mode" hostcall', filename='<mode-b>')

    ed.vm.stack.clear()
    _hostcall(ed, 'ed.keymode-push', 'a')
    _hostcall(ed, 'ed.keymode-push', 'b')
    ed.vm.stack.clear()
    _hostcall(ed, 'ed.keymodes')
    known = ed.vm.pop_list()
    active = ed.vm.pop_list()

    assert active == ['b', 'a']
    assert 'a' in known and 'b' in known

    ed.messages.clear()
    assert ed.exec_command_line('showkey Ctrl-g')
    assert 'command:quit' in ed.messages[-1]
    assert '[mode b]' in ed.messages[-1]

    ed.vm.stack.clear()
    _hostcall(ed, 'ed.keymode-pop')
    popped = ed.vm.pop()
    assert popped == 'b'

    ed.messages.clear()
    assert ed.exec_command_line('showkey Ctrl-g')
    assert 'command:help' in ed.messages[-1]
    assert '[mode a]' in ed.messages[-1]


def test_plugin_reload_cleans_mode_specific_bindings(tmp_path: Path) -> None:
    root = tmp_path / 'plugins'
    p = root / 'p1'
    p.mkdir(parents=True)
    init = p / 'init.mx'

    init.write_text(
        '\n'.join(
            [
                ': init',
                '  "nav" "Ctrl-h" "command:help" "ed.bind-mode" hostcall',
                ';',
            ]
        ),
        encoding='utf-8',
    )

    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer('*scratch*', '')
    pm = PluginManager(ed.vm)
    pm.load_tree(root)

    ed.set_key_mode('nav')
    b = ed.resolve_key_binding('Ctrl-h')
    assert b is not None
    assert b.mode == 'nav'
    assert b.group == 'plugin:p1'

    init.write_text(
        '\n'.join(
            [
                ': init',
                '  "nav" "Ctrl-b" "command:quit" "ed.bind-mode" hostcall',
                ';',
            ]
        ),
        encoding='utf-8',
    )

    pm.reload('p1')

    assert ed.resolve_key_binding('Ctrl-h') is None
    b2 = ed.resolve_key_binding('Ctrl-b')
    assert b2 is not None
    assert b2.mode == 'nav'
    assert b2.group == 'plugin:p1'

    pm.unload('p1')
    assert ed.resolve_key_binding('Ctrl-b') is None


def test_showkeymodes_rejects_unexpected_arguments() -> None:
    ed = Editor()
    assert ed.exec_command_line('showkeymodes extra') is False
    assert ed.messages[-1] == 'usage: showkeymodes'
