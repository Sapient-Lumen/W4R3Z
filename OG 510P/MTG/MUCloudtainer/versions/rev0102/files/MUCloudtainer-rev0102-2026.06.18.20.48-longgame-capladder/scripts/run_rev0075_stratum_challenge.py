#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path
from typing import Mapping, Sequence

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.muc5.counter_response import GUARDED_COUNTER_AXIS
from src.muc5.cpp_rollout import finalize_cpp_shadow_rollout, prepare_cpp_shadow_rollout, sample_prepared_cpp_shadow_rollout
from src.muc5.payoff import aggregate_payoff_rows, write_csv
from src.muc5.population_frontier import (
    COUNTER_POPULATION,
    THREAT_POPULATION,
    aggregate_population_summary_rows,
    counter_threat_population_arms,
    population_precision_gate_rows,
    security_rows_from_cells,
    population_cells_from_summary_rows,
    summarize_population_precision_gate,
)
from src.muc5.population_stratum_challenge import select_underpowered_candidate_cells, summarize_challenge_gate
from src.muc5.terminal_clean import mark_terminal_clean_rows, summarize_terminal_clean_rows
from src.muc5.terminal_decomposition import sample_transition_rows
from src.muc5.threat_response import (
    annotate_threat_response_rows,
    threat_response_mechanism_rows,
    threat_response_stress_specs,
    threat_response_summary_rows,
)

REV = "rev0075"
CODENAME = "stratumchallenge-boolgate"
DATA = ROOT / "data"
REPS = 4
BASE_SEED = 7575000
TERMINAL_MAX_DECISIONS = 900
MAX_CPP_SHADOW_RECORDS = 30000
MIN_GAMES_PER_CELL = 16
MAX_CI_WIDTH = 0.60
CONSERVATIVE_FLOOR_THRESHOLD = 0.50
MIN_MEAN_FLOOR_FOR_CHALLENGE = 0.50


def read_csv(path: Path) -> list[dict[str, object]]:
    if not path.exists():
        return []
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


def selected_context(row: Mapping[str, object], selected: set[tuple[str, int]]) -> bool:
    try:
        life = int(row.get("starting_life", 0) or 0)
    except (TypeError, ValueError):
        return False
    return (str(row.get("size_axis", "")), life) in selected


def evaluate_pooled(
    rows: Sequence[Mapping[str, object]],
    *,
    selected: set[tuple[str, int]],
    stage: str,
) -> tuple[list[dict[str, object]], list[dict[str, object]], list[dict[str, object]]]:
    counter_axes = tuple(axis for axis, _agent, _note in COUNTER_POPULATION)
    threat_axes = tuple(axis for axis, _agent, _note in THREAT_POPULATION)
    pooled = aggregate_population_summary_rows(rows, context_axes=("size_axis", "starting_life"))
    pooled = [row for row in pooled if selected_context(row, selected)]
    cells = population_cells_from_summary_rows(
        pooled,
        context_axes=("size_axis", "starting_life"),
        row_policies=counter_axes,
        column_policies=threat_axes,
    )
    security = security_rows_from_cells(cells, iterations=40000)
    gate = population_precision_gate_rows(
        pooled,
        context_axes=("size_axis", "starting_life"),
        row_policies=counter_axes,
        column_policies=threat_axes,
        min_games_per_cell=MIN_GAMES_PER_CELL,
        max_ci_width=MAX_CI_WIDTH,
        conservative_floor_threshold=CONSERVATIVE_FLOOR_THRESHOLD,
        iterations=40000,
    )
    for collection in (pooled, security, gate):
        for row in collection:
            row["challenge_stage"] = stage
            try:
                life = int(row.get("starting_life", 0) or 0)
            except (TypeError, ValueError):
                life = 0
            row["targeted_for_stress"] = (str(row.get("size_axis", "")), life) in selected
    return pooled, security, gate


