from pathlib import Path

from src.muc5.cpp_segment import (
    PUBLIC_INTERFACE,
    REWARD_CONVENTION,
    build_nochoice_segment_specs,
    run_nochoice_segment_cpp_panel_batched,
)
from src.muc5.promotion import PromotionGateConfig, audit_promotion_rows
from src.muc5.strategy_sets import mapelite_mulligan_variant_bundles

ROOT = Path(__file__).resolve().parents[1]


def test_mapelite_mulligan_variant_bundles_load():
    bundles = mapelite_mulligan_variant_bundles(ROOT / "data" / "rev0014_map_elites_archive.csv", limit_cells=1)
    assert len(bundles) == 4
    assert any("repeated_counterfactual" in str(b.mulligan_policy) for b in bundles)
    assert all(b.deck.size in {40, 60} for b in bundles)


def test_batched_cpp_segment_rows_have_promotion_columns():
    bundles = mapelite_mulligan_variant_bundles(ROOT / "data" / "rev0014_map_elites_archive.csv", limit_cells=1)[:2]
    specs = build_nochoice_segment_specs(
        bundles,
        simulator_revision="rev0032test",
        life_totals=(20,),
        reps=1,
        base_seed=932000,
        max_decisions=120,
        limit_pairs=2,
    )
    games, segments, summary = run_nochoice_segment_cpp_panel_batched(specs, revision="rev0032test")
    assert games
    assert segments
    assert summary.cpp_segment_mismatches == 0
    row = games[0]
    assert row["reward_convention"] == REWARD_CONVENTION
    assert row["interface"] == PUBLIC_INTERFACE
    report = audit_promotion_rows(
        games,
        replay_results=(),
        config=PromotionGateConfig(simulator_revision="rev0032test", require_replay_sample=False, max_truncation_rate=1.0),
    )
    assert report.passed, report.errors
