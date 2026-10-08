from __future__ import annotations

from pathlib import Path

from micromax_editor.buffer import Cursor
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

    # Submitting should open (or switch to) that file and report where it landed.
    assert ed.submit_prompt() is True
    assert ed.active == str(p)
    assert ed.messages[-1] == f'opened: {p} @ 1:0'


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


def test_recent_dir_section_summary_rows_and_showrecentdirgroups_surface(tmp_path: Path) -> None:
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

    rows = ed.recent_dir_section_summary_rows('b.txt')
    assert rows == [[str(b.parent), 1, 'b.txt #1 [active] @ 1:0', 'current buffer']]

    ed.vm.stack.clear()
    ed.vm.stack.append('b.txt')
    ed.vm.stack.append('ed.recent-dir-section-summary-rows')
    ed.vm.eval('hostcall')
    host_rows = ed.vm.pop_list()
    assert host_rows == rows

    ed.messages.clear()
    assert ed.exec_command_line('showrecentdirgroups b.txt') is True
    assert ed.messages == [
        'showrecentdirgroups b.txt: 1 section(s), 1 file(s)',
        f'{b.parent}: 1 (e.g. b.txt #1 [active] @ 1:0 — current buffer)',
    ]

    ed.messages.clear()
    assert ed.exec_command_line('showrecentdirgroups zzz-no-such-recent-file') is True
    assert ed.messages == ['showrecentdirgroups zzz-no-such-recent-file: 0 section(s), 0 file(s)']


def test_showrecentdirgroups_top_level_bucket_omits_duplicate_directory_echo(tmp_path: Path) -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    root = tmp_path / 'root.md'
    root.write_text('root', encoding='utf-8')

    ed.open_file(str(root))

    rows = ed.recent_dir_section_summary_rows('root.md')
    assert rows == [[str(tmp_path), 1, 'root.md #1 [active] @ 1:0', 'current buffer']]

    ed.messages.clear()
    assert ed.exec_command_line('showrecentdirgroups root.md') is True
    assert ed.messages == [
        'showrecentdirgroups root.md: 1 section(s), 1 file(s)',
        f'{tmp_path}: 1 (e.g. root.md #1 [active] @ 1:0 — current buffer)',
    ]


