from __future__ import annotations

import json

import pytest

from micromax.vm import MicromaxError
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



def test_plugin_dependency_cycle_is_reported_without_loading(tmp_path) -> None:
    root = tmp_path / "plugins"
    root.mkdir()

    a = root / "a"
    a.mkdir()
    (a / "init.mx").write_text(': aword "a" ;\n', encoding="utf-8")
    (a / "plugin.json").write_text(json.dumps({"requires": ["b"]}), encoding="utf-8")

    b = root / "b"
    b.mkdir()
    (b / "init.mx").write_text(': bword "b" ;\n', encoding="utf-8")
    (b / "plugin.json").write_text(json.dumps({"requires": ["a"]}), encoding="utf-8")

    ed = Editor()
    install_editor_hostcalls(ed)
    pm = PluginManager(ed.vm)
    ed.plugin_manager = pm

    loaded = pm.load_tree(root)

    assert loaded == []
    assert set(pm.candidates) == {"a", "b"}
    assert "a" not in pm.plugins
    assert "b" not in pm.plugins
    assert any(name == "a" and "dependency cycle" in err for name, err in pm.load_errors)
    assert any(name == "b" and "dependency cycle" in err for name, err in pm.load_errors)


def test_plugin_unload_refuses_loaded_dependents(tmp_path) -> None:
    root = tmp_path / "plugins"
    root.mkdir()

    b = root / "b"
    b.mkdir()
    (b / "init.mx").write_text(': bword "b" ;\n', encoding="utf-8")

    a = root / "a"
    a.mkdir()
    (a / "init.mx").write_text(': aword "a" ;\n', encoding="utf-8")
    (a / "plugin.json").write_text(json.dumps({"requires": ["b"]}), encoding="utf-8")

    ed = Editor()
    install_editor_hostcalls(ed)
    pm = PluginManager(ed.vm)
    ed.plugin_manager = pm

    loaded = pm.load_tree(root)
    assert [pl.name for pl in loaded] == ["b", "a"]
    assert pm.loaded_dependents("b") == ["a"]

    with pytest.raises(MicromaxError, match="loaded dependents: a"):
        pm.unload("b")

    assert set(pm.plugins) == {"a", "b"}
    ed.vm.eval("use a aword use b bword", filename="<test>")
    assert ed.vm.stack.pop() == "b"
    assert ed.vm.stack.pop() == "a"

    pm.unload("a")
    pm.unload("b")
    assert pm.plugins == {}
