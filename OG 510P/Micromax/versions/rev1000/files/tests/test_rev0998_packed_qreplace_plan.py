from __future__ import annotations

import copy
import importlib.util
import sys

import pytest
from pathlib import Path
from types import ModuleType

from micromax_editor.editor import Editor
from micromax_editor.replace_plan import (
    ReplacementEdit,
    ReplacementEdits,
    scan_literal_replacement_edits_lines,
    scan_replacement_edits,
)

ROOT = Path(__file__).resolve().parents[1]


def _load_measurement_tool() -> ModuleType:
    path = ROOT / "tools" / "measure_qreplace_dense_plan.py"
    spec = importlib.util.spec_from_file_location(
        "test_measure_qreplace_dense_plan",
        path,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_packed_replacement_edits_preserve_sequence_contract() -> None:
    edits = ReplacementEdits(
        (
            ReplacementEdit(0, 1, "X"),
            ReplacementEdit(3, 4, "X"),
            ReplacementEdit(8, 10, "X"),
        )
    )

    assert len(edits) == 3
    assert edits.coordinate_bytes == 3 * 2 * 8
    assert edits.uses_uniform_replacement is True
    assert edits.retained_replacement_values == 1
    assert edits[0] == ReplacementEdit(0, 1, "X")
    assert edits[-1] == ReplacementEdit(8, 10, "X")
    assert edits[1:] == (
        ReplacementEdit(3, 4, "X"),
        ReplacementEdit(8, 10, "X"),
    )
    assert tuple(edits) == (
        ReplacementEdit(0, 1, "X"),
        ReplacementEdit(3, 4, "X"),
        ReplacementEdit(8, 10, "X"),
    )
    assert copy.deepcopy(edits) is edits
    assert not hasattr(edits, "append")
    with pytest.raises(TypeError):
        _ = edits[1.5]  # type: ignore[index]


def test_regex_rows_retain_per_match_values_only_when_expansion_varies() -> None:
    uniform = ReplacementEdits.from_rows(
        ((0, 2, "same"), (3, 5, "same"), (6, 8, "same"))
    )
    varied = ReplacementEdits.from_rows(
        ((0, 2, "v1"), (3, 5, "v2"), (6, 8, "v1"))
    )

    assert uniform.uses_uniform_replacement is True
    assert uniform.retained_replacement_values == 1
    assert varied.uses_uniform_replacement is False
    assert varied.retained_replacement_values == 3
    assert [edit.new for edit in varied] == ["v1", "v2", "v1"]
    assert varied.coordinate_bytes == uniform.coordinate_bytes == 48


def test_literal_scanner_retains_packed_coordinates_not_edit_objects() -> None:
    matches = 4_000
    scan = scan_literal_replacement_edits_lines(
        ("a " * matches,),
        "a",
        "XYZ",
        replace_all=True,
        max_matches=matches,
    )

    assert scan.ok is True
    assert isinstance(scan.edits, ReplacementEdits)
    assert len(scan.edits) == matches
    assert scan.edits.coordinate_bytes == matches * 16
    assert scan.edits.retained_replacement_values == 1
    assert scan.edits[0] == ReplacementEdit(0, 1, "XYZ")
    assert scan.edits[-1] == ReplacementEdit(
        (matches - 1) * 2,
        (matches - 1) * 2 + 1,
        "XYZ",
    )


def test_flat_literal_and_regex_scans_keep_exact_public_rows() -> None:
    literal = scan_replacement_edits(
        "a a a",
        "a",
        "X",
        literal=True,
        replace_all=True,
    )
    regex = scan_replacement_edits(
        "a1 a2 a1",
        r"a([0-9])",
        r"b$1",
        replace_all=True,
    )

    assert literal.edits == (
        ReplacementEdit(0, 1, "X"),
        ReplacementEdit(2, 3, "X"),
        ReplacementEdit(4, 5, "X"),
    )
    assert regex.edits == (
        ReplacementEdit(0, 2, "b1"),
        ReplacementEdit(3, 5, "b2"),
        ReplacementEdit(6, 8, "b1"),
    )
    assert literal.edits.uses_uniform_replacement is True
    assert regex.edits.uses_uniform_replacement is False


def test_qreplace_runtime_snapshot_shares_immutable_dense_plan() -> None:
    editor = Editor()
    editor.new_buffer("*packed-qreplace*", "a " * 2_000)

    assert editor.begin_query_replace("a", "XYZ", literal=True)
    assert editor.qreplace is not None
    plan = editor.qreplace.planned_matches
    snapshot = editor._qreplace_state(captured=True)

    assert isinstance(plan, ReplacementEdits)
    assert len(plan) == 2_000
    assert snapshot.session is not None
    assert snapshot.session.planned_matches is plan
    assert copy.deepcopy(plan) is plan


def test_regex_qreplace_collapses_identical_expansions_but_preserves_captures() -> None:
    editor = Editor()
    editor.new_buffer("*packed-regex-qreplace*", "a1 a2 a3")

    assert editor.begin_query_replace(r"a([0-9])", r"b$1", literal=False)
    assert editor.qreplace is not None
    plan = editor.qreplace.planned_matches

    assert plan.uses_uniform_replacement is False
    assert [edit.new for edit in plan] == ["b1", "b2", "b3"]
    assert editor.qreplace_all()
    assert editor.cur().buf.get_text() == "b1 b2 b3"


def test_regex_qreplace_shares_one_identical_expansion_value() -> None:
    editor = Editor()
    editor.new_buffer("*packed-uniform-regex-qreplace*", "a1 a2 a3")

    assert editor.begin_query_replace(r"a[0-9]", "same", literal=False)
    assert editor.qreplace is not None
    plan = editor.qreplace.planned_matches

    assert plan.uses_uniform_replacement is True
    assert plan.retained_replacement_values == 1
    assert [edit.new for edit in plan] == ["same", "same", "same"]


def test_dense_plan_measurement_reports_substantive_retained_reduction() -> None:
    module = _load_measurement_tool()
    report = module.build_report(matches=12_000, samples=1)

    assert report["schema"] == "micromax.qreplace-dense-plan-measurement.v1"
    reference = report["rev0997_object_rows_reference"]
    product = report["packed_plan_product"]
    comparison = report["comparison"]

    assert comparison["plans_exactly_equal"] is True
    assert comparison["product_deepcopy_shares_plan"] is True
    assert reference["matches"] == product["matches"] == 12_000
    assert product["coordinate_bytes"] == 12_000 * 16
    assert product["retained_replacement_values"] == 1
    assert comparison["traced_current_reduction_percent"] > 70
