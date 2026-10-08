from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from micromax_editor.editor import Editor
from micromax_editor.micromax_bridge import install_editor_hostcalls
from micromax_editor.plugins import PluginManager


def _manager() -> tuple[Editor, PluginManager]:
    ed = Editor()
    install_editor_hostcalls(ed)
    pm = PluginManager(ed.vm)
    ed.plugin_manager = pm
    return ed, pm


@pytest.mark.skipif(not hasattr(os, "symlink"), reason="symlink support required")
def test_plugin_entry_symlink_escape_is_not_loaded(tmp_path: Path) -> None:
    root = tmp_path / "plugins"
    root.mkdir()
    outside = tmp_path / "outside.mx"
    outside.write_text(': outsideword "outside" ;\n', encoding="utf-8")

    plug = root / "escape"
    plug.mkdir()
    (plug / "plugin.json").write_text(json.dumps({"entry": "init.mx"}), encoding="utf-8")
    os.symlink(outside, plug / "init.mx")

    ed, pm = _manager()
    loaded = pm.load_tree(root)

    assert loaded == []
    assert "escape" not in pm.plugins
    assert any(name == "escape" and "outside" in err.lower() for name, err in pm.load_errors)
    with pytest.raises(Exception):
        ed.vm.eval("use escape outsideword", filename="<test>")


@pytest.mark.skipif(not hasattr(os, "symlink"), reason="symlink support required")
def test_plugin_json_symlink_escape_is_not_read(tmp_path: Path) -> None:
    root = tmp_path / "plugins"
    root.mkdir()
    outside_meta = tmp_path / "plugin.json"
    outside_meta.write_text(json.dumps({"name": "escape", "entry": "init.mx"}), encoding="utf-8")

    plug = root / "escape"
    plug.mkdir()
    (plug / "init.mx").write_text(': okword "ok" ;\n', encoding="utf-8")
    os.symlink(outside_meta, plug / "plugin.json")

    _ed, pm = _manager()
    loaded = pm.load_tree(root)

    assert loaded == []
    assert "escape" not in pm.plugins
    assert any(name == "escape" and "outside" in err.lower() for name, err in pm.load_errors)


@pytest.mark.skipif(not hasattr(os, "symlink"), reason="symlink support required")
def test_plugin_directory_symlink_escape_is_skipped(tmp_path: Path) -> None:
    root = tmp_path / "plugins"
    root.mkdir()
    outside_dir = tmp_path / "outside-plugin"
    outside_dir.mkdir()
    (outside_dir / "init.mx").write_text(': outsideword "outside" ;\n', encoding="utf-8")
    os.symlink(outside_dir, root / "escape")

    _ed, pm = _manager()
    loaded = pm.load_tree(root)

    assert loaded == []
    assert "escape" not in pm.plugins
    assert any(name == "escape" and "outside plugin root" in err for name, err in pm.load_errors)


def test_plugin_source_cannot_self_enable_capability_option(tmp_path: Path) -> None:
    root = tmp_path / "plugins"
    root.mkdir()
    plug = root / "caps"
    plug.mkdir()
    (plug / "init.mx").write_text('set cap.fs-save true\n', encoding="utf-8")

    ed, pm = _manager()
    loaded = pm.load_tree(root)

    assert loaded == []
    assert not bool(ed.options.get("cap.fs-save"))
    assert any(name == "caps" and "cannot modify capability option" in err for name, err in pm.load_errors)


def test_plugin_lifecycle_cannot_self_enable_capability_option(tmp_path: Path) -> None:
    root = tmp_path / "plugins"
    root.mkdir()
    plug = root / "caps"
    plug.mkdir()
    (plug / "init.mx").write_text(': init set cap.fs-save true ;\n', encoding="utf-8")

    ed, pm = _manager()
    loaded = pm.load_tree(root)

    assert loaded == []
    assert not bool(ed.options.get("cap.fs-save"))
    assert any(name == "caps" and "cannot modify capability option" in err for name, err in pm.load_errors)


def test_plugin_lifecycle_can_use_safe_hostcall_without_granting_itself(tmp_path: Path) -> None:
    root = tmp_path / "plugins"
    root.mkdir()
    plug = root / "msg"
    plug.mkdir()
    (plug / "init.mx").write_text(': init "plugin ready" "ed.msg" hostcall ;\n', encoding="utf-8")

    ed, pm = _manager()
    assert pm.load_tree(root)

    assert ed.messages == ["plugin ready"]
    assert "msg" in pm.plugins


def test_nested_plugin_entry_keeps_plugin_root_for_reload_and_package_include(tmp_path: Path) -> None:
    root = tmp_path / "plugins"
    root.mkdir()
    plug = root / "nested"
    src = plug / "src"
    src.mkdir(parents=True)
    (src / "main.mx").write_text('"../helper.mx" include\n: nword helper-word ;\n', encoding="utf-8")
    (plug / "helper.mx").write_text(': helper-word "one" ;\n', encoding="utf-8")
    (plug / "plugin.json").write_text(json.dumps({"entry": "src/main.mx"}), encoding="utf-8")

    ed, pm = _manager()
    loaded = pm.load_tree(root)

    assert [p.name for p in loaded] == ["nested"]
    assert pm.plugins["nested"].root == plug.resolve()
    ed.vm.eval("use nested nword", filename="<test>")
    assert ed.vm.stack.pop() == "one"

    (plug / "helper.mx").write_text(': helper-word "two" ;\n', encoding="utf-8")
    pm.reload("nested")
    ed.vm.eval("use nested nword", filename="<test>")
    assert ed.vm.stack.pop() == "two"


def test_plugin_source_can_include_package_local_helper_without_global_require_cap(tmp_path: Path) -> None:
    root = tmp_path / "plugins"
    root.mkdir()
    plug = root / "split"
    plug.mkdir()
    (plug / "init.mx").write_text('"helper.mx" include\n', encoding="utf-8")
    (plug / "helper.mx").write_text(': splitword "split-ok" ;\n', encoding="utf-8")

    ed, pm = _manager()
    assert not bool(ed.options.get("cap.fs-require"))
    loaded = pm.load_tree(root)

    assert [p.name for p in loaded] == ["split"]
    ed.vm.eval("use split splitword", filename="<test>")
    assert ed.vm.stack.pop() == "split-ok"


@pytest.mark.skipif(not hasattr(os, "symlink"), reason="symlink support required")
def test_plugin_private_include_refuses_symlink_escape_without_global_require_cap(tmp_path: Path) -> None:
    root = tmp_path / "plugins"
    root.mkdir()
    outside = tmp_path / "outside.mx"
    outside.write_text(': outsideword "outside" ;\n', encoding="utf-8")

    plug = root / "split"
    plug.mkdir()
    (plug / "init.mx").write_text('"helper.mx" include\n', encoding="utf-8")
    os.symlink(outside, plug / "helper.mx")

    ed, pm = _manager()
    loaded = pm.load_tree(root)

    assert loaded == []
    assert "split" not in pm.plugins
    assert any(name == "split" and "outside" in err.lower() for name, err in pm.load_errors)
    with pytest.raises(Exception):
        ed.vm.eval("use split outsideword", filename="<test>")


