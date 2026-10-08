from __future__ import annotations

from pathlib import Path
import json

import pytest

from micromax.vm import HookHandler, HookWord

from micromax_editor.buffer import Cursor
from micromax_editor.commandbar import Prompt
from micromax_editor.editor import ActiveKeyMode, Editor, MacroStep, QueryReplaceSession
from micromax_editor.micromax_bridge import install_editor_hostcalls
from micromax_editor.plugin_runtime import (
    RuntimeGroupOperationError,
    restore_runtime_generation_state,
    restore_runtime_group_state,
    snapshot_runtime_generation_state,
    snapshot_runtime_group_state,
)
from micromax_editor.plugins import PluginManager
from micromax_editor.runtime_policy import RuntimeRegistrationAuthority
from micromax_editor.search import SearchState


def _manager() -> tuple[Editor, PluginManager]:
    ed = Editor()
    install_editor_hostcalls(ed)
    pm = PluginManager(ed.vm)
    ed.plugin_manager = pm
    return ed, pm


def _plugin(root: Path, name: str, source: str) -> Path:
    plug = root / name
    plug.mkdir()
    (plug / "init.mx").write_text(source, encoding="utf-8")
    return plug


def _command_plugin_source(label: str, doc: str) -> str:
    return "\n".join(
        [
            f': {label}-cmd ( args -- ok ) drop 1 ;',
            ': init',
            f'  \' {label}-cmd "same" "{doc}" "ed.cmd-add" hostcall drop',
            ';',
            '',
        ]
    )


def test_unload_cleanup_failure_aborts_false_unload_and_restores_partial_sweep(tmp_path: Path) -> None:
    root = tmp_path / "plugins"
    root.mkdir()
    _plugin(root, "alpha", _command_plugin_source("old", "old command"))

    ed, pm = _manager()
    assert [p.name for p in pm.load_tree(root)] == ["alpha"]
    old_plugin = pm.plugins["alpha"]
    assert ed.command_dispatcher.get("same") is not None

    def broken_search_cleanup(group: str) -> int:
        assert group == "plugin:alpha"
        raise RuntimeError("search cleanup broke")

    ed.remove_search_group = broken_search_cleanup  # type: ignore[method-assign]

    with pytest.raises(RuntimeGroupOperationError) as raised:
        pm.unload("alpha")

    assert "plugin unload cleanup" in str(raised.value)
    assert "search cleanup broke" in str(raised.value)
    assert pm.plugins["alpha"] is old_plugin
    assert ed.vm.modules["alpha"] == old_plugin.wid
    same = ed.command_dispatcher.get("same")
    assert same is not None
    assert same.doc == "old command"
    assert same.group == "plugin:alpha"
    assert any(report is raised.value.report for report in pm.runtime_group_failures())
    assert any(name == "alpha" and "search cleanup broke" in err for name, err in pm.load_errors)


def test_reload_old_cleanup_failure_keeps_old_plugin_and_scrubs_staged_generation(tmp_path: Path) -> None:
    root = tmp_path / "plugins"
    root.mkdir()
    plug = _plugin(root, "alpha", _command_plugin_source("old", "old command"))

    ed, pm = _manager()
    assert [p.name for p in pm.load_tree(root)] == ["alpha"]
    old_plugin = pm.plugins["alpha"]
    assert ed.command_dispatcher.get("same").doc == "old command"  # type: ignore[union-attr]

    (plug / "init.mx").write_text(_command_plugin_source("new", "new command"), encoding="utf-8")

    def broken_search_cleanup(group: str) -> int:
        if group == "plugin:alpha":
            raise RuntimeError("old cleanup broke")
        return 0

    ed.remove_search_group = broken_search_cleanup  # type: ignore[method-assign]

    with pytest.raises(RuntimeGroupOperationError) as raised:
        pm.reload("alpha")

    assert "reload cleanup old generation" in str(raised.value)
    assert pm.plugins["alpha"] is old_plugin
    assert ed.vm.modules["alpha"] == old_plugin.wid
    same = ed.command_dispatcher.get("same")
    assert same is not None
    assert same.doc == "old command"
    assert same.group == "plugin:alpha"
    assert all("#reload" not in group for group in ed.command_dispatcher.groups())
    assert any(name == "alpha" and "old cleanup broke" in err for name, err in pm.load_errors)


def test_reload_retag_failure_restores_old_plugin_instead_of_promoting_partial_stage(tmp_path: Path) -> None:
    root = tmp_path / "plugins"
    root.mkdir()
    plug = _plugin(root, "alpha", _command_plugin_source("old", "old command"))

    ed, pm = _manager()
    assert [p.name for p in pm.load_tree(root)] == ["alpha"]
    old_plugin = pm.plugins["alpha"]

    (plug / "init.mx").write_text(_command_plugin_source("new", "new command"), encoding="utf-8")

    def broken_search_retag(old: str, new: str) -> int:
        assert old.startswith("plugin:alpha#reload")
        assert new == "plugin:alpha"
        raise RuntimeError("retag search broke")

    ed.retag_search_group = broken_search_retag  # type: ignore[method-assign]

    with pytest.raises(RuntimeGroupOperationError) as raised:
        pm.reload("alpha")

    assert "reload promote staged generation" in str(raised.value)
    assert pm.plugins["alpha"] is old_plugin
    assert ed.vm.modules["alpha"] == old_plugin.wid
    same = ed.command_dispatcher.get("same")
    assert same is not None
    assert same.doc == "old command"
    assert same.group == "plugin:alpha"
    assert all("#reload" not in group for group in ed.command_dispatcher.groups())
    assert any(name == "alpha" and "retag search broke" in err for name, err in pm.load_errors)


def test_force_unload_cleanup_failure_uses_narrow_group_snapshot_not_options(tmp_path: Path) -> None:
    root = tmp_path / "plugins"
    root.mkdir()
    _plugin(root, "alpha", _command_plugin_source("old", "old command"))

    ed, pm = _manager()
    assert [p.name for p in pm.load_tree(root)] == ["alpha"]
    old_plugin = pm.plugins["alpha"]

    def option_snapshot_should_not_run():  # type: ignore[no-untyped-def]
        raise AssertionError("runtime-group cleanup should not snapshot unrelated options")

    def broken_search_cleanup(group: str) -> int:
        assert group == "plugin:alpha"
        raise RuntimeError("search cleanup broke after command removal")

    ed._snapshot_option_state = option_snapshot_should_not_run  # type: ignore[method-assign]
    ed.remove_search_group = broken_search_cleanup  # type: ignore[method-assign]

    with pytest.raises(RuntimeGroupOperationError) as raised:
        pm.unload("alpha", force=True)

    assert "plugin unload cleanup" in str(raised.value)
    assert "search cleanup broke after command removal" in str(raised.value)
    assert pm.plugins["alpha"] is old_plugin
    assert ed.vm.modules["alpha"] == old_plugin.wid
    same = ed.command_dispatcher.get("same")
    assert same is not None
    assert same.doc == "old command"
    assert same.group == "plugin:alpha"
    assert any(report is raised.value.report for report in pm.runtime_group_failures())



def test_runtime_group_snapshot_captures_only_touched_command_group() -> None:
    ed, _pm = _manager()

    def ok(_ed: Editor, _args: list[str]) -> bool:
        return True

    ed.register_command_checked("trusted-core", ok, doc="trusted core", group="trusted")
    ed.register_command_checked("alpha-owned", ok, doc="alpha command", group="plugin:alpha")

    snap = snapshot_runtime_group_state(ed.vm, groups=("plugin:alpha",))

    assert snap.command_state is not None
    assert snap.command_state.groups == ("plugin:alpha",)
    assert sorted(snap.command_state.commands) == ["alpha-owned"]
    assert "trusted-core" not in snap.command_state.commands



