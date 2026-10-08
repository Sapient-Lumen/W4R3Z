from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.muc5.action_counterfactual import build_action_counterfactual_specs
from src.muc5.action_label_compare import collect_matched_action_label_comparison
from src.muc5.cpp_segment import build_nochoice_segment_specs
from src.muc5.cpp_segment_benchmark import benchmark_cpp_segment_vs_one_action
from src.muc5.payoff import write_csv
from src.muc5.strategy_sets import mapelite_mulligan_variant_bundles, outcome_ranker_probe_bundles

REV = "rev0037"
DATA = ROOT / "data"


def main() -> None:
    DATA.mkdir(exist_ok=True)

    behavior_strategies = outcome_ranker_probe_bundles(DATA / "seed_decks.json")[:6]
    cf_specs = build_action_counterfactual_specs(
        behavior_strategies,
        life_totals=(20, 40),
        base_seed=3700000,
        max_decisions=430,
        limit_games=12,
    )
    candidate_rows, branch_rows, comparison_rows, transition_rows, label_summary = collect_matched_action_label_comparison(
        cf_specs,
        revision=REV,
        max_situations=12,
        max_actions_per_frame=3,
        sample_high_action_frames=True,
        branch_action_budget=5,
        budget_rng_seed=37037,
        fixed_rollouts_per_action=3,
        adaptive_base_rollouts_per_action=1,
        adaptive_max_extra_rollouts_per_situation=None,
        adaptive_stop_margin=0.50,
        adaptive_target_confidence=0.62,
        branch_max_decisions=320,
    )

    segment_strategies = mapelite_mulligan_variant_bundles(DATA / "rev0014_map_elites_archive.csv", limit_cells=1)
    segment_specs = build_nochoice_segment_specs(
        segment_strategies,
        simulator_revision=REV,
        life_totals=(20, 40),
        reps=1,
        base_seed=3705000,
        max_decisions=540,
        limit_pairs=48,
    )
    segment_games, segment_rows, segment_summary = benchmark_cpp_segment_vs_one_action(segment_specs, revision=REV)

    write_csv(DATA / "rev0037_matched_label_candidates.csv", candidate_rows)
    write_csv(DATA / "rev0037_matched_label_branch_games.csv", branch_rows)
    write_csv(DATA / "rev0037_matched_label_comparison.csv", comparison_rows)
    write_csv(DATA / "rev0037_matched_label_cpp_transitions.csv", transition_rows)
    write_csv(DATA / "rev0037_segment_benchmark_games.csv", segment_games)
    write_csv(DATA / "rev0037_segment_benchmark_segments.csv", segment_rows)

    payload = {
        "revision": REV,
        "codename": "matchedlabel-segmentbench",
        "matched_label_summary": label_summary.as_dict(),
        "segment_benchmark_summary": segment_summary.as_dict(),
        "label_candidate_rows": len(candidate_rows),
        "label_branch_rows": len(branch_rows),
        "label_comparison_rows": len(comparison_rows),
        "label_cpp_transition_rows": len(transition_rows),
        "segment_games": len(segment_games),
        "segment_rows": len(segment_rows),
        "priority_after_rev0037": [
            "increase decisive action-counterfactual labels by screening for frames with nontrivial disagreement/margins",
            "use matched-label audits before promoting future adaptive/racing labelers",
            "turn no-choice segment benchmarking into a live execution candidate only under pre/post SIGv2 gates",
            "run larger MAP-Elites/meta-rank panels only on nontruncated promoted tables",
            "start search/rollout labels for unchosen gameplay alternatives once label uncertainty is better controlled",
        ],
        "notes": [
            "Fixed-equal and adaptive-race labelers consume the same precomputed branch-outcome matrix for each sampled public situation.",
            "Adaptive-race comparisons are label audits, not claims that the resulting learned policy would be stronger.",
            "The C++ segment benchmark is still shadow/parity infrastructure; Python remains semantic authority.",
        ],
    }
    (DATA / "rev0037_matched_label_segment_summary.json").write_text(json.dumps(payload, indent=2))
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
