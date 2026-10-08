#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from collections import Counter
from functools import lru_cache
from itertools import product
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_feasible_interval_state_dense_index_law import (
    build_all_realized_feasible_interval_states,
    encode_feasible_interval_state_as_dense_index,
)
from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_feasible_interval_state_prefix_law import (
    encode_feasible_interval_state_dense_index_as_prefix_bits,
)
from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_exact_shortest_script_transport_law import (
    summarize_shared_interval_state_exact_shortest_script_batch,
)
from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shortest_generator_word_choice_prefix_law import (
    encode_shortest_generator_word_as_choice_prefix_bits,
)
from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shortest_generator_word_family_law import (
    build_closed_form_shortest_generator_words_for_feasible_interval_state,
    classify_feasible_interval_state,
)
from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shortest_generator_word_prefix_law import (
    encode_shortest_generator_word_as_prefix_bits,
)
from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_generator_stream_feasible_interval_law import (
    FeasibleIntervalKernelState,
    serialize_feasible_interval_kernel_state,
)


class WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateExactShortestScriptThresholdLawError(RuntimeError):
    pass


@lru_cache(maxsize=None)
def _normalize_feasible_interval_state(
    state: tuple[int, int] | list[int],
) -> FeasibleIntervalKernelState:
    if len(state) != 2:
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateExactShortestScriptThresholdLawError(
            'feasible interval state must contain exactly two ranks'
        )
    lower_rank = int(state[0])
    upper_rank = int(state[1])
    if lower_rank < 0 or upper_rank < lower_rank or upper_rank > 16:
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateExactShortestScriptThresholdLawError(
            'feasible interval state must stay within the realized 17-rank path bounds'
        )
    return lower_rank, upper_rank


@lru_cache(maxsize=None)
def build_shared_interval_state_exact_shortest_script_threshold_profile(
    state: tuple[int, int] | list[int],
) -> dict[str, Any]:
    state = _normalize_feasible_interval_state(state)
    family = build_closed_form_shortest_generator_words_for_feasible_interval_state(state)
    state_prefix_bit_length = len(
        encode_feasible_interval_state_dense_index_as_prefix_bits(
            encode_feasible_interval_state_as_dense_index(state)
        )
    )
    local_choice_prefix_bit_lengths = [
        len(encode_shortest_generator_word_as_choice_prefix_bits(state, word))
        for word in family
    ]
    global_exact_word_prefix_bit_lengths = [
        len(encode_shortest_generator_word_as_prefix_bits(word))
        for word in family
    ]
    max_local_choice_prefix_bit_length = max(local_choice_prefix_bit_lengths)
    min_global_exact_word_prefix_bit_length = min(global_exact_word_prefix_bit_lengths)
    per_word_margin_bits = min_global_exact_word_prefix_bit_length - max_local_choice_prefix_bit_length
    if per_word_margin_bits <= 0:
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateExactShortestScriptThresholdLawError(
            f'state {state} has nonpositive shared-state margin {per_word_margin_bits}'
        )

    weak_switch_threshold = (state_prefix_bit_length + per_word_margin_bits - 1) // per_word_margin_bits
    strict_switch_threshold = state_prefix_bit_length // per_word_margin_bits + 1

    return {
        'interval_kernel_state': serialize_feasible_interval_kernel_state(state),
        'state_category': classify_feasible_interval_state(state),
        'family_cardinality': len(family),
        'state_prefix_bit_length': state_prefix_bit_length,
        'local_choice_prefix_bit_length_spectrum': dict(sorted(Counter(local_choice_prefix_bit_lengths).items())),
        'global_exact_word_prefix_bit_length_spectrum': dict(sorted(Counter(global_exact_word_prefix_bit_lengths).items())),
        'max_local_choice_prefix_bit_length': max_local_choice_prefix_bit_length,
        'min_global_exact_word_prefix_bit_length': min_global_exact_word_prefix_bit_length,
        'per_word_margin_bits': per_word_margin_bits,
        'weak_switch_threshold': weak_switch_threshold,
        'strict_switch_threshold': strict_switch_threshold,
    }


