from __future__ import annotations

import json

from micromax_editor.editor import Editor
from micromax_editor.micromax_bridge import install_editor_hostcalls
from micromax_editor.plugins import PluginManager


def _editor_with_plugin_manager() -> tuple[Editor, PluginManager]:
    ed = Editor()
    install_editor_hostcalls(ed)
    pm = PluginManager(ed.vm)
    ed.plugin_manager = pm
    return ed, pm


def test_plugin_reload_keeps_loaded_plugin_after_failed_source_reload(tmp_path) -> None:
    root = tmp_path / "plugins"
    root.mkdir()

    plug = root / "alpha"
    plug.mkdir()
    (plug / "main.mx").write_text(': aword "a1" ;\n', encoding="utf-8")
    (plug / "plugin.json").write_text(json.dumps({"entry": "main.mx"}), encoding="utf-8")

    ed, pm = _editor_with_plugin_manager()
    assert [p.name for p in pm.load_tree(root)] == ["alpha"]

    (plug / "main.mx").write_text("unknownword\n", encoding="utf-8")
    try:
        pm.reload("alpha")
    except Exception:
        pass
    else:  # pragma: no cover - defensive assertion
        raise AssertionError("reload should fail while plugin source is broken")

    assert "alpha" in pm.plugins
    assert any(name == "alpha" and "unknownword" in err for name, err in pm.load_errors)
    ed.vm.eval("use alpha aword", filename="<test>")
    assert ed.vm.stack.pop() == "a1"

    (plug / "main.mx").write_text(': aword "a2" ;\n', encoding="utf-8")
    ed.messages.clear()
    assert ed.plugin_reload_with_feedback("alpha")

    assert ed.messages == ["plugin reload: alpha [loaded]"]
    assert "alpha" in pm.plugins
    assert not any(name == "alpha" for name, _err in pm.load_errors)

    ed.vm.eval("use alpha aword", filename="<test>")
    assert ed.vm.stack.pop() == "a2"


