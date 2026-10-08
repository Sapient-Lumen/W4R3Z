from __future__ import annotations

import json

from micromax_editor.editor import Editor
from micromax_editor.micromax_bridge import install_editor_hostcalls
from micromax_editor.plugins import PluginManager


def _hostcall(ed: Editor, name: str, *args: object) -> object:
    vm = ed.vm
    vm.stack.clear()
    for a in args:
        vm.stack.append(a)
    vm.stack.append(name)
    vm.eval('hostcall')
    assert vm.stack
    return vm.stack.pop()


def test_pluginpick_opens_prompt_and_dispatches_reload_or_errors(tmp_path) -> None:
    root = tmp_path / "plugins"
    root.mkdir()

    # Loaded plugin.
    a = root / "a"
    a.mkdir()
    (a / "main.mx").write_text(": init ( -- ) ;\n", encoding="utf-8")
    (a / "plugin.json").write_text(json.dumps({"entry": "main.mx", "version": "1.0.0"}), encoding="utf-8")

    # Candidate plugin that is blocked by a missing dependency.
    b = root / "b"
    b.mkdir()
    (b / "main.mx").write_text(": init ( -- ) ;\n", encoding="utf-8")
    (b / "plugin.json").write_text(json.dumps({"entry": "main.mx", "requires": ["missingdep"]}), encoding="utf-8")

    ed = Editor()
    install_editor_hostcalls(ed)

    pm = PluginManager(ed.vm)
    ed.plugin_manager = pm
    pm.load_tree(root)

    # Open plugin picker.
    ed.exec_command_line("pluginpick")
    assert ed.prompt is not None
    assert ed.prompt.kind == "plugin"
    assert "a" in ed.prompt.suggestions
    assert "b" in ed.prompt.suggestions

    # Picking a loaded plugin triggers reload with explicit post-reload state.
    ed.messages.clear()
    ed.prompt.suggest_index = ed.prompt.suggestions.index("a")
    assert ed.submit_prompt()
    assert ed.messages and ed.messages[-1] == "plugin reload: a [loaded, v1.0.0]"

    # Direct command-bar reload uses the same message shape.
    ed.messages.clear()
    assert ed.exec_command_line("plugin reload a") is True
    assert ed.messages == ["plugin reload: a [loaded, v1.0.0]"]

    # Picking a broken plugin now opens the filtered error detail path instead of generic info.
    ed.exec_command_line("pluginpick")
    assert ed.prompt is not None
    ed.messages.clear()
    ed.prompt.suggest_index = ed.prompt.suggestions.index("b")
    assert ed.submit_prompt()
    assert ed.messages == [
        "plugin errors: b [error, deps:missingdep]",
        "  errors: missing dependency: missingdep",
    ]


def test_plugin_reload_failures_use_inventory_dialect_for_broken_and_unknown_targets(tmp_path) -> None:
    root = tmp_path / "plugins"
    root.mkdir()

    a = root / "a"
    a.mkdir()
    (a / "main.mx").write_text(": init ( -- ) ;\n", encoding="utf-8")
    (a / "plugin.json").write_text(json.dumps({"entry": "main.mx", "version": "1.0.0"}), encoding="utf-8")

    b = root / "b"
    b.mkdir()
    (b / "main.mx").write_text(": init ( -- ) ;\n", encoding="utf-8")
    (b / "plugin.json").write_text(json.dumps({"entry": "main.mx", "requires": ["missingdep"]}), encoding="utf-8")

    ed = Editor()
    install_editor_hostcalls(ed)
    pm = PluginManager(ed.vm)
    ed.plugin_manager = pm
    pm.load_tree(root)

    ed.messages.clear()
    assert ed.exec_command_line("plugin reload b") is False
    assert ed.messages == [
        "plugin reload: b [error, deps:missingdep]",
        "  reload: missing dependency: missingdep · not loaded",
    ]

    ed.messages.clear()
    assert ed.exec_command_line("plugin reload missing") is False
    assert ed.messages == ["plugin reload: no such plugin: missing"]


def test_plugin_reload_available_candidate_loads_from_known_candidate(tmp_path) -> None:
    root = tmp_path / "plugins"
    root.mkdir()

    optional = root / "optional"
    optional.mkdir()
    (optional / "main.mx").write_text(": init ( -- ) ;\n", encoding="utf-8")
    (optional / "plugin.json").write_text(json.dumps({"entry": "main.mx", "version": "0.2.0"}), encoding="utf-8")

    ed = Editor()
    install_editor_hostcalls(ed)
    pm = PluginManager(ed.vm)
    ed.plugin_manager = pm
    pm.load_tree(root)
    pm.unload("optional")

    ed.messages.clear()
    assert ed.exec_command_line("plugin reload optional") is True
    assert ed.messages == ["plugin reload: optional [loaded, v0.2.0]"]
    assert "optional" in pm.plugins