def test_runtime_group_snapshot_captures_only_touched_action_keymap_timer_groups() -> None:
    ed, _pm = _manager()

    def ok(_ed: Editor) -> bool:
        return True

    ed.actions.register("trusted-action", ok, doc="trusted", group="trusted")
    ed.actions.register("alpha-action", ok, doc="alpha", group="plugin:alpha")
    ed.keymap.bind("Ctrl-T", "trusted-action", group="trusted")
    ed.keymap.bind("Ctrl-A", "alpha-action", group="plugin:alpha")
    trusted_timer = ed.timers.schedule(now=0.0, delay_ms=1000, xt="trusted", group="trusted")
    alpha_timer = ed.timers.schedule(now=0.0, delay_ms=1000, xt="alpha", group="plugin:alpha")

    snap = snapshot_runtime_group_state(ed.vm, groups=("plugin:alpha",))

    assert snap.action_state is not None
    assert snap.action_state.groups == ("plugin:alpha",)
    assert sorted(snap.action_state.actions) == ["alpha-action"]
    assert "trusted-action" not in snap.action_state.actions
    assert snap.keymap_state is not None
    assert snap.keymap_state.groups == ("plugin:alpha",)
    assert snap.keymap_state.bindings == {"global": {"Ctrl-A": ed.keymap.get_binding_exact("Ctrl-A")}}
    assert snap.timer_state is not None
    assert snap.timer_state.groups == ("plugin:alpha",)
    assert sorted(snap.timer_state.tasks) == [alpha_timer]
    assert trusted_timer not in snap.timer_state.tasks


def test_runtime_group_restore_does_not_rewind_unrelated_action_keymap_timer_changes() -> None:
    ed, _pm = _manager()

    def ok(_ed: Editor) -> bool:
        return True

    ed.actions.register("trusted-action", ok, doc="trusted", group="trusted")
    ed.actions.register("alpha-action", ok, doc="alpha", group="plugin:alpha")
    ed.keymap.bind("Ctrl-T", "trusted-action", group="trusted")
    ed.keymap.bind("Ctrl-A", "alpha-action", group="plugin:alpha")
    trusted_timer = ed.timers.schedule(now=0.0, delay_ms=1000, xt="trusted", group="trusted")
    alpha_timer = ed.timers.schedule(now=0.0, delay_ms=1000, xt="alpha", group="plugin:alpha")

    snap = snapshot_runtime_group_state(ed.vm, groups=("plugin:alpha",))

    ed.actions.remove("alpha-action")
    ed.actions.remove("trusted-action")
    ed.keymap.unbind("Ctrl-A")
    ed.keymap.unbind("Ctrl-T")
    ed.timers.cancel(alpha_timer)
    ed.timers.cancel(trusted_timer)

    restore_runtime_group_state(ed.vm, snap)

    assert ed.actions.get("alpha-action") is not None
    assert ed.actions.get("alpha-action").group == "plugin:alpha"  # type: ignore[union-attr]
    assert ed.keymap.get_binding_exact("Ctrl-A") is not None
    assert ed.keymap.get_binding_exact("Ctrl-A").group == "plugin:alpha"  # type: ignore[union-attr]
    assert ed.timers.get(alpha_timer) is not None
    assert ed.timers.get(alpha_timer).canceled is False  # type: ignore[union-attr]

    assert ed.actions.get("trusted-action") is None
    assert ed.keymap.get_binding_exact("Ctrl-T") is None
    assert ed.timers.get(trusted_timer) is not None
    assert ed.timers.get(trusted_timer).canceled is True  # type: ignore[union-attr]


def test_runtime_group_snapshot_captures_only_touched_hook_and_mark_groups() -> None:
    ed, _pm = _manager()
    ed.new_buffer("main", "")

    alpha_hook = HookWord(
        name="ed.test.alpha",
        handlers=[
            HookHandler(xt="alpha", group="plugin:alpha"),
            HookHandler(xt="co-located-trusted", group="trusted"),
        ],
    )
    trusted_hook = HookWord(
        name="ed.test.trusted",
        handlers=[HookHandler(xt="trusted-only", group="trusted")],
    )
    ed.vm.wordlists[ed.vm.current_wid]["ed.test.alpha"] = alpha_hook
    ed.vm.wordlists[ed.vm.current_wid]["ed.test.trusted"] = trusted_hook
    ed.marks["alpha-mark"] = ("main", Cursor(0, 0))
    ed._mark_authority["alpha-mark"] = RuntimeRegistrationAuthority(group="plugin:alpha")
    ed.marks["trusted-mark"] = ("main", Cursor(0, 1))
    ed._mark_authority["trusted-mark"] = RuntimeRegistrationAuthority(group="trusted")

    snap = snapshot_runtime_group_state(ed.vm, groups=("plugin:alpha",))

    assert snap.hook_state is not None
    assert snap.hook_state.groups == ("plugin:alpha",)
    assert sorted(name for _wid, name in snap.hook_state.handlers) == ["ed.test.alpha"]
    assert "ed.test.trusted" not in [name for _wid, name in snap.hook_state.handlers]
    assert snap.mark_state is not None
    assert snap.mark_state.groups == ("plugin:alpha",)
    assert sorted(snap.mark_state.marks) == ["alpha-mark"]
    assert "trusted-mark" not in snap.mark_state.marks


def test_runtime_group_restore_does_not_rewind_unrelated_hook_or_mark_changes() -> None:
    ed, _pm = _manager()
    ed.new_buffer("main", "")

    alpha_hook = HookWord(
        name="ed.test.alpha",
        handlers=[HookHandler(xt="alpha", group="plugin:alpha")],
    )
    trusted_hook = HookWord(
        name="ed.test.trusted",
        handlers=[HookHandler(xt="trusted-only", group="trusted")],
    )
    ed.vm.wordlists[ed.vm.current_wid]["ed.test.alpha"] = alpha_hook
    ed.vm.wordlists[ed.vm.current_wid]["ed.test.trusted"] = trusted_hook
    ed.marks["alpha-mark"] = ("main", Cursor(0, 0))
    ed._mark_authority["alpha-mark"] = RuntimeRegistrationAuthority(group="plugin:alpha")
    ed.marks["trusted-mark"] = ("main", Cursor(0, 1))
    ed._mark_authority["trusted-mark"] = RuntimeRegistrationAuthority(group="trusted")

    snap = snapshot_runtime_group_state(ed.vm, groups=("plugin:alpha",))

    alpha_hook.handlers.clear()
    trusted_hook.handlers.clear()
    ed.marks.pop("alpha-mark")
    ed._mark_authority.pop("alpha-mark")
    ed.marks.pop("trusted-mark")
    ed._mark_authority.pop("trusted-mark")

    restore_runtime_group_state(ed.vm, snap)

    assert [handler.group for handler in alpha_hook.handlers] == ["plugin:alpha"]
    assert trusted_hook.handlers == []
    assert "alpha-mark" in ed.marks
    assert ed._mark_authority["alpha-mark"].group == "plugin:alpha"
    assert "trusted-mark" not in ed.marks
    assert "trusted-mark" not in ed._mark_authority


