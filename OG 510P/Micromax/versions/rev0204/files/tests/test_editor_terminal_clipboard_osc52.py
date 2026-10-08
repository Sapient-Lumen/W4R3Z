from __future__ import annotations

from micromax_editor.editor import Editor
from micromax_editor.micromax_bridge import install_editor_hostcalls
from micromax_editor.osc52 import osc52_sequence


def test_osc52_sequence_encodes_basic() -> None:
    seq, err = osc52_sequence("hi", max_bytes=100)
    assert err == ""
    assert seq is not None
    assert seq.startswith("\x1b]52;c;")
    assert seq.endswith("\x07")
    assert "aGk=" in seq  # base64("hi")


def test_osc52_sequence_limits_size() -> None:
    seq, err = osc52_sequence("x" * 10, max_bytes=5)
    assert seq is None
    assert "too large" in err


def test_editor_clipboard_terminal_export_gates_script_origin() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.exec_command_line("set clipboard terminal")
    ed.exec_command_line("set clipboard.osc52 true")
    ed.exec_command_line("set clipboard.osc52.max 100")

    # Interactive clipboard changes should export.
    ed.set_clipboard_items(["hi"], kind="items")
    seq, err = ed.clipboard_terminal_export_sequence()
    assert err == ""
    assert seq is not None

    # Script-driven clipboard changes are gated by cap.clipboard-write.
    with ed.script_context():
        ed.set_clipboard_items(["hi"], kind="items")
    seq2, err2 = ed.clipboard_terminal_export_sequence()
    assert seq2 is None
    assert "cap.clipboard-write" in err2

    ed.exec_command_line("set cap.clipboard-write true")
    seq3, err3 = ed.clipboard_terminal_export_sequence()
    assert err3 == ""
    assert seq3 is not None
