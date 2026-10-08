#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path
from typing import Mapping, Sequence

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.muc5.cpp_rollout import finalize_cpp_shadow_rollout, prepare_cpp_shadow_rollout
from src.muc5.cpp_trace import finalize_cpp_trace_batch, prepare_public_traces_for_cpp
from src.muc5.mulligan_ranker import make_mulligan_agent
from src.muc5.payoff import aggregate_payoff_rows, write_csv
from src.muc5.public_agents import make_public_agent
from src.muc5.replay import record_public_decision_trace, replay_public_decision_trace, write_trace_jsonl
from src.muc5.terminal_clean import mark_terminal_clean_rows, summarize_terminal_clean_rows
from src.muc5.terminal_decomposition import (
    annotate_decomposition_rows,
    compare_decomposition_by_life,
    decomposition_gate_report,
    decomposition_mechanism_rows,
    decomposition_specs,
    decomposition_summary_rows,
    rev0058_decomposition_arms,
    sample_transition_rows,
)
from src.muc5.terminal_mechanisms import target_summary_rows

REV = "rev0059"
CODENAME = "seedconfirm-shelltruth"
DATA = ROOT / "data"
REPS = 5
TERMINAL_MAX_DECISIONS = 900
BASE_SEED = 5959000
FOCUSED_ARM_IDS = (
    "A_original_size_skew",
    "B_pilot_swap_size_skew",
    "C_equalized_40v40",
    "D_equalized_60v60",
)


def dump_json(path: Path, obj) -> None:
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _coerce_csv_value(key: str, value: object) -> object:
    if value == "":
        return value
    numeric_int_keys = {"starting_life", "target_deck_size", "opponent_deck_size", "target_seat", "rep", "decisions", "turn_number", "games"}
    numeric_float_prefixes = ("p0_", "p1_", "focus_", "target_", "library_", "truncation_", "mean_", "median_", "score_")
    if key in numeric_int_keys:
        try:
            return int(float(str(value)))
        except Exception:
            return value
    if key.endswith("_rate") or key.endswith("_share") or key.startswith(numeric_float_prefixes):
        try:
            return float(str(value))
        except Exception:
            return value
    return value


def read_csv_dicts(path: Path) -> list[dict[str, object]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as f:
        return [{k: _coerce_csv_value(k, v) for k, v in dict(row).items()} for row in csv.DictReader(f)]


def _record_replay_samples(specs, count: int = 12):
    agent_cache = {}
    mulligan_cache = {}

    def agent(name: str):
        if name not in agent_cache:
            agent_cache[name] = make_public_agent(name)
        return agent_cache[name]

    def mull(name: str):
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
            mulligan_agents=(mull(spec.mulligan0), mull(spec.mulligan1)),
        )
        traces.append(trace)
        results.append(replay_public_decision_trace(trace).as_dict())
    return traces, results


def _current_vs_previous_rows(current: Sequence[Mapping[str, object]], previous: Sequence[Mapping[str, object]]) -> list[dict[str, object]]:
    cur = {(str(r.get("arm_id")), int(r.get("starting_life", 0))): r for r in current}
    prev = {(str(r.get("arm_id")), int(r.get("starting_life", 0))): r for r in previous}
    out: list[dict[str, object]] = []
    for key in sorted(set(cur) | set(prev)):
        c = cur.get(key, {})
        p = prev.get(key, {})
        def score(row: Mapping[str, object]) -> float:
            try:
                return float(row.get("target_mean_score_draw_half", 0.0))
            except Exception:
                return 0.0
        def games(row: Mapping[str, object]) -> int:
            try:
                return int(float(row.get("games", 0)))
            except Exception:
                return 0
        out.append(
            {
                "arm_id": key[0],
                "starting_life": key[1],
                "rev0058_games": games(p),
                "rev0058_score": score(p),
                "rev0059_games": games(c),
                "rev0059_score": score(c),
                "score_delta_rev0059_minus_rev0058": score(c) - score(p),
            }
        )
    return out


