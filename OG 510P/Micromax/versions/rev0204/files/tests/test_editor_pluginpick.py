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


def test_pluginpick_opens_prompt_and_dispatches_reload_or_info(tmp_path) -> None:
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

    # Picking a loaded plugin triggers reload.
    ed.messages.clear()
    ed.prompt.suggest_index = ed.prompt.suggestions.index("a")
    assert ed.submit_prompt()
    assert ed.messages and ed.messages[-1] == "reloaded a"

    # Picking a non-loaded plugin triggers info.
    ed.exec_command_line("pluginpick")
    assert ed.prompt is not None
    ed.messages.clear()
    ed.prompt.suggest_index = ed.prompt.suggestions.index("b")
    assert ed.submit_prompt()
    assert any(m.startswith("plugin b: not loaded") for m in ed.messages)
    assert any("requires:" in m for m in ed.messages)


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
        ['Errors', [['b', 'plugin', 'not loaded deps:missingdep ERROR', 'missing dependency: missingdep']]],
        ['Loaded', [['a', 'plugin', 'loaded', '']]],
    ]

    assert ed.exec_command_line('pluginpick') is True
    assert ed.prompt is not None
    assert ed.prompt.kind == 'plugin'
    assert ed.prompt_current_section() == 'Errors'
    assert ed.prompt_current_preview().startswith('Errors: b')



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