def test_plugin_command_cannot_self_enable_capability_option(tmp_path: Path) -> None:
    root = tmp_path / "plugins"
    root.mkdir()
    plug = root / "cmdcap"
    plug.mkdir()
    (plug / "init.mx").write_text(
        ': grant drop set cap.fs-save true 1 ;\n'
        "' grant \"grantcap\" \"try cap grant\" \"ed.cmd-add\" hostcall drop\n",
        encoding="utf-8",
    )

    ed, pm = _manager()
    assert pm.load_tree(root)
    assert not bool(ed.options.get("cap.fs-save"))

    assert ed.exec_command_line("grantcap") is False
    assert not bool(ed.options.get("cap.fs-save"))
    assert any("cannot modify capability option" in msg for msg in ed.messages)


def test_plugin_command_can_include_package_local_helper_without_global_require_cap(tmp_path: Path) -> None:
    root = tmp_path / "plugins"
    root.mkdir()
    plug = root / "cmdsplit"
    plug.mkdir()
    (plug / "init.mx").write_text(
        ': run drop "helper.mx" include helper-msg "ed.msg" hostcall 1 ;\n'
        "' run \"cmdsplit\" \"include helper\" \"ed.cmd-add\" hostcall drop\n",
        encoding="utf-8",
    )
    (plug / "helper.mx").write_text(': helper-msg "cmd-helper" ;\n', encoding="utf-8")

    ed, pm = _manager()
    assert not bool(ed.options.get("cap.fs-require"))
    assert pm.load_tree(root)

    assert ed.exec_command_line("cmdsplit") is True
    assert ed.messages[-1] == "cmd-helper"


def test_plugin_keybinding_cannot_self_enable_capability_option(tmp_path: Path) -> None:
    root = tmp_path / "plugins"
    root.mkdir()
    plug = root / "keycap"
    plug.mkdir()
    (plug / "init.mx").write_text(
        '"F6" "command:set cap.fs-save true" "ed.bind" hostcall\n',
        encoding="utf-8",
    )

    ed, pm = _manager()
    assert pm.load_tree(root)

    binding = ed.keymap.get_binding("F6")
    assert binding is not None
    assert binding.script_context is True
    assert binding.group == "plugin:keycap"

    assert ed.dispatch_key("F6") is False
    assert not bool(ed.options.get("cap.fs-save"))
    assert any("cannot modify capability option" in msg for msg in ed.messages)


def test_plugin_keybinding_keeps_package_local_include_root(tmp_path: Path) -> None:
    root = tmp_path / "plugins"
    root.mkdir()
    plug = root / "keysplit"
    plug.mkdir()
    (plug / "init.mx").write_text(
        ': runhelper "helper.mx" include helper-msg "ed.msg" hostcall 1 ;\n'
        '"F7" "mx:use keysplit runhelper" "ed.bind" hostcall\n',
        encoding="utf-8",
    )
    (plug / "helper.mx").write_text(': helper-msg "key-helper" ;\n', encoding="utf-8")

    ed, pm = _manager()
    assert not bool(ed.options.get("cap.fs-require"))
    assert pm.load_tree(root)

    binding = ed.keymap.get_binding("F7")
    assert binding is not None
    assert binding.script_context is True
    assert binding.plugin_load_root and Path(binding.plugin_load_root).resolve() == plug.resolve()

    assert ed.dispatch_key("F7") is True
    assert ed.messages[-1] == "key-helper"


def test_plugin_timer_keeps_package_load_root_without_global_require_cap(tmp_path: Path) -> None:
    root = tmp_path / "plugins"
    root.mkdir()
    plug = root / "timersplit"
    plug.mkdir()
    (plug / "init.mx").write_text(
        '0 [ "helper.mx" include helper-msg "ed.msg" hostcall ] "ed.after" hostcall drop\n',
        encoding="utf-8",
    )
    (plug / "helper.mx").write_text(': helper-msg "timer-helper" ;\n', encoding="utf-8")

    ed, pm = _manager()
    assert not bool(ed.options.get("cap.fs-require"))
    assert pm.load_tree(root)

    assert ed.pump_timers() == 1
    assert ed.messages[-1] == "timer-helper"


def test_plugin_hook_keeps_package_load_root_without_global_require_cap(tmp_path: Path) -> None:
    root = tmp_path / "plugins"
    root.mkdir()
    plug = root / "hooksplit"
    plug.mkdir()
    (plug / "init.mx").write_text(
        ': hookrun 2drop "helper.mx" include helper-msg "ed.msg" hostcall ;\n'
        "' hookrun hook-add ed.on-action\n",
        encoding="utf-8",
    )
    (plug / "helper.mx").write_text(': helper-msg "hook-helper" ;\n', encoding="utf-8")

    ed, pm = _manager()
    assert not bool(ed.options.get("cap.fs-require"))
    assert pm.load_tree(root)

    ed.run_action("Noop")
    assert ed.messages[-1] == "hook-helper"


def test_plugin_keybinding_runs_in_plugin_wordlist_and_keeps_include_defs_private(tmp_path: Path) -> None:
    root = tmp_path / "plugins"
    root.mkdir()
    plug = root / "keyns"
    plug.mkdir()
    (plug / "init.mx").write_text(
        ': runhelper "helper.mx" include helper-msg "ed.msg" hostcall 1 ;\n'
        '"F8" "mx:runhelper" "ed.bind" hostcall\n',
        encoding="utf-8",
    )
    (plug / "helper.mx").write_text(': helper-msg "key-private" ;\n', encoding="utf-8")

    ed, pm = _manager()
    assert not bool(ed.options.get("cap.fs-require"))
    assert pm.load_tree(root)
    plugin = pm.plugins["keyns"]

    assert "helper-msg" not in ed.vm.wordlists[ed.vm.forth_wid]
    assert ed.dispatch_key("F8") is True
    assert ed.messages[-1] == "key-private"
    assert "helper-msg" in ed.vm.wordlists[plugin.wid]
    assert "helper-msg" not in ed.vm.wordlists[ed.vm.forth_wid]


def test_plugin_command_callback_include_defs_stay_in_plugin_wordlist(tmp_path: Path) -> None:
    root = tmp_path / "plugins"
    root.mkdir()
    plug = root / "cmdns"
    plug.mkdir()
    (plug / "init.mx").write_text(
        ': run drop "helper.mx" include helper-msg "ed.msg" hostcall 1 ;\n'
        "' run \"cmdns\" \"include helper\" \"ed.cmd-add\" hostcall drop\n",
        encoding="utf-8",
    )
    (plug / "helper.mx").write_text(': helper-msg "cmd-private" ;\n', encoding="utf-8")

    ed, pm = _manager()
    assert pm.load_tree(root)
    plugin = pm.plugins["cmdns"]

    assert ed.exec_command_line("cmdns") is True
    assert ed.messages[-1] == "cmd-private"
    assert "helper-msg" in ed.vm.wordlists[plugin.wid]
    assert "helper-msg" not in ed.vm.wordlists[ed.vm.forth_wid]


