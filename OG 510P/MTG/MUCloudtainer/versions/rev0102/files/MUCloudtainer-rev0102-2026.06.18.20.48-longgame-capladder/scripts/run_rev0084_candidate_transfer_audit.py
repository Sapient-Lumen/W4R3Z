#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path
from typing import Mapping, Sequence

ROOT = Path(__file__).resolve().parents[1]
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT))

from src.muc5.counter_response import GUARDED_COUNTER_AXIS
from src.muc5.cpp_rollout import (
    finalize_cpp_shadow_rollout,
    prepare_cpp_shadow_rollout,
    run_cpp_shadow_outcome_rows,
    sample_prepared_cpp_shadow_rollout,
    sample_sequence_evenly,
)
from src.muc5.payoff import aggregate_payoff_rows, write_csv
from src.muc5.population_candidate_transfer import (
    candidate_transfer_arms,
    paired_candidate_delta_rows,
    paired_candidate_transfer_specs,
    summarize_candidate_transfer_rows,
    transfer_context_summary_rows,
)
from src.muc5.population_counterprobe import REPAIR_COUNTER_AXIS
from src.muc5.terminal_clean import mark_terminal_clean_rows, summarize_terminal_clean_rows
from src.muc5.terminal_decomposition import sample_transition_rows
from src.muc5.terminal_mechanisms import to_float, to_int
from src.muc5.threat_response import CLOSURE_THREAT_AXIS, annotate_threat_response_rows, threat_response_mechanism_rows, threat_response_summary_rows

REV = "rev0084"
CODENAME = "holdouttransfer-candidatequarantine"
DATA = ROOT / "data"
TERMINAL_MAX_DECISIONS = 900
THRESHOLD = 0.50
TRANSFER_REPS = 2
HOLDOUT_REPS = 24
TRANSFER_BASE_SEED = 8484000
HOLDOUT_BASE_SEED = 8489000
MAX_CPP_SHADOW_SPECS = 96
MAX_CPP_SHADOW_RECORDS = 14000


