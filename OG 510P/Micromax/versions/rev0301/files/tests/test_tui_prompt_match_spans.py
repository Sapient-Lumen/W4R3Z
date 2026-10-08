from __future__ import annotations


from micromax_editor.tui import prompt_match_spans


def test_prompt_match_spans_highlights_query_tokens_case_insensitive() -> None:
    assert prompt_match_spans("hello world", "wo") == [(6, 8)]
    assert prompt_match_spans("Hello World", "wo") == [(6, 8)]


def test_prompt_match_spans_highlights_multiple_tokens_and_occurrences() -> None:
    spans = prompt_match_spans("foo bar baz", "ba")
    assert spans == [(4, 6), (8, 10)]


def test_prompt_match_spans_merges_overlapping_spans() -> None:
    # "fo" and "foo" overlap; merged span should cover the larger match.
    assert prompt_match_spans("foobar", "fo foo") == [(0, 3)]


def test_prompt_match_spans_falls_back_to_subsequence_when_no_substring_hit() -> None:
    # "fr" isn't a substring of "foobar", but it is a subsequence (f...r).
    assert prompt_match_spans("foobar", "fr") == [(0, 1), (5, 6)]


def test_prompt_match_spans_prefers_substring_over_subsequence() -> None:
    # "foo" is a substring, so we highlight the whole token, not f..o..o.
    assert prompt_match_spans("foobar", "foo") == [(0, 3)]
