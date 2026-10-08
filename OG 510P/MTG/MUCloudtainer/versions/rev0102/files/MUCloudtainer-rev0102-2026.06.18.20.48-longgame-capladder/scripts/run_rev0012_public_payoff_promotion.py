from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.muc5.agents import MatchResult, play_public_agent_game
from src.muc5.payoff import aggregate_payoff_rows, mulligan_strategy_bundles, write_csv
from src.muc5.public_agents import make_public_agent
from src.muc5.promotion import PromotionGateConfig, audit_promotion_rows, strategy_standings
from src.muc5.replay import record_public_decision_trace, replay_public_decision_trace, write_trace_jsonl
from src.muc5.reward_guard import reward_packet_from_state

REV = "rev0012"
REWARD_CONVENTION = "draw_half_reporting_terminal_only_training"
INTERFACE = "public_decision_frame"


def score_for_player(result: MatchResult, player: int) -> float:
    if result.winner is None:
        return 0.5
    return 1.0 if result.winner == player else 0.0


def play_public_strategy_pair(left, right, *, seed: int, starting_player: int, starting_life: int, max_decisions: int = 500):
    state, result = play_public_agent_game(
        left.deck,
        right.deck,
        make_public_agent(left.agent_name),
        make_public_agent(right.agent_name),
        seed=seed,
        starting_player=starting_player,
        starting_life=starting_life,
        max_decisions=max_decisions,
        mulligan_policies=(left.mulligan_policy, right.mulligan_policy),
        record_log=False,
    )
    p0_packet = reward_packet_from_state(state, 0)
    p1_packet = reward_packet_from_state(state, 1)
    return {
        "simulator_revision": REV,
        "strategy0": left.strategy_id,
        "strategy1": right.strategy_id,
        "deck0": left.deck_name,
        "deck1": right.deck_name,
        "agent0": left.agent_name,
        "agent1": right.agent_name,
        "mulligan0": str(left.mulligan_policy),
        "mulligan1": str(right.mulligan_policy),
        "starting_life": int(starting_life),
        "starting_player": int(starting_player),
        "seed": int(seed),
        "winner": "None" if result.winner is None else str(result.winner),
        "p0_score": score_for_player(result, 0),
        "p1_score": score_for_player(result, 1),
        "p0_terminal_win": 1.0 if result.winner == 0 else 0.0,
        "p1_terminal_win": 1.0 if result.winner == 1 else 0.0,
        "is_nonterminal_draw": result.winner is None,
        "is_truncation": result.loss_reason == "max_decisions_reached",
        "loss_reason": result.loss_reason,
        "decisions": result.decisions,
        "log_events": result.log_events,
        "turn_number": state.turn_number,
        "reward_convention": REWARD_CONVENTION,
        "interface": INTERFACE,
        "p0_terminal_only_score": "None" if p0_packet.terminal_only_score is None else p0_packet.terminal_only_score,
        "p1_terminal_only_score": "None" if p1_packet.terminal_only_score is None else p1_packet.terminal_only_score,
    }


def main() -> None:
    data = ROOT / "data"
    strategies = mulligan_strategy_bundles(data / "seed_decks.json")
    rows = []
    k = 0
    for life in (20, 40):
        for i, left in enumerate(strategies):
            for j, right in enumerate(strategies):
                for starting_player in (0, 1):
                    seed = 12000 + k
                    row = play_public_strategy_pair(left, right, seed=seed, starting_player=starting_player, starting_life=life)
                    row["pair_index"] = f"{i}:{j}"
                    row["rep"] = 0
                    rows.append(row)
                    k += 1

    games_path = data / "rev0012_public_payoff_games.csv"
    agg_path = data / "rev0012_public_payoff_aggregate.csv"
    standings_path = data / "rev0012_public_payoff_standings.csv"
    write_csv(games_path, rows)
    write_csv(agg_path, aggregate_payoff_rows(rows))
    write_csv(standings_path, strategy_standings(rows))

    # Replay a deterministic sample across life totals and mulligan policies.
    traces = []
    replay_results = []
    sample_specs = [
        (0, 1, 20, 0),
        (1, 2, 40, 1),
        (3, 4, 20, 1),
        (5, 6, 40, 0),
        (7, 8, 20, 0),
        (8, 0, 40, 1),
    ]
    for t, (i, j, life, starting_player) in enumerate(sample_specs):
        left = strategies[i]
        right = strategies[j]
        trace = record_public_decision_trace(
            left.deck,
            right.deck,
            make_public_agent(left.agent_name),
            make_public_agent(right.agent_name),
            seed=22000 + t,
            transition_seed=32000 + t,
            agent_seed=42000 + t,
            starting_player=starting_player,
            starting_life=life,
            max_decisions=500,
            mulligan_policies=(left.mulligan_policy, right.mulligan_policy),
        )
        traces.append(trace)
        replay_results.append(replay_public_decision_trace(trace).as_dict())
    write_trace_jsonl(traces, data / "rev0012_public_payoff_replay_traces.jsonl")
    (data / "rev0012_public_payoff_replay_results.json").write_text(json.dumps(replay_results, indent=2, sort_keys=True))

    gate_config = PromotionGateConfig(min_rows=len(rows), min_replay_traces=6)
    gate = audit_promotion_rows(rows, replay_results=replay_results, config=gate_config)
    summary = {
        "revision": REV,
        "games": len(rows),
        "strategies": len(strategies),
        "life_totals": [20, 40],
        "replay_samples": len(replay_results),
        "promotion_gate": gate.as_dict(),
        "top_standings": strategy_standings(rows)[:5],
        "warning": "Smoke-scale public payoff table, not strategic truth.",
    }
    (data / "rev0012_public_payoff_summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True))
    print(json.dumps(summary, indent=2, sort_keys=True))
    if not gate.passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
