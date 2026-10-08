#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path
from typing import Iterable, Mapping, Sequence

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.muc5.population_frontier import (
    COUNTER_POPULATION,
    THREAT_POPULATION,
    aggregate_population_summary_rows,
    population_precision_gate_rows,
    security_rows_from_cells,
    population_cells_from_summary_rows,
    summarize_population_precision_gate,
)

REV = "rev0073"
CODENAME = "exactmaximin-poolrobustness"
DATA = ROOT / "data"
MIN_GAMES_PER_CELL = 24
MAX_CI_WIDTH = 0.60
CONSERVATIVE_FLOOR_THRESHOLD = 0.50
ITERATIONS = 40000  # fallback only; the current two-row game uses the exact solver.


def read_csv(path: Path) -> list[dict[str, object]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def write_union_csv(path: Path, rows: Sequence[Mapping[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fieldnames: list[str] = []
    seen: set[str] = set()
    for row in rows:
        for key in row.keys():
            if key not in seen:
                seen.add(key)
                fieldnames.append(key)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(dict(row))


def dump_json(path: Path, obj: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def with_source_revision(rows: Iterable[Mapping[str, object]], revision: str) -> list[dict[str, object]]:
    out: list[dict[str, object]] = []
    for row in rows:
        item = dict(row)
        item["source_revision"] = revision
        out.append(item)
    return out


def add_scope(rows: Iterable[Mapping[str, object]], *, scope: str, value: str) -> list[dict[str, object]]:
    out: list[dict[str, object]] = []
    for row in rows:
        item = dict(row)
        item["robustness_scope"] = scope
        item["robustness_value"] = value
        out.append(item)
    return out


def evaluate(
    rows: Sequence[Mapping[str, object]],
    *,
    scope: str,
    value: str,
    context_axes: tuple[str, ...] = ("robustness_scope", "robustness_value"),
) -> tuple[list[dict[str, object]], list[dict[str, object]], list[dict[str, object]]]:
    counter_axes = tuple(axis for axis, _agent, _note in COUNTER_POPULATION)
    threat_axes = tuple(axis for axis, _agent, _note in THREAT_POPULATION)
    scoped = add_scope(rows, scope=scope, value=value)
    pooled = aggregate_population_summary_rows(scoped, context_axes=context_axes)
    cells = population_cells_from_summary_rows(
        pooled,
        context_axes=context_axes,
        row_policies=counter_axes,
        column_policies=threat_axes,
    )
    security = security_rows_from_cells(cells, iterations=ITERATIONS)
    gate = population_precision_gate_rows(
        pooled,
        context_axes=context_axes,
        row_policies=counter_axes,
        column_policies=threat_axes,
        min_games_per_cell=MIN_GAMES_PER_CELL,
        max_ci_width=MAX_CI_WIDTH,
        conservative_floor_threshold=CONSERVATIVE_FLOOR_THRESHOLD,
        iterations=ITERATIONS,
    )
    for collection in (pooled, security, gate):
        for row in collection:
            row["robustness_scope"] = scope
            row["robustness_value"] = value
            row["context_axes"] = ";".join(context_axes)
    return pooled, security, gate


def distinct(rows: Sequence[Mapping[str, object]], key: str) -> list[str]:
    return sorted({str(row.get(key, "")) for row in rows if row.get(key) not in {None, ""}})


def main() -> None:
    DATA.mkdir(exist_ok=True)
    source_rows = with_source_revision(read_csv(DATA / "rev0069_population_frontier_arm_summary.csv"), "rev0069")
    source_rows += with_source_revision(read_csv(DATA / "rev0070_population_precision_arm_summary.csv"), "rev0070")

    evaluations: list[tuple[str, str, list[dict[str, object]]]] = []
    evaluations.append(("all_source_pool", "all", list(source_rows)))

    for source in distinct(source_rows, "source_revision"):
        evaluations.append(("source_revision_only", source, [row for row in source_rows if row.get("source_revision") == source]))
        evaluations.append(("leave_one_source_revision", f"without_{source}", [row for row in source_rows if row.get("source_revision") != source]))
    for size_axis in distinct(source_rows, "size_axis"):
        evaluations.append(("size_axis_only", size_axis, [row for row in source_rows if row.get("size_axis") == size_axis]))
        evaluations.append(("leave_one_size_axis", f"without_{size_axis}", [row for row in source_rows if row.get("size_axis") != size_axis]))
    for life in distinct(source_rows, "starting_life"):
        evaluations.append(("starting_life_only", life, [row for row in source_rows if str(row.get("starting_life")) == life]))
        evaluations.append(("leave_one_starting_life", f"without_{life}", [row for row in source_rows if str(row.get("starting_life")) != life]))

    pooled_rows: list[dict[str, object]] = []
    security_rows: list[dict[str, object]] = []
    gate_rows: list[dict[str, object]] = []
    for scope, value, rows in evaluations:
        pooled, security, gate = evaluate(rows, scope=scope, value=value)
        pooled_rows.extend(pooled)
        security_rows.extend(security)
        gate_rows.extend(gate)

    write_union_csv(DATA / "rev0073_population_pool_robustness_pooled_arm_summary.csv", pooled_rows)
    write_union_csv(DATA / "rev0073_population_pool_robustness_security.csv", security_rows)
    write_union_csv(DATA / "rev0073_population_pool_robustness_gate.csv", gate_rows)

    gate_summary = summarize_population_precision_gate(gate_rows)
    methods = sorted({str(row.get("mixed_solution_method", "")) for row in gate_rows if row.get("mixed_solution_method")})
    exact_gate_rows = sum(1 for row in gate_rows if row.get("mixed_solution_method") == "exact_two_row")
    promotable = [row for row in gate_rows if row.get("gate_passed") in {True, "True", "true", "1"}]
    low_floor = [row for row in gate_rows if row.get("status") == "quarantined_low_security_floor"]
    underpowered = [row for row in gate_rows if row.get("status") == "underpowered_min_games"]
    precision_blocked = [row for row in gate_rows if row.get("status") == "precision_target_not_met"]
    finite_widths = [float(row["max_ci_width_observed"]) for row in gate_rows if row.get("max_ci_width_observed") not in {None, ""}]
    finite_lcbs = [float(row["conservative_pure_security_lcb"]) for row in gate_rows if row.get("conservative_pure_security_lcb") not in {None, ""}]
    min_games = [int(row["min_games_per_observed_cell"]) for row in gate_rows if row.get("min_games_per_observed_cell") not in {None, ""}]

    summary = {
        "revision": REV,
        "codename": CODENAME,
        "source_revisions": ["rev0069", "rev0070"],
        "source_arm_summary_rows": len(source_rows),
        "source_population_games": 144 + 288,
        "evaluation_count": len(evaluations),
        "pooled_arm_summary_rows": len(pooled_rows),
        "security_rows": len(security_rows),
        "gate_rows": len(gate_rows),
        "gate_min_games_per_cell": MIN_GAMES_PER_CELL,
        "gate_max_ci_width": MAX_CI_WIDTH,
        "gate_conservative_floor_threshold": CONSERVATIVE_FLOOR_THRESHOLD,
        "gate_summary": gate_summary,
        "mixed_solution_methods": methods,
        "exact_gate_rows": exact_gate_rows,
        "gate_passed_cells": len(promotable),
        "quarantined_low_security_floor_cells": len(low_floor),
        "underpowered_min_games_cells": len(underpowered),
        "precision_target_not_met_cells": len(precision_blocked),
        "min_games_per_population_cell_observed": min(min_games) if min_games else None,
        "max_ci_width_observed": max(finite_widths) if finite_widths else None,
        "worst_conservative_pure_security_lcb": min(finite_lcbs) if finite_lcbs else None,
        "best_conservative_pure_security_lcb": max(finite_lcbs) if finite_lcbs else None,
        "robustness_read": "no_promotable_pooling_cut" if not promotable else "pooling_cut_promoted_candidate",
        "scopes": [
            {"scope": scope, "value": value, "source_rows": len(rows)} for scope, value, rows in evaluations
        ],
    }
    dump_json(DATA / "rev0073_population_pool_robustness_summary.json", summary)
    print(json.dumps(summary, indent=2, sort_keys=True))
    if promotable:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