def test_plugin_reload_failure_cleans_staged_side_effects_and_keeps_old_runtime(tmp_path) -> None:
    root = tmp_path / "plugins"
    root.mkdir()

    plug = root / "alpha"
    plug.mkdir()
    init = plug / "init.mx"
    init.write_text(
        "\n".join(
            [
                ": hi-cmd ( args -- ok ) drop 1 ;",
                ": old-hook ( -- ) ;",
                ": init",
                "  ' hi-cmd \"hi\" \"say hi\" \"ed.cmd-add\" hostcall",
                "  \"Ctrl-h\" \"command:hi\" \"ed.bind\" hostcall",
                "  ' old-hook hook-add ed.pre-action",
                "  100 [ 1 drop ] \"ed.after\" hostcall drop",
                ";",
            ]
        ),
        encoding="utf-8",
    )

    ed, pm = _editor_with_plugin_manager()
    assert [p.name for p in pm.load_tree(root)] == ["alpha"]
    old_wid = pm.plugins["alpha"].wid
    assert ed.command_dispatcher.get("hi") is not None
    assert ed.keymap.get_binding("Ctrl-h") is not None
    assert ed.timers.pending_count() == 1
    before_word_authority = ed._snapshot_word_authority()

    init.write_text(
        "\n".join(
            [
                ": hi-cmd ( args -- ok ) drop 1 ;",
                ": new-hook ( -- ) ;",
                ": init",
                "  ' hi-cmd \"hi\" \"staged replacement\" \"ed.cmd-add\" hostcall",
                "  \"Ctrl-h\" \"command:staged\" \"ed.bind\" hostcall",
                "  ' new-hook hook-add ed.pre-action",
                "  100 [ 2 drop ] \"ed.after\" hostcall drop",
                "  missingword",
                ";",
            ]
        ),
        encoding="utf-8",
    )

    try:
        pm.reload("alpha")
    except Exception:
        pass
    else:  # pragma: no cover - defensive assertion
        raise AssertionError("reload should fail while staged init is broken")

    assert pm.plugins["alpha"].wid == old_wid
    assert pm.plugins["alpha"].group == "plugin:alpha"
    assert ed.command_dispatcher.get("hi") is not None
    assert ed.command_dispatcher.get("hi").doc == "say hi"
    assert ed.command_dispatcher.get("bye") is None
    assert ed.keymap.get_binding("Ctrl-h") is not None
    assert ed.keymap.get_binding("Ctrl-h").action_spec == "command:hi"
    assert ed.keymap.get_binding("Ctrl-b") is None
    assert ed.timers.pending_count() == 1
    assert ed._snapshot_word_authority() == before_word_authority
    ed.vm.eval("hook-detail ed.pre-action", filename="<test>")
    rows = ed.vm.pop_list()
    assert [(r[0], r[1]) for r in rows] == [("old-hook", "plugin:alpha")]
    assert any(name == "alpha" and "missingword" in err for name, err in pm.load_errors)

    init.write_text(
        "\n".join(
            [
                ": bye-cmd ( args -- ok ) drop 1 ;",
                ": new-hook ( -- ) ;",
                ": init",
                "  ' bye-cmd \"bye\" \"say bye\" \"ed.cmd-add\" hostcall",
                "  \"Ctrl-b\" \"command:bye\" \"ed.bind\" hostcall",
                "  ' new-hook hook-add ed.pre-action",
                "  100 [ 2 drop ] \"ed.after\" hostcall drop",
                ";",
            ]
        ),
        encoding="utf-8",
    )
    pm.reload("alpha")

    assert pm.plugins["alpha"].wid != old_wid
    assert pm.plugins["alpha"].group == "plugin:alpha"
    assert ed.command_dispatcher.get("hi") is None
    assert ed.command_dispatcher.get("bye") is not None
    assert ed.keymap.get_binding("Ctrl-h") is None
    assert ed.keymap.get_binding("Ctrl-b") is not None
    assert ed.timers.pending_count() == 1
    ed.vm.eval("hook-detail ed.pre-action", filename="<test>")
    rows = ed.vm.pop_list()
    assert [(r[0], r[1]) for r in rows] == [("new-hook", "plugin:alpha")]
    assert not any(name == "alpha" for name, _err in pm.load_errors)




def test_plugin_reload_failure_restores_overwritten_command_and_key(tmp_path) -> None:
    root = tmp_path / "plugins"
    root.mkdir()

    plug = root / "alpha"
    plug.mkdir()
    init = plug / "init.mx"
    init.write_text(
        "\n".join(
            [
                ": old-cmd ( args -- ok ) drop 1 ;",
                ": init",
                "  ' old-cmd \"same\" \"old command\" \"ed.cmd-add\" hostcall",
                "  \"Ctrl-s\" \"command:same\" \"ed.bind\" hostcall",
                ";",
            ]
        ),
        encoding="utf-8",
    )

    ed, pm = _editor_with_plugin_manager()
    assert [p.name for p in pm.load_tree(root)] == ["alpha"]
    old_wid = pm.plugins["alpha"].wid
    old_cmd = ed.command_dispatcher.get("same")
    assert old_cmd is not None
    assert old_cmd.doc == "old command"
    assert old_cmd.group == "plugin:alpha"
    old_binding = ed.keymap.get_binding("Ctrl-s")
    assert old_binding is not None
    assert old_binding.action_spec == "command:same"

    init.write_text(
        "\n".join(
            [
                ": new-cmd ( args -- ok ) drop 1 ;",
                ": init",
                "  ' new-cmd \"same\" \"new command\" \"ed.cmd-add\" hostcall",
                "  \"Ctrl-s\" \"command:new-same\" \"ed.bind\" hostcall",
                "  missingword",
                ";",
            ]
        ),
        encoding="utf-8",
    )

    try:
        pm.reload("alpha")
    except Exception:
        pass
    else:  # pragma: no cover - defensive assertion
        raise AssertionError("reload should fail after overwriting command/key during staged init")

    assert pm.plugins["alpha"].wid == old_wid
    same = ed.command_dispatcher.get("same")
    assert same is not None
    assert same.doc == "old command"
    assert same.group == "plugin:alpha"
    binding = ed.keymap.get_binding("Ctrl-s")
    assert binding is not None
    assert binding.action_spec == "command:same"
    assert binding.group == "plugin:alpha"
    assert all("#reload" not in group for group in ed.command_dispatcher.groups())
    assert all("#reload" not in group for group in ed.keymap.groups())

    init.write_text(
        "\n".join(
            [
                ": new-cmd ( args -- ok ) drop 1 ;",
                ": init",
                "  ' new-cmd \"same\" \"new command\" \"ed.cmd-add\" hostcall",
                "  \"Ctrl-s\" \"command:new-same\" \"ed.bind\" hostcall",
                ";",
            ]
        ),
        encoding="utf-8",
    )
    pm.reload("alpha")

    same = ed.command_dispatcher.get("same")
    assert same is not None
    assert same.doc == "new command"
    assert same.group == "plugin:alpha"
    binding = ed.keymap.get_binding("Ctrl-s")
    assert binding is not None
    assert binding.action_spec == "command:new-same"
    assert binding.group == "plugin:alpha"
    assert all("#reload" not in group for group in ed.command_dispatcher.groups())
    assert all("#reload" not in group for group in ed.keymap.groups())

