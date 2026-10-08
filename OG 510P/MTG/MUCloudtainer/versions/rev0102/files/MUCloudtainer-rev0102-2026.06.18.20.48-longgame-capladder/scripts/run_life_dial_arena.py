from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, List, Tuple
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.muc5.agents import HeuristicAgent, play_agent_game
from src.muc5.deckspace import DeckVector
from src.muc5.tournament import standard_life_configs

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


def _rate_counter_to_rows(wins: Counter[str], games: Counter[str]) -> List[Dict[str, object]]:
    ranking = []
    for name, n_games in games.items():
        ranking.append({
            "name": name,
            "wins": wins[name],
            "seat_games": n_games,
            "win_rate": wins[name] / n_games if n_games else 0.0,
        })
    ranking.sort(key=lambda r: (r["win_rate"], r["wins"], r["name"]), reverse=True)
    return ranking


def main() -> None:
    records = load_seed_decks()
    agent = HeuristicAgent(name="heuristic_rev0004_lifeaware")
    rows: List[Dict[str, object]] = []
    games_per_pair = 2
    max_decisions = 500
    base_seed = 4000

    context_wins: Dict[str, Counter[str]] = defaultdict(Counter)
    context_games: Dict[str, Counter[str]] = defaultdict(Counter)
    actual_life_wins: Dict[int, Counter[str]] = defaultdict(Counter)
    actual_life_games: Dict[int, Counter[str]] = defaultdict(Counter)
    loss_reasons: Counter[str] = Counter()

    for config in standard_life_configs():
        for i, rec0 in enumerate(records):
            for j, rec1 in enumerate(records):
                d0 = deck_from_record(rec0)
                d1 = deck_from_record(rec1)
                for local_game in range(games_per_pair):
                    starting_player = local_game % 2
                    seed = base_seed + len(rows)
                    state, result = play_agent_game(
                        d0,
                        d1,
                        agent,
                        agent,
                        seed=seed,
                        starting_player=starting_player,
                        max_decisions=max_decisions,
                        starting_life=config.starting_life,
                    )
                    name0 = str(rec0["name"])
                    name1 = str(rec1["name"])
                    winner_name = "draw_or_timeout"
                    if result.winner == 0:
                        winner_name = name0
                        context_wins[config.name][name0] += 1
                        actual_life_wins[config.starting_life][name0] += 1
                    elif result.winner == 1:
                        winner_name = name1
                        context_wins[config.name][name1] += 1
                        actual_life_wins[config.starting_life][name1] += 1
                    for name in (name0, name1):
                        context_games[config.name][name] += 1
                        actual_life_games[config.starting_life][name] += 1
                    loss_reasons[result.loss_reason] += 1
                    rows.append({
                        "seed": seed,
                        "config_name": config.name,
                        "starting_life": config.starting_life,
                        "construction_knows_life": config.construction_knows_life,
                        "constructor_known_life": config.construction_context.known_starting_life,
                        "constructor_possible_life_totals": "|".join(map(str, config.construction_context.possible_starting_life_totals)),
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
                    })

    out_csv = DATA / "rev0004_life_dial_arena.csv"
    with out_csv.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    ranking_by_context = {name: _rate_counter_to_rows(context_wins[name], context_games[name]) for name in sorted(context_games)}
    ranking_by_actual_life = {str(life): _rate_counter_to_rows(actual_life_wins[life], actual_life_games[life]) for life in sorted(actual_life_games)}

    # A robust/unknown constructor would pick by average actual-life performance, not by knowing the draw.
    average_by_life: Dict[str, List[float]] = defaultdict(list)
    for life, ranking in ranking_by_actual_life.items():
        for row in ranking:
            average_by_life[str(row["name"])].append(float(row["win_rate"]))
    robust_unknown_ranking = [
        {"name": name, "mean_life_win_rate": sum(vals) / len(vals), "life_rates": vals}
        for name, vals in average_by_life.items()
    ]
    robust_unknown_ranking.sort(key=lambda r: (r["mean_life_win_rate"], r["name"]), reverse=True)

    known_best = {life: rows[0]["name"] if rows else None for life, rows in ranking_by_actual_life.items()}
    summary = {
        "rev": "rev0004",
        "agent": agent.name,
        "games": len(rows),
        "seed_decks": len(records),
        "ordered_pairs": len(records) * len(records),
        "games_per_pair_per_config": games_per_pair,
        "max_decisions": max_decisions,
        "configs": [config.as_dict() for config in standard_life_configs()],
        "loss_reasons": dict(loss_reasons),
        "ranking_by_context": ranking_by_context,
        "ranking_by_actual_life": ranking_by_actual_life,
        "known_best_by_actual_life": known_best,
        "robust_unknown_ranking": robust_unknown_ranking,
        "important_caveat": "Known-vs-unknown construction is represented as context metadata and seed-deck rankings here. It becomes a real constructor experiment once constructors choose decks conditionally on ConstructionContext.",
    }
    (DATA / "rev0004_life_dial_arena_summary.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
