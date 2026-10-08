from __future__ import annotations

import json

import pytest

from micromax_editor.editor import Editor
from micromax_editor.plugin_runtime import restore_plugin_callback_state, snapshot_plugin_callback_state


def test_recent_persistence_requires_cap_persist(tmp_path) -> None:
    recent_file = tmp_path / 'recent.json'

    ed = Editor()
    ed.new_buffer('*scratch*', '')
    ed.options.set('recent.persist', 'true')
    ed.options.set('recent.file', str(recent_file))

    # Without cap.persist, nothing should be written.
    ed._push_recent_file('hello.txt')
    assert not recent_file.exists()

    # Enable persistence capability.
    ed.options.set('cap.persist', 'true')
    ed.options.set('cap.persist-root', str(tmp_path))
    ed._push_recent_file('hello.txt')
    assert recent_file.exists()
    data = json.loads(recent_file.read_text(encoding='utf-8'))
    assert isinstance(data, list)
    assert data and 'hello.txt' in data[0]


def test_persist_root_sandboxes_persistence_paths(tmp_path) -> None:
    root = tmp_path / 'persistroot'
    root.mkdir()
    outside = tmp_path / 'outside.json'

    ed = Editor()
    ed.new_buffer('*scratch*', '')
    ed.options.set('cap.persist', 'true')
    ed.options.set('cap.persist-root', str(root))

    ed.options.set('recent.persist', 'true')
    ed.options.set('recent.file', str(outside))

    ed._push_recent_file('x.txt')
    assert not outside.exists()


def test_prompt_history_persistence_roundtrip(tmp_path) -> None:
    root = tmp_path / 'persist'
    root.mkdir()

    ed = Editor()
    ed.new_buffer('*scratch*', '')
    ed.options.set('cap.persist', 'true')
    ed.options.set('cap.persist-root', str(root))
    ed.options.set('savehistory', 'true')
    ed.options.set('history.file', 'history.json')
    ed.options.set('history.limit', '50')

    # Push history; should auto-persist.
    ed._push_history('command', 'open foo.txt')
    hist_file = root / 'history.json'
    assert hist_file.exists()
    data = json.loads(hist_file.read_text(encoding='utf-8'))
    assert isinstance(data, dict)
    assert 'command' in data
    assert data['command'][-1] == 'open foo.txt'

    # New editor loads it.
    ed2 = Editor()
    ed2.new_buffer('*scratch*', '')
    ed2.options.set('cap.persist', 'true')
    ed2.options.set('cap.persist-root', str(root))
    ed2.options.set('savehistory', 'true')
    ed2.options.set('history.file', 'history.json')
    assert ed2.load_prompt_history() is True
    assert ed2.history.get('command') and ed2.history['command'][-1] == 'open foo.txt'


def test_savecursor_persistence_roundtrip_restores_cursor_on_open(tmp_path) -> None:
    root = tmp_path / 'persist'
    root.mkdir()
    doc = tmp_path / 'notes.txt'
    doc.write_text('alpha\nbeta\ngamma\n', encoding='utf-8')

    ed = Editor()
    ed.new_buffer('*scratch*', '')
    ed.options.set('cap.persist', 'true')
    ed.options.set('cap.persist-root', str(root))
    ed.options.set('savecursor', 'true')
    ed.options.set('savecursor.file', 'cursor.json')
    assert ed.open_file(str(doc)) is True

    eb = ed.cur()
    eb.cursors[0].line = 2
    eb.cursors[0].col = 3
    assert ed.close_buffer(force=True) is True

    cursor_file = root / 'cursor.json'
    assert cursor_file.exists()
    data = json.loads(cursor_file.read_text(encoding='utf-8'))
    norm = ed._normalize_path(str(doc))
    assert data[norm] == {'line': 2, 'col': 3}

    ed2 = Editor()
    ed2.new_buffer('*scratch*', '')
    ed2.options.set('cap.persist', 'true')
    ed2.options.set('cap.persist-root', str(root))
    ed2.options.set('savecursor', 'true')
    ed2.options.set('savecursor.file', 'cursor.json')
    assert ed2.load_saved_cursors() is True
    assert ed2.open_file(str(doc)) is True
    c = ed2.cur().cursors[0]
    assert (c.line, c.col) == (2, 3)


