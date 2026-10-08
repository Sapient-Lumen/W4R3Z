from src.muc5.action_race_audit import compare_fixed_vs_adaptive_labels


def test_compare_fixed_vs_adaptive_labels_basic() -> None:
    rows = []
    for action, vals in {0: [0.0, 0.0, 0.0], 1: [1.0, 1.0, 1.0]}.items():
        for rollout, score in enumerate(vals):
            rows.append({
                "situation_id": "s0",
                "action_index": action,
                "rollout": rollout,
                "actor_score": score,
                "behavior_chosen": 1 if action == 0 else 0,
                "starting_life": 20,
                "starting_player": 0,
                "action_count": 2,
                "union_branched_action_count": 2,
            })
    detail, pivot, summary = compare_fixed_vs_adaptive_labels(rows, revision="test", fixed_rollouts_per_action=3, adaptive_extra_budget=2, min_decisive_margin=0.2)
    assert summary.situations == 1
    assert summary.fixed_decisive_situations == 1
    assert summary.adaptive_decisive_situations == 1
    assert summary.best_set_agreement_rate == 1.0
    assert summary.adaptive_rollouts_spent < summary.fixed_rollouts_spent
    assert len(detail) == 2
    assert pivot[0]["fixed_best_actions"] == "1"