def test_plugin_commands_without_manager_fail_with_typed_feedback() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.messages.clear()
    assert ed.exec_command_line("plugin list") is False
    assert ed.messages == ["plugin list: no plugin manager"]

    ed.messages.clear()
    assert ed.exec_command_line("plugin errors") is False
    assert ed.messages == ["plugin errors: no plugin manager"]

    ed.messages.clear()
    assert ed.exec_command_line("plugin info missing") is False
    assert ed.messages == ["plugin info: no plugin manager"]


def test_plugin_root_without_manager_reports_runtime_summary_then_usage() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.messages.clear()
    assert ed.exec_command_line("plugin") is False
    assert ed.messages == [
        "plugin: no plugin manager",
        "usage: plugin list|reload NAME|info NAME|errors [NAME]",
    ]


def test_plugin_root_empty_manager_reports_runtime_summary_then_usage() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.plugin_manager = PluginManager(ed.vm)

    ed.messages.clear()
    assert ed.exec_command_line("plugin") is False
    assert ed.messages == [
        "plugin: 0 plugin(s)",
        "usage: plugin list|reload NAME|info NAME|errors [NAME]",
    ]


def test_plugin_root_live_inventory_reports_runtime_summary_then_usage(tmp_path) -> None:
    root = tmp_path / "plugins"
    root.mkdir()

    a = root / "a"
    a.mkdir()
    (a / "main.mx").write_text(": init ( -- ) ;\n", encoding="utf-8")
    (a / "plugin.json").write_text(json.dumps({"entry": "main.mx", "version": "1.0.0"}), encoding="utf-8")

    b = root / "b"
    b.mkdir()
    (b / "main.mx").write_text(": init ( -- ) ;\n", encoding="utf-8")
    (b / "plugin.json").write_text(json.dumps({"entry": "main.mx", "requires": ["missingdep"]}), encoding="utf-8")

    ed = Editor()
    install_editor_hostcalls(ed)
    pm = PluginManager(ed.vm)
    ed.plugin_manager = pm
    pm.load_tree(root)

    ed.messages.clear()
    assert ed.exec_command_line("plugin") is False
    assert ed.messages == [
        "plugin: 2 plugin(s) (1 error, 1 loaded) · e.g. a [loaded, v1.0.0]",
        "usage: plugin list|reload NAME|info NAME|errors [NAME]",
    ]


def test_showplugin_root_without_manager_reports_runtime_summary_then_usage() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.messages.clear()
    assert ed.exec_command_line("showplugin") is False
    assert ed.messages == [
        "showplugin: no plugin manager",
        "usage: showplugin NAME",
    ]


def test_showplugins_without_manager_fails_with_typed_feedback() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.messages.clear()
    assert ed.exec_command_line("showplugins") is False
    assert ed.messages == ["showplugins: no plugin manager"]


def test_showplugin_root_empty_manager_reports_runtime_summary_then_usage() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.plugin_manager = PluginManager(ed.vm)

    ed.messages.clear()
    assert ed.exec_command_line("showplugin") is False
    assert ed.messages == [
        "showplugin: 0 plugin(s)",
        "usage: showplugin NAME",
    ]


def test_showplugin_root_live_inventory_reports_runtime_summary_then_usage(tmp_path) -> None:
    root = tmp_path / "plugins"
    root.mkdir()

    a = root / "a"
    a.mkdir()
    (a / "main.mx").write_text(": init ( -- ) ;\n", encoding="utf-8")
    (a / "plugin.json").write_text(json.dumps({"entry": "main.mx", "version": "1.0.0"}), encoding="utf-8")

    b = root / "b"
    b.mkdir()
    (b / "main.mx").write_text(": init ( -- ) ;\n", encoding="utf-8")
    (b / "plugin.json").write_text(json.dumps({"entry": "main.mx", "requires": ["missingdep"]}), encoding="utf-8")

    ed = Editor()
    install_editor_hostcalls(ed)
    pm = PluginManager(ed.vm)
    ed.plugin_manager = pm
    pm.load_tree(root)

    ed.messages.clear()
    assert ed.exec_command_line("showplugin") is False
    assert ed.messages == [
        "showplugin: 2 plugin(s) · e.g. a [loaded, v1.0.0]",
        "usage: showplugin NAME",
    ]


def test_pluginpick_without_manager_fails_with_typed_feedback() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.messages.clear()
    assert ed.exec_command_line("pluginpick missing") is True
    assert ed.prompt is not None
    assert ed.prompt.kind == 'plugin'
    assert ed.submit_prompt() is False
    assert ed.messages == ["pluginpick: no plugin manager"]