@lru_cache(maxsize=1)
def build_shared_interval_state_exact_shortest_script_threshold_validation_summary() -> dict[str, Any]:
    weak_threshold_counter: Counter[int] = Counter()
    strict_threshold_counter: Counter[int] = Counter()
    profile_counter: Counter[str] = Counter()
    safe_but_not_strict_counter: Counter[int] = Counter()
    representative_profile_rows: list[dict[str, Any]] = []
    seen_profile_keys: set[str] = set()

    total_audited_batch_cases = 0

    for state in build_all_realized_feasible_interval_states():
        profile = build_shared_interval_state_exact_shortest_script_threshold_profile(state)
        family = build_closed_form_shortest_generator_words_for_feasible_interval_state(state)
        weak_threshold = int(profile['weak_switch_threshold'])
        strict_threshold = int(profile['strict_switch_threshold'])
        weak_threshold_counter[weak_threshold] += 1
        strict_threshold_counter[strict_threshold] += 1
        profile_key = (
            f"{profile['state_category']}|state_prefix_bits={profile['state_prefix_bit_length']}"
            f"|max_local_choice_bits={profile['max_local_choice_prefix_bit_length']}"
            f"|per_word_margin_bits={profile['per_word_margin_bits']}"
            f"|weak_threshold={weak_threshold}|strict_threshold={strict_threshold}"
        )
        profile_counter[profile_key] += 1
        if profile_key not in seen_profile_keys:
            representative_profile_rows.append(profile)
            seen_profile_keys.add(profile_key)

        for batch_length in (1, 2, 3):
            statuses = Counter(
                summarize_shared_interval_state_exact_shortest_script_batch(state, generator_word_batch)['comparison_status']
                for generator_word_batch in product(family, repeat=batch_length)
            )
            total_audited_batch_cases += len(family) ** batch_length

            if batch_length < weak_threshold:
                if statuses.get('loss', 0) == 0:
                    raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateExactShortestScriptThresholdLawError(
                        f'state {state} should still lose below weak threshold {weak_threshold}, but batch length {batch_length} did not'
                    )
            elif batch_length < strict_threshold:
                safe_but_not_strict_counter[batch_length] += 1
                if statuses.get('loss', 0) != 0 or statuses.get('tie', 0) == 0:
                    raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateExactShortestScriptThresholdLawError(
                        f'state {state} should be safe-but-not-strict at batch length {batch_length}, found statuses {statuses}'
                    )
            else:
                if statuses != Counter({'strict_win': len(family) ** batch_length}):
                    raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateExactShortestScriptThresholdLawError(
                        f'state {state} should be strict by batch length {batch_length}, found statuses {statuses}'
                    )

    if weak_threshold_counter != Counter({1: 138, 2: 15}):
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateExactShortestScriptThresholdLawError(
            f'unexpected weak-threshold counter: {weak_threshold_counter}'
        )
    if strict_threshold_counter != Counter({1: 106, 2: 39, 3: 8}):
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateExactShortestScriptThresholdLawError(
            f'unexpected strict-threshold counter: {strict_threshold_counter}'
        )
    if safe_but_not_strict_counter != Counter({1: 32, 2: 8}):
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateExactShortestScriptThresholdLawError(
            f'unexpected safe-but-not-strict counts: {safe_but_not_strict_counter}'
        )
    if total_audited_batch_cases != 94179:
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateExactShortestScriptThresholdLawError(
            f'unexpected audited case count {total_audited_batch_cases}'
        )

    return {
        'total_audited_batch_cases': total_audited_batch_cases,
        'weak_threshold_counter': {str(key): value for key, value in sorted(weak_threshold_counter.items())},
        'strict_threshold_counter': {str(key): value for key, value in sorted(strict_threshold_counter.items())},
        'safe_but_not_strict_counter': {str(key): value for key, value in sorted(safe_but_not_strict_counter.items())},
        'profile_counter': dict(sorted(profile_counter.items())),
        'representative_profile_rows': representative_profile_rows,
        'all_states_have_nine_bit_global_floor': all(
            build_shared_interval_state_exact_shortest_script_threshold_profile(state)['min_global_exact_word_prefix_bit_length'] == 9
            for state in build_all_realized_feasible_interval_states()
        ),
        'all_state_thresholds_match_the_closed_form_margin_rule': True,
    }


@lru_cache(maxsize=None)
def recommend_shared_interval_state_exact_shortest_script_transport_by_threshold(
    state: tuple[int, int] | list[int],
    batch_length: int,
) -> dict[str, Any]:
    state = _normalize_feasible_interval_state(state)
    batch_length = int(batch_length)
    if batch_length <= 0:
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateExactShortestScriptThresholdLawError(
            'batch length must be positive'
        )
    profile = build_shared_interval_state_exact_shortest_script_threshold_profile(state)
    weak_threshold = int(profile['weak_switch_threshold'])
    strict_threshold = int(profile['strict_switch_threshold'])
    if batch_length < weak_threshold:
        guarantee = 'loss_possible'
        recommendation = 'keep_global_exact_word_prefix_frontier'
        rationale = 'The state prefix overhead has not yet been amortized enough to dominate the smallest per-word global exact prefix in the worst case.'
    elif batch_length < strict_threshold:
        guarantee = 'weak_win'
        recommendation = 'shared_interval_state_prefix_plus_local_choice_prefixes'
        rationale = 'The batch is already large enough to eliminate losses but not yet large enough to rule out every tie.'
    else:
        guarantee = 'strict_win'
        recommendation = 'shared_interval_state_prefix_plus_local_choice_prefixes'
        rationale = 'The batch is past the closed-form strict threshold, so worst-case local choices still beat the smallest admissible per-word global exact prefixes.'
    return {
        **profile,
        'batch_length': batch_length,
        'recommendation': recommendation,
        'guarantee': guarantee,
        'rationale': rationale,
    }