def test_plugin_reload_replaces_existing_search_order_wordlist(tmp_path) -> None:
    root = tmp_path / "plugins"
    root.mkdir()

    plug = root / "alpha"
    plug.mkdir()
    init = plug / "init.mx"
    init.write_text(': aword "old" ;\n', encoding="utf-8")

    ed, pm = _editor_with_plugin_manager()
    pm.load_tree(root)
    old_wid = pm.plugins["alpha"].wid
    ed.vm.eval("use alpha", filename="<test>")
    assert old_wid in ed.vm.search_order

    init.write_text(': aword "new" ;\n', encoding="utf-8")
    pm.reload("alpha")
    new_wid = pm.plugins["alpha"].wid

    assert new_wid in ed.vm.search_order
    assert old_wid not in ed.vm.search_order
    ed.vm.eval("aword", filename="<test>")
    assert ed.vm.stack.pop() == "new"



def test_plugin_reload_old_deinit_resolves_old_module_until_promotion(tmp_path) -> None:
    root = tmp_path / "plugins"
    root.mkdir()

    plug = root / "alpha"
    plug.mkdir()
    init = plug / "init.mx"
    init.write_text(
        "\n".join(
            [
                ': aword "old" ;',
                ': deinit use alpha aword "ed.msg" hostcall ;',
            ]
        ),
        encoding="utf-8",
    )

    ed, pm = _editor_with_plugin_manager()
    assert [p.name for p in pm.load_tree(root)] == ["alpha"]

    init.write_text(': aword "new" ;\n', encoding="utf-8")
    ed.messages.clear()
    pm.reload("alpha")

    assert ed.messages == ["old"]
    ed.vm.eval("use alpha aword", filename="<test>")
    assert ed.vm.stack.pop() == "new"



