from __future__ import annotations

from dataclasses import asdict, dataclass
from math import comb
from typing import Dict, Iterable, Tuple

from .cards import CARD_COUNTERSPELL, CARD_FORCE, CARD_ISLAND, CARD_JACE, CARD_OVERLORD
from .deckspace import DeckVector


def _safe_comb(n: int, k: int) -> int:
    if k < 0 or k > n:
        return 0
    return comb(n, k)


def hypergeom_at_least(population: int, successes: int, draws: int, at_least: int) -> float:
    """P[X >= at_least] for X ~ Hypergeometric(population, successes, draws)."""
    if population <= 0:
        raise ValueError("population must be positive")
    if not 0 <= successes <= population:
        raise ValueError("successes must be in [0, population]")
    if not 0 <= draws <= population:
        raise ValueError("draws must be in [0, population]")
    denom = _safe_comb(population, draws)
    lo = max(at_least, 0)
    hi = min(successes, draws)
    if lo > hi:
        return 0.0
    return sum(_safe_comb(successes, k) * _safe_comb(population - successes, draws - k) for k in range(lo, hi + 1)) / denom


def joint_at_least_two_categories(
    population: int,
    success_a: int,
    success_b: int,
    draws: int,
    min_a: int,
    min_b: int,
) -> float:
    """P[A >= min_a and B >= min_b] for disjoint categories A/B in a hypergeometric draw."""
    if success_a + success_b > population:
        raise ValueError("categories must be disjoint and no larger than population")
    denom = _safe_comb(population, draws)
    other = population - success_a - success_b
    total = 0
    for a in range(min_a, min(success_a, draws) + 1):
        for b in range(min_b, min(success_b, draws - a) + 1):
            c = draws - a - b
            if 0 <= c <= other:
                total += _safe_comb(success_a, a) * _safe_comb(success_b, b) * _safe_comb(other, c)
    return total / denom


def prob_force_with_pitch(deck: DeckVector, draws: int = 7) -> float:
    """Opening probability of Force of Will plus any *other* blue card to exile.

    Since a second Force can pitch to the first one, this is equivalent to:
    Force count >= 1 and total blue nonland count >= 2 in the sampled cards.
    """
    n = deck.size
    denom = _safe_comb(n, draws)
    total = 0
    other_blue = deck.counterspell + deck.jace + deck.overlord
    for f in range(1, min(deck.force, draws) + 1):
        for ob in range(0, min(other_blue, draws - f) + 1):
            if f + ob < 2:
                continue
            islands = draws - f - ob
            if 0 <= islands <= deck.island:
                total += _safe_comb(deck.force, f) * _safe_comb(other_blue, ob) * _safe_comb(deck.island, islands)
    return total / denom


def prob_card_and_lands(deck: DeckVector, card: str, draws: int, min_lands: int) -> float:
    """P[first `draws` cards contain at least one `card` and at least `min_lands` Islands]."""
    card_count = deck.counts()[card]
    non_island_non_card = deck.size - deck.island - card_count
    denom = _safe_comb(deck.size, draws)
    total = 0
    for lands in range(min_lands, min(deck.island, draws) + 1):
        for c in range(1, min(card_count, draws - lands) + 1):
            rest = draws - lands - c
            if 0 <= rest <= non_island_non_card:
                total += _safe_comb(deck.island, lands) * _safe_comb(card_count, c) * _safe_comb(non_island_non_card, rest)
    return total / denom


def prob_keepable_land_band(deck: DeckVector, draws: int = 7, low: int = 2, high: int = 5) -> float:
    """Probability opening hand has a crude keepable Island count band."""
    denom = _safe_comb(deck.size, draws)
    total = 0
    for lands in range(low, min(high, deck.island, draws) + 1):
        total += _safe_comb(deck.island, lands) * _safe_comb(deck.size - deck.island, draws - lands)
    return total / denom


@dataclass(frozen=True)
class DeckProbe:
    deck_size: int
    island: int
    counterspell: int
    force: int
    jace: int
    overlord: int
    p_keepable_2_to_5_islands: float
    p_force_plus_pitch_open7: float
    p_counterspell_online_turn2_play: float
    p_overlord_impending_turn3_play: float
    p_jace_turn4_play: float
    p_overlord_full_turn5_play: float
    crude_probe_score: float

    def to_row(self) -> Dict[str, float | int]:
        return asdict(self)


def deck_probe(deck: DeckVector) -> DeckProbe:
    """Exact hypergeometric probes for pre-game screening.

    Draw windows assume player on the play in two-player Magic:
      - opening hand: 7
      - by turn 2: 8 cards seen (opening + one draw; first player skips turn-1 draw)
      - by turn 3: 9 cards seen
      - by turn 4: 10 cards seen
      - by turn 5: 11 cards seen
    These are not strategic evaluations; they are constructor/debugging probes.
    """
    keep = prob_keepable_land_band(deck, 7, 2, 5)
    force_pitch = prob_force_with_pitch(deck, 7)
    cspell_t2 = prob_card_and_lands(deck, CARD_COUNTERSPELL, draws=8, min_lands=2)
    ovl_t3 = prob_card_and_lands(deck, CARD_OVERLORD, draws=9, min_lands=3)
    jace_t4 = prob_card_and_lands(deck, CARD_JACE, draws=10, min_lands=4)
    ovl_t5 = prob_card_and_lands(deck, CARD_OVERLORD, draws=11, min_lands=5)
    # Intentional crude mixture: consistency + interaction + two threat paths.
    score = (
        0.24 * keep
        + 0.19 * force_pitch
        + 0.22 * cspell_t2
        + 0.12 * ovl_t3
        + 0.15 * jace_t4
        + 0.08 * ovl_t5
    )
    return DeckProbe(
        deck_size=deck.size,
        island=deck.island,
        counterspell=deck.counterspell,
        force=deck.force,
        jace=deck.jace,
        overlord=deck.overlord,
        p_keepable_2_to_5_islands=keep,
        p_force_plus_pitch_open7=force_pitch,
        p_counterspell_online_turn2_play=cspell_t2,
        p_overlord_impending_turn3_play=ovl_t3,
        p_jace_turn4_play=jace_t4,
        p_overlord_full_turn5_play=ovl_t5,
        crude_probe_score=score,
    )
