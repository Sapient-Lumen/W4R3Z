from __future__ import annotations

from micromax_editor.editor import Editor


def test_load_user_init_from_env(monkeypatch, tmp_path) -> None:
    init = tmp_path / 'init.mx'
    init.write_text(': hello "ok" ;\n', encoding='utf-8')

    monkeypatch.setenv('MICROMAX_INIT', str(init))

    ed = Editor()
    assert ed.load_user_init() is True

    ed.vm.eval('hello', filename='<test>')
    assert ed.vm.stack.pop() == 'ok'


def test_load_user_init_uses_vm_read_timeout_boundary(monkeypatch, tmp_path) -> None:
    from types import SimpleNamespace
    import micromax_editor.editor as editor_mod

    init = tmp_path / 'init.mx'
    init.write_text(': placeholder ;\n', encoding='utf-8')

    ed = Editor()
    ed.vm.editor_hostcall_fs_read_timeout_seconds = 0.25
    calls: list[float | None] = []

    def fake_read(path, *, encoding, containment_root=None, max_bytes=None, timeout_seconds=None):  # type: ignore[no-untyped-def]
        calls.append(timeout_seconds)
        return SimpleNamespace(text=': hello "ok" ;\n', path=str(path))

    monkeypatch.setattr(editor_mod, "read_file_for_editor", fake_read)

    assert ed.load_user_init(path=str(init)) is True
    assert calls == [0.25]
    ed.vm.eval('hello', filename='<test>')
    assert ed.vm.stack.pop() == 'ok'
