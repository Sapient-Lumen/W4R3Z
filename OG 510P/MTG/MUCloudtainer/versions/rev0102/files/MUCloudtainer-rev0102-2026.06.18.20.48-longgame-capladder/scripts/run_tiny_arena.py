from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, List
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.muc5.agents import HeuristicAgent, play_agent_game
from src.muc5.deckspace import DeckVector

DATA = ROOT / "data"


def deck_from_record(record: Dict[str, object]) -> DeckVector:
    counts = record["counts"]
    assert isinstance(counts, dict)
    return DeckVector(
        int(record["size"]),
        int(counts["Island"]),
        int(counts["Counterspell"]),
        int(counts["ForceOfWill"]),
        int(counts["JaceTheMindSculptor"]),
        int(counts["OverlordOfTheFloodpits"]),
    )


def load_seed_decks() -> List[Dict[str, object]]:
    payload = json.loads((DATA / "seed_decks.json").read_text())
    return list(payload["seed_decks"])


def main() -> None:
    records = load_seed_decks()
    agent = HeuristicAgent()
    rows: List[Dict[str, object]] = []
    deck_wins: Counter[str] = Counter()
    deck_games: Counter[str] = Counter()
    loss_reasons: Counter[str] = Counter()
    max_decisions = 400
    game_seed = 3000
    games_per_pair = 2  # one starting-player swap per ordered pair

    for i, rec0 in enumerate(records):
        for j, rec1 in enumerate(records):
            d0 = deck_from_record(rec0)
            d1 = deck_from_record(rec1)
            for local_game in range(games_per_pair):
                starting_player = local_game % 2
                seed = game_seed + len(rows)
                state, result = play_agent_game(
                    d0,
                    d1,
                    agent,
                    agent,
                    seed=seed,
                    starting_player=starting_player,
                    max_decisions=max_decisions,
                )
                name0 = str(rec0["name"])
                name1 = str(rec1["name"])
                winner_name = "draw_or_timeout"
                if result.winner == 0:
                    winner_name = name0
                    deck_wins[name0] += 1
                elif result.winner == 1:
                    winner_name = name1
                    deck_wins[name1] += 1
                deck_games[name0] += 1
                deck_games[name1] += 1
                loss_reasons[result.loss_reason] += 1
                rows.append(
                    {
                        "seed": seed,
                        "deck0_name": name0,
                        "deck1_name": name1,
                        "deck0_tuple": d0.as_tuple(),
                        "deck1_tuple": d1.as_tuple(),
                        "starting_player": starting_player,
                        "winner_index": result.winner,
                        "winner_name": winner_name,
                        "loss_reason": result.loss_reason,
                        "decisions": result.decisions,
                        "log_events": result.log_events,
                    }
                )

    out_csv = DATA / "rev0003_tiny_arena.csv"
    with out_csv.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    ranking = []
    for name, games in deck_games.items():
        ranking.append({"name": name, "wins": deck_wins[name], "seat_games": games, "win_rate": deck_wins[name] / games if games else 0.0})
    ranking.sort(key=lambda r: (r["win_rate"], r["wins"]), reverse=True)

    summary = {
        "rev": "rev0003",
        "agent": agent.name,
        "max_decisions": max_decisions,
        "games": len(rows),
        "ordered_pairs": len(records) * len(records),
        "games_per_pair": games_per_pair,
        "loss_reasons": dict(loss_reasons),
        "ranking_by_seat_win_rate": ranking,
        "note": "Tiny heuristic-vs-heuristic arena. This is plumbing data, not strategic evidence yet.",
    }
    (DATA / "rev0003_tiny_arena_summary.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
