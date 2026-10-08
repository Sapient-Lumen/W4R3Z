from __future__ import annotations

from pathlib import Path

from src.muc5.counter_response import GUARDED_COUNTER_AXIS, LEGACY_COUNTER_AXIS
from src.muc5.evidence_index import build_evidence_index, is_active_reference_path
from src.muc5.population_frontier import population_cells_from_summary_rows, population_precision_gate_rows
from src.muc5.threat_response import CLOSURE_THREAT_AXIS, PRESSURE_THREAT_AXIS


def _complete_precision_rows(*, games: int = 16, lcb_guard: float = 0.56, width: float = 0.20) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for counter in (LEGACY_COUNTER_AXIS, GUARDED_COUNTER_AXIS):
        for threat in (CLOSURE_THREAT_AXIS, PRESSURE_THREAT_AXIS):
            mean = 0.55 if counter == LEGACY_COUNTER_AXIS else max(lcb_guard + width / 2.0, 0.65)
            lcb = 0.40 if counter == LEGACY_COUNTER_AXIS else lcb_guard
            rows.append(
                {
                    "size_axis": "cellA",
                    "starting_life": 20,
                    "counter_policy_axis": counter,
                    "threat_policy_axis": threat,
                    "target_mean_score_draw_half": mean,
                    "target_score_lcb_95": lcb,
                    "target_score_ucb_95": min(1.0, lcb + width),
                    "games": games,
                }
            )
    return rows


def test_population_cells_treat_present_but_semantically_empty_rows_as_incomplete() -> None:
    rows = [
        {
            "size_axis": "cellA",
            "starting_life": 20,
            "counter_policy_axis": GUARDED_COUNTER_AXIS,
            "threat_policy_axis": CLOSURE_THREAT_AXIS,
            "target_mean_score_draw_half": "",
            "games": 8,
        },
        {
            "size_axis": "cellA",
            "starting_life": 20,
            "counter_policy_axis": LEGACY_COUNTER_AXIS,
            "threat_policy_axis": CLOSURE_THREAT_AXIS,
            "target_mean_score_draw_half": 0.5,
            "games": 0,
        },
    ]
    [cell] = population_cells_from_summary_rows(
        rows,
        row_policies=(LEGACY_COUNTER_AXIS, GUARDED_COUNTER_AXIS),
        column_policies=(CLOSURE_THREAT_AXIS,),
    )
    assert not cell.complete
    assert set(cell.missing_cells) == {
        (LEGACY_COUNTER_AXIS, CLOSURE_THREAT_AXIS),
        (GUARDED_COUNTER_AXIS, CLOSURE_THREAT_AXIS),
    }


def test_population_precision_gate_requires_preregistered_games_before_promotion() -> None:
    [row] = population_precision_gate_rows(
        _complete_precision_rows(games=8, lcb_guard=0.70, width=0.10),
        row_policies=(LEGACY_COUNTER_AXIS, GUARDED_COUNTER_AXIS),
        column_policies=(CLOSURE_THREAT_AXIS, PRESSURE_THREAT_AXIS),
        min_games_per_cell=16,
        max_ci_width=0.20,
        conservative_floor_threshold=0.50,
        iterations=200,
    )
    assert row["status"] == "underpowered_min_games"
    assert row["gate_passed"] is False


def test_population_precision_gate_requires_precision_not_just_high_mean() -> None:
    [row] = population_precision_gate_rows(
        _complete_precision_rows(games=16, lcb_guard=0.70, width=0.65),
        row_policies=(LEGACY_COUNTER_AXIS, GUARDED_COUNTER_AXIS),
        column_policies=(CLOSURE_THREAT_AXIS, PRESSURE_THREAT_AXIS),
        min_games_per_cell=16,
        max_ci_width=0.20,
        conservative_floor_threshold=0.50,
        iterations=200,
    )
    assert row["status"] == "precision_target_not_met"
    assert row["gate_passed"] is False


def test_population_precision_gate_can_pass_on_complete_precise_conservative_floor() -> None:
    [row] = population_precision_gate_rows(
        _complete_precision_rows(games=16, lcb_guard=0.62, width=0.10),
        row_policies=(LEGACY_COUNTER_AXIS, GUARDED_COUNTER_AXIS),
        column_policies=(CLOSURE_THREAT_AXIS, PRESSURE_THREAT_AXIS),
        min_games_per_cell=16,
        max_ci_width=0.20,
        conservative_floor_threshold=0.50,
        iterations=200,
    )
    assert row["status"] == "candidate_promotable"
    assert row["gate_passed"] is True
    assert row["conservative_best_pure_row_policy"] == GUARDED_COUNTER_AXIS


def test_evidence_index_distinguishes_historical_data_mentions_from_active_blockers(tmp_path: Path) -> None:
    root = tmp_path
    (root / "data").mkdir()
    (root / "scripts").mkdir()
    raw = root / "data" / "rev0999_demo_cpp_transitions.csv"
    raw.write_text("a,b\n" + "1,2\n" * 20, encoding="utf-8")
    (root / "data" / "rev0999_demo_cpp_transition_sample.csv").write_text("a,b\n1,2\n", encoding="utf-8")
    (root / "data" / "old_audit_summary.json").write_text(
        '{"path":"data/rev0999_demo_cpp_transitions.csv"}\n',
        encoding="utf-8",
    )
    [record] = build_evidence_index(root, min_bytes=10)
    assert record.referenced_by == ("data/old_audit_summary.json",)
    assert record.active_referenced_by == ()
    assert record.historical_referenced_by == ("data/old_audit_summary.json",)
    assert record.retention_class == "evidence_archive_candidate"

    (root / "scripts" / "live.py").write_text("open('rev0999_demo_cpp_transitions.csv')\n", encoding="utf-8")
    [record] = build_evidence_index(root, min_bytes=10)
    assert record.retention_class == "blocked_by_live_reference"
    assert record.active_referenced_by == ("scripts/live.py",)


def test_active_reference_path_classifier() -> None:
    assert is_active_reference_path("scripts/audit_cube.py")
    assert is_active_reference_path("docs/experiment_matrix_rev0042.md")
    assert not is_active_reference_path("data/rev0057_cloudtainer_size_audit_summary.json")
