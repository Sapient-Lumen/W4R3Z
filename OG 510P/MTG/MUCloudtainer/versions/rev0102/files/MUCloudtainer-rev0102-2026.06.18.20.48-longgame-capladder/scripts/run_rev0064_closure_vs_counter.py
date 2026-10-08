#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Mapping

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.muc5.closure_vs_counter import (
    annotate_closure_vs_counter_rows,
    closure_vs_counter_gate_report,
    closure_vs_counter_mechanism_rows,
    closure_vs_counter_specs,
    closure_vs_counter_summary_rows,
    compare_closure_vs_counter_by_life,
    compare_closure_vs_counter_features_by_life,
    rev0064_closure_vs_counter_arms,
)
from src.muc5.cpp_rollout import finalize_cpp_shadow_rollout, prepare_cpp_shadow_rollout
from src.muc5.mulligan_ranker import make_mulligan_agent
from src.muc5.payoff import aggregate_payoff_rows, write_csv
from src.muc5.public_agents import make_public_agent
from src.muc5.replay import record_public_decision_trace, replay_public_decision_trace, write_trace_jsonl
from src.muc5.terminal_clean import mark_terminal_clean_rows, summarize_terminal_clean_rows
from src.muc5.terminal_decomposition import sample_transition_rows
from src.muc5.terminal_mechanisms import target_summary_rows
from src.muc5.threat_closure import (
    summarize_threat_closure_features,
    threat_closure_trace_features_from_spec,
)
from src.muc5.trajectory_forensics import summarize_forensic_rows, trajectory_forensics_from_spec, validate_forensics_against_game_row

REV = "rev0064"
CODENAME = "closurevscounter-claimdemotion"
DATA = ROOT / "data"
REPS = 3
TERMINAL_MAX_DECISIONS = 900
BASE_SEED = 6464000


def dump_json(path: Path, obj: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")


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


def _slim_counter_case(row: Mapping[str, object]) -> dict[str, object]:
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
        "threat_declared_attackers_to_player",
        "threat_declared_attack_draw_cost_total",
        "threat_declared_lethal_attack_actions",
        "threat_selfdeck_on_attack_trigger",
        "threat_selfdeck_on_declared_lethal_attack",
        "threat_overlord_cast_draw_events",
        "threat_selfdeck_on_overlord_cast",
        "threat_jace_zero_actions",
        "threat_jace_zero_at_library_le_10",
        "threat_selfdeck_on_jace_zero",
        "threat_ultimate_self_actions",
        "threat_ultimate_opponent_actions",
        "threat_pass_attack_actions",
        "threat_last_action_before_loss",
        "target_final_life",
        "threat_final_life",
        "target_final_library",
        "threat_final_library",
    ]
    return {k: row.get(k, "") for k in keys}


