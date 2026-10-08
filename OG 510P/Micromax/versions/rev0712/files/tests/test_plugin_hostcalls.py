from __future__ import annotations

import json

from micromax_editor.editor import Editor
from micromax_editor.micromax_bridge import install_editor_hostcalls
from micromax_editor.plugins import PluginManager


def _hostcall(ed: Editor, name: str, *args: object) -> list[object]:
    vm = ed.vm
    for a in args:
        vm.stack.append(a)
    vm.stack.append(name)
    vm.eval("hostcall")
    return list(vm.stack)


def test_plugin_hostcalls_list_reload_errors(tmp_path) -> None:
    root = tmp_path / "plugins"
    root.mkdir()

    a = root / "a"
    a.mkdir()
    (a / "main.mx").write_text(': aword "a" ;\n', encoding="utf-8")
    (a / "plugin.json").write_text(json.dumps({"entry": "main.mx", "version": "1.0.0"}), encoding="utf-8")

    ed = Editor()
    install_editor_hostcalls(ed)
    pm = PluginManager(ed.vm)
    ed.plugin_manager = pm
    pm.load_tree(root)

    _hostcall(ed, "plugin.list")
    xs = ed.vm.stack.pop()
    assert isinstance(xs, list)
    assert "a" in xs

    # Reload via hostcall should succeed and reuse the command-path summary dialect.
    (a / "main.mx").write_text(': aword "a2" ;\n', encoding="utf-8")
    _hostcall(ed, "plugin.reload", "a")
    ok = ed.vm.stack.pop()
    assert ok == 1
    assert ed.messages == ["plugin reload: a [loaded, v1.0.0]"]

    _hostcall(ed, "plugin.errors")
    errs = ed.vm.stack.pop()
    assert isinstance(errs, list)


def test_plugin_reload_hostcall_uses_same_failure_dialect_as_command_path(tmp_path) -> None:
    root = tmp_path / "plugins"
    root.mkdir()

    broken = root / "broken"
    broken.mkdir()
    (broken / "plugin.json").write_text(
        json.dumps({"entry": "main.mx", "requires": ["missingdep"]}), encoding="utf-8"
    )
    (broken / "main.mx").write_text(': broken-word "broken" ;\n', encoding="utf-8")

    ed = Editor()
    install_editor_hostcalls(ed)
    pm = PluginManager(ed.vm)
    ed.plugin_manager = pm
    pm.load_tree(root)

    _hostcall(ed, "plugin.reload", "broken")
    ok = ed.vm.stack.pop()
    assert ok == 0
    assert ed.messages == [
        "plugin reload: broken [error, deps:missingdep]",
        "  errors: 1",
        "    - missing dependency: missingdep",
    ]

    ed.messages.clear()
    _hostcall(ed, "plugin.reload", "missing")
    ok = ed.vm.stack.pop()
    assert ok == 0
    assert ed.messages == ["plugin reload: no such plugin: missing"]


def test_plugin_reload_hostcall_without_manager_uses_typed_feedback() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    _hostcall(ed, "plugin.reload", "missing")
    ok = ed.vm.stack.pop()
    assert ok == 0
    assert ed.messages == ["plugin reload: no plugin manager"]
