from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.muc5.deckspace import DeckVector
from src.muc5.mulligan import POLICY_LAND_BAND, POLICY_LAND_BAND_BUSINESS
from src.muc5.payoff import StrategyBundle, aggregate_payoff_rows, write_csv
from src.muc5.public_agents import make_public_agent
from src.muc5.public_payoff import build_public_payoff_rows
from src.muc5.promotion import PromotionGateConfig, audit_promotion_rows
from src.muc5.replay import record_public_decision_trace, replay_public_decision_trace, write_trace_jsonl
from src.muc5.statgate import audit_statistical_gate, pairwise_stat_rows, statistical_standings

REV = "rev0015"


def selected_mapelite_bundles(path: Path, *, cells: int = 4) -> list[StrategyBundle]:
    rows = list(csv.DictReader(path.open()))
    chosen = rows[:cells]
    bundles: list[StrategyBundle] = []
    for rank, row in enumerate(chosen, 1):
        deck = DeckVector(
            int(row["deck_size"]),
            int(row["island"]),
            int(row["counterspell"]),
            int(row["force"]),
            int(row["jace"]),
            int(row["overlord"]),
        )
        # Pair each elite with two distinct public profiles so we learn whether
        # a static construction prior survives different pilots.
        bundles.append(StrategyBundle(f"me{rank}_heur", f"mapelite_{rank}_{row['cell_id']}", deck, "heuristic", POLICY_LAND_BAND))
        if rank <= 2:
            bundles.append(StrategyBundle(f"me{rank}_threat", f"mapelite_{rank}_{row['cell_id']}", deck, "threat_rush", POLICY_LAND_BAND_BUSINESS))
    return bundles[:6]


def main() -> None:
    data = ROOT / "data"
    strategies = selected_mapelite_bundles(data / "rev0014_map_elites_archive.csv", cells=4)
    rows = build_public_payoff_rows(strategies, simulator_revision=REV, reps=2, base_seed=151500, max_decisions=500)
    write_csv(data / "rev0015_mapelite_eval_games.csv", rows)
    write_csv(data / "rev0015_mapelite_eval_aggregate.csv", aggregate_payoff_rows(rows))
    standings = statistical_standings(rows, min_games_for_claim=40)
    pair_rows = pairwise_stat_rows(rows, min_games_for_claim=4)
    write_csv(data / "rev0015_mapelite_eval_standings.csv", standings)
    write_csv(data / "rev0015_mapelite_eval_pairwise.csv", pair_rows)

    sample_specs = [(0, 1, 20, 0), (1, 2, 20, 1), (2, 3, 40, 0), (3, 4, 40, 1), (4, 5, 20, 0), (5, 0, 40, 1)]
    traces = []
    replay_results = []
    for t, (i, j, life, starting_player) in enumerate(sample_specs):
        left = strategies[i % len(strategies)]
        right = strategies[j % len(strategies)]
        trace = record_public_decision_trace(
            left.deck,
            right.deck,
            make_public_agent(left.agent_name),
            make_public_agent(right.agent_name),
            seed=25150 + t,
            transition_seed=35150 + t,
            agent_seed=45150 + t,
            starting_player=starting_player,
            starting_life=life,
            max_decisions=500,
            mulligan_policies=(left.mulligan_policy, right.mulligan_policy),
        )
        traces.append(trace)
        replay_results.append(replay_public_decision_trace(trace).as_dict())
    write_trace_jsonl(traces, data / "rev0015_mapelite_eval_replay_traces.jsonl")
    (data / "rev0015_mapelite_eval_replay_results.json").write_text(json.dumps(replay_results, indent=2, sort_keys=True))

    promo = audit_promotion_rows(rows, replay_results=replay_results, config=PromotionGateConfig(simulator_revision=REV, min_rows=len(rows), min_replay_traces=6, max_truncation_rate=0.20))
    stat_gate = audit_statistical_gate(rows, standings, pair_rows, min_raw_rows=len(rows), max_truncation_rate=0.20)
    summary = {
        "revision": REV,
        "strategies": [s.as_dict() for s in strategies],
        "games": len(rows),
        "aggregate_rows": len(aggregate_payoff_rows(rows)),
        "standings_rows": len(standings),
        "pairwise_rows": len(pair_rows),
        "promotion_gate": promo.as_dict(),
        "statistical_gate": stat_gate.as_dict(),
        "truncation_games": sum(1 for r in rows if r.get("is_truncation")),
        "note": "Selected MAP-Elites cells are now evaluated by actual public DecisionFrame games; still smoke-scale.",
    }
    (data / "rev0015_mapelite_eval_summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True))
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