def test_retag_failure_restores_hook_handler_groups_and_mark_groups() -> None:
    ed, pm = _manager()
    ed.new_buffer("main", "")
    old = "plugin:alpha#reload1"
    new = "plugin:alpha"

    hook = HookWord(
        name="ed.test.alpha",
        handlers=[
            HookHandler(xt="alpha", group=old),
            HookHandler(xt="trusted", group="trusted"),
        ],
    )
    ed.vm.wordlists[ed.vm.current_wid]["ed.test.alpha"] = hook
    ed.marks["alpha-mark"] = ("main", Cursor(0, 0))
    ed._mark_authority["alpha-mark"] = RuntimeRegistrationAuthority(group=old)

    def broken_clipboard_retag(_old: str, _new: str) -> int:
        assert _old == old
        assert _new == new
        raise RuntimeError("clipboard retag broke after hooks and marks")

    ed.retag_clipboard_group = broken_clipboard_retag  # type: ignore[method-assign]

    with pytest.raises(RuntimeGroupOperationError) as raised:
        pm._retag_group_or_restore("alpha", old, new, "test retag")

    assert "clipboard retag broke after hooks and marks" in str(raised.value)
    assert [handler.group for handler in hook.handlers] == [old, "trusted"]
    assert ed._mark_authority["alpha-mark"].group == old


def test_retag_failure_restores_only_touched_command_group() -> None:
    ed, pm = _manager()

    def ok(_ed: Editor, _args: list[str]) -> bool:
        return True

    ed.register_command_checked("trusted-core", ok, doc="trusted core", group="trusted")
    ed.register_command_checked("alpha-owned", ok, doc="staged command", group="plugin:alpha#reload1")
    trusted_before = ed.command_dispatcher.get("trusted-core")

    def broken_action_retag(old: str, new: str) -> int:
        assert old == "plugin:alpha#reload1"
        assert new == "plugin:alpha"
        raise RuntimeError("action retag broke after command promotion")

    ed.actions.retag_group = broken_action_retag  # type: ignore[method-assign]

    with pytest.raises(RuntimeGroupOperationError) as raised:
        pm._retag_group_or_restore(
            "alpha",
            "plugin:alpha#reload1",
            "plugin:alpha",
            "test retag",
        )

    assert "action retag broke after command promotion" in str(raised.value)
    assert ed.command_dispatcher.get("trusted-core") is trusted_before
    owned = ed.command_dispatcher.get("alpha-owned")
    assert owned is not None
    assert owned.group == "plugin:alpha#reload1"
    assert owned.doc == "staged command"


def test_unload_generation_cleanup_failure_restores_group_cleanup_and_delayed_state(tmp_path: Path) -> None:
    root = tmp_path / "plugins"
    root.mkdir()
    _plugin(root, "alpha", _command_plugin_source("old", "old command"))

    ed, pm = _manager()
    assert [p.name for p in pm.load_tree(root)] == ["alpha"]
    old_plugin = pm.plugins["alpha"]
    ed.recent_files[:] = ["trusted.txt", "alpha.txt"]
    ed.recent_files_authority[:] = [
        RuntimeRegistrationAuthority(script_context=False, group="trusted"),
        RuntimeRegistrationAuthority(
            script_context=True,
            plugin_load_root=str(old_plugin.root),
            plugin_generation=old_plugin.generation,
            group="plugin:alpha",
        ),
    ]

    def broken_recent_generation(plugin_root: object, generation: object) -> int:
        assert str(plugin_root) == str(old_plugin.root)
        assert int(generation) == old_plugin.generation
        ed.recent_files.clear()
        raise RuntimeError("recent generation cleanup broke")

    ed.remove_plugin_recent_files_generation = broken_recent_generation  # type: ignore[method-assign]

    with pytest.raises(RuntimeGroupOperationError) as raised:
        pm.unload("alpha", force=True)

    assert "plugin unload cleanup" in str(raised.value)
    assert "generation-cleanup" in str(raised.value)
    assert "recent generation cleanup broke" in str(raised.value)
    assert pm.plugins["alpha"] is old_plugin
    assert ed.vm.modules["alpha"] == old_plugin.wid
    same = ed.command_dispatcher.get("same")
    assert same is not None
    assert same.doc == "old command"
    assert same.group == "plugin:alpha"
    assert ed.recent_files == ["alpha.txt"]
    assert any(report is raised.value.report for report in pm.runtime_group_failures())


def test_reload_commit_generation_cleanup_failure_restores_old_runtime_after_group_sweep(tmp_path: Path) -> None:
    root = tmp_path / "plugins"
    root.mkdir()
    plug = _plugin(root, "alpha", _command_plugin_source("old", "old command"))

    ed, pm = _manager()
    assert [p.name for p in pm.load_tree(root)] == ["alpha"]
    old_plugin = pm.plugins["alpha"]
    ed.recent_files[:] = ["trusted.txt", "alpha.txt"]
    ed.recent_files_authority[:] = [
        RuntimeRegistrationAuthority(script_context=False, group="trusted"),
        RuntimeRegistrationAuthority(
            script_context=True,
            plugin_load_root=str(old_plugin.root),
            plugin_generation=old_plugin.generation,
            group="plugin:alpha",
        ),
    ]

    plug.joinpath("init.mx").write_text(_command_plugin_source("new", "new command"), encoding="utf-8")
    calls = 0

    def broken_on_commit(plugin_root: object, generation: object) -> int:
        nonlocal calls
        assert str(plugin_root) == str(old_plugin.root)
        assert int(generation) == old_plugin.generation
        calls += 1
        if calls == 1:
            return 0
        ed.recent_files.clear()
        raise RuntimeError("commit generation cleanup broke")

    ed.remove_plugin_recent_files_generation = broken_on_commit  # type: ignore[method-assign]

    with pytest.raises(RuntimeGroupOperationError) as raised:
        pm.reload("alpha")

    assert calls == 2
    assert "plugin reload cleanup old generation" in str(raised.value)
    assert "generation-cleanup" in str(raised.value)
    assert "commit generation cleanup broke" in str(raised.value)
    assert pm.plugins["alpha"] is old_plugin
    assert ed.vm.modules["alpha"] == old_plugin.wid
    same = ed.command_dispatcher.get("same")
    assert same is not None
    assert same.doc == "old command"
    assert same.group == "plugin:alpha"
    assert ed.recent_files == ["trusted.txt", "alpha.txt"]
    assert all("#reload" not in group for group in ed.command_dispatcher.groups())
    assert any(name == "alpha" and "commit generation cleanup broke" in err for name, err in pm.load_errors)



def _seed_delayed_group_rows(ed: Editor, *, group: str = "plugin:alpha") -> None:
    ed.recent_files[:] = ["trusted.txt", "alpha.txt"]
    ed.recent_files_authority[:] = [
        RuntimeRegistrationAuthority(group="trusted"),
        RuntimeRegistrationAuthority(group=group),
    ]
    ed._palette_recent[:] = [("command", "trusted-cmd"), ("command", "alpha-cmd")]
    ed._palette_recent_authority[:] = [
        RuntimeRegistrationAuthority(group="trusted"),
        RuntimeRegistrationAuthority(group=group),
    ]
    ed.history["command"] = ["trusted-cmd", "alpha-cmd"]
    ed.history_authority["command"] = [
        RuntimeRegistrationAuthority(group="trusted"),
        RuntimeRegistrationAuthority(group=group),
    ]
    ed._saved_cursors = {
        "trusted.txt": {"line": 1, "col": 2},
        "alpha.txt": {"line": 3, "col": 4},
    }
    ed._saved_cursors_authority = {
        "trusted.txt": RuntimeRegistrationAuthority(group="trusted"),
        "alpha.txt": RuntimeRegistrationAuthority(group=group),
    }


