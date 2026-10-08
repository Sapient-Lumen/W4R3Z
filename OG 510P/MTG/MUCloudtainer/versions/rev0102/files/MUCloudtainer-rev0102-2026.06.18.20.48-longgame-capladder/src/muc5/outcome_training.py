from __future__ import annotations

from dataclasses import asdict, dataclass
from random import Random
from typing import Sequence

from .action_features import action_feature_dict
from .decision import PublicDecisionAgent, apply_decision_index, build_decision_frame
from .deckspace import DeckVector
from .engine import start_game
from .imitation import context_feature_dict
from .mulligan import MulliganPolicy


@dataclass(frozen=True)
class OutcomeCollectionSummary:
    """Summary for public trajectory rows tagged with terminal outcomes."""

    games: int
    terminal_games: int
    truncated_games: int
    decisions: int
    rows: int
    chosen_rows: int
    winning_chosen_rows: int
    losing_chosen_rows: int
    neutral_chosen_rows: int
    max_action_count: int
    mean_action_count: float
    total_training_weight: float

    def as_dict(self) -> dict[str, object]:
        return asdict(self)


def _actor_score(winner: int | None, actor: int) -> float:
    if winner is None:
        return 0.5
    return 1.0 if int(winner) == int(actor) else 0.0


def outcome_weight_for_score(score: float, *, terminal: bool) -> float:
    """Conservative weighted-behavior-cloning weight.

    Winning trajectories become strong teachers. Losing terminal trajectories are
    retained at low weight so the model still sees legal alternatives from hard
    states, but they do not dominate. Nonterminal truncations deliberately carry
    zero training weight; they may be reported, but they are not a positive
    teacher. This is a small guardrail against learning to stall into draw-half
    reporting scores.
    """

    if not terminal:
        return 0.0
    if score >= 0.999:
        return 1.0
    if score <= 0.001:
        return 0.15
    return 0.0


def collect_outcome_weighted_action_rows(
    games: Sequence[
        tuple[
            DeckVector,
            DeckVector,
            PublicDecisionAgent,
            PublicDecisionAgent,
            int,
            int,
            tuple[str | MulliganPolicy | None, str | MulliganPolicy | None],
        ]
    ],
    *,
    seed_base: int = 2502500,
    max_decisions: int = 420,
) -> tuple[list[dict[str, object]], OutcomeCollectionSummary]:
    """Collect public candidate-action rows and tag them with terminal outcome.

    This is the first outcome-weighted policy-improvement dataset. It still uses
    behavior-policy actions, not search or counterfactual values: for every
    public DecisionFrame, it records every legal action candidate, which action
    was chosen, and the eventual terminal score for the player who made that
    decision. Hidden hands/libraries never enter row features; rows are built from
    the same public context/action features used by imitation rankers.
    """

    all_rows: list[dict[str, object]] = []
    decisions = 0
    terminal_games = 0
    truncated_games = 0
    action_counts: list[int] = []
    winning_chosen = 0
    losing_chosen = 0
    neutral_chosen = 0
    total_weight = 0.0

    for game_i, (deck0, deck1, agent0, agent1, starting_player, starting_life, mulligans) in enumerate(games):
        state_seed = seed_base + game_i
        state_rng = Random(state_seed)
        agent_rng = Random(seed_base + 100000 + game_i)
        state = start_game(
            deck0,
            deck1,
            seed=state_seed,
            starting_player=starting_player,
            starting_life=starting_life,
            mulligan_policies=mulligans,
            record_log=False,
        )
        agents = [agent0, agent1]
        game_rows: list[dict[str, object]] = []
        for step in range(1, max_decisions + 1):
            if state.winner is not None:
                break
            frame = build_decision_frame(state)
            if frame.action_count <= 0:
                break
            chosen_idx = int(agents[frame.player].choose_action_index(frame, agent_rng))
            if chosen_idx < 0 or chosen_idx >= frame.action_count:
                raise ValueError(f"agent chose illegal action index {chosen_idx}")
            decisions += 1
            action_counts.append(frame.action_count)
            ctx = context_feature_dict(frame.observation)
            decision_id = f"g{game_i:04d}_s{step:04d}"
            actor = int(frame.player)
            for action_idx, action in enumerate(frame.legal_actions):
                feats: dict[str, float] = {}
                feats.update(ctx)
                feats.update(action_feature_dict(action, frame.observation))
                row: dict[str, object] = {
                    "game_index": game_i,
                    "decision_id": decision_id,
                    "step": step,
                    "player": actor,
                    "agent_name": getattr(agents[actor], "name", type(agents[actor]).__name__),
                    "starting_player": int(starting_player),
                    "starting_life": int(starting_life),
                    "action_index": int(action_idx),
                    "action_count": int(frame.action_count),
                    "chosen": 1 if action_idx == chosen_idx else 0,
                    "action": action.compact(),
                }
                row.update(feats)
                game_rows.append(row)
            apply_decision_index(state, frame, chosen_idx, state_rng)

        terminal = state.winner is not None
        if terminal:
            terminal_games += 1
        else:
            truncated_games += 1
            state.loss_reason = state.loss_reason or "max_decisions_reached"

        # Add outcome labels after the game is over. This keeps the acting
        # observation public while still allowing outcome-weighted training.
        for row in game_rows:
            actor = int(row["player"])
            score = _actor_score(state.winner, actor)
            weight = outcome_weight_for_score(score, terminal=terminal)
            row["terminal"] = 1 if terminal else 0
            row["winner"] = "None" if state.winner is None else int(state.winner)
            row["loss_reason"] = state.loss_reason
            row["actor_terminal_score"] = float(score)
            row["outcome_weight"] = float(weight)
            if int(row["chosen"]) == 1:
                if terminal and score >= 0.999:
                    winning_chosen += 1
                elif terminal and score <= 0.001:
                    losing_chosen += 1
                else:
                    neutral_chosen += 1
            if int(row["chosen"]) == 1:
                total_weight += weight
            all_rows.append(row)

    summary = OutcomeCollectionSummary(
        games=len(games),
        terminal_games=terminal_games,
        truncated_games=truncated_games,
        decisions=decisions,
        rows=len(all_rows),
        chosen_rows=sum(int(r["chosen"]) for r in all_rows),
        winning_chosen_rows=winning_chosen,
        losing_chosen_rows=losing_chosen,
        neutral_chosen_rows=neutral_chosen,
        max_action_count=max(action_counts) if action_counts else 0,
        mean_action_count=(sum(action_counts) / len(action_counts)) if action_counts else 0.0,
        total_training_weight=total_weight,
    )
    return all_rows, summary