def test_plugin_timer_callback_include_defs_stay_in_plugin_wordlist(tmp_path: Path) -> None:
    root = tmp_path / "plugins"
    root.mkdir()
    plug = root / "timerns"
    plug.mkdir()
    (plug / "init.mx").write_text(
        '0 [ "helper.mx" include helper-msg "ed.msg" hostcall ] "ed.after" hostcall drop\n',
        encoding="utf-8",
    )
    (plug / "helper.mx").write_text(': helper-msg "timer-private" ;\n', encoding="utf-8")

    ed, pm = _manager()
    assert pm.load_tree(root)
    plugin = pm.plugins["timerns"]

    assert ed.pump_timers() == 1
    assert ed.messages[-1] == "timer-private"
    assert "helper-msg" in ed.vm.wordlists[plugin.wid]
    assert "helper-msg" not in ed.vm.wordlists[ed.vm.forth_wid]


def test_stale_plugin_callback_root_is_not_honored_after_unload(tmp_path: Path) -> None:
    plug = tmp_path / "gone"
    plug.mkdir()
    (plug / "helper.mx").write_text(': stale-helper "should-not-load" ;\n', encoding="utf-8")

    ed, pm = _manager()
    # The plugin manager exists, but no loaded plugin owns this root anymore.
    assert pm.plugins == {}

    with ed.plugin_callback_context(str(plug), "plugin:gone"):
        with ed.script_context():
            with pytest.raises(Exception) as excinfo:
                ed.vm.eval('"helper.mx" include', filename="<stale-callback>")

    assert "cap.fs-require" in str(excinfo.value)
    assert "stale-helper" not in ed.vm.wordlists[ed.vm.forth_wid]


def test_failed_plugin_key_callback_rolls_back_partial_include_definitions(tmp_path: Path) -> None:
    root = tmp_path / "plugins"
    root.mkdir()
    plug = root / "keyrollback"
    plug.mkdir()
    (plug / "init.mx").write_text(
        ': run "helper.mx" include 1 ;\n'
        '"F10" "mx:run" "ed.bind" hostcall\n',
        encoding="utf-8",
    )
    (plug / "helper.mx").write_text(
        ': half-loaded "should-not-survive" ;\n'
        'missing-word-after-partial-define\n',
        encoding="utf-8",
    )

    ed, pm = _manager()
    assert pm.load_tree(root)
    plugin = pm.plugins["keyrollback"]
    assert "half-loaded" not in ed.vm.wordlists[plugin.wid]

    assert ed.dispatch_key("F10") is False

    assert "half-loaded" not in ed.vm.wordlists[plugin.wid]
    assert "half-loaded" not in ed.vm.wordlists[ed.vm.forth_wid]


def test_failed_plugin_command_callback_rolls_back_runtime_registrations(tmp_path: Path) -> None:
    root = tmp_path / "plugins"
    root.mkdir()
    plug = root / "cmdrollback"
    plug.mkdir()
    (plug / "init.mx").write_text(
        ': run drop "helper.mx" include 1 ;\n'
        "' run \"cmdrollback\" \"fail after partial register\" \"ed.cmd-add\" hostcall drop\n",
        encoding="utf-8",
    )
    (plug / "helper.mx").write_text(
        ': half-command "should-not-survive" ;\n'
        '"F11" "command:noop" "ed.bind" hostcall drop\n'
        ': tempcmd drop 1 ;\n'
        "' tempcmd \"tempplugin\" \"temporary command\" \"ed.cmd-add\" hostcall drop\n"
        'missing-word-after-registration\n',
        encoding="utf-8",
    )

    ed, pm = _manager()
    assert pm.load_tree(root)
    plugin = pm.plugins["cmdrollback"]
    assert ed.keymap.get_binding("F11") is None
    assert "tempplugin" not in ed.command_dispatcher.names()

    assert ed.exec_command_line("cmdrollback") is False

    assert ed.keymap.get_binding("F11") is None
    assert "tempplugin" not in ed.command_dispatcher.names()
    assert "half-command" not in ed.vm.wordlists[plugin.wid]



def test_plugin_delayed_callbacks_receive_only_declared_stack_inputs(
    tmp_path: Path,
) -> None:
    root = tmp_path / "plugins"
    root.mkdir()
    plug = root / "callbackstack"
    plug.mkdir()
    (plug / "init.mx").write_text(
        """
        : report-stack ( label -- )
          depth 1 = [ "-stack-clean" ] [ "-stack-leak" ] if s+ "ed.msg" hostcall
        ;
        : report-local ( label -- )
          [ ambient-local drop ] catch 0 =
            [ "-local-leak" ] [ "-local-clean" ] if s+ "ed.msg" hostcall
        ;
        : command-run ( args -- ok )
          drop "command" report-stack "command" report-local 1
        ;
        : timer-run ( -- )
          "timer" report-stack "timer" report-local
        ;
        : hook-run ( action ok -- )
          2drop "hook" report-stack "hook" report-local
        ;
        : key-run ( -- )
          "key" report-stack "key" report-local
        ;
        ' command-run "isolated-command" "isolated command" "ed.cmd-add" hostcall drop
        0 [ timer-run ] "ed.after" hostcall drop
        ' hook-run hook-add ed.on-action
        "F12" "mx:key-run" "ed.bind" hostcall
        """,
        encoding="utf-8",
    )

    ed, pm = _manager()
    assert [plugin.name for plugin in pm.load_tree(root)] == ["callbackstack"]
    ed.messages.clear()

    marker = ["sensitive-stack-value"]
    local_frame = ed.vm.locals_stack[0]
    ed.vm.stack[:] = [marker]
    local_frame["ambient-local"] = "sensitive-local-value"

    assert ed.exec_command_line("isolated-command") is True
    assert ed.messages == ["command-stack-clean", "command-local-clean"]

    ed.messages.clear()
    assert ed.pump_timers() == 1
    assert ed.messages == ["timer-stack-clean", "timer-local-clean"]

    ed.messages.clear()
    assert ed.run_action("Noop") is False
    assert ed.messages == ["hook-stack-clean", "hook-local-clean"]

    ed.messages.clear()
    assert ed.dispatch_key("F12") is True
    assert ed.messages == ["key-stack-clean", "key-local-clean"]

    assert ed.vm.stack == [marker]
    assert ed.vm.stack[0] is marker
    assert ed.vm.locals_stack == [local_frame]
    assert ed.vm.locals_stack[0] is local_frame
    assert local_frame == {"ambient-local": "sensitive-local-value"}

