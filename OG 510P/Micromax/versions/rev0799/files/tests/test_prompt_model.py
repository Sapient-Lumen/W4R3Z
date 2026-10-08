from __future__ import annotations

from micromax_editor.prompt_model import (
    current_prompt_row,
    move_prompt_index,
    next_section_index,
    normalize_prompt_row,
    normalize_prompt_rows,
    prev_section_index,
    prompt_position_model,
    prompt_section_starts,
)


def _section(row: list[str]) -> str:
    return str(row[1] or 'Items')


def test_normalize_prompt_row_pads_and_stringifies() -> None:
    assert normalize_prompt_row(['name', 3]) == ['name', '3', '', '']
    assert normalize_prompt_rows([['a'], ['b', 'kind', 'menu', 'info', 'ignored']]) == [
        ['a', '', '', ''],
        ['b', 'kind', 'menu', 'info'],
    ]


def test_current_prompt_row_clamps_selection() -> None:
    rows = [['first', 'A'], ['second', 'B']]
    assert current_prompt_row(rows, -4) == ['first', 'A', '', '']
    assert current_prompt_row(rows, 9) == ['second', 'B', '', '']
    assert current_prompt_row([], 0) == []


def test_prompt_section_starts_collapses_contiguous_labels() -> None:
    rows = [
        ['a1', 'A'],
        ['a2', 'A'],
        ['b1', 'B'],
        ['b2', 'B'],
        ['a3', 'A'],
    ]
    assert prompt_section_starts(rows, _section) == [0, 2, 4]


def test_prompt_section_jumps_wrap_and_clamp() -> None:
    starts = [0, 2, 5]
    assert next_section_index(starts, 0, wrap=True) == 2
    assert next_section_index(starts, 6, wrap=True) == 0
    assert next_section_index(starts, 6, wrap=False) == 5
    assert prev_section_index(starts, 4, wrap=True) == 2
    assert prev_section_index(starts, 2, wrap=True) == 0
    assert prev_section_index(starts, 0, wrap=True) == 5
    assert prev_section_index(starts, 0, wrap=False) == 0


def test_move_prompt_index_wraps_or_clamps() -> None:
    assert move_prompt_index(0, 3, -1, wrap=True) == 2
    assert move_prompt_index(2, 3, 1, wrap=True) == 0
    assert move_prompt_index(0, 3, -1, wrap=False) == 0
    assert move_prompt_index(2, 3, 1, wrap=False) == 2


def test_prompt_position_model_counts_position_inside_section() -> None:
    rows = [
        ['a1', 'A'],
        ['a2', 'A'],
        ['b1', 'B'],
        ['a3', 'A'],
    ]
    model = prompt_position_model(rows, 3, kind='demo', labeler=_section)
    assert model == {
        'index': 4,
        'count': 4,
        'section': 'A',
        'section_index': 3,
        'section_count': 3,
        'summary': '4/4 • A 3/3',
    }