def test_plugin_inventory_rows_hostcall_matches_plain_plugin_list_summary(tmp_path) -> None:
    root = tmp_path / "plugins"
    root.mkdir()

    a = root / "a"
    a.mkdir()
    (a / "main.mx").write_text(": init ( -- ) ;\n", encoding="utf-8")
    (a / "plugin.json").write_text(json.dumps({"entry": "main.mx", "version": "1.0.0"}), encoding="utf-8")

    b = root / "b"
    b.mkdir()
    (b / "main.mx").write_text(": init ( -- ) ;\n", encoding="utf-8")
    (b / "plugin.json").write_text(json.dumps({"entry": "main.mx", "requires": ["missingdep"]}), encoding="utf-8")

    ed = Editor()
    install_editor_hostcalls(ed)
    pm = PluginManager(ed.vm)
    ed.plugin_manager = pm
    pm.load_tree(root)

    rows = _hostcall(ed, 'ed.plugin-inventory-rows')
    assert rows == [
        ['a', 'loaded', '1.0.0', '', 0],
        ['b', 'error', '', 'missingdep', 1],
    ]

    assert ed.exec_command_line('plugin list') is True
    assert ed.messages == [
        'plugin list: 2 plugin(s) (1 error, 1 loaded); a [loaded, v1.0.0]; b [error, deps:missingdep]'
    ]




def test_plugin_detail_row_and_showplugin_surface_exact_plugin_state(tmp_path) -> None:
    root = tmp_path / "plugins"
    root.mkdir()

    a = root / "a"
    a.mkdir()
    (a / "main.mx").write_text(": init ( -- ) ;\n", encoding="utf-8")
    (a / "plugin.json").write_text(
        json.dumps({"entry": "main.mx", "version": "1.0.0", "description": "demo plugin"}),
        encoding="utf-8",
    )

    b = root / "b"
    b.mkdir()
    (b / "main.mx").write_text(": init ( -- ) ;\n", encoding="utf-8")
    (b / "plugin.json").write_text(json.dumps({"entry": "main.mx", "requires": ["missingdep"]}), encoding="utf-8")

    ed = Editor()
    install_editor_hostcalls(ed)
    pm = PluginManager(ed.vm)
    ed.plugin_manager = pm
    pm.load_tree(root)

    row = ed.plugin_detail_row('a')
    assert row == ['a', 'a', 'loaded', '1.0.0', '', 0, 'demo plugin']
    assert _hostcall(ed, 'ed.plugin-detail-row', 'a') == row

    ed.messages.clear()
    assert ed.exec_command_line('showplugin a') is True
    assert ed.messages == ['plugin a [loaded, v1.0.0] errors=0 — demo plugin']

    row = ed.plugin_detail_row('b')
    assert row == ['b', 'b', 'error', '', 'missingdep', 1, 'missing dependency: missingdep']

    ed.messages.clear()
    assert ed.exec_command_line('showplugin b') is True
    assert ed.messages == ['plugin b [error, deps:missingdep] errors=1 — missing dependency: missingdep']

    assert ed.plugin_detail_row('missing') is None
    ed.messages.clear()
    assert ed.exec_command_line('showplugin missing') is False
    assert ed.messages == ['showplugin: no such plugin: missing']


def test_plugin_reload_broken_target_keeps_multi_error_count_and_last_detail(tmp_path) -> None:
    root = tmp_path / "plugins"
    root.mkdir()

    b = root / "b"
    b.mkdir()
    (b / "main.mx").write_text(": init ( -- ) ;\n", encoding="utf-8")
    (b / "plugin.json").write_text(json.dumps({"entry": "main.mx", "requires": ["missingdep"]}), encoding="utf-8")

    ed = Editor()
    install_editor_hostcalls(ed)
    pm = PluginManager(ed.vm)
    ed.plugin_manager = pm
    pm.load_tree(root)
    pm.load_errors.append(("b", "secondary issue"))

    ed.messages.clear()
    assert ed.exec_command_line("plugin reload b") is False
    assert ed.messages == [
        "plugin reload: b [error, deps:missingdep]",
        "  reload: 2 load errors · last: secondary issue · not loaded",
        "    - missing dependency: missingdep",
        "    - secondary issue",
    ]


def test_showplugin_runtime_keeps_multi_error_count_and_last_detail(tmp_path) -> None:
    root = tmp_path / "plugins"
    root.mkdir()

    b = root / "b"
    b.mkdir()
    (b / "main.mx").write_text(": init ( -- ) ;\n", encoding="utf-8")
    (b / "plugin.json").write_text(json.dumps({"entry": "main.mx", "requires": ["missingdep"]}), encoding="utf-8")

    ed = Editor()
    install_editor_hostcalls(ed)
    pm = PluginManager(ed.vm)
    ed.plugin_manager = pm
    pm.load_tree(root)
    pm.load_errors.append(("b", "secondary issue"))

    ed.messages.clear()
    assert ed.exec_command_line("showplugin b") is True
    assert ed.messages == [
        "plugin b [error, deps:missingdep] errors=2 — 2 load errors · last: secondary issue"
    ]


