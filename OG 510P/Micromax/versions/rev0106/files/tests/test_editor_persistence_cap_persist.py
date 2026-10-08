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
    ed.options.set('history.persist', 'true')
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
    ed2.options.set('history.persist', 'true')
    ed2.options.set('history.file', 'history.json')
    assert ed2.load_prompt_history() is True
    assert ed2.history.get('command') and ed2.history['command'][-1] == 'open foo.txt'
