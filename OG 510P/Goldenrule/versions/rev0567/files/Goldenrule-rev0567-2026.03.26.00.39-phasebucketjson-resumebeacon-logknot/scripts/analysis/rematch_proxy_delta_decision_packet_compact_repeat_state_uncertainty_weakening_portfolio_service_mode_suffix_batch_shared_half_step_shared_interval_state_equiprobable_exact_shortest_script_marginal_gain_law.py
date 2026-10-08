#!/usr/bin/env python3
from __future__ import annotations

import json
import math
import sys
from collections import Counter
from fractions import Fraction
from functools import lru_cache
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_feasible_interval_state_dense_index_law import (
    build_all_realized_feasible_interval_states,
)
from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_generator_stream_feasible_interval_law import (
    FeasibleIntervalKernelState,
    serialize_feasible_interval_kernel_state,
)
from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_mean_cost_law import (
    build_shared_interval_state_equiprobable_exact_shortest_script_mean_cost_profile,
    evaluate_shared_interval_state_equiprobable_exact_shortest_script_mean_cost,
)


class WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptMarginalGainLawError(RuntimeError):
    pass


@lru_cache(maxsize=None)
def _normalize_state(state: tuple[int, int] | list[int]) -> FeasibleIntervalKernelState:
    if len(state) != 2:
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptMarginalGainLawError(
            'feasible interval state must contain exactly two ranks'
        )
    lower_rank = int(state[0])
    upper_rank = int(state[1])
    if lower_rank < 0 or upper_rank < lower_rank or upper_rank > 16:
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptMarginalGainLawError(
            'feasible interval state must stay within the realized 17-rank path bounds'
        )
    return lower_rank, upper_rank


MARGINAL_GAIN_FAMILY_FORMULAS: dict[str, dict[str, Any]] = {
    'seven_bit_state_prefix_marginal_gain': {
        'state_prefix_bits': 7,
        'formula': '7/(n(n+1))',
        'state_class_description': 'all 7-bit interval-state prefix families',
    },
    'eight_bit_state_prefix_marginal_gain': {
        'state_prefix_bits': 8,
        'formula': '8/(n(n+1))',
        'state_class_description': 'all 8-bit interval-state prefix families',
    },
}


@lru_cache(maxsize=None)
def classify_shared_interval_state_equiprobable_exact_shortest_script_marginal_gain_family(
    state: tuple[int, int] | list[int],
) -> str:
    state = _normalize_state(state)
    profile = build_shared_interval_state_equiprobable_exact_shortest_script_mean_cost_profile(state)
    state_prefix_bits = int(profile['state_prefix_bit_length'])
    if state_prefix_bits == 7:
        return 'seven_bit_state_prefix_marginal_gain'
    if state_prefix_bits == 8:
        return 'eight_bit_state_prefix_marginal_gain'
    raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptMarginalGainLawError(
        f'unrecognized state-prefix width for state {state}: {state_prefix_bits}'
    )


@lru_cache(maxsize=None)
def build_shared_interval_state_equiprobable_exact_shortest_script_marginal_gain_profile(
    state: tuple[int, int] | list[int],
) -> dict[str, Any]:
    state = _normalize_state(state)
    mean_cost_profile = build_shared_interval_state_equiprobable_exact_shortest_script_mean_cost_profile(state)
    family_name = classify_shared_interval_state_equiprobable_exact_shortest_script_marginal_gain_family(state)
    formula = MARGINAL_GAIN_FAMILY_FORMULAS[family_name]
    return {
        **mean_cost_profile,
        'marginal_gain_family': family_name,
        'marginal_gain_formula': formula['formula'],
        'marginal_gain_state_class_description': formula['state_class_description'],
        'marginal_gain_state_prefix_bits': int(formula['state_prefix_bits']),
    }


