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
