from __future__ import annotations

from micromax_editor.editor import Editor, md_fenced_code_line_flags, md_html_block_line_flags, md_html_comment_line_spans
from micromax_editor.tui import md_autolink_token_spans, md_footnote_ref_token_spans, md_image_token_spans, md_link_label_spans, md_link_source_token_spans, md_raw_html_tag_token_spans


def _defs_from_lines(lines: list[str]) -> tuple[dict[str, str], dict[str, tuple[int, int]]]:
    ed = Editor()
    # Use the editor's own small markdown parsers.
    return (ed._md_reference_defs(list(lines)), ed._md_footnote_defs(list(lines)))


def test_md_link_label_spans_cover_inline_reference_shortcut_and_autolink() -> None:
    lines = [
        '- [Vision](00-vision.md)',
        '- [Vision ref][visionref]',
        '- [Vision shortcut]',
        '- <https://micro-editor.github.io/>',
        '',
        '[visionref]: 00-vision.md',
        '[Vision shortcut]: 00-vision.md',
    ]
    defs, footdefs = _defs_from_lines(lines)

    s1 = lines[0]
    spans1 = md_link_label_spans(s1, defs, footdefs)
    assert any(s1[a:b] == 'Vision' for a, b in spans1)

    s2 = lines[1]
    spans2 = md_link_label_spans(s2, defs, footdefs)
    assert any(s2[a:b] == 'Vision ref' for a, b in spans2)

    s3 = lines[2]
    spans3 = md_link_label_spans(s3, defs, footdefs)
    assert any(s3[a:b] == 'Vision shortcut' for a, b in spans3)

    s4 = lines[3]
    spans4 = md_link_label_spans(s4, defs, footdefs)
    assert any(s4[a:b].startswith('https://') for a, b in spans4)


def test_md_link_label_spans_do_not_underline_reference_definitions() -> None:
    lines = [
        '[foo]: https://example.com',
        'text [foo] more',
    ]
    defs, footdefs = _defs_from_lines(lines)

    s_def = lines[0]
    spans_def = md_link_label_spans(s_def, defs, footdefs)
    # definition line should not be underlined
    assert spans_def == []

    s_use = lines[1]
    spans_use = md_link_label_spans(s_use, defs, footdefs)
    assert any(s_use[a:b] == 'foo' for a, b in spans_use)


def test_md_link_label_spans_cover_footnote_refs_but_not_definitions() -> None:
    lines = [
        'Micromax also recognizes footnotes[^browser-fn].',
        '',
        '[^browser-fn]: Tiny, best-effort docs-browser footnote support.',
    ]
    defs, footdefs = _defs_from_lines(lines)

    s_ref = lines[0]
    spans_ref = md_link_label_spans(s_ref, defs, footdefs)
    assert any(s_ref[a:b] == '^browser-fn' for a, b in spans_ref)

    s_def = lines[2]
    spans_def = md_link_label_spans(s_def, defs, footdefs)
    assert spans_def == []


def test_md_footnote_ref_token_spans_cover_whole_visible_token() -> None:
    lines = [
        'Micromax also recognizes footnotes[^browser-fn].',
        r'Escaped \[^ghost] and code `[^ghost-code]` stay prose.',
        '',
        '[^browser-fn]: Tiny, best-effort docs-browser footnote support.',
        '[^ghost]: Hidden because the use-site is escaped.',
        '[^ghost-code]: Hidden because the use-site is inline code.',
    ]
    _defs, footdefs = _defs_from_lines(lines)

    s_ref = lines[0]
    spans_ref = md_footnote_ref_token_spans(s_ref, footdefs)
    assert any(s_ref[a:b] == '[^browser-fn]' for a, b in spans_ref)

    s_ignored = lines[1]
    spans_ignored = [s_ignored[a:b] for a, b in md_footnote_ref_token_spans(s_ignored, footdefs)]
    assert '[^ghost]' not in spans_ignored
    assert '[^ghost-code]' not in spans_ignored


def test_md_autolink_token_spans_cover_whole_visible_token() -> None:
    lines = [
        'Visit <https://micro-editor.github.io/> for details.',
        r'Escaped \<https://example.invalid/ghost> and code `<https://example.invalid/code>` stay prose.',
    ]

    s_ref = lines[0]
    spans_ref = md_autolink_token_spans(s_ref)
    assert any(s_ref[a:b] == '<https://micro-editor.github.io/>' for a, b in spans_ref)

    s_ignored = lines[1]
    spans_ignored = [s_ignored[a:b] for a, b in md_autolink_token_spans(s_ignored)]
    assert '<https://example.invalid/ghost>' not in spans_ignored
    assert '<https://example.invalid/code>' not in spans_ignored



