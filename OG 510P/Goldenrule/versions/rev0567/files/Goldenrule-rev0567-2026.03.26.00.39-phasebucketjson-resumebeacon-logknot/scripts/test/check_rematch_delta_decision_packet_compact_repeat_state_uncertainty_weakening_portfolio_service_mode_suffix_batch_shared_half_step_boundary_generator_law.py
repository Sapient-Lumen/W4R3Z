#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_boundary_generator_law import (
    apply_shared_half_step_boundary_generator_factorization,
    build_batch_shared_half_step_boundary_generator_examples,
    build_batch_shared_half_step_boundary_generator_validation_summary,
    build_boundary_generator_omission_catalog,
    build_service_mode_suffix_batch_shared_half_step_boundary_generator_snapshot,
    factorize_shared_half_step_kernel,
)


def _assert_equal(actual, expected, message: str) -> None:
    if actual != expected:
        raise AssertionError(f'{message}: expected {expected!r}, got {actual!r}')



def main() -> None:
    validation = build_batch_shared_half_step_boundary_generator_validation_summary()
    snapshot = build_service_mode_suffix_batch_shared_half_step_boundary_generator_snapshot()
    omission_catalog = build_boundary_generator_omission_catalog()

    _assert_equal(validation['validated_realized_interval_count'], 153, 'realized interval count mismatch')
    _assert_equal(validation['validated_half_step_selector_index_class_count'], 33, 'selector class count mismatch')
    _assert_equal(validation['half_step_selector_index_range'], [0, 32], 'selector range mismatch')
    _assert_equal(validation['distinct_lower_floor_generator_count'], 17, 'lower-floor generator count mismatch')
    _assert_equal(validation['distinct_upper_cap_generator_count'], 17, 'upper-cap generator count mismatch')
    _assert_equal(validation['distinct_one_sided_generator_interval_count'], 33, 'distinct generator interval count mismatch')
    _assert_equal(validation['shared_identity_generator_interval'], [0, 16], 'shared identity mismatch')
    _assert_equal(validation['generator_closure_interval_count'], 153, 'generator closure size mismatch')
    _assert_equal(validation['generator_closure_reconstructs_full_realized_interval_catalog'], True, 'generator closure theorem mismatch')
    _assert_equal(validation['canonical_factorization_count'], 153, 'canonical factorization count mismatch')
    _assert_equal(validation['factorization_validation_case_count'], 5049, 'factorization case count mismatch')
    _assert_equal(validation['factorization_equivalence_check_count'], 10098, 'equivalence check count mismatch')
    _assert_equal(validation['lower_floor_then_upper_cap_matches_direct_interval_kernel'], True, 'lower-then-upper theorem mismatch')
    _assert_equal(validation['upper_cap_then_lower_floor_matches_direct_interval_kernel'], True, 'upper-then-lower theorem mismatch')
    _assert_equal(validation['factorization_orders_commute_for_every_feasible_interval'], True, 'commutativity mismatch')
    _assert_equal(validation['generator_omission_case_count'], 33, 'generator omission count mismatch')
    _assert_equal(validation['every_one_sided_generator_is_essential'], True, 'generator essentiality mismatch')
    _assert_equal(validation['identity_omission_missing_interval_count'], 1, 'identity omission mismatch')
    _assert_equal(validation['lower_floor_omission_missing_interval_count_range'], [1, 16], 'lower omission range mismatch')
    _assert_equal(validation['upper_cap_omission_missing_interval_count_range'], [1, 16], 'upper omission range mismatch')
    _assert_equal(
        validation['one_sided_generators_form_a_minimal_generating_family_for_realized_feasible_kernels'],
        True,
        'minimal generator theorem mismatch',
    )

    factorization = factorize_shared_half_step_kernel([3, 8])
    _assert_equal(factorization['lower_floor_generator_interval'], [3, 16], 'factorization lower generator mismatch')
    _assert_equal(factorization['upper_cap_generator_interval'], [0, 8], 'factorization upper generator mismatch')
    _assert_equal(factorization['factorization_by_intersection'], [3, 8], 'factorization intersection mismatch')

    execution = apply_shared_half_step_boundary_generator_factorization([3, 8], half_step_selector_index=1)
    _assert_equal(execution['lower_floor_then_upper_cap']['projected_half_step_witness_index'], 6, 'lower-then-upper projection mismatch')
    _assert_equal(execution['upper_cap_then_lower_floor']['projected_half_step_witness_index'], 6, 'upper-then-lower projection mismatch')
    _assert_equal(execution['direct_interval_kernel']['projected_half_step_witness_index'], 6, 'direct projection mismatch')
    _assert_equal(execution['factorization_matches_direct_interval_kernel'], True, 'factorization direct match mismatch')

    omitted_cap = next(row for row in omission_catalog if row['omitted_generator_interval'] == [0, 4])
    _assert_equal(omitted_cap['missing_interval_count'], 5, 'omitted cap missing count mismatch')
    _assert_equal(
        omitted_cap['missing_intervals'],
        [[0, 4], [1, 4], [2, 4], [3, 4], [4, 4]],
        'omitted cap missing cone mismatch',
    )

    omitted_floor = next(row for row in omission_catalog if row['omitted_generator_interval'] == [12, 16])
    _assert_equal(omitted_floor['missing_interval_count'], 5, 'omitted floor missing count mismatch')
    _assert_equal(
        omitted_floor['missing_intervals'],
        [[12, 12], [12, 13], [12, 14], [12, 15], [12, 16]],
        'omitted floor missing cone mismatch',
    )

    examples = build_batch_shared_half_step_boundary_generator_examples()
    _assert_equal(
        examples[0]['canonical_factorization_of_interval_kernel']['direct_interval_kernel']['projected_half_step_witness_index'],
        6,
        'example factorization mismatch',
    )
    _assert_equal(
        examples[1]['identity_kernel_is_the_shared_generator_overlap']['is_identity_kernel'],
        True,
        'identity example mismatch',
    )
    _assert_equal(
        examples[2]['omitting_upper_cap_generator_deletes_exact_upper_boundary_cone']['missing_interval_count'],
        5,
        'cap omission example mismatch',
    )
    _assert_equal(
        examples[3]['omitting_lower_floor_generator_deletes_exact_lower_boundary_cone']['missing_interval_count'],
        5,
        'floor omission example mismatch',
    )

    _assert_equal(
        snapshot['headline_findings']['every_realized_normalized_batch_l2_and_batch_linf_interval_kernel_factors_canonically_into_one_lower_floor_and_one_upper_cap_generator'],
        True,
        'snapshot theorem mismatch',
    )

    print('ok')


if __name__ == '__main__':
    main()
