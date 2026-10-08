from random import Random

from src.muc5.cards import CARD_ISLAND, CARD_JACE
from src.muc5.deckspace import DeckVector
from src.muc5.engine import GameState, PlayerState, legal_actions, start_game
from src.muc5.env import MUC5SlotEnv
from src.muc5.features import observation_vector
from src.muc5.invariants import assert_card_conservation, card_conservation_report
from src.muc5.mulligan import (
    POLICY_KEEP_ALWAYS,
    POLICY_LAND_BAND,
    MulliganPolicy,
    choose_bottom_cards,
    london_mulligan_opening_hand,
)


def seed_deck() -> DeckVector:
    return DeckVector(40, 24, 6, 4, 3, 3)


def test_keep_always_mulligan_matches_opening_size():
    library = [CARD_ISLAND] * 40
    rng = Random(1)
    hand, result = london_mulligan_opening_hand(library, rng, POLICY_KEEP_ALWAYS, player=0)
    assert sum(hand.values()) == 7
    assert result.mulligans_taken == 0
    assert result.kept_hand_size == 7
    assert len(library) == 33


def test_land_band_policy_mulligans_bad_all_spell_hand_and_bottoms():
    # Top seven are all Jace, so a land-band policy must mulligan at least once.
    library = [CARD_ISLAND] * 33 + [CARD_JACE] * 7
    rng = Random(2)
    hand, result = london_mulligan_opening_hand(library, rng, MulliganPolicy(POLICY_LAND_BAND, max_mulligans=1), player=1)
    assert result.mulligans_taken == 1
    assert result.kept_hand_size == 6
    assert len(library) == 34
    assert sum(result.bottomed.values()) == 1


def test_choose_bottom_cards_keeps_two_islands_when_possible():
    hand = {CARD_ISLAND: 4, CARD_JACE: 2}
    bottomed = choose_bottom_cards(hand, 2)
    assert bottomed[CARD_ISLAND] == 2
    assert hand[CARD_ISLAND] == 2


def test_start_game_with_mulligan_policy_records_public_metadata_and_features():
    d = seed_deck()
    state = start_game(d, d, seed=9, mulligan_policy=POLICY_LAND_BAND)
    assert len(state.mulligan_log) == 2
    assert all("mulligans_taken" in row for row in state.mulligan_log)
    obs = state.observation(0)
    assert "mulligans_taken" in obs["public_self"]
    vec, names = observation_vector(obs)
    fd = dict(zip(names, vec))
    assert "self_mulligans_taken" in fd
    assert "opp_mulligans_taken" in fd


def test_slot_env_forwards_mulligan_policy():
    d = seed_deck()
    env = MUC5SlotEnv(d, d, max_action_slots=64, mulligan_policy=POLICY_LAND_BAND)
    obs = env.reset(seed=12)
    assert "self_mulligans_taken" in obs.feature_names
    assert env.state is not None
    assert len(env.state.mulligan_log) == 2


def test_aggregate_overlord_combat_action_count_has_small_formula():
    p0 = PlayerState(overlord_ready=3)
    p1 = PlayerState(jace_loyalty=3)
    state = GameState(players=[p0, p1], active_player=0, frame="ATTACK")
    actions = legal_actions(state)
    # PASS plus all nonzero splits of up to three identical Overlords between face/Jace.
    assert len(actions) == 10


def test_card_conservation_holds_after_start_and_some_actions():
    d = seed_deck()
    state = start_game(d, d, seed=22, mulligan_policy=POLICY_LAND_BAND)
    assert_card_conservation(state)
    report = card_conservation_report(state)
    assert report.passed
    assert report.counts_by_player[0][CARD_ISLAND] == d.island
