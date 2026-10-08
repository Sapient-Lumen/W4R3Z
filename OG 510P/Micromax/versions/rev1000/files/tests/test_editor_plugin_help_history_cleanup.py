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


def _help_source(first: str, second: str, *, suffix: str = "") -> str:
    return (
        ": init\n"
        f'  "{first}" "ed.help-doc" hostcall drop\n'
        f'  "{second}" "ed.help-doc" hostcall drop\n'
        ";\n"
        f"{suffix}\n"
    )


def test_plugin_unload_removes_plugin_owned_help_history(tmp_path: Path) -> None:
    root = tmp_path / "plugins"
    root.mkdir()
    _plugin(root, "helpful", _help_source("help-browser", "setext-headings"))

    ed, pm = _manager()
    assert [p.name for p in pm.load_tree(root)] == ["helpful"]
    plugin = pm.plugins["helpful"]

    assert ed._help_stack
    assert ed._help_stack_authority[-1].group == "plugin:helpful"
    assert ed._help_stack_authority[-1].plugin_generation == plugin.generation
    assert ed._help_session_authority.group == "plugin:helpful"
    assert ed._help_session_authority.plugin_generation == plugin.generation

    pm.unload("helpful")

    assert ed._help_stack == []
    assert ed._help_stack_authority == []
    assert ed._help_forward_stack == []
    assert ed._help_forward_stack_authority == []
    assert ed._help_session_entry is None
    assert ed._help_session_authority.script_context is False


def test_plugin_unload_does_not_remove_user_help_history(tmp_path: Path) -> None:
    root = tmp_path / "plugins"
    root.mkdir()
    _plugin(root, "quiet", ": init ;\n")

    ed, pm = _manager()
    assert ed.open_help_doc("help-browser") is True
    assert ed.open_help_doc("setext-headings") is True
    assert ed._help_stack
    assert ed._help_stack_authority[-1].script_context is False

    assert [p.name for p in pm.load_tree(root)] == ["quiet"]
    pm.unload("quiet")

    assert ed._help_stack
    assert ed._help_stack_authority[-1].script_context is False
    assert ed._help_session_entry is not None
    assert ed._help_session_authority.script_context is False


def test_plugin_reload_retags_help_history_for_later_unload(tmp_path: Path) -> None:
    root = tmp_path / "plugins"
    root.mkdir()
    plug = _plugin(root, "helpful", _help_source("help-browser", "setext-headings"))

    ed, pm = _manager()
    assert [p.name for p in pm.load_tree(root)] == ["helpful"]
    old_generation = pm.plugins["helpful"].generation

    (plug / "init.mx").write_text(
        _help_source("help-browser", "multiline-setext-headings"),
        encoding="utf-8",
    )
    new_plugin = pm.reload("helpful")

    assert new_plugin.generation != old_generation
    assert ed._help_stack
    assert ed._help_stack_authority[-1].group == "plugin:helpful"
    assert ed._help_stack_authority[-1].plugin_generation == new_plugin.generation
    assert ed._help_session_authority.group == "plugin:helpful"
    assert ed._help_session_authority.plugin_generation == new_plugin.generation

    pm.unload("helpful")
    assert ed._help_stack == []
    assert ed._help_session_entry is None


def test_failed_plugin_reload_restores_help_history(tmp_path: Path) -> None:
    root = tmp_path / "plugins"
    root.mkdir()
    plug = _plugin(root, "helpful", _help_source("help-browser", "setext-headings"))

    ed, pm = _manager()
    assert [p.name for p in pm.load_tree(root)] == ["helpful"]
    old_plugin = pm.plugins["helpful"]
    old_stack = list(ed._help_stack)
    old_session = ed._help_session_entry

    (plug / "init.mx").write_text(
        _help_source("help-browser", "multiline-setext-headings", suffix="missing-word-from-help-reload"),
        encoding="utf-8",
    )
    with pytest.raises(MicromaxError):
        pm.reload("helpful")

    assert pm.plugins["helpful"] is old_plugin
    assert ed._help_stack == old_stack
    assert ed._help_stack_authority[-1].group == "plugin:helpful"
    assert ed._help_stack_authority[-1].plugin_generation == old_plugin.generation
    assert ed._help_session_entry == old_session
    assert ed._help_session_authority.group == "plugin:helpful"
    assert ed._help_session_authority.plugin_generation == old_plugin.generation
