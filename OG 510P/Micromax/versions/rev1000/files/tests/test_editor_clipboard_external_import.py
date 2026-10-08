from __future__ import annotations

import pytest

from micromax import MicromaxError
from micromax_editor.editor import Editor
from micromax_editor.micromax_bridge import install_editor_hostcalls


def test_clipboard_external_import_reads_from_tool(monkeypatch) -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer('*t*', '')
    ed.exec_command_line('set clipboard external')

    import micromax_editor.clipboard_external as ce

    monkeypatch.setattr(ce, 'detect_external_clipboard_read_cmd', lambda: ce.ClipboardCmd(['fakepaste']))

    captured = {}

    def fake_run(argv, **kw):
        captured['argv'] = list(argv)
        from micromax_editor.host_process import BoundedProcessResult

        return BoundedProcessResult(returncode=0, stdout='hello\n', stderr='')

    import micromax_editor.host_process as hp

    monkeypatch.setattr(hp, 'run_argv_bounded', fake_run)

    text, err = ed.clipboard_external_import_text()
    assert err == ''
    assert text == 'hello\n'
    assert captured['argv'] == ['fakepaste']


def test_paste_action_imports_external_when_internal_empty(monkeypatch) -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer('*t*', '')
    ed.exec_command_line('set clipboard external')

    import micromax_editor.clipboard_external as ce

    monkeypatch.setattr(ce, 'detect_external_clipboard_read_cmd', lambda: ce.ClipboardCmd(['fakepaste']))

    from micromax_editor.host_process import BoundedProcessResult
    import micromax_editor.host_process as hp

    monkeypatch.setattr(hp, 'run_argv_bounded', lambda argv, **kw: BoundedProcessResult(0, 'abc', ''))

    # Ensure internal clipboard is empty.
    ed.set_clipboard_items([], kind='items')

    ok = ed.run_action('Paste')
    assert ok
    assert ed.cur().buf.get_text() == 'abc'


def test_paste_action_does_not_import_in_script_context_without_cap(monkeypatch) -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer('*t*', '')
    ed.exec_command_line('set clipboard external')

    import micromax_editor.clipboard_external as ce

    monkeypatch.setattr(ce, 'detect_external_clipboard_read_cmd', lambda: ce.ClipboardCmd(['fakepaste']))

    # Would return text if called, but script context should gate it.
    from micromax_editor.host_process import BoundedProcessResult
    import micromax_editor.host_process as hp

    monkeypatch.setattr(hp, 'run_argv_bounded', lambda argv, **kw: BoundedProcessResult(0, 'abc', ''))

    ed.set_clipboard_items([], kind='items')

    with ed.script_context():
        ok = ed.run_action('Paste')
    assert not ok
    assert ed.cur().buf.get_text() == ''


def test_hostcall_clipboard_import_is_capability_gated(monkeypatch) -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer('*t*', '')
    ed.exec_command_line('set clipboard external')

    vm = ed.vm
    vm.stack.append('ed.clipboard-import')
    with pytest.raises(MicromaxError):
        vm.eval('hostcall')

    # Enable script capability.
    assert ed.exec_command_line('set cap.clipboard-read true')

    import micromax_editor.clipboard_external as ce

    monkeypatch.setattr(ce, 'detect_external_clipboard_read_cmd', lambda: ce.ClipboardCmd(['fakepaste']))

    from micromax_editor.host_process import BoundedProcessResult
    import micromax_editor.host_process as hp

    monkeypatch.setattr(hp, 'run_argv_bounded', lambda argv, **kw: BoundedProcessResult(0, 'xyz', ''))

    vm.stack.append('ed.clipboard-import')
    vm.eval('hostcall')
    err = str(vm.stack.pop())
    text = str(vm.stack.pop())
    ok = int(vm.stack.pop())

    assert ok == 1
    assert text == 'xyz'
    assert err == ''


def test_clipboard_external_import_output_budget_reports_error(monkeypatch) -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer('*t*', '')
    ed.exec_command_line('set clipboard external')
    ed.exec_command_line('set clipboard.external.outputmax 4')

    import micromax_editor.clipboard_external as ce

    monkeypatch.setattr(ce, 'detect_external_clipboard_read_cmd', lambda: ce.ClipboardCmd(['fakepaste']))

    from micromax_editor.host_process import BoundedProcessResult
    import micromax_editor.host_process as hp

    def fake_run(argv, **kw):
        assert kw.get('max_output_bytes') == 4
        return BoundedProcessResult(
            125,
            'abcd',
            'clipboard read tool: output exceeded process output budget 4 bytes',
            output_truncated=True,
        )

    monkeypatch.setattr(hp, 'run_argv_bounded', fake_run)

    text, err = ed.clipboard_external_import_text()
    assert text is None
    assert 'output exceeded process output budget 4 bytes' in err
