from micromax_editor.editor import Editor
from micromax_editor.micromax_bridge import install_editor_hostcalls


def _hostcall(ed: Editor, name: str, *args: object) -> list[object]:
    vm = ed.vm
    for a in args:
        vm.stack.append(a)
    vm.stack.append(name)
    vm.eval("hostcall")
    return list(vm.stack)


def test_marks_hostcalls_set_and_jump() -> None:
    ed = Editor()
    ed.new_buffer("a", "hello\nworld\nzzz")
    install_editor_hostcalls(ed)

    # place cursor at line 1, col 2 (0-based)
    ed.vm.stack.clear()
    _hostcall(ed, "ed.set-cursors", [[1, 2]])

    # set mark "m"
    ed.vm.stack.clear()
    _hostcall(ed, "ed.mark-set", "m")
    ok = ed.vm.pop_int()
    assert ok == 1

    # move cursor elsewhere
    ed.vm.stack.clear()
    _hostcall(ed, "ed.set-cursors", [[2, 1]])

    # jump back
    ed.vm.stack.clear()
    _hostcall(ed, "ed.mark-jump", "m")
    ok2 = ed.vm.pop_int()
    assert ok2 == 1

    # verify cursor
    ed.vm.stack.clear()
    _hostcall(ed, "ed.cursors")
    curs = ed.vm.pop_list()
    assert curs == [[1, 2]]

    # and marks rows are enumerable
    ed.vm.stack.clear()
    _hostcall(ed, "ed.marks")
    rows = ed.vm.pop_list()
    assert rows and rows[0][0] == "m"


def test_mark_inventory_rows_hostcall_exposes_preview_and_active_here_flags() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.new_buffer("alpha", "zero\n  target  \n")
    ed.vm.stack.clear()
    _hostcall(ed, "ed.set-cursors", [[1, 0]])
    ed.vm.stack.clear()
    _hostcall(ed, "ed.mark-set", "here")
    assert ed.vm.pop_int() == 1

    ed.new_buffer("beta", "other\n")
    ed.vm.stack.clear()
    _hostcall(ed, "ed.set-cursors", [[0, 0]])
    ed.vm.stack.clear()
    _hostcall(ed, "ed.mark-set", "there")
    assert ed.vm.pop_int() == 1

    ed.vm.stack.clear()
    _hostcall(ed, "ed.set-active-buffer", "alpha")
    assert ed.vm.pop_int() == 1
    ed.vm.stack.clear()
    _hostcall(ed, "ed.set-cursors", [[1, 0]])

    ed.vm.stack.clear()
    _hostcall(ed, "ed.mark-inventory-rows")
    rows = ed.vm.pop_list()
    assert rows == [
        ["here", "alpha", "2:0", "target", 1, 1],
        ["there", "beta", "1:0", "other", 0, 0],
    ]


def test_buffers_hostcalls_and_switch() -> None:
    ed = Editor()
    ed.new_buffer("a", "x")
    ed.new_buffer("b", "y")
    install_editor_hostcalls(ed)

    ed.vm.stack.clear()
    _hostcall(ed, "ed.buffers")
    names = ed.vm.pop_list()
    assert sorted(names) == ["a", "b"]

    ed.vm.stack.clear()
    _hostcall(ed, "ed.set-active-buffer", "a")
    ok = ed.vm.pop_int()
    assert ok == 1

    ed.vm.stack.clear()
    _hostcall(ed, "ed.active-buffer")
    assert ed.vm.pop_str() == "a"


def test_buffer_inventory_rows_hostcall_exposes_position_and_flags() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.new_buffer("alpha", "a\nb\n")
    ed.vm.stack.clear()
    _hostcall(ed, "ed.set-cursors", [[1, 0]])
    ed.cur().buf.dirty = True
    ed.cur().local_options["readonly"] = True

    ed.new_buffer("beta", "xyz\n")
    ed.vm.stack.clear()
    _hostcall(ed, "ed.set-cursors", [[0, 2]])

    ed.vm.stack.clear()
    _hostcall(ed, "ed.buffer-inventory-rows")
    rows = ed.vm.pop_list()
    assert rows == [
        ["alpha", "2:0", 0, 1, 1],
        ["beta", "1:2", 1, 0, 0],
    ]


