#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Mapping

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.muc5.cpp_rollout import finalize_cpp_shadow_rollout, prepare_cpp_shadow_rollout
from src.muc5.mechanism_ablation import (
    annotate_mechanism_ablation_rows,
    compare_forensic_ablation_by_life,
    compare_mechanism_ablation_by_life,
    mechanism_ablation_gate_report,
    mechanism_ablation_mechanism_rows,
    mechanism_ablation_specs,
    mechanism_ablation_summary_rows,
    rev0061_mechanism_ablation_arms,
)
from src.muc5.mulligan_ranker import make_mulligan_agent
from src.muc5.payoff import aggregate_payoff_rows, write_csv
from src.muc5.public_agents import make_public_agent
from src.muc5.replay import record_public_decision_trace, replay_public_decision_trace, write_trace_jsonl
from src.muc5.terminal_clean import mark_terminal_clean_rows, summarize_terminal_clean_rows
from src.muc5.terminal_decomposition import sample_transition_rows
from src.muc5.terminal_mechanisms import target_summary_rows
from src.muc5.trajectory_forensics import summarize_forensic_rows, trajectory_forensics_from_spec, validate_forensics_against_game_row

REV = "rev0061"
CODENAME = "jacecounterablate-shellcausality"
DATA = ROOT / "data"
REPS = 6
TERMINAL_MAX_DECISIONS = 900
BASE_SEED = 6161000


def dump_json(path: Path, obj: object) -> None:
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _record_replay_samples(specs, count: int = 10):
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


def _slim_forensic_case(row: Mapping[str, object]) -> dict[str, object]:
    keys = [
        "arm_id",
        "starting_life",
        "seed",
        "target_seat",
        "starting_player",
        "focus_target_score",
        "focus_terminal_mechanism",
        "focus_terminal_loser_role",
        "loss_reason",
        "decisions",
        "turn_number",
        "target_final_library",
        "opponent_final_library",
        "target_library_buffer_final",
        "target_cast_jace",
        "target_activate_jace_zero",
        "target_cast_counterspell",
        "target_cast_force_pitch",
        "target_min_life",
        "opponent_min_life",
        "opponent_cast_overlord_impending",
        "opponent_cast_overlord_full_cost",
        "opponent_attack_to_player_total",
    ]
    return {k: row.get(k, "") for k in keys}