def read_csv(path: Path) -> list[dict[str, object]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


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


def axis_summary_rows(rows: Sequence[Mapping[str, object]], axis: str) -> list[dict[str, object]]:
    groups: dict[str, list[Mapping[str, object]]] = {}
    for row in rows:
        if str(row.get("complete_pair", "")).lower() != "true" and row.get("complete_pair") is not True:
            continue
        groups.setdefault(str(row.get(axis, "")), []).append(row)
    out: list[dict[str, object]] = []
    for value, group in sorted(groups.items()):
        summary = summarize_candidate_transfer_rows(group).as_dict()
        out.append({"axis": axis, "value": value, **summary})
    return out


def _selected_cell_from_rev0083() -> dict[str, object]:
    prior = json.loads((DATA / "rev0083_deficient_cell_counterprobe_summary.json").read_text(encoding="utf-8"))
    selected = prior.get("selected_cell", {}) if isinstance(prior.get("selected_cell", {}), dict) else {}
    if selected.get("size_axis") != "counter40_vs_threat40" or str(selected.get("starting_life")) != "20" or selected.get("threat_policy_axis") != CLOSURE_THREAT_AXIS:
        raise SystemExit(f"rev0084 expected rev0083 selected cell to remain the life-20 40-vs-40 closure cell, got {selected}")
    return selected


def main() -> None:
    DATA.mkdir(exist_ok=True)
    selected = _selected_cell_from_rev0083()

    transfer_arms = candidate_transfer_arms(DATA / "seed_decks.json")
    transfer_specs, transfer_meta = paired_candidate_transfer_specs(
        transfer_arms,
        simulator_revision=REV,
        life_totals=(20, 40),
        reps=TRANSFER_REPS,
        base_seed=TRANSFER_BASE_SEED,
        max_decisions=TERMINAL_MAX_DECISIONS,
        design_label="adaptive_candidate_transfer_seedpaired",
        game_prefix="x",
    )

    holdout_arms = candidate_transfer_arms(
        DATA / "seed_decks.json",
        threat_axes=(CLOSURE_THREAT_AXIS,),
        size_axes=("counter40_vs_threat40",),
    )
    holdout_specs, holdout_meta = paired_candidate_transfer_specs(
        holdout_arms,
        simulator_revision=REV,
        life_totals=(20,),
        reps=HOLDOUT_REPS,
        base_seed=HOLDOUT_BASE_SEED,
        max_decisions=TERMINAL_MAX_DECISIONS,
        design_label="selected_cell_seed_disjoint_holdout",
        game_prefix="h",
    )

    specs = tuple(transfer_specs) + tuple(holdout_specs)
    meta = {**transfer_meta, **holdout_meta}
    outcome_rows_raw, python_errors = run_cpp_shadow_outcome_rows(specs, revision=REV)
    game_rows = mark_terminal_clean_rows(list(outcome_rows_raw), revision=REV, max_decisions=TERMINAL_MAX_DECISIONS, strict=False)
    annotated_rows = annotate_threat_response_rows(game_rows, meta)
    for row in annotated_rows:
        row["source_revision"] = REV
        row["broad_pool_eligible"] = False
        row["candidate_pool_eligible"] = False
        row["adaptive_selection_source"] = "rev0083_deficient_cell_counterprobe"
        row["adaptive_selection_reason"] = "candidate created from selected deficient-cell repair attempt; transfer audit only"
    terminal_summary = summarize_terminal_clean_rows(annotated_rows, revision=REV, max_decisions=TERMINAL_MAX_DECISIONS)
    terminal_payload = terminal_summary.as_dict()

    arm_summary = [dict(row, source_revision=REV) for row in threat_response_summary_rows(annotated_rows)]
    aggregate_rows = aggregate_payoff_rows(annotated_rows)
    mechanism_rows = threat_response_mechanism_rows(annotated_rows)
    deltas = paired_candidate_delta_rows(annotated_rows)
    complete_deltas = [row for row in deltas if str(row.get("complete_pair", "")).lower() == "true" or row.get("complete_pair") is True]
    context_rows = transfer_context_summary_rows(deltas)
    axis_rows = axis_summary_rows(deltas, "sampling_design") + axis_summary_rows(deltas, "threat_policy_axis") + axis_summary_rows(deltas, "size_axis") + axis_summary_rows(deltas, "starting_life")

    overall = summarize_candidate_transfer_rows(deltas)
    holdout_rows = [row for row in deltas if row.get("sampling_design") == "selected_cell_seed_disjoint_holdout"]
    transfer_rows = [row for row in deltas if row.get("sampling_design") == "adaptive_candidate_transfer_seedpaired"]
    holdout_summary = summarize_candidate_transfer_rows(holdout_rows)
    transfer_summary = summarize_candidate_transfer_rows(transfer_rows)

    negative_contexts = [row for row in context_rows if bool(row.get("candidate_negative_transfer_detected"))]
    dominance_contexts = [row for row in context_rows if bool(row.get("candidate_dominates_pairwise"))]
    mixed_contexts = [row for row in context_rows if str(row.get("status", "")).startswith("candidate_quarantined")]

    shadow_specs = sample_sequence_evenly(specs, max_items=MAX_CPP_SHADOW_SPECS)
    prepared = prepare_cpp_shadow_rollout(shadow_specs, revision=REV)
    raw_transition_events = len(prepared.transition_rows)
    sampled_prepared = sample_prepared_cpp_shadow_rollout(prepared, max_records=MAX_CPP_SHADOW_RECORDS)
    cpp_summary, cpp_transition_rows = finalize_cpp_shadow_rollout(sampled_prepared)

    write_csv(DATA / "rev0084_candidate_transfer_games.csv", annotated_rows)
    write_csv(DATA / "rev0084_candidate_transfer_arm_summary.csv", arm_summary)
    write_csv(DATA / "rev0084_candidate_transfer_aggregate.csv", aggregate_rows)
    write_csv(DATA / "rev0084_candidate_transfer_mechanisms.csv", mechanism_rows)
    write_union_csv(DATA / "rev0084_candidate_transfer_paired_deltas.csv", deltas)
    write_union_csv(DATA / "rev0084_candidate_transfer_context_summary.csv", context_rows)
    write_union_csv(DATA / "rev0084_candidate_transfer_axis_summary.csv", axis_rows)
    write_union_csv(DATA / "rev0084_candidate_transfer_cpp_transition_sample.csv", sample_transition_rows(cpp_transition_rows, limit=180))

    payload = {
        "revision": REV,
        "codename": CODENAME,
        "audit_focus": "seed-disjoint holdout and transfer audit for the rev0083 low-life stabilizer candidate before it can enter any broad counter population",
        "selected_cell": selected,
        "candidate_axis": REPAIR_COUNTER_AXIS,
        "baseline_axis": GUARDED_COUNTER_AXIS,
        "transfer_reps": TRANSFER_REPS,
        "holdout_reps": HOLDOUT_REPS,
        "specs": len(specs),
        "games": len(annotated_rows),
        "paired_delta_rows": len(deltas),
        "complete_pairs": len(complete_deltas),
        "arm_summary_rows": len(arm_summary),
        "context_summary_rows": len(context_rows),
        "python_errors": len(python_errors),
        "terminal_summary": terminal_payload,
        "cpp_shadow_checked_events": cpp_summary.supported_events,
        "cpp_shadow_mismatches": cpp_summary.mismatches,
        "cpp_shadow_skipped_events": cpp_summary.skipped_events,
        "cpp_shadow_python_errors": cpp_summary.python_errors,
        "raw_transition_events_from_shadow_sample": raw_transition_events,
        "overall_summary": overall.as_dict(),
        "holdout_summary": holdout_summary.as_dict(),
        "transfer_summary": transfer_summary.as_dict(),
        "negative_transfer_contexts": len(negative_contexts),
        "dominance_contexts": len(dominance_contexts),
        "mixed_or_negative_contexts": len(mixed_contexts),
        "candidate_broad_pool_eligible": False,
        "candidate_pool_eligible": False,
        "status": (
            "candidate_quarantined_transfer_or_holdout_risk"
            if (overall.candidate_negative_transfer_detected or holdout_summary.candidate_negative_transfer_detected or not overall.candidate_dominates_pairwise)
            else "candidate_transfer_dominates_guard_but_requires_preregistered_complete_panel"
        ),
        "read": (
            "The rev0083 stabilizer remains an adaptive targeted probe, not a broad counter-population member. "
            "Seed-paired holdout/transfer evidence must dominate the guard before any future promotion path may include it."
        ),
    }
    dump_json(DATA / "rev0084_candidate_transfer_summary.json", payload)
    print(json.dumps(payload, indent=2, sort_keys=True))

    expected_transfer_specs = 2 * 3 * 3 * 2 * 2 * 2 * TRANSFER_REPS
    expected_holdout_specs = 2 * 1 * 1 * 1 * 2 * 2 * HOLDOUT_REPS
    if len(transfer_specs) != expected_transfer_specs or len(holdout_specs) != expected_holdout_specs:
        raise SystemExit(f"unexpected spec counts: transfer={len(transfer_specs)} holdout={len(holdout_specs)}")
    if len(python_errors) != 0 or terminal_summary.truncation_rows != 0:
        raise SystemExit("candidate transfer audit produced Python errors or truncations")
    if overall.pairs != len(complete_deltas) or len(complete_deltas) != (len(specs) // 2):
        raise SystemExit("paired delta rows do not cover every guard/stabilizer pair")
    if cpp_summary.mismatches != 0 or cpp_summary.python_errors != 0:
        raise SystemExit("candidate transfer C++ shadow sample mismatch or Python error")
    if not all(row.get("broad_pool_eligible") is False for row in annotated_rows):
        raise SystemExit("candidate transfer rows must remain excluded from broad promotion pools")


if __name__ == "__main__":
    main()
