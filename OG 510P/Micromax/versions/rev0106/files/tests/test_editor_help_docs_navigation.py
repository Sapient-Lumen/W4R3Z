from __future__ import annotations


from micromax_editor.editor import Editor
from micromax_editor.buffer import Cursor


def _set_cursor_on_substring(ed: Editor, needle: str) -> None:
    eb = ed.cur()
    for i, line in enumerate(eb.buf.lines):
        s = str(line)
        if needle in s:
            col = s.index(needle)
            eb.cursors[0] = Cursor(i, col)
            eb.primary = 0
            return
    raise AssertionError(f"needle not found: {needle}")


def test_helpfollow_and_helpback_navigate_between_docs_pages() -> None:
    ed = Editor()
    assert ed.open_help_doc("help-browser") is True
    assert ed.cur().name.startswith("help:")

    _set_cursor_on_substring(ed, "Softwrap")
    assert ed.exec_command_line("helpfollow") is True
    assert ed.cur().name.startswith("help:softwrap")

    # helpback returns to the prior docs page.
    assert ed.exec_command_line("helpback") is True
    assert ed.cur().name.startswith("help:help-browser")




def test_helpfollow_can_follow_reference_style_link() -> None:
    ed = Editor()
    assert ed.open_help_doc("help-browser") is True

    _set_cursor_on_substring(ed, "Vision ref")
    assert ed.exec_command_line("helpfollow") is True
    assert ed.cur().name.startswith("help:vision")



def test_helpfollow_can_follow_shortcut_reference_link() -> None:
    ed = Editor()
    assert ed.open_help_doc("help-browser") is True

    _set_cursor_on_substring(ed, "Vision shortcut")
    assert ed.exec_command_line("helpfollow") is True
    assert ed.cur().name.startswith("help:vision")


def test_helpfollow_autolink_is_detected_and_blocked_cleanly() -> None:
    ed = Editor()
    assert ed.open_help_doc("help-browser") is True

    _set_cursor_on_substring(ed, "https://micro-editor.github.io/")
    assert ed.exec_command_line("helpfollow") is False
    assert "external link" in (ed.messages[-1] if ed.messages else "")


def test_helpfollow_external_link_is_blocked_cleanly() -> None:
    ed = Editor()
    assert ed.open_help_doc("help-browser") is True
    _set_cursor_on_substring(ed, "micro editor")
    assert ed.exec_command_line("helpfollow") is False
    assert "external link" in (ed.messages[-1] if ed.messages else "")


def test_help_docs_keys_enter_and_backspace_navigate() -> None:
    ed = Editor()
    assert ed.open_help_doc("help-browser") is True
    _set_cursor_on_substring(ed, "Softwrap")

    # Enter follows link under cursor.
    assert ed.dispatch_key("Enter") is True
    assert ed.cur().name.startswith("help:softwrap")

    # Backspace returns to previous page.
    assert ed.dispatch_key("Backspace") is True
    assert ed.cur().name.startswith("help:help-browser")
