from __future__ import annotations

from pathlib import Path

from src.muc5.action_margin_screen import (
    MARGIN_SCREEN_FEATURES,
    load_margin_screen_model,
    save_margin_screen_model,
    train_margin_screen_model,
)


def _row(i: int, margin: float) -> dict[str, object]:
    return {
        "revision": "unit",
        "situation_id": f"s{i}",
        "action_count": 4 + (i % 8),
        "branched_action_count": 3 + (i % 4),
        "branched_subset": 1 if i % 3 else 0,
        "screen_unique_votes": 1 + (i % 4),
        "screen_vote_entropy_proxy": (i % 5) / 5.0,
        "profile_spread": (i % 7) / 8.0,
        "ranker_spread": (i % 6) / 7.0,
        "screen_score": (i % 9) / 10.0,
        "starting_life": 40 if i % 2 else 20,
        "starting_player": i % 2,
        "situation_best_margin": margin,
        "label_confidence_proxy": min(1.0, margin + 0.2),
    }


def test_rev0044_margin_screen_model_roundtrip(tmp_path: Path) -> None:
    rows = [_row(i, 0.0 if i % 3 else 0.5) for i in range(24)]
    model, holdout = train_margin_screen_model(rows, revision="revtest", source_files=["unit.csv"], seed=17)
    assert model.train_rows > 0
    assert model.holdout_rows == len(holdout)
    assert tuple(model.feature_names) == MARGIN_SCREEN_FEATURES
    p = tmp_path / "model.json"
    save_margin_screen_model(model, p)
    loaded = load_margin_screen_model(p)
    pred = loaded.predict_margin(rows[0])
    score = loaded.predict_queue_score(rows[0])
    assert isinstance(pred, float)
    assert 0.0 <= score <= 1.0
    assert "rmse" in loaded.metrics
