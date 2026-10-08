from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.muc5.metarank import meta_rank_from_aggregate
from src.muc5.payoff import aggregate_payoff_rows, write_csv
from src.muc5.public_agents import make_public_agent
from src.muc5.public_payoff import build_public_payoff_rows
from src.muc5.promotion import PromotionGateConfig, audit_promotion_rows
from src.muc5.replay import record_public_decision_trace, replay_public_decision_trace, write_trace_jsonl
from src.muc5.statgate import audit_statistical_gate, pairwise_stat_rows, statistical_standings
from src.muc5.strategy_sets import statgate_probe_strategy_bundles

REV = "rev0017"


def main() -> None:
    data = ROOT / "data"
    strategies = statgate_probe_strategy_bundles(data / "seed_decks.json")
    rows = build_public_payoff_rows(
        strategies,
        simulator_revision=REV,
        base_seed=171700,
        max_decisions=500,
        reps=2,
    )
    aggregate = aggregate_payoff_rows(rows)
    standings = statistical_standings(rows, min_games_for_claim=40)
    pair_rows = pairwise_stat_rows(rows, min_games_for_claim=4)
    metarank_all = [r.as_dict() for r in meta_rank_from_aggregate(aggregate)]
    metarank_20 = [r.as_dict() for r in meta_rank_from_aggregate(aggregate, life=20)]
    metarank_40 = [r.as_dict() for r in meta_rank_from_aggregate(aggregate, life=40)]

    write_csv(data / f"{REV}_metarank_payoff_games.csv", rows)
    write_csv(data / f"{REV}_metarank_payoff_aggregate.csv", aggregate)
    write_csv(data / f"{REV}_metarank_standings.csv", standings)
    write_csv(data / f"{REV}_metarank_pairwise.csv", pair_rows)
    write_csv(data / f"{REV}_metarank_all.csv", metarank_all)
    write_csv(data / f"{REV}_metarank_life20.csv", metarank_20)
    write_csv(data / f"{REV}_metarank_life40.csv", metarank_40)

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
            seed=27170 + t,
            transition_seed=37170 + t,
            agent_seed=47170 + t,
            starting_player=starting_player,
            starting_life=life,
            max_decisions=500,
            mulligan_policies=(left.mulligan_policy, right.mulligan_policy),
        )
        traces.append(trace)
        replay_results.append(replay_public_decision_trace(trace).as_dict())
    write_trace_jsonl(traces, data / f"{REV}_metarank_replay_traces.jsonl")
    (data / f"{REV}_metarank_replay_results.json").write_text(json.dumps(replay_results, indent=2, sort_keys=True))

    promo = audit_promotion_rows(
        rows,
        replay_results=replay_results,
        config=PromotionGateConfig(simulator_revision=REV, min_rows=len(rows), min_replay_traces=len(replay_results)),
    )
    stat_gate = audit_statistical_gate(rows, standings, pair_rows, min_raw_rows=len(rows), max_truncation_rate=0.10)
    rank_disagreement = []
    stand_map = {r["strategy"]: int(r["rank_by_lcb"]) for r in standings}
    for i, r in enumerate(metarank_all, 1):
        rank_disagreement.append(
            {
                "strategy": r["strategy"],
                "metarank_rank": i,
                "standings_rank_by_lcb": stand_map.get(r["strategy"]),
                "meta_rank_mass": r["meta_rank_mass"],
            }
        )
    write_csv(data / f"{REV}_metarank_rank_disagreement.csv", rank_disagreement)

    summary = {
        "revision": REV,
        "games": len(rows),
        "strategies": len(strategies),
        "aggregate_rows": len(aggregate),
        "promotion_gate": promo.as_dict(),
        "statistical_gate": stat_gate.as_dict(),
        "replay_samples": len(replay_results),
        "top_standings_lcb": standings[:5],
        "top_metarank_all": metarank_all[:5],
        "top_metarank_20": metarank_20[:3],
        "top_metarank_40": metarank_40[:3],
        "rank_disagreement_top": rank_disagreement[:8],
    }
    (data / f"{REV}_metarank_summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True))
    print(json.dumps(summary, indent=2, sort_keys=True))
    if not promo.passed or not stat_gate.passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
