from __future__ import annotations

import pytest

from micromax.vm import MicromaxError
from micromax_editor.buffer import Cursor
from micromax_editor.editor import Editor
from micromax_editor.micromax_bridge import install_editor_hostcalls


def _hostcall(ed: Editor, name: str) -> None:
    ed.vm.stack.append(name)
    ed.vm.eval("hostcall", filename="<test>")


def test_with_cursorstate_restores_active_buffer_and_all_existing_buffer_cursors() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer("a", "alpha")
    ed.new_buffer("b", "bravo")

    assert ed.switch_buffer("a")
    ed.cur().cursors[:] = [Cursor(0, 1)]
    assert ed.switch_buffer("b")
    ed.cur().cursors[:] = [Cursor(0, 2)]
    assert ed.switch_buffer("a")

    ed.vm.eval(
        '[ "buffer b" "ed.command" hostcall 0 4 "ed.set-cursor" hostcall ] '
        '"ed.with-cursorstate" hostcall',
        filename="<test>",
    )

    assert ed.active == "a"
    assert [(c.line, c.col) for c in ed.buffers["a"].cursors] == [(0, 1)]
    assert [(c.line, c.col) for c in ed.buffers["b"].cursors] == [(0, 2)]
    assert ed.vm.stack[-1] == 1


def test_with_cursorstate_restores_after_failing_cross_buffer_helper() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer("a", "alpha")
    ed.new_buffer("b", "bravo")
    assert ed.switch_buffer("a")
    ed.cur().cursors[:] = [Cursor(0, 1)]
    assert ed.switch_buffer("b")
    ed.cur().cursors[:] = [Cursor(0, 2)]
    assert ed.switch_buffer("a")

    with pytest.raises(MicromaxError):
        ed.vm.eval(
            '[ "buffer b" "ed.command" hostcall 0 4 "ed.set-cursor" hostcall missing-word ] '
            '"ed.with-cursorstate" hostcall',
            filename="<test>",
        )

    assert ed.active == "a"
    assert [(c.line, c.col) for c in ed.buffers["a"].cursors] == [(0, 1)]
    assert [(c.line, c.col) for c in ed.buffers["b"].cursors] == [(0, 2)]


@pytest.mark.parametrize("host", ["ed.with-cursorstate", "ed.with-messages", "ed.capture-messages"])
def test_transaction_quote_type_errors_preserve_bad_operand(host: str) -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.vm.stack[:] = [123]
    with pytest.raises(MicromaxError, match="expected quotation"):
        _hostcall(ed, host)

    assert ed.vm.stack == [123]


def test_timer_schedule_type_errors_preserve_operands() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.vm.eval('[ 1 ]', filename="<test>")
    q = ed.vm.stack.pop()
    ed.vm.stack[:] = ["soon", q]
    with pytest.raises(MicromaxError, match="ed.after: expected int"):
        _hostcall(ed, "ed.after")

    assert ed.vm.stack == ["soon", q]


def test_script_cannot_cancel_trusted_timer_and_timer_id_remains_visible() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.vm.eval('10 [ 1 ] "ed.after" hostcall', filename="<trusted>")
    tid = ed.vm.stack.pop()
    assert isinstance(tid, int)

    with ed.script_context():
        ed.vm.stack[:] = [tid]
        with pytest.raises(Exception, match="timer"):
            _hostcall(ed, "ed.cancel-timer")

    assert ed.vm.stack == [tid]
    assert ed.timers.get(tid) is not None


def test_command_like_hostcalls_preserve_operands_when_execution_raises() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.vm.stack[:] = ["definitely-not-a-valid-action"]
    with pytest.raises(Exception):
        _hostcall(ed, "ed.run")

    assert ed.vm.stack == ["definitely-not-a-valid-action"]


@pytest.mark.parametrize(
    "expr",
    [
        '[ drop "junk" nope ] "ed.with-viewport" hostcall',
        '"a" [ drop "junk" nope ] "ed.with-buffer" hostcall',
        '[ drop "junk" nope ] "ed.with-cursorstate" hostcall',
        '[ drop "junk" nope ] "ed.with-messages" hostcall',
        '[ drop "junk" nope ] "ed.capture-messages" hostcall',
        '"group" [ drop "junk" nope ] "ed.with-undo" hostcall',
    ],
)
def test_scope_transaction_failures_restore_vm_stack_snapshot(expr: str) -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer("a", "alpha")
    assert ed.switch_buffer("a")
    ed.vm.stack[:] = ["sentinel"]

    with pytest.raises(MicromaxError, match="Unknown word: nope"):
        ed.vm.eval(expr, filename="<test>")

    assert ed.vm.stack == ["sentinel"]


def test_scope_transaction_failure_restores_mutable_stack_values() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.vm.stack[:] = [["safe"], {"status": ["clean"]}]

    with pytest.raises(MicromaxError, match="Unknown word: nope"):
        ed.vm.eval(
            '[ '
            '  "status" swap m@ "dirty" swap push drop '
            '  "evil" swap push drop '
            '  nope '
            '] "ed.with-messages" hostcall',
            filename="<test>",
        )

    assert ed.vm.stack == [["safe"], {"status": ["clean"]}]