def test_plugin_reload_failed_old_deinit_restores_overwritten_registrations(tmp_path) -> None:
    root = tmp_path / "plugins"
    root.mkdir()

    plug = root / "alpha"
    plug.mkdir()
    init = plug / "init.mx"
    init.write_text(
        "\n".join(
            [
                ': aword "old" ;',
                ": old-cmd ( args -- ok ) drop 1 ;",
                ": init",
                "  ' old-cmd \"same\" \"old command\" \"ed.cmd-add\" hostcall",
                "  \"Ctrl-d\" \"command:same\" \"ed.bind\" hostcall",
                ";",
                ": deinit missingword ;",
            ]
        ),
        encoding="utf-8",
    )

    ed, pm = _editor_with_plugin_manager()
    assert [p.name for p in pm.load_tree(root)] == ["alpha"]
    old_wid = pm.plugins["alpha"].wid

    init.write_text(
        "\n".join(
            [
                ': aword "new" ;',
                ": new-cmd ( args -- ok ) drop 1 ;",
                ": init",
                "  ' new-cmd \"same\" \"new command\" \"ed.cmd-add\" hostcall",
                "  \"Ctrl-d\" \"command:new-same\" \"ed.bind\" hostcall",
                ";",
            ]
        ),
        encoding="utf-8",
    )

    try:
        pm.reload("alpha")
    except Exception:
        pass
    else:  # pragma: no cover - defensive assertion
        raise AssertionError("reload should fail while old deinit is broken")

    assert pm.plugins["alpha"].wid == old_wid
    ed.vm.eval("use alpha aword", filename="<test>")
    assert ed.vm.stack.pop() == "old"
    same = ed.command_dispatcher.get("same")
    assert same is not None
    assert same.doc == "old command"
    assert same.group == "plugin:alpha"
    binding = ed.keymap.get_binding("Ctrl-d")
    assert binding is not None
    assert binding.action_spec == "command:same"
    assert binding.group == "plugin:alpha"
    assert any(name == "alpha" and "missingword" in err for name, err in pm.load_errors)
    assert all("#reload" not in group for group in ed.command_dispatcher.groups())
    assert all("#reload" not in group for group in ed.keymap.groups())



def test_plugin_reload_failed_old_deinit_drops_uncommitted_wordlist(tmp_path) -> None:
    root = tmp_path / "plugins"
    root.mkdir()

    plug = root / "alpha"
    plug.mkdir()
    init = plug / "init.mx"
    init.write_text(
        "\n".join(
            [
                ': aword "old" ;',
                ': deinit 2 constant aword 3 constant leaked-deinit missingword ;',
            ]
        ),
        encoding="utf-8",
    )

    ed, pm = _editor_with_plugin_manager()
    assert [p.name for p in pm.load_tree(root)] == ["alpha"]
    old_wid = pm.plugins["alpha"].wid
    before_wordlists = {wid: dict(words) for wid, words in ed.vm.wordlists.items()}
    before_names = dict(ed.vm.wordlist_names)
    before_search = list(ed.vm.search_order)

    init.write_text(': aword "new" ;\n', encoding="utf-8")

    try:
        pm.reload("alpha")
    except Exception:
        pass
    else:  # pragma: no cover - defensive assertion
        raise AssertionError("reload should fail while old deinit is broken")

    assert pm.plugins["alpha"].wid == old_wid
    assert ed.vm.modules["alpha"] == old_wid
    assert ed.vm.wordlists == before_wordlists
    assert ed.vm.wordlist_names == before_names
    assert ed.vm.search_order == before_search
    assert all("#reload" not in group for group in ed.command_dispatcher.groups())
    assert all("#reload" not in group for group in ed.keymap.groups())
    assert all("#reload" not in group for group in ed.timers.groups())
    assert any(name == "alpha" and "missingword" in err for name, err in pm.load_errors)

    ed.vm.eval("use alpha aword", filename="<test>")
    assert ed.vm.stack.pop() == "old"

def test_plugin_reload_rereads_plugin_json_entry_after_failure(tmp_path) -> None:
    root = tmp_path / "plugins"
    root.mkdir()

    plug = root / "alpha"
    plug.mkdir()
    (plug / "main.mx").write_text(': aword "a1" ;\n', encoding="utf-8")
    (plug / "plugin.json").write_text(json.dumps({"entry": "main.mx"}), encoding="utf-8")

    ed, pm = _editor_with_plugin_manager()
    assert [p.name for p in pm.load_tree(root)] == ["alpha"]

    (plug / "main.mx").write_text("unknownword\n", encoding="utf-8")
    try:
        pm.reload("alpha")
    except Exception:
        pass
    else:  # pragma: no cover - defensive assertion
        raise AssertionError("reload should fail while plugin source is broken")

    (plug / "alt.mx").write_text(': aword "alt" ;\n', encoding="utf-8")
    (plug / "plugin.json").write_text(json.dumps({"entry": "alt.mx"}), encoding="utf-8")

    assert ed.plugin_reload_with_feedback("alpha")
    ed.vm.eval("use alpha aword", filename="<test>")
    assert ed.vm.stack.pop() == "alt"


