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
    assert ed.prompt_current_section() == "Files"

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
    assert ed.prompt_current_section() == "External"


def test_helplinkpick_query_can_match_heading_context_terms() -> None:
    ed = Editor()
    assert ed.open_help_doc("help-browser") is True

    assert ed.exec_command_line("helplinkpick External micro editor") is True
    assert ed.prompt is not None
    assert ed.prompt.kind == "helplink"
    assert ed.prompt.suggestion_rows
    assert ed.prompt.suggestion_rows[0][0] == "micro editor"
    assert ed.prompt_current_section() == "External"


def test_helplinkpick_query_can_match_target_doc_title_terms() -> None:
    ed = Editor()
    assert ed.open_help_doc("help-browser") is True

    assert ed.exec_command_line("helplinkpick image metadata") is True
    assert ed.prompt is not None
    assert ed.prompt.kind == "helplink"
    assert ed.prompt.suggestion_rows
    assert ed.prompt.suggestion_rows[0][0] == "Metadata note"
    assert ed.prompt_current_section() == "Files"


def test_helplinkpick_query_can_match_target_heading_title_terms() -> None:
    ed = Editor()
    assert ed.open_help_doc("help-browser") is True

    assert ed.exec_command_line("helplinkpick hidden image metadata anchor") is True
    assert ed.prompt is not None
    assert ed.prompt.kind == "helplink"
    assert ed.prompt.suggestion_rows
    assert ed.prompt.suggestion_rows[0][0] == "Image anchor note"
    assert ed.prompt_current_section() == "Files"


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
    assert ed.prompt_current_section() == "Files"

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
    assert ed.prompt_current_section() == "External"


def test_helplinkpick_includes_footnote_references() -> None:
    ed = Editor()
    assert ed.open_help_doc("help-browser") is True

    assert ed.exec_command_line("helplinkpick") is True
    assert ed.prompt is not None
    assert ed.prompt.kind == "helplink"
    assert ed.prompt.suggestion_rows

    idx = None
    for i, row in enumerate(ed.prompt.suggestion_rows):
        if str(row[0]) == "[^help-footnote]":
            idx = i
            break
    assert idx is not None
    ed.prompt.suggest_index = int(idx)
    assert ed.prompt_current_section() == "Docs"

    want_line = next(i for i, ln in enumerate(ed.cur().buf.lines) if str(ln).startswith("[^help-footnote]:"))
    assert ed.submit_prompt() is True
    assert ed.cur().name.startswith("help:help-browser")
    assert ed.cur().cursors[ed.cur().primary].line == want_line


def test_helplinkpick_ignores_markdown_images() -> None:
    ed = Editor()
    assert ed.open_help_doc("help-browser") is True

    assert ed.exec_command_line("helplinkpick") is True
    assert ed.prompt is not None
    labels = [str(row[0]) for row in ed.prompt.suggestion_rows]
    assert "Vision" in labels
    assert "Vision ref" in labels
    assert "Vision image" not in labels
    assert "Vision ref image" not in labels


def test_helplinkpick_ignores_html_comment_links_and_defs() -> None:
    ed = Editor()
    assert ed.open_help_doc("help-browser") is True

    assert ed.exec_command_line("helplinkpick") is True
    assert ed.prompt is not None
    labels = [str(row[0]) for row in ed.prompt.suggestion_rows]
    targets = [str(row[2]) for row in ed.prompt.suggestion_rows]

    assert 'Visible link before comment' in labels
    assert 'Visible link after comment block' in labels
    assert 'Ghost inline comment link' not in labels
    assert 'Ghost block comment link' not in labels
    assert 'Ghost commented ref' not in labels
    assert '#^ghost-comment-footnote' not in targets


def test_helplinkpick_ignores_code_indented_defs_and_footnotes() -> None:
    ed = Editor()
    assert ed.open_help_doc('indented-codeish-markdown') is True

    assert ed.exec_command_line('helplinkpick') is True
    assert ed.prompt is not None
    labels = [str(row[0]) for row in ed.prompt.suggestion_rows]
    targets = [str(row[2]) for row in ed.prompt.suggestion_rows]

    assert 'Visible doc link' in labels
    assert 'Ghost four-space reference' not in labels
    assert '[^ghost-four-space-footnote]' not in labels
    assert '94-softwrap.md' not in targets


