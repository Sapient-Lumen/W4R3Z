from __future__ import annotations


from micromax_editor.editor import (
    Editor,
    md_html_block_line_flags,
    md_inline_link_target,
    md_inline_link_target_multiline,
    md_leading_spaces_upto3,
    md_link_matches,
    md_reference_def_target,
    md_reference_def_target_info,
)
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
    eb0 = ed.cur()
    c0 = eb0.cursors[eb0.primary]
    assert ed.exec_command_line("helpfollow") is True
    assert ed.cur().name.startswith("help:softwrap")
    assert ed.status_model()["last_message"] == "helpjump: softwrap @ 1:0"

    # helpback returns to the prior docs page.
    assert ed.exec_command_line("helpback") is True
    assert ed.cur().name.startswith("help:help-browser")
    assert ed.status_model()["last_message"] == f"helpback: help-browser @ {c0.line + 1}:{c0.col}"


def test_helpback_empty_history_reports_typed_feedback() -> None:
    ed = Editor()

    assert ed.exec_command_line("helpback") is False
    assert ed.messages[-1] == "helpback: back stack empty"

def test_helpfollow_requires_docs_buffer_with_typed_feedback() -> None:
    ed = Editor()
    ed.new_buffer("*t*", "hi")

    assert ed.exec_command_line("helpfollow") is False
    assert ed.messages[-1] == "helpfollow: not in a docs buffer"


def test_helpfollow_without_link_reports_typed_feedback() -> None:
    ed = Editor()
    assert ed.open_help_doc("help-browser") is True

    _set_cursor_on_substring(ed, "This page exists mostly")
    assert ed.exec_command_line("helpfollow") is False
    assert ed.messages[-1] == "helpfollow: no link under cursor"



def test_helpfollow_missing_fragment_reports_typed_helpjump_miss() -> None:
    ed = Editor()
    assert ed.open_help_doc("help-browser") is True

    eb = ed.cur()
    eb.buf.set_text("[Missing section](#zzz-no-such-section)\n")
    _set_cursor_on_substring(ed, "Missing section")

    assert ed.exec_command_line("helpfollow") is False
    assert ed.messages[-1] == "helpjump: no section or footnote: #zzz-no-such-section"

def test_helpfollow_missing_doc_reports_typed_doc_miss() -> None:
    ed = Editor()
    assert ed.open_help_doc("help-browser") is True

    eb = ed.cur()
    eb.buf.set_text("[Missing](zzz-no-such-doc)\n")
    _set_cursor_on_substring(ed, "Missing")

    assert ed.exec_command_line("helpfollow") is False
    assert ed.status_model()["last_message"] == "help docs: no such doc: zzz-no-such-doc"


def test_helpback_missing_doc_reports_typed_doc_miss() -> None:
    ed = Editor()
    assert ed.open_help_doc("help-browser") is True
    ed._help_stack = ["zzz-no-such-doc"]

    assert ed.exec_command_line("helpback") is False
    assert ed.status_model()["last_message"] == "helpback: missing doc: zzz-no-such-doc"
    assert ed._help_stack == ["zzz-no-such-doc"]


def test_helpback_restores_saved_cursor_after_prior_help_buffer_was_closed() -> None:
    ed = Editor()
    assert ed.open_help_doc("help-browser") is True

    _set_cursor_on_substring(ed, "Softwrap")
    eb0 = ed.cur()
    c0 = eb0.cursors[eb0.primary]
    assert ed.exec_command_line("helpfollow") is True
    assert ed.cur().name.startswith("help:softwrap")

    assert ed.close_buffer("help:help-browser", force=True) is True
    assert "help:help-browser" not in ed.buffers

    assert ed.exec_command_line("helpback") is True
    assert ed.cur().name.startswith("help:help-browser")
    c = ed.cur().cursors[ed.cur().primary]
    assert c.line == c0.line
    assert c.col == c0.col
    assert ed.status_model()["last_message"] == f"helpback: help-browser @ {c0.line + 1}:{c0.col}"


def test_helpforward_empty_history_reports_typed_feedback() -> None:
    ed = Editor()

    assert ed.exec_command_line("helpforward") is False
    assert ed.messages[-1] == "helpforward: forward stack empty"


def test_helpback_and_helpforward_keep_separate_back_and_forward_targets() -> None:
    ed = Editor()
    assert ed.open_help_doc("help-browser") is True

    _set_cursor_on_substring(ed, "Softwrap")
    eb0 = ed.cur()
    c0 = eb0.cursors[eb0.primary]
    assert ed.exec_command_line("helpfollow") is True
    eb1 = ed.cur()
    c1 = eb1.cursors[eb1.primary]

    assert ed.exec_command_line("helpback") is True
    st_back = ed.status_model()
    assert st_back["help_topic"] == "help-browser"
    assert st_back["help_back_available"] == 0
    assert st_back["help_forward_available"] == 1
    assert st_back["help_forward_count"] == 1
    assert st_back["help_forward_target"] == "softwrap"
    assert st_back["help_forward_position"] == f"{c1.line + 1}:{c1.col}"
    assert st_back["help_navigation_summary"] == f"help-browser -> softwrap @ {c1.line + 1}:{c1.col} (+1)"

    assert ed.exec_command_line("helpforward") is True
    st_forward = ed.status_model()
    assert st_forward["help_topic"] == "softwrap"
    assert st_forward["help_back_available"] == 1
    assert st_forward["help_back_count"] == 1
    assert st_forward["help_back_target"] == "help-browser"
    assert st_forward["help_back_position"] == f"{c0.line + 1}:{c0.col}"
    assert st_forward["help_forward_available"] == 0
    assert st_forward["help_forward_count"] == 0
    assert st_forward["help_navigation_summary"] == f"softwrap <- help-browser @ {c0.line + 1}:{c0.col} (+1)"


