from __future__ import annotations

from random import Random

from src.muc5.action_schema import PASS, activate_jace
from src.muc5.decision import DecisionFrame
from src.muc5.deckspace import DeckVector
from src.muc5.learned_response_oracle import (
    LEARNED_AGENT_PREFIX,
    LearnedResponseAgent,
    LearnedResponseModel,
    learned_feature_dict,
    learned_feature_names,
    learned_response_candidates,
    load_registry,
    sampled_learned_models,
    write_registry,
)
from src.muc5.payoff import StrategyBundle
from src.muc5.psro import strategy_signature


def _frame(info: dict[str, object]) -> DecisionFrame:
    obs = {
        "frame": "MAIN",
        "player": 0,
        "starting_life": 20,
        "own_library_count": 9,
        "public_self": {"life": 20, "library_count": 9, "islands_tapped": 0, "islands_untapped": 4},
        "public_opponent": {"life": 20, "library_count": 12, "islands_tapped": 3, "islands_untapped": 1},
        "stack": [],
    }
    return DecisionFrame(
        player=0,
        state_revision=1,
        observation=obs,
        legal_actions=(PASS, activate_jace("zero"), activate_jace("plus2", target_player="opponent")),
        information_state=info,
    )


def test_learned_features_exercise_information_state_known_top_cards() -> None:
    zero = activate_jace("zero")
    plus = activate_jace("plus2", target_player="opponent")
    own_island = learned_feature_dict(_frame({"known_top_cards": {"0": "Island"}}), zero)
    own_business = learned_feature_dict(_frame({"known_top_cards": {"0": "JaceTheMindSculptor"}}), zero)
    opp_business = learned_feature_dict(_frame({"known_top_cards": {"1": "ForceOfWill"}}), plus)
    opp_island = learned_feature_dict(_frame({"known_top_cards": {"1": "Island"}}), plus)

    assert own_island["known_own_top_island_jace_zero"] == 1.0
    assert own_business["known_own_top_business_jace_zero"] == 1.0
    assert opp_business["known_opp_top_business_fateseal"] == 1.0
    assert opp_island["known_opp_top_island_fateseal"] == 1.0


def test_registry_roundtrip_validates_and_preserves_feature_shape(tmp_path) -> None:
    weights = {name: 0.0 for name in learned_feature_names()}
    weights["jace_zero"] = 3.0
    model = LearnedResponseModel(f"{LEARNED_AGENT_PREFIX}_g0_77", "threat_pressure", weights, generation=0)
    path = tmp_path / "registry.json"
    write_registry(path, [model], metadata={"unit": True})
    loaded = load_registry(path)

    assert set(loaded) == {f"{LEARNED_AGENT_PREFIX}_g0_77"}
    assert tuple(loaded[f"{LEARNED_AGENT_PREFIX}_g0_77"].as_dict()["weights"].keys()) == learned_feature_names()


def test_learned_agent_ranks_with_registered_weights() -> None:
    weights = {name: 0.0 for name in learned_feature_names()}
    weights["jace_zero"] = 10.0
    agent = LearnedResponseAgent(LearnedResponseModel(f"{LEARNED_AGENT_PREFIX}_g0_78", "threat_pressure", weights))
    frame = _frame({"known_top_cards": {"0": "Island"}})
    assert agent.choose_action_index(frame, Random(3)) == 1


def test_sampled_models_are_deterministic_and_candidates_reject_population_duplicates() -> None:
    models_a = sampled_learned_models(seed=123, generation0_per_profile=1)
    models_b = sampled_learned_models(seed=123, generation0_per_profile=1)
    assert [m.as_dict() for m in models_a] == [m.as_dict() for m in models_b]

    deck = DeckVector(40, 16, 12, 0, 7, 5)
    existing = StrategyBundle("existing", "existing", deck, models_a[0].normalized_id(), "land_band_business")
    candidates = learned_response_candidates(models_a[:1], [deck], forbidden_signatures={strategy_signature(existing)})
    assert candidates
    assert all(candidate.strategy.strategy_id.startswith("learned_") for candidate in candidates)
    assert strategy_signature(existing) not in {strategy_signature(candidate.strategy) for candidate in candidates}