def main() -> None:
    DATA.mkdir(exist_ok=True)
    all_arms = rev0058_decomposition_arms(DATA / "seed_decks.json")
    arms = [a for a in all_arms if a.arm_id in FOCUSED_ARM_IDS]
    specs, meta = decomposition_specs(
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
    annotated_rows = annotate_decomposition_rows(game_rows, meta)
    terminal_summary = summarize_terminal_clean_rows(annotated_rows, revision=REV, max_decisions=TERMINAL_MAX_DECISIONS)
    arm_summary = decomposition_summary_rows(annotated_rows)
    mechanism_rows = decomposition_mechanism_rows(annotated_rows)
    life_rollup = target_summary_rows(annotated_rows, group_keys=("starting_life",))
    comparisons = compare_decomposition_by_life(arm_summary)
    aggregate = aggregate_payoff_rows(annotated_rows)

    replay_traces, replay_results = _record_replay_samples(specs, count=12)
    prepared_trace = prepare_public_traces_for_cpp(replay_traces, revision=REV)
    cpp_trace_summary, cpp_trace_rows = finalize_cpp_trace_batch(prepared_trace)

    previous_rows = [r for r in read_csv_dicts(DATA / "rev0058_decomposition_games.csv") if str(r.get("arm_id")) in FOCUSED_ARM_IDS]
    previous_arm_summary = decomposition_summary_rows(previous_rows)
    cumulative_rows = previous_rows + annotated_rows
    cumulative_arm_summary = decomposition_summary_rows(cumulative_rows)
    cumulative_comparisons = compare_decomposition_by_life(cumulative_arm_summary)
    previous_vs_current = _current_vs_previous_rows(arm_summary, previous_arm_summary)

    write_csv(DATA / "rev0059_seed_disjoint_games.csv", annotated_rows)
    write_csv(DATA / "rev0059_seed_disjoint_aggregate.csv", aggregate)
    write_csv(DATA / "rev0059_seed_disjoint_arm_summary.csv", arm_summary)
    write_csv(DATA / "rev0059_seed_disjoint_mechanisms.csv", mechanism_rows)
    write_csv(DATA / "rev0059_seed_disjoint_life_rollup.csv", life_rollup)
    write_csv(DATA / "rev0059_seed_disjoint_comparisons.csv", comparisons)
    write_csv(DATA / "rev0059_seed_disjoint_cumulative_arm_summary.csv", cumulative_arm_summary)
    write_csv(DATA / "rev0059_seed_disjoint_cumulative_comparisons.csv", cumulative_comparisons)
    write_csv(DATA / "rev0059_seed_disjoint_rev0058_vs_rev0059.csv", previous_vs_current)
    write_csv(DATA / "rev0059_seed_disjoint_cpp_transition_sample.csv", sample_transition_rows(cpp_transition_rows))
    write_csv(DATA / "rev0059_seed_disjoint_cpp_trace_rows.csv", [r.as_dict() for r in cpp_trace_rows])
    write_trace_jsonl(replay_traces, DATA / "rev0059_seed_disjoint_replay_traces.jsonl")
    dump_json(DATA / "rev0059_seed_disjoint_replay_results.json", replay_results)
    dump_json(DATA / "rev0059_seed_disjoint_arms.json", [a.as_dict() for a in arms])

    summary = {
        "revision": REV,
        "codename": CODENAME,
        "purpose": "Seed-disjoint focused confirmation of the rev0058 pilot/deck-size decomposition, restricted to the four riskiest explanatory arms A-D.",
        "reps_per_seat_start_life_arm": REPS,
        "base_seed": BASE_SEED,
        "max_decisions": TERMINAL_MAX_DECISIONS,
        "focused_arm_ids": list(FOCUSED_ARM_IDS),
        "arms": [a.as_dict() for a in arms],
        "games": len(annotated_rows),
        "python_errors": len(prepared.python_errors),
        "terminal_clean_summary": terminal_summary.as_dict(),
        "cpp_shadow_summary": cpp_summary.as_dict(),
        "cpp_trace_summary": cpp_trace_summary.as_dict(),
        "replay_samples": len(replay_results),
        "replay_passed": int(sum(1 for r in replay_results if r.get("passed") is True)),
        "raw_cpp_transition_rows_generated_but_not_shipped": len(cpp_transition_rows),
        "cpp_transition_sample_rows_shipped": min(240, len(cpp_transition_rows)),
        "previous_rev0058_focused_games": len(previous_rows),
        "cumulative_focused_games_rev0058_plus_rev0059": len(cumulative_rows),
        "arm_summary_rows": arm_summary,
        "life_rollup": life_rollup,
        "comparisons": comparisons,
        "cumulative_comparisons": cumulative_comparisons,
        "previous_vs_current": previous_vs_current,
        "decomposition_gate": {},
        "notes": [
            "This is seed-disjoint from rev0058 and focuses compute on A-D rather than expanding bureaucracy.",
            "The gate checks terminal cleanliness, replay, and C++ parity; it does not promote a general Magic claim.",
            "Full C++ transition rows are generated and checked but only a compact sample is shipped.",
        ],
    }
    summary["decomposition_gate"] = decomposition_gate_report(
        summary,
        replay_results,
        annotated_rows,
        min_games=160,
        required_arms=FOCUSED_ARM_IDS,
        min_replay_passed=12,
    )
    dump_json(DATA / "rev0059_seed_disjoint_summary.json", summary)
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
