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


def test_keymode_inventory_rows_hostcall_matches_plain_showkeymodes_surface() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer('*scratch*', '')

    ed.vm.eval('"nav" "x" "command:help" "ed.bind-mode" hostcall', filename='<nav-bind>')
    ed.vm.eval('"goto" "g" "command:showstatus" "ed.bind-mode" hostcall', filename='<goto-bind>')

    assert ed.exec_command_line('pushkeymode nav')
    assert ed.exec_command_line('pushkeymode-once goto')

    rows = _hostcall(ed, 'ed.keymode-inventory-rows')[-1]
    assert rows == [
        ['active', 'goto', 1],
        ['active', 'nav', 0],
        ['known', 'global', 0],
        ['known', 'goto', 1],
        ['known', 'nav', 0],
    ]

    ed.messages.clear()
    assert ed.exec_command_line('showkeymodes') is True
    assert ed.messages == [
        'active keymodes: goto!, nav',
        'known keymodes: global, goto, nav',
    ]


def test_keymode_inventory_rows_keep_active_internal_modes_out_of_known_list() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer('*scratch*', '')

    rows = _hostcall(ed, 'ed.keymode-inventory-rows')[-1]
    assert rows == [
        ['active', 'global', 0],
        ['known', 'global', 0],
    ]

    ed.push_key_mode('prompt', once=True, capture=True)
    rows = _hostcall(ed, 'ed.keymode-inventory-rows')[-1]
    assert rows[0] == ['active', 'prompt', 1]
    assert ['known', 'prompt', 1] not in rows

    ed.messages.clear()
    assert ed.exec_command_line('showkeymodes') is True
    assert ed.messages == [
        'active keymodes: prompt!',
        'known keymodes: global',
    ]


def test_showkeymode_root_runtime_reports_inventory_then_usage() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer('*scratch*', '')

    ed.vm.eval('"nav" "x" "command:help" "ed.bind-mode" hostcall', filename='<nav-bind>')
    ed.vm.eval('"goto" "g" "command:showstatus" "ed.bind-mode" hostcall', filename='<goto-bind>')
    assert ed.exec_command_line('pushkeymode nav')
    assert ed.exec_command_line('pushkeymode-once goto')

    ed.messages.clear()
    assert ed.exec_command_line('showkeymode') is False
    assert ed.messages == [
        'showkeymode: active goto!, nav · known=3 · goto g->command:showstatus',
        'usage: showkeymode MODE',
    ]


def test_keymode_detail_row_and_showkeymode_surface_exact_mode_state() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer('*scratch*', '')

    ed.vm.eval('"nav" "x" "command:help" "ed.bind-mode" hostcall', filename='<nav-bind>')
    ed.vm.eval('"goto" "g" "command:showstatus" "ed.bind-mode" hostcall', filename='<goto-bind>')

    assert ed.exec_command_line('pushkeymode nav')
    assert ed.exec_command_line('pushkeymode-once goto')

    row = _hostcall(ed, 'ed.keymode-detail-row', 'goto')[-1]
    assert row == ['goto', 1, 1, 1, 1, 'g', 'command:showstatus', 'show portable statusline summary']

    ed.messages.clear()
    assert ed.exec_command_line('showkeymode goto') is True
    assert ed.messages == [
        'keymode goto [active once known] bindings=1 sample=g->command:showstatus (show portable statusline summary)'
    ]

    row = _hostcall(ed, 'ed.keymode-detail-row', 'global')[-1]
    assert row[:5] == ['global', 0, 1, 0, 0]


def test_keymode_detail_row_surfaces_active_internal_modes_but_hides_unknown_inactive_modes() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer('*scratch*', '')

    ed.push_key_mode('prompt', once=True, capture=True)
    row = _hostcall(ed, 'ed.keymode-detail-row', 'prompt')[-1]
    assert row[:4] == ['prompt', 1, 0, 1]
    assert int(row[4]) >= 1
    assert row[5] not in (0, '')
    assert row[6] not in (0, '')

    ed.messages.clear()
    assert ed.exec_command_line('showkeymode prompt') is True
    assert ed.messages[-1].startswith('keymode prompt [active once internal] bindings=')

    assert _hostcall(ed, 'ed.keymode-detail-row', 'no-such-mode')[-1] == 0
    ed.messages.clear()
    assert ed.exec_command_line('showkeymode no-such-mode') is False
    assert ed.messages == ['showkeymode: no such keymode: no-such-mode']