def test_savecursor_requires_cap_persist(tmp_path) -> None:
    doc = tmp_path / 'notes.txt'
    doc.write_text('alpha\n', encoding='utf-8')
    cursor_file = tmp_path / 'cursor.json'

    ed = Editor()
    ed.new_buffer('*scratch*', '')
    ed.options.set('savecursor', 'true')
    ed.options.set('savecursor.file', str(cursor_file))
    assert ed.open_file(str(doc)) is True
    ed.cur().cursors[0].col = 1
    assert ed.close_buffer(force=True) is True

    assert not cursor_file.exists()


def test_savecursor_clamps_to_shorter_reopened_file(tmp_path) -> None:
    root = tmp_path / 'persist'
    root.mkdir()
    doc = tmp_path / 'notes.txt'
    doc.write_text('alpha\nbeta\ngamma\n', encoding='utf-8')

    ed = Editor()
    ed.new_buffer('*scratch*', '')
    ed.options.set('cap.persist', 'true')
    ed.options.set('cap.persist-root', str(root))
    ed.options.set('savecursor', 'true')
    ed.options.set('savecursor.file', 'cursor.json')
    assert ed.open_file(str(doc)) is True
    ed.cur().cursors[0].line = 2
    ed.cur().cursors[0].col = 4
    assert ed.close_buffer(force=True) is True

    doc.write_text('x\n', encoding='utf-8')

    ed2 = Editor()
    ed2.new_buffer('*scratch*', '')
    ed2.options.set('cap.persist', 'true')
    ed2.options.set('cap.persist-root', str(root))
    ed2.options.set('savecursor', 'true')
    ed2.options.set('savecursor.file', 'cursor.json')
    assert ed2.load_saved_cursors() is True
    assert ed2.open_file(str(doc)) is True
    c = ed2.cur().cursors[0]
    assert (c.line, c.col) == (1, 0)


def test_parsecursor_target_overrides_saved_cursor_position(tmp_path) -> None:
    root = tmp_path / 'persist'
    root.mkdir()
    doc = tmp_path / 'notes.txt'
    doc.write_text('alpha\nbeta\ngamma\n', encoding='utf-8')

    ed = Editor()
    ed.new_buffer('*scratch*', '')
    ed.options.set('cap.persist', 'true')
    ed.options.set('cap.persist-root', str(root))
    ed.options.set('savecursor', 'true')
    ed.options.set('savecursor.file', 'cursor.json')
    assert ed.open_file(str(doc)) is True
    ed.cur().cursors[0].line = 2
    ed.cur().cursors[0].col = 4
    assert ed.close_buffer(force=True) is True

    ed2 = Editor()
    ed2.new_buffer('*scratch*', '')
    ed2.options.set('cap.persist', 'true')
    ed2.options.set('cap.persist-root', str(root))
    ed2.options.set('savecursor', 'true')
    ed2.options.set('savecursor.file', 'cursor.json')
    ed2.options.set('parsecursor', 'true')
    assert ed2.load_saved_cursors() is True
    assert ed2.open_file(f'{doc}:2:1') is True
    c = ed2.cur().cursors[0]
    assert (c.line, c.col) == (1, 1)


def test_persistence_write_rechecks_cap_root_after_late_symlink_swap(tmp_path, monkeypatch) -> None:
    from micromax_editor import persist_io

    root = tmp_path / 'persist'
    root.mkdir()
    outside = tmp_path / 'outside.json'
    outside.write_text('["outside"]\n', encoding='utf-8')
    target = root / 'recent.json'

    ed = Editor()
    ed.new_buffer('*scratch*', '')
    ed.options.set('cap.persist', 'true')
    ed.options.set('cap.persist-root', str(root))
    ed.options.set('recent.persist', 'true')
    ed.options.set('recent.file', 'recent.json')
    ed.recent_files[:] = ['inside.txt']

    original_ensure = persist_io.ensure_parent_directory
    swapped = {'done': False}

    def swap_after_parent(path, **kwargs):  # type: ignore[no-untyped-def]
        original_ensure(path, **kwargs)
        if not swapped['done']:
            swapped['done'] = True
            try:
                target.unlink()
            except FileNotFoundError:
                pass
            try:
                target.symlink_to(outside)
            except (OSError, NotImplementedError) as e:
                pytest.skip(f'symlink unavailable: {e}')

    monkeypatch.setattr(persist_io, 'ensure_parent_directory', swap_after_parent)

    assert ed.save_recent_files() is False
    assert swapped['done'] is True
    assert outside.read_text(encoding='utf-8') == '["outside"]\n'
    assert any('recent save error:' in msg and 'outside containment root' in msg for msg in ed.messages)


