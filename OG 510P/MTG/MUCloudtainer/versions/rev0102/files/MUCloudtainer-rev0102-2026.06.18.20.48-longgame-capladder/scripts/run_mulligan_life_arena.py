from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean
from typing import Dict, List, Tuple
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.muc5.agents import HeuristicAgent, play_agent_game
from src.muc5.deckspace import DeckVector
from src.muc5.mulligan import MULLIGAN_POLICY_NAMES, RuleMulliganAgent
from src.muc5.tournament import LIFE_TOTAL_OPTIONS

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


def _rate_counter_to_rows(wins: Counter[str], games: Counter[str], extra: Dict[str, List[float]]) -> List[Dict[str, object]]:
    ranking = []
    for name, n_games in games.items():
        ranking.append({
            "name": name,
            "wins": wins[name],
            "seat_games": n_games,
            "win_rate": wins[name] / n_games if n_games else 0.0,
            "avg_mulligans_taken": mean(extra.get(name, [0.0])),
        })
    ranking.sort(key=lambda r: (r["win_rate"], r["wins"], -r["avg_mulligans_taken"], r["name"]), reverse=True)
    return ranking


def main() -> None:
    records = load_seed_decks()
    pilot = HeuristicAgent(name="heuristic_rev0006_mulligan_lifeaware")
    rows: List[Dict[str, object]] = []
    games_per_pair_life_policy = 2
    max_decisions = 500
    base_seed = 660_000

    bucket_wins: Dict[str, Counter[str]] = defaultdict(Counter)
    bucket_games: Dict[str, Counter[str]] = defaultdict(Counter)
    bucket_mulls: Dict[str, Dict[str, List[float]]] = defaultdict(lambda: defaultdict(list))
    policy_wins: Dict[str, Counter[str]] = defaultdict(Counter)
    policy_games: Dict[str, Counter[str]] = defaultdict(Counter)
    loss_reasons: Counter[str] = Counter()

    for life in LIFE_TOTAL_OPTIONS:
        for policy in MULLIGAN_POLICY_NAMES:
            magent = RuleMulliganAgent(policy)
            bucket = f"life{life}|{policy}"
            for i, rec0 in enumerate(records):
                for j, rec1 in enumerate(records):
                    d0 = deck_from_record(rec0)
                    d1 = deck_from_record(rec1)
                    for local_game in range(games_per_pair_life_policy):
                        starting_player = local_game % 2
                        seed = base_seed + len(rows)
                        state, result = play_agent_game(
                            d0,
                            d1,
                            pilot,
                            pilot,
                            seed=seed,
                            starting_player=starting_player,
                            max_decisions=max_decisions,
                            starting_life=life,
                            mulligan_agents=(magent, magent),
                        )
                        name0 = str(rec0["name"])
                        name1 = str(rec1["name"])
                        winner_name = "draw_or_timeout"
                        if result.winner == 0:
                            winner_name = name0
                            bucket_wins[bucket][name0] += 1
                            policy_wins[policy][name0] += 1
                        elif result.winner == 1:
                            winner_name = name1
                            bucket_wins[bucket][name1] += 1
                            policy_wins[policy][name1] += 1
                        for name in (name0, name1):
                            bucket_games[bucket][name] += 1
                            policy_games[policy][name] += 1
                        bucket_mulls[bucket][name0].append(float(state.players[0].mulligans_taken))
                        bucket_mulls[bucket][name1].append(float(state.players[1].mulligans_taken))
                        loss_reasons[result.loss_reason] += 1
                        rows.append({
                            "seed": seed,
                            "bucket": bucket,
                            "starting_life": life,
                            "mulligan_policy": policy,
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
                            "p0_mulligans": state.players[0].mulligans_taken,
                            "p1_mulligans": state.players[1].mulligans_taken,
                            "mulligan_decision_events": len(state.mulligan_decision_log),
                        })

    out_csv = DATA / "rev0006_mulligan_life_arena.csv"
    with out_csv.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    ranking_by_bucket = {
        bucket: _rate_counter_to_rows(bucket_wins[bucket], bucket_games[bucket], bucket_mulls[bucket])
        for bucket in sorted(bucket_games)
    }
    ranking_by_policy = {
        policy: _rate_counter_to_rows(policy_wins[policy], policy_games[policy], defaultdict(list))
        for policy in sorted(policy_games)
    }
    mull_by_bucket = {
        bucket: {
            "avg_mulligans_per_seat": mean(vals for deck_vals in per_deck.values() for vals in deck_vals),
            "max_avg_deck_mulligans": max((mean(vals) for vals in per_deck.values()), default=0.0),
        }
        for bucket, per_deck in bucket_mulls.items()
    }
    summary = {
        "rev": "rev0006",
        "pilot": pilot.name,
        "games": len(rows),
        "seed_decks": len(records),
        "ordered_pairs": len(records) * len(records),
        "games_per_pair_life_policy": games_per_pair_life_policy,
        "life_totals": list(LIFE_TOTAL_OPTIONS),
        "mulligan_policies": list(MULLIGAN_POLICY_NAMES),
        "loss_reasons": dict(loss_reasons),
        "ranking_by_bucket": ranking_by_bucket,
        "ranking_by_policy": ranking_by_policy,
        "mulligans_by_bucket": mull_by_bucket,
        "caveat": "The same heuristic pilot plays all games; this tests simulator plumbing and policy dials, not final strategic truth.",
    }
    out_json = DATA / "rev0006_mulligan_life_arena_summary.json"
    out_json.write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
