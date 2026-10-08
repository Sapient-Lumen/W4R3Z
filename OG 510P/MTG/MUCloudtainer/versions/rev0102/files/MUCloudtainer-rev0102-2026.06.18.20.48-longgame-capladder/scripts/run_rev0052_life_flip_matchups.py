from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.muc5.cpp_rollout import finalize_cpp_shadow_rollout, prepare_cpp_shadow_rollout
from src.muc5.cpp_trace import finalize_cpp_trace_batch, prepare_public_traces_for_cpp
from src.muc5.mulligan_ranker import make_mulligan_agent
from src.muc5.payoff import aggregate_payoff_rows, write_csv
from src.muc5.promotion import PromotionGateConfig, audit_promotion_rows, strategy_standings
from src.muc5.public_agents import make_public_agent
from src.muc5.replay import record_public_decision_trace, replay_public_decision_trace, write_trace_jsonl
from src.muc5.statgate import audit_statistical_gate, pairwise_stat_rows, statistical_standings
from src.muc5.strategy_sets import terminal_clean_yield_ranker_bundles
from src.muc5.terminal_clean import mark_terminal_clean_rows, summarize_terminal_clean_rows, terminal_clean_by_strategy
from src.muc5.terminal_matchup import (
    annotate_life_matchup_rows,
    focused_life_matchup_specs,
    life_flip_gate,
    life_flip_matchups_from_target_pairs,
    life_flip_retest_rows,
    target_life_cell_rows,
)

REV = "rev0052"
CODENAME = "lifeflip-targetcells"
DATA = ROOT / "data"
TERMINAL_MAX_DECISIONS = 900
REPS = 8
TOP_N = 4


