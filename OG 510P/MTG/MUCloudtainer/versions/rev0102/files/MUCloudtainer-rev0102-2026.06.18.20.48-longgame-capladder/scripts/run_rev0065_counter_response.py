#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path
from typing import Mapping

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.muc5.counter_response import (
    annotate_counter_response_rows,
    claim_quarantine_rows,
    compare_counter_response_by_life,
    counter_response_gate_report,
    counter_response_mechanism_rows,
    counter_response_specs,
    counter_response_stress_specs,
    counter_response_summary_rows,
    rev0065_counter_response_arms,
)
from src.muc5.cpp_rollout import finalize_cpp_shadow_rollout, prepare_cpp_shadow_rollout
from src.muc5.mulligan_ranker import make_mulligan_agent
from src.muc5.payoff import aggregate_payoff_rows, write_csv
from src.muc5.public_agents import make_public_agent
from src.muc5.replay import record_public_decision_trace, replay_public_decision_trace, write_trace_jsonl
from src.muc5.terminal_clean import mark_terminal_clean_rows, summarize_terminal_clean_rows
from src.muc5.terminal_decomposition import sample_transition_rows
from src.muc5.terminal_mechanisms import target_summary_rows
from src.muc5.threat_closure import summarize_threat_closure_features, threat_closure_trace_features_from_spec
from src.muc5.trajectory_forensics import summarize_forensic_rows, trajectory_forensics_from_spec, validate_forensics_against_game_row

REV = "rev0065"
CODENAME = "counterresponse-quarantinegate"
DATA = ROOT / "data"
REPS = 3
STRESS_REPS = 4
TERMINAL_MAX_DECISIONS = 900
BASE_SEED = 6565000
STRESS_BASE_SEED = 6565900
STRESS_CELLS = (
    ("counter40_vs_threat40", 20),
    ("counter60_vs_threat40", 40),
    ("counter60_vs_threat60", 20),
)


