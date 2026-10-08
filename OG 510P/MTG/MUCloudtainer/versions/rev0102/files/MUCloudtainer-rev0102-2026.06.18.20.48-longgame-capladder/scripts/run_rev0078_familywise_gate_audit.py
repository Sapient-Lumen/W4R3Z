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
    population_familywise_gate_rows,
    population_precision_gate_rows,
    summarize_population_precision_gate,
)
from src.muc5.population_sampling import annotate_sampling_frame_rows, global_pool_source_rows  # noqa: E402
from src.muc5.terminal_mechanisms import to_float  # noqa: E402

REV = "rev0078"
CODENAME = "familywisegate-fallbacksolver"
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


def evaluate(rows: Sequence[Mapping[str, object]], *, label: str, context_axes: tuple[str, ...]) -> tuple[list[dict[str, object]], list[dict[str, object]], list[dict[str, object]]]:
    pooled = aggregate_population_summary_rows(rows, context_axes=context_axes)
    ordinary = population_precision_gate_rows(
        pooled,
        row_policies=ROW_POLICIES,
        column_policies=COLUMN_POLICIES,
        context_axes=context_axes,
        min_games_per_cell=MIN_GAMES_PER_CELL,
        max_ci_width=MAX_CI_WIDTH,
        conservative_floor_threshold=CONSERVATIVE_FLOOR_THRESHOLD,
    )
    familywise = population_familywise_gate_rows(
        pooled,
        row_policies=ROW_POLICIES,
        column_policies=COLUMN_POLICIES,
        context_axes=context_axes,
        min_games_per_cell=MIN_GAMES_PER_CELL,
        max_ci_width=MAX_CI_WIDTH,
        conservative_floor_threshold=CONSERVATIVE_FLOOR_THRESHOLD,
        alpha=FAMILY_ALPHA,
    )
    for row in pooled:
        row["pool_label"] = label
        row["context_axes"] = ";".join(context_axes) if context_axes else "<global>"
    for gate_kind, collection in (("ordinary_per_cell", ordinary), ("familywise_bonferroni", familywise)):
        for row in collection:
            row["pool_label"] = label
            row["gate_kind"] = gate_kind
            row["context_axes"] = ";".join(context_axes) if context_axes else "<global>"
    return pooled, ordinary, familywise


def comparison_rows(label: str, ordinary: Sequence[Mapping[str, object]], familywise: Sequence[Mapping[str, object]]) -> list[dict[str, object]]:
    ordinary_by_context = {tuple(sorted((key, str(value)) for key, value in row.items() if key in {"starting_life"})): row for row in ordinary}
    out: list[dict[str, object]] = []
    for fam in familywise:
        context_key = tuple(sorted((key, str(value)) for key, value in fam.items() if key in {"starting_life"}))
        ord_row = ordinary_by_context.get(context_key, {})
        ordinary_lcb = to_float(ord_row.get("conservative_pure_security_lcb"), float("nan"))
        family_lcb = to_float(fam.get("conservative_pure_security_lcb"), float("nan"))
        ordinary_width = to_float(ord_row.get("max_ci_width_observed"), float("nan"))
        family_width = to_float(fam.get("max_ci_width_observed"), float("nan"))
        out.append(
            {
                "pool_label": label,
                "starting_life": fam.get("starting_life", "<global>"),
                "ordinary_status": ord_row.get("status", ""),
                "familywise_status": fam.get("status", ""),
                "ordinary_gate_passed": ord_row.get("gate_passed", ""),
                "familywise_gate_passed": fam.get("gate_passed", ""),
                "ordinary_conservative_lcb": ordinary_lcb,
                "familywise_conservative_lcb": family_lcb,
                "familywise_minus_ordinary_lcb": family_lcb - ordinary_lcb,
                "ordinary_max_ci_width": ordinary_width,
                "familywise_max_ci_width": family_width,
                "familywise_minus_ordinary_width": family_width - ordinary_width,
                "interval_per_cell_alpha": fam.get("interval_per_cell_alpha", ""),
                "interval_family_cell_count": fam.get("interval_family_cell_count", ""),
            }
        )
    return out


