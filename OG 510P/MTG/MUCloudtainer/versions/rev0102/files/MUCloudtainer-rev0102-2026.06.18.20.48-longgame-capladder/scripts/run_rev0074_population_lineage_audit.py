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
    population_cells_from_summary_rows,
    population_precision_gate_rows,
    security_rows_from_cells,
    summarize_population_precision_gate,
)
from src.muc5.population_lineage import (  # noqa: E402
    POPULATION_RAW_SUMMARY_KEYS,
    compare_recomputed_to_source_summaries,
    population_raw_lineage_index,
    raw_population_lineage_checks,
    summarize_population_raw_games,
)

REV = "rev0074"
CODENAME = "rawlineage-strataguard"
DATA = ROOT / "data"
SOURCE_GAME_FILES = (
    ("rev0069", DATA / "rev0069_population_frontier_games.csv", DATA / "rev0069_population_frontier_arm_summary.csv"),
    ("rev0070", DATA / "rev0070_population_precision_games.csv", DATA / "rev0070_population_precision_arm_summary.csv"),
)
FINE_CONTEXT_AXES = ("source_revision", "size_axis", "starting_life")
PLEDGED_BALANCE_CONTEXT_AXES = ("source_revision", "arm_id", "starting_life")
ROW_POLICIES = tuple(axis for axis, _agent, _note in COUNTER_POPULATION)
COLUMN_POLICIES = tuple(axis for axis, _agent, _note in THREAT_POPULATION)


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


def with_source_revision(rows: Sequence[Mapping[str, object]], revision: str) -> list[dict[str, object]]:
    out: list[dict[str, object]] = []
    for row in rows:
        item = dict(row)
        item["source_revision"] = revision
        out.append(item)
    return out


def _float_or_none(value: object) -> float | None:
    if value in {None, ""}:
        return None
    try:
        return float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return None


