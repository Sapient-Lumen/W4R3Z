from __future__ import annotations

from micromax_editor.editor import Editor


def test_qreplace_direct_accept_refuses_after_buffer_becomes_readonly() -> None:
    ed = Editor()
    ed.new_buffer("*t*", "one one")

    assert ed.exec_command_line("qreplace one X -l") is True
    assert ed.qreplace is not None
    ed.cur().local_options["readonly"] = True

    assert ed.qreplace_yes() is False
    assert ed.cur().buf.get_text() == "one one"
    assert ed.qreplace is not None
    assert ed.current_capture_key_mode() == "qreplace"
    assert ed.status_model()["last_message"] == "qreplace: read-only buffer"

    assert ed.qreplace_quit() is True
    assert ed.qreplace is None