def test_showplugin_loaded_target_keeps_runtime_state_witness(tmp_path) -> None:
    root = tmp_path / "plugins"
    root.mkdir()

    a = root / "a"
    a.mkdir()
    (a / "main.mx").write_text(": init ( -- ) ;\n", encoding="utf-8")
    (a / "plugin.json").write_text(json.dumps({"entry": "main.mx", "version": "1.0.0"}), encoding="utf-8")

    ed = Editor()
    install_editor_hostcalls(ed)
    pm = PluginManager(ed.vm)
    ed.plugin_manager = pm
    pm.load_tree(root)

    ed.messages.clear()
    assert ed.exec_command_line("showplugin a") is True
    assert ed.messages == [
        "plugin a [loaded, v1.0.0] errors=0 — loaded plugin",
    ]


def test_showplugin_available_candidate_keeps_runtime_state_witness(tmp_path) -> None:
    root = tmp_path / "plugins"
    root.mkdir()

    optional = root / "optional"
    optional.mkdir()
    (optional / "main.mx").write_text(": init ( -- ) ;\n", encoding="utf-8")
    (optional / "plugin.json").write_text(json.dumps({"entry": "main.mx", "version": "0.2.0"}), encoding="utf-8")

    ed = Editor()
    install_editor_hostcalls(ed)
    pm = PluginManager(ed.vm)
    ed.plugin_manager = pm
    pm.load_tree(root)
    pm.plugins.pop("optional", None)

    ed.messages.clear()
    assert ed.exec_command_line('showplugin optional') is True
    assert ed.messages == ['plugin optional [available, v0.2.0] errors=0 — available plugin · not loaded']


def test_showplugin_without_manager_fails_with_typed_feedback() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.messages.clear()
    assert ed.exec_command_line('showplugin missing') is False
    assert ed.messages == ['showplugin: no plugin manager']


def test_pluginpick_exposes_grouped_sections_and_preview_labels(tmp_path) -> None:
    root = tmp_path / "plugins"
    root.mkdir()

    a = root / "a"
    a.mkdir()
    (a / "main.mx").write_text(": init ( -- ) ;\n", encoding="utf-8")
    (a / "plugin.json").write_text(json.dumps({"entry": "main.mx"}), encoding="utf-8")

    b = root / "b"
    b.mkdir()
    (b / "main.mx").write_text(": init ( -- ) ;\n", encoding="utf-8")
    (b / "plugin.json").write_text(json.dumps({"entry": "main.mx", "requires": ["missingdep"]}), encoding="utf-8")

    ed = Editor()
    install_editor_hostcalls(ed)
    pm = PluginManager(ed.vm)
    ed.plugin_manager = pm
    pm.load_tree(root)

    sections = _hostcall(ed, 'ed.plugin-section-rows', '')
    assert sections == [
        ['Errors (1)', [['b', 'plugin', '[error, deps:missingdep]', 'missing dependency: missingdep']]],
        ['Loaded (1)', [['a', 'plugin', '[loaded]', '']]],
    ]

    assert ed.exec_command_line('pluginpick') is True
    assert ed.prompt is not None
    assert ed.prompt.kind == 'plugin'
    assert ed.prompt_current_section() == 'Errors (1)'
    assert ed.prompt_current_preview().startswith('Errors (1): b [error, deps:missingdep]')



def test_pluginpick_preview_rows_use_inventory_summary_dialect(tmp_path) -> None:
    root = tmp_path / "plugins"
    root.mkdir()

    a = root / "a"
    a.mkdir()
    (a / "main.mx").write_text(": init ( -- ) ;\n", encoding="utf-8")
    (a / "plugin.json").write_text(json.dumps({"entry": "main.mx", "version": "1.0.0", "description": "demo plugin"}), encoding="utf-8")

    ed = Editor()
    install_editor_hostcalls(ed)
    pm = PluginManager(ed.vm)
    ed.plugin_manager = pm
    pm.load_tree(root)

    rows = ed.plugin_prompt_rows()
    assert rows == [["a", "plugin", "[loaded, v1.0.0]", "demo plugin"]]

    assert ed.exec_command_line("pluginpick") is True
    assert ed.prompt is not None
    assert ed.prompt_current_preview() == "Loaded (1): a [loaded, v1.0.0] — demo plugin"


