from __future__ import annotations

from dataclasses import asdict, dataclass
from heapq import heappush, heappushpop, nlargest
from typing import Dict, Iterable, List, Tuple

from .cards import STARTING_LIFE_OPTIONS
from .deckspace import DeckVector, enumerate_decks, plausibility_filter
from .probability import DeckProbe, deck_probe

LABEL_KNOWN_20 = "known_life20"
LABEL_KNOWN_40 = "known_life40"
LABEL_UNKNOWN_ROBUST = "unknown_robust"
LIFE_CONSTRUCTOR_LABELS: Tuple[str, str, str] = (LABEL_KNOWN_20, LABEL_KNOWN_40, LABEL_UNKNOWN_ROBUST)


@dataclass(frozen=True)
class LifeDialScore:
    deck_size: int
    island: int
    counterspell: int
    force: int
    jace: int
    overlord: int
    score_life20: float
    score_life40: float
    score_robust_unknown: float
    target_label: str
    selected_score: float

    def to_row(self) -> Dict[str, int | float | str]:
        return asdict(self)


def _shape_terms(deck: DeckVector) -> Dict[str, float]:
    n = float(deck.size)
    return {
        "size40": 1.0 if deck.size == 40 else 0.0,
        "size60": 1.0 if deck.size == 60 else 0.0,
        "force_frac": deck.force / n,
        "counter_frac": deck.counterspell / n,
        "jace_frac": deck.jace / n,
        "overlord_frac": deck.overlord / n,
        "land_frac": deck.island / n,
        "threat_frac": (deck.jace + deck.overlord) / n,
    }


def _life_static_score_from_probe(deck: DeckVector, p: DeckProbe, starting_life: int) -> float:
    if starting_life not in STARTING_LIFE_OPTIONS:
        raise ValueError("starting_life must be 20 or 40")
    s = _shape_terms(deck)
    base = p.crude_probe_score
    force_support = p.p_force_plus_pitch_open7
    early_interaction = p.p_counterspell_online_turn2_play
    early_overlord = p.p_overlord_impending_turn3_play
    jace_curve = p.p_jace_turn4_play
    full_overlord = p.p_overlord_full_turn5_play

    if starting_life == 20:
        # At 20, a 5-power flyer is a real clock. Consistency and Force tempo are
        # rewarded; the static prior is willing to accept 40-card vulnerability.
        return (
            0.38 * base
            + 0.20 * early_overlord
            + 0.12 * full_overlord
            + 0.11 * force_support
            + 0.08 * early_interaction
            + 0.06 * jace_curve
            + 0.03 * s["size40"]
            + 0.02 * min(1.0, s["overlord_frac"] / 0.20)
        )

    # At 40, the same clock is slower. The static prior leans toward long-game
    # resilience: 60-card cushions, Jace access, and denser interaction.
    return (
        0.34 * base
        + 0.17 * jace_curve
        + 0.16 * early_interaction
        + 0.11 * force_support
        + 0.07 * early_overlord
        + 0.04 * full_overlord
        + 0.08 * s["size60"]
        + 0.03 * min(1.0, s["jace_frac"] / 0.15)
    )


def life_static_score(deck: DeckVector, starting_life: int) -> float:
    """A deliberately weak pre-simulation deck-construction prior.

    This is not an optimizer and not MUC theory. Its purpose is to create named
    constructor cohorts so the life-total dial can be plumbed through arenas
    before we have learned deck builders.
    """
    return _life_static_score_from_probe(deck, deck_probe(deck), starting_life)


def robust_unknown_life_score(deck: DeckVector) -> float:
    """Score for constructors that must register before knowing 20 vs 40."""
    p = deck_probe(deck)
    s20 = _life_static_score_from_probe(deck, p, 20)
    s40 = _life_static_score_from_probe(deck, p, 40)
    return 0.5 * (s20 + s40) - 0.12 * abs(s20 - s40)


def all_life_dial_scores(deck: DeckVector) -> Dict[str, LifeDialScore]:
    p = deck_probe(deck)
    s20 = _life_static_score_from_probe(deck, p, 20)
    s40 = _life_static_score_from_probe(deck, p, 40)
    robust = 0.5 * (s20 + s40) - 0.12 * abs(s20 - s40)
    base = dict(
        deck_size=deck.size,
        island=deck.island,
        counterspell=deck.counterspell,
        force=deck.force,
        jace=deck.jace,
        overlord=deck.overlord,
        score_life20=s20,
        score_life40=s40,
        score_robust_unknown=robust,
    )
    return {
        LABEL_KNOWN_20: LifeDialScore(**base, target_label=LABEL_KNOWN_20, selected_score=s20),
        LABEL_KNOWN_40: LifeDialScore(**base, target_label=LABEL_KNOWN_40, selected_score=s40),
        LABEL_UNKNOWN_ROBUST: LifeDialScore(**base, target_label=LABEL_UNKNOWN_ROBUST, selected_score=robust),
    }


def score_for_label(deck: DeckVector, label: str) -> LifeDialScore:
    scores = all_life_dial_scores(deck)
    if label not in scores:
        raise ValueError(f"label must be one of {LIFE_CONSTRUCTOR_LABELS}")
    return scores[label]


def top_life_dial_decks(label: str, n: int = 25, *, candidates: Iterable[DeckVector] | None = None) -> List[LifeDialScore]:
    pool = candidates if candidates is not None else (d for d in enumerate_decks() if plausibility_filter(d))
    return nlargest(n, (score_for_label(d, label) for d in pool), key=lambda r: r.selected_score)


def top_life_dial_decks_all_labels(n: int = 25, *, candidates: Iterable[DeckVector] | None = None) -> Dict[str, List[LifeDialScore]]:
    """Return top decks for all life-constructor labels in one streaming pass.

    Earlier plumbing recomputed exact hypergeometric probes separately for each
    label. This heap-based pass is a small rev0004 refactor/optimization: one
    deck probe feeds the 20-life, 40-life, and robust-unknown shortlists.
    """
    pool = candidates if candidates is not None else (d for d in enumerate_decks() if plausibility_filter(d))
    heaps: Dict[str, List[Tuple[float, int, LifeDialScore]]] = {label: [] for label in LIFE_CONSTRUCTOR_LABELS}
    counter = 0
    for deck in pool:
        scores = all_life_dial_scores(deck)
        for label, score in scores.items():
            item = (score.selected_score, counter, score)
            heap = heaps[label]
            if len(heap) < n:
                heappush(heap, item)
            elif item[0] > heap[0][0]:
                heappushpop(heap, item)
        counter += 1
    return {
        label: [item[2] for item in sorted(heap, key=lambda t: (t[0], t[1]), reverse=True)]
        for label, heap in heaps.items()
    }
