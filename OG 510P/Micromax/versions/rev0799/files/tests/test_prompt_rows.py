from __future__ import annotations

from micromax_editor.prompt_rank import (
    completion_fuzzy_positions,
    completion_fuzzy_sort_key,
    multi_term_field_key,
)
from micromax_editor.prompt_rows import (
    filter_section_summary_rows,
    flatten_grouped_prompt_sections,
    group_prompt_rows_by_section,
    limit_grouped_prompt_sections,
    normalize_prompt_row,
    section_summary_prompt_row_detail,
    section_summary_rows,
)


def test_completion_fuzzy_key_prefers_boundary_when_span_ties() -> None:
    candidates = ["helpavim", "help-vim", "showhelpvim"]

    ranked = sorted(candidates, key=lambda name: completion_fuzzy_sort_key(name, "hv") or ())

    assert completion_fuzzy_positions("help-vim", "hv") == [0, 5]
    assert ranked[0] == "help-vim"
    assert completion_fuzzy_sort_key("plain", "zz") is None


def test_multi_term_field_key_requires_every_term_and_prefers_primary_fields() -> None:
    key_primary = multi_term_field_key(
        [(0, "recent root"), (1, "secondary metadata")],
        "recent root",
        fallback_rank=5,
        tie_name="a",
    )
    key_secondary = multi_term_field_key(
        [(0, "recent"), (1, "root metadata")],
        "recent root",
        fallback_rank=5,
        tie_name="b",
    )

    assert key_primary is not None
    assert key_secondary is not None
    assert key_primary < key_secondary
    assert multi_term_field_key(
        [(0, "recent only")],
        "recent missing",
        fallback_rank=5,
        tie_name="c",
    ) is None


def test_group_prompt_rows_normalizes_preserves_and_sorts_sections() -> None:
    rows = [
        ["beta", "item", "B"],
        ["alpha", "item", "A", "info", "extra"],
        ["gamma", "item", "G"],
    ]

    grouped = group_prompt_rows_by_section(
        rows,
        label_fn=lambda row: "late" if row[0] == "gamma" else "early",
        label_sort_key=lambda label: {"early": 0, "late": 1}[label],
    )

    assert grouped == [
        ["early", [["beta", "item", "B", ""], ["alpha", "item", "A", "info"]]],
        ["late", [["gamma", "item", "G", ""]]],
    ]
    assert normalize_prompt_row(["x", 1]) == ["x", "1", "", ""]


def test_limit_grouped_prompt_sections_browse_budget_is_round_robin() -> None:
    sections = [
        ["A", [["a1"], ["a2"], ["a3"]]],
        ["B", [["b1"]]],
        ["C", [["c1"], ["c2"]]],
    ]

    limited = limit_grouped_prompt_sections(sections, limit=4, browse_budget=True)
    flat = flatten_grouped_prompt_sections(sections, limit=4, browse_budget=True)

    assert limited == [
        ["A", [["a1", "", "", ""], ["a2", "", "", ""]]],
        ["B", [["b1", "", "", ""]]],
        ["C", [["c1", "", "", ""]]],
    ]
    assert [row[0] for row in flat] == ["a1", "a2", "b1", "c1"]


def test_section_summary_rows_and_filter_use_prompt_detail_policy() -> None:
    sections = [
        ["Docs", [["topic", "doc", "Title", "Summary"]]],
        ["Empty", []],
        ["Buffers", [["main", "buffer", "main.py", "main.py · modified"]]],
    ]

    rows = section_summary_rows(
        sections,
        sample_detail_fn=section_summary_prompt_row_detail,
    )

    assert rows == [
        ["Docs", 1, "topic", "Title · Summary"],
        ["Buffers", 1, "main", "main.py · modified"],
    ]
    assert filter_section_summary_rows(rows, "modified") == [["Buffers", 1, "main", "main.py · modified"]]
    assert filter_section_summary_rows(rows, "", limit=1) == [["Docs", 1, "topic", "Title · Summary"]]
