from __future__ import annotations

import csv
import json
from pathlib import Path

from src.muc5.counter_response import GUARDED_COUNTER_AXIS, LEGACY_COUNTER_AXIS
from src.muc5.population_frontier import population_column_rescue_rows, summarize_population_column_rescue
from src.muc5.threat_response import CLOSURE_THREAT_AXIS, PRESSURE_THREAT_AXIS

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
ROW_POLICIES = (LEGACY_COUNTER_AXIS, GUARDED_COUNTER_AXIS)


def _read_csv(name: str) -> list[dict[str, object]]:
    with (DATA / name).open(newline="", encoding="utf-8") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def _frontier_row(threat: str, legacy: tuple[float, float, float], guard: tuple[float, float, float]) -> dict[str, object]:
    return {
        "complete": True,
        "hierarchy_layer": "global",
        "hierarchy_layer_mandatory": True,
        "threat_policy_axis": threat,
        "status": "no_credible_counter_answer_for_threat_column",
        "column_answer_passed": False,
        "min_games_per_observed_cell": 64,
        "max_ci_width_observed": 0.2,
        "mean_legacy_cf34_counter_ranker": legacy[0],
        "lcb_legacy_cf34_counter_ranker": legacy[1],
        "ucb_legacy_cf34_counter_ranker": legacy[2],
        "games_legacy_cf34_counter_ranker": 64,
        "mean_public_counter_guard": guard[0],
        "lcb_public_counter_guard": guard[1],
        "ucb_public_counter_guard": guard[2],
        "games_public_counter_guard": 64,
    }


def test_rescue_envelope_splits_certification_gap_from_counter_set_deficiency() -> None:
    rows = [
        _frontier_row(CLOSURE_THREAT_AXIS, (0.20, 0.10, 0.30), (0.56, 0.46, 0.66)),
        _frontier_row(PRESSURE_THREAT_AXIS, (0.20, 0.10, 0.30), (0.35, 0.25, 0.45)),
    ]
    rescue = population_column_rescue_rows(rows, row_policies=ROW_POLICIES, conservative_floor_threshold=0.50)
    assert rescue[0]["rescue_status"] == "certification_limited_existing_counter_candidate"
    assert rescue[0]["best_mean_policy"] == GUARDED_COUNTER_AXIS
    assert rescue[0]["ucb_rescue_possible"] is True
    assert rescue[1]["rescue_status"] == "current_counter_set_deficient_even_by_upper_bound"
    assert rescue[1]["ucb_rescue_possible"] is False
    summary = summarize_population_column_rescue(rescue)
    assert summary["rescue_status_counts"] == {
        "certification_limited_existing_counter_candidate": 1,
        "current_counter_set_deficient_even_by_upper_bound": 1,
    }
    assert summary["mandatory_current_counter_set_deficient_rows"] == 1


def test_actual_rev0082_rescue_audit_keeps_global_failures_unpromoted_but_prioritized() -> None:
    summary = json.loads((DATA / "rev0082_counterset_rescue_summary.json").read_text(encoding="utf-8"))
    assert summary["source_frontier_rows"] == 36
    assert summary["rescue_rows"] == 36
    assert summary["existing_counter_certified_rows"] == 0
    assert summary["current_counter_set_deficient_rows"] == 1
    assert summary["mandatory_current_counter_set_deficient_rows"] == 0
    assert summary["mandatory_certification_limited_rows"] == 11
    assert summary["mandatory_mean_below_rescuable_rows"] == 7
    assert summary["global_rescue_status_counts"] == {
        "certification_limited_existing_counter_candidate": 2,
        "mean_below_threshold_but_upper_bound_allows_rescue": 1,
    }
    weakest = summary["weakest_ucb_case"]
    assert weakest["hierarchy_layer"] == "by_size_life"
    assert weakest["size_axis"] == "counter40_vs_threat40"
    assert str(weakest["starting_life"]) == "20"
    assert weakest["threat_policy_axis"] == CLOSURE_THREAT_AXIS
    assert weakest["ucb_gap_to_threshold"] < 0


def test_rescue_csv_preserves_all_layers_and_has_no_certified_existing_counter() -> None:
    rows = _read_csv("rev0082_counterset_rescue_envelope.csv")
    assert len(rows) == 36
    layer_counts: dict[str, int] = {}
    status_counts: dict[str, int] = {}
    for row in rows:
        layer_counts[row["hierarchy_layer"]] = layer_counts.get(row["hierarchy_layer"], 0) + 1
        status_counts[row["rescue_status"]] = status_counts.get(row["rescue_status"], 0) + 1
        assert row["existing_counter_certified"].lower() == "false"
    assert layer_counts == {"global": 3, "by_life": 6, "by_size": 9, "by_size_life": 18}
    assert status_counts == {
        "certification_limited_existing_counter_candidate": 21,
        "mean_below_threshold_but_upper_bound_allows_rescue": 14,
        "current_counter_set_deficient_even_by_upper_bound": 1,
    }
