from __future__ import annotations

import pytest

from micromax import MicromaxError
from micromax_editor.editor import Editor
from micromax_editor.micromax_bridge import install_editor_hostcalls


def _editor() -> Editor:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer("*actions*", "")
    return ed


def _hostcall(ed: Editor, name: str, *args: object) -> list[object]:
    ed.vm.stack[:] = list(args)
    ed.vm.stack.append(str(name))
    ed.vm.eval("hostcall", filename="<action-authority-test>")
    return list(ed.vm.stack)


def test_script_action_inventory_hides_dynamic_trusted_actions_but_keeps_core_actions() -> None:
    ed = _editor()

    def trusted_action(_ed: Editor) -> bool:
        return True

    ed.actions.register("TrustedSecretAction", trusted_action, doc="trusted action docs")

    with ed.script_context(origin_id="script-a"):
        names = set(ed.action_names())
        assert "InsertText" in names
        assert "TrustedSecretAction" not in names
        assert ed.action_detail_row("InsertText") is not None
        assert ed.action_detail_row("TrustedSecretAction") is None
        assert not any(row[0] == "TrustedSecretAction" for row in ed.command_palette_rows())
        assert not any(row[0] == "TrustedSecretAction" for row in ed.help_topic_rows())


def test_action_read_capability_reveals_dynamic_action_metadata() -> None:
    ed = _editor()

    def trusted_action(_ed: Editor) -> bool:
        return True

    ed.actions.register("TrustedSecretAction", trusted_action, doc="trusted action docs")
    assert ed.exec_command_line("set cap.action-read true") is True

    with ed.script_context(origin_id="script-a"):
        row = ed.action_detail_row("TrustedSecretAction")
        names = set(ed.action_names())
        palette = ed.command_palette_rows()

    assert row is not None
    assert row[:2] == ["TrustedSecretAction", "trusted action docs"]
    assert "TrustedSecretAction" in names
    assert any(r[:3] == ["TrustedSecretAction", "action", "trusted action docs"] for r in palette)


def test_action_detail_hostcall_denial_preserves_name_operand() -> None:
    ed = _editor()

    def trusted_action(_ed: Editor) -> bool:
        return True

    ed.actions.register("TrustedSecretAction", trusted_action, doc="trusted action docs")

    with ed.script_context(origin_id="script-a"):
        ed.vm.stack[:] = ["TrustedSecretAction"]
        with pytest.raises(MicromaxError, match="cannot read action: TrustedSecretAction"):
            ed.vm.stack.append("ed.action-detail-row")
            ed.vm.eval("hostcall", filename="<action-authority-test>")

    assert ed.vm.stack == ["TrustedSecretAction"]


def test_script_cannot_run_dynamic_trusted_action_without_run_capability() -> None:
    ed = _editor()
    calls: list[str] = []

    def trusted_action(_ed: Editor) -> bool:
        calls.append("ran")
        return True

    ed.actions.register("TrustedSecretAction", trusted_action, doc="trusted action docs")

    with ed.script_context(origin_id="script-a"):
        assert ed.run_action("TrustedSecretAction") is False
        stack = _hostcall(ed, "ed.run", "TrustedSecretAction")

    assert stack[-1] == 0
    assert calls == []
    assert any("cap.action-run" in msg for msg in ed.messages)


def test_action_run_capability_runs_dynamic_action_under_script_authority() -> None:
    ed = _editor()
    calls: list[str] = []

    def trusted_action(inner: Editor) -> bool:
        calls.append("ran")
        # Running the action is not the same as becoming trusted: cap.* option
        # mutation still routes through script-context policy.
        inner.exec_command_line("set cap.fs-save true")
        return True

    ed.actions.register("TrustedSecretAction", trusted_action, doc="trusted action docs")
    assert ed.exec_command_line("set cap.action-run true") is True

    with ed.script_context(origin_id="script-a"):
        assert ed.run_action("TrustedSecretAction") is True

    assert calls == ["ran"]
    assert ed.options.get("cap.fs-save") is False


