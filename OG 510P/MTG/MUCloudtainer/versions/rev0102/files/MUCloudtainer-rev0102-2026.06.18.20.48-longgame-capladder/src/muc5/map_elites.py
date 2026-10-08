from __future__ import annotations

from dataclasses import asdict, dataclass
from random import Random
from typing import Dict, Iterable, List, Mapping, Sequence, Tuple

from .deckspace import DeckVector, plausibility_filter, random_deck
from .life_constructor import life_static_score, robust_unknown_life_score
from .oracle_seed import mutate_deck


@dataclass(frozen=True)
class EliteCell:
    cell_id: str
    deck: DeckVector
    quality: float
    descriptors: Dict[str, object]
    source: str

    def as_dict(self) -> Dict[str, object]:
        return {
            "cell_id": self.cell_id,
            "quality": self.quality,
            "source": self.source,
            "deck_size": self.deck.size,
            "island": self.deck.island,
            "counterspell": self.deck.counterspell,
            "force": self.deck.force,
            "jace": self.deck.jace,
            "overlord": self.deck.overlord,
            **{f"desc_{k}": v for k, v in self.descriptors.items()},
        }


def deck_descriptor(deck: DeckVector) -> Dict[str, object]:
    """Small interpretable MAP-Elites descriptor grid for MUC-5 decks."""

    n = float(deck.size)
    land_frac = deck.island / n
    force_frac = deck.force / n
    counter_frac = deck.counterspell / n
    threat_total = deck.jace + deck.overlord
    if land_frac < 0.45:
        land_bin = "land_light"
    elif land_frac <= 0.58:
        land_bin = "land_mid"
    else:
        land_bin = "land_heavy"
    if force_frac == 0:
        force_bin = "force_none"
    elif force_frac < 0.12:
        force_bin = "force_low"
    else:
        force_bin = "force_high"
    if counter_frac < 0.15:
        counter_bin = "counter_low"
    elif counter_frac <= 0.32:
        counter_bin = "counter_mid"
    else:
        counter_bin = "counter_wall"
    if threat_total == 0:
        threat_bin = "no_threat"
    elif deck.jace >= 2 * max(1, deck.overlord):
        threat_bin = "jace_heavy"
    elif deck.overlord >= 2 * max(1, deck.jace):
        threat_bin = "overlord_heavy"
    else:
        threat_bin = "mixed_threats"
    s20 = life_static_score(deck, 20)
    s40 = life_static_score(deck, 40)
    if s20 - s40 > 0.025:
        life_bias = "life20_lean"
    elif s40 - s20 > 0.025:
        life_bias = "life40_lean"
    else:
        life_bias = "life_robust"
    return {
        "size": deck.size,
        "land_bin": land_bin,
        "force_bin": force_bin,
        "counter_bin": counter_bin,
        "threat_bin": threat_bin,
        "life_bias": life_bias,
    }


def cell_id(descriptor: Mapping[str, object]) -> str:
    return "|".join(str(descriptor[k]) for k in ("size", "land_bin", "force_bin", "counter_bin", "threat_bin", "life_bias"))


def map_elites_quality(deck: DeckVector) -> float:
    """Static illumination quality, not a tournament result."""

    return 0.45 * robust_unknown_life_score(deck) + 0.30 * life_static_score(deck, 20) + 0.25 * life_static_score(deck, 40)


def build_static_map_elites_archive(
    seed_decks: Sequence[DeckVector],
    *,
    seed: int = 14014,
    random_samples: int = 2500,
    mutations_per_seed: int = 120,
) -> List[EliteCell]:
    """Build a tiny static MAP-Elites style deck archive.

    This does not replace gameplay evaluation. It creates a diverse candidate
    frontier so later expensive game simulations can test more than one local
    optimum around seed decks.
    """

    rng = Random(seed)
    archive: Dict[str, EliteCell] = {}
    seen = set()

    def add(deck: DeckVector, source: str) -> None:
        if deck.as_tuple() in seen or not plausibility_filter(deck):
            return
        seen.add(deck.as_tuple())
        desc = deck_descriptor(deck)
        cid = cell_id(desc)
        q = map_elites_quality(deck)
        old = archive.get(cid)
        if old is None or q > old.quality:
            archive[cid] = EliteCell(cid, deck, q, desc, source)

    for base in seed_decks:
        add(base, "seed")
        for _ in range(mutations_per_seed):
            add(mutate_deck(base, rng, steps=rng.choice([1, 1, 2, 3, 5])), "mutation")
    for _ in range(random_samples):
        add(random_deck(rng), "random_plausible")
    return sorted(archive.values(), key=lambda e: (e.quality, e.cell_id), reverse=True)


def archive_summary(cells: Sequence[EliteCell]) -> Dict[str, object]:
    if not cells:
        return {"cells": 0, "mean_quality": 0.0, "best_quality": 0.0, "sources": {}}
    source_counts: Dict[str, int] = {}
    size_counts: Dict[str, int] = {}
    life_bias_counts: Dict[str, int] = {}
    for c in cells:
        source_counts[c.source] = source_counts.get(c.source, 0) + 1
        size_counts[str(c.descriptors["size"])] = size_counts.get(str(c.descriptors["size"]), 0) + 1
        life_bias_counts[str(c.descriptors["life_bias"])] = life_bias_counts.get(str(c.descriptors["life_bias"]), 0) + 1
    return {
        "cells": len(cells),
        "mean_quality": sum(c.quality for c in cells) / len(cells),
        "best_quality": max(c.quality for c in cells),
        "worst_quality": min(c.quality for c in cells),
        "sources": source_counts,
        "size_cells": size_counts,
        "life_bias_cells": life_bias_counts,
    }
