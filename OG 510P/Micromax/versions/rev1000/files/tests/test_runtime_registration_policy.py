from __future__ import annotations

import pytest

from micromax_editor.editor import Editor
from micromax_editor.micromax_bridge import install_editor_hostcalls
from micromax_editor.plugins import PluginManager


def _hostcall(ed: Editor, name: str, *args: object) -> list[object]:
    vm = ed.vm
    vm.stack.clear()
    for arg in args:
        vm.stack.append(arg)
    vm.stack.append(name)
    vm.eval("hostcall", filename="<hostcall>")
    return list(vm.stack)


def test_script_context_cannot_overwrite_trusted_command() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    original = ed.command_dispatcher.get("save")
    assert original is not None
    assert not getattr(original, "script_context", False)

    ed.vm.eval(": fake-save ( args -- ok ) drop 1 ;", filename="<script>")
    with ed.script_context():
        with pytest.raises(Exception) as excinfo:
            ed.vm.eval("' fake-save \"save\" \"fake save\" \"ed.cmd-add\" hostcall", filename="<script>")

    assert "cannot modify command: save" in str(excinfo.value)
    assert "trusted registration" in str(excinfo.value)
    assert ed.command_dispatcher.get("save") is original
    assert ed.command_dispatcher.get("save").doc == original.doc


def test_script_context_cannot_remove_trusted_command() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    assert ed.command_dispatcher.get("save") is not None

    with ed.script_context():
        with pytest.raises(Exception) as excinfo:
            _hostcall(ed, "ed.cmd-rm", "save")

    assert "cannot modify command: save" in str(excinfo.value)
    assert ed.command_dispatcher.get("save") is not None


def test_script_command_bar_cannot_rebind_or_unbind_trusted_key() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    assert ed.exec_command_line("bind Ctrl-x command:help") is True
    trusted = ed.keymap.get_binding_exact("Ctrl-x")
    assert trusted is not None
    assert not trusted.script_context

    with ed.script_context():
        assert ed.exec_command_line("bind Ctrl-x command:quit") is False
    assert "bind: script context cannot modify keybinding: Ctrl-x" in ed.messages[-1]
    assert ed.keymap.get_binding_exact("Ctrl-x").action_spec == "command:help"

    with ed.script_context():
        assert ed.exec_command_line("unbind Ctrl-x") is False
    assert "unbind: script context cannot modify keybinding: Ctrl-x" in ed.messages[-1]
    assert ed.keymap.get_binding_exact("Ctrl-x").action_spec == "command:help"


def test_script_hostcalls_cannot_modify_trusted_key_doc_or_remove_binding() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    assert ed.exec_command_line("bind Ctrl-y command:help") is True

    with ed.script_context():
        with pytest.raises(Exception) as excinfo:
            _hostcall(ed, "ed.bind-doc", "Ctrl-y", "spoofed")
    assert "cannot modify keybinding: Ctrl-y" in str(excinfo.value)
    assert ed.keymap.get_binding_exact("Ctrl-y").desc == ""

    with ed.script_context():
        with pytest.raises(Exception) as excinfo2:
            _hostcall(ed, "ed.unbind", "Ctrl-y")
    assert "cannot modify keybinding: Ctrl-y" in str(excinfo2.value)
    assert ed.keymap.get_binding_exact("Ctrl-y") is not None


def test_script_context_cannot_cancel_trusted_timer() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.vm.eval('1000 [ 1 drop ] "ed.after" hostcall', filename="<trusted-timer>")
    tid = ed.vm.pop_int()
    assert ed.timers.pending_count() == 1

    with ed.script_context():
        ed.vm.stack[:] = [tid]
        with pytest.raises(Exception) as excinfo:
            ed.vm.stack.append("ed.cancel-timer")
            ed.vm.eval("hostcall", filename="<hostcall>")

    assert "cannot modify timer" in str(excinfo.value)
    assert ed.vm.stack == [tid]
    assert ed.timers.pending_count() == 1


def test_script_context_cannot_clear_trusted_hook_handler() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.vm.eval(
        "\n".join(
            [
                "hook guarded-hook",
                ": trusted-handler 1 drop ;",
                "' trusted-handler hook-add guarded-hook",
            ]
        ),
        filename="<trusted-hook>",
    )
    ed.vm.eval("hook-detail guarded-hook", filename="<test>")
    assert len(ed.vm.pop_list()) == 1

    with ed.script_context():
        with pytest.raises(Exception) as excinfo:
            ed.vm.eval("hook-clear guarded-hook", filename="<script>")

    assert "cannot modify hook handler: guarded-hook" in str(excinfo.value)
    ed.vm.eval("hook-detail guarded-hook", filename="<test>")
    assert len(ed.vm.pop_list()) == 1


