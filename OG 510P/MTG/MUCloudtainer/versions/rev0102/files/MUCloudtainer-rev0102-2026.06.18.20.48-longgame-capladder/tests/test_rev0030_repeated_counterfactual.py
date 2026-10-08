from __future__ import annotations

from random import Random

from src.muc5.mulligan import MULLIGAN_KEEP, MULLIGAN_TAKE, MulliganObservation
from src.muc5.mulligan_counterfactual import CounterfactualMulliganModel, CounterfactualFirstLookMulliganAgent, REPEATED_COUNTERFACTUAL_MODEL_NAME
from src.muc5.mulligan_ranker import LinearMulliganRankerAgent, load_mulligan_ranker_model, model_path_for_name, OUTCOME_MODEL_NAME, mulligan_ranker_feature_names
from src.muc5.opening_counterfactual import build_counterfactual_specs
from src.muc5.opening_counterfactual_repeat import run_repeated_opening_counterfactual_panel
from src.muc5.payoff import load_seed_decks
from src.muc5.nochoice_segments import aggregate_nochoice_fingerprint_rows, play_public_game_with_nochoice_fingerprints
from src.muc5.public_agents import make_public_agent
from src.muc5.mulligan_ranker import make_mulligan_agent


def test_repeated_counterfactual_panel_one_spec_one_rep_runs():
    seed_decks = load_seed_decks("data/seed_decks.json")
    spec = build_counterfactual_specs(seed_decks, samples_per_shell_life=1, base_seed=303030)[0]
    result = run_repeated_opening_counterfactual_panel([spec], rollout_reps=1, revision="test")
    assert result.summary["branch_games"] == 2
    assert result.summary["paired_rows"] == 1
    assert result.summary["transition_events"] > 0
    assert result.summary["skipped_cpp_events"] == 0
    assert result.summary["cpp_mismatches"] == 0
    pair = result.paired_rows[0]
    assert pair["rollout_reps"] == 1
    assert pair["better_branch_mean"] in {"keep", "mulligan", "tie"}


def test_repeated_counterfactual_agent_name_and_first_decision_contract():
    features = tuple(mulligan_ranker_feature_names())
    model = CounterfactualMulliganModel(
        model_id="test_positive_delta",
        feature_names=features,
        delta_weights=tuple(0.0 for _ in features),
        delta_intercept=1.0,
        source_revision="test",
        fallback_mulligan=OUTCOME_MODEL_NAME,
        training_summary={},
    )
    fallback = LinearMulliganRankerAgent(load_mulligan_ranker_model(model_path_for_name(OUTCOME_MODEL_NAME)), name=OUTCOME_MODEL_NAME)
    agent = CounterfactualFirstLookMulliganAgent(model=model, fallback=fallback, name=REPEATED_COUNTERFACTUAL_MODEL_NAME)
    obs = MulliganObservation(
        player=0,
        stage="keep_or_mulligan",
        mulligans_taken=0,
        hand={"Island": 2, "Counterspell": 1, "ForceOfWill": 1, "JaceTheMindSculptor": 1, "OverlordOfTheFloodpits": 2},
        hand_size=7,
        library_count=33,
        bottom_remaining=0,
        starting_life=20,
        deck_counts={"Island": 24, "Counterspell": 6, "ForceOfWill": 4, "JaceTheMindSculptor": 3, "OverlordOfTheFloodpits": 3},
    )
    assert agent.name == REPEATED_COUNTERFACTUAL_MODEL_NAME
    assert agent.choose_mulligan_action(obs, [MULLIGAN_KEEP, MULLIGAN_TAKE], Random(1)) == MULLIGAN_TAKE


def test_nochoice_segment_fingerprints_have_start_and_end_hashes():
    seed_decks = load_seed_decks("data/seed_decks.json")
    deck0 = seed_decks["forty_force_jace_pressure"]
    deck1 = seed_decks["sixty_counterwall_jace"]
    state, result, summary, segments = play_public_game_with_nochoice_fingerprints(
        deck0,
        deck1,
        make_public_agent("code_jace_lock_rev0013"),
        make_public_agent("counter_happy"),
        game_id="test_nochoice_fp",
        seed=3030300,
        starting_life=20,
        max_decisions=160,
        mulligan_agents=(make_mulligan_agent("land_band"), make_mulligan_agent("land_band_business")),
    )
    assert summary.decisions > 0
    assert len(segments) > 0
    assert all(s.start_fingerprint and s.end_fingerprint for s in segments)
    agg = aggregate_nochoice_fingerprint_rows([summary], segments)
    assert agg.segments == len(segments)
    assert agg.total_forced_actions == sum(s.length for s in segments)
