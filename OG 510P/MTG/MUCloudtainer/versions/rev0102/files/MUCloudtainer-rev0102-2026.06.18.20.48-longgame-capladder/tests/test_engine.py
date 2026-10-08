from random import Random

from src.muc5.action_schema import Action, PASS, PLAY_ISLAND, cast
from src.muc5.cards import CARD_COUNTERSPELL, CARD_FORCE, CARD_ISLAND, CARD_JACE, CARD_OVERLORD
from src.muc5.deckspace import DeckVector
from src.muc5.engine import GameState, PlayerState, StackSpell, apply_action, legal_actions, play_random_game, start_game


def test_start_game_and_play_island():
    d = DeckVector(40, 24, 6, 4, 3, 3)
    s = start_game(d, d, seed=3)
    actions = legal_actions(s)
    assert PASS in actions
    if PLAY_ISLAND in actions:
        before = s.players[0].hand[CARD_ISLAND]
        apply_action(s, PLAY_ISLAND, Random(3))
        assert s.players[0].hand[CARD_ISLAND] == before - 1
        assert s.players[0].islands_untapped == 1


def test_response_actions_can_target_any_stack_spell():
    p0 = PlayerState()
    p1 = PlayerState(hand={CARD_COUNTERSPELL: 1, CARD_FORCE: 1, CARD_JACE: 1}, islands_untapped=5, life=20)
    s = GameState(
        players=[p0, p1],
        active_player=0,
        priority_player=1,
        frame="RESPONSE",
        stack=[StackSpell(1, 0, CARD_JACE), StackSpell(2, 0, CARD_OVERLORD)],
    )
    compact = [a.compact() for a in legal_actions(s)]
    assert any("target_id=1" in a for a in compact)
    assert any("target_id=2" in a for a in compact)


def test_random_game_smoke_no_crash():
    d = DeckVector(40, 24, 6, 4, 3, 3)
    s = play_random_game(d, d, seed=4, max_decisions=250)
    assert s.frame == "GAME_OVER"
    assert s.winner in (0, 1, None)
    assert s.loss_reason
