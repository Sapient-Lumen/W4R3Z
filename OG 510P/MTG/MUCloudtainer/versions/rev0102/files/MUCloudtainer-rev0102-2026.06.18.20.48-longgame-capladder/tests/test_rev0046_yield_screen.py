from __future__ import annotations

import csv
from pathlib import Path

from src.muc5.action_yield_screen import (
    YIELD_SCREEN_FEATURES,
    YieldScreenModel,
    load_historical_yield_rows,
    load_yield_screen_model,
)

ROOT = Path(__file__).resolve().parents[1]


def test_yield_screen_model_roundtrip_and_predicts() -> None:
    path = ROOT / "data" / "rev0046_yield_screen_model.json"
    if path.exists():
        model = load_yield_screen_model(path)
    else:
        model = YieldScreenModel(
            revision="unit",
            feature_names=YIELD_SCREEN_FEATURES,
            mean=tuple(0.0 for _ in YIELD_SCREEN_FEATURES),
            scale=tuple(1.0 for _ in YIELD_SCREEN_FEATURES),
            coef=tuple(0.01 for _ in YIELD_SCREEN_FEATURES),
            intercept=0.0,
            train_rows=1,
            holdout_rows=1,
            metrics={},
            source_files=(),
        )
    row = {
        "action_count": 12,
        "screen_unique_votes": 3,
        "screen_vote_entropy_proxy": 0.6,
        "profile_spread": 0.2,
        "ranker_spread": 0.1,
        "screen_score": 0.7,
        "starting_life_40": 1,
        "starting_player": 0,
    }
    assert len(model.feature_names) == len(YIELD_SCREEN_FEATURES)
    assert isinstance(model.predict_yield_per_100(row), float)
    q = model.predict_queue_score(row)
    assert 0.0 <= q <= 1.0


def test_historical_yield_rows_have_public_features() -> None:
    path = ROOT / "data" / "rev0045_margin_match_candidates.csv"
    rows = load_historical_yield_rows([path]) if path.exists() else []
    if rows:
        first = rows[0]
        assert "label_yield_per_100_rollouts" in first
        assert "total_branch_rollouts" in first
        assert "action_count" in first
        assert int(first["total_branch_rollouts"]) >= 1


def test_rev0046_yield_match_outputs_if_generated() -> None:
    summary_path = ROOT / "data" / "rev0046_yield_match_summary.json"
    method_path = ROOT / "data" / "rev0046_yield_match_method_summary.csv"
    if not summary_path.exists():
        return
    assert method_path.exists()
    rows = list(csv.DictReader(method_path.open()))
    methods = {r["method"] for r in rows}
    assert {"hard_screen", "margin_screen", "yield_screen"}.issubset(methods)
