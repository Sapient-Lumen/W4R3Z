from __future__ import annotations

import csv
import json
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Mapping, Sequence

from .agents import MatchResult, make_agent, play_agent_game
from .cards import STARTING_LIFE_OPTIONS
from .deckspace import DeckVector
from .mulligan import POLICY_KEEP_ALWAYS, POLICY_LAND_BAND, POLICY_LAND_BAND_BUSINESS, MulliganPolicy
from .mulligan_ranker import make_mulligan_agent


@dataclass(frozen=True)
class StrategyBundle:
    """A population-strategy unit for early MUC-5 payoff tables.

    A future PSRO/NFSP/CFR branch can replace any component with a learned object,
    but the table key should stay stable: construction + mulligan policy + pilot.
    """

    strategy_id: str
    deck_name: str
    deck: DeckVector
    agent_name: str
    mulligan_policy: str | MulliganPolicy = POLICY_LAND_BAND

    def as_dict(self) -> Dict[str, object]:
        return {
            "strategy_id": self.strategy_id,
            "deck_name": self.deck_name,
            "agent_name": self.agent_name,
            "mulligan_policy": str(self.mulligan_policy),
            **{f"deck_{k}": v for k, v in self.deck.counts().items()},
            "deck_size": self.deck.size,
        }


def load_seed_decks(path: str | Path) -> Dict[str, DeckVector]:
    payload = json.loads(Path(path).read_text())
    decks: Dict[str, DeckVector] = {}
    for row in payload["seed_decks"]:
        counts = row["counts"]
        deck = DeckVector(
            int(row["size"]),
            int(counts.get("Island", 0)),
            int(counts.get("Counterspell", 0)),
            int(counts.get("ForceOfWill", 0)),
            int(counts.get("JaceTheMindSculptor", 0)),
            int(counts.get("OverlordOfTheFloodpits", 0)),
        )
        deck.validate()
        decks[str(row["name"])] = deck
    return decks


def default_strategy_bundles(seed_decks_path: str | Path) -> List[StrategyBundle]:
    """Small fixed population for smoke-payoff tables.

    This is not a metagame claim. It deliberately mixes deck shapes and pilot
    personalities so the payoff-table machinery has nontrivial axes. The default
    rev0008 population used one shared mulligan baseline; rev0009 keeps that
    function stable and adds ``mulligan_strategy_bundles`` for explicit policy
    variation.
    """

    decks = load_seed_decks(seed_decks_path)
    plan = [
        ("fjace_bal", "forty_force_jace_pressure", "heuristic"),
        ("fovr_threat", "forty_overlord_impending", "threat_rush"),
        ("flight_counter", "forty_land_light_force_comboish", "counter_happy"),
        ("sibig_bal", "sixty_drawless_control_big", "heuristic"),
        ("siovr_threat", "sixty_overlord_heavy", "threat_rush"),
        ("sicounter_counter", "sixty_counterwall_jace", "counter_happy"),
        ("gambit_counter", "forty_minimal_threat_decking_gambit", "counter_happy"),
        ("jaceonly_bal", "sixty_no_overlord_jace_only", "heuristic"),
    ]
    return [StrategyBundle(sid, deck_name, decks[deck_name], agent_name) for sid, deck_name, agent_name in plan]


def mulligan_strategy_bundles(seed_decks_path: str | Path) -> List[StrategyBundle]:
    """Tiny population that varies mulligan policy as part of the bundle.

    This exists because mulligan policy must become an agent choice, not a hidden
    shared tournament parameter. It also prevents a subtle evaluation bug: when
    two strategies use different mulligan policies, each seat must run its own
    policy rather than silently falling back to no mulligan.
    """

    decks = load_seed_decks(seed_decks_path)
    base = [
        ("fjace", "forty_force_jace_pressure", "heuristic"),
        ("ovr", "forty_overlord_impending", "threat_rush"),
        ("sicounter", "sixty_counterwall_jace", "counter_happy"),
    ]
    policies = [POLICY_KEEP_ALWAYS, POLICY_LAND_BAND, POLICY_LAND_BAND_BUSINESS]
    out: List[StrategyBundle] = []
    for sid, deck_name, agent_name in base:
        for pol in policies:
            out.append(StrategyBundle(f"{sid}_{pol}", deck_name, decks[deck_name], agent_name, pol))
    return out


