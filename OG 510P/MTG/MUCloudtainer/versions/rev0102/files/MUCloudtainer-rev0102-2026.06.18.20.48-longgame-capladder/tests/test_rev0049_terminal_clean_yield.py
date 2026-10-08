from __future__ import annotations

from pathlib import Path

from src.muc5.terminal_clean import mark_terminal_clean_rows, summarize_terminal_clean_rows, terminal_clean_by_strategy
from src.muc5.public_agents import make_public_agent


def test_terminal_clean_annotations_and_summary() -> None:
    rows = [
        {"strategy0": "a", "strategy1": "b", "is_truncation": False, "loss_reason": "life_total"},
        {"strategy0": "b", "strategy1": "a", "is_truncation": True, "loss_reason": "max_decisions_reached"},
    ]
    marked = mark_terminal_clean_rows(rows, revision="revtest", max_decisions=900)
    assert marked[0]["terminal_clean_game"] is True
    assert marked[1]["terminal_clean_game"] is False
    summary = summarize_terminal_clean_rows(marked, revision="revtest", max_decisions=900)
    assert summary.rows == 2
    assert summary.terminal_clean is False
    assert summary.truncation_rows == 1
    by_strategy = terminal_clean_by_strategy(marked)
    assert {r["strategy"] for r in by_strategy} == {"a", "b"}


def test_rev0049_counterfactual_ranker_alias_if_model_exists() -> None:
    model_path = Path(__file__).resolve().parents[1] / "data" / "rev0049_counterfactual_action_ranker_model.json"
    if not model_path.exists():
        return
    agent = make_public_agent("counterfactual_ranker_blend_counter_rev0049")
    assert "rev0049" in agent.name