def test_recent_dir_detail_row_and_showrecentdir_surface(tmp_path: Path) -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    assert ed.exec_command_line('set cap.fs-list true')

    a = tmp_path / 'proj' / 'src' / 'a.txt'
    b = tmp_path / 'proj' / 'tests' / 'b.txt'
    c = tmp_path / 'proj' / 'tests' / 'c.txt'
    a.parent.mkdir(parents=True)
    b.parent.mkdir(parents=True)
    a.write_text('a\n', encoding='utf-8')
    b.write_text('b\nnext\n', encoding='utf-8')
    c.write_text('c\n', encoding='utf-8')

    ed.open_file(str(a))
    ed.open_file(str(b))
    ed.open_file(str(c))
    assert ed.switch_buffer(str(b))
    eb = ed.cur()
    ed._normalize_cursor_lists(eb)
    eb.cursors[eb.primary] = eb.buf.clamp(Cursor(1, 0))
    eb.buf.dirty = True

    query = str(tmp_path / 'proj' / 'tests' / '..' / 'tests')
    row = ed.recent_dir_detail_row(str(b.parent))
    assert row == [
        str(b.parent),
        str(b.parent),
        2,
        1,
        2,
        1,
        0,
        str(c),
        str(b.parent),
        'c.txt #1 [open] @ 1:0',
        f'{b.parent} | existing file | switch buffer',
    ]

    alias_row = ed.recent_dir_detail_row(query)
    assert alias_row == [
        query,
        str(b.parent),
        2,
        1,
        2,
        1,
        0,
        str(c),
        str(b.parent),
        'c.txt #1 [open] @ 1:0',
        f'{b.parent} | existing file | switch buffer',
    ]

    ed.vm.stack.clear()
    ed.vm.stack.append(str(b.parent))
    ed.vm.stack.append('ed.recent-dir-detail-row')
    ed.vm.eval('hostcall')
    host_row = ed.vm.pop()
    assert host_row == row

    ed.vm.stack.clear()
    ed.vm.stack.append(1)
    ed.vm.stack.append('ed.recent-slot-dir-detail-row')
    ed.vm.eval('hostcall')
    slot_row = ed.vm.pop()
    assert slot_row == [
        1,
        str(b.parent),
        2,
        1,
        2,
        1,
        0,
        str(c),
        str(b.parent),
        'c.txt #1 [open] @ 1:0',
        f'{b.parent} | existing file | switch buffer',
    ]

    ed.vm.stack.clear()
    ed.vm.eval('1 recent-slot-dir-detail', filename='<test>')
    assert ed.vm.stack.pop() == slot_row

    ed.vm.stack.clear()
    ed.vm.eval('"#1" recent-slot-dir-detail', filename='<test>')
    assert ed.vm.stack.pop() == slot_row

    ed.messages.clear()
    assert ed.exec_command_line(f'showrecentdir {b.parent}') is True
    assert ed.messages == [
        f'recentdir {b.parent}: 2 files [active, open=2, dirty=1] — e.g. c.txt #1 [open] @ 1:0 | existing file | switch buffer',
    ]

    ed.messages.clear()
    assert ed.exec_command_line('showrecentdir 1') is True
    assert ed.messages == [
        f'recentdir 1 -> {b.parent}: 2 files [active, open=2, dirty=1] — e.g. c.txt #1 [open] @ 1:0 | existing file | switch buffer',
    ]

    ed.messages.clear()
    assert ed.exec_command_line('showrecentdir #1') is True
    assert ed.messages == [
        f'recentdir #1 -> {b.parent}: 2 files [active, open=2, dirty=1] — e.g. c.txt #1 [open] @ 1:0 | existing file | switch buffer',
    ]

    ed.messages.clear()
    assert ed.exec_command_line('showrecentdir no-such-recent-dir') is False
    assert ed.messages == ['showrecentdir: no such recent directory: no-such-recent-dir']

    ed.messages.clear()
    missing_dir = tmp_path / 'missing-dir'
    assert ed.exec_command_line(f'showrecentdir {missing_dir}') is False
    assert ed.messages == [f'showrecentdir: no such recent directory: {missing_dir}']

    ed.messages.clear()
    assert ed.exec_command_line('showrecentdir #9') is False
    assert ed.messages == ['showrecentdir: no such recent directory: #9']


def test_recent_detail_row_and_showrecent_surface(tmp_path: Path) -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    assert ed.exec_command_line('set cap.fs-list true')

    (tmp_path / 'pyproject.toml').write_text('[project]\nname = "demo"\n', encoding='utf-8')
    p = tmp_path / 'guide' / 'intro.md'
    q = tmp_path / 'notes' / 'daily.txt'
    p.parent.mkdir(parents=True)
    q.parent.mkdir(parents=True)
    p.write_text('intro\nnext\n', encoding='utf-8')
    q.write_text('notes\n', encoding='utf-8')

    ed.open_file(str(p))
    ed.open_file(str(q))
    assert ed.switch_buffer(str(p))
    eb = ed.cur()
    ed._normalize_cursor_lists(eb)
    eb.cursors[eb.primary] = eb.buf.clamp(Cursor(1, 1))
    eb.buf.dirty = True

    query = str(tmp_path / 'guide' / '..' / 'guide' / 'intro.md')
    row = ed.recent_detail_row(str(p))
    assert row == [
        str(p),
        str(p),
        2,
        '2:1',
        1,
        1,
        1,
        0,
        str(tmp_path),
        'guide/intro.md',
        'existing file',
        'current buffer',
    ]

    alias_row = ed.recent_detail_row(query)
    assert alias_row == [
        query,
        str(p),
        2,
        '2:1',
        1,
        1,
        1,
        0,
        str(tmp_path),
        'guide/intro.md',
        'existing file',
        'current buffer',
    ]

    ed.vm.stack.clear()
    ed.vm.stack.append(str(p))
    ed.vm.stack.append('ed.recent-detail-row')
    ed.vm.eval('hostcall')
    host_row = ed.vm.pop()
    assert host_row == row

    ed.vm.stack.clear()
    ed.vm.stack.append(2)
    ed.vm.stack.append('ed.recent-slot-detail-row')
    ed.vm.eval('hostcall')
    slot_row = ed.vm.pop()
    assert slot_row == [
        2,
        str(p),
        2,
        '2:1',
        1,
        1,
        1,
        0,
        str(tmp_path),
        'guide/intro.md',
        'existing file',
        'current buffer',
    ]

    ed.vm.stack.clear()
    ed.vm.eval('2 recent-slot-detail', filename='<test>')
    assert ed.vm.stack.pop() == slot_row

    ed.vm.stack.clear()
    ed.vm.eval('"#2" recent-slot-detail', filename='<test>')
    assert ed.vm.stack.pop() == slot_row

    ed.messages.clear()
    assert ed.exec_command_line('showrecent 2') is True
    assert ed.messages == [
        f'recent #2 {p} [active, dirty] @ 2:1 — section={tmp_path} | guide/intro.md | existing file | current buffer',
    ]

    ed.messages.clear()
    assert ed.exec_command_line('showrecent #2') is True
    assert ed.messages == [
        f'recent #2 {p} [active, dirty] @ 2:1 — section={tmp_path} | guide/intro.md | existing file | current buffer',
    ]

    ed.messages.clear()
    assert ed.exec_command_line(f'showrecent {p}') is True
    assert ed.messages == [
        f'recent #2 {p} [active, dirty] @ 2:1 — section={tmp_path} | guide/intro.md | existing file | current buffer',
    ]

    ed.messages.clear()
    assert ed.exec_command_line('showrecent no-such-recent-file') is False
    assert ed.messages == ['showrecent: no such recent file: no-such-recent-file']


