from __future__ import annotations

from micromax_editor.editor import Editor
from micromax_editor.micromax_bridge import install_editor_hostcalls


def _hostcall(ed: Editor, name: str, *args: object) -> list[object]:
    ed.vm.stack.clear()
    for arg in args:
        ed.vm.stack.append(arg)
    ed.vm.stack.append(name)
    ed.vm.eval("hostcall", filename="<hostcall>")
    return list(ed.vm.stack)


def test_script_context_restores_action_input_scratch_after_hostcall() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer("*scratch*", "")
    ed.input["text"] = "safe"

    with ed.script_context():
        _hostcall(ed, "ed.input-set", "text", "unsafe")
        assert ed.input["text"] == "unsafe"

    assert ed.input == {"text": "safe"}
    assert ed.run_action("InsertText") is True
    assert ed.cur().buf.get_text() == "safe"


def test_nested_script_run_can_use_input_then_outer_exit_restores_it() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer("*scratch*", "")
    ed.input["text"] = "base"

    with ed.script_context():
        _hostcall(ed, "ed.input-set", "text", "yo")
        _hostcall(ed, "ed.run", "InsertText")
        assert ed.cur().buf.get_text() == "yo"
        assert ed.input == {"text": "yo"}

    assert ed.input == {"text": "base"}


def test_deferred_script_keybinding_cannot_leave_stale_action_input() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer("*scratch*", "")

    with ed.script_context():
        _hostcall(ed, "ed.bind", "F40", 'mx:"text" "late" "ed.input-set" hostcall')

    ed.input["text"] = "safe"
    assert ed.dispatch_key("F40") is True
    assert ed.input == {"text": "safe"}
    assert ed.run_action("InsertText") is True
    assert ed.cur().buf.get_text() == "safe"


def test_deferred_script_timer_cannot_leave_stale_action_input() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.input["text"] = "safe"

    with ed.script_context():
        ed.vm.eval(
            '0 [ "text" "late" "ed.input-set" hostcall ] "ed.after" hostcall',
            filename="<script>",
        )
        assert ed.vm.pop_int() > 0

    assert ed.input == {"text": "safe"}
    assert ed.pump_timers() == 1
    assert ed.input == {"text": "safe"}


def test_script_context_restores_mutable_action_input_values() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.input["payload"] = ["safe"]
    ed.input["meta"] = {"status": ["clean"]}

    with ed.script_context():
        ed.vm.eval(
            '"payload" "ed.input-get" hostcall "evil" swap push drop '
            '"meta" "ed.input-get" hostcall "status" swap m@ "dirty" swap push drop',
            filename="<script>",
        )
        assert ed.input["payload"] == ["safe", "evil"]
        assert ed.input["meta"] == {"status": ["clean", "dirty"]}

    assert ed.input == {"payload": ["safe"], "meta": {"status": ["clean"]}}


def test_set_text_hostcall_is_single_undoable_direct_edit() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer("*scratch*", "old")

    _hostcall(ed, "ed.set-text", "new\ntext")
    assert ed.cur().buf.get_text() == "new\ntext"
    assert ed.undo.can_undo()

    assert ed.undo.undo() is True
    assert ed.cur().buf.get_text() == "old"

    assert ed.undo.redo() is True
    assert ed.cur().buf.get_text() == "new\ntext"