def test_runtime_group_snapshot_captures_only_touched_delayed_rows() -> None:
    ed, _pm = _manager()
    _seed_delayed_group_rows(ed)

    snap = snapshot_runtime_group_state(ed.vm, groups=("plugin:alpha",))

    assert snap.recent_files_state is not None
    assert [entry.value for entry in snap.recent_files_state.entries] == ["alpha.txt"]
    assert snap.palette_recent_state is not None
    assert [entry.value for entry in snap.palette_recent_state.entries] == [("command", "alpha-cmd")]
    assert snap.prompt_history_state is not None
    assert [(entry.kind, entry.value) for entry in snap.prompt_history_state.entries] == [("command", "alpha-cmd")]
    assert snap.saved_cursors_state is not None
    assert snap.saved_cursors_state.cursors == {"alpha.txt": {"line": 3, "col": 4}}
    assert "trusted.txt" not in snap.saved_cursors_state.cursors


def test_runtime_group_restore_does_not_rewind_unrelated_delayed_rows() -> None:
    ed, _pm = _manager()
    _seed_delayed_group_rows(ed)

    snap = snapshot_runtime_group_state(ed.vm, groups=("plugin:alpha",))

    ed.recent_files.clear()
    ed.recent_files_authority.clear()
    ed._palette_recent.clear()
    ed._palette_recent_authority.clear()
    ed.history["command"] = []
    ed.history_authority["command"] = []
    ed._saved_cursors.clear()
    ed._saved_cursors_authority.clear()

    restore_runtime_group_state(ed.vm, snap)

    assert ed.recent_files == ["alpha.txt"]
    assert [auth.group for auth in ed.recent_files_authority] == ["plugin:alpha"]
    assert ed._palette_recent == [("command", "alpha-cmd")]
    assert [auth.group for auth in ed._palette_recent_authority] == ["plugin:alpha"]
    assert ed.history["command"] == ["alpha-cmd"]
    assert [auth.group for auth in ed.history_authority["command"]] == ["plugin:alpha"]
    assert ed._saved_cursors == {"alpha.txt": {"line": 3, "col": 4}}
    assert ed._saved_cursors_authority["alpha.txt"].group == "plugin:alpha"
    assert "trusted.txt" not in ed._saved_cursors_authority


def test_retag_failure_restores_delayed_row_groups() -> None:
    ed, pm = _manager()
    old = "plugin:alpha#reload1"
    new = "plugin:alpha"
    _seed_delayed_group_rows(ed, group=old)

    def broken_search_retag(_old: str, _new: str) -> int:
        assert _old == old
        assert _new == new
        raise RuntimeError("search retag broke after delayed row promotion")

    ed.retag_search_group = broken_search_retag  # type: ignore[method-assign]

    with pytest.raises(RuntimeGroupOperationError) as raised:
        pm._retag_group_or_restore("alpha", old, new, "test retag")

    assert "search retag broke after delayed row promotion" in str(raised.value)
    assert [auth.group for auth in ed.recent_files_authority] == ["trusted", old]
    assert [auth.group for auth in ed._palette_recent_authority] == ["trusted", old]
    assert [auth.group for auth in ed.history_authority["command"]] == ["trusted", old]
    assert ed._saved_cursors_authority["alpha.txt"].group == old
    assert ed._saved_cursors_authority["trusted.txt"].group == "trusted"


def _seed_singleton_group_rows(ed: Editor, *, group: str = "plugin:alpha") -> None:
    ed.clipboard_items = ["alpha clip"]
    ed.clipboard_kind = "chars"
    ed.clipboard_authority = RuntimeRegistrationAuthority(group=group)
    ed.clipboard_serial = 7
    ed.clipboard_from_script = True
    ed.search = SearchState(query="alpha", literal=True, case_sensitive=False)
    ed.search_authority = RuntimeRegistrationAuthority(group=group)
    ed._help_stack[:] = [{"topic": "trusted-help"}, {"topic": "alpha-help"}]
    ed._help_stack_authority[:] = [
        RuntimeRegistrationAuthority(group="trusted"),
        RuntimeRegistrationAuthority(group=group),
    ]
    ed._help_forward_stack[:] = [{"topic": "alpha-forward"}]
    ed._help_forward_stack_authority[:] = [RuntimeRegistrationAuthority(group=group)]
    ed._help_session_entry = {"topic": "alpha-session"}
    ed._help_session_authority = RuntimeRegistrationAuthority(group=group)


def test_runtime_group_snapshot_captures_only_touched_singleton_and_help_rows() -> None:
    ed, _pm = _manager()
    _seed_singleton_group_rows(ed)

    snap = snapshot_runtime_group_state(ed.vm, groups=("plugin:alpha",))

    assert snap.clipboard_state is not None
    assert snap.clipboard_state.captured is True
    assert snap.clipboard_state.items == ("alpha clip",)
    assert snap.clipboard_state.authority.group == "plugin:alpha"
    assert snap.search_state is not None
    assert snap.search_state.captured is True
    assert snap.search_state.state[0].query == "alpha"
    assert snap.search_state.state[1].group == "plugin:alpha"
    assert snap.help_history_state is not None
    assert [(entry.lane, entry.value["topic"]) for entry in snap.help_history_state.entries] == [
        ("back", "alpha-help"),
        ("forward", "alpha-forward"),
    ]
    assert snap.help_history_state.session_captured is True
    assert snap.help_history_state.session_entry == {"topic": "alpha-session"}


def test_runtime_group_snapshot_skips_unrelated_singleton_registers() -> None:
    ed, _pm = _manager()
    _seed_singleton_group_rows(ed, group="trusted")

    snap = snapshot_runtime_group_state(ed.vm, groups=("plugin:alpha",))

    assert snap.clipboard_state is not None
    assert snap.clipboard_state.captured is False
    assert snap.search_state is not None
    assert snap.search_state.captured is False
    assert snap.help_history_state is not None
    assert snap.help_history_state.entries == ()
    assert snap.help_history_state.session_captured is False


def test_runtime_group_restore_does_not_rewind_unrelated_singleton_or_help_changes() -> None:
    ed, _pm = _manager()
    _seed_singleton_group_rows(ed)

    snap = snapshot_runtime_group_state(ed.vm, groups=("plugin:alpha",))

    ed.clipboard_items = ["trusted clip"]
    ed.clipboard_kind = "lines"
    ed.clipboard_authority = RuntimeRegistrationAuthority(group="trusted")
    ed.clipboard_serial = 99
    ed.clipboard_from_script = False
    ed.search = SearchState(query="trusted", literal=False, case_sensitive=True)
    ed.search_authority = RuntimeRegistrationAuthority(group="trusted")
    ed._help_stack[:] = [{"topic": "trusted-new"}]
    ed._help_stack_authority[:] = [RuntimeRegistrationAuthority(group="trusted")]
    ed._help_forward_stack[:] = []
    ed._help_forward_stack_authority[:] = []
    ed._help_session_entry = {"topic": "trusted-session"}
    ed._help_session_authority = RuntimeRegistrationAuthority(group="trusted")

    restore_runtime_group_state(ed.vm, snap)

    assert ed.clipboard_items == ["alpha clip"]
    assert ed.clipboard_kind == "chars"
    assert ed.clipboard_authority.group == "plugin:alpha"
    assert ed.clipboard_serial == 7
    assert ed.clipboard_from_script is True
    assert ed.search.query == "alpha"
    assert ed.search_authority.group == "plugin:alpha"
    assert [entry["topic"] for entry in ed._help_stack] == ["trusted-new", "alpha-help"]
    assert [auth.group for auth in ed._help_stack_authority] == ["trusted", "plugin:alpha"]
    assert [entry["topic"] for entry in ed._help_forward_stack] == ["alpha-forward"]
    assert [auth.group for auth in ed._help_forward_stack_authority] == ["plugin:alpha"]
    assert ed._help_session_entry == {"topic": "alpha-session"}
    assert ed._help_session_authority.group == "plugin:alpha"


