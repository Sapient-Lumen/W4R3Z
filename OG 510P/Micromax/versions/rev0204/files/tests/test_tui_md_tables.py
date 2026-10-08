from __future__ import annotations

from micromax_editor.tui import (
    md_table_delimiter_row,
    md_table_pipe_spans,
    md_table_row_kinds,
)


def test_md_table_delimiter_row_accepts_common_gfm_forms() -> None:
    assert md_table_delimiter_row('| --- | --- |') is True
    assert md_table_delimiter_row('| :--- | ---: |') is True
    assert md_table_delimiter_row('--- | ---') is True



def test_md_table_delimiter_row_rejects_non_delimiters() -> None:
    assert md_table_delimiter_row('| Key | Meaning |') is False
    assert md_table_delimiter_row('| -- | --- |') is False
    assert md_table_delimiter_row('no pipes here') is False



def test_md_table_row_kinds_mark_header_delimiter_and_body_rows() -> None:
    lines = [
        'before',
        '| Key | Meaning |',
        '| --- | --- |',
        '| `y` / `Enter` | replace this match |',
        '| `n` | skip this match |',
        '',
        '| not | a table without delimiter following |',
    ]
    kinds = md_table_row_kinds(lines)
    assert kinds == {1: 'header', 2: 'delimiter', 3: 'body', 4: 'body'}



def test_md_table_pipe_spans_return_literal_separator_positions() -> None:
    s = '| Key | Meaning |'
    spans = md_table_pipe_spans(s)
    assert [s[a:b] for a, b in spans] == ['|', '|', '|']
    assert spans == [(0, 1), (6, 7), (16, 17)]