def test_mark_detail_row_hostcall_and_showmark_surface() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.new_buffer("alpha", "zero\n  target  \n")
    ed.vm.stack.clear()
    _hostcall(ed, "ed.set-cursors", [[1, 0]])
    assert ed.mark_set("here") is True

    row = ed.mark_detail_row("here")
    assert row == ["here", "alpha", "2:0", "target", 1, 1]

    ed.vm.stack.clear()
    _hostcall(ed, "ed.mark-detail-row", "here")
    host_row = ed.vm.pop_list()
    assert host_row == row

    assert ed.exec_command_line("showmark here") is True
    assert ed.messages[-1] == 'mark here -> *alpha [here] @ 2:0 — target'

    assert ed.exec_command_line("showmark nope") is False
    assert ed.messages[-1] == 'showmark: no such mark: nope'



def test_showmark_root_reports_runtime_summary_then_usage() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.new_buffer("alpha", "zero\n  target  \n")
    ed.vm.stack.clear()
    _hostcall(ed, "ed.set-cursors", [[1, 0]])
    assert ed.mark_set("here") is True

    ed.messages.clear()
    assert ed.exec_command_line("showmark") is False
    assert ed.messages == [
        f"showmark: {ed._mark_inventory_preview_summary()}",
        'usage: showmark NAME',
    ]
    assert 'here -> alpha [active, here] @ 2:0' in ed.messages[0]
    assert 'target' in ed.messages[0]



def test_mark_and_markjump_roots_report_runtime_summary_then_usage() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.new_buffer("alpha", "zero\n  target  \n")
    ed.vm.stack.clear()
    _hostcall(ed, "ed.set-cursors", [[1, 0]])
    assert ed.mark_set("here") is True

    ed.messages.clear()
    assert ed.exec_command_line("mark") is False
    assert ed.messages == [
        f"mark: {ed._mark_inventory_preview_summary()}",
        'usage: mark NAME',
    ]
    assert 'here -> alpha [active, here] @ 2:0' in ed.messages[0]
    assert 'target' in ed.messages[0]

    ed.messages.clear()
    assert ed.exec_command_line("markjump") is False
    assert ed.messages == [
        f"markjump: {ed._mark_inventory_preview_summary()}",
        'usage: markjump NAME',
    ]
    assert 'here -> alpha [active, here] @ 2:0' in ed.messages[0]
    assert 'target' in ed.messages[0]


def test_mark_section_summary_rows_hostcall_and_showmarkgroups_surface() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.new_buffer("alpha", "zero\n  target  \n")
    ed.vm.stack.clear()
    _hostcall(ed, "ed.set-cursors", [[1, 0]])
    assert ed.mark_set("here") is True

    ed.new_buffer("beta", "other\n")
    ed.vm.stack.clear()
    _hostcall(ed, "ed.set-cursors", [[0, 0]])
    assert ed.mark_set("there") is True

    rows = ed.mark_section_summary_rows("target")
    assert rows == [["alpha", 1, "here", "target"]]

    ed.vm.stack.clear()
    _hostcall(ed, "ed.mark-section-summary-rows", "")
    host_rows = ed.vm.pop_list()
    assert host_rows == [
        ["beta", 1, "there", "other"],
        ["alpha", 1, "here", "target"],
    ]

    assert ed.exec_command_line("showmarkgroups target") is True
    assert ed.messages == [
        "showmarkgroups target: 1 section(s), 1 mark(s)",
        "alpha: 1 (e.g. here — target)",
    ]

    assert ed.exec_command_line("showmarkgroups zzz-no-such-mark") is True
    assert ed.messages[-1] == "showmarkgroups zzz-no-such-mark: 0 section(s), 0 mark(s)"
