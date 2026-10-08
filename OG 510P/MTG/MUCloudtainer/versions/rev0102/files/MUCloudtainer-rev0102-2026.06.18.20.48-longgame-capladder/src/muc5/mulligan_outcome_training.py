from __future__ import annotations

from dataclasses import asdict, dataclass
from random import Random
from typing import Mapping, Sequence, Tuple

from .action_schema import Action
from .cards import CARD_ORDER
from .decision import PublicDecisionAgent
from .deckspace import DeckVector
from .agents import play_public_agent_game
from .mulligan import (
    MULLIGAN_BOTTOM_KIND,
    MULLIGAN_KEEP,
    MULLIGAN_TAKE,
    MulliganObservation,
    MulliganPolicy,
    legal_bottom_actions,
    legal_mulligan_actions,
)
from .mulligan_ranker import mulligan_ranker_feature_names, mulligan_ranker_feature_vector


@dataclass(frozen=True)
class MulliganOutcomeCollectionSummary:
    """Summary for mulligan-decision rows tagged with terminal outcomes.

    The rows are pregame-only: they are built from MulliganObservation fields and
    legal London-mulligan actions.  Hidden opponent hands/libraries never enter
    the feature vectors.  Outcomes are attached only after the game ends.
    """

    games: int
    terminal_games: int
    truncated_games: int
    decision_events: int
    keep_rows: int
    bottom_rows: int
    chosen_keep_events: int
    chosen_take_events: int
    chosen_bottom_events: int
    winning_events: int
    losing_events: int
    neutral_events: int
    total_training_weight: float

    def as_dict(self) -> dict[str, object]:
        return asdict(self)


def _event_hand(event: Mapping[str, object]) -> dict[str, int]:
    return {card: int(event.get(f"hand_{card}", 0) or 0) for card in CARD_ORDER if int(event.get(f"hand_{card}", 0) or 0) > 0}


def _event_deck(event: Mapping[str, object]) -> dict[str, int]:
    return {card: int(event.get(f"deck_{card}", 0) or 0) for card in CARD_ORDER}


def _obs_from_event(event: Mapping[str, object]) -> MulliganObservation:
    hand = _event_hand(event)
    deck_counts = _event_deck(event)
    deck_total = sum(deck_counts.values())
    hand_size = int(event.get("hand_size", sum(hand.values())) or sum(hand.values()))
    library_count = max(0, deck_total - hand_size)
    return MulliganObservation(
        player=int(event.get("player", 0) or 0),
        stage=str(event.get("stage", "keep_or_mulligan")),
        mulligans_taken=int(event.get("mulligans_taken", 0) or 0),
        hand=hand,
        hand_size=hand_size,
        library_count=library_count,
        bottom_remaining=int(event.get("bottom_remaining", 0) or 0),
        starting_life=int(event.get("starting_life", 20) or 20),
        deck_counts=deck_counts,
    )


def _actor_score(winner: int | None, actor: int) -> float:
    if winner is None:
        return 0.5
    return 1.0 if int(winner) == int(actor) else 0.0


def outcome_weight_for_mulligan(score: float, *, terminal: bool) -> float:
    """Conservative trajectory weight for pregame policy learning.

    Winning terminal games are strong teachers.  Losing terminal games are kept
    at a very low weight so the model does not forget the shape of legal choices,
    but they cannot dominate.  Nonterminal truncations receive zero weight to
    avoid rewarding stall/draw-half behavior.
    """

    if not terminal:
        return 0.0
    if score >= 0.999:
        return 1.0
    if score <= 0.001:
        return 0.08
    return 0.0


def _legal_from_obs(obs: MulliganObservation) -> list[Action]:
    from collections import Counter

    hand_counter = Counter(obs.hand)
    if obs.stage == "keep_or_mulligan":
        return legal_mulligan_actions(hand_counter, obs.mulligans_taken)
    if obs.stage == "bottom":
        return legal_bottom_actions(hand_counter)
    return []


