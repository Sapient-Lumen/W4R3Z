from __future__ import annotations

from dataclasses import dataclass
from math import comb
from random import Random
from typing import Dict, Iterable, Iterator, List, Tuple

from .cards import CARD_ORDER, LEGAL_DECK_SIZES


@dataclass(frozen=True)
class DeckVector:
    size: int
    island: int
    counterspell: int
    force: int
    jace: int
    overlord: int

    def as_tuple(self) -> Tuple[int, int, int, int, int, int]:
        return (self.size, self.island, self.counterspell, self.force, self.jace, self.overlord)

    def counts(self) -> Dict[str, int]:
        return {
            "Island": self.island,
            "Counterspell": self.counterspell,
            "ForceOfWill": self.force,
            "JaceTheMindSculptor": self.jace,
            "OverlordOfTheFloodpits": self.overlord,
        }

    @property
    def pitchable_blue(self) -> int:
        return self.counterspell + self.force + self.jace + self.overlord

    @property
    def threats(self) -> int:
        return self.jace + self.overlord

    @property
    def interaction(self) -> int:
        return self.counterspell + self.force

    def features(self) -> Dict[str, float]:
        n = float(self.size)
        return {
            "land_frac": self.island / n,
            "pitchable_blue_frac": self.pitchable_blue / n,
            "interaction_frac": self.interaction / n,
            "threat_frac": self.threats / n,
            "force_frac": self.force / n,
            "jace_frac": self.jace / n,
            "overlord_frac": self.overlord / n,
        }

    def validate(self) -> None:
        if self.size not in LEGAL_DECK_SIZES:
            raise ValueError(f"deck size must be 40 or 60, got {self.size}")
        if min(self.island, self.counterspell, self.force, self.jace, self.overlord) < 0:
            raise ValueError(f"negative card count in {self}")
        total = self.island + self.counterspell + self.force + self.jace + self.overlord
        if total != self.size:
            raise ValueError(f"counts sum to {total}, expected {self.size}")


def deck_count(size: int) -> int:
    """Number of nonnegative five-card count vectors summing to size."""
    if size not in LEGAL_DECK_SIZES:
        raise ValueError("MUC-5 currently allows only 40 or 60 cards")
    return comb(size + 4, 4)


def total_deck_count() -> int:
    return deck_count(40) + deck_count(60)


def enumerate_decks(size: int | None = None) -> Iterator[DeckVector]:
    sizes = LEGAL_DECK_SIZES if size is None else (size,)
    for n in sizes:
        if n not in LEGAL_DECK_SIZES:
            raise ValueError("MUC-5 currently allows only 40 or 60 cards")
        for islands in range(n + 1):
            for c in range(n - islands + 1):
                for force in range(n - islands - c + 1):
                    for jace in range(n - islands - c - force + 1):
                        overlord = n - islands - c - force - jace
                        yield DeckVector(n, islands, c, force, jace, overlord)


def random_deck(rng: Random, size: int | None = None) -> DeckVector:
    """Uniform-ish over separator positions, not weighted by strategic plausibility."""
    n = rng.choice(list(LEGAL_DECK_SIZES)) if size is None else size
    cuts = sorted(rng.sample(range(n + 4), 4))
    counts = []
    last = -1
    for cut in cuts + [n + 4]:
        counts.append(cut - last - 1)
        last = cut
    deck = DeckVector(n, *counts[:5])
    deck.validate()
    return deck


def plausibility_filter(deck: DeckVector) -> bool:
    """A deliberately weak filter for early experiments, not a claim of optimality."""
    f = deck.features()
    return (
        0.35 <= f["land_frac"] <= 0.65
        and deck.threats >= 1
        and deck.interaction >= 1
        and (deck.force == 0 or deck.pitchable_blue >= max(8, deck.size // 5))
    )


def stratified_buckets(deck: DeckVector) -> Tuple[str, str, str, str]:
    """Coarse labels for sampling/evaluation grids."""
    f = deck.features()
    def band(x: float, cuts=(0.25, 0.40, 0.55, 0.70)) -> str:
        for i, c in enumerate(cuts):
            if x < c:
                return f"b{i}"
        return f"b{len(cuts)}"
    return (
        f"size{deck.size}",
        "land_" + band(f["land_frac"]),
        "force_" + band(f["force_frac"], cuts=(0.05, 0.10, 0.20, 0.35)),
        "threat_" + band(f["threat_frac"], cuts=(0.02, 0.08, 0.15, 0.30)),
    )


if __name__ == "__main__":
    print("40-card decks:", deck_count(40))
    print("60-card decks:", deck_count(60))
    print("total:", total_deck_count())
    rng = Random(1)
    for _ in range(3):
        d = random_deck(rng)
        print(d, d.features(), stratified_buckets(d))