def main() -> None:
    all_rows: list[dict[str, object]] = []
    for revision, path in SUMMARY_SOURCES:
        all_rows.extend(with_source_revision(read_csv(path), revision))
    annotated = annotate_sampling_frame_rows(all_rows)
    eligible = global_pool_source_rows(annotated)

    global_pooled, global_ordinary, global_familywise = evaluate(eligible, label="eligible_complete_panels_only", context_axes=())
    life_pooled, life_ordinary, life_familywise = evaluate(eligible, label="eligible_complete_panels_only_by_life", context_axes=("starting_life",))
    naive_pooled, naive_ordinary, naive_familywise = evaluate(annotated, label="naive_includes_adaptive_challenge", context_axes=())

    comp = (
        comparison_rows("eligible_complete_panels_only", global_ordinary, global_familywise)
        + comparison_rows("eligible_complete_panels_only_by_life", life_ordinary, life_familywise)
        + comparison_rows("naive_includes_adaptive_challenge", naive_ordinary, naive_familywise)
    )

    write_union_csv(DATA / "rev0078_familywise_global_gate.csv", global_familywise)
    write_union_csv(DATA / "rev0078_familywise_life_gate.csv", life_familywise)
    write_union_csv(DATA / "rev0078_familywise_naive_adaptive_gate.csv", naive_familywise)
    write_union_csv(DATA / "rev0078_familywise_gate_comparison.csv", comp)

    global_ord_summary = summarize_population_precision_gate(global_ordinary)
    global_fam_summary = summarize_population_precision_gate(global_familywise)
    life_ord_summary = summarize_population_precision_gate(life_ordinary)
    life_fam_summary = summarize_population_precision_gate(life_familywise)
    naive_ord_summary = summarize_population_precision_gate(naive_ordinary)
    naive_fam_summary = summarize_population_precision_gate(naive_familywise)

    lcb_delta = to_float(global_familywise[0].get("conservative_pure_security_lcb"), float("nan")) - to_float(global_ordinary[0].get("conservative_pure_security_lcb"), float("nan"))
    width_delta = to_float(global_familywise[0].get("max_ci_width_observed"), float("nan")) - to_float(global_ordinary[0].get("max_ci_width_observed"), float("nan"))

    summary = {
        "revision": REV,
        "codename": CODENAME,
        "audit_focus": "matrix-level promotion gates must use simultaneous familywise uncertainty, not only per-cell 95% intervals",
        "source_summary_rows": len(annotated),
        "eligible_summary_rows": len(eligible),
        "eligible_summary_game_rows": sum(int(row.get("games", 0)) for row in eligible),
        "row_policy_count": len(ROW_POLICIES),
        "column_policy_count": len(COLUMN_POLICIES),
        "family_cell_count": len(ROW_POLICIES) * len(COLUMN_POLICIES),
        "family_alpha": FAMILY_ALPHA,
        "per_cell_alpha": FAMILY_ALPHA / float(len(ROW_POLICIES) * len(COLUMN_POLICIES)),
        "ordinary_global_gate_summary": global_ord_summary,
        "familywise_global_gate_summary": global_fam_summary,
        "ordinary_by_life_gate_summary": life_ord_summary,
        "familywise_by_life_gate_summary": life_fam_summary,
        "ordinary_naive_adaptive_gate_summary": naive_ord_summary,
        "familywise_naive_adaptive_gate_summary": naive_fam_summary,
        "familywise_minus_ordinary_global_lcb_delta": lcb_delta,
        "familywise_minus_ordinary_global_width_delta": width_delta,
        "global_gate_rows": len(global_familywise),
        "life_gate_rows": len(life_familywise),
        "naive_gate_rows": len(naive_familywise),
        "comparison_rows": len(comp),
        "read": "familywise adjustment strengthens quarantine; public_counter_guard remains below the conservative floor under eligible-only broad pooling",
    }
    dump_json(DATA / "rev0078_familywise_gate_summary.json", summary)
    print(json.dumps(summary, indent=2, sort_keys=True))

    if global_fam_summary.get("gate_passed_cells") != 0:
        raise SystemExit("familywise eligible broad pool unexpectedly promoted")
    if naive_fam_summary.get("gate_passed_cells") != 0:
        raise SystemExit("familywise naive adaptive pool unexpectedly promoted")
    if not (lcb_delta < -0.02 and width_delta > 0.05):
        raise SystemExit("familywise gate did not materially tighten uncertainty relative to ordinary intervals")
    if life_fam_summary.get("status_counts", {}).get("quarantined_low_security_floor") != 2:
        raise SystemExit("familywise life gate should quarantine both life contexts")


if __name__ == "__main__":
    main()