def test_new_docs_navigation_clears_helpforward_history() -> None:
    ed = Editor()
    assert ed.open_help_doc("help-browser") is True

    _set_cursor_on_substring(ed, "Softwrap")
    assert ed.exec_command_line("helpfollow") is True
    assert ed.exec_command_line("helpback") is True

    _set_cursor_on_substring(ed, "Vision")
    assert ed.exec_command_line("helpfollow") is True
    st = ed.status_model()
    assert st["help_topic"] == "vision"
    assert st["help_back_available"] == 1
    assert st["help_back_target"] == "help-browser"
    assert st["help_forward_available"] == 0
    assert st["help_forward_count"] == 0

    assert ed.exec_command_line("helpforward") is False
    assert ed.messages[-1] == "helpforward: forward stack empty"


def test_helpforward_missing_doc_reports_typed_doc_miss() -> None:
    ed = Editor()
    assert ed.open_help_doc("help-browser") is True
    ed._help_forward_stack = ["zzz-no-such-doc"]

    assert ed.exec_command_line("helpforward") is False
    assert ed.status_model()["last_message"] == "helpforward: missing doc: zzz-no-such-doc"


def test_helpresume_reopens_last_session_help_target_after_switching_away() -> None:
    ed = Editor()
    assert ed.open_help_doc("help-browser") is True

    _set_cursor_on_substring(ed, "Softwrap")
    eb0 = ed.cur()
    c0 = eb0.cursors[eb0.primary]
    ed.new_buffer("*scratch*", "hi")

    st = ed.status_model()
    assert st["help_navigation_active"] == 0
    assert st["help_navigation_dormant"] == 1
    assert st["help_session_topic"] == "help-browser"
    assert st["help_session_position"] == f"{c0.line + 1}:{c0.col}"

    assert ed.exec_command_line("helpresume") is True
    assert ed.cur().name.startswith("help:help-browser")
    c = ed.cur().cursors[ed.cur().primary]
    assert c.line == c0.line
    assert c.col == c0.col
    assert ed.status_model()["last_message"] == f"helpresume: help-browser @ {c0.line + 1}:{c0.col}"


def test_help_navigation_model_separates_current_page_from_back_target() -> None:
    ed = Editor()
    assert ed.open_help_doc("help-browser") is True

    st0 = ed.status_model()
    assert st0["help_topic"] == "help-browser"
    assert st0["help_back_available"] == 0
    assert st0["help_back_count"] == 0
    assert st0["help_back_target"] == ""
    assert st0["help_forward_available"] == 0
    assert st0["help_forward_count"] == 0
    assert st0["help_forward_target"] == ""
    assert st0["help_navigation_scope"] == "session"
    assert st0["help_navigation_persisted"] == 0
    assert st0["help_navigation_summary"] == "help-browser"

    _set_cursor_on_substring(ed, "Softwrap")
    eb0 = ed.cur()
    c0 = eb0.cursors[eb0.primary]
    assert ed.exec_command_line("helpfollow") is True

    st = ed.status_model()
    assert st["help_topic"] == "softwrap"
    assert st["help_back_available"] == 1
    assert st["help_back_count"] == 1
    assert st["help_back_target"] == "help-browser"
    assert st["help_back_position"] == f"{c0.line + 1}:{c0.col}"
    assert st["help_forward_available"] == 0
    assert st["help_forward_count"] == 0
    assert st["help_forward_target"] == ""
    assert st["help_navigation_scope"] == "session"
    assert st["help_navigation_persisted"] == 0
    assert st["help_navigation_summary"] == f"softwrap <- help-browser @ {c0.line + 1}:{c0.col} (+1)"


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


def test_helpfollow_can_follow_same_page_fragment_link() -> None:
    ed = Editor()
    assert ed.open_help_doc("help-browser") is True

    want_line = next(i for i, ln in enumerate(ed.cur().buf.lines) if "## Outline picker" in str(ln))
    _set_cursor_on_substring(ed, "Outline picker section")

    assert ed.exec_command_line("helpfollow") is True
    assert ed.cur().name.startswith("help:help-browser")
    c = ed.cur().cursors[ed.cur().primary]
    assert c.line == want_line
    assert ed.status_model()["last_message"] == f"helpjump: help-browser @ {want_line + 1}:{c.col}"




def test_helpfollow_same_page_fragment_pushes_local_help_history() -> None:
    ed = Editor()
    assert ed.open_help_doc("help-browser") is True

    _set_cursor_on_substring(ed, "Outline picker section")
    eb0 = ed.cur()
    c0 = eb0.cursors[eb0.primary]

    assert ed.exec_command_line("helpfollow") is True
    c1 = ed.cur().cursors[ed.cur().primary]
    st = ed.status_model()
    assert st["help_topic"] == "help-browser"
    assert st["help_position"] == f"{c1.line + 1}:{c1.col}"
    assert st["help_back_available"] == 1
    assert st["help_back_count"] == 1
    assert st["help_back_target"] == "help-browser"
    assert st["help_back_position"] == f"{c0.line + 1}:{c0.col}"
    assert st["help_navigation_summary"] == f"help-browser @ {c1.line + 1}:{c1.col} <- help-browser @ {c0.line + 1}:{c0.col} (+1)"

    assert ed.exec_command_line("helpback") is True
    c_back = ed.cur().cursors[ed.cur().primary]
    assert (c_back.line, c_back.col) == (c0.line, c0.col)

    assert ed.exec_command_line("helpforward") is True
    c_forward = ed.cur().cursors[ed.cur().primary]
    assert (c_forward.line, c_forward.col) == (c1.line, c1.col)


