from __future__ import annotations

import numpy as np

from src.muc5.counter_response import (
    GUARDED_COUNTER_AXIS,
    LEGACY_COUNTER_AXIS,
    compare_counter_response_by_life,
)
from src.muc5.population_frontier import (
    population_cells_from_summary_rows,
    security_rows_from_cells,
    zero_sum_fictitious_play,
)
from src.muc5.response_matrix import SURGE_THREAT_AXIS
from src.muc5.threat_response import CLOSURE_THREAT_AXIS, PRESSURE_THREAT_AXIS, compare_threat_response_by_life


def test_counter_response_compare_missing_policy_fails_closed() -> None:
    rows = [
        {
            "size_axis": "counter60_vs_threat40",
            "counter_policy_axis": GUARDED_COUNTER_AXIS,
            "starting_life": 40,
            "target_mean_score_draw_half": 0.75,
        }
    ]
    [cell] = compare_counter_response_by_life(rows)
    assert cell["provisional_read"] == "incomplete_matrix"
    assert cell["legacy_cf34_counter_score"] is None
    assert cell["guard_minus_legacy_counter_score_delta"] is None
    assert cell["missing_counter_policy_axes"] == [LEGACY_COUNTER_AXIS]


def test_threat_response_compare_missing_policy_fails_closed() -> None:
    rows = [
        {
            "size_axis": "counter40_vs_threat40",
            "threat_policy_axis": CLOSURE_THREAT_AXIS,
            "starting_life": 20,
            "target_mean_score_draw_half": 0.5,
        }
    ]
    [cell] = compare_threat_response_by_life(rows)
    assert cell["provisional_read"] == "incomplete_matrix"
    assert cell["counter_guard_score_vs_threat_pressure"] is None
    assert cell["missing_threat_policy_axes"] == [PRESSURE_THREAT_AXIS]


def test_zero_sum_fictitious_play_finds_matching_pennies_value() -> None:
    result = zero_sum_fictitious_play([[1.0, 0.0], [0.0, 1.0]], iterations=5000)
    assert abs(sum(result.row_strategy) - 1.0) < 1e-12
    assert abs(sum(result.column_strategy) - 1.0) < 1e-12
    assert abs(result.midpoint_value - 0.5) < 0.02
    assert max(result.row_strategy) - min(result.row_strategy) < 0.03
    assert max(result.column_strategy) - min(result.column_strategy) < 0.03


def test_population_security_reports_complete_and_incomplete_cells() -> None:
    complete_rows = [
        {
            "size_axis": "cellA",
            "starting_life": 20,
            "counter_policy_axis": LEGACY_COUNTER_AXIS,
            "threat_policy_axis": CLOSURE_THREAT_AXIS,
            "target_mean_score_draw_half": 0.25,
            "games": 4,
        },
        {
            "size_axis": "cellA",
            "starting_life": 20,
            "counter_policy_axis": LEGACY_COUNTER_AXIS,
            "threat_policy_axis": PRESSURE_THREAT_AXIS,
            "target_mean_score_draw_half": 0.75,
            "games": 4,
        },
        {
            "size_axis": "cellA",
            "starting_life": 20,
            "counter_policy_axis": GUARDED_COUNTER_AXIS,
            "threat_policy_axis": CLOSURE_THREAT_AXIS,
            "target_mean_score_draw_half": 0.60,
            "games": 4,
        },
        {
            "size_axis": "cellA",
            "starting_life": 20,
            "counter_policy_axis": GUARDED_COUNTER_AXIS,
            "threat_policy_axis": PRESSURE_THREAT_AXIS,
            "target_mean_score_draw_half": 0.55,
            "games": 4,
        },
        {
            "size_axis": "cellB",
            "starting_life": 20,
            "counter_policy_axis": GUARDED_COUNTER_AXIS,
            "threat_policy_axis": CLOSURE_THREAT_AXIS,
            "target_mean_score_draw_half": 0.50,
            "games": 4,
        },
    ]
    cells = population_cells_from_summary_rows(
        complete_rows,
        row_policies=(LEGACY_COUNTER_AXIS, GUARDED_COUNTER_AXIS),
        column_policies=(CLOSURE_THREAT_AXIS, PRESSURE_THREAT_AXIS),
    )
    reports = security_rows_from_cells(cells, iterations=1000)
    by_cell = {r["size_axis"]: r for r in reports}
    assert by_cell["cellA"]["status"] == "complete_population_matrix"
    assert by_cell["cellA"]["best_pure_row_policy"] == GUARDED_COUNTER_AXIS
    assert np.isclose(float(by_cell["cellA"][f"pure_floor_{GUARDED_COUNTER_AXIS}"]), 0.55)
    assert by_cell["cellB"]["status"] == "incomplete_population_matrix"
    assert by_cell["cellB"]["missing_cell_count"] == 3

from pathlib import Path

from src.muc5.evidence_index import build_evidence_index, compact_derivatives


def test_evidence_index_classifies_unreferenced_bulk_with_derivative(tmp_path: Path) -> None:
    root = tmp_path
    (root / "data").mkdir()
    (root / "src").mkdir()
    raw = root / "data" / "rev0999_demo_cpp_transitions.csv"
    raw.write_text("a,b\n" + "1,2\n" * 20, encoding="utf-8")
    derivative = root / "data" / "rev0999_demo_cpp_transition_sample.csv"
    derivative.write_text("a,b\n1,2\n", encoding="utf-8")
    records = build_evidence_index(root, min_bytes=10)
    [record] = records
    assert record.path == "data/rev0999_demo_cpp_transitions.csv"
    assert record.row_count == 20
    assert record.compact_derivatives == ("data/rev0999_demo_cpp_transition_sample.csv",)
    assert record.retention_class == "evidence_archive_candidate"


def test_evidence_index_blocks_live_source_reference(tmp_path: Path) -> None:
    root = tmp_path
    (root / "data").mkdir()
    (root / "scripts").mkdir()
    raw = root / "data" / "rev0999_demo_replay_traces.jsonl"
    raw.write_text("{}\n{}\n", encoding="utf-8")
    (root / "data" / "rev0999_demo_replay_results.json").write_text("{}\n", encoding="utf-8")
    (root / "scripts" / "check.py").write_text("open('rev0999_demo_replay_traces.jsonl')\n", encoding="utf-8")
    [record] = build_evidence_index(root, min_bytes=1)
    assert record.retention_class == "blocked_by_live_reference"
    assert record.referenced_by == ("scripts/check.py",)


def test_evidence_index_is_idempotent_with_generated_index_present(tmp_path: Path) -> None:
    root = tmp_path
    (root / "data").mkdir()
    raw = root / "data" / "rev0999_demo_cpp_transitions.csv"
    raw.write_text("a,b\n" + "1,2\n" * 20, encoding="utf-8")
    (root / "data" / "rev0999_demo_cpp_transition_sample.csv").write_text("a,b\n1,2\n", encoding="utf-8")
    (root / "data" / "rev0999_evidence_index.json").write_text(
        '{"records":[{"path":"data/rev0999_demo_cpp_transitions.csv"}]}\n',
        encoding="utf-8",
    )
    [record] = build_evidence_index(root, min_bytes=10)
    assert record.retention_class == "evidence_archive_candidate"
    assert record.referenced_by == ()