def dump_json(path: Path, obj: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def read_csv(path: Path) -> list[dict[str, object]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as f:
        return [dict(r) for r in csv.DictReader(f)]


def _record_replay_samples(specs, count: int = 12):
    agent_cache = {}
    mulligan_cache = {}

    def agent(name: str):
        if name not in agent_cache:
            agent_cache[name] = make_public_agent(name)
        return agent_cache[name]

    def mulligan(name: str):
        if name not in mulligan_cache:
            mulligan_cache[name] = make_mulligan_agent(name)
        return mulligan_cache[name]

    if not specs:
        return [], []
    if len(specs) <= count:
        sample_indices = list(range(len(specs)))
    else:
        sample_indices = sorted({round(i * (len(specs) - 1) / (count - 1)) for i in range(count)})
    traces = []
    results = []
    for idx in sample_indices:
        spec = specs[idx]
        trace = record_public_decision_trace(
            spec.deck0,
            spec.deck1,
            agent(spec.agent0),
            agent(spec.agent1),
            seed=int(spec.seed),
            transition_seed=int(spec.seed),
            agent_seed=int(spec.seed) + 1000003,
            starting_player=int(spec.starting_player),
            starting_life=int(spec.starting_life),
            max_decisions=int(spec.max_decisions),
            mulligan_agents=(mulligan(spec.mulligan0), mulligan(spec.mulligan1)),
        )
        traces.append(trace)
        results.append(replay_public_decision_trace(trace).as_dict())
    return traces, results


def _slim_case(row: Mapping[str, object]) -> dict[str, object]:
    keys = [
        "arm_id",
        "starting_life",
        "seed",
        "target_seat",
        "threat_seat",
        "target_score",
        "threat_score",
        "loss_reason",
        "decisions",
        "size_axis",
        "counter_policy_axis",
        "target_agent",
        "opponent_agent",
        "target_final_life",
        "threat_final_life",
        "target_final_library",
        "threat_final_library",
        "threat_declared_attackers_to_player",
        "threat_declared_attack_draw_cost_total",
        "threat_declared_lethal_attack_actions",
        "threat_pass_attack_actions",
        "threat_last_action_before_loss",
    ]
    return {k: row.get(k, "") for k in keys}


def _run_counter_panel(prefix: str, specs, meta, *, replay_count: int = 0) -> dict[str, object]:
    prepared = prepare_cpp_shadow_rollout(specs, revision=REV)
    cpp_summary, cpp_transition_rows = finalize_cpp_shadow_rollout(prepared)
    game_rows = mark_terminal_clean_rows(
        list(prepared.game_rows),
        revision=REV,
        max_decisions=TERMINAL_MAX_DECISIONS,
        strict=False,
    )
    annotated_rows = annotate_counter_response_rows(game_rows, meta)
    terminal_summary = summarize_terminal_clean_rows(annotated_rows, revision=REV, max_decisions=TERMINAL_MAX_DECISIONS)
    arm_summary = counter_response_summary_rows(annotated_rows)
    mechanism_rows = counter_response_mechanism_rows(annotated_rows)
    life_rollup = target_summary_rows(annotated_rows, group_keys=("starting_life", "counter_policy_axis", "size_axis"))
    aggregate = aggregate_payoff_rows(annotated_rows)
    comparisons = compare_counter_response_by_life(arm_summary)

    replay_traces, replay_results = ([], [])
    if replay_count:
        replay_traces, replay_results = _record_replay_samples(specs, count=replay_count)
        write_trace_jsonl(replay_traces, DATA / f"{prefix}_replay_traces.jsonl")
        dump_json(DATA / f"{prefix}_replay_results.json", replay_results)

    game_by_id = {str(r.get("cpp_shadow_game_id")): r for r in game_rows}
    forensic_rows = []
    closure_feature_rows = []
    forensic_validation_errors = []
    for spec in specs:
        gid_meta = meta[spec.game_id]
        target_seat = int(gid_meta["target_seat"])
        threat_seat = int(gid_meta["threat_seat"])
        forensic = trajectory_forensics_from_spec(spec, target_seat=target_seat)
        forensic.update(gid_meta)
        errors = validate_forensics_against_game_row(forensic, game_by_id.get(spec.game_id, {}))
        if errors:
            forensic_validation_errors.append({"game_id": spec.game_id, "errors": errors})
        forensic_rows.append(forensic)

        closure = threat_closure_trace_features_from_spec(spec, threat_seat=threat_seat, target_seat=target_seat)
        closure.update(gid_meta)
        closure_feature_rows.append(closure)

    forensic_arm_summary = summarize_forensic_rows(forensic_rows, group_keys=("arm_id", "starting_life", "size_axis", "counter_policy_axis"))
    closure_feature_summary = summarize_threat_closure_features(closure_feature_rows, group_keys=("size_axis", "starting_life", "counter_policy_axis", "target_agent"))

    write_csv(DATA / f"{prefix}_games.csv", annotated_rows)
    write_csv(DATA / f"{prefix}_aggregate.csv", aggregate)
    write_csv(DATA / f"{prefix}_arm_summary.csv", arm_summary)
    write_csv(DATA / f"{prefix}_mechanisms.csv", mechanism_rows)
    write_csv(DATA / f"{prefix}_life_rollup.csv", life_rollup)
    write_csv(DATA / f"{prefix}_comparisons.csv", comparisons)
    write_csv(DATA / f"{prefix}_cpp_transition_sample.csv", sample_transition_rows(cpp_transition_rows, limit=240))
    write_csv(DATA / f"{prefix}_forensics.csv", forensic_rows)
    write_csv(DATA / f"{prefix}_forensic_arm_summary.csv", forensic_arm_summary)
    write_csv(DATA / f"{prefix}_features.csv", closure_feature_rows)
    write_csv(DATA / f"{prefix}_feature_summary.csv", closure_feature_summary)

    return {
        "games": len(annotated_rows),
        "rows": annotated_rows,
        "arm_summary_rows": arm_summary,
        "mechanism_rows": mechanism_rows,
        "life_rollup": life_rollup,
        "comparisons": comparisons,
        "closure_feature_summary": closure_feature_summary,
        "closure_feature_rows": closure_feature_rows,
        "forensic_games": len(forensic_rows),
        "forensic_validation_errors": forensic_validation_errors,
        "forensic_validation_error_count": len(forensic_validation_errors),
        "closure_feature_games": len(closure_feature_rows),
        "terminal_clean_summary": terminal_summary.as_dict(),
        "cpp_shadow_summary": cpp_summary.as_dict(),
        "python_errors": len(prepared.python_errors),
        "truncations": int(sum(1 for r in annotated_rows if str(r.get("is_truncation")).lower() in {"true", "1"})),
        "raw_cpp_transition_rows_generated_but_not_shipped": len(cpp_transition_rows),
        "cpp_transition_sample_rows_shipped": min(240, len(cpp_transition_rows)),
        "replay_samples": len(replay_results),
        "replay_passed": int(sum(1 for r in replay_results if r.get("passed") is True)),
    }


def main() -> None:
    DATA.mkdir(exist_ok=True)
    arms = rev0065_counter_response_arms(DATA / "seed_decks.json")
    specs, meta = counter_response_specs(
        arms,
        simulator_revision=REV,
        reps=REPS,
        base_seed=BASE_SEED,
        max_decisions=TERMINAL_MAX_DECISIONS,
    )
    primary = _run_counter_panel("rev0065_counter_response", specs, meta, replay_count=12)

    stress_specs, stress_meta = counter_response_stress_specs(
        arms,
        candidate_cells=STRESS_CELLS,
        simulator_revision=REV,
        reps=STRESS_REPS,
        base_seed=STRESS_BASE_SEED,
        max_decisions=TERMINAL_MAX_DECISIONS,
    )
    stress = _run_counter_panel("rev0065_counter_response_stress", stress_specs, stress_meta, replay_count=0)

    old_closure_comparisons = read_csv(DATA / "rev0064_closure_vs_counter_comparisons.csv")
    quarantine = claim_quarantine_rows(old_closure_comparisons, primary["comparisons"])
    stress_quarantine = claim_quarantine_rows(old_closure_comparisons, stress["comparisons"])
    write_csv(DATA / "rev0065_claim_quarantine.csv", quarantine)
    write_csv(DATA / "rev0065_claim_quarantine_stress.csv", stress_quarantine)
    dump_json(DATA / "rev0065_counter_response_arms.json", [a.as_dict() for a in arms])

    primary_features = list(primary["closure_feature_rows"])
    stress_features = list(stress["closure_feature_rows"])
    all_features = primary_features + stress_features
    guard_rescue_cases = [
        _slim_case(r)
        for r in sorted(all_features, key=lambda r: (str(r.get("size_axis")), int(r.get("starting_life", 0)), int(r.get("seed", 0))))
        if str(r.get("counter_policy_axis")) == "public_counter_guard" and float(r.get("target_score", 0.5)) > 0.5
    ][:60]
    legacy_escape_cases = [
        _slim_case(r)
        for r in sorted(all_features, key=lambda r: (str(r.get("size_axis")), int(r.get("starting_life", 0)), int(r.get("seed", 0))))
        if str(r.get("counter_policy_axis")) == "legacy_cf34_counter_ranker" and float(r.get("target_score", 0.5)) > 0.5
    ][:60]
    write_csv(DATA / "rev0065_counter_guard_rescue_cases.csv", guard_rescue_cases)
    write_csv(DATA / "rev0065_legacy_counter_escape_cases.csv", legacy_escape_cases)

    summary = {
        "revision": REV,
        "codename": CODENAME,
        "purpose": "Counter-response audit: test whether a public counter_guard pilot rescues the counter-wall deck against the guarded threat_closure baseline, stress-test the promising cells on disjoint seeds, and quarantine old counter-wall claims that only held against legacy threat_rush.",
        "reps_per_seat_start_life_arm": REPS,
        "stress_reps_per_seat_start_life_arm": STRESS_REPS,
        "stress_cells": [f"{axis}_life{life}" for axis, life in STRESS_CELLS],
        "base_seed": BASE_SEED,
        "stress_base_seed": STRESS_BASE_SEED,
        "max_decisions": TERMINAL_MAX_DECISIONS,
        "arms": [a.as_dict() for a in arms],
        "primary": {k: v for k, v in primary.items() if k not in {"rows", "closure_feature_rows"}},
        "stress": {k: v for k, v in stress.items() if k not in {"rows", "closure_feature_rows"}},
        "games": int(primary["games"]) + int(stress["games"]),
        "forensic_games": int(primary["forensic_games"]) + int(stress["forensic_games"]),
        "closure_feature_games": int(primary["closure_feature_games"]) + int(stress["closure_feature_games"]),
        "forensic_validation_error_count": int(primary["forensic_validation_error_count"]) + int(stress["forensic_validation_error_count"]),
        "python_errors": int(primary["python_errors"]) + int(stress["python_errors"]),
        "truncations": int(primary["truncations"]) + int(stress["truncations"]),
        "raw_cpp_transition_rows_generated_but_not_shipped": int(primary["raw_cpp_transition_rows_generated_but_not_shipped"]) + int(stress["raw_cpp_transition_rows_generated_but_not_shipped"]),
        "cpp_transition_sample_rows_shipped": int(primary["cpp_transition_sample_rows_shipped"]) + int(stress["cpp_transition_sample_rows_shipped"]),
        "replay_samples": int(primary["replay_samples"]),
        "replay_passed": int(primary["replay_passed"]),
        "claim_quarantine_rows": quarantine,
        "claim_quarantine_stress_rows": stress_quarantine,
        "counter_response_gate": {},
        "notes": [
            "Focus score is the counter-wall target score.  The threat side is fixed to public threat_closure in every primary and stress arm.",
            "counter_guard is public-information-only and does not change simulator rules or existing CF34/ranker behavior.",
            "The stress pass is seed-disjoint and limited to the cells where the primary pass suggested a counter-deck rescue or partial rescue.",
            "The claim quarantine table converts the rev0064 demotion into a live gate: old threat_rush-dependent counter-wall claims must be rerun against threat_closure or a stronger named threat baseline before citation.",
            "Full raw transition CSVs are not shipped; compact C++ transition samples and forensic summaries are retained.",
        ],
    }
    gate = counter_response_gate_report(primary, primary_features, min_games=120)
    for panel_name, panel in (("primary", primary), ("stress", stress)):
        if int(panel["truncations"]) != 0:
            gate["errors"].append(f"{panel_name} panel had truncations")
        if int(panel["python_errors"]) != 0:
            gate["errors"].append(f"{panel_name} panel had python errors")
        cpp = panel.get("cpp_shadow_summary", {})
        if isinstance(cpp, Mapping) and int(cpp.get("mismatches", 0)) != 0:
            gate["errors"].append(f"{panel_name} panel had C++ mismatches")
        if int(panel["forensic_validation_error_count"]) != 0:
            gate["errors"].append(f"{panel_name} forensic rerun mismatched live game rows")
    if int(primary["replay_passed"]) < 10:
        gate["errors"].append("fewer than 10 replay samples passed")
    if not quarantine:
        gate["errors"].append("claim quarantine rows were not produced")
    if not stress_quarantine:
        gate["errors"].append("stress quarantine rows were not produced")
    gate["passed"] = not gate["errors"]
    summary["counter_response_gate"] = gate
    dump_json(DATA / "rev0065_counter_response_summary.json", summary)
    print(json.dumps(summary, indent=2, sort_keys=True))
    if not gate["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