def test_md_raw_html_tag_token_spans_cover_inline_tags_but_not_autolinks_or_code() -> None:
    s = 'Press <kbd>Ctrl-b</kbd> or <a name="anchor"></a> before <https://example.invalid/> and `<ins>code</ins>`.'
    spans = md_raw_html_tag_token_spans(s)
    parts = [s[a:b] for a, b in spans]

    assert '<kbd>' in parts
    assert '</kbd>' in parts
    assert '<a name="anchor">' in parts
    assert '</a>' in parts
    assert '<https://example.invalid/>' not in parts
    assert '<ins>' not in parts
    assert '</ins>' not in parts


def test_md_image_token_spans_cover_inline_reference_and_shortcut_tokens() -> None:
    lines = [
        'inline ![Vision image](00-vision.md)',
        'ref ![Vision ref image][visionimg]',
        'shortcut ![Vision shortcut image]',
        r'Escaped \![Ghost image](00-vision.md) and code `![Ghost code](00-vision.md)` stay prose.',
        '',
        '[visionimg]: 00-vision.md',
        '[Vision shortcut image]: 00-vision.md',
    ]
    defs, _footdefs = _defs_from_lines(lines)

    s_inline = lines[0]
    spans_inline = md_image_token_spans(s_inline, defs)
    assert any(s_inline[a:b] == '![Vision image](00-vision.md)' for a, b in spans_inline)

    s_ref = lines[1]
    spans_ref = md_image_token_spans(s_ref, defs)
    assert any(s_ref[a:b] == '![Vision ref image][visionimg]' for a, b in spans_ref)

    s_short = lines[2]
    spans_short = md_image_token_spans(s_short, defs)
    assert any(s_short[a:b] == '![Vision shortcut image]' for a, b in spans_short)

    s_ignored = lines[3]
    spans_ignored = [s_ignored[a:b] for a, b in md_image_token_spans(s_ignored, defs)]
    assert '![Ghost image](00-vision.md)' not in spans_ignored
    assert '![Ghost code](00-vision.md)' not in spans_ignored


def test_md_link_source_token_spans_cover_inline_reference_and_shortcut_links() -> None:
    lines = [
        'inline [Vision](00-vision.md)',
        'ref [Vision ref][visionref]',
        'shortcut [Vision shortcut]',
        'footnote [^browser-fn]',
        'auto <https://example.invalid/>',
        r'Escaped \[Ghost](00-vision.md), code `[Ghost code](00-vision.md)`, and image ![Ghost image](00-vision.md) stay prose.',
        '',
        '[visionref]: 00-vision.md',
        '[Vision shortcut]: 00-vision.md',
        '[^browser-fn]: Tiny, best-effort docs-browser footnote support.',
    ]
    defs, footdefs = _defs_from_lines(lines)

    s_inline = lines[0]
    parts_inline = [s_inline[a:b] for a, b in md_link_source_token_spans(s_inline, defs, footdefs)]
    assert '[' in parts_inline
    assert '](00-vision.md)' in parts_inline

    s_ref = lines[1]
    parts_ref = [s_ref[a:b] for a, b in md_link_source_token_spans(s_ref, defs, footdefs)]
    assert '[' in parts_ref
    assert '][visionref]' in parts_ref

    s_short = lines[2]
    parts_short = [s_short[a:b] for a, b in md_link_source_token_spans(s_short, defs, footdefs)]
    assert parts_short == ['[', ']']

    s_ignored = lines[5]
    parts_ignored = [s_ignored[a:b] for a, b in md_link_source_token_spans(s_ignored, defs, footdefs)]
    assert '[' not in parts_ignored
    assert '](00-vision.md)' not in parts_ignored

    assert md_link_source_token_spans(lines[3], defs, footdefs) == []
    assert md_link_source_token_spans(lines[4], defs, footdefs) == []

