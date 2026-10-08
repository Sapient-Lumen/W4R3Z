from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional, Tuple

from .cards import STARTING_LIFE, STARTING_LIFE_OPTIONS, validate_starting_life

LIFE_TOTAL_OPTIONS: Tuple[int, int] = STARTING_LIFE_OPTIONS


@dataclass(frozen=True)
class ConstructionContext:
    """Information visible to a deck constructor before it commits to a deck.

    Gameplay observations always include actual life totals. This context is only
    for deck registration: a constructor may know the exact tournament life total,
    or may only know that the event will choose one of the allowed life totals.
    """

    known_starting_life: Optional[int]
    possible_starting_life_totals: Tuple[int, ...] = LIFE_TOTAL_OPTIONS

    def __post_init__(self) -> None:
        for life in self.possible_starting_life_totals:
            validate_starting_life(life)
        if self.known_starting_life is not None:
            validate_starting_life(self.known_starting_life)

    @property
    def knows_life_total(self) -> bool:
        return self.known_starting_life is not None

    def as_dict(self) -> Dict[str, object]:
        return {
            "knows_life_total": self.knows_life_total,
            "known_starting_life": self.known_starting_life,
            "possible_starting_life_totals": list(self.possible_starting_life_totals),
        }


@dataclass(frozen=True)
class TournamentConfig:
    """Small tournament dial bundle for MUC-5.

    `starting_life` is a gameplay fact and is always exposed in observations.
    `construction_context` controls what a deck constructor was allowed to know before
    choosing its 40/60-card five-count vector.
    """

    name: str
    starting_life: int = STARTING_LIFE
    construction_context: ConstructionContext = ConstructionContext(STARTING_LIFE)

    def __post_init__(self) -> None:
        validate_starting_life(self.starting_life)

    @property
    def construction_knows_life(self) -> bool:
        return self.construction_context.knows_life_total

    def as_dict(self) -> Dict[str, object]:
        return {
            "name": self.name,
            "starting_life": self.starting_life,
            "construction_context": self.construction_context.as_dict(),
        }


def known_life_config(life: int) -> TournamentConfig:
    life = validate_starting_life(life)
    return TournamentConfig(
        name=f"known_life_{life}",
        starting_life=life,
        construction_context=ConstructionContext(known_starting_life=life),
    )


def unknown_life_config(actual_life: int) -> TournamentConfig:
    actual_life = validate_starting_life(actual_life)
    return TournamentConfig(
        name=f"unknown_life_actual_{actual_life}",
        starting_life=actual_life,
        construction_context=ConstructionContext(known_starting_life=None),
    )


def standard_life_configs() -> Tuple[TournamentConfig, ...]:
    return (
        known_life_config(20),
        known_life_config(40),
        unknown_life_config(20),
        unknown_life_config(40),
    )
