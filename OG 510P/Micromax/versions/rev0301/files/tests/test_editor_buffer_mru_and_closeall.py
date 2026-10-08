from __future__ import annotations

from pathlib import Path

from micromax_editor.editor import Editor
from micromax_editor.micromax_bridge import install_editor_hostcalls


def test_buffer_mru_close_picks_previous_buffer() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.new_buffer('a', 'A')
    ed.new_buffer('b', 'B')
    ed.new_buffer('c', 'C')

    assert ed.active == 'c'

    # Switch around to build MRU: b becomes previous.
    assert ed.switch_buffer('a')
    assert ed.switch_buffer('b')
    assert ed.active == 'b'

    # Closing the active buffer should pick the MRU previous one ('a').
    assert ed.exec_command_line('close') is True
    assert ed.active == 'a'
    assert 'b' not in ed.buffers


def test_prevbuf_command_switches_to_previous() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.new_buffer('one', '1')
    ed.new_buffer('two', '2')
    ed.new_buffer('three', '3')

    assert ed.active == 'three'
    assert ed.switch_buffer('one')
    assert ed.active == 'one'

    # Previous should be three (MRU other).
    assert ed.exec_command_line('prevbuf') is True
    assert ed.active == 'three'


def test_only_closes_other_buffers_with_dirty_guard() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.new_buffer('a', 'A')
    ed.new_buffer('b', 'B')
    ed.new_buffer('c', 'C')
    assert ed.active == 'c'

    # Mark another buffer dirty.
    ed.buffers['b'].buf.dirty = True

    # First attempt should warn and refuse.
    assert ed.exec_command_line('only') is False
    assert ed.prompt is None
    assert ed.active == 'c'
    assert any('unsaved changes' in m for m in ed.messages[-2:])

    # Second attempt should proceed.
    assert ed.exec_command_line('only') is True
    assert sorted(ed.buffers.keys()) == ['c']


def test_closeall_closes_everything_and_leaves_scratch() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.new_buffer('a', 'A')
    ed.new_buffer('b', 'B')
    ed.buffers['b'].buf.dirty = True

    # First attempt warns.
    assert ed.exec_command_line('closeall') is False
    assert 'a' in ed.buffers and 'b' in ed.buffers

    # Force form proceeds immediately.
    assert ed.exec_command_line('closeall -f') is True
    assert '*scratch*' in ed.buffers
    assert ed.active == '*scratch*'


def test_command_palette_includes_recent_files_and_can_open_them(tmp_path: Path) -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    p = tmp_path / 'hello.txt'
    p.write_text('hi', encoding='utf-8')
    ed.open_file(str(p))

    # Empty-query palette should surface recent files first.
    ed.enter_command_palette('')
    st = ed.status_model()
    assert st['prompt_kind'] == 'palette'
    assert st['prompt_current_kind'] == 'recentfile'
    assert st['prompt_current_section'] == 'Recent Files'
    assert str(p) in st['prompt_current_insert']

    # Submitting should open (or switch to) that file.
    assert ed.submit_prompt() is True
    assert ed.active == str(p)


def test_recent_section_rows_hostcall_shapes(tmp_path: Path) -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    p1 = tmp_path / 'a.txt'
    p2 = tmp_path / 'b.txt'
    p1.write_text('a', encoding='utf-8')
    p2.write_text('b', encoding='utf-8')
    ed.open_file(str(p1))
    ed.open_file(str(p2))

    # Project grouping will likely fall back to directory in a tmp dir.
    sections = ed.recent_section_rows_by_project('')
    assert isinstance(sections, list)
    if sections:
        assert isinstance(sections[0], list)
        assert len(sections[0]) == 2
        label, items = sections[0]
        assert isinstance(label, str)
        assert isinstance(items, list)


def test_recent_dir_section_rows_hostcall_groups_by_parent_directory(tmp_path: Path) -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    a = tmp_path / 'proj' / 'src' / 'a.txt'
    b = tmp_path / 'proj' / 'tests' / 'b.txt'
    a.parent.mkdir(parents=True)
    b.parent.mkdir(parents=True)
    a.write_text('a', encoding='utf-8')
    b.write_text('b', encoding='utf-8')
    ed.open_file(str(a))
    ed.open_file(str(b))

    sections = ed.recent_section_rows_by_dir('')
    assert sections == [
        [str(b.parent), [[str(b), 'recent', 'b.txt', str(b.parent)]]],
        [str(a.parent), [[str(a), 'recent', 'a.txt', str(a.parent)]]],
    ]
