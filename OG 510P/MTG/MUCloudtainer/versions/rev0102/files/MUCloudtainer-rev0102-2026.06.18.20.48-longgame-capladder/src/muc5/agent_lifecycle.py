from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, runtime_checkable


@dataclass(frozen=True)
class EpisodeContext:
    """Public, seat-scoped metadata supplied before one game.

    The context deliberately excludes the transition/shuffle seed and all hidden
    state.  Stateful policies may use it to clear recurrent memory and attach
    diagnostics to one seat without gaining information unavailable in play.
    """

    episode_id: str
    player: int
    starting_player: int
    starting_life: int


@dataclass(frozen=True)
class EpisodeResult:
    """Public terminal feedback supplied after one game."""

    episode_id: str
    player: int
    score: float
    winner: int | None
    loss_reason: str
    decisions: int


@runtime_checkable
class EpisodeResettable(Protocol):
    def reset_episode(self, context: EpisodeContext) -> None: ...


@runtime_checkable
class EpisodeFinalizable(Protocol):
    def end_episode(self, result: EpisodeResult) -> None: ...


def reset_episode(agent: object, context: EpisodeContext) -> bool:
    """Reset one policy object for a new seat/game.

    Stateless policies need no method and return ``False``.  A policy may set
    ``requires_episode_reset = True`` to fail closed if its reset method is lost
    during wrapping or refactoring.
    """

    method = getattr(agent, "reset_episode", None)
    if callable(method):
        method(context)
        return True
    if bool(getattr(agent, "requires_episode_reset", False)):
        raise TypeError(
            f"agent {getattr(agent, 'name', type(agent).__name__)!r} declares "
            "requires_episode_reset but provides no reset_episode(context) method"
        )
    return False


def end_episode(agent: object, result: EpisodeResult) -> bool:
    """Deliver public terminal feedback when the policy opts into it."""

    method = getattr(agent, "end_episode", None)
    if callable(method):
        method(result)
        return True
    return False


def require_distinct_seat_objects(agent0: object, agent1: object) -> None:
    """Reject one mutable policy instance being shared by both seats.

    Even a correctly reset recurrent policy cannot represent two independent
    players when both seats call into the same object during one game.  Callers
    may reuse models or immutable weights, but must construct separate wrappers.
    """

    if agent0 is agent1:
        raise ValueError(
            "agent0 and agent1 must be distinct policy objects; sharing one "
            "instance across seats can merge private memories"
        )