def test_failed_plugin_command_callback_restores_mutable_stack_values(tmp_path: Path) -> None:
    root = tmp_path / "plugins"
    root.mkdir()
    plug = root / "cmdstack"
    plug.mkdir()
    (plug / "init.mx").write_text(
        ': run drop "evil" swap push drop missing-after-stack-mutation ;\n'
        "' run \"cmdstack\" \"mutate stack then fail\" \"ed.cmd-add\" hostcall drop\n",
        encoding="utf-8",
    )

    ed, pm = _manager()
    assert pm.load_tree(root)

    ed.vm.stack[:] = [["safe"]]
    assert ed.exec_command_line("cmdstack") is False

    assert ed.vm.stack == [["safe"]]


def test_false_plugin_command_callback_rolls_back_lazy_include_side_effects(tmp_path: Path) -> None:
    root = tmp_path / "plugins"
    root.mkdir()
    plug = root / "cmdfalse"
    plug.mkdir()
    (plug / "init.mx").write_text(
        ': run drop "helper.mx" include 0 ;\n'
        "' run \"cmdfalse\" \"return false after lazy include\" \"ed.cmd-add\" hostcall drop\n",
        encoding="utf-8",
    )
    (plug / "helper.mx").write_text(
        ': half-false "should-not-survive" ;\n'
        ': tempfalse drop 1 ;\n'
        "' tempfalse \"tempfalse\" \"temporary false command\" \"ed.cmd-add\" hostcall drop\n",
        encoding="utf-8",
    )

    ed, pm = _manager()
    assert pm.load_tree(root)
    plugin = pm.plugins["cmdfalse"]

    assert ed.exec_command_line("cmdfalse") is False

    assert "half-false" not in ed.vm.wordlists[plugin.wid]
    assert "tempfalse" not in ed.command_dispatcher.names()


def test_script_spoofed_plugin_group_does_not_grant_plugin_callback_root(tmp_path: Path) -> None:
    root = tmp_path / "plugins"
    root.mkdir()
    plug = root / "victim"
    plug.mkdir()
    (plug / "init.mx").write_text(': victim-ready "ready" ;\n', encoding="utf-8")
    (plug / "helper.mx").write_text(': spoof-msg "spoofed-root" ;\n', encoding="utf-8")

    ed, pm = _manager()
    assert pm.load_tree(root)
    assert not bool(ed.options.get("cap.fs-require"))

    # Simulate a stale/malicious registration row that carries a plugin:* group
    # but no captured package root.  The group is cleanup/provenance metadata;
    # it must not be enough to regain package-local include authority later.
    ed.keymap.bind(
        "F13",
        'mx:"helper.mx" include spoof-msg "ed.msg" hostcall',
        group="plugin:victim",
        script_context=True,
    )

    assert ed.dispatch_key("F13") is False
    assert "spoofed-root" not in ed.messages
    assert "spoof-msg" not in ed.vm.wordlists[pm.plugins["victim"].wid]
    assert any("cap.fs-require" in str(msg) for msg in ed.messages)


def test_script_cannot_assign_reserved_editor_plugin_group(tmp_path: Path) -> None:
    root = tmp_path / "plugins"
    root.mkdir()
    plug = root / "victim"
    plug.mkdir()
    (plug / "init.mx").write_text(': victim-ready "ready" ;\n', encoding="utf-8")

    ed, pm = _manager()
    assert pm.load_tree(root)

    with ed.script_context():
        ed.vm.stack.append("plugin:victim")
        ed.vm.stack.append("ed.group!")
        with pytest.raises(Exception) as excinfo:
            ed.vm.eval("hostcall", filename="<script>")

    assert "reserved editor group" in str(excinfo.value)
    assert ed.vm.current_editor_group is None


def test_script_cannot_assign_reserved_hook_plugin_group(tmp_path: Path) -> None:
    root = tmp_path / "plugins"
    root.mkdir()
    plug = root / "victim"
    plug.mkdir()
    (plug / "init.mx").write_text(': victim-ready "ready" ;\n', encoding="utf-8")

    ed, pm = _manager()
    assert pm.load_tree(root)

    with ed.script_context():
        with pytest.raises(Exception) as excinfo:
            ed.vm.eval('"plugin:victim" hook-group!', filename="<script>")

    assert "reserved hook group" in str(excinfo.value)
    assert ed.vm.current_hook_group is None


def test_mismatched_plugin_root_and_group_do_not_borrow_either_plugin_context(tmp_path: Path) -> None:
    root = tmp_path / "plugins"
    root.mkdir()
    plug_a = root / "alpha"
    plug_b = root / "bravo"
    plug_a.mkdir()
    plug_b.mkdir()
    (plug_a / "init.mx").write_text(': alpha-ready "ready" ;\n', encoding="utf-8")
    (plug_b / "init.mx").write_text(': bravo-ready "ready" ;\n', encoding="utf-8")
    (plug_a / "helper.mx").write_text(': alpha-helper "alpha" ;\n', encoding="utf-8")

    ed, pm = _manager()
    assert pm.load_tree(root)
    assert not bool(ed.options.get("cap.fs-require"))

    ed.keymap.bind(
        "F14",
        'mx:"helper.mx" include alpha-helper "ed.msg" hostcall',
        group="plugin:bravo",
        script_context=True,
        plugin_load_root=str(plug_a),
    )

    assert ed.dispatch_key("F14") is False
    assert "alpha" not in ed.messages
    assert "alpha-helper" not in ed.vm.wordlists[pm.plugins["alpha"].wid]
    assert "alpha-helper" not in ed.vm.wordlists[pm.plugins["bravo"].wid]
    assert any("cap.fs-require" in str(msg) for msg in ed.messages)


def test_plugin_callback_root_requires_current_generation_after_reload(tmp_path: Path) -> None:
    root = tmp_path / "plugins"
    root.mkdir()
    plug = root / "regen"
    plug.mkdir()
    (plug / "init.mx").write_text(': ready "v1" ;\n', encoding="utf-8")
    (plug / "helper.mx").write_text(': helper-msg "old-helper" ;\n', encoding="utf-8")

    ed, pm = _manager()
    assert pm.load_tree(root)
    old = pm.plugins["regen"]
    old_generation = int(old.generation)
    assert old_generation > 0

    (plug / "init.mx").write_text(': ready "v2" ;\n', encoding="utf-8")
    (plug / "helper.mx").write_text(': helper-msg "new-helper" ;\n', encoding="utf-8")
    reloaded = pm.reload("regen")
    assert int(reloaded.generation) != old_generation
    assert not bool(ed.options.get("cap.fs-require"))

    with ed.plugin_callback_context(
        str(plug),
        "plugin:regen",
        plugin_generation=old_generation,
    ):
        with ed.script_context():
            with pytest.raises(Exception) as excinfo:
                ed.vm.eval('"helper.mx" include helper-msg "ed.msg" hostcall', filename="<stale-generation>")

    assert "cap.fs-require" in str(excinfo.value)
    assert "old-helper" not in ed.messages
    assert "new-helper" not in ed.messages
    assert "helper-msg" not in ed.vm.wordlists[reloaded.wid]

    with ed.plugin_callback_context(
        str(plug),
        "plugin:regen",
        plugin_generation=reloaded.generation,
    ):
        with ed.script_context():
            ed.vm.eval('"helper.mx" include helper-msg "ed.msg" hostcall', filename="<current-generation>")

    assert ed.messages[-1] == "new-helper"
    assert "helper-msg" in ed.vm.wordlists[reloaded.wid]


