from __future__ import annotations

import random
from collections.abc import Iterable

import pytest

from micromax_editor.buffer import Cursor
from micromax_editor.editor import Editor
from micromax_editor.simultaneous_edits import (
    SimultaneousEditError,
    SimultaneousTextEdit,
    line_start_offsets,
    line_start_offsets_for_lines,
    offset_to_cursor,
    plan_simultaneous_edits,
    plan_simultaneous_edits_lines,
)


def _install_cursors(
    editor: Editor,
    cursors: Iterable[Cursor],
    anchors: Iterable[Cursor | None] | None = None,
) -> None:
    eb = editor.cur()
    cursor_rows = [Cursor(int(cursor.line), int(cursor.col)) for cursor in cursors]
    anchor_rows = (
        [None] * len(cursor_rows)
        if anchors is None
        else [
            Cursor(int(anchor.line), int(anchor.col)) if anchor is not None else None
            for anchor in anchors
        ]
    )
    eb.cursors[:] = cursor_rows
    eb.sel_anchors[:] = anchor_rows
    eb.cursor_ids[:] = list(range(1, len(cursor_rows) + 1))
    eb.primary = 0
    editor._normalize_cursor_lists(eb)


def test_line_vector_planner_matches_flat_oracle_across_seeded_unicode_plans() -> None:
    rng = random.Random(991)
    source_alphabet = "ab Ω🙂\n"
    replacement_alphabet = "XYβ🙂\n"

    for _case in range(2000):
        source = "".join(
            rng.choice(source_alphabet) for _ in range(rng.randrange(0, 90))
        )
        starts = line_start_offsets(source)
        flat_edits: list[tuple[int, int, str]] = []
        source_at = 0
        while source_at <= len(source) and len(flat_edits) < 9:
            source_at += rng.randrange(0, 8)
            if source_at > len(source):
                break
            end = min(len(source), source_at + rng.randrange(0, 8))
            replacement = "".join(
                rng.choice(replacement_alphabet)
                for _ in range(rng.randrange(0, 8))
            )
            flat_edits.append((source_at, end, replacement))
            source_at = max(source_at + 1, end)

        requests = [
            SimultaneousTextEdit(
                offset_to_cursor(source, starts, start),
                offset_to_cursor(source, starts, end),
                replacement,
                owner=index,
            )
            for index, (start, end, replacement) in enumerate(flat_edits)
        ]
        flat_plan = plan_simultaneous_edits(
            source,
            requests,
            source_starts=starts,
        )
        source_lines = tuple(source.split("\n"))
        line_starts = line_start_offsets_for_lines(source_lines)
        line_plan = plan_simultaneous_edits_lines(
            source_lines,
            requests,
            source_starts=line_starts,
            capture_history_witness=True,
        )
        suppressed_plan = plan_simultaneous_edits_lines(
            source_lines,
            requests,
            source_starts=line_starts,
            capture_history_witness=False,
        )

        assert "\n".join(line_plan.new_lines) == flat_plan.new_text
        assert "\n".join(suppressed_plan.new_lines) == flat_plan.new_text
        assert line_plan.result_length == len(flat_plan.new_text)
        assert suppressed_plan.result_length == line_plan.result_length
        assert line_plan.edit_count == flat_plan.edit_count
        assert suppressed_plan.edit_count == line_plan.edit_count
        assert line_plan.owner_offsets == flat_plan.owner_offsets
        assert suppressed_plan.owner_offsets == line_plan.owner_offsets
        assert line_plan.compact_history_witness() == flat_plan.compact_history_witness()
        assert line_plan.text_changed == flat_plan.text_changed
        assert suppressed_plan.text_changed == line_plan.text_changed
        assert suppressed_plan.history_witness is None

        points = {0, len(source)}
        for start, end, _replacement in flat_edits:
            points.update((start, end))
        if source:
            points.add(rng.randrange(0, len(source) + 1))
        for affinity in ("left", "right"):
            for point in points:
                assert line_plan.map_offset(point, affinity=affinity) == flat_plan.map_offset(
                    point,
                    affinity=affinity,
                )
                assert suppressed_plan.map_offset(
                    point,
                    affinity=affinity,
                ) == flat_plan.map_offset(point, affinity=affinity)


