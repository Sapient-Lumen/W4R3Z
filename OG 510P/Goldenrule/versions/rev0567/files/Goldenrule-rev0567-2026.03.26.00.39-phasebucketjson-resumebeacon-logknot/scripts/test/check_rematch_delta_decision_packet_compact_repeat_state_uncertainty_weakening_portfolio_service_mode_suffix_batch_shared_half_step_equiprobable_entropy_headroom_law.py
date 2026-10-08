#!/usr/bin/env python3
from __future__ import annotations

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_equiprobable_entropy_headroom_law import (
    build_equiprobable_entropy_headroom_summary,
)


def main() -> None:
    summary = build_equiprobable_entropy_headroom_summary()
    assert summary['global_exact_word_prefix_has_less_than_one_total_residual_bit_over_uniform_entropy'] is True
    assert summary['all_positive_state_known_local_choice_headroom_is_concentrated_in_interior_singleton_families'] is True
    assert summary['size_1_and_size_2_local_choice_families_are_entropy_tight'] is True
    assert summary['changing_tree_shape_cannot_recover_more_bits_than_these_headroom_profiles_allow_under_equiprobable_models'] is True
    assert summary['max_mean_headroom_profile_name'] == 'state_prefix'

    state = summary['state_prefix_profile']
    canonical = summary['canonical_shortest_word_prefix_profile']
    exact = summary['global_exact_word_prefix_profile']
    choice = summary['state_known_local_choice_prefix_profile']
    by_cat = summary['state_known_local_choice_headroom_by_state_category']

    assert state['represented_count'] == 153
    assert canonical == state
    assert math.isclose(state['total_headroom_bits'], 1121 - 153 * math.log2(153))
    assert math.isclose(state['mean_headroom_bits'], 1121 / 153 - math.log2(153))
    assert state['catalogs_needed_to_save_one_whole_bit_at_mean_rate'] == 15

    assert exact['represented_count'] == 513
    assert math.isclose(exact['total_headroom_bits'], 4619 - 513 * math.log2(513))
    assert math.isclose(exact['mean_headroom_bits'], 4619 / 513 - math.log2(513))
    assert exact['catalogs_needed_to_save_one_whole_bit_at_mean_rate'] == 923
    assert exact['total_headroom_bits'] < 1.0

    assert choice['represented_count'] == 513
    assert math.isclose(choice['total_headroom_bits'], 1350 - 15 * 18 * math.log2(18) - 105 * 2 * math.log2(2))
    assert math.isclose(choice['mean_headroom_bits'], (1350 - 15 * 18 * math.log2(18) - 105 * 2 * math.log2(2)) / 513)
    assert choice['catalogs_needed_to_save_one_whole_bit_at_mean_rate'] == 37

    assert by_cat['unique_state']['represented_count'] == 33
    assert by_cat['unique_state']['total_headroom_bits'] == 0.0
    assert by_cat['unique_state']['mean_headroom_bits'] == 0.0
    assert by_cat['unique_state']['catalogs_needed_to_save_one_whole_bit_at_mean_rate'] is None

    assert by_cat['interior_nonsingleton']['represented_count'] == 210
    assert by_cat['interior_nonsingleton']['total_headroom_bits'] == 0.0
    assert by_cat['interior_nonsingleton']['mean_headroom_bits'] == 0.0
    assert by_cat['interior_nonsingleton']['catalogs_needed_to_save_one_whole_bit_at_mean_rate'] is None

    assert by_cat['interior_singleton']['represented_count'] == 270
    assert math.isclose(by_cat['interior_singleton']['total_headroom_bits'], 15 * (76 - 18 * math.log2(18)))
    assert math.isclose(by_cat['interior_singleton']['mean_headroom_bits'], 76 / 18 - math.log2(18))
    assert by_cat['interior_singleton']['catalogs_needed_to_save_one_whole_bit_at_mean_rate'] == 20
    assert math.isclose(by_cat['interior_singleton']['total_headroom_bits'], choice['total_headroom_bits'])

    print('ok')


if __name__ == '__main__':
    main()
