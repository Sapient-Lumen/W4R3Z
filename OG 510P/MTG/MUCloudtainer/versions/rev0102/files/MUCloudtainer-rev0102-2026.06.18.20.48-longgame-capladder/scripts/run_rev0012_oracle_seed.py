from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.muc5.payoff import load_seed_decks, mulligan_strategy_bundles, write_csv
from src.muc5.oracle_seed import generate_oracle_candidates, candidates_to_strategy_bundles
from src.muc5.public_agents import make_public_agent
from src.muc5.agents import play_public_agent_game
from src.muc5.reward_guard import reward_packet_from_state
from src.muc5.promotion import strategy_standings

REV = "rev0012"
REWARD_CONVENTION = "draw_half_reporting_terminal_only_training"
INTERFACE = "public_decision_frame"


def score(result, player: int) -> float:
    if result.winner is None:
        return 0.5
    return 1.0 if result.winner == player else 0.0


def main() -> None:
    data = ROOT / "data"
    seed_decks = load_seed_decks(data / "seed_decks.json")
    candidates = generate_oracle_candidates(list(seed_decks.values()), keep=10, random_samples=900, mutations_per_base=80)
    cand_rows = [c.as_dict() for c in candidates]
    write_csv(data / "rev0012_oracle_seed_candidates.csv", cand_rows)

    candidate_bundles = candidates_to_strategy_bundles(candidates)[:12]
    base_population = mulligan_strategy_bundles(data / "seed_decks.json")[:6]
    rows = []
    k = 0
    for candidate in candidate_bundles:
        for opponent in base_population:
            for life in (20, 40):
                for starting_player in (0, 1):
                    # Candidate in seat 0.
                    state, result = play_public_agent_game(
                        candidate.deck,
                        opponent.deck,
                        make_public_agent(candidate.agent_name),
                        make_public_agent(opponent.agent_name),
                        seed=52000 + k,
                        starting_player=starting_player,
                        starting_life=life,
                        max_decisions=500,
                        mulligan_policies=(candidate.mulligan_policy, opponent.mulligan_policy),
                        record_log=False,
                    )
                    rows.append({
                        "simulator_revision": REV,
                        "candidate_strategy": candidate.strategy_id,
                        "opponent_strategy": opponent.strategy_id,
                        "strategy0": candidate.strategy_id,
                        "strategy1": opponent.strategy_id,
                        "deck0": candidate.deck_name,
                        "deck1": opponent.deck_name,
                        "agent0": candidate.agent_name,
                        "agent1": opponent.agent_name,
                        "mulligan0": str(candidate.mulligan_policy),
                        "mulligan1": str(opponent.mulligan_policy),
                        "starting_life": life,
                        "starting_player": starting_player,
                        "seed": 52000 + k,
                        "winner": "None" if result.winner is None else str(result.winner),
                        "p0_score": score(result, 0),
                        "p1_score": score(result, 1),
                        "p0_terminal_win": 1.0 if result.winner == 0 else 0.0,
                        "p1_terminal_win": 1.0 if result.winner == 1 else 0.0,
                        "is_nonterminal_draw": result.winner is None,
                        "is_truncation": result.loss_reason == "max_decisions_reached",
                        "loss_reason": result.loss_reason,
                        "decisions": result.decisions,
                        "reward_convention": REWARD_CONVENTION,
                        "interface": INTERFACE,
                        "turn_number": state.turn_number,
                    })
                    k += 1
    write_csv(data / "rev0012_oracle_seed_games.csv", rows)
    standings = strategy_standings(rows)
    write_csv(data / "rev0012_oracle_seed_standings.csv", standings)
    summary = {
        "revision": REV,
        "candidate_decks": len(candidates),
        "candidate_strategy_bundles_evaluated": len(candidate_bundles),
        "base_opponents": len(base_population),
        "games": len(rows),
        "top_candidate_standings": [r for r in standings if str(r["strategy"]).startswith("oracle_seed_")][:8],
        "warning": "This is an oracle-seed smoke loop using static candidate priors and public heuristic pilots, not a learned best response yet.",
    }
    (data / "rev0012_oracle_seed_summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True))
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
