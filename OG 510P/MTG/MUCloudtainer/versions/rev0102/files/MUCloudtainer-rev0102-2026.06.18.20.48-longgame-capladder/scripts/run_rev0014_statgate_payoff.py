from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.muc5.payoff import aggregate_payoff_rows, write_csv
from src.muc5.public_agents import make_public_agent
from src.muc5.public_payoff import build_public_payoff_rows
from src.muc5.promotion import PromotionGateConfig, audit_promotion_rows
from src.muc5.replay import record_public_decision_trace, replay_public_decision_trace, write_trace_jsonl
from src.muc5.statgate import audit_statistical_gate, pairwise_stat_rows, statistical_standings
from src.muc5.strategy_sets import statgate_probe_strategy_bundles

REV = "rev0014"


def main() -> None:
    data = ROOT / "data"
    strategies = statgate_probe_strategy_bundles(data / "seed_decks.json")
    rows = build_public_payoff_rows(
        strategies,
        simulator_revision=REV,
        base_seed=141400,
        max_decisions=500,
        reps=3,
    )
    games_path = data / "rev0014_statgate_payoff_games.csv"
    agg_path = data / "rev0014_statgate_payoff_aggregate.csv"
    standings_path = data / "rev0014_statgate_standings.csv"
    pair_path = data / "rev0014_statgate_pairwise.csv"
    write_csv(games_path, rows)
    write_csv(agg_path, aggregate_payoff_rows(rows))
    standings = statistical_standings(rows, min_games_for_claim=60)
    pair_rows = pairwise_stat_rows(rows, min_games_for_claim=6)
    write_csv(standings_path, standings)
    write_csv(pair_path, pair_rows)

    sample_specs = [
        (0, 2, 20, 0), (2, 3, 20, 1), (4, 0, 40, 0), (5, 1, 40, 1),
        (6, 7, 20, 0), (7, 2, 40, 1), (3, 6, 20, 1), (1, 4, 40, 0),
    ]
    traces = []
    replay_results = []
    for t, (i, j, life, starting_player) in enumerate(sample_specs):
        left = strategies[i]
        right = strategies[j]
        trace = record_public_decision_trace(
            left.deck,
            right.deck,
            make_public_agent(left.agent_name),
            make_public_agent(right.agent_name),
            seed=24140 + t,
            transition_seed=34140 + t,
            agent_seed=44140 + t,
            starting_player=starting_player,
            starting_life=life,
            max_decisions=500,
            mulligan_policies=(left.mulligan_policy, right.mulligan_policy),
        )
        traces.append(trace)
        replay_results.append(replay_public_decision_trace(trace).as_dict())
    write_trace_jsonl(traces, data / "rev0014_statgate_replay_traces.jsonl")
    (data / "rev0014_statgate_replay_results.json").write_text(json.dumps(replay_results, indent=2, sort_keys=True))

    promo = audit_promotion_rows(
        rows,
        replay_results=replay_results,
        config=PromotionGateConfig(simulator_revision=REV, min_rows=len(rows), min_replay_traces=len(replay_results)),
    )
    stat_gate = audit_statistical_gate(rows, standings, pair_rows, min_raw_rows=len(rows), max_truncation_rate=0.10)
    summary = {
        "revision": REV,
        "games": len(rows),
        "strategies": len(strategies),
        "aggregate_rows": len(list(aggregate_payoff_rows(rows))),
        "standings_rows": len(standings),
        "pairwise_rows": len(pair_rows),
        "claim_ready_strategy_count": stat_gate.claim_ready_strategy_count,
        "claim_ready_pair_count": stat_gate.claim_ready_pair_count,
        "promotion_gate": promo.as_dict(),
        "statistical_gate": stat_gate.as_dict(),
        "replay_samples": len(replay_results),
        "top_standings_lcb": standings[:8],
    }
    (data / "rev0014_statgate_summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True))
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