def test_helpjump_pushes_same_page_help_history() -> None:
    ed = Editor()
    assert ed.open_help_doc("help-browser") is True

    c0 = ed.cur().cursors[ed.cur().primary]
    assert ed.exec_command_line("helpjump Outline picker") is True
    c1 = ed.cur().cursors[ed.cur().primary]
    assert (c1.line, c1.col) != (c0.line, c0.col)

    st = ed.status_model()
    assert st["help_topic"] == "help-browser"
    assert st["help_position"] == f"{c1.line + 1}:{c1.col}"
    assert st["help_back_available"] == 1
    assert st["help_back_target"] == "help-browser"
    assert st["help_back_position"] == f"{c0.line + 1}:{c0.col}"
    assert st["help_navigation_summary"] == f"help-browser @ {c1.line + 1}:{c1.col} <- help-browser @ {c0.line + 1}:{c0.col} (+1)"

    assert ed.exec_command_line("helpback") is True
    c_back = ed.cur().cursors[ed.cur().primary]
    assert (c_back.line, c_back.col) == (c0.line, c0.col)

def test_helpfollow_can_follow_cross_doc_fragment_link() -> None:
    ed = Editor()
    assert ed.open_help_doc("help-browser") is True

    _set_cursor_on_substring(ed, "Vision key commitment")
    assert ed.exec_command_line("helpfollow") is True
    assert ed.cur().name.startswith("help:vision")

    want_line = next(i for i, ln in enumerate(ed.cur().buf.lines) if "## Key commitment" in str(ln))
    assert ed.cur().cursors[ed.cur().primary].line == want_line


def test_helpfollow_can_follow_setext_fragment_links() -> None:
    ed = Editor()
    assert ed.open_help_doc("setext-headings") is True

    want_line = next(i for i, ln in enumerate(ed.cur().buf.lines) if "Outline section" in str(ln))
    _set_cursor_on_substring(ed, "Jump to outline section")

    assert ed.exec_command_line("helpfollow") is True
    assert ed.cur().name.startswith("help:setext-headings")
    assert ed.cur().cursors[ed.cur().primary].line == want_line


def test_helpfollow_can_follow_explicit_setext_heading_id_fragment_link() -> None:
    ed = Editor()
    assert ed.open_help_doc("setext-headings") is True

    want_line = next(i for i, ln in enumerate(ed.cur().buf.lines) if "Explicit setext target {#custom-setext-frag}" in str(ln))
    _set_cursor_on_substring(ed, "Jump to explicit setext fragment")

    assert ed.exec_command_line("helpfollow") is True
    assert ed.cur().name.startswith("help:setext-headings")
    assert ed.cur().cursors[ed.cur().primary].line == want_line


def test_helpfollow_can_follow_multiline_setext_fragment_links() -> None:
    ed = Editor()
    assert ed.open_help_doc("multiline-setext-headings") is True

    want_line = next(i for i, ln in enumerate(ed.cur().buf.lines) if "Outline section for" in str(ln))
    _set_cursor_on_substring(ed, "Jump to multi-line outline section")

    assert ed.exec_command_line("helpfollow") is True
    assert ed.cur().name.startswith("help:multiline-setext-headings")
    assert ed.cur().cursors[ed.cur().primary].line == want_line


def test_helpfollow_can_follow_explicit_multiline_setext_heading_id_fragment_link() -> None:
    ed = Editor()
    assert ed.open_help_doc("multiline-setext-headings") is True

    want_line = next(i for i, ln in enumerate(ed.cur().buf.lines) if "Explicit multi-line" in str(ln))
    _set_cursor_on_substring(ed, "Jump to explicit multi-line setext fragment")

    assert ed.exec_command_line("helpfollow") is True
    assert ed.cur().name.startswith("help:multiline-setext-headings")
    assert ed.cur().cursors[ed.cur().primary].line == want_line


def test_helpfollow_can_follow_explicit_heading_id_fragment_link() -> None:
    ed = Editor()
    assert ed.open_help_doc("help-browser") is True

    want_line = next(i for i, ln in enumerate(ed.cur().buf.lines) if "## Explicit fragment target {#custom-frag}" in str(ln))
    _set_cursor_on_substring(ed, "Explicit fragment target")

    assert ed.exec_command_line("helpfollow") is True
    assert ed.cur().name.startswith("help:help-browser")
    assert ed.cur().cursors[ed.cur().primary].line == want_line


def test_helpfollow_autolink_is_detected_and_blocked_cleanly() -> None:
    ed = Editor()
    assert ed.open_help_doc("help-browser") is True

    _set_cursor_on_substring(ed, "https://micro-editor.github.io/")
    assert ed.exec_command_line("helpfollow") is False
    assert ed.messages[-1] == "helpfollow: disabled (cap.open-url). Enable with: set cap.open-url true\nhttps://micro-editor.github.io/"