def test_runtime_group_restore_leaves_unrelated_singletons_when_nothing_captured() -> None:
    ed, _pm = _manager()
    _seed_singleton_group_rows(ed, group="trusted")

    snap = snapshot_runtime_group_state(ed.vm, groups=("plugin:alpha",))

    ed.clipboard_items = ["new trusted clip"]
    ed.clipboard_kind = "items"
    ed.clipboard_authority = RuntimeRegistrationAuthority(group="trusted")
    ed.search = SearchState(query="new trusted", literal=True, case_sensitive=True)
    ed.search_authority = RuntimeRegistrationAuthority(group="trusted")
    ed._help_stack[:] = [{"topic": "trusted-only"}]
    ed._help_stack_authority[:] = [RuntimeRegistrationAuthority(group="trusted")]
    ed._help_session_entry = {"topic": "trusted-session"}
    ed._help_session_authority = RuntimeRegistrationAuthority(group="trusted")

    restore_runtime_group_state(ed.vm, snap)

    assert ed.clipboard_items == ["new trusted clip"]
    assert ed.clipboard_authority.group == "trusted"
    assert ed.search.query == "new trusted"
    assert ed.search_authority.group == "trusted"
    assert ed._help_stack == [{"topic": "trusted-only"}]
    assert [auth.group for auth in ed._help_stack_authority] == ["trusted"]
    assert ed._help_session_entry == {"topic": "trusted-session"}
    assert ed._help_session_authority.group == "trusted"


def test_retag_failure_restores_clipboard_search_and_help_groups() -> None:
    ed, pm = _manager()
    old = "plugin:alpha#reload1"
    new = "plugin:alpha"
    _seed_singleton_group_rows(ed, group=old)

    def broken_recovery_retag(_old: str, _new: str) -> int:
        assert _old == old
        assert _new == new
        raise RuntimeError("recovery retag broke after singleton promotion")

    ed.retag_recovery_group = broken_recovery_retag  # type: ignore[method-assign]

    with pytest.raises(RuntimeGroupOperationError) as raised:
        pm._retag_group_or_restore("alpha", old, new, "test retag")

    assert "recovery retag broke after singleton promotion" in str(raised.value)
    assert ed.clipboard_authority.group == old
    assert ed.search_authority.group == old
    assert [auth.group for auth in ed._help_stack_authority] == ["trusted", old]
    assert [auth.group for auth in ed._help_forward_stack_authority] == [old]
    assert ed._help_session_authority.group == old


def test_plugin_unload_feedback_points_to_cleanup_diagnostics(tmp_path: Path) -> None:
    root = tmp_path / "plugins"
    root.mkdir()
    _plugin(root, "alpha", _command_plugin_source("old", "old command"))

    ed, pm = _manager()
    assert [p.name for p in pm.load_tree(root)] == ["alpha"]

    def broken_search_cleanup(group: str) -> int:
        assert group == "plugin:alpha"
        raise RuntimeError("search cleanup broke for hint")

    ed.remove_search_group = broken_search_cleanup  # type: ignore[method-assign]

    ed.messages.clear()
    assert ed.exec_command_line("plugin unload alpha") is False

    assert ed.messages[0] == "plugin unload: alpha [error]"
    assert "search cleanup broke for hint" in ed.messages[1]
    assert "still loaded · see plugin cleanup alpha" in ed.messages[1]
    assert "alpha" in pm.plugins


def test_plugin_cleanup_command_surfaces_retained_cleanup_report(tmp_path: Path) -> None:
    root = tmp_path / "plugins"
    root.mkdir()
    _plugin(root, "alpha", _command_plugin_source("old", "old command"))

    ed, pm = _manager()
    assert [p.name for p in pm.load_tree(root)] == ["alpha"]

    def broken_search_cleanup(group: str) -> int:
        assert group == "plugin:alpha"
        raise RuntimeError("search cleanup broke for ux")

    ed.remove_search_group = broken_search_cleanup  # type: ignore[method-assign]

    with pytest.raises(RuntimeGroupOperationError):
        pm.unload("alpha", force=True)

    ed.messages.clear()
    assert ed.exec_command_line("plugin cleanup alpha") is True
    assert ed.messages[0] == "plugin cleanup alpha: 1 failure(s)"
    assert ed.messages[1].startswith("  - alpha cleanup search.remove_search_group:")
    assert "search cleanup broke for ux" in ed.messages[1]

    ed.messages.clear()
    assert ed.exec_command_line("plugin cleanup") is True
    assert ed.messages[0] == "plugin cleanup: 1 plugin(s), 1 failure(s)"
    assert "alpha cleanup search.remove_search_group" in ed.messages[1]

    ed.vm.stack.append("alpha")
    ed.vm.eval('"ed.plugin-cleanup-failure-rows" hostcall')
    rows = ed.vm.stack.pop()
    assert rows == [[
        "alpha",
        "cleanup",
        "plugin:alpha",
        "",
        "search",
        "remove_search_group",
        "RuntimeError: search cleanup broke for ux",
    ]]


def test_plugin_cleanup_failure_persisted_log_survives_new_editor(tmp_path: Path) -> None:
    root = tmp_path / "plugins"
    root.mkdir()
    _plugin(root, "alpha", _command_plugin_source("old", "old command"))
    persist = tmp_path / "persist"
    persist.mkdir()

    ed, pm = _manager()
    ed.options.set("cap.persist", "true")
    ed.options.set("cap.persist-root", str(persist))
    ed.options.set("plugin.cleanup-log.persist", "true")
    ed.options.set("plugin.cleanup-log.file", "plugin-cleanup.jsonl")
    assert [p.name for p in pm.load_tree(root)] == ["alpha"]

    def broken_search_cleanup(group: str) -> int:
        assert group == "plugin:alpha"
        raise RuntimeError("search cleanup broke durably")

    ed.remove_search_group = broken_search_cleanup  # type: ignore[method-assign]

    with pytest.raises(RuntimeGroupOperationError):
        pm.unload("alpha", force=True)

    log_path = persist / "plugin-cleanup.jsonl"
    records = [json.loads(line) for line in log_path.read_text(encoding="utf-8").splitlines()]
    assert records[-1]["plugin"] == "alpha"
    assert records[-1]["surface"] == "search"
    assert "search cleanup broke durably" in records[-1]["detail"]

    ed2, _pm2 = _manager()
    ed2.options.set("cap.persist", "true")
    ed2.options.set("cap.persist-root", str(persist))
    ed2.options.set("plugin.cleanup-log.persist", "true")
    ed2.options.set("plugin.cleanup-log.file", "plugin-cleanup.jsonl")

    assert ed2.plugin_cleanup_failure_rows("alpha") == [[
        "alpha",
        "cleanup",
        "plugin:alpha",
        "",
        "search",
        "remove_search_group",
        "RuntimeError: search cleanup broke durably",
    ]]

    assert ed2.exec_command_line("plugin cleanup alpha") is True
    assert ed2.messages[0] == "plugin cleanup alpha: 1 failure(s)"
    assert "alpha cleanup search.remove_search_group" in ed2.messages[1]


