from __future__ import annotations

from micromax_editor.tui import md_inline_code_spans


def test_md_inline_code_spans_basic_multiple() -> None:
    s = "alpha `code` beta `more`"
    spans = md_inline_code_spans(s)
    # inside spans (excluding backticks)
    assert spans == [(7, 11), (19, 23)]


def test_md_inline_code_spans_ignores_fences_and_escapes() -> None:
    assert md_inline_code_spans("```python") == []
    assert md_inline_code_spans("\\`notcode`") == []