def comparison_rows(pre_gate: Sequence[Mapping[str, object]], post_gate: Sequence[Mapping[str, object]]) -> list[dict[str, object]]:
    pre = {(str(row.get("size_axis", "")), str(row.get("starting_life", ""))): dict(row) for row in pre_gate}
    post = {(str(row.get("size_axis", "")), str(row.get("starting_life", ""))): dict(row) for row in post_gate}
    rows: list[dict[str, object]] = []
    for key in sorted(set(pre) | set(post)):
        a = pre.get(key, {})
        b = post.get(key, {})
        rows.append(
            {
                "size_axis": key[0],
                "starting_life": key[1],
                "pre_status": a.get("status", ""),
                "post_status": b.get("status", ""),
                "pre_min_games": a.get("min_games_per_observed_cell", ""),
                "post_min_games": b.get("min_games_per_observed_cell", ""),
                "pre_mean_pure_security_value": a.get("mean_pure_security_value", ""),
                "post_mean_pure_security_value": b.get("mean_pure_security_value", ""),
                "pre_conservative_lcb": a.get("conservative_pure_security_lcb", ""),
                "post_conservative_lcb": b.get("conservative_pure_security_lcb", ""),
                "pre_max_ci_width": a.get("max_ci_width_observed", ""),
                "post_max_ci_width": b.get("max_ci_width_observed", ""),
                "post_blocking_reason": b.get("blocking_reason", ""),
            }
        )
    return rows


