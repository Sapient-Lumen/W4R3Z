from __future__ import annotations

from dataclasses import dataclass
from random import Random
from typing import Dict, List, Optional, Tuple

from .action_schema import Action
from .cards import STARTING_LIFE, validate_starting_life
from .deckspace import DeckVector
from .engine import GameState, apply_action, legal_actions, start_game
from .mulligan import MulliganAgent, MulliganPolicy
from .features import observation_vector


@dataclass
class SlotObservation:
    """A small RL/search-facing wrapper around the referee observation.

    `action_slots[i]` is the exact legal macro-action behind `action_mask[i] == 1`.
    Slots beyond the current legal list are padding. This avoids a global Magic action
    catalog while still giving neural experiments a fixed-size output surface.
    """

    player: int
    raw: Dict[str, object]
    feature_vector: List[float]
    feature_names: List[str]
    action_mask: List[int]
    action_strings: List[str]


class MUC5SlotEnv:
    """Minimal AEC-like environment wrapper for MUC-5.

    It is intentionally smaller than Gym/PettingZoo. The moving parts we need now are:
    reset, current player, masked legal action slots, and step-by-slot. A formal
    PettingZoo adapter can later wrap this once the engine is stable.
    """

    def __init__(
        self,
        deck0: DeckVector,
        deck1: DeckVector,
        *,
        max_action_slots: int = 256,
        max_decisions: int = 500,
        starting_life: int = STARTING_LIFE,
        mulligan_policy: str | MulliganPolicy | None = None,
        mulligan_agents: Tuple[MulliganAgent | str | MulliganPolicy | None, MulliganAgent | str | MulliganPolicy | None] | None = None,
    ) -> None:
        if max_action_slots <= 0:
            raise ValueError("max_action_slots must be positive")
        self.deck0 = deck0
        self.deck1 = deck1
        self.max_action_slots = max_action_slots
        self.max_decisions = max_decisions
        self.starting_life = validate_starting_life(starting_life)
        self.mulligan_policy = mulligan_policy
        self.mulligan_agents = mulligan_agents
        self.rng = Random(0)
        self.state: Optional[GameState] = None
        self.decisions = 0

    def reset(self, *, seed: int = 1, starting_player: int = 0, starting_life: int | None = None, mulligan_policy: str | MulliganPolicy | None = None, mulligan_agents: Tuple[MulliganAgent | str | MulliganPolicy | None, MulliganAgent | str | MulliganPolicy | None] | None = None) -> SlotObservation:
        self.rng = Random(seed)
        if starting_life is not None:
            self.starting_life = validate_starting_life(starting_life)
        if mulligan_policy is not None:
            self.mulligan_policy = mulligan_policy
            self.mulligan_agents = None
        if mulligan_agents is not None:
            self.mulligan_agents = mulligan_agents
            self.mulligan_policy = None
        self.state = start_game(
            self.deck0,
            self.deck1,
            seed=seed,
            starting_player=starting_player,
            starting_life=self.starting_life,
            mulligan_policy=self.mulligan_policy,
            mulligan_agents=self.mulligan_agents,
        )
        self.decisions = 0
        return self.observe()

    @property
    def current_player(self) -> int:
        if self.state is None:
            raise RuntimeError("environment has not been reset")
        return self.state.current_player()

    def observe(self, player: Optional[int] = None) -> SlotObservation:
        if self.state is None:
            raise RuntimeError("environment has not been reset")
        if player is None:
            player = self.state.current_player()
        raw = self.state.observation(player)
        vec, names = observation_vector(raw)
        actions = legal_actions(self.state)
        if len(actions) > self.max_action_slots:
            # Keep this loud. If we hit it, we should either raise the slot budget or
            # compress a high-branching decision frame.
            raise RuntimeError(f"legal action count {len(actions)} exceeds max_action_slots={self.max_action_slots}")
        action_strings = [a.compact() for a in actions]
        action_mask = [1] * len(actions) + [0] * (self.max_action_slots - len(actions))
        return SlotObservation(player, raw, vec, names, action_mask, action_strings)

    def legal_action_objects(self) -> List[Action]:
        if self.state is None:
            raise RuntimeError("environment has not been reset")
        actions = legal_actions(self.state)
        if len(actions) > self.max_action_slots:
            raise RuntimeError(f"legal action count {len(actions)} exceeds max_action_slots={self.max_action_slots}")
        return actions

    def reward_for(self, player: int) -> float:
        if self.state is None or self.state.winner is None:
            return 0.0
        return 1.0 if self.state.winner == player else -1.0

    def step(self, action_slot: int) -> Tuple[SlotObservation, Dict[int, float], bool, Dict[str, object]]:
        if self.state is None:
            raise RuntimeError("environment has not been reset")
        actions = self.legal_action_objects()
        if action_slot < 0 or action_slot >= len(actions):
            raise ValueError(f"invalid action slot {action_slot}; legal slots are 0..{len(actions)-1}")
        actor = self.state.current_player()
        chosen = actions[action_slot]
        apply_action(self.state, chosen, self.rng, validate=False)
        self.decisions += 1
        if self.state.winner is None and self.decisions >= self.max_decisions:
            self.state.frame = "GAME_OVER"
            self.state.loss_reason = "max_decisions_reached"
        done = self.state.winner is not None or self.state.frame == "GAME_OVER"
        rewards = {0: self.reward_for(0), 1: self.reward_for(1)}
        info = {
            "actor": actor,
            "action": chosen.compact(),
            "decisions": self.decisions,
            "winner": self.state.winner,
            "loss_reason": self.state.loss_reason,
            "starting_life": self.starting_life,
            "legal_action_count": 0 if done else len(legal_actions(self.state)),
        }
        return self.observe(self.state.current_player()), rewards, done, info
