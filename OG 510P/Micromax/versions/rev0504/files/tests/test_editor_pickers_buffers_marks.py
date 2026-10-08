from micromax_editor.editor import Editor
from micromax_editor.micromax_bridge import install_editor_hostcalls
from micromax_editor.buffer import Cursor


def _hostcall(ed: Editor, name: str, *args: object) -> object:
    vm = ed.vm
    vm.stack.clear()
    for a in args:
        vm.stack.append(a)
    vm.stack.append(name)
    vm.eval('hostcall')
    assert vm.stack
    return vm.stack.pop()


def _set_primary_cursor(ed: Editor, *, line: int, col: int) -> None:
    eb = ed.cur()
    ed._normalize_cursor_lists(eb)
    eb.cursors[eb.primary] = eb.buf.clamp(Cursor(int(line), int(col)))


def _primary_cursor(ed: Editor) -> tuple[int, int]:
    eb = ed.cur()
    ed._normalize_cursor_lists(eb)
    c = eb.cursors[eb.primary]
    return (int(c.line), int(c.col))


def test_bufferpick_switches_active_buffer() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.new_buffer("a", "hello\nworld\n")
    ed.new_buffer("b", "x\n")
    assert ed.active == "b"

    ed.exec_command_line("bufferpick")
    assert ed.prompt is not None
    assert ed.prompt.kind == "buffer"
    assert ed.prompt.suggestions
    assert "a" in ed.prompt.suggestions

    # Pick buffer 'a' by selecting its suggestion row.
    ed.prompt.suggest_index = ed.prompt.suggestions.index("a")
    assert ed.submit_prompt()
    assert ed.active == "a"
    assert ed.status_model()['last_message'] == 'buffer: a @ 1:0'


def test_markpick_jumps_to_mark_and_buffer() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.new_buffer("a", "one\ntwo\nthree\n")
    ed.new_buffer("b", "zzz\n")
    # Set a mark in buffer a at line 2 col 1 (0-based).
    ed.switch_buffer("a")
    _set_primary_cursor(ed, line=2, col=1)
    assert ed.mark_set("m")
    ed.switch_buffer("b")
    assert ed.active == "b"

    ed.exec_command_line("markpick")
    assert ed.prompt is not None
    assert ed.prompt.kind == "mark"
    assert ed.prompt.suggestions
    assert "m" in ed.prompt.suggestions

    ed.prompt.suggest_index = ed.prompt.suggestions.index("m")
    assert ed.submit_prompt()

    assert ed.active == "a"
    assert _primary_cursor(ed) == (2, 1)
    assert ed.status_model()['last_message'] == 'markjump: m -> a @ 3:1'


def test_markjump_command_reports_missing_mark_plainly() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.new_buffer("alpha", "a\n")

    assert ed.exec_command_line("markjump missing") is False
    assert ed.status_model()['last_message'] == 'markjump: no such mark: missing'


def test_markjump_command_reports_landed_target() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.new_buffer("alpha", "a\nb\n")
    ed.new_buffer("beta", "x\n")
    ed.switch_buffer("alpha")
    _set_primary_cursor(ed, line=1, col=0)
    assert ed.mark_set("here")
    ed.switch_buffer("beta")

    assert ed.exec_command_line("markjump here") is True
    assert ed.active == "alpha"
    assert _primary_cursor(ed) == (1, 0)
    assert ed.status_model()['last_message'] == 'markjump: here -> alpha @ 2:0'


def test_mark_command_reports_anchor_target() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.new_buffer("alpha", "a\nb\n")
    _set_primary_cursor(ed, line=1, col=0)

    assert ed.exec_command_line("mark here") is True
    assert ed.status_model()['last_message'] == 'mark set: here -> alpha @ 2:0'


def test_marks_command_reports_zero_inventory_count() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    assert ed.exec_command_line("marks") is True
    assert ed.messages == ['marks: 0 mark(s)']


def test_marks_command_reports_active_owner_and_here_flag() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.new_buffer("alpha", "a\nb\n")
    _set_primary_cursor(ed, line=1, col=0)
    assert ed.mark_set("here")

    ed.new_buffer("beta", "x\ny\n")
    _set_primary_cursor(ed, line=0, col=1)
    assert ed.mark_set("there")

    ed.switch_buffer("alpha")
    _set_primary_cursor(ed, line=1, col=0)

    assert ed.exec_command_line("marks") is True
    assert ed.status_model()['last_message'] == 'marks: 2 mark(s), here -> *alpha [here] @ 2:0; there -> beta @ 1:1'


