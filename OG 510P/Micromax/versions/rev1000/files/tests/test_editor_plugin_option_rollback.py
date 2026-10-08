from __future__ import annotations

from pathlib import Path

import pytest

from micromax.vm import MicromaxError
from micromax_editor.editor import Editor
from micromax_editor.micromax_bridge import install_editor_hostcalls
from micromax_editor.plugins import PluginManager


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


def test_failed_plugin_load_rolls_back_global_option_mutation(tmp_path: Path) -> None:
    root = tmp_path / "plugins"
    root.mkdir()
    _plugin(root, "badopts", ': init set tabsize 9 missing-word-after-option ;\n')

    ed, pm = _manager()
    assert ed.options.get("tabsize") == 4

    assert pm.load_tree(root) == []

    assert "badopts" not in pm.plugins
    assert ed.options.get("tabsize") == 4
    assert any(name == "badopts" and "missing-word-after-option" in err for name, err in pm.load_errors)


def test_failed_plugin_load_rolls_back_local_option_mutation(tmp_path: Path) -> None:
    root = tmp_path / "plugins"
    root.mkdir()
    _plugin(root, "badlocal", ': init setlocal tabsize 11 missing-word-after-local-option ;\n')

    ed, pm = _manager()
    ed.new_buffer("scratch", "")
    eb = ed.cur()
    assert "tabsize" not in eb.local_options

    assert pm.load_tree(root) == []

    assert "badlocal" not in pm.plugins
    assert "tabsize" not in eb.local_options
    assert ed.options.get("tabsize", local=eb.local_options) == 4


def test_failed_plugin_reload_restores_prior_option_state(tmp_path: Path) -> None:
    root = tmp_path / "plugins"
    root.mkdir()
    plug = _plugin(root, "opts", ': init set tabsize 5 ;\n')

    ed, pm = _manager()
    assert [p.name for p in pm.load_tree(root)] == ["opts"]
    old_plugin = pm.plugins["opts"]
    assert ed.options.get("tabsize") == 5

    (plug / "init.mx").write_text(': init set tabsize 9 missing-word-from-reload-option ;\n', encoding="utf-8")
    with pytest.raises(MicromaxError):
        pm.reload("opts")

    assert pm.plugins["opts"] is old_plugin
    assert ed.options.get("tabsize") == 5
    assert any(name == "opts" and "missing-word-from-reload-option" in err for name, err in pm.load_errors)


def test_failed_plugin_command_callback_rolls_back_option_mutation(tmp_path: Path) -> None:
    root = tmp_path / "plugins"
    root.mkdir()
    _plugin(
        root,
        "cmdopts",
        '\n'.join(
            [
                ': run drop set tabsize 13 missing-word-from-command-option 1 ;',
                '\' run "optionboom" "mutate option then fail" "ed.cmd-add" hostcall drop',
                '',
            ]
        ),
    )

    ed, pm = _manager()
    assert [p.name for p in pm.load_tree(root)] == ["cmdopts"]
    assert ed.options.get("tabsize") == 4

    assert ed.exec_command_line("optionboom") is False

    assert ed.options.get("tabsize") == 4
    assert any("missing-word-from-command-option" in msg for msg in ed.messages)



def test_plugin_unload_discards_deinit_option_mutation(tmp_path: Path) -> None:
    root = tmp_path / "plugins"
    root.mkdir()
    _plugin(root, "opts", ": init set tabsize 5 ;\n: deinit set tabsize 9 ;\n")

    ed, pm = _manager()
    assert [p.name for p in pm.load_tree(root)] == ["opts"]
    assert ed.options.get("tabsize") == 5

    pm.unload("opts")

    assert "opts" not in pm.plugins
    assert ed.options.get("tabsize") == 5


def test_option_snapshot_restores_renamed_live_buffer_by_identity() -> None:
    ed, _pm = _manager()
    ed.new_buffer("scratch", "")
    eb = ed.cur()
    before = dict(eb.local_options)
    snap = ed._snapshot_option_state()

    eb.local_options["readonly"] = True
    del ed.buffers["scratch"]
    ed.buffers["renamed"] = eb
    eb.name = "renamed"
    ed.active = "renamed"

    ed._restore_option_state(snap)

    assert "renamed" in ed.buffers
    assert ed.buffers["renamed"] is eb
    assert eb.local_options == before


def test_option_snapshot_does_not_restore_replacement_buffer_with_reused_name() -> None:
    ed, _pm = _manager()
    ed.new_buffer("scratch", "")
    original = ed.cur()
    snap = ed._snapshot_option_state()

    del ed.buffers["scratch"]
    ed.new_buffer("scratch", "")
    replacement = ed.cur()
    assert replacement is not original
    replacement.local_options["readonly"] = True

    ed._restore_option_state(snap)

    assert ed.buffers["scratch"] is replacement
    assert replacement.local_options["readonly"] is True


def test_broad_registration_option_snapshot_restore_uses_editor_owner() -> None:
    from micromax_editor.plugin_runtime import snapshot_runtime_registrations, restore_runtime_registrations

    ed, _pm = _manager()
    events: list[str] = []
    original_snapshot = ed.snapshot_option_state
    original_restore = ed.restore_option_state

    def snapshot_owner() -> object:
        events.append("snapshot")
        return original_snapshot()

    def restore_owner(snap: object) -> None:
        events.append("restore")
        original_restore(snap)

    ed.snapshot_option_state = snapshot_owner  # type: ignore[method-assign]
    ed.restore_option_state = restore_owner  # type: ignore[method-assign]

    ed.options.set("tabsize", "6")
    snap = snapshot_runtime_registrations(ed.vm)
    ed.options.set("tabsize", "13")

    restore_runtime_registrations(ed.vm, snap)

    assert events == ["snapshot", "restore"]
    assert ed.options.get("tabsize") == 6


def test_scoped_plugin_callback_option_snapshot_restore_uses_editor_owner(tmp_path: Path) -> None:
    from micromax_editor.plugin_runtime import snapshot_plugin_callback_state, restore_plugin_callback_state

    ed, _pm = _manager()
    root = tmp_path / "owned"
    root.mkdir()
    events: list[str] = []
    original_snapshot = ed.snapshot_option_state
    original_restore = ed.restore_option_state

    def snapshot_owner() -> object:
        events.append("snapshot")
        return original_snapshot()

    def restore_owner(snap: object) -> None:
        events.append("restore")
        original_restore(snap)

    ed.snapshot_option_state = snapshot_owner  # type: ignore[method-assign]
    ed.restore_option_state = restore_owner  # type: ignore[method-assign]

    ed.options.set("tabsize", "7")
    snap = snapshot_plugin_callback_state(
        ed.vm,
        group="plugin:owned",
        plugin_load_root=str(root),
        plugin_generation=3,
    )
    ed.options.set("tabsize", "17")

    restore_plugin_callback_state(ed.vm, snap)

    assert events == ["snapshot", "restore"]
    assert ed.options.get("tabsize") == 7