def main() -> None:
    DATA.mkdir(exist_ok=True)
    fine_gate = read_csv(DATA / "rev0074_population_raw_fine_gate.csv")
    selected_cells = select_underpowered_candidate_cells(
        fine_gate,
        min_mean_floor=MIN_MEAN_FLOOR_FOR_CHALLENGE,
        required_best_policy=GUARDED_COUNTER_AXIS,
    )
    if not selected_cells:
        raise SystemExit("no underpowered candidate strata selected")
    selected_set = set(selected_cells)

    arms = counter_threat_population_arms(DATA / "seed_decks.json")
    specs, meta = threat_response_stress_specs(
        arms,
        candidate_cells=selected_cells,
        simulator_revision=REV,
        reps=REPS,
        base_seed=BASE_SEED,
        max_decisions=TERMINAL_MAX_DECISIONS,
    )
    prepared = prepare_cpp_shadow_rollout(specs, revision=REV)
    raw_transition_events = len(prepared.transition_rows)
    shadow_prepared = sample_prepared_cpp_shadow_rollout(prepared, max_records=MAX_CPP_SHADOW_RECORDS)
    cpp_summary, cpp_transition_rows = finalize_cpp_shadow_rollout(shadow_prepared)

    game_rows = mark_terminal_clean_rows(
        list(prepared.game_rows),
        revision=REV,
        max_decisions=TERMINAL_MAX_DECISIONS,
        strict=False,
    )
    annotated_rows = annotate_threat_response_rows(game_rows, meta)
    for row in annotated_rows:
        row["source_revision"] = REV
        row["stress_selected_from"] = "rev0074_population_raw_fine_gate"
        row["stress_selection_rule"] = f"underpowered;mean_floor>={MIN_MEAN_FLOOR_FOR_CHALLENGE};best={GUARDED_COUNTER_AXIS}"
    terminal_summary = summarize_terminal_clean_rows(
        annotated_rows,
        revision=REV,
        max_decisions=TERMINAL_MAX_DECISIONS,
    )
    arm_summary = threat_response_summary_rows(annotated_rows)
    arm_summary = [dict(row, source_revision=REV) for row in arm_summary]
    mechanism_rows = threat_response_mechanism_rows(annotated_rows)
    aggregate = aggregate_payoff_rows(annotated_rows)

    old_rows = with_source_revision(read_csv(DATA / "rev0069_population_frontier_arm_summary.csv"), "rev0069")
    old_rows += with_source_revision(read_csv(DATA / "rev0070_population_precision_arm_summary.csv"), "rev0070")
    combined_rows = old_rows + arm_summary
    pre_pooled, pre_security, pre_gate = evaluate_pooled(old_rows, selected=selected_set, stage="pre_rev0075")
    post_pooled, post_security, post_gate = evaluate_pooled(combined_rows, selected=selected_set, stage="post_rev0075")
    compare = comparison_rows(pre_gate, post_gate)

    write_csv(DATA / "rev0075_stratum_challenge_games.csv", annotated_rows)
    write_csv(DATA / "rev0075_stratum_challenge_aggregate.csv", aggregate)
    write_csv(DATA / "rev0075_stratum_challenge_arm_summary.csv", arm_summary)
    write_csv(DATA / "rev0075_stratum_challenge_mechanisms.csv", mechanism_rows)
    write_csv(DATA / "rev0075_stratum_challenge_cpp_transition_sample.csv", sample_transition_rows(cpp_transition_rows, limit=360))
    write_union_csv(DATA / "rev0075_stratum_challenge_pre_pooled_arm_summary.csv", pre_pooled)
    write_union_csv(DATA / "rev0075_stratum_challenge_post_pooled_arm_summary.csv", post_pooled)
    write_union_csv(DATA / "rev0075_stratum_challenge_pre_security.csv", pre_security)
    write_union_csv(DATA / "rev0075_stratum_challenge_post_security.csv", post_security)
    write_union_csv(DATA / "rev0075_stratum_challenge_pre_gate.csv", pre_gate)
    write_union_csv(DATA / "rev0075_stratum_challenge_post_gate.csv", post_gate)
    write_union_csv(DATA / "rev0075_stratum_challenge_comparison.csv", compare)
    dump_json(DATA / "rev0075_stratum_challenge_selected_cells.json", [
        {"size_axis": axis, "starting_life": life} for axis, life in selected_cells
    ])

    post_summary = summarize_challenge_gate(post_gate)
    precision_summary = summarize_population_precision_gate(post_gate)
    summary = {
        "revision": REV,
        "codename": CODENAME,
        "selected_cells": [{"size_axis": axis, "starting_life": life} for axis, life in selected_cells],
        "selection_source_rows": len(fine_gate),
        "selection_rule": {
            "status": "underpowered_min_games",
            "min_mean_floor": MIN_MEAN_FLOOR_FOR_CHALLENGE,
            "required_best_policy": GUARDED_COUNTER_AXIS,
        },
        "games": len(annotated_rows),
        "arms": len(arms),
        "targeted_specs": len(specs),
        "reps_per_selected_arm_seat_start": REPS,
        "source_population_games_before_rev0075": 144 + 288,
        "pre_gate_summary": summarize_challenge_gate(pre_gate),
        "post_gate_summary": post_summary,
        "precision_gate_summary_after_csv_safe_bool_refactor": precision_summary,
        "gate_min_games_per_cell": MIN_GAMES_PER_CELL,
        "gate_max_ci_width": MAX_CI_WIDTH,
        "gate_conservative_floor_threshold": CONSERVATIVE_FLOOR_THRESHOLD,
        "terminal_clean_summary": terminal_summary.as_dict(),
        "cpp_shadow_summary": cpp_summary.as_dict(),
        "python_errors": len(prepared.python_errors),
        "truncations": int(sum(1 for r in annotated_rows if str(r.get("is_truncation")).lower() in {"true", "1"})),
        "raw_cpp_transition_rows_generated_but_not_shipped": raw_transition_events,
        "cpp_shadow_records_checked": len(shadow_prepared.records),
        "cpp_shadow_record_cap": MAX_CPP_SHADOW_RECORDS,
        "cpp_transition_sample_rows_shipped": min(360, len(cpp_transition_rows)),
        "read": "targeted_high_mean_strata_remain_quarantined" if post_summary["gate_passed_cells"] == 0 else "targeted_high_mean_strata_contains_promotable_candidate",
    }
    dump_json(DATA / "rev0075_stratum_challenge_summary.json", summary)
    print(json.dumps(summary, indent=2, sort_keys=True))
    if summary["python_errors"]:
        raise SystemExit(1)
    if summary["truncations"]:
        raise SystemExit(1)
    if summary["cpp_shadow_summary"].get("mismatches"):
        raise SystemExit(1)
    if post_summary["gate_passed_cells"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
