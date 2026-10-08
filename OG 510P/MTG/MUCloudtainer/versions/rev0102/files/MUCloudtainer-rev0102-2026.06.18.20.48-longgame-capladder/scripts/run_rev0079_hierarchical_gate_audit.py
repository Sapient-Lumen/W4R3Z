#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path
from typing import Mapping, Sequence

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.muc5.population_frontier import (  # noqa: E402
    COUNTER_POPULATION,
    THREAT_POPULATION,
    exact_support_enumeration_maximin,
    population_hierarchical_familywise_gate_rows,
    summarize_population_hierarchical_gate,
    zero_sum_fictitious_play,
)
from src.muc5.population_sampling import annotate_sampling_frame_rows, global_pool_source_rows  # noqa: E402
from src.muc5.terminal_mechanisms import to_float  # noqa: E402

REV = "rev0079"
CODENAME = "hierarchicalgate-exactfallback"
DATA = ROOT / "data"
ROW_POLICIES = tuple(axis for axis, _agent, _note in COUNTER_POPULATION)
COLUMN_POLICIES = tuple(axis for axis, _agent, _note in THREAT_POPULATION)
MIN_GAMES_PER_CELL = 24
MAX_CI_WIDTH = 0.60
CONSERVATIVE_FLOOR_THRESHOLD = 0.50
FAMILY_ALPHA = 0.05

SUMMARY_SOURCES = (
    ("rev0069", DATA / "rev0069_population_frontier_arm_summary.csv"),
    ("rev0070", DATA / "rev0070_population_precision_arm_summary.csv"),
    ("rev0075", DATA / "rev0075_stratum_challenge_arm_summary.csv"),
)

HIERARCHY_LAYERS = (
    ("global", (), True),
    ("by_life", ("starting_life",), True),
    ("by_size", ("size_axis",), True),
    ("by_size_life", ("size_axis", "starting_life"), False),
)

SOLVER_DIAGNOSTIC_MATRIX = (
    (0.8, 0.2, 0.4),
    (0.3, 0.7, 0.5),
    (0.6, 0.4, 0.9),
)


