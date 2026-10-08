from micromax_editor.editor import Editor
from micromax_editor.micromax_bridge import install_editor_hostcalls


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