def test_script_can_update_its_own_command_but_not_another_script_origin() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.vm.eval(
        "\n".join(
            [
                ": owned_a ( args -- ok ) drop 1 ;",
                ": owned_b ( args -- ok ) drop 1 ;",
            ]
        ),
        filename="<script-words>",
    )

    with ed.script_context():
        ed.vm.eval("' owned_a \"ownedcmd\" \"owned a\" \"ed.cmd-add\" hostcall", filename="<script-a>")
        assert ed.vm.pop_int() == 1
        first = ed.command_dispatcher.get("ownedcmd")
        assert first is not None
        first_origin = getattr(first, "script_origin_id", None)
        assert first_origin

        ed.vm.eval("' owned_b \"ownedcmd\" \"owned b\" \"ed.cmd-add\" hostcall", filename="<script-a>")
        assert ed.vm.pop_int() == 1

    updated = ed.command_dispatcher.get("ownedcmd")
    assert updated is not None
    assert updated.doc == "owned b"
    assert getattr(updated, "script_origin_id", None) == first_origin

    with ed.script_context():
        with pytest.raises(Exception) as excinfo:
            _hostcall(ed, "ed.cmd-rm", "ownedcmd")

    assert "different script origin" in str(excinfo.value)
    assert ed.command_dispatcher.get("ownedcmd") is updated


def test_plugin_deinit_can_remove_its_own_runtime_registrations(tmp_path) -> None:
    root = tmp_path / "plugins"
    plug = root / "owned"
    plug.mkdir(parents=True)
    (plug / "init.mx").write_text(
        "\n".join(
            [
                ": owned-cmd ( args -- ok ) drop 1 ;",
                ": owned-hook ( -- ) ;",
                ": init",
                "  ' owned-cmd \"owned\" \"owned command\" \"ed.cmd-add\" hostcall drop",
                "  \"F21\" \"command:owned\" \"ed.bind\" hostcall",
                "  ' owned-hook hook-add ed.pre-action",
                "  10000 [ 1 drop ] \"ed.after\" hostcall drop",
                ";",
                ": deinit",
                "  \"owned\" \"ed.cmd-rm\" hostcall drop",
                "  \"F21\" \"ed.unbind\" hostcall drop",
                "  ' owned-hook hook-rm ed.pre-action",
                ";",
            ]
        ),
        encoding="utf-8",
    )

    ed = Editor()
    install_editor_hostcalls(ed)
    pm = PluginManager(ed.vm)
    assert [p.name for p in pm.load_tree(root)] == ["owned"]
    assert ed.command_dispatcher.get("owned") is not None
    assert ed.keymap.get_binding_exact("F21") is not None

    pm.unload("owned")

    assert ed.command_dispatcher.get("owned") is None
    assert ed.keymap.get_binding_exact("F21") is None
    ed.vm.eval("hook-detail ed.pre-action", filename="<test>")
    assert ed.vm.pop_list() == []


def test_independent_plain_script_cannot_mutate_another_script_binding() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    with ed.script_context():
        _hostcall(ed, "ed.bind", "F31", "command:help")
    binding = ed.keymap.get_binding_exact("F31")
    assert binding is not None
    assert bool(getattr(binding, "script_context", False)) is True
    first_origin = str(getattr(binding, "script_origin_id", "") or "")
    assert first_origin

    with ed.script_context():
        assert ed.current_script_origin_id() != first_origin
        with pytest.raises(Exception) as excinfo:
            _hostcall(ed, "ed.bind-doc", "F31", "spoofed")

    assert "cannot modify keybinding: F31" in str(excinfo.value)
    assert "different script origin" in str(excinfo.value)
    assert ed.keymap.get_binding_exact("F31").desc == ""


def test_nested_plain_script_context_inherits_registration_origin() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    with ed.script_context():
        outer = ed.current_script_origin_id()
        _hostcall(ed, "ed.bind", "F32", "command:help")
        with ed.script_context():
            assert ed.current_script_origin_id() == outer
            _hostcall(ed, "ed.bind-doc", "F32", "nested owner")

    binding = ed.keymap.get_binding_exact("F32")
    assert binding is not None
    assert binding.desc == "nested owner"
    assert str(getattr(binding, "script_origin_id", "") or "") == outer
