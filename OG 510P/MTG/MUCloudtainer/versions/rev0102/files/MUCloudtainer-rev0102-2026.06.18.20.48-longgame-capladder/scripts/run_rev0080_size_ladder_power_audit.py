#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path
from typing import Mapping, Sequence

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.muc5.cpp_rollout import (
    finalize_cpp_shadow_rollout,
    prepare_cpp_shadow_rollout,
    run_cpp_shadow_outcome_rows,
    sample_prepared_cpp_shadow_rollout,
    sample_sequence_evenly,
)
from src.muc5.payoff import aggregate_payoff_rows, write_csv
from src.muc5.population_frontier import (
    COUNTER_POPULATION,
    THREAT_POPULATION,
    aggregate_population_summary_rows,
    counter_threat_population_arms,
    population_hierarchical_familywise_gate_rows,
    summarize_population_hierarchical_gate,
)
from src.muc5.population_power import population_precision_power_ladder_rows, summarize_power_ladder_rows
from src.muc5.population_sampling import annotate_sampling_frame_rows, global_pool_source_rows, sampling_frame_summary_rows
from src.muc5.terminal_clean import mark_terminal_clean_rows, summarize_terminal_clean_rows
from src.muc5.terminal_decomposition import sample_transition_rows
from src.muc5.terminal_mechanisms import to_float, to_int
from src.muc5.threat_response import annotate_threat_response_rows, threat_response_mechanism_rows, threat_response_specs, threat_response_summary_rows

REV = "rev0080"
CODENAME = "sizeladder-poweraudit"
DATA = ROOT / "data"
REPS = 5
BASE_SEED = 8080000
TERMINAL_MAX_DECISIONS = 900
MAX_CPP_SHADOW_SPECS = 96
MAX_CPP_SHADOW_RECORDS = 15000
MIN_GAMES_PER_CELL = 24
MAX_CI_WIDTH = 0.60
CONSERVATIVE_FLOOR_THRESHOLD = 0.50
FAMILY_ALPHA = 0.05
ROW_POLICIES = tuple(axis for axis, _agent, _note in COUNTER_POPULATION)
COLUMN_POLICIES = tuple(axis for axis, _agent, _note in THREAT_POPULATION)
HIERARCHY_LAYERS = (
    ("global", (), True),
    ("by_life", ("starting_life",), True),
    ("by_size", ("size_axis",), True),
    ("by_size_life", ("size_axis", "starting_life"), False),
)
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


def layer_status_counts(gate_rows: Sequence[Mapping[str, object]]) -> dict[str, dict[str, int]]:
    out: dict[str, dict[str, int]] = {}
    for row in gate_rows:
        layer = str(row.get("hierarchy_layer", ""))
        status = str(row.get("status", ""))
        out.setdefault(layer, {})[status] = out.setdefault(layer, {}).get(status, 0) + 1
    return out


def best_finite(rows: Sequence[Mapping[str, object]], field: str) -> float | None:
    values = [to_float(row.get(field), float("nan")) for row in rows]
    values = [value for value in values if value == value]
    return max(values) if values else None