def test_showrecent_root_reports_runtime_summary_then_usage(tmp_path: Path) -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    p = tmp_path / 'demo.txt'
    q = tmp_path / 'other.txt'
    p.write_text('demo\n', encoding='utf-8')
    q.write_text('other\n', encoding='utf-8')
    ed.open_file(str(p))
    ed.open_file(str(q))

    ed.messages.clear()
    assert ed.exec_command_line('showrecent') is False
    assert ed.messages == [
        f"showrecent: {ed._recent_inventory_preview_summary()}",
        'usage: showrecent PATH|N|#N',
    ]
    assert 'latest #1' in ed.messages[0]
    assert str(tmp_path) in ed.messages[0]
    assert 'other.txt' in ed.messages[0]
    assert 'current buffer' in ed.messages[0]


def test_showrecentdir_root_reports_runtime_summary_then_usage(tmp_path: Path) -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    a = tmp_path / 'proj' / 'src' / 'a.txt'
    b = tmp_path / 'proj' / 'tests' / 'b.txt'
    c = tmp_path / 'proj' / 'tests' / 'c.txt'
    a.parent.mkdir(parents=True)
    b.parent.mkdir(parents=True)
    a.write_text('a\n', encoding='utf-8')
    b.write_text('b\n', encoding='utf-8')
    c.write_text('c\n', encoding='utf-8')
    ed.open_file(str(a))
    ed.open_file(str(b))
    ed.open_file(str(c))

    ed.messages.clear()
    assert ed.exec_command_line('showrecentdir') is False
    assert ed.messages == [
        f"showrecentdir: {ed._recent_dir_inventory_preview_summary()}",
        'usage: showrecentdir DIR|N|#N',
    ]
    assert 'latest #1' in ed.messages[0]
    assert str(b.parent) in ed.messages[0]
    assert 'c.txt' in ed.messages[0]
    assert 'current buffer' in ed.messages[0]


def test_recent_detail_row_and_showrecent_surface_keep_missing_file_truth(tmp_path: Path) -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    assert ed.exec_command_line('set cap.fs-list true')

    scratch = tmp_path / 'scratch.md'
    ed.open_file(str(scratch))

    row = ed.recent_detail_row(str(scratch))
    assert row == [
        str(scratch),
        str(scratch),
        1,
        '1:0',
        1,
        1,
        0,
        0,
        str(tmp_path),
        'scratch.md',
        'new file',
        'current buffer',
    ]

    ed.messages.clear()
    assert ed.exec_command_line(f'showrecent {scratch}') is True
    assert ed.messages == [
        f'recent #1 {scratch} [active] @ 1:0 — section={tmp_path} | new file | current buffer',
    ]