def test_persistence_read_rechecks_cap_root_after_late_symlink_swap(tmp_path, monkeypatch) -> None:
    from micromax_editor import persist_io

    root = tmp_path / 'persist'
    root.mkdir()
    outside = tmp_path / 'outside.json'
    outside.write_text('{"command": ["leaked"]}\n', encoding='utf-8')
    target = root / 'history.json'
    target.write_text('{"command": ["safe"]}\n', encoding='utf-8')

    ed = Editor()
    ed.new_buffer('*scratch*', '')
    ed.options.set('cap.persist', 'true')
    ed.options.set('cap.persist-root', str(root))
    ed.options.set('history.persist', 'true')
    ed.options.set('history.file', 'history.json')

    original_read = persist_io.read_file_bytes_contained
    swapped = {'done': False}

    def swap_then_read(path, **kwargs):  # type: ignore[no-untyped-def]
        if not swapped['done']:
            swapped['done'] = True
            target.unlink()
            try:
                target.symlink_to(outside)
            except (OSError, NotImplementedError) as e:
                pytest.skip(f'symlink unavailable: {e}')
        return original_read(path, **kwargs)

    monkeypatch.setattr(persist_io, 'read_file_bytes_contained', swap_then_read)

    assert ed.load_prompt_history() is False
    assert swapped['done'] is True
    assert ed.history.get('command') != ['leaked']
    assert any('history load error:' in msg and 'outside containment root' in msg for msg in ed.messages)


def test_persistence_read_obeys_maxbytes(tmp_path) -> None:
    root = tmp_path / 'persist'
    root.mkdir()
    hist = root / 'history.json'
    hist.write_text('{"command": ["abcdef"]}\n', encoding='utf-8')

    ed = Editor()
    ed.new_buffer('*scratch*', '')
    ed.options.set('cap.persist', 'true')
    ed.options.set('cap.persist-root', str(root))
    ed.options.set('history.persist', 'true')
    ed.options.set('history.file', 'history.json')
    ed.options.set('persist.maxbytes', '8')

    assert ed.load_prompt_history() is False
    assert any('history load error:' in msg and 'file too large' in msg for msg in ed.messages)



def test_savecursor_script_open_does_not_replay_or_overwrite_trusted_cursor(tmp_path) -> None:
    doc = tmp_path / 'trusted-cursor.txt'
    doc.write_text('alpha\nbeta\ngamma\n', encoding='utf-8')

    ed = Editor()
    ed.options.set('savecursor', 'true')
    norm = ed._normalize_path(str(doc))
    ed._saved_cursors[norm] = {'line': 2, 'col': 1}

    with ed.script_context(origin_id='script:a'):
        assert ed.open_file(str(doc)) is True
        c = ed.cur().cursors[0]
        assert (c.line, c.col) == (0, 0)
        # Closing would normally remember the current cursor.  A lower-authority
        # script must not poison the trusted/user saved cursor row as an
        # incidental side effect of opening/switching/closing buffers.
        assert ed.close_buffer(force=True) is True

    assert ed._saved_cursors[norm] == {'line': 2, 'col': 1}

    assert ed.open_file(str(doc)) is True
    c = ed.cur().cursors[0]
    assert (c.line, c.col) == (2, 1)


def test_savecursor_same_script_origin_can_replay_its_own_cursor(tmp_path) -> None:
    doc = tmp_path / 'script-cursor.txt'
    doc.write_text('alpha\nbeta\ngamma\n', encoding='utf-8')

    ed = Editor()
    ed.options.set('savecursor', 'true')

    with ed.script_context(origin_id='script:a'):
        assert ed.open_file(str(doc)) is True
        ed.cur().cursors[0].line = 1
        ed.cur().cursors[0].col = 3
        assert ed.close_buffer(force=True) is True
        assert ed.open_file(str(doc)) is True
        c = ed.cur().cursors[0]
        assert (c.line, c.col) == (1, 3)