def test_plugin_cleanup_failure_log_requires_cap_persist(tmp_path: Path) -> None:
    root = tmp_path / "plugins"
    root.mkdir()
    _plugin(root, "alpha", _command_plugin_source("old", "old command"))
    persist = tmp_path / "persist"

    ed, pm = _manager()
    ed.options.set("cap.persist-root", str(persist))
    ed.options.set("plugin.cleanup-log.persist", "true")
    ed.options.set("plugin.cleanup-log.file", "plugin-cleanup.jsonl")
    assert [p.name for p in pm.load_tree(root)] == ["alpha"]

    def broken_search_cleanup(group: str) -> int:
        assert group == "plugin:alpha"
        raise RuntimeError("search cleanup broke without cap")

    ed.remove_search_group = broken_search_cleanup  # type: ignore[method-assign]

    with pytest.raises(RuntimeGroupOperationError):
        pm.unload("alpha", force=True)

    assert not (persist / "plugin-cleanup.jsonl").exists()
    assert ed.plugin_cleanup_log_rows("alpha") == []


def test_plugin_cleanup_command_reports_empty_and_unknown_targets(tmp_path: Path) -> None:
    root = tmp_path / "plugins"
    root.mkdir()
    _plugin(root, "alpha", _command_plugin_source("old", "old command"))

    ed, pm = _manager()
    assert [p.name for p in pm.load_tree(root)] == ["alpha"]

    ed.messages.clear()
    assert ed.exec_command_line("plugin cleanup alpha") is True
    assert ed.messages == ["plugin cleanup alpha: 0 cleanup failure(s)"]

    ed.messages.clear()
    assert ed.exec_command_line("plugin cleanup missing") is False
    assert ed.messages == ["plugin cleanup: no such plugin: missing"]



def _cursor_state_at(line: int, col: int) -> tuple[list[Cursor], list[Cursor | None], list[int], int]:
    return ([Cursor(line, col)], [None], [line * 100 + col + 1], 0)


def _seed_recovery_group_rows(ed: Editor, *, group: str = "plugin:alpha"):
    ed.new_buffer("main", "alpha\ntrusted\n")
    eb = ed.cur()
    eb.sel_stack[:] = [_cursor_state_at(0, 0), _cursor_state_at(1, 0)]
    eb.sel_stack_authority[:] = [
        RuntimeRegistrationAuthority(group="trusted"),
        RuntimeRegistrationAuthority(group=group),
    ]
    eb.jump_list[:] = [_cursor_state_at(0, 1), _cursor_state_at(1, 1)]
    eb.jump_list_authority[:] = [
        RuntimeRegistrationAuthority(group="trusted"),
        RuntimeRegistrationAuthority(group=group),
    ]
    eb.jump_index = 1
    return eb


def test_runtime_group_snapshot_captures_only_touched_recovery_rows() -> None:
    ed, _pm = _manager()
    _seed_recovery_group_rows(ed)

    snap = snapshot_runtime_group_state(ed.vm, groups=("plugin:alpha",))

    assert snap.recovery_state is not None
    assert len(snap.recovery_state.buffers) == 1
    buf = snap.recovery_state.buffers[0]
    assert [row.index for row in buf.selection_rows] == [1]
    assert [row.index for row in buf.jump_rows] == [1]
    assert buf.selection_rows[0].authority.group == "plugin:alpha"
    assert buf.jump_rows[0].authority.group == "plugin:alpha"


def test_runtime_group_restore_does_not_rewind_unrelated_recovery_rows() -> None:
    ed, _pm = _manager()
    eb = _seed_recovery_group_rows(ed)

    snap = snapshot_runtime_group_state(ed.vm, groups=("plugin:alpha",))

    eb.sel_stack[:] = [_cursor_state_at(2, 0)]
    eb.sel_stack_authority[:] = [RuntimeRegistrationAuthority(group="trusted")]
    eb.jump_list[:] = [_cursor_state_at(2, 1)]
    eb.jump_list_authority[:] = [RuntimeRegistrationAuthority(group="trusted")]
    eb.jump_index = 0

    restore_runtime_group_state(ed.vm, snap)

    assert [auth.group for auth in eb.sel_stack_authority] == ["trusted", "plugin:alpha"]
    assert [auth.group for auth in eb.jump_list_authority] == ["trusted", "plugin:alpha"]
    assert eb.jump_index == 1
    assert eb.sel_stack[0][0][0] == Cursor(2, 0)
    assert eb.sel_stack[1][0][0] == Cursor(1, 0)
    assert eb.jump_list[0][0][0] == Cursor(2, 1)
    assert eb.jump_list[1][0][0] == Cursor(1, 1)


def _seed_interaction_group_rows(ed: Editor, *, group: str = "plugin:alpha"):
    from micromax_editor.commandbar import Prompt
    from micromax_editor.editor import ActiveKeyMode, QueryReplaceSession

    ed.new_buffer("main", "alpha\n")
    eb = ed.cur()
    eb.sel_anchors[0] = Cursor(0, 2)
    ed.key_mode_stack[:] = [
        ActiveKeyMode("trusted", group="trusted"),
        ActiveKeyMode("alpha", group=group),
        ActiveKeyMode("qreplace", capture=True, group=group),
        ActiveKeyMode("openurl", capture=True, group=group),
    ]
    ed.prompt = Prompt("command", text="alpha")
    ed.prompt.group = group
    ed.qreplace = QueryReplaceSession(
        buffer_name="main",
        search="a",
        value="b",
        literal=True,
        authority=RuntimeRegistrationAuthority(group=group),
    )
    ed._pending_open_url = "https://example.invalid"
    ed._pending_open_url_source = "alpha.md"
    ed._pending_open_url_authority = RuntimeRegistrationAuthority(group=group)
    return eb


def test_runtime_group_snapshot_captures_only_touched_interaction_rows() -> None:
    ed, _pm = _manager()
    _seed_interaction_group_rows(ed)

    snap = snapshot_runtime_group_state(ed.vm, groups=("plugin:alpha",))

    assert snap.interaction_state is not None
    assert [entry.value.name for entry in snap.interaction_state.key_modes] == ["alpha", "qreplace", "openurl"]
    assert snap.interaction_state.prompt_captured is True
    assert snap.interaction_state.prompt.text == "alpha"
    assert snap.interaction_state.qreplace_captured is True
    assert snap.interaction_state.qreplace.search == "a"
    assert snap.interaction_state.qreplace_cursor is not None
    assert snap.interaction_state.open_url_captured is True
    assert snap.interaction_state.open_url == "https://example.invalid"


def test_runtime_group_snapshot_skips_unrelated_interaction_rows() -> None:
    ed, _pm = _manager()
    _seed_interaction_group_rows(ed, group="trusted")

    snap = snapshot_runtime_group_state(ed.vm, groups=("plugin:alpha",))

    assert snap.interaction_state is not None
    assert snap.interaction_state.key_modes == ()
    assert snap.interaction_state.prompt_captured is False
    assert snap.interaction_state.qreplace_captured is False
    assert snap.interaction_state.open_url_captured is False


