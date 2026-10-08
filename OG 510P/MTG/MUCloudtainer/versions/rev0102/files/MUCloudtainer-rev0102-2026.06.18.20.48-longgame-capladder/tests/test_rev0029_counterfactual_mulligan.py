from __future__ import annotations

from random import Random

from src.muc5.deckspace import DeckVector
from src.muc5.mulligan import MULLIGAN_KEEP, MULLIGAN_TAKE, MulliganObservation
from src.muc5.mulligan_counterfactual import (
    COUNTERFACTUAL_MODEL_NAME,
    CounterfactualFirstLookMulliganAgent,
    CounterfactualMulliganModel,
    counterfactual_training_rows_from_pairs,
    train_counterfactual_mulligan_model,
)
from src.muc5.mulligan_ranker import make_mulligan_agent, mulligan_ranker_feature_names
from src.muc5.nochoice_segments import aggregate_nochoice_summaries, play_public_game_with_nochoice_audit
from src.muc5.public_agents import make_public_agent


def test_counterfactual_training_rows_and_model_fit_minimal() -> None:
    deck = DeckVector(40, 24, 6, 4, 3, 3)
    deck_counts = {"d": deck.counts()}
    base = {
        "deck0": "d",
        "starting_life": 20,
        "starting_player": 0,
        "initial_hand_Island": 3,
        "initial_hand_Counterspell": 1,
        "initial_hand_ForceOfWill": 1,
        "initial_hand_JaceTheMindSculptor": 1,
        "initial_hand_OverlordOfTheFloodpits": 1,
    }
    pairs = []
    for i in range(12):
        row = dict(base)
        row["pair_id"] = f"p{i}"
        row["keep_score"] = 1.0 if i % 3 == 0 else 0.0
        row["mulligan_score"] = 0.0 if i % 3 == 0 else 1.0
        pairs.append(row)
    rows = counterfactual_training_rows_from_pairs(pairs, deck_counts)
    model, metrics = train_counterfactual_mulligan_model(rows)
    assert len(rows) == 12
    assert len(model.feature_names) == len(mulligan_ranker_feature_names())
    assert metrics["rows"] == 12
    assert metrics["feature_count"] == len(mulligan_ranker_feature_names())


def test_counterfactual_agent_delegates_after_first_decision() -> None:
    features = mulligan_ranker_feature_names()
    model = CounterfactualMulliganModel(
        model_id="test",
        feature_names=features,
        delta_weights=tuple(0.0 for _ in features),
        delta_intercept=1.0,  # positive means mulligan first look
        source_revision="test",
        fallback_mulligan="keep_always",
        training_summary={},
    )
    fallback = make_mulligan_agent("keep_always")
    agent = CounterfactualFirstLookMulliganAgent(model=model, fallback=fallback)
    obs0 = MulliganObservation(
        player=0,
        stage="keep_or_mulligan",
        mulligans_taken=0,
        hand={"Island": 7},
        hand_size=7,
        library_count=33,
        bottom_remaining=0,
        starting_life=20,
        deck_counts={"Island": 40},
    )
    obs1 = MulliganObservation(
        player=0,
        stage="keep_or_mulligan",
        mulligans_taken=1,
        hand={"Island": 7},
        hand_size=7,
        library_count=33,
        bottom_remaining=0,
        starting_life=20,
        deck_counts={"Island": 40},
    )
    assert agent.choose_mulligan_action(obs0, [MULLIGAN_KEEP, MULLIGAN_TAKE], Random(1)) == MULLIGAN_TAKE
    assert agent.choose_mulligan_action(obs1, [MULLIGAN_KEEP, MULLIGAN_TAKE], Random(1)) == MULLIGAN_KEEP


def test_counterfactual_factory_name_available_after_model_exists() -> None:
    # The generated rev0029 model is present in the archive after the script run;
    # this verifies future payoff/replay factories can load it by name.
    agent = make_mulligan_agent(COUNTERFACTUAL_MODEL_NAME)
    assert agent.name == COUNTERFACTUAL_MODEL_NAME


def test_nochoice_segment_audit_runs_and_aggregates() -> None:
    deck = DeckVector(40, 24, 6, 4, 3, 3)
    state, result, summary = play_public_game_with_nochoice_audit(
        deck,
        deck,
        make_public_agent("counter_happy"),
        make_public_agent("threat_rush"),
        game_id="unit_nochoice",
        seed=2929,
        starting_player=0,
        starting_life=20,
        max_decisions=80,
        mulligan_agents=("keep_always", "keep_always"),
    )
    agg = aggregate_nochoice_summaries([summary])
    assert summary.decisions > 0
    assert summary.choice_frames + summary.forced_frames <= summary.decisions
    assert agg.games == 1
    assert agg.decisions == summary.decisions