def read_csv(path: Path) -> list[dict[str, object]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def with_source_revision(rows: Sequence[Mapping[str, object]], revision: str) -> list[dict[str, object]]:
    out: list[dict[str, object]] = []
    for row in rows:
        item = dict(row)
        item["source_revision"] = str(item.get("source_revision") or revision)
        out.append(item)
    return out


def write_union_csv(path: Path, rows: Sequence[Mapping[str, object]], *, fallback_fields: Sequence[str] = ()) -> None:
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


def layer_summary_rows(gate_rows: Sequence[Mapping[str, object]]) -> list[dict[str, object]]:
    layer_names = []
    for row in gate_rows:
        layer = str(row.get("hierarchy_layer", ""))
        if layer and layer not in layer_names:
            layer_names.append(layer)
    out: list[dict[str, object]] = []
    for layer in layer_names:
        rows = [row for row in gate_rows if row.get("hierarchy_layer") == layer]
        finite_lcbs = [to_float(row.get("conservative_pure_security_lcb"), float("nan")) for row in rows]
        finite_lcbs = [value for value in finite_lcbs if value == value]
        finite_widths = [to_float(row.get("max_ci_width_observed"), float("nan")) for row in rows]
        finite_widths = [value for value in finite_widths if value == value]
        statuses: dict[str, int] = {}
        for row in rows:
            status = str(row.get("status", ""))
            statuses[status] = statuses.get(status, 0) + 1
        out.append(
            {
                "hierarchy_layer": layer,
                "mandatory": rows[0].get("hierarchy_layer_mandatory", "") if rows else "",
                "context_axes": rows[0].get("hierarchy_context_axes", "") if rows else "",
                "gate_rows": len(rows),
                "gate_passed_rows": sum(1 for row in rows if str(row.get("gate_passed", "")).lower() == "true" or row.get("gate_passed") is True),
                "status_counts_json": json.dumps(statuses, sort_keys=True),
                "worst_conservative_lcb": min(finite_lcbs) if finite_lcbs else "",
                "best_conservative_lcb": max(finite_lcbs) if finite_lcbs else "",
                "max_ci_width_observed": max(finite_widths) if finite_widths else "",
            }
        )
    return out


def solver_diagnostic_rows() -> list[dict[str, object]]:
    exact = exact_support_enumeration_maximin(SOLVER_DIAGNOSTIC_MATRIX)
    approx = zero_sum_fictitious_play(SOLVER_DIAGNOSTIC_MATRIX, iterations=200)
    return [
        {
            "matrix_label": "three_counter_policy_future_surface_smoke",
            "method": exact.solution_method,
            "iterations": exact.iterations,
            "guaranteed_value": exact.guaranteed_value,
            "upper_value": exact.exploitability_upper_value,
            "value_gap": exact.exploitability_upper_value - exact.guaranteed_value,
            "row_strategy": ";".join(f"{x:.12f}" for x in exact.row_strategy),
            "column_strategy": ";".join(f"{x:.12f}" for x in exact.column_strategy),
        },
        {
            "matrix_label": "three_counter_policy_future_surface_smoke",
            "method": approx.solution_method,
            "iterations": approx.iterations,
            "guaranteed_value": approx.guaranteed_value,
            "upper_value": approx.exploitability_upper_value,
            "value_gap": approx.exploitability_upper_value - approx.guaranteed_value,
            "row_strategy": ";".join(f"{x:.12f}" for x in approx.row_strategy),
            "column_strategy": ";".join(f"{x:.12f}" for x in approx.column_strategy),
        },
    ]


def main() -> None:
    all_rows: list[dict[str, object]] = []
    for revision, path in SUMMARY_SOURCES:
        all_rows.extend(with_source_revision(read_csv(path), revision))
    annotated = annotate_sampling_frame_rows(all_rows)
    eligible = global_pool_source_rows(annotated)

    gate_rows = population_hierarchical_familywise_gate_rows(
        eligible,
        row_policies=ROW_POLICIES,
        column_policies=COLUMN_POLICIES,
        layers=HIERARCHY_LAYERS,
        min_games_per_cell=MIN_GAMES_PER_CELL,
        max_ci_width=MAX_CI_WIDTH,
        conservative_floor_threshold=CONSERVATIVE_FLOOR_THRESHOLD,
        alpha=FAMILY_ALPHA,
    )
    layer_rows = layer_summary_rows(gate_rows)
    solver_rows = solver_diagnostic_rows()
    hierarchy_summary = summarize_population_hierarchical_gate(gate_rows)

    global_rows = [row for row in gate_rows if row.get("hierarchy_layer") == "global"]
    size_rows = [row for row in gate_rows if row.get("hierarchy_layer") == "by_size"]
    size_life_rows = [row for row in gate_rows if row.get("hierarchy_layer") == "by_size_life"]
    life_rows = [row for row in gate_rows if row.get("hierarchy_layer") == "by_life"]
    exact_solver = next(row for row in solver_rows if row["method"] == "exact_support_enumeration")
    approx_solver = next(row for row in solver_rows if row["method"] == "fictitious_play")

    write_union_csv(DATA / "rev0079_hierarchical_familywise_gate.csv", gate_rows)
    write_union_csv(DATA / "rev0079_hierarchical_gate_layer_summary.csv", layer_rows)
    write_union_csv(DATA / "rev0079_solver_diagnostic.csv", solver_rows)

    global_lcb = to_float(global_rows[0].get("conservative_pure_security_lcb"), float("nan")) if global_rows else float("nan")
    mandatory_lcbs = [to_float(row.get("conservative_pure_security_lcb"), float("nan")) for row in gate_rows if row.get("hierarchy_layer_mandatory")]
    mandatory_lcbs = [value for value in mandatory_lcbs if value == value]
    worst_mandatory_lcb = min(mandatory_lcbs) if mandatory_lcbs else float("nan")

    summary = {
        "revision": REV,
        "codename": CODENAME,
        "audit_focus": "promotion must not rely only on a broad global pool when size/life strata or future exact-solver paths expose weaker evidence",
        "source_summary_rows": len(annotated),
        "eligible_summary_rows": len(eligible),
        "eligible_summary_game_rows": sum(int(row.get("games", 0)) for row in eligible),
        "hierarchy_summary": hierarchy_summary,
        "hierarchy_gate_rows": len(gate_rows),
        "layer_summary_rows": len(layer_rows),
        "global_familywise_lcb": global_lcb,
        "worst_mandatory_layer_lcb": worst_mandatory_lcb,
        "global_minus_worst_mandatory_lcb": global_lcb - worst_mandatory_lcb,
        "global_status": global_rows[0].get("status") if global_rows else None,
        "life_status_counts": {str(row.get("status")): sum(1 for item in life_rows if item.get("status") == row.get("status")) for row in life_rows},
        "size_status_counts": {str(row.get("status")): sum(1 for item in size_rows if item.get("status") == row.get("status")) for row in size_rows},
        "size_life_status_counts": {str(row.get("status")): sum(1 for item in size_life_rows if item.get("status") == row.get("status")) for row in size_life_rows},
        "mandatory_gate_passed_rows": hierarchy_summary.get("mandatory_gate_passed_rows"),
        "mandatory_all_passed": hierarchy_summary.get("mandatory_all_passed"),
        "diagnostic_gate_passed_rows": hierarchy_summary.get("diagnostic_gate_passed_rows"),
        "solver_exact_method": exact_solver["method"],
        "solver_exact_value": exact_solver["guaranteed_value"],
        "solver_exact_value_gap": exact_solver["value_gap"],
        "solver_fictitious_play_value_gap_200_iterations": approx_solver["value_gap"],
        "solver_exact_minus_fp_guarantee": to_float(exact_solver["guaranteed_value"], float("nan")) - to_float(approx_solver["guaranteed_value"], float("nan")),
        "read": "eligible broad pool remains quarantined; more importantly, size strata still fail precision and fine size/life strata remain underpowered, so aggregate-only promotion would be unsafe even before adding new policies",
    }
    dump_json(DATA / "rev0079_hierarchical_gate_summary.json", summary)
    print(json.dumps(summary, indent=2, sort_keys=True))

    if hierarchy_summary.get("gate_passed_cells") != 0:
        raise SystemExit("hierarchical eligible familywise gate unexpectedly promoted a cell")
    if hierarchy_summary.get("hierarchy_layers") != {"global": 1, "by_life": 2, "by_size": 3, "by_size_life": 6}:
        raise SystemExit("hierarchical gate produced an unexpected layer shape")
    if summary["size_status_counts"].get("precision_target_not_met") != 3:
        raise SystemExit("size-layer precision weakness was not detected")
    if summary["size_life_status_counts"].get("underpowered_min_games") != 6:
        raise SystemExit("fine size/life underpower was not detected")
    if abs(float(exact_solver["guaranteed_value"]) - 0.5) > 1e-12 or abs(float(exact_solver["value_gap"])) > 1e-12:
        raise SystemExit("exact support enumeration diagnostic did not solve the known small game")


if __name__ == "__main__":
    main()
