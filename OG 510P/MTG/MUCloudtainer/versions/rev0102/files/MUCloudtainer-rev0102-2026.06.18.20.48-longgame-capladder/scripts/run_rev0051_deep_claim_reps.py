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
from src.muc5.terminal_deep import (
    annotate_focus_rows,
    deep_claim_gate,
    deep_pair_rows,
    deep_target_summary_rows,
    strategy_ids_from_claims,
    targeted_strategy_pair_specs,
)
from src.muc5.terminal_meta import (
    claim_ledger_rows,
    life_split_stability_rows,
    rank_disagreement_rows,
    terminal_meta_gate,
    terminal_meta_rank_rows,
)

REV = "rev0051"
CODENAME = "deepclaim-lifesplitgate"
DATA = ROOT / "data"
TERMINAL_MAX_DECISIONS = 900
REPS = 2


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
    prev_claims = _read_csv_rows(DATA / "rev0050_terminal_meta_claim_ledger.csv")
    target_ids = strategy_ids_from_claims(prev_claims, top_n=3)
    if not target_ids:
        target_ids = [s.strategy_id for s in strategies[:3]]

    eval_specs = targeted_strategy_pair_specs(
        strategies,
        target_ids=target_ids,
        simulator_revision=REV,
        life_totals=(20, 40),
        reps=REPS,
        base_seed=5151000,
        max_decisions=TERMINAL_MAX_DECISIONS,
    )
    prepared = prepare_cpp_shadow_rollout(eval_specs, revision=REV)
    cpp_summary, cpp_transition_rows = finalize_cpp_shadow_rollout(prepared)

    game_rows = mark_terminal_clean_rows(
        annotate_focus_rows(list(prepared.game_rows), target_ids),
        revision=REV,
        max_decisions=TERMINAL_MAX_DECISIONS,
        strict=False,
    )
    terminal_summary = summarize_terminal_clean_rows(game_rows, revision=REV, max_decisions=TERMINAL_MAX_DECISIONS)
    aggregate = aggregate_payoff_rows(game_rows)
    standings = strategy_standings(game_rows)
    stat_standings = statistical_standings(game_rows, min_games_for_claim=64)
    pairwise = pairwise_stat_rows(game_rows, min_games_for_claim=8)
    by_strategy = terminal_clean_by_strategy(game_rows)

    meta_rows = terminal_meta_rank_rows(aggregate, life_totals=(20, 40), selection_strength=12.0)
    life_rows = life_split_stability_rows(game_rows, life_totals=(20, 40))
    disagreement = rank_disagreement_rows(standings, stat_standings, meta_rows)
    claims = claim_ledger_rows(standings, stat_standings, meta_rows, life_rows)
    target_summary = deep_target_summary_rows(game_rows, target_ids=target_ids, previous_claim_rows=prev_claims, life_totals=(20, 40))
    target_pairs = deep_pair_rows(game_rows, target_ids=target_ids)

    replay_traces, replay_results = _record_replay_samples(eval_specs, count=8)
    prepared_trace = prepare_public_traces_for_cpp(replay_traces, revision=REV)
    cpp_trace_summary, cpp_trace_rows = finalize_cpp_trace_batch(prepared_trace)

    promotion = audit_promotion_rows(
        game_rows,
        replay_results=replay_results,
        config=PromotionGateConfig(simulator_revision=REV, min_rows=300, min_replay_traces=6, max_truncation_rate=0.0),
    )
    stat_gate = audit_statistical_gate(game_rows, stat_standings, pairwise, min_raw_rows=300, max_truncation_rate=0.0)
    meta_gate = terminal_meta_gate(game_rows, aggregate, meta_rows, min_raw_rows=300, min_aggregate_games=4, require_terminal_clean=True)
    deep_gate = deep_claim_gate(game_rows, revision=REV, target_ids=target_ids, cpp_summary=cpp_summary.as_dict(), min_rows=300, min_target_games=96)

    write_csv(DATA / "rev0051_deep_claim_games.csv", game_rows)
    write_csv(DATA / "rev0051_deep_claim_aggregate.csv", aggregate)
    write_csv(DATA / "rev0051_deep_claim_standings.csv", standings)
    write_csv(DATA / "rev0051_deep_claim_stat_standings.csv", stat_standings)
    write_csv(DATA / "rev0051_deep_claim_pairwise.csv", pairwise)
    write_csv(DATA / "rev0051_deep_claim_by_strategy.csv", by_strategy)
    write_csv(DATA / "rev0051_deep_claim_metarank.csv", meta_rows)
    write_csv(DATA / "rev0051_deep_claim_life_stability.csv", life_rows)
    write_csv(DATA / "rev0051_deep_claim_rank_disagreement.csv", disagreement)
    write_csv(DATA / "rev0051_deep_claim_claim_ledger.csv", claims)
    write_csv(DATA / "rev0051_deep_claim_target_summary.csv", target_summary)
    write_csv(DATA / "rev0051_deep_claim_target_pairs.csv", target_pairs)
    write_csv(DATA / "rev0051_deep_claim_cpp_transitions.csv", [r.as_dict() for r in cpp_transition_rows])
    write_csv(DATA / "rev0051_deep_claim_cpp_trace_rows.csv", [r.as_dict() for r in cpp_trace_rows])
    write_trace_jsonl(replay_traces, DATA / "rev0051_deep_claim_replay_traces.jsonl")
    (DATA / "rev0051_deep_claim_replay_results.json").write_text(json.dumps(replay_results, indent=2))

    focus_rows = [r for r in game_rows if r.get("focus_targets")]
    summary = {
        "revision": REV,
        "codename": CODENAME,
        "based_on": "rev0050 terminal-clean claim ledger",
        "strategies": len(strategies),
        "target_ids": target_ids,
        "reps": REPS,
        "games": len(game_rows),
        "focus_rows": len(focus_rows),
        "aggregate_rows": len(aggregate),
        "target_pair_rows": len(target_pairs),
        "max_decisions": TERMINAL_MAX_DECISIONS,
        "terminal_clean_summary": terminal_summary.as_dict(),
        "promotion": promotion.as_dict(),
        "statistical_gate": stat_gate.as_dict(),
        "terminal_meta_gate": meta_gate.as_dict(),
        "deep_claim_gate": deep_gate.as_dict(),
        "cpp_shadow_summary": cpp_summary.as_dict(),
        "cpp_trace_summary": cpp_trace_summary.as_dict(),
        "replay_samples": len(replay_results),
        "replay_passed": int(sum(1 for r in replay_results if r.get("passed") is True)),
        "target_summary": target_summary,
        "target_pair_signal_counts": {
            label: sum(1 for r in target_pairs if str(r.get("pair_signal")) == label)
            for label in ("favored", "uncertain", "unfavored")
        },
        "top_meta_rank_all_life": [r for r in meta_rows if str(r.get("life_scope")) == "all"][:5],
        "top_deep_claims": target_summary[:5],
        "notes": [
            "rev0051 spends extra terminal-clean repetitions on the rev0050 claim-ledger agenda: robust and life-sensitive candidates are sampled against the full eight-strategy field.",
            "The table is focused, not a replacement for the full all-pairs population table; rows are annotated with focus_targets and focus_kind.",
            "No gameplay policy is promoted here.  This is a deeper sample / claim-gate revision for deciding where future repetitions should go.",
        ],
    }
    (DATA / "rev0051_deep_claim_summary.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
