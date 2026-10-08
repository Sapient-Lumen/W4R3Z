from __future__ import annotations

import json

from micromax_editor.editor import Editor
from micromax_editor.micromax_bridge import install_editor_hostcalls
from micromax_editor.plugins import PluginManager


def test_plugin_json_name_mismatch_is_error(tmp_path) -> None:
    root = tmp_path / "plugins"
    root.mkdir()

    p = root / "x"
    p.mkdir()
    (p / "init.mx").write_text(': okword "ok" ;\n', encoding="utf-8")
    (p / "plugin.json").write_text(json.dumps({"name": "y"}), encoding="utf-8")

    ed = Editor()
    install_editor_hostcalls(ed)
    pm = PluginManager(ed.vm)
    ed.plugin_manager = pm

    loaded = pm.load_tree(root)
    assert not loaded
    assert any(name == "x" for name, _err in pm.load_errors)


def test_plugin_json_entry_override_and_requires_order(tmp_path) -> None:
    root = tmp_path / "plugins"
    root.mkdir()

    b = root / "b"
    b.mkdir()
    (b / "init.mx").write_text(': bword "b" ;\n', encoding="utf-8")
    (b / "plugin.json").write_text(json.dumps({"version": "0.1.0"}), encoding="utf-8")

    a = root / "a"
    a.mkdir()
    (a / "main.mx").write_text(': aword "a" ;\n', encoding="utf-8")
    (a / "plugin.json").write_text(json.dumps({"entry": "main.mx", "requires": ["b"]}), encoding="utf-8")

    ed = Editor()
    install_editor_hostcalls(ed)
    pm = PluginManager(ed.vm)
    ed.plugin_manager = pm

    loaded = pm.load_tree(root)
    assert [pl.name for pl in loaded] == ["b", "a"]

    ed.vm.eval("use a aword use b bword", filename="<test>")
    assert ed.vm.stack.pop() == "b"
    assert ed.vm.stack.pop() == "a"


def test_plugin_missing_dependency_skips_plugin(tmp_path) -> None:
    root = tmp_path / "plugins"
    root.mkdir()

    a = root / "a"
    a.mkdir()
    (a / "init.mx").write_text(': aword "a" ;\n', encoding="utf-8")
    (a / "plugin.json").write_text(json.dumps({"requires": ["nope"]}), encoding="utf-8")

    ed = Editor()
    install_editor_hostcalls(ed)
    pm = PluginManager(ed.vm)
    ed.plugin_manager = pm

    loaded = pm.load_tree(root)
    assert not loaded
    assert "a" not in pm.plugins
    assert any(name == "a" and "missing dependency" in err for name, err in pm.load_errors)


def test_plugin_reload_uses_entry_when_present(tmp_path) -> None:
    root = tmp_path / "plugins"
    root.mkdir()

    a = root / "a"
    a.mkdir()
    (a / "main.mx").write_text(': aword "a1" ;\n', encoding="utf-8")
    (a / "plugin.json").write_text(json.dumps({"entry": "main.mx"}), encoding="utf-8")

    ed = Editor()
    install_editor_hostcalls(ed)
    pm = PluginManager(ed.vm)
    ed.plugin_manager = pm

    loaded = pm.load_tree(root)
    assert [pl.name for pl in loaded] == ["a"]

    # Reload should succeed even though there is no init.mx.
    (a / "main.mx").write_text(': aword "a2" ;\n', encoding="utf-8")
    pm.reload("a")

    ed.vm.eval("use a aword", filename="<test>")
    assert ed.vm.stack.pop() == "a2"
