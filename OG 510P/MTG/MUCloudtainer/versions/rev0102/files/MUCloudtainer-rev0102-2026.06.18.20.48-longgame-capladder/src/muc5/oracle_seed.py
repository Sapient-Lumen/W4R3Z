from __future__ import annotations

from dataclasses import dataclass
from random import Random
from typing import Dict, Iterable, List, Sequence, Tuple

from .deckspace import DeckVector, plausibility_filter, random_deck
from .life_constructor import robust_unknown_life_score, life_static_score
from .payoff import StrategyBundle
from .mulligan import POLICY_LAND_BAND, POLICY_LAND_BAND_BUSINESS


@dataclass(frozen=True)
class OracleCandidate:
    candidate_id: str
    deck: DeckVector
    prior_score: float
    source: str

    def as_dict(self) -> Dict[str, object]:
        return {
            "candidate_id": self.candidate_id,
            "source": self.source,
            "prior_score": self.prior_score,
            "deck_size": self.deck.size,
            "island": self.deck.island,
            "counterspell": self.deck.counterspell,
            "force": self.deck.force,
            "jace": self.deck.jace,
            "overlord": self.deck.overlord,
        }


def mutate_deck(deck: DeckVector, rng: Random, *, steps: int = 1) -> DeckVector:
    """Move one card at a time between card counts, preserving deck size."""

    counts = [deck.island, deck.counterspell, deck.force, deck.jace, deck.overlord]
    for _ in range(max(1, steps)):
        nonzero = [i for i, c in enumerate(counts) if c > 0]
        src = rng.choice(nonzero)
        dst = rng.randrange(5)
        if dst == src:
            continue
        counts[src] -= 1
        counts[dst] += 1
    out = DeckVector(deck.size, *counts)
    out.validate()
    return out


def candidate_prior(deck: DeckVector) -> float:
    """Cheap construction prior for oracle seeding, not a gameplay result."""

    return 0.50 * robust_unknown_life_score(deck) + 0.25 * life_static_score(deck, 20) + 0.25 * life_static_score(deck, 40)


def generate_oracle_candidates(
    base_decks: Sequence[DeckVector],
    *,
    seed: int = 12012,
    random_samples: int = 1500,
    mutations_per_base: int = 120,
    keep: int = 12,
) -> List[OracleCandidate]:
    """Generate a small, inspectable first response-oracle candidate set.

    This is deliberately not an optimizer yet. It mixes local mutations around
    existing seed decks with random plausible decks, then uses a transparent
    static prior to produce a tiny list worth evaluating with actual games.
    """

    rng = Random(seed)
    seen = set()
    scored: List[Tuple[float, str, DeckVector]] = []

    def add(deck: DeckVector, source: str) -> None:
        if deck.as_tuple() in seen or not plausibility_filter(deck):
            return
        seen.add(deck.as_tuple())
        scored.append((candidate_prior(deck), source, deck))

    for base in base_decks:
        add(base, "seed")
        for _ in range(mutations_per_base):
            add(mutate_deck(base, rng, steps=rng.choice([1, 1, 2, 3])), "mutation")

    while len(seen) < random_samples:
        add(random_deck(rng), "random_plausible")

    scored.sort(key=lambda x: x[0], reverse=True)
    out: List[OracleCandidate] = []
    for rank, (score, source, deck) in enumerate(scored[:keep], 1):
        out.append(OracleCandidate(f"oracle_seed_{rank:02d}", deck, score, source))
    return out


def candidates_to_strategy_bundles(candidates: Sequence[OracleCandidate]) -> List[StrategyBundle]:
    """Turn oracle candidates into concrete strategy bundles for smoke games."""

    bundles: List[StrategyBundle] = []
    for cand in candidates:
        # Give each candidate one balanced and one slightly stricter mulligan
        # entry only when the deck has enough spells. This keeps the first
        # oracle population small while preserving mulligan as a strategy axis.
        bundles.append(
            StrategyBundle(
                strategy_id=f"{cand.candidate_id}_heur_landband",
                deck_name=cand.candidate_id,
                deck=cand.deck,
                agent_name="heuristic",
                mulligan_policy=POLICY_LAND_BAND,
            )
        )
        bundles.append(
            StrategyBundle(
                strategy_id=f"{cand.candidate_id}_threat_business",
                deck_name=cand.candidate_id,
                deck=cand.deck,
                agent_name="threat_rush",
                mulligan_policy=POLICY_LAND_BAND_BUSINESS,
            )
        )
    return bundles