def test_plugin_lifecycle_failure_does_not_leave_half_loaded_runtime(tmp_path) -> None:
    root = tmp_path / "plugins"
    root.mkdir()

    plug = root / "alpha"
    plug.mkdir()
    (plug / "init.mx").write_text(
        "\n".join(
            [
                ": leaked-cmd ( args -- ok ) drop 1 ;",
                ": leaked-hook ( -- ) ;",
                ": init",
                "  ' leaked-cmd \"leaked\" \"leaked command\" \"ed.cmd-add\" hostcall",
                "  \"Ctrl-l\" \"command:leaked\" \"ed.bind\" hostcall",
                "  ' leaked-hook hook-add ed.pre-action",
                "  100 [ 1 drop ] \"ed.after\" hostcall drop",
                "  missingword",
                ";",
            ]
        ),
        encoding="utf-8",
    )

    ed, pm = _editor_with_plugin_manager()
    assert pm.load_tree(root) == []

    assert "alpha" not in pm.plugins
    assert "alpha" not in ed.vm.modules
    assert ed.command_dispatcher.get("leaked") is None
    assert ed.keymap.get_binding("Ctrl-l") is None
    assert ed.timers.pending_count() == 0
    ed.vm.eval("hook-detail ed.pre-action", filename="<test>")
    assert ed.vm.pop_list() == []
    assert any(name == "alpha" and "missingword" in err for name, err in pm.load_errors)




def test_plugin_unload_deinit_failure_keeps_plugin_loaded_and_restores_runtime(tmp_path) -> None:
    root = tmp_path / "plugins"
    root.mkdir()

    plug = root / "alpha"
    plug.mkdir()
    init = plug / "init.mx"
    init.write_text(
        "\n".join(
            [
                ': aword "alive" ;',
                ": old-cmd ( args -- ok ) drop 1 ;",
                ": old-hook ( -- ) ;",
                ": deinit-cmd ( args -- ok ) drop 1 ;",
                ": deinit-hook ( -- ) ;",
                ": init",
                "  ' old-cmd \"same\" \"old command\" \"ed.cmd-add\" hostcall",
                "  \"Ctrl-u\" \"command:same\" \"ed.bind\" hostcall",
                "  ' old-hook hook-add ed.pre-action",
                "  100 [ 1 drop ] \"ed.after\" hostcall drop",
                ";",
                ": deinit",
                "  \"same\" \"ed.cmd-rm\" hostcall drop",
                "  ' deinit-cmd \"same\" \"deinit command\" \"ed.cmd-add\" hostcall",
                "  \"Ctrl-u\" \"command:deinit\" \"ed.bind\" hostcall",
                "  ' deinit-hook hook-add ed.pre-action",
                "  100 [ 2 drop ] \"ed.after\" hostcall drop",
                "  missingword",
                ";",
            ]
        ),
        encoding="utf-8",
    )

    ed, pm = _editor_with_plugin_manager()
    assert [p.name for p in pm.load_tree(root)] == ["alpha"]
    old_wid = pm.plugins["alpha"].wid
    before_search = list(ed.vm.search_order)

    try:
        pm.unload("alpha")
    except Exception:
        pass
    else:  # pragma: no cover - defensive assertion
        raise AssertionError("unload should fail while plugin deinit is broken")

    assert pm.plugins["alpha"].wid == old_wid
    assert ed.vm.modules["alpha"] == old_wid
    assert ed.vm.search_order == before_search
    ed.vm.eval("use alpha aword", filename="<test>")
    assert ed.vm.stack.pop() == "alive"

    same = ed.command_dispatcher.get("same")
    assert same is not None
    assert same.doc == "old command"
    assert same.group == "plugin:alpha"
    binding = ed.keymap.get_binding("Ctrl-u")
    assert binding is not None
    assert binding.action_spec == "command:same"
    assert binding.group == "plugin:alpha"
    assert ed.timers.pending_count() == 1
    ed.vm.eval("hook-detail ed.pre-action", filename="<test>")
    rows = ed.vm.pop_list()
    assert [(r[0], r[1]) for r in rows] == [("old-hook", "plugin:alpha")]
    assert any(name == "alpha" and "missingword" in err for name, err in pm.load_errors)

    # A broken committed deinit cannot be repaired by reload because reload must
    # run the old deinit before promotion.  The explicit force lane is the
    # operator escape hatch: skip lifecycle, scrub grouped runtime state, and
    # clear the current error witness.
    pm.unload("alpha", force=True)

    assert "alpha" not in pm.plugins
    assert "alpha" not in ed.vm.modules
    assert ed.command_dispatcher.get("same") is None
    assert ed.keymap.get_binding("Ctrl-u") is None
    assert ed.timers.pending_count() == 0
    assert not any(name == "alpha" for name, _err in pm.load_errors)