def test_buffers_command_reports_zero_inventory_count() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    assert ed.exec_command_line("buffers") is True
    assert ed.messages == ['buffers: 0 buffer(s)']


def test_buffers_command_reports_active_cursor_and_flags() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.new_buffer("alpha", "a\nb\n")
    _set_primary_cursor(ed, line=1, col=0)
    ed.cur().buf.dirty = True
    ed.cur().local_options["readonly"] = True

    ed.new_buffer("beta", "xyz\n")
    _set_primary_cursor(ed, line=0, col=2)

    assert ed.exec_command_line("buffers") is True
    assert ed.status_model()['last_message'] == 'buffers: 2 buffer(s), alpha [dirty, readonly] @ 2:0; *beta @ 1:2'


def test_command_prompt_completion_for_buffer_and_markjump() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.new_buffer("alpha", "a\n")
    ed.new_buffer("beta", "b\n")
    ed.switch_buffer("alpha")
    _set_primary_cursor(ed, line=0, col=0)
    ed.mark_set("here")
    ed.switch_buffer("beta")
    _set_primary_cursor(ed, line=0, col=0)
    ed.mark_set("there")
    ed.switch_buffer("alpha")

    # buffer NAME completion
    ed.enter_prompt("command", prefill="buffer ")
    assert ed.prompt is not None
    assert ed.prompt_complete(direction=1)
    rows = ed.prompt_suggestion_rows()
    assert any(r[1] == "buffer" for r in rows)

    # markjump NAME completion
    ed.enter_prompt("command", prefill="markjump ")
    assert ed.prompt is not None
    assert ed.prompt_complete(direction=1)
    rows = ed.prompt_suggestion_rows()
    assert any(r[1] == "mark" for r in rows)


def test_bufferpick_exposes_grouped_sections_and_preview_labels(tmp_path) -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.new_buffer('*scratch*', 'x\n')
    assert ed.open_help_doc('help-browser') is True

    p = tmp_path / 'notes.txt'
    p.write_text('hi\n', encoding='utf-8')
    ed.open_file(str(p))

    sections = _hostcall(ed, 'ed.buffer-section-rows', '')
    assert isinstance(sections, list)
    assert [sec[0] for sec in sections] == ['Help', 'Scratch', str(tmp_path)]
    help_rows = next(sec[1] for sec in sections if sec[0] == 'Help')
    scratch_rows = next(sec[1] for sec in sections if sec[0] == 'Scratch')
    file_rows = next(sec[1] for sec in sections if sec[0] == str(tmp_path))
    assert any(row[0] == 'help:help-browser' and 'docs/98-help-browser.md' in row[3] for row in help_rows)
    assert scratch_rows == [['*scratch*', 'buffer', 'buffer', '2 lines']]
    assert any(row[0] == str(p) and row[2] == 'active' and str(p) in row[3] for row in file_rows)

    assert ed.exec_command_line('bufferpick') is True
    assert ed.prompt is not None
    assert ed.prompt.kind == 'buffer'
    assert ed.prompt_current_section() == 'Help'
    assert ed.prompt_current_preview().startswith('Help: help:help-browser')


def test_markpick_groups_rows_by_buffer_and_exposes_buffer_section_labels() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.new_buffer("a", "one\n")
    ed.new_buffer("b", "two\n")

    ed.switch_buffer("a")
    _set_primary_cursor(ed, line=0, col=0)
    assert ed.mark_set("alpha")

    ed.switch_buffer("b")
    _set_primary_cursor(ed, line=0, col=0)
    assert ed.mark_set("beta")

    rows = ed.mark_prompt_rows()
    assert [row[0] for row in rows] == ["beta", "alpha"]
    assert ed.mark_section_rows("") == [
        ["b", [["beta", "mark", "b:1:1", "two"]]],
        ["a", [["alpha", "mark", "a:1:1", "one"]]],
    ]

    ed.exec_command_line("markpick")
    assert ed.prompt is not None
    assert ed.prompt.kind == "mark"
    assert ed.prompt.suggestion_rows

    labels = [
        ed.prompt_row_section_label([str(x) for x in row[:4]], prompt_kind="mark")
        for row in ed.prompt.suggestion_rows
    ]
    assert labels == ["b", "a"]
    assert ed.prompt_current_section() == "b"
    assert ed.prompt_current_preview().startswith("b: beta")