def test_md_link_label_spans_ignore_links_inside_inline_code() -> None:
    lines = [
        'real [Vision](00-vision.md) and ``[Nope](99-missing.md)`` and `https://example.com`',
    ]
    defs, footdefs = _defs_from_lines(lines)
    spans = md_link_label_spans(lines[0], defs, footdefs)
    labels = [lines[0][a:b] for a, b in spans]
    assert 'Vision' in labels
    assert 'Nope' not in labels
    assert not any(lbl.startswith('https://example.com') for lbl in labels)


def test_md_link_label_spans_ignore_images_inline_and_reference() -> None:
    lines = [
        'inline ![Vision image](00-vision.md) and real [Vision](00-vision.md)',
        'ref ![Vision ref image][visionimg] and real [Vision ref][visionref]',
        '',
        '[visionimg]: 00-vision.md',
        '[visionref]: 00-vision.md',
    ]
    defs, footdefs = _defs_from_lines(lines)

    s1 = lines[0]
    spans1 = [s1[a:b] for a, b in md_link_label_spans(s1, defs, footdefs)]
    assert 'Vision' in spans1
    assert 'Vision image' not in spans1

    s2 = lines[1]
    spans2 = [s2[a:b] for a, b in md_link_label_spans(s2, defs, footdefs)]
    assert 'Vision ref' in spans2
    assert 'Vision ref image' not in spans2



def test_md_link_label_spans_cover_destination_escape_examples() -> None:
    lines = [
        r'inline [Space path doc](103-space\ path.md)',
        r'inline [Paren topic doc](104-paren\(topic\).md)',
        'inline [Space path doc percent](103-space%20path.md)',
        'ref [Space path doc ref][space-path-doc]',
        'ref [Paren topic doc ref][paren-topic-doc]',
        '',
        r'[space-path-doc]: 103-space\ path.md',
        r'[paren-topic-doc]: 104-paren\(topic\).md',
    ]
    defs, footdefs = _defs_from_lines(lines)

    got = []
    for line in lines[:5]:
        got.extend(line[a:b] for a, b in md_link_label_spans(line, defs, footdefs))

    assert 'Space path doc' in got
    assert 'Paren topic doc' in got
    assert 'Space path doc percent' in got
    assert 'Space path doc ref' in got
    assert 'Paren topic doc ref' in got

def test_md_link_label_spans_cover_tiny_multiline_reference_definitions() -> None:
    lines = [
        'ref [Space path doc ref (dest next line)][space-path-doc-multiline]',
        'ref [Paren topic doc ref (dest + title next line)][paren-topic-doc-multiline]',
        'ref [Space path doc ref (title next line)][space-path-doc-title-next-line]',
        '',
        '[space-path-doc-multiline]:',
        r'  103-space\ path.md',
        '[paren-topic-doc-multiline]:',
        r'  104-paren\(topic\).md',
        '  "tiny title"',
        r'[space-path-doc-title-next-line]: 103-space\ path.md',
        '  "other title"',
    ]
    defs, footdefs = _defs_from_lines(lines)

    got = []
    for line in lines[:3]:
        got.extend(line[a:b] for a, b in md_link_label_spans(line, defs, footdefs))

    assert 'Space path doc ref (dest next line)' in got
    assert 'Paren topic doc ref (dest + title next line)' in got
    assert 'Space path doc ref (title next line)' in got


def test_md_link_label_spans_cover_tiny_wrapped_inline_links() -> None:
    lines = [
        'inline [Space path doc (inline dest next line)](',
        r'  103-space\ path.md)',
        r'inline [Paren topic doc (inline title next line)](104-paren\(topic\).md',
        '  "tiny title")',
        'inline [Angle space path doc (inline dest next line)](',
        '  <103-space path.md>)',
    ]
    defs, footdefs = _defs_from_lines(lines)

    spans0 = [lines[0][a:b] for a, b in md_link_label_spans(lines[0], defs, footdefs, next_line=lines[1])]
    spans2 = [lines[2][a:b] for a, b in md_link_label_spans(lines[2], defs, footdefs, next_line=lines[3])]
    spans4 = [lines[4][a:b] for a, b in md_link_label_spans(lines[4], defs, footdefs, next_line=lines[5])]

    assert 'Space path doc (inline dest next line)' in spans0
    assert 'Paren topic doc (inline title next line)' in spans2
    assert 'Angle space path doc (inline dest next line)' in spans4