def test_plugin_load_tree_clears_stale_error_after_plugin_is_fixed(tmp_path) -> None:
    root = tmp_path / "plugins"
    root.mkdir()

    plug = root / "alpha"
    plug.mkdir()
    (plug / "init.mx").write_text("unknownword\n", encoding="utf-8")

    ed, pm = _editor_with_plugin_manager()
    assert pm.load_tree(root) == []
    assert any(name == "alpha" and "unknownword" in err for name, err in pm.load_errors)

    (plug / "init.mx").write_text(': aword "fixed" ;\n', encoding="utf-8")
    loaded = pm.load_tree(root)

    assert [p.name for p in loaded] == ["alpha"]
    assert not any(name == "alpha" for name, _err in pm.load_errors)
    assert ed.plugin_inventory_entry("alpha") == "alpha [loaded]"

    ed.vm.eval("use alpha aword", filename="<test>")
    assert ed.vm.stack.pop() == "fixed"


def test_plugin_reload_keeps_loaded_plugin_when_new_metadata_is_invalid(tmp_path) -> None:
    root = tmp_path / "plugins"
    root.mkdir()

    plug = root / "alpha"
    plug.mkdir()
    (plug / "main.mx").write_text(': aword "old" ;\n', encoding="utf-8")
    (plug / "plugin.json").write_text(json.dumps({"entry": "main.mx"}), encoding="utf-8")

    ed, pm = _editor_with_plugin_manager()
    assert [p.name for p in pm.load_tree(root)] == ["alpha"]

    (plug / "plugin.json").write_text(json.dumps({"entry": "missing.mx"}), encoding="utf-8")
    ed.messages.clear()
    assert not ed.plugin_reload_with_feedback("alpha")

    assert "alpha" in pm.plugins
    assert any(name == "alpha" and "entry file not found" in err for name, err in pm.load_errors)
    assert ed.messages[0] == "plugin reload: alpha [error]"
    assert ed.messages[1].endswith("previous version still loaded")
    ed.vm.eval("use alpha aword", filename="<test>")
    assert ed.vm.stack.pop() == "old"



def test_plugin_source_and_lifecycle_cannot_read_ambient_stack_or_session_locals(
    tmp_path,
) -> None:
    root = tmp_path / "plugins"
    root.mkdir()

    plug = root / "isolated"
    plug.mkdir()
    (plug / "init.mx").write_text(
        """
        depth 0 = [ "source-stack-clean" ] [ "source-stack-leak" ] if "ed.msg" hostcall
        [ ambient-local drop ] catch 0 =
          [ "source-local-leak" ] [ "source-local-clean" ] if "ed.msg" hostcall
        : init
          depth 0 = [ "init-stack-clean" ] [ "init-stack-leak" ] if "ed.msg" hostcall
          [ ambient-local drop ] catch 0 =
            [ "init-local-leak" ] [ "init-local-clean" ] if "ed.msg" hostcall
        ;
        """,
        encoding="utf-8",
    )

    ed, pm = _editor_with_plugin_manager()
    marker = ["sensitive-stack-value"]
    local_frame = ed.vm.locals_stack[0]
    ed.vm.stack[:] = [marker]
    local_frame["ambient-local"] = "sensitive-local-value"

    assert [plugin.name for plugin in pm.load_tree(root)] == ["isolated"]

    assert ed.messages == [
        "source-stack-clean",
        "source-local-clean",
        "init-stack-clean",
        "init-local-clean",
    ]
    assert ed.vm.stack == [marker]
    assert ed.vm.stack[0] is marker
    assert ed.vm.locals_stack == [local_frame]
    assert ed.vm.locals_stack[0] is local_frame
    assert local_frame == {"ambient-local": "sensitive-local-value"}

