from __future__ import annotations

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


def _palette_source(command: str, *, suffix: str = "") -> str:
    return (
        ': init\n'
        '  "" "ed.command-palette" hostcall\n'
        f'  "{command}" "ed.prompt-set" hostcall\n'
        '  "ed.prompt-submit" hostcall drop\n'
        ';\n'
        f'{suffix}\n'
    )


def _plugin(root: Path, name: str, source: str) -> Path:
    plug = root / name
    plug.mkdir()
    (plug / 'init.mx').write_text(source, encoding='utf-8')
    return plug


def test_plugin_unload_removes_plugin_owned_palette_recent_row(tmp_path: Path) -> None:
    root = tmp_path / 'plugins'
    root.mkdir()
    _plugin(root, 'pal', _palette_source('buffers'))

    ed, pm = _manager()
    assert [p.name for p in pm.load_tree(root)] == ['pal']
    plugin = pm.plugins['pal']

    assert ed._palette_recent == [('command', 'buffers')]
    auth = ed._palette_recent_authority[0]
    assert auth.group == 'plugin:pal'
    assert auth.plugin_generation == plugin.generation

    pm.unload('pal')

    assert ed._palette_recent == []
    assert ed._palette_recent_authority == []
    assert ed.command_palette_recent_rows() == []


def test_plugin_unload_does_not_remove_user_palette_recent_row(tmp_path: Path) -> None:
    root = tmp_path / 'plugins'
    root.mkdir()
    _plugin(root, 'quiet', ': init ;\n')

    ed, pm = _manager()
    assert ed._record_palette_recent('command', 'help') is True
    assert [p.name for p in pm.load_tree(root)] == ['quiet']

    pm.unload('quiet')

    assert ed._palette_recent == [('command', 'help')]
    assert ed._palette_recent_authority[0].script_context is False
    assert [row[0] for row in ed.command_palette_recent_rows()] == ['help']


def test_plugin_reload_retags_palette_recent_and_prunes_old_generation(tmp_path: Path) -> None:
    root = tmp_path / 'plugins'
    root.mkdir()
    plug = _plugin(root, 'pal', _palette_source('buffers'))

    ed, pm = _manager()
    assert [p.name for p in pm.load_tree(root)] == ['pal']
    old_generation = pm.plugins['pal'].generation
    assert ed._palette_recent == [('command', 'buffers')]

    (plug / 'init.mx').write_text(_palette_source('pwd'), encoding='utf-8')
    pm.reload('pal')

    assert ed._palette_recent == [('command', 'pwd')]
    auth = ed._palette_recent_authority[0]
    assert auth.group == 'plugin:pal'
    assert auth.plugin_generation == pm.plugins['pal'].generation
    assert auth.plugin_generation != old_generation

    pm.unload('pal')
    assert ed._palette_recent == []


def test_failed_plugin_reload_restores_palette_recent_row(tmp_path: Path) -> None:
    root = tmp_path / 'plugins'
    root.mkdir()
    plug = _plugin(root, 'pal', _palette_source('buffers'))

    ed, pm = _manager()
    assert [p.name for p in pm.load_tree(root)] == ['pal']
    old_generation = pm.plugins['pal'].generation

    (plug / 'init.mx').write_text(
        _palette_source('pwd', suffix='missingword-from-palette-reload'),
        encoding='utf-8',
    )
    with pytest.raises(Exception):
        pm.reload('pal')

    assert ed._palette_recent == [('command', 'buffers')]
    auth = ed._palette_recent_authority[0]
    assert auth.group == 'plugin:pal'
    assert auth.plugin_generation == old_generation
    assert any(name == 'pal' and 'missingword' in err for name, err in pm.load_errors)