@lru_cache(maxsize=None)
def evaluate_shared_interval_state_equiprobable_exact_shortest_script_marginal_mean_cost_gain(
    state: tuple[int, int] | list[int],
    current_batch_length: int,
) -> dict[str, Any]:
    state = _normalize_state(state)
    current_batch_length = int(current_batch_length)
    if current_batch_length <= 0:
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptMarginalGainLawError(
            'current batch length must be positive'
        )
    profile = build_shared_interval_state_equiprobable_exact_shortest_script_marginal_gain_profile(state)
    prefix_bits = int(profile['marginal_gain_state_prefix_bits'])
    gain = Fraction(prefix_bits, current_batch_length * (current_batch_length + 1))
    return {
        **profile,
        'current_batch_length': current_batch_length,
        'next_batch_length': current_batch_length + 1,
        'equiprobable_marginal_mean_cost_gain_bits_per_script': {
            'numerator': gain.numerator,
            'denominator': gain.denominator,
            'decimal': float(gain),
        },
    }


def _serialize_fraction(value: Fraction) -> dict[str, int | float]:
    return {
        'numerator': value.numerator,
        'denominator': value.denominator,
        'decimal': float(value),
    }


@lru_cache(maxsize=None)
def compute_max_current_batch_length_for_state_target_marginal_gain(
    state: tuple[int, int] | list[int],
    target_bits_numerator: int,
    target_bits_denominator: int = 1,
) -> dict[str, Any]:
    state = _normalize_state(state)
    target = Fraction(int(target_bits_numerator), int(target_bits_denominator))
    if target <= 0:
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptMarginalGainLawError(
            'target marginal gain must be positive'
        )
    profile = build_shared_interval_state_equiprobable_exact_shortest_script_marginal_gain_profile(state)
    prefix_bits = int(profile['marginal_gain_state_prefix_bits'])
    if target > Fraction(prefix_bits, 2):
        return {
            **profile,
            'target_marginal_gain_bits_per_script': _serialize_fraction(target),
            'maximum_current_batch_length': None,
            'qualifying_batch_exists': False,
            'reason': 'target_above_single_step_gain_at_batch_length_one',
            'achieved_marginal_gain_bits_per_script': None,
            'next_nonqualifying_marginal_gain_bits_per_script': None,
        }
    quota = (prefix_bits * target.denominator) // target.numerator
    maximum_current_batch_length = (math.isqrt(1 + 4 * quota) - 1) // 2
    achieved = Fraction(prefix_bits, maximum_current_batch_length * (maximum_current_batch_length + 1))
    next_gain = Fraction(prefix_bits, (maximum_current_batch_length + 1) * (maximum_current_batch_length + 2))
    return {
        **profile,
        'target_marginal_gain_bits_per_script': _serialize_fraction(target),
        'maximum_current_batch_length': maximum_current_batch_length,
        'qualifying_batch_exists': True,
        'reason': 'closed_form_marginal_gain_inversion',
        'achieved_marginal_gain_bits_per_script': _serialize_fraction(achieved),
        'next_nonqualifying_marginal_gain_bits_per_script': _serialize_fraction(next_gain),
    }


@lru_cache(maxsize=None)
def compute_universal_max_current_batch_length_for_target_marginal_gain(
    target_bits_numerator: int,
    target_bits_denominator: int = 1,
) -> dict[str, Any]:
    target = Fraction(int(target_bits_numerator), int(target_bits_denominator))
    if target <= 0:
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptMarginalGainLawError(
            'target marginal gain must be positive'
        )
    prefix_bits = 7
    if target > Fraction(prefix_bits, 2):
        return {
            'target_marginal_gain_bits_per_script': _serialize_fraction(target),
            'maximum_current_batch_length': None,
            'qualifying_batch_exists': False,
            'guarantee_scope': 'all_realized_states',
            'guarantee_formula': '7/(n(n+1))',
            'reason': 'target_above_universal_single_step_gain_at_batch_length_one',
            'achieved_marginal_gain_bits_per_script': None,
            'next_nonqualifying_marginal_gain_bits_per_script': None,
        }
    quota = (prefix_bits * target.denominator) // target.numerator
    maximum_current_batch_length = (math.isqrt(1 + 4 * quota) - 1) // 2
    achieved = Fraction(prefix_bits, maximum_current_batch_length * (maximum_current_batch_length + 1))
    next_gain = Fraction(prefix_bits, (maximum_current_batch_length + 1) * (maximum_current_batch_length + 2))
    return {
        'target_marginal_gain_bits_per_script': _serialize_fraction(target),
        'maximum_current_batch_length': maximum_current_batch_length,
        'qualifying_batch_exists': True,
        'guarantee_scope': 'all_realized_states',
        'guarantee_formula': '7/(n(n+1))',
        'reason': 'closed_form_marginal_gain_inversion',
        'achieved_marginal_gain_bits_per_script': _serialize_fraction(achieved),
        'next_nonqualifying_marginal_gain_bits_per_script': _serialize_fraction(next_gain),
    }


