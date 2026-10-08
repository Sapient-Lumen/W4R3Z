from __future__ import annotations

from micromax_editor.editor import Editor
from micromax_editor.tui import md_link_label_spans


def _defs_from_lines(lines: list[str]) -> dict[str, str]:
    ed = Editor()
    # Use the editor's own small reference-def parser.
    return ed._md_reference_defs(list(lines))


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
    defs = _defs_from_lines(lines)

    s1 = lines[0]
    spans1 = md_link_label_spans(s1, defs)
    assert any(s1[a:b] == 'Vision' for a, b in spans1)

    s2 = lines[1]
    spans2 = md_link_label_spans(s2, defs)
    assert any(s2[a:b] == 'Vision ref' for a, b in spans2)

    s3 = lines[2]
    spans3 = md_link_label_spans(s3, defs)
    assert any(s3[a:b] == 'Vision shortcut' for a, b in spans3)

    s4 = lines[3]
    spans4 = md_link_label_spans(s4, defs)
    assert any(s4[a:b].startswith('https://') for a, b in spans4)


def test_md_link_label_spans_do_not_underline_reference_definitions() -> None:
    lines = [
        '[foo]: https://example.com',
        'text [foo] more',
    ]
    defs = _defs_from_lines(lines)

    s_def = lines[0]
    spans_def = md_link_label_spans(s_def, defs)
    # definition line should not be underlined
    assert spans_def == []

    s_use = lines[1]
    spans_use = md_link_label_spans(s_use, defs)
    assert any(s_use[a:b] == 'foo' for a, b in spans_use)