def test_command_prompt_completion_for_plugin_subcommands_and_names(tmp_path) -> None:
    root = tmp_path / "plugins"
    root.mkdir()

    a = root / "a"
    a.mkdir()
    (a / "main.mx").write_text(": init ( -- ) ;\n", encoding="utf-8")
    (a / "plugin.json").write_text(json.dumps({"entry": "main.mx"}), encoding="utf-8")

    b = root / "b"
    b.mkdir()
    (b / "main.mx").write_text(": init ( -- ) ;\n", encoding="utf-8")
    (b / "plugin.json").write_text(json.dumps({"entry": "main.mx", "requires": ["missingdep"]}), encoding="utf-8")

    ed = Editor()
    install_editor_hostcalls(ed)
    pm = PluginManager(ed.vm)
    ed.plugin_manager = pm
    pm.load_tree(root)

    # Subcommand completion.
    ed.enter_prompt("command", prefill="plugin ")
    assert ed.prompt is not None
    assert ed.prompt_complete(direction=1)
    assert set(ed.prompt.suggestions) >= {"list ", "reload ", "info ", "errors "}

    # reload suggests only loaded plugins.
    ed.enter_prompt("command", prefill="plugin reload ")
    assert ed.prompt is not None
    assert ed.prompt_complete(direction=1)
    # Only one loaded plugin, so completion inserts it immediately.
    assert ed.prompt.text == "plugin reload a "
    assert not ed.prompt.suggestions

    # info/errors suggest known plugins (loaded + candidates).
    ed.enter_prompt("command", prefill="plugin info ")
    assert ed.prompt is not None
    assert ed.prompt_complete(direction=1)
    assert "a " in ed.prompt.suggestions
    assert "b " in ed.prompt.suggestions

    ed.enter_prompt("command", prefill="plugin errors ")
    assert ed.prompt is not None
    assert ed.prompt_complete(direction=1)
    assert "a " in ed.prompt.suggestions
    assert "b " in ed.prompt.suggestions


def test_plugin_list_reports_stateful_inventory_rows(tmp_path) -> None:
    root = tmp_path / "plugins"
    root.mkdir()

    a = root / "a"
    a.mkdir()
    (a / "main.mx").write_text(": init ( -- ) ;\n", encoding="utf-8")
    (a / "plugin.json").write_text(json.dumps({"entry": "main.mx", "version": "1.0.0"}), encoding="utf-8")

    b = root / "b"
    b.mkdir()
    (b / "main.mx").write_text(": init ( -- ) ;\n", encoding="utf-8")
    (b / "plugin.json").write_text(json.dumps({"entry": "main.mx", "version": "2.0.0", "requires": ["a"]}), encoding="utf-8")

    c = root / "c"
    c.mkdir()
    (c / "main.mx").write_text(": init ( -- ) ;\n", encoding="utf-8")
    (c / "plugin.json").write_text(json.dumps({"entry": "main.mx", "version": "0.3.0", "requires": ["missingdep"]}), encoding="utf-8")

    ed = Editor()
    install_editor_hostcalls(ed)
    pm = PluginManager(ed.vm)
    ed.plugin_manager = pm
    pm.load_tree(root)

    ed.messages.clear()
    assert ed.exec_command_line("plugin list") is True
    assert ed.messages == [
        "plugin list: 3 plugin(s) (1 error, 2 loaded); a [loaded, v1.0.0]; b [loaded, v2.0.0, deps:a]; c [error, v0.3.0, deps:missingdep]"
    ]


def test_plugin_list_empty_inventory_reports_zero_plugins() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    pm = PluginManager(ed.vm)
    ed.plugin_manager = pm

    ed.messages.clear()
    assert ed.exec_command_line("plugin list") is True
    assert ed.messages == ["plugin list: 0 plugin(s)"]


def test_plugin_info_lists_current_errors_and_dependency_states_explicitly(tmp_path) -> None:
    root = tmp_path / "plugins"
    root.mkdir()

    a = root / "a"
    a.mkdir()
    (a / "main.mx").write_text(": init ( -- ) ;\n", encoding="utf-8")
    (a / "plugin.json").write_text(json.dumps({"entry": "main.mx", "version": "1.0.0", "description": "demo plugin"}), encoding="utf-8")

    c = root / "c"
    c.mkdir()
    (c / "main.mx").write_text(": init ( -- ) ;\n", encoding="utf-8")
    (c / "plugin.json").write_text(json.dumps({"entry": "main.mx", "version": "0.3.0", "requires": ["missingdep"]}), encoding="utf-8")

    b = root / "b"
    b.mkdir()
    (b / "main.mx").write_text(": init ( -- ) ;\n", encoding="utf-8")
    (b / "plugin.json").write_text(json.dumps({"entry": "main.mx", "requires": ["a", "c", "missingdep"]}), encoding="utf-8")

    ed = Editor()
    install_editor_hostcalls(ed)
    pm = PluginManager(ed.vm)
    ed.plugin_manager = pm
    pm.load_tree(root)

    ed.messages.clear()
    assert ed.exec_command_line("plugin info a") is True
    assert ed.messages[0] == "plugin info: a [loaded, v1.0.0]"
    assert "  desc: demo plugin" in ed.messages
    assert "  requires: 0" in ed.messages
    assert "  errors: 0 · loaded plugin" in ed.messages

    ed.messages.clear()
    assert ed.exec_command_line("plugin info b") is True
    assert ed.messages == [
        "plugin info: b [error, deps:a,c,missingdep]",
        "  entry: main.mx",
        f"  root: {b}",
        "  requires: 3 (1 loaded, 1 error, 1 missing)",
        "    - a [loaded, v1.0.0]",
        "    - c [error, v0.3.0, deps:missingdep]",
        "    - missingdep [missing]",
        "  errors: missing dependency: missingdep",
    ]

    ed.messages.clear()
    assert ed.exec_command_line("plugin info missing") is False
    assert ed.messages == ["plugin info: no such plugin: missing"]