def test_runtime_group_restore_does_not_rewind_unrelated_interactions_when_nothing_captured() -> None:
    from micromax_editor.commandbar import Prompt
    from micromax_editor.editor import ActiveKeyMode

    ed, _pm = _manager()
    _seed_interaction_group_rows(ed, group="trusted")

    snap = snapshot_runtime_group_state(ed.vm, groups=("plugin:alpha",))

    ed.key_mode_stack[:] = [ActiveKeyMode("trusted-new", group="trusted")]
    ed.prompt = Prompt("command", text="trusted-new")
    ed.prompt.group = "trusted"
    ed.qreplace = None
    ed._pending_open_url = "https://trusted.invalid"
    ed._pending_open_url_source = "trusted.md"
    ed._pending_open_url_authority = RuntimeRegistrationAuthority(group="trusted")

    restore_runtime_group_state(ed.vm, snap)

    assert [km.name for km in ed.key_mode_stack] == ["trusted-new"]
    assert ed.prompt is not None and ed.prompt.text == "trusted-new"
    assert ed.qreplace is None
    assert ed._pending_open_url == "https://trusted.invalid"
    assert ed._pending_open_url_authority.group == "trusted"


def test_remove_interaction_group_does_not_drop_trusted_named_keymodes() -> None:
    from micromax_editor.editor import ActiveKeyMode, QueryReplaceSession

    ed, _pm = _manager()
    _seed_interaction_group_rows(ed)
    ed.key_mode_stack.insert(0, ActiveKeyMode("qreplace", capture=True, group="trusted"))
    ed.key_mode_stack.insert(1, ActiveKeyMode("openurl", capture=True, group="trusted"))
    ed.qreplace = QueryReplaceSession(
        buffer_name="main",
        search="a",
        value="b",
        literal=True,
        authority=RuntimeRegistrationAuthority(group="plugin:alpha"),
    )

    removed = ed.remove_interaction_group("plugin:alpha")

    assert removed >= 3
    assert [(km.name, km.group) for km in ed.key_mode_stack] == [("qreplace", "trusted"), ("openurl", "trusted"), ("trusted", "trusted")]
    assert ed.qreplace is None
    assert ed._pending_open_url is None


def test_retag_failure_restores_recovery_and_interaction_groups() -> None:
    ed, pm = _manager()
    old = "plugin:alpha#reload1"
    new = "plugin:alpha"
    eb = _seed_recovery_group_rows(ed, group=old)
    _seed_interaction_group_rows(ed, group=old)

    def broken_search_retag(_old: str, _new: str) -> int:
        assert _old == old
        assert _new == new
        raise RuntimeError("search retag broke after recovery and interactions")

    ed.retag_search_group = broken_search_retag  # type: ignore[method-assign]

    with pytest.raises(RuntimeGroupOperationError) as raised:
        pm._retag_group_or_restore("alpha", old, new, "test retag")

    assert "search retag broke after recovery and interactions" in str(raised.value)
    assert [auth.group for auth in eb.sel_stack_authority] == ["trusted", old]
    assert [auth.group for auth in eb.jump_list_authority] == ["trusted", old]
    assert [km.group for km in ed.key_mode_stack if km.group != "trusted"] == [old, old, old]
    assert ed.prompt is not None and ed.prompt.group == old
    assert ed.qreplace is not None and ed.qreplace.authority.group == old
    assert ed._pending_open_url_authority.group == old


def _plugin_generation_auth(root: Path, generation: int, *, group: str = "plugin:alpha") -> RuntimeRegistrationAuthority:
    return RuntimeRegistrationAuthority(
        script_context=True,
        plugin_load_root=str(root),
        plugin_generation=int(generation),
        group=str(group),
    )


def test_runtime_generation_snapshot_scopes_nonmacro_delayed_rows(tmp_path: Path) -> None:
    ed, _pm = _manager()
    root = tmp_path / "plugins" / "alpha"
    root.parent.mkdir()
    root.mkdir()
    alpha = _plugin_generation_auth(root, 1)
    trusted = RuntimeRegistrationAuthority(script_context=False, group="trusted")

    ed.new_buffer("main", "")
    eb = ed.cur()
    trusted_recovery = ([Cursor(1, 2)], [None], [1], 0)
    alpha_recovery = ([Cursor(3, 4)], [None], [2], 0)
    eb.sel_stack[:] = [trusted_recovery, alpha_recovery]
    eb.sel_stack_authority[:] = [trusted, alpha]

    ed.recent_files[:] = ["trusted.txt", "alpha.txt"]
    ed.recent_files_authority[:] = [trusted, alpha]
    ed._palette_recent[:] = [("command", "trusted"), ("command", "alpha")]
    ed._palette_recent_authority[:] = [trusted, alpha]
    ed.history["command"] = ["trusted", "alpha"]
    ed.history_authority["command"] = [trusted, alpha]
    ed._saved_cursors = {
        "trusted.txt": {"line": 1, "col": 2},
        "alpha.txt": {"line": 3, "col": 4},
    }
    ed._saved_cursors_authority = {"trusted.txt": trusted, "alpha.txt": alpha}
    ed.clipboard_items = ["alpha clip"]
    ed.clipboard_kind = "items"
    ed.clipboard_authority = alpha
    ed.search = SearchState(query="alpha", literal=True, case_sensitive=False)
    ed.search_authority = alpha
    ed._help_stack[:] = [{"topic": "trusted"}, {"topic": "alpha"}]
    ed._help_stack_authority[:] = [trusted, alpha]

    snap = snapshot_runtime_generation_state(
        ed.vm,
        plugin_load_root=root,
        plugin_generation=1,
    )

    assert snap.recent_files is None
    assert snap.cursor_state is None
    assert snap.recent_files_generation_state is not None
    assert [entry.value for entry in snap.recent_files_generation_state.entries] == ["alpha.txt"]
    assert snap.palette_recent_generation_state is not None
    assert [entry.value for entry in snap.palette_recent_generation_state.entries] == [("command", "alpha")]
    assert snap.prompt_history_generation_state is not None
    assert [(entry.kind, entry.value) for entry in snap.prompt_history_generation_state.entries] == [("command", "alpha")]
    assert snap.saved_cursors_generation_state is not None
    assert snap.saved_cursors_generation_state.cursors == {"alpha.txt": {"line": 3, "col": 4}}
    assert snap.clipboard_generation_state is not None
    assert snap.clipboard_generation_state.captured is True
    assert snap.search_generation_state is not None
    assert snap.search_generation_state.captured is True
    assert snap.help_history_generation_state is not None
    assert [(entry.lane, entry.value) for entry in snap.help_history_generation_state.entries] == [("back", {"topic": "alpha"})]
    assert snap.recovery_generation_state is not None
    assert len(snap.recovery_generation_state.buffers) == 1
    assert len(snap.recovery_generation_state.buffers[0].selection_rows) == 1

    ed.recent_files.clear()
    ed.recent_files_authority.clear()
    ed._palette_recent.clear()
    ed._palette_recent_authority.clear()
    ed.history["command"] = []
    ed.history_authority["command"] = []
    ed._saved_cursors.clear()
    ed._saved_cursors_authority.clear()
    ed._clear_clipboard_register()
    ed._clear_search_register()
    ed._help_stack.clear()
    ed._help_stack_authority.clear()
    eb.sel_stack.clear()
    eb.sel_stack_authority.clear()

    restore_runtime_generation_state(ed.vm, snap)

    assert ed.recent_files == ["alpha.txt"]
    assert ed._palette_recent == [("command", "alpha")]
    assert ed.history["command"] == ["alpha"]
    assert ed._saved_cursors == {"alpha.txt": {"line": 3, "col": 4}}
    assert ed.clipboard_items == ["alpha clip"]
    assert ed.search.query == "alpha"
    assert ed._help_stack == [{"topic": "alpha"}]
    assert len(eb.sel_stack) == 1
    assert eb.sel_stack[0][0][0] == Cursor(3, 4)


