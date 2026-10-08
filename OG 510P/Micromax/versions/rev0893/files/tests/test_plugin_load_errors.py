from __future__ import annotations

from micromax_editor.editor import Editor
from micromax_editor.micromax_bridge import install_editor_hostcalls
from micromax_editor.plugins import PluginManager


def test_plugin_load_tree_continues_after_failure(tmp_path) -> None:
    root = tmp_path / 'plugins'
    root.mkdir()

    good = root / 'good'
    good.mkdir()
    (good / 'init.mx').write_text(': okword "ok" ;\n', encoding='utf-8')

    bad = root / 'bad'
    bad.mkdir()
    # Bind a key, then fail so we can verify cleanup.
    (bad / 'init.mx').write_text('"Ctrl-x" "CursorDown" "ed.bind" hostcall\nunknownword\n', encoding='utf-8')

    ed = Editor()
    install_editor_hostcalls(ed)

    pm = PluginManager(ed.vm)
    ed.plugin_manager = pm

    loaded = pm.load_tree(root)

    assert any(pl.name == 'good' for pl in loaded)
    assert 'good' in pm.plugins
    assert 'bad' not in pm.plugins

    assert pm.load_errors
    assert any(name == 'bad' for name, _err in pm.load_errors)

    # The bad plugin's binding should have been cleaned up.
    assert ed.resolve_key_binding('Ctrl-x') is None

    # The good plugin's word should be present.
    ed.vm.eval('use good okword', filename='<test>')
    assert ed.vm.stack.pop() == 'ok'
