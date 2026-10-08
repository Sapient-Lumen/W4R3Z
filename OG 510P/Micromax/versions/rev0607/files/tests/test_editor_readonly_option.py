from __future__ import annotations

from pathlib import Path

from micromax_editor.editor import Editor
from micromax_editor.micromax_bridge import install_editor_hostcalls


def _call_ed_save(ed: Editor):
    vm = ed.vm
    vm.stack.append("ed.save")
    vm.eval("hostcall")
    err = str(vm.stack.pop())
    ok = int(vm.stack.pop())
    return ok, err


def test_global_readonly_blocks_mutating_actions_and_save(tmp_path: Path) -> None:
    p = tmp_path / "ro.txt"
    ed = Editor()
    ed.new_buffer(name=str(p), text="alpha\n", path=str(p))
    eb = ed.cur()
    eb.buf.dirty = True

    assert ed.exec_command_line("set readonly true") is True
    assert ed.is_protected_buffer() is True

    st = ed.status_model()
    assert int(st.get("protected", 0)) == 1
    assert int(st.get("readonly", 0)) == 1

    before = eb.buf.get_text()
    ed.input["text"] = "X"
    assert ed.run_action("InsertText") is False
    assert eb.buf.get_text() == before
    assert "read-only buffer" in (ed.messages[-1] if ed.messages else "")

    try:
        ed.save()
    except RuntimeError as exc:
        assert str(exc) == "Buffer is read-only"
    else:
        raise AssertionError("save should fail for readonly buffers")



def test_local_readonly_can_override_global_setting_for_current_buffer(tmp_path: Path) -> None:
    p = tmp_path / "local-override.txt"
    ed = Editor()
    ed.new_buffer(name=str(p), text="alpha", path=str(p))
    eb = ed.cur()

    assert ed.exec_command_line("set readonly true") is True
    assert ed.is_protected_buffer() is True

    # Local false should override the global protected state for this buffer.
    assert ed.exec_command_line("setlocal readonly false") is True
    assert ed.is_protected_buffer() is False

    ed.input["text"] = "!"
    assert ed.run_action("InsertText") is True
    assert eb.buf.get_text() == "!alpha"



def test_local_readonly_blocks_capability_gated_ed_save_hostcall(tmp_path: Path) -> None:
    p = tmp_path / "hostcall-ro.txt"
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer(name=str(p), text="alpha", path=str(p))
    ed.cur().buf.dirty = True

    assert ed.exec_command_line("set cap.fs-save true") is True
    ed.vm.eval('"readonly" "true" "ed.opt-set-local" hostcall')
    assert int(ed.vm.stack.pop()) == 1

    ok, err = _call_ed_save(ed)
    assert ok == 0
    assert err == "Buffer is read-only"