def test_showrecent_top_level_file_omits_duplicate_section_location(tmp_path: Path) -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    assert ed.exec_command_line('set cap.fs-list true')

    old = tmp_path / 'old.md'
    old.write_text('old\n', encoding='utf-8')

    ed.open_file(str(old))
    assert ed.exec_command_line('close')

    ed.messages.clear()
    assert ed.exec_command_line(f'showrecent {old}') is True
    assert ed.messages == [
        f'recent #1 {old} — section={tmp_path} | existing file',
    ]




def test_showrecentdir_omits_duplicate_directory_echo_in_sample_info(tmp_path: Path) -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    assert ed.exec_command_line('set cap.fs-list true')

    old = tmp_path / 'old.md'
    old.write_text('old\n', encoding='utf-8')

    ed.open_file(str(old))

    row = ed.recent_dir_detail_row(str(tmp_path))
    assert row is not None
    assert row[8] == str(tmp_path)
    assert row[9] == 'old.md #1 [active] @ 1:0'
    assert row[10] == f'{tmp_path} | existing file | current buffer'

    ed.messages.clear()
    assert ed.exec_command_line(f'showrecentdir {tmp_path}') is True
    assert ed.messages == [
        f'recentdir {tmp_path}: 1 file [active, open=1] — e.g. old.md #1 [active] @ 1:0 | existing file | current buffer',
    ]


def test_recent_section_summary_rows_and_showrecentgroups_surface(tmp_path: Path) -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    (tmp_path / 'pyproject.toml').write_text('[project]\nname = "demo"\n', encoding='utf-8')
    guide = tmp_path / 'guide' / 'intro.md'
    notes = tmp_path / 'notes' / 'daily.txt'
    guide.parent.mkdir(parents=True)
    notes.parent.mkdir(parents=True)
    guide.write_text('guide', encoding='utf-8')
    notes.write_text('notes', encoding='utf-8')

    ed.open_file(str(guide))
    ed.open_file(str(notes))

    # Include the extension so fuzzy path matching does not count the pytest
    # fixture directory name itself as an ``intro`` hit.
    rows = ed.recent_section_summary_rows('intro.md')
    assert rows == [[str(tmp_path), 1, 'intro.md #2 [open] @ 1:0', 'guide/intro.md | switch buffer']]

    ed.vm.stack.clear()
    ed.vm.stack.append('intro.md')
    ed.vm.stack.append('ed.recent-section-summary-rows')
    ed.vm.eval('hostcall')
    host_rows = ed.vm.pop_list()
    assert host_rows == rows

    ed.messages.clear()
    assert ed.exec_command_line('showrecentgroups intro.md') is True
    assert ed.messages == [
        'showrecentgroups intro.md: 1 section(s), 1 file(s)',
        f'{tmp_path}: 1 (e.g. intro.md #2 [open] @ 1:0 — guide/intro.md | switch buffer)',
    ]

    ed.messages.clear()
    assert ed.exec_command_line('showrecentgroups zzz-no-such-recent-file') is True
    assert ed.messages == ['showrecentgroups zzz-no-such-recent-file: 0 section(s), 0 file(s)']


def test_showrecentgroups_project_root_bucket_omits_duplicate_filename_echo(tmp_path: Path) -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    (tmp_path / 'pyproject.toml').write_text('[project]\nname = "demo"\n', encoding='utf-8')
    root = tmp_path / 'root.md'
    root.write_text('root', encoding='utf-8')

    ed.open_file(str(root))

    rows = ed.recent_section_summary_rows('root.md')
    assert rows == [[str(tmp_path), 1, 'root.md #1 [active] @ 1:0', 'current buffer']]

    ed.messages.clear()
    assert ed.exec_command_line('showrecentgroups root.md') is True
    assert ed.messages == [
        'showrecentgroups root.md: 1 section(s), 1 file(s)',
        f'{tmp_path}: 1 (e.g. root.md #1 [active] @ 1:0 — current buffer)',
    ]