def main() -> None:
    DATA.mkdir(exist_ok=True)
    arms = rev0064_closure_vs_counter_arms(DATA / "seed_decks.json")
    specs, meta = closure_vs_counter_specs(
        arms,
        simulator_revision=REV,
        reps=REPS,
        base_seed=BASE_SEED,
        max_decisions=TERMINAL_MAX_DECISIONS,
    )

    prepared = prepare_cpp_shadow_rollout(specs, revision=REV)
    cpp_summary, cpp_transition_rows = finalize_cpp_shadow_rollout(prepared)
    game_rows = mark_terminal_clean_rows(
        list(prepared.game_rows),
        revision=REV,
        max_decisions=TERMINAL_MAX_DECISIONS,
        strict=False,
    )
    annotated_rows = annotate_closure_vs_counter_rows(game_rows, meta)
    terminal_summary = summarize_terminal_clean_rows(annotated_rows, revision=REV, max_decisions=TERMINAL_MAX_DECISIONS)
    arm_summary = closure_vs_counter_summary_rows(annotated_rows)
    mechanism_rows = closure_vs_counter_mechanism_rows(annotated_rows)
    life_rollup = target_summary_rows(annotated_rows, group_keys=("starting_life", "threat_policy_axis", "size_axis"))
    aggregate = aggregate_payoff_rows(annotated_rows)
    comparisons = compare_closure_vs_counter_by_life(arm_summary)

    replay_traces, replay_results = _record_replay_samples(specs, count=12)

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

    forensic_arm_summary = summarize_forensic_rows(forensic_rows, group_keys=("arm_id", "starting_life", "size_axis", "threat_policy_axis"))
    closure_feature_summary = summarize_threat_closure_features(closure_feature_rows, group_keys=("size_axis", "starting_life", "threat_policy_axis", "opponent_agent"))
    closure_feature_comparisons = compare_closure_vs_counter_features_by_life(closure_feature_summary)

    legacy_selfdeck_cases = [
        _slim_counter_case(r)
        for r in sorted(closure_feature_rows, key=lambda r: (str(r.get("size_axis")), int(r.get("starting_life", 0)), int(r.get("seed", 0))))
        if str(r.get("threat_policy_axis")) == "legacy_threat_rush" and str(r.get("threat_loss_vector")) == "selfdeck"
    ][:60]
    closure_counter_rescue_cases = [
        _slim_counter_case(r)
        for r in sorted(closure_feature_rows, key=lambda r: (str(r.get("size_axis")), int(r.get("starting_life", 0)), int(r.get("seed", 0))))
        if str(r.get("threat_policy_axis")) == "library_aware_threat_closure" and float(r.get("threat_score", 0.5)) > 0.5
    ][:60]

    write_csv(DATA / "rev0064_closure_vs_counter_games.csv", annotated_rows)
    write_csv(DATA / "rev0064_closure_vs_counter_aggregate.csv", aggregate)
    write_csv(DATA / "rev0064_closure_vs_counter_arm_summary.csv", arm_summary)
    write_csv(DATA / "rev0064_closure_vs_counter_mechanisms.csv", mechanism_rows)
    write_csv(DATA / "rev0064_closure_vs_counter_life_rollup.csv", life_rollup)
    write_csv(DATA / "rev0064_closure_vs_counter_comparisons.csv", comparisons)
    write_csv(DATA / "rev0064_closure_vs_counter_cpp_transition_sample.csv", sample_transition_rows(cpp_transition_rows, limit=240))
    write_trace_jsonl(replay_traces, DATA / "rev0064_closure_vs_counter_replay_traces.jsonl")
    dump_json(DATA / "rev0064_closure_vs_counter_replay_results.json", replay_results)
    dump_json(DATA / "rev0064_closure_vs_counter_arms.json", [a.as_dict() for a in arms])
    write_csv(DATA / "rev0064_closure_vs_counter_forensics.csv", forensic_rows)
    write_csv(DATA / "rev0064_closure_vs_counter_forensic_arm_summary.csv", forensic_arm_summary)
    write_csv(DATA / "rev0064_closure_vs_counter_features.csv", closure_feature_rows)
    write_csv(DATA / "rev0064_closure_vs_counter_feature_summary.csv", closure_feature_summary)
    write_csv(DATA / "rev0064_closure_vs_counter_feature_comparisons.csv", closure_feature_comparisons)
    write_csv(DATA / "rev0064_closure_vs_counter_legacy_selfdeck_cases.csv", legacy_selfdeck_cases)
    write_csv(DATA / "rev0064_closure_vs_counter_closure_rescue_cases.csv", closure_counter_rescue_cases)

    summary = {
        "revision": REV,
        "codename": CODENAME,
        "purpose": "Claim-relevant closure audit: test whether active counter-wall edges survive when the Overlord threat shell uses the public-information threat_closure guard instead of legacy threat_rush.",
        "reps_per_seat_start_life_arm": REPS,
        "base_seed": BASE_SEED,
        "max_decisions": TERMINAL_MAX_DECISIONS,
        "arms": [a.as_dict() for a in arms],
        "games": len(annotated_rows),
        "closure_feature_games": len(closure_feature_rows),
        "forensic_games": len(forensic_rows),
        "forensic_validation_error_count": len(forensic_validation_errors),
        "forensic_validation_errors": forensic_validation_errors[:10],
        "python_errors": len(prepared.python_errors),
        "truncations": int(sum(1 for r in annotated_rows if str(r.get("is_truncation")).lower() in {"true", "1"})),
        "terminal_clean_summary": terminal_summary.as_dict(),
        "cpp_shadow_summary": cpp_summary.as_dict(),
        "replay_samples": len(replay_results),
        "replay_passed": int(sum(1 for r in replay_results if r.get("passed") is True)),
        "raw_cpp_transition_rows_generated_but_not_shipped": len(cpp_transition_rows),
        "cpp_transition_sample_rows_shipped": min(240, len(cpp_transition_rows)),
        "arm_summary_rows": arm_summary,
        "life_rollup": life_rollup,
        "closure_vs_counter_comparisons": comparisons,
        "closure_feature_summary": closure_feature_summary,
        "closure_feature_comparisons": closure_feature_comparisons,
        "closure_vs_counter_gate": {},
        "notes": [
            "Focus score is the active counter-wall target score. Lower counter score under threat_closure means the prior edge was threat-pilot-sensitive.",
            "This revision does not promote threat_closure into historical strategy sets and does not change simulator semantics.",
            "The same closure-feature extractor from rev0063 is reused against active counter targets, converting the inert-only audit into a claim-relevant threat gate.",
            "Full raw transition CSVs are not shipped; compact C++ transition samples and forensic summaries are retained.",
        ],
    }
    gate = closure_vs_counter_gate_report(summary, closure_feature_rows, min_games=120)
    if forensic_validation_errors:
        gate["errors"].append("forensic rerun mismatched live game rows")
    if int(sum(1 for r in replay_results if r.get("passed") is True)) < 10:
        gate["errors"].append("fewer than 10 replay samples passed")
    gate["passed"] = not gate["errors"]
    summary["closure_vs_counter_gate"] = gate
    dump_json(DATA / "rev0064_closure_vs_counter_summary.json", summary)
    print(json.dumps(summary, indent=2, sort_keys=True))
    if not gate["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
