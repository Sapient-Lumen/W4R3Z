from __future__ import annotations

import json

from micromax_editor.editor import Editor


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