def test_buffer_section_summary_rows_and_showbuffergroups_surface(tmp_path: Path) -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.new_buffer('help:guide', 'guide')
    ed.new_buffer('*notes*', 'notes')

    p = tmp_path / 'proj' / 'file.txt'
    p.parent.mkdir(parents=True)
    p.write_text('file', encoding='utf-8')
    ed.open_file(str(p))

    rows = ed.buffer_section_summary_rows('guide')
    assert rows == [['Help', 1, 'help:guide', '1 lines']]

    ed.vm.stack.clear()
    ed.vm.stack.append('guide')
    ed.vm.stack.append('ed.buffer-section-summary-rows')
    ed.vm.eval('hostcall')
    host_rows = ed.vm.pop_list()
    assert host_rows == rows

    ed.messages.clear()
    assert ed.exec_command_line('showbuffergroups guide') is True
    assert ed.messages == [
        'showbuffergroups guide: 1 section(s), 1 buffer(s)',
        'Help: 1 (e.g. help:guide — 1 lines)',
    ]

    ed.messages.clear()
    assert ed.exec_command_line('showbuffergroups zzz-no-such-buffer') is True
    assert ed.messages == ['showbuffergroups zzz-no-such-buffer: 0 section(s), 0 buffer(s)']



def test_buffer_detail_row_and_showbuffer_surface(tmp_path: Path) -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    p = tmp_path / 'proj' / 'file.txt'
    p.parent.mkdir(parents=True)
    p.write_text('file\nsecond\n', encoding='utf-8')
    ed.open_file(str(p))
    eb = ed.cur()
    ed._normalize_cursor_lists(eb)
    eb.cursors[eb.primary] = eb.buf.clamp(Cursor(1, 2))
    eb.buf.dirty = True

    row = ed.buffer_detail_row(str(p))
    assert row == [str(p), '2:2', 1, 1, 0, str(tmp_path / 'proj'), str(p), 3]

    ed.vm.stack.clear()
    ed.vm.stack.append(str(p))
    ed.vm.stack.append('ed.buffer-detail-row')
    ed.vm.eval('hostcall')
    host_row = ed.vm.pop()
    assert host_row == row

    ed.messages.clear()
    assert ed.exec_command_line(f'showbuffer {p}') is True
    assert ed.messages == [
        f'buffer {p} [active, dirty] @ 2:2 — section={tmp_path / "proj"} | {p} | 3 lines',
    ]

    ed.messages.clear()
    assert ed.exec_command_line('showbuffer no-such-buffer') is False
    assert ed.messages == ['showbuffer: no such buffer: no-such-buffer']


def test_showbuffer_root_reports_runtime_summary_then_usage(tmp_path: Path) -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    p = tmp_path / 'proj' / 'root.txt'
    p.parent.mkdir(parents=True)
    p.write_text('root\nsecond\n', encoding='utf-8')
    ed.open_file(str(p))
    eb = ed.cur()
    ed._normalize_cursor_lists(eb)
    eb.cursors[eb.primary] = eb.buf.clamp(Cursor(1, 1))
    eb.buf.dirty = True

    ed.messages.clear()
    assert ed.exec_command_line('showbuffer') is False
    assert ed.messages == [
        f"showbuffer: {ed._buffer_inventory_preview_summary()}",
        'usage: showbuffer NAME',
    ]
    assert str(p) in ed.messages[0]
    assert '[active, dirty]' in ed.messages[0]
    assert '@ 2:1' in ed.messages[0]



def test_buffer_root_reports_runtime_summary_then_usage(tmp_path: Path) -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    p = tmp_path / 'proj' / 'root.txt'
    p.parent.mkdir(parents=True)
    p.write_text('root\nsecond\n', encoding='utf-8')
    ed.open_file(str(p))
    eb = ed.cur()
    ed._normalize_cursor_lists(eb)
    eb.cursors[eb.primary] = eb.buf.clamp(Cursor(1, 1))
    eb.buf.dirty = True

    ed.messages.clear()
    assert ed.exec_command_line('buffer') is False
    assert ed.messages == [
        f"buffer: {ed._buffer_inventory_preview_summary()}",
        'usage: buffer NAME',
    ]
    assert str(p) in ed.messages[0]
    assert '[active, dirty]' in ed.messages[0]
    assert '@ 2:1' in ed.messages[0]