def test_md_link_label_spans_ignore_code_indented_reference_and_footnote_defs() -> None:
    lines = [
        'ref [Visible ref][ok-ref] and [Ghost four-space ref][ghost-four-space-ref] and [Ghost tab ref][ghost-tab-ref]',
        'note [^ok-footnote] [^ghost-four-space-footnote] [^ghost-tab-footnote]',
        '',
        '   [ok-ref]: 00-vision.md',
        '   [^ok-footnote]: yes',
        '    [ghost-four-space-ref]: 94-softwrap.md',
        '    [^ghost-four-space-footnote]: no',
        '\t[ghost-tab-ref]: 94-softwrap.md',
        '\t[^ghost-tab-footnote]: no',
    ]
    defs, footdefs = _defs_from_lines(lines)

    spans0 = [lines[0][a:b] for a, b in md_link_label_spans(lines[0], defs, footdefs)]
    spans1 = [lines[1][a:b] for a, b in md_link_label_spans(lines[1], defs, footdefs)]

    assert 'Visible ref' in spans0
    assert 'Ghost four-space ref' not in spans0
    assert 'Ghost tab ref' not in spans0
    assert '^ok-footnote' in spans1
    assert '^ghost-four-space-footnote' not in spans1
    assert '^ghost-tab-footnote' not in spans1


def test_md_link_label_spans_ignore_escaped_markdown_forms() -> None:
    lines = [
        r'literal \[Vision](00-vision.md) and \[Vision ref][visionref] and \[Vision shortcut] and \[^browser-fn] and \<https://example.invalid/escaped>',
        '',
        '[visionref]: 00-vision.md',
        '[Vision shortcut]: 00-vision.md',
        '[^browser-fn]: Tiny, best-effort docs-browser footnote support.',
    ]
    defs, footdefs = _defs_from_lines(lines)

    spans = [lines[0][a:b] for a, b in md_link_label_spans(lines[0], defs, footdefs)]
    assert spans == []


def test_md_link_label_spans_cover_nested_bracket_labels() -> None:
    lines = [
        'inline [Vision [nested inline]](00-vision.md)',
        'ref [Vision [nested ref]][nested-vision-ref]',
        'shortcut [Vision [nested shortcut]]',
        '',
        '[nested-vision-ref]: 00-vision.md',
        '[Vision [nested shortcut]]: 00-vision.md',
    ]
    defs, footdefs = _defs_from_lines(lines)

    got = []
    for line in lines[:3]:
        got.extend(line[a:b] for a, b in md_link_label_spans(line, defs, footdefs))

    assert 'Vision [nested inline]' in got
    assert 'Vision [nested ref]' in got
    assert 'Vision [nested shortcut]' in got


def test_md_link_label_spans_prefer_valid_inner_links_over_outer_nested_links() -> None:
    lines = [
        'inline [Outer prose [Nested inner inline](94-softwrap.md)](00-vision.md)',
        'ref [Outer prose [Nested inner ref][visionref]](00-vision.md)',
        '',
        '[visionref]: 00-vision.md',
    ]
    defs, footdefs = _defs_from_lines(lines)

    spans0 = [lines[0][a:b] for a, b in md_link_label_spans(lines[0], defs, footdefs)]
    spans1 = [lines[1][a:b] for a, b in md_link_label_spans(lines[1], defs, footdefs)]

    assert spans0 == ['Nested inner inline']
    assert spans1 == ['Nested inner ref']


def test_md_link_label_spans_ignore_empty_and_whitespace_only_labels() -> None:
    lines = [
        'empty [](99-empty-inline-should-stay-prose.md)',
        'space [ ](99-space-inline-should-stay-prose.md)',
        'ref [  ][space-only-ref]',
        'shortcut []',
        '[space-only-ref]: 99-space-ref-should-stay-prose.md',
    ]
    defs, footdefs = _defs_from_lines(lines)

    assert md_link_label_spans(lines[0], defs, footdefs) == []
    assert md_link_label_spans(lines[1], defs, footdefs) == []
    assert md_link_label_spans(lines[2], defs, footdefs) == []
    assert md_link_label_spans(lines[3], defs, footdefs) == []


