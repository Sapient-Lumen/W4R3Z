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


def test_helplinkcopy_copies_target_under_cursor() -> None:
    ed = Editor()
    assert ed.open_help_doc("help-browser") is True

    _set_cursor_on_substring(ed, "Softwrap")
    assert ed.exec_command_line("helplinkcopy") is True
    assert ed.clipboard_text().strip() == "94-softwrap.md"


def test_docs_buffer_y_copies_target_under_cursor() -> None:
    ed = Editor()
    assert ed.open_help_doc("help-browser") is True

    _set_cursor_on_substring(ed, "Vision")
    assert ed.dispatch_key("y") is True
    assert ed.clipboard_text().strip() == "00-vision.md"


def test_external_help_link_requires_confirmation_when_enabled() -> None:
    ed = Editor()
    assert ed.open_help_doc("help-browser") is True
    ed.options.set("cap.open-url", "true")

    opened: list[str] = []

    def _opener(url: str, new: int = 0):
        opened.append(url)
        return True

    ed._open_url_fn = _opener

    _set_cursor_on_substring(ed, "micro editor")

    # Starts a confirmation mode; does not open yet.
    assert ed.exec_command_line("helpfollow") is True
    assert ed.current_key_mode() == "openurl"
    assert opened == []

    # Copy cancels and copies.
    assert ed.dispatch_key("c") is True
    assert opened == []
    assert ed.clipboard_text().strip() == "https://micro-editor.github.io/"
    assert ed.current_key_mode() != "openurl"

    # Try again and accept.
    assert ed.exec_command_line("helpfollow") is True
    assert ed.dispatch_key("y") is True
    assert opened == ["https://micro-editor.github.io/"]


def test_external_help_link_cancel_does_not_open() -> None:
    ed = Editor()
    assert ed.open_help_doc("help-browser") is True
    ed.options.set("cap.open-url", "true")

    opened: list[str] = []
    ed._open_url_fn = lambda url, new=0: opened.append(url) or True

    _set_cursor_on_substring(ed, "micro editor")
    assert ed.exec_command_line("helpfollow") is True
    assert ed.dispatch_key("n") is True
    assert opened == []