def test_plugin_keybinding_records_generation_for_deferred_authority(tmp_path: Path) -> None:
    root = tmp_path / "plugins"
    root.mkdir()
    plug = root / "keygen"
    plug.mkdir()
    (plug / "init.mx").write_text(
        ': runhelper "helper.mx" include helper-msg "ed.msg" hostcall 1 ;\n'
        '"F15" "mx:runhelper" "ed.bind" hostcall\n',
        encoding="utf-8",
    )
    (plug / "helper.mx").write_text(': helper-msg "keygen-helper" ;\n', encoding="utf-8")

    ed, pm = _manager()
    assert pm.load_tree(root)
    plugin = pm.plugins["keygen"]
    binding = ed.keymap.get_binding("F15")

    assert binding is not None
    assert binding.plugin_load_root and Path(binding.plugin_load_root).resolve() == plug.resolve()
    assert int(binding.plugin_generation or 0) == int(plugin.generation)
    assert ed.dispatch_key("F15") is True
    assert ed.messages[-1] == "keygen-helper"


def test_failed_plugin_command_callback_rolls_back_prompt_history(tmp_path: Path) -> None:
    root = tmp_path / "plugins"
    root.mkdir()
    plug = root / "cmdhistoryrollback"
    plug.mkdir()
    (plug / "init.mx").write_text(
        ': run drop "help" "ed.command" hostcall drop missing-after-history ;\n'
        "' run \"cmdhistoryrollback\" \"fail after history write\" \"ed.cmd-add\" hostcall drop\n",
        encoding="utf-8",
    )

    ed, pm = _manager()
    assert pm.load_tree(root)
    assert ed.history.get("command", []) == []

    assert ed.exec_command_line("cmdhistoryrollback") is False

    assert ed.history.get("command", []) == ["cmdhistoryrollback"]
    assert "help" not in ed.history.get("command", [])

def test_failed_plugin_command_callback_rolls_back_qreplace_capture_state(tmp_path: Path) -> None:
    root = tmp_path / "plugins"
    root.mkdir()
    plug = root / "qrollback"
    plug.mkdir()
    (plug / "init.mx").write_text(
        ': run drop "qreplace one X -l" "ed.command" hostcall drop 0 ;\n'
        "' run \"qrollback\" \"start qreplace then fail\" \"ed.cmd-add\" hostcall drop\n",
        encoding="utf-8",
    )

    ed, pm = _manager()
    ed.new_buffer("main", "one one")
    assert pm.load_tree(root)

    assert ed.exec_command_line("qrollback") is False

    assert ed.qreplace is None
    assert ed.current_capture_key_mode() is None
    assert ed.key_mode_stack == []
    assert ed.cur().buf.get_text() == "one one"
    assert ed.selection_text() == ""


def test_failed_plugin_command_callback_rolls_back_prompt_capture_state(tmp_path: Path) -> None:
    root = tmp_path / "plugins"
    root.mkdir()
    plug = root / "promptrollback"
    plug.mkdir()
    (plug / "init.mx").write_text(
        ': run drop "help" "ed.command-edit" hostcall 0 ;\n'
        "' run \"promptrollback\" \"open prompt then fail\" \"ed.cmd-add\" hostcall drop\n",
        encoding="utf-8",
    )

    ed, pm = _manager()
    assert pm.load_tree(root)

    assert ed.exec_command_line("promptrollback") is False

    assert ed.prompt is None
    assert ed.current_capture_key_mode() is None
    assert ed.key_mode_stack == []


def test_plugin_cannot_clear_editor_group_to_escape_unload_cleanup(tmp_path: Path) -> None:
    root = tmp_path / "plugins"
    root.mkdir()
    plug = root / "leaker"
    plug.mkdir()
    (plug / "init.mx").write_text(
        "\n".join(
            [
                ': leaked-cmd ( args -- ok ) drop "leaked" "ed.msg" hostcall 1 ;',
                ': init',
                '  0 "ed.group!" hostcall',
                '  \' leaked-cmd "leaked" "leaked command" "ed.cmd-add" hostcall drop',
                ';',
            ]
        ),
        encoding="utf-8",
    )

    ed, pm = _manager()
    assert pm.load_tree(root) == []

    assert "leaker" not in pm.plugins
    assert ed.command_dispatcher.get("leaked") is None
    assert any(
        name == "leaker" and "cannot clear plugin editor group" in err
        for name, err in pm.load_errors
    )


def test_plugin_cannot_assign_ordinary_editor_group_to_escape_unload_cleanup(tmp_path: Path) -> None:
    root = tmp_path / "plugins"
    root.mkdir()
    plug = root / "leaker"
    plug.mkdir()
    (plug / "init.mx").write_text(
        "\n".join(
            [
                ': leaked-cmd ( args -- ok ) drop "leaked" "ed.msg" hostcall 1 ;',
                ': init',
                '  "loose" "ed.group!" hostcall',
                '  \' leaked-cmd "leaked" "leaked command" "ed.cmd-add" hostcall drop',
                ';',
            ]
        ),
        encoding="utf-8",
    )

    ed, pm = _manager()
    assert pm.load_tree(root) == []

    assert "leaker" not in pm.plugins
    assert ed.command_dispatcher.get("leaked") is None
    assert any(
        name == "leaker" and "cannot change plugin editor group" in err
        for name, err in pm.load_errors
    )


