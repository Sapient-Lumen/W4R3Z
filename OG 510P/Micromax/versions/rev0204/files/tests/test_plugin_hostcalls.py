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
    (a / "plugin.json").write_text(json.dumps({"entry": "main.mx"}), encoding="utf-8")

    ed = Editor()
    install_editor_hostcalls(ed)
    pm = PluginManager(ed.vm)
    ed.plugin_manager = pm
    pm.load_tree(root)

    _hostcall(ed, "plugin.list")
    xs = ed.vm.stack.pop()
    assert isinstance(xs, list)
    assert "a" in xs

    # Reload via hostcall should succeed.
    (a / "main.mx").write_text(': aword "a2" ;\n', encoding="utf-8")
    _hostcall(ed, "plugin.reload", "a")
    ok = ed.vm.stack.pop()
    assert ok == 1

    _hostcall(ed, "plugin.errors")
    errs = ed.vm.stack.pop()
    assert isinstance(errs, list)
