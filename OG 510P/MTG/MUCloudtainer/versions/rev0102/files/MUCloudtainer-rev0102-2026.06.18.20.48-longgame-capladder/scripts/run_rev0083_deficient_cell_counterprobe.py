#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path
from typing import Mapping, Sequence

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.muc5.counter_response import GUARDED_COUNTER_AXIS, LEGACY_COUNTER_AXIS
from src.muc5.cpp_rollout import (
    finalize_cpp_shadow_rollout,
    prepare_cpp_shadow_rollout,
    run_cpp_shadow_outcome_rows,
    sample_prepared_cpp_shadow_rollout,
    sample_sequence_evenly,
)
from src.muc5.payoff import aggregate_payoff_rows, write_csv
from src.muc5.population_counterprobe import (
    REPAIR_COUNTER_AXIS,
    counterprobe_policy_delta_rows,
    deficient_cell_counterprobe_arms,
    paired_deficient_cell_specs,
    summarize_counterprobe_rescue,
)
from src.muc5.population_frontier import population_column_frontier_rows, population_column_rescue_rows, summarize_population_column_rescue
from src.muc5.terminal_clean import mark_terminal_clean_rows, summarize_terminal_clean_rows
from src.muc5.terminal_decomposition import sample_transition_rows
from src.muc5.terminal_mechanisms import to_float, to_int
from src.muc5.threat_response import annotate_threat_response_rows, threat_response_mechanism_rows, threat_response_summary_rows
from src.muc5.threat_closure import THREAT_CLOSURE_AGENT
from src.muc5.threat_response import CLOSURE_THREAT_AXIS

REV = "rev0083"
CODENAME = "deficientcell-counterprobe"
DATA = ROOT / "data"
REPS = 16
BASE_SEED = 8383000
TERMINAL_MAX_DECISIONS = 900
MAX_CPP_SHADOW_SPECS = 72
MAX_CPP_SHADOW_RECORDS = 12000
THRESHOLD = 0.50
ROW_POLICIES = (LEGACY_COUNTER_AXIS, GUARDED_COUNTER_AXIS, REPAIR_COUNTER_AXIS)
COLUMN_POLICIES = (CLOSURE_THREAT_AXIS,)


