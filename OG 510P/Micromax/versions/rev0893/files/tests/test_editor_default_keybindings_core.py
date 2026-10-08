from __future__ import annotations

from pathlib import Path

from micromax_editor.editor import Editor
from micromax_editor.micromax_bridge import install_editor_hostcalls
from micromax_editor.plugins import PluginManager


def _load_core_plugins(ed: Editor) -> PluginManager:
    install_editor_hostcalls(ed)
    pm = PluginManager(ed.vm)
    ed.plugin_manager = pm
    root = Path(__file__).resolve().parents[1] / 'plugins'
    pm.load_tree(root)
    return pm



def test_repo_default_plugins_load_cleanly() -> None:
    ed = Editor()
    pm = _load_core_plugins(ed)

    assert pm.load_errors == []
    assert "core" in pm.plugins
    assert "capdemo" in pm.plugins


def test_core_default_keybindings_for_pick_open_replace() -> None:
    ed = Editor()
    pm = _load_core_plugins(ed)
    ed.new_buffer('*scratch*', '')

    b_buf = ed.resolve_key_binding('Ctrl-b')
    assert b_buf is not None
    assert b_buf.action_spec == 'command:bufferpick'

    b_open = ed.resolve_key_binding('Ctrl-o')
    assert b_open is not None
    assert b_open.action_spec == 'command-edit:open '

    b_rep = ed.resolve_key_binding('Ctrl-r')
    assert b_rep is not None
    assert b_rep.action_spec == 'command-edit:replace '

    b_pal = ed.resolve_key_binding('Ctrl-Space')
    assert b_pal is not None
    assert b_pal.action_spec == 'CommandPalette'

    b_bind = ed.resolve_key_binding('Alt-g')
    assert b_bind is not None
    assert b_bind.action_spec == 'BindingPrompt'
