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
from src.muc5.tournament import standard_life_configs, TournamentConfig

DATA = ROOT / "data"


def label_for_config(config: TournamentConfig) -> str:
    if not config.construction_knows_life:
        return "unknown_robust"
    return "known_life20" if config.starting_life == 20 else "known_life40"


def deck_from_shortlist_row(row: Dict[str, str]) -> DeckVector:
    return DeckVector(
        int(row["deck_size"]),
        int(row["island"]),
        int(row["counterspell"]),
        int(row["force"]),
        int(row["jace"]),
        int(row["overlord"]),
    )


def load_shortlist(top_n: int = 4) -> Dict[str, List[Dict[str, str]]]:
    path = DATA / "rev0004_life_constructor_shortlists.csv"
    if not path.exists():
        raise FileNotFoundError("run scripts/build_life_constructor_shortlists.py first")
    by_label: Dict[str, List[Dict[str, str]]] = defaultdict(list)
    with path.open() as f:
        for row in csv.DictReader(f):
            label = row["target_label"]
            if int(row["rank"]) <= top_n:
                by_label[label].append(row)
    return dict(by_label)


def _rank(wins: Counter[str], games: Counter[str]) -> List[Dict[str, object]]:
    rows = []
    for name, n in games.items():
        rows.append({"name": name, "wins": wins[name], "seat_games": n, "win_rate": wins[name] / n if n else 0.0})
    rows.sort(key=lambda r: (r["win_rate"], r["wins"], r["name"]), reverse=True)
    return rows


def main() -> None:
    shortlists = load_shortlist(top_n=4)
    agent = HeuristicAgent(name="heuristic_rev0004_lifeaware")
    rows: List[Dict[str, object]] = []
    games_per_pair = 2
    max_decisions = 600
    base_seed = 4400
    wins: Dict[str, Counter[str]] = defaultdict(Counter)
    games: Dict[str, Counter[str]] = defaultdict(Counter)
    loss_reasons: Counter[str] = Counter()

    for config in standard_life_configs():
        label = label_for_config(config)
        records = shortlists[label]
        for rec0 in records:
            for rec1 in records:
                d0 = deck_from_shortlist_row(rec0)
                d1 = deck_from_shortlist_row(rec1)
                name0 = f"{label}_r{rec0['rank']}_{d0.as_tuple()}"
                name1 = f"{label}_r{rec1['rank']}_{d1.as_tuple()}"
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
                    context_key = config.name
                    winner_name = "draw_or_timeout"
                    if result.winner == 0:
                        winner_name = name0
                        wins[context_key][name0] += 1
                    elif result.winner == 1:
                        winner_name = name1
                        wins[context_key][name1] += 1
                    games[context_key][name0] += 1
                    games[context_key][name1] += 1
                    loss_reasons[result.loss_reason] += 1
                    rows.append({
                        "seed": seed,
                        "config_name": config.name,
                        "starting_life": config.starting_life,
                        "construction_knows_life": config.construction_knows_life,
                        "constructor_label": label,
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

    out_csv = DATA / "rev0004_life_constructor_arena.csv"
    with out_csv.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    summary = {
        "rev": "rev0004",
        "agent": agent.name,
        "games": len(rows),
        "top_n_per_constructor_label": 4,
        "games_per_pair_per_config": games_per_pair,
        "max_decisions": max_decisions,
        "loss_reasons": dict(loss_reasons),
        "ranking_by_config": {k: _rank(wins[k], games[k]) for k in sorted(games)},
        "caveat": "This is a static-prior constructor arena. Learned constructors later replace the shortlist scorer.",
    }
    (DATA / "rev0004_life_constructor_arena_summary.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