def candidate_rows_from_mulligan_event(
    event: Mapping[str, object],
    *,
    game_index: int,
    event_index: int,
    winner: int | None,
    terminal: bool,
    strategy_id: str,
) -> tuple[list[dict[str, object]], list[dict[str, object]], dict[str, object]]:
    """Expand one recorded MulliganDecisionEvent row into legal candidate rows."""

    obs = _obs_from_event(event)
    legal = _legal_from_obs(obs)
    chosen_compact = str(event.get("action", ""))
    actor = int(obs.player)
    score = _actor_score(winner, actor)
    weight = outcome_weight_for_mulligan(score, terminal=terminal)
    features = list(mulligan_ranker_feature_names())
    keep_rows: list[dict[str, object]] = []
    bottom_rows: list[dict[str, object]] = []
    example_id = f"g{game_index:05d}_m{event_index:03d}_p{actor}"

    if obs.stage == "keep_or_mulligan":
        label_keep = 1 if chosen_compact == MULLIGAN_KEEP.compact() else 0
        fd = dict(zip(features, mulligan_ranker_feature_vector(obs)))
        keep_rows.append({
            "example_id": example_id,
            "game_index": int(game_index),
            "event_index": int(event_index),
            "strategy_id": strategy_id,
            "player": actor,
            "agent_name": str(event.get("agent_name", "")),
            "stage": obs.stage,
            "mulligans_taken": int(obs.mulligans_taken),
            "starting_life": int(obs.starting_life),
            "chosen_action": chosen_compact,
            "label_keep": int(label_keep),
            "actor_terminal_score": float(score),
            "outcome_weight": float(weight),
            "terminal": 1 if terminal else 0,
            "winner": "None" if winner is None else int(winner),
            **fd,
        })
    elif obs.stage == "bottom":
        for action in legal:
            card = str(action.params.get("card", ""))
            fd = dict(zip(features, mulligan_ranker_feature_vector(obs, card)))
            bottom_rows.append({
                "example_id": example_id,
                "game_index": int(game_index),
                "event_index": int(event_index),
                "strategy_id": strategy_id,
                "player": actor,
                "agent_name": str(event.get("agent_name", "")),
                "stage": obs.stage,
                "mulligans_taken": int(obs.mulligans_taken),
                "bottom_remaining": int(obs.bottom_remaining),
                "starting_life": int(obs.starting_life),
                "candidate_card": card,
                "candidate_action": action.compact(),
                "chosen_action": chosen_compact,
                "label_bottom": 1 if action.compact() == chosen_compact else 0,
                "actor_terminal_score": float(score),
                "outcome_weight": float(weight),
                "terminal": 1 if terminal else 0,
                "winner": "None" if winner is None else int(winner),
                **fd,
            })
    event_summary = {
        "stage": obs.stage,
        "label_keep": 1 if chosen_compact == MULLIGAN_KEEP.compact() else 0,
        "label_take": 1 if chosen_compact == MULLIGAN_TAKE.compact() else 0,
        "label_bottom": 1 if chosen_compact.startswith(MULLIGAN_BOTTOM_KIND) else 0,
        "score": float(score),
        "weight": float(weight),
        "terminal": bool(terminal),
    }
    return keep_rows, bottom_rows, event_summary


def collect_outcome_weighted_mulligan_rows(
    games: Sequence[
        tuple[
            DeckVector,
            DeckVector,
            PublicDecisionAgent,
            PublicDecisionAgent,
            int,
            int,
            tuple[str | MulliganPolicy | object | None, str | MulliganPolicy | object | None],
            str,
            str,
        ]
    ],
    *,
    seed_base: int = 2702700,
    max_decisions: int = 520,
) -> tuple[list[dict[str, object]], list[dict[str, object]], MulliganOutcomeCollectionSummary]:
    """Collect outcome-weighted rows for keep/take and bottom-card models.

    Each game tuple is ``deck0, deck1, agent0, agent1, starting_player,
    starting_life, mulligan_agents, strategy0_id, strategy1_id``.
    """

    keep_rows: list[dict[str, object]] = []
    bottom_rows: list[dict[str, object]] = []
    terminal_games = 0
    truncated_games = 0
    decision_events = 0
    chosen_keep = 0
    chosen_take = 0
    chosen_bottom = 0
    winning_events = 0
    losing_events = 0
    neutral_events = 0
    total_weight = 0.0

    for game_i, (deck0, deck1, agent0, agent1, starting_player, starting_life, mulligans, strategy0_id, strategy1_id) in enumerate(games):
        seed = seed_base + game_i
        state, result = play_public_agent_game(
            deck0,
            deck1,
            agent0,
            agent1,
            seed=seed,
            transition_seed=seed,
            agent_seed=seed + 1000003,
            starting_player=starting_player,
            starting_life=starting_life,
            max_decisions=max_decisions,
            mulligan_agents=mulligans,  # type: ignore[arg-type]
            record_log=False,
        )
        terminal = result.winner is not None
        if terminal:
            terminal_games += 1
        else:
            truncated_games += 1
        strategy_for_player = {0: strategy0_id, 1: strategy1_id}
        for event_i, event in enumerate(state.mulligan_decision_log):
            decision_events += 1
            actor = int(event.get("player", 0) or 0)
            kr, br, es = candidate_rows_from_mulligan_event(
                event,
                game_index=game_i,
                event_index=event_i,
                winner=result.winner,
                terminal=terminal,
                strategy_id=strategy_for_player.get(actor, "unknown"),
            )
            keep_rows.extend(kr)
            bottom_rows.extend(br)
            chosen_keep += int(es["label_keep"])
            chosen_take += int(es["label_take"])
            chosen_bottom += int(es["label_bottom"])
            score = float(es["score"])
            if terminal and score >= 0.999:
                winning_events += 1
            elif terminal and score <= 0.001:
                losing_events += 1
            else:
                neutral_events += 1
            total_weight += float(es["weight"])

    summary = MulliganOutcomeCollectionSummary(
        games=len(games),
        terminal_games=terminal_games,
        truncated_games=truncated_games,
        decision_events=decision_events,
        keep_rows=len(keep_rows),
        bottom_rows=len(bottom_rows),
        chosen_keep_events=chosen_keep,
        chosen_take_events=chosen_take,
        chosen_bottom_events=chosen_bottom,
        winning_events=winning_events,
        losing_events=losing_events,
        neutral_events=neutral_events,
        total_training_weight=total_weight,
    )
    return keep_rows, bottom_rows, summary