def test_prevbuf_reports_no_previous_buffer_when_mru_has_no_other_buffer() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.new_buffer('one', '1')

    assert ed.exec_command_line('prevbuf') is False
    assert ed.status_model()['last_message'] == 'prevbuf: no previous buffer'


def test_prevbuf_reports_no_previous_buffer_when_previous_buffer_disappeared() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.new_buffer('one', '1')
    ed.new_buffer('two', '2')
    assert ed.switch_buffer('one')
    assert ed.previous_buffer_name() == 'two'
    del ed.buffers['two']

    assert ed.exec_command_line('prevbuf') is False
    assert ed.status_model()['last_message'] == 'prevbuf: no previous buffer'

def test_prevbuf_message_reports_landed_buffer_and_cursor() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.new_buffer('one', 'a\nb\n')
    ed.new_buffer('two', 'x\ny\nz\n')
    assert ed.switch_buffer('one')
    eb = ed.cur()
    ed._normalize_cursor_lists(eb)
    eb.cursors[eb.primary] = eb.buf.clamp(Cursor(1, 1))
    assert ed.switch_buffer('two')

    assert ed.exec_command_line('prevbuf') is True
    assert ed.status_model()['last_message'] == 'prevbuf: one @ 2:1'




def test_buffer_command_reports_missing_target_plainly() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.new_buffer('one', '1')

    assert ed.exec_command_line('buffer missing') is False
    assert ed.status_model()['last_message'] == 'buffer: no such buffer: missing'


def test_close_named_buffer_reports_missing_target_plainly() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.new_buffer('one', '1')

    assert ed.exec_command_line('close missing') is False
    assert ed.status_model()['last_message'] == 'close: no such buffer: missing'

def test_close_message_reports_new_active_buffer_when_closing_current() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.new_buffer('a', 'A\nB\n')
    ed.new_buffer('b', 'X\nY\n')
    assert ed.switch_buffer('a')
    eb = ed.cur()
    ed._normalize_cursor_lists(eb)
    eb.cursors[eb.primary] = eb.buf.clamp(Cursor(1, 1))
    assert ed.switch_buffer('b')

    assert ed.exec_command_line('close') is True
    assert ed.active == 'a'
    assert ed.status_model()['last_message'] == 'close: b -> buffer: a @ 2:1'


def test_only_and_closeall_report_landed_buffer() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.new_buffer('a', 'A\n')
    ed.new_buffer('b', 'B\n')
    ed.new_buffer('c', 'C\n')
    assert ed.switch_buffer('b')
    eb = ed.cur()
    ed._normalize_cursor_lists(eb)
    eb.cursors[eb.primary] = eb.buf.clamp(Cursor(0, 1))

    assert ed.exec_command_line('only') is True
    assert ed.active == 'b'
    assert ed.status_model()['last_message'] == 'only -> buffer: b @ 1:1'

    assert ed.exec_command_line('closeall -f') is True
    assert ed.active == '*scratch*'
    assert ed.status_model()['last_message'] == 'closeall -> buffer: *scratch* @ 1:0'


def test_only_runtime_failure_names_the_command() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.new_buffer('a', 'A\n')
    ed.new_buffer('b', 'B\n')

    def boom(*args: object, **kwargs: object) -> None:
        raise RuntimeError('boom')

    ed.close_buffers = boom  # type: ignore[assignment]

    assert ed.exec_command_line('only') is False
    assert ed.status_model()['last_message'] == 'only: error: boom'


def test_closeall_runtime_failure_names_the_command() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.new_buffer('a', 'A\n')
    ed.new_buffer('b', 'B\n')

    def boom(*args: object, **kwargs: object) -> None:
        raise RuntimeError('boom')

    ed.close_buffers = boom  # type: ignore[assignment]

    assert ed.exec_command_line('closeall -f') is False
    assert ed.status_model()['last_message'] == 'closeall: error: boom'
