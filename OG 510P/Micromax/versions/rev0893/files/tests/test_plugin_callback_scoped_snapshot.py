from __future__ import annotations

from pathlib import Path

from micromax_editor.editor import Editor, MacroStep
from micromax_editor.micromax_bridge import install_editor_hostcalls
from micromax_editor.plugin_runtime import (
    restore_plugin_callback_state,
    snapshot_plugin_callback_state,
)


def _editor() -> Editor:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer("*scratch*", "")
    return ed


def _ok(_ed: Editor, _args: list[str]) -> bool:
    return True


def test_scoped_plugin_callback_snapshot_restores_plugin_commands_only(tmp_path: Path) -> None:
    ed = _editor()
    root = tmp_path / "alpha"
    root.mkdir()

    ed.command_dispatcher.register("trusted", _ok, doc="trusted before", group="trusted")
    ed.command_dispatcher.register(
        "owned",
        _ok,
        doc="owned before",
        group="plugin:alpha",
        script_context=True,
        plugin_load_root=str(root),
        plugin_generation=7,
    )

    snap = snapshot_plugin_callback_state(
        ed.vm,
        group="plugin:alpha",
        plugin_load_root=str(root),
        plugin_generation=7,
    )

    assert snap.registrations is None
    assert snap.group_state is not None
    assert snap.group_state.command_state is not None
    assert sorted(snap.group_state.command_state.commands) == ["owned"]
    assert snap.generation_state is not None

    ed.command_dispatcher.register(
        "owned",
        _ok,
        doc="owned during callback",
        group="plugin:alpha",
        script_context=True,
        plugin_load_root=str(root),
        plugin_generation=7,
    )
    ed.command_dispatcher.register(
        "new-owned",
        _ok,
        doc="new owned",
        group="plugin:alpha",
        script_context=True,
        plugin_load_root=str(root),
        plugin_generation=7,
    )
    ed.command_dispatcher.register("trusted", _ok, doc="trusted changed elsewhere", group="trusted")

    restore_plugin_callback_state(ed.vm, snap)

    owned = ed.command_dispatcher.get("owned")
    assert owned is not None
    assert owned.doc == "owned before"
    assert owned.group == "plugin:alpha"
    assert ed.command_dispatcher.get("new-owned") is None
    trusted = ed.command_dispatcher.get("trusted")
    assert trusted is not None
    assert trusted.doc == "trusted changed elsewhere"


def test_scoped_plugin_callback_snapshot_restores_plugin_generation_macros_only(tmp_path: Path) -> None:
    ed = _editor()
    root = tmp_path / "alpha"
    root.mkdir()

    ed.set_macro(
        "trusted",
        [MacroStep(kind="command", name="command", payload={"cmdline": "trusted before"})],
    )
    ed.set_macro(
        "owned",
        [
            MacroStep(
                kind="command",
                name="command",
                payload={"cmdline": "owned before"},
                script_context=True,
                plugin_load_root=str(root),
                plugin_generation=7,
            )
        ],
    )

    snap = snapshot_plugin_callback_state(
        ed.vm,
        group="plugin:alpha",
        plugin_load_root=str(root),
        plugin_generation=7,
    )

    assert snap.registrations is None
    assert snap.generation_state is not None
    assert snap.generation_state.macro_generation_state is not None
    assert [slot.name for slot in snap.generation_state.macro_generation_state.slots] == ["owned"]

    ed.set_macro(
        "owned",
        [
            MacroStep(
                kind="command",
                name="command",
                payload={"cmdline": "owned during callback"},
                script_context=True,
                plugin_load_root=str(root),
                plugin_generation=7,
            )
        ],
    )
    ed.set_macro(
        "new-owned",
        [
            MacroStep(
                kind="command",
                name="command",
                payload={"cmdline": "new owned"},
                script_context=True,
                plugin_load_root=str(root),
                plugin_generation=7,
            )
        ],
    )
    ed.set_macro(
        "trusted",
        [MacroStep(kind="command", name="command", payload={"cmdline": "trusted changed elsewhere"})],
    )

    restore_plugin_callback_state(ed.vm, snap)

    assert ed.get_macro("owned")[0].payload == {"cmdline": "owned before"}
    assert ed.get_macro("new-owned") == []
    assert ed.get_macro("trusted")[0].payload == {"cmdline": "trusted changed elsewhere"}


def test_legacy_callback_snapshot_without_plugin_tokens_keeps_broad_registration_fallback() -> None:
    ed = _editor()
    snap = snapshot_plugin_callback_state(ed.vm)

    assert snap.registrations is not None
    assert snap.group_state is None
    assert snap.generation_state is None
