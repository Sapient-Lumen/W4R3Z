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
    aggregate_population_summary_rows,
    population_precision_gate_rows,
    summarize_population_precision_gate,
)
from src.muc5.population_sampling import (  # noqa: E402
    adaptive_pooling_guard,
    annotate_sampling_frame_rows,
    global_pool_source_rows,
    sampling_frame_summary_rows,
)
from src.muc5.terminal_mechanisms import to_float  # noqa: E402

REV = "rev0077"
CODENAME = "adaptivepooling-leakguard"
DATA = ROOT / "data"
ROW_POLICIES = tuple(axis for axis, _agent, _note in COUNTER_POPULATION)
COLUMN_POLICIES = tuple(axis for axis, _agent, _note in THREAT_POPULATION)
MIN_GAMES_PER_CELL = 24
MAX_CI_WIDTH = 0.60
CONSERVATIVE_FLOOR_THRESHOLD = 0.50

SUMMARY_SOURCES = (
    ("rev0069", DATA / "rev0069_population_frontier_arm_summary.csv"),
    ("rev0070", DATA / "rev0070_population_precision_arm_summary.csv"),
    ("rev0075", DATA / "rev0075_stratum_challenge_arm_summary.csv"),
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
            if key not in seen:
                seen.add(str(key))
                fieldnames.append(str(key))
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


def evaluate_pool(rows: Sequence[Mapping[str, object]], *, pool_label: str, context_axes: tuple[str, ...] = ()) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    tagged = []
    for row in rows:
        item = dict(row)
        item["pool_label"] = pool_label
        tagged.append(item)
    pooled = aggregate_population_summary_rows(tagged, context_axes=context_axes)
    gate = population_precision_gate_rows(
        pooled,
        row_policies=ROW_POLICIES,
        column_policies=COLUMN_POLICIES,
        context_axes=context_axes,
        min_games_per_cell=MIN_GAMES_PER_CELL,
        max_ci_width=MAX_CI_WIDTH,
        conservative_floor_threshold=CONSERVATIVE_FLOOR_THRESHOLD,
    )
    for collection in (pooled, gate):
        for row in collection:
            row["pool_label"] = pool_label
            row["context_axes"] = ";".join(context_axes) if context_axes else "<global>"
    return pooled, gate


def _first_finite(rows: Sequence[Mapping[str, object]], key: str) -> float | None:
    values = [to_float(row.get(key), float("nan")) for row in rows]
    values = [value for value in values if value == value]
    return values[0] if values else None


def main() -> None:
    all_summary_rows: list[dict[str, object]] = []
    source_counts: list[dict[str, object]] = []
    for revision, path in SUMMARY_SOURCES:
        rows = with_source_revision(read_csv(path), revision)
        all_summary_rows.extend(rows)
        source_counts.append({"source_revision": revision, "summary_rows": len(rows), "summary_game_rows": sum(int(row.get("games", 0)) for row in rows)})

    annotated = annotate_sampling_frame_rows(all_summary_rows)
    frame_rows = sampling_frame_summary_rows(annotated)
    guard = adaptive_pooling_guard(annotated)
    eligible = global_pool_source_rows(annotated)
    ineligible = [row for row in annotated if row.get("global_pool_eligible") is not True]

    eligible_pooled, eligible_gate = evaluate_pool(eligible, pool_label="eligible_complete_panels_only", context_axes=())
    naive_pooled, naive_gate = evaluate_pool(annotated, pool_label="naive_includes_adaptive_challenge", context_axes=())
    life_eligible_pooled, life_eligible_gate = evaluate_pool(eligible, pool_label="eligible_complete_panels_only_by_life", context_axes=("starting_life",))
    life_naive_pooled, life_naive_gate = evaluate_pool(annotated, pool_label="naive_includes_adaptive_challenge_by_life", context_axes=("starting_life",))

    comparison_rows: list[dict[str, object]] = []
    for label, gate_rows in (
        ("eligible_complete_panels_only", eligible_gate),
        ("naive_includes_adaptive_challenge", naive_gate),
        ("eligible_complete_panels_only_by_life", life_eligible_gate),
        ("naive_includes_adaptive_challenge_by_life", life_naive_gate),
    ):
        summary = summarize_population_precision_gate(gate_rows)
        comparison_rows.append(
            {
                "pool_label": label,
                "gate_rows": len(gate_rows),
                "gate_passed_cells": summary.get("gate_passed_cells"),
                "status_counts": json.dumps(summary.get("status_counts", {}), sort_keys=True),
                "best_conservative_pure_security_lcb": summary.get("best_conservative_pure_security_lcb"),
                "worst_conservative_pure_security_lcb": summary.get("worst_conservative_pure_security_lcb"),
                "max_ci_width_observed": summary.get("max_ci_width_observed"),
                "min_games_per_observed_cell_min": min(int(row.get("min_games_per_observed_cell", 0)) for row in gate_rows) if gate_rows else None,
            }
        )

    eligible_lcb = _first_finite(eligible_gate, "conservative_pure_security_lcb")
    naive_lcb = _first_finite(naive_gate, "conservative_pure_security_lcb")
    lcb_delta = None if eligible_lcb is None or naive_lcb is None else naive_lcb - eligible_lcb
    eligible_mean_floor = _first_finite(eligible_gate, "mean_pure_security_value")
    naive_mean_floor = _first_finite(naive_gate, "mean_pure_security_value")
    mean_delta = None if eligible_mean_floor is None or naive_mean_floor is None else naive_mean_floor - eligible_mean_floor

    write_union_csv(DATA / "rev0077_sampling_frame_summary.csv", frame_rows)
    write_union_csv(DATA / "rev0077_population_pool_eligible_arm_summary.csv", eligible_pooled)
    write_union_csv(DATA / "rev0077_population_pool_eligible_gate.csv", eligible_gate)
    write_union_csv(DATA / "rev0077_population_pool_naive_adaptive_gate.csv", naive_gate)
    write_union_csv(DATA / "rev0077_population_pool_life_gate_comparison.csv", life_eligible_gate + life_naive_gate)
    write_union_csv(DATA / "rev0077_population_pool_guard_comparison.csv", comparison_rows)

    summary = {
        "revision": REV,
        "codename": CODENAME,
        "audit_focus": "prevent adaptive targeted stratum-challenge evidence from silently contaminating broad population-pool promotion gates",
        "source_counts": source_counts,
        "sampling_guard": guard,
        "summary_rows_total": len(annotated),
        "summary_rows_global_pool_eligible": len(eligible),
        "summary_rows_excluded_from_global_pool": len(ineligible),
        "eligible_global_gate_summary": summarize_population_precision_gate(eligible_gate),
        "naive_adaptive_global_gate_summary": summarize_population_precision_gate(naive_gate),
        "eligible_by_life_gate_summary": summarize_population_precision_gate(life_eligible_gate),
        "naive_by_life_gate_summary": summarize_population_precision_gate(life_naive_gate),
        "naive_minus_eligible_global_lcb_delta": lcb_delta,
        "naive_minus_eligible_global_mean_floor_delta": mean_delta,
        "eligible_global_gate_rows": len(eligible_gate),
        "naive_global_gate_rows": len(naive_gate),
        "guarded_read": "rev0075 targeted challenge remains valid for selected strata but is excluded from broad pooled promotion evidence",
        "risk_quantified": "including adaptive challenge rows would raise the broad global conservative LCB even though it still would not promote",
    }
    dump_json(DATA / "rev0077_adaptive_pooling_guard_summary.json", summary)
    print(json.dumps(summary, indent=2, sort_keys=True))

    if not guard.get("global_pool_guard_passed"):
        raise SystemExit("adaptive pooling guard failed")
    if len(eligible) != 72 or len(ineligible) != 18:
        raise SystemExit("unexpected eligible/ineligible summary-row split")
    if summarize_population_precision_gate(eligible_gate).get("gate_passed_cells") != 0:
        raise SystemExit("eligible broad population pool unexpectedly promoted")
    if summarize_population_precision_gate(naive_gate).get("gate_passed_cells") != 0:
        raise SystemExit("naive adaptive pool unexpectedly promoted; inspect selection contamination")
    if lcb_delta is None or lcb_delta <= 0.05:
        raise SystemExit("adaptive challenge did not measurably perturb the broad global LCB; guard audit may be stale")


if __name__ == "__main__":
    main()
