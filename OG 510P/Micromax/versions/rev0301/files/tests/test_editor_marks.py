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