def main() -> None:
    raw_games: list[dict[str, object]] = []
    source_summary_rows: list[dict[str, object]] = []
    per_source: list[dict[str, object]] = []
    mismatches: list[dict[str, object]] = []

    for revision, games_path, summary_path in SOURCE_GAME_FILES:
        games = with_source_revision(read_csv(games_path), revision)
        source_summary = read_csv(summary_path)
        recomputed = summarize_population_raw_games(games)
        source_mismatches = compare_recomputed_to_source_summaries(recomputed, source_summary)
        for mismatch in source_mismatches:
            item = dict(mismatch)
            item["source_revision"] = revision
            mismatches.append(item)
        raw_games.extend(games)
        source_summary_rows.extend(with_source_revision(source_summary, revision))
        per_source.append(
            {
                "source_revision": revision,
                "raw_games": len(games),
                "source_summary_rows": len(source_summary),
                "recomputed_summary_rows": len(recomputed),
                "summary_mismatch_rows": len(source_mismatches),
            }
        )

    lineage = population_raw_lineage_index(raw_games)
    recomputed_all = summarize_population_raw_games(raw_games)
    # Keep the source revision in the recomputed summary so it can be used as a fine-grained context axis.
    write_union_csv(DATA / "rev0074_population_lineage_index.csv", lineage)
    write_union_csv(DATA / "rev0074_population_raw_recomputed_arm_summary.csv", recomputed_all)
    write_union_csv(DATA / "rev0074_population_source_summary_comparison_mismatches.csv", mismatches)

    raw_checks = raw_population_lineage_checks(raw_games)
    fine_cells = population_cells_from_summary_rows(
        recomputed_all,
        context_axes=FINE_CONTEXT_AXES,
        row_policies=ROW_POLICIES,
        column_policies=COLUMN_POLICIES,
    )
    fine_security = security_rows_from_cells(fine_cells)
    fine_gate = population_precision_gate_rows(
        recomputed_all,
        context_axes=FINE_CONTEXT_AXES,
        row_policies=ROW_POLICIES,
        column_policies=COLUMN_POLICIES,
        min_games_per_cell=12,
        max_ci_width=0.60,
        conservative_floor_threshold=0.50,
    )
    write_union_csv(DATA / "rev0074_population_raw_fine_security.csv", fine_security)
    write_union_csv(DATA / "rev0074_population_raw_fine_gate.csv", fine_gate)

    finite_point_floors = [_float_or_none(row.get("pure_security_value")) for row in fine_security]
    finite_point_floors = [x for x in finite_point_floors if x is not None]
    finite_lcbs = [_float_or_none(row.get("conservative_pure_security_lcb")) for row in fine_gate]
    finite_lcbs = [x for x in finite_lcbs if x is not None]
    gate_summary = summarize_population_precision_gate(fine_gate)
    fine_status_counts = gate_summary.get("status_counts", {}) if isinstance(gate_summary, dict) else {}
    high_point_floor_rows = [row for row in fine_security if (_float_or_none(row.get("pure_security_value")) or 0.0) >= 0.50]
    high_point_floor_min_games = [int(row.get("min_games_per_observed_cell", 0)) for row in high_point_floor_rows]

    summary = {
        "revision": REV,
        "codename": CODENAME,
        "source_revisions": [revision for revision, _games, _summary in SOURCE_GAME_FILES],
        "per_source": per_source,
        "raw_games": len(raw_games),
        "lineage_rows": len(lineage),
        "source_summary_rows": len(source_summary_rows),
        "recomputed_arm_summary_rows": len(recomputed_all),
        "summary_mismatch_rows": len(mismatches),
        "raw_lineage_checks": raw_checks,
        "fine_context_axes": list(FINE_CONTEXT_AXES),
        "fine_population_cells": len(fine_cells),
        "fine_complete_cells": sum(1 for cell in fine_cells if cell.complete),
        "fine_security_rows": len(fine_security),
        "fine_gate_rows": len(fine_gate),
        "fine_gate_summary": gate_summary,
        "fine_gate_status_counts": fine_status_counts,
        "fine_gate_passed_cells": gate_summary.get("gate_passed_cells") if isinstance(gate_summary, dict) else None,
        "fine_underpowered_cells": fine_status_counts.get("underpowered_min_games", 0) if isinstance(fine_status_counts, dict) else None,
        "fine_precision_blocked_cells": fine_status_counts.get("precision_target_not_met", 0) if isinstance(fine_status_counts, dict) else None,
        "fine_low_floor_cells": fine_status_counts.get("quarantined_low_security_floor", 0) if isinstance(fine_status_counts, dict) else None,
        "fine_point_floor_ge_0_50_rows": len(high_point_floor_rows),
        "fine_high_point_floor_max_min_games": max(high_point_floor_min_games) if high_point_floor_min_games else None,
        "fine_worst_point_floor": min(finite_point_floors) if finite_point_floors else None,
        "fine_best_point_floor": max(finite_point_floors) if finite_point_floors else None,
        "fine_worst_conservative_lcb": min(finite_lcbs) if finite_lcbs else None,
        "fine_best_conservative_lcb": max(finite_lcbs) if finite_lcbs else None,
        "lineage_read": "source_qualified_raw_games_match_shipped_summaries_and_fine_strata_do_not_promote",
        "notable_refactor": "source_qualified_game_id added because local cpp_shadow_game_id is not archive-global across source revisions",
    }
    dump_json(DATA / "rev0074_population_lineage_audit_summary.json", summary)
    print(json.dumps(summary, indent=2, sort_keys=True))

    if mismatches:
        raise SystemExit("raw recomputed population summaries did not match source summaries")
    if not bool(raw_checks.get("passed")):
        raise SystemExit("raw population lineage checks failed")
    if int(gate_summary.get("gate_passed_cells", 1)) != 0:
        raise SystemExit("fine raw strata unexpectedly produced a promotable cell")


if __name__ == "__main__":
    main()
