from __future__ import annotations

from dataclasses import dataclass
from math import ceil
from typing import Dict, Iterable, Tuple

from .cards import OVERLORD_POWER
from .tournament import LIFE_TOTAL_OPTIONS


def validate_starting_life(life_total: int) -> int:
    if life_total not in LIFE_TOTAL_OPTIONS:
        raise ValueError(f"starting life must be one of {LIFE_TOTAL_OPTIONS}")
    return life_total


@dataclass(frozen=True)
class LifeDialRegime:
    """Tournament-level life-total condition for construction experiments.

    `construction_knows_life` describes what the deck constructor was allowed to
    know before registering the deck. It does not hide life totals during gameplay;
    any pilot in an actual game must see both current life totals.
    """

    name: str
    life_totals: Tuple[int, ...]
    construction_knows_life: bool
    description: str

    def validate(self) -> "LifeDialRegime":
        if not self.life_totals:
            raise ValueError("LifeDialRegime.life_totals cannot be empty")
        for life in self.life_totals:
            validate_starting_life(life)
        return self


def canonical_life_regimes() -> Tuple[LifeDialRegime, ...]:
    return (
        LifeDialRegime(
            name="known20",
            life_totals=(20,),
            construction_knows_life=True,
            description="Constructor knows games start at 20 life.",
        ),
        LifeDialRegime(
            name="known40",
            life_totals=(40,),
            construction_knows_life=True,
            description="Constructor knows games start at 40 life.",
        ),
        LifeDialRegime(
            name="unknown_balanced_20_40",
            life_totals=LIFE_TOTAL_OPTIONS,
            construction_knows_life=False,
            description="Constructor registers before knowing whether the tournament/game starts at 20 or 40 life; evaluation averages both.",
        ),
    )


def overlord_unblocked_hits_to_kill(life_total: int) -> int:
    life_total = validate_starting_life(life_total)
    return ceil(life_total / OVERLORD_POWER)


def force_pitch_life_budget(life_total: int) -> int:
    """Maximum number of Force pitch payments a player can make from starting life and not die solely from those payments."""
    life_total = validate_starting_life(life_total)
    return max(0, life_total - 1)


def life_dial_summary() -> Dict[str, Dict[str, int]]:
    return {
        str(life): {
            "overlord_unblocked_hits_to_kill": overlord_unblocked_hits_to_kill(life),
            "force_pitch_life_budget": force_pitch_life_budget(life),
        }
        for life in LIFE_TOTAL_OPTIONS
    }


def robust_average(values: Iterable[float]) -> float:
    vals = list(values)
    return sum(vals) / len(vals) if vals else 0.0


def robust_floor(values: Iterable[float]) -> float:
    vals = list(values)
    return min(vals) if vals else 0.0