def test_helplinkpick_ignores_inline_links_inside_indented_codeish_blocks() -> None:
    ed = Editor()
    assert ed.open_help_doc('indented-codeish-markdown') is True

    assert ed.exec_command_line('helplinkpick') is True
    assert ed.prompt is not None
    labels = [str(row[0]) for row in ed.prompt.suggestion_rows]
    targets = [str(row[2]) for row in ed.prompt.suggestion_rows]

    assert 'Ghost indented inline link' not in labels
    assert '94-softwrap.md' not in targets
    assert 'https://example.invalid/indented-not-a-real-help-link' not in targets


def test_helplinkpick_ignores_markdown_looking_links_inside_inline_code() -> None:
    ed = Editor()
    assert ed.open_help_doc("help-browser") is True

    assert ed.exec_command_line("helplinkpick") is True
    assert ed.prompt is not None
    labels = [str(row[0]) for row in ed.prompt.suggestion_rows]
    targets = [str(row[2]) for row in ed.prompt.suggestion_rows]

    assert "Fake inline link" not in labels
    assert "Fake ref link" not in labels
    assert "99-missing.md" not in targets
    assert "https://example.invalid/not-a-real-help-link" not in targets



def test_helplinkpick_includes_destination_escape_examples() -> None:
    ed = Editor()
    assert ed.open_help_doc("help-browser") is True

    assert ed.exec_command_line('helplinkpick') is True
    assert ed.prompt is not None
    labels = [str(row[0]) for row in ed.prompt.suggestion_rows]
    targets = [str(row[2]) for row in ed.prompt.suggestion_rows]

    assert 'Space path doc (escaped space)' in labels
    assert 'Space path doc (percent-encoded)' in labels
    assert 'Paren topic doc' in labels
    assert 'Space path doc ref' in labels
    assert 'Paren topic doc ref' in labels
    assert '103-space path.md' in targets
    assert '104-paren(topic).md' in targets

def test_helplinkpick_includes_tiny_multiline_reference_examples() -> None:
    ed = Editor()
    assert ed.open_help_doc("help-browser") is True

    assert ed.exec_command_line('helplinkpick') is True
    assert ed.prompt is not None
    labels = [str(row[0]) for row in ed.prompt.suggestion_rows]
    targets = [str(row[2]) for row in ed.prompt.suggestion_rows]

    assert 'Space path doc ref (dest next line)' in labels
    assert 'Paren topic doc ref (dest + title next line)' in labels
    assert 'Space path doc ref (title next line)' in labels
    assert '103-space path.md' in targets
    assert '104-paren(topic).md' in targets


def test_helplinkpick_ignores_escaped_markdown_forms() -> None:
    ed = Editor()
    assert ed.open_help_doc("help-browser") is True

    assert ed.exec_command_line("helplinkpick") is True
    assert ed.prompt is not None
    labels = [str(row[0]) for row in ed.prompt.suggestion_rows]
    targets = [str(row[2]) for row in ed.prompt.suggestion_rows]

    assert 'Literal inline link' not in labels
    assert 'Literal ref link' not in labels
    assert 'Literal shortcut' not in labels
    assert targets.count('#^help-footnote') == 1
    assert '#^escaped-help-footnote' not in targets
    assert 'https://example.invalid/escaped-help-autolink' not in targets


def test_helplinkpick_includes_nested_bracket_label_links() -> None:
    ed = Editor()
    assert ed.open_help_doc("help-browser") is True

    assert ed.exec_command_line("helplinkpick") is True
    assert ed.prompt is not None
    labels = [str(row[0]) for row in ed.prompt.suggestion_rows]

    assert 'Vision [nested inline]' in labels
    assert 'Vision [nested ref]' in labels
    assert 'Vision [nested shortcut]' in labels