def test_action_capabilities_are_advertised() -> None:
    ed = _editor()
    rows = {str(row[0]): row for row in _hostcall(ed, "host.capabilities")[-1]}
    assert rows["ed.action-read"][1] == "cap.action-read"
    assert rows["ed.action-read"][3] == 0
    assert rows["ed.action-run"][1] == "cap.action-run"
    assert rows["ed.action-run"][3] == 0

    ed.vm.eval('"ed.action-run" host.feature?')
    assert int(ed.vm.stack.pop()) == 0
    assert ed.exec_command_line("set cap.action-run true") is True
    ed.vm.eval('"ed.action-run" host.feature?')
    assert int(ed.vm.stack.pop()) == 1


def test_script_registered_action_is_same_origin_visible_and_runnable() -> None:
    ed = _editor()
    calls: list[str] = []

    def script_action(_ed: Editor) -> bool:
        calls.append("ran")
        return True

    with ed.script_context(origin_id="script-a"):
        ed.actions.register("ScriptLocalAction", script_action, doc="script docs")
        assert "ScriptLocalAction" in set(ed.action_names())
        assert ed.action_detail_row("ScriptLocalAction")[:2] == ["ScriptLocalAction", "script docs"]
        assert ed.run_action("ScriptLocalAction") is True

    with ed.script_context(origin_id="script-b"):
        assert "ScriptLocalAction" not in set(ed.action_names())
        assert ed.action_detail_row("ScriptLocalAction") is None
        assert ed.run_action("ScriptLocalAction") is False

    assert calls == ["ran"]


def test_script_registered_action_cannot_overwrite_trusted_core_action() -> None:
    ed = _editor()

    def replacement(_ed: Editor) -> bool:
        return True

    original = ed.actions.get("InsertText")
    with ed.script_context(origin_id="script-a"):
        with pytest.raises(PermissionError, match="cannot modify action: InsertText"):
            ed.actions.register("InsertText", replacement, doc="replacement")
    assert ed.actions.get("InsertText") is original


def test_plugin_group_cleanup_removes_directly_registered_action(tmp_path) -> None:
    from micromax_editor.plugins import PluginManager
    from micromax_editor.vm_load_policy import plugin_load_root_context

    root = tmp_path / "plugins"
    plug = root / "alpha"
    plug.mkdir(parents=True)
    (plug / "init.mx").write_text(": init ( -- ) ;\n", encoding="utf-8")

    ed = _editor()
    pm = PluginManager(ed.vm)
    ed.plugin_manager = pm
    plugin = pm.load_tree(root)[0]
    calls: list[str] = []

    def plugin_action(_ed: Editor) -> bool:
        calls.append("ran")
        return True

    old_group = ed.vm.current_editor_group
    try:
        ed.vm.current_editor_group = plugin.group
        with plugin_load_root_context(ed.vm, plugin.root, generation=plugin.generation):
            with ed.script_context(origin_id="plugin:alpha"):
                ed.actions.register("AlphaPluginAction", plugin_action, doc="plugin action docs")
                assert ed.run_action("AlphaPluginAction") is True
    finally:
        ed.vm.current_editor_group = old_group

    action = ed.actions.get("AlphaPluginAction")
    assert action is not None
    assert action.group == plugin.group
    assert calls == ["ran"]

    pm.unload("alpha")
    assert ed.actions.get("AlphaPluginAction") is None


def test_failed_plugin_callback_rolls_back_direct_action_registration(tmp_path) -> None:
    from micromax_editor.plugins import PluginManager

    root = tmp_path / "plugins"
    plug = root / "alpha"
    plug.mkdir(parents=True)
    (plug / "init.mx").write_text(": init ( -- ) ;\n", encoding="utf-8")

    ed = _editor()
    pm = PluginManager(ed.vm)
    ed.plugin_manager = pm
    plugin = pm.load_tree(root)[0]

    def lazy_action(_ed: Editor) -> bool:
        return True

    with pytest.raises(RuntimeError, match="boom"):
        with ed.plugin_callback_context(plugin.root, plugin.group, plugin_generation=plugin.generation):
            with ed.script_context(origin_id="plugin:alpha"):
                ed.actions.register("LazyPluginAction", lazy_action, doc="half registered")
                assert ed.actions.get("LazyPluginAction") is not None
                raise RuntimeError("boom")

    assert ed.actions.get("LazyPluginAction") is None