def test_plugin_source_and_lifecycle_do_not_leak_vm_stack_on_load_failure(tmp_path) -> None:
    root = tmp_path / "plugins"
    root.mkdir()

    plug = root / "alpha"
    plug.mkdir()
    (plug / "init.mx").write_text(
        "\n".join(
            [
                '"source-junk"',
                ': init',
                '  "init-junk"',
                '  missingword',
                ';',
            ]
        ),
        encoding="utf-8",
    )

    ed, pm = _editor_with_plugin_manager()
    ed.vm.stack.append("sentinel")

    assert pm.load_tree(root) == []

    assert ed.vm.stack == ["sentinel"]
    assert ed.vm.rstack == []
    assert "alpha" not in pm.plugins
    assert any(name == "alpha" and "missingword" in err for name, err in pm.load_errors)


def test_plugin_lifecycle_stack_is_isolated_across_load_reload_and_unload(tmp_path) -> None:
    root = tmp_path / "plugins"
    root.mkdir()

    plug = root / "alpha"
    plug.mkdir()
    init = plug / "init.mx"
    init.write_text(
        "\n".join(
            [
                ': aword "old" ;',
                ': init "load-junk" ;',
                ': deinit "unload-junk" ;',
            ]
        ),
        encoding="utf-8",
    )

    ed, pm = _editor_with_plugin_manager()
    ed.vm.stack.append("sentinel")
    assert [p.name for p in pm.load_tree(root)] == ["alpha"]
    assert ed.vm.stack == ["sentinel"]

    init.write_text(
        "\n".join(
            [
                ': aword "new" ;',
                ': init "reload-init-junk" ;',
                ': deinit "reload-unload-junk" ;',
            ]
        ),
        encoding="utf-8",
    )
    pm.reload("alpha")
    assert ed.vm.stack == ["sentinel"]
    ed.vm.eval("use alpha aword", filename="<test>")
    assert ed.vm.stack == ["sentinel", "new"]
    assert ed.vm.stack.pop() == "new"

    pm.unload("alpha")
    assert ed.vm.stack == ["sentinel"]
    assert "alpha" not in pm.plugins


def test_failed_plugin_source_rolls_back_modules_and_wordlists(tmp_path) -> None:
    root = tmp_path / "plugins"
    root.mkdir()

    plug = root / "alpha"
    plug.mkdir()
    (plug / "init.mx").write_text(
        "\n".join(
            [
                ': ghost "leaked" ;',
                "unknownword",
            ]
        ),
        encoding="utf-8",
    )

    ed, pm = _editor_with_plugin_manager()
    before_modules = dict(ed.vm.modules)
    before_wordlists = {wid: dict(words) for wid, words in ed.vm.wordlists.items()}
    before_wordlist_names = dict(ed.vm.wordlist_names)
    before_search = list(ed.vm.search_order)
    before_current = ed.vm.current_wid
    before_next = ed.vm._next_wid
    before_word_authority = ed._snapshot_word_authority()

    assert pm.load_tree(root) == []

    assert "alpha" not in pm.plugins
    assert "alpha" not in ed.vm.modules
    assert "leakedmod" not in ed.vm.modules
    assert ed.vm.modules == before_modules
    assert ed.vm.wordlists == before_wordlists
    assert ed.vm.wordlist_names == before_wordlist_names
    assert ed.vm.search_order == before_search
    assert ed.vm.current_wid == before_current
    assert ed.vm._next_wid == before_next
    assert ed.vm._module_stack == []
    assert ed._snapshot_word_authority() == before_word_authority
    assert any(name == "alpha" and "unknownword" in err for name, err in pm.load_errors)