def test_helpfollow_external_link_is_blocked_cleanly() -> None:
    ed = Editor()
    assert ed.open_help_doc("help-browser") is True
    _set_cursor_on_substring(ed, "micro editor")
    assert ed.exec_command_line("helpfollow") is False
    assert ed.messages[-1] == "helpfollow: disabled (cap.open-url). Enable with: set cap.open-url true\nhttps://micro-editor.github.io/"


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


def test_helpfollow_can_follow_footnote_reference() -> None:
    ed = Editor()
    assert ed.open_help_doc("help-browser") is True

    want_line = next(i for i, ln in enumerate(ed.cur().buf.lines) if str(ln).startswith("[^help-footnote]:"))
    _set_cursor_on_substring(ed, "[^help-footnote]")

    assert ed.exec_command_line("helpfollow") is True
    assert ed.cur().name.startswith("help:help-browser")
    assert ed.cur().cursors[ed.cur().primary].line == want_line


def test_helpfollow_does_not_treat_images_as_docs_links() -> None:
    ed = Editor()
    assert ed.open_help_doc("help-browser") is True

    _set_cursor_on_substring(ed, "Vision image")
    assert ed.exec_command_line("helpfollow") is False
    assert "no link under cursor" in (ed.messages[-1] if ed.messages else "")


def test_md_link_matches_reject_outer_links_that_contain_valid_inner_links() -> None:
    defs = {"visionref": "00-vision.md"}

    got_inline = md_link_matches('[Outer prose [Nested inner inline](94-softwrap.md)](00-vision.md)', defs)
    got_ref = md_link_matches('[Outer prose [Nested inner ref][visionref]](00-vision.md)', defs)

    assert [m.display for m in got_inline] == ['Nested inner inline']
    assert [m.target for m in got_inline] == ['94-softwrap.md']
    assert [m.display for m in got_ref] == ['Nested inner ref']
    assert [m.target for m in got_ref] == ['00-vision.md']


def test_md_link_matches_reject_empty_and_whitespace_only_labels() -> None:
    defs = {
        'visionref': '00-vision.md',
        '': '99-empty-shortcut-should-stay-prose.md',
        ' ': '99-space-shortcut-should-stay-prose.md',
        'space-only-ref': '99-space-ref-should-stay-prose.md',
    }

    assert md_link_matches('[](99-empty-inline-should-stay-prose.md)', defs) == []
    assert md_link_matches('[ ](99-space-inline-should-stay-prose.md)', defs) == []
    assert md_link_matches('[  ][space-only-ref]', defs) == []
    assert md_link_matches('[]', defs) == []
    assert md_link_matches('[   ]', defs) == []


def test_helpfollow_prefers_valid_inner_link_when_outer_label_contains_link() -> None:
    ed = Editor()
    assert ed.open_help_doc("help-browser") is True

    _set_cursor_on_substring(ed, "Outer prose ")
    assert ed.exec_command_line("helpfollow") is False
    assert "no link under cursor" in (ed.messages[-1] if ed.messages else "")

    _set_cursor_on_substring(ed, "Nested inner inline")
    assert ed.exec_command_line("helpfollow") is True
    assert ed.cur().name.startswith("help:softwrap")


def test_helpfollow_prefers_valid_inner_reference_link_when_outer_label_contains_link() -> None:
    ed = Editor()
    assert ed.open_help_doc("help-browser") is True

    _set_cursor_on_substring(ed, "Nested inner ref")
    assert ed.exec_command_line("helpfollow") is True
    assert ed.cur().name.startswith("help:vision")


def test_helpfollow_ignores_markdown_looking_links_inside_html_comments() -> None:
    ed = Editor()
    assert ed.open_help_doc("help-browser") is True

    _set_cursor_on_substring(ed, "Ghost inline comment link")
    assert ed.exec_command_line("helpfollow") is False
    assert "no link under cursor" in (ed.messages[-1] if ed.messages else "")

    _set_cursor_on_substring(ed, "Ghost block comment link")
    assert ed.exec_command_line("helpfollow") is False
    assert "no link under cursor" in (ed.messages[-1] if ed.messages else "")

    _set_cursor_on_substring(ed, "Visible link before comment")
    assert ed.exec_command_line("helpfollow") is True
    assert ed.cur().name.startswith("help:vision")


def test_helpfollow_ignores_comment_defined_refs_and_footnotes() -> None:
    ed = Editor()
    assert ed.open_help_doc("help-browser") is True

    _set_cursor_on_substring(ed, "Ghost commented ref")
    assert ed.exec_command_line("helpfollow") is False
    assert "no link under cursor" in (ed.messages[-1] if ed.messages else "")

    _set_cursor_on_substring(ed, "[^ghost-comment-footnote]")
    assert ed.exec_command_line("helpfollow") is False
    assert "no link under cursor" in (ed.messages[-1] if ed.messages else "")

    _set_cursor_on_substring(ed, "Visible link after comment block")
    assert ed.exec_command_line("helpfollow") is True
    assert ed.cur().name.startswith("help:softwrap")