def read_csv(path: Path) -> list[dict[str, object]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


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


def paired_seed_balance_rows(rows: Sequence[Mapping[str, object]]) -> list[dict[str, object]]:
    buckets: dict[tuple[str, str, str], set[str]] = {}
    for row in rows:
        key = (str(row.get("target_seat", "")), str(row.get("starting_player", "")), str(row.get("rep", "")))
        buckets.setdefault(key, set()).add(str(row.get("counter_policy_axis", "")))
    out: list[dict[str, object]] = []
    for key, axes in sorted(buckets.items()):
        out.append(
            {
                "target_seat": key[0],
                "starting_player": key[1],
                "rep": key[2],
                "policy_count": len(axes),
                "policies": ";".join(sorted(axes)),
                "complete_policy_triplet": axes == set(ROW_POLICIES),
            }
        )
    return out


def paired_guard_candidate_outcome_rows(rows: Sequence[Mapping[str, object]]) -> list[dict[str, object]]:
    by_key: dict[tuple[str, str, str], dict[str, Mapping[str, object]]] = {}
    for row in rows:
        key = (str(row.get("target_seat", "")), str(row.get("starting_player", "")), str(row.get("rep", "")))
        by_key.setdefault(key, {})[str(row.get("counter_policy_axis", ""))] = row
    out: list[dict[str, object]] = []
    for (target_seat, starting_player, rep), policies in sorted(by_key.items()):
        guard = policies.get(GUARDED_COUNTER_AXIS)
        candidate = policies.get(REPAIR_COUNTER_AXIS)
        if guard is None or candidate is None:
            continue
        guard_score = to_float(guard.get("focus_target_score"), float("nan"))
        candidate_score = to_float(candidate.get("focus_target_score"), float("nan"))
        if candidate_score > guard_score:
            comparison = "candidate_better"
        elif guard_score > candidate_score:
            comparison = "guard_better"
        else:
            comparison = "same_score"
        out.append(
            {
                "target_seat": target_seat,
                "starting_player": starting_player,
                "rep": rep,
                "guard_score": guard_score,
                "candidate_score": candidate_score,
                "candidate_minus_guard_score": candidate_score - guard_score,
                "comparison": comparison,
                "guard_mechanism": guard.get("focus_terminal_mechanism", ""),
                "candidate_mechanism": candidate.get("focus_terminal_mechanism", ""),
                "guard_loss_reason": guard.get("loss_reason", ""),
                "candidate_loss_reason": candidate.get("loss_reason", ""),
            }
        )
    return out


def summarize_paired_outcome_comparison(rows: Sequence[Mapping[str, object]]) -> dict[str, object]:
    counts: dict[str, int] = {}
    for row in rows:
        key = str(row.get("comparison", ""))
        counts[key] = counts.get(key, 0) + 1
    return {
        "rows": len(rows),
        "comparison_counts": counts,
        "candidate_better_rows": counts.get("candidate_better", 0),
        "guard_better_rows": counts.get("guard_better", 0),
        "same_score_rows": counts.get("same_score", 0),
        "candidate_mean_delta": sum(to_float(row.get("candidate_minus_guard_score"), 0.0) for row in rows) / len(rows) if rows else 0.0,
    }


def main() -> None:
    DATA.mkdir(exist_ok=True)
    prior = json.loads((DATA / "rev0082_counterset_rescue_summary.json").read_text(encoding="utf-8"))
    weakest = prior.get("weakest_ucb_case", {}) if isinstance(prior.get("weakest_ucb_case", {}), dict) else {}
    if weakest.get("size_axis") != "counter40_vs_threat40" or str(weakest.get("starting_life")) != "20" or weakest.get("threat_policy_axis") != CLOSURE_THREAT_AXIS:
        raise SystemExit(f"rev0083 counterprobe expected the rev0082 weak cell, got {weakest}")

    arms = deficient_cell_counterprobe_arms(DATA / "seed_decks.json")
    specs, meta = paired_deficient_cell_specs(
        arms,
        simulator_revision=REV,
        reps=REPS,
        base_seed=BASE_SEED,
        max_decisions=TERMINAL_MAX_DECISIONS,
    )
    outcome_rows_raw, python_errors = run_cpp_shadow_outcome_rows(specs, revision=REV)
    game_rows = mark_terminal_clean_rows(list(outcome_rows_raw), revision=REV, max_decisions=TERMINAL_MAX_DECISIONS, strict=False)
    annotated_rows = annotate_threat_response_rows(game_rows, meta)
    for row in annotated_rows:
        row["source_revision"] = REV
        row["sampling_design"] = "targeted_counterprobe_same_seed_grid"
        row["broad_pool_eligible"] = False
        row["adaptive_selection_source"] = "rev0082_counterset_rescue_envelope"
        row["adaptive_selection_reason"] = "only upper-bound-deficient fine cell in current counter set"
    terminal_summary = summarize_terminal_clean_rows(annotated_rows, revision=REV, max_decisions=TERMINAL_MAX_DECISIONS)
    terminal_payload = terminal_summary.as_dict()
    arm_summary = [dict(row, source_revision=REV, sampling_design="targeted_counterprobe_same_seed_grid") for row in threat_response_summary_rows(annotated_rows)]
    aggregate_rows = aggregate_payoff_rows(annotated_rows)
    mechanism_rows = threat_response_mechanism_rows(annotated_rows)
    deltas = counterprobe_policy_delta_rows(arm_summary)
    paired_outcome = paired_guard_candidate_outcome_rows(annotated_rows)
    paired_outcome_summary = summarize_paired_outcome_comparison(paired_outcome)

    frontier = population_column_frontier_rows(
        arm_summary,
        row_policies=ROW_POLICIES,
        column_policies=COLUMN_POLICIES,
        context_axes=("size_axis", "starting_life"),
        min_games_per_cell=48,
        max_ci_width=0.45,
        conservative_floor_threshold=THRESHOLD,
        alpha=0.05,
    )
    rescue = population_column_rescue_rows(frontier, row_policies=ROW_POLICIES, conservative_floor_threshold=THRESHOLD)
    rescue_summary = summarize_population_column_rescue(rescue)
    candidate_summary = summarize_counterprobe_rescue(deltas, threshold=THRESHOLD, candidate_axis=REPAIR_COUNTER_AXIS)
    seed_balance = paired_seed_balance_rows(annotated_rows)

    shadow_specs = sample_sequence_evenly(specs, max_items=MAX_CPP_SHADOW_SPECS)
    prepared = prepare_cpp_shadow_rollout(shadow_specs, revision=REV)
    raw_transition_events = len(prepared.transition_rows)
    sampled_prepared = sample_prepared_cpp_shadow_rollout(prepared, max_records=MAX_CPP_SHADOW_RECORDS)
    cpp_summary, cpp_transition_rows = finalize_cpp_shadow_rollout(sampled_prepared)

    write_csv(DATA / "rev0083_deficient_cell_counterprobe_games.csv", annotated_rows)
    write_csv(DATA / "rev0083_deficient_cell_counterprobe_aggregate.csv", aggregate_rows)
    write_csv(DATA / "rev0083_deficient_cell_counterprobe_arm_summary.csv", arm_summary)
    write_csv(DATA / "rev0083_deficient_cell_counterprobe_mechanisms.csv", mechanism_rows)
    write_union_csv(DATA / "rev0083_deficient_cell_counterprobe_policy_deltas.csv", deltas)
    write_union_csv(DATA / "rev0083_deficient_cell_counterprobe_frontier.csv", frontier)
    write_union_csv(DATA / "rev0083_deficient_cell_counterprobe_rescue.csv", rescue)
    write_union_csv(DATA / "rev0083_deficient_cell_counterprobe_seed_balance.csv", seed_balance)
    write_union_csv(DATA / "rev0083_deficient_cell_counterprobe_paired_outcome_delta.csv", paired_outcome)
    write_union_csv(DATA / "rev0083_deficient_cell_counterprobe_cpp_transition_sample.csv", sample_transition_rows(cpp_transition_rows, limit=180))

    best_old = max(
        [row for row in deltas if row.get("counter_policy_axis") in {LEGACY_COUNTER_AXIS, GUARDED_COUNTER_AXIS}],
        key=lambda row: to_float(row.get("target_mean_score_draw_half"), float("nan")),
    )
    candidate_row = next(row for row in deltas if row.get("counter_policy_axis") == REPAIR_COUNTER_AXIS)
    payload = {
        "revision": REV,
        "codename": CODENAME,
        "audit_focus": "directly challenge the only rev0082 upper-bound-deficient fine cell with a seed-paired counter-policy repair candidate",
        "adaptive_selection_source": "rev0082_counterset_rescue_summary.json",
        "selected_cell": {
            "size_axis": "counter40_vs_threat40",
            "starting_life": 20,
            "threat_policy_axis": CLOSURE_THREAT_AXIS,
            "threat_agent": THREAT_CLOSURE_AGENT,
        },
        "reps": REPS,
        "arms": len(arms),
        "games": len(annotated_rows),
        "specs": len(specs),
        "python_errors": len(python_errors),
        "terminal_summary": terminal_payload,
        "cpp_shadow_checked_events": cpp_summary.supported_events,
        "cpp_shadow_mismatches": cpp_summary.mismatches,
        "cpp_shadow_skipped_events": cpp_summary.skipped_events,
        "cpp_shadow_python_errors": cpp_summary.python_errors,
        "raw_transition_events_from_shadow_sample": raw_transition_events,
        "seed_balance_rows": len(seed_balance),
        "seed_balance_complete_rows": sum(1 for row in seed_balance if str(row.get("complete_policy_triplet", "")).lower() == "true"),
        "frontier_rows": len(frontier),
        "rescue_rows": len(rescue),
        "rescue_summary": rescue_summary,
        "candidate_summary": candidate_summary,
        "paired_outcome_summary": paired_outcome_summary,
        "candidate_axis": REPAIR_COUNTER_AXIS,
        "candidate_mean": candidate_summary.get("candidate_mean"),
        "candidate_lcb": candidate_summary.get("candidate_lcb"),
        "candidate_ucb": candidate_summary.get("candidate_ucb"),
        "best_old_axis": best_old.get("counter_policy_axis"),
        "best_old_mean": best_old.get("target_mean_score_draw_half"),
        "best_old_ucb": best_old.get("target_score_ucb_familywise_probe"),
        "candidate_minus_best_old_mean": to_float(candidate_row.get("target_mean_score_draw_half"), float("nan")) - to_float(best_old.get("target_mean_score_draw_half"), float("nan")),
        "candidate_minus_best_old_ucb": to_float(candidate_row.get("target_score_ucb_familywise_probe"), float("nan")) - to_float(best_old.get("target_score_ucb_familywise_probe"), float("nan")),
        "status": candidate_summary.get("status"),
        "broad_pool_eligible": False,
        "read": (
            "targeted_candidate_repairs_deficient_cell"
            if candidate_summary.get("candidate_certified") is True
            else "targeted_candidate_does_not_certify_deficient_cell; keep out of broad pools and prioritize either stronger counter invention or deck-level counterfactuals"
        ),
    }
    dump_json(DATA / "rev0083_deficient_cell_counterprobe_summary.json", payload)
    print(json.dumps(payload, indent=2, sort_keys=True))

    if len(annotated_rows) != 3 * 2 * 2 * REPS:
        raise SystemExit("counterprobe did not run the expected paired policy grid")
    if len(python_errors) != 0 or terminal_summary.truncation_rows != 0:
        raise SystemExit("counterprobe produced Python errors or truncations")
    if len(seed_balance) != 2 * 2 * REPS or payload["seed_balance_complete_rows"] != len(seed_balance):
        raise SystemExit("paired seed grid is incomplete across counter policies")
    if cpp_summary.mismatches != 0 or cpp_summary.python_errors != 0:
        raise SystemExit("C++ shadow sample mismatch or Python error")
    if len(frontier) != 1 or len(rescue) != 1:
        raise SystemExit("counterprobe frontier/rescue should describe exactly one targeted column")
    if candidate_summary.get("candidate_axis") != REPAIR_COUNTER_AXIS:
        raise SystemExit("candidate summary did not track repair axis")
    if paired_outcome_summary.get("rows") != 2 * 2 * REPS:
        raise SystemExit("paired guard/candidate comparison did not cover the seed grid")


if __name__ == "__main__":
    main()
