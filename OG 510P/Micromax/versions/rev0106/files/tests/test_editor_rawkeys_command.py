from micromax_editor.editor import Editor


def test_rawkeys_command_toggles_option() -> None:
    ed = Editor()

    assert bool(ed.options.get('tui.rawkeys')) is False
    assert ed.exec_command_line('rawkeys') is True
    assert bool(ed.options.get('tui.rawkeys')) is True

    assert ed.exec_command_line('rawkeys off') is True
    assert bool(ed.options.get('tui.rawkeys')) is False

    assert ed.exec_command_line('rawkeys on') is True
    assert bool(ed.options.get('tui.rawkeys')) is True


def test_rawkeys_command_rejects_garbage_args() -> None:
    ed = Editor()
    assert ed.exec_command_line('rawkeys maybe') is False