def test_runtime_generation_snapshot_scopes_interaction_rows(tmp_path: Path) -> None:
    ed, _pm = _manager()
    root = tmp_path / "plugins" / "alpha"
    root.parent.mkdir()
    root.mkdir()
    alpha = _plugin_generation_auth(root, 1)
    trusted = RuntimeRegistrationAuthority(script_context=False, group="trusted")

    ed.new_buffer("main", "one one\n")
    ed.key_mode_stack[:] = [
        ActiveKeyMode("trusted", group="trusted"),
        ActiveKeyMode(
            "alpha",
            capture=True,
            script_context=True,
            plugin_load_root=str(root),
            plugin_generation=1,
            script_origin_id="origin-alpha",
            group="plugin:alpha",
        ),
    ]
    ed.prompt = Prompt("command", text="alpha command")
    ed.prompt.script_context = True
    ed.prompt.plugin_load_root = str(root)
    ed.prompt.plugin_generation = 1
    ed.prompt.script_origin_id = "origin-alpha"
    ed.prompt.group = "plugin:alpha"
    ed.qreplace = QueryReplaceSession(
        buffer_name="main",
        search="one",
        value="two",
        literal=True,
        authority=alpha,
    )
    ed._pending_open_url = "https://alpha.invalid"
    ed._pending_open_url_source = "command"
    ed._pending_open_url_authority = alpha

    snap = snapshot_runtime_generation_state(
        ed.vm,
        plugin_load_root=root,
        plugin_generation=1,
    )

    assert snap.interaction_generation_state is not None
    assert [entry.value.name for entry in snap.interaction_generation_state.key_modes] == ["alpha"]
    assert snap.interaction_generation_state.prompt_captured is True
    assert snap.interaction_generation_state.qreplace_captured is True
    assert snap.interaction_generation_state.open_url_captured is True
    assert snap.cursor_state is None

    ed.key_mode_stack[:] = [ActiveKeyMode("trusted-new", group="trusted")]
    ed.prompt = Prompt("command", text="trusted")
    ed.prompt.group = "trusted"
    ed.qreplace = None
    ed._pending_open_url = "https://trusted.invalid"
    ed._pending_open_url_source = "trusted"
    ed._pending_open_url_authority = trusted

    restore_runtime_generation_state(ed.vm, snap)

    assert [(km.name, km.group) for km in ed.key_mode_stack] == [
        ("trusted-new", "trusted"),
        ("alpha", "plugin:alpha"),
    ]
    assert ed.prompt is not None and ed.prompt.text == "alpha command"
    assert ed.qreplace is not None and ed.qreplace.search == "one"
    assert ed._pending_open_url == "https://alpha.invalid"
    assert ed._pending_open_url_authority.plugin_generation == 1


def _macro_step(
    name: str,
    *,
    root: Path | None = None,
    generation: int | None = None,
    trusted: bool = False,
) -> MacroStep:
    return MacroStep(
        kind="command",
        name=str(name),
        payload={},
        script_context=not trusted,
        plugin_load_root=str(root) if root is not None else None,
        plugin_generation=generation,
        script_origin_id=f"origin-{name}" if not trusted else None,
    )


def test_runtime_generation_snapshot_scopes_macro_slots_and_recording(tmp_path: Path) -> None:
    ed, _pm = _manager()
    root = tmp_path / "plugins" / "alpha"
    root.parent.mkdir()
    root.mkdir()
    alpha_step = _macro_step("alpha-step", root=root, generation=1)
    last_step = _macro_step("last-step", root=root, generation=1)
    trusted_step = _macro_step("trusted-step", trusted=True)
    trusted_new = _macro_step("trusted-new", trusted=True)

    ed.macros.clear()
    ed.macros["trusted"] = [trusted_step]
    ed.macros["alpha"] = [alpha_step]
    ed.macro[:] = [last_step]
    ed.macros["last"] = ed.macro
    ed.macro_recording = True
    ed._macro_target = "alpha-record"
    ed._macro_buffer[:] = [alpha_step]
    ed._macro_prev_last = [trusted_step]
    ed._macro_recording_script_context = True
    ed._macro_recording_plugin_load_root = str(root)
    ed._macro_recording_plugin_generation = 1
    ed._macro_recording_script_origin_id = "origin-alpha"

    snap = snapshot_runtime_generation_state(
        ed.vm,
        plugin_load_root=root,
        plugin_generation=1,
    )

    assert snap.macros is None
    assert snap.macro_default is None
    assert snap.macro_generation_state is not None
    assert [(entry.index, entry.name) for entry in snap.macro_generation_state.slots] == [
        (1, "alpha"),
        (2, "last"),
    ]
    assert snap.macro_generation_state.recording is not None
    assert snap.macro_generation_state.recording.target == "alpha-record"

    ed.macros["trusted"] = [trusted_new]
    ed.macros.pop("alpha", None)
    ed.macro[:] = []
    ed.macros["last"] = ed.macro
    ed.macro_recording = False
    ed._macro_buffer.clear()
    ed._macro_target = "last"
    ed._macro_prev_last = None
    ed._reset_macro_recording_origin()

    restore_runtime_generation_state(ed.vm, snap)

    assert ed.macros["trusted"] == [trusted_new]
    assert ed.macros["alpha"] == [alpha_step]
    assert ed.macros["last"] is ed.macro
    assert ed.macro == [last_step]
    assert list(ed.macros) == ["trusted", "alpha", "last"]
    assert ed.macro_recording is True
    assert ed._macro_target == "alpha-record"
    assert ed._macro_buffer == [alpha_step]
    assert ed._macro_prev_last == [trusted_step]
    assert ed._macro_recording_plugin_load_root == str(root)
    assert ed._macro_recording_plugin_generation == 1


def test_generation_cleanup_failure_restores_macro_tail_without_rewinding_trusted_slots(tmp_path: Path) -> None:
    root = tmp_path / "plugins"
    root.mkdir()
    _plugin(root, "alpha", _command_plugin_source("old", "old command"))

    ed, pm = _manager()
    assert [p.name for p in pm.load_tree(root)] == ["alpha"]
    old_plugin = pm.plugins["alpha"]
    alpha_step = _macro_step("alpha-step", root=old_plugin.root, generation=old_plugin.generation)
    trusted_step = _macro_step("trusted-step", trusted=True)
    trusted_new = _macro_step("trusted-new", trusted=True)
    ed.macros.clear()
    ed.macros["trusted"] = [trusted_step]
    ed.macros["alpha"] = [alpha_step]
    ed.macros["last"] = ed.macro

    def broken_recent_generation(plugin_root: object, generation: object) -> int:
        assert str(plugin_root) == str(old_plugin.root)
        assert int(generation) == old_plugin.generation
        ed.macros["trusted"] = [trusted_new]
        raise RuntimeError("recent generation cleanup broke after macros")

    ed.remove_plugin_recent_files_generation = broken_recent_generation  # type: ignore[method-assign]

    with pytest.raises(RuntimeGroupOperationError) as raised:
        pm.unload("alpha", force=True)

    assert "recent generation cleanup broke after macros" in str(raised.value)
    assert pm.plugins["alpha"] is old_plugin
    assert ed.macros["trusted"] == [trusted_new]
    assert ed.macros["alpha"] == [alpha_step]
    assert ed.command_dispatcher.get("same") is not None
