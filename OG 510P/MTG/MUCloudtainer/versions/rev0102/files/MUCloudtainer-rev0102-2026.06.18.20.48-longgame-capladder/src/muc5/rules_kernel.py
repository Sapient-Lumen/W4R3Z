from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from .action_schema import Action, PASS, PLAY_ISLAND, activate_jace, cast
from .cards import (
    BLUE_NONLANDS,
    CARD_COUNTERSPELL,
    CARD_FORCE,
    CARD_ISLAND,
    CARD_JACE,
    CARD_OVERLORD,
)


@dataclass
class PlayerPublic:
    life: int = 20
    islands_untapped: int = 0
    islands_tapped: int = 0
    jace_loyalty: Optional[int] = None
    jace_used_this_turn: bool = False
    # legacy aggregate Overlord model; later can track individual permanents.
    overlord_creatures_ready: int = 0
    overlord_creatures_sick: int = 0
    impending_4: int = 0
    impending_3: int = 0
    impending_2: int = 0
    impending_1: int = 0
    library_count: int = 0
    hand_count_public: int = 0


@dataclass
class SpellOnStack:
    controller: int
    card: str
    mode: str = "normal"  # e.g. Overlord full/impending


@dataclass
class DecisionState:
    """Minimal state needed to enumerate legacy legal macro-actions.

    This is not a complete game state. It is the seed legal-action kernel.
    """

    player_to_act: int
    active_player: int
    frame: str  # MAIN_EMPTY_STACK or RESPONSE_TO_SPELL etc.
    hand: Dict[str, int]
    public_self: PlayerPublic
    public_opp: PlayerPublic
    stack: List[SpellOnStack] = field(default_factory=list)
    land_played_this_turn: bool = False


def _hand_count(hand: Dict[str, int], card: str) -> int:
    return int(hand.get(card, 0))


def _can_pay(islands_untapped: int, generic: int, blue: int) -> bool:
    # In MUC-5 all mana sources are blue Islands, so total cost is generic+blue.
    return islands_untapped >= generic + blue


def _force_pitch_cards(hand: Dict[str, int]) -> List[str]:
    """Blue cards available to exile when casting one Force of Will from hand."""
    out: List[str] = []
    for card in BLUE_NONLANDS:
        available = _hand_count(hand, card)
        if card == CARD_FORCE:
            # One Force is the spell being cast; only additional copies can be pitch fodder.
            available -= 1
        if available > 0:
            out.append(card)
    return out


def legal_actions(state: DecisionState) -> List[Action]:
    actions: List[Action] = [PASS]
    h = state.hand
    me = state.public_self

    if state.frame == "MAIN_EMPTY_STACK":
        if not state.land_played_this_turn and _hand_count(h, CARD_ISLAND) > 0:
            actions.append(PLAY_ISLAND)
        if _hand_count(h, CARD_JACE) > 0 and _can_pay(me.islands_untapped, generic=2, blue=2):
            actions.append(cast(CARD_JACE))
        if _hand_count(h, CARD_OVERLORD) > 0 and _can_pay(me.islands_untapped, generic=3, blue=2):
            actions.append(cast(CARD_OVERLORD, mode="full_cost"))
        if _hand_count(h, CARD_OVERLORD) > 0 and _can_pay(me.islands_untapped, generic=1, blue=2):
            actions.append(cast(CARD_OVERLORD, mode="impending"))
        if me.jace_loyalty is not None and not me.jace_used_this_turn:
            actions.append(activate_jace("plus2", target_player="self"))
            actions.append(activate_jace("plus2", target_player="opponent"))
            actions.append(activate_jace("zero"))
            if state.public_opp.overlord_creatures_ready + state.public_opp.overlord_creatures_sick > 0:
                actions.append(activate_jace("minus1", target="opponent_overlord"))
            if me.jace_loyalty >= 12:
                actions.append(activate_jace("ultimate", target_player="opponent"))
                actions.append(activate_jace("ultimate", target_player="self"))

    elif state.frame == "RESPONSE_TO_SPELL":
        if state.stack:
            counter_targets = list(enumerate(state.stack))
            for target_index, target_spell in counter_targets:
                target_card = target_spell.card
                if _hand_count(h, CARD_COUNTERSPELL) > 0 and _can_pay(me.islands_untapped, generic=0, blue=2):
                    actions.append(cast(CARD_COUNTERSPELL, target_index=target_index, target_card=target_card))
                if _hand_count(h, CARD_FORCE) > 0 and _can_pay(me.islands_untapped, generic=3, blue=2):
                    actions.append(cast(CARD_FORCE, payment="mana", target_index=target_index, target_card=target_card))
                if _hand_count(h, CARD_FORCE) > 0 and me.life > 1:
                    for pitch_card in _force_pitch_cards(h):
                        actions.append(cast(CARD_FORCE, payment="pitch", pitch_card=pitch_card, target_index=target_index, target_card=target_card))

    elif state.frame == "ATTACK_CHOICE":
        # Aggregate placeholders. Real version will enumerate distributions to player/Jace.
        if me.overlord_creatures_ready > 0:
            actions.append(Action("ATTACK", {"to_player": me.overlord_creatures_ready, "to_jace": 0}))
            if state.public_opp.jace_loyalty is not None:
                actions.append(Action("ATTACK", {"to_player": 0, "to_jace": me.overlord_creatures_ready}))

    return actions


def demo_state() -> DecisionState:
    return DecisionState(
        player_to_act=0,
        active_player=0,
        frame="MAIN_EMPTY_STACK",
        hand={
            CARD_ISLAND: 1,
            CARD_COUNTERSPELL: 1,
            CARD_FORCE: 1,
            CARD_JACE: 1,
            CARD_OVERLORD: 1,
        },
        public_self=PlayerPublic(life=20, islands_untapped=4, islands_tapped=0, jace_loyalty=None, library_count=33, hand_count_public=5),
        public_opp=PlayerPublic(life=20, islands_untapped=2, islands_tapped=2, jace_loyalty=None, library_count=33, hand_count_public=5),
        stack=[],
        land_played_this_turn=False,
    )


if __name__ == "__main__":
    for a in legal_actions(demo_state()):
        print(a.compact())
