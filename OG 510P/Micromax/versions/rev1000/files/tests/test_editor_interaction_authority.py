from __future__ import annotations

from micromax_editor.editor import Editor
from micromax_editor.micromax_bridge import install_editor_hostcalls


def _editor(text: str = "one one\n") -> Editor:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer("main", text)
    return ed


def test_script_cannot_answer_trusted_qreplace_session() -> None:
    ed = _editor()
    assert ed.exec_command_line("qreplace one X -l") is True
    assert ed.qreplace is not None

    with ed.script_context(origin_id="script-a"):
        assert ed.qreplace_yes() is False

    assert ed.cur().buf.get_text() == "one one\n"
    assert ed.qreplace is not None
    assert "script context cannot answer qreplace" in ed.messages[-1]
    assert "trusted registration" in ed.messages[-1]

    assert ed.qreplace_quit() is True


def test_same_script_can_answer_own_qreplace_via_later_keypress() -> None:
    ed = _editor()

    with ed.script_context(origin_id="script-a"):
        assert ed.begin_query_replace("one", "X", literal=True) is True

    # The physical keypress happens after the script returned, but the active
    # capture mode carries the script-origin token back into the response.
    assert ed.dispatch_key("y") is True
    assert ed.cur().buf.get_text() == "X one\n"
    assert ed.qreplace is not None

    with ed.script_context(origin_id="script-a"):
        assert ed.qreplace_quit() is True



def test_qreplace_accept_marks_script_dirty_before_session_finishes() -> None:
    ed = _editor()
    target = ed.cur()

    with ed.script_context(origin_id="script-a"):
        assert ed.begin_query_replace("one", "X", literal=True) is True
        assert ed.qreplace_yes() is True

    assert ed.qreplace is not None
    assert target.buf.get_text() == "X one\n"
    assert target.script_dirty_since_sync is True
    assert ed.undo.depth() == 0

    with ed.script_context(origin_id="script-a"):
        assert ed.qreplace_quit() is True
    assert ed.undo.depth() == 1


def test_independent_script_cannot_cancel_other_script_qreplace() -> None:
    ed = _editor()

    with ed.script_context(origin_id="script-a"):
        assert ed.begin_query_replace("one", "X", literal=True) is True

    with ed.script_context(origin_id="script-b"):
        assert ed.qreplace_quit() is False

    assert ed.qreplace is not None
    assert "different script origin" in ed.messages[-1]

    with ed.script_context(origin_id="script-a"):
        assert ed.qreplace_quit() is True



def test_script_cannot_approve_trusted_open_url_confirmation() -> None:
    ed = _editor()
    opened: list[str] = []
    ed._open_url_fn = lambda url, new=0: opened.append(str(url)) or True
    assert ed.exec_command_line("set cap.open-url true") is True
    assert ed.begin_open_url_confirm("https://example.invalid/trusted", source="help") is True

    with ed.script_context(origin_id="script-a"):
        assert ed.run_action("OpenUrlYes") is False

    assert opened == []
    assert ed._pending_open_url == "https://example.invalid/trusted"
    assert ed.current_capture_key_mode() == "openurl"
    assert "script context cannot approve openurl" in ed.messages[-1]
    assert "trusted registration" in ed.messages[-1]

    assert ed.run_action("OpenUrlNo") is True



def test_same_script_can_approve_own_open_url_confirmation_via_later_keypress() -> None:
    ed = _editor()
    opened: list[str] = []
    ed._open_url_fn = lambda url, new=0: opened.append(str(url)) or True
    assert ed.exec_command_line("set cap.open-url true") is True

    with ed.script_context(origin_id="script-a"):
        assert ed.begin_open_url_confirm("https://example.invalid/script", source="command") is True

    assert ed.dispatch_key("y") is True
    assert opened == ["https://example.invalid/script"]
    assert ed._pending_open_url is None



def test_independent_script_cannot_copy_other_script_open_url_confirmation() -> None:
    ed = _editor()
    assert ed.exec_command_line("set cap.open-url true") is True

    with ed.script_context(origin_id="script-a"):
        assert ed.begin_open_url_confirm("https://example.invalid/script", source="command") is True

    with ed.script_context(origin_id="script-b"):
        assert ed.run_action("OpenUrlCopy") is False

    assert ed.clipboard_items == []
    assert ed._pending_open_url == "https://example.invalid/script"
    assert "different script origin" in ed.messages[-1]

    with ed.script_context(origin_id="script-a"):
        assert ed.run_action("OpenUrlNo") is True


def test_script_cannot_replace_trusted_qreplace_session_before_answering() -> None:
    ed = _editor("one two\n")
    assert ed.exec_command_line("qreplace one X -l") is True
    original = ed.qreplace
    assert original is not None

    with ed.script_context(origin_id="script-a"):
        assert ed.begin_query_replace("two", "Y", literal=True) is False

    assert ed.qreplace is original
    assert ed.current_capture_key_mode() == "qreplace"
    assert ed.cur().buf.get_text() == "one two\n"
    assert "script context cannot replace qreplace" in ed.messages[-1]

    assert ed.qreplace_quit() is True


def test_script_cannot_replace_trusted_open_url_confirmation() -> None:
    ed = _editor()
    assert ed.exec_command_line("set cap.open-url true") is True
    assert ed.begin_open_url_confirm("https://example.invalid/first", source="help") is True
    original_authority = ed._pending_open_url_authority

    with ed.script_context(origin_id="script-a"):
        assert ed.begin_open_url_confirm("https://example.invalid/second", source="command") is False

    assert ed._pending_open_url == "https://example.invalid/first"
    assert ed._pending_open_url_authority == original_authority
    assert ed.current_capture_key_mode() == "openurl"
    assert "script context cannot replace openurl" in ed.messages[-1]

    assert ed.run_action("OpenUrlNo") is True
