from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from src.muc5.action_margin_compare import QueueMethodStats

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"


def test_rev0045_margin_match_summary_artifacts() -> None:
    summary_path = DATA / "rev0045_margin_match_summary.json"
    assert summary_path.exists()
    payload = json.loads(summary_path.read_text())
    summary = payload["summary"]
    assert summary["revision"] == "rev0045"
    assert summary["hard_selected"] == 10
    assert summary["margin_selected"] == 10
    assert summary["union_selected"] >= 10
    assert summary["overlap_selected"] >= 1
    assert summary["branch_truncations"] == 0
    assert summary["cpp_checked_transitions"] >= 10000
    assert summary["cpp_skipped_transitions"] == 0
    assert summary["cpp_mismatches"] == 0


def test_rev0045_method_rows_are_matched() -> None:
    methods = pd.read_csv(DATA / "rev0045_margin_match_methods.csv")
    assert set(methods["method"]) == {"hard_screen", "margin_screen"}
    assert len(methods[methods["method"] == "hard_screen"]) == 10
    assert len(methods[methods["method"] == "margin_screen"]) == 10
    assert methods["branched"].sum() == 20
    assert methods["branch_rollouts"].sum() > 100
    assert methods["decisive"].sum() >= 1


def test_rev0045_queue_method_stats_dataclass() -> None:
    stats = QueueMethodStats(
        method="x",
        selected_situations=1,
        branched_situations=1,
        high_action_selected=1,
        decisive_situations=1,
        branch_rollouts=5,
        decisive_per_100_rollouts=20.0,
        mean_situation_best_margin=0.5,
        mean_label_confidence_proxy=0.25,
        mean_behavior_chosen_best=1.0,
        mean_action_count=7.0,
        mean_queue_score=0.6,
    )
    d = stats.as_dict()
    assert d["method"] == "x"
    assert d["decisive_per_100_rollouts"] == 20.0