def test_plugin_info_multi_error_target_keeps_count_and_last_detail(tmp_path) -> None:
    root = tmp_path / "plugins"
    root.mkdir()

    b = root / "b"
    b.mkdir()
    (b / "main.mx").write_text(": init ( -- ) ;\n", encoding="utf-8")
    (b / "plugin.json").write_text(json.dumps({"entry": "main.mx", "requires": ["missingdep"]}), encoding="utf-8")

    ed = Editor()
    install_editor_hostcalls(ed)
    pm = PluginManager(ed.vm)
    ed.plugin_manager = pm
    pm.load_tree(root)
    pm.load_errors.append(("b", "secondary issue"))

    ed.messages.clear()
    assert ed.exec_command_line("plugin info b") is True
    assert ed.messages == [
        "plugin info: b [error, deps:missingdep]",
        "  entry: main.mx",
        f"  root: {b}",
        "  requires: 1 (1 missing)",
        "    - missingdep [missing]",
        "  errors: 2 load errors · last: secondary issue",
        "    - missing dependency: missingdep",
        "    - secondary issue",
    ]


def test_plugin_info_loaded_target_keeps_state_witness(tmp_path) -> None:
    root = tmp_path / "plugins"
    root.mkdir()

    a = root / "a"
    a.mkdir()
    (a / "main.mx").write_text(": init ( -- ) ;\n", encoding="utf-8")
    (a / "plugin.json").write_text(json.dumps({"entry": "main.mx", "version": "1.0.0"}), encoding="utf-8")

    ed = Editor()
    install_editor_hostcalls(ed)
    pm = PluginManager(ed.vm)
    ed.plugin_manager = pm
    pm.load_tree(root)

    ed.messages.clear()
    assert ed.exec_command_line("plugin info a") is True
    assert ed.messages == [
        "plugin info: a [loaded, v1.0.0]",
        "  version: 1.0.0",
        "  entry: main.mx",
        f"  root: {a}",
        "  requires: 0",
        "  errors: 0 · loaded plugin",
    ]


def test_plugin_info_available_candidate_keeps_state_witness(tmp_path) -> None:
    root = tmp_path / "plugins"
    root.mkdir()

    optional = root / "optional"
    optional.mkdir()
    (optional / "main.mx").write_text(": init ( -- ) ;\n", encoding="utf-8")
    (optional / "plugin.json").write_text(json.dumps({"entry": "main.mx", "version": "0.2.0"}), encoding="utf-8")

    ed = Editor()
    install_editor_hostcalls(ed)
    pm = PluginManager(ed.vm)
    ed.plugin_manager = pm
    pm.load_tree(root)
    pm.plugins.pop("optional", None)

    ed.messages.clear()
    assert ed.exec_command_line("plugin info optional") is True
    assert ed.messages == [
        "plugin info: optional [available, v0.2.0]",
        "  version: 0.2.0",
        "  entry: main.mx",
        f"  root: {optional}",
        "  requires: 0",
        "  errors: 0 · available plugin · not loaded",
    ]



def test_plugin_errors_available_candidate_keeps_state_witness(tmp_path) -> None:
    root = tmp_path / "plugins"
    root.mkdir()

    optional = root / "optional"
    optional.mkdir()
    (optional / "main.mx").write_text(": init ( -- ) ;\n", encoding="utf-8")
    (optional / "plugin.json").write_text(json.dumps({"entry": "main.mx", "version": "0.2.0"}), encoding="utf-8")

    ed = Editor()
    install_editor_hostcalls(ed)
    pm = PluginManager(ed.vm)
    ed.plugin_manager = pm
    pm.load_tree(root)
    pm.plugins.pop("optional", None)

    ed.messages.clear()
    assert ed.exec_command_line("plugin errors optional") is True
    assert ed.messages == [
        "plugin errors: optional [available, v0.2.0]",
        "  errors: 0 · available plugin · not loaded",
    ]