def test_plugin_unload_deinit_failure_rolls_back_dictionary_mutations(tmp_path) -> None:
    root = tmp_path / "plugins"
    root.mkdir()

    plug = root / "alpha"
    plug.mkdir()
    init = plug / "init.mx"
    init.write_text(
        "\n".join(
            [
                ': aword "alive" ;',
                ': deinit',
                '  2 constant aword',
                '  3 constant leaked-deinit',
                '  unknownword',
                ';',
            ]
        ),
        encoding="utf-8",
    )

    ed, pm = _editor_with_plugin_manager()
    assert [p.name for p in pm.load_tree(root)] == ["alpha"]
    before_modules = dict(ed.vm.modules)
    before_wordlists = {wid: dict(words) for wid, words in ed.vm.wordlists.items()}
    before_wordlist_names = dict(ed.vm.wordlist_names)
    before_search = list(ed.vm.search_order)
    before_current = ed.vm.current_wid
    before_next = ed.vm._next_wid
    before_word_authority = ed._snapshot_word_authority()

    try:
        pm.unload("alpha")
    except Exception:
        pass
    else:  # pragma: no cover - defensive assertion
        raise AssertionError("unload should fail after mutating dictionary state")

    assert "alpha" in pm.plugins
    assert "leakedmod" not in ed.vm.modules
    assert ed.vm.modules == before_modules
    assert ed.vm.wordlists == before_wordlists
    assert ed.vm.wordlist_names == before_wordlist_names
    assert ed.vm.search_order == before_search
    assert ed.vm.current_wid == before_current
    assert ed.vm._next_wid == before_next
    assert ed.vm._module_stack == []
    assert ed._snapshot_word_authority() == before_word_authority
    ed.vm.eval("use alpha aword", filename="<test>")
    assert ed.vm.stack.pop() == "alive"
    assert any(name == "alpha" and "unknownword" in err for name, err in pm.load_errors)


def test_plugin_unload_success_discards_deinit_dictionary_mutations(tmp_path) -> None:
    root = tmp_path / "plugins"
    root.mkdir()

    plug = root / "alpha"
    plug.mkdir()
    (plug / "init.mx").write_text(
        "\n".join(
            [
                ': aword "alive" ;',
                ': deinit',
                '  2 constant aword',
                '  "cleanup seen" "ed.msg" hostcall',
                ';',
            ]
        ),
        encoding="utf-8",
    )

    ed, pm = _editor_with_plugin_manager()
    assert [p.name for p in pm.load_tree(root)] == ["alpha"]

    pm.unload("alpha")

    assert ed.messages == ["cleanup seen"]
    assert "alpha" not in pm.plugins
    assert "alpha" not in ed.vm.modules
    assert "leakedmod" not in ed.vm.modules
    assert ed.vm._module_stack == []


def test_plugin_reload_success_discards_old_deinit_dictionary_mutations(tmp_path) -> None:
    root = tmp_path / "plugins"
    root.mkdir()

    plug = root / "alpha"
    plug.mkdir()
    init = plug / "init.mx"
    init.write_text(
        "\n".join(
            [
                ': aword "old" ;',
                ': deinit',
                '  2 constant aword',
                '  "old cleanup" "ed.msg" hostcall',
                ';',
            ]
        ),
        encoding="utf-8",
    )

    ed, pm = _editor_with_plugin_manager()
    assert [p.name for p in pm.load_tree(root)] == ["alpha"]

    init.write_text(': aword "new" ;\n', encoding="utf-8")
    pm.reload("alpha")

    assert ed.messages == ["old cleanup"]
    assert "leakedmod" not in ed.vm.modules
    assert ed.vm._module_stack == []
    ed.vm.eval("use alpha aword", filename="<test>")
    assert ed.vm.stack.pop() == "new"