@lru_cache(maxsize=1)
def build_marginal_gain_family_summary() -> dict[str, Any]:
    states = build_all_realized_feasible_interval_states()
    family_counts: Counter[str] = Counter()
    representatives: dict[str, list[int]] = {}
    for raw_state in states:
        state = tuple(raw_state)
        family = classify_shared_interval_state_equiprobable_exact_shortest_script_marginal_gain_family(state)
        family_counts[family] += 1
        representatives.setdefault(family, list(state))

    ordered = []
    for family_name in ['seven_bit_state_prefix_marginal_gain', 'eight_bit_state_prefix_marginal_gain']:
        formula = MARGINAL_GAIN_FAMILY_FORMULAS[family_name]
        ordered.append({
            'family_name': family_name,
            'state_count': family_counts[family_name],
            'representative_state': serialize_feasible_interval_kernel_state(tuple(representatives[family_name])),
            'marginal_gain_formula': formula['formula'],
            'state_prefix_bits': formula['state_prefix_bits'],
            'state_class_description': formula['state_class_description'],
        })

    return {
        'family_count': len(family_counts),
        'families': ordered,
        'catalog_state_count': sum(family_counts.values()),
    }


@lru_cache(maxsize=1)
def build_marginal_gain_validation_summary() -> dict[str, Any]:
    states = [tuple(state) for state in build_all_realized_feasible_interval_states()]
    audited_batch_lengths = tuple(range(1, 9))
    matched_gain_cases = 0
    for state in states:
        for current_batch_length in audited_batch_lengths:
            current_cost = Fraction(
                int(evaluate_shared_interval_state_equiprobable_exact_shortest_script_mean_cost(state, current_batch_length)['equiprobable_mean_shared_state_transport_bits_per_script']['numerator']),
                int(evaluate_shared_interval_state_equiprobable_exact_shortest_script_mean_cost(state, current_batch_length)['equiprobable_mean_shared_state_transport_bits_per_script']['denominator']),
            )
            next_cost = Fraction(
                int(evaluate_shared_interval_state_equiprobable_exact_shortest_script_mean_cost(state, current_batch_length + 1)['equiprobable_mean_shared_state_transport_bits_per_script']['numerator']),
                int(evaluate_shared_interval_state_equiprobable_exact_shortest_script_mean_cost(state, current_batch_length + 1)['equiprobable_mean_shared_state_transport_bits_per_script']['denominator']),
            )
            direct_gain = current_cost - next_cost
            law_gain = Fraction(
                int(evaluate_shared_interval_state_equiprobable_exact_shortest_script_marginal_mean_cost_gain(state, current_batch_length)['equiprobable_marginal_mean_cost_gain_bits_per_script']['numerator']),
                int(evaluate_shared_interval_state_equiprobable_exact_shortest_script_marginal_mean_cost_gain(state, current_batch_length)['equiprobable_marginal_mean_cost_gain_bits_per_script']['denominator']),
            )
            if direct_gain != law_gain:
                raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptMarginalGainLawError(
                    f'marginal gain mismatch for state {state} at batch length {current_batch_length}: {direct_gain} != {law_gain}'
                )
            matched_gain_cases += 1

    audited_targets = [Fraction(1, 10), Fraction(1, 4), Fraction(1, 2), Fraction(1, 1), Fraction(2, 1)]
    state_target_matches = 0
    for state in states:
        for target in audited_targets:
            summary = compute_max_current_batch_length_for_state_target_marginal_gain(state, target.numerator, target.denominator)
            n = summary['maximum_current_batch_length']
            if n is None:
                raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptMarginalGainLawError(
                    f'audited target {target} unexpectedly impossible for state {state}'
                )
            achieved = Fraction(
                int(summary['achieved_marginal_gain_bits_per_script']['numerator']),
                int(summary['achieved_marginal_gain_bits_per_script']['denominator']),
            )
            if achieved < target:
                raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptMarginalGainLawError(
                    f'target {target} missed for state {state} at batch length {n}'
                )
            next_gain = Fraction(
                int(summary['next_nonqualifying_marginal_gain_bits_per_script']['numerator']),
                int(summary['next_nonqualifying_marginal_gain_bits_per_script']['denominator']),
            )
            if next_gain >= target:
                raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptMarginalGainLawError(
                    f'marginal threshold not maximal for state {state} and target {target}'
                )
            state_target_matches += 1

    impossible_state_target = compute_max_current_batch_length_for_state_target_marginal_gain((15, 15), 5)
    if impossible_state_target['maximum_current_batch_length'] is not None or impossible_state_target['qualifying_batch_exists']:
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptMarginalGainLawError(
            'target 5 should be impossible even for the strongest single-step state gain'
        )

    universal_targets = [Fraction(1, 10), Fraction(1, 4), Fraction(1, 2), Fraction(1, 1), Fraction(2, 1)]
    universal_matches = 0
    for target in universal_targets:
        summary = compute_universal_max_current_batch_length_for_target_marginal_gain(target.numerator, target.denominator)
        n = summary['maximum_current_batch_length']
        if n is None:
            raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptMarginalGainLawError(
                f'audited universal target {target} unexpectedly impossible'
            )
        worst_gain = min(
            Fraction(
                int(evaluate_shared_interval_state_equiprobable_exact_shortest_script_marginal_mean_cost_gain(state, n)['equiprobable_marginal_mean_cost_gain_bits_per_script']['numerator']),
                int(evaluate_shared_interval_state_equiprobable_exact_shortest_script_marginal_mean_cost_gain(state, n)['equiprobable_marginal_mean_cost_gain_bits_per_script']['denominator']),
            )
            for state in states
        )
        if worst_gain < target:
            raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptMarginalGainLawError(
                f'universal target {target} missed at current batch length {n}'
            )
        next_worst = min(
            Fraction(
                int(evaluate_shared_interval_state_equiprobable_exact_shortest_script_marginal_mean_cost_gain(state, n + 1)['equiprobable_marginal_mean_cost_gain_bits_per_script']['numerator']),
                int(evaluate_shared_interval_state_equiprobable_exact_shortest_script_marginal_mean_cost_gain(state, n + 1)['equiprobable_marginal_mean_cost_gain_bits_per_script']['denominator']),
            )
            for state in states
        )
        if next_worst >= target:
            raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptMarginalGainLawError(
                f'universal threshold not maximal for target {target}'
            )
        universal_matches += 1

    impossible_universal_target = compute_universal_max_current_batch_length_for_target_marginal_gain(4)
    if impossible_universal_target['maximum_current_batch_length'] is not None or impossible_universal_target['qualifying_batch_exists']:
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptMarginalGainLawError(
            'target 4 should be impossible for the universal worst-case marginal gain'
        )

    minimum_by_batch_length = []
    maximum_by_batch_length = []
    for current_batch_length in audited_batch_lengths:
        gains = [
            Fraction(
                int(evaluate_shared_interval_state_equiprobable_exact_shortest_script_marginal_mean_cost_gain(state, current_batch_length)['equiprobable_marginal_mean_cost_gain_bits_per_script']['numerator']),
                int(evaluate_shared_interval_state_equiprobable_exact_shortest_script_marginal_mean_cost_gain(state, current_batch_length)['equiprobable_marginal_mean_cost_gain_bits_per_script']['denominator']),
            )
            for state in states
        ]
        minimum_by_batch_length.append({
            'current_batch_length': current_batch_length,
            'minimum_marginal_gain_bits_per_script': _serialize_fraction(min(gains)),
            'guarantee_formula': '7/(n(n+1))',
        })
        maximum_by_batch_length.append({
            'current_batch_length': current_batch_length,
            'maximum_marginal_gain_bits_per_script': _serialize_fraction(max(gains)),
            'maximizer_formula': '8/(n(n+1))',
        })

    return {
        'audited_state_count': len(states),
        'validated_state_batch_gain_pairs': matched_gain_cases,
        'audited_target_count': len(audited_targets),
        'validated_state_target_pairs': state_target_matches,
        'validated_universal_targets': universal_matches,
        'validated_impossible_targets': 2,
        'universal_lower_envelope_formula': '7/(n(n+1))',
        'universal_upper_envelope_formula': '8/(n(n+1))',
        'minimum_marginal_gain_by_batch_length': minimum_by_batch_length,
        'maximum_marginal_gain_by_batch_length': maximum_by_batch_length,
    }


