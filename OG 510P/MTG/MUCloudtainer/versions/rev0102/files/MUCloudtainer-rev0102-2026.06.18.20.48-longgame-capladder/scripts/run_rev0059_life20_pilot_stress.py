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
from src.muc5.payoff import write_csv
from src.muc5.public_agents import make_public_agent
from src.muc5.replay import record_public_decision_trace, replay_public_decision_trace, write_trace_jsonl
from src.muc5.terminal_clean import mark_terminal_clean_rows, summarize_terminal_clean_rows
from src.muc5.terminal_decomposition import (
    annotate_decomposition_rows,
    decomposition_gate_report,
    decomposition_mechanism_rows,
    decomposition_specs,
    decomposition_summary_rows,
    rev0058_decomposition_arms,
    sample_transition_rows,
)

REV = "rev0059"
CODENAME = "life20-pilotstress"
DATA = ROOT / "data"
REPS = 12
BASE_SEED = 5959200
TERMINAL_MAX_DECISIONS = 900
FOCUSED_ARM_IDS = ("A_original_size_skew", "B_pilot_swap_size_skew")


def dump_json(path: Path, obj) -> None:
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _coerce(key: str, value: object) -> object:
    if value == "":
        return value
    if key in {"starting_life", "target_deck_size", "opponent_deck_size", "target_seat", "rep", "decisions", "turn_number", "games"}:
        try:
            return int(float(str(value)))
        except Exception:
            return value
    if key.endswith("_rate") or key.endswith("_share") or key.startswith(("p0_", "p1_", "focus_", "target_", "library_", "mean_", "median_")):
        try:
            return float(str(value))
        except Exception:
            return value
    return value


