from __future__ import annotations

import json

import pytest

from micromax import MicromaxError
from micromax_editor.editor import Editor
from micromax_editor.micromax_bridge import install_editor_hostcalls
from micromax_editor.plugins import PluginManager
from micromax_editor.vm_load_policy import plugin_load_root_context


def _editor_with_plugins(tmp_path):
    root = tmp_path / "plugins"
    root.mkdir()

    a = root / "a"
    a.mkdir()
    (a / "main.mx").write_text(": init ( -- ) ;\n", encoding="utf-8")
    (a / "plugin.json").write_text(
        json.dumps({"entry": "main.mx", "version": "1.0.0", "description": "alpha plugin"}),
        encoding="utf-8",
    )

    b = root / "b"
    b.mkdir()
    (b / "main.mx").write_text(": init ( -- ) ;\n", encoding="utf-8")
    (b / "plugin.json").write_text(
        json.dumps({"entry": "main.mx", "requires": ["missingdep"], "description": "broken plugin"}),
        encoding="utf-8",
    )

    ed = Editor()
    install_editor_hostcalls(ed)
    pm = PluginManager(ed.vm)
    ed.plugin_manager = pm
    pm.load_tree(root)
    return ed, pm


def _hostcall(ed: Editor, name: str, *args: object) -> list[object]:
    ed.vm.stack[:] = list(args)
    ed.vm.stack.append(str(name))
    ed.vm.eval("hostcall", filename="<plugin-authority-test>")
    return list(ed.vm.stack)


def test_script_plugin_inventory_hides_trusted_candidate_and_error_rows(tmp_path) -> None:
    ed, _pm = _editor_with_plugins(tmp_path)

    assert {str(row[0]) for row in ed.plugin_inventory_rows()} == {"a", "b"}

    with ed.script_context(origin_id="script-a"):
        assert ed.plugin_names() == []
        assert ed.plugin_inventory_rows() == []
        assert ed.plugin_detail_row("a") is None
        assert ed.plugin_detail_row("b") is None
        assert _hostcall(ed, "ed.plugin-inventory-rows")[-1] == []
        assert _hostcall(ed, "ed.plugin-section-rows", "")[-1] == []
        assert _hostcall(ed, "plugin.list")[-1] == []
        assert _hostcall(ed, "plugin.errors")[-1] == []


def test_loaded_plugin_can_read_its_own_plugin_row_only(tmp_path) -> None:
    ed, pm = _editor_with_plugins(tmp_path)
    plugin = pm.plugins["a"]

    with plugin_load_root_context(ed.vm, plugin.root, generation=plugin.generation):
        with ed.script_context(origin_id="plugin:a"):
            assert ed.plugin_names() == ["a"]
            own = ed.plugin_detail_row("a")
            assert own is not None
            assert own[1:4] == ["a", "loaded", "1.0.0"]
            assert ed.plugin_detail_row("b") is None
            assert {str(row[0]) for row in ed.plugin_inventory_rows()} == {"a"}


def test_plugin_read_capability_reveals_protected_plugin_state(tmp_path) -> None:
    ed, _pm = _editor_with_plugins(tmp_path)
    assert ed.exec_command_line("set cap.plugin-read true") is True

    with ed.script_context(origin_id="script-a"):
        names = set(ed.plugin_names())
        detail = ed.plugin_detail_row("b")
        rows = {str(row[0]): row for row in _hostcall(ed, "ed.plugin-inventory-rows")[-1]}

    assert names == {"a", "b"}
    assert detail is not None
    assert detail[1] == "b"
    assert detail[2] == "error"
    assert "missingdep" in str(detail[4])
    assert rows["a"][1] == "loaded"
    assert rows["b"][1] == "error"


def test_plugin_detail_hostcall_denial_preserves_name_operand(tmp_path) -> None:
    ed, _pm = _editor_with_plugins(tmp_path)

    with ed.script_context(origin_id="script-a"):
        ed.vm.stack[:] = ["a"]
        with pytest.raises(MicromaxError, match="cannot read plugin: a"):
            ed.vm.stack.append("ed.plugin-detail-row")
            ed.vm.eval("hostcall", filename="<plugin-authority-test>")

    assert ed.vm.stack == ["a"]


def test_script_plugin_info_and_errors_do_not_leak_protected_rows(tmp_path) -> None:
    ed, _pm = _editor_with_plugins(tmp_path)

    with ed.script_context(origin_id="script-a"):
        ed.messages.clear()
        assert ed.exec_command_line("plugin list") is True
        assert ed.messages == ["plugin list: 0 plugin(s)"]

        ed.messages.clear()
        assert ed.exec_command_line("plugin info a") is False
        assert ed.messages == ["plugin info: no such plugin: a"]

        ed.messages.clear()
        assert ed.exec_command_line("plugin errors b") is False
        assert ed.messages == ["plugin errors: no such plugin: b"]

    assert ed.exec_command_line("set cap.plugin-read true") is True
    with ed.script_context(origin_id="script-b"):
        ed.messages.clear()
        assert ed.exec_command_line("plugin errors b") is True
        assert ed.messages[:2] == [
            "plugin errors: b [error, deps:missingdep]",
            "  errors: missing dependency: missingdep",
        ]


def test_plugin_read_capability_is_advertised() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    _hostcall(ed, "host.capabilities")
    rows = {str(row[0]): row for row in ed.vm.stack[-1]}
    assert rows["ed.plugin-read"][1] == "cap.plugin-read"
    assert rows["ed.plugin-read"][3] == 0

    assert ed.exec_command_line("set cap.plugin-read true") is True
    _hostcall(ed, "host.capabilities")
    rows = {str(row[0]): row for row in ed.vm.stack[-1]}
    assert rows["ed.plugin-read"][3] == 1
