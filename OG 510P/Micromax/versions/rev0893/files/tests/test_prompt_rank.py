from __future__ import annotations

from micromax_editor.prompt_rank import (
    completion_fuzzy_positions,
    completion_fuzzy_sort_key,
    multi_term_field_key,
    picker_row_sort_key,
)


def test_completion_fuzzy_positions_are_casefolded_subsequence_offsets() -> None:
    assert completion_fuzzy_positions("showBindings", "sB") == [0, 4]
    assert completion_fuzzy_positions("showBindings", "zz") is None


def test_completion_fuzzy_sort_prefers_camel_boundary_over_loose_subsequence() -> None:
    boundary = completion_fuzzy_sort_key("showBindings", "sB")
    loose = completion_fuzzy_sort_key("saxophonebongo", "sB")
    assert boundary is not None
    assert loose is not None
    assert boundary < loose


def test_picker_row_sort_key_preserves_common_key_info_menu_multi_term_policy() -> None:
    key_row = ["alpha", "kind", "menu text", "info text"]
    info_row = ["beta", "kind", "menu text", "alpha appears in info"]
    menu_row = ["gamma", "kind", "alpha appears in menu", "info text"]
    multi_row = ["delta", "kind", "project menu", "buffer info"]

    assert picker_row_sort_key(key_row, "alpha") is not None
    assert picker_row_sort_key(info_row, "alpha") is not None
    assert picker_row_sort_key(menu_row, "alpha") is not None
    assert picker_row_sort_key(key_row, "alpha") < picker_row_sort_key(info_row, "alpha")  # type: ignore[operator]
    assert picker_row_sort_key(info_row, "alpha") < picker_row_sort_key(menu_row, "alpha")  # type: ignore[operator]
    assert picker_row_sort_key(multi_row, "project buffer") is not None
    assert picker_row_sort_key(multi_row, "project missing") is None


def test_picker_row_sort_key_keeps_exact_key_match_escape_hatch_for_visible_indexes() -> None:
    def same_visible_index(query: str, key: str) -> bool:
        return query.lstrip("#") == key.lstrip("#")

    exact = picker_row_sort_key(["#3", "jump", "*3/5", "preview"], "3", exact_key_match=same_visible_index)
    fuzzy = picker_row_sort_key(["#30", "jump", " 30/50", "preview"], "3", exact_key_match=same_visible_index)
    assert exact is not None
    assert fuzzy is not None
    assert exact < fuzzy


def test_multi_term_field_key_is_stable_and_sortable_with_fuzzy_keys() -> None:
    multi = multi_term_field_key([(0, "alpha"), (1, "project buffer")], "alpha buffer", fallback_rank=5, tie_name="alpha")
    fuzzy = (0, *completion_fuzzy_sort_key("alpha", "alpha"), "alpha")  # type: ignore[misc]
    assert multi is not None
    # The two rank families intentionally have slightly different tuple shapes;
    # sorting must remain safe because the leading rank separates them.
    assert sorted([multi, fuzzy])[0] == fuzzy


def test_completion_fuzzy_sort_prefers_candidate_start_over_hidden_substring() -> None:
    start = completion_fuzzy_sort_key("showkey", "sk")
    hidden = completion_fuzzy_sort_key("diskdiff", "sk")
    assert start is not None
    assert hidden is not None
    assert start < hidden