def read_csv_dicts(path: Path) -> list[dict[str, object]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as f:
        return [{k: _coerce(k, v) for k, v in dict(row).items()} for row in csv.DictReader(f)]


def _record_replay_samples(specs, count: int = 8):
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


def _ab_delta(summary_rows: Sequence[Mapping[str, object]]) -> list[dict[str, object]]:
    by = {(str(r.get("arm_id")), int(r.get("starting_life", 0))): r for r in summary_rows}
    out = []
    for life in sorted({life for (_arm, life) in by}):
        a = by.get(("A_original_size_skew", life), {})
        b = by.get(("B_pilot_swap_size_skew", life), {})
        def score(row):
            try:
                return float(row.get("target_mean_score_draw_half", 0.0))
            except Exception:
                return 0.0
        def games(row):
            try:
                return int(float(row.get("games", 0)))
            except Exception:
                return 0
        out.append(
            {
                "starting_life": life,
                "original_games": games(a),
                "original_score": score(a),
                "pilot_swap_games": games(b),
                "pilot_swap_score": score(b),
                "original_minus_pilot_swap": score(a) - score(b),
                "read": "pilot_not_rejected" if abs(score(a) - score(b)) < 0.15 else ("shell_favored" if score(a) > score(b) else "pilot_swap_favored"),
            }
        )
    return out


def main() -> None:
    all_arms = rev0058_decomposition_arms(DATA / "seed_decks.json")
    arms = [a for a in all_arms if a.arm_id in FOCUSED_ARM_IDS]
    specs, meta = decomposition_specs(
        arms,
        simulator_revision=REV,
        life_totals=(20,),
        reps=REPS,
        base_seed=BASE_SEED,
        max_decisions=TERMINAL_MAX_DECISIONS,
    )
    prepared = prepare_cpp_shadow_rollout(specs, revision=REV)
    cpp_summary, cpp_transition_rows = finalize_cpp_shadow_rollout(prepared)
    game_rows = mark_terminal_clean_rows(list(prepared.game_rows), revision=REV, max_decisions=TERMINAL_MAX_DECISIONS, strict=False)
    annotated_rows = annotate_decomposition_rows(game_rows, meta)
    terminal_summary = summarize_terminal_clean_rows(annotated_rows, revision=REV, max_decisions=TERMINAL_MAX_DECISIONS)
    arm_summary = decomposition_summary_rows(annotated_rows)
    mechanism_rows = decomposition_mechanism_rows(annotated_rows)
    ab_delta = _ab_delta(arm_summary)

    replay_traces, replay_results = _record_replay_samples(specs, count=8)
    prepared_trace = prepare_public_traces_for_cpp(replay_traces, revision=REV)
    cpp_trace_summary, cpp_trace_rows = finalize_cpp_trace_batch(prepared_trace)

    previous_rows = [r for r in read_csv_dicts(DATA / "rev0058_decomposition_games.csv") if str(r.get("arm_id")) in FOCUSED_ARM_IDS and int(r.get("starting_life", 0)) == 20]
    panel_rows = [r for r in read_csv_dicts(DATA / "rev0059_seed_disjoint_games.csv") if str(r.get("arm_id")) in FOCUSED_ARM_IDS and int(r.get("starting_life", 0)) == 20]
    cumulative_rows = previous_rows + panel_rows + annotated_rows
    cumulative_arm_summary = decomposition_summary_rows(cumulative_rows)
    cumulative_delta = _ab_delta(cumulative_arm_summary)

    write_csv(DATA / "rev0059_life20_pilotstress_games.csv", annotated_rows)
    write_csv(DATA / "rev0059_life20_pilotstress_arm_summary.csv", arm_summary)
    write_csv(DATA / "rev0059_life20_pilotstress_mechanisms.csv", mechanism_rows)
    write_csv(DATA / "rev0059_life20_pilotstress_ab_delta.csv", ab_delta)
    write_csv(DATA / "rev0059_life20_pilotstress_cumulative_arm_summary.csv", cumulative_arm_summary)
    write_csv(DATA / "rev0059_life20_pilotstress_cumulative_delta.csv", cumulative_delta)
    write_csv(DATA / "rev0059_life20_pilotstress_cpp_transition_sample.csv", sample_transition_rows(cpp_transition_rows))
    write_csv(DATA / "rev0059_life20_pilotstress_cpp_trace_rows.csv", [r.as_dict() for r in cpp_trace_rows])
    write_trace_jsonl(replay_traces, DATA / "rev0059_life20_pilotstress_replay_traces.jsonl")
    dump_json(DATA / "rev0059_life20_pilotstress_replay_results.json", replay_results)

    summary = {
        "revision": REV,
        "codename": CODENAME,
        "purpose": "Targeted life-20 stress pass on A/B after the seed-disjoint A-D run contradicted the rev0058 life-20 pilot-swap read.",
        "reps_per_seat_start_life_arm": REPS,
        "base_seed": BASE_SEED,
        "max_decisions": TERMINAL_MAX_DECISIONS,
        "games": len(annotated_rows),
        "python_errors": len(prepared.python_errors),
        "terminal_clean_summary": terminal_summary.as_dict(),
        "cpp_shadow_summary": cpp_summary.as_dict(),
        "cpp_trace_summary": cpp_trace_summary.as_dict(),
        "replay_samples": len(replay_results),
        "replay_passed": int(sum(1 for r in replay_results if r.get("passed") is True)),
        "raw_cpp_transition_rows_generated_but_not_shipped": len(cpp_transition_rows),
        "arm_summary_rows": arm_summary,
        "ab_delta": ab_delta,
        "cumulative_delta_rev0058_plus_rev0059_panel_plus_stress": cumulative_delta,
        "decomposition_gate": {},
        "notes": [
            "This is a contradiction-resolution stress pass, not a claim promotion.",
            "It focuses only on life 20 A_original_size_skew versus B_pilot_swap_size_skew.",
        ],
    }
    summary["decomposition_gate"] = decomposition_gate_report(
        summary,
        replay_results,
        annotated_rows,
        min_games=96,
        required_arms=FOCUSED_ARM_IDS,
        min_replay_passed=8,
    )
    dump_json(DATA / "rev0059_life20_pilotstress_summary.json", summary)
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
