from __future__ import annotations

from micromax_editor.tui import (
    md_table_cell_entries,
    md_table_delimiter_entries,
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



def test_md_table_cell_entries_trim_outer_padding_and_track_columns() -> None:
    entries = md_table_cell_entries('| Key | Value with spaces | Tail |')
    assert [(entry['column'], entry['text']) for entry in entries] == [
        (0, 'Key'),
        (1, 'Value with spaces'),
        (2, 'Tail'),
    ]
    assert entries[0]['start'] == 2
    assert entries[0]['end'] == 5
    assert entries[1]['start'] < entries[1]['end']


def test_md_table_delimiter_entries_capture_alignment_and_marker_counts() -> None:
    entries = md_table_delimiter_entries('| :--- | :---: | ---: | --- |')
    assert [(entry['column'], entry['align'], entry['marker_count']) for entry in entries] == [
        (0, 'left', 3),
        (1, 'center', 3),
        (2, 'right', 3),
        (3, 'default', 3),
    ]
    assert [entry['kind'] for entry in entries] == ['delimiter-cell'] * 4
