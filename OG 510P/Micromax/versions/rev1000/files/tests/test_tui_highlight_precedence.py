from __future__ import annotations

import curses

from micromax_editor.tui import (
    HIGHLIGHT_PRECEDENCE,
    highlight_segment_points,
    replace_curses_color,
    syntax_highlight_attr,
    viewport_highlight_attr,
    viewport_highlight_work_needed,
)


def test_reference_highlight_precedence_is_small_and_explicit() -> None:
    assert HIGHLIGHT_PRECEDENCE == (
        "syntax",
        "docs-inline",
        "showchar",
        "color-column",
        "whitespace-diagnostic",
        "brace-match",
        "search",
        "selection-secondary",
        "selection-primary",
        "search-current",
    )
    assert highlight_segment_points(
        2,
        9,
        [(0, 4), (7, 12)],
        [(5, 6)],
    ) == [2, 4, 5, 6, 7, 9]


def test_search_overrides_dim_but_preserves_noncompeting_emphasis() -> None:
    base = int(curses.A_DIM | curses.A_UNDERLINE)
    attr = viewport_highlight_attr(
        base,
        2,
        3,
        colorcolumn=[(2, 3)],
        braces=[(2, 3)],
        search=[(2, 3)],
        brace_attr=int(curses.A_BOLD | curses.A_UNDERLINE),
    )

    assert attr & curses.A_REVERSE
    assert attr & curses.A_BOLD
    assert attr & curses.A_UNDERLINE
    assert not (attr & curses.A_DIM)


def test_current_search_is_independently_reverse_bold_and_not_dim() -> None:
    attr = viewport_highlight_attr(
        int(curses.A_DIM),
        0,
        1,
        current_search=[(0, 1)],
    )

    assert attr & curses.A_REVERSE
    assert attr & curses.A_BOLD
    assert attr & curses.A_UNDERLINE
    assert not (attr & curses.A_DIM)


def test_selection_is_visible_over_syntax_and_search() -> None:
    syntax_attr = syntax_highlight_attr(int(curses.A_DIM), "comment", colors=False)
    secondary = viewport_highlight_attr(
        syntax_attr,
        1,
        2,
        search=[(1, 2)],
        secondary_selection=[(1, 2)],
    )
    primary = viewport_highlight_attr(
        syntax_attr,
        1,
        2,
        search=[(1, 2)],
        primary_selection=[(1, 2)],
    )

    assert secondary & curses.A_REVERSE
    assert secondary & curses.A_UNDERLINE
    assert not (secondary & curses.A_DIM)
    assert primary & curses.A_REVERSE
    assert primary & curses.A_BOLD
    assert not (primary & curses.A_DIM)


def test_selection_layers_replace_lower_emphasis_and_keep_current_search_distinct() -> None:
    definition = syntax_highlight_attr(0, "def", colors=False)
    assert definition & curses.A_BOLD
    assert definition & curses.A_UNDERLINE

    secondary = viewport_highlight_attr(
        definition,
        0,
        1,
        secondary_selection=[(0, 1)],
    )
    assert secondary & curses.A_REVERSE
    assert secondary & curses.A_UNDERLINE
    assert not (secondary & curses.A_BOLD)

    primary = viewport_highlight_attr(
        definition,
        0,
        1,
        secondary_selection=[(0, 1)],
        primary_selection=[(0, 1)],
    )
    assert primary & curses.A_REVERSE
    assert primary & curses.A_BOLD
    assert not (primary & curses.A_UNDERLINE)

    current = viewport_highlight_attr(
        definition,
        0,
        1,
        primary_selection=[(0, 1)],
        current_search=[(0, 1)],
    )
    assert current & curses.A_REVERSE
    assert current & curses.A_BOLD
    assert current & curses.A_UNDERLINE


def test_syntax_attributes_are_restrained_without_color_support() -> None:
    assert syntax_highlight_attr(0, "comment", colors=False) & curses.A_DIM
    assert syntax_highlight_attr(0, "kw", colors=False) & curses.A_BOLD
    definition = syntax_highlight_attr(0, "def", colors=False)
    assert definition & curses.A_BOLD
    assert definition & curses.A_UNDERLINE
    assert syntax_highlight_attr(0, "str", colors=False) == 0


def test_color_pair_precedence_replaces_old_color_bits() -> None:
    mask = 0b11110000
    base = 0b00100001
    replacement = 0b10000000

    assert replace_curses_color(base, replacement, color_mask=mask) == 0b10000001


def test_current_search_alone_cannot_take_the_plain_fast_path() -> None:
    assert viewport_highlight_work_needed() is False
    assert viewport_highlight_work_needed([(3, 5)]) is True
    assert viewport_highlight_work_needed(colorcolumn_x=7) is True