def test_helpfollow_ignores_markdown_looking_links_inside_inline_code() -> None:
    ed = Editor()
    assert ed.open_help_doc("help-browser") is True

    _set_cursor_on_substring(ed, "Fake inline link")
    assert ed.exec_command_line("helpfollow") is False
    assert "no link under cursor" in (ed.messages[-1] if ed.messages else "")

    _set_cursor_on_substring(ed, "Fake ref link")
    assert ed.exec_command_line("helpfollow") is False
    assert "no link under cursor" in (ed.messages[-1] if ed.messages else "")

    _set_cursor_on_substring(ed, "https://example.invalid/not-a-real-help-link")
    assert ed.exec_command_line("helpfollow") is False
    assert "no link under cursor" in (ed.messages[-1] if ed.messages else "")



def test_md_inline_link_target_supports_tiny_destination_escapes() -> None:
    assert md_inline_link_target(r'103-space\ path.md') == '103-space path.md'
    assert md_inline_link_target(r'104-paren\(topic\).md') == '104-paren(topic).md'
    assert md_inline_link_target(r'104-paren\(topic\).md "title"') == '104-paren(topic).md'
    assert md_inline_link_target(r'103-space%20path.md') == '103-space%20path.md'


def test_md_leading_spaces_upto3_rejects_tabs_and_code_indent() -> None:
    assert md_leading_spaces_upto3('topic') == 0
    assert md_leading_spaces_upto3('   topic') == 3
    assert md_leading_spaces_upto3('    topic') is None
    assert md_leading_spaces_upto3('\ttopic') is None


def test_helpfollow_can_follow_inline_link_with_escaped_space_destination() -> None:
    ed = Editor()
    assert ed.open_help_doc("help-browser") is True

    _set_cursor_on_substring(ed, 'Space path doc (escaped space)')
    assert ed.exec_command_line('helpfollow') is True
    assert ed.cur().name.startswith('help:space path')


def test_helpfollow_can_follow_inline_link_with_percent_encoded_destination() -> None:
    ed = Editor()
    assert ed.open_help_doc("help-browser") is True

    _set_cursor_on_substring(ed, 'Space path doc (percent-encoded)')
    assert ed.exec_command_line('helpfollow') is True
    assert ed.cur().name.startswith('help:space path')


def test_helpfollow_can_follow_inline_link_with_escaped_paren_destination() -> None:
    ed = Editor()
    assert ed.open_help_doc("help-browser") is True

    _set_cursor_on_substring(ed, 'Paren topic doc')
    assert ed.exec_command_line('helpfollow') is True
    assert ed.cur().name.startswith('help:paren(topic)')


def test_md_reference_def_target_supports_tiny_multiline_reference_forms() -> None:
    assert md_reference_def_target('', r'103-space\ path.md') == '103-space path.md'
    assert md_reference_def_target('', r'104-paren\(topic\).md', '  "title"') == '104-paren(topic).md'
    assert md_reference_def_target(r'103-space\ path.md', '  "title"') == '103-space path.md'
    assert md_reference_def_target('', '  <103-space path.md>') == '103-space path.md'
    assert md_reference_def_target('', '  <103-space path.md>', '  "title"') == '103-space path.md'
    assert md_reference_def_target('<103-space path.md>"broken"') == ''


def test_md_inline_link_target_multiline_supports_tiny_wrapped_inline_forms() -> None:
    assert md_inline_link_target_multiline('', r'  103-space\ path.md)') == '103-space path.md'
    assert md_inline_link_target_multiline(r'104-paren\(topic\).md', '  "tiny title")') == '104-paren(topic).md'
    assert md_inline_link_target_multiline(r'103-space\ path.md', '  "tiny title"', '  )') == '103-space path.md'
    assert md_inline_link_target_multiline('', '  <103-space path.md>)') == '103-space path.md'
    assert md_inline_link_target_multiline('<103-space path.md>', '  "tiny title")') == '103-space path.md'
    assert md_inline_link_target_multiline(r'103-space\ path.md', '  "broken title" trailing') == ''
    assert md_inline_link_target_multiline('<103-space path.md>"broken")') == ''


def test_markdown_definition_parser_unescapes_tiny_destinations() -> None:
    ed = Editor()
    defs = ed._md_reference_defs([
        r'[space-path-doc]: 103-space\ path.md',
        r'[paren-topic-doc]: 104-paren\(topic\).md',
        '[percent-space-doc]: 103-space%20path.md',
    ])

    assert defs.get('space-path-doc') == '103-space path.md'
    assert defs.get('paren-topic-doc') == '104-paren(topic).md'
    assert defs.get('percent-space-doc') == '103-space%20path.md'


def test_markdown_definition_parser_supports_tiny_multiline_reference_definitions() -> None:
    ed = Editor()
    defs = ed._md_reference_defs([
        '[space-path-doc-multiline]:',
        r'  103-space\ path.md',
        '[paren-topic-doc-multiline]:',
        r'  104-paren\(topic\).md',
        '  "tiny title"',
        r'[space-path-doc-title-next-line]: 103-space\ path.md',
        '  "other title"',
        '[broken-doc]:',
        r'  103-space\ path.md',
        '  "broken title" trailing',
    ])

    assert defs.get('space-path-doc-multiline') == '103-space path.md'
    assert defs.get('paren-topic-doc-multiline') == '104-paren(topic).md'
    assert defs.get('space-path-doc-title-next-line') == '103-space path.md'
    assert 'broken-doc' not in defs


def test_markdown_definition_parser_ignores_code_indented_reference_definitions() -> None:
    ed = Editor()
    defs = ed._md_reference_defs([
        '   [ok-ref]: 00-vision.md',
        '    [ghost-four-space-ref]: 94-softwrap.md',
        '\t[ghost-tab-ref]: 94-softwrap.md',
    ])

    assert defs.get('ok-ref') == '00-vision.md'
    assert 'ghost-four-space-ref' not in defs
    assert 'ghost-tab-ref' not in defs


