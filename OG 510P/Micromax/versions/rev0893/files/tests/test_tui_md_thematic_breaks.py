from __future__ import annotations

from micromax_editor.tui import md_thematic_break_char_spans, md_thematic_break_span


def test_md_thematic_break_span_accepts_common_forms() -> None:
    assert md_thematic_break_span('---') == (0, 3)
    assert md_thematic_break_span('***   ') == (0, 3)
    assert md_thematic_break_span('___') == (0, 3)
    assert md_thematic_break_span('  - - -') == (2, 7)
    assert md_thematic_break_span(' * * * ') == (1, 6)


def test_md_thematic_break_span_rejects_non_break_lines() -> None:
    assert md_thematic_break_span('--') is None
    assert md_thematic_break_span('+++') is None
    assert md_thematic_break_span('- - _') is None
    assert md_thematic_break_span('    ---') is None
    assert md_thematic_break_span('text ---') is None


def test_md_thematic_break_char_spans_return_visible_marker_positions() -> None:
    assert md_thematic_break_char_spans('  - - -  ') == [(2, 3), (4, 5), (6, 7)]
    assert md_thematic_break_char_spans('plain text') == []
