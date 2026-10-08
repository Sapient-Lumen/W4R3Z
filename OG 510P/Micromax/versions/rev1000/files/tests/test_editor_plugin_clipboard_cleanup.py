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


def _clipboard_source(payload: str, *, suffix: str = "") -> str:
    return f'''
: init
  "{payload}" "ed.set-clipboard" hostcall
;
{suffix}
'''


def test_plugin_unload_removes_plugin_owned_clipboard(tmp_path: Path) -> None:
    root = tmp_path / "plugins"
    root.mkdir()
    _plugin(root, "clip", _clipboard_source("owned"))

    ed, pm = _manager()
    assert [p.name for p in pm.load_tree(root)] == ["clip"]
    plugin = pm.plugins["clip"]

    assert ed.clipboard_text() == "owned"
    assert ed.clipboard_authority.group == "plugin:clip"
    assert ed.clipboard_authority.plugin_generation == plugin.generation

    pm.unload("clip")

    assert ed.clipboard_items == []
    assert ed.clipboard_kind == "items"
    assert ed.clipboard_authority.script_context is False
    assert ed.clipboard_from_script is False


def test_plugin_unload_does_not_remove_trusted_clipboard(tmp_path: Path) -> None:
    root = tmp_path / "plugins"
    root.mkdir()
    _plugin(root, "quiet", ": init ;\n")

    ed, pm = _manager()
    ed.set_clipboard_items(["trusted"], kind="items")
    assert [p.name for p in pm.load_tree(root)] == ["quiet"]

    pm.unload("quiet")

    assert ed.clipboard_text() == "trusted"
    assert ed.clipboard_authority.script_context is False


def test_plugin_reload_retags_new_clipboard_and_prunes_old_generation(tmp_path: Path) -> None:
    root = tmp_path / "plugins"
    root.mkdir()
    plug = _plugin(root, "clip", _clipboard_source("old"))

    ed, pm = _manager()
    assert [p.name for p in pm.load_tree(root)] == ["clip"]
    old_generation = pm.plugins["clip"].generation
    assert ed.clipboard_text() == "old"

    (plug / "init.mx").write_text(_clipboard_source("new"), encoding="utf-8")
    new_plugin = pm.reload("clip")

    assert new_plugin.generation != old_generation
    assert ed.clipboard_text() == "new"
    assert ed.clipboard_authority.group == "plugin:clip"
    assert ed.clipboard_authority.plugin_generation == new_plugin.generation

    pm.unload("clip")
    assert ed.clipboard_items == []


def test_plugin_reload_without_new_clipboard_drops_old_plugin_clipboard(tmp_path: Path) -> None:
    root = tmp_path / "plugins"
    root.mkdir()
    plug = _plugin(root, "clip", _clipboard_source("old"))

    ed, pm = _manager()
    assert [p.name for p in pm.load_tree(root)] == ["clip"]
    assert ed.clipboard_text() == "old"

    (plug / "init.mx").write_text(": init ;\n", encoding="utf-8")
    pm.reload("clip")

    assert ed.clipboard_items == []
    assert ed.clipboard_authority.script_context is False


def test_failed_plugin_reload_restores_clipboard_register(tmp_path: Path) -> None:
    root = tmp_path / "plugins"
    root.mkdir()
    plug = _plugin(root, "clip", _clipboard_source("old"))

    ed, pm = _manager()
    assert [p.name for p in pm.load_tree(root)] == ["clip"]
    old_plugin = pm.plugins["clip"]

    (plug / "init.mx").write_text(
        _clipboard_source("staged", suffix="missing-word-from-clipboard-reload"),
        encoding="utf-8",
    )
    with pytest.raises(MicromaxError):
        pm.reload("clip")

    assert pm.plugins["clip"] is old_plugin
    assert ed.clipboard_text() == "old"
    assert ed.clipboard_authority.group == "plugin:clip"
    assert ed.clipboard_authority.plugin_generation == old_plugin.generation