def test_markdown_footnote_parser_ignores_code_indented_definitions() -> None:
    ed = Editor()
    defs = ed._md_footnote_defs([
        '   [^ok-footnote]: yes',
        '    [^ghost-four-space-footnote]: no',
        '\t[^ghost-tab-footnote]: no',
    ])

    assert defs.get('ok-footnote') == (1, 4)
    assert 'ghost-four-space-footnote' not in defs
    assert 'ghost-tab-footnote' not in defs


def test_helpfollow_can_follow_tiny_wrapped_inline_links() -> None:
    ed = Editor()
    assert ed.open_help_doc("help-browser") is True

    _set_cursor_on_substring(ed, 'Space path doc (inline dest next line)')
    assert ed.exec_command_line('helpfollow') is True
    assert ed.cur().name.startswith('help:space path')

    assert ed.open_help_doc("help-browser") is True
    _set_cursor_on_substring(ed, 'Paren topic doc (inline title next line)')
    assert ed.exec_command_line('helpfollow') is True
    assert ed.cur().name.startswith('help:paren(topic)')

    assert ed.open_help_doc("help-browser") is True
    _set_cursor_on_substring(ed, 'Angle space path doc (inline dest next line)')
    assert ed.exec_command_line('helpfollow') is True
    assert ed.cur().name.startswith('help:space path')


def test_helpfollow_can_follow_reference_link_with_unescaped_destination() -> None:
    ed = Editor()
    assert ed.open_help_doc("help-browser") is True

    _set_cursor_on_substring(ed, 'Space path doc ref')
    assert ed.exec_command_line('helpfollow') is True
    assert ed.cur().name.startswith('help:space path')

    assert ed.exec_command_line('helpback') is True
    _set_cursor_on_substring(ed, 'Paren topic doc ref')
    assert ed.exec_command_line('helpfollow') is True
    assert ed.cur().name.startswith('help:paren(topic)')

def test_helpfollow_can_follow_multiline_reference_definitions() -> None:
    ed = Editor()
    assert ed.open_help_doc("help-browser") is True

    _set_cursor_on_substring(ed, 'Space path doc ref (dest next line)')
    assert ed.exec_command_line('helpfollow') is True
    assert ed.cur().name.startswith('help:space path')

    assert ed.exec_command_line('helpback') is True
    _set_cursor_on_substring(ed, 'Paren topic doc ref (dest + title next line)')
    assert ed.exec_command_line('helpfollow') is True
    assert ed.cur().name.startswith('help:paren(topic)')

    assert ed.exec_command_line('helpback') is True
    _set_cursor_on_substring(ed, 'Space path doc ref (title next line)')
    assert ed.exec_command_line('helpfollow') is True
    assert ed.cur().name.startswith('help:space path')

    assert ed.open_help_doc("help-browser") is True
    _set_cursor_on_substring(ed, 'Angle space path doc ref (dest next line)')
    assert ed.exec_command_line('helpfollow') is True
    assert ed.cur().name.startswith('help:space path')


def test_helpfollow_ignores_code_indented_reference_and_footnote_definitions() -> None:
    ed = Editor()
    assert ed.open_help_doc('indented-codeish-markdown') is True

    _set_cursor_on_substring(ed, 'Ghost four-space reference')
    assert ed.exec_command_line('helpfollow') is False
    assert 'no link under cursor' in (ed.messages[-1] if ed.messages else '')

    _set_cursor_on_substring(ed, '[^ghost-four-space-footnote]')
    assert ed.exec_command_line('helpfollow') is False
    assert 'no link under cursor' in (ed.messages[-1] if ed.messages else '')

    _set_cursor_on_substring(ed, 'Visible doc link')
    assert ed.exec_command_line('helpfollow') is True
    assert ed.cur().name.startswith('help:vision')


def test_helpfollow_ignores_escaped_markdown_forms() -> None:
    ed = Editor()
    assert ed.open_help_doc("help-browser") is True

    for needle in [
        "Literal inline link",
        "Literal ref link",
        "Literal shortcut",
        "^escaped-help-footnote",
        "https://example.invalid/escaped-help-autolink",
    ]:
        _set_cursor_on_substring(ed, needle)
        assert ed.exec_command_line("helpfollow") is False
        assert "no link under cursor" in (ed.messages[-1] if ed.messages else "")


def test_markdown_definition_parsers_ignore_escaped_definitions() -> None:
    ed = Editor()
    defs = ed._md_reference_defs([
        r'\[escaped-ref]: 00-vision.md',
        '[real-ref]: 00-vision.md',
    ])
    footdefs = ed._md_footnote_defs([
        r'\[^escaped-fn]: prose only',
        '[^real-fn]: actual footnote',
    ])

    assert 'escaped-ref' not in defs
    assert defs.get('real-ref') == '00-vision.md'
    assert 'escaped-fn' not in footdefs
    assert footdefs.get('real-fn') == (2, 1)


def test_helpfollow_can_follow_nested_bracket_label_links() -> None:
    ed = Editor()
    assert ed.open_help_doc("help-browser") is True

    _set_cursor_on_substring(ed, "Vision [nested inline]")
    assert ed.exec_command_line("helpfollow") is True
    assert ed.cur().name.startswith("help:vision")