def game_score_for_player(result: MatchResult, player: int) -> float:
    if result.winner is None:
        return 0.5
    return 1.0 if result.winner == player else 0.0


def play_strategy_pair(
    left: StrategyBundle,
    right: StrategyBundle,
    *,
    seed: int,
    starting_player: int,
    starting_life: int,
    max_decisions: int = 500,
    validate_actions: bool = False,
) -> Dict[str, object]:
    state, result = play_agent_game(
        left.deck,
        right.deck,
        make_agent(left.agent_name),
        make_agent(right.agent_name),
        seed=seed,
        starting_player=starting_player,
        max_decisions=max_decisions,
        starting_life=starting_life,
        mulligan_policy=None,
        mulligan_agents=(make_mulligan_agent(left.mulligan_policy), make_mulligan_agent(right.mulligan_policy)),
        validate_actions=validate_actions,
        record_log=False,
    )
    return {
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
        "p0_score": game_score_for_player(result, 0),
        "p1_score": game_score_for_player(result, 1),
        "p0_terminal_win": 1.0 if result.winner == 0 else 0.0,
        "p1_terminal_win": 1.0 if result.winner == 1 else 0.0,
        "is_nonterminal_draw": result.winner is None,
        "is_truncation": str(result.loss_reason) == "max_decisions_reached",
        "loss_reason": result.loss_reason,
        "decisions": result.decisions,
        "log_events": result.log_events,
        "turn_number": state.turn_number,
    }


def build_payoff_rows(
    strategies: Sequence[StrategyBundle],
    *,
    life_totals: Sequence[int] = STARTING_LIFE_OPTIONS,
    reps: int = 1,
    base_seed: int = 8000,
    max_decisions: int = 500,
) -> List[Dict[str, object]]:
    rows: List[Dict[str, object]] = []
    k = 0
    for life in life_totals:
        for i, left in enumerate(strategies):
            for j, right in enumerate(strategies):
                for starting_player in (0, 1):
                    for rep in range(reps):
                        seed = base_seed + k
                        rows.append(
                            play_strategy_pair(
                                left,
                                right,
                                seed=seed,
                                starting_player=starting_player,
                                starting_life=int(life),
                                max_decisions=max_decisions,
                            )
                        )
                        rows[-1]["rep"] = rep
                        rows[-1]["pair_index"] = f"{i}:{j}"
                        k += 1
    return rows


def aggregate_payoff_rows(rows: Iterable[Mapping[str, object]]) -> List[Dict[str, object]]:
    grouped: dict[tuple[str, str, int], list[Mapping[str, object]]] = defaultdict(list)
    for row in rows:
        grouped[(str(row["strategy0"]), str(row["strategy1"]), int(row["starting_life"]))].append(row)
    out: List[Dict[str, object]] = []
    for (s0, s1, life), group in sorted(grouped.items()):
        n = len(group)
        mean_score = sum(float(r["p0_score"]) for r in group) / max(1, n)
        mean_terminal_win = sum(float(r.get("p0_terminal_win", 0.0)) for r in group) / max(1, n)
        mean_decisions = sum(float(r["decisions"]) for r in group) / max(1, n)
        maxed = sum(1 for r in group if str(r.get("loss_reason")) == "max_decisions_reached")
        out.append(
            {
                "strategy0": s0,
                "strategy1": s1,
                "starting_life": life,
                "games": n,
                "p0_mean_score_draw_half": mean_score,
                "p1_mean_score_draw_half": 1.0 - mean_score,
                "p0_terminal_win_rate": mean_terminal_win,
                "mean_decisions": mean_decisions,
                "max_decision_games": maxed,
            }
        )
    return out


def write_csv(path: str | Path, rows: Sequence[Mapping[str, object]]) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("")
        return
    fields = list(rows[0].keys())
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
