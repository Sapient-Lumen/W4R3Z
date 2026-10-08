from __future__ import annotations

from micromax_editor.editor import Editor
from micromax_editor.micromax_bridge import install_editor_hostcalls


def test_micromax_set_show_toggle_words_refresh_caps() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer('*scratch*', '')

    # set parses tokens like an immediate word and returns the set value.
    ed.vm.eval('set cap.shell true', filename='<test>')
    assert int(ed.vm.stack.pop()) == 1

    # capability advertisement should refresh for cap.* changes.
    ed.vm.eval('"ed.shell" host.feature?', filename='<test>')
    assert int(ed.vm.stack.pop()) == 1

    # show reads the current value.
    ed.vm.eval('show cap.shell', filename='<test>')
    assert int(ed.vm.stack.pop()) == 1

    # toggle flips (bool only) and returns the new value.
    ed.vm.eval('toggle cap.shell', filename='<test>')
    assert int(ed.vm.stack.pop()) == 0
    ed.vm.eval('"ed.shell" host.feature?', filename='<test>')
    assert int(ed.vm.stack.pop()) == 0


def test_opt_bang_refreshes_caps_for_cap_dot_options() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer('*scratch*', '')

    # stack-oriented path: opt! uses ed.opt-set hostcall.
    ed.vm.eval('"cap.shell" "true" opt!', filename='<test>')
    assert int(ed.vm.stack.pop()) == 1

    # should refresh host.feature? like set/toggle.
    ed.vm.eval('"ed.shell" host.feature?', filename='<test>')
    assert int(ed.vm.stack.pop()) == 1


def test_option_alias_savehistory_updates_canonical_history_persist() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer('*scratch*', '')

    ed.vm.eval('set savehistory true', filename='<test>')
    assert int(ed.vm.stack.pop()) == 1
    assert bool(ed.options.get('history.persist')) is True
    assert bool(ed.options.get('savehistory')) is True

    ed.vm.eval('show savehistory', filename='<test>')
    assert int(ed.vm.stack.pop()) == 1

    ed.vm.eval('toggle savehistory', filename='<test>')
    assert int(ed.vm.stack.pop()) == 0
    assert bool(ed.options.get('history.persist')) is False



def test_option_inventory_rows_expose_show_surface_and_local_override_state() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer('*scratch*', '')

    ed.exec_command_line('setlocal readonly true')

    rows = ed.option_inventory_rows(names=['readonly', 'savehistory', 'history.persist', 'clipboard'])
    assert rows == [
        ['readonly', 'true', 'false', 'bool', 1],
        ['history.persist', 'false', 'false', 'bool', 0],
        ['clipboard', 'internal', 'internal', 'enum[internal|external|terminal]', 0],
    ]

    ed.exec_command_line('show readonly')
    assert ed.messages[-1] == 'readonly=true (local)'

    ed.exec_command_line('show clipboard')
    assert ed.messages[-1] == 'clipboard=internal'



def test_option_inventory_rows_hostcall_uses_canonical_names_only() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer('*scratch*', '')

    ed.exec_command_line('setlocal readonly true')
    ed.vm.eval('"ed.option-inventory-rows" hostcall', filename='<test>')
    rows = ed.vm.stack.pop()
    by_name = {row[0]: row for row in rows}

    assert by_name['readonly'] == ['readonly', 'true', 'false', 'bool', 1]
    assert by_name['history.persist'] == ['history.persist', 'false', 'false', 'bool', 0]
    assert 'savehistory' not in by_name


def test_option_detail_row_and_showoption_surface_exact_option_state() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer('*scratch*', '')

    ed.exec_command_line('setlocal readonly true')
    row = ed.option_detail_row('readonly')
    assert row == [
        'readonly',
        'readonly',
        'true',
        'false',
        'bool',
        1,
        'disallow edits and saves in the current buffer unless locally overridden',
    ]

    ed.exec_command_line('showoption readonly')
    assert ed.messages[-1] == (
        'option readonly [bool] value=true default=false (local): disallow edits and saves in the current buffer unless locally overridden'
    )

    ed.exec_command_line('showoption savehistory')
    assert ed.messages[-1] == (
        'option savehistory -> history.persist [bool] value=false default=false: '
        'remember prompt/command history between sessions (requires cap.persist)'
    )



def test_showoption_root_reports_runtime_summary_then_usage() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer('*scratch*', '')
    ed.exec_command_line('setlocal readonly true')

    rows = ed.option_inventory_rows()
    target = next((row for row in rows if int(row[4]) and str(row[1]) != str(row[2])), next((row for row in rows if int(row[4])), rows[0]))
    summary = f"{len(rows)} options · {target[0]}={target[1]}" + (" (local)" if int(target[4]) else "")

    ed.messages.clear()
    assert ed.exec_command_line('showoption') is False
    assert ed.messages == [
        f'showoption: {summary}',
        'usage: showoption NAME',
    ]



def test_option_section_summary_rows_and_showoptiongroups_surface() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer('*scratch*', '')

    rows = ed.option_section_summary_rows('disallow edits')
    assert rows == [[
        'Editor',
        1,
        'readonly',
        'disallow edits and saves in the current buffer unless locally overridden',
    ]]

    ed.vm.eval('"disallow edits" "ed.option-section-summary-rows" hostcall', filename='<test>')
    assert ed.vm.stack.pop() == [[
        'Editor',
        1,
        'readonly',
        'disallow edits and saves in the current buffer unless locally overridden',
    ]]

    assert ed.exec_command_line('showoptiongroups disallow edits') is True
    assert ed.messages == [
        'showoptiongroups disallow edits: 1 section(s), 1 option(s)',
        'Editor: 1 (e.g. readonly — disallow edits and saves in the current buffer unless locally overridden)',
    ]

    cap_rows = ed.option_section_summary_rows('cap.')
    by_label = {str(row[0]): row for row in cap_rows}
    assert 'Capabilities' in by_label
    assert str(by_label['Capabilities'][2]).startswith('cap.')

def test_option_detail_row_hostcall_preserves_alias_query_and_missing_surface() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer('*scratch*', '')

    ed.vm.eval('"savehistory" "ed.option-detail-row" hostcall', filename='<test>')
    assert ed.vm.stack.pop() == [
        'savehistory',
        'history.persist',
        'false',
        'false',
        'bool',
        0,
        'remember prompt/command history between sessions (requires cap.persist)',
    ]

    assert ed.option_detail_row('no-such-option') is None
    assert ed.exec_command_line('showoption no-such-option') is False
    assert ed.messages[-1] == 'showoption: no such option: no-such-option'
