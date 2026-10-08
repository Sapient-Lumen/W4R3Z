from __future__ import annotations

from dataclasses import dataclass, field
from random import Random
from typing import Dict, List, Protocol, Sequence, Tuple

from .action_schema import Action
from .engine import GameState, apply_action, legal_actions


@dataclass(frozen=True)
class DecisionFrame:
    """Public/agent-facing decision packet for one MUC-5 choice.

    The referee remains omniscient, but learned or external policies should not
    receive the omniscient ``GameState``. They should receive a DecisionFrame:
    the current player's observation, the exact legal macro-actions, and an
    internal revision number used only to reject stale/replayed choices.

    This is the safe version of the rev0008 speed idea. We still avoid duplicate
    legality enumeration in hot loops, but the policy no longer needs the full
    state object to choose a move.
    """

    player: int
    state_revision: int
    observation: Dict[str, object]
    legal_actions: Tuple[Action, ...]
    information_state: Dict[str, object] = field(default_factory=dict)

    @property
    def legal_action_strings(self) -> Tuple[str, ...]:
        return tuple(action.compact() for action in self.legal_actions)

    @property
    def action_count(self) -> int:
        return len(self.legal_actions)


def build_decision_frame(state: GameState) -> DecisionFrame:
    """Create a safe policy-facing frame for the current player."""

    player = state.current_player()
    return DecisionFrame(
        player=player,
        state_revision=state.revision,
        observation=state.observation(player),
        legal_actions=tuple(legal_actions(state)),
        information_state=state.information_state(player),
    )


def apply_decision_index(state: GameState, frame: DecisionFrame, action_index: int, rng: Random) -> Action:
    """Apply an action chosen from a DecisionFrame without recomputing legality.

    This rejects stale frames and actor mismatches, then applies the chosen action
    through ``apply_action(..., validate=False)``. The caller gets fast-path speed
    and an anti-cheat contract: the action must come from the exact legal list
    emitted by the referee for this state revision.
    """

    if frame.state_revision != state.revision:
        raise ValueError(
            f"stale DecisionFrame revision={frame.state_revision}; current state revision={state.revision}"
        )
    actor = state.current_player()
    if frame.player != actor:
        raise ValueError(f"DecisionFrame player={frame.player} but current actor={actor}")
    if action_index < 0 or action_index >= len(frame.legal_actions):
        raise ValueError(f"action_index {action_index} outside legal range 0..{len(frame.legal_actions)-1}")
    action = frame.legal_actions[action_index]
    apply_action(state, action, rng, validate=False)
    return action


def action_index_in_frame(frame: DecisionFrame, action: Action) -> int:
    """Return the slot of an action inside a frame, or raise if absent."""

    try:
        return list(frame.legal_actions).index(action)
    except ValueError as exc:
        raise ValueError(f"action {action.compact()} not present in this DecisionFrame") from exc


class PublicDecisionAgent(Protocol):
    """Protocol for agents that never receive omniscient GameState."""

    name: str

    def choose_action_index(self, frame: DecisionFrame, rng: Random) -> int: ...


@dataclass
class PublicRandomAgent:
    name: str = "public_random_rev0009"

    def choose_action_index(self, frame: DecisionFrame, rng: Random) -> int:
        if frame.action_count <= 0:
            raise ValueError("no legal actions")
        return rng.randrange(frame.action_count)


@dataclass
class PublicHeuristicAgent:
    """Safe wrapper around the existing heuristic scorer.

    The scorer consumes only ``frame.observation`` and individual legal actions.
    It never receives the hidden state, libraries, or opponent hand. This is the
    baseline interface future learned policies should imitate.
    """

    name: str = "public_heuristic_rev0009"

    def choose_action_index(self, frame: DecisionFrame, rng: Random) -> int:
        if frame.action_count <= 0:
            raise ValueError("no legal actions")
        # Local import avoids an import cycle: agents.py imports engine.py, and
        # engine.py is already imported above.
        from .agents import HeuristicAgent

        scorer = HeuristicAgent()
        scored = [(scorer.score_action(frame.observation, action), rng.random(), i) for i, action in enumerate(frame.legal_actions)]
        scored.sort(key=lambda x: (x[0], x[1]), reverse=True)
        return scored[0][2]
