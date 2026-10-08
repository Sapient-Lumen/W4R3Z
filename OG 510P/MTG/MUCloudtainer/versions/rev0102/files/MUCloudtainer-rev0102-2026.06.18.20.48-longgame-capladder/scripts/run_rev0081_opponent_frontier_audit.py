#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path
from typing import Mapping, Sequence

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.muc5.population_frontier import (
    COUNTER_POPULATION,
    THREAT_POPULATION,
    aggregate_population_summary_rows,
    population_column_frontier_rows,
    population_hierarchical_familywise_gate_rows,
    summarize_population_column_frontier,
    summarize_population_hierarchical_gate,
)
from src.muc5.population_sampling import annotate_sampling_frame_rows, global_pool_source_rows, sampling_frame_summary_rows
from src.muc5.terminal_mechanisms import to_float, to_int

REV = "rev0081"
CODENAME = "opponentfrontier-threataudit"
DATA = ROOT / "data"
ROW_POLICIES = tuple(axis for axis, _agent, _note in COUNTER_POPULATION)
COLUMN_POLICIES = tuple(axis for axis, _agent, _note in THREAT_POPULATION)
HIERARCHY_LAYERS: tuple[tuple[str, tuple[str, ...], bool], ...] = (
    ("global", (), True),
    ("by_life", ("starting_life",), True),
    ("by_size", ("size_axis",), True),
    ("by_size_life", ("size_axis", "starting_life"), False),
)
SUMMARY_SOURCES: tuple[tuple[str, str], ...] = (
    ("rev0069", "rev0069_population_frontier_arm_summary.csv"),
    ("rev0070", "rev0070_population_precision_arm_summary.csv"),
    ("rev0075", "rev0075_stratum_challenge_arm_summary.csv"),
    ("rev0080", "rev0080_size_ladder_arm_summary.csv"),
)
MIN_GAMES_PER_CELL = 24
MAX_CI_WIDTH = 0.60
CONSERVATIVE_FLOOR_THRESHOLD = 0.50
FAMILY_ALPHA = 0.05


def read_csv(path: Path) -> list[dict[str, object]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def with_source_revision(rows: Sequence[Mapping[str, object]], revision: str) -> list[dict[str, object]]:
    return [dict(row, source_revision=revision) for row in rows]


def write_union_csv(path: Path, rows: Sequence[Mapping[str, object]], fallback_fields: Sequence[str] = ()) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames: list[str] = []
    seen: set[str] = set()
    for row in rows:
        for key in row.keys():
            key_s = str(key)
            if key_s not in seen:
                seen.add(key_s)
                fieldnames.append(key_s)
    if not fieldnames:
        fieldnames = list(fallback_fields)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in fieldnames})