def test_savecursor_persisted_rows_are_not_script_replayed_by_default(tmp_path) -> None:
    root = tmp_path / 'persist'
    root.mkdir()
    doc = tmp_path / 'persisted-cursor.txt'
    doc.write_text('alpha\nbeta\ngamma\n', encoding='utf-8')
    norm = str(doc.resolve())
    (root / 'cursor.json').write_text(
        json.dumps({norm: {'line': 2, 'col': 2}}),
        encoding='utf-8',
    )

    ed = Editor()
    ed.options.set('cap.persist', 'true')
    ed.options.set('cap.persist-root', str(root))
    ed.options.set('savecursor', 'true')
    ed.options.set('savecursor.file', 'cursor.json')
    assert ed.load_saved_cursors() is True

    with ed.script_context(origin_id='script:a'):
        assert ed.open_file(str(doc)) is True
        c = ed.cur().cursors[0]
        assert (c.line, c.col) == (0, 0)


def test_savecursor_cursor_restore_capability_allows_script_replay(tmp_path) -> None:
    doc = tmp_path / 'cursor-cap.txt'
    doc.write_text('alpha\nbeta\ngamma\n', encoding='utf-8')

    ed = Editor()
    ed.options.set('savecursor', 'true')
    ed.options.set('cap.cursor-restore', 'true')
    norm = ed._normalize_path(str(doc))
    ed._saved_cursors[norm] = {'line': 2, 'col': 1}

    with ed.script_context(origin_id='script:a'):
        assert ed.open_file(str(doc)) is True
        c = ed.cur().cursors[0]
        assert (c.line, c.col) == (2, 1)


def test_cursor_restore_capability_does_not_let_script_overwrite_trusted_saved_cursor(tmp_path) -> None:
    doc = tmp_path / 'cursor-cap-write.txt'
    doc.write_text('alpha\nbeta\ngamma\n', encoding='utf-8')

    ed = Editor()
    ed.options.set('savecursor', 'true')
    ed.options.set('cap.cursor-restore', 'true')
    norm = ed._normalize_path(str(doc))
    ed._saved_cursors[norm] = {'line': 2, 'col': 1}

    with ed.script_context(origin_id='script:a'):
        assert ed.open_file(str(doc)) is True
        ed.cur().cursors[0].line = 0
        ed.cur().cursors[0].col = 0
        assert ed.close_buffer(force=True) is True

    assert ed._saved_cursors[norm] == {'line': 2, 'col': 1}


def test_plugin_callback_rollback_restores_saved_cursor_register_and_authority(tmp_path) -> None:
    from micromax_editor.plugin_runtime import restore_plugin_callback_state, snapshot_plugin_callback_state

    doc = tmp_path / 'rollback-cursor.txt'
    doc.write_text('alpha\nbeta\ngamma\n', encoding='utf-8')

    ed = Editor()
    ed.vm.editor_owner = ed
    norm = ed._normalize_path(str(doc))
    ed._saved_cursors[norm] = {'line': 2, 'col': 1}
    ed._normalize_saved_cursor_authority()
    snap = snapshot_plugin_callback_state(ed.vm)

    with ed.script_context(origin_id='script:a'):
        ed._saved_cursors[norm] = {'line': 0, 'col': 0}
        ed._saved_cursors_authority[norm] = ed._current_runtime_authority(kind='editor')

    restore_plugin_callback_state(ed.vm, snap)
    assert ed._saved_cursors[norm] == {'line': 2, 'col': 1}
    assert ed._saved_cursor_entry_authority(norm).script_context is False


def test_buffer_transaction_snapshot_restores_saved_cursor_register_authority(tmp_path) -> None:
    doc = tmp_path / 'transaction-cursor.txt'
    doc.write_text('alpha\nbeta\ngamma\n', encoding='utf-8')

    ed = Editor()
    ed.new_buffer('*scratch*', '')
    norm = ed._normalize_path(str(doc))
    ed._saved_cursors[norm] = {'line': 2, 'col': 1}
    ed._normalize_saved_cursor_authority()
    snap = ed._buffer_transaction_snapshot()

    with ed.script_context(origin_id='script:a'):
        ed._saved_cursors[norm] = {'line': 0, 'col': 0}
        ed._saved_cursors_authority[norm] = ed._current_runtime_authority(kind='editor')

    assert ed._saved_cursors[norm] == {'line': 0, 'col': 0}
    assert ed._saved_cursors_authority[norm].script_origin_id == 'script:a'

    ed._restore_buffer_transaction_snapshot(snap)

    assert ed._saved_cursors[norm] == {'line': 2, 'col': 1}
    assert ed._saved_cursors_authority[norm].script_context is False
