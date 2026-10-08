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