def test_helplinkpick_prefers_valid_inner_links_over_outer_nested_links() -> None:
    ed = Editor()
    assert ed.open_help_doc("help-browser") is True

    assert ed.exec_command_line("helplinkpick") is True
    assert ed.prompt is not None
    labels = [str(row[0]) for row in ed.prompt.suggestion_rows]

    assert 'Nested inner inline' in labels
    assert 'Nested inner ref' in labels
    assert 'Outer prose [Nested inner inline](94-softwrap.md)' not in labels
    assert 'Outer prose [Nested inner ref][visionref]' not in labels


def test_helplinkpick_ignores_empty_and_whitespace_only_labels() -> None:
    ed = Editor()
    assert ed.open_help_doc("help-browser") is True

    assert ed.exec_command_line("helplinkpick") is True
    assert ed.prompt is not None
    targets = [str(row[2]) for row in ed.prompt.suggestion_rows]

    assert '99-empty-inline-should-stay-prose.md' not in targets
    assert '99-space-inline-should-stay-prose.md' not in targets
    assert '99-space-ref-should-stay-prose.md' not in targets


def test_helplinkpick_ignores_markdown_looking_links_inside_fenced_code_blocks() -> None:
    ed = Editor()
    assert ed.open_help_doc("help-browser") is True

    assert ed.exec_command_line("helplinkpick") is True
    assert ed.prompt is not None
    labels = [str(row[0]) for row in ed.prompt.suggestion_rows]
    targets = [str(row[2]) for row in ed.prompt.suggestion_rows]

    assert 'Fake fenced inline link' not in labels
    assert 'Fake fenced ref' not in labels
    assert '99-missing.md' not in targets
    assert 'https://example.invalid/fenced-not-a-real-help-link' not in targets


def test_helplinkpick_ignores_raw_html_tag_and_autolink_precedence_inside_labels() -> None:
    ed = Editor()
    assert ed.open_help_doc("help-browser") is True

    assert ed.exec_command_line("helplinkpick") is True
    assert ed.prompt is not None
    labels = [str(row[0]) for row in ed.prompt.suggestion_rows]
    targets = [str(row[2]) for row in ed.prompt.suggestion_rows]

    assert 'Fake raw HTML tag <span title="' not in labels
    assert 'Fake raw HTML ref <span title="' not in labels
    assert not any('raw-help-autolink' in t for t in targets)
    assert 'Visible link after raw HTML precedence' in labels


def test_helplinkpick_ignores_raw_html_block_links_and_defs() -> None:
    ed = Editor()
    assert ed.open_help_doc("help-browser") is True

    assert ed.exec_command_line("helplinkpick") is True
    assert ed.prompt is not None
    labels = [str(row[0]) for row in ed.prompt.suggestion_rows]
    targets = [str(row[2]) for row in ed.prompt.suggestion_rows]

    assert 'Ghost html block link' not in labels
    assert 'Ghost pre block link' not in labels
    assert 'Visible link after raw HTML block' in labels
    assert 'Visible link after pre block' in labels
    assert 'Ghost html block ref' not in labels
    assert '#^ghost-html-block-footnote' not in targets


def test_helplinkpick_ignores_generic_html_block_links_and_defs() -> None:
    ed = Editor()
    assert ed.open_help_doc("help-browser") is True

    assert ed.exec_command_line("helplinkpick") is True
    assert ed.prompt is not None
    labels = [str(row[0]) for row in ed.prompt.suggestion_rows]
    targets = [str(row[2]) for row in ed.prompt.suggestion_rows]

    assert 'Ghost generic html block link' not in labels
    assert 'Visible link after generic raw HTML block' in labels
    assert 'Visible link after paragraph-adjacent generic tag' in labels
    assert 'Ghost generic html block ref' not in labels
    assert '#^ghost-generic-html-block-footnote' not in targets


def test_helplinkpick_includes_tiny_wrapped_inline_examples() -> None:
    ed = Editor()
    assert ed.open_help_doc("help-browser") is True

    rows = ed.help_link_rows()
    labels = [str(r[0]) for r in rows]

    assert 'Space path doc (inline dest next line)' in labels
    assert 'Paren topic doc (inline title next line)' in labels
    assert 'Angle space path doc (inline dest next line)' in labels
    assert 'Angle space path doc ref (dest next line)' in labels

