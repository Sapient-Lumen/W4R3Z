from __future__ import annotations

from src.muc5.deckspace import DeckVector
from src.muc5.mulligan import POLICY_LAND_BAND
from src.muc5.neural_oracle import NeuralDeckSource, neural_model_audit, neural_response_candidates
from src.muc5.oracle_reporting import flatten_score_rows, stage_seed_overlaps
from src.muc5.payoff import StrategyBundle
from src.muc5.psro import strategy_signature


def test_neural_model_audit_reports_frozen_mlp_shape() -> None:
    audit = neural_model_audit()
    assert audit["model_path"] == "rev0023_mlp_ranker_model.json"
    assert audit["feature_count"] == 81
    assert int(audit["hidden_size"]) > 0
    assert audit["coefficients_finite"] is True


def test_neural_response_candidates_are_bounded_deduplicated_and_not_population_duplicates() -> None:
    deck = DeckVector(40, 18, 10, 4, 4, 4)
    population_strategy = StrategyBundle("inc", "incumbent", deck, "mlp_ranker_rev0023", POLICY_LAND_BAND)
    sources = [
        NeuralDeckSource("duplicate", deck, POLICY_LAND_BAND, "unit", 10),
        NeuralDeckSource("fresh", DeckVector(40, 17, 12, 3, 5, 3), POLICY_LAND_BAND, "unit", 9),
    ]
    candidates = neural_response_candidates(
        sources,
        agent_names=("mlp_ranker_rev0023", "mlp_ranker_blend_threat_rev0023"),
        max_decks=2,
        forbidden_signatures={strategy_signature(population_strategy)},
    )
    assert candidates
    assert all(c.strategy.strategy_id.startswith("neural_") for c in candidates)
    assert strategy_signature(population_strategy) not in {strategy_signature(c.strategy) for c in candidates}
    assert len({c.strategy.strategy_id for c in candidates}) == len(candidates)


def test_oracle_reporting_flattens_scores_and_detects_seed_overlap() -> None:
    rows = [
        {"stage": "a", "seed": 1, "score": 1.0},
        {"stage": "b", "seed": 1, "score": 0.0},
        {"stage": "b", "seed": 2, "score": 1.0},
    ]
    assert stage_seed_overlaps(rows) == {"a|b": 1}
    flat = flatten_score_rows(
        [
            {
                "candidate_strategy": "c",
                "opponent_scores": {"o": 0.5},
                "deck": {"Island": 20},
                "mixture_support": {"strategy_ids": ["o"]},
            }
        ],
        stage="unit",
    )
    assert flat[0]["stage"] == "unit"
    assert "opponent_scores_json" in flat[0]
    assert "deck_json" in flat[0]
    assert "mixture_support_json" in flat[0]