def test_plugin_cannot_clear_or_reassign_hook_group_to_escape_unload_cleanup(tmp_path: Path) -> None:
    root = tmp_path / "plugins"
    root.mkdir()
    plug = root / "leaker"
    plug.mkdir()
    (plug / "init.mx").write_text(
        "\n".join(
            [
                "hook leaky-hook",
                ": leaked-hook ( -- ) ;",
                ": init",
                "  0 hook-group!",
                "  ' leaked-hook hook-add leaky-hook",
                ";",
            ]
        ),
        encoding="utf-8",
    )

    ed, pm = _manager()
    assert pm.load_tree(root) == []

    assert "leaker" not in pm.plugins
    assert any(
        name == "leaker" and "cannot clear plugin hook group" in err
        for name, err in pm.load_errors
    )
    with pytest.raises(Exception) as excinfo:
        ed.vm.eval("hook-detail leaky-hook", filename="<test>")
    assert "Expected hook word" in str(excinfo.value)

    pm.clear_load_errors()
    (plug / "init.mx").write_text(
        "\n".join(
            [
                "hook leaky-hook",
                ": leaked-hook ( -- ) ;",
                ": init",
                "  \"loose\" hook-group!",
                "  ' leaked-hook hook-add leaky-hook",
                ";",
            ]
        ),
        encoding="utf-8",
    )

    assert pm.load_tree(root) == []
    assert "leaker" not in pm.plugins
    assert any(
        name == "leaker" and "cannot change plugin hook group" in err
        for name, err in pm.load_errors
    )
    with pytest.raises(Exception) as excinfo:
        ed.vm.eval("hook-detail leaky-hook", filename="<test>")
    assert "Expected hook word" in str(excinfo.value)


def test_plugin_unload_clears_plugin_owned_active_keymode(tmp_path: Path) -> None:
    root = tmp_path / "plugins"
    root.mkdir()
    plug = root / "modal"
    plug.mkdir()
    (plug / "init.mx").write_text(
        ': init "pluginmode" "ed.keymode!" hostcall ;\n',
        encoding="utf-8",
    )

    ed, pm = _manager()
    assert pm.load_tree(root)
    assert ed.current_key_mode() == "pluginmode"
    assert ed.key_mode_stack[-1].group == "plugin:modal"

    pm.unload("modal")

    assert ed.current_key_mode() is None
    assert ed.key_mode_stack == []


def test_plugin_reload_retags_active_keymode_so_later_unload_cleans_it(tmp_path: Path) -> None:
    root = tmp_path / "plugins"
    root.mkdir()
    plug = root / "modal"
    plug.mkdir()
    (plug / "init.mx").write_text(
        ': modal-word "one" ;\n'
        ': init "pluginmode" "ed.keymode!" hostcall ;\n',
        encoding="utf-8",
    )

    ed, pm = _manager()
    assert pm.load_tree(root)
    (plug / "init.mx").write_text(
        ': modal-word "two" ;\n'
        ': init "pluginmode" "ed.keymode!" hostcall ;\n',
        encoding="utf-8",
    )
    pm.reload("modal")

    assert ed.current_key_mode() == "pluginmode"
    assert ed.key_mode_stack[-1].group == "plugin:modal"
    pm.unload("modal")

    assert ed.current_key_mode() is None
    assert ed.key_mode_stack == []


def test_plugin_unload_closes_plugin_owned_prompt_and_qreplace(tmp_path: Path) -> None:
    root = tmp_path / "plugins"
    root.mkdir()
    plug = root / "interactive"
    plug.mkdir()
    (plug / "init.mx").write_text(
        ': init "seed" "ed.command-edit" hostcall ;\n',
        encoding="utf-8",
    )

    ed, pm = _manager()
    assert pm.load_tree(root)
    assert ed.prompt is not None
    assert ed.prompt.group == "plugin:interactive"

    pm.unload("interactive")

    assert ed.prompt is None
    assert "prompt" not in ed.active_key_modes()

    plug2 = root / "qmodal"
    plug2.mkdir()
    (plug2 / "init.mx").write_text(
        ': init "qreplace one two -l" "ed.command" hostcall drop ;\n',
        encoding="utf-8",
    )

    ed.new_buffer("main", "one one")
    assert pm.load_tree(root)
    assert ed.qreplace is not None
    assert ed.qreplace.authority.group == "plugin:qmodal"
    assert "qreplace" in ed.active_key_modes()

    pm.unload("qmodal")

    assert ed.qreplace is None
    assert "qreplace" not in ed.active_key_modes()
    assert ed.selection_text() == ""


def _recovery_init_source() -> str:
    return ': init "ed.push-selections" hostcall "ed.push-jump" hostcall drop ;\n'


def test_plugin_unload_removes_plugin_owned_selection_and_jump_recovery(tmp_path: Path) -> None:
    root = tmp_path / "plugins"
    root.mkdir()
    plug = root / "recover"
    plug.mkdir()
    (plug / "init.mx").write_text(_recovery_init_source(), encoding="utf-8")

    ed, pm = _manager()
    ed.new_buffer("main", "alpha")
    assert pm.load_tree(root)
    plugin = pm.plugins["recover"]
    eb = ed.cur()

    assert len(eb.sel_stack) == 1
    assert eb.sel_stack_authority[-1].group == "plugin:recover"
    assert eb.sel_stack_authority[-1].plugin_generation == plugin.generation
    assert ed.jump_info() == (0, 1)
    assert eb.jump_list_authority[-1].group == "plugin:recover"
    assert eb.jump_list_authority[-1].plugin_generation == plugin.generation

    pm.unload("recover")

    assert eb.sel_stack == []
    assert eb.sel_stack_authority == []
    assert ed.jump_info() == (-1, 0)
    assert eb.jump_list == []
    assert eb.jump_list_authority == []


def test_plugin_reload_recreates_same_recovery_rows_under_new_generation(tmp_path: Path) -> None:
    root = tmp_path / "plugins"
    root.mkdir()
    plug = root / "recover"
    plug.mkdir()
    init = plug / "init.mx"
    init.write_text(_recovery_init_source(), encoding="utf-8")

    ed, pm = _manager()
    ed.new_buffer("main", "alpha")
    assert pm.load_tree(root)
    old_generation = pm.plugins["recover"].generation

    init.write_text(_recovery_init_source(), encoding="utf-8")
    pm.reload("recover")
    new_generation = pm.plugins["recover"].generation

    assert new_generation != old_generation
    eb = ed.cur()
    assert len(eb.sel_stack) == 1
    assert eb.sel_stack_authority[-1].group == "plugin:recover"
    assert eb.sel_stack_authority[-1].plugin_generation == new_generation
    assert ed.jump_info() == (0, 1)
    assert eb.jump_list_authority[-1].group == "plugin:recover"
    assert eb.jump_list_authority[-1].plugin_generation == new_generation


def test_plugin_reload_failure_restores_old_recovery_rows(tmp_path: Path) -> None:
    root = tmp_path / "plugins"
    root.mkdir()
    plug = root / "recover"
    plug.mkdir()
    init = plug / "init.mx"
    init.write_text(_recovery_init_source(), encoding="utf-8")

    ed, pm = _manager()
    ed.new_buffer("main", "alpha")
    assert pm.load_tree(root)
    old_generation = pm.plugins["recover"].generation

    init.write_text(_recovery_init_source() + "missingword\n", encoding="utf-8")
    with pytest.raises(Exception):
        pm.reload("recover")

    assert pm.plugins["recover"].generation == old_generation
    eb = ed.cur()
    assert len(eb.sel_stack) == 1
    assert eb.sel_stack_authority[-1].plugin_generation == old_generation
    assert ed.jump_info() == (0, 1)
    assert eb.jump_list_authority[-1].plugin_generation == old_generation




