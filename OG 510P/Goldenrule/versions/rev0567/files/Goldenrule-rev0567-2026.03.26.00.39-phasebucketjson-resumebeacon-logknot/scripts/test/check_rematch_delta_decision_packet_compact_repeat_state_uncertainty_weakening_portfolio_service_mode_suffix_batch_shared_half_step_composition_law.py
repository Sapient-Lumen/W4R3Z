#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_composition_law import (
    apply_shared_half_step_interval_kernel,
    build_batch_shared_half_step_composition_examples,
    build_batch_shared_half_step_composition_validation_summary,
    build_service_mode_suffix_batch_shared_half_step_composition_snapshot,
    compose_shared_half_step_interval_kernels,
)


def _assert_equal(actual, expected, message: str) -> None:
    if actual != expected:
        raise AssertionError(f'{message}: expected {expected!r}, got {actual!r}')


def main() -> None:
    validation = build_batch_shared_half_step_composition_validation_summary()
    snapshot = build_service_mode_suffix_batch_shared_half_step_composition_snapshot()

    _assert_equal(validation['validated_realized_interval_count'], 153, 'realized interval count mismatch')
    _assert_equal(validation['validated_half_step_selector_index_class_count'], 33, 'selector class count mismatch')
    _assert_equal(validation['half_step_selector_index_range'], [0, 32], 'selector range mismatch')
    _assert_equal(validation['idempotence_validation_case_count'], 5049, 'idempotence case count mismatch')
    _assert_equal(validation['feasible_overlap_ordered_interval_pair_count'], 15657, 'feasible ordered pair count mismatch')
    _assert_equal(validation['feasible_overlap_composition_case_count'], 516681, 'feasible composition case count mismatch')
    _assert_equal(validation['feasible_overlap_composition_equivalence_check_count'], 1033362, 'equivalence check count mismatch')
    _assert_equal(validation['disjoint_ordered_interval_pair_count'], 7752, 'disjoint ordered pair count mismatch')
    _assert_equal(validation['disjoint_order_sensitive_case_count'], 255816, 'disjoint order-sensitive count mismatch')
    _assert_equal(validation['distinct_pairwise_intersection_interval_count'], 153, 'distinct intersection count mismatch')
    _assert_equal(validation['distinct_input_to_output_transition_pair_count'], 577, 'distinct transition pair count mismatch')
    _assert_equal(
        validation['distinct_transition_pair_breakdown'],
        {
            'preserve_within_band': 33,
            'clamp_up_to_lower_boundary': 272,
            'clamp_down_to_upper_boundary': 272,
        },
        'transition pair breakdown mismatch',
    )
    _assert_equal(validation['feasible_overlap_compositions_equal_direct_intersection_kernel'], True, 'intersection theorem mismatch')
    _assert_equal(validation['feasible_overlap_compositions_commute'], True, 'commutativity theorem mismatch')
    _assert_equal(validation['single_interval_kernels_are_idempotent'], True, 'idempotence theorem mismatch')
    _assert_equal(validation['disjoint_interval_compositions_are_totally_order_sensitive'], True, 'disjoint order-sensitivity mismatch')
    _assert_equal(validation['pairwise_intersections_regenerate_the_full_realized_interval_catalog'], True, 'intersection regeneration mismatch')

    overlap_forward = compose_shared_half_step_interval_kernels([0, 5], [3, 8], half_step_selector_index=3)
    overlap_reverse = compose_shared_half_step_interval_kernels([3, 8], [0, 5], half_step_selector_index=3)
    _assert_equal(overlap_forward['second_pass']['projected_half_step_witness_index'], 6, 'overlap forward output mismatch')
    _assert_equal(overlap_reverse['second_pass']['projected_half_step_witness_index'], 6, 'overlap reverse output mismatch')
    _assert_equal(overlap_forward['direct_intersection_kernel']['projected_half_step_witness_index'], 6, 'direct intersection output mismatch')
    _assert_equal(overlap_forward['second_pass']['projected_fingerprint_word'], overlap_reverse['second_pass']['projected_fingerprint_word'], 'overlap fingerprint mismatch')

    idempotent_once = apply_shared_half_step_interval_kernel([4, 9], half_step_selector_index=2)
    idempotent_twice = apply_shared_half_step_interval_kernel([4, 9], half_step_selector_index=idempotent_once['projected_half_step_witness_index'])
    _assert_equal(idempotent_once['projected_half_step_witness_index'], 8, 'idempotent first output mismatch')
    _assert_equal(idempotent_twice['projected_half_step_witness_index'], 8, 'idempotent second output mismatch')

    disjoint_forward = compose_shared_half_step_interval_kernels([0, 2], [5, 7], half_step_selector_index=17)
    disjoint_reverse = compose_shared_half_step_interval_kernels([5, 7], [0, 2], half_step_selector_index=17)
    _assert_equal(disjoint_forward['second_pass']['projected_half_step_witness_index'], 10, 'disjoint forward output mismatch')
    _assert_equal(disjoint_reverse['second_pass']['projected_half_step_witness_index'], 4, 'disjoint reverse output mismatch')

    examples = build_batch_shared_half_step_composition_examples()
    _assert_equal(examples[0]['overlap_composition_is_order_independent']['forward']['second_pass']['projected_half_step_witness_index'], 6, 'example overlap mismatch')
    _assert_equal(examples[1]['single_interval_idempotence']['second_application']['projected_half_step_witness_index'], 8, 'example idempotence mismatch')
    _assert_equal(examples[2]['disjoint_intervals_are_totally_order_sensitive']['forward']['second_pass']['projected_half_step_witness_index'], 10, 'example disjoint forward mismatch')
    _assert_equal(examples[2]['disjoint_intervals_are_totally_order_sensitive']['reverse']['second_pass']['projected_half_step_witness_index'], 4, 'example disjoint reverse mismatch')

    _assert_equal(
        snapshot['headline_findings']['once_batch_requests_are_normalized_to_half_step_selector_index_feasible_interval_kernels_compose_by_interval_intersection'],
        True,
        'snapshot theorem mismatch',
    )

    print('ok')


if __name__ == '__main__':
    main()