def test_plugin_info_dependency_counts_include_available_candidates(tmp_path) -> None:
    root = tmp_path / "plugins"
    root.mkdir()

    a = root / "a"
    a.mkdir()
    (a / "main.mx").write_text(": init ( -- ) ;\n", encoding="utf-8")
    (a / "plugin.json").write_text(json.dumps({"entry": "main.mx", "version": "1.0.0"}), encoding="utf-8")

    optional = root / "optional"
    optional.mkdir()
    (optional / "main.mx").write_text(": init ( -- ) ;\n", encoding="utf-8")
    (optional / "plugin.json").write_text(json.dumps({"entry": "main.mx", "version": "0.2.0"}), encoding="utf-8")

    b = root / "b"
    b.mkdir()
    (b / "main.mx").write_text(": init ( -- ) ;\n", encoding="utf-8")
    (b / "plugin.json").write_text(json.dumps({"entry": "main.mx", "requires": ["a", "optional"]}), encoding="utf-8")

    ed = Editor()
    install_editor_hostcalls(ed)
    pm = PluginManager(ed.vm)
    ed.plugin_manager = pm
    pm.load_tree(root)
    pm.plugins.pop("optional", None)

    ed.messages.clear()
    assert ed.exec_command_line("plugin info b") is True
    assert "  requires: 2 (1 loaded, 1 available)" in ed.messages
    assert "    - optional [available, v0.2.0]" in ed.messages

def test_plugin_errors_filtered_starts_with_inventory_summary_and_unknown_plugins_fail_cleanly(tmp_path) -> None:
    root = tmp_path / "plugins"
    root.mkdir()

    a = root / "a"
    a.mkdir()
    (a / "main.mx").write_text(": init ( -- ) ;\n", encoding="utf-8")
    (a / "plugin.json").write_text(json.dumps({"entry": "main.mx", "version": "1.0.0"}), encoding="utf-8")

    b = root / "b"
    b.mkdir()
    (b / "main.mx").write_text(": init ( -- ) ;\n", encoding="utf-8")
    (b / "plugin.json").write_text(json.dumps({"entry": "main.mx", "requires": ["missingdep"]}), encoding="utf-8")

    ed = Editor()
    install_editor_hostcalls(ed)
    pm = PluginManager(ed.vm)
    ed.plugin_manager = pm
    pm.load_tree(root)

    ed.messages.clear()
    assert ed.exec_command_line("plugin errors a") is True
    assert ed.messages == [
        "plugin errors: a [loaded, v1.0.0]",
        "  errors: 0 · loaded plugin",
    ]

    ed.messages.clear()
    assert ed.exec_command_line("plugin errors b") is True
    assert ed.messages == [
        "plugin errors: b [error, deps:missingdep]",
        "  errors: missing dependency: missingdep",
    ]

    ed.messages.clear()
    assert ed.exec_command_line("plugin errors missing") is False
    assert ed.messages == ["plugin errors: no such plugin: missing"]


def test_plugin_errors_filtered_multi_error_target_keeps_count_and_last_detail(tmp_path) -> None:
    root = tmp_path / "plugins"
    root.mkdir()

    b = root / "b"
    b.mkdir()
    (b / "main.mx").write_text(": init ( -- ) ;\n", encoding="utf-8")
    (b / "plugin.json").write_text(json.dumps({"entry": "main.mx", "requires": ["missingdep"]}), encoding="utf-8")

    ed = Editor()
    install_editor_hostcalls(ed)
    pm = PluginManager(ed.vm)
    ed.plugin_manager = pm
    pm.load_tree(root)
    pm.load_errors.append(("b", "secondary issue"))

    ed.messages.clear()
    assert ed.exec_command_line("plugin errors b") is True
    assert ed.messages == [
        "plugin errors: b [error, deps:missingdep]",
        "  errors: 2 load errors · last: secondary issue",
        "    - missing dependency: missingdep",
        "    - secondary issue",
    ]


def test_plugin_errors_unfiltered_empty_is_count_aware(tmp_path) -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.plugin_manager = PluginManager(ed.vm)

    ed.messages.clear()
    assert ed.exec_command_line("plugin errors") is True
    assert ed.messages == ["plugin errors: 0 plugin(s), 0 error(s)"]


def test_plugin_errors_unfiltered_empty_keeps_inventory_witness(tmp_path) -> None:
    root = tmp_path / "plugins"
    root.mkdir()

    a = root / "a"
    a.mkdir()
    (a / "main.mx").write_text(": init ( -- ) ;\n", encoding="utf-8")
    (a / "plugin.json").write_text(json.dumps({"entry": "main.mx", "version": "1.0.0"}), encoding="utf-8")

    ed = Editor()
    install_editor_hostcalls(ed)
    pm = PluginManager(ed.vm)
    ed.plugin_manager = pm
    pm.load_tree(root)

    ed.messages.clear()
    assert ed.exec_command_line("plugin errors") is True
    assert ed.messages == [
        "plugin errors: 0 plugin(s), 0 error(s) · 1 plugin total · e.g. a [loaded, v1.0.0]"
    ]