def _search_init_source(query: str) -> str:
    return f': init "{query}" "ed.find" hostcall drop ;\n'


def test_plugin_unload_clears_plugin_owned_active_search(tmp_path: Path) -> None:
    root = tmp_path / "plugins"
    root.mkdir()
    plug = root / "searcher"
    plug.mkdir()
    (plug / "init.mx").write_text(_search_init_source("alpha"), encoding="utf-8")

    ed, pm = _manager()
    ed.new_buffer("main", "alpha beta alpha")
    assert [p.name for p in pm.load_tree(root)] == ["searcher"]
    plugin = pm.plugins["searcher"]

    assert ed.search.query == "alpha"
    assert ed.search_authority.group == "plugin:searcher"
    assert ed.search_authority.plugin_generation == plugin.generation

    pm.unload("searcher")

    assert ed.search.query == ""
    assert ed.search.last_match is None
    assert ed.search_authority.script_context is False
    ed.messages.clear()
    assert ed.find_next() is False
    assert ed.messages == ["findnext: no active search"]


def test_plugin_unload_does_not_clear_user_active_search(tmp_path: Path) -> None:
    root = tmp_path / "plugins"
    root.mkdir()
    plug = root / "quiet"
    plug.mkdir()
    (plug / "init.mx").write_text(": init ;\n", encoding="utf-8")

    ed, pm = _manager()
    ed.new_buffer("main", "alpha beta alpha")
    assert ed.find("beta", literal=True) is True
    assert ed.search_authority.script_context is False

    assert [p.name for p in pm.load_tree(root)] == ["quiet"]
    pm.unload("quiet")

    assert ed.search.query == "beta"
    assert ed.search_authority.script_context is False


def test_plugin_reload_retags_active_search_and_unload_cleans_new_generation(tmp_path: Path) -> None:
    root = tmp_path / "plugins"
    root.mkdir()
    plug = root / "searcher"
    plug.mkdir()
    init = plug / "init.mx"
    init.write_text(_search_init_source("alpha"), encoding="utf-8")

    ed, pm = _manager()
    ed.new_buffer("main", "alpha beta alpha")
    assert [p.name for p in pm.load_tree(root)] == ["searcher"]
    old_generation = pm.plugins["searcher"].generation

    init.write_text(_search_init_source("beta"), encoding="utf-8")
    pm.reload("searcher")
    new_generation = pm.plugins["searcher"].generation

    assert new_generation != old_generation
    assert ed.search.query == "beta"
    assert ed.search_authority.group == "plugin:searcher"
    assert ed.search_authority.plugin_generation == new_generation

    pm.unload("searcher")

    assert ed.search.query == ""
    assert ed.search_authority.script_context is False


def test_plugin_reload_failure_restores_old_active_search(tmp_path: Path) -> None:
    root = tmp_path / "plugins"
    root.mkdir()
    plug = root / "searcher"
    plug.mkdir()
    init = plug / "init.mx"
    init.write_text(_search_init_source("alpha"), encoding="utf-8")

    ed, pm = _manager()
    ed.new_buffer("main", "alpha beta alpha")
    assert [p.name for p in pm.load_tree(root)] == ["searcher"]
    old_generation = pm.plugins["searcher"].generation

    init.write_text(_search_init_source("beta") + "missingword\n", encoding="utf-8")
    with pytest.raises(Exception):
        pm.reload("searcher")

    assert pm.plugins["searcher"].generation == old_generation
    assert ed.search.query == "alpha"
    assert ed.search_authority.group == "plugin:searcher"
    assert ed.search_authority.plugin_generation == old_generation
    assert any(name == "searcher" and "missingword" in err for name, err in pm.load_errors)


def _history_init_source(cmdline: str) -> str:
    return f': init "{cmdline}" "ed.command" hostcall drop ;\n'


def test_plugin_unload_removes_plugin_owned_prompt_history(tmp_path: Path) -> None:
    root = tmp_path / "plugins"
    root.mkdir()
    plug = root / "historyer"
    plug.mkdir()
    (plug / "init.mx").write_text(_history_init_source("buffers"), encoding="utf-8")

    ed, pm = _manager()
    assert [p.name for p in pm.load_tree(root)] == ["historyer"]
    plugin = pm.plugins["historyer"]

    assert ed.history["command"] == ["buffers"]
    auth = ed.history_authority["command"][0]
    assert auth.group == "plugin:historyer"
    assert auth.plugin_generation == plugin.generation

    pm.unload("historyer")

    assert ed.history.get("command") == []
    assert ed.history_authority.get("command") == []


def test_plugin_unload_does_not_remove_user_prompt_history(tmp_path: Path) -> None:
    root = tmp_path / "plugins"
    root.mkdir()
    plug = root / "quiet"
    plug.mkdir()
    (plug / "init.mx").write_text(": init ;\n", encoding="utf-8")

    ed, pm = _manager()
    ed.exec_command_line("buffers")
    assert ed.history["command"] == ["buffers"]
    assert ed.history_authority["command"][0].script_context is False

    assert [p.name for p in pm.load_tree(root)] == ["quiet"]
    pm.unload("quiet")

    assert ed.history["command"] == ["buffers"]
    assert ed.history_authority["command"][0].script_context is False


def test_plugin_unload_persists_prompt_history_prune_when_enabled(tmp_path: Path) -> None:
    persist = tmp_path / "persist"
    persist.mkdir()
    root = tmp_path / "plugins"
    root.mkdir()
    plug = root / "historyer"
    plug.mkdir()
    (plug / "init.mx").write_text(_history_init_source("buffers"), encoding="utf-8")

    ed, pm = _manager()
    ed.options.set("cap.persist", "true")
    ed.options.set("cap.persist-root", str(persist))
    ed.options.set("history.persist", "true")
    ed.options.set("history.file", "history.json")

    assert [p.name for p in pm.load_tree(root)] == ["historyer"]
    history_file = persist / "history.json"
    assert json.loads(history_file.read_text(encoding="utf-8")) == {"command": ["buffers"]}

    pm.unload("historyer")

    assert ed.history.get("command") == []
    assert json.loads(history_file.read_text(encoding="utf-8")) == {}


def test_plugin_reload_retags_prompt_history_and_prunes_old_generation(tmp_path: Path) -> None:
    root = tmp_path / "plugins"
    root.mkdir()
    plug = root / "historyer"
    plug.mkdir()
    init = plug / "init.mx"
    init.write_text(_history_init_source("buffers"), encoding="utf-8")

    ed, pm = _manager()
    assert [p.name for p in pm.load_tree(root)] == ["historyer"]
    old_generation = pm.plugins["historyer"].generation
    assert ed.history["command"] == ["buffers"]

    init.write_text(_history_init_source("pwd"), encoding="utf-8")
    pm.reload("historyer")

    assert ed.history["command"] == ["pwd"]
    auth = ed.history_authority["command"][0]
    assert auth.group == "plugin:historyer"
    assert auth.plugin_generation == pm.plugins["historyer"].generation
    assert auth.plugin_generation != old_generation


