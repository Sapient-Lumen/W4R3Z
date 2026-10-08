#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path
from typing import Mapping

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.muc5.cpp_rollout import finalize_cpp_shadow_rollout, prepare_cpp_shadow_rollout
from src.muc5.mulligan_ranker import make_mulligan_agent
from src.muc5.payoff import aggregate_payoff_rows, write_csv
from src.muc5.public_agents import make_public_agent
from src.muc5.replay import record_public_decision_trace, replay_public_decision_trace, write_trace_jsonl
from src.muc5.terminal_clean import mark_terminal_clean_rows, summarize_terminal_clean_rows
from src.muc5.terminal_decomposition import sample_transition_rows
from src.muc5.terminal_mechanisms import target_summary_rows
from src.muc5.threat_closure import summarize_threat_closure_features, threat_closure_trace_features_from_spec
from src.muc5.threat_response import (
    counter_target_ownership_features_from_spec,
    summarize_counter_ownership_rows,
)
from src.muc5.response_matrix import (
    compare_response_matrix_by_life,
    response_matrix_gate_report,
    response_matrix_specs,
    response_matrix_stress_specs,
    rev0067_response_matrix_arms,
    threat_response_mechanism_rows,
    threat_response_summary_rows,
    annotate_threat_response_rows,
)
from src.muc5.trajectory_forensics import summarize_forensic_rows, trajectory_forensics_from_spec, validate_forensics_against_game_row

REV = "rev0067"
CODENAME = "threatsurgeaudit-responsematrix"
DATA = ROOT / "data"
REPS = 2
STRESS_REPS = 3
DEEP_REPS = 4
TERMINAL_MAX_DECISIONS = 900
BASE_SEED = 6767000
STRESS_BASE_SEED = 6767900
DEEP_BASE_SEED = 6768800
STRESS_CELLS = (
    ("counter40_vs_threat40", 40),
    ("counter60_vs_threat40", 40),
    ("counter60_vs_threat60", 20),
)
DEEP_CELLS = (
    ("counter60_vs_threat60", 20),
    ("counter60_vs_threat60", 40),
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
        "threat_policy_axis",
        "target_agent",
        "opponent_agent",
        "target_final_life",
        "threat_final_life",
        "target_final_library",
        "threat_final_library",
        "threat_declared_attackers_to_player",
        "threat_declared_attackers_to_jace",
        "threat_declared_attack_draw_cost_total",
        "threat_declared_lethal_attack_actions",
        "threat_pass_attack_actions",
        "threat_last_action_before_loss",
        "threat_selected_counter_actions",
        "threat_selected_own_spell_counters",
    ]
    return {k: row.get(k, "") for k in keys}


