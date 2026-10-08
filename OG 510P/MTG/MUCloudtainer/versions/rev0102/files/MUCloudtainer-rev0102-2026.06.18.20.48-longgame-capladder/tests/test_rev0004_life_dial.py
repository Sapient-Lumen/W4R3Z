from src.muc5.deckspace import DeckVector
from src.muc5.engine import legal_actions, start_game
from src.muc5.env import MUC5SlotEnv
from src.muc5.features import observation_vector
from src.muc5.tournament import LIFE_TOTAL_OPTIONS, known_life_config, standard_life_configs, unknown_life_config
from src.muc5.lifedial import life_dial_summary, overlord_unblocked_hits_to_kill
from src.muc5.life_constructor import top_life_dial_decks


def seed_deck() -> DeckVector:
    return DeckVector(40, 24, 6, 4, 3, 3)


def test_starting_life_40_is_visible_in_true_state_and_observation():
    d = seed_deck()
    state = start_game(d, d, seed=44, starting_life=40)
    assert state.starting_life == 40
    assert state.players[0].life == 40
    assert state.players[1].life == 40
    obs0 = state.observation(0)
    assert obs0["starting_life"] == 40
    assert obs0["public_self"]["life"] == 40


def test_env_forwards_starting_life_to_feature_vector():
    d = seed_deck()
    env = MUC5SlotEnv(d, d, starting_life=40, max_action_slots=64)
    obs = env.reset(seed=4)
    assert obs.raw["starting_life"] == 40
    fd = dict(zip(obs.feature_names, obs.feature_vector))
    assert fd["starting_life"] == 40.0
    assert fd["self_life_fraction"] == 1.0
    assert fd["opp_life_fraction"] == 1.0


def test_tournament_config_known_and_unknown_construction_contexts():
    assert LIFE_TOTAL_OPTIONS == (20, 40)
    k40 = known_life_config(40)
    u40 = unknown_life_config(40)
    assert k40.starting_life == 40
    assert k40.construction_knows_life is True
    assert k40.construction_context.known_starting_life == 40
    assert u40.starting_life == 40
    assert u40.construction_knows_life is False
    assert u40.construction_context.known_starting_life is None
    assert len(standard_life_configs()) == 4


def test_life_dial_does_not_change_initial_legal_actions_except_life_metadata():
    d = seed_deck()
    s20 = start_game(d, d, seed=10, starting_life=20)
    s40 = start_game(d, d, seed=10, starting_life=40)
    assert [a.compact() for a in legal_actions(s20)] == [a.compact() for a in legal_actions(s40)]
    assert s20.observation(0)["public_self"]["life"] == 20
    assert s40.observation(0)["public_self"]["life"] == 40


def test_life_dial_scalar_summary_and_static_constructor_shortlist():
    summary = life_dial_summary()
    assert summary["20"]["overlord_unblocked_hits_to_kill"] == 4
    assert summary["40"]["overlord_unblocked_hits_to_kill"] == 8
    assert overlord_unblocked_hits_to_kill(40) == 8
    candidates = [
        DeckVector(40, 24, 6, 4, 3, 3),
        DeckVector(60, 30, 9, 6, 9, 6),
        DeckVector(60, 30, 7, 7, 6, 10),
    ]
    ranked = top_life_dial_decks("unknown_robust", n=2, candidates=candidates)
    assert len(ranked) == 2
    assert ranked[0].selected_score >= ranked[1].selected_score