def test_plugin_reload_failure_restores_old_prompt_history(tmp_path: Path) -> None:
    root = tmp_path / "plugins"
    root.mkdir()
    plug = root / "historyer"
    plug.mkdir()
    init = plug / "init.mx"
    init.write_text(_history_init_source("buffers"), encoding="utf-8")

    ed, pm = _manager()
    assert [p.name for p in pm.load_tree(root)] == ["historyer"]
    old_generation = pm.plugins["historyer"].generation

    init.write_text(_history_init_source("pwd") + "missingword\n", encoding="utf-8")
    with pytest.raises(Exception):
        pm.reload("historyer")

    assert ed.history["command"] == ["buffers"]
    auth = ed.history_authority["command"][0]
    assert auth.group == "plugin:historyer"
    assert auth.plugin_generation == old_generation
    assert any(name == "historyer" and "missingword" in err for name, err in pm.load_errors)


def _macro_set_source(slot: str, cmdline: str = "noop") -> str:
    return "\n".join(
        [
            ": init",
            f"  list list \"c\" swap push \"{cmdline}\" swap push swap push \"{slot}\" \"ed.macro-set\" hostcall",
            ";",
            "",
        ]
    )


def test_failed_plugin_load_rolls_back_saved_macro_side_effect(tmp_path: Path) -> None:
    root = tmp_path / "plugins"
    root.mkdir()
    plug = root / "macrofail"
    plug.mkdir()
    (plug / "init.mx").write_text(
        _macro_set_source("leaked") + "\nmissingword\n",
        encoding="utf-8",
    )

    ed, pm = _manager()
    assert pm.load_tree(root) == []

    assert "macrofail" not in pm.plugins
    assert ed.get_macro("leaked") == []
    assert ed.macro_names() == []
    assert any(name == "macrofail" and "missingword" in err for name, err in pm.load_errors)


def test_plugin_unload_removes_plugin_owned_saved_macro(tmp_path: Path) -> None:
    root = tmp_path / "plugins"
    root.mkdir()
    plug = root / "macros"
    plug.mkdir()
    (plug / "init.mx").write_text(_macro_set_source("survivor"), encoding="utf-8")

    ed, pm = _manager()
    assert [p.name for p in pm.load_tree(root)] == ["macros"]
    steps = ed.get_macro("survivor")
    assert len(steps) == 1
    assert steps[0].script_context is True
    assert steps[0].plugin_generation == pm.plugins["macros"].generation

    pm.unload("macros")

    assert ed.get_macro("survivor") == []
    assert ed.macro_names() == []


def test_plugin_reload_prunes_old_generation_macros_but_keeps_staged_macros(tmp_path: Path) -> None:
    root = tmp_path / "plugins"
    root.mkdir()
    plug = root / "macros"
    plug.mkdir()
    init = plug / "init.mx"
    init.write_text(_macro_set_source("oldslot", "old-cmd"), encoding="utf-8")

    ed, pm = _manager()
    assert [p.name for p in pm.load_tree(root)] == ["macros"]
    old_generation = pm.plugins["macros"].generation
    assert "oldslot" in ed.macro_names()

    init.write_text(_macro_set_source("newslot", "new-cmd"), encoding="utf-8")
    pm.reload("macros")

    assert pm.plugins["macros"].generation != old_generation
    assert "oldslot" not in ed.macro_names()
    assert "newslot" in ed.macro_names()
    steps = ed.get_macro("newslot")
    assert len(steps) == 1
    assert steps[0].plugin_generation == pm.plugins["macros"].generation


def test_plugin_unload_deinit_failure_rolls_back_saved_macro_mutation(tmp_path: Path) -> None:
    root = tmp_path / "plugins"
    root.mkdir()
    plug = root / "macrodeinit"
    plug.mkdir()
    (plug / "init.mx").write_text(
        "\n".join(
            [
                ": init ;",
                ": deinit",
                "  list list \"c\" swap push \"noop\" swap push swap push \"deinitleak\" \"ed.macro-set\" hostcall",
                "  missingword",
                ";",
                "",
            ]
        ),
        encoding="utf-8",
    )

    ed, pm = _manager()
    assert [p.name for p in pm.load_tree(root)] == ["macrodeinit"]

    with pytest.raises(Exception):
        pm.unload("macrodeinit")

    assert "macrodeinit" in pm.plugins
    assert ed.get_macro("deinitleak") == []
    assert ed.macro_names() == []


def test_plugin_reload_can_replace_same_named_saved_macro(tmp_path: Path) -> None:
    root = tmp_path / "plugins"
    root.mkdir()
    plug = root / "macroreplace"
    plug.mkdir()
    init = plug / "init.mx"
    init.write_text(_macro_set_source("slot", "old-cmd"), encoding="utf-8")

    ed, pm = _manager()
    assert [p.name for p in pm.load_tree(root)] == ["macroreplace"]
    old_generation = pm.plugins["macroreplace"].generation
    old_steps = ed.get_macro("slot")
    assert old_steps[0].payload["cmdline"] == "old-cmd"

    init.write_text(_macro_set_source("slot", "new-cmd"), encoding="utf-8")
    pm.reload("macroreplace")

    new_steps = ed.get_macro("slot")
    assert len(new_steps) == 1
    assert new_steps[0].payload["cmdline"] == "new-cmd"
    assert new_steps[0].plugin_generation == pm.plugins["macroreplace"].generation
    assert new_steps[0].plugin_generation != old_generation


def test_plugin_reload_failure_restores_old_saved_macro(tmp_path: Path) -> None:
    root = tmp_path / "plugins"
    root.mkdir()
    plug = root / "macrorestore"
    plug.mkdir()
    init = plug / "init.mx"
    init.write_text(_macro_set_source("slot", "old-cmd"), encoding="utf-8")

    ed, pm = _manager()
    assert [p.name for p in pm.load_tree(root)] == ["macrorestore"]
    old_generation = pm.plugins["macrorestore"].generation

    init.write_text(_macro_set_source("slot", "new-cmd") + "\nmissingword\n", encoding="utf-8")
    with pytest.raises(Exception):
        pm.reload("macrorestore")

    restored_steps = ed.get_macro("slot")
    assert len(restored_steps) == 1
    assert restored_steps[0].payload["cmdline"] == "old-cmd"
    assert restored_steps[0].plugin_generation == old_generation
    assert pm.plugins["macrorestore"].generation == old_generation
    assert any(name == "macrorestore" and "missingword" in err for name, err in pm.load_errors)