def _read_csv_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def _record_replay_samples(eval_specs, count: int = 8):
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

    if not eval_specs:
        return [], []
    sample_indices = [0, 1, 2, 3, max(0, len(eval_specs)//2 - 1), len(eval_specs)//2, len(eval_specs)-2, len(eval_specs)-1]
    traces = []
    results = []
    seen = set()
    for idx in sample_indices[:count + 4]:
        if idx in seen or idx < 0 or idx >= len(eval_specs):
            continue
        seen.add(idx)
        spec = eval_specs[idx]
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
        if len(traces) >= count:
            break
    return traces, results


def main() -> None:
    DATA.mkdir(exist_ok=True)
    strategies = terminal_clean_yield_ranker_bundles(DATA / "seed_decks.json")
    prev_target_pairs = _read_csv_rows(DATA / "rev0051_deep_claim_target_pairs.csv")
    matchups = life_flip_matchups_from_target_pairs(prev_target_pairs, top_n=TOP_N, life_low=20, life_high=40)
    if not matchups:
        raise SystemExit("no life-flip matchups selected")

    specs = focused_life_matchup_specs(
        strategies,
        matchups,
        simulator_revision=REV,
        life_totals=(20, 40),
        reps=REPS,
        base_seed=5252000,
        max_decisions=TERMINAL_MAX_DECISIONS,
    )
    prepared = prepare_cpp_shadow_rollout(specs, revision=REV)
    cpp_summary, cpp_transition_rows = finalize_cpp_shadow_rollout(prepared)

    annotated = annotate_life_matchup_rows(list(prepared.game_rows), matchups)
    game_rows = mark_terminal_clean_rows(
        annotated,
        revision=REV,
        max_decisions=TERMINAL_MAX_DECISIONS,
        strict=False,
    )
    terminal_summary = summarize_terminal_clean_rows(game_rows, revision=REV, max_decisions=TERMINAL_MAX_DECISIONS)
    aggregate = aggregate_payoff_rows(game_rows)
    standings = strategy_standings(game_rows)
    stat_standings = statistical_standings(game_rows, min_games_for_claim=32)
    pairwise = pairwise_stat_rows(game_rows, min_games_for_claim=8)
    by_strategy = terminal_clean_by_strategy(game_rows)
    cell_rows = target_life_cell_rows(game_rows, matchups, life_totals=(20, 40))
    flip_rows = life_flip_retest_rows(cell_rows, matchups, life_low=20, life_high=40)

    replay_traces, replay_results = _record_replay_samples(specs, count=8)
    prepared_trace = prepare_public_traces_for_cpp(replay_traces, revision=REV)
    cpp_trace_summary, cpp_trace_rows = finalize_cpp_trace_batch(prepared_trace)

    promotion = audit_promotion_rows(
        game_rows,
        replay_results=replay_results,
        config=PromotionGateConfig(simulator_revision=REV, min_rows=200, min_replay_traces=6, max_truncation_rate=0.0),
    )
    stat_gate = audit_statistical_gate(game_rows, stat_standings, pairwise, min_raw_rows=200, max_truncation_rate=0.0)
    flip_gate = life_flip_gate(
        game_rows,
        cell_rows,
        flip_rows,
        revision=REV,
        cpp_summary=cpp_summary.as_dict(),
        min_rows=200,
        min_cell_games=32,
    )

    write_csv(DATA / "rev0052_life_flip_selected_matchups.csv", matchups)
    write_csv(DATA / "rev0052_life_flip_games.csv", game_rows)
    write_csv(DATA / "rev0052_life_flip_aggregate.csv", aggregate)
    write_csv(DATA / "rev0052_life_flip_standings.csv", standings)
    write_csv(DATA / "rev0052_life_flip_stat_standings.csv", stat_standings)
    write_csv(DATA / "rev0052_life_flip_pairwise.csv", pairwise)
    write_csv(DATA / "rev0052_life_flip_by_strategy.csv", by_strategy)
    write_csv(DATA / "rev0052_life_flip_target_life_cells.csv", cell_rows)
    write_csv(DATA / "rev0052_life_flip_retest.csv", flip_rows)
    write_csv(DATA / "rev0052_life_flip_cpp_transitions.csv", [r.as_dict() for r in cpp_transition_rows])
    write_csv(DATA / "rev0052_life_flip_cpp_trace_rows.csv", [r.as_dict() for r in cpp_trace_rows])
    write_trace_jsonl(replay_traces, DATA / "rev0052_life_flip_replay_traces.jsonl")
    (DATA / "rev0052_life_flip_replay_results.json").write_text(json.dumps(replay_results, indent=2))

    signal_counts = {}
    for row in flip_rows:
        label = str(row.get("life_flip_label"))
        signal_counts[label] = signal_counts.get(label, 0) + 1

    summary = {
        "revision": REV,
        "codename": CODENAME,
        "based_on": "rev0051 deep target-pair life splits",
        "strategies": len(strategies),
        "selected_matchups": len(matchups),
        "selected_matchup_rows": matchups,
        "reps": REPS,
        "games": len(game_rows),
        "aggregate_rows": len(aggregate),
        "target_life_cell_rows": len(cell_rows),
        "life_flip_rows": len(flip_rows),
        "max_decisions": TERMINAL_MAX_DECISIONS,
        "terminal_clean_summary": terminal_summary.as_dict(),
        "promotion": promotion.as_dict(),
        "statistical_gate": stat_gate.as_dict(),
        "life_flip_gate": flip_gate.as_dict(),
        "cpp_shadow_summary": cpp_summary.as_dict(),
        "cpp_trace_summary": cpp_trace_summary.as_dict(),
        "replay_samples": len(replay_results),
        "replay_passed": int(sum(1 for r in replay_results if r.get("passed") is True)),
        "life_flip_label_counts": signal_counts,
        "top_life_flips": flip_rows[:10],
        "notes": [
            "rev0052 treats rev0051 target-pair life splits as an agenda, not as a theorem.",
            "The selected target/opponent cells are retested terminal-clean with both target seats, both starting players, both life totals, and C++ shadow transition checks.",
            "No gameplay policy is promoted here.  This is a focused life-split cell audit for deciding which matchup/life cells deserve even deeper repetitions.",
        ],
    }
    (DATA / "rev0052_life_flip_summary.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