def test_markdown_definition_parser_supports_nested_bracket_ids() -> None:
    ed = Editor()
    defs = ed._md_reference_defs([
        '[Vision [nested shortcut]]: 00-vision.md',
        '[real-ref]: 31-host-api.md',
    ])

    assert defs.get('vision [nested shortcut]') == '00-vision.md'
    assert defs.get('real-ref') == '31-host-api.md'


def test_helpfollow_ignores_markdown_looking_links_inside_fenced_code_blocks() -> None:
    ed = Editor()
    assert ed.open_help_doc("help-browser") is True

    _set_cursor_on_substring(ed, "Fake fenced inline link")
    assert ed.exec_command_line("helpfollow") is False
    assert "no link under cursor" in (ed.messages[-1] if ed.messages else "")

    _set_cursor_on_substring(ed, "Fake fenced ref")
    assert ed.exec_command_line("helpfollow") is False
    assert "no link under cursor" in (ed.messages[-1] if ed.messages else "")

    _set_cursor_on_substring(ed, "https://example.invalid/fenced-not-a-real-help-link")
    assert ed.exec_command_line("helpfollow") is False
    assert "no link under cursor" in (ed.messages[-1] if ed.messages else "")


def test_helpfollow_ignores_markdown_looking_links_inside_indented_codeish_blocks() -> None:
    ed = Editor()
    assert ed.open_help_doc("indented-codeish-markdown") is True

    _set_cursor_on_substring(ed, "Ghost indented inline link")
    assert ed.exec_command_line("helpfollow") is False
    assert "no link under cursor" in (ed.messages[-1] if ed.messages else "")

    _set_cursor_on_substring(ed, "https://example.invalid/indented-not-a-real-help-link")
    assert ed.exec_command_line("helpfollow") is False
    assert "no link under cursor" in (ed.messages[-1] if ed.messages else "")


def test_helpfollow_ignores_raw_html_tag_and_autolink_precedence_inside_labels() -> None:
    ed = Editor()
    assert ed.open_help_doc("help-browser") is True

    _set_cursor_on_substring(ed, "Fake raw HTML tag")
    assert ed.exec_command_line("helpfollow") is False
    assert "no link under cursor" in (ed.messages[-1] if ed.messages else "")

    _set_cursor_on_substring(ed, "Fake raw HTML ref")
    assert ed.exec_command_line("helpfollow") is False
    assert "no link under cursor" in (ed.messages[-1] if ed.messages else "")

    _set_cursor_on_substring(ed, "Fake raw HTML autolink")
    assert ed.exec_command_line("helpfollow") is False
    assert "no link under cursor" in (ed.messages[-1] if ed.messages else "")

    _set_cursor_on_substring(ed, "Visible link after raw HTML precedence")
    assert ed.exec_command_line("helpfollow") is True
    assert ed.cur().name.startswith("help:vision")


def test_helpfollow_ignores_markdown_looking_links_inside_raw_html_blocks() -> None:
    ed = Editor()
    assert ed.open_help_doc("help-browser") is True

    _set_cursor_on_substring(ed, "Ghost html block link")
    assert ed.exec_command_line("helpfollow") is False
    assert "no link under cursor" in (ed.messages[-1] if ed.messages else "")

    _set_cursor_on_substring(ed, "Ghost pre block link")
    assert ed.exec_command_line("helpfollow") is False
    assert "no link under cursor" in (ed.messages[-1] if ed.messages else "")

    _set_cursor_on_substring(ed, "Visible link after raw HTML block")
    assert ed.exec_command_line("helpfollow") is True
    assert ed.cur().name.startswith("help:softwrap")


def test_helpfollow_ignores_html_block_defined_refs_and_footnotes() -> None:
    ed = Editor()
    assert ed.open_help_doc("help-browser") is True

    _set_cursor_on_substring(ed, "Ghost html block ref")
    assert ed.exec_command_line("helpfollow") is False
    assert "no link under cursor" in (ed.messages[-1] if ed.messages else "")

    _set_cursor_on_substring(ed, "[^ghost-html-block-footnote]")
    assert ed.exec_command_line("helpfollow") is False
    assert "no link under cursor" in (ed.messages[-1] if ed.messages else "")

    _set_cursor_on_substring(ed, "Visible link after pre block")
    assert ed.exec_command_line("helpfollow") is True
    assert ed.cur().name.startswith("help:vision")


def test_markdown_definition_parsers_ignore_raw_html_blocks() -> None:
    ed = Editor()
    defs = ed._md_reference_defs([
        '<div>',
        '[ghost-div]: 00-vision.md',
        '</div>',
        '',
        '<pre>',
        '[ghost-pre]: 94-softwrap.md',
        '',
        '</pre>',
        '[real]: 105-setext-headings.md',
    ])
    footdefs = ed._md_footnote_defs([
        '<div>',
        '[^ghost-div]: hidden footnote',
        '</div>',
        '',
        '<pre>',
        '[^ghost-pre]: hidden footnote',
        '',
        '</pre>',
        '[^real]: visible footnote',
    ])
    assert defs == {'real': '105-setext-headings.md'}
    assert footdefs == {'real': (9, 1)}


def test_markdown_heading_scan_ignores_raw_html_blocks() -> None:
    ed = Editor()
    headings = ed._md_heading_entries([
        '<div>',
        '## Hidden heading',
        '</div>',
        '',
        '<pre>',
        'Also hidden',
        '-----------',
        '',
        '</pre>',
        '',
        '## Visible heading',
    ])
    assert headings == [(10, 2, 'Visible heading', '', 3)]


