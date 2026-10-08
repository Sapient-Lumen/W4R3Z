from __future__ import annotations

import json
from pathlib import Path

import pytest

from micromax.vm import MicromaxError
from micromax_editor.startup import create_editor_runtime


def _plugin(root: Path, name: str, source: str = ': noop ;\n') -> Path:
    plug = root / name
    plug.mkdir()
    (plug / 'init.mx').write_text(source, encoding='utf-8')
    return plug


def _runtime(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, source: str = ': noop ;\n'):
    root = tmp_path / 'plugins'
    root.mkdir()
    plug = _plugin(root, 'probe', source)
    monkeypatch.setenv('MICROMAX_INIT', str(tmp_path / 'missing-init.mx'))
    runtime = create_editor_runtime(plugins_root=root, workspace_trust='trusted')
    return runtime, plug


def _configure_persisted_file_navigation(ed, tmp_path: Path) -> None:
    persist = tmp_path / 'persist'
    persist.mkdir(exist_ok=True)
    ed.options.set('cap.persist', 'true')
    ed.options.set('cap.persist-root', str(persist))
    ed.options.set('recent.persist', 'true')
    ed.options.set('recent.file', 'recent.json')
    ed.options.set('savecursor', 'true')
    ed.options.set('savecursor.file', 'cursor.json')


def _plugin_owned_recent_and_cursor(ed, plugin, doc: Path) -> str:
    norm = ed._normalize_path(str(doc))
    with ed.plugin_callback_context(plugin.root, plugin.group, plugin_generation=plugin.generation):
        with ed.script_context(origin_id='plugin:probe'):
            assert ed._push_recent_file(str(doc)) is True
            ed._saved_cursors[norm] = {'line': 2, 'col': 1}
            ed._saved_cursors_authority[norm] = ed._current_runtime_authority(kind='editor')
            ed._normalize_saved_cursor_authority()
            assert ed.save_saved_cursors() is True
    return norm


def test_plugin_unload_prunes_persisted_recent_and_saved_cursor_rows(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    runtime, _plug = _runtime(tmp_path, monkeypatch)
    ed = runtime.editor
    pm = runtime.plugin_manager
    plugin = pm.plugins['probe']
    doc = tmp_path / 'owned.txt'
    doc.write_text('alpha\nbeta\ngamma\n', encoding='utf-8')
    _configure_persisted_file_navigation(ed, tmp_path)

    norm = _plugin_owned_recent_and_cursor(ed, plugin, doc)
    assert ed.recent_files == [str(doc)]
    assert ed.recent_files_authority[0].group == 'plugin:probe'
    assert ed.recent_files_authority[0].plugin_generation == plugin.generation
    assert ed._saved_cursors[norm] == {'line': 2, 'col': 1}
    assert ed._saved_cursor_entry_authority(norm).group == 'plugin:probe'

    pm.unload('probe')

    assert str(doc) not in ed.recent_files
    assert norm not in ed._saved_cursors
    recent_path = tmp_path / 'persist' / 'recent.json'
    cursor_path = tmp_path / 'persist' / 'cursor.json'
    assert str(doc) not in json.loads(recent_path.read_text(encoding='utf-8'))
    assert norm not in json.loads(cursor_path.read_text(encoding='utf-8'))


def test_failed_plugin_reload_restores_file_navigation_rows(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    runtime, plug = _runtime(tmp_path, monkeypatch)
    ed = runtime.editor
    pm = runtime.plugin_manager
    old_plugin = pm.plugins['probe']
    doc = tmp_path / 'restore.txt'
    doc.write_text('alpha\nbeta\ngamma\n', encoding='utf-8')
    _configure_persisted_file_navigation(ed, tmp_path)
    norm = _plugin_owned_recent_and_cursor(ed, old_plugin, doc)

    (plug / 'init.mx').write_text('missing-word-from-failed-reload\n', encoding='utf-8')
    with pytest.raises(MicromaxError):
        pm.reload('probe')

    assert pm.plugins['probe'] is old_plugin
    assert ed.recent_files == [str(doc)]
    assert ed.recent_files_authority[0].plugin_generation == old_plugin.generation
    assert ed._saved_cursors[norm] == {'line': 2, 'col': 1}
    assert ed._saved_cursor_entry_authority(norm).plugin_generation == old_plugin.generation


def test_plugin_reload_retags_new_file_navigation_rows_for_later_unload(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    runtime, plug = _runtime(tmp_path, monkeypatch)
    ed = runtime.editor
    pm = runtime.plugin_manager
    old_plugin = pm.plugins['probe']
    doc1 = tmp_path / 'new-a.txt'
    doc2 = tmp_path / 'new-b.txt'
    doc1.write_text('alpha\nbeta\ngamma\n', encoding='utf-8')
    doc2.write_text('delta\n', encoding='utf-8')
    _configure_persisted_file_navigation(ed, tmp_path)
    ed.options.set('cap.fs-open', 'true')
    ed.options.set('cap.fs-root', str(tmp_path))

    (plug / 'init.mx').write_text(
        f'"{doc1}" "ed.open" hostcall drop drop\n'
        '2 1 "ed.set-cursor" hostcall\n'
        f'"{doc2}" "ed.open" hostcall drop drop\n',
        encoding='utf-8',
    )

    new_plugin = pm.reload('probe')
    assert new_plugin.generation != old_plugin.generation

    assert ed.recent_files[:2] == [str(doc2), str(doc1)]
    assert [a.group for a in ed.recent_files_authority[:2]] == ['plugin:probe', 'plugin:probe']
    assert [a.plugin_generation for a in ed.recent_files_authority[:2]] == [new_plugin.generation, new_plugin.generation]
    norm1 = ed._normalize_path(str(doc1))
    assert ed._saved_cursors[norm1] == {'line': 2, 'col': 1}
    assert ed._saved_cursor_entry_authority(norm1).group == 'plugin:probe'
    assert ed._saved_cursor_entry_authority(norm1).plugin_generation == new_plugin.generation

    pm.unload('probe')
    assert str(doc1) not in ed.recent_files
    assert str(doc2) not in ed.recent_files
    assert norm1 not in ed._saved_cursors