def main() -> None:
    DATA.mkdir(exist_ok=True)
    prior_rows: list[dict[str, object]] = []
    all_known_rows: list[dict[str, object]] = []
    for revision, path in SUMMARY_SOURCES:
        rows = with_source_revision(read_csv(path), revision)
        all_known_rows.extend(rows)
        if revision in {"rev0069", "rev0070"}:
            prior_rows.extend(rows)

    prior_eligible = global_pool_source_rows(annotate_sampling_frame_rows(prior_rows))
    pre_ladder = population_precision_power_ladder_rows(
        prior_eligible,
        row_policies=ROW_POLICIES,
        column_policies=COLUMN_POLICIES,
        layers=HIERARCHY_LAYERS,
        min_games_per_cell=MIN_GAMES_PER_CELL,
        max_ci_width=MAX_CI_WIDTH,
        conservative_floor_threshold=CONSERVATIVE_FLOOR_THRESHOLD,
        alpha=FAMILY_ALPHA,
        iterations=40000,
    )

    arms = counter_threat_population_arms(DATA / "seed_decks.json")
    specs, meta = threat_response_specs(
        arms,
        simulator_revision=REV,
        life_totals=(20, 40),
        reps=REPS,
        base_seed=BASE_SEED,
        max_decisions=TERMINAL_MAX_DECISIONS,
    )
    outcome_rows_raw, python_errors = run_cpp_shadow_outcome_rows(specs, revision=REV)
    game_rows = mark_terminal_clean_rows(list(outcome_rows_raw), revision=REV, max_decisions=TERMINAL_MAX_DECISIONS, strict=False)
    annotated_rows = annotate_threat_response_rows(game_rows, meta)
    annotated_rows = [dict(row, source_revision=REV, sampling_design="complete_population_panel_seed_disjoint_outcome_ladder") for row in annotated_rows]
    terminal_summary = summarize_terminal_clean_rows(annotated_rows, revision=REV, max_decisions=TERMINAL_MAX_DECISIONS)
    arm_summary = [dict(row, source_revision=REV) for row in threat_response_summary_rows(annotated_rows)]
    mechanism_rows = threat_response_mechanism_rows(annotated_rows)
    aggregate_rows = aggregate_payoff_rows(annotated_rows)

    shadow_specs = sample_sequence_evenly(specs, max_items=MAX_CPP_SHADOW_SPECS)
    prepared = prepare_cpp_shadow_rollout(shadow_specs, revision=REV)
    shadow_prepared = sample_prepared_cpp_shadow_rollout(prepared, max_records=MAX_CPP_SHADOW_RECORDS)
    cpp_summary, cpp_transition_rows = finalize_cpp_shadow_rollout(shadow_prepared)

    combined_rows = prior_rows + arm_summary
    combined_eligible = global_pool_source_rows(annotate_sampling_frame_rows(combined_rows))
    post_ladder = population_precision_power_ladder_rows(
        combined_eligible,
        row_policies=ROW_POLICIES,
        column_policies=COLUMN_POLICIES,
        layers=HIERARCHY_LAYERS,
        min_games_per_cell=MIN_GAMES_PER_CELL,
        max_ci_width=MAX_CI_WIDTH,
        conservative_floor_threshold=CONSERVATIVE_FLOOR_THRESHOLD,
        alpha=FAMILY_ALPHA,
        iterations=40000,
    )
    post_gate = population_hierarchical_familywise_gate_rows(
        combined_eligible,
        row_policies=ROW_POLICIES,
        column_policies=COLUMN_POLICIES,
        layers=HIERARCHY_LAYERS,
        min_games_per_cell=MIN_GAMES_PER_CELL,
        max_ci_width=MAX_CI_WIDTH,
        conservative_floor_threshold=CONSERVATIVE_FLOOR_THRESHOLD,
        alpha=FAMILY_ALPHA,
        iterations=40000,
    )
    hierarchy_summary = summarize_population_hierarchical_gate(post_gate)
    pooled_fine = aggregate_population_summary_rows(combined_eligible, context_axes=("size_axis", "starting_life"))
    pooled_size = aggregate_population_summary_rows(combined_eligible, context_axes=("size_axis",))

    sampling_rows = sampling_frame_summary_rows(all_known_rows + arm_summary)
    write_csv(DATA / "rev0080_size_ladder_games.csv", annotated_rows)
    write_csv(DATA / "rev0080_size_ladder_aggregate.csv", aggregate_rows)
    write_csv(DATA / "rev0080_size_ladder_arm_summary.csv", arm_summary)
    write_csv(DATA / "rev0080_size_ladder_mechanisms.csv", mechanism_rows)
    write_union_csv(DATA / "rev0080_size_ladder_cpp_transition_sample.csv", sample_transition_rows(cpp_transition_rows, limit=180))
    write_union_csv(DATA / "rev0080_pre_power_ladder.csv", pre_ladder)
    write_union_csv(DATA / "rev0080_post_power_ladder.csv", post_ladder)
    write_union_csv(DATA / "rev0080_post_hierarchical_familywise_gate.csv", post_gate)
    write_union_csv(DATA / "rev0080_sampling_frame_summary.csv", sampling_rows)
    write_union_csv(DATA / "rev0080_post_pooled_size_summary.csv", pooled_size)
    write_union_csv(DATA / "rev0080_post_pooled_fine_summary.csv", pooled_fine)

    pre_power_summary = summarize_power_ladder_rows(pre_ladder)
    post_power_summary = summarize_power_ladder_rows(post_ladder)
    statuses = layer_status_counts(post_gate)
    gate_passed = int(hierarchy_summary.get("gate_passed_cells", 0))
    summary = {
        "revision": REV,
        "codename": CODENAME,
        "audit_focus": "convert the rev0079 size/fine precision blocker into a seed-disjoint complete-panel outcome ladder and verify promotion remains blocked for evidential reasons rather than missing power",
        "reps": REPS,
        "games": len(annotated_rows),
        "arms": len(arms),
        "specs": len(specs),
        "prior_eligible_summary_rows": len(prior_eligible),
        "prior_eligible_summary_game_rows": sum(to_int(row.get("games"), 0) for row in prior_eligible),
        "post_eligible_summary_rows": len(combined_eligible),
        "post_eligible_summary_game_rows": sum(to_int(row.get("games"), 0) for row in combined_eligible),
        "pre_power_summary": pre_power_summary,
        "post_power_summary": post_power_summary,
        "pre_mandatory_complete_panel_reps_needed": pre_power_summary.get("mandatory_max_complete_panel_reps_needed"),
        "pre_all_layer_complete_panel_reps_needed": pre_power_summary.get("max_complete_panel_reps_needed"),
        "post_mandatory_complete_panel_reps_needed": post_power_summary.get("mandatory_max_complete_panel_reps_needed"),
        "post_all_layer_complete_panel_reps_needed": post_power_summary.get("max_complete_panel_reps_needed"),
        "hierarchy_summary": hierarchy_summary,
        "hierarchy_layer_status_counts": statuses,
        "post_hierarchical_gate_rows": len(post_gate),
        "post_gate_passed_cells": gate_passed,
        "post_mandatory_all_passed": hierarchy_summary.get("mandatory_all_passed"),
        "post_global_familywise_lcb": best_finite([row for row in post_gate if row.get("hierarchy_layer") == "global"], "conservative_pure_security_lcb"),
        "post_best_fine_familywise_lcb": best_finite([row for row in post_gate if row.get("hierarchy_layer") == "by_size_life"], "conservative_pure_security_lcb"),
        "post_worst_fine_familywise_lcb": min(
            [to_float(row.get("conservative_pure_security_lcb"), float("nan")) for row in post_gate if row.get("hierarchy_layer") == "by_size_life" and to_float(row.get("conservative_pure_security_lcb"), float("nan")) == to_float(row.get("conservative_pure_security_lcb"), float("nan"))],
            default=None,
        ),
        "terminal_clean_summary": terminal_summary.as_dict(),
        "python_errors": len(python_errors) + len(prepared.python_errors),
        "truncations": int(sum(1 for row in annotated_rows if str(row.get("is_truncation", "")).lower() in {"true", "1"})),
        "cpp_shadow_summary": cpp_summary.as_dict(),
        "cpp_shadow_specs_checked": len(shadow_specs),
        "cpp_shadow_record_cap": MAX_CPP_SHADOW_RECORDS,
        "cpp_shadow_records_checked": len(shadow_prepared.records),
        "cpp_transition_sample_rows_shipped": min(180, len(cpp_transition_rows)),
        "read": "size_and_fine_precision_blockers_cleared_without_promotion" if gate_passed == 0 else "post_ladder_contains_promotable_candidate",
    }
    dump_json(DATA / "rev0080_size_ladder_power_summary.json", summary)
    print(json.dumps(summary, indent=2, sort_keys=True))

    if summary["python_errors"]:
        raise SystemExit("python errors occurred during outcome or C++ shadow sample")
    if summary["truncations"]:
        raise SystemExit("rev0080 outcome ladder produced truncations")
    if summary["cpp_shadow_summary"].get("mismatches"):
        raise SystemExit("C++ shadow mismatch in rev0080 sample")
    if int(summary["pre_all_layer_complete_panel_reps_needed"]) != REPS:
        raise SystemExit("pre-run power ladder did not identify the preregistered rep count")
    if int(summary["post_all_layer_complete_panel_reps_needed"]) != 0:
        raise SystemExit("post-run power ladder still requires more complete-panel reps for precision/min-games")
    if gate_passed != 0:
        raise SystemExit("population promotion gate unexpectedly passed after size ladder")


if __name__ == "__main__":
    main()
