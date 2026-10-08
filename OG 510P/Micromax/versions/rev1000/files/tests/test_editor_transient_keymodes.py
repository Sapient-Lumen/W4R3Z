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

    # ed.press-key is a script-origin synthetic replay surface now; this
    # low-level transient-keymode smoke test explicitly opts into replaying the
    # trusted test binding while preserving script authority.
    assert ed.exec_command_line('set cap.keybinding-press true') is True
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


def test_script_activated_once_keymode_runs_trusted_binding_with_script_authority() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer('*scratch*', '')

    # Trusted/user code owns this binding.  Without keymode-origin provenance, a
    # lower-authority script could activate the mode and a later physical key
    # press would run this trusted binding outside script policy.
    ed.bind_key_checked('F40', 'command:set cap.fs-save true', mode='danger')
    assert ed.options.get('cap.fs-save') is False

    with ed.script_context():
        _hostcall(ed, 'ed.keymode-push-once', 'danger')
    km = ed.key_mode_stack[-1]
    assert km.name == 'danger'
    assert bool(getattr(km, 'script_context', False)) is True
    origin = str(getattr(km, 'script_origin_id', '') or '')
    assert origin

    assert ed.dispatch_key('F40') is False

    assert ed.options.get('cap.fs-save') is False
    assert ed.current_key_mode() is None
    assert any('script context cannot modify capability option: cap.fs-save' in m for m in ed.messages)


def test_script_activated_persistent_keymode_runs_trusted_binding_with_script_authority() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer('*scratch*', '')

    ed.bind_key_checked('F41', 'command:set cap.fs-open true', mode='danger')
    assert ed.options.get('cap.fs-open') is False

    with ed.script_context():
        _hostcall(ed, 'ed.keymode-push', 'danger')
    assert ed.current_key_mode() == 'danger'

    assert ed.dispatch_key('F41') is False

    assert ed.options.get('cap.fs-open') is False
    # Persistent modes remain active; only their authority was lowered.
    assert ed.current_key_mode() == 'danger'
    assert any('script context cannot modify capability option: cap.fs-open' in m for m in ed.messages)


def test_script_cannot_pop_or_clear_trusted_active_keymode() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer('*scratch*', '')
    ed.push_key_mode('trusted')
    assert ed.current_key_mode() == 'trusted'

    with ed.script_context():
        try:
            _hostcall(ed, 'ed.keymode-pop')
        except Exception as e:
            assert 'script context cannot pop active keymode: trusted' in str(e)
        else:  # pragma: no cover - failure witness
            raise AssertionError('script unexpectedly popped trusted keymode')
    assert ed.current_key_mode() == 'trusted'

    with ed.script_context():
        try:
            _hostcall(ed, 'ed.keymode!', 0)
        except Exception as e:
            assert 'script context cannot replace active keymode: trusted' in str(e)
        else:  # pragma: no cover - failure witness
            raise AssertionError('script unexpectedly cleared trusted keymode')
    assert ed.current_key_mode() == 'trusted'


def test_script_cannot_shadow_trusted_capture_keymode() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer('*scratch*', '')
    ed.push_key_mode('trusted-capture', capture=True)
    assert ed.current_capture_key_mode() == 'trusted-capture'

    with ed.script_context():
        try:
            _hostcall(ed, 'ed.keymode-push', 'danger')
        except Exception as e:
            assert 'script context cannot shadow active keymode: trusted-capture' in str(e)
        else:  # pragma: no cover - failure witness
            raise AssertionError('script unexpectedly shadowed trusted capture mode')

    assert ed.current_capture_key_mode() == 'trusted-capture'
    assert ed.current_key_mode() == 'trusted-capture'