@lru_cache(maxsize=1)
def build_shared_interval_state_exact_shortest_script_threshold_examples() -> list[dict[str, Any]]:
    return [
        {
            'unique_or_seven_bit_margin_four_or_better_switches_immediately': recommend_shared_interval_state_exact_shortest_script_transport_by_threshold((0, 16), 1)
        },
        {
            'eight_bit_interior_nonsingleton_is_safe_at_one_word_and_strict_at_two': {
                'one_word': recommend_shared_interval_state_exact_shortest_script_transport_by_threshold((8, 15), 1),
                'two_words': recommend_shared_interval_state_exact_shortest_script_transport_by_threshold((8, 15), 2),
            }
        },
        {
            'seven_bit_interior_singleton_needs_two_words_for_both_safety_and_strictness': {
                'one_word': recommend_shared_interval_state_exact_shortest_script_transport_by_threshold((1, 1), 1),
                'two_words': recommend_shared_interval_state_exact_shortest_script_transport_by_threshold((1, 1), 2),
            }
        },
        {
            'eight_bit_interior_singleton_is_safe_at_two_words_but_only_strict_at_three': {
                'two_words': recommend_shared_interval_state_exact_shortest_script_transport_by_threshold((8, 8), 2),
                'three_words': recommend_shared_interval_state_exact_shortest_script_transport_by_threshold((8, 8), 3),
            }
        },
    ]


@lru_cache(maxsize=1)
def build_headline_findings() -> dict[str, Any]:
    summary = build_shared_interval_state_exact_shortest_script_threshold_validation_summary()
    return {
        'total_audited_batch_cases': summary['total_audited_batch_cases'],
        'weak_threshold_counter': summary['weak_threshold_counter'],
        'strict_threshold_counter': summary['strict_threshold_counter'],
        'safe_but_not_strict_counter': summary['safe_but_not_strict_counter'],
        'all_states_have_nine_bit_global_floor': summary['all_states_have_nine_bit_global_floor'],
    }


@lru_cache(maxsize=1)
def build_decision_rules() -> list[str]:
    return [
        'For any shared-state exact batch, compute the weak threshold as ceil(state_prefix_bits / (9 - max_local_choice_bits)) and the strict threshold as floor(state_prefix_bits / (9 - max_local_choice_bits)) + 1.',
        'Unique-word states always switch immediately because they spend 0 local choice bits per word against a 9-bit global floor.',
        'Interior nonsingletons spend at most 1 local choice bit per word, so 7-bit states are strict at one word while 8-bit states are safe at one word and strict at two.',
        'Interior singletons spend at most 5 local choice bits per word, so 7-bit states switch safely and strictly at two words, while 8-bit states are safe at two but need three for strict dominance.',
    ]


@lru_cache(maxsize=1)
def build_service_mode_suffix_batch_shared_half_step_shared_interval_state_exact_shortest_script_threshold_snapshot() -> dict[str, Any]:
    return {
        'focus': 'Once exact shortest scripts share one feasible interval state, safe and strict batch switch points are determined exactly by the local worst-case bit margin, not by ad hoc batch-length folklore.',
        'headline_findings': build_headline_findings(),
        'decision_rules': build_decision_rules(),
        'threshold_examples': build_shared_interval_state_exact_shortest_script_threshold_examples(),
        'validation_summary': build_shared_interval_state_exact_shortest_script_threshold_validation_summary(),
        'source_reports': [
            'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_exact_shortest_script_transport_law_snapshot_20260309.json',
            'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_feasible_interval_state_prefix_law_snapshot_20260309.json',
            'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shortest_generator_word_choice_prefix_law_snapshot_20260309.json',
            'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shortest_generator_word_prefix_law_snapshot_20260309.json',
        ],
        'analysis_script': 'scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_exact_shortest_script_threshold_law.py',
    }


if __name__ == '__main__':
    print(json.dumps(build_service_mode_suffix_batch_shared_half_step_shared_interval_state_exact_shortest_script_threshold_snapshot(), indent=2, sort_keys=True))
