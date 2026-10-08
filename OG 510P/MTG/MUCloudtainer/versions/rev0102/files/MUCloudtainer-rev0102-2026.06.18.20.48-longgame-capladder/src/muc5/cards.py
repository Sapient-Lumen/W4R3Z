from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Tuple

CARD_ISLAND = "Island"
CARD_COUNTERSPELL = "Counterspell"
CARD_FORCE = "ForceOfWill"
CARD_JACE = "JaceTheMindSculptor"
CARD_OVERLORD = "OverlordOfTheFloodpits"

CARD_ORDER = [CARD_ISLAND, CARD_COUNTERSPELL, CARD_FORCE, CARD_JACE, CARD_OVERLORD]
BLUE_NONLANDS = [CARD_COUNTERSPELL, CARD_FORCE, CARD_JACE, CARD_OVERLORD]
THREATS = [CARD_JACE, CARD_OVERLORD]
INTERACTION = [CARD_COUNTERSPELL, CARD_FORCE]


@dataclass(frozen=True)
class ManaCost:
    generic: int = 0
    blue: int = 0

    @property
    def total_islands_needed(self) -> int:
        # MUC-5 has only Islands, so blue plus generic is just this many untapped Islands.
        return self.generic + self.blue


@dataclass(frozen=True)
class CardSpec:
    card_id: str
    display_name: str
    card_type: str
    mana_cost: ManaCost | None
    oracle_summary: str
    source_hint: str = ""


CARD_SPECS: Dict[str, CardSpec] = {
    CARD_ISLAND: CardSpec(
        CARD_ISLAND,
        "Island",
        "Basic Land — Island",
        None,
        "Tap for U. In MUC-5 Islands are anonymous blue mana sources.",
        "Scryfall/Gatherer oracle-style metadata",
    ),
    CARD_COUNTERSPELL: CardSpec(
        CARD_COUNTERSPELL,
        "Counterspell",
        "Instant",
        ManaCost(0, 2),
        "Counter target spell.",
        "Scryfall oracle text",
    ),
    CARD_FORCE: CardSpec(
        CARD_FORCE,
        "Force of Will",
        "Instant",
        ManaCost(3, 2),
        "You may pay 1 life and exile a blue card from your hand rather than pay this spell's mana cost. Counter target spell.",
        "Scryfall oracle text",
    ),
    CARD_JACE: CardSpec(
        CARD_JACE,
        "Jace, the Mind Sculptor",
        "Legendary Planeswalker — Jace",
        ManaCost(2, 2),
        "+2 fateseal/look; 0 Brainstorm; -1 return target creature; -12 exile target player's library then shuffle their hand into their library. Starts at 3 loyalty.",
        "Scryfall/Gatherer oracle-style metadata",
    ),
    CARD_OVERLORD: CardSpec(
        CARD_OVERLORD,
        "Overlord of the Floodpits",
        "Enchantment Creature — Avatar Horror",
        ManaCost(3, 2),
        "5/3 flying. Impending 4—1UU. Whenever it enters or attacks, draw two cards, then discard a card.",
        "Duskmourn release notes and oracle-style metadata",
    ),
}

OVERLORD_IMPENDING_COST = ManaCost(1, 2)
OVERLORD_FULL_COST = ManaCost(3, 2)
JACE_STARTING_LOYALTY = 3
JACE_ULTIMATE_LOYALTY = 12
OVERLORD_POWER = 5
OVERLORD_TOUGHNESS = 3
STARTING_LIFE = 20
LEGAL_STARTING_LIFE_TOTALS = (20, 40)
STARTING_LIFE_OPTIONS: Tuple[int, int] = (20, 40)
OPENING_HAND_SIZE = 7
MAX_HAND_SIZE = 7
LEGAL_DECK_SIZES: Tuple[int, int] = (40, 60)


def is_blue_pitch_card(card_id: str) -> bool:
    return card_id in BLUE_NONLANDS


def validate_starting_life(life_total: int) -> int:
    """Validate the MUC-5 tournament life-total dial.

    Rev0004 intentionally permits only 20 and 40. Keeping this strict is useful:
    every extra dial value multiplies matchup data requirements and makes early
    conclusions harder to interpret.
    """
    if life_total not in STARTING_LIFE_OPTIONS:
        raise ValueError(f"starting_life must be one of {STARTING_LIFE_OPTIONS}, got {life_total}")
    return int(life_total)