@lru_cache(maxsize=1)
def build_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_marginal_gain_snapshot() -> dict[str, Any]:
    family_summary = build_marginal_gain_family_summary()
    validation_summary = build_marginal_gain_validation_summary()
    universal_schedule = [
        compute_universal_max_current_batch_length_for_target_marginal_gain(2),
        compute_universal_max_current_batch_length_for_target_marginal_gain(1),
        compute_universal_max_current_batch_length_for_target_marginal_gain(1, 2),
        compute_universal_max_current_batch_length_for_target_marginal_gain(1, 4),
        compute_universal_max_current_batch_length_for_target_marginal_gain(1, 10),
    ]
    state_examples = [
        compute_max_current_batch_length_for_state_target_marginal_gain((0, 16), 1, 2),
        compute_max_current_batch_length_for_state_target_marginal_gain((7, 12), 1, 4),
        compute_max_current_batch_length_for_state_target_marginal_gain((8, 8), 1, 10),
        compute_max_current_batch_length_for_state_target_marginal_gain((15, 15), 2),
    ]
    return {
        'focus': 'shared-state equiprobable exact-shortest-script batch-closing by one-more-script marginal mean-cost gain',
        'headline_findings': {
            'catalog_state_count': family_summary['catalog_state_count'],
            'marginal_gain_family_count': family_summary['family_count'],
            'seven_bit_states': family_summary['families'][0]['state_count'],
            'eight_bit_states': family_summary['families'][1]['state_count'],
            'universal_lower_envelope_formula': validation_summary['universal_lower_envelope_formula'],
            'universal_upper_envelope_formula': validation_summary['universal_upper_envelope_formula'],
            'validated_state_batch_gain_pairs': validation_summary['validated_state_batch_gain_pairs'],
        },
        'decision_rules': [
            'When the active source model is equiprobable exact branches inside one shared feasible interval state, the per-script value of waiting for one more same-state exact script is exactly state_prefix_bits / (n(n+1)).',
            'Use 7/(n(n+1)) as the all-state guaranteed marginal-gain floor on the current path, because every realized state prefix is either 7 or 8 bits.',
            'Use 8/(n(n+1)) as the best-case marginal-gain ceiling on the current path when planning eight-bit state families.',
            'For any positive target marginal gain t, keep a current shared-state batch open only while current_batch_length <= floor((sqrt(1 + 4 * floor(state_prefix_bits / t)) - 1) / 2).',
            'For all-state guarantees, replace state_prefix_bits with 7 and close the batch once the universal marginal gain falls below the desired threshold.',
        ],
        'marginal_gain_family_summary': family_summary,
        'validation_summary': validation_summary,
        'universal_target_schedule': universal_schedule,
        'state_examples': state_examples,
        'source_reports': [
            'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_mean_cost_law_snapshot_20260309.json',
        ],
        'analysis_script': 'scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_marginal_gain_law.py',
    }


if __name__ == '__main__':
    print(json.dumps(build_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_marginal_gain_snapshot(), indent=2, sort_keys=True))
