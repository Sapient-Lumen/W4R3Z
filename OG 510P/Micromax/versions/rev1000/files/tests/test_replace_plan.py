from __future__ import annotations

from micromax_editor.replace_plan import (
    ReplacementEdit,
    plan_replace,
    scan_replacement_edits,
    scan_replacement_matches,
)


def test_plan_replace_literal_replaceall_is_side_effect_free_plain_data() -> None:
    plan = plan_replace("one two one", "one", "X", replace_all=True, literal=True)

    assert plan.ok is True
    assert plan.count == 2
    assert plan.new_text == "X two X"
    assert plan.matches[0].row() == [0, 0, 0, 3, "one", "X"]
    assert plan.summary_row()[0:6] == [1, 2, 1, 1, 1, 0]


def test_plan_replace_from_cursor_only_changes_next_match() -> None:
    plan = plan_replace("one two one", "one", "X", start_index=4, literal=True)

    assert plan.ok is True
    assert plan.count == 1
    assert plan.new_text == "one two X"
    assert plan.matches[0].line == 0
    assert plan.matches[0].col == 8


def test_plan_replace_regex_template_and_coordinates() -> None:
    plan = plan_replace("a1\na2", r"a([0-9])", r"b$1", replace_all=True)

    assert plan.ok is True
    assert plan.count == 2
    assert plan.new_text == "b1\nb2"
    assert [m.row() for m in plan.matches] == [
        [0, 0, 0, 2, "a1", "b1"],
        [1, 0, 1, 2, "a2", "b2"],
    ]


def test_plan_replace_rejects_template_error_even_when_not_found() -> None:
    plan = plan_replace("abc", r"z([0-9])", "$2")

    assert plan.ok is False
    assert plan.error.startswith("invalid replacement: ")
    assert plan.new_text is None


def test_plan_replace_rejects_zero_width_before_new_text() -> None:
    plan = plan_replace("abc", r"abc|$", "X", replace_all=True)

    assert plan.ok is False
    assert plan.error == "zero-width matches are not supported"
    assert plan.new_text is None



def test_dense_replace_plan_keeps_only_requested_rich_samples() -> None:
    text = "a\n" * 2_000

    plan = plan_replace(
        text,
        "a",
        "longer",
        replace_all=True,
        literal=True,
        sample_limit=2,
    )

    assert plan.ok is True
    assert plan.count == 2_000
    assert len(plan.matches) == 2
    assert [match.row() for match in plan.matches] == [
        [0, 0, 0, 1, "a", "longer"],
        [1, 0, 1, 1, "a", "longer"],
    ]
    assert plan.new_text == "longer\n" * 2_000


def test_compact_replacement_scan_defers_source_slices_and_coordinates() -> None:
    scan = scan_replacement_edits(
        "a1\na2",
        r"a([0-9])",
        r"b$1",
        replace_all=True,
    )

    assert scan.ok is True
    assert scan.edits == (
        ReplacementEdit(0, 2, "b1"),
        ReplacementEdit(3, 5, "b2"),
    )
    assert not hasattr(scan.edits[0], "old")
    assert not hasattr(scan.edits[0], "line")


def test_rich_replacement_scan_remains_coordinate_compatible() -> None:
    scan = scan_replacement_matches(
        "a1\na2",
        r"a([0-9])",
        r"b$1",
        replace_all=True,
    )

    assert scan.ok is True
    assert [match.row() for match in scan.matches] == [
        [0, 0, 0, 2, "a1", "b1"],
        [1, 0, 1, 2, "a2", "b2"],
    ]
