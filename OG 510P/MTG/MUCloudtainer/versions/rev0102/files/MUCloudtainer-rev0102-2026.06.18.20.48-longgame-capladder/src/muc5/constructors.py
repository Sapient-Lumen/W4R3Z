from __future__ import annotations

from dataclasses import dataclass
from random import Random
from typing import Callable, Iterable, List, Protocol, Sequence, Tuple

from .deckspace import DeckVector, enumerate_decks, plausibility_filter, random_deck


class DeckScorer(Protocol):
    def __call__(self, deck: DeckVector) -> float: ...


@dataclass
class ConstructorResult:
    method: str
    candidates: List[Tuple[DeckVector, float]]
    games_or_evals: int
    notes: str = ""


def random_search(scorer: DeckScorer, samples: int, seed: int = 1) -> ConstructorResult:
    rng = Random(seed)
    seen = set()
    scored: List[Tuple[DeckVector, float]] = []
    while len(scored) < samples:
        d = random_deck(rng)
        if d.as_tuple() in seen:
            continue
        seen.add(d.as_tuple())
        scored.append((d, scorer(d)))
    scored.sort(key=lambda x: x[1], reverse=True)
    return ConstructorResult("random_search", scored[:25], samples)


def filtered_enumeration(scorer: DeckScorer, limit: int | None = None) -> ConstructorResult:
    scored: List[Tuple[DeckVector, float]] = []
    evals = 0
    for d in enumerate_decks():
        if not plausibility_filter(d):
            continue
        scored.append((d, scorer(d)))
        evals += 1
        if limit is not None and evals >= limit:
            break
    scored.sort(key=lambda x: x[1], reverse=True)
    return ConstructorResult("filtered_enumeration", scored[:25], evals)


def toy_static_scorer(deck: DeckVector) -> float:
    """A deliberately fake scorer for plumbing tests only.

    It rewards plausible mana, interaction, threat density, and Force support.
    It is not strategic truth. It exists so constructor code can run before games exist.
    """
    f = deck.features()
    land_target = 0.52 if deck.size == 40 else 0.50
    land_score = 1.0 - abs(f["land_frac"] - land_target) / 0.50
    interaction_score = min(1.0, f["interaction_frac"] / 0.35)
    threat_score = min(1.0, f["threat_frac"] / 0.18)
    force_support = 1.0 if deck.force == 0 else min(1.0, f["pitchable_blue_frac"] / 0.45)
    size_bonus = 0.05 if deck.size == 40 else 0.0
    return 0.35 * land_score + 0.25 * interaction_score + 0.25 * threat_score + 0.10 * force_support + size_bonus


if __name__ == "__main__":
    result = random_search(toy_static_scorer, samples=1000, seed=7)
    for d, s in result.candidates[:10]:
        print(round(s, 4), d)