def dump_json(path: Path, obj: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def layer_summary_rows(rows: Sequence[Mapping[str, object]]) -> list[dict[str, object]]:
    out: list[dict[str, object]] = []
    for layer, _axes, mandatory in HIERARCHY_LAYERS:
        layer_rows = [row for row in rows if row.get("hierarchy_layer") == layer]
        summary = summarize_population_column_frontier(layer_rows)
        out.append(
            {
                "hierarchy_layer": layer,
                "mandatory": bool(mandatory),
                "rows": summary["rows"],
                "column_answer_passed_rows": summary["column_answer_passed_rows"],
                "worst_best_response_lcb": summary["worst_best_response_lcb"],
                "best_best_response_lcb": summary["best_best_response_lcb"],
                "max_ci_width_observed": summary["max_ci_width_observed"],
                "status_counts": json.dumps(summary["status_counts"], sort_keys=True),
                "worst_threat_policy_axis": summary["worst_threat_policy_axis"],
                "worst_size_axis": summary["worst_size_axis"] or "",
                "worst_starting_life": summary["worst_starting_life"] or "",
                "worst_best_response_row_policy": summary["worst_best_response_row_policy"],
            }
        )
    return out


def frontier_rows_for_layers(source_rows: Sequence[Mapping[str, object]]) -> list[dict[str, object]]:
    out: list[dict[str, object]] = []
    for layer, axes, mandatory in HIERARCHY_LAYERS:
        pooled = aggregate_population_summary_rows(source_rows, context_axes=axes)
        rows = population_column_frontier_rows(
            pooled,
            row_policies=ROW_POLICIES,
            column_policies=COLUMN_POLICIES,
            context_axes=axes,
            min_games_per_cell=MIN_GAMES_PER_CELL,
            max_ci_width=MAX_CI_WIDTH,
            conservative_floor_threshold=CONSERVATIVE_FLOOR_THRESHOLD,
            alpha=FAMILY_ALPHA,
        )
        for row in rows:
            item = dict(row)
            item["hierarchy_layer"] = layer
            item["hierarchy_context_axes"] = ";".join(axes) if axes else "<global>"
            item["hierarchy_layer_mandatory"] = bool(mandatory)
            item["source_summary_rows"] = len(source_rows)
            item["pooled_summary_rows"] = len(pooled)
            out.append(item)
    return out


def main() -> None:
    DATA.mkdir(exist_ok=True)
    all_rows: list[dict[str, object]] = []
    for revision, name in SUMMARY_SOURCES:
        path = DATA / name
        if path.exists():
            all_rows.extend(with_source_revision(read_csv(path), revision))
    annotated = annotate_sampling_frame_rows(all_rows)
    eligible = global_pool_source_rows(annotated)

    hierarchy_gate = population_hierarchical_familywise_gate_rows(
        eligible,
        row_policies=ROW_POLICIES,
        column_policies=COLUMN_POLICIES,
        layers=HIERARCHY_LAYERS,
        min_games_per_cell=MIN_GAMES_PER_CELL,
        max_ci_width=MAX_CI_WIDTH,
        conservative_floor_threshold=CONSERVATIVE_FLOOR_THRESHOLD,
        alpha=FAMILY_ALPHA,
        iterations=40000,
    )
    frontier_rows = frontier_rows_for_layers(eligible)
    summary = summarize_population_column_frontier(frontier_rows)
    layer_rows = layer_summary_rows(frontier_rows)
    sampling_rows = sampling_frame_summary_rows(annotated)

    write_union_csv(DATA / "rev0081_opponent_frontier_familywise.csv", frontier_rows)
    write_union_csv(DATA / "rev0081_opponent_frontier_layer_summary.csv", layer_rows)
    write_union_csv(DATA / "rev0081_opponent_frontier_hierarchical_gate_reference.csv", hierarchy_gate)
    write_union_csv(DATA / "rev0081_sampling_frame_summary.csv", sampling_rows)

    hierarchy_summary = summarize_population_hierarchical_gate(hierarchy_gate)
    weak_threats = sorted(
        {
            str(row.get("threat_policy_axis"))
            for row in frontier_rows
            if str(row.get("status")) == "no_credible_counter_answer_for_threat_column"
        }
    )
    global_frontier = [row for row in frontier_rows if row.get("hierarchy_layer") == "global"]
    mandatory_frontier = [row for row in frontier_rows if str(row.get("hierarchy_layer_mandatory")).lower() in {"true", "1"}]
    finite_lcbs = [to_float(row.get("best_response_lcb"), float("nan")) for row in frontier_rows]
    finite_lcbs = [value for value in finite_lcbs if value == value]
    payload = {
        "revision": REV,
        "codename": CODENAME,
        "audit_focus": "resolve the rev0080 low-floor conclusion by threat column instead of letting one scalar hide which opponent axes lack credible counter answers",
        "source_summary_rows_total": len(all_rows),
        "eligible_summary_rows": len(eligible),
        "eligible_summary_game_rows": sum(to_int(row.get("games"), 0) for row in eligible),
        "adaptive_summary_rows_excluded": len(annotated) - len(eligible),
        "hierarchy_summary": hierarchy_summary,
        "frontier_summary": summary,
        "frontier_rows": len(frontier_rows),
        "frontier_layer_rows": len(layer_rows),
        "global_frontier_rows": len(global_frontier),
        "mandatory_frontier_rows": len(mandatory_frontier),
        "mandatory_column_answer_passed_rows": sum(1 for row in mandatory_frontier if str(row.get("column_answer_passed")).lower() in {"true", "1"}),
        "weak_threat_axes": weak_threats,
        "weak_threat_axis_count": len(weak_threats),
        "worst_best_response_lcb": min(finite_lcbs) if finite_lcbs else None,
        "best_best_response_lcb": max(finite_lcbs) if finite_lcbs else None,
        "max_ci_width_observed": max(to_float(row.get("max_ci_width_observed"), float("nan")) for row in frontier_rows),
        "min_games_per_observed_column_cell": min(to_int(row.get("min_games_per_observed_cell"), 0) for row in frontier_rows),
        "read": "opponent_column_frontier_has_no_promotable_counter_answers" if summary["column_answer_passed_rows"] == 0 else "some_threat_columns_have_candidate_answers",
    }
    dump_json(DATA / "rev0081_opponent_frontier_summary.json", payload)
    print(json.dumps(payload, indent=2, sort_keys=True))

    if payload["eligible_summary_game_rows"] != 1152:
        raise SystemExit("unexpected eligible game-row total for rev0081 frontier audit")
    if payload["frontier_rows"] != 36:
        raise SystemExit("unexpected frontier row count")
    if payload["frontier_summary"].get("column_answer_passed_rows") != 0:
        raise SystemExit("opponent frontier unexpectedly found a promotable threat-column answer")
    if payload["mandatory_column_answer_passed_rows"] != 0:
        raise SystemExit("mandatory opponent frontier unexpectedly passed")
    if payload["weak_threat_axis_count"] != len(COLUMN_POLICIES):
        raise SystemExit("not all threat axes were identified as lacking credible familywise counter answers")
    if payload["max_ci_width_observed"] > MAX_CI_WIDTH:
        raise SystemExit("frontier audit is still precision-limited")
    if payload["min_games_per_observed_column_cell"] < MIN_GAMES_PER_CELL:
        raise SystemExit("frontier audit is underpowered")


if __name__ == "__main__":
    main()
