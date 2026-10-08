#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from collections import Counter
from fractions import Fraction
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
from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_exact_shortest_script_threshold_law import (
    build_shared_interval_state_exact_shortest_script_threshold_profile,
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


class WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptThresholdLawError(RuntimeError):
    pass


@lru_cache(maxsize=None)
def _normalize_feasible_interval_state(
    state: tuple[int, int] | list[int],
) -> FeasibleIntervalKernelState:
    if len(state) != 2:
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptThresholdLawError(
            'feasible interval state must contain exactly two ranks'
        )
    lower_rank = int(state[0])
    upper_rank = int(state[1])
    if lower_rank < 0 or upper_rank < lower_rank or upper_rank > 16:
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptThresholdLawError(
            'feasible interval state must stay within the realized 17-rank path bounds'
        )
    return lower_rank, upper_rank


@lru_cache(maxsize=None)
def build_shared_interval_state_equiprobable_exact_shortest_script_threshold_profile(
    state: tuple[int, int] | list[int],
) -> dict[str, Any]:
    state = _normalize_feasible_interval_state(state)
    family = build_closed_form_shortest_generator_words_for_feasible_interval_state(state)
    family_cardinality = len(family)
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
    total_local_choice_prefix_bits = sum(local_choice_prefix_bit_lengths)
    total_global_exact_word_prefix_bits = sum(global_exact_word_prefix_bit_lengths)
    per_word_margin_numerator = total_global_exact_word_prefix_bits - total_local_choice_prefix_bits
    per_word_margin_denominator = family_cardinality
    if per_word_margin_numerator <= 0:
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptThresholdLawError(
            f'state {state} has nonpositive equiprobable expected margin'
        )

    weak_expected_switch_threshold = (
        state_prefix_bit_length * family_cardinality + per_word_margin_numerator - 1
    ) // per_word_margin_numerator
    strict_expected_switch_threshold = (
        state_prefix_bit_length * family_cardinality
    ) // per_word_margin_numerator + 1

    return {
        'interval_kernel_state': serialize_feasible_interval_kernel_state(state),
        'state_category': classify_feasible_interval_state(state),
        'family_cardinality': family_cardinality,
        'state_prefix_bit_length': state_prefix_bit_length,
        'local_choice_prefix_bit_length_spectrum': dict(sorted(Counter(local_choice_prefix_bit_lengths).items())),
        'global_exact_word_prefix_bit_length_spectrum': dict(sorted(Counter(global_exact_word_prefix_bit_lengths).items())),
        'global_exact_word_prefix_width_is_uniform_within_state': len(set(global_exact_word_prefix_bit_lengths)) == 1,
        'minimum_global_exact_word_prefix_bit_length': min(global_exact_word_prefix_bit_lengths),
        'maximum_global_exact_word_prefix_bit_length': max(global_exact_word_prefix_bit_lengths),
        'total_local_choice_prefix_bits': total_local_choice_prefix_bits,
        'total_global_exact_word_prefix_bits': total_global_exact_word_prefix_bits,
        'equiprobable_mean_local_choice_prefix_bits': {
            'numerator': total_local_choice_prefix_bits,
            'denominator': family_cardinality,
            'decimal': float(Fraction(total_local_choice_prefix_bits, family_cardinality)),
        },
        'equiprobable_mean_global_exact_word_prefix_bits': {
            'numerator': total_global_exact_word_prefix_bits,
            'denominator': family_cardinality,
            'decimal': float(Fraction(total_global_exact_word_prefix_bits, family_cardinality)),
        },
        'equiprobable_per_word_margin_bits': {
            'numerator': per_word_margin_numerator,
            'denominator': per_word_margin_denominator,
            'decimal': float(Fraction(per_word_margin_numerator, per_word_margin_denominator)),
        },
        'weak_expected_switch_threshold': weak_expected_switch_threshold,
        'strict_expected_switch_threshold': strict_expected_switch_threshold,
    }


@lru_cache(maxsize=None)
def summarize_shared_interval_state_exact_shortest_script_batch_by_equiprobable_mean(
    state: tuple[int, int] | list[int],
    batch_length: int,
) -> dict[str, Any]:
    state = _normalize_feasible_interval_state(state)
    batch_length = int(batch_length)
    if batch_length <= 0:
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptThresholdLawError(
            'batch length must be positive'
        )

    profile = build_shared_interval_state_equiprobable_exact_shortest_script_threshold_profile(state)
    family = build_closed_form_shortest_generator_words_for_feasible_interval_state(state)
    family_cardinality = len(family)
    state_prefix_bit_length = int(profile['state_prefix_bit_length'])
    total_local_choice_prefix_bits = int(profile['total_local_choice_prefix_bits'])
    total_global_exact_word_prefix_bits = int(profile['total_global_exact_word_prefix_bits'])

    shared_transport_total_bits = Fraction(
        state_prefix_bit_length * family_cardinality + batch_length * total_local_choice_prefix_bits,
        family_cardinality,
    )
    global_transport_total_bits = Fraction(
        batch_length * total_global_exact_word_prefix_bits,
        family_cardinality,
    )
    winning_margin_bits = global_transport_total_bits - shared_transport_total_bits
    if winning_margin_bits > 0:
        status = 'strict_expected_win'
        recommendation = 'shared_interval_state_prefix_plus_local_choice_prefixes'
        rationale = 'The equiprobable mean shared-state transport is already strictly below the equiprobable mean standalone exact-word transport.'
    elif winning_margin_bits == 0:
        status = 'expected_tie'
        recommendation = 'either_frontier_or_shared_interval_state_prefix_plus_local_choice_prefixes'
        rationale = 'The equiprobable mean shared-state and standalone exact-word transports tie exactly, so the choice should defer to non-mean criteria.'
    else:
        status = 'expected_loss'
        recommendation = 'keep_global_exact_word_prefix_frontier'
        rationale = 'The equiprobable mean state-prefix overhead has not yet been amortized enough to beat standalone exact-word transport.'

    return {
        **profile,
        'batch_length': batch_length,
        'equiprobable_mean_shared_state_transport_bits': {
            'numerator': shared_transport_total_bits.numerator,
            'denominator': shared_transport_total_bits.denominator,
            'decimal': float(shared_transport_total_bits),
        },
        'equiprobable_mean_global_exact_word_transport_bits': {
            'numerator': global_transport_total_bits.numerator,
            'denominator': global_transport_total_bits.denominator,
            'decimal': float(global_transport_total_bits),
        },
        'equiprobable_mean_winning_margin_bits': {
            'numerator': winning_margin_bits.numerator,
            'denominator': winning_margin_bits.denominator,
            'decimal': float(winning_margin_bits),
        },
        'recommendation': recommendation,
        'guarantee': status,
        'rationale': rationale,
    }


@lru_cache(maxsize=1)
def build_shared_interval_state_equiprobable_exact_shortest_script_threshold_validation_summary() -> dict[str, Any]:
    weak_threshold_counter: Counter[int] = Counter()
    strict_threshold_counter: Counter[int] = Counter()
    expected_comparison_counter_by_batch_length: dict[int, Counter[str]] = {1: Counter(), 2: Counter(), 3: Counter()}
    profile_counter: Counter[str] = Counter()
    improved_vs_worst_case_strict_counter: Counter[str] = Counter()
    total_audited_batch_cases = 0

    for state in build_all_realized_feasible_interval_states():
        profile = build_shared_interval_state_equiprobable_exact_shortest_script_threshold_profile(state)
        worst_case_profile = build_shared_interval_state_exact_shortest_script_threshold_profile(state)
        weak_threshold = int(profile['weak_expected_switch_threshold'])
        strict_threshold = int(profile['strict_expected_switch_threshold'])
        weak_threshold_counter[weak_threshold] += 1
        strict_threshold_counter[strict_threshold] += 1
        if strict_threshold < int(worst_case_profile['strict_switch_threshold']):
            improved_vs_worst_case_strict_counter[profile['state_category']] += 1
        profile_key = (
            f"{profile['state_category']}|state_prefix_bits={profile['state_prefix_bit_length']}"
            f"|local_choice_total_bits={profile['total_local_choice_prefix_bits']}"
            f"|family_cardinality={profile['family_cardinality']}"
            f"|weak_expected_threshold={weak_threshold}|strict_expected_threshold={strict_threshold}"
        )
        profile_counter[profile_key] += 1

        family = build_closed_form_shortest_generator_words_for_feasible_interval_state(state)
        family_case_count = 0
        for batch_length in (1, 2, 3):
            shared_total = 0
            global_total = 0
            cases = 0
            for generator_word_batch in product(family, repeat=batch_length):
                summary = summarize_shared_interval_state_exact_shortest_script_batch(state, generator_word_batch)
                shared_total += int(summary['shared_state_transport_bit_length'])
                global_total += int(summary['global_exact_word_transport_bit_length'])
                cases += 1
            family_case_count += cases
            comparison = expected_comparison_counter_by_batch_length[batch_length]
            if shared_total < global_total:
                comparison['strict_expected_win'] += 1
            elif shared_total == global_total:
                comparison['expected_tie'] += 1
            else:
                comparison['expected_loss'] += 1

            mean_summary = summarize_shared_interval_state_exact_shortest_script_batch_by_equiprobable_mean(state, batch_length)
            if shared_total * mean_summary['equiprobable_mean_shared_state_transport_bits']['denominator'] != mean_summary['equiprobable_mean_shared_state_transport_bits']['numerator'] * cases:
                raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptThresholdLawError(
                    f'equiprobable shared mean mismatch for state {state} at batch length {batch_length}'
                )
            if global_total * mean_summary['equiprobable_mean_global_exact_word_transport_bits']['denominator'] != mean_summary['equiprobable_mean_global_exact_word_transport_bits']['numerator'] * cases:
                raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptThresholdLawError(
                    f'equiprobable global mean mismatch for state {state} at batch length {batch_length}'
                )

            expected_status = mean_summary['guarantee']
            if batch_length < weak_threshold:
                if expected_status != 'expected_loss':
                    raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptThresholdLawError(
                        f'state {state} should still lose in expectation below weak threshold {weak_threshold} at batch length {batch_length}'
                    )
            elif batch_length < strict_threshold:
                if expected_status != 'expected_tie':
                    raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptThresholdLawError(
                        f'state {state} should tie in expectation between weak {weak_threshold} and strict {strict_threshold}, found {expected_status}'
                    )
            else:
                if expected_status != 'strict_expected_win':
                    raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptThresholdLawError(
                        f'state {state} should strictly win in expectation at batch length {batch_length}, found {expected_status}'
                    )
        total_audited_batch_cases += family_case_count

    if weak_threshold_counter != Counter({1: 138, 2: 15}):
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptThresholdLawError(
            f'unexpected weak expected-threshold counter: {weak_threshold_counter}'
        )
    if strict_threshold_counter != Counter({1: 106, 2: 47}):
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptThresholdLawError(
            f'unexpected strict expected-threshold counter: {strict_threshold_counter}'
        )
    if expected_comparison_counter_by_batch_length[1] != Counter({'strict_expected_win': 106, 'expected_tie': 32, 'expected_loss': 15}):
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptThresholdLawError(
            f'unexpected state-uniform expected comparison counts at batch length 1: {expected_comparison_counter_by_batch_length[1]}'
        )
    if expected_comparison_counter_by_batch_length[2] != Counter({'strict_expected_win': 153}):
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptThresholdLawError(
            f'unexpected state-uniform expected comparison counts at batch length 2: {expected_comparison_counter_by_batch_length[2]}'
        )
    if expected_comparison_counter_by_batch_length[3] != Counter({'strict_expected_win': 153}):
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptThresholdLawError(
            f'unexpected state-uniform expected comparison counts at batch length 3: {expected_comparison_counter_by_batch_length[3]}'
        )
    if improved_vs_worst_case_strict_counter != Counter({'interior_singleton': 8}):
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptThresholdLawError(
            f'unexpected strict-threshold improvement profile: {improved_vs_worst_case_strict_counter}'
        )
    if total_audited_batch_cases != 94179:
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptThresholdLawError(
            f'unexpected audited case count {total_audited_batch_cases}'
        )

    return {
        'total_audited_batch_cases': total_audited_batch_cases,
        'weak_expected_threshold_counter': {str(key): value for key, value in sorted(weak_threshold_counter.items())},
        'strict_expected_threshold_counter': {str(key): value for key, value in sorted(strict_threshold_counter.items())},
        'state_uniform_expected_comparison_counter_by_batch_length': {
            str(batch_length): dict(sorted(counter.items()))
            for batch_length, counter in sorted(expected_comparison_counter_by_batch_length.items())
        },
        'profile_counter': dict(sorted(profile_counter.items())),
        'strict_threshold_improvement_vs_worst_case_counter': dict(sorted(improved_vs_worst_case_strict_counter.items())),
        'all_states_match_the_closed_form_expected_margin_rule': True,
        'all_states_are_expected_strict_winners_by_batch_length_2': expected_comparison_counter_by_batch_length[2] == Counter({'strict_expected_win': 153}),
        'only_eight_bit_interior_singletons_improve_against_the_worst_case_strict_threshold': improved_vs_worst_case_strict_counter == Counter({'interior_singleton': 8}),
        'states_with_nonuniform_global_exact_word_prefix_width': {
            '15-15': {'9': 16, '10': 2}
        },
    }


@lru_cache(maxsize=1)
def build_shared_interval_state_equiprobable_exact_shortest_script_threshold_examples() -> list[dict[str, Any]]:
    return [
        {
            'eight_bit_interior_nonsingleton_ties_in_expectation_at_one_word': summarize_shared_interval_state_exact_shortest_script_batch_by_equiprobable_mean((8, 15), 1)
        },
        {
            'eight_bit_interior_singleton_becomes_a_strict_expected_winner_by_two_words': {
                'one_word': summarize_shared_interval_state_exact_shortest_script_batch_by_equiprobable_mean((8, 8), 1),
                'two_words': summarize_shared_interval_state_exact_shortest_script_batch_by_equiprobable_mean((8, 8), 2),
            }
        },
    ]


@lru_cache(maxsize=1)
def build_headline_findings() -> dict[str, Any]:
    summary = build_shared_interval_state_equiprobable_exact_shortest_script_threshold_validation_summary()
    return {
        'total_audited_batch_cases': summary['total_audited_batch_cases'],
        'weak_expected_threshold_counter': summary['weak_expected_threshold_counter'],
        'strict_expected_threshold_counter': summary['strict_expected_threshold_counter'],
        'state_uniform_expected_comparison_counter_by_batch_length': summary['state_uniform_expected_comparison_counter_by_batch_length'],
        'all_states_are_expected_strict_winners_by_batch_length_2': summary['all_states_are_expected_strict_winners_by_batch_length_2'],
        'only_eight_bit_interior_singletons_improve_against_the_worst_case_strict_threshold': summary['only_eight_bit_interior_singletons_improve_against_the_worst_case_strict_threshold'],
    }


@lru_cache(maxsize=1)
def build_decision_rules() -> list[str]:
    return [
        'Under the equiprobable exact-branch model for a fixed shared interval state, compute the weak expected switch threshold as ceil(state_prefix_bits * family_cardinality / (total_global_exact_word_prefix_bits - total_local_choice_bits)).',
        'Compute the strict expected switch threshold as floor(state_prefix_bits * family_cardinality / (total_global_exact_word_prefix_bits - total_local_choice_bits)) + 1.',
        'All realized states are already strict expected winners by batch length 2, so any two-word shared-state exact batch can switch immediately if equiprobable mean cost is the governing criterion.',
        'The only gap between mean and worst-case strict thresholds is the eight 8-bit interior singleton states, which move from strict threshold 3 in the worst case down to 2 in expectation; one of them, state [15,15], is also the lone family whose global exact-word widths split across 9 and 10 bits.',
    ]


@lru_cache(maxsize=1)
def build_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_threshold_snapshot() -> dict[str, Any]:
    return {
        'focus': 'Once exact shortest scripts share one feasible interval state, the equiprobable expected batch switch point is determined exactly by the mean local bit margin, and every realized state becomes a strict expected winner by batch length 2.',
        'headline_findings': build_headline_findings(),
        'decision_rules': build_decision_rules(),
        'threshold_examples': build_shared_interval_state_equiprobable_exact_shortest_script_threshold_examples(),
        'validation_summary': build_shared_interval_state_equiprobable_exact_shortest_script_threshold_validation_summary(),
        'source_reports': [
            'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_exact_shortest_script_transport_law_snapshot_20260309.json',
            'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_exact_shortest_script_threshold_law_snapshot_20260309.json',
            'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_feasible_interval_state_prefix_law_snapshot_20260309.json',
            'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shortest_generator_word_choice_prefix_law_snapshot_20260309.json',
            'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shortest_generator_word_prefix_law_snapshot_20260309.json',
        ],
        'analysis_script': 'scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_threshold_law.py',
    }


if __name__ == '__main__':
    print(json.dumps(build_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_threshold_snapshot(), indent=2, sort_keys=True))
