from __future__ import annotations

from collections import Counter
from random import Random

from src.muc5.cards import CARD_COUNTERSPELL, CARD_FORCE, CARD_ISLAND, CARD_JACE, CARD_ORDER, CARD_OVERLORD
from src.muc5.deckspace import DeckVector
from src.muc5.engine import start_game
from src.muc5.mulligan import MULLIGAN_KEEP, MULLIGAN_TAKE, MulliganObservation, legal_mulligan_actions, legal_bottom_actions
from src.muc5.mulligan_ranker import (
    LinearMulliganRankerAgent,
    LinearMulliganRankerModel,
    make_mulligan_agent,
    mulligan_ranker_feature_names,
    mulligan_ranker_feature_vector,
    oracle_bottom_card,
    oracle_keep_label,
)


def tiny_model() -> LinearMulliganRankerModel:
    names = mulligan_ranker_feature_names()
    keep = [0.0] * len(names)
    bottom = [0.0] * len(names)
    keep[names.index("hand_Island")] = 0.5
    keep[names.index("has_any_threat")] = 2.0
    bottom[names.index("candidate_Island")] = 1.0
    return LinearMulliganRankerModel(
        model_id="test",
        feature_names=names,
        keep_weights=tuple(keep),
        keep_intercept=-2.0,
        bottom_weights=tuple(bottom),
        bottom_intercept=0.0,
        source_revision="test",
        training_summary={},
    )


def test_mulligan_observation_features_include_life_and_deck_counts() -> None:
    obs = MulliganObservation(
        player=0,
        stage="keep_or_mulligan",
        mulligans_taken=0,
        hand={CARD_ISLAND: 3, CARD_JACE: 1, CARD_FORCE: 1, CARD_COUNTERSPELL: 2},
        hand_size=7,
        library_count=33,
        starting_life=40,
        deck_counts={CARD_ISLAND: 24, CARD_COUNTERSPELL: 6, CARD_FORCE: 4, CARD_JACE: 3, CARD_OVERLORD: 3},
    )
    names = mulligan_ranker_feature_names()
    vec = dict(zip(names, mulligan_ranker_feature_vector(obs)))
    assert vec["starting_life_40"] == 1.0
    assert vec["deck_size_40"] == 1.0
    assert vec["hand_Island"] == 3.0
    assert vec["deck_frac_Island"] > 0.5


def test_linear_mulligan_agent_returns_legal_keep_and_bottom_actions() -> None:
    agent = LinearMulliganRankerAgent(tiny_model())
    obs = MulliganObservation(
        player=0,
        stage="keep_or_mulligan",
        mulligans_taken=0,
        hand={CARD_ISLAND: 3, CARD_JACE: 1},
        hand_size=4,
        library_count=36,
        starting_life=20,
        deck_counts={CARD_ISLAND: 24, CARD_COUNTERSPELL: 6, CARD_FORCE: 4, CARD_JACE: 3, CARD_OVERLORD: 3},
    )
    action = agent.choose_mulligan_action(obs, [MULLIGAN_KEEP, MULLIGAN_TAKE], Random(1))
    assert action in [MULLIGAN_KEEP, MULLIGAN_TAKE]
    bottom_obs = MulliganObservation(
        player=0,
        stage="bottom",
        mulligans_taken=1,
        hand={CARD_ISLAND: 4, CARD_JACE: 1, CARD_FORCE: 1, CARD_COUNTERSPELL: 1},
        hand_size=7,
        library_count=33,
        bottom_remaining=1,
        starting_life=20,
        deck_counts={CARD_ISLAND: 24, CARD_COUNTERSPELL: 6, CARD_FORCE: 4, CARD_JACE: 3, CARD_OVERLORD: 3},
    )
    bottom = agent.choose_mulligan_action(bottom_obs, legal_bottom_actions(Counter(bottom_obs.hand)), Random(2))
    assert bottom in legal_bottom_actions(Counter(bottom_obs.hand))


def test_start_game_accepts_learned_mulligan_name_after_model_exists() -> None:
    # Standard policies still work through the same lazy factory path.
    assert make_mulligan_agent("land_band").name.startswith("mulligan_rule")


def test_pseudo_oracle_is_reasonable_for_extreme_hands() -> None:
    deck_counts = {CARD_ISLAND: 24, CARD_COUNTERSPELL: 6, CARD_FORCE: 4, CARD_JACE: 3, CARD_OVERLORD: 3}
    good = {CARD_ISLAND: 3, CARD_COUNTERSPELL: 2, CARD_FORCE: 1, CARD_JACE: 1}
    bad = {CARD_ISLAND: 7}
    assert oracle_keep_label(good, deck_counts, 20, 0) == 1
    assert oracle_keep_label(bad, deck_counts, 20, 0) == 0
    assert oracle_bottom_card({CARD_ISLAND: 5, CARD_COUNTERSPELL: 1, CARD_JACE: 1}, deck_counts, 20, 1, 1) == CARD_ISLAND
