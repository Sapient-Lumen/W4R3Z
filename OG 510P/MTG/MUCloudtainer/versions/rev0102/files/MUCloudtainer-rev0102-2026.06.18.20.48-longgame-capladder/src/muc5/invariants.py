from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import Dict, List

from .cards import CARD_ISLAND, CARD_JACE, CARD_ORDER, CARD_OVERLORD
from .engine import GameState


@dataclass(frozen=True)
class InvariantReport:
    passed: bool
    errors: List[str]
    counts_by_player: List[Dict[str, int]]


def zone_card_counts(state: GameState, player_idx: int) -> Counter[str]:
    """Count actual MUC-5 cards controlled/owned by a player across zones.

    This intentionally ignores synthetic audit markers such as
    JaceExiledLibraryCards because those are not real cards in the deck.
    """
    p = state.players[player_idx]
    counts: Counter[str] = Counter()
    counts.update(p.library)
    counts.update(p.hand)
    counts.update(p.graveyard)
    counts.update({card: n for card, n in p.exile.items() if card in CARD_ORDER})
    counts[CARD_ISLAND] += p.islands_untapped + p.islands_tapped
    if p.jace_loyalty is not None:
        counts[CARD_JACE] += 1
    # During the legend-rule choice, one Jace is on the battlefield and one is
    # in a small referee limbo until the player chooses which object to keep.
    if state.pending_choice is not None and state.pending_choice.kind == "jace_legend" and state.pending_choice.player == player_idx:
        counts[CARD_JACE] += 1
    counts[CARD_OVERLORD] += (
        p.overlord_ready
        + p.overlord_sick
        + p.overlord_tapped
        + p.impending_4
        + p.impending_3
        + p.impending_2
        + p.impending_1
    )
    if state.pending_combat is not None and state.pending_combat.attacker == player_idx:
        counts[CARD_OVERLORD] += state.pending_combat.total_attackers
    for spell in state.stack:
        if spell.controller == player_idx and spell.card in CARD_ORDER:
            counts[spell.card] += 1
    return counts


def card_conservation_report(state: GameState) -> InvariantReport:
    counts_by_player: List[Dict[str, int]] = []
    errors: List[str] = []
    for player_idx in range(len(state.players)):
        counts = zone_card_counts(state, player_idx)
        counts_by_player.append({card: int(counts.get(card, 0)) for card in CARD_ORDER})
        if player_idx >= len(state.starting_deck_counts):
            continue
        expected = state.starting_deck_counts[player_idx]
        for card in CARD_ORDER:
            got = int(counts.get(card, 0))
            want = int(expected.get(card, 0))
            if got != want:
                errors.append(f"player={player_idx} card={card} got={got} expected={want}")
    return InvariantReport(not errors, errors, counts_by_player)


def assert_card_conservation(state: GameState) -> None:
    report = card_conservation_report(state)
    if not report.passed:
        raise AssertionError("card conservation failed: " + "; ".join(report.errors))
