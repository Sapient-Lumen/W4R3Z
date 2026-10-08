from __future__ import annotations

from src.muc5.deckspace import DeckVector
from src.muc5.gameplay_map_elites import (
    archive_summary,
    dedupe_candidates,
    gameplay_cell_id,
    pilot_templates_for_deck,
    strategy_descriptor,
    update_archive,
)
from src.muc5.payoff import StrategyBundle
from src.muc5.psro import FiniteOracleCandidate, strategy_signature
from src.muc5.terminal_decomposition import CF34_MULLIGAN, THREAT_MULLIGAN


def _candidate(strategy_id: str, deck: DeckVector, agent: str, mulligan: str) -> FiniteOracleCandidate:
    return FiniteOracleCandidate(
        StrategyBundle(strategy_id, strategy_id, deck, agent, mulligan),
        "unit",
        "unit source",
    )


def test_gameplay_cell_id_is_deck_pilot_and_mulligan_aware():
    deck = DeckVector(40, 18, 10, 2, 6, 4)
    counter = StrategyBundle("a", "d", deck, "infostate_counter_guard", CF34_MULLIGAN)
    pressure = StrategyBundle("b", "d", deck, "infostate_threat_pressure", "land_band")
    business = StrategyBundle("c", "d", deck, "infostate_threat_pressure", "land_band_business")

    assert gameplay_cell_id(counter) != gameplay_cell_id(pressure)
    assert gameplay_cell_id(pressure) != gameplay_cell_id(business)
    assert strategy_descriptor(counter)["pilot_family"] == "counter"
    assert strategy_descriptor(business)["mulligan_bin"] == "business"


def test_pilot_templates_are_bounded_and_descriptor_sensitive():
    counter_wall = DeckVector(60, 25, 21, 4, 5, 5)
    jace_pressure = DeckVector(40, 18, 10, 2, 8, 2)
    wall_templates = pilot_templates_for_deck(counter_wall)
    pressure_templates = pilot_templates_for_deck(jace_pressure)

    assert any(template.family == "counter_guard" for template in wall_templates)
    assert any(template.family in {"threat_pressure", "business_pressure"} for template in pressure_templates)
    assert 1 <= len(wall_templates) <= 2
    assert 1 <= len(pressure_templates) <= 2


def test_update_archive_keeps_best_gameplay_score_per_cell():
    deck = DeckVector(40, 18, 10, 2, 6, 4)
    low = _candidate("low", deck, "infostate_threat_pressure", THREAT_MULLIGAN)
    high = _candidate("high", deck, "infostate_threat_pressure", THREAT_MULLIGAN)
    archive = {}
    by_id = {"low": low, "high": high}

    changed_low = update_archive(
        archive,
        by_id,
        [
            {
                "candidate_strategy": "low",
                "mixture_mean_score": 0.375,
                "mixture_ci_low": 0.1,
                "games": 8,
                "truncations": 0,
                "oracle_family": "unit",
            }
        ],
        generation=0,
    )
    changed_high = update_archive(
        archive,
        by_id,
        [
            {
                "candidate_strategy": "high",
                "mixture_mean_score": 0.625,
                "mixture_ci_low": 0.3,
                "games": 8,
                "truncations": 0,
                "oracle_family": "unit",
            }
        ],
        generation=1,
    )

    assert len(archive) == 1
    assert changed_low[0].strategy_id == "low"
    assert changed_high[0].strategy_id == "high"
    assert next(iter(archive.values())).strategy_id == "high"
    assert archive_summary(archive)["best_strategy_id"] == "high"


def test_dedupe_candidates_rejects_existing_strategy_signatures():
    deck = DeckVector(40, 18, 10, 2, 6, 4)
    existing = StrategyBundle("existing", "d", deck, "infostate_threat_pressure", THREAT_MULLIGAN)
    duplicate = _candidate("dupe", deck, "infostate_threat_pressure", THREAT_MULLIGAN)
    unique = _candidate("unique", deck, "infostate_counter_guard", CF34_MULLIGAN)

    kept = dedupe_candidates([duplicate, unique], forbidden_signatures={strategy_signature(existing)})

    assert [candidate.strategy.strategy_id for candidate in kept] == ["unique"]
