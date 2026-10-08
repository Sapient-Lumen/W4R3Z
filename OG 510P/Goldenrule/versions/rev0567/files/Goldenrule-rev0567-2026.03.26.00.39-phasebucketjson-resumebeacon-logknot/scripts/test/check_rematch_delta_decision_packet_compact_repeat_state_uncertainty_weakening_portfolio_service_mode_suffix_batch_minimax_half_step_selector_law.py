#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_minimax_half_step_selector_law import (
    build_batch_minimax_half_step_selector_examples,
    build_batch_minimax_half_step_selector_validation_summary,
    build_service_mode_suffix_batch_minimax_half_step_selector_snapshot,
    select_batch_minimax_projection_witness_set,
    summarize_preferred_state_codes_by_linf_half_step_selector_index,
)
from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_mean_projection_law import (
    build_interval_realizer,
)


def _assert_equal(actual, expected, message: str) -> None:
    if actual != expected:
        raise AssertionError(f'{message}: expected {expected!r}, got {actual!r}')


def main() -> None:
    validation = build_batch_minimax_half_step_selector_validation_summary()
    snapshot = build_service_mode_suffix_batch_minimax_half_step_selector_snapshot()

    _assert_equal(validation['validated_total_bundle_count'], 26333, 'bundle count mismatch')
    _assert_equal(validation['validated_endpoint_pair_class_count'], 153, 'endpoint pair count mismatch')
    _assert_equal(validation['validated_half_step_selector_index_class_count'], 33, 'half-step class count mismatch')
    _assert_equal(validation['validation_case_count'], 4028949, 'validation case count mismatch')
    _assert_equal(validation['width_to_bundle_count'], {1: 17, 2: 153, 3: 969, 4: 4845, 5: 20349}, 'width bundle counts mismatch')
    _assert_equal(validation['width_to_endpoint_pair_class_count'], {1: 17, 2: 153, 3: 153, 4: 153, 5: 153}, 'width endpoint counts mismatch')
    _assert_equal(validation['width_to_half_step_selector_index_class_count'], {1: 17, 2: 33, 3: 33, 4: 33, 5: 33}, 'width selector counts mismatch')
    _assert_equal(validation['half_step_selector_index_range'], [0, 32], 'selector range mismatch')
    _assert_equal(validation['path_linf_half_step_selector_matches_bruteforce_argmin'], True, 'bruteforce mismatch')
    _assert_equal(validation['path_linf_uses_the_same_half_step_clamp_formula_as_path_l2'], True, 'shared clamp formula mismatch')
    _assert_equal(validation['tie_interval_count'], 877248, 'tie count mismatch')
    _assert_equal(validation['tie_interval_count_by_preference_width'], {2: 4344, 3: 30864, 4: 159864, 5: 682176}, 'tie count by width mismatch')
    _assert_equal(validation['same_as_path_l2_count'], 2473337, 'same-as-L2 count mismatch')
    _assert_equal(validation['differs_from_path_l2_count'], 1555612, 'diff-vs-L2 count mismatch')
    _assert_equal(validation['same_as_path_l1_count'], 2043577, 'same-as-L1 count mismatch')
    _assert_equal(validation['differs_from_path_l1_count'], 1985372, 'diff-vs-L1 count mismatch')
    _assert_equal(validation['differing_case_count_by_preference_width_vs_l2'], {3: 51098, 4: 277068, 5: 1227446}, 'diff-vs-L2 by width mismatch')
    _assert_equal(validation['differing_case_count_by_preference_width_vs_l1'], {2: 11504, 3: 66624, 4: 408336, 5: 1498908}, 'diff-vs-L1 by width mismatch')
    _assert_equal(validation['width_greater_than_one_realizes_all_half_step_selector_classes'], True, 'width>=2 coverage mismatch')
    _assert_equal(validation['width_one_realizes_only_singleton_selector_classes'], True, 'width1 singleton mismatch')

    summary = summarize_preferred_state_codes_by_linf_half_step_selector_index(['S10', 'S10', 'S8'])
    _assert_equal(summary['endpoint_pair_summary'], [0, 3], 'endpoint pair summary mismatch')
    _assert_equal(summary['half_step_selector_index'], 3, 'selector index mismatch')
    _assert_equal(summary['selector_interval_summary'], [1, 2], 'selector interval mismatch')

    selection = select_batch_minimax_projection_witness_set(
        [build_interval_realizer(0, 2)],
        preferred_state_codes=['S10', 'S10', 'S8'],
    )
    _assert_equal(selection['projected_optimal_state_codes'], ['S9', 'E8'], 'all-three-split minimax selection mismatch')

    examples = build_batch_minimax_half_step_selector_examples()
    _assert_equal(examples[0]['bundle_a_selection']['projected_optimal_state_codes'], ['E8'], 'shared-selector example A mismatch')
    _assert_equal(examples[0]['bundle_b_selection']['projected_optimal_state_codes'], ['E8'], 'shared-selector example B mismatch')
    _assert_equal(examples[1]['path_linf_selection']['projected_optimal_state_codes'], ['S10', 'S9'], 'endpoint-only tie example Linf mismatch')
    _assert_equal(examples[1]['path_l2_selection']['projected_optimal_state_codes'], ['S10'], 'endpoint-only tie example L2 mismatch')
    _assert_equal(examples[1]['path_l1_selection']['projected_optimal_state_codes'], ['S10'], 'endpoint-only tie example L1 mismatch')
    _assert_equal(examples[2]['path_linf_selection']['projected_optimal_state_codes'], ['S9', 'E8'], 'all-three split Linf mismatch')
    _assert_equal(examples[2]['path_l2_selection']['projected_optimal_state_codes'], ['S9'], 'all-three split L2 mismatch')
    _assert_equal(examples[2]['path_l1_selection']['projected_optimal_state_codes'], ['S10'], 'all-three split L1 mismatch')
    _assert_equal(examples[3]['decoded_half_step_selector_index']['selector_interval_summary'], [4, 5], 'decoded half-step example mismatch')
    _assert_equal(examples[4]['infeasible_selection']['selection_status'], 'infeasible', 'infeasible example mismatch')

    _assert_equal(
        snapshot['headline_findings']['path_linf_bundles_collapse_directly_from_26333_audited_bundles_to_33_half_step_selector_classes'],
        [26333, 33],
        'snapshot collapse mismatch',
    )

    print('ok')


if __name__ == '__main__':
    main()
