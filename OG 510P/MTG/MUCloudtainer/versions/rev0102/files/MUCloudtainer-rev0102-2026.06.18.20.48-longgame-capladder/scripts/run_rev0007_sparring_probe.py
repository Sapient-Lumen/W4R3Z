from __future__ import annotations

import csv
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.muc5.agents import make_agent, play_agent_game
from src.muc5.deckspace import DeckVector
from src.muc5.mulligan import RuleMulliganAgent

AGENTS = ["random", "heuristic", "counter_happy", "threat_rush"]
DECK_NAMES = [
    "forty_force_jace_pressure",
    "forty_overlord_impending",
    "sixty_counterwall_jace",
    "sixty_overlord_heavy",
]
LIFE_TOTALS = [20, 40]


def load_decks() -> dict[str, DeckVector]:
    payload = json.loads((ROOT / "data" / "seed_decks.json").read_text())
    out: dict[str, DeckVector] = {}
    for row in payload["seed_decks"]:
        if row["name"] not in DECK_NAMES:
            continue
        c = row["counts"]
        out[row["name"]] = DeckVector(
            int(row["size"]),
            int(c["Island"]),
            int(c["Counterspell"]),
            int(c["ForceOfWill"]),
            int(c["JaceTheMindSculptor"]),
            int(c["OverlordOfTheFloodpits"]),
        )
    return out


def main() -> None:
    decks = load_decks()
    rows: list[dict[str, object]] = []
    game_id = 0
    for life in LIFE_TOTALS:
        for agent0_name in AGENTS:
            for agent1_name in AGENTS:
                for deck0_name in DECK_NAMES:
                    for deck1_name in DECK_NAMES:
                        game_id += 1
                        seed = 7000 + game_id
                        state, result = play_agent_game(
                            decks[deck0_name],
                            decks[deck1_name],
                            make_agent(agent0_name),
                            make_agent(agent1_name),
                            seed=seed,
                            starting_player=game_id % 2,
                            max_decisions=300,
                            starting_life=life,
                            mulligan_agents=(RuleMulliganAgent("land_band"), RuleMulliganAgent("land_band")),
                        )
                        rows.append(
                            {
                                "game_id": game_id,
                                "life": life,
                                "seed": seed,
                                "starting_player": game_id % 2,
                                "agent0": agent0_name,
                                "agent1": agent1_name,
                                "deck0": deck0_name,
                                "deck1": deck1_name,
                                "winner": result.winner if result.winner is not None else "none",
                                "loss_reason": result.loss_reason,
                                "decisions": result.decisions,
                                "log_events": result.log_events,
                                "p0_mulligans": state.players[0].mulligans_taken,
                                "p1_mulligans": state.players[1].mulligans_taken,
                            }
                        )
    out_path = ROOT / "data" / "rev0007_sparring_agent_probe.csv"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    by_agent = defaultdict(lambda: Counter(games=0, wins=0, losses=0, draws=0))
    by_life = defaultdict(lambda: Counter(games=0, p0_wins=0, p1_wins=0, no_winner=0))
    for row in rows:
        winner = row["winner"]
        a0, a1 = str(row["agent0"]), str(row["agent1"])
        by_agent[a0]["games"] += 1
        by_agent[a1]["games"] += 1
        by_life[int(row["life"])] ["games"] += 1
        if winner == 0:
            by_agent[a0]["wins"] += 1
            by_agent[a1]["losses"] += 1
            by_life[int(row["life"])] ["p0_wins"] += 1
        elif winner == 1:
            by_agent[a1]["wins"] += 1
            by_agent[a0]["losses"] += 1
            by_life[int(row["life"])] ["p1_wins"] += 1
        else:
            by_agent[a0]["draws"] += 1
            by_agent[a1]["draws"] += 1
            by_life[int(row["life"])] ["no_winner"] += 1

    summary = {
        "revision": "rev0007",
        "games": len(rows),
        "agents": AGENTS,
        "deck_names": DECK_NAMES,
        "life_totals": LIFE_TOTALS,
        "by_agent": {
            agent: {
                **dict(counter),
                "win_rate": (counter["wins"] / counter["games"] if counter["games"] else 0.0),
            }
            for agent, counter in sorted(by_agent.items())
        },
        "by_life": {str(life): dict(counter) for life, counter in sorted(by_life.items())},
    }
    summary_path = ROOT / "data" / "rev0007_sparring_agent_probe_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