def main() -> None:
    DATA.mkdir(exist_ok=True)
    arms = rev0061_mechanism_ablation_arms(DATA / "seed_decks.json")
    specs, meta = mechanism_ablation_specs(
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
    annotated_rows = annotate_mechanism_ablation_rows(game_rows, meta)
    terminal_summary = summarize_terminal_clean_rows(annotated_rows, revision=REV, max_decisions=TERMINAL_MAX_DECISIONS)
    arm_summary = mechanism_ablation_summary_rows(annotated_rows)
    mechanism_rows = mechanism_ablation_mechanism_rows(annotated_rows)
    life_rollup = target_summary_rows(annotated_rows, group_keys=("starting_life",))
    aggregate = aggregate_payoff_rows(annotated_rows)
    comparisons = compare_mechanism_ablation_by_life(arm_summary)

    replay_traces, replay_results = _record_replay_samples(specs, count=10)

    # Compact transition-level explanatory pass.  This reruns the same public-agent
    # games to avoid shipping full transition traces but still provides action, Jace,
    # library-buffer, and pressure features.
    game_by_id = {str(r.get("cpp_shadow_game_id")): r for r in game_rows}
    forensic_rows = []
    forensic_validation_errors = []
    for spec in specs:
        target_seat = int(meta[spec.game_id]["target_seat"])
        forensic = trajectory_forensics_from_spec(spec, target_seat=target_seat)
        forensic.update(meta[spec.game_id])
        errors = validate_forensics_against_game_row(forensic, game_by_id.get(spec.game_id, {}))
        if errors:
            forensic_validation_errors.append({"game_id": spec.game_id, "errors": errors})
        forensic_rows.append(forensic)

    forensic_arm_summary = summarize_forensic_rows(forensic_rows, group_keys=("arm_id", "starting_life"))
    forensic_result_summary = summarize_forensic_rows(
        forensic_rows,
        group_keys=("arm_id", "starting_life", "focus_target_result", "focus_terminal_mechanism", "focus_terminal_loser_role"),
    )
    forensic_feature_comparisons = compare_forensic_ablation_by_life(forensic_arm_summary)
    no_counter_losses = [
        _slim_forensic_case(r)
        for r in sorted(
            forensic_rows,
            key=lambda r: (str(r.get("arm_id")), int(r.get("starting_life", 0)), float(r.get("focus_target_score", 0.5)), int(r.get("decisions", 0))),
        )
        if str(r.get("arm_id")) == "H_target_no_counterspell60" and float(r.get("focus_target_score", 0.5)) < 0.5
    ][:32]
    no_jace_wins = [
        _slim_forensic_case(r)
        for r in sorted(
            forensic_rows,
            key=lambda r: (int(r.get("starting_life", 0)), str(r.get("focus_terminal_mechanism")), int(r.get("decisions", 0))),
        )
        if str(r.get("arm_id")) == "G_target_no_jace60" and float(r.get("focus_target_score", 0.5)) > 0.5
    ][:32]

    write_csv(DATA / "rev0061_mechanism_ablation_games.csv", annotated_rows)
    write_csv(DATA / "rev0061_mechanism_ablation_aggregate.csv", aggregate)
    write_csv(DATA / "rev0061_mechanism_ablation_arm_summary.csv", arm_summary)
    write_csv(DATA / "rev0061_mechanism_ablation_mechanisms.csv", mechanism_rows)
    write_csv(DATA / "rev0061_mechanism_ablation_life_rollup.csv", life_rollup)
    write_csv(DATA / "rev0061_mechanism_ablation_comparisons.csv", comparisons)
    write_csv(DATA / "rev0061_mechanism_ablation_cpp_transition_sample.csv", sample_transition_rows(cpp_transition_rows, limit=240))
    write_trace_jsonl(replay_traces, DATA / "rev0061_mechanism_ablation_replay_traces.jsonl")
    dump_json(DATA / "rev0061_mechanism_ablation_replay_results.json", replay_results)
    dump_json(DATA / "rev0061_mechanism_ablation_arms.json", [a.as_dict() for a in arms])
    write_csv(DATA / "rev0061_mechanism_ablation_forensics.csv", forensic_rows)
    write_csv(DATA / "rev0061_mechanism_ablation_forensic_arm_summary.csv", forensic_arm_summary)
    write_csv(DATA / "rev0061_mechanism_ablation_forensic_result_summary.csv", forensic_result_summary)
    write_csv(DATA / "rev0061_mechanism_ablation_forensic_feature_comparisons.csv", forensic_feature_comparisons)
    write_csv(DATA / "rev0061_mechanism_ablation_nojace_win_cases.csv", no_jace_wins)
    write_csv(DATA / "rev0061_mechanism_ablation_nocounter_loss_cases.csv", no_counter_losses)

    summary = {
        "revision": REV,
        "codename": CODENAME,
        "purpose": "Focused causal ablation: split passive 60-card endurance from active Jace/Brainstorm and dense Counterspell machinery in the cf34 counter-wall shell.",
        "reps_per_seat_start_life_arm": REPS,
        "base_seed": BASE_SEED,
        "max_decisions": TERMINAL_MAX_DECISIONS,
        "arms": [a.as_dict() for a in arms],
        "games": len(annotated_rows),
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
        "comparisons": comparisons,
        "forensic_feature_comparisons": forensic_feature_comparisons,
        "ablation_gate": {},
        "notes": [
            "This is not a promotion claim; it is a causal mechanism panel for the already-replicated local matchup.",
            "No-Jace replaces Jace copies with Islands to preserve passive library size and countermagic density.",
            "No-Counterspell replaces Counterspell copies with Islands to preserve passive library size and Jace count while removing dense two-mana permission.",
            "The linked cube ships compact C++ samples and forensic features, not raw full transition CSV ballast.",
        ],
    }
    gate = mechanism_ablation_gate_report(summary, annotated_rows, min_games=180)
    if forensic_validation_errors:
        gate["errors"].append("forensic rerun mismatched live game rows")
    if int(sum(1 for r in replay_results if r.get("passed") is True)) < 10:
        gate["errors"].append("fewer than 10 replay samples passed")
    gate["passed"] = not gate["errors"]
    summary["ablation_gate"] = gate
    dump_json(DATA / "rev0061_mechanism_ablation_summary.json", summary)
    print(json.dumps(summary, indent=2, sort_keys=True))
    if not gate["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
