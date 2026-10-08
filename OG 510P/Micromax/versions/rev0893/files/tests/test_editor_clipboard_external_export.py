from __future__ import annotations

import types

from micromax_editor.editor import Editor
from micromax_editor.micromax_bridge import install_editor_hostcalls


def test_clipboard_external_export_pipes_to_tool(monkeypatch) -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.exec_command_line('set clipboard external')

    # Pretend an external tool exists.
    import micromax_editor.clipboard_external as ce

    monkeypatch.setattr(ce, 'detect_external_clipboard_cmd', lambda: ce.ClipboardCmd(['fakeclip']))

    captured = {}

    def fake_run(argv, **kw):
        captured['argv'] = list(argv)
        captured['input'] = kw.get('input')
        # emulate subprocess.CompletedProcess
        return types.SimpleNamespace(returncode=0, stderr='')

    import subprocess

    monkeypatch.setattr(subprocess, 'run', fake_run)

    ed.set_clipboard_items(['hi'], kind='items')
    ok, err = ed.clipboard_external_export()
    assert ok
    assert err == ''
    assert captured['argv'] == ['fakeclip']
    assert captured['input'] == 'hi'


def test_clipboard_external_export_gates_script_origin(monkeypatch) -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.exec_command_line('set clipboard external')

    import micromax_editor.clipboard_external as ce

    monkeypatch.setattr(ce, 'detect_external_clipboard_cmd', lambda: ce.ClipboardCmd(['fakeclip']))

    import subprocess

    monkeypatch.setattr(subprocess, 'run', lambda argv, **kw: types.SimpleNamespace(returncode=0, stderr=''))

    with ed.script_context():
        ed.set_clipboard_items(['hi'], kind='items')

    ok, err = ed.clipboard_external_export()
    assert not ok
    assert 'cap.clipboard-write' in err

    ed.exec_command_line('set cap.clipboard-write true')
    ok2, err2 = ed.clipboard_external_export()
    assert ok2
    assert err2 == ''


def test_clipboard_external_export_missing_tool_returns_hint(monkeypatch) -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.exec_command_line('set clipboard external')

    import micromax_editor.clipboard_external as ce

    monkeypatch.setattr(ce, 'detect_external_clipboard_cmd', lambda: None)

    ed.set_clipboard_items(['hi'], kind='items')
    ok, err = ed.clipboard_external_export()
    assert not ok
    assert 'no external clipboard tool' in err