def _run_matrix_panel(prefix: str, specs, meta, *, replay_count: int = 0) -> dict[str, object]:
    prepared = prepare_cpp_shadow_rollout(specs, revision=REV)
    cpp_summary, cpp_transition_rows = finalize_cpp_shadow_rollout(prepared)
    game_rows = mark_terminal_clean_rows(
        list(prepared.game_rows),
        revision=REV,
        max_decisions=TERMINAL_MAX_DECISIONS,
        strict=False,
    )
    annotated_rows = annotate_threat_response_rows(game_rows, meta)
    terminal_summary = summarize_terminal_clean_rows(annotated_rows, revision=REV, max_decisions=TERMINAL_MAX_DECISIONS)
    arm_summary = threat_response_summary_rows(annotated_rows)
    mechanism_rows = threat_response_mechanism_rows(annotated_rows)
    life_rollup = target_summary_rows(annotated_rows, group_keys=("starting_life", "threat_policy_axis", "size_axis"))
    aggregate = aggregate_payoff_rows(annotated_rows)
    comparisons = compare_response_matrix_by_life(arm_summary)

    replay_traces, replay_results = ([], [])
    if replay_count:
        replay_traces, replay_results = _record_replay_samples(specs, count=replay_count)
        write_trace_jsonl(replay_traces, DATA / f"{prefix}_replay_traces.jsonl")
        dump_json(DATA / f"{prefix}_replay_results.json", replay_results)

    game_by_id = {str(r.get("cpp_shadow_game_id")): r for r in game_rows}
    forensic_rows = []
    closure_feature_rows = []
    ownership_rows = []
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

        ownership = counter_target_ownership_features_from_spec(spec, target_seat=target_seat, threat_seat=threat_seat)
        ownership.update(gid_meta)
        ownership_rows.append(ownership)

    forensic_arm_summary = summarize_forensic_rows(forensic_rows, group_keys=("arm_id", "starting_life", "size_axis", "threat_policy_axis"))
    closure_feature_summary = summarize_threat_closure_features(closure_feature_rows, group_keys=("size_axis", "starting_life", "threat_policy_axis", "opponent_agent"))
    ownership_summary = summarize_counter_ownership_rows(ownership_rows, group_keys=("size_axis", "starting_life", "threat_policy_axis", "opponent_agent"))

    # Merge ownership counts into compact case outputs.
    ownership_by_id = {str(r.get("cpp_shadow_game_id")): r for r in ownership_rows}
    feature_by_id = {str(r.get("cpp_shadow_game_id")): r for r in closure_feature_rows}
    merged_cases = []
    for row in annotated_rows:
        gid = str(row.get("cpp_shadow_game_id"))
        case = dict(row)
        case.update(ownership_by_id.get(gid, {}))
        case.update(feature_by_id.get(gid, {}))
        merged_cases.append(case)

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
    write_csv(DATA / f"{prefix}_counter_ownership.csv", ownership_rows)
    write_csv(DATA / f"{prefix}_counter_ownership_summary.csv", ownership_summary)

    surge_refutes = [r for r in merged_cases if str(r.get("threat_policy_axis")) == "face_protect_threat_surge" and float(r.get("focus_target_score", 0)) == 0.0]
    counter_survives = [r for r in merged_cases if str(r.get("threat_policy_axis")) == "face_protect_threat_surge" and float(r.get("focus_target_score", 0)) == 1.0]
    write_csv(DATA / f"{prefix}_surge_refute_cases.csv", [_slim_case(r) for r in surge_refutes[:64]])
    write_csv(DATA / f"{prefix}_counter_survive_cases.csv", [_slim_case(r) for r in counter_survives[:64]])

    return {
        "games": len(annotated_rows),
        "rows": annotated_rows,
        "arm_summary_rows": arm_summary,
        "mechanism_rows": mechanism_rows,
        "life_rollup": life_rollup,
        "comparisons": comparisons,
        "closure_feature_summary": closure_feature_summary,
        "closure_feature_rows": closure_feature_rows,
        "ownership_rows": ownership_rows,
        "ownership_summary": ownership_summary,
        "forensic_games": len(forensic_rows),
        "forensic_validation_errors": forensic_validation_errors,
        "forensic_validation_error_count": len(forensic_validation_errors),
        "closure_feature_games": len(closure_feature_rows),
        "counter_ownership_games": len(ownership_rows),
        "selected_own_spell_counters": int(sum(int(r.get("selected_own_spell_counters", 0) or 0) for r in ownership_rows)),
        "threat_selected_own_spell_counters": int(sum(int(r.get("threat_selected_own_spell_counters", 0) or 0) for r in ownership_rows)),
        "terminal_clean_summary": terminal_summary.as_dict(),
        "cpp_shadow_summary": cpp_summary.as_dict(),
        "python_errors": len(prepared.python_errors),
        "truncations": int(sum(1 for r in annotated_rows if str(r.get("is_truncation")).lower() in {"true", "1"})),
        "raw_cpp_transition_rows_generated_but_not_shipped": len(cpp_transition_rows),
        "cpp_transition_sample_rows_shipped": min(240, len(cpp_transition_rows)),
        "replay_samples": len(replay_results),
        "replay_passed": int(sum(1 for r in replay_results if r.get("passed") is True)),
        "surge_refute_cases": len(surge_refutes),
        "counter_survive_cases": len(counter_survives),
    }


