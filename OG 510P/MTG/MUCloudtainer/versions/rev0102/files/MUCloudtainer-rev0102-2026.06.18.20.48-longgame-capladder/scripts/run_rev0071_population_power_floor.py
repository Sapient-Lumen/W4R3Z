#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.muc5.population_frontier import (
    COUNTER_POPULATION,
    THREAT_POPULATION,
    aggregate_population_summary_rows,
    population_cells_from_summary_rows,
    population_precision_gate_rows,
    security_rows_from_cells,
    summarize_population_precision_gate,
)

REV = "rev0071"
CODENAME = "powerfloor-derivativebridge"
DATA = ROOT / "data"
MIN_GAMES_PER_CELL = 24
MAX_CI_WIDTH = 0.60
CONSERVATIVE_FLOOR_THRESHOLD = 0.50


def read_csv(path: Path) -> list[dict[str, object]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def dump_json(path: Path, obj: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")



def write_union_csv(path: Path, rows: list[dict[str, object]]) -> None:
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
            writer.writerow(row)

def with_source_revision(rows: Iterable[dict[str, object]], revision: str) -> list[dict[str, object]]:
    out: list[dict[str, object]] = []
    for row in rows:
        item = dict(row)
        item["source_revision"] = revision
        out.append(item)
    return out


def evaluate_pool(
    rows: list[dict[str, object]],
    *,
    context_axes: tuple[str, ...],
    label: str,
) -> tuple[list[dict[str, object]], list[dict[str, object]], list[dict[str, object]]]:
    counter_axes = tuple(axis for axis, _agent, _note in COUNTER_POPULATION)
    threat_axes = tuple(axis for axis, _agent, _note in THREAT_POPULATION)
    pooled = aggregate_population_summary_rows(rows, context_axes=context_axes)
    for row in pooled:
        row["pool_label"] = label
        row["context_axes"] = ";".join(context_axes)
    cells = population_cells_from_summary_rows(
        pooled,
        context_axes=context_axes,
        row_policies=counter_axes,
        column_policies=threat_axes,
    )
    security = security_rows_from_cells(cells, iterations=40000)
    gate = population_precision_gate_rows(
        pooled,
        context_axes=context_axes,
        row_policies=counter_axes,
        column_policies=threat_axes,
        min_games_per_cell=MIN_GAMES_PER_CELL,
        max_ci_width=MAX_CI_WIDTH,
        conservative_floor_threshold=CONSERVATIVE_FLOOR_THRESHOLD,
        iterations=40000,
    )
    for row in security:
        row["pool_label"] = label
        row["context_axes"] = ";".join(context_axes)
    for row in gate:
        row["pool_label"] = label
        row["context_axes"] = ";".join(context_axes)
    return pooled, security, gate


def main() -> None:
    DATA.mkdir(exist_ok=True)
    rev0069_rows = with_source_revision(read_csv(DATA / "rev0069_population_frontier_arm_summary.csv"), "rev0069")
    rev0070_rows = with_source_revision(read_csv(DATA / "rev0070_population_precision_arm_summary.csv"), "rev0070")
    source_rows = rev0069_rows + rev0070_rows

    life_pooled, life_security, life_gate = evaluate_pool(
        source_rows,
        context_axes=("starting_life",),
        label="pooled_across_size_by_life",
    )
    all_source_rows = []
    for row in source_rows:
        item = dict(row)
        item["population_scope"] = "all_sizes_and_lives"
        all_source_rows.append(item)
    all_pooled, all_security, all_gate = evaluate_pool(
        all_source_rows,
        context_axes=("population_scope",),
        label="pooled_across_size_and_life",
    )

    pooled_rows = life_pooled + all_pooled
    security_rows = life_security + all_security
    gate_rows = life_gate + all_gate
    gate_summary = summarize_population_precision_gate(gate_rows)

    write_union_csv(DATA / "rev0071_population_power_floor_pooled_arm_summary.csv", pooled_rows)
    write_union_csv(DATA / "rev0071_population_power_floor_security.csv", security_rows)
    write_union_csv(DATA / "rev0071_population_power_floor_gate.csv", gate_rows)

    max_widths = [float(r["max_ci_width_observed"]) for r in gate_rows if r.get("max_ci_width_observed") not in {"", None}]
    lcb_floors = [float(r["conservative_pure_security_lcb"]) for r in gate_rows if r.get("conservative_pure_security_lcb") not in {"", None}]
    min_games = [int(r["min_games_per_observed_cell"]) for r in gate_rows if r.get("min_games_per_observed_cell") not in {"", None, ""}]
    summary = {
        "revision": REV,
        "codename": CODENAME,
        "source_revisions": ["rev0069", "rev0070"],
        "source_arm_summary_rows": len(source_rows),
        "source_population_games": 144 + 288,
        "source_cpp_checked_transitions": 24533 + 30000,
        "pooling_scopes": ["pooled_across_size_by_life", "pooled_across_size_and_life"],
        "pooled_arm_summary_rows": len(pooled_rows),
        "pooled_security_rows": len(security_rows),
        "pooled_gate_rows": len(gate_rows),
        "gate_min_games_per_cell": MIN_GAMES_PER_CELL,
        "gate_max_ci_width": MAX_CI_WIDTH,
        "gate_conservative_floor_threshold": CONSERVATIVE_FLOOR_THRESHOLD,
        "min_games_per_population_cell_observed": min(min_games) if min_games else None,
        "max_games_per_population_cell_observed": max(min_games) if min_games else None,
        "max_ci_width_observed": max(max_widths) if max_widths else None,
        "worst_conservative_pure_security_lcb": min(lcb_floors) if lcb_floors else None,
        "best_conservative_pure_security_lcb": max(lcb_floors) if lcb_floors else None,
        "precision_gate_summary": gate_summary,
        "scope": "pooled_seed_disjoint_reanalysis_for_power_floor_not_size_specific_promotion",
    }
    dump_json(DATA / "rev0071_population_power_floor_summary.json", summary)
    print(json.dumps(summary, indent=2, sort_keys=True))
    if gate_summary.get("gate_passed_cells"):
        raise SystemExit(1)
    if gate_summary.get("status_counts", {}).get("precision_target_not_met", 0):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