def test_helpfollow_ignores_markdown_looking_links_inside_generic_html_blocks() -> None:
    ed = Editor()
    assert ed.open_help_doc("help-browser") is True

    _set_cursor_on_substring(ed, "Ghost generic html block link")
    assert ed.exec_command_line("helpfollow") is False
    assert "no link under cursor" in (ed.messages[-1] if ed.messages else "")

    _set_cursor_on_substring(ed, "Visible link after generic raw HTML block")
    assert ed.exec_command_line("helpfollow") is True
    assert ed.cur().name.startswith("help:vision")



def test_helpfollow_generic_html_blocks_do_not_interrupt_paragraphs() -> None:
    ed = Editor()
    assert ed.open_help_doc("help-browser") is True

    _set_cursor_on_substring(ed, "Visible link after paragraph-adjacent generic tag")
    assert ed.exec_command_line("helpfollow") is True
    assert ed.cur().name.startswith("help:setext-headings")



def test_markdown_definition_parsers_and_heading_scan_ignore_generic_html_blocks() -> None:
    ed = Editor()
    defs = ed._md_reference_defs([
        '<widget-box data-kind="demo">',
        '[ghost-widget]: 00-vision.md',
        '',
        '[real]: 94-softwrap.md',
    ])
    footdefs = ed._md_footnote_defs([
        '<widget-box data-kind="demo">',
        '[^ghost-widget]: hidden footnote',
        '',
        '[^real]: visible footnote',
    ])
    headings = ed._md_heading_entries([
        '<widget-box data-kind="demo">',
        '## Hidden widget heading',
        '',
        '## Visible heading',
    ])
    assert defs == {'real': '94-softwrap.md'}
    assert footdefs == {'real': (4, 1)}
    assert headings == [(3, 2, 'Visible heading', '', 3)]



def test_md_html_block_line_flags_mark_type7_blocks_but_not_paragraph_interruptions() -> None:
    lines = [
        '<widget-box data-kind="demo">',
        '[ghost-widget](00-vision.md)',
        '</widget-box>',
        '',
        'Paragraph before generic tag',
        '<span class="inlineish-demo">',
        '[visible-after-paragraph](00-vision.md)',
        '',
        '</widget-box>',
        '[ghost-closing-only](00-vision.md)',
        '',
        'after [visible](00-vision.md)',
    ]
    assert md_html_block_line_flags(lines) == [True, True, True, False, False, False, False, False, True, True, False, False]



def test_md_html_block_line_flags_mark_type6_and_type1_blocks() -> None:
    lines = [
        '<div>',
        '[ghost-div](00-vision.md)',
        '</div>',
        '',
        '<pre>',
        '[ghost-pre](00-vision.md)',
        '',
        '</pre>',
        'after [visible](00-vision.md)',
    ]
    assert md_html_block_line_flags(lines) == [True, True, True, False, True, True, True, True, False]


def test_markdown_definition_parsers_ignore_fenced_code_blocks() -> None:
    ed = Editor()
    defs = ed._md_reference_defs([
        '```text',
        '[ghost]: 00-vision.md',
        '```',
        '[real]: 94-softwrap.md',
    ])
    footdefs = ed._md_footnote_defs([
        '```text',
        '[^ghost]: hidden footnote',
        '```',
        '[^real]: visible footnote',
    ])

    assert 'ghost' not in defs
    assert defs.get('real') == '94-softwrap.md'
    assert 'ghost' not in footdefs
    assert 'real' in footdefs


def test_md_reference_def_target_info_reports_wrapped_line_usage() -> None:
    assert md_reference_def_target_info(r'103-space\ path.md') == ('103-space path.md', 0)
    assert md_reference_def_target_info('', r'103-space\ path.md') == ('103-space path.md', 1)
    assert md_reference_def_target_info(r'104-paren\(topic\).md', '  "tiny title"') == ('104-paren(topic).md', 1)
    assert md_reference_def_target_info('', r'104-paren\(topic\).md', '  "tiny title"') == ('104-paren(topic).md', 2)


def test_md_definition_line_roles_cover_reference_wrapped_lines_and_footnotes() -> None:
    ed = Editor()
    roles = ed._md_definition_line_roles([
        '[vision]: 00-vision.md',
        '[space-path-doc-multiline]:',
        r'  103-space\ path.md',
        '[paren-topic-doc-multiline]:',
        r'  104-paren\(topic\).md',
        '  "tiny multiline title"',
        '[^help-footnote]: Tiny footnote body.',
        '[^help-footnote-more]: Tiny first line.',
        '    Tiny indented continuation line.',
        '\tSecond continuation line via tab indent.',
        'plain text',
    ])

    assert roles[0] == ('reference', 0, 9)
    assert roles[1] == ('reference', 0, 27)
    assert roles[2] == ('reference-cont', 0, 0)
    assert roles[3] == ('reference', 0, 28)
    assert roles[4] == ('reference-cont', 0, 0)
    assert roles[5] == ('reference-cont', 0, 0)
    assert roles[6] == ('footnote', 0, 18)
    assert roles[7] == ('footnote', 0, 23)
    assert roles[8] == ('footnote-cont', 0, 0)
    assert roles[9] == ('footnote-cont', 0, 0)
    assert 10 not in roles