def test_line_vector_planner_reuses_every_complete_untouched_line_object() -> None:
    source_lines = tuple(f"{index:05d}:" + ("a" * 90) for index in range(5000))
    starts = line_start_offsets_for_lines(source_lines)
    plan = plan_simultaneous_edits_lines(
        source_lines,
        [
            SimultaneousTextEdit(Cursor(100, 10), Cursor(100, 11), "X", owner=0),
            SimultaneousTextEdit(Cursor(4900, 20), Cursor(4900, 21), "Y", owner=1),
        ],
        source_starts=starts,
        capture_history_witness=True,
    )

    assert plan.text_changed is True
    assert len(plan.new_lines) == len(source_lines)
    assert sum(
        1
        for index, line in enumerate(plan.new_lines)
        if line is source_lines[index]
    ) == len(source_lines) - 2
    assert plan.compact_history_witness().retained_texts() == ("a", "X", "a", "Y")


def test_product_multirange_edit_and_history_never_call_full_text_methods(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    source_lines = [f"{index:05d}:" + ("a" * 90) for index in range(5000)]
    source = "\n".join(source_lines)
    editor = Editor()
    editor.new_buffer("line-vector-product", source)
    eb = editor.cur()
    eb.buf.set_fastdirty(True)
    _install_cursors(editor, [Cursor(100, 10), Cursor(4900, 20)])

    commits = 0
    original_replace_lines = eb.buf.replace_lines

    def counted_replace_lines(lines: Iterable[str]) -> None:
        nonlocal commits
        commits += 1
        original_replace_lines(lines)

    def forbidden_full_text(*_args, **_kwargs):
        raise AssertionError("genuine multi-range product path materialized full text")

    monkeypatch.setattr(eb.buf, "replace_lines", counted_replace_lines)
    monkeypatch.setattr(eb.buf, "get_text", forbidden_full_text)
    monkeypatch.setattr(eb.buf, "set_text", forbidden_full_text)

    before_version = int(eb.buf.version)
    editor.input["text"] = "X"
    assert editor.run_action("InsertText") is True
    expected_lines = list(source_lines)
    expected_lines[100] = source_lines[100][:10] + "X" + source_lines[100][10:]
    expected_lines[4900] = source_lines[4900][:20] + "X" + source_lines[4900][20:]
    assert list(eb.buf.lines) == expected_lines
    assert int(eb.buf.version) == before_version + 1
    assert commits == 1

    assert editor.undo_feedback() is True
    assert list(eb.buf.lines) == source_lines
    assert commits == 2
    assert editor.redo_feedback() is True
    assert list(eb.buf.lines) == expected_lines
    assert commits == 3


def test_suppressed_multirange_edit_skips_discarded_old_slice_capture(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import micromax_editor.simultaneous_edits as simultaneous_module

    source = "a" * 300_000
    editor = Editor()
    editor.new_buffer("suppressed", source)
    eb = editor.cur()
    eb.buf.set_fastdirty(True)
    _install_cursors(editor, [Cursor(0, 80_000), Cursor(0, 260_000)])

    def forbidden_range_text(*_args, **_kwargs):
        raise AssertionError("suppressed owner captured a discarded old slice")

    monkeypatch.setattr(
        simultaneous_module,
        "_line_vector_range_text",
        forbidden_range_text,
    )
    requests = [
        SimultaneousTextEdit(Cursor(0, 20_000), Cursor(0, 80_000), "LEFT", owner=0),
        SimultaneousTextEdit(
            Cursor(0, 220_000),
            Cursor(0, 260_000),
            "RIGHT",
            owner=1,
        ),
    ]

    with editor.undo.suppress_recording():
        result = editor._apply_undoable_simultaneous_buffer_edits(
            eb,
            requests,
            clear_selection_indices=(0, 1),
            description="suppressed line-vector witness",
        )

    assert result.changed is True
    assert result.history_witness is None
    assert editor.undo.depth() == 0
    assert "\n".join(eb.buf.lines) == (
        source[:20_000]
        + "LEFT"
        + source[80_000:220_000]
        + "RIGHT"
        + source[260_000:]
    )


def test_history_capture_reads_only_changed_coalesced_source_ranges(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import micromax_editor.simultaneous_edits as simultaneous_module

    source_lines = ("alpha", "beta", "gamma")
    starts = line_start_offsets_for_lines(source_lines)
    calls = 0
    original = simultaneous_module._line_vector_range_text

    def counted_range_text(lines, start, end):
        nonlocal calls
        calls += 1
        return original(lines, start, end)

    monkeypatch.setattr(simultaneous_module, "_line_vector_range_text", counted_range_text)
    plan = plan_simultaneous_edits_lines(
        source_lines,
        [
            SimultaneousTextEdit(Cursor(0, 0), Cursor(0, 5), "ALPHA", owner=0),
            SimultaneousTextEdit(Cursor(1, 0), Cursor(1, 4), "beta", owner=1),
            SimultaneousTextEdit(Cursor(2, 0), Cursor(2, 5), "G", owner=2),
        ],
        source_starts=starts,
        capture_history_witness=True,
    )

    assert calls == 2
    assert len(plan.compact_history_witness().splices) == 2
    assert "\n".join(plan.new_lines) == "ALPHA\nbeta\nG"


def test_equal_multiline_plan_avoids_discarded_source_slice_and_result_build(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import micromax_editor.simultaneous_edits as simultaneous_module

    source_lines = ("alpha", "beta", "gamma", "delta")
    source_starts = line_start_offsets_for_lines(source_lines)

    def forbidden(*_args, **_kwargs):
        raise AssertionError("equal replacement allocated or rebuilt document text")

    monkeypatch.setattr(simultaneous_module, "_line_vector_range_text", forbidden)
    monkeypatch.setattr(
        simultaneous_module,
        "_build_line_vector_replacements",
        forbidden,
    )
    plan = plan_simultaneous_edits_lines(
        source_lines,
        [
            SimultaneousTextEdit(
                Cursor(0, 2),
                Cursor(1, 2),
                "pha\nbe",
                owner=0,
            ),
            SimultaneousTextEdit(
                Cursor(2, 0),
                Cursor(3, 5),
                "gamma\ndelta",
                owner=1,
            ),
        ],
        source_starts=source_starts,
        capture_history_witness=True,
    )

    assert plan.text_changed is False
    assert plan.new_lines is source_lines
    assert plan.result_starts is source_starts
    assert plan.compact_history_witness().splices == ()


def test_net_zero_component_changes_collapse_to_sidecar_only_history() -> None:
    source_lines = ("a  aabΩ", "")
    source_starts = line_start_offsets_for_lines(source_lines)
    requests = [
        SimultaneousTextEdit(Cursor(0, 7), Cursor(1, 0), "", owner=0),
        SimultaneousTextEdit(Cursor(1, 0), Cursor(1, 0), "\r", owner=1),
    ]

    flat = plan_simultaneous_edits("\n".join(source_lines), requests)
    line = plan_simultaneous_edits_lines(
        source_lines,
        requests,
        source_starts=source_starts,
        capture_history_witness=True,
    )

    assert flat.new_text == "\n".join(source_lines)
    assert flat.text_changed is False
    assert flat.compact_history_witness().splices == ()
    assert line.text_changed is False
    assert line.new_lines is source_lines
    assert line.result_starts is source_starts
    assert line.compact_history_witness().splices == ()


def test_net_zero_product_edit_undo_redo_never_publish_text(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    editor = Editor()
    editor.new_buffer("net-zero", "a  aabΩ\n")
    eb = editor.cur()
    eb.buf.set_fastdirty(True)
    _install_cursors(editor, [Cursor(0, 0), Cursor(0, 1)])

    commits = 0
    original_replace_lines = eb.buf.replace_lines

    def counted_replace_lines(lines: Iterable[str]) -> None:
        nonlocal commits
        commits += 1
        original_replace_lines(lines)

    monkeypatch.setattr(eb.buf, "replace_lines", counted_replace_lines)
    before_version = int(eb.buf.version)
    result = editor._apply_undoable_simultaneous_buffer_edits(
        eb,
        [
            SimultaneousTextEdit(Cursor(0, 7), Cursor(1, 0), "", owner=0),
            SimultaneousTextEdit(Cursor(1, 0), Cursor(1, 0), "\r", owner=1),
        ],
        clear_selection_indices=(0, 1),
        description="net-zero multiline exchange",
    )

    assert result.changed is True
    assert result.text_changed is False
    assert result.history_witness is not None
    assert result.history_witness.splices == ()
    assert "\n".join(eb.buf.lines) == "a  aabΩ\n"
    assert int(eb.buf.version) == before_version
    assert commits == 0
    assert editor.undo.depth() == 1

    assert editor.undo_feedback() is True
    assert "\n".join(eb.buf.lines) == "a  aabΩ\n"
    assert int(eb.buf.version) == before_version
    assert commits == 0

    assert editor.redo_feedback() is True
    assert "\n".join(eb.buf.lines) == "a  aabΩ\n"
    assert int(eb.buf.version) == before_version
    assert commits == 0


def test_line_vector_overlap_refuses_before_result_construction(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import micromax_editor.simultaneous_edits as simultaneous_module

    def forbidden_builder(*_args, **_kwargs):
        raise AssertionError("overlap reached result construction")

    monkeypatch.setattr(
        simultaneous_module,
        "_build_line_vector_replacements",
        forbidden_builder,
    )
    with pytest.raises(SimultaneousEditError, match="overlapping edit ranges"):
        plan_simultaneous_edits_lines(
            ("abcdef",),
            [
                SimultaneousTextEdit(Cursor(0, 0), Cursor(0, 4), "X", owner=0),
                SimultaneousTextEdit(Cursor(0, 2), Cursor(0, 5), "Y", owner=1),
            ],
        )


def test_line_vector_plan_coalesces_exact_duplicate_owners() -> None:
    source_lines = ("alpha", "beta", "gamma")
    plan = plan_simultaneous_edits_lines(
        source_lines,
        [
            SimultaneousTextEdit(Cursor(1, 0), Cursor(1, 4), "B", owner=0),
            SimultaneousTextEdit(Cursor(1, 0), Cursor(1, 4), "B", owner=1),
        ],
    )

    assert plan.edit_count == 1
    assert plan.owner_offsets == ((0, 7), (1, 7))
    assert list(plan.new_lines) == ["alpha", "B", "gamma"]
    assert plan.new_lines[0] is source_lines[0]
    assert plan.new_lines[2] is source_lines[2]


def test_multirange_measurement_reports_flat_string_elimination() -> None:
    import importlib.util
    import sys
    from pathlib import Path

    path = Path(__file__).resolve().parents[1] / "tools" / "measure_multirange_planning.py"
    spec = importlib.util.spec_from_file_location(
        "test_measure_multirange_planning",
        path,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)

    report = module.build_report(
        line_count=300,
        line_width=60,
        edit_count=8,
        samples=1,
    )
    reference = report["rev0990_flat_reference"]
    product = report["rev0991_line_vector_product"]
    comparison = report["comparison"]

    assert report["schema"] == module.SCHEMA
    assert reference["full_document_get_text_calls"] == 1
    assert reference["full_document_set_text_calls"] == 1
    assert reference["complete_result_strings"] == 1
    assert reference["complete_document_string_generations"] == 2
    assert reference["line_vector_commits"] == 0
    assert product["full_document_get_text_calls"] == 0
    assert product["full_document_set_text_calls"] == 0
    assert product["complete_result_strings"] == 0
    assert product["complete_document_string_generations"] == 0
    assert product["line_vector_commits"] == 1
    assert product["reused_source_line_percent"] > 95.0
    assert (
        comparison["complete_document_string_generation_reduction_percent"]
        == 100.0
    )
    assert comparison["sidecars_exact"] is True
    assert comparison["history_shape_exact"] is True
    assert comparison["traced_current_reduction_percent"] > 50.0
    assert comparison["traced_peak_reduction_percent"] > 50.0
    assert reference["result_exact"] is True
    assert reference["undo_exact"] is True
    assert reference["redo_exact"] is True
    assert product["result_exact"] is True
    assert product["undo_exact"] is True
    assert product["redo_exact"] is True