def test_plugin_errors_unfiltered_groups_by_plugin_inventory_entry(tmp_path) -> None:
    root = tmp_path / "plugins"
    root.mkdir()

    b = root / "b"
    b.mkdir()
    (b / "main.mx").write_text(": init ( -- ) ;\n", encoding="utf-8")
    (b / "plugin.json").write_text(json.dumps({"entry": "main.mx", "requires": ["missingdep"]}), encoding="utf-8")

    c = root / "c"
    c.mkdir()
    (c / "main.mx").write_text(": init ( -- ) ;\n", encoding="utf-8")
    (c / "plugin.json").write_text(json.dumps({"entry": "main.mx", "requires": ["otherdep"]}), encoding="utf-8")

    ed = Editor()
    install_editor_hostcalls(ed)
    pm = PluginManager(ed.vm)
    ed.plugin_manager = pm
    pm.load_tree(root)
    pm.load_errors.append(("b", "secondary issue"))

    ed.messages.clear()
    assert ed.exec_command_line("plugin errors") is True
    assert ed.messages == [
        "plugin errors: 2 plugin(s), 3 error(s)",
        "  - b [error, deps:missingdep] (2 errors)",
        "    - missing dependency: missingdep",
        "    - secondary issue",
        "  - c [error, deps:otherdep] (1 error)",
        "    - missing dependency: otherdep",
    ]


def test_plugin_section_summary_rows_and_showplugins_are_count_aware(tmp_path) -> None:
    root = tmp_path / "plugins"
    root.mkdir()

    for name in ("alpha", "amber"):
        d = root / name
        d.mkdir()
        (d / "main.mx").write_text(": init ( -- ) ;\n", encoding="utf-8")
        (d / "plugin.json").write_text(json.dumps({"entry": "main.mx"}), encoding="utf-8")

    broken = root / "beta"
    broken.mkdir()
    (broken / "main.mx").write_text(": init ( -- ) ;\n", encoding="utf-8")
    (broken / "plugin.json").write_text(json.dumps({"entry": "main.mx", "requires": ["missingdep"]}), encoding="utf-8")

    ed = Editor()
    install_editor_hostcalls(ed)
    pm = PluginManager(ed.vm)
    ed.plugin_manager = pm
    pm.load_tree(root)

    rows = _hostcall(ed, 'ed.plugin-section-summary-rows', '')
    assert rows == [
        ['Errors', 1, 'beta', 'missing dependency: missingdep'],
        ['Loaded', 2, 'alpha', '[loaded]'],
    ]

    loaded_rows = _hostcall(ed, 'ed.plugin-section-summary-rows', 'loaded')
    assert loaded_rows == [
        ['Loaded', 2, 'alpha', '[loaded]'],
    ]

    assert ed.exec_command_line('showplugins') is True
    assert ed.messages == [
        'showplugins: 2 section(s), 3 plugin(s)',
        'Errors: 1 (e.g. beta — missing dependency: missingdep)',
        'Loaded: 2 (e.g. alpha — [loaded])',
    ]

    ed.messages[:] = []
    assert ed.exec_command_line('showplugins loaded') is True
    assert ed.messages == [
        'showplugins loaded: 1 section(s), 2 plugin(s)',
        'Loaded: 2 (e.g. alpha — [loaded])',
    ]


def test_pluginpick_section_counts_track_visible_query_slice(tmp_path) -> None:
    root = tmp_path / "plugins"
    root.mkdir()

    for name in ("alpha", "amber"):
        d = root / name
        d.mkdir()
        (d / "main.mx").write_text(": init ( -- ) ;\n", encoding="utf-8")
        (d / "plugin.json").write_text(json.dumps({"entry": "main.mx"}), encoding="utf-8")

    broken = root / "beta"
    broken.mkdir()
    (broken / "main.mx").write_text(": init ( -- ) ;\n", encoding="utf-8")
    (broken / "plugin.json").write_text(json.dumps({"entry": "main.mx", "requires": ["missingdep"]}), encoding="utf-8")

    ed = Editor()
    install_editor_hostcalls(ed)
    pm = PluginManager(ed.vm)
    ed.plugin_manager = pm
    pm.load_tree(root)

    sections = ed.plugin_section_rows("loaded")
    assert sections == [
        ['Loaded (2)', [
            ['alpha', 'plugin', '[loaded]', ''],
            ['amber', 'plugin', '[loaded]', ''],
        ]],
    ]

    assert ed.exec_command_line("pluginpick loaded") is True
    assert ed.prompt is not None
    assert ed.prompt.kind == "plugin"
    assert ed.prompt_current_section() == "Loaded (2)"
    assert ed.prompt_current_preview().startswith("Loaded (2): alpha [loaded]")
