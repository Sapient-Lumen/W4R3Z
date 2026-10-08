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


def test_editor_registration_groups_and_detail_rows() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.vm.eval(': hi-cmd ( args -- ok ) drop 1 ;', filename='<group-test>')

    ed.vm.stack.clear()
    _hostcall(ed, 'ed.group!', 'cfg')
    ed.vm.stack.clear()
    _hostcall(ed, 'ed.group@')
    current = ed.vm.pop()

    ed.vm.eval('\' hi-cmd "hi" "say hi" "ed.cmd-add" hostcall', filename='<group-test>')
    ed.vm.stack.clear()
    ed.vm.eval('"Ctrl-h" "command:hi" "ed.bind" hostcall', filename='<group-test>')

    ed.vm.stack.clear()
    _hostcall(ed, 'ed.cmd-rows')
    cmd_rows = ed.vm.pop_list()
    ed.vm.stack.clear()
    _hostcall(ed, 'ed.binding-detail')
    binding_rows = ed.vm.pop_list()

    ed.vm.stack.clear()
    _hostcall(ed, 'ed.group!', 0)
    ed.vm.stack.clear()
    _hostcall(ed, 'ed.group@')
    cleared = ed.vm.pop()

    assert current == 'cfg'
    assert cleared == 0

    crow = next(r for r in cmd_rows if r[0] == 'hi')
    assert crow[1] == 'say hi'
    assert crow[2] == 'cfg'
    assert crow[3][0] == '<group-test>'

    brow = next(r for r in binding_rows if r[0] == 'Ctrl-h')
    assert brow[1] == 'command:hi'
    assert brow[2] == 'cfg'
    assert brow[3][0] == '<group-test>'

    ed.messages.clear()
    assert ed.exec_command_line('showcmd hi')
    assert '[group cfg]' in ed.messages[-1]
    assert '<group-test>:' in ed.messages[-1]

    ed.messages.clear()
    assert ed.exec_command_line('showkey Ctrl-h')
    assert '[group cfg]' in ed.messages[-1]
    assert '<group-test>:' in ed.messages[-1]


def test_plugin_reload_cleans_grouped_editor_registrations(tmp_path: Path) -> None:
    root = tmp_path / 'plugins'
    p = root / 'p1'
    p.mkdir(parents=True)
    init = p / 'init.mx'

    init.write_text(
        '\n'.join(
            [
                ': hi-cmd ( args -- ok ) drop 1 ;',
                ': init',
                "  ' hi-cmd \"hi\" \"say hi\" \"ed.cmd-add\" hostcall",
                '  "Ctrl-h" "command:hi" "ed.bind" hostcall',
                ';',
            ]
        ),
        encoding='utf-8',
    )

    ed = Editor()
    install_editor_hostcalls(ed)
    pm = PluginManager(ed.vm)
    pm.load_tree(root)

    assert ed.command_dispatcher.get('hi') is not None
    assert ed.command_dispatcher.get('hi').group == 'plugin:p1'
    assert ed.keymap.get_binding('Ctrl-h') is not None
    assert ed.keymap.get_binding('Ctrl-h').group == 'plugin:p1'

    init.write_text(
        '\n'.join(
            [
                ': bye-cmd ( args -- ok ) drop 1 ;',
                ': init',
                "  ' bye-cmd \"bye\" \"say bye\" \"ed.cmd-add\" hostcall",
                '  "Ctrl-b" "command:bye" "ed.bind" hostcall',
                ';',
            ]
        ),
        encoding='utf-8',
    )

    pm.reload('p1')

    assert ed.command_dispatcher.get('hi') is None
    assert ed.keymap.get_binding('Ctrl-h') is None
    assert ed.command_dispatcher.get('bye') is not None
    assert ed.command_dispatcher.get('bye').group == 'plugin:p1'
    assert ed.keymap.get_binding('Ctrl-b') is not None
    assert ed.keymap.get_binding('Ctrl-b').group == 'plugin:p1'

    pm.unload('p1')
    assert ed.command_dispatcher.get('bye') is None
    assert ed.keymap.get_binding('Ctrl-b') is None
