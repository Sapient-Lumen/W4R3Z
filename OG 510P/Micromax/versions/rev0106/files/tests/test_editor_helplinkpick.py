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


def test_helplinkpick_opens_link_target_doc() -> None:
    ed = Editor()
    assert ed.open_help_doc("help-browser") is True

    assert ed.exec_command_line("helplinkpick") is True
    assert ed.prompt is not None
    assert ed.prompt.kind == "helplink"
    assert ed.prompt.suggestion_rows

    # Select the Softwrap link.
    idx = None
    for i, row in enumerate(ed.prompt.suggestion_rows):
        if str(row[0]) == "Softwrap":
            idx = i
            break
    assert idx is not None
    ed.prompt.suggest_index = int(idx)

    # UX: link classification is reflected in prompt section naming.
    assert ed.prompt_current_section() == "File link"

    assert ed.submit_prompt() is True
    assert ed.cur().name.startswith("help:softwrap")


def test_helplinkpick_sections_classify_external_links() -> None:
    ed = Editor()
    assert ed.open_help_doc("help-browser") is True

    assert ed.exec_command_line("helplinkpick") is True
    assert ed.prompt is not None
    assert ed.prompt.kind == "helplink"
    assert ed.prompt.suggestion_rows

    idx = None
    for i, row in enumerate(ed.prompt.suggestion_rows):
        if str(row[0]) == "micro editor":
            idx = i
            break
    assert idx is not None
    ed.prompt.suggest_index = int(idx)
    assert ed.prompt_current_section() == "External link"


def test_helplinkpick_requires_docs_buffer() -> None:
    ed = Editor()
    ed.new_buffer("*scratch*", "")
    assert ed.exec_command_line("helplinkpick") is False


def test_helpfollow_can_open_external_link_when_enabled() -> None:
    ed = Editor()
    ed.options.set("cap.open-url", "true")
    ed.refresh_capabilities()

    opened: list[str] = []

    def _fake_open(url: str, new: int = 0) -> bool:
        opened.append(url)
        return True

    ed._open_url_fn = _fake_open

    assert ed.open_help_doc("help-browser") is True
    _set_cursor_on_substring(ed, "micro editor")
    # External links confirm by default when enabled.
    assert ed.exec_command_line("helpfollow") is True
    assert opened == []
    assert ed.current_key_mode() == "openurl"

    assert ed.dispatch_key("y") is True
    assert opened and opened[0].startswith("https://")
    assert "opened external link" in (ed.messages[-1] if ed.messages else "")


def test_helplinkpick_includes_reference_style_links() -> None:
    ed = Editor()
    assert ed.open_help_doc("help-browser") is True

    assert ed.exec_command_line("helplinkpick") is True
    assert ed.prompt is not None
    assert ed.prompt.kind == "helplink"
    assert ed.prompt.suggestion_rows

    idx = None
    for i, row in enumerate(ed.prompt.suggestion_rows):
        if str(row[0]) == "Vision ref":
            idx = i
            break
    assert idx is not None
    ed.prompt.suggest_index = int(idx)
    assert ed.prompt_current_section() == "File link"

    assert ed.submit_prompt() is True
    assert ed.cur().name.startswith("help:vision")


def test_helplinkpick_sections_classify_autolinks() -> None:
    ed = Editor()
    assert ed.open_help_doc("help-browser") is True

    assert ed.exec_command_line("helplinkpick") is True
    assert ed.prompt is not None
    assert ed.prompt.kind == "helplink"
    assert ed.prompt.suggestion_rows

    idx = None
    for i, row in enumerate(ed.prompt.suggestion_rows):
        if str(row[0]).startswith("https://micro-editor.github.io/"):
            idx = i
            break
    assert idx is not None
    ed.prompt.suggest_index = int(idx)
    assert ed.prompt_current_section() == "External link"
