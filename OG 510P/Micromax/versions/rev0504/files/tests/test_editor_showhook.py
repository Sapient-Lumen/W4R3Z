from micromax_editor.editor import Editor
from micromax_editor.micromax_bridge import install_editor_hostcalls


def _hostcall(ed: Editor, name: str, *args: object) -> list[object]:
    vm = ed.vm
    for arg in args:
        vm.stack.append(arg)
    vm.stack.append(name)
    vm.eval("hostcall")
    return list(vm.stack)


def test_showhook_reports_handlers_and_provenance() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.vm.eval(
        '\n'.join([
            '"cfg" hook-group!',
            ': h1 drop ;',
            "' h1 hook-add ed.pre-action",
            '0 hook-group!',
        ]),
        filename="<hook-test>",
    )

    assert ed.exec_command_line('showhook ed.pre-action')
    assert ed.messages
    msg = ed.messages[-1]
    assert 'hook ed.pre-action: 1 handler(s),' in msg
    assert 'h1#cfg@<hook-test>:' in msg
    assert 'defined at <editor>:' in msg


def test_showhook_rejects_non_hooks() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    assert not ed.exec_command_line('showhook nope')
    assert ed.messages[-1] == 'showhook: not a hook: nope'


def test_showhook_reports_empty_hook_count() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    assert ed.exec_command_line('showhook ed.pre-action')
    assert ed.messages
    msg = ed.messages[-1]
    assert 'hook ed.pre-action: 0 handler(s)' in msg
    assert 'defined at <editor>:' in msg


def test_showhook_reuses_shared_hook_inventory_rows() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.vm.eval(
        '\n'.join([
            '"cfg" hook-group!',
            ': h1 drop ;',
            "' h1 hook-add ed.pre-action",
            '0 hook-group!',
        ]),
        filename='<hook-test>',
    )

    rows = _hostcall(ed, 'ed.hook-inventory-rows', 'ed.pre-action')[-1]
    assert rows == [['h1', 'cfg', ['<hook-test>', 3, 6]]]

    assert ed.exec_command_line('showhook ed.pre-action') is True
    assert ed.messages[-1] == (
        'hook ed.pre-action: 1 handler(s), h1#cfg@<hook-test>:3:6 '
        '(defined at <editor>:1:1)'
    )


def test_hook_detail_row_matches_showhook_first_stop_state() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.vm.eval(
        '\n'.join([
            'hook ed.test.alpha',
            '"cfg" hook-group!',
            ': h1 drop ;',
            "' h1 hook-add ed.test.alpha",
            '0 hook-group!',
        ]),
        filename='<hook-detail>',
    )

    row = _hostcall(ed, 'ed.hook-detail-row', 'ed.test.alpha')[-1]
    assert row == [
        'ed.test.alpha',
        'ed.test.alpha',
        1,
        'h1#cfg',
        'h1#cfg@<hook-detail>:4:6',
        ['<hook-detail>', 1, 1],
    ]

    ed.vm.eval('"ed.test.alpha" hook-state', filename='<hook-state>')
    assert ed.vm.stack.pop() == row

    assert ed.exec_command_line('showhook ed.test.alpha') is True
    assert ed.messages[-1] == (
        'hook ed.test.alpha: 1 handler(s), h1#cfg@<hook-detail>:4:6 '
        '(defined at <hook-detail>:1:1)'
    )


def test_hook_inventory_rows_reject_non_hooks() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    row = _hostcall(ed, 'ed.hook-detail-row', 'showstatus')[-1]
    assert row == 0

    rows = _hostcall(ed, 'ed.hook-inventory-rows', 'showstatus')[-1]
    assert rows == 0


def test_hook_summary_rows_and_showhooks_surface_broad_live_hook_state() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.vm.eval(
        '\n'.join([
            'hook ed.test.alpha',
            'hook ed.test.beta',
            '"cfg" hook-group!',
            ': h1 drop ;',
            "' h1 hook-add ed.test.alpha",
            '0 hook-group!',
        ]),
        filename='<hook-summary>',
    )

    rows = _hostcall(ed, 'ed.hook-summary-rows', 'ed.test')[-1]
    assert rows == [
        ['ed.test.beta', 0, 0, ['<hook-summary>', 2, 1]],
        ['ed.test.alpha', 1, 'h1#cfg', ['<hook-summary>', 1, 1]],
    ]

    assert ed.exec_command_line('showhooks ed.test') is True
    assert ed.messages == [
        'showhooks ed.test: 2 hook(s), 1 handler(s)',
        'ed.test.beta: 0 handler(s) (defined at <hook-summary>:2:1)',
        'ed.test.alpha: 1 handler(s) (e.g. h1#cfg) (defined at <hook-summary>:1:1)',
    ]
