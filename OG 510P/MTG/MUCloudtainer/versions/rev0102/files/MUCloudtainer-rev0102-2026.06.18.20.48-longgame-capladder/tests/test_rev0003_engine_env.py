from random import Random

from src.muc5.action_schema import PASS, cast, choose
from src.muc5.agents import HeuristicAgent, RandomAgent, play_agent_game
from src.muc5.cards import CARD_COUNTERSPELL, CARD_FORCE, CARD_ISLAND, CARD_JACE, CARD_OVERLORD, MAX_HAND_SIZE
from src.muc5.deckspace import DeckVector
from src.muc5.engine import GameState, PlayerState, StackSpell, apply_action, legal_actions, start_game
from src.muc5.env import MUC5SlotEnv


def seed_deck() -> DeckVector:
    return DeckVector(40, 24, 6, 4, 3, 3)


def test_main_pass_moves_to_attack_then_postcombat_then_next_turn():
    s = GameState(players=[PlayerState(), PlayerState(library=[CARD_ISLAND] * 5)], active_player=0, frame="MAIN", main_phase="precombat")
    apply_action(s, PASS, Random(1))
    assert s.frame == "ATTACK"
    apply_action(s, PASS, Random(1))
    assert s.frame == "MAIN"
    assert s.main_phase == "postcombat"
    apply_action(s, PASS, Random(1))
    assert s.active_player == 1
    assert s.frame == "MAIN"
    assert s.main_phase == "precombat"


def test_cleanup_after_end_step_does_not_tick_impending_twice():
    p0 = PlayerState(hand={CARD_ISLAND: 8}, impending_4=1)
    p1 = PlayerState(library=[CARD_ISLAND] * 10)
    s = GameState(players=[p0, p1], active_player=0, frame="MAIN", main_phase="postcombat")
    apply_action(s, PASS, Random(2))
    assert s.pending_choice is not None
    assert s.pending_choice.kind == "cleanup_discard"
    assert s.players[0].impending_3 == 1
    assert s.players[0].impending_2 == 0
    discard = choose("cleanup_discard", discard=CARD_ISLAND)
    apply_action(s, discard, Random(2))
    assert s.active_player == 1
    assert s.players[0].impending_3 == 1
    assert s.players[0].impending_2 == 0
    assert s.players[0].total_hand() == MAX_HAND_SIZE


def test_force_pitch_at_one_life_is_legal_but_loses_after_casting():
    p0 = PlayerState()
    p1 = PlayerState(hand={CARD_FORCE: 1, CARD_JACE: 1}, life=1)
    s = GameState(
        players=[p0, p1],
        active_player=0,
        priority_player=1,
        frame="RESPONSE",
        stack=[StackSpell(1, 0, CARD_JACE)],
    )
    force_actions = [a for a in legal_actions(s) if a.kind == "CAST" and a.params.get("card") == CARD_FORCE]
    assert force_actions
    apply_action(s, force_actions[0], Random(3))
    assert s.winner == 0
    assert "life_total" in s.loss_reason


def test_new_jace_from_legend_rule_can_be_used_even_if_old_jace_was_used():
    d = seed_deck()
    s = start_game(d, d, seed=100)
    p0 = s.players[0]
    p0.hand[CARD_JACE] += 1
    p0.islands_untapped = 4
    p0.jace_loyalty = 5
    p0.jace_used_this_turn = True
    apply_action(s, cast(CARD_JACE), Random(4))
    apply_action(s, PASS, Random(4))
    apply_action(s, PASS, Random(4))
    assert s.pending_choice is not None
    assert s.pending_choice.kind == "jace_legend"
    apply_action(s, choose("jace_legend", keep="new"), Random(4))
    assert s.players[0].jace_loyalty == 3
    assert s.players[0].jace_used_this_turn is False
    assert any(a.kind == "ACTIVATE_JACE" for a in legal_actions(s))


def test_slot_env_smoke_and_feature_vector():
    env = MUC5SlotEnv(seed_deck(), seed_deck(), max_action_slots=64, max_decisions=20)
    obs = env.reset(seed=5)
    assert len(obs.action_mask) == 64
    assert len(obs.feature_vector) == len(obs.feature_names)
    assert sum(obs.action_mask) == len(obs.action_strings)
    next_obs, rewards, done, info = env.step(0)
    assert set(rewards) == {0, 1}
    assert "action" in info
    assert len(next_obs.action_mask) == 64


def test_heuristic_agent_game_smoke():
    d = seed_deck()
    state, result = play_agent_game(d, d, HeuristicAgent(), RandomAgent(), seed=8, max_decisions=100)
    assert result.decisions <= 100
    assert result.loss_reason
    assert state.frame == "GAME_OVER"