def test_md_link_label_spans_ignore_html_comments_but_keep_visible_links() -> None:
    lines = [
        'visible [Vision](00-vision.md) <!-- [Ghost inline](94-softwrap.md) -->',
        '<!--',
        '[ghost-comment-ref]: 94-softwrap.md',
        '[^ghost-comment-footnote]: hidden footnote',
        '- [Ghost block](94-softwrap.md)',
        '-->',
        'after [Visible softwrap](94-softwrap.md)',
        'after [Ghost commented ref][ghost-comment-ref]',
        'after [^ghost-comment-footnote]',
    ]
    defs, footdefs = _defs_from_lines(lines)
    comment_spans = md_html_comment_line_spans(lines)

    spans0 = [lines[0][a:b] for a, b in md_link_label_spans(lines[0], defs, footdefs, masked_spans=comment_spans[0])]
    assert 'Vision' in spans0
    assert 'Ghost inline' not in spans0

    spans6 = [lines[6][a:b] for a, b in md_link_label_spans(lines[6], defs, footdefs, masked_spans=comment_spans[6])]
    spans7 = [lines[7][a:b] for a, b in md_link_label_spans(lines[7], defs, footdefs, masked_spans=comment_spans[7])]
    spans8 = [lines[8][a:b] for a, b in md_link_label_spans(lines[8], defs, footdefs, masked_spans=comment_spans[8])]
    assert 'Visible softwrap' in spans6
    assert spans7 == []
    assert spans8 == []
    assert defs == {}
    assert footdefs == {}


def test_md_fenced_code_line_flags_mark_fenced_blocks() -> None:
    lines = [
        'before',
        '```text',
        '[ghost](00-vision.md)',
        '[ghost]: 94-softwrap.md',
        '```',
        'after',
        '~~~md',
        '[ghost2](00-vision.md)',
        '~~~',
    ]
    flags = md_fenced_code_line_flags(lines)
    assert flags == [False, True, True, True, True, False, True, True, True]


def test_md_link_label_spans_do_not_resolve_reference_defs_inside_fenced_blocks() -> None:
    lines = [
        '```text',
        '[ghost]: 00-vision.md',
        '```',
        'outside [ghost]',
    ]
    defs, footdefs = _defs_from_lines(lines)
    assert defs == {}
    assert md_link_label_spans(lines[3], defs, footdefs) == []


def test_md_link_label_spans_ignore_raw_html_tag_and_autolink_precedence_inside_labels() -> None:
    lines = [
        '[fake raw html <span title="](00-vision.md)">',
        '[fake raw html ref <span title="][visionref]">',
        '[fake raw html autolink <https://example.invalid/raw?x=](00-vision.md)>',
        '',
        '[visionref]: 00-vision.md',
    ]
    defs, footdefs = _defs_from_lines(lines)

    assert md_link_label_spans(lines[0], defs, footdefs) == []
    assert md_link_label_spans(lines[2], defs, footdefs) == []


def test_md_link_label_spans_ignore_raw_html_blocks_and_hidden_defs() -> None:
    lines = [
        '<div>',
        '[ghost-div](00-vision.md)',
        '[ghost-div-ref]: 00-vision.md',
        '</div>',
        '',
        '<pre>',
        '[ghost-pre](00-vision.md)',
        '',
        '</pre>',
        'after [visible](00-vision.md)',
        'after [ghost-div-ref]',
    ]
    defs, footdefs = _defs_from_lines(lines)
    flags = md_html_block_line_flags(lines)

    assert defs == {}
    assert flags == [True, True, True, True, False, True, True, True, True, False, False]
    assert md_link_label_spans(lines[9], defs, footdefs) == [(7, 14)]
    assert md_link_label_spans(lines[10], defs, footdefs) == []



def test_md_link_label_spans_ignore_generic_html_blocks_but_not_paragraph_adjacent_tags() -> None:
    lines = [
        '<widget-box data-kind="demo">',
        '[ghost-widget](00-vision.md)',
        '[ghost-widget-ref]: 00-vision.md',
        '',
        'Paragraph before generic tag',
        '<span class="inlineish-demo">',
        '[visible-after-paragraph](00-vision.md)',
        '',
        '[visible-ref]: 00-vision.md',
        'after [visible-ref]',
    ]
    defs, footdefs = _defs_from_lines(lines)
    flags = md_html_block_line_flags(lines)

    assert defs == {'visible-ref': '00-vision.md'}
    assert flags == [True, True, True, False, False, False, False, False, False, False]
    assert md_link_label_spans(lines[6], defs, footdefs) == [(1, 24)]
    assert md_link_label_spans(lines[9], defs, footdefs) == [(7, 18)]