def main() -> None:
    DATA.mkdir(exist_ok=True)
    arms = rev0067_response_matrix_arms(DATA / "seed_decks.json")
    specs, meta = response_matrix_specs(
        arms,
        simulator_revision=REV,
        reps=REPS,
        base_seed=BASE_SEED,
        max_decisions=TERMINAL_MAX_DECISIONS,
    )
    primary = _run_matrix_panel("rev0067_response_matrix", specs, meta, replay_count=12)

    stress_specs, stress_meta = response_matrix_stress_specs(
        arms,
        candidate_cells=STRESS_CELLS,
        simulator_revision=REV,
        reps=STRESS_REPS,
        base_seed=STRESS_BASE_SEED,
        max_decisions=TERMINAL_MAX_DECISIONS,
    )
    stress = _run_matrix_panel("rev0067_response_matrix_stress", stress_specs, stress_meta, replay_count=0)

    deep_specs, deep_meta = response_matrix_stress_specs(
        arms,
        candidate_cells=DEEP_CELLS,
        simulator_revision=REV,
        reps=DEEP_REPS,
        base_seed=DEEP_BASE_SEED,
        max_decisions=TERMINAL_MAX_DECISIONS,
    )
    deep = _run_matrix_panel("rev0067_response_matrix_deep60", deep_specs, deep_meta, replay_count=0)

    combined_rows = list(primary["rows"]) + list(stress["rows"]) + list(deep["rows"])
    combined_arm_summary = threat_response_summary_rows(combined_rows)
    combined_mechanisms = threat_response_mechanism_rows(combined_rows)
    combined_life_rollup = target_summary_rows(combined_rows, group_keys=("starting_life", "threat_policy_axis", "size_axis"))
    combined_comparisons = compare_response_matrix_by_life(combined_arm_summary)
    write_csv(DATA / "rev0067_response_matrix_cumulative_arm_summary.csv", combined_arm_summary)
    write_csv(DATA / "rev0067_response_matrix_cumulative_mechanisms.csv", combined_mechanisms)
    write_csv(DATA / "rev0067_response_matrix_cumulative_life_rollup.csv", combined_life_rollup)
    write_csv(DATA / "rev0067_response_matrix_cumulative_comparisons.csv", combined_comparisons)

    old_quarantine = read_csv(DATA / "rev0065_claim_quarantine_stress.csv")
    dump_json(DATA / "rev0067_response_matrix_arms.json", [a.as_dict() for a in arms])
    primary_features = primary.get("closure_feature_rows", [])
    summary = {
        "revision": REV,
        "codename": CODENAME,
        "purpose": "Response-matrix audit: test whether counter_guard survives closure, pressure, and a sharper face/protection threat_surge response across legal size cells.",
        "reps_per_seat_start_life_arm": REPS,
        "stress_reps_per_seat_start_life_arm": STRESS_REPS,
        "deep_reps_per_seat_start_life_arm": DEEP_REPS,
        "stress_cells": [f"{axis}_life{life}" for axis, life in STRESS_CELLS],
        "deep_cells": [f"{axis}_life{life}" for axis, life in DEEP_CELLS],
        "base_seed": BASE_SEED,
        "stress_base_seed": STRESS_BASE_SEED,
        "deep_base_seed": DEEP_BASE_SEED,
        "max_decisions": TERMINAL_MAX_DECISIONS,
        "arms": [a.as_dict() for a in arms],
        "primary": {k: v for k, v in primary.items() if k not in {"rows", "closure_feature_rows", "ownership_rows"}},
        "stress": {k: v for k, v in stress.items() if k not in {"rows", "closure_feature_rows", "ownership_rows"}},
        "deep": {k: v for k, v in deep.items() if k not in {"rows", "closure_feature_rows", "ownership_rows"}},
        "cumulative_comparisons": combined_comparisons,
        "games": int(primary["games"]) + int(stress["games"]) + int(deep["games"]),
        "forensic_games": int(primary["forensic_games"]) + int(stress["forensic_games"]) + int(deep["forensic_games"]),
        "closure_feature_games": int(primary["closure_feature_games"]) + int(stress["closure_feature_games"]) + int(deep["closure_feature_games"]),
        "counter_ownership_games": int(primary["counter_ownership_games"]) + int(stress["counter_ownership_games"]) + int(deep["counter_ownership_games"]),
        "forensic_validation_error_count": int(primary["forensic_validation_error_count"]) + int(stress["forensic_validation_error_count"]) + int(deep["forensic_validation_error_count"]),
        "python_errors": int(primary["python_errors"]) + int(stress["python_errors"]) + int(deep["python_errors"]),
        "truncations": int(primary["truncations"]) + int(stress["truncations"]) + int(deep["truncations"]),
        "selected_own_spell_counters": int(primary["selected_own_spell_counters"]) + int(stress["selected_own_spell_counters"]) + int(deep["selected_own_spell_counters"]),
        "threat_selected_own_spell_counters": int(primary["threat_selected_own_spell_counters"]) + int(stress["threat_selected_own_spell_counters"]) + int(deep["threat_selected_own_spell_counters"]),
        "raw_cpp_transition_rows_generated_but_not_shipped": int(primary["raw_cpp_transition_rows_generated_but_not_shipped"]) + int(stress["raw_cpp_transition_rows_generated_but_not_shipped"]) + int(deep["raw_cpp_transition_rows_generated_but_not_shipped"]),
        "cpp_transition_sample_rows_shipped": int(primary["cpp_transition_sample_rows_shipped"]) + int(stress["cpp_transition_sample_rows_shipped"]) + int(deep["cpp_transition_sample_rows_shipped"]),
        "replay_samples": int(primary["replay_samples"]),
        "replay_passed": int(primary["replay_passed"]),
        "old_rev0065_stress_quarantine_rows_loaded": old_quarantine,
        "response_matrix_gate": {},
        "notes": [
            "Focus score is the counter_guard target score. Lower score means that threat policy weakens or refutes the counter rescue.",
            "threat_surge is public-information-only: no hidden hand/library access, only DecisionFrame observations and legal actions.",
            "The stress pass is seed-disjoint and focused on the most dangerous live cells: life-40 small/size-skew and life-20 60-vs-60.",
            "Full raw transition CSVs are not shipped; compact C++ transition samples and forensic summaries are retained.",
        ],
    }
    gate = response_matrix_gate_report(primary, primary_features, primary.get("ownership_rows", []), min_games=120)
    for panel_name, panel in (("primary", primary), ("stress", stress), ("deep", deep)):
        if int(panel["truncations"]) != 0:
            gate["errors"].append(f"{panel_name} panel had truncations")
        if int(panel["python_errors"]) != 0:
            gate["errors"].append(f"{panel_name} panel had python errors")
        cpp = panel.get("cpp_shadow_summary", {})
        if isinstance(cpp, Mapping) and int(cpp.get("mismatches", 0)) != 0:
            gate["errors"].append(f"{panel_name} panel had C++ mismatches")
        if int(panel["forensic_validation_error_count"]) != 0:
            gate["errors"].append(f"{panel_name} forensic rerun mismatched live game rows")
        if int(panel["selected_own_spell_counters"]) != 0:
            gate["errors"].append(f"{panel_name} selected own-spell counters remained")
    if int(primary["replay_passed"]) < 10:
        gate["errors"].append("fewer than 10 replay samples passed")
    gate["passed"] = not gate["errors"]
    summary["response_matrix_gate"] = gate
    dump_json(DATA / "rev0067_response_matrix_summary.json", summary)
    print(json.dumps(summary, indent=2, sort_keys=True))
    if not gate["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
